"""Linux host sanitizer tests and freestanding AArch64 compilation; no device I/O."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True, timeout=60)
    record = {'argv': [str(x) for x in command], 'exit_code': result.returncode,
              'stdout': result.stdout, 'stderr': result.stderr}
    if result.returncode:
        raise RuntimeError(json.dumps(record))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unixnu', type=Path, required=True)
    args = parser.parse_args()
    gen = args.unixnu / 'drivers/NativeGeniSpi'
    local = ROOT / 'drivers/EnumaPlatform'
    pins = json.loads((local / 'sources.json').read_text())
    for relative, expected in pins['geni_sha256'].items():
        if digest(gen / relative) != expected:
            raise ValueError(f'GENI source pin mismatch: {relative}')
    gcc = ROOT / 'out/references/Xiaomi_Kernel_OpenSource/drivers/clk/qcom/gcc-kona.c'
    if digest(gcc) != pins['gcc_sha256']:
        raise ValueError('Kona GCC source pin mismatch')
    text = gcc.read_text()
    names = ['axi', 'ahb', 'aggre', 'unipro', 'ice', 'aux', 'tx0', 'rx0', 'rx1']
    symbols = ['gcc_ufs_phy_axi_clk', 'gcc_ufs_phy_ahb_clk', 'gcc_aggre_ufs_phy_axi_clk',
               'gcc_ufs_phy_unipro_core_clk', 'gcc_ufs_phy_ice_core_clk', 'gcc_ufs_phy_phy_aux_clk',
               'gcc_ufs_phy_tx_symbol_0_clk', 'gcc_ufs_phy_rx_symbol_0_clk', 'gcc_ufs_phy_rx_symbol_1_clk']
    facts = []
    for name, symbol in zip(names, symbols):
        block = re.search(r'static struct clk_branch ' + symbol + r' = \{(.*?)\n\};', text, re.S)
        if not block:
            raise ValueError(f'missing branch {symbol}')
        offset = int(re.search(r'\.enable_reg = (0x[0-9a-fA-F]+)', block[1])[1], 16)
        facts.append({'name': name, 'symbol': symbol, 'enable_reg': offset,
                      'line': text[:block.start()].count('\n') + 1})
    local_text = (local / 'EnumaUfsClock.c').read_text()
    array = re.search(r'offsets\[ENUMA_UFS_CLOCK_COUNT\] = \{(.*?)\};', local_text, re.S)[1]
    if [int(v, 16) for v in re.findall(r'0x[0-9a-fA-F]+', array)] != [f['enable_reg'] for f in facts]:
        raise ValueError('local UFS offsets disagree with pinned manufacturer branches')
    out = ROOT / 'out/enuma-drivers'; out.mkdir(parents=True, exist_ok=True)
    flags = ['clang', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I'+str(gen), '-I'+str(local)]
    sanitizer = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
    records = []
    records.append(run([*flags, *sanitizer, '-DGENI_TEST_SOURCE="'+str(gen / 'Test/geni-spi.c')+'"',
                        ROOT/'tests/enuma_spi.c', local/'EnumaGeniSpi.c', gen/'GeniSpi.c', '-o', out/'spi-test']))
    records.append(run([out/'spi-test']))
    records.append(run([*flags, *sanitizer, ROOT/'tests/enuma_ufs_clock.c', local/'EnumaUfsClock.c', '-o', out/'ufs-clock-test']))
    records.append(run([out/'ufs-clock-test']))
    for source in [local/'EnumaGeniSpi.c', local/'EnumaUfsClock.c', gen/'GeniSpi.c']:
        records.append(run([*flags, '--target=aarch64-none-elf', '-ffreestanding', '-fno-builtin', '-O2',
                            '-c', source, '-o', out/(source.stem+'.o')]))
    report = {'scope': 'host register model and AArch64 objects; not IOKit link, QEMU or hardware execution',
              'gcc_branch_facts': facts, 'checks': records,
              'objects': {p.name: digest(p) for p in out.glob('*.o')},
              'local_sources': {p.name: digest(p) for p in local.glob('*.[ch]')}}
    (ROOT/'reports/enuma-driver-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: upstream GENI + enuma adapter, nine Kona GCC facts, atomic snapshots, three AArch64 objects')


if __name__ == '__main__':
    main()
