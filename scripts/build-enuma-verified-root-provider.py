#!/usr/bin/env python3
"""Isolated VerifiedRoot object audit; never a kernel link or a deployment tool."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/mnt/d/Code/PortingiOS/UniXNU')
PIN = '693f5d9cae8a408dd18b39f3f9fdc4228c934241'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['test-only', 'production'])
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--compile-record', required=True, type=Path)
    p.add_argument('--candidate', required=True, type=Path)
    p.add_argument('--anchor', type=Path)
    p.add_argument('--os-policy', type=Path)
    p.add_argument('--systemos-policy', type=Path)
    a = p.parse_args()
    out = a.output.resolve()
    if not out.is_relative_to((ROOT / 'out').resolve()) or out == (ROOT / 'out').resolve():
        p.error('output must be a new directory under device out/')
    if a.mode == 'production' and not all((a.anchor, a.os_policy, a.systemos_policy)):
        p.error('production requires explicit --anchor, --os-policy and --systemos-policy')
    if a.mode == 'test-only' and any((a.anchor, a.os_policy, a.systemos_policy)):
        p.error('test-only does not accept production inputs')
    head = subprocess.check_output(['git', '-C', str(BASE), 'rev-parse', 'HEAD'], text=True).strip()
    if head != PIN:
        raise ValueError('base HEAD differs from pinned 693f5d9')
    out.mkdir(parents=True, exist_ok=False)
    report = {'mode': a.mode, 'base_head': head, 'commands': [], 'kernel_linked': False,
              'signature_checked': False, 'deployment': False}
    def save():
        (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    def run(args, cwd=None):
        args = list(map(str, args))
        proc = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        report['commands'].append({'argv': args, 'cwd': str(cwd or Path.cwd()), 'exit': proc.returncode, 'output': proc.stdout})
        save()
        if proc.returncode:
            raise RuntimeError(f'{args[0]} failed: {proc.stdout[-2000:]}')
        return proc.stdout
    try:
        inputs = [a.anchor, a.os_policy, a.systemos_policy]
        if a.mode == 'test-only':
            inputs = [out / 'TEST_ONLY-invalid-anchor.bin', out / 'TEST_ONLY-invalid-os.bin', out / 'TEST_ONLY-invalid-systemos.bin']
            for path, data in zip(inputs, [bytes(395), b'TEST_ONLY_INVALID_OS', b'TEST_ONLY_INVALID_SYSTEMOS']):
                path.write_bytes(data)
        inputs = [x.resolve() for x in inputs]
        if inputs[0].stat().st_size != 395 or any(x.stat().st_size == 0 for x in inputs[1:]):
            raise ValueError('anchor must be 395 bytes and policies must be nonempty')
        report['inputs'] = [{'path': str(x), 'size': x.stat().st_size, 'sha256': digest(x)} for x in inputs]
        sources = [BASE / 'kits/VerifiedRoot/src/verified_root.c', BASE / 'kits/VerifiedRoot/adapters/xnu_crypto.c', BASE / 'kits/VerifiedRoot/include/verified_root.h', BASE / 'drivers/VirtioMmioBlock/VerifiedBlockPolicy.h', a.candidate, a.compile_record]
        report['source_sha256'] = {str(x): digest(x) for x in sources}
        asm = out / 'provider.S'
        def inc(path):
            return str(path).replace('\\', '\\\\').replace('"', '\\"')
        asm.write_text('.section __TEXT,__const\n.p2align 3\npolicy0:\n.incbin "' + inc(inputs[1]) + '"\npolicy1:\n.incbin "' + inc(inputs[2]) + '"\n.globl _verified_root_key\n_verified_root_key:\n.incbin "' + inc(inputs[0]) + '"\n.p2align 3\n.globl _verified_root_policy_count\n_verified_root_policy_count: .quad 2\n.section __DATA_CONST,__const\n.p2align 3\n.globl _verified_root_policies\n_verified_root_policies:\n.quad policy0\n.quad ' + str(inputs[1].stat().st_size) + '\n.quad policy1\n.quad ' + str(inputs[2].stat().st_size) + '\n')
        rec = json.loads(a.compile_record.read_text().strip().rstrip(','))
        objs = []
        for source in sources[:2]:
            obj = out / (source.stem + '.o')
            args, raw, i = [], rec['arguments'], 0
            while i < len(raw):
                value = raw[i]
                if value in ('-MF', '-MJ', '-MT', '-MQ'):
                    i += 2; continue
                if value in ('-MD', '-MMD', '-MP'):
                    i += 1; continue
                if value.startswith('-W') and not value.startswith('-Wno-'):
                    i += 1; continue
                if value in ('-I', '-isystem', '-iquote'):
                    directory = Path(raw[i + 1])
                    if not directory.is_absolute():
                        directory = Path(rec['directory']) / directory
                    if not directory.is_dir():
                        i += 2; continue
                if value.startswith('-I') and len(value) > 2:
                    directory = Path(value[2:])
                    if not directory.is_absolute():
                        directory = Path(rec['directory']) / directory
                    if not directory.is_dir():
                        i += 1; continue
                if value == '-o':
                    args += ['-o', str(obj)]; i += 2; continue
                args.append(str(source) if value == rec['file'] else value)
                i += 1
            if str(source) not in args:
                raise ValueError('compile record source not found in arguments')
            args += ['-I' + str(BASE / 'kits/VerifiedRoot/include'), '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter']
            run(args, rec['directory']); objs.append(obj)
        provider = out / 'provider.o'
        run(['clang', '-target', 'arm64-apple-ios17.0', '-c', asm, '-o', provider]); objs.append(provider)
        sys.path.insert(0, str(BASE / 'scripts'))
        from kernel_target import check_object
        for obj in [a.candidate, *objs]:
            check_object(obj.read_bytes(), str(obj))
        definitions, undefined = {}, {}
        for obj in [a.candidate, *objs]:
            defs = run(['llvm-nm', '-g', '--defined-only', obj])
            undefs = run(['llvm-nm', '-u', obj])
            definitions[str(obj)] = sorted(line.split()[-1] for line in defs.splitlines() if line.split())
            undefined[str(obj)] = sorted(line.split()[-1] for line in undefs.splitlines() if line.split())
        all_defs = set().union(*map(set, definitions.values()))
        all_undefs = set().union(*map(set, undefined.values()))
        provider_names = {'_verified_root_key', '_verified_root_policies', '_verified_root_policy_count', '_vr_open', '_vr_verify_block', '_vr_xnu_crypto'}
        report.update(definitions=definitions, undefined_by_object=undefined,
                      unresolved_after_set_resolution=sorted(all_undefs - all_defs),
                      unresolved_provider=sorted((all_undefs - all_defs) & provider_names),
                      audit='offline object symbol set only; no linker or archive extraction proof',
                      object_sha256={str(x): digest(x) for x in objs})
        save()
        if report['unresolved_provider']:
            raise ValueError('provider symbols remain unresolved')
    finally:
        save()


if __name__ == '__main__':
    main()
