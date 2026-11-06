"""Build a source-derived Data candidate only in the explicitly authorized CI job."""
import ctypes,hashlib,importlib.util,json,os,plistlib,re,stat,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
O=R/'out/data-seed-macos'
SOURCE=O/'source';TARGET=O/'target';IMAGE=O/'data.dmg';RAW=O/'data.cdr'
APPLE=R/'out/apple-owner-inputs/044-76040-038.dmg'
PROPOSAL=R/'reports/enuma-data-seed-macos-proposal.json'
HELPER_COMMANDS=[]
XATTR=None

def xattr_api():
    # Darwin declarations: apple-oss-distributions/xnu bsd/sys/xattr.h.
    # Never use XATTR_NOSECURITY; reads include compression metadata and do
    # not follow symlinks. Linux's os.*xattr API is absent in macOS Python.
    global XATTR
    if sys.platform!='darwin':raise ValueError('Darwin xattr API required')
    if XATTR is None:
        XATTR=ctypes.CDLL(None,use_errno=True)
        c=ctypes
        for name,args,result in [
            ('listxattr',[c.c_char_p,c.c_void_p,c.c_size_t,c.c_int],c.c_ssize_t),
            ('getxattr',[c.c_char_p,c.c_char_p,c.c_void_p,c.c_size_t,c.c_uint32,c.c_int],c.c_ssize_t),
            ('setxattr',[c.c_char_p,c.c_char_p,c.c_void_p,c.c_size_t,c.c_uint32,c.c_int],c.c_int),
            ('removexattr',[c.c_char_p,c.c_char_p,c.c_int],c.c_int)]:
            fn=getattr(XATTR,name);fn.argtypes=args;fn.restype=result
    return XATTR

def xattr_read(path,name=None):
    api=xattr_api();encoded=os.fsencode(path)
    def call(buffer,size):
        # XATTR_NOFOLLOW | XATTR_SHOWCOMPRESSION.
        n=api.listxattr(encoded,buffer,size,0x21) if name is None else api.getxattr(encoded,os.fsencode(name),buffer,size,0,0x21)
        if n<0:raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()),str(path))
        return n
    size=call(None,0)
    if size>64<<20:raise ValueError('Extended metadata exceeds bounded copy helper capacity')
    buf=ctypes.create_string_buffer(size)
    if call(buf,size)!=size:raise ValueError('Extended metadata changed during read')
    return buf.raw[:size]

def xattr_names(path):
    data=xattr_read(path)
    if not data:return []
    if not data.endswith(b'\0'):raise ValueError('Malformed Darwin xattr list')
    return [os.fsdecode(n) for n in data[:-1].split(b'\0')]

def xattr_set(path,name,value):
    buf=ctypes.create_string_buffer(value)
    if xattr_api().setxattr(os.fsencode(path),os.fsencode(name),buf,len(value),0,1)<0:
        raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()),str(path))

def xattr_remove(path,name):
    if xattr_api().removexattr(os.fsencode(path),os.fsencode(name),1)<0:
        raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()),str(path))

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()

def execute(args):
    p=subprocess.run(list(map(str,args)),capture_output=True,timeout=240)
    HELPER_COMMANDS.append(dict(argv=list(map(str,args)),exit_code=p.returncode,
        stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr=p.stderr.decode(errors='replace')))
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-4000:])
    return p.stdout

def image_mount(image,point,readonly=False):
    args=['/usr/bin/hdiutil','attach','-nobrowse','-owners','on','-mountpoint',point,'-plist']
    if readonly:args+=['-readonly']
    result=plistlib.loads(execute([*args,image]))
    matches=[e for e in result['system-entities'] if e.get('mount-point')==str(point)]
    if len(matches)!=1:raise ValueError('Ambiguous image mount')
    return matches[0]['dev-entry'],result['system-entities'][0]['dev-entry']

def acl(path):
    text=execute(['/bin/ls','-ledn',path]).decode()
    return [m.group(1) for line in text.splitlines() if (m:=re.match(r'^\s*\d+: (.*)$',line))]

def manifest(root,exclude=False):
    entries={};links={}
    def one(path):
        info=path.lstat();relative=path.relative_to(root).as_posix()
        item=dict(uid=info.st_uid,gid=info.st_gid,mode=stat.S_IMODE(info.st_mode),mtime_ns=info.st_mtime_ns,
                  flags=info.st_flags,acl=acl(path),xattrs={})
        for name in sorted(xattr_names(path)):
            item['xattrs'][name]=hashlib.sha256(xattr_read(path,name)).hexdigest()
        if stat.S_ISLNK(info.st_mode):item.update(type='symlink',target=os.readlink(path))
        elif stat.S_ISDIR(info.st_mode):item['type']='directory'
        elif stat.S_ISREG(info.st_mode):
            item.update(type='regular',bytes=info.st_size,sha256=sha(path))
            links.setdefault((info.st_dev,info.st_ino),[]).append(relative)
        else:raise ValueError('Unsupported source entry: '+relative)
        entries[relative]=item
    one(root)
    for current,dirs,files in os.walk(root,followlinks=False):
        if exclude and Path(current)==root:dirs[:]=[n for n in dirs if n!='staged_system_apps']
        for name in sorted(dirs+files):one(Path(current)/name)
    return dict(entries=entries,hardlinks=sorted(sorted(v) for v in links.values() if len(v)>1))

def validate_mounts():
    if sys.platform!='darwin' or os.geteuid()!=0:raise ValueError('Copy helper requires the authorized ephemeral macOS root context')
    if not json.loads(PROPOSAL.read_text())['approved']:raise ValueError('No Data authorization')
    if not os.environ.get('GITHUB_ACTIONS'):raise ValueError('Not an ephemeral CI job')
    for p in (SOURCE,TARGET):
        if p.is_symlink() or p.resolve()!=p or p.parent!=O:raise ValueError('Mount path drift')
        if p.stat().st_dev==O.stat().st_dev:raise ValueError('Not an image mount')
    if SOURCE.stat().st_dev==TARGET.stat().st_dev:raise ValueError('Same source/target device')
    if not os.statvfs(SOURCE).f_flag & os.ST_RDONLY:raise ValueError('Source is not read-only')
    mounted=plistlib.loads(execute(['/usr/bin/hdiutil','info','-plist']))['images']
    for image,point in ((APPLE,SOURCE),(IMAGE,TARGET)):
        matches=[x for x in mounted if Path(x.get('image-path','')).resolve()==image.resolve()
                 and any(e.get('mount-point')==str(point) for e in x.get('system-entities',[]))]
        if len(matches)!=1:raise ValueError('Image backing identity mismatch')

def copy_and_compare(copy):
    validate_mounts();source=SOURCE/'private/var'
    if source.is_symlink():raise ValueError('Unexpected var symlink')
    before=manifest(source,True)
    (O/('copy-source-manifest.json' if copy else 'readonly-source-manifest.json')).write_text(json.dumps(before,indent=2)+'\n')
    counts={k:sum(e['type']==k for e in before['entries'].values()) for k in ('directory','regular','symlink')}
    if counts!={'directory':166,'regular':39,'symlink':1}:raise ValueError('Source inventory differs from Enuma extraction')
    if copy:
        if os.statvfs(TARGET).f_flag & os.ST_RDONLY:raise ValueError('Target is read-only')
        if before['entries']['.']['acl']:raise ValueError('Root ACL needs an explicit preservation implementation')
        # ditto preserves metadata for each real top-level subtree; never follows
        # a fabricated source tree or copies the excluded staged application tree.
        for path in sorted(source.iterdir()):
            if path.name=='staged_system_apps':continue
            execute(['/usr/bin/ditto','--rsrc','--extattr','--acl',path,TARGET/path.name])
        # ditto recreates symlinks with a fresh mtime. Preserve the observed
        # link timestamp itself, never its possibly absolute target.
        for relative,entry in before['entries'].items():
            if entry['type']!='symlink':continue
            original=source/relative;copied=TARGET/relative
            if not copied.is_symlink() or os.readlink(copied)!=entry['target']:raise ValueError('Copied symlink identity mismatch')
            info=original.lstat()
            os.utime(copied,ns=(info.st_atime_ns,info.st_mtime_ns),follow_symlinks=False)
        info=source.lstat()
        os.chown(TARGET,info.st_uid,info.st_gid);os.chmod(TARGET,stat.S_IMODE(info.st_mode))
        if acl(TARGET):execute(['/bin/chmod','-N',TARGET])
        source_attrs=xattr_names(source)
        for name in xattr_names(TARGET):
            if name not in source_attrs:xattr_remove(TARGET,name)
        for name in source_attrs:
            xattr_set(TARGET,name,xattr_read(source,name))
        os.utime(TARGET,ns=(info.st_atime_ns,info.st_mtime_ns));os.chflags(TARGET,info.st_flags)
    after=manifest(TARGET)
    (O/('copy-observation.json' if copy else 'readonly-observation.json')).write_text(json.dumps(after,indent=2)+'\n')
    # APFS/host bookkeeping is disclosed separately; no arbitrary extra content
    # is accepted as an imported source entry.
    extras=[n for n in after['entries'] if n not in before['entries']]
    allowed={'.fseventsd','.Trashes','.Spotlight-V100','.TemporaryItems'}
    if any(n.split('/')[0] not in allowed for n in extras):raise ValueError('Unexpected target content')
    for name,entry in before['entries'].items():
        actual=after['entries'].get(name)
        if actual!=entry:raise ValueError('Source metadata/content mismatch: '+name)
    if before['hardlinks']!=after['hardlinks']:raise ValueError('Hardlink topology mismatch')
    result=dict(passed=True,counts=counts,source=before,target=after,host_bookkeeping_entries=extras,
                native_ios_mount_verified=False,production_seed_bound=False)
    (O/('copy-manifest.json' if copy else 'readonly-manifest.json')).write_text(json.dumps(result,indent=2)+'\n')

def preflight():
    if sys.platform!='darwin' or os.geteuid()==0 or not os.environ.get('GITHUB_ACTIONS'):raise ValueError('Preflight requires unprivileged macOS CI')
    if not json.loads(PROPOSAL.read_text())['approved']:raise ValueError('No Data authorization')
    O.mkdir(parents=True,exist_ok=False);SOURCE.mkdir();TARGET.mkdir()
    report=dict(passed=False);disk=None
    try:
        probe=O/'xattr-api-probe';probe.write_bytes(b'host-only metadata API check')
        link=O/'xattr-api-link';link.symlink_to(probe.name)
        original_time=probe.stat().st_mtime_ns;link_time=original_time-123456789
        os.utime(link,ns=(link_time,link_time),follow_symlinks=False)
        if link.lstat().st_mtime_ns!=link_time or probe.stat().st_mtime_ns!=original_time:raise ValueError('Symlink nanosecond no-follow timestamp check failed')
        report['symlink_timestamp_nofollow_nanoseconds']=True
        for value in (b'\0\xffenuma\0',b''):
            xattr_set(probe,'com.enuma.preflight',value)
            if xattr_read(probe,'com.enuma.preflight')!=value:raise ValueError('Binary xattr roundtrip failed')
            if 'com.enuma.preflight' not in xattr_names(probe):raise ValueError('xattr list mismatch')
            if 'com.enuma.preflight' in xattr_names(link):raise ValueError('xattr lookup followed symlink')
        xattr_remove(probe,'com.enuma.preflight')
        if 'com.enuma.preflight' in xattr_names(probe):raise ValueError('xattr removal failed')
        report['darwin_xattr_roundtrip_and_nofollow']=True
        for name,args in [('create-help',['/usr/bin/hdiutil','create','-help']),('filesystems',['/usr/sbin/diskutil','listFilesystems'])]:
            p=subprocess.run(args,capture_output=True)
            (O/(name+'.log')).write_bytes(p.stdout+p.stderr)
            report[name+'_exit_code']=p.returncode
        execute(['/usr/bin/hdiutil','create','-size','1g','-layout','NONE','-fs','Case-sensitive APFS','-volname','EnumaData','-type','UDIF',IMAGE])
        volume,disk=image_mount(IMAGE,TARGET)
        info=plistlib.loads(execute(['/usr/sbin/diskutil','info','-plist',volume]))
        report['volume_info']=info
        if info.get('FilesystemName')!='Case-sensitive APFS':raise ValueError('Case-sensitive APFS was not created')
        execute(['/usr/bin/hdiutil','detach',disk]);disk=None
        report['image_sha256']=sha(IMAGE);report['passed']=True
    finally:
        if disk:
            try:execute(['/usr/bin/hdiutil','detach',disk])
            except Exception as error:report['cleanup_error']=str(error);report['passed']=False
        report['commands']=HELPER_COMMANDS
        (O/'preflight.json').write_text(json.dumps(report,indent=2,default=str)+'\n')

def main():
    if sys.argv[1:]==['--preflight']:return preflight()
    if len(sys.argv)>1:
        if sys.argv[1] not in ('--copy-only','--verify-only'):raise ValueError('Unknown helper mode')
        try:copy_and_compare(sys.argv[1]=='--copy-only')
        finally:
            if O.is_dir():(O/(sys.argv[1][2:]+'-commands.json')).write_text(json.dumps(HELPER_COMMANDS,indent=2)+'\n')
        return
    if sys.platform!='darwin' or os.geteuid()==0 or not os.environ.get('GITHUB_ACTIONS'):raise ValueError('Controller must be an unprivileged macOS CI process')
    if not json.loads(PROPOSAL.read_text())['approved']:raise ValueError('No Data authorization')
    pre=json.loads((O/'preflight.json').read_text())
    if not pre['passed'] or sha(IMAGE)!=pre['image_sha256']:raise ValueError('Blank image preflight missing or changed')
    if (O/'result.json').exists():raise ValueError('Refusing to overwrite prior Data result')
    report=dict(passed=False,commands=[],merge_ready=False,deployment_enabled=False,production_seed_bound=False)
    attached=[]
    def run(args):
        p=subprocess.run(list(map(str,args)),capture_output=True,timeout=600)
        log=O/f'command-{len(report["commands"]):02}.log';log.write_bytes(p.stdout+p.stderr)
        report['commands'].append(dict(argv=list(map(str,args)),exit_code=p.returncode,log=log.name,sha256=sha(log)))
        p.check_returncode();return p.stdout
    try:
        if sha(APPLE)!='3f99b859c9728379110b66657c7b15285bcb1925ad8b5726542e2cdcf8b1028d':raise ValueError('Original OS component drift')
        report['source_component_sha256']=sha(APPLE)
        source_volume,source_disk=image_mount(APPLE,SOURCE,True);attached.append(source_disk)
        volume,disk=image_mount(IMAGE,TARGET);attached.append(disk)
        run(['/usr/bin/sudo','-n','/usr/bin/env','GITHUB_ACTIONS=true',sys.executable,__file__,'--copy-only'])
        run(['/usr/bin/hdiutil','detach',disk]);attached.remove(disk)
        volume,disk=image_mount(IMAGE,TARGET,True);attached.append(disk)
        report['volume_info']=plistlib.loads(run(['/usr/sbin/diskutil','info','-plist',volume]))
        run(['/usr/sbin/diskutil','verifyVolume',volume])
        run(['/usr/bin/sudo','-n','/usr/bin/env','GITHUB_ACTIONS=true',sys.executable,__file__,'--verify-only'])
        for device in reversed(attached[:]):run(['/usr/bin/hdiutil','detach',device]);attached.remove(device)
        run(['/usr/bin/hdiutil','convert',IMAGE,'-format','UDTO','-o',RAW])
        if RAW.stat().st_size!=1<<30:raise ValueError('Raw APFS geometry mismatch')
        with RAW.open('rb') as f:
            if f.read(36)[32:36]!=b'NXSB':raise ValueError('Not a raw APFS container')
        packer=R/'ci/native-ufs-inputs/driver/packed_ramdisk.py'
        spec=importlib.util.spec_from_file_location('packer',packer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        packed=O/'data.dbr';report['packed']=m.pack(RAW,packed)
        report['raw_sha256']=sha(RAW);report['packed_sha256']=sha(packed);report['packer_sha256']=sha(packer)
        if report['packed']['sha256']!=report['raw_sha256']:raise ValueError('Full packed readback mismatch')
        if sha(APPLE)!=report['source_component_sha256']:raise ValueError('OS input changed')
        report['passed']=True
    finally:
        for device in reversed(attached):
            try:run(['/usr/bin/hdiutil','detach',device])
            except Exception as error:report.setdefault('cleanup_errors',[]).append(str(error))
        report['mount_commands']=HELPER_COMMANDS
        if report.get('cleanup_errors'):report['passed']=False
        (O/'result.json').write_text(json.dumps(report,indent=2,default=str)+'\n')

if __name__=='__main__':main()
