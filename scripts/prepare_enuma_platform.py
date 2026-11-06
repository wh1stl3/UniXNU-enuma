"""Generate enuma Mu platform tables from its hash-locked OEM config, not alioth."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    inventory = json.loads((ROOT / 'reports/enuma-oem-modules.json').read_text())
    source = ROOT / 'out/firmware-vendor/raw/uefiplat.cfg'
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != inventory['raw_inputs']['uefiplat.cfg']:
        raise ValueError('OEM configuration digest mismatch')
    text = raw.decode('ascii').rstrip('\0')
    rows = []; parameters = []; section = ''; ignored = []
    for line in text.splitlines():
        line = line.split('#', 1)[0].strip()
        if not line: continue
        if line.startswith('['): section = line; continue
        if section in ('[MemoryMap]', '[RegisterMap]'):
            match = re.fullmatch(r'(0x[0-9a-fA-F]+),\s*(0x[0-9a-fA-F]+),\s*"([^"]+)",\s*(\w+),\s*(\w+),\s*(\w+),\s*(\w+),\s*(\w+)', line)
            if not match: raise ValueError('unsupported OEM memory entry: ' + line)
            base, size, name, *attrs = match.groups()
            if len(name) >= 32 or not int(size, 16): raise ValueError('invalid region')
            rows.append({'name': name, 'base': int(base, 16), 'size': int(size, 16), 'attributes': attrs,
                         'section': section})
        elif section == '[ConfigParameters]':
            key, value = [x.strip() for x in line.split('=', 1)]
            if key == 'ConfigParameterCount': continue
            if re.fullmatch(r'0x[0-9a-fA-F]+|[0-9]+', value): parameters.append((key, int(value, 0)))
            else: ignored.append(key)
    regions = {r['name']: r for r in rows}
    if len(regions) != len(rows) or not {'DXE Heap', 'UEFI FD', 'UEFI Stack', 'Display Reserved'} <= regions.keys():
        raise ValueError('required unique platform regions missing')
    package = ROOT / 'firmware/Platforms/Xiaomi/enumaPkg'
    # Numerical hardware configuration is regenerated; OEM text/binaries stay in out/.
    memory = '#include <Library/MemoryMapLib.h>\n\n// Generated from enuma XBL; provenance in reports/enuma-platform-config.json.\n'
    memory += 'STATIC EFI_MEMORY_REGION_DESCRIPTOR mRegions[] = {\n'
    for r in rows:
        memory += '  {"%s", 0x%xULL, 0x%xULL, %s},\n' % (r['name'], r['base'], r['size'], ', '.join(r['attributes']))
    memory += '};\n\nVOID GetMemoryMap (EFI_MEMORY_REGION_DESCRIPTOR **Map, UINT8 *Count) {\n  *Map = mRegions;\n  *Count = ARRAY_SIZE (mRegions);\n}\n'
    config = '#include <Uefi.h>\n#include <Library/ConfigurationMapLib.h>\n\nSTATIC EFI_CONFIGURATION_ENTRY_DESCRIPTOR mConfig[] = {\n'
    for key, value in parameters: config += '  {"%s", 0x%xULL},\n' % (key, value)
    config += '};\n\nVOID GetConfigurationMap (EFI_CONFIGURATION_ENTRY_DESCRIPTOR **Map, UINT8 *Count) {\n  *Map = mConfig;\n  *Count = ARRAY_SIZE (mConfig);\n}\n'
    for name, code, guid, packages in [
        ('MemoryMapLib', memory, '895c7dc3-d160-45e1-a5bd-91a4c8900088', ['ArmPkg/ArmPkg.dec', 'MdePkg/MdePkg.dec', 'SiliciumPkg/SiliciumPkg.dec']),
        ('ConfigurationMapLib', config, '07299917-d5d4-43bc-b9c8-b85a93c5b250', ['MdePkg/MdePkg.dec', 'QcomPkg/QcomPkg.dec'])]:
        directory = package / 'Library' / name; directory.mkdir(parents=True, exist_ok=True)
        (directory / (name + '.c')).write_text(code, newline='\n')
        inf = f'[Defines]\n  INF_VERSION = 0x00010005\n  BASE_NAME = Enuma{name}\n  FILE_GUID = {guid}\n  MODULE_TYPE = BASE\n  VERSION_STRING = 1.0\n  LIBRARY_CLASS = {name}\n\n[Sources]\n  {name}.c\n\n[Packages]\n'
        (directory / (name + '.inf')).write_text(inf + ''.join('  ' + p + '\n' for p in packages), newline='\n')
    stack = regions['UEFI Stack']; fd = regions['UEFI FD']
    # Use the native enuma display provider; query the resulting GOP at runtime.
    platform = f'''# enuma OEM memory and numeric configuration. No foreign-board table.
[LibraryClasses]
  MemoryMapLib|enumaPkg/Library/MemoryMapLib/MemoryMapLib.inf
  ConfigurationMapLib|enumaPkg/Library/ConfigurationMapLib/ConfigurationMapLib.inf
  # Native GOP is established later. Avoid early framebuffer writes with guessed format.
  SerialPortLib|MdePkg/Library/BaseSerialPortLibNull/BaseSerialPortLibNull.inf

[PcdsFixedAtBuild]
  gArmTokenSpaceGuid.PcdSystemMemoryBase|0x80000000
  gArmPlatformTokenSpaceGuid.PcdCPUCoresStackBase|{hex(stack['base'])}
  gArmPlatformTokenSpaceGuid.PcdCPUCorePrimaryStackSize|{hex(stack['size'])}
  gSiliciumPkgTokenSpaceGuid.PcdFrameBufferWidth|1600
  gSiliciumPkgTokenSpaceGuid.PcdFrameBufferHeight|2560

# DisplayDxe and K81 raw resources come from this enuma's XBL.
# No assumed framebuffer address/pitch/color depth is supplied to SimpleFb.

!ifndef ENUMA_VENDOR_DSC
  !error ENUMA_VENDOR_DSC must bind the extracted enuma modules
!endif
!include $(ENUMA_VENDOR_DSC)
'''
    (package / 'Include/PlatformConfig.inc').write_text(platform, newline='\n')
    resource = ROOT / 'firmware/Resources/Configs/enuma.toml'; resource.parent.mkdir(parents=True, exist_ok=True)
    resource.write_text(f'''# Candidate packaging profile. OEM addresses are facts, not a proved re-entry contract.
[boot_shim]
requires_kernel_header = true
[uefi_fd]
base = {hex(fd['base'])}
size = {hex(fd['size'])}
[boot_image_kernel]
kernel_compression = "none"
append_dtb = false
[boot_image]
header_version = 3
''', newline='\n')
    report = {'source_xbl_sha256': inventory['xbl_sha256'], 'config_sha256': inventory['raw_inputs']['uefiplat.cfg'],
              'regions': rows, 'numeric_parameters': dict(parameters), 'string_parameters_not_representable_in_Mu_table': ignored,
              'gop': {'width': 1600, 'height': 2560, 'source': 'live Android DRM modes and FDT dual DSI',
                      'provider': 'native enuma DisplayDxe + CPRDxe + K81 XML; runtime initialization pending',
                      'boot_framebuffer_address': None, 'boot_stride': None, 'boot_pixel_format': None},
              'cautions': ['OEM map describes original firmware; re-entry placement and lifetimes still need testing',
                           'OEM Display Reserved combines 35 MiB splash and 1 MiB DFPS; never assume all is pixel storage',
                           'numeric parameters preserve OEM values including EnableUfsIOC=0',
                           'UEFI map and RamPartition protocol after dispatch are not observed'],
              'generated_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(package.glob('Library/*/*'))}}
    (ROOT / 'reports/enuma-platform-config.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: generated {len(rows)} OEM regions and {len(parameters)} numeric parameters; native GOP provider selected')


if __name__ == '__main__': main()
