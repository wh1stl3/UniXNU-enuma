"""Read-only, bounded console-ramoops collector; raw bytes stay in local out/.

Does not reboot, mount, unlink, clear pstore, load modules or read physical RAM.
Start before an independently gated trial. A missing marker is inconclusive:
reset/bootloader retention and Android's early log consumers remain separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
CONSOLE = '/sys/fs/pstore/console-ramoops-0'


def marker_for(nonce):
    if not re.fullmatch(r'[0-9a-f]{32}', nonce):
        raise ValueError('nonce must be 32 lowercase hexadecimal characters')
    return ('ENUMA-R017:' + nonce + '\n').encode('ascii')


def collect(adb, serial, nonce, output, seconds=75, run=subprocess.run):
    marker = marker_for(nonce)
    output = Path(output).resolve()
    if not output.is_relative_to((ROOT / 'out').resolve()):
        raise ValueError('raw console output must remain under local out/')
    if not serial or not 0 < seconds <= 120:
        raise ValueError('explicit target serial and deadline 0..120 seconds required')
    output.mkdir(parents=True, exist_ok=False)
    deadline = time.monotonic() + seconds
    snapshots = []
    errors = 0
    seen = set()

    def read(*args):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired('collector deadline', seconds)
        return run([adb, '-s', serial, *args], capture_output=True,
                   timeout=min(3, remaining), check=False)

    try:
        while time.monotonic() < deadline:
            try:
                identity = read('shell', 'getprop ro.product.device')
                if identity.returncode != 0 or not identity.stdout.strip():
                    time.sleep(0.25)
                    continue
                if identity.stdout.strip() != b'enuma':
                    raise ValueError('selected serial is not enuma; collector stopped')
                # Query identity on every iteration before the fixed root read.
                uid = read('shell', 'su -c "id -u"')
                if uid.returncode != 0 or uid.stdout.strip() != b'0':
                    errors += 1
                    time.sleep(0.25)
                    continue
                console = read('exec-out', 'su -c "cat ' + CONSOLE + '"')
                if console.returncode == 0 and console.stdout:
                    digest = hashlib.sha256(console.stdout).hexdigest()
                    if digest not in seen:
                        seen.add(digest)
                        name = 'console-' + str(len(snapshots)) + '.bin'
                        (output / name).write_bytes(console.stdout)
                        snapshots.append(dict(file=name, sha256=digest, size=len(console.stdout),
                                              marker_present=marker in console.stdout))
                    if marker in console.stdout:
                        break
                else:
                    errors += 1
            except subprocess.TimeoutExpired:
                errors += 1
            time.sleep(0.25)
    finally:
        report = dict(scope='read-only pstore files; no physical RAM or device writes',
                      snapshots=snapshots, read_errors=errors,
                      marker_present=any(s['marker_present'] for s in snapshots),
                      nonce=nonce, absence_is_inconclusive=True)
        (output / 'collection.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', default='adb')
    parser.add_argument('--serial', required=True)
    parser.add_argument('--nonce', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=75)
    args = parser.parse_args()
    report = collect(args.adb, args.serial, args.nonce, args.output, args.seconds)
    print(json.dumps({k: report[k] for k in ('marker_present', 'read_errors', 'absence_is_inconclusive')}))


if __name__ == '__main__':
    main()
