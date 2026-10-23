"""Audit staged Core-owned GOP candidates without invoking ADB or fastboot."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SUFFIXES=('.c','.h','.inf','.inc','.dsc','.fdf','.patch','.toml','.py','.json')

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def digest(data):return hashlib.sha256(data).hexdigest()

def main(config_name='gop-split-probes.json',report_name='enuma-gop-core-split.json'):
    config=read(ROOT/'config'/config_name)
    pin=read(ROOT/'config/uefi-source.lock.json')
    assert config['firmware_commit']==pin['commit']
    assert config['transport']=='core-warning-v2'
    assert [x['step'] for x in config['profiles']] in ([0,1],[2,5],[3,8])
    wanted={}
    for name,sha in pin['file_sha256'].items():
        raw=(ROOT/'firmware'/name).read_bytes();assert digest(raw)==sha,name
        if Path(name).suffix in SUFFIXES:wanted['firmware/'+name]=digest(raw.replace(b'\r\n',b'\n'))
    records=[];definitions=[]
    for profile in config['profiles']:
        snap=ROOT/'out/entry-probe'/profile['variant']
        b=read(snap/'enuma-firmware-build.json')
        assert b['uefi_source_commit']==pin['commit'] and b['complete'] and b['core_patch_reversion_checked']
        assert b['diagnostic_gop_transport']==config['transport'] and b['diagnostic_gop_reset_owner']=='DxeCore'
        assert b['diagnostic_gop_query']==1 and b['diagnostic_gop_step']==profile['step']
        assert (b['diagnostic_stop_stage'],b['diagnostic_detail_point'],b['diagnostic_delay_seconds'])==(13,16,2)
        assert b['diagnostic_dispatch_guid']=='dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92'
        assert b['diagnostic_dispatch_guid_only'] and b['diagnostic_dispatch_completion_fallback']
        assert b['diagnostic_dispatch_ordinal']==1 and b['diagnostic_simplefb_metadata_only']
        assert b['diagnostic_omitted_oem_modules']==['CPRDxe','DisplayDxe','UFSDxe']
        assert b['source_inputs_sha256']==wanted
        generated=b['gop_provider_generated_contract']
        assert all(generated[k] for k in ('inf_matches_baseline','reset_library_absent','psci_constructor_absent'))
        autogen=(snap/'SimpleFb.AutoGen.c').read_text(encoding='utf-8')
        libraries=(snap/'SimpleFb.static_library_files.lst').read_text(encoding='utf-8')
        assert digest(autogen.encode())==generated['autogen_sha256']
        assert digest(libraries.encode())==generated['static_library_list_sha256']
        assert 'ArmPsciResetSystemLibConstructor' not in autogen
        assert not any(x in libraries.lower() for x in ('pscireset','resetsystemlib'))
        fd=(snap/'SILICIUM_UEFI.fd').read_bytes();assert digest(fd)==b['fd_sha256']
        audit=read(snap/'enuma-fd-audit.json');assert audit['fd_sha256']==b['fd_sha256']
        image=ROOT/'out/boot-candidate'/(profile['variant']+'-boot-v3.img')
        raw=image.read_bytes();meta=read(image.with_suffix('.json'))
        assert digest(raw)==meta['image_sha256']
        assert raw[:8]==b'ANDROID!' and struct.unpack_from('<I',raw,40)[0]==3
        kernel_size,ramdisk_size=struct.unpack_from('<II',raw,8)
        assert ramdisk_size==0 and kernel_size==192+len(fd)
        assert raw[4096+192:4096+kernel_size]==fd
        definitions.append(b['firmware_configuration']['defines'])
        records.append(dict(id=profile['id'],step=profile['step'],variant=profile['variant'],
            image_sha256=digest(raw),fd_sha256=digest(fd),generated_contract=generated,
            image_local_path=image.relative_to(ROOT).as_posix(),
            local_build_report=(snap/'enuma-firmware-build.json').relative_to(ROOT).as_posix()))
    assert {k:v for k,v in definitions[0].items() if k!='ENUMA_DIAG_GOP_STEP'}=={
        k:v for k,v in definitions[1].items() if k!='ENUMA_DIAG_GOP_STEP'}
    previous=read(ROOT/'reports/enuma-simplefb-reuse-audit.json')
    reference=next(x for x in previous['sources'] if x['id']=='E5')
    assert digest((ROOT/reference['local_path']).read_bytes())==reference['sha256']
    report=dict(scope='offline bundle audit; no device calls, no new runtime evidence',
        firmware_commit=pin['commit'],transport=config['transport'],all_passed=True,
        source_inputs_identical=True,only_firmware_define_difference='ENUMA_DIAG_GOP_STEP',
        profiles=records,host_report='reports/enuma-gop-audit-host.json',
        core_report='reports/enuma-dispatch-details-host.json',hardware_execution=False,
        prior_timeout_unresolved=True,old_timeout_candidate_not_retested=True,
        reuse_reference={k:reference[k] for k in ('repository','commit','path','sha256')},
        reuse_assessment='Reuse provider/consumer separation; do not import physical clear/cache/address assumptions',
        remaining_steps=([] if config['profiles'][0]['step']==3 else [6,7,3,4] if config['profiles'][0]['step']==2 else [2,3,4]),runtime_limit='Core return gate and completion fallback cannot recover a hung service')
    (ROOT/'reports'/report_name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS: two Core-owned GOP profiles, fixed sources, no provider reset dependency, matching embedded FD and image hashes; no device calls')

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='gop-split-probes.json',choices=('gop-split-probes.json','gop-mode-split-probes.json','r004-scanout-probes.json'))
    args=parser.parse_args()
    main(args.config, 'enuma-r004-scanout-bundle.json' if args.config=='r004-scanout-probes.json' else 'enuma-gop-mode-split.json' if args.config=='gop-mode-split-probes.json' else 'enuma-gop-core-split.json')
