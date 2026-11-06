"""Sanitize the unbound dual-interface observer, no runtime MMIO or boot."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
    out=ROOT/'out/native-display-observe';out.mkdir(exist_ok=True)
    source=lib/'NativeObserve.c';test=ROOT/'tests/native_observe.c'
    common=['clang','-std=c11','-Wall','-Wextra','-Werror','-fno-builtin','-I'+str(lib)]
    host=[*common,'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',str(source),str(test),'-o',str(out/'test')]
    subprocess.run(host,check=True);result=subprocess.check_output([str(out/'test')],text=True).strip()
    arm=[*common,'-target','aarch64-none-elf','-ffreestanding','-O2','-c',str(source),'-o',str(out/'NativeObserve.o')]
    subprocess.run(arm,check=True)
    undef=subprocess.check_output(['llvm-nm','--undefined-only',str(out/'NativeObserve.o')],text=True)
    if undef.strip():raise ValueError('unexpected dependency '+undef)
    report=dict(scope='unbound pure callback observer; synthetic host inputs only',result=result,host_command=host,aarch64_command=arm,
      sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,lib/'NativeObserve.h',lib/'NativeMaskResult.h',test,Path(__file__)]},
      maximum_reads=26,maximum_waits=2,wait_us=100000,full_gop_predicate_unchanged=True,
      mmio_writes=False,pixel_access=False,hardware_executed=False,runtime_binding=False)
    (ROOT/'reports/enuma-native-display-observe-host.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result);print('PASS: AArch64 freestanding object, no undefined dependencies; not hardware qualification')
if __name__=='__main__':main()
