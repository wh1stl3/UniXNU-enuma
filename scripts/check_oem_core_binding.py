"""Build real binding headers against relocated exact OEM PEs under sanitizers."""
import argparse,json,subprocess,sys,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'firmware/Resources/Scripts'))
from enuma_oem_identity import generate

def main():
    p=argparse.ArgumentParser();p.add_argument('--pair',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--runtime-config',type=Path)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    reports={};inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include'
    for variant in ('oem-control','oem-mmu-only'):
        d=out/variant;d.mkdir();pe=a.pair/variant/'vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi'
        identity=generate(pe,d/'EnumaOemBuildIdentity.h',json.loads(a.runtime_config.read_text()) if a.runtime_config else None)
        cmd=['/usr/bin/clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-fshort-wchar','-fno-builtin','-DMDEPKG_NDEBUG',
             '-I'+str(inc),'-I'+str(inc/'X64'),'-I'+str(ROOT/'firmware/Mu_Basecore/MdeModulePkg/Include'),'-I'+str(ROOT/'firmware/diagnostics'),'-I'+str(d),
             '-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',str(ROOT/'tests/oem_core_binding.c'),'-o',str(d/'test')]
        subprocess.run(cmd,check=True);r=subprocess.run([d/'test',pe],check=True,capture_output=True,text=True)
        other='oem-mmu-only' if variant=='oem-control' else 'oem-control'
        cross=subprocess.run([d/'test',a.pair/other/'vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi','reject'],check=True,capture_output=True,text=True)
        reports[variant]={'identity':identity,'output':r.stdout,'cross_profile':cross.stdout}
    lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
    shutil.copytree(lib,out/'OemInherited')
    cmd=['/usr/bin/clang','-target','aarch64-unknown-windows-msvc','-ffreestanding','-fno-stack-protector',
         '-mno-stack-arg-probe','-mno-implicit-float','-Wall','-Wextra','-Werror','-Wno-unused-function','-Os','-DMDEPKG_NDEBUG']
    if a.runtime_config:cmd.append('-DENUMA_OEM_RUNTIME=1')
    if a.runtime_config and json.loads(a.runtime_config.read_text())['experiment'] in ('oem-progress-v2','oem-early-v3','oem-post-kernel-v4','oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10'):cmd.append('-DENUMA_OEM_PROGRESS=1')
    if a.runtime_config and json.loads(a.runtime_config.read_text())['experiment']=='oem-early-v3':cmd.append('-DENUMA_OEM_EARLY=1')
    if a.runtime_config and json.loads(a.runtime_config.read_text())['experiment']=='oem-post-kernel-v4':cmd.append('-DENUMA_OEM_POST_KERNEL=1')
    if a.runtime_config and json.loads(a.runtime_config.read_text())['experiment'] in ('oem-registration-v5','oem-main-entry-v6','oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10'):cmd.append('-DENUMA_OEM_REGISTRATION=1')
    if a.runtime_config and json.loads(a.runtime_config.read_text())['experiment']=='oem-main-entry-v6':cmd.append('-DENUMA_OEM_MAIN_ENTRY=1')
    if a.runtime_config and json.loads(a.runtime_config.read_text())['experiment'] in ('oem-far-chain-v7','oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10'):cmd.append('-DENUMA_OEM_FAR_CHAIN=1')
    if a.runtime_config and json.loads(a.runtime_config.read_text())['experiment'] in ('oem-far-event-v8','oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10'):cmd.append('-DENUMA_OEM_RAM_EVENT=1')
    clock=a.runtime_config and json.loads(a.runtime_config.read_text())['experiment'] in ('oem-far-clock-v9','oem-far-clock-low-v9','oem-far-clock-high-v9','oem-gop-mode-v10','oem-gop-mode-low-v10','oem-gop-mode-high-v10')
    if clock and json.loads(a.runtime_config.read_text())['experiment'].startswith('oem-gop-mode-'):cmd+=['-DENUMA_OEM_GOP_MODE=1']
    if clock:cmd+=['-DENUMA_OEM_EXIT_CLOCK=1','-DENUMA_OEM_CLOCK_FORCE='+str({'oem-far-clock-low-v9':1,'oem-far-clock-high-v9':5,'oem-gop-mode-low-v10':1,'oem-gop-mode-high-v10':6}.get(json.loads(a.runtime_config.read_text())['experiment'],0))]
    for path in (inc,inc/'AArch64',ROOT/'firmware/Mu_Basecore/MdeModulePkg/Include',ROOT/'firmware/Mu_Basecore/ArmPkg/Include',
                 ROOT/'firmware/Silicon/Silicium/SiliciumPkg/Include',ROOT/'firmware/diagnostics',lib,out):cmd.append('-I'+str(path))
    subprocess.run(cmd+['-c',str(ROOT/('tests/oem_clock_arm.c' if clock else 'tests/oem_board_capture_arm.c')),'-o',str(out/'board.obj')],check=True)
    assembly=subprocess.check_output(['/usr/bin/llvm-objdump','-dr',out/'board.obj'],text=True)
    (out/'board.disassembly.txt').write_text(assembly)
    for token in (('MicroSecondDelay','ResetCold','CpuPause') if clock else ('LocateMemoryRegionByName','ResetCold','dsb','CurrentEL','PAR_EL1')):
        if token.lower() not in assembly.lower():raise ValueError('board code optimized out: '+token)
    strict_sha=None
    if clock:
        strict=[x for x in cmd if x!='-Wno-unused-function']+['-I'+str(out/'oem-control'),'-c',str(ROOT/'tests/oem_clock_binding_arm.c'),'-o',str(out/'strict-binding.obj')]
        subprocess.run(strict,check=True)
        strict_sha=hashlib.sha256((out/'strict-binding.obj').read_bytes()).hexdigest()
    result=dict(strict_binding_arm_sha256=strict_sha,passed=True,profiles=reports,hardware_executed=False,board_io_tested=False,
                source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in [
                    'tests/oem_core_binding.c','tests/oem_board_capture_arm.c','firmware/diagnostics/EnumaOemBoardCapture.h','firmware/diagnostics/EnumaOemCoreBinding.h','firmware/diagnostics/EnumaOemLoadedIdentity.h','firmware/Resources/Scripts/enuma_oem_identity.py']+(['tests/oem_clock_binding_arm.c','firmware/diagnostics/EnumaOemProgress.h','firmware/diagnostics/EnumaOemServiceTrace.h','tests/oem_clock_arm.c','firmware/diagnostics/EnumaOemExitClock.h','firmware/diagnostics/EnumaOemClockCapture.h','firmware/diagnostics/EnumaOemGopMode.h'] if clock else [])},
                board_arm_object_sha256=hashlib.sha256((out/'board.obj').read_bytes()).hexdigest())
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
