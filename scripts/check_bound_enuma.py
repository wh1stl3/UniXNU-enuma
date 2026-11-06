"""Independent read-only check of the previously bound enuma; no reboot/flash."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
from enuma_paths import evidence_path
ROOT=Path(__file__).resolve().parents[1]
ADB='D:/Code/PortingiOSLegacy/common/tools/platform-tools/adb.exe'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.relative_to(ROOT/'out')
    if out.exists():raise ValueError('new independent output required')
    result=dict(passed=False,time_utc=datetime.now(timezone.utc).isoformat(),boot_issued=False,
                scope='bound enuma only; read-only identity/root/partition/backup check')
    try:
        state_path=ROOT/'out/device-tests/current.local.json';before=state_path.read_bytes();state=json.loads(before)
        target=json.loads((evidence_path(state['directory'],ROOT)/'target.local.json').read_text())['serial']
        def invoke(args,timeout=30):
            r=subprocess.run([ADB,*args],capture_output=True,timeout=timeout)
            if r.returncode:raise ValueError('bound ADB read failed')
            return r.stdout.decode(errors='replace').strip()
        devices=invoke(['devices']).splitlines()[1:]
        if [line.split()[1] for line in devices if len(line.split())==2 and line.split()[0]==target]!=['device']:
            raise ValueError('previously bound enuma is not online/authorized; other devices untouched')
        def shell(command,rooted=False):return invoke(['-s',target,'shell','su -c '+shlex.quote(command) if rooted else command])
        if shell('getprop ro.product.device')!='enuma':raise ValueError('bound identity mismatch')
        boot_id=shell('cat /proc/sys/kernel/random/boot_id')
        checks=dict(device='enuma',boot_completed=shell('getprop sys.boot_completed'),slot=shell('getprop ro.boot.slot_suffix'),
                    flash_locked=shell('getprop ro.boot.flash.locked'),root_available='uid=0(root)' in shell('id',True))
        result['checks']=checks
        if checks!=dict(device='enuma',boot_completed='1',slot='_a',flash_locked='0',root_available=True):raise ValueError('Android/root/slot/unlock mismatch')
        if state['slot']!='_a' or {b['partition'] for b in state['backups']}!={'boot_a','vendor_boot_a'}:raise ValueError('backup contract changed')
        backup=evidence_path(state.get('recovery_backup_directory',state['directory']),ROOT);parts=[]
        for b in state['backups']:
            if sha(backup/(b['partition']+'.bin'))!=b['sha256']:raise ValueError('local backup changed')
            if shell('sha256sum /dev/block/bootdevice/by-name/'+b['partition'],True).split()[0]!=b['sha256']:raise ValueError('partition changed')
            parts.append(dict(partition=b['partition'],device_and_backup_match=True))
        if shell('cat /proc/sys/kernel/random/boot_id')!=boot_id or state_path.read_bytes()!=before:raise ValueError('state changed during independent check')
        result.update(passed=True,partitions=parts,boot_id_sha256=hashlib.sha256(boot_id.encode()).hexdigest(),
                      current_local_unchanged=True,checker_sha256=sha(Path(__file__)))
    except Exception as exc:result['error']=str(exc)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
