"""Emit a same-donor graphics/HID closure using the pinned real prelink emitter.

No device access, board changes, fake services, or hardware qualification.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=['com.apple.filesystems.apfs','com.apple.driver.AppleMobileFileIntegrity',
      'com.apple.security.AppleImage4','com.apple.kext.CoreTrust','com.apple.security.sandbox',
      'com.apple.iokit.IOHIDFamily','com.apple.iokit.IOSurface','com.apple.iokit.IOMobileGraphicsFamily',
      'com.apple.AppleFSCompression.AppleFSCompressionTypeZlib']
EXTRA=['com.apple.iokit.IOGPUFamily','com.apple.iokit.IOHIDEventDriver']
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();e=a.evidence_root.resolve();out=a.output.resolve()
    out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    lock=json.loads((ROOT/'config/sources.lock.json').read_text())['sources']['UniXNU']
    kit=ROOT/'out/sources/UniXNU/kits/NativePrelink';pin=lock['gitlinks']['kits/NativePrelink']
    sources={}
    # Validate every imported Python module, not only the CLI entry point.
    for path in kit.glob('*.py'):
        tracked=subprocess.check_output(['git','-C',str(kit),'show',pin+':'+path.name])
        if tracked!=path.read_bytes():raise ValueError('modified upstream module '+path.name)
        sources[path.name]=sha(tracked)
    peer=e/'out/sources/UniXNU-umi';peer_lock=json.loads((ROOT/'config/system-reuse-sources.lock.json').read_text())['references'][0]
    recipe=peer/'bringup/tools/build_umi_prelink.py'
    if sha(recipe.read_bytes())!=peer_lock['files']['bringup/tools/build_umi_prelink.py']['sha256']:raise ValueError('peer recipe changed')
    if any(repr(n) not in recipe.read_text() and '"'+n+'"' not in recipe.read_text() for n in EXTRA):raise ValueError('peer roots absent')
    kernel=(e/'out/ci-runs/39927966148/enuma-macos-platform-39927966148/platform-kernel.macho').read_bytes()
    donor=(e/'out/donor-audit/kernelcache.decompressed').read_bytes()
    if sha(kernel)!='b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d':raise ValueError('platform kernel changed')
    if sha(donor)!='f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7':raise ValueError('donor changed')
    sys.path.insert(0,str(kit));import native_prelink,emit_prelink
    attempts=[];chosen=None
    for slide in range(0,-0x2000001,-0x200000):
        try:native_prelink.plan(kernel,donor,BASE+EXTRA,slide)
        except ValueError as exc:
            attempts.append(dict(slide=hex(slide),error=str(exc)))
            if 'collid' not in str(exc).lower() and 'overlap' not in str(exc).lower():raise
        else:chosen=slide;break
    if chosen is None:raise ValueError('no nonoverlapping placement')
    # Same donor initializer already established in original enuma prelink.
    early={'com.apple.driver.AppleMobileFileIntegrity':0xfffffff005ab4ae0}
    image,details=emit_prelink.emit(kernel,donor,BASE+EXTRA,chosen,early)
    target=out/'userland-components.experimental.macho';target.write_bytes(image)
    (out/'emitter.json').write_text(json.dumps(details,indent=2)+'\n')
    # Reuse the real enuma entry/TCR audit, preserving ordinary ARM64/4K.
    if sys.version_info<(3,11):
        import tomli;sys.modules['tomllib']=tomli
    from audit_enuma_kernel_baseline import inspect
    audit=inspect(image,native_prelink)
    segments=[s for s in native_prelink.macho(image)['segments'] if s['size'] and s['name']!='__PAGEZERO']
    span=max(s['va']+s['size'] for s in segments)-min(s['va'] for s in segments)
    report=dict(passed=True,scope='experimental same-donor prelink emission, not kernel/userland execution',
        roots=BASE+EXTRA,added_roots=EXTRA,components=details['components'],image_sha256=sha(image),image_bytes=len(image),
        virtual_span=span,source_kernel_sha256=sha(kernel),donor_sha256=sha(donor),slide=hex(chosen),rejected_slides=attempts,
        prelink_commit=pin,prelink_sources=sources,peer_commit=peer_lock['evaluation_commit'],peer_recipe_sha256=sha(recipe.read_bytes()),
        entry_audit=audit,hardware_executed=False,runtime_qualified=False,
        remaining=['IOKit-linked enuma UFS and stream ownership','PMGR ABI/service integration',
                   'OS/SystemOS root volumes and disposable Data seed','framebuffer/IOSurface presentation',
                   'NT36523 HID integration','launchd and SpringBoard runtime evidence'])
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['passed','image_sha256','image_bytes','virtual_span','slide','runtime_qualified']}))
if __name__=='__main__':main()
