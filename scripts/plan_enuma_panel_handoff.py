"""Export the exact enuma K81 panel transport contract for offline integration.

FD/FF interpretation follows the referenced Qualcomm source model, not a
claim that the closed enuma interpreter has executed identically.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XML_SHA = '62aa7bd9b434c7622da7b3bb1709c69c1962a9a3ea026c2fea25602b557f480f'


def contract(blob):
    if hashlib.sha256(blob).hexdigest() != XML_SHA:
        raise ValueError('not the exact enuma K81 resource')
    text = blob.decode('utf-8')
    body = re.search(r'<DSIInitSequence>(.*?)</DSIInitSequence>', text, re.S).group(1)
    mask = 1
    streams = [[], []]
    events = []
    for line in body.splitlines():
        if not line.strip():
            continue
        packet = bytes.fromhex(line.strip())
        if packet[0] == 0xfd:
            if len(packet) != 2 or packet[1] not in (1, 2, 3):
                raise ValueError('unexpected controller selector')
            mask = packet[1]
            events.append(dict(kind='select', mask=mask))
        elif packet[0] == 0xff:
            if len(packet) != 2:
                raise ValueError('unexpected delay')
            events.append(dict(kind='delay', ms=packet[1]))
        elif packet[0] in (5, 0x15, 0x39):
            event = dict(kind='dcs', data_type=packet[0], payload=packet[1:].hex(), mask=mask)
            events.append(event)
            for controller in (0, 1):
                if mask & (1 << controller):
                    streams[controller].append(dict(data_type=packet[0], payload=packet[1:].hex()))
        else:
            raise ValueError('unsupported packet; do not silently drop it')
    if streams[0] != streams[1] or len(streams[0]) != 188:
        raise ValueError('unexpected per-controller stream')
    tags = ['HorizontalActive', 'VerticalActive', 'HorizontalFrontPorch', 'HorizontalBackPorch',
            'HorizontalSyncPulse', 'VerticalFrontPorch', 'VerticalBackPorch', 'VerticalSyncPulse',
            'DSICPhyMode', 'DSILanes', 'DSIRefreshRate', 'DisplayResetInfo', 'BacklightDefault']
    return dict(schema=1, route='elish-csot-reference-with-native-enuma-k81', xml_sha256=XML_SHA,
                resource_policy='preserve original XML bytes; no command or timing patch',
                interpreter_model='Rivko/android-firmware-qti-sdm670@20bb8ae36c93fc16bbadda0e0a83f930c0c8a271 dsiDriver.c',
                timing={tag: re.search(fr'<{tag}>(.*?)</{tag}>', text, re.S).group(1).strip() for tag in tags},
                events=events, controller_streams=streams,
                deployment_qualified=False, hardware_executed=False,
                prerequisites=['Validate loaded native K81 identity and active CSOT panel selection',
                               'Use native controller/PHY/power implementation; this JSON does not drive hardware',
                               'Prove predecessor scanout/memory ownership before inherited-GOP publication',
                               'Keep cold reinitialization separate from inherited framebuffer adoption'],
                forbidden_shortcuts=['Do not delete the split-link sleep-out commands',
                                     'Do not replace native 100ms/16ms waits with Android 70ms without evidence',
                                     'Do not infer physical framebuffer pitch/format from panel dimensions'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--xml', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    result = contract(args.xml.read_bytes())
    output = args.output.resolve()
    output.relative_to(ROOT / 'out')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(output=str(output), commands_per_controller=[len(s) for s in result['controller_streams']], deployment_qualified=False)))


if __name__ == '__main__':
    main()
