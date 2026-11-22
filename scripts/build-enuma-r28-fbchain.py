#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause-Patent
"""Replay r26's isolated recipe with the r28 framebuffer instrumentation."""
import argparse
from pathlib import Path
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
R26 = runpy.run_path(str(HERE / 'build-enuma-r26-fbcount.py'))
DEVICE, OUT = R26['DEVICE'], R26['OUT']
BASE = OUT / 'ufs-sm8250-launchd-fbcount-20261122-r26'
DEFAULT = OUT / 'ufs-sm8250-launchd-fbcount-20261123-r28'

# Keep the pinned r26 replay intact; splice only r28's additional patch and
# ensure the link is checked before the prelink and package stages.
text = (HERE / 'build-enuma-r26-fbcount.py').read_text()
needle = "    cc = steps['compile-kern_exec.o']\n"
replacement = """    shutil.copyfile(DEVICE / 'package/EnumaFbChain.inc', bsd / 'EnumaFbChain.inc')
    exec_path = bsd / 'kern_exec.c'
    source = exec_path.read_text()
    assert source.count('EnumaFbCount.inc') == 1
    exec_path.write_text(source.replace('EnumaFbCount.inc', 'EnumaFbChain.inc'))
    display_path = display / 'NativeLegacyDisplay.cpp'
    source = display_path.read_text()
    replacements = [
        ('extern "C" void enuma_fb_record_client(void);',
         'extern "C" unsigned int enuma_fb_record_client(uint32_t);\\n'
         'extern "C" void enuma_fb_record_client_done(unsigned int,int);', 1),
        ('enuma_fb_record_client();',
         'unsigned int enuma_fb_open_slot=enuma_fb_record_client(type);', 1),
        ('native_legacy_client_observed(status,status==kIOReturnSuccess && client?*client:nullptr);return status;',
         'enuma_fb_record_client_done(enuma_fb_open_slot,status);\\n'
         '        native_legacy_client_observed(status,status==kIOReturnSuccess && client?*client:nullptr);return status;', 1),
        ('extern "C" void enuma_fb_record_swap(void);',
         'extern "C" void enuma_fb_record_swap(void);\\n'
         'extern "C" void enuma_fb_record_refresh(void);\\n'
         'extern "C" void enuma_fb_record_kick(void);\\n'
         'extern "C" void enuma_fb_record_scanout(void);', 1),
        ('bool getRefreshAttributes(uint64_t *words,bool fixed) override {',
         'bool getRefreshAttributes(uint64_t *words,bool fixed) override {\\n'
         '        enuma_fb_record_refresh();', 1),
        ('void kickSwapQueue() override {',
         'void kickSwapQueue() override {\\n        enuma_fb_record_kick();', 1),
        ('!native_legacy_prepare_scanout()',
         '!(enuma_fb_record_scanout(),native_legacy_prepare_scanout())', 4),
    ]
    for old, new, expected in replacements:
        assert source.count(old) == expected, (old, source.count(old))
        source = source.replace(old, new)
    display_path.write_text(source)

    cc = steps['compile-kern_exec.o']
"""
assert text.count(needle) == 1
text = text.replace(needle, replacement)
needle = "        call(tag, argv, out if tag == 'prelink' else step['cwd'])\n"
replacement = needle + """        if tag == 'link':
            undefined = call('link-undefined', ['llvm-nm', '-u', out / 'native.macho'])
            assert not undefined.strip(), undefined
            symbols = call('link-symbols', ['llvm-nm', out / 'native.macho'])
            assert '__GLOBAL__sub_I_NativeLegacyDisplay.cpp' in symbols
"""
assert text.count(needle) == 1
text = text.replace(needle, replacement)
namespace = {'__name__': 'r28_recipe', '__file__': str(HERE / 'build-enuma-r26-fbcount.py')}
exec(compile(text, namespace['__file__'], 'exec'), namespace)

def check_linked(path, call):
    formats = ['enuma-fb: begin\n', 'enuma-fb: end\n'] + [
        'enuma-fb: ' + key + '=%llu comm=%s\n'
        for key in ('start', 'open', 'refresh', 'kick', 'scanout', 'swap')]
    blob = path.read_bytes()
    formats += ['enuma-fb: open[%u]=%s pid=%d type=%u ret=%d\n',
                'enuma-fb: open[%u]=-\n']
    counts = {fmt: blob.count(fmt.encode() + b'\0') for fmt in formats}
    assert all(n == 1 for n in counts.values()) and blob.count(b'enuma-fb: ') == 10, counts
    assert not call('undefined-' + path.name, ['llvm-nm', '-u', path]).strip()
    _, symbols = namespace['H']['symbols'](blob, namespace['H']['macho'](blob))
    assert not [s for s in symbols if not s[1] & 0xe0 and s[1] & 0x0e == 0]
    return {'formats': counts, 'undefined_including_weak': 0}

namespace['check_linked'] = check_linked

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=DEFAULT)
    parser.add_argument('--dtb', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    assert out.parent == OUT and not out.exists()
    before = namespace['snapshot'](p for p in sorted(BASE.rglob('*')) if p.is_file())
    namespace['build'](out, args.dtb.resolve())
    assert before == namespace['snapshot'](p for p in sorted(BASE.rglob('*')) if p.is_file())
    print('r26 files unchanged:', len(before))
