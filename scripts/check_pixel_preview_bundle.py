"""Offline review of an explicitly protected R-005 pair; never grants approval."""
import hashlib,json,struct,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 config=read(ROOT/'config/pixel-preview-probes.json');pin_path=(ROOT/'config'/config.get('source_lock','uefi-source.lock.json')).resolve()
 assert pin_path.is_relative_to((ROOT/'config').resolve())
 pin=read(pin_path);checkout=subprocess.check_output(['git','-C',str(ROOT/'firmware'),'rev-parse','HEAD'],text=True).strip()
 assert config['firmware_commit']==pin['commit']
 wanted={}
 for name,digest in pin['file_sha256'].items():
  raw=((ROOT/'firmware'/name).read_bytes() if checkout==pin['commit'] else subprocess.check_output(['git','-C',str(ROOT/'firmware'),'show',pin['commit']+':'+name]));assert sha(raw)==digest,name
  if Path(name).suffix in ('.c','.h','.inf','.inc','.dsc','.fdf','.patch','.toml','.py','.json'):wanted['firmware/'+name]=sha(raw.replace(b'\r\n',b'\n'))
 records=[];defines=[];shims=[]
 for profile,step,pixel in [(config['control'],12,False),(config['preview'],13,True)]:
  variant=profile['variant'];snap=ROOT/'out/entry-probe'/variant;b=read(snap/'enuma-firmware-build.json')
  assert b['uefi_source_commit']==pin['commit'] and b['complete'] and b['core_patch_reversion_checked']
  assert b['source_inputs_sha256']==wanted
  assert (b['diagnostic_gop_step'],b['diagnostic_gop_query'],b['diagnostic_gop_transport'])==(step,1,'core-warning-v2')
  assert b['diagnostic_pixel_preview']==pixel and b['diagnostic_simplefb_metadata_only']==(not pixel)
  assert b['hardware_review_required']==('R-005' if pixel else None)
  assert (b['diagnostic_stop_stage'],b['diagnostic_detail_point'],b['diagnostic_delay_seconds'])==(13,16,2)
  assert b['diagnostic_dispatch_guid']=='dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92' and b['diagnostic_dispatch_guid_only'] and b['diagnostic_dispatch_completion_fallback']
  assert b['diagnostic_omitted_oem_modules']==['CPRDxe','DisplayDxe','UFSDxe']
  contract=b['gop_provider_generated_contract'];assert all(contract[k] for k in ['inf_matches_baseline','reset_library_absent','psci_constructor_absent'])
  autogen=(snap/'SimpleFb.AutoGen.c').read_text(encoding='utf-8');libs=(snap/'SimpleFb.static_library_files.lst').read_text(encoding='utf-8')
  assert sha(autogen.encode())==contract['autogen_sha256'] and sha(libs.encode())==contract['static_library_list_sha256']
  assert 'ArmPsciResetSystemLibConstructor' not in autogen and not any(x in libs.lower() for x in ['pscireset','resetsystemlib'])
  fd=(snap/'SILICIUM_UEFI.fd').read_bytes();audit=read(snap/'enuma-fd-audit.json');assert sha(fd)==b['fd_sha256']==audit['fd_sha256']
  if pixel:assert audit['pixel_preview_code']['cache_instructions_in_packaged_pe'] and audit['pixel_preview_code']['hardware_review_required']=='R-005'
  image=ROOT/'out/boot-candidate'/(variant+'-boot-v3.img');raw=image.read_bytes();meta=read(image.with_suffix('.json'))
  assert not meta['fixture_only'] and sha(raw)==meta['image_sha256'] and meta.get('hardware_review')==('R-005' if pixel else None)
  assert raw[:8]==b'ANDROID!' and struct.unpack_from('<I',raw,40)[0]==3
  ks,rs=struct.unpack_from('<II',raw,8);assert rs==0 and ks==192+len(fd) and raw[4288:4096+ks]==fd
  shims.append(raw[4096:4288]);defines.append(b['firmware_configuration']['defines'])
  records.append(dict(step=step,variant=variant,pixel_preview=pixel,fd_sha256=sha(fd),image_sha256=sha(raw),hardware_review=meta.get('hardware_review'),generated_contract=contract))
 skip={'ENUMA_DIAG_GOP_STEP','ENUMA_DIAG_PIXEL_PREVIEW'}
 assert {k:v for k,v in defines[0].items() if k not in skip}=={k:v for k,v in defines[1].items() if k not in skip}
 assert defines[0].get('ENUMA_DIAG_PIXEL_PREVIEW','0')=='0' and defines[1]['ENUMA_DIAG_PIXEL_PREVIEW']=='1' and shims[0]==shims[1]
 host=read(ROOT/'reports/enuma-pixel-preview-host.json');assert host['all_passed'] and host['window']==[128,8] and host['saved_bytes']==4096 and not host['physical_pixels_accessed']
 for name,digest in host['sources'].items():assert sha((ROOT/'firmware/diagnostics'/name).read_bytes())==digest
 report=dict(scope='offline R-005 review; no device calls and no execution approval',all_passed=True,firmware_commit=pin['commit'],only_define_differences=sorted(skip),source_inputs_identical=True,profiles=records,window=[128,8],saved_bytes=4096,delay_us=500000,pixel_reads_max=2048,pixel_stores_max=2048,register_reads_max=96,mmio_writes=False,hardware_executed=False,approval_ledger='config/hardware-review-approvals.json')
 (ROOT/'reports/enuma-pixel-preview-bundle.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS: R-005 pair source/defines/generated contract/FD/boot-v3 protection tags; hardware approval not granted')
if __name__=='__main__':main()
