"""Remove automatic lists only; retain compiler bytes/relocations for late init."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(objects,records,out,run):
    sys.path.insert(0,str(R/'experiments/native-ufs-reuse'))
    from late_object_contract import inspect,verify,REMOVED
    llvm=Path(subprocess.check_output(['brew','--prefix','llvm'],text=True).strip())/'bin/llvm-objcopy'
    replacement={};proof={}
    for name in ('NativeUfs','NativeRamBlock','NativeVirtioBlock'):
        original=next(p for p in objects if p.name==name+'.o')
        baseline=out/(name+'.baseline.o');late=original.parent/(name+'.late.o')
        run([llvm,'--strip-debug',original,baseline])
        before=baseline.read_bytes();sections,symbols=inspect(before)
        init='__GLOBAL__sub_I_'+name+'.cpp'
        assert init in symbols and symbols[init][0]&1
        removed=set(sections)&REMOVED
        assert '__DATA,__mod_init_func' in removed
        # Debug removal may not modify any runtime section or its relocations.
        raw_sections,_=inspect(original.read_bytes())
        assert {k:v for k,v in raw_sections.items() if not k.startswith('__DWARF,')}==sections
        run([llvm,*['--remove-section='+s for s in sorted(removed)],baseline,late])
        counts=verify(before,late.read_bytes(),removed,init)
        try:verify(before,before,removed,init)
        except ValueError:pass
        else:raise AssertionError('Automatic initializer accepted')
        replacement[original]=late
        proof[name]=dict(original_sha256=sha(original),late_sha256=sha(late),removed=sorted(removed),
                         unchanged_runtime_sections=counts[0],unchanged_relocations=counts[1],automatic_list_negative_rejected=True)
    record=next(x for x in records['records'] if x['source'].endswith('/NativeUfs.cpp'))
    source=R/'ci/native-ufs-inputs/driver/EnumaStorageLateInit.cpp'
    wrapper=objects[0].parent/'EnumaStorageLateInit.o'
    command=record['command'][:]
    command=[str(source) if x==record['source'] else x for x in command]
    command[command.index('-o')+1]=str(wrapper)
    command+=['-Werror']
    captured=R/'out/ci-single-crypto-41016592491/driver-inputs'
    manifest=json.loads((captured/'manifest.json').read_text())
    cpp=next(x for x in manifest['compile_records'] if x['source_file'].endswith('.cpp'))
    cwd=captured/'tree'/cpp['directory_relative']
    # The captured bundle contains no libsa export directory. Drop only that
    # known absent search entry, preserving Werror and all real header inputs.
    absent=captured/'tree/build/xnu/ios-obj/EXPORT_HDRS/libsa'
    removed=[];filtered=[];i=0
    while i<len(command):
        arg=command[i]
        value=command[i+1] if arg=='-I' and i+1<len(command) else arg[2:] if arg.startswith('-I') else None
        if value is not None and (cwd/value).resolve()==absent.resolve() and not absent.exists():
            removed.append(value);i+=2 if arg=='-I' else 1;continue
        filtered.append(arg);i+=1
    command=filtered
    proof['removed_absent_capture_search_paths']=removed
    run(command,cwd)
    assert not set(inspect(wrapper.read_bytes())[0])&REMOVED
    proof['wrapper']=dict(source_sha256=sha(source),object_sha256=sha(wrapper),automatic_initializer=False)
    return [replacement.get(p,p) for p in objects]+[wrapper],proof
