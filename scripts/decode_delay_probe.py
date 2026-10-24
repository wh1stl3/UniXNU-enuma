"""Decode the values that came back through the reset-delay channel.

The firmware encodes four bits of a display register into the length of the
reset delay: one second per bit value, on top of a two second base. The host
sees the whole thing as a longer return time, so the measured return time minus
the plain two second baseline is the encoded nibble.

Usage:
  python scripts/decode_delay_probe.py 22.365 21.0 17.2 ...
  python scripts/decode_delay_probe.py --baseline 16.7 22.365 21.0 ...
"""
import sys

BASE = 16.7  # return time of the same profile with the plain two second delay


def decode(seconds, baseline):
    code = round(seconds - baseline)
    if code < 0 or code > 15:
        return None
    return code


def main():
    args = sys.argv[1:]
    baseline = BASE
    if args and args[0] == '--baseline':
        baseline = float(args[1])
        args = args[2:]
    if not args:
        raise SystemExit('give at least one measured return time')
    for index, raw in enumerate(args):
        seconds = float(raw)
        code = decode(seconds, baseline)
        if code is None:
            print(f'probe {index}: {seconds:.3f}s -> out of range')
            continue
        print(f'probe {index}: {seconds:.3f}s -> nibble {code} (0b{code:04b})')


if __name__ == '__main__':
    main()
