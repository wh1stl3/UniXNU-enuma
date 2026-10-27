"""Compile root bridge archive and exercise transport and packed Data failures."""
import argparse, hashlib, json, os, random, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    pins=json.loads((ROOT/'config/sources.lock.json').read_text())['sources']['UniXNU']['gitlinks']
    up=ROOT/'out/sources/UniXNU/drivers';sources={}
    for component,name in [('NativeUfs','RootWindowRead.h'),('NativeRamBlock','SparseDisk.h')]:
        path=up/component/name;pin=pins['drivers/'+component]
        if path.read_bytes()!=subprocess.check_output(['git','-C',str(path.parent),'show',pin+':'+name]):raise ValueError('source changed '+name)
        sources[component+'/'+name]=dict(commit=pin,sha256=sha(path))
    commands=[]
    def run(args):
        r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=120)
        commands.append(dict(command=list(map(str,args)),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        if r.returncode:raise ValueError(r.stderr+r.stdout)
        return r.stdout
    local=ROOT/'drivers/EnumaPlatform';inc=['-I'+str(local),'-I'+str(up/'NativeUfs')]
    warnings=['-Wall','-Wextra','-Werror']
    sanitize=['-fsanitize=address,undefined','-fno-pie','-no-pie']
    # Compile C with C linkage, then link C++ production adapter and harness.
    run(['/usr/bin/clang','-std=c11',*warnings,'-fsanitize=address,undefined','-c',local/'EnumaUfsRead.c','-o',out/'host-read.o'])
    run(['/usr/bin/clang++','-std=c++17',*warnings,*sanitize,*inc,ROOT/'tests/enuma_root_read.cpp',local/'EnumaRootRead.cpp',out/'host-read.o','-o',out/'root-test'])
    run([out/'root-test'])
    objects=[]
    for name in ['EnumaUfsRead.c','EnumaUfsSmmu.c','EnumaRootRead.cpp']:
        obj=out/(Path(name).stem+'.o');objects.append(obj)
        run(['/usr/bin/clang++' if name.endswith('.cpp') else '/usr/bin/clang',
             '-std=c++17' if name.endswith('.cpp') else '-std=c11',*warnings,*inc,
             '--target=arm64-apple-darwin','-ffreestanding','-fno-builtin','-fno-stack-protector',
             *(['-fno-exceptions','-fno-rtti','-nostdinc++'] if name.endswith('.cpp') else []),'-O2','-c',local/name,'-o',obj])
    archive=out/'libEnumaRootRead.a';run(['/usr/bin/llvm-ar','rcs',archive,*objects])
    symbols=run(['/usr/bin/llvm-nm',archive]);(out/'symbols.txt').write_text(symbols)
    if '_enuma_root_read' not in symbols or '_enuma_ufs_prepare_read' not in symbols:raise ValueError('archive entry missing')
    run(['/usr/bin/clang++','-std=c++17',*warnings,*sanitize,'-I'+str(up/'NativeRamBlock'),ROOT/'tests/enuma_packed_seed.cpp','-o',out/'seed-test'])
    from enuma_data_seed import inspect_seed
    # Synthetic transport-only fixture, deliberately NOT an APFS seed.
    good=struct.pack('<8sIIQQQQ',b'DBRDISK1',1,4096,16384,1,4096,4096)+bytes([0x5a])*4096
    cases=[good,good[:31],good+b'x',good[:-1]]
    for at,value in [(8,2),(12,512),(16,0),(24,65537),(32,16384),(40,0),(40,4097)]:
        b=bytearray(good);struct.pack_into('<I' if at<16 else '<Q',b,at,value);cases.append(bytes(b))
    rng=random.Random(27)
    for _ in range(128):
        b=bytearray(good);i=rng.randrange(48);b[i]^=1<<rng.randrange(8);cases.append(bytes(b))
    accepted=rejected=0
    env=dict(os.environ,ASAN_OPTIONS='detect_leaks=1')
    for i,blob in enumerate(cases):
        path=out/f'seed-case-{i}.bin';path.write_bytes(blob)
        try:info=inspect_seed(path,sha(path));valid=True
        except ValueError:valid=False
        r=subprocess.run([str(out/'seed-test'),str(path)],capture_output=True,text=True,env=env,timeout=10)
        if r.returncode not in (0,1) or bool(r.stderr) or (r.returncode==0)!=valid:raise ValueError('packed parser disagreement '+str(i)+' '+r.stderr)
        if valid:
            if int(r.stdout)!=info['logical_bytes']:raise ValueError('logical geometry differs')
            accepted+=1
        else:rejected+=1
    try:inspect_seed(out/'seed-case-0.bin','0'*64)
    except ValueError:pass
    else:raise ValueError('digest mismatch accepted')
    result=dict(passed=True,sources=sources,local_sources={p.name:sha(p) for p in [local/'EnumaRootRead.cpp',local/'EnumaRootRead.h',ROOT/'scripts/enuma_data_seed.py']},
        archive_sha256=sha(archive),objects={p.name:sha(p) for p in objects},packed_cases=len(cases),accepted=accepted,rejected=rejected,
        hardware_executed=False,iokit_linked=False,apfs_seed_created=False,kernel_relinked=False,
        scope='Mach-O ARM64 reusable archive, production window reader and packed format differential tests')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
