"""Pin mixer/right-role facts and remaining physical GOP admission gaps; no I/O."""
import hashlib
import json
from pathlib import Path
import re
from audit_inputs import parse_fdt,cells
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    lock=json.loads((ROOT/'config/inherited-gop-sources.lock.json').read_text())
    for entry in lock['files']:
        if sha(ROOT/entry['local_path'])!=entry['sha256']: raise ValueError('source changed: '+entry['local_path'])
    lm=(ROOT/'out/display-native-sources/sde_hw_lm.c').read_text()
    if not re.search(r'if \(mixer->right_mixer\)\s*op_mode \|= BIT\(31\)',lm): raise ValueError('LM right-role fact changed')
    if not re.search(r'else\s*op_mode &= ~BIT\(31\)',lm): raise ValueError('LM left-role fact changed')
    fdt=ROOT/'out/device/live-fdt.bin'
    if sha(fdt)!='643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62': raise ValueError('saved FDT changed')
    nodes=parse_fdt(fdt.read_bytes()); mdp=nodes['/soc/qcom,mdss_mdp@ae00000']
    panel_handle=cells(nodes['/soc/qcom,dsi-display-primary']['qcom,dsi-default-panel'])[0]
    panel=next(n for n,p in nodes.items() if p.get('phandle')==panel_handle.to_bytes(4,'big'))
    timing_nodes=[(n,p) for n,p in nodes.items() if n.startswith(panel+'/') and 'qcom,display-topology' in p]
    if len(timing_nodes)!=1: raise ValueError('default topology needs explicit timing selection')
    timing,tp=timing_nodes[0]; index=cells(tp['qcom,default-topology-index'])[0]
    topology=cells(tp['qcom,display-topology'])[index*3:index*3+3]
    parser=(ROOT/'out/inherited-gop/routing-sources/dsi_panel.c').read_text()
    for field,offset in [('num_lm',''),('num_enc',' + 1'),('num_intf',' + 2')]:
        if 'top->'+field+' = array[i * TOPOLOGY_SET_LEN'+offset+'];' not in parser: raise ValueError('topology tuple semantics changed')
    dbg=(ROOT/'out/inherited-gop/routing-sources/sde_dbg.c').read_text()
    if 'pm_runtime_get_sync(sde_dbg_base.dev)' not in dbg or 'if (_sde_power_check(sde_dbg_base.dump_mode))' not in dbg: raise ValueError('native dump power gating changed')
    cb=nodes['/soc/qcom,mdss_mdp@ae00000/qcom,smmu_sde_unsec_cb']; iommu=cells(cb['iommus'])
    providers=[(n,p) for n,p in nodes.items() if p.get('phandle')==iommu[0].to_bytes(4,'big')]
    if len(providers)!=1: raise ValueError('ambiguous SMMU provider')
    memory=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c'
    line=next(x.strip() for x in memory.read_text().splitlines() if '"Display Reserved"' in x)
    if 'WRITE_THROUGH_XN' not in line: raise ValueError('display mapping policy changed: review actual attributes')
    report=dict(scope='pinned manufacturer register facts and saved board inputs; not a fresh UEFI register snapshot',
      sources=lock['files'],saved_fdt_sha256=sha(fdt),lm_origin_rule='LM_OP_MODE bit31 chooses right mixer; numeric LM order is not panel order',
      mixer_offsets=cells(mdp['qcom,sde-mixer-off']),mixer_pair_mask=cells(mdp['qcom,sde-mixer-pair-mask']),
      source_split_supported_by_soc='qcom,sde-has-src-split' in mdp,
      default_panel_topology=dict(timing=timing,index=index,tuple=topology,num_lm=topology[0],num_compression_encoders=topology[1],num_intf=topology[2],is_fresh_uefi_observation=False),
      independent_SSPP_count_not_specified_by_topology=True,
      native_debug_dump_requires_runtime_power_or_already_clocked_context=True,
      alpha_policy='RGBX/source-alpha-disabled only; Mu VideoFill combines RGB, unlike cas opaque physical writer',
      nonsecure_display_iommu=dict(provider=providers[0][0],args=iommu[1:],provider_reg=cells(providers[0][1]['reg'])),
      original_display_memory_record=line,original_memory_source_sha256=sha(memory),
      physical_gop_admitted=False,gop_protocol_published=False,device_boot_issued=False,
      unresolved=['fresh stable UEFI dual-link snapshot','LM/PP/DSC/INTF downstream association','display SMMU stream translation or bypass','CPU identity mapping and cache policy compatible with backend'],
      next='Video-only routed capture; omit command/unused PP/SSPP fields, keep observed masks and physical requirements; default no-DSC route first')
    (ROOT/'reports/enuma-inherited-gop-policy.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: pinned right-role semantics, saved SMMU binding and original write-through mapping; physical GOP correctly not admitted')
if __name__=='__main__': main()
