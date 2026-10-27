"""Extract and verify an OEM stage10 development FD; never grant deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import uuid
from uefi_firmware.uefi import FirmwareVolume, FirmwareFile

ROOT=Path(__file__).resolve().parents[1]
IDENTITIES={'oem-control':'6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425',
            'oem-mmu-only':'ed37a4e137cca2fcf4d5fa5718e18a319c2aa1b7a1cfab480693325bfbe2b5e3'}
DISPLAY='4138022f-06c7-4f79-9c94-7e33b511a4e7'
def sha(b):return hashlib.sha256(b).hexdigest()


def audit(build, runtime=False):
    build=Path(build).resolve();build.relative_to(ROOT/'out')
    report=json.loads((build/'build-result.json').read_text());profile=report.get('profile')
    if profile not in IDENTITIES or report.get('complete') is not True or report.get('deployment_ready') is not False:
        raise ValueError('not a complete unqualified OEM development build')
    if report.get('hardware_execution') is not False:raise ValueError('unexpected execution claim')
    fd=(ROOT/report['fd']).resolve();fd.relative_to(build)
    blob=fd.read_bytes()
    if sha(blob)!=report['fd_sha256'] or len(blob)!=0x300000 or blob[40:44]!=b'_FVH':
        raise ValueError('FD envelope/hash mismatch')
    manifest_path=build/'source-manifest.json'
    if sha(manifest_path.read_bytes())!=report['source_manifest_sha256']:raise ValueError('manifest mismatch')
    manifest=json.loads(manifest_path.read_text())
    for n,h in manifest['snapshot_files'].items():
        p=(build/'source'/n).resolve();p.relative_to(build/'source')
        if sha(p.read_bytes())!=h:raise ValueError('snapshot mismatch: '+n)
    required={'ENUMA_DIAG_STAGE':'10','ENUMA_DIAG_SIMPLEFB':'0','ENUMA_GOP_SELFTEST':'0',
              'ENUMA_DIAG_DISABLE_UFS':'1','ENUMA_DIRECT_MENU':'0','ENUMA_DEFERRED_MENU':'0',
              'ENUMA_FULL_MENU':'0','ENUMA_BOUNDED_MENU':'0'}
    if runtime:
        identity=report.get('oem_trace_identity') or {}
        if profile!='oem-control' or not report.get('oem_trace_build') or not report.get('oem_run_config') or \
           identity.get('stage10_gate') is not False or identity.get('trial_nonce') is not True:
            raise ValueError('runtime trace identity absent')
        required.update(ENUMA_DIAG_STAGE='13',ENUMA_DIAG_DETAIL_POINT='13',ENUMA_DIAG_GUID_ENABLED='1',
                        ENUMA_DIAG_GUID_ONLY='1',ENUMA_DIAG_GUID_LOW64='0x4f7906c74138022f',
                        ENUMA_DIAG_GUID_HIGH64='0xe7a411b5337e949c',ENUMA_DIAG_DISPATCH_FALLBACK='1')
    if runtime and report['oem_run_config']['experiment']=='oem-far-chain-v7':required['ENUMA_OEM_FAR_CHAIN']='1'
    defs=report['firmware_configuration']['defines']
    if any(defs.get(n)!=v for n,v in required.items()):raise ValueError('wrong profile defines')
    binding=report['oem_profile_binding']
    if binding['profile']!=profile or binding['expected_pe_sha256']!=IDENTITIES[profile]:raise ValueError('variant mismatch')
    volume=FirmwareVolume(blob)
    if not volume.process():raise ValueError('cannot decode FD')
    queue=[volume];files={};apriori=[]
    while queue:
        obj=queue.pop(0);queue.extend(getattr(obj,'objects',[]))
        if not isinstance(obj,FirmwareFile) or obj.type==0xf0:continue
        guid=str(uuid.UUID(bytes_le=obj.guid))
        if guid in files:raise ValueError('duplicate file GUID')
        sections=obj.objects
        files[guid]={'name':next((s.data.decode('utf-16-le').rstrip('\0') for s in sections if s.type==0x15),guid),
                     'pe':[s.data for s in sections if s.type==0x10],
                     'depex':[sha(s.data) for s in sections if s.type==0x13],
                     'raw':[sha(s.data) for s in sections if s.type==0x19]}
        if guid=='fc510ee7-ffdc-11d4-bd41-0080c73c8881':
            raws=[s.data for s in sections if s.type==0x19]
            if len(raws)!=1 or len(raws[0])%16:raise ValueError('invalid APRIORI')
            apriori=[str(uuid.UUID(bytes_le=raws[0][i:i+16])) for i in range(0,len(raws[0]),16)]
    if not apriori or DISPLAY not in apriori or any(g not in files for g in apriori):raise ValueError('invalid OEM scheduling identity')
    matched=[]
    inventory=json.loads((ROOT/'reports/enuma-oem-modules.json').read_text())
    for m in inventory['selected_modules']:
        f=files.get(m['guid'])
        if m['name']=='UFSDxe':
            if f or m['guid'] in apriori:raise ValueError('UFS unexpectedly included')
            continue
        wanted=IDENTITIES[profile] if m['guid']==DISPLAY else m['pe_sha256']
        if not f or [sha(b) for b in f['pe']]!=[wanted]:raise ValueError('OEM PE mismatch '+m['name'])
        if f['depex']!=([m['depex_sha256']] if m['depex_sha256'] else []):raise ValueError('DEPEX mismatch '+m['name'])
        matched.append(m['name'])
    if any(f['name'] in ('SimpleFbDxe','EnumaGopSelfTest') for f in files.values()):raise ValueError('adapter leaked into OEM profile')
    for guid,n in [('2962bfba-d7e7-4f37-a4c6-e28f7b5a685a','raw/Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml'),
                   ('c3f9fa09-0b18-b0f8-7aa7-10f761a6c699','raw/Panel_K81_35_02_0b_dualdsi_cphy_lcd_vid.xml')]:
        if files.get(guid,{}).get('raw')!=[binding['vendor_files'][n]]:raise ValueError('native panel RAW mismatch')
    products=build/'work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64'
    flags={};products_verified={}
    for name in (('DxeCore','EnumaProbe','ArmCpuDxe') if runtime else ('DxeCore','EnumaProbe')):
        pes=list(products.rglob('OUTPUT/'+name+'.efi'))
        if len(pes)!=1:raise ValueError('missing/ambiguous product '+name)
        packed=[b for f in files.values() if f['name']==name for b in f['pe']]
        if packed!=[pes[0].read_bytes()]:raise ValueError('compiled product differs from FD '+name)
        response=pes[0].parent/'cc_resp.txt';text=response.read_text()
        for n in ('ENUMA_DIAG_STAGE','ENUMA_DIAG_SIMPLEFB'):
            if '-D'+n+'='+required[n] not in text.split():raise ValueError('compiler flags mismatch '+name)
        if runtime and report['oem_run_config']['experiment']=='oem-far-chain-v7' and '-DENUMA_OEM_FAR_CHAIN=1' not in text.split():raise ValueError('far chain compiler flag missing')
        if runtime and name=='DxeCore':
            for n in ('ENUMA_DIAG_DETAIL_POINT','ENUMA_DIAG_GUID_ENABLED','ENUMA_DIAG_GUID_ONLY',
                      'ENUMA_DIAG_GUID_LOW64','ENUMA_DIAG_GUID_HIGH64','ENUMA_DIAG_DISPATCH_FALLBACK'):
                if '-D'+n+'='+required[n] not in text.split():raise ValueError('runtime compiler flag mismatch '+n)
        flags[name]=sha(response.read_bytes())
        products_verified[name]=sha(packed[0])
    return dict(passed=True,profile=profile,fd_sha256=sha(blob),display_pe_sha256=sha(files[DISPLAY]['pe'][0]),
                matched_oem=matched,apriori_count=len(apriori),panel_raw_verified=True,compiler_response_sha256=flags,
                compiled_products_sha256=products_verified,source_manifest_sha256=report['source_manifest_sha256'],
                auditor_sha256=sha(Path(__file__).read_bytes()),
                deployment_ready=False,hardware_executed=False),files[DISPLAY]['pe'][0]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    result,pe=audit(a.build)
    (out/'DisplayDxe.extracted.efi').write_bytes(pe)
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
