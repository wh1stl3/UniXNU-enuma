"""Isolated attributed-page tests; never writes historical reports or calls devices."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import uuid
from check_cached_log_format import SHAPES
from decode_attributed_pixel_log import decode_lines

ROOT=Path(__file__).resolve().parents[1]
SHAPES={**SHAPES,'Q':(2,5,5,7,3),'G':(7,4,5,5,7)}


def inverse(grid):
    if len(grid)!=160 or any(len(s)!=320 or set(s)-{'0','1'} for s in grid):
        raise ValueError('not an exact 320x160 binary grid')
    rows=[]
    for r in range(5):
        text=''
        for c in range(20):
            allowed=('C' if c==0 else '0' if c==1 else 'd' if c==2 else 'O' if c==4 else '0123456789abcdef' if 5<=c<=12 else '+ ' if c==13 else ' ') if r==0 else (('S' if r==1 else 'Q') if c==0 else '0123456789abcdef' if c<=16 else ' ') if r<3 else ('G' if c==0 else str(r-3) if c==1 else '0123456789abcdef' if c<=17 else ' ')
            observed=[s[c*16:(c+1)*16] for s in grid[r*32:(r+1)*32]]
            candidates=[]
            for ch in allowed:
                expected=[]
                for y in range(32):
                    expected.append(''.join('1' if x<12 and y<20 and SHAPES[ch][y//4]&(1<<(2-x//4)) else '0' for x in range(16)))
                if observed==expected: candidates.append(ch)
            if len(candidates)!=1: raise ValueError('inexact cell, no guessed characters')
            text+=candidates[0]
        rows.append(text)
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    report=dict(passed=False,hardware_executed=False,commands=[])
    def run(cmd):
        r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,cwd=out)
        report['commands'].append(dict(argv=list(map(str,cmd)),returncode=r.returncode,stderr=r.stderr))
        if r.returncode: raise ValueError(r.stdout+r.stderr)
        return r.stdout
    try:
        lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib';diag=ROOT/'firmware/diagnostics'
        shim=ROOT/'out/boot-journal-tests';edk=ROOT/'firmware/Mu_Basecore/MdePkg/Include'
        common=['clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function','-I'+str(lib),'-I'+str(diag)]
        host=common+['-I'+str(shim),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie']
        for name in ('attributed_log_transaction','attributed_log_format','native_log_replay','native_pixel_transaction','native_pixel_text'):
            run(host+[ROOT/'tests'/(name+'.c'),'-o',out/name])
            result=run([out/name])
            if name!='attributed_log_format': report[name]=result.strip();continue
            lines=result.splitlines();assert len(lines)==194*166
            for n in range(194):
                case=lines[n*166:(n+1)*166];ordinal,status,sequence,guid_le=case[0].split()
                text=inverse(case[6:]);assert text==case[1:6]
                decoded=decode_lines(text)
                assert (decoded['ordinal_hex'],decoded['status_hex'],decoded['sequence_hex'],decoded['guid'])==(ordinal,status,sequence,str(uuid.UUID(bytes_le=bytes.fromhex(guid_le))))
            damaged=list(lines[6:166]);damaged[0]=('0' if damaged[0][0]=='1' else '1')+damaged[0][1:]
            try: inverse(damaged)
            except ValueError: pass
            else: raise AssertionError('damaged pixel accepted')
            for r in range(5):
                damaged=list(lines[1:6]);damaged[r]='?'+damaged[r][1:]
                try: decode_lines(damaged)
                except ValueError: pass
                else: raise AssertionError('obscured row accepted')
            # Portable SVG is a synthetic preview, never a photograph or hardware result.
            grid=lines[6:166];rects=[]
            for y in range(0,160,4):
                for x in range(0,320,4):
                    if grid[y][x]=='1': rects.append(f'<rect x="{64+x}" y="{96+y}" width="4" height="4"/>')
            (out/'synthetic-preview.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="480" height="320" viewBox="0 0 480 320"><rect width="480" height="320" fill="#222"/><rect x="64" y="96" width="320" height="160" fill="black"/><g fill="white">'+''.join(rects)+'</g></svg>')
        includes=out/'InheritedVideo';includes.mkdir()
        for name in ('PixelTransaction.h','PixelText.h','PixelLogPage.h','PixelAttributedLogPage.h','Evidence.h','Topology.h','InheritedScanout.h'):
            shutil.copyfile(lib/name,includes/name)
        wrapper=out/'arm.c'
        wrapper.write_text('#include <Uefi.h>\n#include <Library/UefiBootServicesTableLib.h>\n#include "Evidence.h"\nstatic ENUMA_VIDEO_EVIDENCE mEvidence;\nextern int Read(void *,ENUMA_U32,ENUMA_U32 *);\nextern int Wait(void *,ENUMA_U32);\n#include "EnumaPixelTransactionArm.h"\nENUMA_U32 Probe(const ENUMA_INHERITED_FRAME *F,ENUMA_U32 P,ENUMA_U64 El,const ENUMA_BOOT_LOG *L) { if(!EnumaLogPageFromSnapshot(L,&mEnumaLogPage)) return 1;return PixelArmProbe(F,P,El); }\n')
        run(common+['-I'+str(out),'-I'+str(edk),'-I'+str(edk/'AArch64'),'-DENUMA_BOOT_LOG_REPLAY=2','-DENUMA_BOOT_LOG_HOLD_US=8000000','-target','aarch64-none-elf','-ffreestanding','-fshort-wchar','-fstack-usage','-O2','-c',wrapper,'-o',out/'arm.o'])
        stack=(out/'arm.su').read_text();assert max(int(s.split('\t')[1]) for s in stack.splitlines())<224*1024,stack
        (out/'arm.disassembly.txt').write_text(run(['llvm-objdump','-d',out/'arm.o']))
        sources=[Path(__file__),ROOT/'scripts/decode_attributed_pixel_log.py',ROOT/'scripts/check_cached_log_format.py']
        sources += [ROOT/'tests'/(n+'.c') for n in ('attributed_log_transaction','attributed_log_format','native_log_replay','native_pixel_transaction','native_pixel_text')]
        sources += [lib/n for n in ('PixelTransaction.h','PixelAttributedLogPage.h','PixelLogPage.h')]+[diag/n for n in ('EnumaPixelTransactionArm.h','EnumaBootJournal.h','EnumaBootJournalView.h')]
        report.update(passed=True,synthetic_pages=194,checked_pixels=194*320*160,status_bit_walk=64,guid_bit_walk=128,
                      arm_stack_usage=stack,stack_limit_bytes=262144,origin=[64,96],extent=[320,160],
                      reads_max=153600,writes_max=102400,barriers_max=3,hold_us=8000000,
                      limitations=['synthetic exact-grid inverse, not photograph OCR','stack frame bound is not a measured hardware stack high-water mark','physical corner clearance and timing remain untested'],
                      sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    except Exception as exc: report['error']=str(exc)
    finally: (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('passed','error','synthetic_pages','arm_stack_usage') if k in report}))
    return 0 if report['passed'] else 1


if __name__=='__main__': raise SystemExit(main())
