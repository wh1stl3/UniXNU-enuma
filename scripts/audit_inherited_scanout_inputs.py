"""Inspect saved enuma panel inputs; no device reads or board changes."""
import hashlib
import json
from pathlib import Path
import re
from audit_inputs import parse_fdt,cells,strings
ROOT=Path(__file__).resolve().parents[1]


def main():
    path=ROOT/'out/device/live-fdt.bin';data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!='643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62':
        raise ValueError('unreviewed saved FDT')
    nodes=parse_fdt(data);primary=nodes['/soc/qcom,dsi-display-primary']
    handle=cells(primary['qcom,dsi-default-panel'])[0]
    targets=[(n,p) for n,p in nodes.items() if p.get('phandle')==handle.to_bytes(4,'big')]
    if len(targets)!=1:raise ValueError('ambiguous default panel')
    name,panel=targets[0]
    mode=strings(panel['qcom,mdss-dsi-panel-type'])
    if mode!=['dsi_video_mode']:raise ValueError('review video policy')
    timings=[]
    for n,p in nodes.items():
        if n.startswith(name+'/') and 'qcom,mdss-dsi-panel-width' in p:
            timings.append(dict(path=n,width=cells(p['qcom,mdss-dsi-panel-width'])[0],
                                height=cells(p['qcom,mdss-dsi-panel-height'])[0]))
    source=ROOT/'out/display-activity-sources/sde_hw_ctl.c'
    pins=json.loads((ROOT/'config/display-activity-sources.lock.json').read_text())['files']
    pin=next(x for x in pins if x['local_path'].endswith('sde_hw_ctl.c'))
    if hashlib.sha256(source.read_bytes()).hexdigest()!=pin['sha256']:
        raise ValueError('SDE source changed')
    if not re.search(r'intf_mode_sel == SDE_CTL_MODE_SEL_CMD\)\s*mode_sel \|= BIT\(17\)',source.read_text()):
        raise ValueError('v1 command selector fact changed')
    modes=(ROOT/'out/inherited-scanout/android-display-state.local.txt').read_text()
    geometry=sorted({tuple(map(int,x)) for x in re.findall(r'^(\d+)x(\d+)x\d+x\d+vid$',modes,re.M)})
    report=dict(scope='saved FDT plus read-only Android DRM mode inventory; not current UEFI registers',
                fdt_sha256=hashlib.sha256(data).hexdigest(),default_panel=name,
                panel_mode=mode[0],link_indices=cells(panel['qcom,dsi-phy-num']),timings=timings,
                android_drm_mode_dimensions=geometry,source_mode_selector=pin,
                conclusion='Use explicit video policy; cas command-only decoder/kick cannot be directly adopted',
                remaining=['fresh UEFI register snapshot','dual-link mixer to full-panel coordinate mapping',
                           'activity and blend/occlusion','CPU physical relationship','visible GOP execution'],
                board_memory_unchanged=True,pixel_mmio_writes=False)
    (ROOT/'reports/enuma-inherited-scanout-inputs.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: K81 video/two links, per-link timing and Android full-panel mode kept separate; no device operation')


if __name__=='__main__':
    main()
