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
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--image',type=Path,required=True); p.add_argument('--archive',type=Path,required=True); p.add_argument('--native-query',type=int,choices=(0,1,2),default=0); p.add_argument('--native-control',action='store_true'); p.add_argument('--native-mask-field',type=int,choices=range(8),default=0); p.add_argument('--native-route-audit',action='store_true'); p.add_argument('--native-route-detail',action='store_true'); p.add_argument('--boot-log-hold-seconds',type=int,choices=(2,8),default=2); p.add_argument('--boot-log-replay',action='store_true'); p.add_argument('--native-route-cpu-text',action='store_true'); p.add_argument('--native-route-cpu-pattern',action='store_true'); p.add_argument('--native-route-cpu-roi',action='store_true'); p.add_argument('--native-route-cpu-barrier',action='store_true'); p.add_argument('--native-route-cpu-read',action='store_true'); p.add_argument('--native-route-cpu-policy',action='store_true'); p.add_argument('--native-route-cpu-attribute',action='store_true'); p.add_argument('--native-route-cpu-stage1',action='store_true'); p.add_argument('--native-route-alpha-view',action='store_true'); p.add_argument('--native-route-global-detail',action='store_true'); p.add_argument('--native-route-global-output',action='store_true'); p.add_argument('--native-route-structure-detail',action='store_true'); p.add_argument('--native-route-structure',action='store_true'); p.add_argument('--native-route-blend',action='store_true'); p.add_argument('--native-route-layout',action='store_true'); p.add_argument('--native-route-staging',action='store_true'); a=p.parse_args()
    if a.boot_log_hold_seconds!=2 and not a.boot_log_replay: raise ValueError('extended hold requires log replay')
    if a.boot_log_replay and (not a.native_route_cpu_pattern or a.native_route_cpu_text): raise ValueError("log replay requires pixel profile without fixed text")
    if a.native_route_cpu_text and not a.native_route_cpu_pattern: raise ValueError('Text requires pixel transaction')
    if a.native_route_cpu_pattern and not a.native_route_cpu_roi: raise ValueError('Pixel transaction requires ROI profile')
    if a.native_route_cpu_roi and not a.native_route_cpu_barrier: raise ValueError('ROI read requires barrier profile')
    if a.native_route_cpu_barrier and not a.native_route_cpu_read: raise ValueError('CPU barrier requires single read')
    if a.native_route_cpu_read and not a.native_route_cpu_policy: raise ValueError('single CPU read requires whole-range policy')
    if a.native_route_cpu_policy and (not a.native_route_cpu_stage1 or a.native_route_cpu_attribute): raise ValueError('CPU policy requires stage1 and excludes first-attribute selector')
    if a.native_route_cpu_attribute and not a.native_route_cpu_stage1: raise ValueError('CPU attribute requires stage1')
    if a.native_route_cpu_stage1 and not a.native_route_alpha_view: raise ValueError('CPU stage1 requires alpha view')
    if a.native_route_alpha_view and (not a.native_route_global_output or a.native_route_global_detail): raise ValueError('alpha view requires global output and excludes source detail')
    if a.native_route_global_detail and not a.native_route_global_output: raise ValueError('global source detail requires global output')
    if a.native_route_global_output and (not a.native_route_structure or a.native_route_structure_detail): raise ValueError('global output requires structure and excludes structural detail')
    if a.native_route_structure_detail and not a.native_route_structure: raise ValueError('structural geometry requires structure')
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
    required={'boot_log_hold_seconds':a.boot_log_hold_seconds if a.boot_log_replay else None,'boot_log_replay':a.boot_log_replay,'complete':True,'inherited_video_audit_read_only':not a.native_route_cpu_pattern,'gop_backend_selftest_ram_only':False,
      'native_route_cpu_text':a.native_route_cpu_text,'native_route_cpu_pattern':a.native_route_cpu_pattern,'native_route_cpu_roi':a.native_route_cpu_roi,'native_route_cpu_barrier':a.native_route_cpu_barrier,'native_route_cpu_read':a.native_route_cpu_read,'native_route_cpu_policy':a.native_route_cpu_policy,'native_route_cpu_attribute':a.native_route_cpu_attribute,'native_route_cpu_stage1':a.native_route_cpu_stage1,'native_route_alpha_view':a.native_route_alpha_view,'native_route_global_detail':a.native_route_global_detail,'native_route_global_output':a.native_route_global_output,'native_route_structure_detail':a.native_route_structure_detail,'native_route_structure':a.native_route_structure,'native_route_blend':a.native_route_blend,'native_route_layout':a.native_route_layout,'native_route_staging':a.native_route_staging,'native_route_detail':a.native_route_detail,'native_route_audit':a.native_route_audit,'inherited_video_entry_control':False,'native_observe_query':a.native_query,'native_observe_control':a.native_control,'native_mask_field':a.native_mask_field,
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
    make=(output/'OUTPUT/cc_resp.txt').read_text(); defs=build['firmware_configuration']['defines']
    core_folder=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain'
    core_make=(core_folder/'OUTPUT/cc_resp.txt').read_text()
    for k in ['ENUMA_BOOT_LOG_HOLD_US','ENUMA_BOOT_JOURNAL','ENUMA_BOOT_LOG_REPLAY','ENUMA_RAM_PAYLOAD','ENUMA_DIAG_STAGE','ENUMA_DIAG_DETAIL_POINT','ENUMA_DIAG_GOP_QUERY','ENUMA_DIAG_GOP_STEP','ENUMA_DIAG_GUID_ONLY','ENUMA_DIAG_DISPATCH_FALLBACK','ENUMA_DIAG_PIXEL_PREVIEW','ENUMA_VALUE_SOURCE','ENUMA_NATIVE_ROUTE_CPU_TEXT','ENUMA_NATIVE_ROUTE_CPU_PATTERN','ENUMA_NATIVE_ROUTE_CPU_ROI','ENUMA_NATIVE_ROUTE_CPU_BARRIER','ENUMA_NATIVE_ROUTE_CPU_READ','ENUMA_NATIVE_ROUTE_CPU_POLICY','ENUMA_NATIVE_ROUTE_CPU_ATTRIBUTE','ENUMA_NATIVE_ROUTE_CPU_STAGE1','ENUMA_NATIVE_ROUTE_ALPHA_VIEW','ENUMA_NATIVE_ROUTE_GLOBAL_DETAIL','ENUMA_NATIVE_ROUTE_GLOBAL_OUTPUT','ENUMA_NATIVE_ROUTE_STRUCTURE_DETAIL','ENUMA_NATIVE_ROUTE_STRUCTURE','ENUMA_NATIVE_ROUTE_BLEND','ENUMA_NATIVE_ROUTE_LAYOUT','ENUMA_NATIVE_ROUTE_STAGING','ENUMA_NATIVE_ROUTE_DETAIL','ENUMA_NATIVE_ROUTE_AUDIT','ENUMA_NATIVE_MASK_FIELD','ENUMA_NATIVE_CONTROL','ENUMA_NATIVE_OBSERVE_QUERY','ENUMA_VIDEO_TERMINAL','ENUMA_VIDEO_TOPOLOGY_QUERY','ENUMA_VIDEO_REASON_TARGET','ENUMA_VIDEO_REASON_QUERY']:
        if set(re.findall(r'-D'+k+r'=([^\s]+)',make))!={defs[k]}: raise ValueError('actual provider flags mismatch: '+k)
        if set(re.findall(r'-D'+k+r'=([^\s]+)',core_make))!={defs[k]}: raise ValueError('actual Core flags mismatch: '+k)
    core_pe=core_folder/'OUTPUT/DxeCore.efi'
    actual_core=[m for m in modules if m['guid']=='d6a2cb7f-6a18-4e2f-b43b-9920a733700a']
    if len(actual_core)!=1 or hashlib.sha256(actual_core[0]['data']).hexdigest()!=sha(core_pe): raise ValueError('terminal Core PE not the one packaged')
    staged=ROOT/'out/firmware-build/uefi/Silicon/Silicium/SiliciumPkg/Drivers/SimpleFbDxe'
    entry=ROOT/'firmware/diagnostics'/('EnumaInheritedVideoAudit.c' if a.native_route_audit else 'EnumaNativeObserve.c')
    if (staged/'SimpleFb.c').read_bytes()!=entry.read_bytes() or build['inherited_video_compiled_contract']['entry_source_sha256']!=sha(entry): raise ValueError('entry source not bound')
    for n in ['InheritedScanout.h','Decode.c','Capture.c','VideoCapture.c','Topology.h','Topology.c','Evidence.h','Evidence.c','VideoResult.h','NativeObserve.h','NativeObserve.c','NativeMaskResult.h','NativeRouteResult.h','CpuStage1.h','PixelTransaction.h','PixelText.h','PixelLogPage.h']:
        if (staged/'InheritedVideo'/n).read_bytes()!=(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'/n).read_bytes(): raise ValueError('staged source mismatch: '+n)
    if a.native_route_cpu_pattern and (staged/'EnumaPixelTransactionArm.h').read_bytes()!=(ROOT/'firmware/diagnostics/EnumaPixelTransactionArm.h').read_bytes(): raise ValueError('pixel Arm source not staged')
    if a.boot_log_replay:
        for name in ('EnumaBootJournal.h','EnumaBootJournalProtocol.h'):
            if (staged/name).read_bytes()!=(ROOT/'firmware/diagnostics'/name).read_bytes(): raise ValueError('staged replay ABI differs: '+name)
            core_header=ROOT/'out/firmware-build/Mu_Basecore/MdeModulePkg/Core/Dxe/Dispatcher'/name
            if core_header.read_bytes()!=(staged/name).read_bytes(): raise ValueError('Core/provider ABI differs: '+name)
    # Verify the actual FD contains the exact table record prefix checked at runtime.
    prefix=b'Display MDP'+b'\0'*(32-len('Display MDP'))+struct.pack('<QQ',0xae00000,0x85000)
    if not any(prefix in m['data'] for m in modules): raise ValueError('actual FD lacks exact R-004 table record')
    archive.mkdir(parents=True)
    source_files={'image.img':image,'image.json':image.with_suffix('.json'),'SILICIUM_UEFI.fd':fd,'enuma-uefi.raw':raw,
      'SimpleFbDxe.efi':pe,'provider.cc_resp.txt':output/'OUTPUT/cc_resp.txt','entry.c':entry,
      'DxeCore.efi':core_pe,'core.map':core_folder/'DEBUG/DxeCore.map',
      'NativeMaskResult.h':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/NativeMaskResult.h','core.cc_resp.txt':core_folder/'OUTPUT/cc_resp.txt',
      'EnumaDispatchDetailCheckpoint.h':ROOT/'firmware/diagnostics/EnumaDispatchDetailCheckpoint.h',
      'VideoResult.h':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/VideoResult.h',
      'Evidence.c':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/Evidence.c',
      'Evidence.h':ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/Evidence.h',
      'firmware-build.json':ROOT/'reports/enuma-firmware-build.json','fd-audit.json':ROOT/'reports/enuma-fd-audit.json',
      'host-tests.json':ROOT/'reports/enuma-native-display-observe-host.json',
      'provider.map':output/'DEBUG/SimpleFbDxe.map',
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
        for name in ['NativeRouteResult.h','CpuStage1.h','PixelTransaction.h','PixelText.h','VideoCapture.c','Topology.c','Topology.h','Decode.c','InheritedScanout.h']:
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
        from native_route_decode import CATEGORIES,DETAIL_CATEGORIES,STAGING_CATEGORIES,LAYOUT_CATEGORIES,BLEND_CATEGORIES,STRUCTURE_CATEGORIES,GEOMETRY_CATEGORIES,GLOBAL_OUTPUT_CATEGORIES,GLOBAL_DETAIL_CATEGORIES,ALPHA_VIEW_CATEGORIES,CPU_STAGE1_CATEGORIES,CPU_ATTRIBUTE_CATEGORIES,CPU_POLICY_CATEGORIES,CPU_READ_CATEGORIES,CPU_BARRIER_CATEGORIES,CPU_ROI_CATEGORIES,CPU_PATTERN_CATEGORIES
        calibration=ROOT/'reports/enuma-boot-clock-calibration.json'
        if json.loads(calibration.read_text()).get('calibration_passed') is not True: raise ValueError('boot clock not calibrated')
        q.update(trial_kind='native-video-route',native_border_view=not a.native_route_staging,native_route_audit=True,native_route_detail=a.native_route_detail,native_route_staging=a.native_route_staging,native_route_layout=a.native_route_layout,native_route_blend=a.native_route_blend,native_route_structure=a.native_route_structure,native_route_structure_detail=a.native_route_structure_detail,native_route_global_output=a.native_route_global_output,native_route_global_detail=a.native_route_global_detail,native_route_alpha_view=a.native_route_alpha_view,native_route_cpu_stage1=a.native_route_cpu_stage1,native_route_cpu_attribute=a.native_route_cpu_attribute,native_route_cpu_policy=a.native_route_cpu_policy,native_route_cpu_read=a.native_route_cpu_read,native_route_cpu_barrier=a.native_route_cpu_barrier,native_route_cpu_roi=a.native_route_cpu_roi,native_route_cpu_text=a.native_route_cpu_text,native_route_cpu_pattern=a.native_route_cpu_pattern,boot_clock_capture=True,
          maximum_reads=330,scope='STATUS gated stable CTL/SSPP/LM/video layout candidate; no GOP admission',
          terminal_return={'code_delays_seconds':[2,7,12,17,22],'completion_fallback':False},
          decode_plan=make_plan(ROOT),calibration_sha256=sha(calibration),result_categories=CPU_PATTERN_CATEGORIES if a.native_route_cpu_pattern else CPU_ROI_CATEGORIES if a.native_route_cpu_roi else CPU_BARRIER_CATEGORIES if a.native_route_cpu_barrier else CPU_READ_CATEGORIES if a.native_route_cpu_read else CPU_POLICY_CATEGORIES if a.native_route_cpu_policy else CPU_ATTRIBUTE_CATEGORIES if a.native_route_cpu_attribute else CPU_STAGE1_CATEGORIES if a.native_route_cpu_stage1 else ALPHA_VIEW_CATEGORIES if a.native_route_alpha_view else GLOBAL_DETAIL_CATEGORIES if a.native_route_global_detail else GLOBAL_OUTPUT_CATEGORIES if a.native_route_global_output else GEOMETRY_CATEGORIES if a.native_route_structure_detail else STRUCTURE_CATEGORIES if a.native_route_structure else BLEND_CATEGORIES if a.native_route_blend else LAYOUT_CATEGORIES if a.native_route_layout else STAGING_CATEGORIES if a.native_route_staging else DETAIL_CATEGORIES if a.native_route_detail else CATEGORIES,
          result_interpretation='Five first-result categories from native route sampler, not bit masks; code5 stable candidate retains ADDRESS and TOPOLOGY requirements. Indirect timing; ambiguous clock or failed recovery stops additional trials.')
        if a.native_route_layout: q['result_interpretation']='Five first-layout-rejection categories only; code5 is left/right rejection, not success. No extra reads or changed predicates. Ambiguous clock stops additional trials.'
        if a.native_route_staging: q['result_interpretation']='Five captured-staging categories only; code2 normalized border-only route is not admission; code5 is cardinality rejection, not success. No extra reads, no relaxed gate. Ambiguous clock stops additional trials.'
        if a.native_route_blend: q['result_interpretation']='Five captured blend rejection categories; code5 is alpha rejection, not success. No extra reads or changed predicates; outside-source dim does not mean inactive.'
        if a.native_route_structure:
            q['scope']='Read-only structural geometry and raw stability, retaining all blend/processing/address/downstream proof obligations'
            q['result_interpretation']='Code5 proves modeled structure/stability only, requirements22 BLEND|ADDRESS|TOPOLOGY; no blend/dim/processing admission or GOP. All raw words retained for stability.'
        if a.native_route_structure_detail:
            q['scope']='Capture three raw snapshots and verify stability before pure structural geometry classification; no blend or GOP qualification'
            q['result_interpretation']='Code2..5 requires raw stable snapshots and both nonwrapping frame windows before geometry rejection. Code5 means combined width rejection; code1 unclassified includes collection/runtime/decode/success. No numeric values or visual proof.'
        if a.native_route_global_output:
            q['scope']='Raw stable exact global-coordinate logical view then geometry and source decode; blend/physical routing unproven'
            q['result_interpretation']='Exact left0/right-left-width XY and full matching sizes only, local copy converts right XY to explicit logical origin; raw words preserved. Code5 retains BLEND|ADDRESS|TOPOLOGY22; no physical display/GOP/pixel proof.'
        if a.native_route_global_detail:
            q['result_interpretation']='Only ReasonNativeDecode and zero requirements classify code2 geometry/coverage,3 format,4 bounds/consistency,5 security/other source decode rejection. Code1 unclassified includes capture/geometry/runtime/success. Same Native5 sampling and predicates, no extra reads.'
        if a.native_route_alpha_view:
            q['alpha_semantics_unproven']=True
            q['scope']='Raw stable global-coordinate and exact RGBX/RGBA8888 logical RGB view; alpha blend CPU and physical routing unproven'
            q['result_interpretation']='Only236ff/237ff, at least one alpha-enable source; RAM copy clears only bit8. Raw formats retained. Complete code5 requires22 and retains alpha/blend proof; reserved component is not certified opaque or a GOP pixel contract.'
        if a.native_route_cpu_stage1:
            cpu_host=ROOT/'reports/enuma-cpu-stage1-host.json'
            for name,digest in json.loads(cpu_host.read_text())['sources'].items():
                if sha(ROOT/name)!=digest: raise ValueError('CPU stage1 host source changed: '+name)
            shutil.copyfile(cpu_host,archive/'cpu-stage1-host.json')
            q['files']['cpu-stage1-host.json']={'sha256':sha(cpu_host),'bytes':cpu_host.stat().st_size}
            q.update(maximum_translation_operations=18432,cpu_stage1_only=True,cpu_memory_data_access=False,cpu_mapping_changes=False)
            q['scope']='Native6 full logical structure then per4KiB stage1 read/write translations, identity and expected0xbb attribute only'
            q['result_interpretation']='Code1 earlier contract/context/callback failure;2 fault/permission;3 nonidentity;4 unexpected attribute;5 every covering page passed stage1 R/W/identity/WT. No framebuffer data access, page-table setter, final EL1 stage2, SMMU, alpha/blend or display proof. Requirements22 unchanged.'
        if a.native_route_cpu_attribute:
            q['scope']='Classify first non-WT PAR attribute from the unchanged bounded CPU stage1 query'
            q['result_interpretation']='Code1 not an attribute rejection (includes prior/context/fault/nonidentity/all-WT);2 exact44 normal NC;3 exactff normal WB;4 exact00/04/08/0c Device;5 other non-WT encoding. First rejection only, remaining pages/write may be unexecuted. No data access, changed attributes or cleared obligations.'
        if a.native_route_cpu_policy:
            q['scope']='Whole decoded range stage1 read/write permission and identity, aggregate semantic cache policy; no pixel data access'
            q['result_interpretation']='Code1 prior/context/callback/fault/nonidentity;2..5 requires every covering4KiB page read+write translation nonfault and identity. 2 all inner+outerNC;3 allWT;4 allWB, allowing allocation/transient hint differences;5 mixed or other attributes, not normal admission. Original strict-WT API unchanged; callback only replaces ATTR in its RAM copy, no PAR/table/cache change. Requirements22, alpha/data/EL1-stage2/SMMU/downstream remain unproven.'
        if a.native_route_cpu_read:
            q.update(pixel_access=True,cpu_stage1_only=False,cpu_memory_data_access=True,maximum_framebuffer_reads=1,framebuffer_writes=0,cache_maintenance=False)
            q['scope']='Exactly one aligned32-bit CPU data read at decoded base after complete same-observation native structure and full-range R/W identity NormalWT; no data export/cache ops/writes/GOP'
            q['result_interpretation']='Code1 prior/context/fault/nonidentity;2 Normal policy changed from WT baseline;3 mixed/other policy;4 read contract/callback rejected;5 exactly one word read completed. No pixel data value, all22/alpha/blend/SMMU/downstream obligations retained. No read result on timeout; recover and stop, no retry.'
        if a.native_route_cpu_barrier:
            q.update(maximum_barriers=1,barrier_kind='dsb-sy-before-data-read')
            q['scope']='Same single-word read scope plus exactly one DSB SY after full frame validation and before the data load; no cache clean/invalidate or pixel stores'
            q['result_interpretation']='Same prior/policy codes1..3;4 barrier/read contract or callback rejected;5 one DSB SY then one word read completed. Exactly one added barrier, not a post-store/cache-maintenance test. All22/alpha/SMMU/downstream remain; ambiguous clock/timeout stops.'
        if a.native_route_cpu_roi:
            q.update(maximum_framebuffer_reads=1024,roi_origin_x=0,roi_origin_y=0,roi_width=128,roi_height=8,cpu_context_on_completion=True)
            q['scope']='Read exactly128x8 words at decoded origin, one pre-read DSB, same full NormalWT gates; distinguish EL using existing CurrentEL read only on completion'
            q['result_interpretation']='Code1 prior/context/fault/nonidentity;2 Normal policy changed;3 mixed/contract/barrier/read rejected, partial read count unknown;4 all1024 reads+DSB complete EL1;5 same EL2. No extra MRS, writes, data export or cache-line operation. EL1 final stage2/SMMU and visible/write/alpha proof remain unproven.'
        if a.native_route_cpu_pattern:
            from native_mask_decode import make_pixel_plan
            from native_pixel_scope import scope_for_review
            review="R-022" if a.boot_log_replay and a.boot_log_hold_seconds==8 else "R-020" if a.boot_log_replay else "R-019" if a.native_route_cpu_text else "R-018"
            SCOPE=scope_for_review(review)
            host=ROOT/'reports/enuma-pixel-transaction-host.json'
            for name,digest in json.loads(host.read_text())['sources'].items():
                if sha(ROOT/name)!=digest: raise ValueError('pixel host source changed: '+name)
            for name,path in [('pixel-host-tests.json',host),('EnumaPixelTransactionArm.h',ROOT/'firmware/diagnostics/EnumaPixelTransactionArm.h')]:
                shutil.copyfile(path,archive/name);q['files'][name]={'sha256':sha(path),'bytes':path.stat().st_size}
            meta=__import__('json').loads(image.with_suffix('.json').read_text())
            if meta.get('hardware_review')!=review or meta.get('pixel_scope')!=SCOPE or build.get('hardware_review_required')!=review: raise ValueError('protected R-018 image/scope tag missing')
            q.update(maximum_reads=660,maximum_wait_calls=5,maximum_framebuffer_reads=SCOPE["framebuffer_reads_max"],framebuffer_writes=SCOPE["framebuffer_writes_max"],roi_height=SCOPE["height"],
              maximum_barriers=3,barrier_kind='dsb-sy-before-save-after-pattern-after-restore',cpu_context_on_completion=False,
              required_current_el=1,hold_us=SCOPE["hold_us"],hold_calls_max=1,hardware_review=review,pixel_scope=SCOPE,roi_width=SCOPE["width"],
              camera_required=True,execution_approval_required=True,decode_plan=make_pixel_plan(ROOT,review))
            q['scope']='Protected pixel candidate exact scope: save/revalidate/contrast128x8/hold500ms/restore/readback; two bounded Native6 observations and EL1 NormalWT; no MMIO/cache/map writes or GOP'
            q['result_interpretation']='1 no stores: prerequisite/save/revalidation rejected;2 pattern rejected but original region restored;3 hold rejected but restored;4 restoration not established HARD STOP;5 CPU pattern and restoration complete, visible output still requires camera evidence. Save3072reads/2048stores max,3DSB,2 samplers660MDP/4x100ms plus1x500ms hold. Predeclared sampler envelope0..0.9s; no post-result adjustment. R-005 consumed does not approve this image; R-018 exact approved image/scope and camera required before any device action.'
        if a.native_route_cpu_text:
            q['scope']='R-019 pending exact128x32 fixed UEFI bitmap at4x scale; save/revalidate/hold500ms/restore/readback; no GOP/MMIO/map writes'
            q['result_interpretation']='1 no stores;2 text-pattern verification rejected but original region restored;3 hold rejected but restored;4 restoration not established HARD STOP;5 CPU text pattern and exact restoration completed, visible legibility requires camera. Max12288reads/8192stores/3DSB;660MDP/4x100ms plusone500ms hold. Same predeclared0..0.9s envelope; no post-result adjustment. Only R-019 exact-image/scope approval authorizes execution; R-018 is consumed.'
        if a.boot_log_replay:
            if build['boot_journal']['actual_core_cc_define']!='-DENUMA_BOOT_JOURNAL=1': raise ValueError('journal absent from Core')
            q.update(boot_log_replay=True,boot_log_hold_seconds=a.boot_log_hold_seconds,boot_journal=True,cached_replay=True,global_debug=False)
            q['scope']='R-020 cached Core point13 return status snapshot;256x96,2s,save/revalidate/verify/restore/readback; no GOP,ConOut,MMIO/map/cache writes'
            q['result_interpretation']='Same pixel first-result codes1..5. Code1 also includes journal protocol/snapshot/no-return refusal. Code5 supports CPU transaction/restoration only; camera independently judges actual cached status text. Max73728loads/49152stores/3DSB,660MDP/four100ms plus2s hold. Predeclared total sampler/hold envelope0..2.4s. No old consumed authorization reused.'
            for name,path in [('EnumaBootJournal.h',ROOT/'firmware/diagnostics/EnumaBootJournal.h'),('EnumaBootJournalProtocol.h',ROOT/'firmware/diagnostics/EnumaBootJournalProtocol.h'),('PixelLogPage.h',ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/PixelLogPage.h'),('log-replay-host.json',ROOT/'reports/enuma-log-replay-host.json')]:
                shutil.copyfile(path,archive/name);q['files'][name]={'sha256':sha(path),'bytes':path.stat().st_size}
            if a.boot_log_hold_seconds==8:
                q['scope']='R-022 new software: same real cached return page and256x96 rectangle; hold8s, unchanged save/revalidate/verify/restore/readback and73728loads/49152stores/3DSB'
                q['result_interpretation']='8s intended hold, same five Core warning delays. Only unique code5 plus independent recovery supports transaction/restoration; codes1..4 and any overlapping/ambiguous timing stop. Pass window uses nominal8s minimum plus two-window0..0.4s envelope; fail windows conservatively allow0..8.4s. Human readable content remains independent. No old repeat authority reused.'
            host_data=json.loads((ROOT/'reports/enuma-log-replay-host.json').read_text())
            if any(sha(ROOT/name)!=value for name,value in host_data['sources'].items()): raise ValueError('replay host inputs changed')
        target_report='enuma-native-route-qualification.json'
    for path in [archive/'qualification.json' ,ROOT/'reports'/target_report]: path.write_text(json.dumps(q,indent=2)+'\n')
    print('PASS: actual bounded audit PE, R-004 FD record, staged source/flags, full FAT boot-v3 and immutable archive')
if __name__=='__main__': main()
