"""Bind journal compiler input, actual Core PE/FD, and pinned source; no device."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
if sys.version_info < (3,11):
    import tomli
    sys.modules['tomllib'] = tomli
from audit_display_handoff import firmware_files

ROOT = Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    build=json.loads((ROOT/'reports/enuma-firmware-build.json').read_text())
    pin=json.loads((ROOT/'config/uefi-source.lock.json').read_text())
    assert build['complete'] and build['uefi_source_commit']==pin['commit']
    for name,want in pin['file_sha256'].items():
        assert sha(ROOT/'firmware'/name)==want,name
    fd=ROOT/build['fd']; assert sha(fd)==build['fd_sha256']
    module=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain'
    response=module/'OUTPUT/cc_resp.txt'
    assert '-DENUMA_BOOT_JOURNAL=1' in response.read_text().split()
    assert '-DENUMA_NATIVE_ROUTE_CPU_PATTERN=0' in response.read_text().split()
    assert '-DENUMA_NATIVE_ROUTE_CPU_TEXT=0' in response.read_text().split()
    assert '-DENUMA_RAM_PAYLOAD=0' in response.read_text().split()
    pe=module/'OUTPUT/DxeCore.efi'
    cores=[m for m in firmware_files(fd.read_bytes()) if m['name']=='DxeCore']
    assert len(cores)==1 and cores[0]['data']==pe.read_bytes()
    maps=list(module.glob('DEBUG/*.map'))
    assert len(maps)==1 and 'EnumaDxeBootLog' in maps[0].read_text()
    report=dict(scope='offline exact Core PE in FD, actual CC response, retained journal symbol and fixed inputs',
                firmware_commit=pin['commit'],fd_sha256=sha(fd),core_pe_sha256=sha(pe),
                core_in_fd_equal=True,actual_cc_response_sha256=sha(response),
                retained_journal_symbol=True,core_map_sha256=sha(maps[0]),
                boot_journal=build['boot_journal'],hardware_executed=False,
                global_debug_connected=False,screen_sink=False,hardware_candidate=False)
    (ROOT/'reports/enuma-boot-journal-artifact-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: actual Core C flag, retained journal symbol, exact Core PE in FD and source input hashes')
if __name__=='__main__': main()
