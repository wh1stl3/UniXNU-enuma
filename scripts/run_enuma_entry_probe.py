"""Authorized temporary diagnostic boot; never flash/erase/change slots.

Requires an existing matching recovery backup from this task. Selects exactly
one Android enuma, checks image/backup digests, and records only redacted data.
If reset returns to fastboot, rechecks identity and normally reboots Android.
"""
import argparse
import hashlib
import json
import shlex
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = 'D:/Code/PortingiOS/common/tools/platform-tools/adb.exe'
FASTBOOT = 'D:/Code/PortingiOS/common/tools/platform-tools/fastboot.exe'


def fastboot_value_matches(result, variable, expected):
    """Require one exact GetVar value; prefixes and contradictory values fail."""
    output = (result.stdout + result.stderr).decode(errors='replace')
    values = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('(bootloader)'):
            line = line[len('(bootloader)'):].strip()
        key, separator, value = line.partition(':')
        if separator and key == variable:
            values.append(value.strip())
    return result.returncode == 0 and 'FAILED' not in output and values == [expected]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--label', required=True, choices=('shim-entry-2s','shim-entry-7s','shim-copy-2s','sec-entry','sec-memory','dxe-entry','dxe-dispatch','dxe-dispatch-return','dxe-queue-entry','dxe-driver-return','gop-probe','android-log-reservation'))
    args = parser.parse_args()
    image = args.image.resolve()
    if not image.is_relative_to((ROOT/'out').resolve()): raise ValueError('image outside own out/')
    meta = json.loads(image.with_suffix('.json').read_text())
    if hashlib.sha256(image.read_bytes()).hexdigest() != meta['image_sha256']: raise ValueError('image changed')
    previous = json.loads((ROOT/'out/device-tests/current.local.json').read_text())
    backup_dir = Path(previous.get('recovery_backup_directory', previous['directory']))
    backups = previous['backups']
    for backup in backups:
        if hashlib.sha256((backup_dir/(backup['partition']+'.bin')).read_bytes()).hexdigest() != backup['sha256']:
            raise ValueError('recovery backup changed')
    def invoke(tool, argv, timeout=10):
        return subprocess.run([tool,*argv],capture_output=True,timeout=timeout)
    devices = invoke(ADB,['devices']).stdout.decode().splitlines()
    candidates = []
    for line in devices[1:]:
        fields = line.split()
        if len(fields)==2 and fields[1]=='device':
            r=invoke(ADB,['-s',fields[0],'shell','getprop ro.product.device'])
            if r.returncode==0 and r.stdout.strip()==b'enuma': candidates.append(fields[0])
    if len(candidates)!=1: raise ValueError('require exactly one online Android enuma')
    serial=candidates[0]
    def adb(command, rooted=False, timeout=10):
        return invoke(ADB,['-s',serial,'shell',('su -c '+shlex.quote(command)) if rooted else command],timeout)
    if adb('getprop ro.boot.slot_suffix').stdout.decode().strip()!=previous['slot']: raise ValueError('slot changed')
    if adb('getprop sys.boot_completed').stdout.strip()!=b'1' or adb('getprop ro.boot.flash.locked').stdout.strip()!=b'0':
        raise ValueError('require unlocked boot-complete Android')
    if b'uid=0(root)' not in adb('id',True).stdout: raise ValueError('root unavailable')
    def check_partitions():
        for backup in backups:
            r=adb('sha256sum /dev/block/bootdevice/by-name/'+backup['partition'],True,30)
            if r.returncode or r.stdout.decode().split()[0]!=backup['sha256']: raise ValueError('partition differs from backup')
    check_partitions()
    out=ROOT/'out/device-tests'/(time.strftime('%Y%m%dT%H%M%S')+'-'+args.label)
    out.mkdir(parents=True)
    (out/'target.local.json').write_text(json.dumps({'serial':serial,'adb':ADB,'fastboot':FASTBOOT}))
    state={'directory':str(out),'recovery_backup_directory':str(backup_dir),'slot':previous['slot'],
           'backups':backups,'candidate':str(image),'candidate_sha256':meta['image_sha256'],'label':args.label,
           'phase':'preflight-complete','preflight_boot_completed':True,'partition_writes':False}
    def save():
        (ROOT/'out/device-tests/current.local.json').write_text(json.dumps(state,indent=2))
        (out/'result.json').write_text(json.dumps({k:v for k,v in state.items() if k not in ('directory','recovery_backup_directory')},indent=2)+'\n')
    def fastboot_identity():
        # USB enumeration can precede stable GetVar responses. Retry complete
        # sets; never accept a missing or mismatched identity field.
        queries = []
        for attempt in range(5):
            failed=[]
            for var, expected in [('product','enuma'),('current-slot',state['slot'][1:]),('unlocked','yes')]:
                r=invoke(FASTBOOT,['-s',serial,'getvar',var])
                queries.append({'attempt': attempt, 'variable': var, 'returncode': r.returncode,
                    'output': (r.stdout+r.stderr).decode(errors='replace').replace(serial, '<target>')})
                if not fastboot_value_matches(r, var, expected):
                    failed.append(var)
            (out/'fastboot-identity.local.json').write_text(json.dumps(queries,indent=2)+'\n')
            if not failed:
                state['fastboot_identity_retry_count']=attempt
                return
            time.sleep(1)
        state['phase']='fastboot-return-identity-aborted' if 'issued_at' in state else 'fastboot-identity-aborted'
        state['identity_failed_fields']=failed
        save()
        raise ValueError('fastboot identity mismatch: '+','.join(failed))
    save()
    r=invoke(ADB,['-s',serial,'reboot','bootloader'])
    if r.returncode: raise ValueError('reboot bootloader failed')
    for _ in range(25):
        if any(l.split() and l.split()[0]==serial for l in invoke(FASTBOOT,['devices']).stdout.decode().splitlines()):break
        time.sleep(1)
    else: raise ValueError('selected enuma absent in fastboot')
    fastboot_identity()
    state['phase']='temporary-boot-issued';state['issued_at']=time.strftime('%Y-%m-%d %H:%M:%S');save()
    before=time.monotonic()
    r=invoke(FASTBOOT,['-s',serial,'boot',str(image)],30)
    state['boot_returncode']=r.returncode;state['boot_output']=(r.stdout+r.stderr).decode(errors='replace')
    (out/'fastboot-boot.txt').write_text(state['boot_output']);state['phase']='observing-reset-return';save()
    print('Temporary boot command returned '+str(r.returncode),flush=True)
    if r.returncode: raise ValueError('boot command failed; recover normally from fastboot')
    rebooted_fastboot=False
    deadline=time.monotonic()+75
    while time.monotonic()<deadline:
        if not rebooted_fastboot and any(l.split() and l.split()[0]==serial for l in invoke(FASTBOOT,['devices']).stdout.decode().splitlines()):
            state['fastboot_return_seconds']=round(time.monotonic()-before,3);fastboot_identity()
            r=invoke(FASTBOOT,['-s',serial,'reboot'])
            if r.returncode: raise ValueError('normal recovery reboot failed')
            rebooted_fastboot=True;save()
        online=any(l.split() and l.split()[0]==serial and len(l.split())>1 and l.split()[1]=='device'
                   for l in invoke(ADB,['devices']).stdout.decode().splitlines())
        if online:
            if 'adb_return_seconds' not in state: state['adb_return_seconds']=round(time.monotonic()-before,3);save()
            if adb('getprop sys.boot_completed').stdout.strip()==b'1':
                if adb('getprop ro.product.device').stdout.strip()!=b'enuma': raise ValueError('Android identity mismatch')
                if b'uid=0(root)' not in adb('id',True).stdout: raise ValueError('root unavailable after return')
                check_partitions()
                state['phase']='recovered-android-boot-complete';state['recovery_boot_completed']=True
                state['partition_digests_unchanged']=True;state['boot_complete_seconds']=round(time.monotonic()-before,3)
                state['boot_reason']=adb('getprop ro.boot.bootreason').stdout.decode().strip();save()
                print(json.dumps({k:v for k,v in state.items() if k not in ('directory','recovery_backup_directory','backups','candidate')},indent=2),flush=True)
                return
        time.sleep(1)
    state['phase']='manual-recovery-needed';save()
    print('NO AUTOMATIC RETURN: manual fastboot recovery needed; result in '+str(out),flush=True)
    raise SystemExit(2)


if __name__ == '__main__': main()
