"""Verify a kernel-bound driver input directory and stage a relocatable copy.

Does not run compiler commands or make a private-ABI qualification claim.
The build report must be obtained with the matching kernel from the same run.
"""
import argparse
import hashlib
import json
import posixpath
from pathlib import Path, PurePosixPath
import shutil

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def relative(value):
    if not isinstance(value,str) or not value or '\\' in value or ':' in value:
        raise ValueError('invalid relative input path')
    p=PurePosixPath(value)
    if p.is_absolute() or any(part in ('..','.') for part in value.split('/')) or '' in value.split('/'):
        raise ValueError('input path is not canonical')
    return p

def checked_file(root,name):
    p=root/relative(name)
    if any(part.is_symlink() for part in [p,*p.parents] if part!=root and root in part.parents):
        raise ValueError('bundle must contain regular files, not links')
    if not p.resolve(strict=True).is_relative_to(root.resolve()) or not p.is_file():
        raise ValueError('input escapes bundle')
    return p

def mapped_path(value,cwd,source,sdk):
    if not value or value.startswith('@'):raise ValueError('indirect compiler path unsupported')
    path=PurePosixPath(posixpath.normpath(value if value.startswith('/') else cwd+'/'+value))
    for base,label in [(source,'${INPUTS}'),(sdk,'${SDK}')]:
        try:return label+'/'+path.relative_to(PurePosixPath(base)).as_posix()
        except ValueError:pass
    raise ValueError('unclassified compiler path '+value)

def relocate(record,source,sdk):
    """Data-only template. Output/dependency files cannot retain runner paths."""
    args=record['arguments'];cwd=record['directory'];result=['${CXX}'];i=1
    pair={'-I','-isystem','-iquote','-F','-iframework','-isysroot','--sysroot','-include','-imacros'}
    joined=('-isystem=','--sysroot=','-iframework','-isystem','-isysroot','-iquote','-include','-imacros','-I','-F')
    if not isinstance(args,list) or not args or not all(isinstance(a,str) for a in args):raise ValueError('bad compile arguments')
    while i<len(args):
        arg=args[i]
        if arg.startswith(('@','-ivfsoverlay','-include-pch','-fmodule-map-file','-fmodule-file','-fplugin','-specs')) or arg in ('-load','-plugin'):
            raise ValueError('unsupported indirect compiler input')
        if arg in ('-o','-MF','-MT','-MQ','-MJ'):
            if i+1>=len(args):raise ValueError('missing output argument')
            if arg=='-o':result.extend(['-o','${OUTPUT}'])
            i+=2;continue
        if arg in ('-MD','-MMD','-MP'):i+=1;continue
        if arg in ('-target','--target','-arch','-x','-std','-D','-U'):
            if i+1>=len(args):raise ValueError('missing compiler option value')
            result.extend([arg,args[i+1]]);i+=2;continue
        if arg in pair:
            if i+1>=len(args):raise ValueError('missing include argument')
            result.extend([arg,mapped_path(args[i+1],cwd,source,sdk)]);i+=2;continue
        prefix=next((p for p in joined if arg.startswith(p) and len(arg)>len(p)),None)
        if prefix:result.append(prefix+mapped_path(arg[len(prefix):],cwd,source,sdk))
        elif arg.startswith('-'):result.append(arg)
        else:result.append(mapped_path(arg,cwd,source,sdk))
        i+=1
    return dict(arguments=result,working_directory=mapped_path(cwd,cwd,source,sdk),
                executable=False,compiler_sdk_required=True,source_role='original compile record, not new driver startup')

def import_bundle(bundle,build_report,kernel,destination):
    bundle=Path(bundle).resolve();destination=Path(destination).resolve()
    if destination==bundle or destination.is_relative_to(bundle):raise ValueError('output inside input bundle')
    report_bytes=Path(build_report).read_bytes();report_hash=hashlib.sha256(report_bytes).hexdigest()
    report=json.loads(report_bytes);manifest_path=checked_file(bundle,'manifest.json')
    if report.get('status')!='passed' or report.get('platform_build_and_link_passed') is not True:
        raise ValueError('matching successful platform build required')
    if report.get('driver_input_manifest_sha256')!=sha(manifest_path):raise ValueError('manifest not bound to build report')
    m=json.loads(manifest_path.read_text())
    kernel_hash=sha(Path(kernel))
    if m.get('schema')!=1 or m.get('kernel_sha256')!=kernel_hash or report.get('platform_kernel_sha256')!=kernel_hash:
        raise ValueError('kernel/bundle identity mismatch')
    if m.get('private_storage_abi_qualified') is not False or m.get('complete_without_sdk') is not False:
        raise ValueError('bundle overstates qualification')
    files=m['files'];tree=bundle/'tree'
    if tree.is_symlink() or not tree.is_dir():raise ValueError('input tree must be a regular directory')
    if not isinstance(files,dict) or not files:raise ValueError('empty input package')
    for name,digest in files.items():
        if sha(checked_file(tree,name))!=digest:raise ValueError('input checksum mismatch: '+name)
    actual={p.relative_to(tree).as_posix() for p in tree.rglob('*') if p.is_file() or p.is_symlink()}
    if actual!=set(files):raise ValueError('unlisted files in input tree')
    templates=[];seen=set()
    for entry in m['compile_records']:
        name=entry['record'];relative(name)
        if name in seen:raise ValueError('duplicate compile record')
        seen.add(name)
        if name not in files or report.get('driver_compile_records',{}).get(name)!=files[name]:raise ValueError('compile record not bound to final kernel')
        record=json.loads(checked_file(tree,name).read_text().strip().rstrip(','))
        if record['arguments']!=entry['arguments']:raise ValueError('compile metadata differs')
        if not record['directory'].startswith('/') or not m['source_root'].startswith('/') or not m['sdk_root'].startswith('/'):
            raise ValueError('expected captured POSIX build paths')
        expected=mapped_path(record['directory'],record['directory'],m['source_root'],m['sdk_root'])
        if expected!='${INPUTS}/'+entry['directory_relative']:raise ValueError('compile directory differs')
        source=mapped_path(record['file'],record['directory'],m['source_root'],m['sdk_root'])
        if source!='${INPUTS}/'+entry['source_file'] or entry['source_file'] not in files:raise ValueError('source identity differs')
        templates.append(dict(record=name,**relocate(record,m['source_root'],m['sdk_root'])))
    if not templates or seen!=set(report['driver_compile_records']):raise ValueError('incomplete compile record set')
    destination.mkdir(parents=True,exist_ok=False)
    for name,digest in files.items():
        source=checked_file(tree,name);target=destination/'tree'/relative(name);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        if sha(source)!=digest or sha(target)!=digest:raise ValueError('input changed while importing')
    # Re-check provenance after the copy; no success record on races/failures.
    if sha(Path(build_report))!=report_hash or sha(manifest_path)!=report['driver_input_manifest_sha256'] or sha(Path(kernel))!=kernel_hash:raise ValueError('provenance changed')
    result=dict(passed=True,kernel_sha256=kernel_hash,build_report_sha256=sha(Path(build_report)),
        input_manifest_sha256=sha(manifest_path),files=files,templates=templates,
        commands_executed=False,private_abi_qualified=False,kernel_linked=False,
        scope='verified relocation inputs only; SDK, compiler, driver ABI and startup binding remain required')
    (destination/'result.json').write_text(json.dumps(result,indent=2)+'\n');return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','build-report','kernel','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.output.resolve().relative_to(ROOT/'out')
    r=import_bundle(a.bundle,a.build_report,a.kernel,a.output);print('PASS: '+str(len(r['files']))+' bound inputs; no compiler command executed')
if __name__=='__main__':main()
