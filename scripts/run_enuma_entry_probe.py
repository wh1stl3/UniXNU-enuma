"""Authorized temporary diagnostic boot; never flash/erase/change slots.

Requires an existing matching recovery backup from this task. Selects exactly
one Android enuma, checks image/backup digests, and records only redacted data.
If reset returns to fastboot, rechecks identity and normally reboots Android.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import shlex
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = 'D:/Code/PortingiOS/common/tools/platform-tools/adb.exe'
FASTBOOT = 'D:/Code/PortingiOS/common/tools/platform-tools/fastboot.exe'


def require_hardware_review(meta, approvals):
    """Protected profiles require recorded authorization for the exact image."""
    review = meta.get('hardware_review')
    if review is None:
        return
    if review not in ('R-005', 'R-017', 'R-017-MAP', 'R-017-READ', 'R-017-WARM','R-018'):
        raise ValueError('Unknown protected hardware review')
    entry = approvals.get(review, {})
    if entry.get('status') != 'approved' or meta['image_sha256'] not in entry.get('image_sha256', []):
        raise ValueError(review + ' is not approved for this exact image; no device action')
    if review=='R-018':
        from native_pixel_scope import SCOPE
        if meta.get('pixel_scope')!=SCOPE or entry.get('pixel_scope')!=SCOPE:
            raise ValueError('R-018 differs from exact reviewed ROI/operation scope')
    if review in ('R-017','R-017-MAP', 'R-017-READ', 'R-017-WARM') and (not entry.get('ramoops_scope') or meta.get('ramoops_scope') != entry['ramoops_scope']):
        raise ValueError('R-017 scope differs from exact reviewed console canary')


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


def observe_fastboot_return(present, disconnected):
    """A residual enumeration after `boot` is not a reset-return event."""
    return (not present or disconnected), (present and disconnected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--expected-serial', help='local-only camera/collector binding; must equal the independently selected enuma')
    parser.add_argument('--label', required=True, choices=('shim-entry-2s','shim-entry-7s','shim-copy-2s','sec-entry','sec-memory','dxe-entry','dxe-dispatch','dxe-dispatch-return','dxe-queue-entry','dxe-driver-return','gop-probe','android-log-reservation','system-transport'))
    parser.add_argument('--boot-clock',action='store_true',help='read-only before/after boot identity and bounded Linux uptime origin; calibration required')
    args = parser.parse_args()
    image = args.image.resolve()
    if not image.is_relative_to((ROOT/'out').resolve()): raise ValueError('image outside own out/')
    meta = json.loads(image.with_suffix('.json').read_text())
    if hashlib.sha256(image.read_bytes()).hexdigest() != meta['image_sha256']: raise ValueError('image changed')
    if meta.get('hardware_review') is not None:
        require_hardware_review(meta, json.loads((ROOT/'config/hardware-review-approvals.json').read_text(encoding='utf-8')))
    previous = json.loads((ROOT/'out/device-tests/current.local.json').read_text())
    if previous.get('phase') == 'manual-recovery-needed':
        raise ValueError('Previous probe is not recovered; restore and verify Android before any new trial')
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
    if args.expected_serial is not None and serial != args.expected_serial:
        raise ValueError('independently selected enuma differs from camera/collector target')
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
    if args.boot_clock:
        from boot_origin import capture
        pre_clock,pre_samples=capture(adb)
        state['pre_boot_clock']=pre_clock
        (out/'pre-boot-clock.local.json').write_text(json.dumps(pre_samples,indent=2)+'\n');save()
    r=invoke(ADB,['-s',serial,'reboot','bootloader'])
    if r.returncode: raise ValueError('reboot bootloader failed')
    for _ in range(25):
        if any(l.split() and l.split()[0]==serial for l in invoke(FASTBOOT,['devices']).stdout.decode().splitlines()):break
        time.sleep(1)
    else: raise ValueError('selected enuma absent in fastboot')
    fastboot_identity()
    before=time.monotonic()
    state['phase']='temporary-boot-issued';state['issued_at']=time.strftime('%Y-%m-%d %H:%M:%S')
    state['issued_at_utc']=datetime.now(timezone.utc).isoformat()
    state['issued_monotonic']=before;save()
    r=invoke(FASTBOOT,['-s',serial,'boot',str(image)],30)
    state['boot_returncode']=r.returncode;state['boot_output']=(r.stdout+r.stderr).decode(errors='replace')
    state['boot_command_return_seconds']=round(time.monotonic()-before,3)
    state['boot_command_returned_at_utc']=datetime.now(timezone.utc).isoformat()
    (out/'fastboot-boot.txt').write_text(state['boot_output']);state['phase']='observing-reset-return';save()
    print('Temporary boot command returned '+str(r.returncode),flush=True)
    if r.returncode: raise ValueError('boot command failed; recover normally from fastboot')
    rebooted_fastboot=False
    disconnected=False
    deadline=time.monotonic()+75
    while time.monotonic()<deadline:
        present=any(l.split() and l.split()[0]==serial for l in invoke(FASTBOOT,['devices']).stdout.decode().splitlines())
        was_disconnected=disconnected
        disconnected,returned=observe_fastboot_return(present,disconnected)
        if disconnected and not was_disconnected:
            state['fastboot_disconnect_observed_seconds']=round(time.monotonic()-before,3);save()
        if not rebooted_fastboot and returned:
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
                if args.boot_clock:
                    try:
                        post_clock,post_samples=capture(adb,before,pre_clock['boot_id_sha256'])
                        state['post_boot_clock']=post_clock
                        (out/'post-boot-clock.local.json').write_text(json.dumps(post_samples,indent=2)+'\n');save()
                    except Exception as error:
                        state['boot_clock_error']=str(error);save();raise
                print(json.dumps({k:v for k,v in state.items() if k not in ('directory','recovery_backup_directory','backups','candidate')},indent=2),flush=True)
                return
        time.sleep(1)
    state['phase']='manual-recovery-needed';save()
    print('NO AUTOMATIC RETURN: manual fastboot recovery needed; result in '+str(out),flush=True)
    raise SystemExit(2)


if __name__ == '__main__': main()
