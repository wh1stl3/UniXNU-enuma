"""Compare the captured OEM APRIORI with selected drivers and real Mu services."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import tarfile
import uuid
from uefi_firmware.uefi import FirmwareVolume, FirmwareFile
from extract_enuma_xbl import EXPECTED
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xbl',type=Path,default=ROOT/'out/device/xbl_a.bin')
    args=parser.parse_args()
    inventory=json.loads((ROOT/'reports/enuma-oem-modules.json').read_text())
    blob=args.xbl.read_bytes()
    if hashlib.sha256(blob).hexdigest()!=EXPECTED or inventory['xbl_sha256']!=EXPECTED:
        raise ValueError('XBL differs from captured enuma')
    offset=inventory['fv_offset'];size=struct.unpack_from('<Q',blob,offset+32)[0]
    if offset+size>len(blob):raise ValueError('FV bounds')
    volume=FirmwareVolume(blob[offset:offset+size])
    if not volume.process():raise ValueError('FV parse failed')
    queue=[volume];files={};order=[]
    while queue:
        item=queue.pop(0);queue.extend(getattr(item,'objects',[]))
        if not isinstance(item,FirmwareFile) or item.type==0xf0:continue
        guid=str(uuid.UUID(bytes_le=item.guid));sections=item.objects
        names=[s.data.decode('utf-16-le').rstrip('\0') for s in sections if s.type==0x15]
        if guid in files:raise ValueError('duplicate OEM file GUID')
        files[guid]={'name':names[0] if names else guid,'guid':guid}
        if guid=='fc510ee7-ffdc-11d4-bd41-0080c73c8881':
            data=next(s.data for s in sections if s.type==0x19)
            if len(data)%16:raise ValueError('APRIORI GUID size')
            order=[str(uuid.UUID(bytes_le=data[i:i+16])) for i in range(0,len(data),16)]
    if len(order)!=inventory['oem_apriori_count']:raise ValueError('APRIORI count differs')
    selected={m['guid'] for m in inventory['selected_modules']}
    entries=[dict(files[g],selected=g in selected,original_ordinal=i+1) for i,g in enumerate(order)]
    ufs=next(i for i,e in enumerate(entries) if e['name']=='UFSDxe')
    hashes={}
    archive=ROOT/'out/firmware-build/mu-basecore.tar.gz'
    lock=json.loads((ROOT/'config/firmware-build.lock.json').read_text())
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=lock['archive_sha256']['mu-basecore.tar.gz']:
        raise ValueError('Mu archive changed')
    with tarfile.open(archive) as source:
        for name in ('MdeModulePkg/Core/Dxe/Misc/Stall.c','EmbeddedPkg/MetronomeDxe/Metronome.c',
                     'EmbeddedPkg/MetronomeDxe/MetronomeDxe.inf'):
            member=next(m for m in source.getmembers() if m.name.endswith('/'+name))
            data=source.extractfile(member).read().replace(b'\r\n',b'\n')
            if (ROOT/'out/firmware-build/Mu_Basecore'/name).read_bytes().replace(b'\r\n',b'\n')!=data:
                raise ValueError('Mu service source changed: '+name)
            hashes[name]=hashlib.sha256(data).hexdigest()
    report={'scope':'static original XBL APRIORI comparison; omitted OEM entries may have Mu replacements, no runtime/provider proof',
        'xbl_sha256':EXPECTED,'original_apriori':entries,
        'unselected_before_ufs':[e for e in entries[:ufs] if not e['selected']],
        'fixed_mu_commit':lock['reference_gitlinks']['Mu_Basecore'],'fixed_mu_sources_sha256':hashes,
        'mu_service_comparison':{'metronome':{'already_packaged':True,'previously_early':False,
            'new_early_patch':'firmware/patches/apriori-metronome.patch',
            'driver':'EmbeddedPkg/MetronomeDxe/MetronomeDxe.inf',
            'oem_ordinal':next(e['original_ordinal'] for e in entries if e['name']=='MetronomeDxe'),
            'core_stall_source':'MdeModulePkg/Core/Dxe/Misc/Stall.c:57',
            'behavior_without_protocol':'EFI_NOT_AVAILABLE_YET','hardware_causality_for_ufs':'not established by this static audit'},
            'other_unselected_oem_entries':'Some have Mu replacements; packaging does not prove early dispatch or protocol installation.'}}
    (ROOT/'reports/enuma-oem-apriori-gap-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: original '+str(len(entries))+' APRIORI entries and three fixed Mu service sources; runtime closure unproven')


if __name__=='__main__':main()
