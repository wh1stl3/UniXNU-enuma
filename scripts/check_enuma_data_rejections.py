"""Exercise CLI rejection before payload construction; preserve failure logs."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',required=True,type=Path)
    p.add_argument('--prelink',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
    fixture=out/'invalid-seed.bin';fixture.write_bytes(b'not a packed disk')
    cases=[('missing_hash',['--data-seed',str(fixture)],'supplied together'),
           ('missing_seed',['--data-seed-sha256','0'*64],'supplied together'),
           ('short_input',['--data-seed',str(fixture),'--data-seed-sha256',hashlib.sha256(fixture.read_bytes()).hexdigest()],'size outside bound')]
    wide=out/'invalid-wide.bin';wide.write_bytes(bytes(64))
    cases += [('wrong_hash',['--data-seed',str(wide),'--data-seed-sha256','0'*64],'digest mismatch'),
              ('bad_header',['--data-seed',str(wide),'--data-seed-sha256',hashlib.sha256(wide.read_bytes()).hexdigest()],'header mismatch')]
    results=[]
    for name,extra,error in cases:
        target=out/name
        command=[sys.executable,'-B',str(ROOT/'scripts/prepare_enuma_userland_payload.py'),
                 '--evidence-root',str(a.evidence_root),'--prelink',str(a.prelink),'--output',str(target),*extra]
        r=subprocess.run(command,capture_output=True,text=True,timeout=60)
        (out/(name+'.log')).write_text(r.stdout+r.stderr)
        if not r.returncode or error not in r.stderr or (target/'result.json').exists() or (target/'payload').exists():
            raise ValueError('failed rejection '+name)
        results.append(dict(case=name,returncode=r.returncode,expected_error=error,no_payload=True))
    (out/'result.json').write_text(json.dumps(dict(passed=True,cases=results,hardware_executed=False),indent=2)+'\n')
    print('PASS: 5 malformed/unbound Data CLI inputs rejected before payload build')
if __name__=='__main__':main()
