"""Exercise the volatile Data backend against the real APFS seed and raw image."""
import argparse,hashlib,json,subprocess,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--seed-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    up=ROOT/'out/sources/UniXNU/drivers/NativeRamBlock';pin=json.loads((ROOT/'config/sources.lock.json').read_text())['sources']['UniXNU']['gitlinks']['drivers/NativeRamBlock']
    header=up/'SparseDisk.h'
    if header.read_bytes()!=subprocess.check_output(['git','-C',str(up),'show',pin+':SparseDisk.h']):raise ValueError('production algorithm changed')
    report=json.loads((a.seed_dir/'data-linux.json').read_text());seed=a.seed_dir/'data-linux.dbr';raw=a.seed_dir/'data-linux.raw'
    if sha(seed)!=report['packed_sha256'] or sha(raw)!=report['raw_sha256']:raise ValueError('seed binding mismatch')
    local=ROOT/'drivers/EnumaPlatform';commands=[]
    def run(args):
        r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=180)
        commands.append(dict(command=list(map(str,args)),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if r.returncode:raise ValueError(r.stdout+r.stderr)
        return r.stdout
    flags=['-std=c++17','-Wall','-Wextra','-Werror','-I'+str(local),'-I'+str(up)]
    run(['/usr/bin/clang++',*flags,'-fsanitize=address,undefined','-fno-pie','-no-pie','-pthread',local/'EnumaRamDisk.cpp',ROOT/'tests/enuma_ram_disk.cpp','-o',out/'test'])
    result=run([out/'test',seed,raw])
    # Only libc declarations are needed by the production header, no SDK shim
    # classes or fabricated IOKit headers. Use Clang's freestanding C headers.
    include=out/'include';include.mkdir();(include/'string.h').write_text('#include <stddef.h>\nextern "C" { void *memcpy(void *, const void *, size_t); void *memset(void *, int, size_t); int memcmp(const void *, const void *, size_t); }\n')
    run(['/usr/bin/clang++',*flags,'--target=arm64-apple-ios17.0','-nostdinc++','-I'+str(include),'-ffreestanding','-fno-builtin','-fno-exceptions','-fno-rtti','-fno-stack-protector','-O2','-c',local/'EnumaRamDisk.cpp','-o',out/'EnumaRamDisk.o'])
    raw_object=(out/'EnumaRamDisk.o').read_bytes();magic,cpu,subtype,kind,count=struct.unpack_from('<5I',raw_object)
    if (magic,cpu,subtype,kind)!=(0xfeedfacf,0x100000c,0,1):raise ValueError('not plain ARM64 Mach-O object')
    cursor=32;versions=[]
    for _ in range(count):
        command,size=struct.unpack_from('<II',raw_object,cursor)
        if command==0x32:versions.append(struct.unpack_from('<II',raw_object,cursor+8))
        cursor+=size
    if versions!=[(2,0x110000)]:raise ValueError('not iOS17 build target')
    run(['/usr/bin/llvm-ar','rcs',out/'libEnumaRamDisk.a',out/'EnumaRamDisk.o'])
    symbols=run(['/usr/bin/llvm-nm',out/'libEnumaRamDisk.a']);(out/'symbols.txt').write_text(symbols)
    for name in ['start','stop','info','io']:
        if 'T _enuma_ram_'+name not in symbols:raise ValueError('missing entry '+name)
    result=dict(passed=True,native_ram_block_commit=pin,production_header_sha256=sha(header),seed_sha256=sha(seed),raw_sha256=sha(raw),
        source_hashes={p.name:sha(p) for p in [local/'EnumaRamDisk.cpp',local/'EnumaRamDisk.h',ROOT/'tests/enuma_ram_disk.cpp',Path(__file__)]},
        archive_sha256=sha(out/'libEnumaRamDisk.a'),object_build_version=versions,host_result=result.strip(),
        kernel_linked=False,iokit_registered=False,apfs_mounted=False,hardware_executed=False,
        persistence_mode='volatile only, no storage callbacks',scope='real packed Data import and block I/O, host sanitizer execution and ARM64 Mach-O archive')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
