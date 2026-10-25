"""Exercise real native mask selector and Core terminal header with host adapters."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'out/native-mask-terminal';(out/'Library').mkdir(parents=True,exist_ok=True)
    adapter='''#pragma once
#ifndef ENUMA_HOST_TYPES
#define ENUMA_HOST_TYPES
#include <stdint.h>
#include <string.h>
typedef uintptr_t UINTN;typedef uint64_t UINT64;typedef uint8_t UINT8;
typedef uint64_t EFI_STATUS;typedef struct {uint64_t low,high;} EFI_GUID;
#define STATIC static
#define VOID void
#define CONST const
#define EFI_ERROR(s) (((uint64_t)(s)>>63)!=0)
static inline uint64_t ReadUnaligned64(const uint64_t *p){uint64_t v;memcpy(&v,p,8);return v;}
#endif
'''
    for n in ['BaseLib.h','ResetSystemLib.h','TimerLib.h']:(out/'Library'/n).write_text(adapter)
    h=ROOT/'firmware/diagnostics/EnumaDispatchDetailCheckpoint.h';lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
    cmd=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-pie','-no-pie',
         '-I'+str(out),'-I'+str(lib),'-DENUMA_DIAG_STAGE=13','-DENUMA_DIAG_DETAIL_POINT=16','-DENUMA_DIAG_DELAY_US=2000000',
         '-DENUMA_DIAG_DISPATCH_ORDINAL=3','-DENUMA_DIAG_GUID_ENABLED=1','-DENUMA_DIAG_GUID_ONLY=1',
         '-DENUMA_DIAG_GOP_QUERY=1','-DENUMA_VIDEO_TERMINAL=1','-DENUMA_DIAG_DISPATCH_FALLBACK=0','-DENUMA_NATIVE_MASK_FIELD=7',
         '-DENUMA_DIAG_GUID_LOW64=0x1122334455667788ULL','-DENUMA_DIAG_GUID_HIGH64=0x8877665544332211ULL',
         '-DDETAIL_HEADER="'+str(h)+'"',str(ROOT/'tests/native_mask_terminal.c'),'-o',str(out/'test')]
    subprocess.run(cmd,check=True);result=subprocess.check_output([str(out/'test')],text=True).strip()
    invalid=[]
    for flag,value in [('ENUMA_NATIVE_MASK_FIELD',8),('ENUMA_VIDEO_TERMINAL',0),('ENUMA_DIAG_GOP_QUERY',2),('ENUMA_DIAG_GUID_ONLY',0),('ENUMA_DIAG_DISPATCH_FALLBACK',1)]:
        bad=[('-D'+flag+'='+str(value)) if v.startswith('-D'+flag+'=') else v for v in cmd]
        p=subprocess.run(bad,capture_output=True,text=True)
        if p.returncode==0:raise ValueError('invalid selector accepted '+flag)
        invalid.append(flag)
    sources=[h,lib/'NativeMaskResult.h',ROOT/'tests/native_mask_terminal.c',Path(__file__)]
    report=dict(scope='real header/selector with sanitized host callbacks; no device execution',result=result,command=cmd,
                invalid_selectors_rejected=invalid,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                maximum_terminal_delay_us=22000000,display_mmio=False,pixel_access=False)
    (ROOT/'reports/enuma-native-mask-host.json').write_text(json.dumps(report,indent=2)+'\n');print(result)
if __name__=='__main__':main()
