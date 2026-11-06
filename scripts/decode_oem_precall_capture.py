"""Validate complete externally saved pre-forward frames; never infer a hang."""
import re
from decode_oem_service_trace import decode

MARKER = re.compile(r'OEM capture (begin|end) session=([0-9a-f]{16}) selected=([0-9a-f]{16})')
END = re.compile(r'OEM capture end session=([0-9a-f]{16}) selected=([0-9a-f]{16}) hash=([0-9a-f]{16})')


def decode_capture(text, session, selected):
    if not text.endswith('\n'):
        raise ValueError('partial capture terminator')
    rows = text.splitlines()
    if not 4 <= len(rows) <= 131:
        raise ValueError('complete bounded capture required')
    begin, end = MARKER.fullmatch(rows[0]), END.fullmatch(rows[-1])
    if not begin or not end or begin[1] != 'begin':
        raise ValueError('missing capture boundary')
    expected = (f'{session:016x}', f'{selected:016x}')
    if session <= 0 or begin.groups()[1:] != expected or end.groups()[:2] != expected:
        raise ValueError('capture identity mismatch')
    if '\r' in text:
        raise ValueError('noncanonical line endings')
    digest = 14695981039346656037
    for byte in ('\n'.join(rows[:-1])+'\n').encode('ascii'):
        digest = ((digest ^ byte) * 1099511628211) & (2**64-1)
    if digest != int(end[3], 16):
        raise ValueError('capture integrity mismatch')
    result = decode('\n'.join(rows[1:-1]))
    events = [event for event in result['events'] if event['call'] == selected]
    if len(events) != 1 or events[0]['phase'] != 'enter':
        raise ValueError('selected pre-forward entry missing or already returned')
    if result['assessment']['recording_counter_exhausted']:
        raise ValueError('counter exhausted')
    result.update(session=session, selected_call=selected, framing_complete=True,
                  stream_integrity='FNV1a64; accidental corruption check, not authentication',
                  observation='snapshot exported before forwarding selected service',
                  forwarded_call_execution_proven=False)
    result['limitations'].append('Pre-forward export does not prove the original service was entered; output or transition can fail afterwards.')
    return result
