"""Bounded DBRDISK1 inspection; format acceptance is not APFS/OS qualification."""
import hashlib
import struct
from pathlib import Path

def inspect_seed(path, expected_sha256):
    path = Path(path)
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise ValueError('explicit SHA256 binding required')
    # Match pinned NativeRamBlock/SparseDisk.h, without materializing logical RAM.
    with path.open('rb') as stream:
        size = stream.seek(0, 2)
        if not 32 <= size <= 0x10000000:
            raise ValueError('packed size outside bound')
        stream.seek(0)
        blob = stream.read(size + 1)
    digest = hashlib.sha256(blob).hexdigest()
    if len(blob) != size or digest != expected_sha256:
        raise ValueError('Data seed digest mismatch')
    magic, version, page, logical, count = struct.unpack_from('<8sIIQQ', blob)
    if magic != b'DBRDISK1' or version != 1 or page != 4096:
        raise ValueError('packed header mismatch')
    if not 0 < logical <= 1 << 40 or logical % 4096 or count > 65536 or count > (size-32)//16:
        raise ValueError('packed geometry mismatch')
    cursor, end = 32 + count*16, 0
    for i in range(count):
        offset, length = struct.unpack_from('<QQ', blob, 32+i*16)
        if not length or (offset | length) & 4095 or offset < end or offset > logical or length > logical-offset or length > size-cursor:
            raise ValueError('packed extent mismatch')
        cursor += length
        end = offset + length
    if cursor != size:
        raise ValueError('packed trailing bytes')
    return dict(encoded_sha256=digest, encoded_bytes=size, logical_bytes=logical,
                extents=count, format='DBRDISK1', apfs_validated=False,
                os_identity_validated=False, runtime_qualified=False)
