#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Add an OSFMK snapshot unit and rebuild r55's BP caller, then relink and repack."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tomllib
from types import SimpleNamespace

sys.dont_write_bytecode = True
parser_args = argparse.ArgumentParser(description=__doc__)
parser_args.add_argument('--r56', action='store_true', required=True)
parser_args.add_argument('--out', type=Path)
opts = parser_args.parse_args()
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / 'UniXNU'
r54 = device / 'out/ufs-sm8250-fbfill3-20261123-r54'
r55 = device / 'out/ufs-sm8250-dk0-20261123-r55'
out = (opts.out or device / 'out/ufs-sm8250-thsnap-20261123-r56').resolve()
assert out.parent == device / 'out' and not out.exists(), out
helpers = runpy.run_path(str(device / 'scripts/build-enuma-r23-hid-standin.py'))
digest, snapshot, read_member, fat_tree = (helpers['R'][k] for k in
                                           ('digest', 'snapshot', 'read_member', 'fat_tree'))
pin = helpers['BASE_PIN']


def check_pin():
    assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'], text=True).strip() == pin


check_pin()
names = ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img')
prior = json.loads((r55 / 'candidate-manifest.json').read_text())
before = {n: digest(r55 / n) for n in names}
assert before == prior['after']
assert before['boot.img'] == 'e288d0f1759769b945c6fa347e52a546cbd0010e0979a95a76f35b9e1f863b01'
record = json.loads((r54 / 'candidate-manifest.json').read_text())
assert all(before[n] == record['after'][n] for n in names[:3])
recipe = json.loads((r54 / 'commands.json').read_text())
paths = [Path(x) for x in (r54 / 'link.filelist').read_text().splitlines()]
old_obj, = (p for p in paths if p.name == 'kern_exec.o')
assert old_obj == r54 / 'objects/kern_exec.o'
archives = sorted({Path(a.rsplit(',', 1)[-1]) for a in recipe['link']['argv'] if a.endswith('.a')})
preargs = recipe['prelink']['argv']
donor = Path(preargs[preargs.index('--prelinked') + 1])
inputs = snapshot([*paths, *archives, donor])
for p in paths:
    key = str(p)
    if p.parent == r54 / 'objects':
        assert inputs[key] == record['objects'][p.name][1], p
    else:
        assert inputs[key] == record['unchanged_inputs'][key], p
for p in [*archives, donor]:
    assert inputs[str(p)] == record['unchanged_inputs'][str(p)], p

sys.path.insert(0, str(base / 'scripts'))
from unixnu import bootimg, payload as payload_step
from unixnu.cli import parser
from unixnu.config import Context
from unixnu.kernel import linux_env

out.mkdir()
for d in ('objects', 'logs', 'tmp'):
    (out / d).mkdir()
tree = Path(recipe['link']['cwd']).parents[3]
env = {**os.environ, **linux_env(SimpleNamespace(tree=tree)), 'PYTHONDONTWRITEBYTECODE': '1',
       'TMPDIR': str(out / 'tmp')}
env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
commands = {}


def call(tag, argv, cwd=out):
    argv = list(map(str, argv))
    p = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    commands[tag] = dict(argv=argv, cwd=str(cwd), exit=p.returncode)
    (out / 'logs' / (tag + '.log')).write_text(p.stdout)
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if p.returncode:
        print(p.stdout, file=sys.stderr)
        raise SystemExit(f'{tag}: exit {p.returncode}')
    print(tag, flush=True)
    return p.stdout


source = out / 'source/bsd/kern'
shutil.copytree(r54 / 'source/bsd/kern', source)
bridge = 'EnumaThreadSnapshot56Bsd.inc'
shutil.copyfile(device / 'package' / bridge, source / bridge)
bp = source / 'EnumaBootProgress2.inc'
text = bp.read_text()
for old, new in (
    ('enum { ENUMA_BP_INTERVAL', f'#include "{bridge}"\n'
     'enum { ENUMA_TH_TICK = 2 };\nenum { ENUMA_BP_INTERVAL'),
    ('__unused thread_call_param_t arg', 'thread_call_param_t snapshot_call'),
    ('\tenuma_bp_print(idx);\n', '\tenuma_bp_print(idx);\n'
     '\tif (idx == ENUMA_TH_TICK && snapshot_call != NULL) {\n'
     '\t\tthread_call_enter1(snapshot_call, snapshot_call);\n\t}\n'),
    ('\tenuma_bp_print(0);\n', '\tenuma_bp_print(0);\n'
     '\tthread_call_t snapshot_call = enuma_th_alloc(ENUMA_TH_TICK);\n'),
    ('\t    NULL, THREAD_CALL_PRIORITY_KERNEL', '\t    snapshot_call, THREAD_CALL_PRIORITY_KERNEL'),
    ('\t\tthread_call_enter1_delayed(call, call, deadline);\n\t}',
     '\t\tthread_call_enter1_delayed(call, call, deadline);\n'
     '\t} else if (snapshot_call != NULL) {\n\t\tthread_call_free(snapshot_call);\n\t}'),
):
    assert text.count(old) == 1, old
    text = text.replace(old, new)
bp.write_text(text)
obj = out / 'objects/kern_exec.o'
step = recipe['compile-kern_exec.o']
argv = step['argv'].copy()
assert argv[2:5] == [str(r54 / 'source/bsd/kern/kern_exec.c'), '-o', str(old_obj)]
argv[2], argv[4] = source / 'kern_exec.c', obj
if '-MF' in argv:
    argv[argv.index('-MF') + 1] = obj.with_suffix('.d')
call('compile-kern_exec.o', argv, step['cwd'])
assert digest(obj) != inputs[str(old_obj)]
snap_src = device / 'package/EnumaThreadSnapshot56.c'
snap_obj = out / 'objects/EnumaThreadSnapshot56.o'
task_obj, = (p for p in paths if p.name == 'task.o')
task_recipe = json.loads(task_obj.with_suffix('.o.json').read_text().strip().removesuffix(','))
argv = task_recipe['arguments'].copy()
assert 'MACH_KERNEL_PRIVATE' in argv and argv[3:5] == ['-o', 'task.o']
argv[2], argv[4] = snap_src, snap_obj
call('compile-EnumaThreadSnapshot56.o', argv, task_recipe['directory'])
(out / 'link.filelist').write_text(''.join(f'{obj if p == old_obj else p}\n' for p in paths) +
                                  f'{snap_obj}\n')
for tag in ('link', 'prelink'):
    step = recipe[tag]
    argv = [a.replace(str(r54), str(out)) for a in step['argv']]
    call(tag, argv, out if tag == 'prelink' else step['cwd'])

formats = (
    b'enuma-th: tick=%u t=%llu slide=%s saved=possibly-stale/non-atomic\n\0',
    b'enuma-th: p=%d n=%d shown=%u\n\0',
    b'enuma-th: p=%d n=NA shown=0 why=%s\n\0',
    b'enuma-th: %d/%llu st=0x%x we=0x%llx ct=NA pc=%s lr=%s\n\0',
    b'enuma-th: %d/%llu st=NA we=NA ct=NA pc=NA lr=NA why=busy\n\0',
    b'enuma-th\0',
)
for name in ('native.macho', 'prelink.macho'):
    p = out / name
    assert not call('undefined-' + name, ['llvm-nm', '-u', p]).strip()
    blob = p.read_bytes()
    _, syms = helpers['symbols'](blob, helpers['macho'](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    assert all(blob.count(s) == 1 for s in formats), name
    del blob
    symbols = ('_enuma_bp_start', '_enuma_bp_repeat', '_enuma_th_worker',
               '_enuma_th_capture', '_enuma_th_task_ref', '_enuma_th_alloc')
    report = call('calls-' + name, ['llvm-objdump', '-d',
        '--disassemble-symbols=' + ','.join(symbols), p])
    for symbol in symbols:
        assert f'<{symbol}>:' in report, (name, symbol)
    assert len(re.findall(r'\bbl\b.*<_thread_call_enter1>', report)) == 1, name
    assert len(re.findall(r'\bbl\b.*<_proc_find>', report)) == 1, name
    assert 'thread_get_state' not in report, name

shutil.copytree(r55 / 'device', out / 'device')
shutil.copyfile(r55 / 'kernel.macho.adt', out / 'kernel.macho.adt')
shutil.copyfile(r55 / 'payload.img', out / 'payload.img')
old = read_member(r55 / 'payload.img', 'unixnu.toml')
needle = b'"\n[[entry]]\nid = "reset"'
assert old.count(needle) == 1
config = out / 'unixnu.toml'
config.write_bytes(old.replace(needle, b' enuma-th=1' + needle))
for src, member in ((out / 'prelink.macho', 'Payloads/kernel.macho'), (config, 'unixnu.toml')):
    os.utime(src, (payload_step.EPOCH, payload_step.EPOCH))
    call('replace-' + src.name, ['env', 'MTOOLS_SKIP_CHECK=1', 'TZ=UTC', 'mcopy', '-o', '-m',
         '-i', out / 'payload.img', src, '::/EFI/UniXNU/' + member])
tree = fat_tree(r55 / 'payload.img')
assert fat_tree(out / 'payload.img') == tree
members = [p.removeprefix('::/EFI/UniXNU/') for p in tree if not p.endswith('/')]
new_members = {n: hashlib.sha256(read_member(out / 'payload.img', n)).hexdigest() for n in members}
changed = sorted(n for n in members if new_members[n] != prior['payload_members_after'][n])
assert changed == ['Payloads/kernel.macho', 'unixnu.toml']
assert new_members['Payloads/kernel.macho'] == digest(out / 'prelink.macho')
assert read_member(out / 'payload.img', 'Payloads/kernel.macho.adt') == (r55 / 'kernel.macho.adt').read_bytes()

local = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging/local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(device.parent / 'UniXNU-sm8250-common')]))
uefi = device.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
ref = json.loads((r55 / 'boot.json').read_text())
assert digest(fd) == ref['fd_sha256'] and digest(dtb) == ref['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, out / 'payload.img', out / 'boot.img')
offset = prior['boot_payload_offset']
with (r55 / 'boot.img').open('rb') as a, (out / 'boot.img').open('rb') as b:
    x, y = a.read(offset), b.read(offset)
    assert x[:576] == y[:576] and x[596:] == y[596:]
    assert hashlib.file_digest(a, 'sha256').hexdigest() == before['payload.img']
    with (out / 'tmp/boot-payload.img').open('wb') as extracted:
        shutil.copyfileobj(b, extracted)
embedded = out / 'tmp/boot-payload.img'
assert digest(embedded) == digest(out / 'payload.img')
readback = read_member(embedded, 'unixnu.toml')
assert readback == config.read_bytes()
args = next(e['args'] for e in tomllib.loads(readback.decode())['entry'] if e['id'] == 'xnu')
assert args == prior['args_after'] + ' enuma-th=1'
embedded.unlink()
assert {n: digest(r55 / n) for n in names} == before
assert snapshot([*paths, *archives, donor]) == inputs
check_pin()

result = dict(before=before, after={n: digest(out / n) for n in names},
              sizes={n: (out / n).stat().st_size for n in names},
              deltas={n: (out / n).stat().st_size - (r55 / n).stat().st_size for n in names},
              args=args, objects={'kern_exec.o': [inputs[str(old_obj)], digest(obj)],
                                  snap_obj.name: [None, digest(snap_obj)]},
              unchanged_filelist_inputs=len(paths) - 1, unchanged_direct_archives=len(archives),
              changed_payload_members=changed, payload_members_after=new_members,
              boot_payload_offset=offset, zero_undefined_including_weak=True,
              unique_formats=True, single_submit_callsite=True,
              submit_site_line=text[:text.index('thread_call_enter1(snapshot_call,')].count('\n') + 1)
(out / 'candidate-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
