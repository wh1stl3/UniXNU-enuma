"""Isolated host/Arm tests of new attributed replay and EnumaProbe console path.

Never calls prepare(), firmware build, baseline restore, or device tooling.
Requires a new output directory under this checkout's out/.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from decode_dxe_journal import decode, inf_catalog

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    out.relative_to((ROOT/'out').resolve());out.mkdir(parents=True,exist_ok=False)
    commands=[];inputs={};passed=False
    def bind(path):
        inputs[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    def run(argv):
        r=subprocess.run(list(map(str,argv)),cwd=ROOT,text=True,capture_output=True)
        commands.append(dict(argv=list(map(str,argv)),returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        return r.stdout
    try:
        edk=ROOT/'firmware/Mu_Basecore/MdePkg/Include';diag=ROOT/'firmware/diagnostics'
        common=['clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-fshort-wchar','-I'+str(edk),'-I'+str(diag)]
        source=ROOT/'tests/journal_console_test.c';bind(source)
        bind(ROOT/'tests/test_decode_dxe_journal.py')
        for name in ['EnumaBootJournal.h','EnumaBootJournalProtocol.h','EnumaBootJournalView.h','EnumaJournalConsole.h','EnumaMenuConsole.h']:
            bind(diag/name)
        run(common+['-I'+str(edk/'X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',source,'-o',out/'console-test'])
        run([out/'console-test',out/'transcript.txt',out/'wrapped.txt'])
        menu_source=ROOT/'tests/menu_console_test.c';bind(menu_source)
        run(common+['-I'+str(edk/'X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',menu_source,'-o',out/'menu-test'])
        run([out/'menu-test'])
        for name in ['transcript.txt','wrapped.txt']:
            result=decode((out/name).read_text())
            (out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        assert decode((out/'transcript.txt').read_text())['unclosed_before_start']=={'11223344-5566-7788-99aa-bbccddeeff00':[5]}
        # Compile real application translation unit, both off/on and payload
        # branches, against pinned EDK headers and generated memory helpers.
        preflight=ROOT/'firmware/Resources/Scripts/enuma_preflight.py';bind(preflight)
        spec=importlib.util.spec_from_file_location('console_preflight',preflight)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        upstream=ROOT/'out/sources/UniXNU/drivers/DarwinBoot/DarwinBootPkg/Driver'
        darwin=upstream/'DarwinBoot.c';bind(darwin)
        interfaces=ROOT/'firmware/Resources/Enuma/interfaces.json';bind(interfaces)
        assert hashlib.sha256(darwin.read_bytes()).hexdigest()==json.loads(interfaces.read_text())['drivers/DarwinBoot/DarwinBootPkg/Driver/DarwinBoot.c']
        helpers=module.probe_memory_helpers(darwin.read_text())
        assert 'DiagDraw' not in helpers and 'Fb[' not in helpers and 'DiagFont' not in helpers
        (out/'DarwinProbe.inc').write_text(helpers)
        shutil.copyfile(upstream/'BootVideo.h',out/'BootVideo.h');bind(upstream/'BootVideo.h')
        app=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c';bind(app)
        shutil.copyfile(app,out/'EnumaProbe.c')
        inc=ROOT/'out/sources/UniXNU/package/UniXNUPkg/Include'
        arm=common+['-target','aarch64-none-elf','-ffreestanding','-fstack-usage','-O2','-I'+str(edk/'AArch64'),'-I'+str(inc),'-I'+str(out)]
        for replay in [0,1]:
            run(arm+['-DENUMA_RAM_PAYLOAD=0','-DENUMA_PROBE_JOURNAL_REPLAY='+str(replay),'-c',out/'EnumaProbe.c','-o',out/('probe-'+str(replay)+'.o')])
        # Compile the real RAM payload branch in a relative isolated layout.
        payload_dir=out/'Platforms/Xiaomi/enumaPkg/Drivers/EnumaRamPayloadDxe'
        payload_dir.mkdir(parents=True)
        report=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Drivers/EnumaRamPayloadDxe/TransportReport.h'
        shutil.copyfile(report,payload_dir/report.name);bind(report)
        app_dir=out/'Platforms/Xiaomi/enumaPkg/Application/EnumaProbe';app_dir.mkdir(parents=True)
        shutil.copyfile(app,app_dir/app.name)
        run(arm+['-DENUMA_RAM_PAYLOAD=1','-DENUMA_PROBE_JOURNAL_REPLAY=1','-c',app_dir/app.name,'-o',out/'probe-payload.o'])
        nm=shutil.which('llvm-nm') or shutil.which('nm')
        if not nm:raise RuntimeError('need llvm-nm or nm for object dependency check')
        for obj in ['probe-0.o','probe-1.o','probe-payload.o']:
            symbols=run([nm,'-u',out/obj])
            assert 'UniXNURun' in symbols
            assert 'WriteBackDataCacheRange' not in symbols and 'DiagDraw' not in symbols
        invalid=subprocess.run(arm+['-DENUMA_RAM_PAYLOAD=0','-DENUMA_PROBE_JOURNAL_REPLAY=2','-c',str(out/'EnumaProbe.c'),'-o',str(out/'invalid.o')],capture_output=True,text=True)
        assert invalid.returncode and 'Invalid late journal replay selector' in invalid.stderr
        commands.append(dict(case='invalid replay selector',rejected=True,stderr=invalid.stderr))
        run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_decode_dxe_journal.py','-v'])
        run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_cached_log_text.py','-v'])
        # Compatibility with the frozen ABI and pixel-page sources: compile
        # existing journal/8s transaction tests into this new directory only.
        lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
        shim=ROOT/'out/boot-journal-tests'
        host=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-Wno-unused-function',
              '-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(diag),'-I'+str(lib),'-I'+str(shim)]
        for filename,extra in [('boot_journal_test.c',[]),('native_log_replay.c',['-DENUMA_BOOT_LOG_HOLD_US=8000000','-DENUMA_EXPECT_HOLD_US=8000000'])]:
            test=ROOT/'tests'/filename;bind(test)
            run(host+extra+[test,'-o',out/(filename+'.test')])
            run([out/(filename+'.test')])
        for path in [shim/'Uefi.h',lib/'PixelTransaction.h',lib/'PixelLogPage.h']:
            bind(path)
        # Bind a real INF to a synthetic event using its actual canonical GUID.
        inf=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.inf';bind(inf)
        catalog=inf_catalog([inf]);guid=next(iter(catalog))
        synthetic=(out/'transcript.txt').read_text().replace('11223344-5566-7788-99aa-bbccddeeff00',guid)
        mapped=decode(synthetic,catalog)
        assert mapped['events'][0]['driver_source'][0]['name']=='EnumaProbe'
        (out/'synthetic-catalog.json').write_text(json.dumps(mapped,indent=2)+'\n')
        bind(Path(__file__));bind(ROOT/'scripts/decode_dxe_journal.py')
        stacks={p.name:p.read_text() for p in out.glob('*.su')}
        assert stacks and all(int(row.split('\t')[1])<131072 for text in stacks.values() for row in text.splitlines())
        passed=True
    except Exception as exc:
        commands.append(dict(error=str(exc)))
    finally:
        result=dict(passed=passed,scope='new source host ASan/UBSan and real EnumaProbe AArch64 objects; no link/FD/QEMU/device',
                    commands=commands,sources=inputs,stack_usage=locals().get('stacks',{}),
                    hardware_executed=False,screen_log_verified=False,gop_admitted=False,menu_executed=False,
                    frozen_r022_requalified=False)
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=passed,commands=len(commands),output=str(out))))
    return 0 if passed else 1


if __name__=='__main__':sys.exit(main())
