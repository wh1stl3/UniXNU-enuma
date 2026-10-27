"""Preserve real XNU driver compile inputs next to the kernel that used them.

Does not run captured commands, bundle SDKs, or manufacture missing headers.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil

HEADER_SUFFIXES={'.h','.hpp','.inc','.defs','.modulemap'}
PATH_FLAGS={'-I','-isystem','-iquote','-F','-iframework','-isysroot','--sysroot','-include','-imacros'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def export_inputs(source, destination, kernel, records, expected, sdk):
    source=Path(source).resolve();destination=Path(destination).resolve();sdk=Path(sdk).resolve()
    # Evidence output must not be a source subtree that the collector scans.
    if destination==source or source in destination.parents:
        raise ValueError('evidence must be outside source tree')
    if not sdk.is_dir():raise ValueError('SDK directory missing')
    destination.mkdir(parents=True,exist_ok=False)
    files={};captured=[];external=[];absent=[]
    def headers(directory, ancestors=()):
        real=directory.resolve(strict=True)
        if not real.is_relative_to(source) or real.is_relative_to(sdk):raise ValueError('include directory escapes source')
        if real in ancestors:raise ValueError('include directory cycle')
        for child in sorted(directory.iterdir()):
            if child.is_dir():yield from headers(child,(*ancestors,real))
            elif child.is_file() and (child.suffix in HEADER_SUFFIXES or child.name=='module.modulemap'):yield child
    def add(path):
        path=Path(os.path.abspath(path))
        resolved=path.resolve(strict=True)
        if not path.is_relative_to(source) or not resolved.is_relative_to(source):raise ValueError('source input escapes checkout: '+str(path))
        if resolved.is_relative_to(sdk):raise ValueError('SDK cannot be copied as source input')
        if not resolved.is_file():raise ValueError('expected regular input')
        rel=path.relative_to(source).as_posix()
        digest=sha(resolved)
        if rel not in files:
            target=destination/'tree'/rel;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(resolved,target)
            if sha(target)!=digest or sha(resolved)!=digest:raise ValueError('input changed while copying')
            files[rel]=digest
        return rel
    for relative in records:
        record_path=source/relative
        if sha(record_path)!=expected[relative]:raise ValueError('compile record differs from build report')
        record=json.loads(record_path.read_text().strip().rstrip(','))
        if not isinstance(record.get('arguments'),list) or not all(isinstance(v,str) for v in record['arguments']):
            raise ValueError('structured arguments required')
        cwd=Path(record['directory']).resolve(strict=True)
        if not cwd.is_relative_to(source):raise ValueError('compile directory outside source')
        def absolute(value):
            if not value or value.startswith('@'):raise ValueError('unsupported indirect path')
            p=Path(value);return p if p.is_absolute() else cwd/p
        add(absolute(record['file']));add(record_path)
        args=record['arguments'];paths=[];i=1
        while i<len(args):
            arg=args[i]
            if arg.startswith('@'):raise ValueError('response files need explicit input support')
            if arg.startswith(('-ivfsoverlay','-include-pch','-fmodule-map-file','-fmodule-file')):
                raise ValueError('indirect compiler inputs need explicit support')
            if arg in PATH_FLAGS:
                if i+1==len(args):raise ValueError('missing path argument')
                paths.append((arg,absolute(args[i+1])));i+=2;continue
            if arg.startswith('-I') and len(arg)>2:paths.append(('-I',absolute(arg[2:])))
            for prefix in ('-isystem','-iquote','-iframework','-isysroot','-include','-imacros','-F'):
                if arg.startswith(prefix) and len(arg)>len(prefix) and not arg.startswith(prefix+'='):
                    paths.append((prefix,absolute(arg[len(prefix):])))
            if arg.startswith(('-isystem=','--sysroot=')):paths.append((arg.split('=')[0],absolute(arg.split('=',1)[1])))
            i+=1
        for flag,path in paths:
            if not path.exists() and flag in {'-I','-isystem','-iquote','-F','-iframework'}:
                lexical=Path(os.path.abspath(path))
                if not lexical.is_relative_to(source) or not lexical.resolve().is_relative_to(source):
                    raise ValueError('absent include escapes source')
                if any(p.is_symlink() for p in (lexical,*lexical.parents)):
                    raise ValueError('absent include traverses symlink')
                absent.append(dict(flag=flag,path=lexical.relative_to(source).as_posix()))
                continue
            resolved=path.resolve(strict=True)
            if resolved.is_relative_to(sdk):
                external.append(dict(kind='SDK',flag=flag,path=str(path)));continue
            if not resolved.is_relative_to(source):raise ValueError('unclassified external include: '+str(path))
            if resolved.is_file():add(path)
            else:
                for file in headers(path):add(file)
        captured.append(dict(record=relative,directory_relative=cwd.relative_to(source).as_posix(),
                             source_file=str(absolute(record['file']).relative_to(source)),arguments=args))
    for relative,digest in files.items():
        if sha(source/relative)!=digest:raise ValueError('source changed during export')
    manifest=dict(schema=1,kernel_sha256=sha(kernel),source_root=str(source),sdk_root=str(sdk),
                  files=files,compile_records=captured,external_inputs=external,absent_include_paths=absent,
                  complete_without_sdk=False,private_storage_abi_qualified=False,
                  scope='captured real compile records and explicit source/generated include inputs; SDK/toolchain required separately')
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
