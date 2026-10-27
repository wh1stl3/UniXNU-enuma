"""Off-device GOP publication/GraphicsConsole/real UniXNU Ui+Menu chain test.

Builds only a separate RAM-only EFI from explicit current sources, fixed prior
constructor/libraries, and pinned UniXNU source. Never uses firmware adapter,
baseline restore, flash, fastboot, adb, board memory, or original output paths.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import struct
import zlib
import re

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def frame_png(raw,width,height):
    stride=width*4+32
    if len(raw)!=stride*height:raise ValueError('frame size mismatch')
    rows=[]
    for y in range(height):
        row=raw[y*stride:(y+1)*stride]
        if row[width*4:]!=b'\xa5'*32:raise ValueError('frame padding changed')
        rgb=bytearray(width*3)
        rgb[0::3]=row[2:width*4:4];rgb[1::3]=row[1:width*4:4];rgb[2::3]=row[0:width*4:4]
        rows.append(b'\x00'+rgb)
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b'')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--application',type=Path,required=True)
    parser.add_argument('--wt-opaque',action='store_true',help='exercise new WT/opaque access mechanism on allocated VM RAM; not real WT mapping proof')
    parser.add_argument('--bounded-window',action='store_true',help='run the actual bounded menu adapter with VM-only physical callbacks')
    args=parser.parse_args();args.bounded_window=True;out=args.output.resolve();out.relative_to((ROOT/'out').resolve())
    out.mkdir(parents=True,exist_ok=False)
    commands=[];inputs={};passed=False;error=None
    def bind(p):inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
    def run(argv,timeout=45):
        p=subprocess.run(list(map(str,argv)),cwd=ROOT,text=True,capture_output=True,timeout=timeout)
        commands.append(dict(argv=list(map(str,argv)),returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        if p.returncode:raise RuntimeError(p.stdout+p.stderr)
        return p.stdout
    try:
        core=ROOT/'firmware/Mu_Basecore';inc=core/'MdePkg/Include';lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedGopLib'
        backend=lib/'InheritedGop.c';publish=lib/'InheritedGopPublish.c';blt=core/'MdeModulePkg/Library/FrameBufferBltLib/FrameBufferBltLib.c'
        bds=ROOT/'firmware/Silicon/Silicium/SiliciumPkg/Library/BootManagerLib'
        common=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-fno-builtin','-DMDEPKG_NDEBUG',
                '-I'+str(inc),'-I'+str(core/'MdeModulePkg/Include'),'-I'+str(lib),
                '-I'+str(ROOT/'firmware/Silicon/Silicium/SiliciumPkg/Include'),'-I'+str(ROOT/'firmware/diagnostics'),'-I'+str(bds),'-I'+str(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib')]
        host=common+['-I'+str(inc/'X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie']
        for name in ['menu_config_fs','menu_application_lifetime','deferred_menu_dispatch','deferred_menu_provider']:
            test=ROOT/('tests/'+name+'.c');bind(test)
            run(host+[test,'-o',out/name]);run([out/name])
        test=ROOT/'tests/gop_publication.c';bind(test)
        run(host+[test,backend,publish,blt,'-o',out/'publication-test'])
        run([out/'publication-test'])
        lookup=ROOT/'tests/console_gop_lookup.c';bind(lookup);bind(bds/'ConsoleGop.h');bind(bds/'BootManager.c')
        run(host+[lookup,'-o',out/'lookup-test']);run([out/'lookup-test'])
        upstream=ROOT/'out/sources/UniXNU/package/UniXNUPkg/Library/UniXNULib'
        upstream_repo=ROOT/'out/sources/UniXNU'
        expected_revision=json.loads((ROOT/'config/sources.lock.json').read_text())['sources']['UniXNU']['commit']
        if run(['git','-C',upstream_repo,'rev-parse','HEAD']).strip()!=expected_revision:raise ValueError('UniXNU revision differs from fixed source lock')
        for name in ['Ui.c','Menu.c','Font.c','Logo.c','Internal.h','LogoShape.h']:
            locked=subprocess.check_output(['git','-C',str(upstream_repo),'show',expected_revision+':package/UniXNUPkg/Library/UniXNULib/'+name])
            if (upstream/name).read_bytes()!=locked:raise ValueError('UniXNU source differs from fixed revision: '+name)
        module=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/enumaPkg/Application/EnumaGopSelfTest/EnumaGopSelfTest'
        autogen=module/'OUTPUT/AutoGen.obj';bind(autogen);bind(module/'DEBUG/AutoGen.h')
        # Prior absolute paths are read as historical references only. Resolve
        # only the exact old enuma prefix to its migrated checkout; never execute
        # commands from saved response files or pass old paths to any tool.
        libraries=[];library_list=module/'OUTPUT/static_library_files.lst';bind(library_list)
        for line in library_list.read_text().splitlines():
            relative=line.removeprefix('/mnt/d/Code/UniXNU-enuma/')
            if relative==line:raise ValueError('unexpected library reference: '+line)
            p=(ROOT/relative).resolve();p.relative_to(ROOT/'out/firmware-build')
            if p.name in ['EnumaGopSelfTest.lib','InheritedGopLib.lib','FrameBufferBltLib.lib']:continue
            if not p.is_file():raise FileNotFoundError(p)
            bind(p);libraries.append(p)
        sources=[ROOT/'tests/uefi_menu_chain.c',backend,publish,blt]+[upstream/name for name in ['Ui.c','Menu.c','Font.c','Logo.c']]
        if args.bounded_window:
            if args.wt_opaque:raise ValueError('bounded window has its own explicit callback profile')
            shutil.copyfile(upstream/'Internal.h',out/'UniXNUMenuInternal.h')
            (out/'InheritedVideo').symlink_to(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib',target_is_directory=True)
            app=args.application.resolve();app.relative_to(ROOT/'out');bind(app)
            (out/'AppImage.h').write_text('STATIC CONST UINT8 AppImage[]={'+','.join(str(b) for b in app.read_bytes())+'};\n')
            sources=[ROOT/'tests/uefi_deferred_menu.c',ROOT/'firmware/diagnostics/EnumaBoundedMenu.c',blt]+[upstream/name for name in ['Ui.c','Menu.c','Font.c','Logo.c']]
            bind(out/'UniXNUMenuInternal.h');bind(out/'InheritedVideo/MenuWindow.h');bind(out/'InheritedVideo/PixelTransaction.h')
        for p in sources+[lib/'InheritedGop.h',lib/'InheritedGopPublish.h',lib/'InheritedGopAccess.h',lib/'InheritedGopWtArm.h',lib/'OpaqueBlt.h',upstream/'Internal.h',upstream/'LogoShape.h']:
            bind(p)
        for name in ['EnumaDeferredMenu.h','EnumaDeferredMenuDispatch.h','EnumaDeferredMenuProvider.h','EnumaFullMenu.h','EnumaMenuApplication.h','EnumaMenuConfigFs.h','EnumaBootJournal.h','EnumaBootJournalProtocol.h','EnumaBootJournalView.h','EnumaJournalConsole.h','EnumaMenuConsole.h']:
            bind(ROOT/'firmware/diagnostics'/name)
        arm=common+['-target','aarch64-unknown-windows-msvc','-ffreestanding','-fno-stack-protector','-mno-stack-arg-probe','-mno-implicit-float',
                    '-Os','-Wno-unused-function','-Wno-unused-const-variable','-I'+str(inc/'AArch64'),
                    '-I'+str(ROOT/'out/sources/UniXNU/package/UniXNUPkg/Include'),'-I'+str(upstream),
                    '-I'+str(ROOT/'firmware/diagnostics'),'-include',module/'DEBUG/AutoGen.h']
        if args.wt_opaque:arm+=['-DENUMA_MENU_TEST_WT_OPAQUE=1']
        if args.bounded_window:arm+=['-I'+str(out),'-DENUMA_FULL_MENU=1','-DENUMA_DEFERRED_MENU=1']
        # Compile the actual changed BDS library source, with only include paths
        # resolved from its old response file; never execute saved command flags.
        bds_build=ROOT/'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/SiliciumPkg/Library/BootManagerLib/BootManagerLib'
        response=bds_build/'OUTPUT/cc_resp.txt';bind(response);bind(bds_build/'DEBUG/AutoGen.h')
        includes=[]
        for old in re.findall(r'-I([^\s]+)',response.read_text()):
            relative=old.removeprefix('/mnt/d/Code/UniXNU-enuma/')
            if relative==old:raise ValueError('unexpected BDS include reference')
            common_prefix='out/firmware-build/uefi/Common/Mu/'
            if relative.startswith(common_prefix):
                # Preserved generated Common/Mu symlink targets the old checkout.
                # Use its actual migrated fixed source; do not repair the link.
                current=ROOT/'firmware/Common/Mu'/relative.removeprefix(common_prefix)
            else:current=ROOT/relative
            includes.append('-I'+str(current))
        bds_flags=common+['-target','aarch64-unknown-windows-msvc','-ffreestanding','-fno-stack-protector','-mno-stack-arg-probe',
                          '-Os',*includes,'-include',bds_build/'DEBUG/AutoGen.h']
        run(bds_flags+['-c',bds/'BootManager.c','-o',out/'BootManager.obj'])
        objects=[]
        for p in sources:
            obj=out/(p.stem+'.obj');run(arm+['-c',p,'-o',obj]);objects.append(obj)
        efi=out/'MenuChain.efi'
        run(['lld-link','/nologo','/nodefaultlib','/entry:_ModuleEntryPoint','/subsystem:efi_application','/machine:arm64',
             '/dll','/base:0','/align:4096','/opt:ref','/opt:icf','/out:'+str(efi),'/map:'+str(out/'MenuChain.map'),
             *objects,autogen,*libraries])
        # Use a real disposable FAT image. QEMU's writable directory-backed
        # vvfat lost boundary clusters in earlier captures despite VM-side CRC.
        disk=out/'esp.img'
        with disk.open('wb') as stream:stream.truncate(64*1024*1024)
        run(['mformat','-i',disk,'-F','-v','MENUQEMU','::'])
        run(['mmd','-i',disk,'::/EFI','::/EFI/BOOT'])
        run(['mcopy','-i',disk,efi,'::/EFI/BOOT/BOOTAA64.EFI'])
        code=Path('/usr/share/AAVMF/AAVMF_CODE.fd');variables=Path('/usr/share/AAVMF/AAVMF_VARS.fd')
        bind(code);bind(variables);shutil.copyfile(variables,out/'vars.fd')
        cmd=['qemu-system-aarch64','-machine','virt','-cpu','max','-m','512','-nographic','-monitor','none','-net','none','-no-reboot',
             '-drive','if=pflash,format=raw,readonly=on,file='+str(code),'-drive','if=pflash,format=raw,file='+str(out/'vars.fd'),
             '-drive','if=none,format=raw,file='+str(disk)+',id=esp','-device','virtio-blk-device,drive=esp']
        serial=run(cmd,timeout=55);(out/'serial.log').write_text(serial)
        required=['ENUMA_MENU_CHAIN PASS QEMU RAM ONLY','CHAIN published RAM GOP 800x600','CHAIN published RAM GOP 768x1024',
                  'CHAIN GraphicsConsole and attributed ConOut replay accepted','no-input fallback selected default',
                  'CHAIN scripted selection/cancel/confirm and text fallback returned']
        if args.bounded_window:required=['ENUMA_FULL_MENU PASS QEMU RAM ONLY','CHAIN menu rendered 800x600','timeout 8000 ms, input no','starting as application','config: loaded','action: exit','DEFERRED actual driver return accepted before menu']
        if not all(s in serial for s in required) or 'ENUMA_MENU_CHAIN FAIL' in serial or 'ENUMA_BOUNDED_MENU FAIL' in serial or 'ENUMA_FULL_MENU FAIL' in serial:raise RuntimeError('incomplete chain: inspect serial.log')
        if args.wt_opaque and serial.count('CHAIN WT opaque reads=')!=2:raise RuntimeError('WT profile did not complete both geometries')
        if not args.bounded_window and serial.count('CHAIN graphics menu and scripted input accepted with ConOut NULL')!=2:raise RuntimeError('direct graphics menu still depends on ConOut')
        for geometry,w,h in ([('landscape',800,600)] if args.bounded_window else [('landscape',800,600),('portrait',768,1024)]):
            raw=out/('menu-'+geometry+'.bgra')
            run(['mcopy','-i',disk,'::/menu-'+geometry+'.bgra',raw]);bind(raw)
            expected=re.search(r'CHAIN menu rendered '+str(w)+'x'+str(h)+r' crc=([0-9A-Fa-f]+)',serial)
            if not expected or zlib.crc32(raw.read_bytes())!=int(expected[1],16):raise ValueError('frame CRC does not match VM observation')
            (out/('menu-'+geometry+'.png')).write_bytes(frame_png(raw.read_bytes(),w,h))
        bind(Path(__file__));passed=True
    except Exception as exc:
        error=str(exc)
        if isinstance(exc,subprocess.TimeoutExpired):
            (out/'serial-timeout.log').write_bytes(exc.stdout or b'')
    result=dict(passed=passed,error=error,scope=('full FV application + private readonly config + bounded GOP adapter on VM callback memory; no physical input' if args.bounded_window else 'off-device allocated RAM GOP + actual AAVMF GraphicsConsole + pinned real UniXNU Ui/Menu; scripted input fixture'),
                deferred_dispatch=True,full_application=True,bounded_window=args.bounded_window,access_profile='bounded-callback-fixture' if args.bounded_window else 'wt-opaque-software' if args.wt_opaque else 'mu-uncached-software',actual_wt_mapping_verified=False,
                commands=commands,inputs=inputs,qemu_efi_sha256=sha(out/'MenuChain.efi') if (out/'MenuChain.efi').exists() else None,
                enuma_device_action=False,physical_gop_verified=False,board_menu_verified=False,
                new_full_board_firmware_qualified=False,boot_entry_executed=False)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=passed,error=error,commands=len(commands),output=str(out))))
    return 0 if passed else 1


if __name__=='__main__':sys.exit(main())
