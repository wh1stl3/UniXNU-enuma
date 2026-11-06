"""Fetch only hash-locked reference files into out/; never update a source checkout."""
import argparse
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_references(fetch=False):
    lock = json.loads((ROOT / 'config/porting-sources.lock.json').read_text())
    records = []
    cache = (ROOT / 'out/references').resolve()
    for item in lock['files']:
        target = (cache / item['cache_path']).resolve()
        if not target.is_relative_to(cache):
            raise ValueError('reference path escapes cache')
        if not target.exists():
            if not fetch:
                raise ValueError(f'missing reference: {target}; run with --fetch')
            endpoint = f"repos/{item['repository']}/contents/{item['path']}?ref={item['commit']}"
            env = dict(os.environ, GODEBUG='http2client=0')
            result = subprocess.run(['gh', 'api', endpoint], capture_output=True,
                                    text=True, timeout=60, check=True, env=env)
            response = json.loads(result.stdout)
            if response.get('encoding') != 'base64':
                raise ValueError(f'unsupported GitHub response: {endpoint}')
            data = base64.b64decode(response['content'])
            if sha256(data) != item['sha256']:
                raise ValueError(f'download pin mismatch: {target}')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        if sha256(target.read_bytes()) != item['sha256']:
            raise ValueError(f'reference pin mismatch: {target}')
        records.append({'path': item['cache_path'], 'sha256': item['sha256']})
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='download missing pinned files via gh')
    args = parser.parse_args()
    print(json.dumps(check_references(args.fetch), indent=2))
