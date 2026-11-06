# Offline DXE journal and production hook checks. No device/FD qualification.
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    out = ROOT / 'out/boot-journal-tests'
    out.mkdir(parents=True, exist_ok=True)
    (out / 'Uefi.h').write_text('''#ifndef MOCK_UEFI_H
#define MOCK_UEFI_H
#include <stdint.h>
#include <stddef.h>
#define STATIC static
#define EFIAPI
#define EFI_NATIVE_INTERFACE 0
typedef void *EFI_HANDLE;
#define CONST const
#define VOID void
#define TRUE 1
#define FALSE 0
#define MAX_UINT64 UINT64_MAX
#define EFI_ERROR(s) (((s) >> 63) != 0)
typedef uint8_t UINT8; typedef uint32_t UINT32; typedef uint64_t UINT64;
typedef uintptr_t UINTN; typedef UINT64 EFI_STATUS; typedef uint8_t BOOLEAN;
typedef char CHAR8;
typedef struct { UINT32 Data1; uint16_t Data2,Data3; UINT8 Data4[8]; } EFI_GUID;
#endif
''')
    results = []
    commands = []
    def run(cmd):
        commands.append(cmd)
        return subprocess.check_output(cmd, cwd=out, text=True, stderr=subprocess.STDOUT).strip()
    common = ['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function']
    for file, defines, tag in [('boot_journal_test.c', [], 'journal'),
                               ('boot_journal_hook_test.c', ['-DENUMA_BOOT_JOURNAL=1'], 'hook-on'),
                               ('boot_journal_hook_test.c', ['-DENUMA_BOOT_JOURNAL=0'], 'hook-off'),
                               ('boot_journal_hook_test.c', ['-DENUMA_BOOT_JOURNAL=1','-DENUMA_BOOT_LOG_REPLAY=1'], 'protocol-on'),
                               ('boot_journal_hook_test.c', ['-DENUMA_BOOT_JOURNAL=1','-DENUMA_BOOT_LOG_REPLAY=1','-DENUMA_TEST_PROTOCOL_FAIL=1'], 'protocol-fail')]:
        source = str(ROOT / 'tests' / file)
        binary = str(out / tag)
        run(common + ['-I', str(out), '-fsanitize=address,undefined', '-fno-pie', '-no-pie', '-g'] + defines + [source, '-o', binary])
        results.append(run([binary]))
        edk = ROOT / 'out/firmware-build/Mu_Basecore/MdePkg/Include'
        run(common + ['--target=aarch64-none-elf', '-ffreestanding', '-fshort-wchar',
                      '-I', str(edk), '-I', str(edk / 'AArch64'), '-DBOOT_JOURNAL_COMPILE_ONLY'] +
                      defines + ['-c', source, '-o', str(out / (tag + '-aarch64.o'))])
    bad = common + ['-I', str(out), '-DENUMA_BOOT_JOURNAL=2', '-c',
                    str(ROOT / 'tests/boot_journal_hook_test.c'), '-o', str(out / 'invalid.o')]
    commands.append(bad)
    invalid = subprocess.run(bad, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert invalid.returncode != 0 and 'Invalid boot journal selector' in invalid.stdout
    files = ['firmware/diagnostics/EnumaBootJournal.h', 'firmware/diagnostics/EnumaDispatchDetailCheckpoint.h',
             'firmware/Resources/Scripts/enuma_preflight.py', 'firmware/Resources/Scripts/build_enuma_firmware.py',
             'tests/boot_journal_test.c', 'tests/boot_journal_hook_test.c', 'scripts/test_boot_journal.py']
    report = dict(scope='host ASan/UBSan execution and pinned EDK AArch64 objects; no whole FD/QEMU/device run',
                  results=results, aarch64_objects=5, invalid_selector_rejected=True,
                  commands=commands, sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
                  hardware_executed=False, pixel_access=False, global_debug_connected=False, screen_sink=False,
                  default_enabled=False, concurrency='single writer, quiescent copy, immutable replay snapshot')
    (ROOT / 'reports/enuma-boot-journal-tests.json').write_text(json.dumps(report, indent=2)+'\n')
    print('\n'.join(results))
    print('PASS: five AArch64 objects with pinned EDK headers; invalid selector rejected')

if __name__ == '__main__':
    main()
