"""Verify a complete isolated development FD and package a non-release Boot v3.

No hardware commands. Empty ramdisk is explicit: this is a stage10 build/link
artifact, not the R-022 full-payload trial or a physical menu candidate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); build=args.build.resolve();out=args.output.resolve()
    build.relative_to(ROOT/'out');out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    result={'passed':False,'scope':'development FD structure, actual compiler flags and Boot v3 roundtrip',
            'deployment_ready':False,'hardware_executed':False,'full_payload':False,'commands':[]}
    def run(argv):
        argv=list(map(str,argv));r=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True)
        result['commands'].append(dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        if r.returncode: raise ValueError(r.stdout+r.stderr)
        return r.stdout
    try:
        report=json.loads((build/'build-result.json').read_text())
        fd=ROOT/report['fd'];manifest=json.loads((build/'source-manifest.json').read_text())
        if report['complete'] is not True or report['deployment_ready'] is not False or sha(fd)!=report['fd_sha256']:
            raise ValueError('build is incomplete or FD mismatch')
        if sha(build/'source-manifest.json')!=report['source_manifest_sha256']:
            raise ValueError('source manifest changed')
        for name,wanted in manifest['snapshot_files'].items():
            if sha(build/'source'/name)!=wanted: raise ValueError('snapshot changed: '+name)
        run([sys.executable,'-B',ROOT/'scripts/audit_enuma_fd.py','--fd',fd,
             '--build-report',build/'build-result.json','--report',out/'fd-audit.json'])
        uefi=build/'work/uefi';core=build/'work/Mu_Basecore'
        products=uefi/'Build/enumaPkg/DEBUG_CLANGPDB/AARCH64'
        actual={}
        for name in ('DxeCore','EnumaProbe','BdsDxe','EnumaGopSelfTest','UniXNU','GraphicsConsoleDxe'):
            matches=list(products.rglob('OUTPUT/'+name+'.efi'))
            if len(matches)!=1: raise ValueError('missing/ambiguous PE '+name+': '+str(matches))
            pe=matches[0];response=pe.parent/'cc_resp.txt'
            flags=response.read_text().split()
            for flag in ('-DENUMA_DIAG_STAGE=10','-DENUMA_BOOT_JOURNAL=1'):
                # Global EDK build defines select DSC branches; only modules
                # explicitly using a C macro need the corresponding -D.
                if name=='DxeCore' and flag not in flags: raise ValueError('Core lacks '+flag)
            assembly=run(['llvm-objdump','-d',pe])
            (out/(name+'.disassembly.txt')).write_text(assembly)
            actual[name]={'pe_sha256':sha(pe),'cc_response_sha256':sha(response),
                          'pe':str(pe.relative_to(ROOT))}
        # Check that the real generated Probe dependency no longer contains
        # raw framebuffer rendering and that the new console helper is used.
        probe=uefi/'Platforms/Xiaomi/enumaPkg/Application/EnumaProbe'
        generated=(probe/'DarwinProbe.inc').read_text()
        if any(token in generated for token in ('DiagDraw','WriteBackDataCacheRange','Fb[')):
            raise ValueError('raw framebuffer renderer returned to generated Probe')
        probe_text=(probe/'EnumaProbe.c').read_text()
        snapshot_probe=(build/'source/Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c').read_text()
        console_writer=('EnumaConsoleSessionWriteLine' if 'EnumaConsoleSessionWriteLine' in snapshot_probe
                        else 'EnumaConsoleWriteLine')
        if console_writer not in probe_text:
            raise ValueError('attributed console source not staged')
        for name in ('EnumaBootJournalView.h','EnumaJournalConsole.h','EnumaMenuConsole.h'):
            if (probe/name).read_bytes()!=(build/'source/diagnostics'/name).read_bytes():
                raise ValueError('new console header missing from full build: '+name)
        library=list(products.rglob('InheritedGopLib/OUTPUT/InheritedGopLib.lib'))
        if len(library)!=1: raise ValueError('new GOP library archive missing')
        symbols=run(['llvm-nm',library[0]])
        for symbol in ('EnumaGopCreateWtOpaque','EnumaGopPublishWtOpaque','EnumaGopGetAccessState'):
            if symbol not in symbols: raise ValueError('new backend symbol absent: '+symbol)
        result['actual_modules']=actual;result['gop_library_sha256']=sha(library[0])
        result['wt_symbols_in_library']=True
        result['wt_physical_activation']=False
        if sys.version_info<(3,11):
            import tomli
            sys.modules['tomllib']=tomli
        sys.path.insert(0,str(ROOT/'out/sources/UniXNU/scripts'))
        from unixnu.bootimg import compile_shim
        shim=compile_shim(uefi,0x9fc00000,0x300000,True,out)
        raw=out/'enuma-development.raw';raw.write_bytes(shim+fd.read_bytes())
        empty=out/'empty-ramdisk';empty.write_bytes(b'')
        # Resolve the migrated AOSP location without editing the historical lock.
        lock=json.loads((ROOT/'config/porting-sources.lock.json').read_text())['aosp_mkbootimg']
        aosp=Path('/mnt/d/Code/PortingiOSLegacy/common/sources/aosp-mkbootimg')
        for name,wanted in lock['sha256'].items():
            if sha(aosp/name)!=wanted: raise ValueError('AOSP hash mismatch: '+name)
        image=out/'enuma-development-stage10.img'
        run([sys.executable,'-B',aosp/'mkbootimg.py','--header_version','3','--kernel',raw,
             '--ramdisk',empty,'--output',image])
        from package_enuma_boot import verify
        result['boot_v3']=verify(image.read_bytes(),raw.read_bytes(),b'')
        run([sys.executable,'-B',aosp/'unpack_bootimg.py','--boot_img',image,'--out',out/'unpacked'])
        if (out/'unpacked/kernel').read_bytes()!=raw.read_bytes(): raise ValueError('AOSP unpack mismatch')
        result.update(passed=True,fd_sha256=sha(fd),image_sha256=sha(image),image_bytes=image.stat().st_size,
                      image=str(image.relative_to(ROOT)),shim_bytes=len(shim),
                      source_manifest_sha256=sha(build/'source-manifest.json'),
                      limitation='stage10 stops before BDS; journal late replay defaults off; empty ramdisk; no physical menu admission',
                      qualifier_sha256=sha(Path(__file__)))
    except Exception as exc:
        result['error']=str(exc)
    finally:
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':result['passed'],'error':result.get('error'),'output':str(out)}))
    return 0 if result['passed'] else 1


if __name__=='__main__': sys.exit(main())
