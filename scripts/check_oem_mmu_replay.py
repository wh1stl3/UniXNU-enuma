"""Replay actual pinned mapper and board descriptors; host semantics, not live MMU."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 b=a.build.resolve();o=a.output.resolve();o.relative_to(ROOT/'out');o.mkdir(parents=True,exist_ok=False)
 core=b/'work/Mu_Basecore';uefi=b/'work/uefi'
 src=core/'UefiCpuPkg/Library/ArmMmuLib/AArch64/ArmMmuLibCore.c'
 mapping=uefi/'Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c'
 s=src.read_text();s=s[:s.index('STATIC\nUINT64\nGcdAttributeToPageAttribute')]
 (o/'replay_core.c').write_bytes(s.encode());(o/'replay_map.c').write_bytes(mapping.read_bytes())
 includes=[core/'MdePkg/Include',core/'MdePkg/Include/X64',core/'UefiCpuPkg/Include',core/'UefiCpuPkg/Library/ArmMmuLib',uefi/'Silicon/Silicium/SiliciumPkg/Include',o]
 cmd=['/usr/bin/clang','-std=c11','-fshort-wchar','-O1','-fsanitize=address,undefined','-fno-pie','-no-pie']+['-I'+str(i) for i in includes]+[str(ROOT/'tests/oem_mmu_replay.c'),'-o',str(o/'replay')]
 subprocess.run(cmd,check=True);output=subprocess.check_output([o/'replay'],text=True)
 result=dict(passed=True,hardware_executed=False,output=output,limitations=['Real C recursion and descriptor attributes; host allocator and register/cache/TLB stubs. No proof of active hardware mapping.'],sources={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [src,mapping,ROOT/'tests/oem_mmu_replay.c',ROOT/'scripts/check_oem_mmu_replay.py']})
 (o/'result.json').write_bytes(json.dumps(result,indent=2).encode());print(output)
if __name__=='__main__':main()
