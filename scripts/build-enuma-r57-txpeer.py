#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Rebuild the affected IPC diagnostic inputs, then relink and package r57 or r58."""
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
cli = argparse.ArgumentParser(description=__doc__)
mode = cli.add_mutually_exclusive_group(required=True)
mode.add_argument('--r57', action='store_true')
mode.add_argument('--r58', action='store_true')
cli.add_argument('--out', type=Path)
opts = cli.parse_args()
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / 'UniXNU'
r54 = device / 'out/ufs-sm8250-fbfill3-20261123-r54'
r56 = device / 'out/ufs-sm8250-thsnap-20261123-r56'
r57 = device / 'out/ufs-sm8250-txpeer-20261123-r57'
parent = r57 if opts.r58 else r56
out = (opts.out or (device / 'out/ufs-sm8250-rxpid-20261123-r58' if opts.r58 else r57)).resolve()
assert out.parent == device / 'out' and not out.exists(), out
helpers = runpy.run_path(str(device / 'scripts/build-enuma-r23-hid-standin.py'))
digest, snapshot, read_member, fat_tree = (helpers['R'][k] for k in
                                           ('digest', 'snapshot', 'read_member', 'fat_tree'))


def json_file(path):
    return json.loads(path.read_text())


def head(repo):
    return subprocess.check_output(['git', '-C', repo, 'rev-parse', 'HEAD'], text=True).strip()


def insert(text, anchor, new):
    assert text.count(anchor) == 1, anchor
    return text.replace(anchor, new)


assert head(base) == helpers['BASE_PIN']
names = ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img')
prior = json_file(parent / 'candidate-manifest.json')
before = {n: digest(parent / n) for n in names}
assert before == prior['after']
assert before['boot.img'] == ('e669e3bdf2f7f5315d9eb28e1231bdd02fe5f6245c2a961b88e0fa1ebf071169'
                              if opts.r58 else
                              'e22e05438d199d1feedcbcccdbf8248bb2402cf107196660c8745eb7cbcc58f8')
record = json_file(r54 / 'candidate-manifest.json')
r56_record = json_file(r56 / 'candidate-manifest.json') if opts.r58 else prior
recipe = json_file(parent / 'commands.json')
paths = [Path(x) for x in (parent / 'link.filelist').read_text().splitlines()]
arch = sorted({Path(a.rsplit(',', 1)[-1]) for a in recipe['link']['argv'] if a.endswith('.a')})
preargs = recipe['prelink']['argv']
donor = Path(preargs[preargs.index('--prelinked') + 1])
inputs = snapshot([*paths, *arch, donor])
for p in paths:
    if p.parent == parent / 'objects':
        expected = prior['objects'][p.name][1]
    elif p.parent == r56 / 'objects':
        expected = r56_record['objects'][p.name][1]
    elif p.parent == r54 / 'objects':
        expected = record['objects'][p.name][1]
    else:
        expected = record['unchanged_inputs'][str(p)]
    assert inputs[str(p)] == expected, p
for p in [*arch, donor]:
    assert inputs[str(p)] == record['unchanged_inputs'][str(p)], p

ipc_old, = (p for p in paths if p.name == 'ipc_kmsg.o')
snap_old, = (p for p in paths if p.name == 'EnumaThreadSnapshot56.o')
snap = recipe['compile-EnumaThreadSnapshot56.o']
assert snap['argv'][3:5] == ['-o', str(snap_old)]
if opts.r58:
    ipc = recipe['compile-ipc_kmsg.o']
    assert ipc['argv'][3:5] == ['-o', str(ipc_old)]
    ipc_argv, ipc_cwd = ipc['argv'].copy(), ipc['cwd']
    # The r57 compiler command names the isolated copy; recover its pinned original.
    r56_paths = (r56 / 'link.filelist').read_text().splitlines()
    ipc_base, = (Path(p) for p in r56_paths if Path(p).name == ipc_old.name)
else:
    ipc_base = ipc_old
ipc_original = json.loads(ipc_base.with_suffix('.o.json').read_text().strip().removesuffix(','))
assert ipc_original['arguments'][3:5] == ['-o', ipc_old.name]
if not opts.r58:
    ipc_argv, ipc_cwd = ipc_original['arguments'].copy(), ipc_original['directory']
original_ipc = Path(ipc_original['arguments'][2])
xnu = original_ipc.parents[2]
assert head(xnu) == 'd8b80295118ef25ac3a784134bcf95cd8e88109f'
assert digest(original_ipc) == 'da8a8bcec775123fabb3f4cb72952f9ba23497b2aa6cc223b64216656143c550'

sys.path.insert(0, str(base / 'scripts'))
from unixnu import bootimg, payload as payload_step
from unixnu.cli import parser
from unixnu.config import Context
from unixnu.kernel import linux_env

out.mkdir()
for sub in ('source', 'objects', 'logs', 'tmp'):
    (out / sub).mkdir()
tree = Path(recipe['link']['cwd']).parents[3]
env = {**os.environ, **linux_env(SimpleNamespace(tree=tree)), 'PYTHONDONTWRITEBYTECODE': '1',
       'TMPDIR': str(out / 'tmp')}
env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
commands = {}


def call(tag, argv, cwd=out):
    argv = list(map(str, argv))
    proc = subprocess.run(argv, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    commands[tag] = dict(argv=argv, cwd=str(cwd), exit=proc.returncode)
    (out / 'logs' / (tag + '.log')).write_text(proc.stdout)
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if proc.returncode:
        print(proc.stdout, file=sys.stderr)
        raise SystemExit(f'{tag}: exit {proc.returncode}')
    print(tag, flush=True)
    return proc.stdout


ipc_src = out / 'source/ipc_kmsg.c'
inc = 'EnumaTxPeer58.inc' if opts.r58 else 'EnumaTxPeer57.inc'
shutil.copyfile(device / 'package' / inc, ipc_src.with_name(inc))
anchor = 'static TUNABLE(bool, enforce_strict_reply, "ipc_strict_reply", false);'
ipc_text = insert(original_ipc.read_text(), anchor, f'{anchor}\n#include "{inc}"')
anchor = '\tipc_voucher_send_preprocessing(kmsg);\n\n\tport = hdr->msgh_remote_port;\n\tassert(IP_VALID(port));'
if opts.r58:
    anchor += '\n\tip_mq_lock(port);'
    ipc_text = insert(ipc_text, anchor, anchor.removesuffix('\n\tip_mq_lock(port);') + '''
	const int enuma_sender = __improbable(enuma_tx_enabled == 1) ? proc_selfpid() : -1;
	ip_mq_lock(port);
	if (__improbable(enuma_sender == 5 || enuma_sender == 34)) {
		enuma_tx_record(hdr, port, enuma_sender);
	}''')
else:
    ipc_text = insert(ipc_text, anchor, anchor + '''
	if (__improbable(enuma_tx_enabled == 1)) {
		enuma_tx_record(hdr, port);
	}''')
ipc_src.write_text(ipc_text)
compile_steps = [(ipc_old, ipc_src, ipc_argv, ipc_cwd)]
snap_text = Path(snap['argv'][2]).read_text()
if not opts.r58:
    snap_src = out / 'source/EnumaThreadSnapshot56.c'
    snap_text = insert(snap_text, 'enum { ENUMA_TH_CAP = 8 };',
                        'extern void enuma_tx_dump(void);\n\nenum { ENUMA_TH_CAP = 8 };')
    snap_text = insert(snap_text, '\tenuma_th_print(5, &sb);\n',
                        '\tenuma_th_print(5, &sb);\n\tenuma_tx_dump();\n')
    snap_src.write_text(snap_text)
    compile_steps.append((snap_old, snap_src, snap['argv'].copy(), snap['cwd']))

new_objs = {}
for old, src, argv, cwd in compile_steps:
    obj = new_objs[old] = out / 'objects' / old.name
    argv[2], argv[4] = src, obj
    if '-MF' in argv:
        argv[argv.index('-MF') + 1] = obj.with_suffix('.d')
    call('compile-' + old.name, argv, cwd)
    assert digest(obj) != inputs[str(old)], old

(out / 'link.filelist').write_text(''.join(f'{new_objs.get(p, p)}\n' for p in paths))
for tag in ('link', 'prelink'):
    step = recipe[tag]
    argv = [a.replace(str(parent), str(out)) for a in step['argv']]
    call(tag, argv, out if tag == 'prelink' else step['cwd'])

formats = ((b'enuma-tx: %d  id=0x%x port=0x%llx rxpid=%d\n\0',
            b'enuma-tx: %d  id=0x%x port=0x%llx rxpid=NA\n\0',
            b'enuma-tx: %d  id=NA port=NA rxpid=NA\n\0') if opts.r58 else
           (b'enuma-tx: %d  id=0x%x port=0x%llx owner=NA\n\0',
            b'enuma-tx: %d  id=NA port=NA owner=NA\n\0'))
formats += (b'enuma-txpeer\0', b'enuma-th\0')
symbols = ('_ipc_kmsg_send', '_enuma_tx_record', '_enuma_tx_dump', '_enuma_th_worker')
for name in ('native.macho', 'prelink.macho'):
    p = out / name
    assert not call('undefined-' + name, ['llvm-nm', '-u', p]).strip()
    blob = p.read_bytes()
    _, syms = helpers['symbols'](blob, helpers['macho'](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    assert all(blob.count(fmt) == 1 for fmt in formats), name
    del blob
    for symbol in symbols:
        asm = call('calls-' + name + '-' + symbol, ['llvm-objdump', '-d',
                   '--disassemble-symbols=' + symbol, p])
        assert f'<{symbol}>:' in asm, (name, symbol)
        targets = re.findall(r'\bbl\b[^\n]*<(_[^>]+)>', asm)
        if symbol == '_ipc_kmsg_send':
            assert targets.count('_enuma_tx_record') == 1
        elif symbol == '_enuma_th_worker':
            assert targets.count('_enuma_tx_dump') == 1
        elif symbol == '_enuma_tx_record':
            if opts.r58:
                assert targets == ['_ipc_port_get_receiver_task_locked'], targets
            else:
                assert targets == ['_proc_selfpid']
            assert re.search(r'\b(?:casp\w*|stl?xp)\b', asm), name

shutil.copytree(parent / 'device', out / 'device')
shutil.copyfile(parent / 'kernel.macho.adt', out / 'kernel.macho.adt')
assert (out / 'kernel.macho.adt').read_bytes() == (parent / 'kernel.macho.adt').read_bytes()
shutil.copyfile(parent / 'payload.img', out / 'payload.img')
arg = '' if opts.r58 else ' enuma-txpeer=1'
needle = b'"\n[[entry]]\nid = "reset"'
config = out / 'unixnu.toml'
config.write_bytes(insert(read_member(parent / 'payload.img', 'unixnu.toml'), needle, arg.encode() + needle))
replace = [(out / 'prelink.macho', 'Payloads/kernel.macho')]
if not opts.r58:
    replace.append((config, 'unixnu.toml'))
for src, member in replace:
    os.utime(src, (payload_step.EPOCH, payload_step.EPOCH))
    call('replace-' + src.name, ['env', 'MTOOLS_SKIP_CHECK=1', 'TZ=UTC', 'mcopy', '-o', '-m',
         '-i', out / 'payload.img', src, '::/EFI/UniXNU/' + member])
tree = fat_tree(parent / 'payload.img')
assert fat_tree(out / 'payload.img') == tree
members = [p.removeprefix('::/EFI/UniXNU/') for p in tree if not p.endswith('/')]
new_members = {n: hashlib.sha256(read_member(out / 'payload.img', n)).hexdigest() for n in members}
changed = sorted(n for n in members if new_members[n] != prior['payload_members_after'][n])
assert changed == (['Payloads/kernel.macho'] if opts.r58 else ['Payloads/kernel.macho', 'unixnu.toml'])
assert new_members['Payloads/kernel.macho'] == digest(out / 'prelink.macho')
assert read_member(out / 'payload.img', 'Payloads/kernel.macho.adt') == (parent / 'kernel.macho.adt').read_bytes()

local = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21/self-check-package/packaging/local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(device.parent / 'UniXNU-sm8250-common')]))
uefi = device.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
ref = json_file(parent / 'boot.json')
assert digest(fd) == ref['fd_sha256'] and digest(dtb) == ref['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, out / 'payload.img', out / 'boot.img')
offset = prior['boot_payload_offset']
embedded = out / 'tmp/boot-payload.img'
with (parent / 'boot.img').open('rb') as old, (out / 'boot.img').open('rb') as new:
    x, y = old.read(offset), new.read(offset)
    assert x[:576] == y[:576] and x[596:] == y[596:]
    assert hashlib.file_digest(old, 'sha256').hexdigest() == before['payload.img']
    with embedded.open('wb') as extracted:
        shutil.copyfileobj(new, extracted)
assert digest(embedded) == digest(out / 'payload.img')
readback = read_member(embedded, 'unixnu.toml')
assert readback == config.read_bytes()
args = next(e['args'] for e in tomllib.loads(readback.decode())['entry'] if e['id'] == 'xnu')
assert args == prior['args'] + arg
embedded.unlink()
assert {n: digest(parent / n) for n in names} == before
assert snapshot([*paths, *arch, donor]) == inputs
assert head(base) == helpers['BASE_PIN']
assert head(xnu) == 'd8b80295118ef25ac3a784134bcf95cd8e88109f'

result = dict(before=before, after={n: digest(out / n) for n in names},
              sizes={n: (out / n).stat().st_size for n in names},
               deltas={n: (out / n).stat().st_size - (parent / n).stat().st_size for n in names},
              args=args, objects={p.name: [inputs[str(p)], digest(q)] for p, q in new_objs.items()},
              unchanged_filelist_inputs=len(paths) - len(new_objs), unchanged_direct_archives=len(arch),
              changed_payload_members=changed, payload_members_after=new_members,
              boot_payload_offset=offset, zero_undefined_including_weak=True,
              unique_formats=True, single_record_and_dump_callsites=True,
               hook_line=ipc_text[:ipc_text.index('enuma_tx_record(hdr, port')].count('\n') + 1,
              dump_line=snap_text[:snap_text.index('\tenuma_tx_dump();')].count('\n') + 1)
(out / 'candidate-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
