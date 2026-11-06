"""Reuse the pinned BootShim with a bounded, display-independent PSCI reset gate.

This diagnostic never writes a partition. The selected gate deliberately resets
instead of continuing; a returned reset call loops for manual recovery.
"""
import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def instrument(source, stage, seconds):
    if stage not in ('shim-entry', 'shim-copy') or seconds not in (2, 7):
        raise ValueError('unsupported diagnostic gate/delay')
    if stage == 'shim-entry':
        old, new = '_Start:\n', '_Start:\n  b .LEnumaResetGate\n'
    else:
        old, new = '  br    x5\n', '  b .LEnumaResetGate\n'
    if source.count(old) != 1: raise ValueError('BootShim hook changed')
    source = source.replace(old, new)
    marker = '\n.text\n.ltorg\n'
    if source.count(marker) != 1: raise ValueError('BootShim literal pool changed')
    # PSCI ID matches the fixed Mu ArmStdSmc.h / ArmPsciResetSystemLib.
    # No stack, display, memory marker or SoC MMIO is required. Linux's entry
    # contract supplies EL1/EL2 with IRQ/FIQ masked and the MMU off.
    gate = f'''
.LEnumaResetGate:
  msr daifset, #15
  mrs x11, cntfrq_el0
  cbz x11, .LEnumaResetNow
  mov x12, #{seconds}
  mul x11, x11, x12
  mrs x12, cntpct_el0
.LEnumaResetWait:
  mrs x13, cntpct_el0
  sub x13, x13, x12
  cmp x13, x11
  b.lo .LEnumaResetWait
.LEnumaResetNow:
  mov x0, #9
  movk x0, #0x8400, lsl #16
  mov x1, xzr
  mov x2, xzr
  mov x3, xzr
  smc #0
.LEnumaResetReturned:
  wfe
  b .LEnumaResetReturned
'''
    return source.replace(marker, gate + marker)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unixnu', type=Path, required=True)
    parser.add_argument('--stage', choices=('shim-entry', 'shim-copy'), required=True)
    parser.add_argument('--seconds', type=int, choices=(2, 7), default=2)
    parser.add_argument('--qemu', action='store_true')
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        import tomli
        sys.modules['tomllib'] = tomli
    lock = json.loads((ROOT/'config/porting-sources.lock.json').read_text())
    for name in ('scripts/unixnu/bootimg.py', 'scripts/unixnu/util.py'):
        if hashlib.sha256((args.unixnu/name).read_bytes()).hexdigest() != lock['unixnu_interface_sha256'][name]:
            raise ValueError('compiler source pin mismatch')
    baseline = json.loads((ROOT/'reports/enuma-boot-payload.json').read_text())
    original = ROOT/'out/firmware-build/uefi/BootShim/BootShim.S'
    if hashlib.sha256(original.read_bytes()).hexdigest() != baseline['shim_source_sha256']:
        raise ValueError('baseline BootShim changed')
    build = json.loads((ROOT/'reports/enuma-firmware-build.json').read_text())
    fd = (ROOT/build['fd']).read_bytes()
    if hashlib.sha256(fd).hexdigest() != build['fd_sha256'] or len(fd) != 0x300000:
        raise ValueError('baseline FD mismatch')
    out = ROOT/'out/entry-probe'/f'{args.stage}-{args.seconds}s'
    if out.exists(): raise ValueError('refuse diagnostic overwrite')
    (out/'BootShim').mkdir(parents=True)
    (out/'BootShim/BootShim.S').write_text(instrument(original.read_text(), args.stage, args.seconds))
    sys.path.insert(0, str(args.unixnu/'scripts'))
    from unixnu.bootimg import compile_shim
    shim = compile_shim(out, 0x9fc00000, len(fd), True, out)
    raw = out/'kernel.raw'; raw.write_bytes(shim+fd)
    (out/'empty-ramdisk').write_bytes(b'')
    report = {'scope':'diagnostic BootShim only; selected stage resets before continuing',
              'stage':args.stage,'delay_seconds':args.seconds,'raw_path':str(raw.relative_to(ROOT)),
              'raw_sha256':hashlib.sha256(shim+fd).hexdigest(),'shim_bytes':len(shim),
              'fd_sha256':build['fd_sha256'],'text_offset':hex(struct.unpack_from('<Q',shim,8)[0]),
              'image_size':len(shim)+len(fd),'fd_destination':'0x9fc00000',
              'baseline_shim_sha256':baseline['shim_source_sha256'],
              'instrumented_source_sha256':hashlib.sha256((out/'BootShim/BootShim.S').read_bytes()).hexdigest(),
              'reset_service':'PSCI SYSTEM_RESET 0x84000009 via SMC; fixed Mu implementation reference',
              'hardware_execution':'not attempted by this script'}
    if args.qemu:
        argv=['qemu-system-aarch64','-machine','virt,virtualization=on','-cpu','max','-m','4G',
              '-kernel',str(raw),'-display','none','-serial','none','-monitor','none','-nic','none',
              '-no-reboot','-d','in_asm,guest_errors','-D',str(out/'qemu.log')]
        before=time.monotonic()
        try:
            result=subprocess.run(argv,capture_output=True,text=True,timeout=15)
            record={'exit_code':result.returncode,'elapsed_seconds':round(time.monotonic()-before,3),'stderr':result.stderr}
        except subprocess.TimeoutExpired:
            record={'exit_code':None,'timeout':True,'elapsed_seconds':round(time.monotonic()-before,3)}
        trace=(out/'qemu.log').read_text(errors='replace')
        record['smc_instruction_observed']='smc' in trace
        record['argv']=argv
        report['qemu']=record
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__': main()
