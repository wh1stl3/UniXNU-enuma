"""R027 exact instruction review: actual return precedes deferred service call."""
import argparse,json,re
from pathlib import Path
from audit_menu_window_code import sha,image_range,check,CHECKS as WINDOW_CHECKS
from audit_full_menu_code import instructions
ROOT=Path(__file__).resolve().parents[1]
QUALIFICATION='e82028edad3baf06c3a4fd919d61c650da79e09b1d1bd5056402acb198a02af9'
SHIFT=0x411c-0x4a6c
PROVIDER={format(int(a,16)+SHIFT,'x'):(m,re.sub(r'0x[0-9a-f]+',lambda n:hex(int(n[0],16)+SHIFT),v))
          for a,(m,v) in WINDOW_CHECKS.items() if int(a,16)<0x5000}
PROVIDER.update({
 '1294':('add','x0, x20, #184'),'1298':('mov','w2, #80'),'129c':('bl','0x6cd4'),
 '12a8':('movk','x8, #24, lsl #32'),'12b8':('add','x10, x10, #1196'),
 '12c4':('ldr','x8, [x9, #128]'),'12cc':('stp','x19, x10, [x20, #16]'),
 '12d0':('blr','x8'),'12d4':('cmp','x0, #0'),'12d8':('cset','w0, ne'),
 '34dc':('cmp','x0, x9'),'34e0':('b.ne','0x354c'),'34e8':('tbnz','w8, #0, 0x354c'),
 '34f4':('strb','w22, [x8, #1648]'),'3530':('cmp','w8, #13'),'3544':('cbz','x8, 0x3570'),
 '361c':('bl','0x3204'),'3624':('cmp','w0, #3'),'3628':('ccmp','x8, #4, #0, eq'),'362c':('b.ne','0x3548'),
 '3a40':('str','wzr, [x26, #680]'),'3a44':('cbnz','w8, 0x3abc'),'3a4c':('cbnz','x8, 0x3abc'),
 '3a78':('tbnz','x0, #63, 0x3abc'),'3ab8':('cbz','x0, 0x3acc'),'3ac4':('csel','w22, w22, w8, eq'),
 '3e5c':('ldr','x8, [x8, #200]'),'3e68':('blr','x8'),'3eb0':('cmp','w8, #1'),
 '3ed4':('stp','x25, xzr, [x21, #472]'),'3ed8':('stp','xzr, xzr, [x21, #456]'),
 '3f04':('stp','x9, x23, [x8, #16]'),'3f08':('str','xzr, [x8, #56]'),'3f0c':('str','wzr, [x8, #48]'),
 '3f18':('ldr','x8, [x8, #208]'),'3f1c':('blr','x8'),'3f5c':('ldr','x8, [x8, #224]'),
 '3f64':('tbnz','x0, #63, 0x3f98'),'3f88':('cmp','x9, #280'),
 '3fec':('cmp','x23, x8'),'403c':('blr','x13'),'404c':('b','0x3fe4'),
 '40cc':('blr','x11'),'40e8':('b.eq','0x40f0'),'4114':('csel','w22, w9, w8, eq'),
 '4d7c':('cbz','w8, 0x5398'),'4d84':('cbnz','w8, 0x5398')})
CORE={
 '10564':('bl','0xc318'),'10568':('mov','x24, x0'),'1056c':('mov','w0, #13'),
 '10574':('mov','x2, x24'),'10578':('stp','xzr, xzr, [x28]'),'1057c':('bl','0xf910'),
 '105b4':('b.ne','0x10620'),'105d4':('b.ne','0x10620'),
 '10630':('strb','w8, [x9, #771]'),'10634':('cbnz','x24, 0x105e4'),
 '1064c':('bl','0x8de4'),'10664':('cmp','w8, #1'),'10670':('cmp','w8, #24'),
 '1067c':('cmp','x8, x28'),'10680':('b.ne','0x105e4'),'10688':('cbz','x8, 0x105e4'),
 '106a0':('mov','w2, #6168'),'106a4':('bl','0x1d6c4'),
 '106e8':('cmp','w8, #13'),'10704':('cbz','x8, 0x10718'),'1075c':('b.ne','0x10708'),
 '1079c':('b.ne','0x10708'),'107cc':('b.eq','0x10778'),
 '107d8':('ldr','x8, [x24, #16]'),'107e0':('add','x1, x1, #2752'),'107e4':('blr','x8'),
 '107f4':('csel','w20, w8, w0, lo'),
 '105ec':('mov','w0, #28'),'105fc':('bl','0xf9e4'),'10614':('bl','0x1bb0c'),
 '10618':('bl','0x16f4'),'1061c':('bl','0x13b8')}

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.relative_to(ROOT/'out')
 if out.exists():raise ValueError('new output required')
 d=ROOT/'out/deferred-menu-20261027/qualification1'
 if sha(d/'qualification.json')!=QUALIFICATION:raise ValueError('unreviewed qualification')
 q=json.loads((d/'qualification.json').read_text())
 for n,h in q['files'].items():
  if sha(d/n)!=h:raise ValueError('artifact changed: '+n)
 old=ROOT/'out/full-menu-20261027/qualification1/SimpleFbDxe.efi'
 if image_range(old,0x3ebc,584)!=image_range(d/'SimpleFbDxe.efi',0x411c,584):raise ValueError('physical callbacks changed')
 ins=instructions(d/'SimpleFbDxe.disassembly.txt');core=instructions(d/'DxeCore.disassembly.txt')
 check(ins,PROVIDER);check(core,CORE)
 for original,checks,addr in [(ins,PROVIDER,'34f4'),(ins,PROVIDER,'3a40'),(core,CORE,'10578'),(core,CORE,'10634'),(core,CORE,'107e4')]:
  mutation=dict(original);mutation.pop(addr)
  try:check(mutation,checks)
  except ValueError:pass
  else:raise ValueError('deleted gate accepted')
 result=dict(passed=True,image_sha256=q['image_sha256'],qualification_sha256=QUALIFICATION,
   provider_checks=PROVIDER,core_checks=CORE,physical_callback_bytes_equal_R026=584,deleted_instruction_mutations_rejected=5,
   conclusions=['driver entry copies 80-byte frame to owned static storage and publishes on its loaded handle; returns success only if install succeeds',
    'CoreStartImage completes; starting-image bridge cleared; actual point13 status recorded before exact-GUID handoff',
    'Core service lookup uses actual driver handle; version/size/owner and last success snapshot checked before callback',
    'single-use provider callback repeats EL1/identity-WT gate before existing native route validation',
    'unchanged physical callback bytes; application host load/start/unload, private table and 280-byte readonly config verified',
    'Blt revoked before failure cleanup; full-window restore/readback; point28 records menu result separately'],
   full_bds=False,hardware_acceptance=False,timing_decoder='none; no earlier trial decoder inherited')
 out.write_text(json.dumps(result,indent=2)+'\n');print('PASS: R027 compiled dispatcher handoff and provider lifecycle')
if __name__=='__main__':main()
