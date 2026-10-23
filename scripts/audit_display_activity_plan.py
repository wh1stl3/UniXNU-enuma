"""Offline source/DT plan after the one-shot preview; no device or MMIO calls."""
import argparse
import hashlib
import json
from pathlib import Path
from audit_inputs import parse_fdt, cells, strings

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fdt', type=Path, default=ROOT/'out/device/live-fdt.bin')
    args = parser.parse_args()
    lock = json.loads((ROOT/'config/display-activity-sources.lock.json').read_text())
    records = []
    sources = {}
    for item in lock['files']:
        raw = (ROOT/item['local_path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item['sha256'], item['local_path']
        source = raw.decode('utf-8')
        sources[Path(item['local_path']).name] = source
        records.append({key:item[key] for key in ('local_path','commit','url','sha256')})
    intf = sources['sde_hw_intf.c']
    for symbol, value in [('INTF_TIMING_ENGINE_EN','0x000'),('INTF_FRAME_LINE_COUNT_EN','0x0A8'),('INTF_FRAME_COUNT','0x0AC'),('INTF_LINE_COUNT','0x0B0')]:
        assert any(line.startswith('#define') and symbol in line.split() and value in line.split() for line in intf.splitlines()), symbol
    assert 's->is_en = SDE_REG_READ(c, INTF_TIMING_ENGINE_EN)' in intf
    blob = args.fdt.read_bytes()
    nodes = parse_fdt(blob)
    candidates = [(path, props) for path, props in nodes.items() if b'qcom,sde-kms' in props.get('compatible',b'')]
    assert len(candidates) == 1
    mdp_path, mdp = candidates[0]
    reg = cells(mdp['reg']); base, length = reg[:2]
    assert (base, length) == (0x0ae00000,0x84208)
    offsets = cells(mdp['qcom,sde-intf-off'])
    kinds = strings(mdp['qcom,sde-intf-type'])
    assert len(offsets)==len(kinds)==4
    dsi=[]
    for offset, kind in zip(offsets,kinds):
        if kind!='dsi': continue
        addresses = {name:base+offset+relative for name,relative in [('timing_engine',0),('count_enable',0xa8),('frame_count',0xac),('line_count',0xb0)]}
        assert all(base<=address and address+4<=base+length for address in addresses.values())
        dsi.append({'block_offset':hex(offset),'register_addresses':{k:hex(v) for k,v in addresses.items()}})
    assert len(dsi)==2
    defaults=[]
    for path, props in nodes.items():
        if 'qcom,dsi-default-panel' not in props: continue
        phandle=cells(props['qcom,dsi-default-panel'])[0]
        match=[(p,v) for p,v in nodes.items() if 'phandle' in v and cells(v['phandle'])==[phandle]]
        assert len(match)==1
        panel_path,panel=match[0]
        defaults.append({'display_node':path,'panel_node':panel_path,'declared_name':strings(panel['qcom,mdss-dsi-panel-name']),'declared_mode':strings(panel['qcom,mdss-dsi-panel-type']),'meaning':'saved DT default only; not live panel/bootloader route proof'})
    simple = sources['SimpleFbDxe.c']
    assert 'DisplaySetMode(IN EFI_GRAPHICS_OUTPUT_PROTOCOL *This, IN UINT32 ModeNumber)\n{\n  return EFI_SUCCESS;' in simple.replace('\r\n','\n')
    assert 'ZeroMem((void *)FrameBufferAddress, FrameBufferSize)' in simple
    assert 'WriteBackInvalidateDataCacheRange' in simple
    report = {'scope':__doc__,'all_passed':True,'source_inputs':records,'saved_fdt_sha256':hashlib.sha256(blob).hexdigest(),'mdp_node':mdp_path,'mdp_base':hex(base),'dt_length':hex(length),'existing_r004_mapping_length':'0x85000','default_panels':defaults,'dsi_interfaces':dsi,'same_soc_reuse':{'device':'elish / SM8250','decision':'reuse source separation and metadata/cache review only; its SetMode returns success without programming the display, so copying it does not establish a running panel','no_board_values_imported':True},'proposed_first_probe':{'scope':'two DSI TIMING_ENGINE_EN read-only values; classify only configured timing enable, not active scanout','maximum_register_reads':2,'new_mapping':False,'pixel_access':False,'counter_writes':False,'hardware_executed':False},'subsequent_counter_probe_conditions':['Confirm timing-enable first','Observe FRAME_LINE_COUNT_EN without changing it; disabled counters cannot rule out a running interface','Counter delta requires two bounded samples and explicit wrap/enable checks; a single frame count can be stale','CTL/layer routing, physical/IOVA translation, panel/backlight and visible output remain separate unknowns'],'no_new_firmware_candidate':True,'pixel_replay_authorized':False,'xnu_entered':False}
    (ROOT/'reports/enuma-display-activity-plan.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: fixed Qualcomm and same-SoC sources / saved enuma DT; two-read timing plan stays within existing R-004 mapping; no hardware execution')


if __name__ == '__main__':
    main()
