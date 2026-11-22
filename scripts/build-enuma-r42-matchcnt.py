#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay the isolated r40 (r42) or r42 (r43) recipe with two replacements."""
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
from types import SimpleNamespace

sys.dont_write_bytecode = True
device = Path(__file__).resolve().parents[1]
base = device.parents[1] / 'UniXNU'
r40 = device / 'out/ufs-sm8250-storegeom-20261123-r40'
r42 = device / 'out/ufs-sm8250-matchcnt-20261123-r42'
r34 = device / 'out/ufs-sm8250-launchd-ipc-20261123-r34'
r21 = device / 'out/ufs-sm8250-launchd-keystore-20261122-r21'
r10 = device / 'out/ufs-sm8250-launchd-display-20261121-r10/self-check/build-final'
args = argparse.ArgumentParser()
args.add_argument('--r43', action='store_true')
args.add_argument('--out', type=Path)
options = args.parse_args()
baseline = r42 if options.r43 else r40
default_out = device / 'out/ufs-sm8250-matchcnt2-20261123-r43' if options.r43 else r42
out = (options.out or default_out).resolve()
assert out.parent == device / 'out' and not out.exists(), out
fragment = device / 'package' / ('EnumaMatchCount2.inc' if options.r43 else 'EnumaMatchCount.inc')
helpers = runpy.run_path(str(device / 'scripts/build-enuma-r23-hid-standin.py'))
digest, snapshot, read_member, fat_tree = (
    helpers['R'][k] for k in ('digest', 'snapshot', 'read_member', 'fat_tree'))
pin = helpers['BASE_PIN']


def check_head():
    assert subprocess.check_output(['git', '-C', base, 'rev-parse', 'HEAD'],
                                   text=True).strip() == pin


def read_json(path):
    return json.loads(path.read_text())


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


check_head()
names = ('kernel.macho.adt', 'native.macho', 'prelink.macho', 'payload.img', 'boot.img')
prior = read_json(baseline / 'candidate-manifest.json')
for name in names:
    assert digest(baseline / name) == prior[name]['new'], name
assert (baseline / 'kernel.macho.adt').read_bytes() == (r40 / 'kernel.macho.adt').read_bytes()
frozen_paths = [baseline / n for n in (*names, 'link.filelist', 'native-link.map',
                                      'boot.json', 'commands.json', 'candidate-manifest.json')]
frozen = snapshot(frozen_paths)
recipe = read_json(baseline / 'commands.json')
paths = [Path(x) for x in (baseline / 'link.filelist').read_text().splitlines()]
units = ('IOUserClient.cpo', 'kern_exec.o')
old_obj_dir = (r42 if options.r43 else r34) / 'objects'
for unit in units:
    assert [p for p in paths if p.name == unit] == [old_obj_dir / unit], unit
if options.r43:
    assert all(digest(old_obj_dir / unit) == prior['objects'][unit]['new'] for unit in units)
    uc_recipe, exec_recipe = (recipe['compile-' + unit] for unit in units)
else:
    steps = {s['tag']: s for s in
             read_json(r21 / 'self-check/build-final/kernel-build-result.json')['r13_delta']['steps']}
    uc_recipe, = (s for s in read_json(r10 / 'kernel-build-result.json')['commands']
                  if s['tag'] == 'compile-IOUserClient.cpo')
    exec_recipe = steps['compile-kern_exec.o']
direct = sorted({Path(a.rsplit(',', 1)[-1]) for a in recipe['link']['argv'] if a.endswith('.a')})
prelink_args = recipe['prelink']['argv']
donor = Path(prelink_args[prelink_args.index('--prelinked') + 1])
inputs = snapshot([*paths, *direct, donor])

sys.path.insert(0, str(base / 'scripts'))
from unixnu import bootimg, payload as payload_step
from unixnu.cli import parser
from unixnu.config import Context
from unixnu.kernel import linux_env

out.mkdir()
for name in ('objects', 'logs', 'tmp'):
    (out / name).mkdir()
tree = Path(recipe['link']['cwd']).parents[3]
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


source = out / 'source'
source.mkdir()
old_sources = (r42 if options.r43 else r34) / 'source'
bsd = source / 'bsd/kern'
shutil.copytree(old_sources / 'bsd/kern', bsd)
shutil.copyfile(fragment, bsd / fragment.name)
fb = bsd / 'EnumaBbScan.inc'
text = fb.read_text()
if options.r43:
    text = replace_once(text, '#include "EnumaMatchCount.inc"', '#include "EnumaMatchCount2.inc"')
    text = replace_once(text, '\t\tenuma_matchcnt_dump();\n', '')
    text = replace_once(text,
        'enuma_fb_dump(__unused thread_call_param_t unused0, __unused thread_call_param_t unused1)\n{\n',
        '''enuma_fb_dump(thread_call_param_t match_snapshot, thread_call_param_t self)
{
	if (match_snapshot != NULL) {
		enuma_matchcnt_dump();
		thread_call_free(self);
		return;
	}
''')
    text = replace_once(text,
        '''	if (pid == 34 && strcmp(name, "backboardd") == 0) {
		__c11_atomic_store(&enuma_mt_bb_exec, 1, __ATOMIC_RELEASE);
	}
''', '''	if (pid == 34 && strcmp(name, "backboardd") == 0 &&
	    !__c11_atomic_exchange(&enuma_mt_armed, 1, __ATOMIC_RELAXED)) {
		uint64_t deadline;
		thread_call_t snapshot = thread_call_allocate_with_options(enuma_fb_dump, &enuma_mt_armed,
		    THREAD_CALL_PRIORITY_KERNEL, THREAD_CALL_OPTIONS_ONCE);
		clock_interval_to_deadline(ENUMA_FB_INTERVAL, NSEC_PER_SEC, &deadline);
		thread_call_enter1_delayed(snapshot, snapshot, deadline);
	}
''')
else:
    text = replace_once(text, '#include <kern/thread_call.h>',
                        '#include <kern/thread_call.h>\n#include "EnumaMatchCount.inc"')
    text = replace_once(text, '\t\tthread_call_free(enuma_fb_call);',
                        '\t\tenuma_matchcnt_dump();\n\t\tthread_call_free(enuma_fb_call);')
    text = replace_once(text, '\tif (pid == 1 && strcmp(name, "launchd") == 0 &&',
                        '\tif (pid == 34 && strcmp(name, "backboardd") == 0) {\n'
                        '\t\t__c11_atomic_store(&enuma_mt_bb_exec, 1, __ATOMIC_RELEASE);\n'
                        '\t}\n\tif (pid == 1 && strcmp(name, "launchd") == 0 &&')
fb.write_text(text)

uc = source / 'iokit/Kernel/IOUserClient.cpp'
uc.parent.mkdir(parents=True)
text = (old_sources / 'iokit/Kernel/IOUserClient.cpp').read_text()
hooks = {'internal_io_service_get_matching_services': 0,
         'internal_io_service_get_matching_service': 0,
         'internal_io_service_add_notification': 1,
         'is_io_service_open_extended': 2}
if options.r43:
    added_hooks = {'internal_io_service_match_property_table': 3,
                   'internal_io_service_add_interest_notification': 4}
else:
    text = replace_once(text, 'extern "C" void enuma_att_record(unsigned int);',
                        'extern "C" void enuma_att_record(unsigned int);\n'
                        'extern "C" void enuma_matchcnt_record(unsigned int, int);')
    added_hooks = hooks.copy()
for name, kind in added_hooks.items():
    entry, = re.findall(r'\n' + name + r'\([^;{}]*?\)\n\{\n', text)
    text = replace_once(text, entry, entry + f'\tenuma_matchcnt_record({kind}, proc_selfpid());\n')
uc.write_text(text)
hooks.update(added_hooks)
locations = {}
for name, kind in hooks.items():
    match, = re.finditer(r'\n' + name + r'\([^;{}]*?\)\n\{\n', text)
    assert text[match.end():].startswith(f'\tenuma_matchcnt_record({kind}, proc_selfpid());\n')
    locations[name] = text.count('\n', 0, match.end()) + 1

changes = {}
for unit, step, src in ((units[0], uc_recipe, uc),
                        (units[1], exec_recipe, bsd / 'kern_exec.c')):
    obj = out / 'objects' / unit
    argv = step['argv'].copy()
    assert Path(argv[2]).name == src.name and argv[3] == '-o'
    if unit == units[0] and not options.r43:
        argv += ['-iquote', str(Path(argv[2]).parent)]
    argv[2], argv[4] = src, obj
    if '-MF' in argv:
        argv[argv.index('-MF') + 1] = obj.with_suffix('.d')
    assert not {'-MJ', '-serialize-diagnostics'} & set(argv)
    call('compile-' + unit, argv, step['cwd'])
    changes[old_obj_dir / unit] = obj


def delta(old, new):
    return {'old': digest(old), 'new': digest(new), 'bytes': new.stat().st_size,
            'delta_bytes': new.stat().st_size - old.stat().st_size}


objects = {old.name: delta(old, new) for old, new in changes.items()}
assert all(v['old'] != v['new'] for v in objects.values())
(out / 'link.filelist').write_text(''.join(f'{changes.get(p, p)}\n' for p in paths))
for tag in ('link', 'prelink'):
    step = recipe[tag]
    argv = step['argv'].copy()
    for name in ('link.filelist', 'native.macho', 'native-link.map', 'prelink.macho'):
        argv = [a.replace(str(baseline / name), str(out / name)) for a in argv]
    call(tag, argv, out if tag == 'prelink' else step['cwd'])

formats = re.findall(r'"(enuma-mt: [^"]+)"', fragment.read_text())
assert len(formats) == len(set(formats)) == (6 if options.r43 else 4)
calls = {}
for name in ('native.macho', 'prelink.macho'):
    path = out / name
    assert not call('undefined-' + name, ['llvm-nm', '-u', path]).strip()
    blob = path.read_bytes()
    assert all(blob.count(s.replace(r'\n', '\n').encode() + b'\0') == 1 for s in formats)
    del blob
    # Inspect raw nlist as well so that weak undefined symbols cannot be omitted.
    blob = path.read_bytes()
    _, syms = helpers['symbols'](blob, helpers['macho'](blob))
    assert not [s for s in syms if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    del blob
    nm = call('defined-' + name, ['llvm-nm', '--defined-only', path])
    symbols = [line.split()[-1] for line in nm.splitlines() if line.split()]
    endpoints = ('get_matching_service', 'add_notification', 'open_extended',
                 'match_property_table', 'add_interest_notification')
    entries = [s for s in symbols if (s.startswith('_is_io_service_') or s.startswith('__Z')) and
               any(k in s for k in endpoints)]
    report = call('calls-' + name, ['llvm-objdump', '-d', '--disassemble-symbols=' +
                  ','.join(['_enuma_fb_arm', '_enuma_fb_dump', '_enuma_matchcnt_dump',
                            '_enuma_matchcnt_record', *entries]), path])
    owners = {}
    owner = ''
    for line in report.splitlines():
        sym = re.fullmatch(r'[0-9a-f]+ <([^>]+)>:', line.strip())
        if sym:
            owner = sym[1]
        for target in ('_enuma_matchcnt_record', '_enuma_matchcnt_dump', '_printf',
                       '_thread_call_enter1_delayed', '_thread_call_enter_delayed',
                       '_thread_call_free'):
            if f'<{target}>' in line and re.search(r'\bb(?:l)?\s+0x', line):
                owners.setdefault(owner, []).append(target)
    assert owners.get('_enuma_fb_dump', []).count('_enuma_matchcnt_dump') == 1, owners
    # r42 unrolls the four fixed rows and shares the printf within each top pair.
    assert owners.get('_enuma_matchcnt_dump', []).count('_printf') == (6 if options.r43 else 8), owners
    recorders = [s for s, targets in owners.items() if '_enuma_matchcnt_record' in targets]
    if options.r43:
        assert owners['_enuma_fb_arm'].count('_thread_call_enter1_delayed') == 1, owners
        assert owners['_enuma_fb_arm'].count('_thread_call_enter_delayed') == 1, owners
        assert len(recorders) == len(hooks), recorders
        for hook in hooks:
            sites = [s for s in recorders if s == '_' + hook or re.search(r'\d' + hook + r'[Pj]', s)]
            assert len(sites) == 1 and owners[sites[0]].count('_enuma_matchcnt_record') == 1, (hook, sites)
    else:
        assert '_is_io_service_open_extended' in recorders, recorders
        for pattern in ('get_matching_services', 'get_matching_service(?!s)', 'add_notification'):
            assert any(re.search(pattern, s) for s in recorders), recorders
    calls[name] = {s: ts for s, ts in owners.items() if s == '_enuma_matchcnt_dump' or
                   any(t != '_printf' for t in ts)}

shutil.copytree(baseline / 'device', out / 'device')
shutil.copyfile(baseline / 'kernel.macho.adt', out / 'kernel.macho.adt')
shutil.copyfile(baseline / 'payload.img', out / 'payload.img')
os.utime(out / 'prelink.macho', (payload_step.EPOCH, payload_step.EPOCH))
call('replace-kernel', ['env', 'MTOOLS_SKIP_CHECK=1', 'TZ=UTC', 'mcopy', '-o', '-m',
                        '-i', out / 'payload.img', out / 'prelink.macho', '::/EFI/UniXNU/Payloads/kernel.macho'])
old_tree = fat_tree(baseline / 'payload.img')
assert fat_tree(out / 'payload.img') == old_tree
members = [x.removeprefix('::/EFI/UniXNU/') for x in old_tree if not x.endswith('/')]
changed = [n for n in members if read_member(baseline / 'payload.img', n) != read_member(out / 'payload.img', n)]
assert changed == ['Payloads/kernel.macho'], changed
assert read_member(out / 'payload.img', changed[0]) == (out / 'prelink.macho').read_bytes()
assert (read_member(out / 'payload.img', 'Payloads/kernel.macho.adt') ==
        (out / 'kernel.macho.adt').read_bytes() == (baseline / 'kernel.macho.adt').read_bytes()
        == (r40 / 'kernel.macho.adt').read_bytes())
local = r21 / 'self-check-package/packaging/local-build.toml'
ctx = Context(parser().parse_args(['bootimg', '-D', str(out / 'device'), '--out', str(out / 'work'),
    '--config', str(local), '--local-module', 'soc:sm8250=' + str(device.parent / 'UniXNU-sm8250-common')]))
uefi = device.parent / 'uefi-enuma'
fd = uefi / 'Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd'
dtb = Path('/root/enuma-step10/inputs/enuma.dtb')
reference = read_json(baseline / 'boot.json')
assert digest(fd) == reference['fd_sha256'] and digest(dtb) == reference['dtb_sha256']
bootimg.build(ctx, uefi, fd, dtb, out / 'payload.img', out / 'boot.img')
offset = read_json(r34 / 'candidate-manifest.json')['boot_payload_offset']
with (baseline / 'boot.img').open('rb') as a, (out / 'boot.img').open('rb') as b:
    x, y = a.read(offset), b.read(offset)
    assert x[:576] == y[:576] and x[596:] == y[596:] and x[576:596] != y[576:596]
    assert hashlib.file_digest(a, 'sha256').hexdigest() == digest(baseline / 'payload.img')
    assert hashlib.file_digest(b, 'sha256').hexdigest() == digest(out / 'payload.img')

assert snapshot(frozen_paths) == frozen and snapshot([*paths, *direct, donor]) == inputs
check_head()
result = {n: delta(baseline / n, out / n) for n in names}
result.update(objects=objects, unchanged_filelist_inputs=len(paths) - len(changes),
              unchanged_direct_archives=len(direct), unchanged_inputs=inputs,
              changed_payload_members=changed, formats=formats, hook_lines=locations,
              call_sites=calls, zero_undefined=True, frozen=frozen,
              boot_metadata=read_json(out / 'boot.json'))
(out / 'candidate-manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print('candidate manifest written', flush=True)
