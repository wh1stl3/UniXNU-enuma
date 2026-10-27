"""Check actual development-builder selector and vendor binding failure paths."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'firmware/Resources/Scripts/enuma_oem_profile.py'
BUILDER=ROOT/'firmware/Resources/Scripts/build_enuma_development.py'
spec=importlib.util.spec_from_file_location('oem',HELPER)
oem=importlib.util.module_from_spec(spec);spec.loader.exec_module(oem)


def main():
    p=argparse.ArgumentParser();p.add_argument('--pair',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    lock=(ROOT/'firmware/Resources/Enuma/vendor.json').read_bytes()
    checks=[]
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        tmp=Path(tmp)
        for profile,want in [('oem-control',oem.ORIGINAL),('oem-mmu-only',oem.PATCHED)]:
            build=tmp/profile;snapshot=build/'source';meta=snapshot/'Resources/Enuma';meta.mkdir(parents=True)
            (meta/'vendor.json').write_bytes(lock)
            vendor,binding=oem.bind(profile,a.pair,snapshot,build)
            assert binding['expected_pe_sha256']==want and oem.sha((vendor/oem.PE).read_bytes())==want
            assert (meta/'vendor.json.historical').read_bytes()==lock
            derivative=json.loads((meta/'vendor.json').read_text())
            before=json.loads(lock)['files'];after=derivative['files']
            assert [n for n in before if before[n]!=after[n]] == ([] if profile=='oem-control' else [oem.PE])
            flags={'ENUMA_DIAG_SIMPLEFB':'1','ENUMA_DEFERRED_MENU':'1','ENUMA_DIAG_STAGE':'13'}
            oem.defines(profile,flags)
            assert flags['ENUMA_DIAG_SIMPLEFB']=='0' and flags['ENUMA_DIAG_STAGE']=='10'
            assert flags['ENUMA_DEFERRED_MENU']=='0' and flags['ENUMA_GOP_SELFTEST']=='0'
            checks.append(profile+' copies exact bytes and binds snapshot-only derivative with stage10')
        for label,extra in [('missing pair',['--profile','oem-control']),
                            ('pair on old profile',['--profile','stage10','--oem-profile-pair',str(a.pair)]),
                            ('direct menu with OEM',['--profile','oem-mmu-only','--oem-profile-pair',str(a.pair),'--direct-menu'])]:
            dest=tmp/label.replace(' ','-')
            run=subprocess.run([sys.executable,'-B',str(BUILDER),'--device-root',str(ROOT),
                                '--output',str(dest),'--dependency-root',str(tmp/'deps')]+extra,capture_output=True,text=True)
            assert run.returncode==2 and not dest.exists(),run.stdout+run.stderr
            checks.append('CLI rejects '+label+' before output creation')
        broken=tmp/'broken';shutil.copytree(a.pair,broken)
        for label,relative in [('control source', 'oem-control/vendor/'+oem.PE),
                               ('MMU non-patch byte','oem-mmu-only/vendor/'+oem.PE),
                               ('panel','oem-mmu-only/vendor/raw/Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml')]:
            target=broken/relative;data=target.read_bytes();target.write_bytes(data[:-1]+bytes([data[-1]^1]))
            build=tmp/('bad-'+label.replace(' ','-'));snapshot=build/'source';meta=snapshot/'Resources/Enuma';meta.mkdir(parents=True)
            (meta/'vendor.json').write_bytes(lock)
            try:oem.bind('oem-mmu-only',broken,snapshot,build)
            except ValueError:pass
            else:raise AssertionError('accepted '+label)
            assert not (build/'oem-vendor').exists() and (meta/'vendor.json').read_bytes()==lock
            target.write_bytes(data);checks.append('reject '+label+' before staging or lock mutation')
    assert (ROOT/'firmware/Resources/Enuma/vendor.json').read_bytes()==lock
    result=dict(passed=True,count=len(checks),checks=checks,full_fd_built=False,
                source_sha256={str(p.relative_to(ROOT)):oem.sha(p.read_bytes()) for p in [HELPER,BUILDER,Path(__file__)]})
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':main()
