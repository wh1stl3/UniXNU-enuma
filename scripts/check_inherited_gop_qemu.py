"""Execute the linked RAM-only UEFI GOP self-test under QEMU, never on enuma."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
ROOT=Path(__file__).resolve().parents[1]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    build=json.loads((ROOT/'reports/enuma-firmware-build.json').read_text())
    pin=json.loads((ROOT/'config/uefi-source.lock.json').read_text())
    if not build['complete'] or not build.get('gop_backend_selftest_ram_only') or build['uefi_source_commit']!=pin['commit']:
        raise ValueError('require current clean-source linked RAM self-test build')
    fd=ROOT/build['fd']
    if sha(fd)!=build['fd_sha256']: raise ValueError('linked FD changed')
    mod=fd.parents[1]/'AARCH64/enumaPkg/Application/EnumaGopSelfTest/EnumaGopSelfTest'
    app=mod/'OUTPUT/EnumaGopSelfTest.efi'
    libraries=(mod/'OUTPUT/static_library_files.lst').read_text()
    for name in ['InheritedGopLib','FrameBufferBltLib']:
        if name not in libraries: raise ValueError('required actual library absent: '+name)
    out=ROOT/'out/inherited-gop/qemu'; esp=out/'esp/EFI/BOOT'; esp.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(app,esp/'BOOTAA64.EFI')
    code=Path('/usr/share/AAVMF/AAVMF_CODE.fd'); variables=Path('/usr/share/AAVMF/AAVMF_VARS.fd')
    shutil.copyfile(variables,out/'vars.fd')
    command=['qemu-system-aarch64','-machine','virt','-cpu','max','-m','512','-nographic','-monitor','none','-net','none','-no-reboot',
             '-drive','if=pflash,format=raw,readonly=on,file='+str(code),
             '-drive','if=pflash,format=raw,file='+str(out/'vars.fd'),
             '-drive','if=none,format=raw,file=fat:rw:'+str(out/'esp')+',id=esp',
             '-device','virtio-blk-device,drive=esp']
    timed_out=False
    with (out/'serial.log').open('wb') as log:
        try: result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=55)
        except subprocess.TimeoutExpired: timed_out=True; result=None
    log=(out/'serial.log').read_text(errors='replace')
    passed=not timed_out and result.returncode==0 and 'ENUMA_GOP_SELFTEST PASS RAM ONLY' in log and 'ENUMA_GOP_SELFTEST FAIL' not in log
    report=dict(scope='actual linked AArch64 UEFI RAM framebuffer self-test executed by QEMU; no enuma display/device action',
      passed=passed,firmware_commit=pin['commit'],fd_sha256=sha(fd),efi_sha256=sha(app),efi=str(app.relative_to(ROOT)),
      library_list_sha256=hashlib.sha256(libraries.encode()).hexdigest(),
      qemu_version=subprocess.check_output(['qemu-system-aarch64','--version'],text=True).splitlines()[0],
      qemu_firmware_sha256=sha(code),qemu_vars_template_sha256=sha(variables),argv=command,
      exit_code=result.returncode if result else None,timed_out=timed_out,serial_log=str((out/'serial.log').relative_to(ROOT)),
      serial_log_sha256=sha(out/'serial.log'),physical_gop_tested=False,enuma_boot_issued=False,protocol_published=False)
    (ROOT/'reports/enuma-inherited-gop-qemu.json').write_text(json.dumps(report,indent=2)+'\n')
    if not passed: raise RuntimeError('QEMU self-test did not pass; inspect '+report['serial_log'])
    print('PASS: linked AArch64 GOP backend executed by QEMU on allocated RAM; no physical display or enuma boot')

if __name__=='__main__': main()
