#!/usr/bin/env python3
"""Host-only input evidence, never a hardware/activation tool. Requires dtc/PyYAML."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import zlib

import yaml

ROOT = Path(__file__).resolve().parents[1]
UNKNOWN = {key: "UNKNOWN" for key in (
    "sid_context_exclusivity", "post_firmware_utrl_utmrl", "dma_ownership",
    "coherence", "pa_iova_mapping", "linux_sda_to_lun", "future_os_root_uuid",
)}
REFERENCE = "e2b32cc429e8cf1501161c1d8c517f8994ceb9b2"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def cells(node, prop):
    value = node[prop]
    require(isinstance(value, list) and all(isinstance(a, list) for a in value),
            f"invalid cell property {prop}")
    result = [x for a in value for x in a]
    require(all(type(x) is int and 0 <= x <= 0xffffffff for x in result),
            f"invalid cells in {prop}")
    return result


def one(node, prop):
    result = cells(node, prop)
    require(len(result) == 1, f"expected one cell: {prop}")
    return result[0]


def strings(node, prop):
    value = node[prop]
    require(isinstance(value, list) and all(isinstance(x, str) for x in value),
            f"invalid strings: {prop}")
    return [s for x in value for s in x.split('\0') if s]


class Tree:
    def __init__(self, source, fragment=False):
        # dtc handles DTS grammar, labels, numeric widths and phandles; no DTS regex.
        data = source.read_bytes()
        if fragment:
            data = b'/dts-v1/;\n' + data
        with tempfile.NamedTemporaryFile(suffix='.dts') as tmp:
            tmp.write(data)
            tmp.flush()
            proc = subprocess.run(['dtc', '-q', '-I', 'dts', '-O', 'yaml', tmp.name],
                                  capture_output=True, check=True)
        class Loader(yaml.SafeLoader):
            pass
        Loader.add_constructor('!phandle', lambda loader, node: int(loader.construct_scalar(node), 0))
        Loader.add_constructor('!u8', lambda loader, node: loader.construct_sequence(node))
        roots = yaml.load(proc.stdout, Loader=Loader)
        require(len(roots) == 1, 'expected one DT root')
        self.nodes = {}
        self.phandles = {}

        def walk(node, path):
            self.nodes[path] = node
            if 'phandle' in node:
                handle = one(node, 'phandle')
                require(handle not in self.phandles, 'duplicate phandle')
                self.phandles[handle] = path
            for name, child in node.items():
                if isinstance(child, dict):
                    walk(child, path.rstrip('/') + '/' + name)
        walk(roots[0], '/')

    def find(self, basename):
        paths = [p for p in self.nodes if p.rsplit('/', 1)[-1] == basename]
        require(len(paths) == 1, f"missing/ambiguous node {basename}")
        return paths[0]

    def provider(self, handle):
        require(handle in self.phandles, f"unresolved critical phandle {handle:#x}")
        return self.phandles[handle]

    def refs(self, path, prop, count_prop=None):
        data = cells(self.nodes[path], prop)
        result = []
        while data:
            provider = self.provider(data[0])
            count = one(self.nodes[provider], count_prop) if count_prop else 0
            require(count <= 16 and len(data) >= 1 + count, f"truncated {prop}")
            item = {'provider': provider, 'args': data[1:1 + count]}
            if 'compatible' in self.nodes[provider]:
                item['compatible'] = strings(self.nodes[provider], 'compatible')
            result.append(item)
            data = data[1 + count:]
        require(result, f"empty critical references: {prop}")
        return result

    def reg(self, path):
        parent = self.nodes[path.rsplit('/', 1)[0] or '/']
        ac = one(parent, '#address-cells')
        sc = one(parent, '#size-cells')
        require(ac in (1, 2) and sc in (1, 2), 'unsupported reg cell widths')
        data = cells(self.nodes[path], 'reg')
        require(data and len(data) % (ac + sc) == 0, 'malformed reg')
        result = []
        for i in range(0, len(data), ac + sc):
            address = int.from_bytes(struct.pack('>' + 'I' * ac, *data[i:i + ac]), 'big')
            size = int.from_bytes(struct.pack('>' + 'I' * sc, *data[i + ac:i + ac + sc]), 'big')
            require(size > 0 and address + size <= 1 << 64, 'reg overflow/empty range')
            result.append([address, size])
        # These particular resources must be directly addressed through identity buses.
        bus = path.rsplit('/', 1)[0]
        while bus:
            ranges = self.nodes[bus].get('ranges')
            if ranges is not True:
                require(ranges is not None, f"absent ranges: {bus}")
                child_ac = one(self.nodes[bus], '#address-cells')
                size_c = one(self.nodes[bus], '#size-cells')
                parent_ac = one(self.nodes[bus.rsplit('/', 1)[0] or '/'], '#address-cells')
                widths = child_ac + parent_ac + size_c
                raw = cells(self.nodes[bus], 'ranges')
                require(raw and len(raw) % widths == 0, 'invalid bus ranges')
                windows = []
                for i in range(0, len(raw), widths):
                    values = raw[i:i + widths]
                    def number(part):
                        return int.from_bytes(struct.pack('>' + 'I' * len(part), *part), 'big')
                    child = number(values[:child_ac])
                    target = number(values[child_ac:child_ac + parent_ac])
                    extent = number(values[child_ac + parent_ac:])
                    require(child == target and extent > 0, 'non-identity bus range unsupported')
                    windows.append((child, child + extent))
                require(all(any(low <= a and a + n <= high for low, high in windows)
                            for a, n in result), 'resource outside bus ranges')
            bus = bus.rsplit('/', 1)[0]
        return result


def dt_evidence(live, shared):
    t = Tree(live)
    hc = t.find('ufshc@1d84000')
    phy = t.find('ufsphy_mem@1d87000')
    gcc = t.find('qcom,gcc@100000')
    smmu = t.find('apps-smmu@15000000')
    result = {}
    for key, path in [('hc', hc), ('phy', phy)]:
        node = t.nodes[path]
        item = {'path': path, 'reg_bus_address_length': t.reg(path),
                'lanes': one(node, 'lanes-per-direction'),
                'clocks': t.refs(path, 'clocks', '#clock-cells'),
                'clock_names': strings(node, 'clock-names'),
                'supplies': {p: t.refs(path, p) for p in node if p.endswith('-supply')},
                'status': strings(node, 'status'),
                'iommus_present': 'iommus' in node,
                'dma_coherent_present': 'dma-coherent' in node}
        require(len(item['clocks']) == len(item['clock_names']), 'clock names/count mismatch')
        require(item['lanes'] == 2, 'unexpected lane count')
        if item['iommus_present']:
            item['iommus'] = t.refs(path, 'iommus', '#iommu-cells')
        for refs in item['supplies'].values():
            require(len(refs) == 1, 'supply must reference one provider')
        result[key] = item
    require(set(result['hc']['supplies']) == {'vccq-supply', 'vccq2-supply', 'vcc-supply',
            'vdd-hba-supply', 'qcom,vddp-ref-clk-supply', 'qcom,vccq-parent-supply'},
            'missing/unexpected HC supply reference')
    require(set(result['phy']['supplies']) == {'vdda-pll-supply', 'vdda-phy-supply'},
            'missing/unexpected PHY supply reference')
    node = t.nodes[hc]
    result['hc']['resets'] = t.refs(hc, 'resets', '#reset-cells')
    result['hc']['phys'] = t.refs(hc, 'phys', '#phy-cells')
    require(result['hc']['phys'] == [{'provider': phy, 'args': [],
                                     'compatible': strings(t.nodes[phy], 'compatible')}],
            'unexpected HC PHY reference')
    result['hc']['pinctrl'] = {p: t.refs(hc, p) for p in ('pinctrl-0', 'pinctrl-1')}
    result['hc']['pinctrl_names'] = strings(node, 'pinctrl-names')
    # Include only electrical/reset attributes, never arbitrary DT properties.
    for prop, refs in result['hc']['pinctrl'].items():
        for ref in refs:
            provider = t.nodes[ref['provider']]
            require('config' in provider, 'missing reset pin configuration')
            config = provider['config']
            ref['settings'] = {k: config[k] for k in (
                'pins', 'function', 'output-high', 'output-low', 'bias-disable',
                'bias-pull-up', 'bias-pull-down', 'drive-strength') if k in config}
            require(strings(config, 'pins') == ['ufs_reset'] and
                    ('output-low' if prop == 'pinctrl-0' else 'output-high') in config,
                    'unexpected UFS reset pin configuration')
    parent = hc
    while 'interrupt-parent' not in t.nodes[parent]:
        parent = parent.rsplit('/', 1)[0] or '/'
        require(parent != '/' or 'interrupt-parent' in t.nodes[parent], 'missing interrupt-parent')
    ip = t.provider(one(t.nodes[parent], 'interrupt-parent'))
    require(one(t.nodes[ip], '#interrupt-cells') == 3, 'unexpected interrupt cell count')
    irq = cells(node, 'interrupts')
    require(irq == [0, 265, 4] and any('gic' in s for s in strings(t.nodes[ip], 'compatible')),
            'unexpected GIC SPI tuple')
    result['hc']['interrupt'] = {'provider': ip, 'tuple': irq, 'spi': irq[1],
                                 'architectural_intid': irq[1] + 32}
    require(result['hc']['reg_bus_address_length'] == [[0x1d84000, 0x3000], [0x1d90000, 0x8000]], 'HC/ICE mismatch')
    require(result['phy']['reg_bus_address_length'] == [[0x1d87000, 0xe00], [0x1d90000, 0x8000]], 'PHY/ICE mismatch')
    require(len(result['hc']['clocks']) == 9, 'expected nine HC clocks')
    require(len(result['hc']['resets']) == 1 and result['hc']['resets'][0]['provider'] == gcc and
            result['hc']['resets'][0]['args'] == [0x21], 'unexpected GCC reset ID')
    result['gcc'] = {'reg_bus_address_length': t.reg(gcc)}
    require(result['gcc']['reg_bus_address_length'] == [[0x100000, 0x1f0000]], 'GCC mismatch')
    result['smmu'] = {'reg_bus_address_length': t.reg(smmu),
                      'reg_names': strings(t.nodes[smmu], 'reg-names')}
    require(result['smmu']['reg_bus_address_length'] == [[0x15000000, 0x100000], [0x15182000, 0x20]], 'SMMU mismatch')
    s = Tree(shared, fragment=True)
    result['shared'] = {key: {'reg_bus_address_length': s.reg(s.find(name)),
                             'status': strings(s.nodes[s.find(name)], 'status')}
                        for key, name in [('hc', 'ufshc@1d84000'), ('phy', 'phy@1d87000')]}
    require(result['shared']['hc']['reg_bus_address_length'][0] ==
            result['hc']['reg_bus_address_length'][0], 'shared HC mismatch')
    require(all(item['status'] == ['disabled'] for item in result['shared'].values()),
            'shared HC/PHY must remain disabled')
    require(result['shared']['phy']['reg_bus_address_length'] == [[0x1d87000, 0x1000]], 'shared PHY mismatch')
    return result


def firmware_evidence(config, memory):
    def text(path):
        return re.sub(r'/\*.*?\*/|//[^\n]*', '', path.read_text(), flags=re.S)
    cfg, mem = text(config), text(memory)
    result = {}
    for key in ('EnableUfsIOC', 'UfsSmmuConfigForOtherBootDev'):
        values = re.findall(r'\{\s*"' + key + r'"\s*,\s*(0x[0-9a-fA-F]+|[0-9]+)\s*\}', cfg)
        require(len(values) == 1, f"missing/ambiguous firmware entry {key}")
        result[key] = int(values[0], 0)
    maps = re.findall(r'\{\s*"SMMU"\s*,\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*,', mem)
    require(len(maps) == 1, 'missing/ambiguous firmware SMMU map')
    result['smmu_map_base_length'] = [int(x, 0) for x in maps[0]]
    require(result['EnableUfsIOC'] == 0 and result['UfsSmmuConfigForOtherBootDev'] == 1,
            'firmware UFS configuration changed')
    require(result['smmu_map_base_length'] == [0x15000000, 0xd0000], 'firmware SMMU map changed')
    return result


def gpt_evidence(blob, block_bytes, linux_sectors):
    require(block_bytes == 4096, 'GPT logical block size must be 4096')
    require(0 < linux_sectors <= ((1 << 64) - 1) // 512, 'capacity overflow/zero')
    total_bytes = linux_sectors * 512  # Linux sysfs size is always in 512-byte sectors.
    require(total_bytes % block_bytes == 0, 'unaligned capacity')
    blocks = total_bytes // block_bytes
    require(len(blob) >= 2 * block_bytes, 'truncated GPT header')
    require(blob[510:512] == b'\x55\xaa', 'missing protective MBR signature')
    require(any(blob[446 + i * 16 + 4] == 0xee for i in range(4)), 'missing protective MBR entry')
    h = blob[block_bytes:2 * block_bytes]
    signature, rev, size, crc, reserved, current, backup, first, last, _, entries, count, stride, array_crc = struct.unpack_from('<8sIIIIQQQQ16sQIII', h)
    require(signature == b'EFI PART' and rev == 0x10000 and reserved == 0 and 92 <= size <= block_bytes,
            'invalid GPT header')
    check = bytearray(h[:size])
    check[16:20] = b'\0' * 4
    require(zlib.crc32(check) == crc, 'GPT header CRC mismatch')
    require(current == 1 and backup == blocks - 1 and current < first <= last < backup,
            'GPT geometry outside capacity')
    require(count > 0 and stride >= 128 and stride & (stride - 1) == 0, 'invalid GPT entry geometry')
    length = count * stride
    offset = entries * block_bytes
    require(offset <= (1 << 64) - 1 and length <= (1 << 64) - 1 - offset,
            'GPT entry window overflow')
    array_blocks = (length + block_bytes - 1) // block_bytes
    require(entries >= 2 and entries + array_blocks <= first and last < backup - array_blocks,
            'GPT metadata overlaps usable space')
    require(offset + length <= len(blob), 'truncated GPT entries')
    raw = blob[offset:offset + length]
    require(zlib.crc32(raw) == array_crc, 'GPT entry CRC mismatch')
    ranges, userdata = [], []
    for i in range(count):
        entry = raw[i * stride:(i + 1) * stride]
        if entry[:16] == b'\0' * 16:
            continue
        start, end = struct.unpack_from('<QQ', entry, 32)
        require(first <= start <= end <= last, 'partition outside usable GPT range')
        require(end < blocks and (end + 1) * block_bytes <= total_bytes,
                'partition byte window overflow/out of capacity')
        ranges.append((start, end))
        name = entry[56:128].decode('utf-16-le').split('\0', 1)[0]
        if name == 'userdata':
            userdata.append({'first_lba': start, 'last_lba_inclusive': end,
                             'blocks': end - start + 1, 'bytes': (end - start + 1) * block_bytes})
    ranges.sort()
    require(all(a[1] < b[0] for a, b in zip(ranges, ranges[1:])), 'overlapping GPT partitions')
    require(len(userdata) == 1, 'missing/ambiguous userdata')
    return {'status': 'primary_snapshot_checked', 'logical_block_bytes': block_bytes,
            'linux_size_sector_bytes': 512, 'linux_size_sectors': linux_sectors,
            'total_bytes': total_bytes, 'total_logical_blocks': blocks,
            'usable_first_lba': first, 'usable_last_lba': last,
            'userdata': userdata[0], 'backup_gpt': 'UNKNOWN: not captured',
            'current_device_geometry': 'UNKNOWN: historical snapshot only'}


def collect(root=ROOT):
    pkg = root.parent / 'uefi-enuma/Platforms/Xiaomi/enumaPkg/Library'
    live = root / '.cache/device-evidence/20261109-live-dt/live.dts'
    shared = root.parent / 'UniXNU-sm8250-common/dts/sm8250.dtsi'
    config = pkg / 'ConfigurationMapLib/ConfigurationMapLib.c'
    memory = pkg / 'MemoryMapLib/MemoryMapLib.c'
    report = {'scope': 'host-only input validation; NOT activation readiness',
              'validation': 'self-checked', 'unknown': UNKNOWN.copy(),
              'shengufs_reference': {'revision': REFERENCE, 'integration': 'not integrated',
                  'nonportable_assumptions': ['SM8550 probe', 'GCC', 'SID 0x60']},
              'dt': dt_evidence(live, shared), 'firmware': firmware_evidence(config, memory),
              'historical_partition_identity': {
                  'provenance': 'parent-relayed luna read-only inspection; not reparsed by checker',
                  'capture': '.cache/live-capture/20261107T141941555586Z',
                  'by_name_source': 'by_name_links.txt:110',
                  'by_name_mapping': 'userdata -> /dev/block/sda34',
                  'proc_source': 'proc_partitions.txt:70',
                  'proc_partition': {'major': 259, 'minor': 18, 'name': 'sda34',
                                     'capacity_units': 236773356, 'unit_bytes': 1024},
                  'missing_link': 'UFS host -> SCSI H:C:T:L -> [sda] absent from captured dmesg first/last400; no other local capture found by luna',
                  'linux_sda_to_lun': 'UNKNOWN',
              }}
    inputs = [live, shared, config, memory]
    capture = root / '.cache/live-capture/20261107T141941555586Z'
    paths = [capture / name for name in ('sda_first_32768.bin', 'sda_logical_block_size.txt', 'sda_sectors.txt')]
    if all(p.is_file() for p in paths):
        report['gpt'] = gpt_evidence(paths[0].read_bytes(), int(paths[1].read_text().strip()),
                                     int(paths[2].read_text().strip()))
        inputs += paths
    else:
        report['gpt'] = {'status': 'UNKNOWN', 'reason': 'original capture incomplete/missing; prose is not validation'}
    # Paths and whole-input hashes stay only in the ignored machine report.
    report['inputs'] = [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]
    return report


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    destination = ROOT / '.cache/ufs-evidence/report.json'
    subprocess.run(['git', '-C', str(ROOT), 'check-ignore', '-q', str(destination)], check=True)
    try:
        report = collect()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, yaml.YAMLError) as exc:
        # Do not persist arbitrary parser diagnostics or source text/identity.
        report = {'validation': 'REJECTED', 'error_type': type(exc).__name__, 'unknown': UNKNOWN.copy()}
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2) + '\n')
        if isinstance(exc, (ValueError, KeyError)):
            print(f'REJECTED: {exc}')
        else:
            print(f'REJECTED: {type(exc).__name__}; input/tool failure')
        return 1
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print('self-checked: DT/firmware inputs; GPT=' + report['gpt']['status'])
    print('report: .cache/ufs-evidence/report.json; runtime ownership remains UNKNOWN')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
