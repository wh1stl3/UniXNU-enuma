"""Exact OEM PE static parameter provenance; not a captured call stack."""
import argparse,hashlib,json,struct,uuid
from pathlib import Path
from prepare_enuma_mmu_experiment import file_offset
ROOT=Path(__file__).resolve().parents[1]
WORDS={0x156e0:0xf9400008,0x156e4:0xb40000c8,0x156f4:0xf903e928,
 0x263b8:0x2a1f03f4,0x263c0:0x320003e1,0x263c4:0x2a1403e0,0x263c8:0x9400134b,
 0x263d4:0xb9404809,0x263d8:0x6b09029f,0x263dc:0x54ffff23,
 0x2b10c:0x52801614,0x2b110:0x2a0003f3,0x2b114:0x72a00174,
 0x2b118:0x12000036,0x2b11c:0x9400009f,0x2b124:0x331f02d6,
 0x2b128:0x520006c8,0x2b12c:0xf943eaa9,0x2b134:0x8b09000a,
 0x2b138:0x8b140149,0x2b13c:0x2a1303e0,0x2b140:0xb8154128,
 0x2b3a0:0xb9404928,0x2b3a4:0x6b00011f,0x2b3a8:0x540000a9,
 0x2b3b4:0xf8605940,0x2b3bc:0xaa1f03e0,0x2b3c0:0xd65f03c0}
def verify(b):
 for r,w in WORDS.items():
  if struct.unpack_from('<I',b,file_offset(b,r))[0]!=w:raise ValueError('parameter instruction differs '+hex(r))
 if b[0x38d63:0x38d68]!=b'MDSS\0':raise ValueError('region name differs')
 if str(uuid.UUID(bytes_le=b[0x3e328:0x3e338]))!='9e61de7c-9927-4f28-9f3d-320705d81801':raise ValueError('HWIO GUID differs')
def main():
 p=argparse.ArgumentParser();p.add_argument('--pe',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 o=a.output.resolve();o.relative_to(ROOT/'out');o.mkdir(parents=True,exist_ok=False);b=a.pe.read_bytes()
 if hashlib.sha256(b).hexdigest()!='6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425':raise ValueError('foreign OEM PE')
 verify(b)
 for r in WORDS:
  v=bytearray(b);struct.pack_into('<I',v,file_offset(v,r),0xd503201f)
  try:verify(bytes(v))
  except ValueError:pass
  else:raise ValueError('deleted parameter instruction accepted')
 result=dict(passed=True,pe_sha256=hashlib.sha256(b).hexdigest(),instruction_deletions=len(WORDS),
  provenance=['HWIO MapRegion("MDSS") output through structure setter to global RVA 0x467d0','VBIF ID loop starts at 0, compares hardware-info count at offset72; flags=1 at direct call','base + instance_offset + 0xb0004 is the fault effective address'],
  limitations=['Static callers are not proof of this runtime call stack','Invalid ID returns offset0; matching FAR cannot prove individual inputs','No original firmware parameter value changed'])
 (o/'result.json').write_bytes(json.dumps(result,indent=2).encode());print('PASS exact OEM parameter path and deletion checks')
if __name__=='__main__':main()
