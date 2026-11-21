#!/usr/bin/env python3
"""Conservative, synthetic-only UFS handoff event interpreter; never PASS."""
import json
import sys

LIMIT = 1 << 64
CATEGORIES = {'descriptor', 'data', 'bounce', 'task', 'mapping'}


def interval(obj):
    start, length = obj['pa'], obj['length']
    if type(start) is not int or type(length) is not int or start < 0 or length <= 0 or start >= LIMIT or start + length > LIMIT:
        raise ValueError('invalid or overflowing interval')
    return start, start + length


def interpret(log):
    try:
        if log['schema'] != 1 or log['lost'] != 0 or log['overflow'] is not False:
            raise ValueError('schema or lost records')
        events = log['events']
        if not isinstance(events, list) or not events:
            raise ValueError('missing events')
        allocations, active, mappings = {}, {}, set()
        window = None
        ebs = 0
        last = None
        risk = None
        for seq, e in enumerate(events):
            if e['seq'] != seq:
                raise ValueError('event sequence gap')
            kind = e['kind']
            if ebs and kind != 'end':
                raise ValueError('event after EBS')
            if kind == 'window':
                if window is not None:
                    raise ValueError('duplicate window')
                window = interval(e)
            elif kind == 'alloc':
                key = e['id']
                if key in allocations or e['category'] not in CATEGORIES or e['owner'] not in ('loader', 'firmware', 'caller', 'unknown') or type(e['efi_type']) is not int or e['efi_type'] < 0 or e['source'] not in ('pages', 'reuse', 'unknown'):
                    raise ValueError('invalid allocation metadata')
                allocations[key] = (interval(e), e['source'], e['owner'])
            elif kind == 'map':
                if e['id'] not in allocations or e['id'] in mappings:
                    raise ValueError('unmatched map')
                mappings.add(e['id'])
            elif kind == 'unmap':
                if e['id'] not in mappings or any(e['id'] in ids for ids in active.values()):
                    raise ValueError('unmap missing or DMA active')
                mappings.remove(e['id'])
            elif kind == 'submit':
                ids = e['ids']
                if not isinstance(ids, list) or not ids or e['request'] in active or any(i not in allocations for i in ids):
                    raise ValueError('unmatched submission')
                active[e['request']] = ids
            elif kind == 'complete':
                if e['request'] not in active or e['status'] not in ('success', 'failure', 'timeout'):
                    raise ValueError('unmatched completion')
                last = e['status']
                if last == 'success':
                    del active[e['request']]
            elif kind in ('release', 'reuse'):
                key = e['id']
                if key not in allocations or key in mappings or any(key in ids for ids in active.values()):
                    raise ValueError('release/reuse missing or DMA active')
                del allocations[key]
            elif kind == 'ebs':
                if e['attempt'] != 1 or e['status'] != 'success':
                    raise ValueError('failed or retried EBS')
                ebs += 1
            elif kind == 'end':
                if seq != len(events) - 1 or ebs != 1:
                    raise ValueError('invalid terminal')
            else:
                raise ValueError('unknown event')
        if events[-1]['kind'] != 'end' or not ebs or window is None or last is None or active:
            raise ValueError('incomplete lifecycle')
        for extent, source, owner in allocations.values():
            if max(window[0], extent[0]) < min(window[1], extent[1]):
                risk = 'observed live backing overlaps loader window'
            if source == 'unknown' or owner == 'unknown':
                raise ValueError('unknown backing provenance')
        if risk:
            return 'RISK', risk
        return 'UNKNOWN', 'no observed overlap; source coverage and producer exclusion unproven'
    except (KeyError, TypeError, ValueError) as exc:
        return 'UNKNOWN', str(exc)


def main():
    try:
        with open(sys.argv[1], encoding='utf-8') as f:
            result = interpret(json.load(f))
    except (OSError, ValueError, IndexError) as exc:
        result = ('UNKNOWN', str(exc))
    print(json.dumps({'result': result[0], 'reason': result[1]}))
    return 0 if result[0] == 'RISK' else 2


if __name__ == '__main__':
    sys.exit(main())
