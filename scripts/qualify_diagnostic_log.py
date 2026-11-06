"""Bind the new diagnostic-log FD, packaged PEs and full FAT Boot v3; no device."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid
if sys.version_info<(3,11):
    import tomli
    sys.modules['tomllib']=tomli
from package_enuma_boot import verify
from native_pixel_scope import ATTRIBUTED_LOG_SCOPE

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('build','tests','console-tests','menu-tests','output'): p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();build=a.build.resolve();tests=a.tests.resolve();out=a.output.resolve()
    for v in (build,tests,out): v.relative_to(ROOT/'out')
    out.mkdir(parents=True,exist_ok=False)
    result=dict(passed=False,hardware_execution=False,execution_ready=False,hardware_review='R-024',commands=[])
    def run(cmd):
        r=subprocess.run(list(map(str,cmd)),text=True,capture_output=True,cwd=ROOT)
        result['commands'].append(dict(argv=list(map(str,cmd)),returncode=r.returncode,stderr=r.stderr))
        if r.returncode: raise ValueError(r.stdout+r.stderr)
        return r.stdout
    try:
        b=json.loads((build/'build-result.json').read_text());manifest=json.loads((build/'source-manifest.json').read_text())
        assert b['complete'] and b['profile']=='diagnostic-log' and not b['deployment_ready']
        assert sha(build/'source-manifest.json')==b['source_manifest_sha256']
        for n,h in manifest['snapshot_files'].items(): assert sha(build/'source'/n)==h,n
        t=json.loads((tests/'result.json').read_text());assert t['passed'] and not t['hardware_executed']
        assert t['context_free_glyph_inverse'] and t['unique_glyphs']==25
        for n,h in t['sources'].items(): assert sha(ROOT/n)==h,n
        extra_tests={}
        for label,folder in [('console',a.console_tests),('menu',a.menu_tests)]:
            folder=folder.resolve();folder.relative_to(ROOT/'out')
            rp=folder/'result.json';r=json.loads(rp.read_text());assert r['passed'],label
            assert r.get('hardware_executed',False) is False and r.get('enuma_device_action',False) is False
            for n,h in r['sources' if label=='console' else 'inputs'].items(): assert sha(ROOT/n)==h,(label,n)
            extra_tests[label]={'path':str(rp.relative_to(ROOT)),'sha256':sha(rp)}
        for n,h in manifest['original_files'].items(): assert sha(ROOT/'firmware'/n)==h,n
        frozen=ROOT/'out/inherited-gop/qualified-dxe-log-8s-8680ea7'
        q=json.loads((frozen/'qualification.json').read_text())
        assert sha(frozen/'qualification.json')=='1d730f656f05d80b595168736807c1f1afe6fbcab19d5a3041c101a73cf55e9d'
        for n,d in q['files'].items(): assert sha(frozen/n)==d['sha256'],n
        defs=b['firmware_configuration']['defines']
        expected=dict(json.loads((frozen/'firmware-build.json').read_text())['firmware_configuration']['defines'])
        expected['ENUMA_BOOT_LOG_REPLAY']='3';expected['ENUMA_PROBE_JOURNAL_REPLAY']='1';assert defs==expected
        uefi=build/'work/uefi';products=uefi/'Build/enumaPkg/DEBUG_CLANGPDB/AARCH64'
        fd=ROOT/b['fd'];assert sha(fd)==b['fd_sha256'];shutil.copyfile(fd,out/'SILICIUM_UEFI.fd')
        # Preserve build-result; create a separately named actual-profile audit input.
        audit=dict(b,native_route_cpu_pattern=True,native_route_cpu_text=False,boot_log_replay=True,
                   boot_log_hold_seconds=8,diagnostic_pixel_log=True,hardware_review_required='R-024',
                   inherited_video_terminal=True,diagnostic_dispatch_completion_fallback=False,
                   diagnostic_gop_query=1,diagnostic_gop_step=0,value_probe={'source':'off'},
                   diagnostic_simplefb_metadata_only=False,
                   attributed_pixel_scope=dict(origin_x=64,origin_y=96,width=320,height=160,hold_us=8000000,barriers_max=3),
                   inherited_video_compiled_contract=dict(maximum_read_callbacks=660,maximum_wait_calls=5,
                     maximum_framebuffer_reads=153600,framebuffer_writes=102400,pixel_access=True,
                     cache_maintenance=False,protocol_published=False))
        # maximum_wait_calls includes four MDP waits plus the single pixel hold.
        actual={}
        for name in ('DxeCore','SimpleFbDxe','EnumaProbe','BdsDxe','UniXNU','GraphicsConsoleDxe'):
            matches=list(products.rglob('OUTPUT/'+name+'.efi'));assert len(matches)==1,(name,matches)
            pe=matches[0];response=pe.parent/'cc_resp.txt';flags=response.read_text().split()
            if name in ('DxeCore','SimpleFbDxe'):
                for k in ('ENUMA_DIAG_STAGE','ENUMA_DIAG_DETAIL_POINT','ENUMA_DIAG_GUID_LOW64','ENUMA_DIAG_GUID_HIGH64','ENUMA_DIAG_GUID_ONLY','ENUMA_DIAG_GOP_QUERY','ENUMA_VIDEO_TERMINAL','ENUMA_BOOT_JOURNAL','ENUMA_BOOT_LOG_REPLAY','ENUMA_BOOT_LOG_HOLD_US','ENUMA_NATIVE_ROUTE_CPU_PATTERN','ENUMA_RAM_PAYLOAD'):
                    assert '-D'+k+'='+defs[k] in flags,(name,k)
            if name=='EnumaProbe': assert '-DENUMA_PROBE_JOURNAL_REPLAY=1' in flags
            shutil.copyfile(pe,out/(name+'.efi'));shutil.copyfile(response,out/(name+'.cc_resp.txt'))
            dis=run(['llvm-objdump','-d','--print-imm-hex',pe]);(out/(name+'.disassembly.txt')).write_text(dis)
            actual[name]={'pe_sha256':sha(pe),'cc_response_sha256':sha(response)}
        # Match actual packaged PE bytes and provide a GUID->PE catalog for later photographs.
        from audit_display_handoff import firmware_files
        catalog={}
        for item in firmware_files(fd.read_bytes()):
            catalog.setdefault(item['guid'],[]).append(dict(name=item['name'],sha256=hashlib.sha256(item['data']).hexdigest()))
        save(out/'packaged-guid-catalog.json',catalog)
        for name,data in actual.items():
            assert any(x['name']==name and x['sha256']==data['pe_sha256'] for entries in catalog.values() for x in entries),name
        save(out/'actual-profile-build.json',audit)
        run([sys.executable,'-B',ROOT/'scripts/audit_enuma_fd.py','--fd',fd,'--build-report',out/'actual-profile-build.json','--report',out/'fd-audit.json'])
        pe=(out/'SimpleFbDxe.efi').read_bytes();core=(out/'DxeCore.efi').read_bytes()
        journal=uuid.UUID('a84039f7-b861-5dbe-9a09-a4f6cc746d5b').bytes_le
        assert journal in pe and journal in core
        glyph=(build/'source/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/PixelDiagnosticLogPage.h').read_text().split('Glyph[25][5]={')[1].split('};')[0]
        assert bytes(int(x) for x in re.findall(r'\d+',glyph)) in pe
        assembly=(out/'SimpleFbDxe.disassembly.txt').read_text()
        assert len(re.findall(r'\bdsb\s+sy',assembly))==3
        assert not re.search(r'\t(?:dc\s|msr\s+(?:ttbr|tcr|mair|sctlr|vttbr))',assembly), 'forbidden instruction mnemonic'
        # New scope requires an explicit, separate instruction review; fingerprints alone are not it.
        if sys.version_info<(3,11):
            import tomli
            sys.modules['tomllib']=tomli
        sys.path.insert(0,str(ROOT/'out/sources/UniXNU/scripts'))
        from unixnu.bootimg import compile_shim
        shim=compile_shim(uefi,0x9fc00000,0x300000,True,out)
        raw=out/'enuma-uefi.raw';raw.write_bytes(shim+fd.read_bytes())
        fat=ROOT/'out/full-boot/payload/payload.img'
        assert sha(fat)=='49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773'
        aosp=Path('/mnt/d/Code/PortingiOSLegacy/common/sources/aosp-mkbootimg')
        lock=json.loads((ROOT/'config/porting-sources.lock.json').read_text())['aosp_mkbootimg']
        for n,h in lock['sha256'].items(): assert sha(aosp/n)==h,n
        image=out/'image.img'
        run([sys.executable,'-B',aosp/'mkbootimg.py','--header_version','3','--kernel',raw,'--ramdisk',fat,'--output',image])
        package=verify(image.read_bytes(),raw.read_bytes(),fat.read_bytes())
        run([sys.executable,'-B',aosp/'unpack_bootimg.py','--boot_img',image,'--out',out/'unpacked'])
        assert (out/'unpacked/kernel').read_bytes()==raw.read_bytes()
        assert (out/'unpacked/ramdisk').read_bytes()==fat.read_bytes()
        save(out/'image.json',dict(package,image_sha256=sha(image),hardware_review='R-024',hardware_ready=False,
                                  scope=audit['attributed_pixel_scope'],pixel_scope=ATTRIBUTED_LOG_SCOPE,diagnostic_pixel_log=True))
        result.update(passed=True,image_sha256=sha(image),fd_sha256=sha(fd),full_payload_sha256=sha(fat),actual_modules=actual,
                      source_manifest_sha256=sha(build/'source-manifest.json'),tests_sha256=sha(tests/'result.json'),
                      extra_tests=extra_tests,frozen_r022_all_bindings_unchanged=True,scope=audit['attributed_pixel_scope'],
                      pending=['actual PE instruction review','new exact-scope single-shot runner qualification',
                               'explicit single-shot approval and current filming readiness','fresh device identity/backups/recovery/clock gates'],
                      current_provider_return=False,global_debug=False,formal_gop=False,menu_hardware_tested=False)
    except Exception as exc:
        import traceback
        result['error']=repr(exc);result['traceback']=traceback.format_exc()
    finally:
        result['qualifier_sha256']=sha(Path(__file__))
        result['audit_tool_bindings']={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'scripts/firmware_audit_policy.py',ROOT/'scripts/audit_enuma_fd.py',ROOT/'scripts/audit_display_handoff.py',ROOT/'scripts/package_enuma_boot.py',ROOT/'scripts/native_pixel_scope.py']}
        result['files']={str(p.relative_to(out)):sha(p) for p in out.iterdir() if p.is_file()}
        save(out/'qualification.json',result)
    print(json.dumps({k:result[k] for k in ('passed','error','image_sha256','fd_sha256') if k in result}))
    return 0 if result['passed'] else 1


if __name__=='__main__': raise SystemExit(main())
