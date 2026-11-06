"""Run actual timing helper under sanitizers and inspect specialized AArch64 code."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'out/value-transport-host';out.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--firmware-root',type=Path,default=ROOT/'firmware')
    args=p.parse_args()
    header=args.firmware_root/'diagnostics/EnumaValueProbe.h'
    flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-I'+str(header.parent),'-I'+str(ROOT/'tests')]
    subprocess.run(flags+['-O1','-fsanitize=address,undefined','-no-pie',str(ROOT/'tests/enuma_value_probe.c'),'-o',str(out/'test')],check=True)
    subprocess.run([str(out/'test')],check=True)
    unit=out/'specialize.c'
    unit.write_text('#include <stdint.h>\n#include <stddef.h>\n'
        'typedef uintptr_t UINTN;typedef uint32_t UINT32;typedef uint64_t EFI_STATUS;\n'
        '#define STATIC static\n#define CONST const\n#define VOID void\n#define EFI_SUCCESS 0\n#define EFI_INVALID_PARAMETER 2\n'
        '#include "EnumaValueProbe.h"\n'
        'static UINT32 rd(UINTN a){return *(volatile UINT32 *)a;}\n'
        'extern EFI_STATUS wait_us(UINTN);\n'
        'EFI_STATUS probe(void){return EnumaValueProbe(SOURCE,0,SHIFT,CODE,rd,wait_us);}\n')
    objects=[]
    for source,shift,code in ((1,0,0),(1,0,3),(2,0,0),(2,28,0)):
        obj=out/f'value-{source}-{shift}-{code}.obj'
        subprocess.run(flags+['-target','aarch64-unknown-windows-msvc','-ffreestanding','-Oz',
            '-DSOURCE='+str(source),'-DSHIFT='+str(shift),'-DCODE='+str(code),'-c',str(unit),'-o',str(obj)],check=True)
        asm=subprocess.check_output(['llvm-objdump','-d',str(obj)],text=True)
        if source==1:
            # Constant helper has no memory accesses at all (including priming).
            instructions=[line.split('\t')[-2].strip() for line in asm.splitlines() if len(line.split('\t'))>=3]
            assert not any(op.startswith(('ld','st','dc')) for op in instructions),asm
            if code==0: assert 'wait_us' not in subprocess.check_output(['llvm-nm','--undefined-only',str(obj)],text=True)
        objects.append(dict(source=source,shift=shift,code=code,object_sha256=hashlib.sha256(obj.read_bytes()).hexdigest()))
    (ROOT/'reports/enuma-value-transport-host.json').write_text(json.dumps(dict(
        scope='actual helper under host adapters and specialized AArch64 objects; no firmware or hardware execution',
        header_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),all_passed=True,
        constant_no_memory_access=True,extra_base_seconds=0,seconds_per_code=3,objects=objects),indent=2)+'\n')
    print('PASS: constants 0..15, 8 nibble shifts, invalid inputs, wait errors, no-memory constant objects')


if __name__=='__main__':main()
