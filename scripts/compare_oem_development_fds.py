"""Compare audited control/MMU-only FD inputs and extracted OEM instructions."""
import argparse
import json
from pathlib import Path
from audit_oem_development_fd import audit, ROOT, sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--control',type=Path,required=True)
    p.add_argument('--mmu',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    control,cpe=audit(a.control);mmu,mpe=audit(a.mmu)
    if control['profile']!='oem-control' or mmu['profile']!='oem-mmu-only':raise ValueError('reversed profile pair')
    manifests=[json.loads((b/'source-manifest.json').read_text()) for b in (a.control,a.mmu)]
    if manifests[0]['original_files']!=manifests[1]['original_files']:raise ValueError('different firmware source inputs')
    reports=[json.loads((b/'build-result.json').read_text()) for b in (a.control,a.mmu)]
    if reports[0]['firmware_configuration']!=reports[1]['firmware_configuration']:raise ValueError('different build defines')
    if len(cpe)!=len(mpe) or cpe[:0x1994]!=mpe[:0x1994] or cpe[0x1998:]!=mpe[0x1998:]:
        raise ValueError('changes beyond permitted instruction')
    if cpe[0x1994:0x1998]!=bytes.fromhex('e1031f32') or mpe[0x1994:0x1998]!=bytes.fromhex('01008052'):
        raise ValueError('wrong instruction replacement')
    result=dict(passed=True,control=control,mmu=mmu,firmware_source_inputs_identical=True,
                build_configuration_identical=True,display_instruction_offset='0x1994',
                display_before='e1031f32',display_after='01008052',
                display_changed_byte_offsets=[hex(i) for i,(x,y) in enumerate(zip(cpe,mpe)) if x!=y],
                script_sha256=sha(Path(__file__).read_bytes()),
                scope='static build comparison; no OEM execution or deployment qualification')
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
