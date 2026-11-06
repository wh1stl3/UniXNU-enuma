"""Verify reviewed upstream blobs and explicit applicability limits; no device I/O."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    lock = json.loads((ROOT/'config/upstream-route-review-20261025.lock.json').read_text())
    blobs = {}
    for entry in lock['references']:
        repo = ROOT/entry['local']
        for name, item in entry['files'].items():
            data = subprocess.check_output(['git','-C',str(repo),'show',entry['commit']+':'+name])
            if hashlib.sha256(data).hexdigest()!=item['sha256'] or len(data)!=item['bytes']:
                raise ValueError('reviewed source differs: '+name)
            blobs[(repo.name,name)] = data.decode('utf-8')
    ram = blobs[('UniXNU-latest-review','package/UniXNUPkg/Driver/UniXNURamDiskDxe/UniXNURamDiskDxe.c')]
    if '((End - Start) % RAM_BLOCK_SIZE) != 0' not in ram:
        raise ValueError('shared RAM initrd contract changed')
    payload = json.loads((ROOT/'reports/enuma-full-payload.json').read_text())
    # Concrete ABL prefix from the separate saved-input audit; no live RAM read.
    transport = json.loads((ROOT/'reports/enuma-payload-transport.json').read_text())
    prefix = transport['vendor_ramdisk_bytes']
    if prefix != 2230:
        raise ValueError('saved vendor prefix differs from reviewed input')
    if (prefix+payload['payload_bytes']) % 512 == 0:
        raise ValueError('expected prefix sector incompatibility differs')
    hardware = blobs[('uefi-cas-review','Platforms/Xiaomi/casPkg/Library/CasDisplayLib/DisplayHardware.c')]
    if 'CAS_MDP_BASE + B + 0x1c) = 1;' not in hardware:
        raise ValueError('cas command refresh write contract changed')
    gop = blobs[('uefi-cas-review','Platforms/Xiaomi/casPkg/Drivers/CasGopDxe/CasGopDxe.c')]
    if 'EfiBltVideoFill' not in gop or 'CasDisplayRefresh' not in gop:
        raise ValueError('cas GOP write behavior changed')
    cas = next(x for x in lock['references'] if Path(x['local']).name=='uefi-cas-review')
    delta = subprocess.check_output(['git','-C',str(ROOT/cas['local']),'diff','--name-only',
        '893f5025cea91a121f2566730779cb34955325fb',cas['commit'],'--','Platforms/Xiaomi/casPkg'],text=True)
    if delta.strip():
        raise ValueError('cas implementation differs from the hardware-tested tag')
    log = (ROOT/'out/upstream-review-20261025/cas-display-host-test.log').read_text()
    if 'Ran 16 tests' not in log or not log.rstrip().endswith('OK'):
        raise ValueError('actual cas pure decoder/Blt host suite did not pass')
    report = dict(scope='source reuse review and host decoder test only; no new device trial',
        reviewed_repositories=len(lock['references']),
        reviewed_files=sum(len(x['files']) for x in lock['references']),
        cas_tested_firmware='893f5025cea91a121f2566730779cb34955325fb',
        cas_platform_delta_from_tested=[], cas_decoder_host_tests=16,
        host_test_log_sha256=hashlib.sha256(log.encode()).hexdigest(),
        shared_ram_prefix_contract=dict(prefix_bytes=prefix,fat_bytes=payload['payload_bytes'],
            whole_initrd_sector_remainder=(prefix+payload['payload_bytes'])%512,
            scope='predicted exact concatenation contract, not a runtime FDT measurement'),
        cas_contains_pixel_and_CTL_START_writes=True,
        can_copy_board_addresses_or_approve_execution=False,
        recommendation='Evaluate cas pure scanout decode for enuma offline, preserving own bounds; restore real GOP before QR logs; keep OEM service probes as fallback',
        limits=['cas and umi hardware results belong to their specific variants and revisions',
                'QR menu needs working graphics/input and logger producer; it cannot diagnose a pre-menu hang alone',
                'new framework migration is separate from this firmware fault; build pins stay unchanged',
                'host synthetic snapshots do not establish enuma scanout or authorize pixel/MMIO writes'])
    (ROOT/'reports/enuma-latest-porting-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: reviewed pins, cas tested-platform identity and 16 host tests; no device operation')


if __name__=='__main__':
    main()
