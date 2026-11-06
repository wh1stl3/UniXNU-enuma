"""Pin conservative blend facts and saved enuma blend offsets; no device access."""
import hashlib,json
from pathlib import Path
from audit_inputs import parse_fdt,cells
ROOT=Path(__file__).resolve().parents[1]
def main():
 geometry=json.loads((ROOT/'reports/enuma-scanout-geometry-sources.json').read_text(encoding='utf-8'));route=json.loads((ROOT/'reports/enuma-scanout-route-sources.json').read_text(encoding='utf-8'));assert geometry['all_passed'] and route['all_passed']
 pinned={'sde_hw_lm.c':'4e9cec8f99af86c29000b274b7a8958daa4edae85fae85eda3034b8d1086a08f','sde_hw_mdss.h':'af5db81647446aef51a854a3afa3f61383fd5361fbcf6ff06d2067a927a78daa','sde_crtc.c':'7e83811c2da73d754aa4d8c3bf454635a323161c36805e870772d936a27fa469'}
 pinned['sde_hw_ctl.c']=next(x['sha256'] for x in route['sources'] if x['path'].endswith('/sde_hw_ctl.c'))
 sources={};records=[];base='https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/'
 for name,digest in pinned.items():
  raw=(ROOT/'out/display-native-sources'/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest; sources[name]=raw.decode();records.append(dict(url=base+name,sha256=digest,license='GPL-2.0-only reference; no implementation imported'))
 ctl=sources['sde_hw_ctl.c'];lm=sources['sde_hw_lm.c'];mdss=sources['sde_hw_mdss.h'];crtc=sources['sde_crtc.c']
 for text,marker in [(ctl,'mix = (i + 1) & 0x7;'),(ctl,'ext = i >= 7;'),(ctl,'#define CTL_MIXER_BORDER_OUT            BIT(24)'),(lm,'const_alpha = (bg_alpha & 0xFF) | ((fg_alpha & 0xFF) << 16);'),(lm,'IS_SDE_MAJOR_SAME(m->hwversion, SDE_HW_VER_600)'),(lm,'val = BIT(16); /* enable dim layer */'),(lm,'if (stage == SDE_STAGE_BASE)'),(mdss,'SDE_STAGE_BASE = 0'),(mdss,'#define SDE_BLEND_FG_ALPHA_FG_CONST\t(0 << 0)'),(mdss,'#define SDE_BLEND_BG_ALPHA_BG_CONST\t(1 << 8)'),(crtc,'case SDE_DRM_BLEND_OP_OPAQUE:')]:assert marker in text,marker
 raw=(ROOT/'out/device/live-fdt.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==geometry['saved_fdt_sha256'];p=parse_fdt(raw)['/soc/qcom,mdss_mdp@ae00000']
 offsets=cells(p['qcom,sde-mixer-blend-op-off']);assert offsets==list(range(0x20,0x111,0x18)) and cells(p['qcom,sde-mixer-blendstages'])==[11]
 assert cells(p['qcom,sde-mixer-off'])==list(range(0x45000,0x4b000,0x1000)) and max(offsets)+8<=0x320
 report=dict(scope=__doc__,all_passed=True,source_commit='52a2f180865f8368828985d6384130acd093fa93',sources=records,saved_fdt_sha256=geometry['saved_fdt_sha256'],blend_offsets=[hex(x) for x in offsets],maximum_encoded_stage=12,dim_bit=16,packed_opaque_alpha='0x00ff0000',opaque_blend_op='0x100',maximum_mmio_reads=289,maximum_wait_calls=2,mmio_writes=False,pixel_access=False,new_mapping=False,limitations=['conservative sole source/no dim/base-or-constant-opaque pattern, not exhaustive visibility classifier','refusal does not prove occlusion or transparency','shadow state, physical route, exclusions, fetch/IOVA/cache and panel remain unproven'])
 (ROOT/'reports/enuma-scanout-blend-sources.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('PASS: fixed native stage/dim/packed-alpha facts and exact saved blend layout')
if __name__=='__main__':main()
