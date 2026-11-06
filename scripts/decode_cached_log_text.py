"""Parse a literal three-line cached page transcription, never infer unreadable digits.

This is format validation only. It cannot certify that a photo contains these
values, identify its boot, prove restoration, or qualify GOP/global DEBUG.
"""
import argparse,json,re

def decode_lines(lines):
    if not isinstance(lines,list) or len(lines)!=3 or any(type(s) is not str or len(s)>16 for s in lines):
        raise ValueError('require exactly three literal rows, each at most16 characters')
    patterns=[r'C0d O([0-9a-f]{8})(\+)? *',r'S([0-9a-f]{8}) *',r' ([0-9a-f]{8}) *']
    match=[re.fullmatch(p,s) for p,s in zip(patterns,lines)]
    if not all(match):raise ValueError('incomplete or noncanonical row: do not guess, reorder, trim leading blanks or replace unclear digits')
    high,low=match[1][1],match[2][1]
    return dict(scope='literal transcription syntax only; requires independent visual evidence',
        point=13,ordinal_hex=match[0][1],status_hex=high+low,
        efi_error_bit=bool(int(high,16)&0x80000000),older_records_lost=bool(match[0][2]),
        cached_replay=True,screen_log_verified=False,hardware_executed=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lines',nargs=3,required=True)
    args=p.parse_args()
    try:result=decode_lines(args.lines)
    except ValueError as e:p.error(str(e))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
