"""Serialize enuma hardware nodes using the pinned upstream ADT encoder.

This is a composition input, not a bootable ADT: no /chosen, donor identity,
DRAM size, framebuffer or root storage is invented before UEFI observations.
"""
import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from audit_inputs import parse_fdt, strings, cells
from plan_adt import plan

ROOT = Path(__file__).resolve().parents[1]


def locked_encoder(sheng):
    lock = json.loads((ROOT / 'config/sources.lock.json').read_text())['sources']['UniXNU-sheng']
    path = sheng / 'scripts/make-sheng-adt.py'
    expected = lock['file_sha256']['scripts/make-sheng-adt.py']
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('upstream ADT encoder pin mismatch')
    spec = importlib.util.spec_from_file_location('pinned_sheng_adt', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.node


def hardware_fragment(fdt, node):
    evidence = plan(fdt)
    if evidence['fdt_input']['sha256'] != '643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62':
        raise ValueError('FDT differs from the observed enuma snapshot')
    nodes = parse_fdt(fdt.read_bytes())
    timer = cells(nodes[evidence['timer']['path']]['interrupts'])
    # Unchanged ArmCpu handles virtual timer INTID 27. DT PPI cell 11 -> 27.
    if len(timer) != 12 or timer[6:9] != [1, 11, 0xff08] or evidence['timer']['frequency_hz'] != 19200000:
        raise ValueError('timer differs from the pinned ArmCpu virtual-timer contract')
    cpus = sorted(((int.from_bytes(p['reg'], 'big'), p) for n, p in nodes.items()
                   if n.startswith('/cpus/') and p.get('device_type') == b'cpu\0'))
    cpu_nodes = []
    for index, (affinity, props) in enumerate(cpus):
        if strings(props['compatible']) != ['qcom,kryo']:
            raise ValueError('CPU compatible changed')
        cpu_nodes.append(node('cpu' + str(index), [
            ('device_type', b'cpu\0'), ('compatible', props['compatible']),
            ('reg', struct.pack('<I', affinity)),
            ('state', b'running\0' if affinity == 0 else b'waiting\0'),
            ('timebase-frequency', struct.pack('<I', evidence['timer']['frequency_hz']))]))
    gic = evidence['gic']
    values = [int(gic[key], 0) for key in ('distributor_pa', 'distributor_size', 'redistributor_pa', 'redistributor_size')]
    # Widen the *observed* identity-mapped SoC ranges to the 64-bit Apple DT
    # representation consumed by ArmCpu::mapGic; preserve its original span.
    span = cells(nodes['/soc']['ranges'])[3]
    if any(values[i] > span or values[i+1] > span-values[i] for i in (0, 2)):
        raise ValueError('GIC lies outside the observed identity bus range')
    result = node('device-tree', [
        ('compatible', b'xiaomi,enuma\0qcom,sm8250\0'),
        ('#address-cells', struct.pack('<I', 2)), ('#size-cells', struct.pack('<I', 2))], [
        node('cpus', children=cpu_nodes),
        node('psci', [('compatible', b'arm,psci-1.0\0'), ('method', evidence['psci']['method'].encode()+b'\0')]),
        node('arm-io', [('device_type', b'arm-io\0'), ('#address-cells', struct.pack('<I', 2)),
                        ('#size-cells', struct.pack('<I', 2)), ('ranges', struct.pack('<QQQ', 0, 0, span))], [
            node('intc', [('compatible', b'arm,gic-v3\0'), ('reg', struct.pack('<4Q', *values)),
                          ('redistributor-stride', struct.pack('<Q', int(gic['redistributor_stride'], 0)))])])])
    return result, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheng', type=Path, required=True)
    parser.add_argument('--unixnu', type=Path, required=True)
    parser.add_argument('--fdt', type=Path, default=ROOT / 'out/device/live-fdt.bin')
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    lock = json.loads((ROOT / 'config/porting-sources.lock.json').read_text())['unixnu_interface_sha256']
    interfaces = {}
    for name in ('drivers/ArmCpu/ArmCpu.cpp', 'drivers/ArmDTPlatform/ArmDTPlatform.cpp',
                 'drivers/NativeHidInput/NativeHidInput.cpp'):
        digest = hashlib.sha256((args.unixnu / name).read_bytes()).hexdigest()
        if digest != lock[name]: raise ValueError('platform interface pin mismatch: ' + name)
        interfaces[name] = digest
    blob, evidence = hardware_fragment(args.fdt, locked_encoder(args.sheng))
    out = ROOT / 'out/enuma-platform'; out.mkdir(parents=True, exist_ok=True)
    (out / 'hardware.adt-fragment').write_bytes(blob)
    report = {'scope': 'serialized hardware fragment only; not bootable, linked or executed',
              'path': 'out/enuma-platform/hardware.adt-fragment', 'bytes': len(blob),
              'sha256': hashlib.sha256(blob).hexdigest(), 'fdt_sha256': evidence['fdt_input']['sha256'],
              'cpu_compatible': 'qcom,kryo', 'cpu_affinities': evidence['cpu_affinities'],
              'gic': evidence['gic'], 'timer_intid': 27, 'psci': evidence['psci'],
              'interface_sha256': interfaces,
              'smp_policy': 'boot CPU first; do not enable sheng-smp workaround flags by inheritance',
              'missing_for_boot': ['chosen/NVRAM proxy and donor/product identity',
                 'runtime memory allocation and matching DRAM contract', 'actual GOP video contract',
                 'enuma kernel link, root payload and prelink'], 'hardware_execution': False}
    (ROOT / 'reports/enuma-adt-fragment.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: serialized 8 Kryo CPUs, PSCI SMC and enuma GIC windows with pinned upstream encoder; fragment only')


if __name__ == '__main__': main()
