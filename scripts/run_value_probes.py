"""Run the display value probes and decode what came back.

Each probe is a separate image that reads one display register and encodes
four bits of it into the length of the reset delay. The host recovers the
value from the return time, so one image yields one nibble. This script
packages every staged raw, runs it, and prints the decoded table.

Usage: python scripts/run_value_probes.py [probe indices ...]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
BASELINE = 16.7  # return time of the same profile with the plain two second delay
ADDRESSES = {
    1: '0x0ae00000 MDP version',
    2: '0x0ae05014 pipe0 SDE base',
    3: '0x0ae07014 pipe1 SDE base',
    4: '0x0ae09014 pipe2 SDE base',
    5: '0x0ae0b014 pipe3 SDE base',
    6: '0x0ae25014 pipe4 SDE base',
    7: '0x0ae27014 pipe5 SDE base',
}


def run(command):
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)


def main():
    indices = [int(x) for x in sys.argv[1:]] or sorted(ADDRESSES)
    rows = []
    for index in indices:
        raw = ROOT / 'out/boot-candidate' / f'vprobe{index}.raw'
        if not raw.exists():
            print(f'probe {index}: no staged raw, skipped')
            continue
        image = ROOT / 'out/boot-candidate' / f'vprobe{index}-queue1-stage13-delay2-boot-v3.img'
        if image.exists():
            image.unlink()
        result = run([PYTHON, 'scripts/package_enuma_boot.py', '--kernel', str(raw),
                      '--ramdisk', 'out/boot-candidate/empty-ramdisk',
                      '--output', str(image)])
        if result.returncode != 0:
            print(f'probe {index}: packaging failed')
            continue
        result = run([PYTHON, 'scripts/run_enuma_entry_probe.py', '--image', str(image),
                      '--label', 'dxe-driver-return'])
        match = re.search(r'"adb_return_seconds":\s*([0-9.]+)', result.stdout)
        if not match:
            stalled = 'NO AUTOMATIC RETURN' in result.stdout
            print(f'probe {index}: {"stalled" if stalled else "no return time"}')
            rows.append({'index': index, 'result': 'stalled' if stalled else 'unknown'})
            continue
        seconds = float(match.group(1))
        nibble = round(seconds - BASELINE)
        rows.append({'index': index, 'seconds': seconds, 'nibble': nibble,
                     'register': ADDRESSES.get(index, '')})
        print(f'probe {index}: {seconds:.3f}s -> nibble {nibble}  {ADDRESSES.get(index, "")}')
    (ROOT / 'reports/enuma-value-probes.json').write_text(
        json.dumps({'baseline_seconds': BASELINE, 'probes': rows}, indent=2) + '\n')
    print('written to reports/enuma-value-probes.json')


if __name__ == '__main__':
    main()
