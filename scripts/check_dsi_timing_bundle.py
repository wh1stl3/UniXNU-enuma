"""Qualify matching DSI candidates offline; archive generated inputs before reuse."""
import argparse,hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--profile');p.add_argument('--config',default='dsi-timing-probes.json');p.add_argument('--report',default='enuma-dsi-timing-bundle.json');p.add_argument('--archive-generated',action='store_true');a=p.parse_args()
 config=read(ROOT/'config'/a.config);pin_path=(ROOT/'config'/config.get('source_lock','uefi-source.lock.json')).resolve();assert pin_path.is_relative_to((ROOT/'config').resolve())
 pin=read(pin_path);checkout=subprocess.check_output(['git','-C',str(ROOT/'firmware'),'rev-parse','HEAD'],text=True).strip()
 assert config['firmware_commit']==pin['commit']
 wanted={}
 for name,digest in pin['file_sha256'].items():
  raw=((ROOT/'firmware'/name).read_bytes() if checkout==pin['commit'] else subprocess.check_output(['git','-C',str(ROOT/'firmware'),'show',pin['commit']+':'+name]));assert sha(raw)==digest,name
  if Path(name).suffix in ('.c','.h','.inf','.inc','.dsc','.fdf','.patch','.toml','.py','.json'):wanted['firmware/'+name]=sha(raw.replace(b'\r\n',b'\n'))
 records=[];definitions=[];shims=[]
 profiles=[x for x in config['profiles'] if not a.profile or x['tag']==a.profile]
 assert profiles and (not a.profile or len(profiles)==1)
 for profile in profiles:
  variant=profile['variant'];snap=ROOT/'out/entry-probe'/variant;b=read(snap/'enuma-firmware-build.json');audit=read(snap/'enuma-fd-audit.json')
  assert b['complete'] and b['core_patch_reversion_checked'] and b['uefi_source_commit']==pin['commit'] and b['source_inputs_sha256']==wanted
  assert (b['diagnostic_gop_step'],b['diagnostic_gop_query'],b['diagnostic_gop_transport'])==(profile['step'],profile['query'],'core-warning-v2')
  assert (b['diagnostic_stop_stage'],b['diagnostic_detail_point'],b['diagnostic_delay_seconds'])==(13,16,2)
  assert b['diagnostic_dispatch_guid']=='dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92' and b['diagnostic_dispatch_guid_only'] and b['diagnostic_dispatch_completion_fallback']
  assert not b['diagnostic_pixel_preview'] and b['diagnostic_simplefb_metadata_only'] and b['hardware_review_required'] is None
  assert b['diagnostic_omitted_oem_modules']==['CPRDxe','DisplayDxe','UFSDxe'] and len(audit['matched_oem_modules'])==30
  contract=b['gop_provider_generated_contract'];assert all(contract[k] for k in ('inf_matches_baseline','reset_library_absent','psci_constructor_absent'))
  if a.archive_generated:
   assert a.profile and read(ROOT/'reports/enuma-firmware-build.json')['fd_sha256']==b['fd_sha256']
   module=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/SiliciumPkg/Drivers/SimpleFbDxe/SimpleFbDxe'
   for source,target,key in [('DEBUG/AutoGen.c','SimpleFb.AutoGen.c','autogen_sha256'),('OUTPUT/static_library_files.lst','SimpleFb.static_library_files.lst','static_library_list_sha256')]:
    text=(module/source).read_text(encoding='utf-8');assert sha(text.encode())==contract[key];(snap/target).write_bytes(text.encode())
  for name,key in [('SimpleFb.AutoGen.c','autogen_sha256'),('SimpleFb.static_library_files.lst','static_library_list_sha256')]:
   text=(snap/name).read_text(encoding='utf-8');assert sha(text.encode())==contract[key]
   assert 'ArmPsciResetSystemLibConstructor' not in text and not any(v in text.lower() for v in ('pscireset','resetsystemlib'))
  fd=(snap/'SILICIUM_UEFI.fd').read_bytes();assert sha(fd)==b['fd_sha256']==audit['fd_sha256']
  if profile['step']==14:
   assert audit['dsi_timing_code']['static_target_loads']==['0xae6b800','0xae6c000'] and not audit['dsi_timing_code']['static_target_stores']
  if profile['step'] in (15,16):
   code=audit['dsi_counter_code'];offsets=(0,0xa8) if profile['step']==15 else (0,0xa8,0xac)
   assert code['static_possible_target_loads']==sorted(hex(base+off) for base in (0xae6b800,0xae6c000) for off in offsets) and not code['static_target_stores']
   assert code['wait_100000_call_sites']==(1 if profile['step']==16 else 0)
  image=ROOT/'out/boot-candidate'/(variant+'-boot-v3.img');raw=image.read_bytes();meta=read(image.with_suffix('.json'))
  assert sha(raw)==meta['image_sha256'] and not meta['fixture_only'] and meta.get('hardware_review') is None
  assert raw[:8]==b'ANDROID!' and struct.unpack_from('<I',raw,40)[0]==3
  ks,rs=struct.unpack_from('<II',raw,8);assert rs==0 and ks==192+len(fd) and raw[4288:4096+ks]==fd
  shims.append(raw[4096:4288]);definitions.append(b['firmware_configuration']['defines'])
  record=dict(variant=variant,step=profile['step'],query=profile['query'],image_sha256=sha(raw),fd_sha256=sha(fd),firmware_commit=pin['commit'],all_checks_passed=True,scope='offline qualification, not hardware result',generated_contract=contract)
  (snap/'candidate-qualification.json').write_bytes((json.dumps(record,indent=2)+'\n').encode());records.append(record)
 if not a.profile:
  skip={'ENUMA_DIAG_GOP_STEP','ENUMA_DIAG_GOP_QUERY'}
  assert len(records)==len(config['profiles']) and all(shim==shims[0] for shim in shims)
  assert all({k:v for k,v in d.items() if k not in skip}=={k:v for k,v in definitions[0].items() if k not in skip} for d in definitions)
  assert all(d['ENUMA_DIAG_PIXEL_PREVIEW']=='0' for d in definitions)
  host=read(ROOT/'reports'/config.get('host_report','enuma-dsi-timing-host.json'));assert host['all_passed']
  if 'sources' in host:
   for n,h in host['sources'].items():assert h==pin['file_sha256']['diagnostics/'+n]
  else:assert host['source_sha256']==pin['file_sha256']['diagnostics/EnumaScanoutAudit.h']
  report=dict(scope=__doc__,all_passed=True,firmware_commit=pin['commit'],profiles=records,only_define_differences=sorted(skip),maximum_dsi_reads=config.get('maximum_dsi_reads',2),pixel_access=False,mmio_writes=False,new_mapping=False,hardware_executed=False)
  (ROOT/'reports'/a.report).write_bytes((json.dumps(report,indent=2)+'\n').encode())
 print('PASS: DSI '+(a.profile or str(len(profiles))+'-profile bundle')+' source/generated dependencies/actual FD/OEM/Boot v3; no device commands')
if __name__=='__main__':main()
