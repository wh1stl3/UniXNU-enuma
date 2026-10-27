"""R026 exact compiled-code regression, including child lifetime and Core bridge."""
import argparse,json,re
from pathlib import Path
from audit_menu_window_code import sha,image_range,check,CHECKS as PREVIOUS_CHECKS,CORE_CHECKS
from audit_attributed_log_code import sections
ROOT=Path(__file__).resolve().parents[1]
SHIFT=0x3ebc-0x4a6c
CHECKS={format(int(a,16)+SHIFT,'x'):(m,re.sub(r'0x[0-9a-f]+',lambda n:hex(int(n[0],16)+SHIFT),v)) for a,(m,v) in PREVIOUS_CHECKS.items() if int(a,16)<0x5000}
CHECKS.update({
 '4ad8':('cbz','w8, 0x50f4'),'4ae0':('cbnz','w8, 0x50f4'),
 '1ca4':('ldr','x8, [x8, #200]'),'1ca8':('blr','x8'),
 '1cf4':('cmp','w8, #1'),'1cf8':('b.ne','0x1d98'),
 '1d10':('stp','x26, xzr, [x23, #368]'),'1d14':('stp','xzr, xzr, [x23, #352]'),
 '1d4c':('stp','x9, x22, [x8, #16]'),'1d50':('str','xzr, [x8, #56]'),'1d54':('str','wzr, [x8, #48]'),
 '1d60':('ldr','x8, [x8, #208]'),'1d64':('blr','x8'),
 '1dac':('ldr','x8, [x8, #224]'),'1db4':('tbnz','x0, #63, 0x1de8'),
 '1dc0':('strb','wzr, [x8, #8]'),'1dd8':('cmp','x9, #262'),
 '1e30':('cmp','x22, x8'),'1e80':('blr','x13'),'1e90':('b','0x1e28'),
 '1f5c':('csel','w22, w9, w8, eq'),
 '18b0':('str','wzr, [x23, #576]'),'18bc':('cbnz','w8, 0x1940'),
 '18c4':('cbnz','x8, 0x1940'),'18f4':('tbnz','x0, #63, 0x1940'),
 '193c':('cbz','x0, 0x1954'),'1948':('csel','w22, w22, w8, eq'),
 '56a8':('mov','x0, #8'),'56ac':('movk','x0, #32768, lsl #48')})
CORE=dict(CORE_CHECKS,**{
 'f8e8':('cbz','x9, 0xf900'),'f8f0':('cmp','x9, x1'),'f8f8':('ccmp','x8, #0, #4, eq'),
 'f8fc':('b.ne','0xf904'),'f900':('ret',''),
 'c42c':('ldr','x1, [x19, #56]'),'c430':('blr','x8'),
 'c4c4':('cmp','x8, #10'),'c4c8':('b.eq','0xc6c8'),
 'c780':('cmp','x8, #10'),'c784':('b.ne','0xc790'),'c78c':('bl','0xabdc')})
def instructions(path):
 return {m[1]:(m[2],m[3] or '') for m in re.finditer(r'^\s*([0-9a-f]+):(?:\s+[0-9a-f]{2}){4}\s+([a-z0-9.]+)(?:[ \t]+([^\n]*))?$',path.read_text(),re.M)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.relative_to(ROOT/'out')
 if out.exists():raise ValueError('new output required')
 d=ROOT/'out/full-menu-20261027/qualification1';old=ROOT/'out/menu-window-20261026/qualification2'
 if sha(d/'qualification.json')!='10d3564a3cd5d4fce35b7b597098a0de31a546d9186d5cbe74da7d9a60d77221':raise ValueError('qualification changed')
 q=json.loads((d/'qualification.json').read_text())
 for n,h in q['files'].items():
  if sha(d/n)!=h:raise ValueError('artifact changed: '+n)
 if sha(d/'SimpleFbDxe.efi')!='36a63030197d1e2a90ba9f6cdbdfc441d59f0e2e7b757a0cd62d7f6b56d7e489':raise ValueError('provider not reviewed')
 if image_range(old/'SimpleFbDxe.efi',0x4a6c,0x248)!=image_range(d/'SimpleFbDxe.efi',0x3ebc,0x248):raise ValueError('physical callbacks changed')
 for name in ['.text','.data']:
  if sections(old/'DxeCore.efi')[name]!=sections(d/'DxeCore.efi')[name]:raise ValueError('Core changed: '+name)
 ins=instructions(d/'SimpleFbDxe.disassembly.txt');core=instructions(d/'DxeCore.disassembly.txt')
 check(ins,CHECKS);check(core,CORE)
 for address in ['3f70','1d4c','18b0']:
  changed=dict(ins);changed.pop(address)
  try:check(changed,CHECKS)
  except ValueError:pass
  else:raise ValueError('deleted critical instruction accepted')
 result=dict(passed=True,image_sha256=q['image_sha256'],qualification_sha256=sha(d/'qualification.json'),
  provider_checks={a:' '.join(v) for a,v in CHECKS.items()},core_checks={a:' '.join(v) for a,v in CORE.items()},
  physical_callback_bytes_equal_R025=584,core_text_data_equal_R025=True,deleted_instruction_mutations_rejected=3,
  source_runtime_evidence='qemu3 uses exact built UniXNU PE and production config/GOP/lifetime; VM callback memory and FV source fixture',
  conclusions=['budgets/window/requirements22 unchanged','Blt ready and first-fault gates precede drawing','LoadImage/StartImage/UnloadImage calls and private system table stores verified','application options null: no firmware-host ConnectAll','Core application type skips auto-connect; child handle excluded from scheduled-driver bridge','ready cleared before retained-reference or uninstall exits; restoration traverses entire saved window','return code unknown until physical evidence; no R024 timing decoder'],
  hardware_acceptance=False)
 out.write_text(json.dumps(result,indent=2)+'\n');print('PASS: R026 exact instructions, lifecycle and nested Core gates')
if __name__=='__main__':main()
