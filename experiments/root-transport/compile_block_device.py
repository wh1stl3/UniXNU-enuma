"""Compile real IOKit provider with captured headers; never synthesize declarations.

Local clang is a structural cross-compile audit, not the matching Apple build.
--apple-clang uses the original recorded flags and requires Apple clang 17.
"""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
p.add_argument('--apple-clang',type=Path);p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
package=root/'out/ci-single-crypto-41016592491/driver-inputs'
assert hashlib.sha256((package/'manifest.json').read_bytes()).hexdigest()=='f64302555534b0c049f6e56dc7bc3e381ceeddd72a1633e9afa4ae8a268a1a71'
manifest=json.loads((package/'manifest.json').read_text());tree=package/'tree'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in manifest['files'].items():assert sha(tree/path)==digest,path
storage=root/'out/storage-provider-20261030/IOStorageFamily'
assert subprocess.check_output(['git','-C',str(storage),'rev-parse','HEAD'],text=True).strip()=='0993ad6b36e85774fb0bc280e7d795f6dcbc641c'
headers=out/'include/IOKit/storage';headers.mkdir(parents=True)
for header in storage.glob('*.h'):
    assert header.read_bytes()==subprocess.check_output(['git','-C',str(storage),'show','HEAD:'+header.name])
    shutil.copyfile(header,headers/header.name)
record=next(r for r in manifest['compile_records'] if 'IOPlatformExpert' in r['source_file'])
old=manifest['source_root'];cwd=tree/record['directory_relative']
def translated(s):return s.replace(old,str(tree))
compiler=str(a.apple_clang or '/usr/bin/clang++')
version='prepare-only' if a.prepare_only else subprocess.check_output([compiler,'--version'],text=True)
if a.apple_clang:
    if not a.prepare_only:assert 'Apple clang version 17.0.0' in version,version
    args=[translated(s) for s in record['arguments'][1:]]
    args[args.index(translated(record['arguments'][record['arguments'].index('-xc++')+1]))]=str(here/'EnumaBlockDevice.cpp')
    args[args.index('-o')+1]=str(out/'EnumaBlockDevice.o')
else:
    # Preserve all recorded definitions/include search paths. Different compiler
    # code generation and vendor switches are explicitly NOT ABI qualification.
    args=['--target=arm64-apple-ios17.0','-std=gnu++2b','-fapple-kext','-mkernel',
          '-fno-exceptions','-fno-rtti','-fno-builtin','-nostdinc','-nostdinc++','-Werror','-O2']
    raw=record['arguments'];i=1
    while i<len(raw):
        s=raw[i]
        if s in ('-D','-U','-I','-isystem','-include','-iquote','-imacros'):
            args.extend([s,translated(raw[i+1])]);i+=2;continue
        if s.startswith(('-D','-U','-I')):args.append(translated(s))
        i+=1
    resource=subprocess.check_output([compiler,'-print-resource-dir'],text=True).strip()
    args+=['-isystem',resource+'/include','-c',str(here/'EnumaBlockDevice.cpp'),'-o',str(out/'EnumaBlockDevice.o')]
args[:0]=['-I'+str(out/'include'),'-I'+str(here),'-I'+str(root/'drivers/EnumaPlatform')]
if a.prepare_only:
    (out/'command.json').write_text(json.dumps(dict(command=[compiler,*args],cwd=str(cwd)),indent=2)+'\n')
    print('Prepared exact recorded-flag invocation; no compilation');raise SystemExit(0)
sdk_header=None
if a.apple_clang:
    sdk=Path(subprocess.check_output(['xcrun','--sdk','iphoneos','--show-sdk-path'],text=True).strip())
    assert subprocess.check_output(['xcrun','--sdk','iphoneos','--show-sdk-version'],text=True).strip()=='18.5'
    sdk_header=sdk/'usr/include/TargetConditionals.h'
    assert sdk_header.is_file()
    # Kernel headers remain first. Genuine SDK provides TargetConditionals;
    # never replace it with hand-written target macros or IOKitUser headers.
    args+=['-idirafter',str(sdk/'usr/include'),'-Xclang','-fdump-vtable-layouts']
bound=[Path(__file__),here/'EnumaBlockDevice.cpp',here/'EnumaBlockRequest.h',
    here/'EnumaStorageOwner.h',here/'EnumaLifecycle.h',here/'EnumaRootTransport.h',
    root/'drivers/EnumaPlatform/EnumaRootRead.h',root/'drivers/EnumaPlatform/EnumaUfsRead.h',
    package/'manifest.json',*headers.glob('*.h')]
bindings={str(f):sha(f) for f in bound}
if sdk_header:bound.append(sdk_header);bindings[str(sdk_header)]=sha(sdk_header)
result=subprocess.run([compiler,*args],cwd=cwd,capture_output=True,text=True)
assert bindings=={str(f):sha(f) for f in bound},'input changed during compilation'
(out/'stdout.txt').write_text(result.stdout);(out/'stderr.txt').write_text(result.stderr)
report=dict(compiler=version,command=[compiler,*args],cwd=str(cwd),returncode=result.returncode,
    apple_recorded_flags=bool(a.apple_clang),private_abi_qualified=False,kernel_linked=False,
    bindings=bindings)
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
print(result.stderr[-6000:]);result.check_returncode()
if a.apple_clang:
    symbols=subprocess.check_output(['xcrun','nm','-m',str(out/'EnumaBlockDevice.o')],text=True)
    (out/'symbols.txt').write_text(symbols)
    assert '_enuma_storage_publish_readonly' in symbols and 'EnumaBlockDevice' in symbols
    (out/'toolchain.txt').write_text(subprocess.check_output(['xcodebuild','-version'],text=True)+subprocess.check_output(['xcrun','--sdk','iphoneos','--show-sdk-version'],text=True))
print('PASS: actual IOKit/storage header compilation; donor ABI and runtime pending')
