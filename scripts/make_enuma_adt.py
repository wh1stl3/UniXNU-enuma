"""Compose an offline enuma ADT with the pinned umi encoder; no hardware I/O.

SPDX-License-Identifier: BSD-2-Clause-Patent
The external encoder retains its original copyright and license.
"""
import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
    sys.modules['tomllib'] = tomllib
from audit_inputs import parse_fdt, strings, cells
from plan_adt import plan

ROOT = Path(__file__).resolve().parents[1]
FDT_SHA = '643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62'


def encoder():
    ref = json.loads((ROOT / 'config/system-reuse-sources.lock.json').read_text())['references'][0]
    source = ROOT / Path(ref['local'].replace('\\', '/')) / 'scripts/umi_adt.py'
    if hashlib.sha256(source.read_bytes()).hexdigest() != ref['files']['scripts/umi_adt.py']['sha256']:
        raise ValueError('umi ADT encoder hash mismatch')
    spec = importlib.util.spec_from_file_location('pinned_umi_adt', source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def hardware(fdt):
    if hashlib.sha256(fdt.read_bytes()).hexdigest() != FDT_SHA:
        raise ValueError('not the audited enuma FDT snapshot')
    evidence = plan(fdt)
    nodes = parse_fdt(fdt.read_bytes())
    if (cells(nodes['/']['#address-cells']), cells(nodes['/']['#size-cells'])) != ([2], [2]):
        raise ValueError('unsupported physical memory cell geometry')
    banks = []
    for path, props in nodes.items():
        if props.get('device_type') != b'memory\0':
            continue
        raw = props['reg']
        if path.count('/') != 1 or len(raw) % 16:
            raise ValueError('unsupported memory node encoding')
        banks.extend(dict(base=b, size=s) for b, s in struct.iter_unpack('>QQ', raw))
    banks.sort(key=lambda b: b['base'])
    end = 0
    for bank in banks:
        if bank['base'] < end or bank['size'] <= 0 or bank['base'] + bank['size'] >= 1 << 64:
            raise ValueError('invalid or overlapping observed memory banks')
        end = bank['base'] + bank['size']
    if not banks:
        raise ValueError('missing observed DRAM banks')
    if evidence['timer']['interrupt_cells'][6:9] != [1, 11, 0xff08] or evidence['timer']['frequency_hz'] != 19200000:
        raise ValueError('virtual timer contract changed')
    cpus = sorted((int.from_bytes(p['reg'], 'big'), strings(p['compatible']))
                  for n, p in nodes.items() if n.startswith('/cpus/') and p.get('device_type') == b'cpu\0')
    if any(c != ['qcom,kryo'] for _, c in cpus) or evidence['psci']['method'] != 'smc':
        raise ValueError('CPU/PSCI contract changed')
    g = evidence['gic']
    return dict(model='enuma', product_name='Xiaomi Pad 5 Pro 5G',
                compatible=['xiaomi,enuma', 'qcom,sm8250'], memory_banks=banks,
                cpus=[dict(affinity=a, compatible=c) for a, c in cpus],
                psci=dict(compatible='arm,psci-1.0', method='smc'),
                timer=dict(frequency_hz=19200000, virtual_timer_intid=27),
                gic=dict(compatible='arm,gic-v3',
                         distributor=dict(base=int(g['distributor_pa'], 0), size=int(g['distributor_size'], 0)),
                         redistributor=dict(base=int(g['redistributor_pa'], 0), size=int(g['redistributor_size'], 0)),
                         redistributor_stride=int(g['redistributor_stride'], 0)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--fdt', type=Path, default=ROOT / 'out/device/live-fdt.bin')
    p.add_argument('--dram-size', type=lambda s: int(s, 0), required=True)
    p.add_argument('--owned-memory-size', type=lambda s: int(s, 0), default=0x20000000)
    p.add_argument('--cpu-regs', default='0')
    p.add_argument('--psci-method', choices=['smc'], default='smc')
    p.add_argument('--unique-chip-id', type=lambda s: int(s, 16))
    p.add_argument('--chip-id', type=lambda s: int(s, 16))
    p.add_argument('--root-match-volume-uuid')
    data = p.add_mutually_exclusive_group()
    data.add_argument('--data-ramdisk', action='store_true')
    data.add_argument('--packed-data-ramdisk', action='store_true')
    p.add_argument('--trust-cache', action='store_true')
    p.add_argument('--ipad-identity', action='store_true')
    a = p.parse_args()
    if a.owned_memory_size != 0x20000000:
        raise ValueError('only R-001 512 MiB request is approved')
    h = hardware(a.fdt)
    m = encoder()
    tree = m.build_tree(h, dram_size=a.dram_size, owned_memory_size=a.owned_memory_size,
                        cpu_regs=tuple(int(v, 0) for v in a.cpu_regs.split(',')), psci_method=a.psci_method,
                        unique_chip_id=a.unique_chip_id, chip_id=a.chip_id,
                        root_match_volume_uuid=a.root_match_volume_uuid, data_ramdisk=a.data_ramdisk,
                        packed_data_ramdisk=a.packed_data_ramdisk, trust_cache=a.trust_cache,
                        ipad_identity=a.ipad_identity)
    blob = tree.encode()
    if m.decode(blob).encode() != blob:
        raise ValueError('ADT encode/decode differs')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(blob)
    report = dict(scope='offline ADT composition, no runtime allocation or execution',
                  bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(), fdt_sha256=FDT_SHA,
                  observed_memory_banks=h['memory_banks'], summary=m.summary(tree),
                  encoder_roundtrip_equal=True, hardware_tested=False,
                  memory_policy='DRAM fields are historical FDT information, not a free or contiguous map; runtime UEFI allocation required',
                  missing=['root volume/PMGR/UFS integration', 'GOP/error channel', 'private platform identity seed', 'runtime allocation evidence'])
    a.output.with_suffix(a.output.suffix + '.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: enuma ADT composed with pinned encoder; runtime contracts remain open')


if __name__ == '__main__':
    main()
