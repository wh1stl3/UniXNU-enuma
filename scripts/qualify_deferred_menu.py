"""Qualify a new bounded menu window FD/full FAT image offline; never deploy."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
if sys.version_info<(3,11):
    import tomli
    sys.modules['tomllib']=tomli
import tomllib
from deferred_menu_scope import SCOPE
from package_enuma_boot import verify
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('build','tests','menu-tests','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();build=args.build.resolve();out=args.output.resolve()
    build.relative_to(ROOT/'out');out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    result=dict(passed=False,execution_ready=False,hardware_execution=False,hardware_review='R-027',commands=[])
    def run(cmd):
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,cwd=ROOT)
        result['commands'].append(dict(argv=list(map(str,cmd)),returncode=p.returncode,stderr=p.stderr))
        if p.returncode:raise ValueError(p.stdout+p.stderr)
        return p.stdout
    try:
        b=json.loads((build/'build-result.json').read_text());manifest=json.loads((build/'source-manifest.json').read_text())
        if not b['complete'] or b['profile']!='deferred-menu' or b['deployment_ready']:raise ValueError('wrong development build')
        if sha(build/'source-manifest.json')!=b['source_manifest_sha256']:raise ValueError('manifest mismatch')
        for name,h in manifest['snapshot_files'].items():
            if sha(build/'source'/name)!=h:raise ValueError('staged source changed: '+name)
        for name,h in manifest['original_files'].items():
            if sha(ROOT/'firmware'/name)!=h:raise ValueError('current firmware differs: '+name)
        checks={}
        for label,folder in [('host',args.tests),('qemu',args.menu_tests)]:
            folder=folder.resolve();folder.relative_to(ROOT/'out');p=folder/'result.json';t=json.loads(p.read_text())
            if not t['passed'] or t.get('hardware_executed',False) or t.get('enuma_device_action',False):raise ValueError('invalid '+label+' test')
            if label=='qemu' and (not t.get('bounded_window') or not t.get('full_application') or not t.get('deferred_dispatch')):raise ValueError('not actual window adapter test')
            for name,h in t.get('sources',t.get('inputs',{})).items():
                path=Path(name) if Path(name).is_absolute() else ROOT/name
                if sha(path)!=h:raise ValueError('test source binding changed: '+name)
            checks[label]=dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
        recipe=json.loads((ROOT/'out/inherited-gop/qualified-dxe-log-8s-8680ea7/firmware-build.json').read_text())
        expected=dict(recipe['firmware_configuration']['defines'])
        expected.update(ENUMA_DEFERRED_MENU='1',ENUMA_FULL_MENU='1',ENUMA_BOUNDED_MENU='1',ENUMA_BOOT_LOG_REPLAY='0',ENUMA_NATIVE_ROUTE_CPU_TEXT='0',ENUMA_PROBE_JOURNAL_REPLAY='0')
        if b['firmware_configuration']['defines']!=expected:raise ValueError('unexpected build defines')
        config_source=(build/'source/diagnostics/EnumaMenuConfigFs.h').read_text()
        initializer=config_source.split('STATIC CONST CHAR8 mMenuConfig[]=')[1].split(';',1)[0]
        initializer=initializer.replace('ENUMA_MENU_ENTRY_TITLE',json.dumps('Driver returned - Return to firmware'))
        config=''.join(ast.literal_eval(x) for x in re.findall(r'"(?:[^"\\]|\\.)*"',initializer))
        parsed=tomllib.loads(config)
        if parsed!={'version':1,'boot':{'default':'return','timeout':8,'fallback_timeout':8,'connect_all':False},
                    'ui':{'title':'UniXNU','console':'graphics','layout':'landscape','scale':1,'logo':True},
                    'entry':[{'id':'return','title':'Driver returned - Return to firmware','type':'action','action':'exit'}]}:
            raise ValueError('private configuration differs from exit-only scope')
        (out/'private-menu-config.toml').write_text(config)
        fd=ROOT/b['fd']
        if sha(fd)!=b['fd_sha256']:raise ValueError('FD changed')
        shutil.copyfile(fd,out/'SILICIUM_UEFI.fd')
        audit=dict(b,deferred_menu=True,deferred_menu_scope=SCOPE,hardware_review_required='R-027')
        save(out/'actual-profile-build.json',audit)
        run([sys.executable,'-B',ROOT/'scripts/audit_enuma_fd.py','--fd',fd,'--build-report',out/'actual-profile-build.json','--report',out/'fd-audit.json'])
        products=build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64';actual={}
        for name in ('DxeCore','SimpleFbDxe','EnumaProbe','UniXNU','BdsDxe'):
            matches=list(products.rglob('OUTPUT/'+name+'.efi'))
            if len(matches)!=1:raise ValueError('missing/ambiguous '+name)
            pe=matches[0];flags=(pe.parent/'cc_resp.txt').read_text().split()
            if name in ('DxeCore','SimpleFbDxe'):
                for key in expected:
                    if key=='ENUMA_RAM_PAYLOAD':continue
                    if key in ('ENUMA_DEFERRED_MENU','ENUMA_FULL_MENU','ENUMA_BOUNDED_MENU','ENUMA_BOOT_LOG_REPLAY','ENUMA_DIAG_STAGE','ENUMA_DIAG_DETAIL_POINT','ENUMA_NATIVE_ROUTE_CPU_PATTERN') and '-D'+key+'='+expected[key] not in flags:raise ValueError('inactive compiler macro '+key)
            assembly=run(['llvm-objdump','-d',pe]);(out/(name+'.disassembly.txt')).write_text(assembly)
            if name=='SimpleFbDxe':
                if config.encode()+b'\0' not in pe.read_bytes():raise ValueError('exact private config missing from provider')
                if not re.search(r'\bdsb\s+sy',assembly):raise ValueError('actual pixel barriers missing')
                if re.search(r'\t(?:dc\s|msr\s+(?:ttbr|tcr|mair|sctlr|vttbr))',assembly):raise ValueError('unexpected cache/mapping writes')
            shutil.copyfile(pe,out/(name+'.efi'));actual[name]=dict(pe_sha256=sha(pe),cc_response_sha256=sha(pe.parent/'cc_resp.txt'))
        qemu=json.loads((args.menu_tests/'result.json').read_text())
        app_hashes=[h for n,h in qemu['inputs'].items() if n.endswith('/UniXNU.efi')]
        if app_hashes!=[actual['UniXNU']['pe_sha256']]:raise ValueError('QEMU did not execute this exact built UniXNU PE')
        sys.path.insert(0,str(ROOT/'out/sources/UniXNU/scripts'))
        from unixnu.bootimg import compile_shim
        shim=compile_shim(build/'work/uefi',0x9fc00000,0x300000,True,out)
        raw=out/'enuma-uefi.raw';raw.write_bytes(shim+fd.read_bytes())
        fat=ROOT/'out/full-boot/payload/payload.img'
        if sha(fat)!='49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773':raise ValueError('full FAT changed')
        aosp=Path('/mnt/d/Code/PortingiOSLegacy/common/sources/aosp-mkbootimg')
        lock=json.loads((ROOT/'config/porting-sources.lock.json').read_text())['aosp_mkbootimg']
        for name,h in lock['sha256'].items():
            if sha(aosp/name)!=h:raise ValueError('AOSP tool changed')
        image=out/'image.img'
        run([sys.executable,'-B',aosp/'mkbootimg.py','--header_version','3','--kernel',raw,'--ramdisk',fat,'--output',image])
        package=verify(image.read_bytes(),raw.read_bytes(),fat.read_bytes())
        run([sys.executable,'-B',aosp/'unpack_bootimg.py','--boot_img',image,'--out',out/'unpacked'])
        if (out/'unpacked/kernel').read_bytes()!=raw.read_bytes() or (out/'unpacked/ramdisk').read_bytes()!=fat.read_bytes():raise ValueError('AOSP roundtrip mismatch')
        save(out/'image.json',dict(package,image_sha256=sha(image),hardware_review='R-027',hardware_ready=False,pixel_scope=SCOPE))
        result.update(passed=True,image_sha256=sha(image),fd_sha256=sha(fd),scope=SCOPE,tests=checks,actual_modules=actual,
                      source_manifest_sha256=sha(build/'source-manifest.json'),
                      pending=['compiled instruction review','single-shot runner/source-document binding','current capture and fresh device guards'],
                      formal_gop=False,full_unixnu_run=True,bds_reached=False,physical_input=False)
    except Exception as exc:
        import traceback
        result.update(error=str(exc),traceback=traceback.format_exc())
    result['qualifier_sha256']=sha(Path(__file__))
    result['files']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
    save(out/'qualification.json',result)
    print(json.dumps({k:result[k] for k in ('passed','error','image_sha256') if k in result}));return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
