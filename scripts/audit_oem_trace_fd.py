"""Bind compiled OEM trace/capture code to a complete, non-deployable stage10 FD."""
import argparse,json,re,sys,hashlib,subprocess
from pathlib import Path
from audit_oem_development_fd import audit,ROOT,sha
from prepare_enuma_mmu_experiment import file_offset
sys.path.insert(0,str(ROOT/'firmware/Resources/Scripts'))
from enuma_oem_identity import generate


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build=a.build.resolve();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    base,display=audit(build);report=json.loads((build/'build-result.json').read_text())
    if report.get('oem_trace_build') is not True:raise ValueError('not a trace link build')
    identity=report['oem_trace_identity']
    if identity['stage10_gate'] is not True or identity['board_runtime_qualified'] is not False or identity['trial_nonce'] is not False:
        raise ValueError('trace scope mismatch')
    pe=out/'DisplayDxe.extracted.efi';pe.write_bytes(display)
    expected=generate(pe,out/'EnumaOemBuildIdentity.h')
    if any(identity.get(n)!=v for n,v in expected.items()):raise ValueError('generated identity mismatch')
    staged=build/'work/Mu_Basecore/MdeModulePkg/Core/Dxe/Dispatcher/EnumaOemBuildIdentity.h'
    if staged.read_bytes()!=(out/'EnumaOemBuildIdentity.h').read_bytes():raise ValueError('staged fingerprint mismatch')
    product=build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain/OUTPUT'
    core=(product/'DxeCore.efi').read_bytes();mapping=(product/'DxeCore.map').read_text()
    if sha(core)!=base['compiled_products_sha256']['DxeCore']:raise ValueError('Core mismatch')
    names=('EnumaTraceLocateProtocol','EnumaTraceHandleProtocol','EnumaTraceAllocatePool',
           'EnumaCaptureBeforeForward','OemBoardSink','OemCaptureTerminal')
    symbols={}
    for name in names:
        hits=re.findall(r'^([0-9a-f]+)\s+00000000\s+0\s+'+name+r'$',mapping,re.M)
        if len(hits)!=1:raise ValueError('missing/ambiguous linked trace function '+name)
        rva=int(hits[0],16);file_offset(core,rva);symbols[name]=hex(rva)
    assembly=subprocess.check_output(['/usr/bin/llvm-objdump','-d',product/'DxeCore.efi'],text=True)
    (out/'DxeCore.disassembly.txt').write_text(assembly)
    result=dict(passed=True,fd_audit=base,identity=identity,linked_symbols=symbols,
                core_sha256=sha(core),map_sha256=sha((product/'DxeCore.map').read_bytes()),
                disassembly_sha256=sha(assembly.encode()),
                source_sha256={n:sha((ROOT/n).read_bytes()) for n in ('scripts/audit_oem_trace_fd.py','firmware/Resources/Scripts/enuma_oem_identity.py')},
                deployment_ready=False,hardware_executed=False,
                limitation='linked code and exact staged identity; no full control-flow proof or board runtime qualification')
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
