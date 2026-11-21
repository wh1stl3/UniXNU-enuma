#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""WSL host-only delta to the existing r10 kernel and packaging recipe."""
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
DEVICE = Path(__file__).resolve().parents[1]
BASE = DEVICE.parents[1] / 'UniXNU'
R10 = DEVICE / 'out/ufs-sm8250-launchd-display-20261121-r10'
R11 = DEVICE / 'out/ufs-sm8250-launchd-keystore-20261121-r11'
OLD = R10 / 'self-check/build-final'
NEW = R11 / 'self-check/build-final'
PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'
AKS_PIN = '8c70daf814aafdf4a3d35e40dde0322655fd0a83'
COMP = BASE / 'drivers/AppleKeyStoreState'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def init_sections(path):
    blob = path.read_bytes()
    assert blob[:4] == b'\xcf\xfa\xed\xfe', path
    ncmds, = struct.unpack_from('<I', blob, 16)
    offset = 32
    result = {}
    for _ in range(ncmds):
        cmd, length = struct.unpack_from('<II', blob, offset)
        if cmd == 0x19:  # LC_SEGMENT_64
            nsects, = struct.unpack_from('<I', blob, offset + 64)
            for i in range(nsects):
                p = offset + 72 + 80 * i
                section, segment, _, size = struct.unpack_from('<16s16sQQ', blob, p)
                if section.rstrip(b'\0') == b'__mod_init_func':
                    result[segment.rstrip(b'\0').decode()] = size
        offset += length
    return result


def export_initializer(path):
    # Same one-bit nlist change as the late PMGR archive builder. Mach-O
    # llvm-objcopy does not support --globalize-symbol on this host.
    blob = bytearray(path.read_bytes())
    ncmds, = struct.unpack_from('<I', blob, 16)
    offset = 32
    for _ in range(ncmds):
        cmd, length = struct.unpack_from('<II', blob, offset)
        if cmd == 2:  # LC_SYMTAB
            symoff, count, stroff, _ = struct.unpack_from('<4I', blob, offset + 8)
            break
        offset += length
    else:
        raise ValueError(f'{path} has no LC_SYMTAB')
    hits = []
    for i in range(count):
        entry = symoff + i * 16
        string = stroff + struct.unpack_from('<I', blob, entry)[0]
        if blob[string:blob.index(0, string)] == b'__GLOBAL__sub_I_NativeKeyStoreEvents.cpp':
            hits.append(entry + 4)
    kind, = hits
    assert blob[kind] == 0x0e  # local N_SECT
    blob[kind] |= 1            # add N_EXT, no change to code
    path.write_bytes(blob)


def build_kernel():
    data = json.loads((OLD / 'kernel-build-result.json').read_text())
    commands = {entry['tag']: entry for entry in data['commands']}
    linked = commands['link-native-macho']
    objroot = Path(linked['cwd'])
    tree = objroot.parents[3]
    checkout = tree / '.cache/xnu-work'
    old_objects = (OLD / 'link.filelist').read_text().splitlines()
    assert sha(OLD / 'native.macho') == data['diff_vs_r4']['new_sha256']
    assert sha(OLD / 'prelink.macho') == data['diff_vs_r4']['prelink_sha256']
    assert subprocess.check_output(['git', '-C', BASE, 'rev-parse', 'HEAD'], text=True).strip() == PIN
    assert subprocess.check_output(['git', '-C', COMP, 'rev-parse', 'HEAD'], text=True).strip() == AKS_PIN

    NEW.mkdir(parents=True)
    (NEW / 'objects').mkdir()
    (NEW / 'logs').mkdir()
    (NEW / 'tmp').mkdir()
    sys.path.insert(0, str(BASE / 'scripts'))
    from unixnu.kernel import linux_env
    env = dict(os.environ)
    env.update(linux_env(SimpleNamespace(tree=tree)))
    env['PATH'] = '/home/wh1stl3/.local/bin:' + env['PATH']
    env.update(TMPDIR=str(NEW / 'tmp'), PYTHONDONTWRITEBYTECODE='1')
    steps = []

    def run(tag, argv, cwd=NEW):
        argv = list(map(str, argv))
        reply = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
        log = NEW / 'logs' / f'{tag}.log'
        log.write_text(reply.stdout)
        steps.append(dict(tag=tag, argv=argv, cwd=str(cwd), exit=reply.returncode))
        if reply.returncode:
            print(reply.stdout, file=sys.stderr)
            raise SystemExit(f'{tag}: exit {reply.returncode}; see {log}')
        print(tag, flush=True)
        return reply.stdout

    sources = NEW / 'source'
    bsd = sources / 'bsd/kern/bsd_init.c'
    oskext = sources / 'libkern/c++/OSKext.cpp'
    state = sources / 'NativeKeyStoreEvents.cpp'
    for name, original in ((bsd, OLD / 'probe-source/bsd/kern/bsd_init.c'),
                           (oskext, checkout / 'libkern/c++/OSKext.cpp')):
        name.parent.mkdir(parents=True)
        shutil.copyfile(original, name)
    state.write_bytes(subprocess.check_output(
        ['git', '-C', COMP, 'show', f'{AKS_PIN}:{state.name}']))
    for patch in ('board-classes', 'keystore-probe'):
        log = run('apply-' + patch,
                  ['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i',
                   DEVICE / f'patches/xnu/enuma-r11-{patch}.patch'], sources)
        assert 'fuzz' not in log and 'offset' not in log, log

    obj = NEW / 'objects'

    def compile_unit(tag, recipe, src, output, *extra):
        args = list(recipe.get('arguments', recipe.get('argv')))
        assert args[3] == '-o', args[:6]
        args[2], args[4] = str(src), str(obj / output)
        run(tag, args + list(extra), recipe.get('directory', recipe.get('cwd')))

    compile_unit('compile-bsd', commands['compile-bsd_init.o'], bsd, 'bsd_init.o',
                 '-D', 'XNU_ENUMA_KEYSTORE=1')
    recipe = (objroot / 'libkern/DEVELOPMENT/OSKext.cpo.json').read_text()
    oskext_recipe = json.loads(recipe.strip().rstrip(','))  # clang -MJ fragment
    compile_unit('compile-oskext', oskext_recipe, oskext, 'OSKext.cpo')
    cpp = commands['compile-EnumaUfsOwnerQuery']
    compile_unit('compile-state', cpp, state, 'NativeKeyStoreEvents.o')
    compile_unit('compile-probe', cpp, DEVICE / 'package/EnumaKeyStoreProbe.cpp', 'EnumaKeyStoreProbe.o')
    raw, late = (obj / name for name in ('NativeKeyStoreEvents.o', 'NativeKeyStoreEvents.late.o'))
    assert init_sections(raw) == {'__DATA': 8}
    run('defer-state-init', ['llvm-objcopy', '--remove-section=__DATA,__mod_init_func', raw, late])
    assert not init_sections(late)
    export_initializer(late)
    archive = NEW / 'libAppleKeyStoreState.a'
    run('archive-state', ['llvm-ar', 'rcs', archive, late, obj / 'EnumaKeyStoreProbe.o'])

    replacements = {
        str(OLD / 'objects/bsd_init.o'): str(obj / 'bsd_init.o'),
        str(objroot / 'libkern/DEVELOPMENT/OSKext.cpo'): str(obj / 'OSKext.cpo'),
    }
    assert all(old_objects.count(path) == 1 for path in replacements)
    filelist = NEW / 'link.filelist'
    filelist.write_text('\n'.join(replacements.get(line, line) for line in old_objects) + '\n')
    argv = list(linked['argv'])
    argv[argv.index('-filelist') + 1] = str(filelist)
    argv[argv.index('-o') + 1] = str(NEW / 'native.macho')
    argv[argv.index(f'-Wl,-map,{OLD / "native-link.map"}')] = f'-Wl,-map,{NEW / "native-link.map"}'
    run('link', argv + [f'-Wl,-force_load,{archive}'], objroot)
    argv = [arg.replace(str(OLD), str(NEW)) for arg in commands['emit-prelink-macho']['argv']]
    run('prelink', argv)

    linkmap = (NEW / 'native-link.map').read_text(errors='replace').splitlines()
    wanted = {'_OSKextRegisterBoardClasses': 'OSKext.cpo',
              '_enuma_keystore_probe': 'EnumaKeyStoreProbe.o',
              '_native_aks_device_id': 'EnumaKeyStoreProbe.o',
              '_native_keyevents_allocate': 'NativeKeyStoreEvents.late.o',
              '__GLOBAL__sub_I_NativeKeyStoreEvents.cpp': 'NativeKeyStoreEvents.late.o',
              '__ZTV13AppleKeyStore': 'NativeKeyStoreEvents.late.o',
              '__ZTV23AppleKeyStoreUserClient': 'NativeKeyStoreEvents.late.o'}
    owners = {}
    for symbol, member in wanted.items():
        rows = [line.split() for line in linkmap if line.endswith(' ' + symbol)]
        assert len(rows) == 1, (symbol, rows)
        assert any(line.startswith(rows[0][2] + ' ') and member in line for line in linkmap), rows
        owners[symbol] = dict(member=member, address=rows[0][0])
    sections = {}
    for name in ('native.macho', 'prelink.macho'):
        assert not run('nm-u-' + name, ['llvm-nm', '-u', NEW / name]).strip()
        symbols = run('nm-m-' + name, ['llvm-nm', '-m', NEW / name])
        assert '(undefined)' not in symbols
        assert all(sum(line.endswith(' ' + symbol) for line in symbols.splitlines()) == 1
                   for symbol in wanted)
        sections[name] = [init_sections(OLD / name), init_sections(NEW / name)]
        assert sections[name][0] == sections[name][1], sections
    calls = {}
    for unit, target, count in (('bsd_init.o', '_enuma_keystore_probe', 2),
                                ('EnumaKeyStoreProbe.o', '_OSKextRegisterBoardClasses', 1),
                                ('EnumaKeyStoreProbe.o', '_printf', 8)):
        relocs = run('relocations-' + unit + '-' + target,
                     ['llvm-objdump', '--macho', '--reloc', obj / unit])
        calls[target] = sum('BR26' in line and line.rstrip().endswith(target)
                            for line in relocs.splitlines())
        assert calls[target] == count, (target, calls[target])
    inputs = [obj / name for name in ('bsd_init.o', 'OSKext.cpo', 'EnumaKeyStoreProbe.o',
                                      'NativeKeyStoreEvents.o', 'NativeKeyStoreEvents.late.o')]
    inputs += [archive, NEW / 'native.macho', NEW / 'prelink.macho']
    data['diff_vs_r4'].update(new_sha256=sha(NEW / 'native.macho'),
                              prelink_sha256=sha(NEW / 'prelink.macho'),
                              prelink_bytes=(NEW / 'prelink.macho').stat().st_size)
    data['macros']['bsd_init.o']['object_sha256'] = sha(obj / 'bsd_init.o')
    data['r11_delta'] = dict(owners=owners, init_sections=sections, calls=calls, steps=steps,
                            files={p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in inputs})
    (NEW / 'kernel-build-result.json').write_text(json.dumps(data, indent=2) + '\n')
    for name in ('IOKitBSDInit.cpo', 'IOUserClient.cpo', 'EnumaUfsOwnerQuery.o',
                 'kern_exec.o', 'kern_exec.o.i'):
        shutil.copyfile(OLD / 'objects' / name, obj / name)
    shutil.copyfile(R10 / 'self-check/seed-inspection.json', NEW / 'seed-inspection.json')


def package():
    recipe = R10 / 'run_packaging.py'
    wrapper = R10 / 'r7-payload-wrapper.py'
    assert sha(recipe) == 'dfb1a57e1beaca1f1ff6532523c7cc96c80cdfd7927cbb96372771089de39e8f'
    assert sha(wrapper) == '2db5b7f1a215cdabf9394d0d47a2b03a23c6874d9de45bba38d884d36c21867a'
    text = recipe.read_text()

    def change(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)

    change("SELF = DELIVERY / 'self-check-repack2'", "SELF = DELIVERY / 'self-check-package'")
    change('EXPECTED_ARGS = R4_ARGS + DISPLAY_ARGS',
           "EXPECTED_ARGS = R4_ARGS + DISPLAY_ARGS + ['sheng-aks=1']")
    change("'native-ufs-probe', 'native-ufs-observe-reuse')",
           "'native-ufs-probe', 'native-ufs-observe-reuse', 'offline-keystore')")
    start = text.index('    r9objects = ')
    end = text.index("    kernel_build['macros']['kern_exec.o']['object_equals_r4']", start)
    text = text[:start] + """    r10objects = DEVICE / 'out/ufs-sm8250-launchd-display-20261121-r10/self-check/build-final/objects'
    for unit in ('IOKitBSDInit.cpo', 'IOUserClient.cpo', 'EnumaUfsOwnerQuery.o', 'kern_exec.o', 'kern_exec.o.i'):
        assert sha256_file(original / 'objects' / unit) == sha256_file(r10objects / unit), unit
    assert sha256_file(original / 'objects/bsd_init.o') != sha256_file(r10objects / 'bsd_init.o')
""" + text[end:]
    change("    board_txt = board_txt.replace(r4_line, new_line)",
           '''    board_txt = board_txt.replace(r4_line, new_line)
    assert board_txt.count('"RamBlock", "ShengUfs"]') == 1
    board_txt = board_txt.replace('"RamBlock", "ShengUfs"]',
                                  '"RamBlock", "ShengUfs", "AppleKeyStoreState"]')
    assert board_txt.count('  "build-enuma-platform-power.py --inputs ') == 1
    board_txt = board_txt.replace('  "build-enuma-platform-power.py --inputs ',
                                  '  "component:AppleKeyStoreState",\\n'
                                  '  "build-enuma-platform-power.py --inputs ')''')
    change("    sheng_pmgr_run_present = '_sheng_pmgr_run' in names",
           """    assert set(kernel_build['r11_delta']['owners']) <= names
    sheng_pmgr_run_present = '_sheng_pmgr_run' in names""")
    change("'boot_args_identical': True", "'boot_args_identical': False")
    start = text.index("        'status': 'Legacy-display")
    end = text.index("        'validation':", start)
    text = text[:start] + "        'status': 'r11 scratch AppleKeyStore state probe; not deployed',\n" + text[end:]
    change("        'validation': 'self-checked',", """        'validation': 'self-checked',
        'r11_delta': kernel_build['r11_delta'],""")
    shutil.copyfile(wrapper, R11 / wrapper.name)
    packaged = R11 / recipe.name
    packaged.write_text(text)
    feeds = R10 / 'self-check-repack2/packaging/out/feeds'
    assert feeds.is_dir()
    subprocess.run([sys.executable, '-B', packaged, '--seed-feeds-from', feeds],
                   cwd=R11, check=True)
    compare_packages()


def compare_packages():
    prior = json.loads((R10 / 'candidate-manifest.json').read_text())
    now = json.loads((R11 / 'candidate-manifest.json').read_text())
    keys = ('vendor_fd_sha256', 'dtb_sha256', 'adt_sha256', 'payload_bytes', 'boot_bytes')
    for key in keys:
        assert prior['package_audit'][key] == now['package_audit'][key], key
    assert now['package_audit']['boot_args'] == prior['package_audit']['boot_args'] + ' sheng-aks=1'
    for name in ('self-check/scratch-data.img', 'self-check/kernel.macho.adt'):
        assert prior['artifacts'][name] == now['artifacts'][name], name
    for name in ('boot.img', 'payload.img'):
        assert sha(R10 / name) == prior['artifacts'][name]['sha256']
        assert sha(R11 / name) == now['artifacts'][name]['sha256']
        assert now['artifacts'][name]['sha256'] != prior['artifacts'][name]['sha256']
    (R11 / 'delta-vs-r10.json').write_text(json.dumps({
        'before': prior['artifacts'], 'after': now['artifacts'],
        'package_before': prior['package_audit'], 'package_after': now['package_audit'],
    }, indent=2) + '\n')


if __name__ == '__main__':
    commands = {'kernel': build_kernel, 'package': package}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit('usage: build-enuma-r11-keystore.py {kernel|package}')
    commands[sys.argv[1]]()
