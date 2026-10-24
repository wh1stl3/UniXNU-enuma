"""Audit packaged native modules and loader interfaces in the built FD; no boot."""
import argparse
import hashlib
import json
import subprocess
import re
import uuid
from pathlib import Path
from uefi_firmware.uefi import FirmwareVolume, FirmwareFile
from firmware_audit_policy import omitted_oem_modules

ROOT = Path(__file__).resolve().parents[1]


def digest(data): return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fd', type=Path, default=ROOT / 'out/firmware-build/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd')
    parser.add_argument('--build-report',type=Path,default=ROOT/'reports/enuma-firmware-build.json')
    parser.add_argument('--report',type=Path,default=ROOT/'reports/enuma-fd-audit.json')
    args = parser.parse_args()
    blob = args.fd.read_bytes()
    if len(blob) != 0x300000 or blob[40:44] != b'_FVH': raise ValueError('unexpected FD envelope')
    volume = FirmwareVolume(blob)
    if not volume.process(): raise ValueError('cannot decode built FD')
    queue = [volume]; files = {}; pe_payloads = {}; apriori=[]
    while queue:
        obj = queue.pop(0); queue.extend(getattr(obj, 'objects', []))
        if not isinstance(obj, FirmwareFile) or obj.type == 0xf0: continue
        guid = str(uuid.UUID(bytes_le=obj.guid))
        if guid in files: raise ValueError('duplicate firmware file GUID: ' + guid)
        sections = obj.objects
        if guid=='fc510ee7-ffdc-11d4-bd41-0080c73c8881':
            raw=next(s.data for s in sections if s.type==0x19)
            if len(raw)%16:raise ValueError('invalid APRIORI GUID array')
            apriori=[str(uuid.UUID(bytes_le=raw[i:i+16])) for i in range(0,len(raw),16)]
        names = [s.data.decode('utf-16-le').rstrip('\0') for s in sections if s.type == 0x15]
        files[guid] = {'name': names[0] if names else guid,
                       'pe': [digest(s.data) for s in sections if s.type == 0x10],
                       'depex': [digest(s.data) for s in sections if s.type == 0x13]}
        pe_payloads[files[guid]['name']] = [s.data for s in sections if s.type == 0x10]
    inventory = json.loads((ROOT / 'reports/enuma-oem-modules.json').read_text())
    build=json.loads(args.build_report.read_text()) if args.build_report.exists() else {}
    omitted=omitted_oem_modules(build,digest(blob))
    if not apriori or any(g not in files for g in apriori):
        raise ValueError('APRIORI missing or references an absent firmware file')
    matched = []
    for module in inventory['selected_modules']:
        packaged = files.get(module['guid'])
        if module['name'] in omitted:
            if packaged:raise ValueError('diagnostically excluded module still packaged: '+module['name'])
            if module['guid'] in apriori:raise ValueError('excluded driver still in APRIORI')
            continue
        if not packaged or packaged['pe'] != [module['pe_sha256']]:
            raise ValueError('OEM PE bytes changed/missing: ' + module['name'])
        expected = [module['depex_sha256']] if module['depex_sha256'] else []
        if packaged['depex'] != expected: raise ValueError('OEM DEPEX changed: ' + module['name'])
        matched.append(module['name'])
    names = {item['name'] for item in files.values()}
    for required in ('EnumaProbe', 'UniXNU', 'UniXNUDxe', 'DarwinBoot', 'DisplayDxe', 'DDRInfoDxe', 'EnvDxe'):
        if required not in names and required not in omitted: raise ValueError('required module missing: ' + required)
    if 'DisplayDxe' in omitted:
        simple_guid='dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92'
        if 'SimpleFbDxe' not in names or apriori.count(simple_guid)!=1:
            raise ValueError('diagnostic SimpleFb provider missing or not unique in APRIORI')
        if apriori.index(simple_guid)!=32:
            raise ValueError('SimpleFb must replace the audited Display APRIORI position 33; do not guess probe ordinal')
    elif 'SimpleFbDxe' in names: raise ValueError('unqualified framebuffer provider included')
    probe_guid = 'aef8c196-230e-4e19-a306-d62e21e3d780'
    if probe_guid not in files or uuid.UUID(probe_guid).bytes_le not in b''.join(pe_payloads['UniXNUDxe']):
        raise ValueError('UniXNUDxe does not contain the packaged EnumaProbe boot target')
    report = {'scope': 'built FD structure and byte identity; no firmware execution',
              'fd_sha256': digest(blob), 'fd_bytes': len(blob), 'file_count': len(files),
              'matched_oem_modules': matched, 'packaged_names': sorted(names),
              'diagnostic_omitted_oem_modules':sorted(omitted),
              'apriori_guids':apriori,
              'probe_boot_target_guid': probe_guid,
              'runtime_protocol_closure': 'pending hardware dispatch', 'hardware_execution': False}
    if build.get('diagnostic_pixel_preview'):
        payloads=pe_payloads.get('SimpleFbDxe',[])
        if len(payloads)!=1:raise ValueError('pixel provider PE missing or ambiguous')
        out=ROOT/'out/pixel-preview-fd-audit';out.mkdir(exist_ok=True)
        target=out/'SimpleFbDxe.efi';target.write_bytes(payloads[0])
        assembly=subprocess.check_output(['llvm-objdump','-d',str(target)],text=True)
        if not all(x in assembly.lower() for x in ('civac','ctr_el0','dsb')):
            raise ValueError('protected pixel provider lacks actual in-FD cache instructions')
        (out/'SimpleFbDxe.disassembly.txt').write_text(assembly)
        report['pixel_preview_code']={'provider_pe_sha256':digest(payloads[0]),'cache_instructions_in_packaged_pe':True,
            'hardware_review_required':'R-005','hardware_execution':False}
    if build.get('diagnostic_gop_step') == 14:
        payloads=pe_payloads.get('SimpleFbDxe',[])
        if len(payloads)!=1:raise ValueError('DSI provider PE missing or ambiguous')
        out=ROOT/'out/dsi-timing-fd-audit';out.mkdir(exist_ok=True)
        target=out/'SimpleFbDxe.efi';target.write_bytes(payloads[0])
        assembly=subprocess.check_output(['llvm-objdump','-d',str(target)],text=True)
        (out/'SimpleFbDxe.disassembly.txt').write_text(assembly)
        constants={};reads=[];writes=[];wanted={0xae6b800,0xae6c000}
        for line in assembly.splitlines():
            fields=line.split('\t')
            if len(fields)<3:continue
            op,args=fields[-2].strip(),fields[-1].strip()
            move=re.fullmatch(r'([wx]\d+), #(-?(?:0x[0-9a-f]+|\d+))(?:, lsl #(\d+))?',args)
            if op in ('mov','movk') and move:
                register=move[1][1:];value=int(move[2],0);shift=int(move[3] or 0)
                if op=='mov':constants[register]=value & (0xffffffff if move[1][0]=='w' else 0xffffffffffffffff)
                elif register in constants:constants[register]=(constants[register]&~(0xffff<<shift))|((value&0xffff)<<shift)
                continue
            access=re.search(r'\[([wx]\d+)(?:, #(-?(?:0x[0-9a-f]+|\d+)))?\]',args)
            if access and access[1][1:] in constants:
                address=constants[access[1][1:]]+int(access[2] or '0',0)
                if address in wanted:
                    if op in ('ldr','ldur'):reads.append(hex(address))
                    elif op.startswith('st'):writes.append(hex(address))
            if op in ('bl','blr'):constants.clear()
            elif op not in ('cmp','tst','ret') and not op.startswith(('b','st')):
                dest=re.match(r'[wx](\d+)',args)
                if dest:constants.pop(dest[1],None)
        if reads!=['0xae6b800','0xae6c000'] or writes:
            raise ValueError('packaged DSI code does not match two read-only target accesses: '+repr((reads,writes)))
        report['dsi_timing_code']={'provider_pe_sha256':digest(payloads[0]),'static_target_loads':reads,'static_target_stores':writes,'scope':'constant-address accesses in actual packaged PE; not runtime proof','hardware_execution':False}
    if build.get('diagnostic_gop_step') in (15,16,17,18):
        from audit_dsi_counter_code import audit_counter_code
        payloads=pe_payloads.get('SimpleFbDxe',[])
        if len(payloads)!=1:raise ValueError('DSI counter provider PE missing or ambiguous')
        out=ROOT/'out/dsi-counters-fd-audit';out.mkdir(exist_ok=True)
        target=out/'SimpleFbDxe.efi';target.write_bytes(payloads[0])
        assembly=subprocess.check_output(['llvm-objdump','-d',str(target)],text=True)
        (out/'SimpleFbDxe.disassembly.txt').write_text(assembly)
        code=audit_counter_code(payloads[0],assembly,build['diagnostic_gop_step'])
        code['provider_pe_sha256']=digest(payloads[0]);report['dsi_counter_code']=code
    if build.get('diagnostic_gop_step') in (19,20,21,22,23):
        payloads=pe_payloads.get('SimpleFbDxe',[])
        if len(payloads)!=1:raise ValueError('route provider PE missing or ambiguous')
        out=ROOT/'out/scanout-route-fd-audit';out.mkdir(exist_ok=True)
        target=out/'SimpleFbDxe.efi';target.write_bytes(payloads[0])
        assembly=subprocess.check_output(['llvm-objdump','-d',str(target)],text=True)
        (out/'SimpleFbDxe.disassembly.txt').write_text(assembly)
        # Optimized loops compute CTL/source addresses dynamically. These are
        # packaged instruction fingerprints, not full MMIO dataflow proof.
        markers={name:bool(re.search(pattern,assembly)) for name,pattern in {
            'ctl_interface_mask_load':r'ldr\s+w\d+, \[x\d+, #244\]',
            'frame_counter_load':r'ldr\s+w\d+, \[x\d+, #172\]',
            'native_status_load':r'ldr\s+w\d+, \[x\d+, #620\]',
            'bounded_delta_comparison':r'cmp\s+w\d+, #64',
            'wait_low_half':r'mov\s+w0, #34464',
            'wait_high_half':r'movk\s+w0, #1, lsl #16'}.items()}
        if build['diagnostic_gop_step'] in (20,21,22,23):
            markers['source_output_xy_load']=bool(re.search(r'ldr\s+w\d+, \[x\d+, #16\]',assembly))
            markers['mixer_size_load']=bool(re.search(r'ldr\s+w\d+, \[x\d+, #4\]',assembly))
        if build['diagnostic_gop_step']==21:
            markers['dim_bit_test']=bool(re.search(r'tb[n]?z\s+w\d+, #16,',assembly))
            markers['constant_blend_comparison']=bool(re.search(r'cmp\s+w\d+, #256',assembly))
            markers['packed_alpha_comparison']=bool(re.search(r'cmp\s+w\d+, #4080, lsl #12',assembly))
        if build['diagnostic_gop_step']==22:
            markers['encoding_multiplier_low']=bool(re.search(r'mov\s+w\d+, #2304',assembly))
            markers['encoding_multiplier_high']=bool(re.search(r'movk\s+w\d+, #61, lsl #16',assembly))
            markers['encoding_multiply']=bool(re.search(r'mul\s+x0,',assembly))
        if not all(markers.values()):raise ValueError('route PE instruction fingerprint incomplete: '+repr(markers))
        report['scanout_route_code']=dict(provider_pe_sha256=digest(payloads[0]),instruction_markers=markers,
            scope='actual packaged PE fingerprints plus separately locked source/host tests; not complete indirect MMIO/store/control-flow proof',
            complete_mmio_dataflow_proof=False,hardware_execution=False)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(matched)} native PE/DEPEX payloads unchanged; diagnostic omissions={sorted(omitted)}; UniXNU loader modules packaged')


if __name__ == '__main__': main()
