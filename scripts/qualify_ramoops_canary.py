"""Freeze exact R-017 actual FD/Core/map/full-FAT candidate, no device actions."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys
if sys.version_info<(3,11):
    import tomli
    sys.modules['tomllib']=tomli
from audit_display_handoff import firmware_files
from package_enuma_boot import verify
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--reviewed-disassembly-sha256')
    p.add_argument('--tool-path',type=Path)
    p.add_argument('--map-control',action='store_true')
    p.add_argument('--read-header',action='store_true')
    p.add_argument('--warm-control',action='store_true')
    a=p.parse_args();image=a.image.resolve();archive=a.archive.resolve()
    if sum([a.read_header,a.map_control,a.warm_control])>1:raise ValueError('exclusive read/map profile')
    control=a.map_control or a.read_header or a.warm_control
    if a.tool_path:sys.path.insert(0,str(a.tool_path.resolve()))
    if not image.is_relative_to(ROOT/'out') or not archive.is_relative_to(ROOT/'out') or archive.exists():
        raise ValueError('new archive and image must be in out/')
    build=json.loads((ROOT/'reports/enuma-firmware-build.json').read_text())
    pin=json.loads((ROOT/'config/uefi-source.lock.json').read_text())
    expected={'complete':True,'diagnostic_stop_stage':10,'diagnostic_delay_seconds':2,
              'diagnostic_dispatch_guid':None,'diagnostic_dispatch_guid_only':False,
              'diagnostic_dispatch_completion_fallback':False,'diagnostic_gop_query':0,
              'diagnostic_gop_step':0,'diagnostic_pixel_preview':False,
              'inherited_video_audit_read_only':False,'gop_backend_selftest_ram_only':False,
              'hardware_review_required':'R-017-WARM' if a.warm_control else 'R-017-READ' if a.read_header else ('R-017-MAP' if control else 'R-017'),
              'diagnostic_omitted_oem_modules':['CPRDxe','DisplayDxe','UFSDxe']}
    if any(build.get(k)!=v for k,v in expected.items()) or build['uefi_source_commit']!=pin['commit']:
        raise ValueError('wrong R-017 build profile')
    if bool(build.get('ramoops_map_control',False))!=a.map_control:raise ValueError('map control selection differs')
    if bool(build.get('ramoops_read_header',False))!=a.read_header:raise ValueError('read profile differs')
    if bool(build.get('ramoops_warm_control',False))!=a.warm_control:raise ValueError('warm profile differs')
    nonce=build.get('ramoops_canary_nonce','')
    if (control and nonce is not None) or (not control and (not isinstance(nonce,str) or re.fullmatch('[0-9a-f]{32}',nonce) is None)):
        raise ValueError('wrong nonce/control profile')
    defs=build['firmware_configuration']['defines']
    if (defs['ENUMA_RAM_PAYLOAD']!='1' or defs['ENUMA_RAMOOPS_CANARY']!=('0' if control else '1') or
        defs.get('ENUMA_RAMOOPS_MAP')!='1' or defs['ENUMA_VALUE_SOURCE']!='0'):
        raise ValueError('full FAT and standalone canary required')
    if a.read_header and defs.get('ENUMA_RAMOOPS_READ_HEADER')!='1':raise ValueError('read flag missing')
    if a.warm_control and defs.get('ENUMA_RAMOOPS_WARM_CONTROL')!='1':raise ValueError('warm flag missing')
    if any(defs['ENUMA_RAMOOPS_NONCE_'+str(i)]!=str(0 if control else int(nonce[i*8:i*8+8],16))+'U' for i in range(4)):
        raise ValueError('nonce words differ')
    fd=ROOT/build['fd'];raw=ROOT/'out/boot-candidate/enuma-uefi.raw';fat=ROOT/'out/full-boot/payload/payload.img'
    audit=json.loads((ROOT/'reports/enuma-fd-audit.json').read_text());full=json.loads((ROOT/'reports/enuma-full-payload.json').read_text())
    if sha(fd)!=build['fd_sha256'] or sha(fd)!=audit['fd_sha256'] or raw.read_bytes()[192:]!=fd.read_bytes() or sha(fat)!=full['payload_sha256']:
        raise ValueError('FD/raw/full FAT mismatch')
    package=verify(image.read_bytes(),raw.read_bytes(),fat.read_bytes())
    meta=json.loads(image.with_suffix('.json').read_text())
    if meta.get('hardware_review')!=expected['hardware_review_required'] or meta['image_sha256']!=sha(image):raise ValueError('missing protected package tag')
    modules=list(firmware_files(fd.read_bytes())); names=[m['name'] for m in modules]
    if any(n in names for n in ['DisplayDxe','CPRDxe','UFSDxe','EnumaGopSelfTest']) or not all(n in names for n in ['SimpleFbDxe','EnumaRamPayloadDxe','EnumaProbe']):
        raise ValueError('wrong actual modules')
    core=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain'
    pe=core/'OUTPUT/DxeCore.efi';make=core/'GNUmakefile'
    actual=[m for m in modules if m['guid']=='d6a2cb7f-6a18-4e2f-b43b-9920a733700a']
    if len(actual)!=1 or hashlib.sha256(actual[0]['data']).hexdigest()!=sha(pe):raise ValueError('actual packaged Core differs')
    text=make.read_text()
    for k in ['ENUMA_RAMOOPS_MAP','ENUMA_RAMOOPS_CANARY','ENUMA_DIAG_STAGE','ENUMA_DIAG_DELAY_US','ENUMA_RAM_PAYLOAD','ENUMA_DIAG_GOP_QUERY','ENUMA_VALUE_SOURCE']+['ENUMA_RAMOOPS_NONCE_'+str(i) for i in range(4)]:
        if set(re.findall(r'-D'+k+r'=([^\s]+)',text))!={defs[k]}:raise ValueError('actual Core flags differ: '+k)
    if a.read_header and set(re.findall(r'-DENUMA_RAMOOPS_READ_HEADER=([^\s]+)',text))!={'1'}:
        raise ValueError('actual read flag differs')
    if a.warm_control and set(re.findall(r'-DENUMA_RAMOOPS_WARM_CONTROL=([^\s]+)',text))!={'1'}:
        raise ValueError('actual warm flag differs')
    staged=ROOT/'out/firmware-build/Mu_Basecore/MdeModulePkg/Core/Dxe/DxeMain'
    stage_header='EnumaRamoopsWarmCheckpoint.h' if a.warm_control else 'EnumaRamoopsReadCheckpoint.h' if a.read_header else ('EnumaStageCheckpoint.h' if control else 'EnumaRamoopsStageCheckpoint.h')
    if (staged/'EnumaStageCheckpoint.h').read_bytes()!=(ROOT/'firmware/diagnostics'/stage_header).read_bytes():
        raise ValueError('actual staged stage header differs')
    if not control:
        for n in ['EnumaRamoopsCanary.h','EnumaRamoopsBuffer.h']:
            if (staged/n).read_bytes()!=(ROOT/'firmware/diagnostics'/n).read_bytes():raise ValueError('staged writer differs')
    prefix=b'Ramoops Console'+b'\0'*(32-len('Ramoops Console'))+struct.pack('<QQ',0xb0000000,0x200000)
    records=[]
    for m in modules:
        start=0
        while True:
            offset=m['data'].find(prefix,start)
            if offset<0:break
            fields=struct.unpack_from('<IIQII',m['data'],offset+48)
            if fields!=(1,5,0x400,0,0):raise ValueError('actual console descriptor HOB/resource/cache/type differs')
            records.append(dict(module=m['name'],offset=offset,fields=list(fields)))
            start=offset+len(prefix)
    if not records:raise ValueError('console record absent in actual FD')
    source_map=ROOT/'out/firmware-build/uefi/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c'
    if source_map.read_text().count('"Ramoops Console"')!=1 or '"Ramoops Pmsg"' in source_map.read_text():
        raise ValueError('unexpected console/pmsg map source')
    import pefile,capstone
    parsed=pefile.PE(data=pe.read_bytes());md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN);md.skipdata=True
    core_map=(core/'OUTPUT/DxeCore.map').read_text()
    word_match=re.search(r'^([0-9a-fA-F]+)\s+00000000\s+0\s+__const.EnumaWriteRamoopsCanary.Words\s*$',core_map,re.M)
    if control:
        if word_match or b'ENUMA-R017:' in pe.read_bytes():raise ValueError('map control contains marker writer data')
    else:
        if not word_match:raise ValueError('actual nonce word table symbol missing')
        rva=int(word_match[1],16)
        actual_words=struct.unpack('<4I',parsed.get_data(rva,16))
        if actual_words!=tuple(int(nonce[i*8:i*8+8],16) for i in range(4)):raise ValueError('actual nonce data differs')
    assembly='\n'.join(f'{i.address:x}: {i.mnemonic} {i.op_str}' for section in parsed.sections if section.Characteristics&0x20 for i in md.disasm(section.get_data(),section.VirtualAddress))+'\n'
    assembly_sha=hashlib.sha256(assembly.encode()).hexdigest()
    if a.read_header:
        required=['3c8c: mov w9, #4','3c90: mov w8, #-0x50000000',
                  '3c94: movk w9, #0xb000, lsl #16','3c9c: ldr wzr, [x8]',
                  '3ca0: ldr wzr, [x9]','3ca4: ldr wzr, [x9, #4]',
                  '3ca8: bl #0x17ca4','3cac: bl #0x16f4','3cb0: bl #0x13b8']
        if any(line not in assembly.splitlines() for line in required) or 'ResetWarm' in core_map:
            raise ValueError('read-only actual instruction sequence differs; manual re-review needed')
    if a.warm_control:
        required=['3cdc: bl #0x17cd8','3ce0: bl #0x16f4','3ce4: bl #0x13b8',
                  '1708: mov w19, #9','1710: movk w19, #0x8400, lsl #16',
                  '1714: movk w20, #0xc400, lsl #16','174c: stp x20, xzr, [sp]']
        if any(line not in assembly.splitlines() for line in required) or 'ResetWarm' not in core_map:
            raise ValueError('warm-only actual instruction sequence differs; manual re-review needed')
    if a.reviewed_disassembly_sha256 and a.reviewed_disassembly_sha256!=assembly_sha:raise ValueError('actual disassembly changed')
    scope=dict(base='0xB0000000',size='0x200000',marker_bytes=0 if control else 44,stage=10,delay_seconds=2,
               reset='cold' if control else 'warm-with-cold-fallback',pmsg_access=False)
    if a.read_header:scope['header_read_offsets']=[0,4,8]
    if a.warm_control:scope['reset']='warm-with-cold-fallback'
    meta['ramoops_scope']=scope
    image.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    archive.mkdir(parents=True)
    files={'image.img':image,'image.json':image.with_suffix('.json'),'SILICIUM_UEFI.fd':fd,
           'enuma-uefi.raw':raw,'DxeCore.efi':pe,'core.GNUmakefile':make,'core.map':core/'OUTPUT/DxeCore.map',
           'MemoryMapLib.c':source_map,'EnumaStageCheckpoint.h':staged/'EnumaStageCheckpoint.h',
           'firmware-build.json':ROOT/'reports/enuma-firmware-build.json','fd-audit.json':ROOT/'reports/enuma-fd-audit.json',
           'canary-host.json':ROOT/'reports/enuma-ramoops-canary-host.json'}
    if not control:
        for n in ['EnumaRamoopsCanary.h','EnumaRamoopsBuffer.h']:files[n]=staged/n
    for name,path in files.items():shutil.copyfile(path,archive/name)
    (archive/'core.disassembly.txt').write_text(assembly)
    entries={n:dict(sha256=sha(archive/n),bytes=(archive/n).stat().st_size) for n in [*files,'core.disassembly.txt']}
    q=dict(trial_kind='ramoops-warm-control' if a.warm_control else 'ramoops-header-read' if a.read_header else ('ramoops-map-control' if control else 'ramoops-canary'),firmware_commit=pin['commit'],archive=archive.relative_to(ROOT).as_posix(),
           image=(archive/'image.img').relative_to(ROOT).as_posix(),image_sha256=sha(image),nonce=nonce,
           ramoops_scope=scope,files=entries,package=package,ram_payload_sha256=sha(fat),pixel_access=False,
           gop_published=False,review_required=a.reviewed_disassembly_sha256 is None,
           disassembly_sha256=assembly_sha,actual_map_record_present=True,actual_map_records=records,
           actual_nonce_words_equal=None if control else True,packaged_core_equal=True,
           interpretation=('Warm request without any console contents access. Return/timeout supports only comparison with cold controls; reset2 support and actual executed reset path are not directly reported.' if a.warm_control else ('Cold isolation control; header-read variant adds exactly three volatile loads, no stores. Automatic return supports reaching a controlled path, not console content access or logs. No writer/warm test.' if control else 'Only fresh complete nonce in native pstore supports survival; timeout/absence is inconclusive; never reissue consumed image')))
    report_name='enuma-ramoops-warm-control-qualification.json' if a.warm_control else 'enuma-ramoops-header-read-qualification.json' if a.read_header else ('enuma-ramoops-map-control-qualification.json' if control else 'enuma-ramoops-canary-qualification.json')
    for p in [archive/'qualification.json',ROOT/'reports'/report_name]:
        p.write_text(json.dumps(q,indent=2)+'\n')
    print('PASS: actual Core/map/full FAT and immutable archive; actual code review required='+str(q['review_required']))
    print('disassembly sha256='+assembly_sha)
if __name__=='__main__':main()
