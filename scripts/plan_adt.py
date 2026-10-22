"""Derive an enuma ADT input plan from historical FDT; never emit an ADT/image."""
import argparse
import json
from pathlib import Path
from audit_inputs import cells, hashes, parse_fdt, strings

ROOT = Path(__file__).resolve().parents[1]


def plan(path):
    nodes = parse_fdt(path.read_bytes())
    if 'enuma' not in strings(nodes['/']['model'])[0].lower():
        raise ValueError('FDT is not enuma')
    soc = nodes['/soc']
    if cells(soc['#address-cells']) != [1] or cells(soc['#size-cells']) != [1] or cells(soc['ranges']) != [0, 0, 0, 0xFFFFFFFF]:
        raise ValueError('unsupported SoC bus mapping; do not assume physical reg addresses')

    def unique(compatible):
        found = [(name, props) for name, props in nodes.items()
                 if compatible in strings(props.get('compatible', b''))
                 and strings(props.get('status', b'ok\0'))[0] in ('ok', 'okay')]
        if len(found) != 1:
            raise ValueError(f'ambiguous/missing enabled {compatible}')
        return found[0]

    gic_path, gic = unique('arm,gic-v3')
    timer_path, timer = unique('arm,armv8-timer')
    psci_path, psci = unique('arm,psci-1.0')
    cpu = [(name, props) for name, props in nodes.items()
           if name.startswith('/cpus/') and strings(props.get('device_type', b'')) == ['cpu']]
    affinity = sorted(int.from_bytes(props['reg'], 'big') for _, props in cpu)
    if affinity != list(range(0, 0x800, 0x100)):
        raise ValueError('unexpected enuma CPU topology')
    if len(gic['reg']) != 16 or not gic_path.startswith('/soc/'):
        raise ValueError('unsupported GIC layout')
    if len(gic.get('redistributor-stride', b'')) != 8:
        raise ValueError('missing GIC redistributor stride')
    gic_reg = cells(gic['reg'])
    touch_path, touch = unique('novatek,NVT-ts-spi')
    firmwares = {name: strings(props['novatek,fw-name'])[0] for name, props in nodes.items()
                 if name.startswith(touch_path + '/') and 'novatek,fw-name' in props}
    return {
        'scope': 'offline ADT input plan, historical Android tree only; no UEFI or XNU execution',
        'fdt_input': hashes(path), 'source_model': strings(nodes['/']['model']),
        'cpu_affinities': [hex(value) for value in affinity],
        'psci': {'path': psci_path, 'method': strings(psci['method'])[0]},
        'timer': {'path': timer_path, 'frequency_hz': cells(timer['clock-frequency'])[0],
                  'interrupt_cells': cells(timer['interrupts'])},
        'gic': {'path': gic_path, 'distributor_pa': hex(gic_reg[0]), 'distributor_size': hex(gic_reg[1]),
                'redistributor_pa': hex(gic_reg[2]), 'redistributor_size': hex(gic_reg[3]),
                'redistributor_stride': hex(int.from_bytes(gic['redistributor-stride'], 'big')),
                'translation_evidence': '/soc ranges maps bus [0,0xffffffff) to identical root physical addresses'},
        'touch': {'path': touch_path, 'irq_gpio_cells': cells(touch['novatek,irq-gpio']),
                  'firmware_candidates': firmwares, 'driver_binding': 'not_observed_in_this_run'},
        'donor_identity': {'product': 'iPad7,1', 'device_class': 'j120ap', 'build': '21H461'},
        'unresolved': [
            'UEFI allocation map and reviewed DRAM/owned contiguous window',
            'reviewed arm-io parent range and matching relative GIC regs',
            'CPU compatible policy for Kryo 585; do not inherit cortex-a715',
            'GOP framebuffer base/stride/pixel format and persistent scan-out',
            'enuma product/button/display geometry policy',
            'platform identity seed outside Git and selected Data/root UUID',
            'SM8250 UFS clock/PHY/SMMU handoff and storage layout',
        ],
        'disabled_hardware': ['SM8550 NativeUfs path', 'Sheng PMGR', 'A740 NativeAdreno path'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fdt', type=Path, default=Path('D:/Code/PortingiOS/enuma/backups/android-root/20261021T124813939334Z/android-root-fdt.stdout'))
    args = parser.parse_args()
    result = plan(args.fdt)
    output = ROOT / 'reports/enuma-adt-plan.json'
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: enuma GIC/PSCI/timer/topology plan; {len(result["unresolved"])} unresolved contracts; no binary emitted')


if __name__ == '__main__':
    main()
