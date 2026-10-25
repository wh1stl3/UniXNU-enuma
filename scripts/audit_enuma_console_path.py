"""Read-only source/link audit of UEFI text, diagnostics, DEBUG and menu paths."""
import hashlib,json,subprocess
from pathlib import Path
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
      ROOT/'out/sources/UniXNU/package/UniXNUPkg/Library/UniXNULib/Ui.c']
    sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    builds=stage/'Build/enumaPkg/DEBUG_CLANGPDB/AARCH64'
    links={}
    for name in ['EnumaProbe','UniXNU','DxeCore','Sec','GraphicsConsoleDxe','ConSplitterDxe']:
        found=[p for p in builds.rglob('static_library_files.lst') if p.parent.parent.name==name or (name=='DxeCore' and p.parent.parent.name=='DxeMain')]
        links[name]=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
          null_serial='BaseSerialPortLibNull' in p.read_text(),framebuffer_serial='FrameBufferSerialPortLib' in p.read_text(),
          serial_debug='BaseDebugLibSerialPort' in p.read_text()) for p in found]
    report=dict(scope='source and actual generated static-link evidence only; no console connection, visual or boot execution proof',
      firmware_commit=subprocess.check_output(['git','-C',str(firmware),'rev-parse','HEAD'],text=True).strip(),
      unixnu_commit=subprocess.check_output(['git','-C',str(ROOT/'out/sources/UniXNU'),'rev-parse','HEAD'],text=True).strip(),
      sources=sources,links=links,
      paths={
       'graphics_console':'Packaged; BDS BeforeConsole registers ConOut/ErrOut device path, default-console connect precedes AfterConsole. GOP/device-path binding and text visibility need hardware qualification.',
       'print':'EnumaProbe Line calls UefiLib Print through ConOut, not global DEBUG; current bounded diagnostic does not reach BDS/application.',
       'diag_draw':'Generated hash-bound DarwinProbe.inc locates GOP then directly stores ff000000/ffffffff using Video stride; bypasses GOP Blt and assumes channel layout. Requires separate pixel/alpha/sync qualification before execution.',
       'debug':'PlatformConfig overrides SerialPortLib with Null. Source has serial DebugLib; actual generated lists report effective binding per module. GOP/ConOut alone does not reconnect DEBUG.',
       'menu':'EnumaProbe calls UniXNURun after payload checks. It connects controllers, loads config, injects drivers, initializes graphics/text UI then runs menu. Graphics UI uses GOP Blt, text fallback uses ConOut. Implemented but not reached by current diagnostic.',
       'early_log':'No verified early on-screen global logger/replay. SEC/early DXE precede valid GOP and ConsoleOut; need bounded RAM logging plus later safe replay, not early guessed pixel writes.'},
      hardware_executed=False,pixel_access=False,device_action=False)
    assert links['EnumaProbe'] and all(x['null_serial'] and not x['framebuffer_serial'] for x in links['EnumaProbe'])
    (ROOT/'reports/enuma-console-path-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: bound console/menu source and actual module library lists; no hardware execution claimed')
if __name__=='__main__':main()
