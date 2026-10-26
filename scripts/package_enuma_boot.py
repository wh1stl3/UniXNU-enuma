"""Enuma raw-kernel Android boot v3 packaging via pinned AOSP; no device commands."""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = 4096


def padded(value): return (value + PAGE - 1) // PAGE * PAGE
def digest(value): return hashlib.sha256(value).hexdigest()


def verify(data, kernel, ramdisk):
    if len(data) < PAGE or data[:8] != b'ANDROID!': raise ValueError('missing boot v3 header')
    ks, rs, os_version, header_size = struct.unpack_from('<4I', data, 8)
    if struct.unpack_from('<I', data, 40)[0] != 3 or header_size != 1580:
        raise ValueError('not v3')
    if any(data[24:40]) or any(data[44:1580]): raise ValueError('unexpected reserved values or command line')
    end_kernel = PAGE + ks; start_ramdisk = PAGE + padded(ks)
    expected_size = start_ramdisk + padded(rs)
    if len(data) != expected_size or ks != len(kernel) or rs != len(ramdisk):
        raise ValueError('section sizes or trailing payload differ')
    if data[PAGE:end_kernel] != kernel or data[start_ramdisk:start_ramdisk+rs] != ramdisk:
        raise ValueError('section content mismatch')
    if any(data[1580:PAGE]) or any(data[end_kernel:start_ramdisk]) or any(data[start_ramdisk+rs:]):
        raise ValueError('nonzero padding')
    return {'header_version': 3, 'page_bytes': PAGE, 'kernel_bytes': ks, 'ramdisk_bytes': rs,
            'os_version_field': os_version, 'kernel_sha256': digest(kernel), 'ramdisk_sha256': digest(ramdisk)}


def package(kernel_path, ramdisk_path, output, fixture=False, hardware_review=None):
    if hardware_review not in (None, 'R-005', 'R-017', 'R-017-MAP', 'R-017-READ', 'R-017-WARM','R-018','R-019','R-020','R-022'): raise ValueError('unknown hardware review')
    lock = json.loads((ROOT / 'config/porting-sources.lock.json').read_text())['aosp_mkbootimg']
    base = Path(lock['path'])
    for name, expected in lock['sha256'].items():
        if digest((base / name).read_bytes()) != expected: raise ValueError('AOSP source pin mismatch: ' + name)
    output = output.resolve()
    if not output.is_relative_to((ROOT / 'out').resolve()): raise ValueError('output must be inside this repository out/')
    if output.exists(): raise ValueError('refuse to overwrite existing image; choose a new output name')
    kernel = kernel_path.read_bytes(); ramdisk = ramdisk_path.read_bytes()
    if len(kernel) < 64 or kernel[56:60] != b'ARM\x64': raise ValueError('expected raw ARM64 BootShim+FD, not gzip or PE')
    if not fixture and struct.unpack_from('<Q', kernel, 16)[0] != len(kernel):
        raise ValueError('BootShim ARM64 image_size must describe the full appended FD payload')
    if PAGE + padded(len(kernel)) + padded(len(ramdisk)) > 201326592:
        raise ValueError('candidate exceeds captured boot partition size')
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, '-B', str(base / 'mkbootimg.py'), '--header_version', '3',
               '--kernel', str(kernel_path), '--ramdisk', str(ramdisk_path), '--output', str(output)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if result.returncode: raise ValueError(result.stderr)
    data = output.read_bytes(); report = verify(data, kernel, ramdisk)
    # Independent official unpacker, with outputs kept inside this task.
    unpack = output.parent / (output.name + '.unpacked')
    result = subprocess.run([sys.executable, '-B', str(base / 'unpack_bootimg.py'), '--boot_img', str(output),
                             '--out', str(unpack)], capture_output=True, text=True, timeout=60)
    if result.returncode: raise ValueError(result.stderr)
    if (unpack / 'kernel').read_bytes() != kernel: raise ValueError('AOSP kernel roundtrip mismatch')
    if ramdisk and (unpack / 'ramdisk').read_bytes() != ramdisk: raise ValueError('AOSP ramdisk roundtrip mismatch')
    report.update({'image_sha256': digest(data), 'image_bytes': len(data), 'fixture_only': fixture,
                   'hardware_ready': False, 'aosp_commit': lock['commit'],
                   'vendor_boot_policy': 'retain captured stock v3 vendor_boot; no DTB append or vendor_boot rewrite',
                   'unresolved': ['ABL acceptance of raw BootShim ARM64 entry', 'UEFI FD relocation/handoff',
                                  'GOP and vendor protocol runtime closure']})
    if hardware_review is not None: report['hardware_review'] = hardware_review
    if hardware_review in ('R-018','R-019','R-020','R-022'):
        from native_pixel_scope import scope_for_review
        SCOPE=scope_for_review(hardware_review)
        report['pixel_scope']=SCOPE
    output.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel', type=Path, required=True, help='raw ARM64 BootShim plus real UEFI FD')
    parser.add_argument('--ramdisk', type=Path, required=True, help='explicit input; may be an empty file')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hardware-review', choices=('R-005','R-017','R-017-MAP', 'R-017-READ', 'R-017-WARM','R-018','R-019','R-020','R-022'), help='tag a protected candidate; execution still checks the exact authorized image')
    args = parser.parse_args()
    report = package(args.kernel, args.ramdisk, args.output, hardware_review=args.hardware_review)
    print(f'PASS: boot v3 roundtrip, {report["image_bytes"]} bytes; hardware readiness not established')


if __name__ == '__main__': main()
