#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Repackage frozen enuma r21 with a newly generated ADT, without relinking."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tomllib

DEVICE = Path(__file__).resolve().parents[1]
BASE = DEVICE.parents[1] / 'UniXNU'
BASE_PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'
R21 = DEVICE / 'out/ufs-sm8250-launchd-keystore-20261122-r21'
R6_ADT = DEVICE / 'out/ufs-sm8250-launchd-display-20261119-r6/self-check/extracted/kernel.macho.adt'
NEW = DEVICE / 'out/ufs-sm8250-launchd-keystore-20261122-r22'
SIZE_KEY = ('device-tree', 'chosen', 'darwinboot-memory-size')
SEED_KEY = ('device-tree', 'chosen', 'random-seed')
SLEEP_KEY = ('device-tree', 'defaults', 'sleep-disabled')
MEMBERS = ('Payloads/kernel.macho', 'Payloads/kernel.macho.adt',
           'Payloads/kernel.macho.trustcache', 'Payloads/scratch-data.img', 'unixnu.toml')
ADT = MEMBERS[1]
R21_PINS = {
    'boot.img': 'cb02ded1039189582dfb1458a218068c93cdcee152151b4708353d0c2320c23f',
    'payload.img': '546ba82a1e7ae2b1427f76c86d91ec84df109345bf7019c41166364d7fcf03de',
    'self-check/build-final/native.macho': 'b505a024c6f8d226826ad56a6c6c0cec8884dc352c8b3f99dfd4e336adc6c28f',
    'self-check/build-final/prelink.macho': '5c24e268ad59309c08629e6b3a5a770386b364ae072e61052fa7581c02f887bd',
}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_properties(blob):
    # Same serialized ADT layout as the r21 packager; keep path and raw value.
    properties = {}

    def walk(pos, parent):
        count, children = struct.unpack_from('<II', blob, pos)
        pos += 8
        props = {}
        for _ in range(count):
            key, size = struct.unpack_from('<32sI', blob, pos)
            key = key.rstrip(b'\0').decode()
            pos += 36
            assert key not in props and pos + size <= len(blob)
            props[key] = (pos, pos + size)
            pos += (size + 3) & ~3
        start, end = props['name']
        node = (*parent, blob[start:end].rstrip(b'\0').decode())
        for key, span in props.items():
            full_key = (*node, key)
            assert full_key not in properties
            properties[full_key] = blob[slice(*span)]
        for _ in range(children):
            pos = walk(pos, node)
        return pos

    assert walk(0, ()) == len(blob)
    return properties


def read_member(image, member):
    return subprocess.check_output(['mtype', '-i', image, '::/EFI/UniXNU/' + member])


def fat_tree(image):
    return set(subprocess.check_output(['mdir', '-b', '-/', '-i', image, '::/'], text=True).splitlines())


def snapshot(paths):
    return {str(path): digest(path) for path in sorted(set(paths))}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=NEW, help='fresh directory inside device out/')
    ap.add_argument('--dtb', type=Path, required=True, help='r21 Android boot DTB (not the ADT input)')
    args = ap.parse_args()
    out = args.out.resolve()
    assert (DEVICE / 'out') in out.parents and R21 not in out.parents and not out.exists()
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == BASE_PIN
    for rel, sha in R21_PINS.items():
        assert digest(R21 / rel) == sha, f'r21 pin mismatch: {rel}'

    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu import bootimg, devicetree, payload as payload_step
    from unixnu.cli import parser
    from unixnu.config import Context

    pkg = R21 / 'self-check-package/packaging'
    board = pkg / 'device/board.toml'
    hardware = pkg / 'out/enuma/ipados-17.7.11-21H461/enuma/device-tree/hardware.dtb'
    local = pkg / 'local-build.toml'
    uefi = DEVICE.parent / 'uefi-enuma'
    fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
    boot_ref = json.loads((R21 / 'self-check-package/boot.json').read_text())
    assert digest(fd) == boot_ref['fd_sha256'] and digest(args.dtb) == boot_ref['dtb_sha256']
    build = R21 / 'self-check/build-final'
    filelist = build / 'link.filelist'
    objects = snapshot([Path(line) for line in filelist.read_text().splitlines()]
                       + [p for p in (build / 'objects').iterdir() if p.is_file()])
    frozen = snapshot([*(R21 / rel for rel in R21_PINS), R21 / 'candidate-manifest.json',
                       R21 / 'run_packaging.py', R21 / 'r7-payload-wrapper.py',
                       board, hardware, local, filelist, R6_ADT, fd, args.dtb])
    payload_old = R21 / 'payload.img'
    tree = fat_tree(payload_old)
    assert {entry for entry in tree if not entry.endswith('/')} == {
        '::/EFI/UniXNU/' + name for name in MEMBERS}
    old = {name: read_member(payload_old, name) for name in MEMBERS}
    assert old[ADT] == R6_ADT.read_bytes()
    assert hashlib.sha256(old[MEMBERS[0]]).hexdigest() == R21_PINS['self-check/build-final/prelink.macho']
    t = tomllib.loads((DEVICE / 'board.toml').read_text(encoding='utf-8'))
    assert t['payload']['adt']['owned_memory_size'] == '0xaa000000'
    assert t['adt']['defaults']['u32']['sleep-disabled'] == 1
    text = board.read_bytes()
    line = b'owned_memory_size = "0x20000000"'
    defaults = b'[adt.defaults.u32]\n'
    assert text.count(line) == 1
    assert text.count(defaults) == 1

    out.mkdir()
    candidate_board = out / 'device'
    candidate_board.mkdir()
    (candidate_board / 'board.toml').write_bytes(
        text.replace(line, b'owned_memory_size = "0xaa000000"')
        .replace(defaults, defaults + b'sleep-disabled = 1\n'))
    ctx = Context(parser().parse_args([
        'bootimg', '-D', str(candidate_board), '--out', str(out / 'work'), '--config', str(local),
        '--local-module', 'soc:sm8250=' + str(DEVICE.parent / 'UniXNU-sm8250-common'),
    ]))
    seed = tomllib.loads(local.read_text())['build']['unique_chip_id']
    adt = devicetree.generate(hardware, ctx.board, unique_chip_id=seed, data=True, trust=True)
    before, after = read_properties(old[ADT]), read_properties(adt)
    assert before[SIZE_KEY] == struct.pack('<Q', 0x20000000)
    assert SLEEP_KEY not in before and after[SLEEP_KEY] == struct.pack('<I', 1)
    assert len(after[SEED_KEY]) == 256 and before[SEED_KEY] != after[SEED_KEY]
    assert after == (before | {SIZE_KEY: struct.pack('<Q', 0xaa000000),
                               SLEEP_KEY: struct.pack('<I', 1), SEED_KEY: after[SEED_KEY]})
    adt_path = out / 'kernel.macho.adt'
    adt_path.write_bytes(adt)
    os.utime(adt_path, (payload_step.EPOCH, payload_step.EPOCH))

    # The ADT grew by one property. Let the same mtools used by r21 update
    # its directory entry and allocation, without rewriting the other files.
    payload = out / 'payload.img'
    shutil.copyfile(payload_old, payload)
    subprocess.run(['mcopy', '-o', '-m', '-i', payload, adt_path, '::/EFI/UniXNU/' + ADT],
                   check=True, env=dict(os.environ, MTOOLS_SKIP_CHECK='1', TZ='UTC'))
    assert payload.stat().st_size == payload_old.stat().st_size
    assert fat_tree(payload) == tree
    final = {name: read_member(payload, name) for name in MEMBERS}
    readback = read_properties(final[ADT])
    assert readback[SIZE_KEY] == struct.pack('<Q', 0xaa000000), 'payload ADT size read-back'
    assert readback[SLEEP_KEY] == struct.pack('<I', 1), 'payload ADT sleep-disabled read-back'
    assert final == (old | {ADT: adt})

    boot = out / 'boot.img'
    bootimg.build(ctx, uefi, fd, args.dtb, payload, boot)
    new_boot = boot.read_bytes()
    old_boot = (R21 / 'boot.img').read_bytes()
    kernel_bytes, _ = struct.unpack_from('<II', old_boot, 8)
    page_size, version = struct.unpack_from('<II', old_boot, 36)
    assert (page_size, version) == (4096, 1)
    ramdisk = page_size * (1 + (kernel_bytes + page_size - 1) // page_size)
    assert old_boot[ramdisk:] == payload_old.read_bytes() and new_boot[ramdisk:] == payload.read_bytes()
    # Android header v1: 48-byte fixed header + 16-byte name + 512-byte cmdline.
    id_start, id_end = 576, 596  # only the SHA-1, not the padding in the 32-byte ID field
    assert new_boot[:id_start] == old_boot[:id_start]
    assert new_boot[id_start:id_end] != old_boot[id_start:id_end]
    assert new_boot[id_end:ramdisk] == old_boot[id_end:ramdisk]
    assert len(new_boot) <= int(t['package']['boot_partition_bytes'])

    assert frozen == snapshot(map(Path, frozen)), 'frozen r21 inputs changed'
    assert objects == snapshot(map(Path, objects)), 'r21 link input changed'
    (out / 'r21-link-inputs.sha256').write_text(''.join(f'{sha}  {path}\n' for path, sha in objects.items()))
    result = {
        'status': 'self-checked; host only',
        'base': BASE_PIN,
        'r6_r21_adt_sha256': hashlib.sha256(old[ADT]).hexdigest(),
        'memory_size_from_payload': hex(struct.unpack('<Q', readback[SIZE_KEY])[0]),
        'sleep_disabled_from_payload': struct.unpack('<I', readback[SLEEP_KEY])[0],
        'boot_payload_offset': ramdisk,
        'changed_adt_properties': ['/chosen/darwinboot-memory-size', '/defaults/sleep-disabled',
                                   '/chosen/random-seed'],
        'r21_pins_unchanged': R21_PINS,
        'r21_link_inputs_unchanged': len(objects),
        'fat_members': {name: {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
                        for name, data in final.items()},
        'artifacts': {path.name: {'sha256': digest(path), 'bytes': path.stat().st_size}
                      for path in (payload, boot)},
    }
    report = json.dumps(result, indent=2) + '\n'
    (out / 'candidate-manifest.json').write_text(report)
    print(report, end='')


if __name__ == '__main__':
    main()
