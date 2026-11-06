"""Exact OEM main-entry path and fixed AArch64 ChipInfo ABI; offline only."""
import argparse,hashlib,json,struct,subprocess,uuid
from pathlib import Path
from map_oem_trace_rva import identify,sections,map_return
ROOT=Path(__file__).resolve().parents[1]
def analyze(pe):
 b=Path(pe).read_bytes();digest=identify(b)
 def offset(rva):
  s=next(s for s in sections(b) if s[1]<=rva< s[1]+s[2]);return s[3]+rva-s[1]
 def word(rva):return struct.unpack_from('<I',b,offset(rva))[0]
 expected={0x1470:0x940016e3,0x7014:0x17fffad4,0x5cc0:0xf940606a,0x5cc4:0xd63f0140,
           0x5cc8:0xaa1f03e0,0x5cdc:0xd65f03c0,0x1738:0x940069ad,0x1760:0x9400079a,
           0x3600:0xf940a108,0x3604:0xd63f0100,0x3608:0xb50000a0,
           0x3614:0xf9401809,0x3618:0xd63f0120,0x17d8:0x321d03e1,0x17e0:0xd63f0100}
 for rva,value in expected.items():
  if word(rva)!=value:raise ValueError('OEM instruction differs at '+hex(rva))
 guid=uuid.UUID(bytes_le=b[offset(0x3e208):offset(0x3e208)+16])
 if str(guid)!='b0760469-970c-487a-a4b5-28db7b45cef1':raise ValueError('main query GUID differs')
 return dict(pe_sha256=digest,chipinfo_guid=str(guid),registration_return=map_return(b,0x5cc8),
             main_query=map_return(b,0x3608),chip_family_method=map_return(b,0x361c),
             first_create_event=map_return(b,0x17e4),instructions={hex(a):hex(w) for a,w in expected.items()},
             hardware_execution_proven=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--pe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(exist_ok=False,parents=True)
 result=analyze(a.pe)
 src=out/'chipinfo_abi.c';src.write_text('#include <Uefi.h>\n#include <Protocol/EFIChipInfo.h>\n_Static_assert(__builtin_offsetof(EFI_CHIPINFO_PROTOCOL,GetChipFamily)==48,"ChipInfo ABI");\n')
 inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include'
 cmd=['/usr/bin/clang','-target','aarch64-unknown-windows-msvc','-ffreestanding','-Wall','-Wextra','-Werror','-I'+str(inc),'-I'+str(inc/'AArch64'),'-I'+str(ROOT/'firmware/Silicon/Qualcomm/QcomPkg/Include'),'-c',str(src),'-o',str(out/'chipinfo_abi.obj')]
 r=subprocess.run(cmd,capture_output=True,text=True);result['abi_compile']=dict(argv=cmd,returncode=r.returncode,stderr=r.stderr)
 if r.returncode:raise ValueError(r.stderr)
 result['sources']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['scripts/check_oem_main_path.py','firmware/Silicon/Qualcomm/QcomPkg/Include/Protocol/EFIChipInfo.h','firmware/Silicon/Qualcomm/QcomPkg/Include/Protocol/EFIChipInfoTypes.h']}
 result['passed']=True;(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS: exact OEM ChipInfo query, GetChipFamily ABI, registration return and main event sites')
if __name__=='__main__':main()
