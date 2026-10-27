"""Offline capture failure qualification and externally saved non-return test."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from decode_oem_precall_capture import decode_capture

ROOT = Path(__file__).resolve().parents[1]


def review_capture_assembly(asm):
    def body(name):
        return asm.split('<'+name+'>:', 1)[1].split('\n\n', 1)[0]
    for name, offset in [('EnumaTraceLocateProtocol',320), ('EnumaTraceHandleProtocol',152), ('EnumaTraceAllocatePool',64)]:
        code = body(name)
        before = code.index('IMAGE_REL_ARM64_BRANCH26\tEnumaServiceBegin')
        forwarded = re.search(r'ldr\s+x\d+, \[x\d+, #'+str(offset)+r'\]', code)
        if not forwarded or forwarded.start() <= before or 'blr' not in code[forwarded.end():]:
            raise ValueError('pre-forward ordering absent: '+name)
    code = body('EnumaServiceBegin')
    restore = re.search(r'ldr\s+x\d+, \[x\d+, #32\]', code)
    observer = re.search(r'ldr\s+x\d+, \[x\d+, #8752\]', code)
    if not restore or not observer or restore.start() >= observer.start() or 'blr' not in code[restore.end():observer.start()] or 'blr' not in code[observer.end():]:
        raise ValueError('RestoreTPL before observer not established')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.relative_to(ROOT / 'out')
    out.mkdir(parents=True, exist_ok=False)
    commands = []
    report = dict(passed=False, hardware_executed=False, board_sink_connected=False,
                  firmware_profile_activated=False, commands=commands)
    def run(argv):
        result = subprocess.run(list(map(str, argv)), cwd=ROOT, capture_output=True, text=True, timeout=60)
        commands.append(dict(argv=list(map(str, argv)), returncode=result.returncode,
                             stdout=result.stdout, stderr=result.stderr))
        if result.returncode:
            raise ValueError(result.stderr + result.stdout)
        return result.stdout
    try:
        inc = ROOT / 'firmware/Mu_Basecore/MdePkg/Include'
        flags = ['/usr/bin/clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fshort-wchar',
                 '-fno-builtin', '-DMDEPKG_NDEBUG', '-I'+str(inc),
                 '-I'+str(ROOT / 'firmware/diagnostics'),
                 '-I'+str(ROOT / 'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib')]
        for name in ('oem_precall_capture', 'oem_capture_pixel'):
            run(flags + ['-I'+str(inc/'X64'), '-O1', '-fsanitize=address,undefined', '-fno-pie', '-no-pie',
                         ROOT/'tests'/f'{name}.c', '-o', out/name])
            run([out/name])
            run(flags + ['-I'+str(inc/'AArch64'), '-target', 'aarch64-unknown-windows-msvc',
                         '-ffreestanding', '-fno-stack-protector', '-mno-stack-arg-probe', '-mno-implicit-float',
                         '-Os', '-c', ROOT/'tests'/f'{name}_arm.c', '-o', out/f'{name}.obj'])
            asm = run(['/usr/bin/llvm-objdump', '-dr', out/f'{name}.obj'])
            (out/f'{name}.disassembly.txt').write_text(asm)
            review_capture_assembly(asm)
            for removed in ('EnumaServiceBegin', '#8752', '#32]'):
                try:
                    review_capture_assembly(asm.replace(removed, 'DELETED'))
                except (ValueError, IndexError):
                    pass
                else:
                    raise ValueError('machine-code deletion not rejected: '+removed)
            if name == 'oem_capture_pixel':
                body = asm.split('<EnumaCapturePixelRun>:',1)[1].split('\n\n',1)[0]
                if not re.search(r'sub\s+sp, sp, #112\b', body):
                    raise ValueError('pixel stack frame changed; review required')
        # Producer flushes + fsyncs every line before entering a non-returning
        # original service. Parent proves evidence survives killing that process.
        path = out/'external-capture.txt'
        entered = out/'original-service-entered.txt'
        with (out/'producer.stdout').open('w') as stdout, (out/'producer.stderr').open('w') as stderr:
            producer = subprocess.Popen([str(out/'oem_precall_capture'), str(path), str(entered)], stdout=stdout, stderr=stderr)
            try:
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    if producer.poll() is not None:
                        raise ValueError('producer exited before non-return observation')
                    if path.exists() and entered.exists() and entered.read_text() == 'original-service-entered-after-export\n':
                        try:
                            decoded = decode_capture(path.read_text(), 0x123456789, 0)
                            break
                        except ValueError:
                            pass
                    time.sleep(.01)
                else:
                    raise ValueError('no complete external snapshot')
                time.sleep(.1)
                if producer.poll() is not None:
                    raise ValueError('producer did not remain active')
            finally:
                producer.kill()
                producer.wait(timeout=5)
        text = path.read_text()
        decoded = decode_capture(text, 0x123456789, 0)
        (out/'external-decoded.json').write_text(json.dumps(decoded, indent=2)+'\n')
        negative = 0
        mutations = [text[:i] for i in range(len(text))]
        mutations += [text[:i]+('1' if char != '1' else '2')+text[i+1:]
                      for i, char in enumerate(text)]
        mutations += [text+text, text.replace('selected=0000000000000000','selected=0000000000000001',1),
                      text.replace('session=0000000123456789','session=0000000123456788',1)]
        for damaged in mutations:
            try:
                decode_capture(damaged, 0x123456789, 0)
            except ValueError:
                negative += 1
            else:
                raise ValueError('incomplete or mismatched capture accepted')
        report.update(passed=True, truncated_or_mismatched_frames_rejected=negative,
                      original_service_entered_witness=True,
                      producer_terminated_after_export=True, external_snapshot_survived=True,
                      producer_returncode=producer.returncode,
                      aarch64_ordering_and_six_deletion_checks=True,
                      pixel_function_stack_frame_bytes=112,
                      external_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    except Exception as exc:
        report['error'] = str(exc)
    files = ['firmware/diagnostics/EnumaOemServiceTrace.h', 'firmware/diagnostics/EnumaOemPrecallCapture.h',
             'firmware/diagnostics/EnumaOemCapturePixel.h', 'scripts/check_oem_precall_capture.py',
             'scripts/decode_oem_precall_capture.py', 'scripts/decode_oem_service_trace.py']
    files += [f'tests/{name}{suffix}.c' for name in ('oem_precall_capture','oem_capture_pixel') for suffix in ('','_arm')]
    files += ['firmware/diagnostics/EnumaOemServiceTraceView.h', 'firmware/diagnostics/EnumaBootJournalView.h',
              'firmware/diagnostics/EnumaBootJournal.h']
    files += ['firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/'+name
              for name in ('PixelTransaction.h','PixelDiagnosticLogPage.h','Evidence.h')]
    report['inputs'] = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
    (out/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('commands','inputs')}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
