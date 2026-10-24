"""Cold-start temporary boot from fastboot; no flash/erase/slot change.

Starts from an already-powered-off device that the operator has booted straight
into the bootloader, so no Android boot sits between the power cycle and the
probe. Partition digests cannot be read in the bootloader; the caller must have
verified them immediately before the power cycle.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = 'D:/Code/PortingiOS/common/tools/platform-tools/adb.exe'
FASTBOOT = 'D:/Code/PortingiOS/common/tools/platform-tools/fastboot.exe'


def invoke(tool, argv, timeout=15):
    return subprocess.run([tool, *argv], capture_output=True, timeout=timeout)


def fastboot_value(result, variable):
    output = (result.stdout + result.stderr).decode(errors='replace')
    values = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('(bootloader)'):
            line = line[len('(bootloader)'):].strip()
        key, sep, value = line.partition(':')
        if sep and key == variable:
            values.append(value.strip())
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--slot', default='a')
    parser.add_argument('--observe-seconds', type=int, default=75)
    args = parser.parse_args()
    image = args.image.resolve()
    if not image.is_relative_to((ROOT / 'out').resolve()):
        raise ValueError('image outside own out/')
    meta = json.loads(image.with_suffix('.json').read_text())
    if hashlib.sha256(image.read_bytes()).hexdigest() != meta['image_sha256']:
        raise ValueError('image changed')
    if meta.get('hardware_review') is not None:
        raise ValueError('pixel preview candidates are not part of this cold-start path')

    listing = invoke(FASTBOOT, ['devices']).stdout.decode(errors='replace').splitlines()
    serials = [line.split()[0] for line in listing if line.split()]
    if len(serials) != 1:
        raise ValueError('require exactly one fastboot device, saw %r' % (serials,))
    serial = serials[0]
    product = fastboot_value(invoke(FASTBOOT, ['-s', serial, 'getvar', 'product']), 'product')
    slot = fastboot_value(invoke(FASTBOOT, ['-s', serial, 'getvar', 'current-slot']), 'current-slot')
    unlocked = fastboot_value(invoke(FASTBOOT, ['-s', serial, 'getvar', 'unlocked']), 'unlocked')
    if product != ['enuma'] or slot != [args.slot] or unlocked != ['yes']:
        raise ValueError('fastboot identity mismatch: %r %r %r' % (product, slot, unlocked))

    out = ROOT / 'out/device-tests' / (time.strftime('%Y%m%dT%H%M%S') + '-' + args.label)
    out.mkdir(parents=True)
    state = {
        'coordinate': 'cold-start-from-bootloader',
        'serial': serial, 'slot': '_' + args.slot,
        'candidate': str(image), 'candidate_sha256': meta['image_sha256'],
        'label': args.label, 'partition_writes': False,
        'preflight_partition_digests': 'verified immediately before the power cycle; not readable in the bootloader',
    }
    (out / 'fastboot-identity.local.json').write_text(json.dumps(
        {'product': product, 'current-slot': slot, 'unlocked': unlocked}, indent=2) + '\n')

    state['issued_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
    started = time.monotonic()
    result = invoke(FASTBOOT, ['-s', serial, 'boot', str(image)], 60)
    state['boot_returncode'] = result.returncode
    state['boot_output'] = (result.stdout + result.stderr).decode(errors='replace')
    (out / 'fastboot-boot.txt').write_text(state['boot_output'])
    state['phase'] = 'observing-reset-return'
    (out / 'result.json').write_text(json.dumps(state, indent=2) + '\n')
    print('Temporary boot command returned ' + str(result.returncode), flush=True)
    if result.returncode:
        raise SystemExit(3)

    deadline = time.monotonic() + args.observe_seconds
    while time.monotonic() < deadline:
        online = any(line.split()[0] == serial and len(line.split()) > 1 and line.split()[1] == 'device'
                     for line in invoke(ADB, ['devices']).stdout.decode(errors='replace').splitlines()
                     if line.split())
        if online:
            state['adb_return_seconds'] = round(time.monotonic() - started, 3)
            (out / 'result.json').write_text(json.dumps(state, indent=2) + '\n')
            boot = invoke(ADB, ['-s', serial, 'shell', 'getprop', 'sys.boot_completed']).stdout.strip()
            if boot == b'1':
                state['phase'] = 'cold-start-recovered-android-boot-complete'
                state['boot_complete_seconds'] = round(time.monotonic() - started, 3)
                state['boot_reason'] = invoke(ADB, ['-s', serial, 'shell', 'getprop', 'ro.boot.bootreason']).stdout.decode(errors='replace').strip()
                (out / 'result.json').write_text(json.dumps(state, indent=2) + '\n')
                print(json.dumps(state, indent=2), flush=True)
                return
        time.sleep(1)

    state['phase'] = 'manual-recovery-needed'
    (out / 'result.json').write_text(json.dumps(state, indent=2) + '\n')
    print('NO AUTOMATIC RETURN: manual recovery needed; result in ' + str(out), flush=True)
    raise SystemExit(2)


if __name__ == '__main__':
    main()
