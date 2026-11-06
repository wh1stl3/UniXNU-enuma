"""R-002: normal ABI probe then guarded read-only 16-byte marker, no reboot.

Checks current identity, ABI, backup digests, exact FDT and all eight pages.
Starts dmesg streaming before each normal load; never force-loads or writes RAM.
Marker bytes remain private; public output reports expected-marker equality.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import struct
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name',required=True)
    parser.add_argument('--require-seed',action='store_true',help='return 2 if fixed seed does not match; required for future survival trials')
    args=parser.parse_args()
    if not re.fullmatch('[a-z0-9-]+',args.name):raise ValueError('simple output name required')
    out=ROOT/'out/log-readback'/args.name;public=ROOT/'reports'/('enuma-log-'+args.name+'.json')
    if out.exists() or public.exists():raise ValueError('refuse overwrite')
    state=json.loads((ROOT/'out/device-tests/current.local.json').read_text())
    if state['phase']!='recovered-android-boot-complete':raise ValueError('require recovered Android')
    target=json.loads((Path(state['directory'])/'target.local.json').read_text())
    adb=target['adb'];serial=target['serial'];out.mkdir(parents=True)
    def call(command):
        return subprocess.run([adb,'-s',serial,'exec-out','su -c '+shlex.quote(command)],capture_output=True,timeout=30)
    def read(command):
        result=call(command)
        if result.returncode:raise ValueError('command failed: '+command)
        return result.stdout
    if read('getprop ro.product.device').strip()!=b'enuma' or read('getprop sys.boot_completed').strip()!=b'1':raise ValueError('identity/state differs')
    if b'uid=0(root)' not in read('id') or read('uname -r').strip()!=b'4.19.157-perf-gf8cf95f4dc15':raise ValueError('root/kernel ABI differs')
    if read('getprop ro.boot.slot_suffix').strip().decode()!=state['slot']:raise ValueError('slot changed')
    for backup in state['backups']:
        if read('sha256sum /dev/block/bootdevice/by-name/'+backup['partition']).split()[0].decode()!=backup['sha256']:raise ValueError('partition changed')
    blob=read('cat /sys/firmware/fdt')
    if hashlib.sha256(blob).hexdigest()!='6e88ca4a3bfaf8823da9bcf44defdd5ad7a3f8eec671223675076fd5457a0d09':raise ValueError('FDT ownership changed')
    offset=struct.unpack_from('>I',blob,16)[0]
    if struct.unpack_from('>4Q',blob,offset)!=(0x9fff7000,0x8000,0,0):raise ValueError('reserve tuple differs')
    flags=read('dd if=/proc/kpageflags bs=8 skip='+str(0x9fff7000//4096)+' count=8 2>/dev/null')
    if len(flags)!=64 or not all(v&(1<<32) for v in struct.unpack('<8Q',flags)):raise ValueError('range not protected')
    report={'scope':'normal ABI probe and guarded read-only marker; no reboot or physical writes',
        'boot_image_sha256':state['candidate_sha256'],'fdt_sha256':hashlib.sha256(blob).hexdigest(),
        'all_eight_pages_reserved':True,'physical_write_bytes':0,'physical_read_bytes':0,
        'module_runs':[],'started_at':time.strftime('%Y-%m-%d %H:%M:%S')}
    def save():
        public.write_text(json.dumps(report,indent=2)+'\n')
    save()
    for mode in ('abi','marker'):
        module=ROOT/'out/log-readback'/('module-'+mode)/('enuma_r002_'+mode+'.ko')
        meta=json.loads(module.with_suffix('.json').read_text());sha=hashlib.sha256(module.read_bytes()).hexdigest()
        wanted={'abi':'43b6bbd06fa16af578501db60ed917c5c205243aa6f8429763ca79671e4e2313',
                'marker':'6644cf40bd4ee85ce6ec8a0a57eeef08aa0a6a2e79b61b75e1230f6b469bd6f2'}[mode]
        if sha!=wanted or sha!=meta['module_sha256']:raise ValueError('module changed')
        name='enuma_r002_'+mode;remote='/data/local/tmp/'+name+'-'+args.name+'.ko'
        if (name+' ').encode() in read('cat /proc/modules'):raise ValueError('module already loaded')
        if call('test ! -e '+remote).returncode:raise ValueError('upload already exists')
        push=subprocess.run([adb,'-s',serial,'push',str(module),remote],capture_output=True,timeout=30)
        if push.returncode or read('sha256sum '+remote).split()[0].decode()!=sha:raise ValueError('upload mismatch')
        old=read('dmesg');tag=b'ENUMA_R002 ABI_OK no_physical_access' if mode=='abi' else b'ENUMA_R002 MARKER='
        baseline_count=old.count(tag);stream=None
        record={'mode':mode,'module_sha256':sha};report['module_runs'].append(record);save()
        log=out/(mode+'-dmesg.local.txt')
        try:
            with log.open('wb') as sink,(out/(mode+'-stderr.local.txt')).open('wb') as err:
                stream=subprocess.Popen([adb,'-s',serial,'exec-out','su -c '+shlex.quote('dmesg -w')],stdout=sink,stderr=err)
                time.sleep(1)
                if stream.poll() is not None or log.stat().st_size==0:raise ValueError('stream unavailable; no insmod')
                record['stream_started_before_load']=True
                load=call('insmod '+remote);(out/(mode+'-insmod.local.txt')).write_bytes(load.stdout+load.stderr)
                record['insmod_returncode']=load.returncode
                record['loaded']=(name+' ').encode() in read('cat /proc/modules')
                time.sleep(1)
                contents=log.read_bytes();record['new_log_records']=contents.count(tag)-baseline_count
                if mode=='marker':
                    values=re.findall(rb'ENUMA_R002 MARKER=([0-9a-fA-F]{32})',contents)
                    if values and record['new_log_records']==1:
                        actual=bytes.fromhex(values[-1].decode());report['physical_read_bytes']=16
                        report['matches_seed_marker']=actual==b'ENUMA-R002-SEED1'
                if record['loaded']:record['rmmod_returncode']=call('rmmod '+name).returncode
                record['unloaded']=(name+' ').encode() not in read('cat /proc/modules')
        finally:
            if stream and stream.poll() is None:
                stream.terminate()
                try:stream.wait(timeout=5)
                except subprocess.TimeoutExpired:stream.kill();stream.wait(timeout=5)
            record['log_sha256']=hashlib.sha256(log.read_bytes()).hexdigest() if log.exists() else None
            if record.get('unloaded'):
                record['temporary_upload_removed']=call('rm '+remote).returncode==0
            save()
        if record.get('insmod_returncode')!=0 or not record.get('loaded') or not record.get('unloaded') or record.get('new_log_records')!=1:
            raise ValueError('R-002 ABI/readback not satisfied; stop, no force load or alternate address')
    report['android_boot_complete']=read('getprop sys.boot_completed').strip()==b'1'
    report['root_after']=b'uid=0(root)' in read('id')
    report['partition_digests_unchanged']=all(read('sha256sum /dev/block/bootdevice/by-name/'+b['partition']).split()[0].decode()==b['sha256'] for b in state['backups'])
    report['persistence_proven']=False
    save();print(json.dumps(report,indent=2))
    if args.require_seed and report.get('matches_seed_marker') is not True:
        raise SystemExit(2)

if __name__=='__main__':main()
