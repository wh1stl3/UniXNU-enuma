"""R025/S053 explicit single-shot human-camera trial; default is offline only."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from uuid import UUID
from r025_preparation import qualification,require_attempt,ROOT
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute',action='store_true');p.add_argument('--human-camera-ready',action='store_true')
    p.add_argument('--execution-id');p.add_argument('--preparation',type=Path,required=True)
    args=p.parse_args();q,image=qualification(args.preparation,published=args.execute)
    if not args.execute:
        print(json.dumps(dict(image_sha256=q['image_sha256'],device_action=False,scope=q['scope'])));return 0
    if not args.human_camera_ready or not args.execution_id or str(UUID(args.execution_id))!=args.execution_id:
        raise ValueError('current filming readiness and unique execution UUID required before any device access')
    meta=json.loads(image.with_suffix('.json').read_text());require_attempt(ROOT,meta,args.execution_id,True)
    # The existing runner retains bound-target identity, backups, one-shot claim,
    # 75-second observation and recovery checks. No inherited log timing decoder.
    return subprocess.call([sys.executable,'-B',str(ROOT/'scripts/run_enuma_entry_probe.py'),'--image',str(image),
                            '--label','dxe-driver-return','--execution-id',args.execution_id,'--human-camera-ready','--boot-clock'],cwd=ROOT)
if __name__=='__main__':raise SystemExit(main())
