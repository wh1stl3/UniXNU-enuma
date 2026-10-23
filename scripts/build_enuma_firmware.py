"""Firmware-only wrapper around the pinned official UniXNU [firmware] backend.

Sources remain clean; outputs and writable Mu patch staging belong to out/.
The top-level example guard is preserved; this does not build an enuma kernel.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import uuid
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'out/firmware-build'
SOURCE = ROOT / 'firmware'


def diagnostic_guid_defines(value):
    if value is None:
        return {'ENUMA_DIAG_GUID_ENABLED':'0', 'ENUMA_DIAG_GUID_LOW64':'0', 'ENUMA_DIAG_GUID_HIGH64':'0'}
    data = uuid.UUID(value).bytes_le
    return {'ENUMA_DIAG_GUID_ENABLED':'1',
            'ENUMA_DIAG_GUID_LOW64':'0x'+data[:8][::-1].hex()+'ULL',
            'ENUMA_DIAG_GUID_HIGH64':'0x'+data[8:][::-1].hex()+'ULL'}


def source_helper():
    spec = importlib.util.spec_from_file_location('enuma_firmware_inputs', SOURCE / 'Resources/Scripts/enuma_preflight.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Keep the test API lazy: the CLI must check the source pin before executing
# any code from the firmware checkout.
def apply_patch_series(patches):
    return source_helper().apply_patch_series(patches)


def stage_archives(lock):
    WORK.mkdir(parents=True, exist_ok=True)
    for name, url in lock['archives'].items():
        if name == 'uefi-source.tar.gz': continue  # UEFI comes from the fixed source gitlink
        archive = WORK / name
        if not archive.exists():
            subprocess.run(['curl', '-fL', '--retry', '2', '--connect-timeout', '10', '--max-time', '90',
                            '-o', str(archive), url], check=True)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != lock['archive_sha256'][name]:
            raise ValueError('source archive hash mismatch: ' + name)
        root = WORK / ('uefi' if name == 'uefi-source.tar.gz' else 'Mu_Basecore')
        marker = root / '.enuma-archive-staged'
        if marker.exists(): continue
        with tarfile.open(archive) as source:
            members = source.getmembers(); prefix = members[0].name.split('/')[0] + '/'
            for item in members:
                if not item.isfile(): continue
                relative = item.name.removeprefix(prefix)
                if name == 'uefi-source.tar.gz' and not relative.startswith(('Silicon/', 'BootShim/', 'Resources/MuPatches/')) and relative not in ('.gitmodules', 'LICENSE'):
                    continue
                target = (root / relative).resolve()
                if not target.is_relative_to(root.resolve()): raise ValueError('archive path escapes staging')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.extractfile(item).read())
        marker.write_text(lock['archive_sha256'][name])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, default=SOURCE)
    parser.add_argument('--unixnu', type=Path, required=True)
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--stop-stage', type=int, choices=(0,3,4,5,6,7,8,9,10,11,12,13), default=0)
    parser.add_argument('--stop-delay', type=int, choices=(2,7), default=2)
    parser.add_argument('--dispatch-ordinal', type=int, default=1)
    parser.add_argument('--detail-point', type=int, choices=range(13,26), default=13)
    parser.add_argument('--dispatch-guid', help='optional complete file UUID filter for stage 13 detail gates')
    parser.add_argument('--diagnostic-without-ufs',action='store_true',help='GOP isolation only; default firmware retains OEM UFSDxe')
    args = parser.parse_args()
    if not 1 <= args.dispatch_ordinal <= 128: parser.error('--dispatch-ordinal must be 1..128')
    if args.detail_point == 23 and (args.dispatch_guid is not None or args.dispatch_ordinal != 1):
        parser.error('global exception point 23 has no driver GUID/ordinal attribution; omit GUID and use ordinal 1')
    if args.stop_stage != 13 and (args.detail_point != 13 or args.dispatch_guid is not None):
        parser.error('detail point and GUID filters require --stop-stage 13')
    try:
        guid_defines = diagnostic_guid_defines(args.dispatch_guid)
    except ValueError:
        parser.error('--dispatch-guid must be a valid UUID')
    if sys.version_info < (3,11):
        import tomli
        sys.modules['tomllib'] = tomli
    import tomllib
    pin = json.loads((ROOT / 'config/uefi-source.lock.json').read_text())
    def git(path, *argv):
        return subprocess.check_output(['git','-c','safe.directory='+path.as_posix(),'-C',str(path),*argv],text=True).strip()
    if git(SOURCE, 'rev-parse', 'HEAD') != pin['commit']:
        raise ValueError('uefi-enuma revision differs from the device lock')
    if git(SOURCE, 'status', '--porcelain', '--ignore-submodules=all'):
        raise ValueError('uefi-enuma source must be clean')
    for name, wanted in pin['file_sha256'].items():
        if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() != wanted:
            raise ValueError('uefi-enuma source hash mismatch: '+name)
    from upstream_source import qualify
    qualification = qualify(args.unixnu)
    lock = json.loads((ROOT/'config/firmware-build.lock.json').read_text())
    stage_archives(lock)
    uefi = WORK/'uefi'; core = WORK/'Mu_Basecore'
    # Export the actual fixed firmware checkout, never write patches into it.
    for relative in ('BootShim','Silicon','Resources/MuPatches'):
        shutil.copytree(SOURCE/relative, uefi/relative, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('.git','Build','__pycache__'))
    # The official backend reads the packaging profile before its preflight.
    for relative in ('Resources/Configs/enuma.toml','Resources/Scripts/mkbootimg.py'):
        target=uefi/relative; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(SOURCE/relative,target)
    # A Git metadata view lets the official backend read the source timestamp;
    # no checkout or submodule operation modifies the published source.
    if not (uefi/'.git').exists(): subprocess.run(['git','init','-q',str(uefi)],check=True)
    objects = Path(git(SOURCE, 'rev-parse', '--absolute-git-dir')) / 'objects'
    info = uefi/'.git/objects/info'; info.mkdir(parents=True,exist_ok=True)
    (info/'alternates').write_text(objects.as_posix()+'\n')
    subprocess.run(['git','-C',str(uefi),'update-ref','refs/heads/enuma-source',pin['commit']],check=True)
    subprocess.run(['git','-C',str(uefi),'symbolic-ref','HEAD','refs/heads/enuma-source'],check=True)
    for relative in ('BaseTools/Source/C/BrotliCompress/brotli', 'MdeModulePkg/Library/BrotliCustomDecompressLib/brotli',
                     'MdePkg/Library/BaseFdtLib/libfdt', 'MdePkg/Library/MipiSysTLib/mipisyst',
                     'SecurityPkg/DeviceSecurity/SpdmLib/libspdm'):
        target=core/relative
        if not target.exists() or not any(target.iterdir()):
            shutil.copytree(args.reference/'Mu_Basecore'/relative,target,dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('.git','unit_test','os_stub','doc','samples'))
    tree=WORK/'tree'; (tree/'scripts').mkdir(parents=True,exist_ok=True); (tree/'drivers').mkdir(exist_ok=True)
    for origin, link in ((args.unixnu/'package',tree/'package'),
                         (args.unixnu/'drivers/DarwinBoot',tree/'drivers/DarwinBoot')):
        if not link.exists(): link.symlink_to(origin.resolve(),target_is_directory=True)
        elif link.resolve()!=origin.resolve(): raise ValueError('Unexpected official tree link')
    shutil.copyfile(ROOT/'scripts/enuma_firmware_preflight.py',tree/'scripts/enuma_firmware_preflight.py')
    for field, value in {'DEVICE':ROOT,'SOURCE':SOURCE,'UEFI':uefi,'EDK2':core,
                         'UNIXNU':args.unixnu,'REFERENCE':args.reference,'VENDOR':ROOT/'out/firmware-vendor'}.items():
        os.environ['ENUMA_'+field]=str(value.resolve())
    wrappers=core/'BaseTools/BinWrappers/PosixLike'
    for path in wrappers.iterdir():
        if path.is_file(): path.chmod(path.stat().st_mode | 0o111)
    os.environ.update(PATH=str(wrappers)+os.pathsep+os.environ['PATH'],
        PYTHONPATH=str(core/'BaseTools/Source/Python'), PYTHON_COMMAND=sys.executable,
        CLANG_BIN=str(Path(shutil.which('clang')).parent)+'/', SOURCE_DATE_EPOCH='1792540800',
        PYTHONDONTWRITEBYTECODE='1')
    sys.path.insert(0,str(args.unixnu/'scripts'))
    from unixnu import firmware
    board=tomllib.loads((ROOT/'board.toml').read_text())
    assert board['board']['example'] is True
    board=copy.deepcopy(board)
    board['firmware']['defines'].update(ENUMA_DIAG_STAGE=str(args.stop_stage),
        ENUMA_DIAG_DELAY_US=str(args.stop_delay*1000000),ENUMA_DIAG_DISPATCH_ORDINAL=str(args.dispatch_ordinal),
        ENUMA_DIAG_DETAIL_POINT=str(args.detail_point),ENUMA_DIAG_DISABLE_UFS='1' if args.diagnostic_without_ufs else '0', **guid_defines)
    ctx=SimpleNamespace(board=board,args=SimpleNamespace(skip_preflight=False),tree=tree,
                        logs=WORK/'logs',work=WORK/'context',jobs=args.jobs)
    fd=uefi/board['firmware']['fd'].format(target='DEBUG')
    report={'scope':'firmware-only invocation of the official backend; no device boot or enuma kernel',
        'complete':False,'fd':str(fd.relative_to(ROOT)),'uefi_source_commit':pin['commit'],
        'official_backend_sha256':hashlib.sha256((args.unixnu/'scripts/unixnu/firmware.py').read_bytes()).hexdigest(),
        'unixnu_qualification':qualification,'firmware_configuration':board['firmware'],
        'diagnostic_stop_stage':args.stop_stage,'diagnostic_delay_seconds':args.stop_delay,
        'diagnostic_dispatch_ordinal':args.dispatch_ordinal,'archive_sha256':lock['archive_sha256'],
        'diagnostic_detail_point':args.detail_point,
        'diagnostic_dispatch_guid':str(uuid.UUID(args.dispatch_guid)) if args.dispatch_guid else None,
        'diagnostic_omitted_oem_modules':['UFSDxe'] if args.diagnostic_without_ufs else [],
        'reference_gitlinks':lock['reference_gitlinks'],'checks':[]}
    try:
        firmware.build(ctx,{},uefi,core)
        report['complete']=fd.is_file()
        report['fd_exists']=fd.is_file()
        if fd.is_file():report['fd_sha256']=hashlib.sha256(fd.read_bytes()).hexdigest()
        report['source_inputs_sha256']={
            'firmware/'+name:hashlib.sha256((SOURCE/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
            for name in pin['file_sha256'] if Path(name).suffix in ('.c','.h','.inf','.inc','.dsc','.fdf','.patch','.toml','.py','.json')}
        report['probe_upstream_sha256']=json.loads((ROOT/'reports/enuma-firmware-preflight.json').read_text())['probe_upstream_sha256']
        baseline=json.loads((SOURCE/'Resources/Enuma/reset.json').read_text())['diagnostic_baseline_lf_sha256']
        report['core_patch_reversion_checked']=all(hashlib.sha256((core/n).read_bytes()).hexdigest()==sha
            for n,sha in baseline.items() if n.startswith(('MdeModulePkg/','UefiCpuPkg/')))
        if not report['core_patch_reversion_checked']:raise ValueError('Official backend left core patches applied')
        report['checks']=[{'backend':'unixnu.firmware.build','exit_code':0,'log':str((ctx.logs/'firmware.log').relative_to(ROOT))}]
    except Exception as error:
        report['complete']=False;report['error']=str(error);raise
    finally:
        (ROOT/'reports/enuma-firmware-build.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: official firmware backend and patch reversion; FD '+report['fd_sha256'])


if __name__=='__main__':main()
