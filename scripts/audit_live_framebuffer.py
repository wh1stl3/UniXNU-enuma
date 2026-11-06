"""Read-only enuma display evidence; never accesses physical pixel memory."""
import hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 state=json.loads((ROOT/'out/device-tests/current.local.json').read_text())
 target=json.loads((Path(state['directory'])/'target.local.json').read_text())
 def query(command):
  p=subprocess.run([target['adb'],'-s',target['serial'],'shell','su -c '+shlex.quote(command)],capture_output=True,timeout=20)
  if p.returncode:raise RuntimeError('read-only display query failed')
  return p.stdout.decode(errors='strict').replace('\r','').strip()
 assert query('getprop ro.product.device')=='enuma'
 assert query('getprop sys.boot_completed')=='1' and 'uid=0(root)' in query('id')
 raw=query('od -An -tx1 /sys/firmware/devicetree/base/reserved-memory/cont_splash_region@9c000000/reg')
 data=bytes.fromhex(raw);assert len(data)==16
 base=int.from_bytes(data[:8],'big');length=int.from_bytes(data[8:],'big')
 modes=query('cat /sys/class/drm/card0-DSI-1/modes').splitlines()
 assert base==0x9c000000 and length==0x2300000
 assert modes and all(m.startswith('1600x2560x') for m in modes)
 report=dict(scope='live Android DT reservation and DRM modes; no bootloader scanout proof',device='enuma',boot_complete=True,root=True,splash_base=hex(base),splash_length=hex(length),uefi_declared_length='0x2400000',common_reserved_length=hex(length),drm_modes=modes,stride='unverified',pixel_format='unverified',compression='unverified',metadata_32bpp_is_hypothesis=True,pixel_memory_access=False,device_mutation=False,next='Resolve bootloader scanout layout and cache handling before integrating a reversible stripe')
 (ROOT/'reports/enuma-live-framebuffer.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print('PASS: live enuma splash reservation and DRM modes; stride/format/compression remain unverified')
if __name__=='__main__':main()
