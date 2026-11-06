"""WSL: explicit R-002 temporary stock Android Image hook; no device actions.

Preserve original kernel placement and all stock bytes except its first branch
and Image size. Hook/stack live after the original Image size, used only before
stock entry. Preserve stock v3 header, command line, OS version and ramdisk.
The original vendor_boot and all partitions remain external and untouched.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
if sys.version_info < (3,11):
    import tomli
    sys.modules['tomllib']=tomli
import tomllib

ROOT=Path(__file__).resolve().parents[1]
STOCK_SHA='8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959'


def sha(data):return hashlib.sha256(data).hexdigest()
def page(n):return (n+4095)&~4095


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approved-r002',action='store_true',required=True)
    parser.add_argument('--stock-boot',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--seed-marker',action='store_true',help='R-002 only: write fixed 16-byte marker after FDT reservation, before Linux')
    args=parser.parse_args();output=args.output.resolve()
    if not output.is_relative_to((ROOT/'out').resolve()) or output.exists():raise ValueError('new output under own out/ required')
    board=tomllib.loads((ROOT/'board.toml').read_text())
    if board['diagnostics']!={'persistent_log':{'enabled':False,'source_region':'Log Buffer',
        'physical_base':'0x9fff7000','size':'0x8000'}}:raise ValueError('outside R-002 configuration')
    stock=args.stock_boot.read_bytes()
    if sha(stock)!=STOCK_SHA or stock[:8]!=b'ANDROID!' or struct.unpack_from('<I',stock,40)[0]!=3:
        raise ValueError('unreviewed stock boot')
    ks,rs=struct.unpack_from('<II',stock,8)
    kernel=stock[4096:4096+ks];ramdisk=stock[4096+page(ks):4096+page(ks)+rs]
    if len(kernel)!=ks or len(ramdisk)!=rs or kernel[56:60]!=b'ARM\x64':raise ValueError('stock sections differ')
    code0=struct.unpack_from('<I',kernel)[0];original_size=struct.unpack_from('<Q',kernel,16)[0]
    if code0&0xfc000000!=0x14000000 or original_size<len(kernel) or original_size%4096:
        raise ValueError('unsupported stock Image placement/entry')
    imm=code0&0x3ffffff
    if imm&(1<<25):imm-=1<<26
    entry=imm*4
    if not 64<=entry<len(kernel) or original_size>=1<<27:raise ValueError('branch outside stock kernel')
    out=ROOT/'out/log-readback'/('android-hook-seed-build' if args.seed_marker else 'android-hook-build');out.mkdir(parents=True,exist_ok=True)
    compiler=['clang','--target=aarch64-none-elf','-O2','-ffreestanding','-fno-builtin',
        '-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables',
        '-mgeneral-regs-only','-Wall','-Wextra','-Werror','-DENUMA_ARM64_ENTRY']
    if args.seed_marker:compiler+=['-DENUMA_SEED_MARKER']
    for source in ('fdt_reserve.c','android_fdt_entry.S'):
        subprocess.run([*compiler,'-c',str(ROOT/'diagnostics'/source),'-o',str(out/(source+'.o'))],check=True)
    script=f'''ENTRY(_start)
kernel_entry = {entry};
SECTIONS {{
 . = {original_size};
 .text : {{ *(.text.entry) *(.text*) }}
 .rodata : {{ *(.rodata*) }}
 .data : {{ *(.data*) }}
 .bss (NOLOAD) : {{ *(.bss*) *(COMMON) }}
 __end = .;
 /DISCARD/ : {{ *(.comment) *(.note*) *(.eh_frame*) }}
}}
'''
    (out/'hook.ld').write_text(script)
    subprocess.run(['ld.lld','-T',str(out/'hook.ld'),str(out/'android_fdt_entry.S.o'),
        str(out/'fdt_reserve.c.o'),'-o',str(out/'hook.elf')],check=True)
    undefined=subprocess.check_output(['llvm-nm','-u',str(out/'hook.elf')],text=True)
    if undefined.strip():raise ValueError('undefined hook symbols: '+undefined)
    symbols=subprocess.check_output(['llvm-nm','-n',str(out/'hook.elf')],text=True)
    end=int(next(line.split()[0] for line in symbols.splitlines() if line.endswith(' __end')),16)
    start=int(next(line.split()[0] for line in symbols.splitlines() if line.endswith(' _start')),16)
    if start!=original_size or end-start>0x10000:raise ValueError('unexpected hook layout')
    subprocess.run(['llvm-objcopy','-O','binary',str(out/'hook.elf'),str(out/'hook.bin')],check=True)
    hook=(out/'hook.bin').read_bytes()
    patched=bytearray(kernel);patched.extend(bytes(end-len(patched)))
    patched[original_size:original_size+len(hook)]=hook
    struct.pack_into('<I',patched,0,0x14000000|(original_size//4))
    struct.pack_into('<Q',patched,16,end)
    if patched[4:16]!=kernel[4:16] or patched[24:len(kernel)]!=kernel[24:]:raise ValueError('changed unrelated stock kernel bytes')
    header=bytearray(stock[:4096]);struct.pack_into('<I',header,8,len(patched))
    image=bytes(header)+patched+bytes(page(len(patched))-len(patched))+ramdisk+bytes(page(rs)-rs)
    if len(image)>len(stock):raise ValueError('exceeds boot partition')
    lock=json.loads((ROOT/'config/porting-sources.lock.json').read_text())['aosp_mkbootimg']
    aosp=Path('/mnt/'+lock['path'][0].lower()+lock['path'][2:].replace('\\','/'))
    for name,wanted in lock['sha256'].items():
        if sha((aosp/name).read_bytes())!=wanted:raise ValueError('AOSP source changed')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(image)
    unpack=out/'unpacked'
    subprocess.run([sys.executable,'-B',str(aosp/'unpack_bootimg.py'),'--boot_img',str(output),'--out',str(unpack)],
        check=True,stdout=subprocess.DEVNULL)
    if (unpack/'kernel').read_bytes()!=patched or (unpack/'ramdisk').read_bytes()!=ramdisk:raise ValueError('AOSP roundtrip differs')
    report={'scope':'R-002 reservation plus fixed marker seed; no device actions by builder' if args.seed_marker else 'R-002 reservation only; no physical log read/write and no device actions',
        'image_sha256':sha(image),'image_bytes':len(image),'stock_boot_sha256':STOCK_SHA,
        'stock_kernel_sha256':sha(kernel),'stock_ramdisk_sha256':sha(ramdisk),
        'stock_image_size':original_size,'patched_image_size':end,'stock_entry_offset':hex(entry),
        'hook_offset':hex(start),'hook_sha256':sha(hook),'header_version':3,
        'preserved':'stock kernel placement, code except entry branch/size, ramdisk, header except kernel_size, vendor_boot untouched',
        'reservation':['0x9fff7000','0x8000'],'on_unsupported_fdt':'no writes; continue original Android entry',
        'source_sha256':{p:sha((ROOT/'diagnostics'/p).read_bytes()) for p in ('fdt_reserve.c','android_fdt_entry.S','enuma_marker_seed.h')},
        'seed_marker':args.seed_marker,'marker_write_bytes':16 if args.seed_marker else 0,
        'marker_ascii':'ENUMA-R002-SEED1' if args.seed_marker else None,
        'marker_physical_base':'0x9fff7000' if args.seed_marker else None,
        'hardware_executed':False,'log_memory_accessed':False,'verified_flags_changed':False}
    output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'disassembly.txt').write_text(subprocess.check_output(['llvm-objdump','-d',str(out/'hook.elf')],text=True))
    print('PASS: pinned stock Image hook and AOSP v3 roundtrip; '+str(len(image))+' bytes; runtime unverified')

if __name__=='__main__':main()
