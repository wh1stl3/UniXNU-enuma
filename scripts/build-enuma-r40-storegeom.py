#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Rebuild only the r39 UFS snapshot and its BSD startup call site."""
import argparse
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / 'UniXNU'
parser_args = argparse.ArgumentParser()
parser_args.add_argument('--out', type=Path, default=device / 'out/ufs-sm8250-storegeom-20261123-r40')
out = parser_args.parse_args().out.resolve()
assert out.parent == (device / 'out').resolve() and not out.exists()

r39 = device / 'out/ufs-sm8250-launchd-aksid-20261123-r39'
r34 = device / 'out/ufs-sm8250-launchd-ipc-20261123-r34'
r10 = device / 'out/ufs-sm8250-launchd-display-20261121-r10/self-check/build-final'
r11 = device / 'out/ufs-sm8250-launchd-keystore-20261121-r11/self-check/build-final'
r21 = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check/build-final'
ufs = device / 'out/ufs-sm8250-startroot-wip-20261118/self-check/resume-20261118-r11'
ram = device / 'out/ufs-sm8250-startroot-mode0-20261118-r1/self-check/ram-merged'
fragment = device / 'package/EnumaStoreGeometry.inc'
helpers = runpy.run_path(str(device / 'scripts/build-enuma-r23-hid-standin.py'))
h = helpers['R']
digest, snapshot, read_member, fat_tree = (h[k] for k in ('digest', 'snapshot', 'read_member', 'fat_tree'))
pin = helpers['BASE_PIN']
assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == pin

names = ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img')
r39_manifest = json.loads((r39 / 'candidate-manifest.json').read_text())
for name in names:
    assert digest(r39 / name) == r39_manifest[name]['new'], name
frozen_files = [r39 / n for n in (*names, 'link.filelist', 'native-link.map', 'boot.json', 'candidate-manifest.json')]
frozen = snapshot(frozen_files)

steps = {s['tag']: s for s in json.loads((r21 / 'kernel-build-result.json').read_text())['r13_delta']['steps']}
bsd = next(s for s in json.loads((r11 / 'kernel-build-result.json').read_text())['r11_delta']['steps']
           if s['tag'] == 'compile-bsd')
ufs_result = json.loads((ufs / 'result.json').read_text())
compile_ufs = next(s for s in ufs_result['commands'] if s['tag'] == 'compile-target-arm64')
tree = Path(steps['link']['cwd']).parents[3]
sys.path.insert(0, str(base / 'scripts'))
from unixnu.kernel import linux_env
from unixnu import bootimg, payload as payload_step
from unixnu.cli import parser
from unixnu.config import Context

for name in ('objects', 'logs', 'tmp', 'source'):
    (out / name).mkdir(parents=True)
env = {**os.environ, **linux_env(SimpleNamespace(tree=tree)), 'PYTHONDONTWRITEBYTECODE': '1',
       'TMPDIR': str(out / 'tmp')}
env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
commands = {}


def call(tag, argv, cwd=out):
    argv = list(map(str, argv))
    p = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    commands[tag] = dict(argv=argv, cwd=str(cwd), exit=p.returncode)
    (out / 'logs' / (tag + '.log')).write_text(p.stdout)
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if p.returncode:
        print(p.stdout, file=sys.stderr)
        raise SystemExit(f'{tag}: exit {p.returncode}')
    print(tag, flush=True)
    return p.stdout


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


old_native = Path(compile_ufs['argv'][2])
old_bsd = Path(bsd['argv'][2])
assert digest(old_native) == '6ee5fb866c9bcdc5b1c50268ede8dc86f3eef1526c3784b3e8f0664da27ccb69'
assert digest(old_bsd) == '24a21ca6875a56f4e9292221b9e3ab624a7cb49d15ca0ecca0ba8932f8459fbe'
native_source = out / 'source/NativeUfs.cpp'
bsd_source = out / 'source/bsd_init.c'
native_text = old_native.read_text()
old_reserve = '''static uint64_t reserveBlocks (void)
{
  static int64_t cached = -1;
  if (cached < 0) {
    uint32_t mib = kDefaultReserveMiB;
    if (!PE_parse_boot_argn ("sheng-log-reserve", &mib, sizeof (mib)) || mib > 16384) mib = kDefaultReserveMiB;
    cached = static_cast<int64_t> (mib) * 256;   // 4096-byte blocks
  }
  return static_cast<uint64_t> (cached);
}'''
new_reserve = '''static uint64_t readReserveBlocks (void)
{
  uint32_t mib = kDefaultReserveMiB;
  if (!PE_parse_boot_argn ("sheng-log-reserve", &mib, sizeof (mib)) || mib > 16384) mib = kDefaultReserveMiB;
  return static_cast<uint64_t> (mib) * 256;   // 4096-byte blocks
}

static uint64_t reserveBlocks (void)
{
  static int64_t cached = -1;
  if (cached < 0) cached = static_cast<int64_t> (readReserveBlocks ());
  return static_cast<uint64_t> (cached);
}'''
native_text = replace_once(native_text, old_reserve, new_reserve)
anchor = 'extern "C" unsigned native_ufs_store_mode (void) { return storeMode (); }'
native_text = replace_once(native_text, '#if !NATIVE_UFS_EXTERNAL_STORE_PROVIDER\n' + anchor,
                           '#include "EnumaStoreGeometry.inc"\n\n#if !NATIVE_UFS_EXTERNAL_STORE_PROVIDER\n' + anchor)
native_text = replace_once(native_text, '  native_ufs_root_step = 3;',
                           '  enumaStoreGeometryCapture (*layout);\n  native_ufs_root_step = 3;')
native_source.write_text(native_text)
bsd_text = old_bsd.read_text()
seq_anchor = '\tabsolutetime_to_nanoseconds(mach_absolute_time(), &abstime_ns);'
assert bsd_text.count(seq_anchor) == 2
bsd_text = replace_once(bsd_text, '\t\treturn;\n\t}\n\n' + seq_anchor,
                        '\t\treturn;\n\t}\n\n\textern void enuma_storegeom_report(void);\n'
                        '\tenuma_storegeom_report();\n' + seq_anchor)
bsd_source.write_text(bsd_text)

old_archive = r10 / 'libShengUfs.a'
assert digest(old_archive) == ufs_result['artifacts']['libShengUfs.a']['sha256']
old_ufs_obj = ufs / 'NativeUfs.o'
assert digest(old_ufs_obj) == ufs_result['artifacts']['NativeUfs.o']['sha256']
old_bsd_obj = Path(bsd['argv'][4])
ufs_obj = out / 'objects/NativeUfs.o'
bsd_obj = out / 'objects/bsd_init.o'
for tag, step, source, obj, extra in (
    ('compile-ufs', compile_ufs, native_source, ufs_obj, ['-I', fragment.parent, '-I', ram]),
    ('compile-bsd', bsd, bsd_source, bsd_obj, []),
):
    argv = step['argv'].copy()
    argv[2], argv[4] = source, obj
    call(tag, argv + extra, step['cwd'])
assert digest(ufs_obj) != digest(old_ufs_obj) and digest(bsd_obj) != digest(old_bsd_obj)

archive = out / 'objects/libShengUfs.a'
members = call('old-ufs-members', ['llvm-ar', 't', old_archive]).splitlines()
assert members.count(ufs_obj.name) == 1 and len(members) == len(set(members))


def member(ar, name):
    return subprocess.check_output(['llvm-ar', 'p', ar, name], env=env)


assert member(old_archive, ufs_obj.name) == old_ufs_obj.read_bytes()
shutil.copyfile(old_archive, archive)
call('archive-ufs', ['llvm-ar', 'rD', archive, ufs_obj])
assert call('new-ufs-members', ['llvm-ar', 't', archive]).splitlines() == members
assert [n for n in members if member(old_archive, n) != member(archive, n)] == [ufs_obj.name]
assert member(archive, ufs_obj.name) == ufs_obj.read_bytes()

paths = [Path(x) for x in (r39 / 'link.filelist').read_text().splitlines()]
assert paths.count(old_bsd_obj) == 1
(out / 'link.filelist').write_text(''.join(f'{bsd_obj if p == old_bsd_obj else p}\n' for p in paths))
origin = Path(steps['prelink']['cwd'])
old_key = r11 / 'libAppleKeyStoreState.a'
old_display = r10 / 'display/libEnumaGopLegacy.a'
new_key = r39 / 'objects/libAppleKeyStoreState.a'
new_display = r34 / 'objects/libEnumaGopLegacy.a'
hid = device / 'out/ufs-sm8250-launchd-hid-20261122-r23/objects/libShengHidInputStandin.a'
watch = helpers['R19'] / 'objects/libEnumaBootWatchdogPolicy.a'
link_args = steps['link']['argv'].copy()
for old, new in ((old_key, new_key), (old_display, new_display)):
    assert sum(str(old) in a for a in link_args) == 1
    link_args = [a.replace(str(old), str(new)) for a in link_args]
link_args += [f'-Wl,-force_load,{p}' for p in (watch, hid)]
direct_archives = sorted({Path(a.rsplit(',', 1)[-1]) for a in link_args if a.endswith('.a')})
assert old_archive in direct_archives
donor = Path(steps['prelink']['argv'][steps['prelink']['argv'].index('--prelinked') + 1])
immutable_inputs = [*paths, *direct_archives, donor, old_native, old_bsd, fragment]
inputs = snapshot(immutable_inputs)

for tag in ('link', 'prelink'):
    step = steps[tag]
    argv = (link_args if tag == 'link' else step['argv']).copy()
    for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
        argv = [a.replace(str(origin / name), str(out / name)) for a in argv]
    if tag == 'link':
        assert sum(str(old_archive) in a for a in argv) == 1
        argv = [a.replace(str(old_archive), str(archive)) for a in argv]
    call(tag, argv, out if tag == 'prelink' else step['cwd'])

formats = re.findall(r'"(enuma-sg: [^"]+)"', fragment.read_text())
assert formats and len(formats) == len(set(formats))
callees = {}
for name in ('native.macho', 'prelink.macho'):
    path = out / name
    assert not call('undefined-' + name, ['llvm-nm', '-u', path]).strip()
    blob = path.read_bytes()
    assert all(blob.count(s.replace(r'\n', '\n').encode() + b'\0') == 1 for s in formats)
    _, syms = helpers['symbols'](blob, helpers['macho'](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    caller = call('call-' + name, ['llvm-objdump', '-d', '--disassemble-symbols=_bsdinit_task', path])
    assert caller.count('<_enuma_storegeom_report>') == 1
    assert caller.index('<_enuma_storegeom_report>') < caller.index('<_load_init_program>')
    report = call('report-' + name, ['llvm-objdump', '-d', '--disassemble-symbols=_enuma_storegeom_report', path])
    assert not re.search(r'\bblr?\s+x\d+', report)
    targets = set(re.findall(r'\bb(?:l)?\s+0x[0-9a-f]+\s+<([^>]+)>', report))
    callees[name] = sorted(t for t in targets if not t.startswith('_enuma_storegeom_report+'))
    assert set(callees[name]) == {'_printf', '_PE_parse_boot_argn'}, callees[name]

shutil.copytree(r39 / 'device', out / 'device')
shutil.copyfile(r39 / 'kernel.macho.adt', out / 'kernel.macho.adt')
shutil.copyfile(r39 / 'payload.img', out / 'payload.img')
os.utime(out / 'prelink.macho', (payload_step.EPOCH, payload_step.EPOCH))
call('replace-kernel', ['env', 'MTOOLS_SKIP_CHECK=1', 'TZ=UTC', 'mcopy', '-o', '-m',
                        '-i', out / 'payload.img', out / 'prelink.macho', '::/EFI/UniXNU/Payloads/kernel.macho'])
old_tree = fat_tree(r39 / 'payload.img')
assert fat_tree(out / 'payload.img') == old_tree
files = [x.removeprefix('::/EFI/UniXNU/') for x in old_tree if not x.endswith('/')]
changed = [n for n in files if read_member(r39 / 'payload.img', n) != read_member(out / 'payload.img', n)]
assert changed == ['Payloads/kernel.macho'], changed
assert read_member(out / 'payload.img', 'Payloads/kernel.macho') == (out / 'prelink.macho').read_bytes()
assert read_member(out / 'payload.img', 'Payloads/kernel.macho.adt') == (r39 / 'kernel.macho.adt').read_bytes()
local = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging/local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(device.parent / 'UniXNU-sm8250-common')]))
uefi = device.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
reference = json.loads((r39 / 'boot.json').read_text())
assert digest(fd) == reference['fd_sha256'] and digest(dtb) == reference['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, out / 'payload.img', out / 'boot.img')
assert snapshot(frozen_files) == frozen and snapshot(immutable_inputs) == inputs
assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == pin


def delta(old, new):
    return {'old': digest(old), 'new': digest(new), 'bytes': new.stat().st_size,
            'delta_bytes': new.stat().st_size - old.stat().st_size}


results = {n: delta(r39 / n, out / n) for n in names}
results.update(objects={a.name: delta(a, b) for a, b in
                        ((old_ufs_obj, ufs_obj), (old_bsd_obj, bsd_obj), (old_archive, archive))},
               unchanged_filelist_inputs=len(set(paths)) - 1, unchanged_direct_archives=len(direct_archives) - 1,
               archive_members=members, changed_payload_members=changed,
               formats=formats, report_callees=callees, zero_undefined=True, frozen=frozen,
               boot_metadata=json.loads((out / 'boot.json').read_text()))
(out / 'candidate-manifest.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
