"""WSL: build against exact device headers and stock module symbol CRCs."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def sha(b):return hashlib.sha256(b).hexdigest()


def elf_sections(data):
    if data[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',data,18)[0]!=183:raise ValueError('not little-endian ARM64 ELF')
    off=struct.unpack_from('<Q',data,40)[0];entry,count,names=struct.unpack_from('<3H',data,58)
    if entry!=64 or off+entry*count>len(data) or names>=count:raise ValueError('invalid section table')
    sections=[struct.unpack_from('<IIQQQQIIQQ',data,off+i*entry) for i in range(count)]
    st=sections[names];strings=data[st[4]:st[4]+st[5]];result={}
    for s in sections:
        name=strings[s[0]:strings.index(0,s[0])].decode()
        if s[1]!=8 and s[4]+s[5]>len(data):raise ValueError('truncated ELF section')
        result[name]={'size':s[5],'data':data[s[4]:s[4]+s[5]] if s[1]!=8 else b''}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--read-marker',action='store_true')
    args=parser.parse_args();mode='marker' if args.read_marker else 'abi'
    out=ROOT/'out/log-readback'/('module-'+mode);out.mkdir(parents=True,exist_ok=True)
    headers=ROOT/'out/log-readback/kheaders-exact'
    header_tar=ROOT/'out/log-readback/kheaders.tar.xz'
    if sha(header_tar.read_bytes())!='e2482393e1d7ae0d2ec9c8155f940ae70317c907f54ef4f04f186f3c3db63c5c':raise ValueError('headers changed')
    # Compare every regular extracted header with the original archive, including
    # case-sensitive pairs; never silently reuse a Windows-collided extraction.
    import tarfile
    with tarfile.open(header_tar) as archive:
        for m in archive.getmembers():
            if m.isfile() and (headers/m.name).read_bytes()!=archive.extractfile(m).read():raise ValueError('header differs: '+m.name)
    versions={};sources=[];vermagic=None;layout=None
    for name in ('rdbg.ko','qca_cld3_qca6390.ko'):
        data=(ROOT/'out/log-readback'/name).read_bytes();sections=elf_sections(data)
        values=sections['__versions']['data']
        if len(values)%64:raise ValueError('unexpected symbol version stride')
        for pos in range(0,len(values),64):
            symbol=values[pos+8:pos+64].split(b'\0')[0].decode();crc=struct.unpack_from('<Q',values,pos)[0]
            if symbol in versions and versions[symbol]!=crc:raise ValueError('conflicting stock CRC')
            versions[symbol]=crc
        vm=next(v for v in sections['.modinfo']['data'].split(b'\0') if v.startswith(b'vermagic='))
        size=sections['.gnu.linkonce.this_module']['size']
        if vermagic not in (None,vm) or layout not in (None,size):raise ValueError('stock ABI differs')
        vermagic=vm;layout=size;sources.append({'name':name,'sha256':sha(data)})
    if vermagic!=b'vermagic=4.19.157-perf-gf8cf95f4dc15 SMP preempt mod_unload modversions aarch64' or layout!=832:
        raise ValueError('unreviewed stock kernel ABI')
    common=['clang','--target=aarch64-linux-gnu','-O2','-D__KERNEL__','-DMODULE','-DKBUILD_MODNAME="enuma_r002_'+mode+'"',
        '-include',str(headers/'include/linux/kconfig.h'),'-nostdinc','-isystem',
        subprocess.check_output(['clang','-print-resource-dir'],text=True).strip()+'/include',
        '-fno-pic','-fno-stack-protector','-fno-asynchronous-unwind-tables','-fno-unwind-tables',
        '-mgeneral-regs-only','-Wno-address-of-packed-member','-Wno-gnu-variable-sized-type-not-at-end']
    for name in ('arch/arm64/include','arch/arm64/include/generated','include',
                 'arch/arm64/include/uapi','arch/arm64/include/generated/uapi','include/uapi','include/generated/uapi'):
        common+=['-I',str(headers/name)]
    if args.read_marker:common+=['-DENUMA_READ_MARKER']
    source=ROOT/'diagnostics/enuma_log_reader.c'
    subprocess.run([*common,'-c',str(source),'-o',str(out/'reader.o')],check=True)
    undefined=subprocess.check_output(['llvm-nm','-u',str(out/'reader.o')],text=True)
    symbols=sorted(set(line.split()[-1] for line in undefined.splitlines())|{'module_layout'})
    missing=set(symbols)-versions.keys()
    if missing:raise ValueError('stock symbol CRC unavailable; do not force: '+','.join(sorted(missing)))
    metadata='''#include <linux/module.h>
#include <linux/vermagic.h>
MODULE_INFO(vermagic, VERMAGIC_STRING);
__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
 .name = KBUILD_MODNAME, .init = init_module, .exit = cleanup_module,
 .arch = MODULE_ARCH_INIT,
};
static const struct modversion_info versions[]
__used __attribute__((section("__versions"))) = {
'''+''.join('{0x%xUL,"%s"},\n'%(versions[s],s) for s in symbols)+'};\n'
    (out/'reader.mod.c').write_text(metadata)
    subprocess.run([*common,'-c',str(out/'reader.mod.c'),'-o',str(out/'reader.mod.o')],check=True)
    link=ROOT/'out/log-readback/module-link-source'
    pins=json.loads((link/'source.json').read_text())
    for path,info in pins.items():
        if sha((link/Path(path).name).read_bytes())!=info['sha256']:raise ValueError('link source changed')
    output=out/('enuma_r002_'+mode+'.ko')
    subprocess.run(['ld.lld','-r','-T',str(link/'module-common.lds'),'-T',str(link/'module.lds'),
        str(out/'reader.o'),str(out/'reader.mod.o'),'-o',str(output)],check=True)
    data=output.read_bytes();sections=elf_sections(data)
    if sections['.gnu.linkonce.this_module']['size']!=layout:raise ValueError('compiled module layout differs from stock')
    if vermagic not in sections['.modinfo']['data'].split(b'\0'):raise ValueError('compiled vermagic differs from stock')
    for name in ('.plt','.init.plt','.text.ftrace_trampoline'):
        if name not in sections:raise ValueError('missing real ARM64 module loader section')
    report={'scope':'offline compilation only; normal kernel loader checks still required','mode':mode,
        'module_sha256':sha(data),'module_bytes':len(data),'vermagic':vermagic.decode(),
        'module_struct_bytes':layout,'symbol_crcs':{s:hex(versions[s]) for s in symbols},
        'stock_module_sources':sources,'link_script_sources':pins,'source_sha256':sha(source.read_bytes()),
        'kernel_headers_sha256':sha(header_tar.read_bytes()),'physical_writes':False,
        'read_limit_bytes':16 if args.read_marker else 0,'hardware_loaded':False}
    output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: '+mode+' module, stock vermagic/layout and '+str(len(symbols))+' exact CRCs; not loaded')

if __name__=='__main__':main()
