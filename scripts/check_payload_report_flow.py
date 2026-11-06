"""Execute the actual BDS payload/report tail with host failure injection."""
import hashlib
import json
from pathlib import Path
from check_enuma_drivers import run

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'firmware/Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c'
    raw = source.read_text()
    begin = raw.index('#if ENUMA_RAM_PAYLOAD\n  {')
    out = ROOT / 'out/full-boot/report-flow'; out.mkdir(exist_ok=True)
    (out / 'PayloadTail.inc').write_text(raw[begin:])
    driver = ROOT / 'firmware/Platforms/Xiaomi/enumaPkg/Drivers/EnumaRamPayloadDxe'
    records = [run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                    '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-I' + str(out), '-I' + str(driver),
                    ROOT / 'tests/payload_report_flow.c', '-o', out / 'report-flow-test'])]
    records.append(run([out / 'report-flow-test']))
    result = dict(scope='actual extracted BDS payload/report tail with host GOP/boot-service adapters; no framebuffer/device execution',
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), checks=records, hardware_tested=False)
    (ROOT / 'reports/enuma-payload-report-flow.json').write_text(json.dumps(result, indent=2) + '\n')
    print(records[-1]['stdout'].strip())


if __name__ == '__main__': main()
