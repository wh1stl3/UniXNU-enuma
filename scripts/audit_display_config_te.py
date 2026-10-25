"""Inspect the real packed SEC TE configuration table, no device execution."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import struct
import uuid
from uefi_firmware.uefi import FirmwareVolume, FirmwareFile

ROOT = Path(__file__).resolve().parents[1]
SEC = '9affb503-e643-4141-8b90-17e8588b1d35'


def inspect(te):
    if te[:2] != b'VZ' or struct.unpack_from('<H', te, 2)[0] != 0xaa64:
        raise ValueError('expected AARCH64 SEC TE')
    name = b'EnableDisplayThread'
    marker = name + bytes(64 - len(name))
    if te.count(marker) != 1:
        raise ValueError('configuration table entry missing/ambiguous')
    offset = te.index(marker)
    if struct.unpack_from('<Q', te, offset + 64)[0] != 0:
        raise ValueError('actual SEC configuration does not disable display thread')
    return offset


def main():
    build = json.loads((ROOT / 'reports/enuma-firmware-build.json').read_text())
    pin = json.loads((ROOT / 'config/uefi-source.lock.json').read_text())
    if build.get('uefi_source_commit') != pin['commit']:
        raise ValueError('build report belongs to an older firmware pin')
    raw = (ROOT / build['fd']).read_bytes()
    if not build['complete'] or hashlib.sha256(raw).hexdigest() != build['fd_sha256']:
        raise ValueError('stale/incomplete FD build')
    fv = FirmwareVolume(raw)
    with contextlib.redirect_stdout(io.StringIO()):
        if not fv.process(): raise ValueError('FD decode failed')
    queue = [fv]; records = []
    while queue:
        obj = queue.pop(0); queue.extend(getattr(obj, 'objects', []))
        if isinstance(obj, FirmwareFile) and str(uuid.UUID(bytes_le=obj.guid)) == SEC:
            records.extend(s.data for s in obj.objects if s.type == 0x12)
    if len(records) != 1: raise ValueError('missing/ambiguous packed SEC TE')
    te = records[0]; offset = inspect(te)
    mutation = bytearray(te); mutation[offset + 64] = 1
    try: inspect(mutation)
    except ValueError: pass
    else: raise ValueError('old thread policy mutation accepted')
    report = dict(scope='actual packed SEC TE configuration, static only', firmware_commit=build['uefi_source_commit'],
                  fd_sha256=build['fd_sha256'], sec_guid=SEC, te_sha256=hashlib.sha256(te).hexdigest(),
                  entry_file_offset=hex(offset), value=0, mutation_to_old_value_rejected=True, hardware_tested=False)
    (ROOT / 'reports/enuma-display-config-te.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: actual packed SEC TE has display-thread=0; mutation to old value rejected')


if __name__ == '__main__': main()
