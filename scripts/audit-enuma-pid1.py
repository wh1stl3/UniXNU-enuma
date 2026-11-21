#!/usr/bin/env python3
"""Audit actual bound artifacts. Exit 2 means required manual review, NOT PASS.

No build/device operations. Instruction checks are deliberately narrower than
control-flow/argument-provenance review; those items are exported as pending.
"""
import argparse
import bisect
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bound_file(record, key):
    path = Path(record[key])
    if digest(path) != record[key + '_sha256']:
        raise ValueError('stale/mismatched bound artifact: ' + key)
    return path


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def direct_branch(word, pc):
    if word & 0x7c000000 == 0x14000000:  # B / BL imm26
        return pc + 4 * signed(word & 0x3ffffff, 26)
    if word & 0xff000010 == 0x54000000 or word & 0x7e000000 == 0x34000000:
        return pc + 4 * signed((word >> 5) & 0x7ffff, 19)  # B.cond / CBZ
    if word & 0x7e000000 == 0x36000000:
        return pc + 4 * signed((word >> 5) & 0x3fff, 14)  # TBZ / TBNZ
    return None


def check_leaf(words, start, end):
    """Reject calls, external tail branches and unaudited indirect transfers.

    Local LLSC retry branches are legal. This is not a wait-free proof.
    """
    for i, word in enumerate(words):
        pc = start + 4 * i
        if word & 0xfc000000 == 0x94000000:
            raise ValueError(f'out-of-line call at {pc:#x}')
        target = direct_branch(word, pc)
        if target is not None and not start <= target < end:
            raise ValueError(f'external branch/tail call at {pc:#x} -> {target:#x}')
        if word & 0xfe000000 == 0xd6000000 and word != 0xd65f03c0:
            raise ValueError(f'unaudited indirect transfer at {pc:#x}')


def require_hooks(calls):
    for name in ('_enuma_pid1_begin', '_enuma_pid1_svc', '_enuma_pid1_exit'):
        if not calls.get(name):
            raise ValueError('missing actual collector hook: ' + name)


class Image:
    def __init__(self, path):
        self.data = Path(path).read_bytes()
        if struct.unpack_from('<II', self.data) != (0xfeedfacf, 0x100000c):
            raise ValueError('expected ARM64 Mach-O')
        self.sections = [None]
        offset = 32
        symtab = None
        for _ in range(struct.unpack_from('<I', self.data, 16)[0]):
            cmd, size = struct.unpack_from('<II', self.data, offset)
            if cmd == 0x19:
                prot, count = struct.unpack_from('<II', self.data, offset + 60)
                for i in range(count):
                    sec = offset + 72 + 80 * i
                    name = self.data[sec:sec + 16].split(b'\0')[0].decode()
                    segment = self.data[sec + 16:sec + 32].split(b'\0')[0].decode()
                    addr, length, fileoff = struct.unpack_from('<QQI', self.data, sec + 32)
                    flags = struct.unpack_from('<I', self.data, sec + 64)[0]
                    self.sections.append(dict(name=name, segment=segment, address=addr,
                                              size=length, offset=fileoff, flags=flags, prot=prot))
            elif cmd == 2:
                symtab = struct.unpack_from('<IIII', self.data, offset + 8)
            offset += size
        if symtab is None:
            raise ValueError('missing symbol table')
        symoff, count, stroff, _ = symtab
        self.symbols = {}
        for i in range(count):
            string, kind, section, _, value = struct.unpack_from('<IBBHQ', self.data, symoff + 16 * i)
            if kind & 0xe0 or kind & 0x0e != 0x0e:
                continue
            start = stroff + string
            name = self.data[start:self.data.index(b'\0', start)].decode(errors='replace')
            self.symbols[name] = (value, self.sections[section])
        self.text_symbols = sorted((value, name) for name, (value, sec) in self.symbols.items()
                                   if sec['name'] == '__text' and name.startswith('_'))
        self.addresses = sorted(set(v for v, _ in self.text_symbols))
        self.names_at = {v: name for v, name in self.text_symbols}

    def owner(self, pc):
        index = bisect.bisect_right(self.addresses, pc) - 1
        if index < 0:
            raise ValueError('no instruction owner')
        return self.names_at[self.addresses[index]]

    def function(self, name):
        start, sec = self.symbols[name]
        index = bisect.bisect_right(self.addresses, start)
        end = self.addresses[index] if index < len(self.addresses) else sec['address'] + sec['size']
        end = min(end, sec['address'] + sec['size'])
        offset = sec['offset'] + start - sec['address']
        code = self.data[offset:offset + end - start]
        return start, end, list(w[0] for w in struct.iter_unpack('<I', code))

    def calls(self, names):
        targets = {self.symbols[n][0]: n for n in names if n in self.symbols}
        result = {n: [] for n in names}
        for sec in self.sections[1:]:
            if sec['name'] != '__text':
                continue
            code = self.data[sec['offset']:sec['offset'] + sec['size']]
            for i, (word,) in enumerate(struct.iter_unpack('<I', code)):
                if word & 0x7c000000 == 0x14000000:
                    pc = sec['address'] + 4 * i
                    target = direct_branch(word, pc)
                    if target in targets:
                        result[targets[target]].append(dict(pc=pc, owner=self.owner(pc),
                                                           transfer='bl' if word & 0x80000000 else 'b'))
        return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record', required=True, type=Path)
    p.add_argument('--tree', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--objdump', type=Path, default=Path('/usr/bin/llvm-objdump'))
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    # Never leave a prior successful-looking result after a failed rerun.
    result_path = a.out / 'audit.json'
    result_path.write_text(json.dumps({'status': 'incomplete', 'manual_pending': ['audit did not complete']}) + '\n')
    record = json.loads(a.record.read_text())
    paths = {k: bound_file(record, k) for k in ('native', 'prelink', 'metadata', 'patch', 'inputs_stamp')}
    current_patch = Path(__file__).resolve().parents[1] / 'patches/xnu/enuma-pid1-observer.patch'
    if digest(current_patch) != record['patch_sha256']:
        raise ValueError('build record does not match current device patch')
    metadata = json.loads(paths['metadata'].read_text())
    if metadata['native_sha256'] != record['native_sha256']:
        raise ValueError('prelink metadata/native mismatch')
    stamps = json.loads(paths['inputs_stamp'].read_text())['patches']
    if not any(Path(e['path']).name == current_patch.name and e['sha256'] == record['patch_sha256'] for e in stamps):
        raise ValueError('prepared-source stamp does not select this patch')
    required_sources = {'startup.c', 'bsd_init.c', 'sleh.c', 'kern_exit.c', 'video_console.c', 'kern_proc.c'}
    if {Path(i['source']).name for i in record['source_objects']} != required_sources:
        raise ValueError('missing required source/object build bindings')
    for item in record['source_objects']:
        if not Path(item['source']).resolve().is_relative_to((a.tree / '.cache/xnu-work').resolve()):
            raise ValueError('source record belongs to a different tree')
        for key in ('source', 'object', 'compile_record'):
            bound_file(item, key)
    if any(any(n in c for n in ('GopFramebuffer', 'IOFramebuffer', 'IOMobileFramebuffer')) for c in metadata['components']):
        raise ValueError('unexpected display component')
    native, linked = Image(paths['native']), Image(paths['prelink'])
    hooks = ('_enuma_pid1_begin', '_enuma_pid1_svc', '_enuma_pid1_exit')
    for name in hooks:
        if name not in native.symbols or name not in linked.symbols:
            raise ValueError('missing native/prelink symbol: ' + name)
    data_symbols = {n: (v, sec) for n, (v, sec) in native.symbols.items()
                    if n.startswith(('_enuma_pid1_state', '_enuma_pid1_console', '_enuma_pid1_lock_ready'))}
    if len(data_symbols) < 3 or native.symbols['_enuma_pid1_state'][0] % 8:
        raise ValueError('missing/alignment-invalid permanent state')
    for _, sec in data_symbols.values():
        if not (sec['segment'] == '__DATA' and sec['flags'] & 0xff == 1 and sec['prot'] & 2):
            raise ValueError('state is not permanent writable zero-fill BSS')

    callees = hooks + ('_initialize_screen', '_task_clear_return_wait', '_current_cached_proc_cred_update',
                       '_proc_transend', '_proc_getpid', '_proc_pid', '_proc_uniqueid', '_get_bsdthreadtask_info')
    calls = native.calls(callees)
    require_hooks(calls)
    linked_calls = linked.calls(callees)
    require_hooks(linked_calls)
    def locations(image, records):
        return sorted((c['owner'], c['pc'] - image.symbols[c['owner']][0], c['transfer']) for c in records)
    for name in hooks:
        if locations(native, calls[name]) != locations(linked, linked_calls[name]):
            raise ValueError('native/prelink actual collector site mismatch: ' + name)
    startup_calls = [c for c in calls['_initialize_screen'] if c['owner'] == '_kernel_bootstrap_thread']
    if len(startup_calls) < 2:
        raise ValueError('missing actual initialize_screen sites in kernel_bootstrap_thread')
    for hook, owners in [('_enuma_pid1_begin', ('_bsd_init', '_bsd_utaskbootstrap')),
                         ('_enuma_pid1_svc', ('_sleh_synchronous', '_handle_svc')),
                         ('_enuma_pid1_exit', ('_exit_with_reason',))]:
        if any(c['owner'] not in owners for c in calls[hook]):
            raise ValueError('unexpected collector owner: ' + hook + repr(calls[hook]))
    begin = calls['_enuma_pid1_begin'][0]
    if not any(c['owner'] == begin['owner'] and c['pc'] > begin['pc'] for c in calls['_task_clear_return_wait']):
        raise ValueError('missing actual PID1 release after begin')
    svc = calls['_enuma_pid1_svc'][0]
    if not any(c['owner'] == svc['owner'] and c['pc'] < svc['pc'] for c in calls['_current_cached_proc_cred_update']):
        raise ValueError('missing actual credential update before SVC collector')
    exit_site = calls['_enuma_pid1_exit'][0]
    if not any(c['owner'] == exit_site['owner'] and c['pc'] > exit_site['pc'] for c in calls['_proc_transend']):
        raise ValueError('missing actual proc_transend after exit collector')

    leaf_names = ('_enuma_pid1_svc', '_enuma_pid1_exit', '_proc_getpid')
    for name in leaf_names:
        start, end, words = native.function(name)
        check_leaf(words, start, end)
        start, end, words = linked.function(name)
        check_leaf(words, start, end)
    export = set(leaf_names) | set(hooks) | {'_enuma_pid1_observer', '_kernel_bootstrap_thread', '_proc_uniqueid'}
    export.update(c['owner'] for name in hooks for c in calls[name])
    if '_get_bsdthreadtask_info' in native.symbols:
        export.add('_get_bsdthreadtask_info')
    # Identity getters may contain existing zone validation and panic-only
    # branches. Do not label them leaf/pass or ban the syscall's old dispatch.
    # Export the actual direct chain (panic bodies not recursively expanded),
    # with unresolved/indirect edges explicitly pending manual review.
    identity_edges = {}
    queue = [(n, 0) for n in ('_proc_getpid', '_proc_uniqueid', '_get_bsdthreadtask_info') if n in native.symbols]
    while queue:
        name, depth = queue.pop()
        if name in identity_edges:
            continue
        start, end, words = native.function(name)
        edges = []
        for i, word in enumerate(words):
            pc = start + i * 4
            target = direct_branch(word, pc)
            if target is not None and (word & 0xfc000000 == 0x94000000 or not start <= target < end):
                callee = native.names_at.get(target)
                edges.append({'pc': hex(pc), 'target': hex(target), 'callee': callee})
                if callee:
                    export.add(callee)
                    if depth < 4 and 'panic' not in callee:
                        queue.append((callee, depth + 1))
            if word & 0xfe000000 == 0xd6000000 and word != 0xd65f03c0:
                edges.append({'pc': hex(pc), 'indirect': True, 'manual_review_required': True})
        identity_edges[name] = edges
    exports = {}
    for name in sorted(export):
        start, end, _ = native.function(name)
        text = subprocess.check_output([str(a.objdump), '--disassemble-symbols=' + name,
                                        '--no-show-raw-insn', str(paths['native'])], text=True)
        if name not in text:
            raise ValueError('disassembler failed to export ' + name)
        if name in ('_enuma_pid1_svc', '_enuma_pid1_exit'):
            if not re.search(r'\b(?:ldar|ldaxr|ldxr|ldadd\w*|cas\w*)\s', text):
                raise ValueError('missing actual inline atomic instructions: ' + name)
        if name == '_enuma_pid1_svc' and not re.search(r'\b(?:ldxr|ldaxr|ldadd\w*)\s+x\d', text):
            raise ValueError('missing actual 64-bit counter RMW')
        path = a.out / (name.lstrip('_') + '.disasm.txt')
        path.write_text(text)
        exports[name] = {'start': hex(start), 'end': hex(end), 'path': str(path), 'sha256': digest(path)}

    # Macros are tied to compile records/objects and actual artifact hashes above,
    # but are NOT a substitute for instruction/argument review of the linked code.
    startup = next(i for i in record['source_objects'] if Path(i['source']).name == 'startup.c')
    compile_record = json.loads(Path(startup['compile_record']).read_text().strip().rstrip(','))
    command = compile_record['arguments'].copy()
    command.remove('-c')
    command[command.index('-o') + 1] = '-'
    with (a.out / 'startup.preprocess.log').open('w') as diagnostics:
        macros = subprocess.check_output(command + ['-E', '-dM'], cwd=compile_record['directory'], text=True,
                                         stderr=diagnostics)
    (a.out / 'startup.macros.txt').write_text(macros)
    if '#define ENUMA_PID1_DIAGNOSTIC 1' not in macros or '#define XNU_BOOT_PROGRESS 0' not in macros:
        raise ValueError('unexpected diagnostic/boot-progress macro')
    result = dict(status='manual-review-required', self_checked=True, build_record=str(a.record),
                  build_record_sha256=digest(a.record), bound_sha256={k: record[k + '_sha256'] for k in paths},
                  actual_calls=calls, actual_prelinked_calls=linked_calls,
                  exported_functions=exports, identity_chain_manual_review=identity_edges,
                  bss={n: {'address': hex(v), 'section': s} for n, (v, s) in data_symbols.items()},
                  automated_checks=['artifact/metadata/source-object/patch binding', 'actual named callsites and relative release/cred/transend ordering',
                                    'RW zero-fill BSS/alignment', 'collector/proc_getpid leaf ranges: no calls/external tails/unaudited indirect transfers; inline collector atomics and 64-bit counter RMW',
                                    'bound preprocessing macro values', 'no framebuffer driver component'],
                  manual_pending=['kernel_bootstrap_thread actual x0=NULL,w1=2 TextMode then x0=NULL,w1=4 Acquire and dominance before PID1',
                                  'actual SVC non-platform path, proc identity/PC/signed-trap argument provenance before dispatch',
                                  'actual PID1 begin/return-wait release identity and ordering across branches',
                                  'actual selected exit thread p_xstat store then collector numeric p/rv/reason args before proc_transend',
                                  'identity accessor read-only proc/proc_ro lifetime and complete added argument-extraction call chain'])
    result_path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'audit': str(result_path), 'manual_pending': result['manual_pending']}, indent=2))
    return 2


if __name__ == '__main__':
    sys.exit(main())
