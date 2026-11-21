#!/usr/bin/env python3
"""External=1 function-body equivalence between two ShengUfs build cells.

Read-only. Reuses the accepted fix2 cell and the observation build cell as-is:
it runs the stored compile argv with `-E -P` (no object emitted) and decodes the
existing NativeUfs.o objects. It fails closed unless:

* compiler arguments are equal after replacing each isolated tree root;
* preprocessed logic is equal after normalizing panic `__LINE__` constants;
* every runtime section except __TEXT/__text is byte-identical with equal
  relocations, flags and alignment;
* every __TEXT/__text byte difference belongs to a MOV immediate whose
  before/after line numbers are an observed panic location pair;
* __debug_str is equal after tree-path replacement and panic-coordinate
  substitution, and each substituted coordinate maps to the same source line.

This proves equivalence of the external=1, observation=0 translation units; it
does not prove ABI/load/link behaviour and does not rebuild either cell.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys


def load_identity():
    path = Path(__file__).with_name('audit-enuma-ufs-object-identity.py')
    spec = importlib.util.spec_from_file_location('ufs_identity', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(command, cwd, log):
    child = subprocess.run([str(x) for x in command], cwd=str(cwd), capture_output=True, text=True)
    log.append({'command': [str(x) for x in command], 'cwd': str(cwd), 'exit': child.returncode})
    if child.returncode:
        raise SystemExit(f'command failed ({child.returncode}): {command}\n{child.stdout}{child.stderr}')
    return child.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True,
                        help='accepted fix2 cell (external-1-diagnostic-N)')
    parser.add_argument('--after', type=Path, required=True,
                        help='observation-only build cell (external-1-diagnostic-N, observation=0)')
    parser.add_argument('--diagnostic', type=int, choices=(0, 1), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True,
                        help='directory for preprocessed text and raw command log')
    args = parser.parse_args()

    identity = load_identity()
    log = []
    args.evidence.mkdir(parents=True, exist_ok=True)

    cells = (args.before, args.after)
    commands = [json.loads((cell / 'compile-command.json').read_text()) for cell in cells]
    roots = [str(Path(command[2]).parents[2]) for command in commands]
    canonical = [[str(v).replace(root, '<ISOLATED-TREE>') for v in command]
                 for command, root in zip(commands, roots)]
    assert canonical[0] == canonical[1], 'non-path compiler argument drift'

    objects = []
    members = []
    for cell in cells:
        blob = (cell / 'NativeUfs.o').read_bytes()
        assert blob[:4] == b'\xcf\xfa\xed\xfe', 'NativeUfs.o is not a thin Mach-O'
        objects.append(blob)
        member, entries = identity.ar_member(cell / 'libShengUfs.a')
        object_entries = [e for e in entries if e['name'] == 'NativeUfs.o']
        assert len(object_entries) == 1, entries
        assert member == blob, 'standalone NativeUfs.o differs from the archive member'
        members.append(object_entries[0])

    preprocessed = []
    for index, (command, root) in enumerate(zip(commands, roots)):
        cmd = list(command)
        offset = cmd.index('-o')
        del cmd[offset:offset + 2]
        cmd.remove('-c')
        cmd += ['-E', '-P',
                '-DNATIVE_UFS_OBSERVATION_ONLY=0',
                '-DNATIVE_UFS_EXTERNAL_STORE_PROVIDER=1',
                f'-DNATIVE_UFS_REUSE_DIAGNOSTIC={args.diagnostic}',
                '-Wno-missing-designated-field-initializers',
                '-Wno-unused-but-set-global']
        recipe = Path(root) / 'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json'
        cwd = json.loads(recipe.read_text().strip().rstrip(','))['directory']
        text = run(cmd, cwd, log)
        preprocessed.append(text)
        (args.evidence / f'preprocessed-{index}.txt').write_text(text)

    pattern = r'("NativeUfs\.cpp", )(\d+)'
    for text in preprocessed:
        assert all('(panic)(' in line for line in text.splitlines() if re.search(pattern, line))
    normalized = [re.sub(pattern, r'\1<SOURCE-LINE>', text) for text in preprocessed]
    assert normalized[0] == normalized[1], 'preprocessed external=1 logic changed'
    locations = [re.findall(pattern, text) for text in preprocessed]
    assert len(locations[0]) == len(locations[1]), 'panic location count changed'
    pairs = {(int(a[1]), int(b[1])) for a, b in zip(*locations) if a[1] != b[1]}

    sections_before, sections_after = (identity.sections(blob) for blob in objects)
    assert sections_before.keys() == sections_after.keys(), 'section set changed'
    runtime = []
    for name in sections_before:
        row = {'section': name,
               'size_before': sections_before[name]['size'],
               'size_after': sections_after[name]['size'],
               'flags_equal': sections_before[name]['flags'] == sections_after[name]['flags'],
               'alignment_equal': sections_before[name]['alignment'] == sections_after[name]['alignment'],
               'relocations_equal': sections_before[name]['relocations'] == sections_after[name]['relocations']}
        if name.startswith('__DWARF/'):
            continue
        assert row['flags_equal'] and row['alignment_equal'] and row['relocations_equal'], row
        assert row['size_before'] == row['size_after'], row
        payload_equal = sections_before[name]['data'] == sections_after[name]['data']
        if name != '__TEXT/__text':
            assert payload_equal, row
        runtime.append(dict(row, payload_equal=payload_equal))

    instructions = []
    for index, cell in enumerate(cells):
        text = run(['llvm-objdump', '--disassemble', cell / 'NativeUfs.o'],
                   Path(roots[index]), log)
        decoded = {}
        for line in text.splitlines():
            match = re.fullmatch(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s+(.+)', line)
            if match:
                decoded[int(match[1], 16)] = (match[2], match[3])
        assert decoded
        instructions.append(decoded)
    before_ins, after_ins = instructions
    assert before_ins.keys() == after_ins.keys(), 'instruction address set changed'
    changes = []
    for address in before_ins:
        if before_ins[address] == after_ins[address]:
            continue
        old = re.fullmatch(r'mov\s+(w\d+), #(\d+)', before_ins[address][1])
        new = re.fullmatch(r'mov\s+(w\d+), #(\d+)', after_ins[address][1])
        assert old and new and old[1] == new[1] and (int(old[2]), int(new[2])) in pairs, \
            (hex(address), before_ins[address], after_ins[address])
        changes.append({'offset': address, 'before': before_ins[address][1], 'after': after_ins[address][1]})

    text_before = sections_before['__TEXT/__text']['data']
    text_after = sections_after['__TEXT/__text']['data']
    allowed = {change['offset'] + i for change in changes for i in range(4)}
    assert all(i in allowed for i, (x, y) in enumerate(zip(text_before, text_after)) if x != y), \
        'text byte difference not explained by panic-immediate MOVs'

    debug_before = sections_before['__DWARF/__debug_str']['data']
    debug_after = sections_after['__DWARF/__debug_str']['data']
    debug_before = debug_before.replace(roots[0].encode(), roots[1].encode())
    coordinate = rb'NativeUfs\.cpp:(\d+):(\d+)'
    coordinates = [re.findall(coordinate, text) for text in (debug_before, debug_after)]
    assert len(coordinates[0]) == len(coordinates[1]), 'DWARF coordinate count changed'
    sources = [Path(command[2]).read_text().splitlines() for command in commands]
    for old, new in zip(*coordinates):
        assert old[1] == new[1], (old, new)
        assert sources[0][int(old[0]) - 1] == sources[1][int(new[0]) - 1], (old, new)
    assert re.sub(coordinate, rb'NativeUfs.cpp:<LINE>:\2', debug_before) == \
        re.sub(coordinate, rb'NativeUfs.cpp:<LINE>:\2', debug_after), 'unexplained DWARF string drift'

    result = {
        'validation': 'self-checked',
        'claim': 'external=1 observation=0 translation unit is function-body equivalent to the accepted fix2 baseline',
        'diagnostic': args.diagnostic,
        'before_cell': str(args.before),
        'after_cell': str(args.after),
        'before_tree_root': roots[0],
        'after_tree_root': roots[1],
        'canonical_compile_arguments_equal': True,
        'archive_members': [{'before': members[0], 'after': members[1]}],
        'preprocessor_equal_except_panic_source_lines': True,
        'panic_line_pair_count': len(pairs),
        'panic_line_pairs_sample': sorted(pairs)[:5],
        'runtime_sections': runtime,
        'runtime_instruction_changes': changes,
        'runtime_instruction_change_count': len(changes),
        'text_bytes_all_accounted': True,
        'debug_strings_equal_after_tree_path_and_panic_line_substitution': True,
        'whole_object_equal': objects[0] == objects[1],
        'object_before_sha256': identity.digest(objects[0]),
        'object_after_sha256': identity.digest(objects[1]),
        'archive_before_sha256': identity.digest((args.before / 'libShengUfs.a').read_bytes()),
        'archive_after_sha256': identity.digest((args.after / 'libShengUfs.a').read_bytes()),
        'not_claimed': ['final link/load ABI', 'runtime behaviour', 'observation=1 cells'],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    (args.evidence / 'commands.json').write_text(json.dumps(log, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('validation', 'diagnostic', 'panic_line_pair_count',
                                             'runtime_instruction_change_count',
                                             'preprocessor_equal_except_panic_source_lines',
                                             'text_bytes_all_accounted')}, indent=2))


if __name__ == '__main__':
    sys.exit(main())
