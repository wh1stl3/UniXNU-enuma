"""Host renderer tests and real-header AArch64 compile; no firmware integration."""
import hashlib,json,struct,subprocess,zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def run(argv):
    q=subprocess.run([str(x) for x in argv],capture_output=True,text=True,timeout=60)
    if q.returncode:raise RuntimeError(q.stdout+q.stderr)
    return dict(exit_code=q.returncode,argv=[str(x) for x in argv])


def png(path,raw):
    def chunk(tag,body):
        return struct.pack('>I',len(body))+tag+body+struct.pack('>I',zlib.crc32(tag+body)&0xffffffff)
    rows=[]
    for y in range(336):
        row=bytearray(b'\0')
        for x in range(480):
            b,g,r,_=raw[(y*480+x)*4:(y*480+x+1)*4]
            row.extend((r,g,b))
        rows.append(row)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',480,336,8,2,0,0,0))+
                     chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b''))


def main():
    out=ROOT/'out/screen-diagnostics';out.mkdir(exist_ok=True)
    lock=json.loads((ROOT/'config/firmware-build.lock.json').read_text())
    archive=ROOT/'out/firmware-build/mu-basecore.tar.gz'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==lock['archive_sha256']['mu-basecore.tar.gz']
    # Compile against exact archived headers, not mock UEFI type definitions.
    import tarfile
    include=out/'MuInclude'
    with tarfile.open(archive) as source:
        for member in source.getmembers():
            if not member.isfile() or '/MdePkg/Include/' not in member.name:continue
            relative=member.name.split('/MdePkg/Include/',1)[1]
            target=(include/relative).resolve()
            assert target.is_relative_to(include.resolve())
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.extractfile(member).read())
    font=ROOT/'out/sources/UniXNU/drivers/DarwinBoot/DarwinBootPkg/Driver/DiagFont.h'
    expected=json.loads((ROOT/'config/porting-sources.lock.json').read_text())['unixnu_interface_sha256']['drivers/DarwinBoot/DarwinBootPkg/Driver/DiagFont.h']
    assert hashlib.sha256(font.read_bytes()).hexdigest()==expected
    (out/'DiagFont.h').write_bytes(font.read_bytes())
    source=ROOT/'diagnostics/screen/EnumaScreen.c'
    flags=['clang','-std=c11','-Wall','-Wextra','-Werror','-fshort-wchar','-I'+str(include),'-I'+str(out),'-I'+str(source.parent)]
    host=flags+['-I'+str(include/'X64'),'-O1','-fsanitize=address,undefined','-fno-pie','-no-pie',
                str(source),str(ROOT/'tests/enuma_screen.c'),'-o',str(out/'screen-test')]
    records=[run(host),run([out/'screen-test',out/'preview.bgra'])]
    target=flags+['-I'+str(include/'AArch64'),'-target','aarch64-unknown-windows-msvc','-ffreestanding','-Oz','-fno-builtin',
                  '-fshort-wchar','-fno-stack-protector','-mno-implicit-float','-c',str(source),'-o',str(out/'EnumaScreen.obj')]
    records.append(run(target))
    obj=(out/'EnumaScreen.obj').read_bytes()
    assert struct.unpack_from('<H',obj)[0]==0xaa64
    undefined=subprocess.check_output(['llvm-nm','--undefined-only',str(out/'EnumaScreen.obj')],text=True)
    undefined_symbols=[line.split()[-1] for line in undefined.splitlines() if line.split()]
    assert set(undefined_symbols)<=set(('memset','memcpy'))
    raw=(out/'preview.bgra').read_bytes();assert len(raw)==480*336*4
    png(out/'host-preview.png',raw)
    report=dict(scope='GOP Blt renderer host tests and real Mu-header AArch64 COFF compile only',
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        header_sha256=hashlib.sha256((source.parent/'EnumaScreen.h').read_bytes()).hexdigest(),
        font_sha256=expected,mu_commit=lock['reference_gitlinks']['Mu_Basecore'],
        mu_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        object_sha256=hashlib.sha256(obj).hexdigest(),object_machine='AArch64 COFF',checks=records,
        object_undefined_symbols=undefined_symbols,full_firmware_link_checked=False,
        host_checks=['write gate denies before Blt','BltOnly with zero physical framebuffer',
                     'region and scratch bounds','fixed A glyph golden pixels','replacement glyph',
                     'row/label/count rejection','callback reentry refusal','error latches closed',
                     'mode/pointer change latches closed','single bulk Blt per line','scratch canary',
                     '12-row snapshot page and stop after injected third-call failure',
                     '64-bit EFI error high bit preserved in rendered hex'],
        preview='out/screen-diagnostics/host-preview.png',preview_is_device_screenshot=False,
        firmware_integrated=False,write_enabled_on_device=False,new_device_trials=0,
        evening_82ce8a5_bundle_unchanged=True)
    (ROOT/'reports/enuma-screen-diagnostics-host.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: bounded GOP Blt renderer, real-header host sanitizers and AArch64 object; preview is synthetic, firmware not integrated')


if __name__=='__main__':main()
