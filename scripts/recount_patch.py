"""Recount the line numbers in a unified diff hunk header.

Editing a patch by hand means the hunk header no longer matches the body, and
git then refuses it with "corrupt patch". This tool recomputes the old and new
counts of every hunk from the body itself, so the header always follows the
content.

Usage: python scripts/recount_patch.py <patch file> [...]
"""
import re
import sys
from pathlib import Path

HUNK = re.compile(rb'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')


def recount(path):
    raw = path.read_bytes().replace(b'\r\n', b'\n')
    lines = raw.split(b'\n')
    # a trailing newline produces an empty final element; it is not body text
    if lines and lines[-1] == b'':
        lines.pop()
    out = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = HUNK.match(line)
        if not match:
            out.append(line)
            index += 1
            continue
        body = []
        index += 1
        while index < len(lines):
            item = lines[index]
            if item.startswith(b'@@') or item.startswith(b'--- ') or item.startswith(b'+++ '):
                break
            body.append(item)
            index += 1
        # git treats a completely empty line as a context line whose trailing
        # space was stripped, so it counts on both sides.
        def is_context(item):
            return item == b'' or item.startswith(b' ')
        old = sum(1 for item in body if is_context(item) or item.startswith(b'-'))
        new = sum(1 for item in body if is_context(item) or item.startswith(b'+'))
        out.append(b'@@ -%s,%d +%s,%d @@' % (match.group(1), old, match.group(3), new))
        out.extend(body)
    path.write_bytes(b'\n'.join(out) + b'\n')
    return len([line for line in out if HUNK.match(line)])


def main():
    if len(sys.argv) < 2:
        raise SystemExit('give at least one patch file')
    for name in sys.argv[1:]:
        path = Path(name)
        count = recount(path)
        print(f'{name}: {count} hunk header(s) recounted')


if __name__ == '__main__':
    main()
