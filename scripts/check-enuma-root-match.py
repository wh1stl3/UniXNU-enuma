#!/usr/bin/env python3
"""Assert the declared /chosen/root-matching UUID names the media that carries the root.

Split out of scripts/audit-enuma-production-final-link.py on 2026-11-18. That script is one of
the 1078 inputs recorded in out/production-final-link-guard-20261113-r4/result.json, so editing
it fails the r4 reuse gate in scripts/build-enuma-owner-data.py and the audit's own
"build input changed after recording" self-pin; the two assertions cannot both hold in one
build. This checker reads only the candidate board and the verified policy reports, so it runs
against any candidate without rebuilding r4.

The official generator copies board.toml [payload.adt] root_match_volume_uuid verbatim into
/chosen/root-matching (UniXNU/scripts/unixnu/devicetree.py:324-327), and a published native UFS
window waits on the UUID inside its own signed policy (NativeUfsBlock::signedVolumeUuid).
reports[0] is the OS window, whose volume is the root being waited for. That report UUID is the
one audit-enuma-production-final-link.py:audit_image() re-derives from the final MachO bytes
(blob[40:56] of the VROOT01 policy), so the compared value is the signed one, not a constant
copied from a profile. --macho repeats that byte-side derivation here.

Exit 0: the board selects native UFS root and declares the signed OS window UUID, or the board
is a restore-ramdisk recipe that is out of scope. Exit 1: any mismatch or unreadable input.
"""
import argparse
import json
from pathlib import Path
import struct
import sys
import tomllib
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parents[1] / 'UniXNU'
DEFAULT_REPORTS = ROOT / 'out/verify-fresh-20261113'
# Where a candidate keeps the board it actually packaged, in lookup order. The last resort is the
# tracked default recipe, which is a restore-ramdisk build and is therefore skipped, not failed.
BOARD_LAYOUTS = ('device/board.toml', 'self-check/packaging/device/board.toml',
                 'self-check/device/board.toml', 'package/device/board.toml')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def find_board(build_dir):
    for relative in BOARD_LAYOUTS:
        path = build_dir / relative
        if path.is_file():
            return path
    tracked = ROOT / 'board.toml'
    require(tracked.is_file(), 'no board.toml under ' + str(build_dir) + ' or at ' + str(tracked))
    return tracked


def check_root_match(build_dir, reports):
    """The ADT root-match UUID must name the media that carries the root.

    build_dir is the candidate directory (or a packaging work directory holding device/board.toml).
    reports is [OS window, SystemOS window]; reports[0] is the root being waited for.
    """
    path = find_board(Path(build_dir))
    payload = tomllib.loads(path.read_text())['payload']
    declared = payload.get('adt', {}).get('root_match_volume_uuid')
    native = 'native-ufs-root=1' in payload['kernel_args']
    matches = None
    if native:
        require(declared is not None, 'native UFS root build declares no root_match_volume_uuid: ' + str(path))
        require(str(uuid.UUID(declared)).upper() == reports[0]['volume_uuid'],
                'root_match_volume_uuid ' + str(declared) + ' must be the signed OS window UUID ' +
                reports[0]['volume_uuid'] + ', not the restore ramdisk UUID (' + str(path) + ')')
        matches = True
    return {'board': str(path), 'native_ufs_root': native, 'declared': declared,
            'signed_os_volume_uuid': reports[0]['volume_uuid'], 'asserted': matches,
            'scope': 'declared /chosen/root-matching versus the OS VROOT01 policy UUID extracted from the final image; '
                     'restore-ramdisk-root boards are not compared'}


def load_reports(sources):
    """Accept verified policy report JSON files, or a directory holding os/ and systemos/ reports."""
    paths = []
    for source in sources:
        if source.is_dir():
            paths.extend(source / label / 'result.json' for label in ('os', 'systemos'))
        else:
            paths.append(source)
    result = []
    for path in paths:
        require(path.is_file(), 'missing verified policy report: ' + str(path))
        report = json.loads(path.read_text())
        require('volume_uuid' in report, 'verified policy report lacks volume_uuid: ' + str(path))
        result.append(report)
    require(result, 'no verified policy report given')
    return result


def signed_policy_uuids(macho_path):
    """Re-derive the embedded VROOT01 volume UUIDs from the final image bytes.

    Same extraction as audit-enuma-production-final-link.py:audit_image(): the policy table holds
    (pointer, length) pairs and the signed volume UUID is blob[40:56] of each VROOT01 record.
    """
    sys.path.insert(0, str(BASE / 'kits/XnuPrelink'))
    from native_prelink import macho, exports, backed_offset
    data = Path(macho_path).read_bytes()
    image = macho(data)
    by_name = {}
    for address, names in exports(data, image).items():
        for name in names:
            by_name.setdefault(name, []).append(address)

    def one(name):
        require(len(by_name.get(name, [])) == 1, 'missing/nonunique ' + name + ' in ' + str(macho_path))
        return by_name[name][0]

    def read(address, length):
        at = backed_offset(image['segments'], address, length, len(data))
        return data[at:at + length]

    count, = struct.unpack('<Q', read(one('_verified_root_policy_count'), 8))
    require(count >= 1, 'no embedded signed policy in ' + str(macho_path))
    pointers = struct.unpack('<' + 'Q' * (2 * count), read(one('_verified_root_policies'), count * 16))
    uuids = []
    for index in range(count):
        blob = read(pointers[2 * index], pointers[2 * index + 1])
        require(blob[:8] == b'VROOT01\0', 'bad embedded policy magic in ' + str(macho_path))
        uuids.append(str(uuid.UUID(bytes=blob[40:56])).upper())
    return uuids


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--build-dir', type=Path, default=Path.cwd(),
                        help='candidate directory holding the effective board; probed in order '
                             + ', '.join(BOARD_LAYOUTS) + ', then the tracked board.toml '
                             '(default: current directory)')
    parser.add_argument('--reports', type=Path, nargs='+', default=[DEFAULT_REPORTS],
                        help='verified policy report JSON files, or a directory with os/ and '
                             'systemos/ reports (default: out/verify-fresh-20261113)')
    parser.add_argument('--macho', type=Path,
                        help='optional final MachO; its embedded VROOT01 policy bytes must carry '
                             'the same OS window UUID as the report')
    args = parser.parse_args()
    build_dir = args.build_dir.resolve()
    try:
        require(build_dir.is_dir(), 'build dir does not exist: ' + str(build_dir))
        reports = load_reports(args.reports)
        record = check_root_match(build_dir, reports)
        if args.macho:
            uuids = signed_policy_uuids(args.macho)
            require(uuids[0] == record['signed_os_volume_uuid'],
                    'embedded OS policy UUID ' + uuids[0] + ' in ' + str(args.macho) +
                    ' differs from the verified report UUID ' + record['signed_os_volume_uuid'] +
                    ' (' + record['scope'] + ')')
            record['macho'] = {'path': str(args.macho), 'signed_os_volume_uuid': uuids[0],
                               'all_policy_uuids': uuids}
    except ValueError as error:
        print('root-match FAILED: ' + str(error), file=sys.stderr)
        return 1
    if not record['native_ufs_root']:
        print('SKIP: ' + record['board'] + ' does not select native-ufs-root=1; '
              'root-match is not compared')
        return 0
    print('OK: /chosen/root-matching ' + record['declared'] + ' == signed OS window ' +
          record['signed_os_volume_uuid'] + ' (board ' + record['board'] + ')')
    return 0


if __name__ == '__main__':
    sys.exit(main())
