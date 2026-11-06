"""Host sanitizer checks for actual firmware transport functions, no device I/O."""
import hashlib
import importlib.util
import json
from pathlib import Path
from check_enuma_drivers import run

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'firmware'
    driver = source / 'Platforms/Xiaomi/enumaPkg/Drivers/EnumaRamPayloadDxe'
    out = ROOT / 'out/full-boot/transport'; out.mkdir(exist_ok=True)
    spec = importlib.util.spec_from_file_location('enuma_payload_contract', source / 'Resources/Scripts/enuma_payload_contract.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.generate(ROOT, ROOT / 'out/full-boot/payload/payload.img', out / 'PayloadContract.h')
    raw = (driver / 'EnumaRamPayload.c').read_text()
    a = raw.index('STATIC EFI_STATUS EFIAPI\nRamReset')
    b = raw.index('STATIC EFI_BLOCK_IO_PROTOCOL', a)
    (out / 'BlockRead.inc').write_text(raw[a:b])
    a = raw.index('STATIC EFI_STATUS CrcMatches')
    b = raw.index('STATIC EFI_STATUS ReadAddress', a)
    (out / 'CrcMatches.inc').write_text(raw[a:b])
    vendor = (ROOT / 'out/device-tests/20261022T201404/vendor_boot_a.bin').read_bytes()
    contract = json.loads((ROOT / 'reports/enuma-ram-payload-contract.json').read_text())
    (out / 'prefix.bin').write_bytes(vendor[4096:4096 + contract['prefix_bytes']])
    flags = ['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
             '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-I' + str(out), '-I' + str(driver)]
    checks = [run([*flags, ROOT / 'tests/ram_payload_contract.c', '-lz', '-o', out / 'transport-test'])]
    checks.append(run([out / 'transport-test', ROOT / 'out/full-boot/payload/payload.img', out / 'prefix.bin']))
    report = dict(scope='actual production bounds, BlockIO and CRC wrapper with host service adapters; synthetic physical addresses, no FDT/SFS/device execution',
                  sources={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                           [driver / 'EnumaRamPayload.c', driver / 'TransportBounds.h', ROOT / 'tests/ram_payload_contract.c']},
                  checks=checks, hardware_tested=False, new_memory_mapping=False)
    (ROOT / 'reports/enuma-ram-payload-host.json').write_text(json.dumps(report, indent=2) + '\n')
    print(checks[-1]['stdout'].strip())


if __name__ == '__main__':
    main()
