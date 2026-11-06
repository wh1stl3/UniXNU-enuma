"""Offline regression of the isolated integration; never accesses a device."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]).resolve();out.relative_to(ROOT/'out');out.mkdir(parents=True,exist_ok=False)
commands=[]
def run(args):
 p=subprocess.run(list(map(str,args)),cwd=ROOT,capture_output=True,text=True,timeout=120)
 commands.append(dict(args=list(map(str,args)),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 (out/'commands.json').write_text(json.dumps(commands,indent=2))
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs=ROOT/'ci/native-ufs-inputs'
manifest=json.loads((inputs/'manifest.json').read_text())
assert manifest['deployment_enabled'] is False
for path,digest in manifest['files'].items():assert sha(inputs/path)==digest,path
run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_driver_input*.py','-v'])
flags=['-Wall','-Wextra','-Werror','-fno-pie','-no-pie','-fsanitize=address,undefined']
local=ROOT/'drivers/EnumaPlatform'
for unit,test in [('EnumaUfsSmmu','enuma_ufs_smmu'),('EnumaUfsRead','enuma_ufs_read')]:
 run(['/usr/bin/clang','-std=c11',*flags,'-I'+str(local),ROOT/'tests'/(test+'.c'),local/(unit+'.c'),'-o',out/test])
 run([out/test])
 run(['/usr/bin/clang','--target=aarch64-none-elf','-std=c11','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-O2','-c',local/(unit+'.c'),'-o',out/(unit+'.o')])
run(['/usr/bin/clang++','-std=c++17',*flags,ROOT/'experiments/root-transport/test_smmu_routes.cpp','-o',out/'routes'])
run([out/'routes'])
run(['/usr/bin/clang','--version'])
run([sys.executable,'--version'])
sources={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),*local.glob('EnumaUfs*.[ch]'),ROOT/'experiments/root-transport/test_smmu_routes.cpp',ROOT/'experiments/root-transport/EnumaSmmuRoutes.h',ROOT/'experiments/root-transport/EnumaSmmuInventory.h',ROOT/'tests/enuma_ufs_smmu.c',ROOT/'tests/enuma_ufs_read.c',ROOT/'tests/test_driver_inputs.py',ROOT/'tests/test_driver_input_import.py',ROOT/'scripts/ci/driver_inputs.py',ROOT/'scripts/import_enuma_driver_inputs.py']}
report=dict(passed=True,commands=len(commands),native_input_files_verified=len(manifest['files']),sources=sources,objects={p.name:sha(p) for p in out.glob('*.o')},scope='host synthetic MMIO/fault inputs and freestanding AArch64 compilation only',full_kernel_linked=False,donor_prelinked=False,hardware_executed=False,deployment_enabled=False)
(out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
