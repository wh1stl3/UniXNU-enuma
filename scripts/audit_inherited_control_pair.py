"""Compare actual S-008 sampler and new constant-body control FD inventories."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
if sys.version_info<(3,11):
    import tomli
    sys.modules['tomllib']=tomli
from audit_display_handoff import firmware_files
from audit_display_boundary_core import codeview_guid_only
ROOT=Path(__file__).resolve().parents[1]
PROVIDER='dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92'
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sample',type=Path,required=True);p.add_argument('--control',type=Path,required=True);p.add_argument('--topology',action='store_true',help='query1/query2 complementary first-status pair, same source');p.add_argument('--tool-path',type=Path);a=p.parse_args()
    if a.tool_path: sys.path.insert(0,str(a.tool_path.resolve()))
    dirs=[x.resolve() for x in [a.sample,a.control]]
    qs=[json.loads((d/'qualification.json').read_text()) for d in dirs]
    bs=[json.loads((d/'firmware-build.json').read_text()) for d in dirs]
    for d,q in zip(dirs,qs):
        for name,item in q['files'].items():
            if sha((d/name).read_bytes())!=item['sha256']: raise ValueError('archive changed: '+name)
    configs=[json.loads(json.dumps(b['firmware_configuration'])) for b in bs]
    if a.topology:
        if [q.get('topology_status_query') for q in qs]!=[1,2] or any(q['trial_kind']!='inherited-video-audit' for q in qs) or qs[0]['firmware_commit']!=qs[1]['firmware_commit']: raise ValueError('wrong topology pair')
        for i,c in enumerate(configs):
            if c['defines'].pop('ENUMA_VIDEO_TOPOLOGY_QUERY')!=str(i+1): raise ValueError('topology macro differs')
        if (dirs[0]/'entry.c').read_bytes()!=(dirs[1]/'entry.c').read_bytes(): raise ValueError('topology pair entry changed')
        if (dirs[0]/'VideoResult.h').read_bytes()!=(dirs[1]/'VideoResult.h').read_bytes(): raise ValueError('selector changed')
    elif qs[0]['trial_kind']!='inherited-video-audit' or qs[1]['trial_kind']!='inherited-video-entry-control': raise ValueError('wrong pair')
    if configs[0]!=configs[1] or bs[0]['unixnu_qualification']!=bs[1]['unixnu_qualification']: raise ValueError('config/backend changed beyond selected entry source')
    for key in ['autogen_sha256','static_library_list_sha256']:
        if bs[0]['gop_provider_generated_contract'][key]!=bs[1]['gop_provider_generated_contract'][key]: raise ValueError('constructors or library inventory changed: '+key)
    inventories=[{x['guid']:x for x in firmware_files((d/'SILICIUM_UEFI.fd').read_bytes())} for d in dirs]
    if inventories[0].keys()!=inventories[1].keys(): raise ValueError('actual PE inventory changed')
    unchanged=0;metadata={};changed={}
    for guid,left in inventories[0].items():
        right=inventories[1][guid]
        if left['data']==right['data']: unchanged+=1;continue
        changed[guid]=dict(name=left['name'],sample_sha256=sha(left['data']),control_sha256=sha(right['data']))
        if guid!=PROVIDER: metadata[guid]=codeview_guid_only(left['data'],right['data'])
    if PROVIDER not in changed: raise ValueError('provider did not change')
    if (dirs[0]/'enuma-uefi.raw').read_bytes()[:192]!=(dirs[1]/'enuma-uefi.raw').read_bytes()[:192] or qs[0]['ram_payload_sha256']!=qs[1]['ram_payload_sha256']: raise ValueError('BootShim/full inputs changed')
    report=dict(scope='actual two FD PE inventories and full input comparison; source revision differs only for documented control selection, not hardware success',
      sample_firmware=qs[0]['firmware_commit'],control_firmware=qs[1]['firmware_commit'],
      same_firmware_configuration=True,same_autogen_and_library_inventory=True,same_bootshim=True,same_full_fat=True,
      PE_count=len(inventories[0]),unchanged_PE_count=unchanged,changed_PE=changed,debug_GUID_only_PE=metadata,
      sole_runtime_PE_change=PROVIDER,physical_gop_tested=False)
    report['same_firmware_configuration']=not a.topology
    report['same_configuration_except_topology_query']=a.topology
    report['topology_query_pair']=[1,2] if a.topology else None
    (ROOT/'reports'/('enuma-video-topology-pair-code.json' if a.topology else 'enuma-inherited-control-pair.json')).write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: only provider runtime PE changes; remaining differences are individually checked CodeView GUID bytes; constructor/config/BootShim/FAT match')
if __name__=='__main__':main()
