"""Read-only cross-audit of the planned evening images. Never calls USB tools."""
import hashlib
import json
from pathlib import Path
import struct

from package_enuma_boot import verify

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def inside_out(path):
    path=path.resolve()
    if not path.is_relative_to((ROOT/'out').resolve()):
        raise ValueError('Bundle path escapes own out directory')
    return path


def main():
    plan=read(ROOT/'config/evening-probes.json')
    pin=read(ROOT/'config/uefi-source.lock.json')
    if plan['firmware_commit'] != pin['commit']:
        raise ValueError('Bundle source is stale; rebuild and review the plan')
    expected_inputs={'firmware/'+n:hashlib.sha256((ROOT/'firmware'/n).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
                     for n in pin['file_sha256'] if Path(n).suffix in ('.c','.h','.inf','.inc','.dsc','.fdf','.patch','.toml','.py','.json')}
    for n,sha in pin['file_sha256'].items():
        if hashlib.sha256((ROOT/'firmware'/n).read_bytes()).hexdigest()!=sha:
            raise ValueError('Firmware source changed: '+n)
    images=[]
    for spec in plan['images']:
        variant=spec['variant']
        archive=inside_out(ROOT/'out/entry-probe'/variant)
        image=inside_out(ROOT/'out/boot-candidate'/(variant+'-boot-v3.img'))
        b=read(archive/'enuma-firmware-build.json')
        audit=read(archive/'enuma-fd-audit.json')
        payload=read(archive/'enuma-boot-payload.json')
        meta=read(image.with_suffix('.json'))
        if not b['complete'] or not b['core_patch_reversion_checked']:
            raise ValueError('Incomplete build: '+variant)
        if b['uefi_source_commit']!=pin['commit'] or b['source_inputs_sha256']!=expected_inputs:
            raise ValueError('Mixed firmware source: '+variant)
        expected={'diagnostic_stop_stage':spec['stage'],'diagnostic_dispatch_ordinal':1,
                  'diagnostic_delay_seconds':spec['delay_seconds'],
                  'diagnostic_detail_point':20 if spec['stage']==13 else 13,
                  'diagnostic_dispatch_guid':spec['guid'],
                  'diagnostic_dispatch_guid_only':spec['guid_only'],
                  'diagnostic_dispatch_completion_fallback':spec['completion_fallback'],
                  'diagnostic_dispatch_completion_delay_seconds':7 if spec['completion_fallback'] else None,
                  'diagnostic_simplefb_metadata_only':True,
                  'diagnostic_omitted_oem_modules':['CPRDxe','DisplayDxe','UFSDxe']}
        for key,value in expected.items():
            if b.get(key)!=value:raise ValueError('Unexpected build option '+key+': '+variant)
        fd=(archive/'SILICIUM_UEFI.fd').read_bytes()
        fdsha=hashlib.sha256(fd).hexdigest()
        if not fdsha==b['fd_sha256']==audit['fd_sha256']==payload['fd_sha256']:
            raise ValueError('FD audit mismatch: '+variant)
        if len(audit['matched_oem_modules'])!=30:
            raise ValueError('OEM count differs: '+variant)
        data=image.read_bytes()
        if hashlib.sha256(data).hexdigest()!=meta['image_sha256'] or meta['hardware_ready'] or meta['fixture_only']:
            raise ValueError('Image changed or claims hardware readiness: '+variant)
        raw=data[4096:4096+meta['kernel_bytes']]
        result=verify(data,raw,b'')
        if result['kernel_sha256']!=meta['kernel_sha256'] or result['kernel_sha256']!=payload['raw_sha256']:
            raise ValueError('Raw kernel differs: '+variant)
        if payload['shim_bytes']!=192 or raw[192:]!=fd or raw[56:60]!=b'ARM\x64' or struct.unpack_from('<Q',raw,16)[0]!=len(raw):
            raise ValueError('Unexpected BootShim+FD layout: '+variant)
        images.append(dict(id=spec['id'],variant=variant,image=image.relative_to(ROOT).as_posix(),
                           image_sha256=meta['image_sha256'],fd_sha256=fdsha,
                           stage=spec['stage'],delay_seconds=spec['delay_seconds'],
                           guid_only=spec['guid_only'],completion_fallback=spec['completion_fallback'],device_tested=False))
    ids={row['id'] for row in images}
    if len(images)!=3 or len(ids)!=3 or plan['sequence']!=['early-control-2s','simplefb-pre-2s','simplefb-pre-7s','simplefb-pre-2s']:
        raise ValueError('Unexpected control/repeat sequence')
    report=dict(scope='offline bundle source/FD/image audit only',firmware_commit=pin['commit'],
                plan_sha256=hashlib.sha256((ROOT/'config/evening-probes.json').read_bytes()).hexdigest(),
                images=images,sequence=plan['sequence'],repeat_2s_uses_identical_image=True,
                new_device_trials=0,reads_device_state=False,launches_device=False,
                recovery_guaranteed_by_offline_audit=False,
                target_checkpoint_before_pe_call=True,unexpected_fallthrough_not_excluded=True,
                fallback_limit='only runs after normal initial Dispatcher completion; fixed 7s, not an asynchronous watchdog')
    (ROOT/'reports/enuma-evening-probe-bundle.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: three same-source candidates, 30 OEM/FD/v3/BootShim hashes; four planned attempts, no device action')


if __name__=='__main__':main()
