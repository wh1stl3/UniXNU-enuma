"""Qualify and package one original-OEM first-call experiment; no device I/O."""
import argparse,json,subprocess,sys,re
from pathlib import Path
from audit_oem_development_fd import audit,ROOT,sha
from check_oem_runtime_code import verify_with_deletions,check_exception
from check_oem_entry_failure_code import check as check_entry
sys.path.insert(0,str(ROOT/'firmware/Resources/Scripts'))
from enuma_oem_identity import generate
from oem_runtime_candidate import limits_for,CLOCK_SCOPES

def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--progress-check',type=Path)
    p.add_argument('--main-path-check',type=Path)
    p.add_argument('--binding-check',type=Path)
    p.add_argument('--event-check',type=Path)
    p.add_argument('--clock-check',type=Path)
    p.add_argument('--gop-check',type=Path)
    p.add_argument('--exception-check',type=Path)
    a=p.parse_args();build=a.build.resolve();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    base,pe=audit(build,runtime=True);b=json.loads((build/'build-result.json').read_text());config=b['oem_run_config']
    exception=config['experiment'] in ('oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13')
    exception_check=None
    if exception:
        if not a.exception_check:raise ValueError('exception failure/ARM checks required')
        exception_check=json.loads(a.exception_check.read_text())
        if exception_check.get('passed') is not True:raise ValueError('exception tests failed')
        for name,h in exception_check['sources'].items():
            if sha((ROOT/name).read_bytes())!=h:raise ValueError('exception tests stale: '+name)
    clock=config['experiment'] in CLOCK_SCOPES
    gop=config['experiment'].startswith(('oem-gop-mode-','oem-exception-'))
    gop_check=None
    if gop:
        if not a.gop_check:raise ValueError('actual native GOP helper checks required')
        gop_check=json.loads(a.gop_check.read_text())
        if gop_check.get('passed') is not True:raise ValueError('GOP helper tests failed')
        for name,h in gop_check['sources'].items():
            if sha((ROOT/name).read_bytes())!=h:raise ValueError('GOP helper check stale: '+name)
    clock_check=None
    if clock:
        if not a.clock_check:raise ValueError('actual clock helper/ARM force checks required')
        clock_check=json.loads(a.clock_check.read_text())
        if clock_check.get('passed') is not True:raise ValueError('clock helper tests failed')
        for name,h in clock_check['sources'].items():
            if sha((ROOT/name).read_bytes())!=h:raise ValueError('clock helper test stale: '+name)
    event_check=None
    if config['experiment']=='oem-far-event-v8' or clock:
        if not a.event_check:raise ValueError('frozen-race/fixed-event/deleted-hook regression required')
        event_check=json.loads(a.event_check.read_text())
        if event_check.get('passed') is not True:raise ValueError('event race regression failed')
        for name,h in event_check['sources'].items():
            if sha((ROOT/name).read_bytes())!=h:raise ValueError('event regression stale: '+name)
    main_path=None;binding_check=None
    if config['experiment'] in ('oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'):
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
    progress=config['experiment'] in ('oem-progress-v2','oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13')
    if progress:
        if not a.progress_check:raise ValueError('progress failure tests required')
        tests=json.loads(a.progress_check.read_text())
        if tests.get('passed') is not True:raise ValueError('progress tests failed')
        for name,h in tests['sources'].items():
            if sha((ROOT/name).read_bytes())!=h:raise ValueError('progress tests stale: '+name)
    if config['experiment'] in ('oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'):
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
    exception_header=build/'work/Mu_Basecore/UefiCpuPkg/Library/CpuExceptionHandlerLib/AArch64/EnumaUnhandledExceptionCheckpoint.h'
    if exception_header.read_bytes()!=(build/'source/diagnostics/EnumaOemExceptionStop.h').read_bytes():raise ValueError('exception stop not staged')
    if exception:
        for name in ('EnumaOemExceptionView.h','EnumaOemExceptionPage.h','EnumaOemExceptionDisplay.h','EnumaOemCapturePixel.h'):
            if (exception_header.parent/name).read_bytes()!=(build/'source/diagnostics'/name).read_bytes():raise ValueError('exception dependency not staged: '+name)
        expected=('#define ENUMA_EXCEPTION_SESSION 0x%xULL\n'%config['session']).encode()
        if (exception_header.parent/'EnumaOemExceptionIdentity.h').read_bytes()!=expected:raise ValueError('exception session not staged')
    product=build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain/OUTPUT'
    core=(product/'DxeCore.efi').read_bytes();mapping=(product/'DxeCore.map').read_text()
    event=config['experiment']=='oem-far-event-v8' or clock
    runtime_code=None if clock else verify_with_deletions(core,mapping,progress,config['experiment'] in ('oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'),event)
    early_code=None
    if not clock and config['experiment'] in ('oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'):
        from check_oem_early_code import verify as verify_early
        early_code=verify_early(core,mapping,config['experiment'])
    cpus=list((build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64').rglob('OUTPUT/ArmCpuDxe.efi'))
    if len(cpus)!=1:raise ValueError('missing CPU exception product')
    cpu=cpus[0].read_bytes();cpu_map=cpus[0].with_suffix('.map').read_text()
    if clock:
        from check_oem_clock_code import verify as verify_clock
        runtime_code=verify_clock(core,mapping,cpu,cpu_map,int(b['firmware_configuration']['defines']['ENUMA_OEM_CLOCK_FORCE']),gop=gop,exception=exception)
        cpu_exception=runtime_code['cpu_exception_rva']
        if exception and runtime_code['exception_session']!=config['session']:raise ValueError('linked exception session differs')
    else:cpu_exception=check_exception(cpu,cpu_map)
    failure=check_entry(core,mapping)
    symbols={}
    for name in (('OemProgressReturned',) if clock else ('OemProgressRecord','OemProgressReturned','OemProgressPresent') if event else ('OemProgressBefore','OemProgressAfter','OemProgressReturned','OemProgressPresent') if progress else ('OemRuntimeBeforeForward',))+(('EnumaTraceLocateProtocol','EnumaTraceHandleProtocol','EnumaTraceAllocatePool') if clock else ('OemBoardSink','EnumaTraceLocateProtocol','EnumaTraceHandleProtocol','EnumaTraceAllocatePool')):
        hits=re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+'+name+r'$',mapping,re.M)
        if len(hits)!=1:raise ValueError('missing runtime code '+name)
        symbols[name]=hits[0]
    assembly=subprocess.check_output(['/usr/bin/llvm-objdump','-d',product/'DxeCore.efi'],text=True)
    (out/'Core.disassembly.txt').write_text(assembly)
    for token in (() if clock else ('daifset','DAIF','MPIDR_EL1')):
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
    if config['experiment'] in ('oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'):sources+=['scripts/check_oem_early_code.py']
    if config['experiment'] in ('oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'):sources+=['tests/test_oem_runtime_return.py','tests/test_oem_runtime_candidate.py']
    if config['experiment'] in ('oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'):sources+=['scripts/check_oem_main_code.py','scripts/check_oem_far_code.py','scripts/check_oem_main_path.py']+list(main_path['sources'])+list(binding_check['source_sha256'])+['scripts/check_oem_core_binding.py']
    if progress:sources+=list(tests['sources'])
    if event:sources+=['scripts/check_oem_event_code.py']+list(event_check['sources'])
    sources+=['scripts/oem_exit_clock.py','scripts/boot_origin.py']
    if clock:sources+=['scripts/check_oem_clock_code.py','tests/test_oem_exit_clock.py','tests/test_oem_runtime_transport.py']+list(clock_check['sources'])
    if gop:sources+=list(gop_check['sources'])+['scripts/check_oem_gop_code.py']
    if exception:sources+=list(exception_check['sources'])+['scripts/check_oem_exception_code.py','scripts/exception_image_inventory.py','scripts/map_oem_trace_rva.py','scripts/decode_oem_exception.py','tests/test_oem_exception_page.py']
    if config['experiment']=='oem-exception-dispcc-v12':
        sources+=['scripts/check_oem_dispcc_map.py','tests/test_oem_dispcc_map.py']
    if config['experiment']=='oem-exception-display-map-v13':
        sources+=['scripts/check_oem_display_map.py','scripts/check_oem_dispcc_map.py','tests/test_oem_display_map.py','tests/test_oem_dispcc_map.py']
    bindings={n:sha((ROOT/n).read_bytes()) for n in sources}
    result=dict(passed=True,software_ready=True,hardware_executed=False,scope=config['experiment'],run_config=config,
                image_sha256=sha(image.read_bytes()),fd_sha256=b['fd_sha256'],image_bytes=image.stat().st_size,
                build=str(build.relative_to(ROOT)),fd_audit=base,identity=identity,linked_symbols=symbols,
                entry_failure_rva=hex(failure),runtime_code=runtime_code,cpu_exception_rva=hex(cpu_exception) if isinstance(cpu_exception,int) else cpu_exception,
                boot_v3=package,source_bindings=bindings,
                runtime_limits=limits_for(config['experiment']),
                limitations=['pre-forward entry is not proof original service ran','no automatic recovery guarantee for OEM hang',
                             'local interrupt masking does not prove exclusion of AP or external DMA','no GOP/BDS/input acceptance'])
    if clock:result.update(clock_check_sha256=sha(a.clock_check.read_bytes()),clock_force=int(b['firmware_configuration']['defines']['ENUMA_OEM_CLOCK_FORCE']),clock_calibration_complete=False,clock_inference_only=True)
    if early_code:result['early_code']=early_code
    if event:result['event_check_sha256']=sha(a.event_check.read_bytes())
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
        if config['experiment'] in ('oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'):
            result['progress_phases']={1:'first main query before (call>=6/RVA3608)',3:'first SID query before; main query returned',5:'actual CoreStartImage returned'}
        if config['experiment'] in ('oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13'):result['progress_phases']={5:'coarse RAM summary after real Core return and full DXE dispatch completion; one late window'}
        result['limitations']+=['no export if OEM hangs before the selected wrapped service',
            'SID protocol methods and direct MMIO are not observed; last visible stage is not a root cause',
            'each window requires inherited route still valid; refusal after OEM display changes is not OEM failure',
            ('one late DXE-complete summary; no earlier window and no independent watchdog or durable RAM recovery' if config['experiment'] in ('oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10','oem-exception-v11','oem-exception-dispcc-v12','oem-exception-display-map-v13') else 'three entry/Core observations, no service-return drawing; no independent watchdog or durable RAM recovery' if config['experiment']=='oem-main-entry-v6' else 'five observations perturb timing; no independent watchdog or durable RAM recovery'),
            'phase5 Q is next trace sequence, not a synthetic service event']
    if clock:
        result['progress_phases']={}
        result['clock_classes']={1:'instrumented exception',2:'diagnostic terminal',3:'DXE complete without matched Core return',4:'DXE complete with nonzero Core status',5:'DXE complete with Core EFI_SUCCESS'}
        result['limitations']=['No display, GOP query, MDP access or pixel capture in clock scope','Indirect time inference only; variable pre-exit execution and uninstrumented resets can alias a code','Fresh paired low/high calibration and confirmed automatic Android return required; target execution rejects missing/expired plan','No independent watchdog, persistent log, exact error status export or unique execution path proof','No GOP/ConOut/BDS/input/XNU acceptance']
    if exception:
        from exception_image_inventory import inventory
        result['exception_inventory']=inventory(build,ROOT)
        result['exception_check_sha256']=sha(a.exception_check.read_bytes())
        result['exception_pages']={17:'exception type/PC/ESR/FAR/session',18:'owner state/base/RVA/size/session',19:'LR/GUID halves/SPSR/session'}
        result['clock_inference_only']=False
        result['clock_calibration_complete']=None
        result['clock_classes']={}
        result['limitations']=['No Boot Services/GOP/formatting from exception sink; inherited route may be rejected or fault','No independent watchdog or persistent exception recovery; recursive fault resets immediately','PC owner lookup uses bounded, mapped initial firmware RAM metadata, ambiguous/busy/invalid/absent is unknown','No physical GOP/ConOut/BDS/input/XNU success; unhandled exceptions before this CPU handler are not covered']
    if gop:
        result['gop_check_sha256']=sha(a.gop_check.read_bytes())
    if gop and not exception:
        result['clock_classes'][5]='Core EFI_SUCCESS without validated native GOP mode'
        result['clock_classes'][6]='Core EFI_SUCCESS and native GOP SetMode/status/geometry/framebuffer bounds validated'
        result['limitations']=['Post-DXE only; original clock/HAL/OEM path retained; native GOP mode0 queried and SetMode called at most once after matched Core EFI_SUCCESS','Code6 is indirect timing evidence for native API/structure checks, not photons/scanout or ConOut/BDS/XNU acceptance','No direct MDP/pixel access, Blt, display-power cycling, controller ConnectAll, BDS, flash or memory-map changes in new helper','Fresh same-source low2/high27 calibration required; uninstrumented resets/variable prefixes can alias codes; no independent watchdog','Native QueryMode/SetMode may block; bounded call count is not a wall-clock timeout; unknown pointer allocations are not freed and remain bounded until reset']
    (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: runtime software qualification and Boot v3 packaging')
if __name__=='__main__':main()
