"""Qualify and package one original-OEM first-call experiment; no device I/O."""
import argparse,json,subprocess,sys,re
from pathlib import Path
from audit_oem_development_fd import audit,ROOT,sha
from check_oem_runtime_code import verify_with_deletions,check_exception
from check_oem_entry_failure_code import check as check_entry
sys.path.insert(0,str(ROOT/'firmware/Resources/Scripts'))
from enuma_oem_identity import generate
from oem_runtime_candidate import limits_for

def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--progress-check',type=Path)
    p.add_argument('--main-path-check',type=Path)
    p.add_argument('--binding-check',type=Path)
    a=p.parse_args();build=a.build.resolve();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    base,pe=audit(build,runtime=True);b=json.loads((build/'build-result.json').read_text());config=b['oem_run_config']
    main_path=None;binding_check=None
    if config['experiment'] in ('oem-main-entry-v6','oem-far-chain-v7'):
        if not a.binding_check:raise ValueError('current relocated PE and board binding check required')
        binding_check=json.loads(a.binding_check.read_text())
        if binding_check.get('passed') is not True or binding_check['profiles']['oem-control']['identity']['runtime']!=config:raise ValueError('binding result differs')
        for name,h in binding_check['source_sha256'].items():
            if sha((ROOT/name).read_bytes())!=h:raise ValueError('binding source changed: '+name)
        if not a.main_path_check:raise ValueError('exact main path and ABI check required')
        main_path=json.loads(a.main_path_check.read_text())
        if main_path.get('passed') is not True or main_path.get('pe_sha256')!=sha(pe):raise ValueError('main path differs')
        for name,h in main_path['sources'].items():
            if sha((ROOT/name).read_bytes())!=h:raise ValueError('main path source changed: '+name)
    progress=config['experiment'] in ('oem-progress-v2','oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7')
    if progress:
        if not a.progress_check:raise ValueError('progress failure tests required')
        tests=json.loads(a.progress_check.read_text())
        if tests.get('passed') is not True:raise ValueError('progress tests failed')
        for name,h in tests['sources'].items():
            if sha((ROOT/name).read_bytes())!=h:raise ValueError('progress tests stale: '+name)
    if config['experiment'] in ('oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7'):
        actual=build/'work/Mu_Basecore/MdeModulePkg/Core/Dxe/Misc/InstallConfigurationTable.c'
        tested=a.progress_check.parent/'MdeModulePkg/Core/Dxe/Misc/InstallConfigurationTable.c'
        # The build backend reverses Core patches after compilation. Reconstruct
        # the compiled input from that baseline and the immutable build snapshot.
        reconstructed=out/'MdeModulePkg/Core/Dxe/Misc/InstallConfigurationTable.c'
        reconstructed.parent.mkdir(parents=True)
        reconstructed.write_text(actual.read_text())
        subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(build/'source/patches/oem-system-table-sync.patch')],cwd=out,check=True)
        if reconstructed.read_text()!=tested.read_text().replace('#include "oem_system_table_core_fixture.h"','#include "DxeMain.h"'):
            raise ValueError('compiled Core config-table source differs from real-Core regression')
        if len(tests.get('sync_deletion_checks',[]))!=2:raise ValueError('missing Core sync negative tests')
    (out/'DisplayDxe.efi').write_bytes(pe);identity=generate(out/'DisplayDxe.efi',out/'identity.h',config)
    staged=build/'work/Mu_Basecore/MdeModulePkg/Core/Dxe/Dispatcher/EnumaOemBuildIdentity.h'
    if staged.read_bytes()!=(out/'identity.h').read_bytes():raise ValueError('runtime identity not staged')
    if any(b['oem_trace_identity'].get(k)!=v for k,v in identity.items()):raise ValueError('runtime identity mismatch')
    exception=build/'work/Mu_Basecore/UefiCpuPkg/Library/CpuExceptionHandlerLib/AArch64/EnumaUnhandledExceptionCheckpoint.h'
    if exception.read_bytes()!=(build/'source/diagnostics/EnumaOemExceptionStop.h').read_bytes():raise ValueError('exception stop not staged')
    product=build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain/OUTPUT'
    core=(product/'DxeCore.efi').read_bytes();mapping=(product/'DxeCore.map').read_text()
    runtime_code=verify_with_deletions(core,mapping,progress,config['experiment']=='oem-far-chain-v7')
    early_code=None
    if config['experiment'] in ('oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7'):
        from check_oem_early_code import verify as verify_early
        early_code=verify_early(core,mapping,config['experiment'])
    cpus=list((build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64').rglob('OUTPUT/ArmCpuDxe.efi'))
    if len(cpus)!=1:raise ValueError('missing CPU exception product')
    cpu=cpus[0].read_bytes();cpu_map=cpus[0].with_suffix('.map').read_text()
    cpu_exception=check_exception(cpu,cpu_map)
    failure=check_entry(core,mapping)
    symbols={}
    for name in (('OemProgressBefore','OemProgressAfter','OemProgressReturned','OemProgressPresent') if progress else ('OemRuntimeBeforeForward',))+('OemBoardSink','EnumaTraceLocateProtocol','EnumaTraceHandleProtocol','EnumaTraceAllocatePool'):
        hits=re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+'+name+r'$',mapping,re.M)
        if len(hits)!=1:raise ValueError('missing runtime code '+name)
        symbols[name]=hits[0]
    assembly=subprocess.check_output(['/usr/bin/llvm-objdump','-d',product/'DxeCore.efi'],text=True)
    (out/'Core.disassembly.txt').write_text(assembly)
    for token in ('daifset','DAIF','MPIDR_EL1'):
        if token.lower() not in assembly.lower():raise ValueError('runtime interrupt gate missing')
    if sys.version_info<(3,11):import tomli;sys.modules['tomllib']=tomli
    sys.path.insert(0,str(ROOT/'out/sources/UniXNU/scripts'))
    from unixnu.bootimg import compile_shim
    shim=compile_shim(build/'work/uefi',0x9fc00000,0x300000,True,out)
    fd=ROOT/b['fd'];raw=out/'firmware.raw';raw.write_bytes(shim+fd.read_bytes());empty=out/'empty';empty.write_bytes(b'')
    aosp=Path('/mnt/d/Code/PortingiOSLegacy/common/sources/aosp-mkbootimg')
    lock=json.loads((ROOT/'config/porting-sources.lock.json').read_text())['aosp_mkbootimg']
    for name,h in lock['sha256'].items():
        if sha((aosp/name).read_bytes())!=h:raise ValueError('AOSP pin mismatch')
    image=out/'image.img'
    subprocess.run([sys.executable,'-B',aosp/'mkbootimg.py','--header_version','3','--kernel',raw,'--ramdisk',empty,'--output',image],check=True)
    from package_enuma_boot import verify
    package=verify(image.read_bytes(),raw.read_bytes(),b'')
    subprocess.run([sys.executable,'-B',aosp/'unpack_bootimg.py','--boot_img',image,'--out',out/'unpacked'],check=True,stdout=subprocess.DEVNULL)
    if (out/'unpacked/kernel').read_bytes()!=raw.read_bytes():raise ValueError('unpack mismatch')
    sources=['scripts/run_oem_runtime_trial.py','scripts/oem_runtime_candidate.py','scripts/qualify_oem_runtime.py',
             'scripts/run_enuma_entry_probe.py','scripts/audit_oem_development_fd.py',
             'scripts/check_oem_runtime_code.py','scripts/check_oem_entry_failure_code.py','scripts/enuma_paths.py']
    sources+=['firmware/'+n for n in json.loads((build/'source-manifest.json').read_text())['original_files']]
    if progress:sources+=['scripts/check_oem_progress.py','scripts/decode_oem_progress_page.py','tests/oem_progress.c','tests/oem_capture_pixel.c','tests/test_oem_progress_page.py']
    if config['experiment'] in ('oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7'):sources+=['scripts/check_oem_early_code.py']
    if config['experiment'] in ('oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7'):sources+=['tests/test_oem_runtime_return.py','tests/test_oem_runtime_candidate.py']
    if config['experiment'] in ('oem-main-entry-v6','oem-far-chain-v7'):sources+=['scripts/check_oem_main_code.py','scripts/check_oem_far_code.py','scripts/check_oem_main_path.py']+list(main_path['sources'])+list(binding_check['source_sha256'])+['scripts/check_oem_core_binding.py']
    if progress:sources+=list(tests['sources'])
    bindings={n:sha((ROOT/n).read_bytes()) for n in sources}
    result=dict(passed=True,software_ready=True,hardware_executed=False,scope=config['experiment'],run_config=config,
                image_sha256=sha(image.read_bytes()),fd_sha256=b['fd_sha256'],image_bytes=image.stat().st_size,
                build=str(build.relative_to(ROOT)),fd_audit=base,identity=identity,linked_symbols=symbols,
                entry_failure_rva=hex(failure),runtime_code=runtime_code,cpu_exception_rva=hex(cpu_exception),
                boot_v3=package,source_bindings=bindings,
                runtime_limits=limits_for(config['experiment']),
                limitations=['pre-forward entry is not proof original service ran','no automatic recovery guarantee for OEM hang',
                             'local interrupt masking does not prove exclusion of AP or external DMA','no GOP/BDS/input acceptance'])
    if early_code:result['early_code']=early_code
    if main_path:result['main_path']=main_path;result['binding_check_sha256']=sha(a.binding_check.read_bytes())
    if progress:
        result['progress_tests_sha256']=sha(a.progress_check.read_bytes())
        result['progress_phases']={1:'first service before',2:'first service returned',3:'first SID LocateProtocol before',4:'first SID LocateProtocol returned',5:'actual CoreStartImage returned'}
        if config['experiment']=='oem-early-v3':
            result['progress_phases']={1:'call1 before',2:'call1 returned',3:'first Kernel LocateProtocol before',4:'first Kernel LocateProtocol returned',5:'actual CoreStartImage returned'}
        if config['experiment']=='oem-registration-v5':
            result['progress_phases']={1:'target configuration registration before',2:'target configuration registration returned',3:'first SID LocateProtocol before',4:'first SID LocateProtocol returned',5:'actual CoreStartImage returned'}
        if config['experiment']=='oem-post-kernel-v4':
            result['progress_phases']={1:'call4 before',2:'call4 returned',3:'first SID LocateProtocol before',4:'first SID LocateProtocol returned',5:'actual CoreStartImage returned'}
        if config['experiment'] in ('oem-main-entry-v6','oem-far-chain-v7'):
            result['progress_phases']={1:'first main query before (call>=6/RVA3608)',3:'first SID query before; main query returned',5:'actual CoreStartImage returned'}
        if config['experiment']=='oem-far-chain-v7':result['progress_phases']={5:'coarse RAM summary after real Core return and full DXE dispatch completion; one late window'}
        result['limitations']+=['no export if OEM hangs before the selected wrapped service',
            'SID protocol methods and direct MMIO are not observed; last visible stage is not a root cause',
            'each window requires inherited route still valid; refusal after OEM display changes is not OEM failure',
            ('one late DXE-complete summary; no earlier window and no independent watchdog or durable RAM recovery' if config['experiment']=='oem-far-chain-v7' else 'three entry/Core observations, no service-return drawing; no independent watchdog or durable RAM recovery' if config['experiment']=='oem-main-entry-v6' else 'five observations perturb timing; no independent watchdog or durable RAM recovery'),
            'phase5 Q is next trace sequence, not a synthetic service event']
    (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: runtime software qualification and Boot v3 packaging')
if __name__=='__main__':main()
