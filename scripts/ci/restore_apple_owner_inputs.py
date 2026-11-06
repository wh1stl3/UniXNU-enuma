"""Reconstruct approved owner policies from fixed Apple restore components.

Analysis windows only: no SHNGROOT, partition image or deployment package.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out/apple-owner-inputs'
URL = 'https://updates.cdn-apple.com/2025SpringFCS/fullrestores/122-77166/DCA6CFE8-90E9-4B92-880D-3DE171798E40/iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw'
PIN = '16e592abee8a550dec8154ed1f38b5ebc4f16213'
SOURCES = {
    'udif.py': 'c3a2111c2188fb8a9bf0bfdf3675662520688233ba3bbf0ebf9ccb900de10e19',
    'util.py': '1f6efa81051d67f7225783958f1f8e86a38a7d4e538299ce6aa639b3cb4a759d',
    '__init__.py': 'c6ae444a32411f12494607894581cc27d6bfec49c2f5712fe47a26cece5d1007',
}
COMPONENTS = [
    ('OS', '044-76040-038.dmg', '3f99b859c9728379110b66657c7b15285bcb1925ad8b5726542e2cdcf8b1028d'),
    ('SystemOS', '044-76034-038.dmg', 'b4908cde41d23e6bc05e6af51a2c9eeb00cf0f863a6a18b1600c96a3fd70414f'),
]

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()

def download(url, target):
    subprocess.run(['curl', '--fail', '--location', '--retry', '3', '--output', str(target), url], check=True)

def main():
    OUT.mkdir(parents=True, exist_ok=False)
    report = dict(passed=False, source_url=URL, decoder_commit=PIN, deployment_enabled=False)
    try:
        decoder = OUT / 'reference/unixnu'
        decoder.mkdir(parents=True)
        for name, digest in SOURCES.items():
            target = decoder / name
            download(f'https://raw.githubusercontent.com/UniXNU/UniXNU/{PIN}/scripts/unixnu/{name}', target)
            if sha(target) != digest:
                raise ValueError('Decoder source drift: ' + name)
        lzfse = shutil.which('lzfse')
        if not lzfse:
            raise ValueError('Missing LZFSE decoder')
        report['lzfse_sha256'] = sha(Path(lzfse))
        archive = OUT / 'original.ipsw'
        download(URL, archive)
        report['ipsw_sha256'] = sha(archive)
        with zipfile.ZipFile(archive) as z:
            manifest = z.read('BuildManifest.plist')
            if hashlib.sha256(manifest).hexdigest() != '199fb5de41c26d86c080b4e8e402c40309c5f42e7bda18c210451b09bcb49bf7':
                raise ValueError('BuildManifest drift')
            for name, member, digest in COMPONENTS:
                target = OUT / member
                with z.open(member) as src, target.open('xb') as dst:
                    shutil.copyfileobj(src, dst, 8 << 20)
                if sha(target) != digest:
                    raise ValueError('Original Apple component drift: ' + name)
        archive.unlink()  # Only the new CI download; original sources are untouched.
        sys.path.insert(0, str(decoder.parent))
        from unixnu.udif import Image
        contract = json.loads((ROOT / 'ci/enuma-owner-root/contract.json').read_text())
        for (name, member, _), entry in zip(COMPONENTS, contract['windows']):
            if name != entry['name']:
                raise ValueError('Policy order drift')
            image = Image(OUT / member)
            if image.size != entry['image_bytes']:
                raise ValueError('Expanded image geometry drift')
            target = OUT / (name + '.analysis-window.img')
            count = 0
            with target.open('xb') as dst:
                for block in image.blocks():
                    count += len(block)
                    if count > image.size:
                        raise ValueError('Decoder exceeded window')
                    dst.write(block)
            if count != image.size or sha(target) != entry['image_sha256']:
                raise ValueError('Expanded Apple image drift')
        subprocess.run([sys.executable, str(ROOT / 'experiments/native-ufs-reuse/restore_owner_policies.py'), str(ROOT / 'ci/enuma-owner-root'), str(OUT), str(ROOT / 'out/owner-policy-restored')], check=True)
        report['passed'] = True
    finally:
        (OUT / 'result.json').write_text(json.dumps(report, indent=2) + '\n')

if __name__ == '__main__':
    main()
