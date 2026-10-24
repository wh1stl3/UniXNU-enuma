"""One-off: list every OEM module in XBL and find who references DisplayDxe's DEPEX GUIDs."""
import struct
import sys
import uuid
from pathlib import Path

sys.path.insert(0, '/mnt/d/Code/UniXNU-enuma/scripts')
from uefi_firmware.uefi import FirmwareVolume, FirmwareFile

ROOT = Path('/mnt/d/Code/UniXNU-enuma')
blob = (ROOT / 'out/device/xbl_a.bin').read_bytes()
offset = 0x888b0
length = struct.unpack_from('<Q', blob, offset + 32)[0]
volume = FirmwareVolume(blob[offset:offset + length])
if not volume.process():
    raise SystemExit('FV decode failed')

queue = [volume]
files = {}
while queue:
    obj = queue.pop(0)
    queue.extend(getattr(obj, 'objects', []))
    if not isinstance(obj, FirmwareFile) or obj.type == 0xf0:
        continue
    guid = str(uuid.UUID(bytes_le=obj.guid))
    sections = obj.objects
    names = [s.data.decode('utf-16-le').rstrip('\0') for s in sections if s.type == 0x15]
    name = names[0] if names else guid
    pe = [s for s in sections if s.type == 0x10]
    dep = [s for s in sections if s.type == 0x13]
    files[name] = {'guid': guid, 'pe': pe[0].data if pe else None,
                   'depex': dep[0].data if dep else None}

print('total modules:', len(files))
print()
print('=== names containing display/mdp/dsi/panel/cpr/clock/pmic/i2c/gpio ===')
keys = ('display', 'mdp', 'dsi', 'panel', 'cpr', 'clock', 'pmic', 'i2c', 'gpio', 'tlmm', 'spmi', 'backlight')
for name in sorted(files):
    if any(k in name.lower() for k in keys):
        print(' ', name, files[name]['guid'])


def depex_guids(data):
    out, off = [], 0
    while off < len(data):
        op = data[off]
        off += 1
        if op in (0, 1, 2):
            out.append(str(uuid.UUID(bytes_le=data[off:off + 16])))
            off += 16
        elif op in (3, 4, 5, 9):
            continue
        elif op in (6, 7):
            continue
        elif op == 8:
            return out
        else:
            return out
    return out


target = 'DisplayDxe'
if target not in files:
    raise SystemExit('DisplayDxe not present')
dep = files[target]['depex']
print()
print('===', target, 'DEPEX ===')
if dep is None:
    print('  (no depex)')
else:
    guids = depex_guids(dep)
    for g in guids:
        needle = uuid.UUID(g).bytes_le
        holders = [n for n, f in files.items() if f['pe'] and needle in f['pe']]
        print(f'  {g}  referenced-by: {holders if holders else "NONE"}')

f = files['DisplayDxe']
print()
print('=== DisplayDxe raw depex ===')
print('depex bytes:', len(f['depex']) if f['depex'] else None)
if f['depex']:
    print(f['depex'].hex())
print()
print('=== DisplayDxe PE size:', len(f['pe']) if f['pe'] else None)
