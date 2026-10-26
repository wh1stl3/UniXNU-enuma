"""Independent exact-grid inverse of production C pages. Synthetic only, not photo OCR."""
from pathlib import Path
import hashlib,json,subprocess,sys
from decode_cached_log_text import decode_lines
ROOT=Path(__file__).resolve().parents[1]
# Independently transcribed3x5 hexadecimal silhouettes; marker shapes are contextual.
HEX={c:tuple(map(int,rows.split())) for c,rows in zip('0123456789abcdef',[
 '7 5 5 5 7','2 6 2 2 7','7 1 7 4 7','7 1 7 1 7',
 '5 5 7 1 1','7 4 7 1 7','7 4 7 5 7','7 1 1 1 1',
 '7 5 7 5 7','7 5 7 1 7','2 5 7 5 5','6 5 6 5 6',
 '7 4 4 4 7','6 5 5 5 6','7 4 6 4 7','7 4 6 4 4'])}
SHAPES={**HEX,'C':HEX['c'],'O':HEX['0'],'S':HEX['5'],'+':(0,2,7,2,0),' ':(0,)*5}

def inverse_grid(grid):
    if len(grid)!=96 or any(len(row)!=256 or set(row)-{'0','1'} for row in grid):raise ValueError('not exact256x96 binary grid')
    rows=[]
    for r in range(3):
        text=''
        for c in range(16):
            allowed=('C' if c==0 else '0' if c==1 else 'd' if c==2 else 'O' if c==4 else '0123456789abcdef' if 5<=c<=12 else '+ ' if c==13 else ' ') if r==0 else ('S' if c==0 else '0123456789abcdef' if c<=8 else ' ') if r==1 else ('0123456789abcdef' if 1<=c<=8 else ' ')
            candidates=[]
            for ch in allowed:
                ok=True
                for y in range(32):
                    for x in range(16):
                        expected='1' if x<12 and y<20 and SHAPES[ch][y//4]&(1<<(2-x//4)) else '0'
                        if grid[r*32+y][c*16+x]!=expected:ok=False;break
                    if not ok:break
                if ok:candidates.append(ch)
            if len(candidates)!=1:raise ValueError('inexact or ambiguous cell; no fuzzy substitution')
            text+=candidates[0]
        rows.append(text)
    return rows

def main():
    out=ROOT/'out/cached-log-format';out.mkdir(exist_ok=True)
    lib=ROOT/'firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib'
    source=ROOT/'tests/cached_log_format.c';exe=out/'test'
    cmd=['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-Wno-unused-function',
        '-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+str(lib),
        '-I'+str(ROOT/'firmware/diagnostics'),'-I'+str(ROOT/'out/boot-journal-tests'),str(source),'-o',str(exe)]
    subprocess.run(cmd,check=True)
    result=subprocess.check_output([str(exe)],text=True).splitlines();assert len(result)==96*100
    for n in range(96):
        case=result[n*100:(n+1)*100];ordinal,status=case[0].split();grid=case[4:]
        text=inverse_grid(grid);assert text==case[1:4]
        decoded=decode_lines(text)
        assert decoded['ordinal_hex']==ordinal and decoded['status_hex']==status and decoded['older_records_lost']
        assert not decoded['screen_log_verified']
    # A single changed sample must fail exact inverse rather than get rounded.
    damaged=list(result[4:100]);damaged[0]=('0' if damaged[0][0]=='1' else '1')+damaged[0][1:]
    try:inverse_grid(damaged)
    except ValueError:pass
    else:raise AssertionError('damaged grid accepted')
    sources=[source,Path(__file__),ROOT/'scripts/decode_cached_log_text.py',lib/'PixelLogPage.h',ROOT/'firmware/diagnostics/EnumaBootJournal.h']
    report=dict(scope='synthetic C production formatter/rasterizer -> independent exact-grid inverse -> strict text parser; not photo OCR',
        cases=96,status_bit_walk=64,includes_zero_max_and_mixed_bits=True,wrapped_ring_newest_return=True,
        total_pixels_checked=96*256*96,damaged_sample_rejected=True,
        known_contextual_collisions=['O and0','S and5','C andc'],
        limitations=['No blur/exposure/focus tolerance or photograph recognition','No visual identity or real hardware value evidence','128-record snapshot retains only latest point13 on this page; no driver GUID displayed'],
        screen_log_verified=False,hardware_executed=False,device_action=False,command=cmd,
        sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (ROOT/'reports/enuma-cached-log-format.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS:96 production C pages/2359296 pixels,64 status bits and full ordinal; exact inverse and strict parser; damaged pixel rejected; synthetic only')
if __name__=='__main__':main()
