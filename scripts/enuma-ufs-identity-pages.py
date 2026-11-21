#!/usr/bin/env python3
"""Bounded ASCII QR payload framing/manual-page model, no display/device access."""
import base64
import hashlib
import math

MAX_BYTES = 3 * 1024 * 1024
MAX_PAGES = 8192


def encode(data, chunk=384):
    if not data or len(data) > MAX_BYTES or not 64 <= chunk <= 768:
        raise ValueError('snapshot/frame size bound')
    checksum = hashlib.sha256(data).hexdigest()
    total = math.ceil(len(data) / chunk)
    if total > MAX_PAGES:
        raise ValueError('page count bound')
    return [f'EUI2|{checksum[:16]}|{i+1}|{total}|{len(data)}|{checksum}|'
            + base64.b64encode(data[i*chunk:(i+1)*chunk]).decode('ascii') for i in range(total)]


def decode(pages):
    if not pages or len(pages) > MAX_PAGES:
        raise ValueError('missing/bounded pages')
    common = None; chunks = {}
    for page in pages:
        if not isinstance(page, str) or not page.isascii() or len(page) > 1200:
            raise ValueError('invalid ASCII page')
        fields = page.split('|')
        if len(fields) != 7 or fields[0] != 'EUI2':
            raise ValueError('invalid frame')
        _, identity, index, total, length, checksum, payload = fields
        index, total, length = int(index), int(total), int(length)
        if len(checksum) != 64 or identity != checksum[:16] or not 1 <= total <= MAX_PAGES or not 0 < length <= MAX_BYTES:
            raise ValueError('invalid snapshot header')
        key = (identity, total, length, checksum)
        if common is None:
            common = key
        if key != common or not 1 <= index <= total or index in chunks:
            raise ValueError('mixed snapshot/duplicate/out-of-range page')
        chunks[index] = base64.b64decode(payload, validate=True)
    if len(chunks) != common[1]:
        raise ValueError('missing pages')
    data = b''.join(chunks[i] for i in range(1, common[1]+1))
    if len(data) != common[2] or hashlib.sha256(data).hexdigest() != common[3]:
        raise ValueError('length/checksum mismatch')
    return data


class ManualPages:
    """Explicit host input model. No timers, recapture, rotate or continue-XNU event."""
    def __init__(self, count):
        if not 1 <= count <= MAX_PAGES:
            raise ValueError('page count')
        self.count = count; self.index = 0; self.exited = False

    def event(self, key):
        if self.exited:
            return
        if key == 'UP':
            self.index = max(0, self.index - 1)
        elif key == 'DOWN':
            self.index = min(self.count - 1, self.index + 1)
        elif key in ('SCAN_SUSPEND', 'ENTER', 'ESC'):
            self.exited = True
        else:
            raise ValueError('unsupported input event')


def summary_layout(parsed, width, content_height):
    """Geometry/clipping only, NOT a real font/GOP renderer or SetMode request."""
    if not 0 < width <= 16384 or not 0 < content_height <= 16384 or width * content_height * 4 > 64 * 1024 * 1024:
        raise ValueError('zero/overflow/oversized content region')
    envelope = parsed['envelope']; summary = parsed['summary']
    lines = ['CACHED ONLY', f'COMPLETE: {parsed["global_uniqueness_eligible"]}',
             f'COUNT: {envelope["reported_handles"]}/64',
             f'UFS LUN: {summary["ufs_lun_candidate"]}',
             f'USERDATA: {summary["userdata"]}', summary['reason']]
    columns = (width - 16) // 16
    height = len(lines) * 32 + 16
    if columns < 12 or height + 32 > content_height:
        raise ValueError('content too small for large summary and QR')
    clipped = [line if len(line) <= columns else line[:columns-1] + '~' for line in lines]
    return {'lines': clipped, 'cell_width': 16, 'cell_height': 32,
            'summary_height': height, 'qr_region': min(width-16, content_height-height-16)}
