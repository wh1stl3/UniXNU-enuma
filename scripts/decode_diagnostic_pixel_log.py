"""Strict diagnostic replay3 transcription with explicit severity. Never guesses obscured digits."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import uuid


def decode_lines(lines):
    if len(lines)!=5 or any(not isinstance(s,str) or len(s)>20 for s in lines):
        raise ValueError('require five complete rows of at most 20 characters')
    patterns=[r'([CEW])0d O([0-9a-f]{8})(\+?)',r'S([0-9a-f]{16})',
              r'Q([0-9a-f]{16})',r'G0([0-9a-f]{16})',r'G1([0-9a-f]{16})']
    found=[re.fullmatch(p,s.rstrip(' ')) for p,s in zip(patterns,lines)]
    if not all(found): raise ValueError('incomplete/noncanonical page; no inferred characters')
    status=int(found[1][1],16)
    severity='E' if status>>63 else 'W' if status else 'C'
    if found[0][1]!=severity: raise ValueError('severity label contradicts returned EFI status')
    return dict(point=13,phase='cached-start-return',severity=severity,selection='newest at highest retained severity',ordinal_hex=found[0][2],
                older_records_lost=bool(found[0][3]),status_hex=found[1][1],
                sequence_hex=found[2][1],guid=str(uuid.UUID(hex=found[3][1]+found[4][1])),
                current_provider_return=False,boot_identity_available=False,
                screen_log_verified=False)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--transcript',type=Path,required=True)
    p.add_argument('--qualification',type=Path,help='optional exact candidate qualification for packaged GUID attribution')
    args=p.parse_args();raw=args.transcript.read_bytes()
    result=decode_lines(raw.decode('ascii').splitlines())
    result['transcript_sha256']=hashlib.sha256(raw).hexdigest()
    if args.qualification:
        q=json.loads(args.qualification.read_text());directory=args.qualification.parent
        catalog_path=directory/'packaged-guid-catalog.json';catalog_raw=catalog_path.read_bytes()
        if (q.get('passed') is not True or q.get('hardware_review')!='R-024' or
            hashlib.sha256(catalog_raw).hexdigest()!=q.get('files',{}).get('packaged-guid-catalog.json')):
            p.error('packaged GUID catalog is not bound to the candidate')
        image_raw=(directory/'image.img').read_bytes()
        if hashlib.sha256(image_raw).hexdigest()!=q['image_sha256']: p.error('candidate image changed')
        result['candidate_image_sha256']=q['image_sha256']
        result['packaged_driver_candidates']=json.loads(catalog_raw).get(result['guid'],[])
        result['attribution_limit']='GUID maps to packaged file bytes; transcript/photograph must separately be tied to the actual single trial. Sequence is not boot identity.'
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
