"""Read-only recovery verification; preserve the failed trial and append evidence."""
import hashlib
import json
import shlex
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = 'D:/Code/PortingiOS/common/tools/platform-tools/adb.exe'


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def atomic_json(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def reconcile(root=ROOT, invoke=None):
    # Resolve at call time. A default of subprocess.run binds at import, so
    # patching this module's subprocess attribute cannot stub the device
    # commands and a unit test would silently drive the real adb.
    if invoke is None:
        invoke = subprocess.run
    state_path = root / 'out/device-tests/current.local.json'
    original_bytes = state_path.read_bytes()
    state = json.loads(original_bytes)
    def command(args):
        result = invoke([ADB, *args], capture_output=True, text=True, timeout=45)
        if result.returncode:
            raise ValueError('read-only recovery command failed')
        return result.stdout.strip()
    candidates = []
    for line in command(['devices']).splitlines()[1:]:
        parts = line.split()
        if len(parts) == 2 and parts[1] == 'device':
            if command(['-s', parts[0], 'shell', 'getprop ro.product.device']) == 'enuma':
                candidates.append(parts[0])
    if len(candidates) != 1:
        raise ValueError('require exactly one online enuma')
    serial = candidates[0]
    def shell(text, root_command=False):
        return command(['-s', serial, 'shell', 'su -c ' + shlex.quote(text) if root_command else text])
    checks = {'device': shell('getprop ro.product.device'),
              'boot_completed': shell('getprop sys.boot_completed'),
              'slot': shell('getprop ro.boot.slot_suffix'),
              'flash_locked': shell('getprop ro.boot.flash.locked'),
              'root_available': 'uid=0(root)' in shell('id', True)}
    if (checks['device'] != 'enuma' or checks['boot_completed'] != '1' or
            checks['slot'] != state['slot'] or checks['flash_locked'] != '0' or not checks['root_available']):
        raise ValueError('recovery identity, boot, root or slot check failed')
    backup_root = Path(state.get('recovery_backup_directory', state['directory']))
    partitions = []
    if {item['partition'] for item in state['backups']} != {'boot_a', 'vendor_boot_a'} or state['slot'] != '_a':
        raise ValueError('recovery is limited to the captured enuma slot A contract')
    for item in state['backups']:
        name, expected = item['partition'], item['sha256']
        if sha256(backup_root / (name + '.bin')) != expected:
            raise ValueError('local recovery backup changed: ' + name)
        fields = shell('sha256sum /dev/block/bootdevice/by-name/' + name, True).split()
        if not fields or fields[0] != expected:
            raise ValueError('device partition changed: ' + name)
        partitions.append({'partition': name, 'sha256': expected, 'device_and_backup_match': True})
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%dT%H%M%S')
    evidence_path = root / 'out/device-tests' / (stamp + '-recovery-reconciliation.json')
    evidence = {'scope': 'read-only recovery reconciliation; no boot, flash or device writes',
                'time_zone': 'Asia/Shanghai', 'checks': checks, 'partitions': partitions,
                'prior_phase': state['phase'], 'prior_state_sha256': hashlib.sha256(original_bytes).hexdigest(),
                'failed_trial_preserved': True}
    atomic_json(evidence_path, evidence)
    # Do not rewrite the failed trial result.json: current state points to new evidence.
    if state_path.read_bytes() != original_bytes:
        raise ValueError('current state changed during recovery verification')
    state.update(phase='recovered-android-boot-complete', recovery_boot_completed=True,
                 partition_digests_unchanged=True,
                 recovery_reconciliation=str(evidence_path.relative_to(root)))
    atomic_json(state_path, state)
    public = root / 'reports/enuma-recovery-reconciliation.json'
    atomic_json(public, {**evidence, 'evidence': str(evidence_path.relative_to(root))})
    print('PASS: enuma Android/root/slot/unlock and both device/backup digests; failed trial preserved')
    return evidence


if __name__ == '__main__':
    reconcile()
