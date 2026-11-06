"""Rebuild only the four specifically authorized real OS probe samples."""
import hashlib,json
from pathlib import Path

def prepare(root: Path, out: Path, manifest: Path, image=None):
    proposal=json.loads((root/'reports/enuma-owner-probe-material-proposal.json').read_text())
    if proposal['approved'] is not True or proposal['padded_bytes']!=16384:
        raise ValueError('Missing exact probe sample authorization')
    image=Path(image) if image is not None else root/'out/apple-owner-inputs/OS.analysis-window.img'
    h=hashlib.sha256()
    with image.open('rb') as stream:
        for block in iter(lambda:stream.read(8<<20),b''):h.update(block)
    if h.hexdigest()!=proposal['image_sha256']:raise ValueError('OS input drift')
    packed=bytearray()
    with image.open('rb') as stream, manifest.open('rb') as table:
        for sample in proposal['samples']:
            if sample['offset']!=sample['index']*4096:raise ValueError('Sample index drift')
            stream.seek(sample['offset']);block=stream.read(sample['length'])
            digest=hashlib.sha256(block).digest()
            table.seek(544+sample['index']*32)
            if len(block)!=sample['length'] or digest.hex()!=sample['sha256'] or table.read(32)!=digest:
                raise ValueError('Real sample does not match its signed policy table')
            packed.extend(block+bytes(4096-len(block)))
    if len(packed)!=16384 or hashlib.sha256(packed).hexdigest()!=proposal['padded_sha256']:
        raise ValueError('Padded sample drift')
    path=out/'owner-probe-samples.bin';path.write_bytes(packed)
    asm=['.p2align 3','.globl _verified_root_manifest_bytes','_verified_root_manifest_bytes:',f'.quad {manifest.stat().st_size}',
         '.globl _verified_root_sample_indices','_verified_root_sample_indices:',
         '.quad '+','.join(str(s['index']) for s in proposal['samples']),
         '.globl _verified_root_sample_lengths','_verified_root_sample_lengths:',
         '.quad '+','.join(str(s['length']) for s in proposal['samples']),
         '.globl _verified_root_samples','_verified_root_samples:',f'.incbin "{path}"']
    return asm,dict(image_sha256=h.hexdigest(),samples=proposal['samples'],padded_sha256=proposal['padded_sha256'],
                    returned_only_inside_kernel_and_owner_policies=True)
