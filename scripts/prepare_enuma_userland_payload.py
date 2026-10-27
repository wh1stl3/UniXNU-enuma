"""Build/read back a real offline FAT payload using pinned upstream machinery."""
import argparse,hashlib,json,subprocess,sys,os
from pathlib import Path
from types import SimpleNamespace
if sys.version_info<(3,11):
    import tomli;sys.modules['tomllib']=tomli
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--prelink',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();e=a.evidence_root.resolve();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    prelink=a.prelink.resolve();prelink.relative_to(ROOT/'out');r=json.loads((prelink/'result.json').read_text())
    kernel=prelink/'userland-components.experimental.macho'
    if r['passed'] is not True or r['runtime_qualified'] is not False or sha(kernel)!=r['image_sha256']:raise ValueError('prelink binding failed')
    trust=e/'out/full-boot/original-static-system.bundle'
    if sha(trust)!='7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7':raise ValueError('trust input changed')
    base=ROOT/'out/sources/UniXNU';pins=json.loads((ROOT/'reports/enuma-full-payload.json').read_text())['sources']
    for name,digest in pins.items():
        if sha(base/name)!=digest:raise ValueError('upstream payload dependency changed')
    # Existing generator executes read-only references and writes only its
    # explicit --output under this new payload directory. No seed/patch hooks.
    inputs=['scripts/make_enuma_adt.py','scripts/audit_inputs.py','scripts/plan_adt.py',
            'config/system-reuse-sources.lock.json','out/device/live-fdt.bin',
            'out/sources/UniXNU-umi/scripts/umi_adt.py']
    bindings={n:sha(e/n) for n in inputs}
    for name in inputs[:4]:
        if (ROOT/name).read_bytes()!=(e/name).read_bytes():raise ValueError('generator source differs from reviewed local copy')
    from make_enuma_adt import hardware
    total=sum(b['size'] for b in hardware(e/'out/device/live-fdt.bin')['memory_banks'])
    sys.path.insert(0,str(base/'scripts'));from unixnu import payload
    ctx=SimpleNamespace(tree=e,work=out,logs=out/'logs',uefi=None,
        args=SimpleNamespace(trust_cache=trust,data_ramdisk=None,gpu_addon=None),
        board={'payload':dict(dram_size=total,size_mib=96,volume='ENUMAU01',timeout=0,
            title='enuma offline graphics-HID input',kernel_args=['-v'],
            adt=dict(tool='scripts/make_enuma_adt.py',ipad_identity=True,owned_memory_size='0x20000000'))})
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    image=payload.build(ctx,kernel=kernel);readback={}
    for name in ['Payloads/kernel.macho','Payloads/kernel.macho.trustcache','Payloads/kernel.macho.adt','unixnu.toml']:
        content=subprocess.check_output(['mtype','-i',str(image),'::/EFI/UniXNU/'+name])
        readback[name]=hashlib.sha256(content).hexdigest()
        if name.endswith('.adt') or name.endswith('.toml'):(out/Path(name).name).write_bytes(content)
    if readback['Payloads/kernel.macho']!=sha(kernel) or readback['Payloads/kernel.macho.trustcache']!=sha(trust):raise ValueError('FAT readback mismatch')
    if any(sha(e/n)!=h for n,h in bindings.items()):raise ValueError('shared read-only input changed during generation')
    report=dict(passed=True,payload_sha256=sha(image),payload_bytes=image.stat().st_size,readback=readback,
        reference_bindings=bindings,upstream_sources=pins,root_volume_included=False,data_seed_included=False,
        runtime_qualified=False,hardware_executed=False,scope='real FAT component bundle, not a desktop-ready boot image')
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
