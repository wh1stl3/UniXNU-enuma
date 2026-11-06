"""Fault injection against actual built FD audit inputs; never modify originals."""
import argparse
import copy
import json
from pathlib import Path
from unittest.mock import patch
from audit_oem_development_fd import audit, ROOT, sha
from uefi_firmware.uefi import FirmwareVolume, FirmwareFile


def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();build=a.build.resolve();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    valid,pe=audit(build)
    report_path=build/'build-result.json';base=json.loads(report_path.read_text())
    fd=(ROOT/base['fd']).resolve();original_read=Path.read_text;original_bytes=Path.read_bytes
    checks=[]
    for name,change in [('wrong variant',lambda r:r.update(profile='oem-mmu-only' if r['profile']=='oem-control' else 'oem-control')),
                        ('claimed deployment',lambda r:r.update(deployment_ready=True)),
                        ('wrong FD hash',lambda r:r.update(fd_sha256='0'*64)),
                        ('wrong manifest hash',lambda r:r.update(source_manifest_sha256='0'*64)),
                        ('dispatch stage enabled',lambda r:r['firmware_configuration']['defines'].update(ENUMA_DIAG_STAGE='13'))]:
        modified=copy.deepcopy(base);change(modified)
        def read(path,*args,**kwargs):
            return json.dumps(modified) if path==report_path else original_read(path,*args,**kwargs)
        with patch.object(Path,'read_text',read):
            try:audit(build)
            except ValueError:checks.append(name)
            else:raise AssertionError('accepted '+name)
    def read_bytes(path):
        b=original_bytes(path)
        return b[:-1]+bytes([b[-1]^1]) if path==fd else b
    with patch.object(Path,'read_bytes',read_bytes):
        try:audit(build)
        except ValueError:checks.append('FD corruption')
        else:raise AssertionError('accepted altered FD')
    # The FV contains compression. Inject at the decoder output boundary,
    # leaving the envelope valid, to exercise the independent inner PE check.
    class ChangedPayload(FirmwareVolume):
        def process(self):
            result=super().process();queue=[self];changed=0
            while queue:
                obj=queue.pop(0);queue.extend(getattr(obj,'objects',[]))
                if not isinstance(obj,FirmwareFile):continue
                for section in obj.objects:
                    if section.type==0x10 and section.data==pe:
                        data=bytearray(pe);data[0x1994]^=1;section.data=bytes(data);changed+=1
            if changed!=1:raise AssertionError('ambiguous decoded OEM payload')
            return result
    with patch('audit_oem_development_fd.FirmwareVolume',ChangedPayload):
        try:audit(build)
        except ValueError as e:
            if 'OEM PE mismatch DisplayDxe' not in str(e):raise
            checks.append('changed decoded DisplayDxe with valid outer envelope')
        else:raise AssertionError('accepted changed OEM identity')
    after,_=audit(build);assert after==valid
    result=dict(passed=True,negative_checks=checks,count=len(checks),original_reverified=True,
                profile=valid['profile'],fd_sha256=valid['fd_sha256'],
                source_sha256={n:sha((ROOT/'scripts'/n).read_bytes()) for n in ('audit_oem_development_fd.py','check_oem_fd_audit.py')},hardware_executed=False)
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
