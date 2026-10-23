"""Read-only audit of the retained macOS generic kernel using NativePrelink.

This does not prelink a donor, select a physical address or emit a boot kernel.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def inspect(data, parser):
    image = parser.macho(data)
    if image['kind'] != 2:
        raise ValueError('Expected MH_EXECUTE')
    for segment in image['segments']:
        if segment['fileoff'] + segment['filesize'] > len(data):
            raise ValueError('Segment file extent outside image')
    commands = image['commands']
    threads = [(off,length) for kind,off,length in commands if kind == 5]
    versions = [(off,length) for kind,off,length in commands if kind == 0x32]
    if len(threads) != 1 or threads[0][1] != 288 or len(versions) != 1 or versions[0][1] < 24:
        raise ValueError('Expected one ARM64 thread entry and build version')
    thread = threads[0][0]
    if struct.unpack_from('<II',data,thread+8) != (6,68):
        raise ValueError('Unexpected ARM64 thread flavor/count')
    entry = struct.unpack_from('<Q',data,thread+272)[0]
    executable = [s for s in image['segments'] if s['initprot'] & 4 and
                  s['va'] <= entry and entry+4 <= s['va']+s['filesize']]
    if entry & 3 or len(executable) != 1:
        raise ValueError('Entry must be aligned and uniquely backed by executable bytes')
    parser.backed_offset(image['segments'],entry,4,len(data))
    if struct.unpack_from('<II',data,versions[0][0]+8) != (2,0x110000):
        raise ValueError('Expected iOS 17.0 deployment')
    exports = parser.exports(data,image)
    symbols = {name:address for address,names in exports.items() for name in names}
    if '_sysreg_restore' not in symbols:
        raise ValueError('Missing initial TCR symbol')
    offset = parser.backed_offset(image['segments'],symbols['_sysreg_restore'],8,len(data))
    tcr = struct.unpack_from('<Q',data,offset)[0]
    if (tcr >> 14) & 3 or (tcr >> 30) & 3 != 2:
        raise ValueError('Both initial translation granules must be 4K')
    return dict(entry_va=hex(entry),entry_segment=executable[0]['name'],initial_tcr=hex(tcr),
                deployment='iOS 17.0',tg0_bytes=4096,tg1_bytes=4096,
                segment_count=len(image['segments']),exported_symbols=len(symbols),
                selected_platform_symbols={name:name in symbols for name in
                    ('_armdt_platform_configured','_armcpu_registered','_source_pthread_status')})


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kernel',type=Path,default=ROOT/'out/ci-runs/39790786938/enuma-macos-bootstrap-39790786938/bootstrap-kernel.macho')
    a=p.parse_args()
    source=ROOT/'out/sources/UniXNU'
    lock=json.loads((ROOT/'config/sources.lock.json').read_text())['sources']['UniXNU']
    if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=lock['commit']:
        raise ValueError('UniXNU source revision mismatch')
    for relative in ('scripts/unixnu/config.py','scripts/build-xnu-4k-baseline.sh'):
        fixed=subprocess.check_output(['git','-C',str(source),'show',lock['commit']+':'+relative])
        if (source/relative).read_bytes()!=fixed:
            raise ValueError('Kernel audit dependency differs from fixed tree: '+relative)
    kit=source/'kits/NativePrelink'
    expected=lock['gitlinks']['kits/NativePrelink']
    revision=subprocess.check_output(['git','-C',str(kit),'rev-parse','HEAD'],text=True).strip()
    if revision != expected:raise ValueError('NativePrelink revision mismatch')
    path=kit/'native_prelink.py'
    original=subprocess.check_output(['git','-C',str(kit),'show','HEAD:native_prelink.py'])
    if path.read_bytes() != original:raise ValueError('NativePrelink parser differs from locked commit')
    spec=importlib.util.spec_from_file_location('enuma_native_prelink_audit',path)
    parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
    retained=json.loads((ROOT/'reports/enuma-macos-upstream-success.json').read_text())
    data=a.kernel.read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    if sha != retained['kernel_sha256'] or len(data) != retained['kernel_bytes']:
        raise ValueError('Retained generic kernel digest/size mismatch')
    result=inspect(data,parser)
    for name in ('entry_va','initial_tcr','tg0_bytes','tg1_bytes'):
        if result[name] != retained['kernel_audit'][name]:raise ValueError('Retained audit mismatch: '+name)
    image=parser.macho(data)
    thread=next(off for kind,off,_ in image['commands'] if kind==5)
    version=next(off for kind,off,_ in image['commands'] if kind==0x32)
    symbols={name:address for address,names in parser.exports(data,image).items() for name in names}
    tcr_at=parser.backed_offset(image['segments'],symbols['_sysreg_restore'],8,len(data))
    mutations=[('arm64e subtype',8,'I',2),('unmapped entry',thread+272,'Q',4),
               ('wrong thread state',thread+8,'I',1),('wrong deployment',version+12,'I',0x100000),
               ('16K TG0',tcr_at,'Q',int(result['initial_tcr'],16)|(2<<14))]
    rejections=[]
    for label,offset,fmt,value in mutations:
        changed=bytearray(data);struct.pack_into('<'+fmt,changed,offset,value)
        try:inspect(changed,parser)
        except ValueError as error:rejections.append({'case':label,'reason':str(error)})
        else:raise ValueError('Mutation accepted: '+label)
    try:inspect(data[:40],parser)
    except ValueError as error:rejections.append({'case':'truncated image','reason':str(error)})
    else:raise ValueError('Truncated image accepted')
    board=tomllib.loads((ROOT/'board.toml').read_text())
    sys.path.insert(0,str(source/'scripts'))
    from unixnu.config import parse_config
    requested=parse_config((ROOT/'configs/enuma_defconfig').read_text())
    required_archives={
        'XNU_SOURCE_CORECRYPTO14':'build/corecrypto-2023/libcorecrypto_kernel_noasm-namespaced.a',
        'XNU_SOURCE_PTHREAD':'build/libpthread-kernel/libpthread_kernel.a',
        'XNU_ARM_DT_PLATFORM':'build/armdt-platform/libArmDTPlatform.a',
        'XNU_ARMCPU':'build/armcpu/libArmCpu.a'}
    build_script=source/'scripts/build-xnu-4k-baseline.sh'
    script=build_script.read_text()
    for archive in required_archives.values():
        if '$ROOT/'+archive not in script:raise ValueError('Archive path changed in fixed upstream recipe')
    flags=retained['effective_bootstrap_switches']
    if any(value != '0' for value in flags.values()):raise ValueError('Unexpected enabled bootstrap feature')
    report=dict(scope='retained generic kernel re-audit and offline dependency closure only',kernel_sha256=sha,
        kernel_bytes=len(data),native_prelink_commit=expected,native_parser_sha256=hashlib.sha256(original).hexdigest(),
        artifact_origin_run=39790786938,format_audit=result,mutated_images_rejected=rejections,
        generic_bootstrap_all_device_features_disabled=True,
        requested_platform_features={key:requested.get(key,False) for key in required_archives},
        retained_bootstrap_feature_values={key:flags.get(key,'not recorded') for key in required_archives},
        upstream_link_archive_paths=required_archives,
        archive_build_opt_in=requested.get('XNU_BUILD_ARCHIVES',False),
        upstream_build_script_sha256=hashlib.sha256(build_script.read_bytes()).hexdigest(),
        enuma_defconfig_sha256=hashlib.sha256((ROOT/'configs/enuma_defconfig').read_bytes()).hexdigest(),
        owned_memory_request=board['payload']['adt']['owned_memory_size'],
        integration_gaps={'kernel_archives_declared':bool(board['kernel'].get('archives')),
                          'kernel_prelink_declared':bool(board['kernel'].get('prelink')),
                          'payload_adt_tool_declared':bool(board['payload']['adt'].get('tool'))},
        candidate_enuma_kernel=False,prelink_generated=False,new_device_trials=0,
        physical_address_selected=False,hardware_boot_demonstrated=False)
    (ROOT/'reports/enuma-kernel-baseline-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: retained ordinary ARM64/4K entry audit and six mutation rejections; generic kernel is NOT an enuma boot candidate')


if __name__=='__main__':main()
