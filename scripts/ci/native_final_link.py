"""Full source-kernel link attempt with real native/provider objects, no fake policies."""
import hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path

R=Path(__file__).resolve().parents[2]
S=R/'out/ci/macos/UniXNU'; E=R/'out/native-final-link'
E.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(scope='native provider full source-kernel link attempt; not complete root integration',commands=[],deployment_enabled=False,merge_ready=False)
owner_probe=os.environ.get('ENUMA_OWNER_ROOT_PROBE','0')=='1'
report['owner_probe_requested']=owner_probe
def save(): (E/'result.json').write_text(json.dumps(report,indent=2)+'\n')
def run(args,cwd=S,env=None,required=True):
    log=E/f'command-{len(report["commands"]):02d}.log'
    with log.open('w') as stream:p=subprocess.run(list(map(str,args)),cwd=cwd,env=env,stdout=stream,stderr=subprocess.STDOUT)
    report['commands'].append(dict(argv=list(map(str,args)),cwd=str(cwd),exit_code=p.returncode,log=log.name,log_sha256=sha(log)));save()
    if p.returncode and required:raise RuntimeError(log.read_text()[-4000:])
    return p.returncode
try:
    sys.path.insert(0,str(S/'scripts'))
    from unixnu.kernel import toolchain_path
    initial=json.loads((R/'out/ci/macos/evidence/result.json').read_text())
    assert initial['platform_build_and_link_passed']
    report['baseline_kernel_sha256']=initial['platform_kernel_sha256']
    env=dict(os.environ,PATH=toolchain_path());env.update(initial['effective_platform_switches'])
    env.update(ENUMA_UFS_RUNTIME='0',ENUMA_SYSTEMOS_INIT='0',XNU_NATIVE_UFS='1',XNU_NATIVE_RAM_BLOCK='0',XNU_NATIVE_VIRTIO_BLOCK='0',JOBS='2')
    # RAM/Virtio objects are included for link/provider closure; their root
    # personalities are deliberately not claimed configured by this probe.
    report['switches']={k:v for k,v in env.items() if k.startswith(('XNU_','ENUMA_'))}
    from platform_archives import validate_storage_routes
    validate_storage_routes(env)
    native=R/'out/native-ufs-apple'
    records=json.loads((native/'result.json').read_text());assert records['apple_compiled']
    objects=[]
    for item in records['records']:
        source=Path(item['source']);assert sha(source)==item['source_sha256']
        obj=native/(source.stem+'.o');assert sha(obj)==item['object_sha256'];objects.append(obj)
    from native_late_init import prepare as prepare_late
    objects,report['late_registration_objects']=prepare_late(objects,records,E,run)
    # Real parent addresses from the independently audited Enuma donor, not
    # replacement parent implementations. Final prelink must bind this donor.
    contract_path=R/'config/enuma-native-donor-bindings.json'
    contract=json.loads(contract_path.read_text())
    parent_imports=set()
    for obj in objects:
        names=subprocess.check_output(['xcrun','nm','-u','-j',str(obj)],text=True).splitlines()
        parent_imports.update(n for n in names if 'IOBlockStorageDevice' in n)
    assert parent_imports==set(contract['bindings'])
    assert contract['abi_reference_object_sha256']==json.loads((R/'config/native-storage-abi.json').read_text())['reference_object_sha256']
    asm=E/'donor-bindings.S';bind=E/'donor-bindings.o'
    asm.write_text(''.join(f'.globl {name}\n.set {name}, {address}\n' for name,address in sorted(contract['bindings'].items())))
    run(['xcrun','clang','-target','arm64-apple-ios17.0','-c',asm,'-o',bind])
    objects.append(bind)
    report['donor_binding_contract']=dict(sha256=sha(contract_path),bindings=contract['bindings'],raw_donor_sha256=contract['raw_donor_sha256'],donor_slide=contract['donor_slide'],final_prelink_revalidation_required=True)
    report['boot_progress_undefined']=any('_boot_progress_poll' in subprocess.check_output(['xcrun','nm','-u','-j',str(obj)],text=True).splitlines() for obj in objects)
    assert not report['boot_progress_undefined']
    # Only accept byte-identical reconstructed genuine policies. No default
    # empty policy, fabricated key, or unsigned fallback satisfies this path.
    restored=R/'out/owner-policy-restored'
    if (restored/'result.json').exists():
        policy_contract_path=R/'ci/enuma-owner-root/contract.json'
        policy_contract=json.loads(policy_contract_path.read_text())
        restored_report=json.loads((restored/'result.json').read_text())
        assert restored_report['passed'] and restored_report['byte_identical_to_locally_signed_policies']
        assert restored_report['contract_sha256']==sha(policy_contract_path)
        assert sha(restored/'trusted-key.bin')==policy_contract['public_anchor_sha256']
        assert [p['name'] for p in policy_contract['windows']]==['OS','SystemOS']
        lines=['.section __TEXT,__const','.p2align 3']
        for i,entry in enumerate(policy_contract['windows']):
            manifest=restored/entry['name']/'manifest.bin'
            assert sha(manifest)==entry['manifest_sha256']
            if owner_probe and i==0:
                lines+=['.globl _verified_root_manifest','_verified_root_manifest:']
            lines += [f'policy_{i}:',f'.incbin "{manifest}"']
        lines += ['.globl _verified_root_key','_verified_root_key:',f'.incbin "{restored / "trusted-key.bin"}"','.p2align 3','.globl _verified_root_policy_count','_verified_root_policy_count: .quad 2','.section __DATA_CONST,__const','.p2align 3','.globl _verified_root_policies','_verified_root_policies:']
        for i,entry in enumerate(policy_contract['windows']):
            lines += [f'.quad policy_{i}',f'.quad {(restored/entry["name"]/"manifest.bin").stat().st_size}']
        if owner_probe:
            from owner_probe_inputs import prepare as prepare_probe
            probe_lines,report['real_owner_probe_inputs']=prepare_probe(R,E,restored/'OS/manifest.bin')
            lines+=probe_lines
        policy_asm=E/'owner-policies.S';policy_obj=E/'owner-policies.o'
        policy_asm.write_text('\n'.join(lines)+'\n')
        run(['xcrun','clang','-target','arm64-apple-ios17.0','-c',policy_asm,'-o',policy_obj])
        objects.append(policy_obj)
        report['owner_policy_contract_sha256']=sha(policy_contract_path)
    # Use this build's actual C command; do not synthesize a kernel ABI.
    objroot=S/'build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837'
    rec=json.loads((objroot/'bsd/DEVELOPMENT/bsd_init.o.json').read_text().strip().rstrip(','))
    report['removed_nonexistent_include_search_paths']=[]
    crypto_objects=[]
    crypto_sources=['kits/VerifiedRoot/src/verified_root.c','kits/VerifiedRoot/adapters/xnu_crypto.c']
    if owner_probe:crypto_sources.append('scripts/qemu-entry/verified-root-probe.c')
    for relative in crypto_sources:
        source=S/relative;obj=E/(source.stem+'.o');args=[];raw=rec['arguments'];i=0
        while i<len(raw):
            value=raw[i]
            if value in ('-MF','-MJ','-MT','-MQ'):i+=2;continue
            if value in ('-MD','-MMD','-MP'):i+=1;continue
            if value=='-o':args+=['-o',str(obj)];i+=2;continue
            if value in ('-I','-isystem','-iquote'):
                directory=Path(raw[i+1]);directory=directory if directory.is_absolute() else Path(rec['directory'])/directory
                if not directory.is_dir():
                    report['removed_nonexistent_include_search_paths'].append(str(directory));i+=2;continue
            if value.startswith('-I') and len(value)>2:
                directory=Path(value[2:]);directory=directory if directory.is_absolute() else Path(rec['directory'])/directory
                if not directory.is_dir():
                    report['removed_nonexistent_include_search_paths'].append(str(directory));i+=1;continue
            args.append(str(source) if value==rec['file'] else value);i+=1
        assert str(source) in args
        args+=['-I'+str(S/'kits/VerifiedRoot/include'),'-Werror']
        run(args,Path(rec['directory']));crypto_objects.append(obj)
    if owner_probe:
        # Keep the actual verified UFS bridge in the single NativeUfs archive.
        # This stage enables probe/audit, not the unresolved Virtio/AES trust gate.
        probe_archive=E/'libEnumaOwnerProbe.a'
        run(['xcrun','ar','rcs',probe_archive,*crypto_objects])
        env.update(XNU_VERIFIED_ROOT_PROBE='1',XNU_VERIFIED_ROOT_ARCHIVE=str(probe_archive),
            XNU_OWNER_ROOT_AUDIT='1',XNU_OWNER_ROOT_TRUST='0',XNU_OWNER_CACHE_MOUNT='0',
            XNU_OWNER_CACHE_STARTUP='0',XNU_OWNER_BOOT_MANIFEST='0',XNU_OWNER_UNION_SYSTEMOS='0',
            XNU_OWNER_DATA_MOUNT='0')
        report['owner_probe_archive_sha256']=sha(probe_archive)
        report['owner_crypto_sources']={s:sha(S/s) for s in crypto_sources}
        report['switches']={k:v for k,v in env.items() if k.startswith(('XNU_','ENUMA_'))}
    else:objects+=crypto_objects
    archive=S/'build/native-ufs/libNativeUfs.a';archive.parent.mkdir(parents=True,exist_ok=True)
    run(['xcrun','ar','rcs',archive,*objects])
    report['objects']={str(p):sha(p) for p in objects}
    # Reverse only the known personality patch in this generated build tree,
    # then apply its minimal single-root variant through the real recipe.
    patch=S/'patches/xnu/native-aes-personality.patch'
    assert sha(patch)=='02fe52c87a6bd801e602d03b54ce51de1362a2f2c6f75f5fc08122d3901aefff'
    work=S/'.cache/xnu-work';run(['git','apply','--reverse','--check',patch],work);run(['git','apply','--reverse',patch],work)
    text=patch.read_text()
    text,n=re.subn(r'^\+#if defined\(XNU_NATIVE_UFS\) && XNU_NATIVE_UFS\n.*?^\+#endif\n','',text,count=1,flags=re.M|re.S);assert n==1
    assert 'NativeUfs' not in text
    text,n=re.subn(r'(@@ -61,4 \+61,)48( @@)',r'\g<1>35\2',text);assert n==1
    patch.write_bytes(text.encode());run(['git','apply','--check',patch],work)
    report['single_root_patch_sha256']=sha(patch)
    late_patch=R/'patches/kernel/enuma-storage-late-init.patch'
    assert b'\r' not in late_patch.read_bytes()
    run(['git','apply','--check',late_patch],work)
    shutil.copyfile(late_patch,S/'patches/xnu/zzx-enuma-storage-late-init.patch')
    report['late_boot_caller_patch_sha256']=sha(late_patch)
    # Upstream defines XNU_NATIVE_UFS only for KernelConfigTables. The actual
    # BSD caller and error-propagation unit need their own explicit definition.
    recipe=S/'scripts/build-xnu-4k-baseline.sh'
    recipe_text=recipe.read_text()
    for unit in ('bsd_init.o','IOKitBSDInit.cpo'):
        prefix='EXTRA_MAKE_ARGS+=("'+unit+'_CFLAGS_ADD='
        assert recipe_text.count(prefix)==1,unit
        recipe_text=recipe_text.replace(prefix,prefix+'-DXNU_NATIVE_UFS=1 ')
    recipe.write_bytes(recipe_text.encode())
    report['late_caller_recipe_sha256']=sha(recipe)
    report['static_native_ufs_personalities']=0
    report['late_native_ufs_personalities']=1
    rc=run(['bash','scripts/build-xnu-4k-baseline.sh'],env=env,required=False)
    report['native_full_link_exit_code']=rc
    if rc:
        link_log=(E/report['commands'][-1]['log']).read_text()
        missing=re.findall(r'^  "([^"]+)", referenced from:',link_log,re.M)
        report['remaining_link_errors']=missing
        report['only_unbound_policy_symbols']=set(missing)=={'_verified_root_key','_verified_root_policies','_verified_root_policy_count'}
    report['provider_objects']={}
    for name in ('vm_kern.o','ubsan_minimal.o'):
        for p in objroot.rglob(name):
            symbols=subprocess.check_output(['xcrun','nm','-m',str(p)],text=True)
            report['provider_objects'][str(p)]=dict(sha256=sha(p),symbols=[s for s in symbols.splitlines() if any(x in s for x in ('kmem_alloc_guard','kmem_free_guard','ubsan_handle_','ubsan_minimal_init'))])
    kernel=objroot/'mach.development.bcm2837.unstripped.noctf'
    report['kernel_linked']=rc==0 and kernel.exists()
    if report['kernel_linked']:
        report['late_caller_compile_records']={}
        for unit in ('bsd_init.o','IOKitBSDInit.cpo'):
            candidates=list(objroot.rglob(unit+'.json'));assert len(candidates)==1,(unit,candidates)
            compiled=json.loads(candidates[0].read_text().strip().rstrip(','))
            options=compiled['arguments']
            report['late_caller_compile_records'][unit]=dict(sha256=sha(candidates[0]),arguments=options)
            save()
            from compile_defines import require_define
            require_define(options,'XNU_NATIVE_UFS',1)
            if owner_probe and unit=='bsd_init.o':
                for name,value in (('XNU_VERIFIED_ROOT_PROBE',1),('XNU_OWNER_ROOT_AUDIT',1),('XNU_OWNER_ROOT_TRUST',0)):
                    require_define(options,name,value)
        report['kernel_sha256']=sha(kernel)
        shutil.copyfile(kernel,E/'kernel.macho')
        assert sha(E/'kernel.macho')==report['kernel_sha256']
        symbols=subprocess.check_output(['xcrun','nm','-m',str(kernel)],text=True)
        report['kernel_storage_provider_symbols']=[s for s in symbols.splitlines() if any(x in s for x in ('kmem_alloc_guard','kmem_free_guard','ubsan_handle_','verified_root_','vr_open','vr_verify_block','vr_xnu_crypto','enuma_ufs_boot','enuma_storage_start','enuma_smmu_apply'))]
        assert not any(x in symbols for x in ('_enuma_ufs_boot\n','_enuma_storage_start\n'))
        if owner_probe:
            required=('_native_verified_root_probe',
                      '_native_verified_block_root_authorized','_native_verified_block_volume_device')
            report['owner_probe_symbols']={name:any(line.endswith(' '+name) and '(undefined)' not in line for line in symbols.splitlines()) for name in required}
            assert all(report['owner_probe_symbols'].values())
            report['data_consumer_enabled']=False
    report['root_consumers_complete']=False;save()
    if rc:raise RuntimeError('Native full source link failed; original log preserved')
finally:save()
