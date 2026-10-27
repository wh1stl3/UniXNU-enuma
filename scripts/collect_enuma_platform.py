"""Read-only enuma capture. No reboot, partition writes, debugfs mount or MMIO."""
import argparse
import hashlib
import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', default='D:/Code/PortingiOSLegacy/common/tools/platform-tools/adb.exe')
    args = parser.parse_args()
    def run(argv):
        return subprocess.run([args.adb, *argv], capture_output=True, timeout=60)
    devices = run(['devices'])
    if devices.returncode: raise ValueError('ADB discovery failed')
    candidates = []
    for line in devices.stdout.decode().splitlines()[1:]:
        fields = line.split()
        if len(fields) == 2 and fields[1] == 'device':
            serial = fields[0]
            product = run(['-s', serial, 'shell', 'getprop ro.product.device'])
            if product.returncode == 0 and product.stdout.strip() == b'enuma': candidates.append(serial)
    if len(candidates) != 1: raise ValueError('require exactly one connected enuma')
    prefix = ['-s', candidates[0]]
    root = run(prefix + ['shell', 'su -c id'])
    if root.returncode or b'uid=0(root)' not in root.stdout: raise ValueError('root not available')
    out = ROOT / 'out/device'; out.mkdir(parents=True, exist_ok=True)
    commands = {
        'identity': 'getprop ro.product.device; getprop ro.build.fingerprint; getprop ro.boot.flash.locked; getprop ro.boot.verifiedbootstate; getprop sys.boot_completed',
        'iomem': 'cat /proc/iomem',
        'memory': 'cat /proc/meminfo',
        'display-modes': 'cat /sys/class/drm/card0-DSI-1/modes',
        'touch-binding': 'readlink /sys/bus/spi/devices/spi0.0/driver',
        'boot-hashes': 'for p in boot_a vendor_boot_a xbl_a xbl_config_a abl_a; do echo PARTITION:$p; blockdev --getsize64 /dev/block/bootdevice/by-name/$p; sha256sum /dev/block/bootdevice/by-name/$p; done',
    }
    records = []
    for name, command in commands.items():
        result = run(prefix + ['shell', 'su -c ' + shlex.quote(command)])
        (out / (name + '.stdout')).write_bytes(result.stdout)
        (out / (name + '.stderr')).write_bytes(result.stderr)
        records.append({'name': name, 'exit_code': result.returncode, 'bytes': len(result.stdout),
                        'sha256': hashlib.sha256(result.stdout).hexdigest()})
    for name, device in [('live-fdt', '/sys/firmware/fdt'),
                         *[(n, '/dev/block/bootdevice/by-name/' + n) for n in ('xbl_a', 'xbl_config_a', 'abl_a')]]:
        result = run(prefix + ['exec-out', 'su -c ' + shlex.quote('cat ' + device)])
        data = result.stdout
        if result.returncode or not data or len(data) > 16 * 1024 * 1024: raise ValueError('invalid read: ' + name)
        path = out / (name + '.bin')
        if path.exists() and path.read_bytes() != data: raise ValueError('refuse to overwrite different capture: ' + name)
        path.write_bytes(data)
        records.append({'name': name, 'exit_code': 0, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    report = {'scope': 'live Android read-only collection; serial excluded; no boot or writes',
              'product': 'enuma', 'records': records}
    (ROOT / 'reports/enuma-live-capture.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: uniquely identified rooted enuma; captured platform inputs without reboot/writes')


if __name__ == '__main__': main()
