"""Check the published firmware gitlink, exact migrated bytes and board contract."""
import hashlib
import json
from pathlib import Path
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def main():
    lock = json.loads((ROOT/'config/uefi-source.lock.json').read_text())
    source = ROOT/lock['path']
    def git(path, *args):
        return subprocess.check_output(['git','-c','safe.directory='+path.as_posix(),
                                        '-C',str(path),*args],text=True).strip()
    assert git(source,'rev-parse','HEAD') == lock['commit']
    assert git(ROOT,'ls-files','--stage','--',lock['path']) == '160000 '+lock['commit']+' 0\t'+lock['path']
    assert git(ROOT,'config','--file','.gitmodules','submodule.firmware.url') == lock['repository']
    assert not git(source,'status','--porcelain','--ignore-submodules=all')
    for name, wanted in lock['file_sha256'].items():
        assert hashlib.sha256((source/name).read_bytes()).hexdigest() == wanted, name
    migration = json.loads((source/'Resources/Enuma/migration.json').read_text())
    for old, item in migration['files'].items():
        assert hashlib.sha256((source/item['destination']).read_bytes()).hexdigest() == item['sha256'], old
    old = tomllib.loads(git(ROOT,'show','1ab7ee8:board.toml'))
    board = tomllib.loads((ROOT/'board.toml').read_text())
    assert {k:v for k,v in board.items() if k!='firmware'} == old
    assert board['firmware']['preflight'] == ['scripts/enuma_firmware_preflight.py']
    expected = ['patches/dxe-stage-checkpoints.patch','patches/dxe-dispatch-return.patch',
                'patches/dxe-driver-checkpoints.patch','Resources/MuPatches/Gic-Spurious.patch']
    assert board['firmware']['patches'] == expected
    (ROOT/'reports/enuma-firmware-source-migration.json').write_text(json.dumps({
        'scope':'source migration and official board configuration only; no device execution',
        'firmware_repository':lock['repository'],'firmware_commit':lock['commit'],
        'source_device_commit':migration['device_commit'],'migrated_files':migration['files'],
        'new_firmware_table':board['firmware'],'other_board_tables_unchanged':True,
        'firmware_input_files_checked':len(lock['file_sha256'])},indent=2)+'\n')
    print('PASS: fixed firmware gitlink, migrated bytes and official table; all other board tables unchanged')


if __name__=='__main__':main()
