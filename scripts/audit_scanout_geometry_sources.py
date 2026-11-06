"""Pinned Xiaomi geometry packing and exact saved enuma LM offsets; no device access."""
import hashlib,json
from pathlib import Path
from audit_inputs import parse_fdt,cells
ROOT=Path(__file__).resolve().parents[1]
def main():
 old=json.loads((ROOT/'reports/enuma-scanout-route-sources.json').read_text(encoding='utf-8'))
 assert old['all_passed']
 record=next(x for x in old['sources'] if x['path'].endswith('/sde_hw_sspp.c'))
 raw=(ROOT/'out/display-native-sources/sde_hw_sspp.c').read_bytes();assert hashlib.sha256(raw).hexdigest()==record['sha256'];sspp=raw.decode()
 assert '#define SSPP_OUT_SIZE                      0x0c' in sspp and '#define SSPP_OUT_XY                        0x10' in sspp
 assert 'out_size_off = SSPP_OUT_SIZE;' in sspp and 'out_xy_off = SSPP_OUT_XY;' in sspp
 assert 'dst_xy = (cfg->dst_rect.y << 16) | (cfg->dst_rect.x);' in sspp and 'dst_size = (cfg->dst_rect.h << 16) | (cfg->dst_rect.w);' in sspp
 raw=(ROOT/'out/display-native-sources/sde_hw_lm.c').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='4e9cec8f99af86c29000b274b7a8958daa4edae85fae85eda3034b8d1086a08f';lm=raw.decode()
 assert '#define LM_OUT_SIZE                       0x04' in lm and 'outsize = mixer->out_height << 16 | mixer->out_width;' in lm
 dt=(ROOT/'out/device/live-fdt.bin').read_bytes();assert hashlib.sha256(dt).hexdigest()==old['saved_fdt_sha256'];p=parse_fdt(dt)['/soc/qcom,mdss_mdp@ae00000']
 mixers=cells(p['qcom,sde-mixer-off']);assert mixers==list(range(0x45000,0x4b000,0x1000)) and cells(p['qcom,sde-mixer-size'])==[0x320]
 assert all(x+8<=0x84208 for x in mixers)
 url='https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_lm.c'
 result=dict(scope=__doc__,all_passed=True,source_commit='52a2f180865f8368828985d6384130acd093fa93',lm_url=url,lm_sha256=sha,sspp_source=record,saved_fdt_sha256=old['saved_fdt_sha256'],mixer_offsets=[hex(x) for x in mixers],mixer_size='0x320',mmio_reads_max=250,wait_calls_max=2,mmio_writes=False,pixel_access=False,new_mapping=False,limitations=['configured 1:1 rectangle containment only','no scaler/decimator, exclusion, alpha or occlusion proof','no physical LM/pingpong/DSC/fetch/visible-output proof'])
 (ROOT/'reports/enuma-scanout-geometry-sources.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print('PASS: pinned geometry layout and exact saved enuma mixers')
if __name__=='__main__':main()
