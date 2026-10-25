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
    a=p.parse_args();image=a.image.resolve();archive=a.archive.resolve()
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
              'hardware_review_required':'R-017',
              'diagnostic_omitted_oem_modules':['CPRDxe','DisplayDxe','UFSDxe']}
    if any(build.get(k)!=v for k,v in expected.items()) or build['uefi_source_commit']!=pin['commit']:
        raise ValueError('wrong R-017 build profile')
    nonce=build.get('ramoops_canary_nonce','')
    if re.fullmatch('[0-9a-f]{32}',nonce) is None:raise ValueError('missing nonce')
    defs=build['firmware_configuration']['defines']
    if defs['ENUMA_RAM_PAYLOAD']!='1' or defs['ENUMA_RAMOOPS_CANARY']!='1' or defs['ENUMA_VALUE_SOURCE']!='0':
        raise ValueError('full FAT and standalone canary required')
    if any(defs['ENUMA_RAMOOPS_NONCE_'+str(i)]!=str(int(nonce[i*8:i*8+8],16))+'U' for i in range(4)):
        raise ValueError('nonce words differ')
    fd=ROOT/build['fd'];raw=ROOT/'out/boot-candidate/enuma-uefi.raw';fat=ROOT/'out/full-boot/payload/payload.img'
    audit=json.loads((ROOT/'reports/enuma-fd-audit.json').read_text());full=json.loads((ROOT/'reports/enuma-full-payload.json').read_text())
    if sha(fd)!=build['fd_sha256'] or sha(fd)!=audit['fd_sha256'] or raw.read_bytes()[192:]!=fd.read_bytes() or sha(fat)!=full['payload_sha256']:
        raise ValueError('FD/raw/full FAT mismatch')
    package=verify(image.read_bytes(),raw.read_bytes(),fat.read_bytes())
    meta=json.loads(image.with_suffix('.json').read_text())
    if meta.get('hardware_review')!='R-017' or meta['image_sha256']!=sha(image):raise ValueError('missing protected package tag')
    modules=list(firmware_files(fd.read_bytes())); names=[m['name'] for m in modules]
    if any(n in names for n in ['DisplayDxe','CPRDxe','UFSDxe','EnumaGopSelfTest']) or not all(n in names for n in ['SimpleFbDxe','EnumaRamPayloadDxe','EnumaProbe']):
        raise ValueError('wrong actual modules')
    core=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain'
    pe=core/'OUTPUT/DxeCore.efi';make=core/'GNUmakefile'
    actual=[m for m in modules if m['guid']=='d6a2cb7f-6a18-4e2f-b43b-9920a733700a']
    if len(actual)!=1 or hashlib.sha256(actual[0]['data']).hexdigest()!=sha(pe):raise ValueError('actual packaged Core differs')
    text=make.read_text()
    for k in ['ENUMA_RAMOOPS_CANARY','ENUMA_DIAG_STAGE','ENUMA_DIAG_DELAY_US','ENUMA_RAM_PAYLOAD','ENUMA_DIAG_GOP_QUERY','ENUMA_VALUE_SOURCE']+['ENUMA_RAMOOPS_NONCE_'+str(i) for i in range(4)]:
        if set(re.findall(r'-D'+k+r'=([^\s]+)',text))!={defs[k]}:raise ValueError('actual Core flags differ: '+k)
    staged=ROOT/'out/firmware-build/Mu_Basecore/MdeModulePkg/Core/Dxe/DxeMain'
    if (staged/'EnumaStageCheckpoint.h').read_bytes()!=(ROOT/'firmware/diagnostics/EnumaRamoopsStageCheckpoint.h').read_bytes():
        raise ValueError('actual staged stage header differs')
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
    if not word_match:raise ValueError('actual nonce word table symbol missing')
    rva=int(word_match[1],16)
    actual_words=struct.unpack('<4I',parsed.get_data(rva,16))
    if actual_words!=tuple(int(nonce[i*8:i*8+8],16) for i in range(4)):raise ValueError('actual nonce data differs')
    assembly='\n'.join(f'{i.address:x}: {i.mnemonic} {i.op_str}' for section in parsed.sections if section.Characteristics&0x20 for i in md.disasm(section.get_data(),section.VirtualAddress))+'\n'
    assembly_sha=hashlib.sha256(assembly.encode()).hexdigest()
    if a.reviewed_disassembly_sha256 and a.reviewed_disassembly_sha256!=assembly_sha:raise ValueError('actual disassembly changed')
    scope=dict(base='0xB0000000',size='0x200000',marker_bytes=44,stage=10,delay_seconds=2,
               reset='warm-with-cold-fallback',pmsg_access=False)
    meta['ramoops_scope']=scope
    image.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    archive.mkdir(parents=True)
    files={'image.img':image,'image.json':image.with_suffix('.json'),'SILICIUM_UEFI.fd':fd,
           'enuma-uefi.raw':raw,'DxeCore.efi':pe,'core.GNUmakefile':make,'core.map':core/'OUTPUT/DxeCore.map',
           'MemoryMapLib.c':source_map,'EnumaStageCheckpoint.h':staged/'EnumaStageCheckpoint.h',
           'EnumaRamoopsCanary.h':staged/'EnumaRamoopsCanary.h','EnumaRamoopsBuffer.h':staged/'EnumaRamoopsBuffer.h',
           'firmware-build.json':ROOT/'reports/enuma-firmware-build.json','fd-audit.json':ROOT/'reports/enuma-fd-audit.json',
           'canary-host.json':ROOT/'reports/enuma-ramoops-canary-host.json'}
    for name,path in files.items():shutil.copyfile(path,archive/name)
    (archive/'core.disassembly.txt').write_text(assembly)
    entries={n:dict(sha256=sha(archive/n),bytes=(archive/n).stat().st_size) for n in [*files,'core.disassembly.txt']}
    q=dict(trial_kind='ramoops-canary',firmware_commit=pin['commit'],archive=archive.relative_to(ROOT).as_posix(),
           image=(archive/'image.img').relative_to(ROOT).as_posix(),image_sha256=sha(image),nonce=nonce,
           ramoops_scope=scope,files=entries,package=package,ram_payload_sha256=sha(fat),pixel_access=False,
           gop_published=False,review_required=a.reviewed_disassembly_sha256 is None,
           disassembly_sha256=assembly_sha,actual_map_record_present=True,actual_map_records=records,
           actual_nonce_words_equal=True,packaged_core_equal=True,
           interpretation='Only fresh complete nonce in native pstore supports survival; timeout/absence is inconclusive; never reissue consumed image')
    for p in [archive/'qualification.json',ROOT/'reports/enuma-ramoops-canary-qualification.json']:
        p.write_text(json.dumps(q,indent=2)+'\n')
    print('PASS: actual Core/map/full FAT and immutable archive; actual code review required='+str(q['review_required']))
    print('disassembly sha256='+assembly_sha)
if __name__=='__main__':main()
