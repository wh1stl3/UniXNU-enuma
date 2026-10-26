"""Check the manually reviewed R-022 packaged code/data offsets; no device."""
import argparse,hashlib,json,re,sys,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--tool-path',type=Path,required=True);a=p.parse_args();d=a.archive.resolve()
 if not d.is_relative_to(ROOT/'out'):raise ValueError('outside out')
 sys.path.insert(0,str(a.tool_path.resolve()));import pefile
 q=json.loads((d/'qualification.json').read_text());assert q['boot_log_replay'] and q['hardware_review']=='R-022' and q['boot_log_hold_seconds']==8
 for name,v in q['files'].items():assert sha(d/name)==v['sha256'],name
 provider=pefile.PE(str(d/'SimpleFbDxe.efi'));core=pefile.PE(str(d/'DxeCore.efi'))
 guid=uuid.UUID('a84039f7-b861-5dbe-9a09-a4f6cc746d5b').bytes_le
 assert provider.get_data(0x5000,16)==guid and core.get_data(0x202d8,16)==guid
 source=(ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/PixelLogPage.h').read_text()
 table=source.split('Glyph[20][5]={',1)[1].split('};',1)[0]
 glyph=bytes(int(v) for v in re.findall(r'\d+',table));assert len(glyph)==100 and provider.get_data(0x5090,100)==glyph
 text=(d/'SimpleFbDxe.disassembly.txt').read_text();ct=(d/'DxeCore.disassembly.txt').read_text()
 for line in ['106c: sub sp, sp, #0x18, lsl #12','1070: sub sp, sp, #0x1b0','1344: cmp w11, #0xd','1694: cmp x24, #6, lsl #12','191c: mov w0, #0x1200','1924: movk w0, #0x7a, lsl #16','3954: str w19, [x20]','39b4: ldr w8, [x21]','3c24: cmp x10, #0x5f','3c30: cmp x8, #0x400']:
  assert line in text,line
 for line in ['f914: mov w2, #0x1818','f9ac: strb w8, [x0], #0xf5','f9b0: bl #0x8b70','fa84: str x19, [x11, #0x20]','fac0: cmp x21, #0xd']:
  assert line in ct,line
 old=ROOT/'out/inherited-gop/qualified-dxe-log-r020-962f820'
 oldtext=(old/'SimpleFbDxe.disassembly.txt').read_text()
 expected=oldtext.replace('191c: mov w0, #0x8480','191c: mov w0, #0x1200').replace('1924: movk w0, #0x1e, lsl #16','1924: movk w0, #0x7a, lsl #16')
 assert text==expected,'unexpected provider instruction change'
 assert ct==(old/'DxeCore.disassembly.txt').read_text(),'Core instructions changed'
 assert sha(d/'DxeCore.efi')=='753ff2dd2444aeec2404c149c32771933f71d84dcb5e3b371261f7f1c15fb6da'
 assert hashlib.sha256((text+'\n'+ct).encode()).hexdigest()=='e23b12cdeeea632ceec769d97d22d1eecbc51f267f89f6bafab2d444a11f5f38'
 assert sum(': dsb sy' in line for line in text.splitlines())==3
 assert not re.search(r': dc |: msr (?:ttbr|tcr|mair|sctlr|vttbr)',text)
 report=dict(scope='manual disassembly reviewed and fixed offsets/data checked for this exact R-022 PE pair',image_sha256=q['image_sha256'],firmware_commit=q['firmware_commit'],provider_sha256=sha(d/'SimpleFbDxe.efi'),core_sha256=sha(d/'DxeCore.efi'),reviewed_disassembly_sha256='e23b12cdeeea632ceec769d97d22d1eecbc51f267f89f6bafab2d444a11f5f38',
  actual_entry_stack_bytes=0x60+0x18000+0x1b0,core_snapshot_copy_bytes=0x1818,
  observations=['private GUID identical in Core/provider; v1/bytes and EFIAPI snapshot checked before page','newest point13 filtered; full status high/low and ordinal read from actual snapshot offsets','24576-word save and pattern/verify/restore/readback loops; row<96 and column byte offset<1024; read/write counters bound','three DSB; hold immediate0x7a1200; complete restoration attempted despite rejected callbacks','actual mask-aware glyph bytes20x5 match source; no direct cache-line or translation-table setter instructions','Core publish attempted flag before install; true event status stored before same exact GUID-only warning1..5 cold terminal'],hardware_executed=False,gop_admitted=False,global_debug=False)
 (ROOT/'reports/enuma-log-hold8-code-review.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: exact PE protocol/record/glyph/stack/loop/restore code review, hardware unverified')
if __name__=='__main__':main()
