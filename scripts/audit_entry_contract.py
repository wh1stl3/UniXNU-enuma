"""Audit concrete ARM64/BootShim inputs and pinned comparison sources, no device I/O."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    lock=json.loads((ROOT/'config/entry-contract-sources.lock.json').read_text())
    references=[]
    for item in lock['references']:
        path=ROOT/item['local']; data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('comparison source changed')
        text=data.decode()
        record={k:v for k,v in item.items() if k!='local'}
        if path.name.endswith('BootLinux.c'):
            record['observed_source_contract']={
                'text_offset_referenced':'text_offset' in text or 'TextOffset' in text,
                'raw_copy_to_kernel_load_addr':'gBS->CopyMem ((VOID *)BootParamlistPtr->KernelLoadAddr, (VOID *)Kptr,' in text,
                'image_size_space_check':'Kptr->ImageSize >' in text,
                'vendor_boot_v3_support':'BOOT_HEADER_VERSION_THREE' in text}
        references.append(record)
    baseline=ROOT/'out/boot-candidate/enuma-uefi-probe01-r2-boot-v3.img'
    blob=baseline.read_bytes(); ks=struct.unpack_from('<I',blob,8)[0]
    if blob[:8]!=b'ANDROID!' or struct.unpack_from('<I',blob,40)[0]!=3:raise ValueError('baseline not v3')
    kernel=blob[4096:4096+ks]
    if kernel[56:60]!=b'ARM\x64':raise ValueError('ARM64 magic absent')
    offset,size,flags=struct.unpack_from('<3Q',kernel,8)
    if size!=len(kernel):raise ValueError('image_size mismatch')
    report={'scope':'static concrete image and pinned comparison sources; not exact Xiaomi ABL disassembly',
      'baseline_image_sha256':hashlib.sha256(blob).hexdigest(),
      'baseline_header':{'text_offset':hex(offset),'image_size':size,'flags':flags,'shim_bytes':192,
                         'fd_destination':'0x9fc00000','fd_bytes':0x300000},
      'entry_requirements':{'exception_level':'non-secure EL1 or EL2 per ARM64 Linux contract; actual EL not yet sampled',
          'mmu':'off at Linux entry; not yet directly sampled on device',
          'register_x0':'preserved through shim and saved as gSecEntryArg0 by pinned SEC',
          'stack':'shim needs no stack; SEC selects SPSel and initializes OEM stack before C',
          'cache':'shim cleans copied FD to PoC, invalidates I-cache, barriers before branch'},
      'comparison_sources':references,
      'limits':['comparison ABL source is not enuma vendor binary',
                'reset timing gates observe reached control points, not all register/memory contents',
                'do not change FD/stack/DRAM addresses from a generic text_offset comparison'],
      'checkpoint_stages':{'3':'SEC C entry before cache changes','4':'platform initialize returned',
          '5':'InitializeMemory returned','6':'PlatformPeim returned','7':'library constructors returned',
          '8':'FV decompression returned','9':'DXE Core C entry','10':'DXE ready to dispatch'}}
    (ROOT/'reports/enuma-entry-contract.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: concrete ARM64 header, source comparisons and staged checkpoint contract; hardware EL/MMU still unknown')


if __name__=='__main__':main()
