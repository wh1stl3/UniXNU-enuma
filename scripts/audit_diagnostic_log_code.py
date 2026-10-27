"""Recheck inspected replay3 machine code and distinguish diagnostic/late console PEs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from audit_attributed_log_code import sections
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def instructions(path):
    result={}
    for line in path.read_text().splitlines():
        fields=line.split('\t');m=re.match(r'\s*([0-9a-f]+):',fields[0])
        if m and len(fields)>1:result[m[1]]=re.sub(r'\s+',' ',' '.join(fields[1:]).split('//')[0].strip())
    return result
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ('qualification','console-link','output'):ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();qp=a.qualification.resolve();d=qp.parent;out=a.output.resolve()
    qp.relative_to(ROOT/'out');out.relative_to(ROOT/'out');assert not out.exists()
    q=json.loads(qp.read_text());assert q['passed'] and q['hardware_review']=='R-024'
    for n,h in q['files'].items():assert sha(d/n)==h,n
    ins=instructions(d/'SimpleFbDxe.disassembly.txt')
    expected={
        '106c':'sub sp, sp, #0x32, lsl #12','1070':'sub sp, sp, #0x1b0',
        '15e4':'cmp w14, #0xd','15e8':'b.ne 0x1630 <.text+0x630>',
        '15fc':'csel w13, w13, w11, ge','1610':'tst x14, #0x8000000000000000',
        '1620':'cmp w13, w14','1628':'ccmp x23, #0x0, #0x4, ls',
        '162c':'csel x23, x12, x23, eq','1630':'sub w8, w8, #0x1',
        '163c':'ldrb w8, [x23, #0x28]','1640':'cbz w8, 0x1698 <.text+0x698>',
        '16c4':'mov w9, #0x43','16d4':'mov w8, #0x57','16dc':'mov w9, #0x45',
        '1734':'ldr x1, [x23, #0x8]','174c':'ldr x1, [x23]',
        '187c':'dsb sy','1880':'mov w23, #0xc800','1888':'mov w25, #0x140',
        '18b0':'add w8, w8, #0x60','18b8':'add w9, w9, #0x100',
        '1a20':'mov w8, #0xc800','1a94':'dsb sy',
        '1b2c':'mov w0, #0x1200','1b34':'movk w0, #0x7a, lsl #16',
        '1b60':'mov w22, #0xc800','1b88':'ldr w2, [x24, x23, lsl #2]',
        '1bac':'add x23, x23, #0x1','1bd4':'dsb sy','1bdc':'mov w24, #0xc800',
        '1c44':'add x23, x23, #0x1','1c5c':'mov w9, #0x4','1c60':'csel x20, x9, x8, eq',
        '3b68':'lsr w9, w8, #12','3b6c':'cmp w9, #0x18','3b88':'str w19, [x20]',
        '3bc8':'lsr w9, w8, #11','3bcc':'cmp w9, #0x4a','3be8':'ldr w8, [x21]'}
    for addr,value in expected.items():assert ins.get(addr)==value,(addr,ins.get(addr),value)
    assert sum(v=='dsb sy' for v in ins.values())==3
    assert not any(re.match(r'(?:dc |msr (?:ttbr|tcr|mair|sctlr|vttbr))',v) for v in ins.values())
    old=ROOT/'out/inherited-gop/qualified-dxe-log-8s-8680ea7/DxeCore.efi'
    assert sha(old)=='753ff2dd2444aeec2404c149c32771933f71d84dcb5e3b371261f7f1c15fb6da'
    before=sections(old);after=sections(d/'DxeCore.efi')
    assert before['.text']==after['.text'] and before['.data']==after['.data']
    marker='DXE CACHED REPLAY %r'.encode('utf-16le')
    assert marker not in (d/'EnumaProbe.efi').read_bytes()
    assert instructions(d/'EnumaProbe.disassembly.txt')['10f8']=='mov x0, #-0x7ffffffffffffffd'
    cp=a.console_link.resolve();cp.relative_to(ROOT/'out');c=json.loads(cp.read_text())
    assert c['passed'] and not c['packaged_in_fd'] and not c['hardware_execution']
    assert sha(cp.parent/'EnumaProbe.efi')==c['pe_sha256']
    assert marker in (cp.parent/'EnumaProbe.efi').read_bytes()
    paths=[qp,cp,cp.parent/'EnumaProbe.efi',d/'SimpleFbDxe.efi',d/'SimpleFbDxe.disassembly.txt',d/'DxeCore.efi',d/'EnumaProbe.efi',d/'EnumaProbe.disassembly.txt',Path(__file__),ROOT/'scripts/audit_attributed_log_code.py']
    report=dict(passed=True,scope='targeted manual source/disassembly review with exact instruction regression; not execution qualification',
        hardware_execution=False,image_sha256=q['image_sha256'],instruction_checks=expected,
        entry_stack_bytes=0x60+0x32000+0x1b0,configured_stack_bytes=262144,stack_high_water_measured=False,
        core_text_and_initialized_data_identical_to_r022=True,
        diagnostic_probe_is_intentional_unsupported_guard=True,late_console_only_in_separate_module=True,
        observations=['point13-only reverse severity selection, missing selected GUID rejects',
                      'E/W/C classification and full64 status/sequence retained',
                      '51200 words, x64..383/y96..255,8s,three DSB',
                      'whole restore/readback loops continue; restore failure code4 takes precedence',
                      'read/write callbacks bounded153600/102400; no cache or mapping setter instructions'],
        pending=['whole-candidate execution review and independent runner qualification','new exact-image approval and fresh observation/device gates'],
        bindings={str(p.relative_to(ROOT)):sha(p) for p in paths})
    out.write_text(json.dumps(report,indent=2)+'\n');print('PASS: replay3 instruction checks; diagnostic gate intact; separate real console PE linked')
if __name__=='__main__':main()
