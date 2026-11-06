"""Read-only source/link audit of UEFI text, diagnostics, DEBUG and menu paths."""
import hashlib,json,subprocess,sys
from pathlib import Path
if sys.version_info<(3,11):
    import tomli
    sys.modules['tomllib']=tomli
from audit_display_handoff import firmware_files
ROOT=Path(__file__).resolve().parents[1]
def main():
    firmware=ROOT/'firmware';stage=ROOT/'out/firmware-build/uefi'
    files=[firmware/'Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c',
      firmware/'Platforms/Xiaomi/enumaPkg/Include/PlatformConfig.inc',
      firmware/'Platforms/Xiaomi/enumaPkg/Include/DXE.inc',
      firmware/'Platforms/Xiaomi/enumaPkg/Include/UniXNU.dsc.inc',
      firmware/'Silicon/Silicium/SiliciumPkg/Library/BootManagerLib/BootManager.c',
      firmware/'Silicon/Silicium/SiliciumPkg/Include/Configuration/BootDevices.h',
      firmware/'Mu_Basecore/MdeModulePkg/Universal/BdsDxe/BdsEntry.c',
      firmware/'Mu_Basecore/MdeModulePkg/Universal/Console/GraphicsConsoleDxe/GraphicsConsole.c',
      stage/'Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/DarwinProbe.inc',
      ROOT/'out/sources/UniXNU/package/UniXNUPkg/Library/UniXNULib/Main.c',
      ROOT/'out/sources/UniXNU/package/UniXNUPkg/Library/UniXNULib/Ui.c',
      firmware/'Platforms/Xiaomi/enumaPkg/Library/InheritedGopLib/InheritedGop.c',
      firmware/'Mu_Basecore/MdeModulePkg/Library/FrameBufferBltLib/FrameBufferBltLib.c']
    sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    builds=stage/'Build/enumaPkg/DEBUG_CLANGPDB/AARCH64'
    build=json.loads((ROOT/'reports/enuma-firmware-build.json').read_text())
    fd=(ROOT/build['fd']).read_bytes()
    assert build['complete'] is True and hashlib.sha256(fd).hexdigest()==build['fd_sha256']
    modules=list(firmware_files(fd));packaged={}
    for name,relative in [('GraphicsConsoleDxe','MdeModulePkg/Universal/Console/GraphicsConsoleDxe'),
                          ('ConSplitterDxe','MdeModulePkg/Universal/Console/ConSplitterDxe'),
                          ('EnumaProbe','enumaPkg/Application/EnumaProbe'),
                          ('UniXNU','UniXNUPkg/Application/UniXNU')]:
        matching=[m for m in modules if m['name']==name]
        pe=builds/relative/name/'OUTPUT'/(name+'.efi')
        digest=hashlib.sha256(pe.read_bytes()).hexdigest()
        assert len(matching)==1 and hashlib.sha256(matching[0]['data']).hexdigest()==digest,name
        packaged[name]=dict(sha256=digest,actual_fd_equal=True)
    links={}
    library_lists=list(builds.rglob('static_library_files.lst'))
    for name in ['EnumaProbe','UniXNU','DxeCore','Sec','GraphicsConsoleDxe','ConSplitterDxe']:
        found=[p for p in library_lists if p.parent.parent.name==name or (name=='DxeCore' and p.parent.parent.name=='DxeMain')]
        links[name]=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
          null_serial='BaseSerialPortLibNull' in p.read_text(),framebuffer_serial='FrameBufferSerialPortLib' in p.read_text(),
          serial_debug='BaseDebugLibSerialPort' in p.read_text()) for p in found]
    report=dict(scope='source and actual generated static-link evidence only; no console connection, visual or boot execution proof',
      firmware_commit=subprocess.check_output(['git','-C',str(firmware),'rev-parse','HEAD'],text=True).strip(),
      unixnu_commit=subprocess.check_output(['git','-C',str(ROOT/'out/sources/UniXNU'),'rev-parse','HEAD'],text=True).strip(),
      sources=sources,links=links,
      fd_sha256=build['fd_sha256'],packaged_modules=packaged,
      paths={
       'graphics_console':'Packaged; BDS BeforeConsole registers ConOut/ErrOut device path, default-console connect precedes AfterConsole. GOP/device-path binding and text visibility need hardware qualification.',
       'print':'EnumaProbe Line calls UefiLib Print through ConOut, not global DEBUG; current bounded diagnostic does not reach BDS/application.',
       'diag_draw':'Generated hash-bound DarwinProbe.inc locates GOP then directly stores ff000000/ffffffff using Video stride; bypasses GOP Blt and assumes channel layout. Requires separate pixel/alpha/sync qualification before execution.',
       'debug':'PlatformConfig overrides SerialPortLib with Null. Source has serial DebugLib; actual generated lists report effective binding per module. GOP/ConOut alone does not reconnect DEBUG.',
       'menu':'EnumaProbe calls UniXNURun after payload checks. It connects controllers, loads config, injects drivers, initializes graphics/text UI then runs menu. Graphics UI uses GOP Blt, text fallback uses ConOut. Implemented but not reached by current diagnostic.',
       'early_log':'No verified early on-screen global logger/replay. SEC/early DXE precede valid GOP and ConsoleOut; need bounded RAM logging plus later safe replay, not early guessed pixel writes.',
       'opaque_fill':'Actual Mu VideoFill packs RGB masks only; caller Reserved=ff does not make stored alpha opaque. Existing backend SetMode clears all four bytes, so an opaque adapter must change the conversion path before RGBA admission.'},
      hardware_executed=False,pixel_access=False,device_action=False)
    assert links['EnumaProbe'] and all(x['null_serial'] and not x['framebuffer_serial'] for x in links['EnumaProbe'])
    (ROOT/'reports/enuma-console-path-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: bound console/menu source and actual module library lists; no hardware execution claimed')
if __name__=='__main__':main()
