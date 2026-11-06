"""Host protection-page check of the actual read-only stage header; no device."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'out/ramoops-audit/canary-host'
    if not (out/'Base.h').is_file():raise ValueError('run test_ramoops_canary.py to prepare host-only shims')
    cmd=['clang','-std=c11','-D_GNU_SOURCE','-Wall','-Wextra','-Werror','-fsanitize=undefined',
         '-I',str(out),'-DENUMA_RAMOOPS_READ_HEADER=1','-DENUMA_DIAG_STAGE=10','-DENUMA_DIAG_DELAY_US=2000000',
         str(ROOT/'tests/ramoops_read_test.c'),'-o',str(out/'read-test')]
    subprocess.run(cmd,check=True)
    result=subprocess.check_output([str(out/'read-test')],text=True).strip()
    report=dict(scope='host virtual page protection only; not physical RAM access',command=cmd,result=result,
                sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
                  'firmware/diagnostics/EnumaRamoopsReadCheckpoint.h','tests/ramoops_read_test.c','scripts/test_ramoops_read.py']})
    (ROOT/'reports/enuma-ramoops-read-host.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result)
if __name__=='__main__':main()
