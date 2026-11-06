"""Execute the real detail header with sanitized host timer/reset adapters."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from check_enuma_drivers import run
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--firmware-root',type=Path,default=ROOT/'firmware')
    args=parser.parse_args()
    header=(args.firmware_root/'diagnostics/EnumaDispatchDetailCheckpoint.h').resolve()
    out = ROOT/'out/dispatch-detail-test'
    (out/'Library').mkdir(parents=True, exist_ok=True)
    adapter = '''#pragma once
#ifndef ENUMA_HOST_TYPES
#define ENUMA_HOST_TYPES
#include <stdint.h>
#include <string.h>
typedef uintptr_t UINTN;
typedef uint64_t UINT64;
typedef uint8_t UINT8;
typedef uint64_t EFI_STATUS;
typedef void *EFI_HANDLE;
typedef struct { uint64_t low, high; } EFI_GUID;
typedef struct { EFI_GUID VendorGuid; void *VendorTable; } EFI_CONFIGURATION_TABLE;
typedef struct { UINTN NumberOfTableEntries; EFI_CONFIGURATION_TABLE *ConfigurationTable; } EFI_SYSTEM_TABLE;
#define STATIC static
#define VOID void
#define CONST const
#define EFI_ERROR(s) (((uint64_t)(s) >> 63) != 0)
static inline uint64_t ReadUnaligned64(const uint64_t *p) { uint64_t v; memcpy(&v,p,8); return v; }
#endif
'''
    for name in ('BaseLib.h','ResetSystemLib.h','TimerLib.h'):
        (out/'Library'/name).write_text(adapter)
    cases = [(13,point,status,1,0) for point in range(13,28) for status in (0,0x8000000000000001)]
    cases += [(13,15,0,1,guid) for guid in (1,2,3)]
    cases += [(13,15,0,0,3),(0,13,0,1,0),(12,13,0,1,0)]
    cases += [(13,point,0,1,guid) for point in (20,21,22,24,25) for guid in (1,2,3)]
    cases = [(*case,0) for case in cases]
    cases += [(13,point,status,1,guid,1) for point in (*range(13,23),24,25)
              for status in (0,0x8000000000000001) for guid in (0,1,2,3)]
    cases = [(*case,0) for case in cases]
    cases += [(13,point,status,1,0,1,query) for point in (16,17)
              for status in (0,0x8000000000000001) for query in (1,2)]
    cases += [(13,16,status,1,guid,1,query) for status in (1,5)
              for guid in (0,1,2,3) for query in (1,2)]
    cases += [(13,17,status,1,0,1,query) for status in (1,5) for query in (1,2)]
    cases += [(13,16,2,1,0,1,query) for query in (1,2)]
    cases = [(*case,0) for case in cases]
    cases += [(13,16,status,1,guid,1,1,1) for status in (0,1,2,5,0x8000000000000001) for guid in (0,1,2,3)]
    records=[]
    for index,(stage,point,status,enabled,guid,guid_only,query,terminal) in enumerate(cases):
        command=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror',
          '-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(out),
          '-DENUMA_DIAG_STAGE='+str(stage),'-DENUMA_DIAG_DETAIL_POINT='+str(point),
          '-DENUMA_DIAG_DELAY_US=2000000','-DENUMA_DIAG_DISPATCH_ORDINAL=3',
          '-DENUMA_DIAG_GUID_ENABLED='+str(enabled),
          '-DENUMA_DIAG_GUID_ONLY='+str(guid_only),
          '-DENUMA_DIAG_GOP_QUERY='+str(query),
          '-DENUMA_VIDEO_TERMINAL='+str(terminal),'-DENUMA_DIAG_DISPATCH_FALLBACK=0',
          '-DENUMA_DIAG_GUID_LOW64=0x1122334455667788ULL',
          '-DENUMA_DIAG_GUID_HIGH64=0x8877665544332211ULL',
          '-DTEST_GUID_CASE='+str(guid),'-DTEST_STATUS='+hex(status)+'ULL',
          '-DDETAIL_HEADER="'+str(header)+'"',
          '-DIMAGE_HEADER="'+str(header.with_name('EnumaImageEntryCheckpoint.h'))+'"',
          ROOT/'tests/enuma_dispatch_detail_gate.c','-o',out/('case-'+str(index))]
        records.append(run(command));records.append(run([command[-1]]))
    invalid=list(command)
    invalid[next(i for i,v in enumerate(invalid) if str(v).startswith('-DENUMA_DIAG_DETAIL_POINT='))]='-DENUMA_DIAG_DETAIL_POINT=28'
    result=subprocess.run([str(x) for x in invalid],capture_output=True,text=True)
    if result.returncode==0 or 'Unsupported enuma dispatch detail point' not in result.stderr:
        raise ValueError('invalid detail point accepted')
    invalid_selectors=[]
    for flag,value in (('ENUMA_DIAG_GUID_ENABLED',0),('ENUMA_DIAG_STAGE',12),('ENUMA_DIAG_GUID_ONLY',2),('ENUMA_DIAG_DETAIL_POINT',26)):
        invalid=list(command)
        invalid[next(i for i,v in enumerate(invalid) if str(v).startswith('-D'+flag+'='))]='-D'+flag+'='+str(value)
        result=subprocess.run([str(x) for x in invalid],capture_output=True,text=True)
        if result.returncode==0:raise ValueError('invalid GUID-only selection accepted: '+flag)
        invalid_selectors.append(flag)
    completion=(args.firmware_root/'diagnostics/EnumaDispatchCompletionCheckpoint.h').resolve()
    completion_checks=[]
    for fallback,stage,guid_only,enabled in ((0,0,0,0),(0,13,0,0),(1,13,1,1)):
        completion_command=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror',
            '-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(out),
            '-DENUMA_DIAG_STAGE='+str(stage),'-DENUMA_DIAG_DETAIL_POINT=20',
            '-DENUMA_DIAG_GUID_ONLY='+str(guid_only),'-DENUMA_DIAG_GUID_ENABLED='+str(enabled),
            '-DENUMA_DIAG_DISPATCH_FALLBACK='+str(fallback),
            '-DCOMPLETION_HEADER="'+str(completion)+'"',
            ROOT/'tests/enuma_dispatch_completion_gate.c','-o',out/'completion']
        completion_checks.append(run(completion_command));completion_checks.append(run([completion_command[-1]]))
    invalid_fallback=[]
    for flag,value in (('ENUMA_DIAG_STAGE',12),('ENUMA_DIAG_GUID_ONLY',0),('ENUMA_DIAG_GUID_ENABLED',0),('ENUMA_DIAG_DISPATCH_FALLBACK',2),('ENUMA_DIAG_DETAIL_POINT',23),('ENUMA_DIAG_DETAIL_POINT',27)):
        invalid=list(completion_command)
        invalid[next(i for i,v in enumerate(invalid) if str(v).startswith('-D'+flag+'='))]='-D'+flag+'='+str(value)
        result=subprocess.run([str(x) for x in invalid],capture_output=True,text=True)
        if result.returncode==0:raise ValueError('invalid completion fallback accepted: '+flag)
        invalid_fallback.append(flag)
    (ROOT/'reports/enuma-dispatch-details-host.json').write_text(json.dumps({
        'scope':'actual header with host adapters, no firmware/device execution',
        'source_header_sha256':hashlib.sha256(header.read_bytes()).hexdigest(),
        'image_bridge_sha256':hashlib.sha256(header.with_name('EnumaImageEntryCheckpoint.h').read_bytes()).hexdigest(),
        'cases':len(cases),'checks':records,'invalid_detail_rejected':True,
        'video_terminal_cases':20,'video_terminal_contract':'PASS1 and FAIL5 stop at same GUID-filtered return, delay2/7; unexpected statuses/hooks/NULL or mismatched GUID do not reset',
        'guid_only_checks':'all four actual ordinals; exact full GUID, both mismatching halves and NULL; status and nested handle checks retained',
        'invalid_guid_only_rejected':invalid_selectors,
        'completion_header_sha256':hashlib.sha256(completion.read_bytes()).hexdigest(),
        'completion_checks':completion_checks,'invalid_completion_rejected':invalid_fallback,
        'completion_limit':'only after initial CoreDispatcher returns; fixed seven seconds; no async watchdog or target-hit proof',
        'guid_checks':'both 64-bit halves, NULL, and disabled filter',
        'status_checks':'any/error/success returns for real LoadImage/StartImage hooks'},indent=2)+'\n')
    print('PASS: entry/return and read-only canary gates; separate global point23 and selection/guard checks')


if __name__=='__main__':main()
