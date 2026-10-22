"""Capture R-002 live FDT/page metadata only; never access physical log bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import struct
import subprocess
from audit_inputs import parse_fdt

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name',required=True)
    args=parser.parse_args()
    if not args.name.isascii() or not args.name.replace('-','').isalnum():raise ValueError('simple output name required')
    out=ROOT/'out/log-readback'/args.name
    report_path=ROOT/'reports'/('enuma-log-'+args.name+'.json')
    if out.exists() or report_path.exists():raise ValueError('refuse overwrite')
    state=json.loads((ROOT/'out/device-tests/current.local.json').read_text())
    if state['phase']!='recovered-android-boot-complete' or state['label']!='android-log-reservation':raise ValueError('wrong test state')
    target=json.loads((Path(state['directory'])/'target.local.json').read_text())
    def read(command):
        run=subprocess.run([target['adb'],'-s',target['serial'],'exec-out','su -c '+shlex.quote(command)],capture_output=True,timeout=30)
        if run.returncode:raise ValueError('rooted read failed')
        return run.stdout
    if read('getprop ro.product.device').strip()!=b'enuma' or read('getprop sys.boot_completed').strip()!=b'1':raise ValueError('wrong device/state')
    if b'uid=0(root)' not in read('id'):raise ValueError('root unavailable')
    if read('uname -r').strip()!=b'4.19.157-perf-gf8cf95f4dc15':raise ValueError('kernel ABI changed')
    for backup in state['backups']:
        if read('sha256sum /dev/block/bootdevice/by-name/'+backup['partition']).split()[0].decode()!=backup['sha256']:
            raise ValueError('partition changed')
    blob=read('cat /sys/firmware/fdt');parse_fdt(blob)
    pos=struct.unpack_from('>I',blob,16)[0];res=[]
    while pos+16<=len(blob):
        base,size=struct.unpack_from('>QQ',blob,pos);pos+=16
        if not base and not size:break
        res.append({'base':hex(base),'size':hex(size)})
    else:raise ValueError('unterminated reserve map')
    flags=read('dd if=/proc/kpageflags bs=8 skip='+str(0x9fff7000//4096)+' count=8 2>/dev/null')
    if len(flags)!=64:raise ValueError('incomplete page metadata')
    values=struct.unpack('<8Q',flags);reserved=all(v&(1<<32) for v in values)
    protected=reserved and res==[{'base':'0x9fff7000','size':'0x8000'}]
    out.mkdir(parents=True);(out/'active-fdt.bin').write_bytes(blob);(out/'pageflags.bin').write_bytes(flags)
    for name,command in [('iomem.txt','cat /proc/iomem'),('dmesg.txt','dmesg')]:
        (out/name).write_bytes(read(command))
    report={'scope':'Android FDT and page metadata only; no log bytes accessed',
        'image_sha256':state['candidate_sha256'],'issued_at':state['issued_at'],
        'android_boot_complete':True,'root':True,'partition_digests_unchanged':True,
        'adb_return_seconds':state['adb_return_seconds'],'boot_complete_seconds':state['boot_complete_seconds'],
        'fdt_sha256':hashlib.sha256(blob).hexdigest(),'fdt_bytes':len(blob),'header_reservations':res,
        'page_flags':[hex(v) for v in values],'all_eight_pages_reserved':reserved,
        'kernel_page_shift':12,'runtime_reservation_observed':protected,
        'log_memory_accessed':False,'persistence_proven':False,'verified_flags_changed':False}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if not protected:raise SystemExit(2)

if __name__=='__main__':main()
