"""Decode attributed cached DXE text; bind optional driver names to INF bytes.

No device calls or inferred statuses. Input is an explicit saved transcript,
not photo OCR. Sequence/ordinal do not identify a boot. Never auto-retry output.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import uuid

PHASES = {13: 'start-return', 14: 'load-return', 15: 'before-start',
          20: 'before-entry', 21: 'entry-return', 22: 'after-exit'}
HEADER = re.compile(r'DXE cached dropped=([0-9a-f]{16}) next=([0-9a-f]{16})')
EVENT = re.compile(r'DXE seq=([0-9a-f]{16}) p=([0-9a-f]{8}) phase=([a-z-]+) '
                   r'o=([0-9a-f]{8}) s=([0-9a-f]{16}|not-returned|not-a-return) guid=([0-9a-f-]{36}|-)')


def decode(text, catalog=None):
    rows = text.splitlines()
    if not rows or len(rows) > 129:
        raise ValueError('require complete header and at most 128 event rows')
    header = HEADER.fullmatch(rows[0])
    if not header:
        raise ValueError('missing canonical cached snapshot header')
    dropped, next_sequence = (int(x, 16) for x in header.groups())
    count = len(rows)-1
    if count != min(next_sequence, 128):
        raise ValueError('incomplete snapshot: row count disagrees with next sequence')
    if dropped != next_sequence-count:
        raise ValueError('loss counter disagrees with retained sequence range')
    events = []
    pending = {}
    for offset, row in enumerate(rows[1:]):
        match = EVENT.fullmatch(row)
        if not match:
            raise ValueError('noncanonical event row; do not guess missing characters')
        seq, point, phase, ordinal, status, guid = match.groups()
        seq, point = int(seq, 16), int(point, 16)
        if seq != next_sequence-count+offset or phase != PHASES.get(point, 'checkpoint'):
            raise ValueError('sequence gap/reordering or incorrect phase')
        expected = 'not-returned' if point in (15, 20) else 'not-a-return' if point not in (13, 14, 21, 22) else None
        if (expected is not None and status != expected) or (expected is None and not re.fullmatch('[0-9a-f]{16}', status)):
            raise ValueError('checkpoint cannot be reported as a returned status')
        if guid != '-' and str(uuid.UUID(guid)) != guid:
            raise ValueError('noncanonical GUID')
        event = dict(sequence=seq, point=point, phase=phase, ordinal_hex=ordinal,
                     status_hex=status if expected is None else None,
                     guid=None if guid == '-' else guid)
        if catalog and guid in catalog:
            event['driver_source'] = catalog[guid]
        if guid != '-':
            if point == 15:
                pending.setdefault(guid, []).append(seq)
            elif point == 13 and pending.get(guid):
                starts = pending.pop(guid)
                if len(starts) == 1:
                    event['preceding_start_sequence'] = starts[0]
                else:
                    event['ambiguous_start_sequences'] = starts
        events.append(event)
    return dict(scope='saved cached snapshot transcription; not live execution or boot identity',
                dropped=dropped, next_sequence=next_sequence, events=events,
                unclosed_before_start=pending,
                limitations=['Unclosed start may be in progress or truncated execution; not proof of a hang.',
                             'A prior start-return is not the current provider return.',
                             'INF name binds source metadata, not the packaged PE or driver execution.'],
                screen_log_verified=False, hardware_executed=False)


def inf_catalog(paths):
    result = {}
    for path in paths:
        raw = path.read_bytes()
        text = raw.decode('utf-8-sig')
        # Only fields in [Defines]; comments/other sections cannot name drivers.
        sections = re.split(r'^\s*\[([^\]]+)\]\s*$', text, flags=re.M)
        defines = [sections[i+1] for i in range(1, len(sections)-1, 2) if sections[i].strip().lower() == 'defines']
        if len(defines) != 1:
            raise ValueError('INF must have one Defines section: ' + str(path))
        def field(name):
            found = re.findall(r'^\s*'+name+r'\s*=\s*([^#\r\n]+)', defines[0], re.M)
            if len(found) != 1:
                raise ValueError('INF field missing/ambiguous: ' + name)
            return found[0].strip()
        guid = str(uuid.UUID(field('FILE_GUID')))
        binding = dict(name=field('BASE_NAME'), path=str(path.resolve()), sha256=hashlib.sha256(raw).hexdigest())
        result.setdefault(guid, []).append(binding)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--transcript', type=Path, required=True)
    p.add_argument('--inf', type=Path, action='append', default=[])
    args = p.parse_args()
    raw = args.transcript.read_bytes()
    try:
        result = decode(raw.decode('ascii'), inf_catalog(args.inf))
    except (ValueError, UnicodeError) as exc:
        p.error(str(exc))
    result['transcript_sha256'] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
