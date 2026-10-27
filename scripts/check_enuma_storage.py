"""Offline source pins, host failure models and freestanding ARM64 objects."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
if sys.version_info<(3,11):
    import tomli;sys.modules['tomllib']=tomli
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    e=a.evidence_root.resolve();peer=e/'out/sources/UniXNU-umi';up=ROOT/'out/sources/UniXNU/drivers/NativeUfs'
    lock=json.loads((ROOT/'config/system-reuse-sources.lock.json').read_text())['references'][0]
    name='package/UmiSmmuTakeover.h'
    if sha(peer/name)!=lock['files'][name]['sha256']:raise ValueError('peer SMMU source changed')
    pin=json.loads((ROOT/'config/sources.lock.json').read_text())['sources']['UniXNU']['gitlinks']['drivers/NativeUfs']
    sources={name:sha(peer/name)}
    for f in up.glob('*.h'):
        fixed=subprocess.check_output(['git','-C',str(up),'show',pin+':'+f.name])
        if fixed!=f.read_bytes():raise ValueError('upstream header changed '+f.name)
        sources['NativeUfs/'+f.name]=sha(f)
    records=[]
    def run(argv):
        r=subprocess.run(list(map(str,argv)),capture_output=True,text=True,timeout=120)
        records.append(dict(command=list(map(str,argv)),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        (out/'commands.json').write_text(json.dumps(records,indent=2))
        if r.returncode:raise ValueError(r.stderr+r.stdout)
    flags=['-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-pie','-no-pie']
    local=ROOT/'drivers/EnumaPlatform'
    for name,test in [('EnumaUfsSmmu','enuma_ufs_smmu'),('EnumaUfsRead','enuma_ufs_read')]:
        run(['/usr/bin/clang','-std=c11',*flags,'-I'+str(local),ROOT/'tests'/(test+'.c'),local/(name+'.c'),'-o',out/test])
        run([out/test])
        run(['/usr/bin/clang','-std=c11','-Wall','-Wextra','-Werror','--target=aarch64-none-elf','-ffreestanding','-fno-builtin','-O2','-c',local/(name+'.c'),'-o',out/(name+'.o')])
    # Exercise the unchanged production root parser/lifecycle/window reader;
    # these remain external pinned dependencies, not local stand-in drivers.
    for name in ['RootLayout','RootPublication','RootWindowRead']:
        test=up/'tests'/(name+'.cpp')
        if test.read_bytes()!=subprocess.check_output(['git','-C',str(up),'show',pin+':tests/'+name+'.cpp']):raise ValueError('upstream test changed')
        sources['NativeUfs/tests/'+test.name]=sha(test)
        if name=='RootWindowRead':
            # Darwin uint64_t and Linux uint64_t differ in their underlying
            # unsigned type. Normalize only this fixture literal, in out/.
            original=test.read_text();needle='for(auto count:{0ULL,UINT64_MAX})'
            if original.count(needle)!=1:raise ValueError('unexpected portability fixture')
            test=out/'RootWindowRead.cpp';test.write_text(original.replace(needle,'for(auto count:{uint64_t(0),UINT64_MAX})'))
            sources['host_portability_fixture']=sha(test)
        run(['/usr/bin/clang++','-std=c++17',*flags,'-I'+str(up/'tests'),test,'-o',out/name,*(['-lcrypto'] if name=='RootLayout' else ['-pthread'])]);run([out/name])
    from audit_inputs import parse_fdt,cells
    fdt=e/'out/device/live-fdt.bin'
    if sha(fdt)!='643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62':raise ValueError('FDT differs')
    nodes=parse_fdt(fdt.read_bytes());ufs=nodes['/soc/ufshc@1d84000'];smmu=nodes['/soc/apps-smmu@15000000']
    result=dict(passed=True,hardware_executed=False,iokit_linked=False,peer_commit=lock['evaluation_commit'],native_ufs_commit=pin,
        source_hashes=sources,local_sources={p.name:sha(p) for p in local.glob('EnumaUfs*.[ch]')},
        objects={p.name:sha(p) for p in out.glob('*.o')},fdt_sha256=sha(fdt),
        enuma_ufs_reg=cells(ufs['reg']),enuma_smmu_reg=cells(smmu['reg']),ufs_iommus_declared='iommus' in ufs,
        streams_qualified=False,umi_test_streams=['0xe0','0x4e0'],
        limits=['no XNU service or hardware MMIO adapter yet','stream identity not established for enuma',
                'queue stop and exclusive ownership must be implemented by caller','no disk writes or partition geometry borrowed'])
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: storage failure models, pinned root tests and ARM64 objects')
if __name__=='__main__':main()
