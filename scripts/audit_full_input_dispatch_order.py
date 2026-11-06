"""Inspect frozen S-003 FV APRIORI order; no build or device access."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.path.insert(0, str(ROOT / 'out/reverse-tools'))
    from uefi_firmware.uefi import FirmwareVolume, FirmwareFile
    archive = ROOT / 'out/full-boot/transport/return-boundary-cb9e568'
    qualification = json.loads((archive / 'qualification.json').read_text())
    data = (archive / 'candidate.fd').read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != qualification['files']['candidate.fd']['sha256']:
        raise ValueError('frozen FD differs')
    volume = FirmwareVolume(data)
    with contextlib.redirect_stdout(io.StringIO()):
        if not volume.process():
            raise ValueError('FD decode failed')
    queue = [volume]
    lists = []
    while queue:
        item = queue.pop(0)
        queue.extend(getattr(item, 'objects', []))
        if isinstance(item, FirmwareFile) and str(uuid.UUID(bytes_le=item.guid)) == 'fc510ee7-ffdc-11d4-bd41-0080c73c8881':
            for section in item.objects:
                if section.type == 0x19:
                    raw = section.data
                    if len(raw) % 16:
                        raise ValueError('malformed APRIORI')
                    lists.append([str(uuid.UUID(bytes_le=raw[i:i+16])) for i in range(0, len(raw), 16)])
    if len(lists) != 1:
        raise ValueError('missing or ambiguous APRIORI')
    order = lists[0]
    display = '4138022f-06c7-4f79-9c94-7e33b511a4e7'
    ram = '03a65cd0-a246-4cc6-bf65-04e1f784cd78'
    if order.count(display) != 1 or ram in order:
        raise ValueError('dispatch topology differs from reviewed source')
    report = dict(scope='static frozen S-003 FD; not evidence any driver executed',
                  fd_sha256=digest, apriori_guids=order, display_index=order.index(display),
                  ram_payload_in_apriori=False,
                  specification='https://uefi.org/specs/PI/1.8/V2_DXE_Dispatcher.html',
                  inference='With this single FV APRIORI dispatch, RAM payload DXE is not a prerequisite before DisplayDxe; earlier image/layout effects remain possible',
                  hardware_execution=False)
    (ROOT / 'reports/enuma-full-input-dispatch-order.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: actual frozen FD APRIORI includes DisplayDxe and excludes RAM payload DXE; static only')


if __name__ == '__main__':
    main()
