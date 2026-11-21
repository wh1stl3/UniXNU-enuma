#!/usr/bin/env python3
"""Compile/test the actual helper and console reader extracted from the XNU patch.

Host only. Requires a C11 compiler and pthreads; never opens a device.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', default='cc')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    device = Path(__file__).resolve().parents[1]
    patch = (device / 'patches/xnu/enuma-pid1-observer.patch').read_text()
    additions = {}
    filename = None
    for line in patch.splitlines():
        if line.startswith('+++ b/'):
            filename = line[6:]
            additions[filename] = []
        elif line.startswith('+') and not line.startswith('+++') and filename:
            additions[filename].append(line[1:])
    helper = '\n'.join(additions['osfmk/kern/enuma_pid1.h']) + '\n'
    video = '\n'.join(additions['osfmk/console/video_console.c']) + '\n'
    start = video.index('static void\nenuma_pid1_write(')
    end = video.index('\nstatic void\nenuma_pid1_observer', start)
    reader = video[start:end]
    begin_start = video.index('void\nenuma_pid1_begin(')
    begin_end = video.index('\nvoid\nenuma_pid1_svc(', begin_start)
    begin = video[begin_start:begin_end]
    assert 'vcputc(' not in reader and 'gc_putchar(' in reader
    assert 'col += 16' in reader and 'VCPUTC_LOCK_LOCK();' in reader
    assert 'thread_block(' not in reader and 'snprintf(' not in reader
    assert '__ATOMIC_ACQUIRE' in helper and '__ATOMIC_RELEASE' in helper
    startup = '\n'.join(additions['osfmk/kern/startup.c'])
    assert 'ENUMA_PID1_DIAGNOSTIC' in startup and 'kPETextMode' in startup
    # The unchanged acquire remains context, following the new TextMode call.
    assert 'initialize_screen(NULL, kPETextMode);\n+#endif\n \tinitialize_screen(NULL, kPEAcquireScreen);' in patch
    assert video.index('enuma_pid1_lock_ready, __ATOMIC_ACQUIRE', video.index('int ep_lock')) < video.index('int ep_first_mapping')
    out = args.out or device / '.cache/pid1-host'
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='compile-', dir=out) as name:
        temp = Path(name)
        (temp / 'enuma_pid1.h').write_text(helper)
        (temp / 'reader.inc').write_text(reader)
        (temp / 'begin.inc').write_text(begin)
        exe = temp / 'enuma-pid1-test'
        command = [args.cc, '-std=c11', '-O2', '-g', '-Wall', '-Wextra', '-Werror',
                   '-pthread', '-I', str(temp), str(device / 'scripts/tests/enuma-pid1.c'), '-o', str(exe)]
        print(' '.join(command), flush=True)
        subprocess.run(command, check=True)
        subprocess.run([str(exe)], check=True, timeout=30)
    print('enuma PID1: actual helper + console reader tests PASS', flush=True)


if __name__ == '__main__':
    main()
