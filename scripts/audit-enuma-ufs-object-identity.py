#!/usr/bin/env python3
"""Read-only Mach-O section/relocation comparison, including ar member identity.

Does not strip or rewrite objects. Debug differences are reported, not ignored
when claiming whole-object equality. Runtime section equality is a separate fact.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sections(data):
    assert data[:4] == b'\xcf\xfa\xed\xfe'
    result = {}
    offset = 32
    for _ in range(struct.unpack_from('<I', data, 16)[0]):
        cmd, size = struct.unpack_from('<II', data, offset)
        if cmd == 25:
            for i in range(struct.unpack_from('<I', data, offset + 64)[0]):
                item = offset + 72 + i * 80
                name, segment, addr, length, pos, align, rel, nrel, flags = struct.unpack_from('<16s16sQQIIIII', data, item)
                key = segment.rstrip(b'\0').decode() + '/' + name.rstrip(b'\0').decode()
                payload = b'' if flags & 255 in (1, 12) else data[pos:pos + length]
                result[key] = {'data': payload, 'relocations': data[rel:rel + 8*nrel],
                               'size': length, 'flags': flags, 'alignment': align, 'address': addr}
        offset += size
    return result


def ar_member(path):
    data = path.read_bytes()
    assert data[:8] == b'!<arch>\n'
    offset = 8
    entries = []
    member = None
    while offset < len(data):
        header = data[offset:offset+60]
        assert header[58:60] == b'`\n'
        size = int(header[48:58])
        payload = data[offset+60:offset+60+size]
        name = header[:16].decode().strip()
        if name.startswith('#1/'):
            count = int(name[3:])
            name = payload[:count].rstrip(b'\0').decode()
            payload = payload[count:]
        entries.append({'name': name, 'mtime': header[16:28].decode().strip(), 'sha256': digest(payload)})
        if name == 'NativeUfs.o':
            assert member is None
            member = payload
        offset += 60 + size + size % 2
    assert member is not None
    return member, entries


def compare(before, after):
    a, b = sections(before), sections(after)
    assert a.keys() == b.keys()
    result = []
    for name in a:
        x, y = a[name], b[name]
        row = {'section': name, 'size_before': x['size'], 'size_after': y['size'],
               'payload_equal': x['data'] == y['data'],
               'relocations_equal': x['relocations'] == y['relocations'],
               'flags_equal': x['flags'] == y['flags'], 'alignment_equal': x['alignment'] == y['alignment'],
               'sha256_before': digest(x['data']), 'sha256_after': digest(y['data'])}
        if not row['payload_equal'] and not name.startswith('__DWARF/'):
            differences = [i for i, (p, q) in enumerate(zip(x['data'], y['data'])) if p != q]
            row['first_differences'] = differences[:20]
            if differences:
                pos = differences[0]
                row['context_before'] = repr(x['data'][max(0,pos-60):pos+120])
                row['context_after'] = repr(y['data'][max(0,pos-60):pos+120])
        result.append(row)
    return {'object_before_sha256': digest(before), 'object_after_sha256': digest(after),
            'whole_object_equal': before == after, 'sections': result,
            'non_debug_payloads_equal': all(r['payload_equal'] for r in result if not r['section'].startswith('__DWARF/')),
            'all_section_relocations_equal': all(r['relocations_equal'] for r in result)}


def explain_default(before, after, diagnostic, output, run):
    """Fail closed: default PP differs ONLY in panic __LINE__ constants.

    Runtime text must differ ONLY in the matching MOV-immediate encodings;
    every other runtime section and runtime relocation must be identical.
    DWARF is retained and reported, not stripped to force an identity claim.
    """
    objects = [(p/'NativeUfs.o').read_bytes() for p in (before, after)]
    result = compare(*objects)
    commands = [json.loads((p/'compile-command.json').read_text()) for p in (before, after)]
    roots = [str(Path(c[2]).parents[2]) for c in commands]
    canonical = [[v.replace(root, '<ISOLATED-TREE>') for v in c] for c, root in zip(commands, roots)]
    assert canonical[0] == canonical[1], 'Non-path compiler argument drift'
    pp = []
    for i, command in enumerate(commands):
        cmd = list(command)
        j = cmd.index('-o')
        del cmd[j:j+2]
        cmd.remove('-c')
        cmd += ['-E', '-P', f'-DNATIVE_UFS_REUSE_DIAGNOSTIC={diagnostic}']
        recipe = Path(roots[i])/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/iokit/DEVELOPMENT/IOPlatformExpert.cpo.json'
        cwd = json.loads(recipe.read_text().strip().rstrip(','))['directory']
        text = run(cmd, f'identity-{diagnostic}-preprocess-{i}', cwd=cwd)
        pp.append(text)
    pattern = r'("NativeUfs\.cpp", )(\d+)'
    # A source location can only be normalized on a line expanded from panic.
    for text in pp:
        assert all('(panic)(' in line for line in text.splitlines() if re.search(pattern,line))
    assert re.sub(pattern,r'\1<SOURCE-LINE>',pp[0]) == re.sub(pattern,r'\1<SOURCE-LINE>',pp[1]), 'Default preprocessed logic changed'
    locations = [re.findall(pattern,text) for text in pp]
    assert len(locations[0]) == len(locations[1])
    pairs = {(int(a[1]),int(b[1])) for a,b in zip(*locations) if a[1] != b[1]}
    disassemblies = []
    for i, p in enumerate((before,after)):
        text = run(['llvm-objdump','--disassemble',p/'NativeUfs.o'], f'identity-{diagnostic}-disassemble-{i}')
        instructions = {}
        for line in text.splitlines():
            m = re.fullmatch(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} ){3}[0-9a-f]{2})\s+(.+)',line)
            if m:
                instructions[int(m[1],16)] = (m[2],m[3])
        assert instructions
        disassemblies.append(instructions)
    a,b = disassemblies
    assert a.keys() == b.keys()
    changes = []
    for address in a:
        if a[address] == b[address]:
            continue
        old = re.fullmatch(r'mov\s+(w\d+), #(\d+)',a[address][1])
        new = re.fullmatch(r'mov\s+(w\d+), #(\d+)',b[address][1])
        assert old and new and old[1]==new[1] and (int(old[2]),int(new[2])) in pairs, (address,a[address],b[address])
        changes.append({'offset':address,'before':a[address][1],'after':b[address][1]})
    for row in result['sections']:
        if row['section'].startswith('__DWARF/'):
            continue
        assert row['size_before']==row['size_after'] and row['flags_equal'] and row['alignment_equal'] and row['relocations_equal'], row
        if row['section'] != '__TEXT/__text':
            assert row['payload_equal'], row
    # Independently account for EVERY text-byte difference, not just parsed asm.
    sa,sb = (sections(blob) for blob in objects)
    ta,tb = sa['__TEXT/__text']['data'],sb['__TEXT/__text']['data']
    allowed = {r['offset']+i for r in changes for i in range(4)}
    assert all(i in allowed for i,(x,y) in enumerate(zip(ta,tb)) if x!=y)
    debug_a = sa['__DWARF/__debug_str']['data']
    debug_b = sb['__DWARF/__debug_str']['data']
    debug_a = debug_a.replace(roots[0].encode(),roots[1].encode())
    coordinate = rb'NativeUfs\.cpp:(\d+):(\d+)'
    coordinates = [re.findall(coordinate, text) for text in (debug_a,debug_b)]
    sources = [Path(c[2]).read_text().splitlines() for c in commands]
    assert len(coordinates[0]) == len(coordinates[1])
    for old,new in zip(*coordinates):
        assert old[1]==new[1] and sources[0][int(old[0])-1]==sources[1][int(new[0])-1], (old,new)
    # Clang prints lambda source coordinates into template display names.
    assert re.sub(coordinate,rb'NativeUfs.cpp:<LINE>:\2',debug_a) == re.sub(coordinate,rb'NativeUfs.cpp:<LINE>:\2',debug_b), 'Unexplained DWARF string drift'
    result.update(validation='self-checked',canonical_compile_arguments_equal=True,
                  default_preprocessor_equal_except_panic_source_lines=True,
                  runtime_instruction_changes=changes,debug_strings_equal_after_tree_path_and_verified_lambda_line_substitution=True,
                  explanation='panic __LINE__ MOV constants shift with inserted directives; DWARF paths/line tables/index offsets change. Not ar-mtime-only; no default logic/export change.')
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = []
    archives = []
    for path in (args.before, args.after):
        blob = path.read_bytes()
        if blob[:8] == b'!<arch>\n':
            blob, members = ar_member(path)
            archives.append({'path': str(path), 'archive_sha256': digest(path.read_bytes()), 'members': members})
        data.append(blob)
    result = compare(*data)
    result['archives'] = archives
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
