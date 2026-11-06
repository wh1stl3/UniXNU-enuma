"""Host sanitizer/formatter/decoder and AArch64 object qualification; no device."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path
from decode_oem_service_trace import decode
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
 commands=[];passed=False;error=None
 def run(argv):
  q=subprocess.run(list(map(str,argv)),cwd=ROOT,capture_output=True,text=True,timeout=60)
  commands.append(dict(argv=list(map(str,argv)),returncode=q.returncode,stdout=q.stdout,stderr=q.stderr))
  if q.returncode:raise ValueError(q.stdout+q.stderr)
  return q.stdout
 try:
  oem=ROOT/'out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi'
  if sha(oem)!='6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425':raise ValueError('OEM reference PE changed')
  inc=ROOT/'firmware/Mu_Basecore/MdePkg/Include'
  flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-fno-builtin','-DMDEPKG_NDEBUG','-I'+str(inc),'-I'+str(ROOT/'firmware/diagnostics')]
  run(flags+['-I'+str(inc/'X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',ROOT/'tests/oem_service_trace.c','-o',out/'host-test'])
  stdout=run([out/'host-test']);(out/'host.log').write_text(stdout)
  transcript='\n'.join(line for line in stdout.splitlines() if line.startswith(('OEM cached ','OEM seq=')))+'\n'
  decoded=decode(transcript)
  if decoded['pending_calls']!=[dict(call=3,entry_sequence=6,service='locate-protocol')]:raise ValueError('nested pending call lost')
  (out/'fixture-transcript.txt').write_text(transcript);(out/'decoded-fixture.json').write_text(json.dumps(decoded,indent=2)+'\n')
  run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_oem_service_trace.py'])
  run(flags+['-target','aarch64-unknown-windows-msvc','-ffreestanding','-fno-stack-protector','-mno-stack-arg-probe','-mno-implicit-float','-Os','-I'+str(inc/'AArch64'),'-c',ROOT/'tests/oem_service_trace_arm.c','-o',out/'trace-arm.obj'])
  assembly=run(['llvm-objdump','-dr',out/'trace-arm.obj']);(out/'trace-arm.disassembly.txt').write_text(assembly)
  for name,offset in [('EnumaTraceLocateProtocol',320),('EnumaTraceHandleProtocol',152),('EnumaTraceAllocatePool',64)]:
   body=assembly.split('<'+name+'>:',1)[1].split('\n\n',1)[0]
   if not re.search(r'ldr\s+x\d+, \[x\d+, #'+str(offset)+r'\]',body) or 'blr' not in body:raise ValueError('missing actual forwarded service in '+name)
   if not re.search(r'mov\s+x\d+, x30',body):raise ValueError('caller LR capture missing in '+name)
  passed=True
 except Exception as exc:error=str(exc)
 files=['firmware/diagnostics/EnumaOemTraceTarget.h','firmware/diagnostics/EnumaOemServiceTrace.h','firmware/diagnostics/EnumaOemServiceTraceView.h','firmware/diagnostics/EnumaBootJournalView.h','firmware/diagnostics/EnumaBootJournal.h','tests/oem_service_trace.c','tests/oem_service_trace_arm.c','tests/test_oem_service_trace.py','scripts/decode_oem_service_trace.py','scripts/check_oem_service_trace.py']
 files+=['out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi','out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.inf']
 report=dict(passed=passed,error=error,commands=commands,inputs={n:sha(ROOT/n) for n in files},hardware_executed=False,firmware_profile_activated=False,
  scope='three transparent Boot Services wrappers; real forwarding to host test doubles, not OEM PE execution; AArch64 object only',
  remaining=['exact OEM image binding and persistent private-system-table installation','observable bounded output/capture path before any hardware candidate','all nonwrapped calls including protocol methods/MMIO remain outside coverage'])
 (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=passed,error=error,commands=len(commands))));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
