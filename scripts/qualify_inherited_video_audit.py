"""Freeze one full-input, no-pixel inherited-video audit candidate; no boot."""
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
GUID='dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--image',type=Path,required=True); p.add_argument('--archive',type=Path,required=True); p.add_argument('--control',action='store_true'); p.add_argument('--reviewed-control-code-sha256'); p.add_argument('--tool-path',type=Path); a=p.parse_args()
    if a.tool_path: sys.path.insert(0,str(a.tool_path.resolve()))
    if a.reviewed_control_code_sha256 and not a.control: raise ValueError('code review digest requires control profile')
    image=a.image.resolve(); archive=a.archive.resolve()
    if not image.is_relative_to(ROOT/'out') or not archive.is_relative_to(ROOT/'out') or archive.exists(): raise ValueError('require new in-out archive/image')
    build=json.loads((ROOT/'reports/enuma-firmware-build.json').read_text()); pin=json.loads((ROOT/'config/uefi-source.lock.json').read_text())
    required={'complete':True,'inherited_video_audit_read_only':True,'gop_backend_selftest_ram_only':False,
      'inherited_video_entry_control':a.control,
      'diagnostic_stop_stage':13,'diagnostic_detail_point':16,'diagnostic_dispatch_guid':GUID,
      'diagnostic_dispatch_guid_only':True,'diagnostic_dispatch_completion_fallback':True,
      'diagnostic_delay_seconds':2,'diagnostic_gop_query':1,'diagnostic_gop_step':0,
      'diagnostic_pixel_preview':False,'diagnostic_simplefb_metadata_only':False,
      'diagnostic_omitted_oem_modules':['CPRDxe','DisplayDxe','UFSDxe']}
    if any(build.get(k)!=v for k,v in required.items()) or build['uefi_source_commit']!=pin['commit'] or build['value_probe']['source']!='off': raise ValueError('wrong current video audit profile')
    if build['firmware_configuration']['defines']['ENUMA_RAM_PAYLOAD']!='1': raise ValueError('full inputs required')
    fd=ROOT/build['fd']; raw=ROOT/'out/boot-candidate/enuma-uefi.raw'; fat=ROOT/'out/full-boot/payload/payload.img'
    audit=json.loads((ROOT/'reports/enuma-fd-audit.json').read_text()); full=json.loads((ROOT/'reports/enuma-full-payload.json').read_text())
    if sha(fd)!=build['fd_sha256'] or sha(fd)!=audit['fd_sha256'] or raw.read_bytes()[192:]!=fd.read_bytes() or sha(fat)!=full['payload_sha256']: raise ValueError('FD/raw/full FAT mismatch')
    package=verify(image.read_bytes(),raw.read_bytes(),fat.read_bytes())
    modules=list(firmware_files(fd.read_bytes())); names=[m['name'] for m in modules]
    if any(n in names for n in ['DisplayDxe','CPRDxe','UFSDxe','EnumaGopSelfTest']) or not all(n in names for n in ['SimpleFbDxe','EnumaRamPayloadDxe','EnumaProbe']): raise ValueError('wrong actual FD modules')
    output=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/SiliciumPkg/Drivers/SimpleFbDxe/SimpleFbDxe'
    pe=output/'OUTPUT/SimpleFbDxe.efi'; packaged=[m for m in modules if m['name']=='SimpleFbDxe']
    if len(packaged)!=1 or hashlib.sha256(packaged[0]['data']).hexdigest()!=sha(pe): raise ValueError('actual PE not packaged')
    make=(output/'GNUmakefile').read_text(); defs=build['firmware_configuration']['defines']
    for k in ['ENUMA_RAM_PAYLOAD','ENUMA_DIAG_STAGE','ENUMA_DIAG_DETAIL_POINT','ENUMA_DIAG_GOP_QUERY','ENUMA_DIAG_GOP_STEP','ENUMA_DIAG_GUID_ONLY','ENUMA_DIAG_DISPATCH_FALLBACK','ENUMA_DIAG_PIXEL_PREVIEW','ENUMA_VALUE_SOURCE']:
        if set(re.findall(r'-D'+k+r'=([^\s]+)',make))!={defs[k]}: raise ValueError('actual provider flags mismatch: '+k)
    staged=ROOT/'out/firmware-build/uefi/Silicon/Silicium/SiliciumPkg/Drivers/SimpleFbDxe'
    entry=ROOT/'firmware/diagnostics'/('EnumaInheritedVideoEntryControl.c' if a.control else 'EnumaInheritedVideoAudit.c')
    if (staged/'SimpleFb.c').read_bytes()!=entry.read_bytes() or build['inherited_video_compiled_contract']['entry_source_sha256']!=sha(entry): raise ValueError('entry source not bound')
    for n in ['InheritedScanout.h','Decode.c','Capture.c','Topology.h','Topology.c','Evidence.h','Evidence.c']:
        if (staged/'InheritedVideo'/n).read_bytes()!=(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'/n).read_bytes(): raise ValueError('staged source mismatch: '+n)
    # Verify the actual FD contains the exact table record prefix checked at runtime.
    prefix=b'Display MDP'+b'\0'*(32-len('Display MDP'))+struct.pack('<QQ',0xae00000,0x85000)
    if not any(prefix in m['data'] for m in modules): raise ValueError('actual FD lacks exact R-004 table record')
    archive.mkdir(parents=True)
    source_files={'image.img':image,'image.json':image.with_suffix('.json'),'SILICIUM_UEFI.fd':fd,'enuma-uefi.raw':raw,
      'SimpleFbDxe.efi':pe,'provider.GNUmakefile':output/'GNUmakefile','entry.c':entry,
      'firmware-build.json':ROOT/'reports/enuma-firmware-build.json','fd-audit.json':ROOT/'reports/enuma-fd-audit.json',
      'host-tests.json':ROOT/'reports/enuma-inherited-gop-host.json'}
    files={}
    for n,path in source_files.items(): shutil.copyfile(path,archive/n); files[n]={'sha256':sha(archive/n),'bytes':(archive/n).stat().st_size}
    q=dict(trial_kind='inherited-video-entry-control' if a.control else 'inherited-video-audit',scope='qualified same-entry constant marker with no MMIO/map lookup' if a.control else 'qualified bounded read-only three-sample dual-link configuration/counter predicate; not GOP/physical route proof',
      firmware_commit=pin['commit'],archive=archive.relative_to(ROOT).as_posix(),files=files,
      image=(archive/'image.img').relative_to(ROOT).as_posix(),image_sha256=sha(image),ram_payload_sha256=sha(fat),
      maximum_reads=0 if a.control else 969,maximum_wait_calls=0 if a.control else 2,maximum_mmio_offset=None if a.control else '0x73830',pixel_access=False,gop_published=False,
      map_record_in_actual_fd=True,packaged_provider_equal=True,package=package,
      result_interpretation='Exact pass warning selects2s core gate; refusal may reach7s dispatcher fallback. Timing alone is not unique execution proof. 75s host timeout freezes the trial; recover first.')
    if a.control:
        import pefile,capstone
        blob=pe.read_bytes(); parsed=pefile.PE(data=blob); md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_LITTLE_ENDIAN); md.skipdata=True
        mapping=(output/'OUTPUT/SimpleFbDxe.map').read_text()
        symbols={m[2]:int(m[1],16) for m in re.finditer(r'^([0-9a-fA-F]{8,16})\s+[0-9a-fA-F]+\s+0\s+(\S+)\s*$',mapping,re.M)}
        # LTO may inline the entry into its wrapper. Check its actual surviving
        # implementation with a separately reviewed disassembly, not source only.
        assembly='\n'.join(f'{i.address:x}: {i.mnemonic} {i.op_str}' for section in parsed.sections if section.Characteristics&0x20 for i in md.disasm(section.get_data(),section.VirtualAddress))
        (archive/'provider.disassembly.txt').write_text(assembly+'\n')
        code_sha=sha(archive/'provider.disassembly.txt')
        if a.reviewed_control_code_sha256 and a.reviewed_control_code_sha256!=code_sha: raise ValueError('actual control code differs from reviewed disassembly')
        q['control_actual_code']=dict(entry_rva=parsed.OPTIONAL_HEADER.AddressOfEntryPoint,symbols=symbols,disassembly_sha256=code_sha,body_source_sha256=sha(entry),review_required=a.reviewed_control_code_sha256 is None)
        q['files']['provider.disassembly.txt']={'sha256':sha(archive/'provider.disassembly.txt'),'bytes':(archive/'provider.disassembly.txt').stat().st_size}
    target_report='enuma-inherited-video-control-qualification.json' if a.control else 'enuma-inherited-video-qualification.json'
    for path in [archive/'qualification.json',ROOT/'reports'/target_report]: path.write_text(json.dumps(q,indent=2)+'\n')
    print('PASS: actual read-only audit PE, R-004 FD record, staged source/flags, full FAT boot-v3 and immutable archive')
if __name__=='__main__': main()
