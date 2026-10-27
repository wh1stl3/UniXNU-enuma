"""Reject CRLF in new/edited firmware patches before expensive staging."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 fw=ROOT/'firmware'
 tracked=subprocess.check_output(['git','-C',str(fw),'diff','HEAD','--name-only','--','*.patch'],text=True).splitlines()
 added=subprocess.check_output(['git','-C',str(fw),'ls-files','--others','--exclude-standard','--','*.patch'],text=True).splitlines()
 checked=[]
 for name in sorted(set(tracked+added)):
  p=fw/name
  if not p.exists():continue
  b=p.read_bytes()
  if b'\r' in b or b.startswith(b'\xef\xbb\xbf'):raise ValueError('patch must be explicit UTF-8 LF without BOM: '+name)
  b.decode('utf-8')
  if not b.endswith(b'\n'):raise ValueError('patch final LF missing: '+name)
  checked.append(name)
 print('PASS: changed/new patches are UTF-8 LF: '+', '.join(checked))
 print('Next: git apply --check in isolated staging remains mandatory')
if __name__=='__main__':main()
