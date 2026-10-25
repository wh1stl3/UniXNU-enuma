"""Build the unbound production writer on host (ASan/UBSan) and AArch64.

Run in WSL. Outputs remain under out/; no device commands or physical RAM access.
The compatibility Base.h shim checks C logic and layout, not a whole EDK build.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / 'out/ramoops-audit/host'
    (output / 'Library').mkdir(parents=True, exist_ok=True)
    (output / 'Base.h').write_text('''#include <stdint.h>
#include <stddef.h>
#define STATIC static
#define IN
#define CONST const
#define VOID void
#define STATIC_ASSERT _Static_assert
#define OFFSET_OF offsetof
typedef uint8_t UINT8;
typedef uint32_t UINT32;
typedef uintptr_t UINTN;
''')
    (output / 'Library/BaseLib.h').write_text(
        'static inline void MemoryFence(void) { __atomic_thread_fence(__ATOMIC_SEQ_CST); }\n')
    source = ROOT / 'tests/ramoops_buffer_test.c'
    common = ['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', str(output)]
    host = common + ['-fsanitize=address,undefined', '-g', str(source), '-o', str(output / 'ring-test')]
    subprocess.run(host, check=True, cwd=ROOT)
    result = subprocess.check_output([str(output / 'ring-test')], text=True, cwd=ROOT).strip()
    edk = ROOT / 'out/firmware-build/Mu_Basecore/MdePkg/Include'
    if not (edk / 'Base.h').is_file():
        raise FileNotFoundError('fixed firmware build EDK headers unavailable: ' + str(edk))
    arm = ['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', str(edk),
           '-I', str(edk / 'AArch64'), '-fshort-wchar',
           '--target=aarch64-none-elf', '-ffreestanding', '-DRAMOOPS_COMPILE_ONLY',
                    '-c', str(source), '-o', str(output / 'ring-aarch64.o')]
    subprocess.run(arm, check=True, cwd=ROOT)
    files = ['firmware/diagnostics/EnumaRamoopsBuffer.h', 'tests/ramoops_buffer_test.c',
             'scripts/test_ramoops_buffer.py']
    report = dict(scope='unbound writer host tests and AArch64 object; no FD, mapping or device execution',
                  host_result=result, sanitizers=['address', 'undefined'],
                  host_command=host, aarch64_command=arm,
                  sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
                  hardware_verified=False, production_serial_backend='Null', physical_address_in_writer=False)
    # Commands contain local public checkout paths, no serials or raw log contents.
    (ROOT / 'reports/enuma-ramoops-buffer-tests.json').write_text(json.dumps(report, indent=2) + '\n')
    print(result)
    print('PASS: AArch64 freestanding object; not an execution-qualified firmware image')


if __name__ == '__main__':
    main()
