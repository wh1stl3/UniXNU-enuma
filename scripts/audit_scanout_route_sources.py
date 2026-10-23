"""Pin native CTL facts and saved enuma offsets; never access hardware."""
import hashlib,json
from pathlib import Path
from audit_inputs import parse_fdt,cells,strings
ROOT=Path(__file__).resolve().parents[1]
def main():
 lock=json.loads((ROOT/'reports/enuma-native-display-diagnosis-sources.json').read_text(encoding='utf-8'));records=[];sources={}
 for x in lock['files']:
  if Path(x['path']).name not in ('sde_hw_ctl.c','sde_hw_catalog.c','sde_hw_intf.c','sde_hw_sspp.c'):continue
  raw=(ROOT/'out/display-native-sources'/Path(x['path']).name).read_bytes();assert hashlib.sha256(raw).hexdigest()==x['sha256'];records.append(x);sources[Path(x['path']).name]=raw.decode()
 ctl=sources['sde_hw_ctl.c']
 for marker in ['#define   CTL_INTF_ACTIVE               0x0F4','((lm) == LM_5) ? (0x024)', 'mixercfg[3] = SDE_REG_READ(c, CTL_LAYER_EXT3(lm))','intf_active |= BIT(cfg->intf[i] - INTF_0)']:
  assert marker in ctl,marker
 table=ctl[ctl.index('sspp_reg_cfg_tbl[SSPP_MAX]'):ctl.index('static struct sde_ctl_cfg *_ctl_offset')]
 tuples=['{0, 0, 3, BIT(0)}','{0, 3, 3, BIT(2)}','{0, 6, 3, BIT(4)}','{0, 26, 3, BIT(6)}','{0, 18, 3, BIT(16)}','{0, 21, 3, BIT(18)}','{2, 0, 4, 0}','{2, 4, 4, 0}']
 assert all(t in table for t in tuples)
 assert 'sde_cfg->ctl_rev = SDE_CTL_CFG_VERSION_1_0_0;' in sources['sde_hw_catalog.c'].split('IS_KONA_TARGET(hw_rev)')[1].split('IS_SAIPAN_TARGET')[0]
 contract=json.loads((ROOT/'reports/enuma-dsi-native-source-contract.json').read_text(encoding='utf-8'))
 header=(ROOT/'out/display-native-sources/sde_hw_catalog.h').read_bytes();assert hashlib.sha256(header).hexdigest()==contract['catalog_header_sha256']
 assert b'#define SDE_HW_MAJOR_MINOR(rev)' in header and b'((rev) >> 16)' in header and b'SDE_HW_VER(6, 0, 0) /* kona */' in header
 raw=(ROOT/'out/device/live-fdt.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()=='643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62'
 p=parse_fdt(raw)['/soc/qcom,mdss_mdp@ae00000'];ctls=cells(p['qcom,sde-ctl-off']);pipes=cells(p['qcom,sde-sspp-off']);intfs=cells(p['qcom,sde-intf-off'])
 assert ctls==list(range(0x2000,0x2c00,0x200)) and cells(p['qcom,sde-ctl-size'])==[0x1dc]
 assert pipes==[0x5000,0x7000,0x9000,0xb000,0x25000,0x27000,0x29000,0x2b000]
 assert strings(p['qcom,sde-sspp-type'])==['vig']*4+['dma']*4
 assert intfs==[0x6b000,0x6b800,0x6c000,0x6c800] and strings(p['qcom,sde-intf-type'])==['dp','dsi','dsi','dp']
 assert all(off+0xb4<0x84208 for off in ctls)
 report=dict(scope=__doc__,all_passed=True,sources=records,version_header_url=contract['catalog_header_url'],version_header_sha256=contract['catalog_header_sha256'],required_version_major_minor='6.0',saved_fdt_sha256=hashlib.sha256(raw).hexdigest(),ctl_offsets=[hex(x) for x in ctls],sspp_offsets=[hex(x) for x in pipes],dsi_interface_bits=[1,2],nonvirtual_stage_tuples=tuples,maximum_mmio_reads=241,maximum_wait_calls=2,pixel_access=False,mmio_writes=False,new_mapping=False,limitations=['staging register association may be shadow/stale','no proven LM output/pingpong/DSC/fetch or visible pixel route','no numerical device dump'])
 (ROOT/'reports/enuma-scanout-route-sources.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('PASS: pinned native CTL layout and exact saved enuma offsets; no device access')
if __name__=='__main__':main()
