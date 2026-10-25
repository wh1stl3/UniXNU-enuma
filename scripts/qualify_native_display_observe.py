"""Freeze independent native observer actual PE and full-input candidate; no boot."""
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
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--image',type=Path,required=True); p.add_argument('--archive',type=Path,required=True); p.add_argument('--native-query',type=int,choices=(0,1,2),default=0); p.add_argument('--native-control',action='store_true'); p.add_argument('--native-mask-field',type=int,choices=range(8),default=0); p.add_argument('--native-route-audit',action='store_true'); p.add_argument('--native-route-detail',action='store_true'); p.add_argument('--native-route-structure',action='store_true'); p.add_argument('--native-route-blend',action='store_true'); p.add_argument('--native-route-layout',action='store_true'); p.add_argument('--native-route-staging',action='store_true'); a=p.parse_args()
    if a.native_route_structure and (not a.native_route_audit or a.native_route_detail or a.native_route_staging or a.native_route_layout or a.native_route_blend): raise ValueError('invalid structure scope')
    if a.native_route_blend and not a.native_route_layout: raise ValueError('blend requires layout')
    if a.native_route_layout and (not a.native_route_detail or a.native_route_staging): raise ValueError('layout requires detail and excludes staging')
    if a.native_route_staging and not a.native_route_detail: raise ValueError('staging requires detail')
    if a.native_route_detail and not a.native_route_audit: raise ValueError('detail requires route')
    if a.native_route_audit and (a.native_query or a.native_control or a.native_mask_field): raise ValueError('route excludes native selectors')
    if not a.native_route_audit and not a.native_query: raise ValueError('native query required')
    if a.native_mask_field and (a.native_control or a.native_query!=1): raise ValueError('mask requires native query1 without control')
    image=a.image.resolve(); archive=a.archive.resolve()
    if not image.is_relative_to(ROOT/'out') or not archive.is_relative_to(ROOT/'out') or archive.exists(): raise ValueError('require new in-out archive/image')
    build=json.loads((ROOT/'reports/enuma-firmware-build.json').read_text()); pin=json.loads((ROOT/'config/uefi-source.lock.json').read_text())
    required={'complete':True,'inherited_video_audit_read_only':True,'gop_backend_selftest_ram_only':False,
      'native_route_structure':a.native_route_structure,'native_route_blend':a.native_route_blend,'native_route_layout':a.native_route_layout,'native_route_staging':a.native_route_staging,'native_route_detail':a.native_route_detail,'native_route_audit':a.native_route_audit,'inherited_video_entry_control':False,'native_observe_query':a.native_query,'native_observe_control':a.native_control,'native_mask_field':a.native_mask_field,
      'inherited_video_terminal':True,
      'inherited_video_topology_query':0,
      'inherited_video_reason_target':0,'inherited_video_reason_query':0,
      'diagnostic_stop_stage':13,'diagnostic_detail_point':16,'diagnostic_dispatch_guid':GUID,
      'diagnostic_dispatch_guid_only':True,'diagnostic_dispatch_completion_fallback':False,
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
    core_folder=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain'
    core_make=(core_folder/'GNUmakefile').read_text()
    for k in ['ENUMA_RAM_PAYLOAD','ENUMA_DIAG_STAGE','ENUMA_DIAG_DETAIL_POINT','ENUMA_DIAG_GOP_QUERY','ENUMA_DIAG_GOP_STEP','ENUMA_DIAG_GUID_ONLY','ENUMA_DIAG_DISPATCH_FALLBACK','ENUMA_DIAG_PIXEL_PREVIEW','ENUMA_VALUE_SOURCE','ENUMA_NATIVE_ROUTE_STRUCTURE','ENUMA_NATIVE_ROUTE_BLEND','ENUMA_NATIVE_ROUTE_LAYOUT','ENUMA_NATIVE_ROUTE_STAGING','ENUMA_NATIVE_ROUTE_DETAIL','ENUMA_NATIVE_ROUTE_AUDIT','ENUMA_NATIVE_MASK_FIELD','ENUMA_NATIVE_CONTROL','ENUMA_NATIVE_OBSERVE_QUERY','ENUMA_VIDEO_TERMINAL','ENUMA_VIDEO_TOPOLOGY_QUERY','ENUMA_VIDEO_REASON_TARGET','ENUMA_VIDEO_REASON_QUERY']:
        if set(re.findall(r'-D'+k+r'=([^\s]+)',make))!={defs[k]}: raise ValueError('actual provider flags mismatch: '+k)
        if set(re.findall(r'-D'+k+r'=([^\s]+)',core_make))!={defs[k]}: raise ValueError('actual Core flags mismatch: '+k)
    core_pe=core_folder/'OUTPUT/DxeCore.efi'
    actual_core=[m for m in modules if m['guid']=='d6a2cb7f-6a18-4e2f-b43b-9920a733700a']
    if len(actual_core)!=1 or hashlib.sha256(actual_core[0]['data']).hexdigest()!=sha(core_pe): raise ValueError('terminal Core PE not the one packaged')
    staged=ROOT/'out/firmware-build/uefi/Silicon/Silicium/SiliciumPkg/Drivers/SimpleFbDxe'
    entry=ROOT/'firmware/diagnostics'/('EnumaInheritedVideoAudit.c' if a.native_route_audit else 'EnumaNativeObserve.c')
    if (staged/'SimpleFb.c').read_bytes()!=entry.read_bytes() or build['inherited_video_compiled_contract']['entry_source_sha256']!=sha(entry): raise ValueError('entry source not bound')
    for n in ['InheritedScanout.h','Decode.c','Capture.c','VideoCapture.c','Topology.h','Topology.c','Evidence.h','Evidence.c','VideoResult.h','NativeObserve.h','NativeObserve.c','NativeMaskResult.h','NativeRouteResult.h']:
        if (staged/'InheritedVideo'/n).read_bytes()!=(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'/n).read_bytes(): raise ValueError('staged source mismatch: '+n)
    # Verify the actual FD contains the exact table record prefix checked at runtime.
    prefix=b'Display MDP'+b'\0'*(32-len('Display MDP'))+struct.pack('<QQ',0xae00000,0x85000)
    if not any(prefix in m['data'] for m in modules): raise ValueError('actual FD lacks exact R-004 table record')
    archive.mkdir(parents=True)
    source_files={'image.img':image,'image.json':image.with_suffix('.json'),'SILICIUM_UEFI.fd':fd,'enuma-uefi.raw':raw,
      'SimpleFbDxe.efi':pe,'provider.GNUmakefile':output/'GNUmakefile','entry.c':entry,
      'DxeCore.efi':core_pe,'core.map':core_folder/'OUTPUT/DxeCore.map',
      'NativeMaskResult.h':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/NativeMaskResult.h','core.GNUmakefile':core_folder/'GNUmakefile',
      'EnumaDispatchDetailCheckpoint.h':ROOT/'firmware/diagnostics/EnumaDispatchDetailCheckpoint.h',
      'VideoResult.h':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/VideoResult.h',
      'Evidence.c':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/Evidence.c',
      'Evidence.h':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/Evidence.h',
      'firmware-build.json':ROOT/'reports/enuma-firmware-build.json','fd-audit.json':ROOT/'reports/enuma-fd-audit.json',
      'host-tests.json':ROOT/'reports/enuma-native-display-observe-host.json',
      'provider.map':output/'OUTPUT/SimpleFbDxe.map',
      'provider.AutoGen.c':output/'DEBUG/AutoGen.c',
      'provider.libraries.txt':output/'OUTPUT/static_library_files.lst',
      'NativeObserve.c':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/NativeObserve.c',
      'NativeObserve.h':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/NativeObserve.h'}
    if a.native_mask_field or a.native_route_audit:
        mask_host=ROOT/'reports/enuma-native-mask-host.json'
        for name,digest in json.loads(mask_host.read_text())['source_sha256'].items():
            if sha(ROOT/name)!=digest: raise ValueError('mask host test source changed: '+name)
        source_files['mask-host-tests.json']=mask_host
    if a.native_route_audit:
        host=ROOT/'reports/enuma-inherited-gop-host.json'
        for name,digest in json.loads(host.read_text())['sources'].items():
            if sha(ROOT/name)!=digest: raise ValueError('route host source changed: '+name)
        source_files['host-tests.json']=host
        for name in ['NativeRouteResult.h','VideoCapture.c','Topology.c','Topology.h','Decode.c','InheritedScanout.h']:
            source_files[name]=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'/name
    files={}
    for n,path in source_files.items(): shutil.copyfile(path,archive/n); files[n]={'sha256':sha(archive/n),'bytes':(archive/n).stat().st_size}
    q=dict(trial_kind='native-display-observe',native_query=a.native_query,native_control=a.native_control,boot_clock_capture=a.native_control,review_required=True,scope='constant warning1/5, no map lookup or display reads; boot-origin calibration only' if a.native_control else 'independent both-link active/stable/moving observation; exactEnable3 not required; complement includes metadata/collection failure; never GOP admission',
      firmware_commit=pin['commit'],archive=archive.relative_to(ROOT).as_posix(),files=files,
      image=(archive/'image.img').relative_to(ROOT).as_posix(),image_sha256=sha(image),ram_payload_sha256=sha(fat),
      maximum_reads=0 if a.native_control else 26,maximum_wait_calls=0 if a.native_control else 2,maximum_mmio_offset=None if a.native_control else '0x6c26c',pixel_access=False,gop_published=False,
      map_record_in_actual_fd=True,packaged_provider_equal=True,package=package,
      terminal_return={'pass':2,'fail':7,'completion_fallback':False},
      result_interpretation='PASS1 and FAIL5 terminate at same exact Core driver-return hook,2/7s. Timing supports classification, not unique execution proof. Timeout means no recognized terminal report; recover first.')
    target_report='enuma-native-display-q'+str(a.native_query)+'-qualification.json'
    if a.native_mask_field:
        from native_mask_decode import make_plan
        calibration=ROOT/'reports/enuma-boot-clock-calibration.json'
        if json.loads(calibration.read_text()).get('calibration_passed') is not True: raise ValueError('boot clock not calibrated')
        q.update(trial_kind='native-display-mask',native_mask_field=a.native_mask_field,boot_clock_capture=True,
          native_mask_meaning={1:'ActiveThroughout',2:'TimingStableNonzero',3:'EnableStable',4:'Moving',5:'ExactEnable3',6:'ActiveThroughout AND TimingStableNonzero AND EnableStable AND Moving within same observation',7:'All three Timing words zero AND ActiveThroughout AND EnableStable AND Moving within same observation'}[a.native_mask_field],
          scope='independent two-bit native mask with distinct collection-error code; read only; no GOP admission',
          terminal_return={'code_delays_seconds':[2,7,12,17,22],'completion_fallback':False},
          decode_plan=make_plan(ROOT),calibration_sha256=sha(calibration),
          result_interpretation='warning1..4 encode mask0..3, warning5 collection failure. Indirect boot-origin decoding only; ambiguous or failed recovery stops additional trials.')
        target_report='enuma-native-mask-qualification.json'
    if a.native_route_audit:
        from native_mask_decode import make_plan
        from native_route_decode import CATEGORIES,DETAIL_CATEGORIES,STAGING_CATEGORIES,LAYOUT_CATEGORIES,BLEND_CATEGORIES,STRUCTURE_CATEGORIES
        calibration=ROOT/'reports/enuma-boot-clock-calibration.json'
        if json.loads(calibration.read_text()).get('calibration_passed') is not True: raise ValueError('boot clock not calibrated')
        q.update(trial_kind='native-video-route',native_border_view=not a.native_route_staging,native_route_audit=True,native_route_detail=a.native_route_detail,native_route_staging=a.native_route_staging,native_route_layout=a.native_route_layout,native_route_blend=a.native_route_blend,native_route_structure=a.native_route_structure,boot_clock_capture=True,
          maximum_reads=330,scope='STATUS gated stable CTL/SSPP/LM/video layout candidate; no GOP admission',
          terminal_return={'code_delays_seconds':[2,7,12,17,22],'completion_fallback':False},
          decode_plan=make_plan(ROOT),calibration_sha256=sha(calibration),result_categories=STRUCTURE_CATEGORIES if a.native_route_structure else BLEND_CATEGORIES if a.native_route_blend else LAYOUT_CATEGORIES if a.native_route_layout else STAGING_CATEGORIES if a.native_route_staging else DETAIL_CATEGORIES if a.native_route_detail else CATEGORIES,
          result_interpretation='Five first-result categories from native route sampler, not bit masks; code5 stable candidate retains ADDRESS and TOPOLOGY requirements. Indirect timing; ambiguous clock or failed recovery stops additional trials.')
        if a.native_route_layout: q['result_interpretation']='Five first-layout-rejection categories only; code5 is left/right rejection, not success. No extra reads or changed predicates. Ambiguous clock stops additional trials.'
        if a.native_route_staging: q['result_interpretation']='Five captured-staging categories only; code2 normalized border-only route is not admission; code5 is cardinality rejection, not success. No extra reads, no relaxed gate. Ambiguous clock stops additional trials.'
        if a.native_route_blend: q['result_interpretation']='Five captured blend rejection categories; code5 is alpha rejection, not success. No extra reads or changed predicates; outside-source dim does not mean inactive.'
        if a.native_route_structure:
            q['scope']='Read-only structural geometry and raw stability, retaining all blend/processing/address/downstream proof obligations'
            q['result_interpretation']='Code5 proves modeled structure/stability only, requirements22 BLEND|ADDRESS|TOPOLOGY; no blend/dim/processing admission or GOP. All raw words retained for stability.'
        target_report='enuma-native-route-qualification.json'
    for path in [archive/'qualification.json' ,ROOT/'reports'/target_report]: path.write_text(json.dumps(q,indent=2)+'\n')
    print('PASS: actual read-only audit PE, R-004 FD record, staged source/flags, full FAT boot-v3 and immutable archive')
if __name__=='__main__': main()
