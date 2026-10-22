"""Audit a proposed persistent log range without changing memory or boot images."""
import hashlib
import json
from pathlib import Path
import re
import struct
import tarfile
from audit_inputs import parse_fdt,cells,strings
ROOT=Path(__file__).resolve().parents[1]


def main():
    platform=json.loads((ROOT/'reports/enuma-platform-config.json').read_text())
    regions=[v for v in platform['regions'] if v['name']=='Log Buffer']
    if len(regions)!=1:raise ValueError('ambiguous OEM Log Buffer')
    region=regions[0];base=region['base'];size=region['size'];end=base+size
    if base%4096 or size%4096:raise ValueError('log range is not page aligned')
    blob=(ROOT/'out/device/live-fdt.bin').read_bytes();nodes=parse_fdt(blob)
    if hashlib.sha256(blob).hexdigest()!='643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62':
        raise ValueError('live FDT changed; recapture/review required')
    parent=nodes['/reserved-memory']
    if cells(parent['#address-cells'])!=[2] or cells(parent['#size-cells'])!=[2]:
        raise ValueError('unsupported reservation address layout')
    covering=[];banks=[]
    for path,props in nodes.items():
        if 'reg' not in props:continue
        is_reserved=path.startswith('/reserved-memory/') and path.count('/')==2
        is_memory=strings(props.get('device_type',b''))==['memory']
        if not (is_reserved or is_memory):continue
        raw=cells(props['reg'])
        if len(raw)%4:raise ValueError('unsupported memory reg tuple')
        for i in range(0,len(raw),4):
            start=(raw[i]<<32)|raw[i+1];length=(raw[i+2]<<32)|raw[i+3]
            entry={'node':path,'base':hex(start),'bytes':hex(length)}
            if is_reserved and start<=base and end<=start+length:covering.append(entry)
            if is_memory and start<end and base<start+length:banks.append(entry)
    reservations=[];offset=struct.unpack_from('>I',blob,16)[0]
    while offset+16<=len(blob):
        start,length=struct.unpack_from('>QQ',blob,offset);offset+=16
        if start==0 and length==0:break
        reservations.append({'base':hex(start),'bytes':hex(length),'covers_log':start<=base and end<=start+length})
    else:raise ValueError('unterminated FDT reserve map')
    iomem=ROOT/'out/device/iomem.stdout';ranges=[]
    for line in iomem.read_text().splitlines():
        m=re.match(r'\s*([0-9a-f]+)-([0-9a-f]+) : (.*)',line)
        if m and int(m[1],16)<end and base<=int(m[2],16):ranges.append(line.strip())
    pages=json.loads((ROOT/'out/mainline/log-buffer-pageflags.local.json').read_text())
    if pages.get('physical_base')!=base or pages.get('page_shift')!=12:
        raise ValueError('page flag sample target/layout mismatch')
    if pages.get('returncode')!=0 or pages.get('bytes')!=size//4096*8:
        raise ValueError('missing complete read-only page flag sample')
    with tarfile.open(ROOT/'out/log-readback/kheaders.tar.xz') as source:
        member=next(m for m in source.getmembers() if m.name.endswith('/include/linux/kernel-page-flags.h'))
        header=source.extractfile(member).read()
        member=next(m for m in source.getmembers() if m.name.endswith('/include/generated/autoconf.h'))
        config=source.extractfile(member).read()
    if not re.search(rb'#define\s+KPF_RESERVED\s+32\b',header):raise ValueError('reserved flag definition changed')
    if not re.search(rb'#define\s+CONFIG_ARM64_PAGE_SHIFT\s+12\b',config):raise ValueError('kernel page size differs')
    flags=[int(v,16) for v in pages['page_flags']]
    if len(flags)!=size//4096:raise ValueError('wrong page flag count')
    reserved=[bool(v&(1<<32)) for v in flags]
    unprotected=bool(banks) and not covering and not any(r['covers_log'] for r in reservations) and not any(reserved)
    report={'scope':'read-only audit, no memory writes, module loading, reservations or image changes',
        'review':'R-002 pending','oem_region':region,'source_xbl_sha256':platform['source_xbl_sha256'],
        'live_fdt_sha256':hashlib.sha256(blob).hexdigest(),'covering_reserved_memory_nodes':covering,
        'overlapping_memory_banks':banks,'fdt_header_reservations':reservations,'kernel_iomem_covering_ranges':ranges,
        'kernel_iomem_sha256':hashlib.sha256(iomem.read_bytes()).hexdigest(),
        'kernel_page_reserved_bits':reserved,'page_flags_source_sha256':hashlib.sha256(header).hexdigest(),
        'kernel_page_size':4096,'kernel_autoconf_sha256':hashlib.sha256(config).hexdigest(),
        'linux_reclaims_candidate_range':unprotected,
        'safe_to_use_for_persistent_log_now':False,
        'conclusion':'Do not write/read this as retained UEFI log: Linux treats it as ordinary pages. A dedicated reservation plus survival/readback tests or external UART is needed.' if unprotected else 'Reservation ownership requires further review; no logger enabled.'}
    (ROOT/'reports/enuma-log-reservation-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('AUDIT: ordinary Linux pages='+str(unprotected)+'; persistent logging remains disabled; R-002 pending')


if __name__=='__main__':main()
