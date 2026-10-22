"""WSL host check of actual marker reader with mocked kernel APIs; no device."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'out/log-readback/reader-host';out.mkdir(parents=True,exist_ok=True)
    inputs=['diagnostics/enuma_log_reader.c','tests/log_reader_guard.c',
            'tests/log_reader_shim/linux/module.h','tests/log_reader_shim/linux/mm.h',
            'tests/log_reader_shim/asm/memory.h']
    command=['clang','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-no-pie',
             '-fsanitize=address,undefined','-fno-omit-frame-pointer',
             '-I',str(ROOT/'tests/log_reader_shim'),str(ROOT/'tests/log_reader_guard.c'),
             '-o',str(out/'guard')]
    subprocess.run(command,check=True)
    subprocess.run([str(out/'guard')],check=True)
    report={'scope':'host only, actual C source with kernel API mocks; not kernel ABI/runtime proof',
        'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in inputs},
        'sanitizers':['address','undefined'],
        'unreserved_page_positions_rejected':list(range(8)),
        'mapping_and_output_calls_on_rejection':0,'reserved_pages_required_before_mapping':8,
        'exact_marker_bytes':16,'source_bytes_unchanged':True,
        'hardware_loaded':False,'physical_memory_accessed':False}
    (ROOT/'reports/enuma-log-reader-host.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: actual reader rejects all 8 unreserved-page positions before mapping; exact 16-byte read leaves source unchanged (ASan/UBSan)')

if __name__=='__main__':main()
