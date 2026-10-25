"""One authorized full-input temporary boot with camera; offline by default.

Run --camera-check or --execute with the existing Python3.12 camera environment.
No partition flash/erase/slot change. Reuses the guarded entry/recovery runner.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def qualification(published=False, report=None):
    report = (report or ROOT / 'reports/enuma-ram-payload-qualification.json').resolve()
    if not any(report.is_relative_to(ROOT / folder) for folder in ['out', 'reports']):
        raise ValueError('qualification must stay inside repository out/ or reports/')
    q = json.loads(report.read_text())
    if q.get('trial_kind') in ('inherited-video-audit','inherited-video-entry-control'):
        frozen=(ROOT/q['archive']/'qualification.json').resolve()
        if not frozen.is_relative_to((ROOT/'out').resolve()) or json.loads(frozen.read_text())!=q:
            raise ValueError('video audit differs from frozen qualification')
        expected=0 if q['trial_kind']=='inherited-video-entry-control' else 330
        if q.get('terminal_return')!={'pass':2,'fail':7,'completion_fallback':False}:
            raise ValueError('video trials require symmetric terminal return; old dispatcher-fallback profiles are consumed/historical')
        if q.get('pixel_access') is not False or q.get('gop_published') is not False or q.get('maximum_reads')!=expected:
            raise ValueError('unsupported video audit scope')
        query=q.get('topology_status_query',0)
        if type(query) is not int or query not in (0,1,2) or (query and (expected!=330 or q.get('topology_status_value')!=13)):
            raise ValueError('unsupported topology status classification')
        if expected==0 and q.get('control_actual_code',{}).get('review_required') is not False:
            raise ValueError('actual control PE disassembly still needs review')
    if 'detail_point' in q:
        frozen_manifest = (ROOT / q['archive'] / 'qualification.json').resolve()
        if not frozen_manifest.is_relative_to((ROOT / 'out').resolve()) or json.loads(frozen_manifest.read_text()) != q:
            raise ValueError('boundary report differs from frozen qualification manifest')
        fat = json.loads((ROOT / 'reports/enuma-full-payload.json').read_text())
        if (q['detail_point'] not in (13, 15, 20, 21, 22) or q['target_guid'] != '4138022f-06c7-4f79-9c94-7e33b511a4e7'
                or q.get('completion_fallback_enabled') is not False or q.get('ram_payload_sha256') != fat['payload_sha256']):
            raise ValueError('boundary mode requires exact DisplayDxe pre-call/entry/return, full FAT and no fallback')
    pin = json.loads((ROOT / 'config/uefi-source.lock.json').read_text())
    if q['firmware_commit'] != pin['commit']:
        raise ValueError('qualification differs from current firmware pin')
    for name, entry in q['files'].items():
        p = (ROOT / q['archive'] / name).resolve()
        if not p.is_relative_to((ROOT / 'out').resolve()) or digest(p) != entry['sha256']:
            raise ValueError('immutable archive differs: ' + name)
    image = (ROOT / q['image']).resolve()
    if not image.is_relative_to((ROOT / 'out').resolve()) or digest(image) != q['image_sha256']:
        raise ValueError('candidate differs')
    if published:
        for repo in (ROOT, ROOT / 'firmware'):
            def git(*args):
                return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()
            if git('status', '--porcelain', '--ignore-submodules=all'):
                raise ValueError('source/current documents must be clean before a trial')
            head = git('rev-parse', 'HEAD')
            if git('ls-remote', 'origin', 'refs/heads/main').split()[0] != head:
                raise ValueError('source/current documents must be pushed before a trial')
            if repo.name == 'firmware' and head != q['firmware_commit']:
                raise ValueError('firmware checkout differs')
        if (ROOT / 'out/device-tests' / ('consumed-' + q['image_sha256'] + '.local.json')).exists():
            raise ValueError('candidate already issued; do not repeat a failed/consumed image')
    return q, image


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--camera-check', action='store_true')
    mode.add_argument('--execute', action='store_true')
    p.add_argument('--qualification', type=Path, help='explicit full-input/no-fallback pre-call or return qualification; defaults to full-chain report')
    a = p.parse_args()
    if not a.camera_check:
        q, image = qualification(a.execute, a.qualification)
        if not a.execute:
            print('PASS: qualified full-input candidate; offline only, no camera/device operation')
            return
    sys.path.insert(0, str(ROOT / 'out/camera-tools-py312'))
    import cv2
    stamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    out = ROOT / 'out/camera-capture' / (stamp + '-system-transport')
    out.mkdir()
    report = dict(scope='host camera preflight; device action only with --execute',
                  started_utc=datetime.now(timezone.utc).isoformat(), camera_ready=False,
                  device_runner_started=False, boot_issued=False)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    writer = process = log = None
    try:
        if not cap.isOpened(): raise RuntimeError('camera index0 DirectShow unavailable; no device command issued')
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920); cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        for _ in range(10): ok, frame = cap.read()
        if not ok: raise RuntimeError('no camera frame; no device command issued')
        h, w = frame.shape[:2]
        cv2.imwrite(str(out / 'before-raw.jpg'), frame)
        cv2.imwrite(str(out / 'before-rotated.jpg'), cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE))
        report.update(camera_ready=True, width=w, height=h, rotation='90 clockwise; inspect actual orientation', opencv=cv2.__version__)
        if a.camera_check:
            print('PASS: camera frames saved; host only, no device command')
            return
        video = out / 'system-transport.avi'
        writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'MJPG'), 5, (w, h))
        if not writer.isOpened(): raise RuntimeError('video writer failed; no device command issued')
        log = (out / 'runner.log').open('w', encoding='utf-8')
        label = 'dxe-driver-return' if 'detail_point' in q else 'system-transport'
        process = subprocess.Popen([sys.executable, '-X', 'utf8', '-u', '-B', str(ROOT / 'scripts/run_enuma_entry_probe.py'),
                                    '--image', str(image), '--label', label], cwd=ROOT,
                                   stdout=log, stderr=subprocess.STDOUT)
        report['device_runner_started'] = True
        start = time.monotonic(); last = -1; finished = None; times = []
        while time.monotonic() - start < 240:
            ok, frame = cap.read()
            if not ok: raise RuntimeError('camera lost; stop runner and reconcile device before any new trial')
            now = time.monotonic() - start
            if not times or now - times[-1] >= 0.19:
                writer.write(frame); times.append(now)
                second = int(now * 2)
                if second != last:
                    cv2.imwrite(str(out / ('frame-%04d-raw.jpg' % second)), frame)
                    cv2.imwrite(str(out / ('frame-%04d-rotated.jpg' % second)), cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE))
                    last = second
            if process.poll() is not None:
                if finished is None: finished = time.monotonic()
                if time.monotonic() - finished >= 3: break
        else:
            raise RuntimeError('host bound reached; no further candidate, reconcile recovery')
        writer.release(); writer = None
        report.update(runner_exit=process.returncode, frames=len(times), frame_timestamps_seconds=times,
                      video=video.relative_to(ROOT).as_posix(), video_sha256=digest(video))
        reader = cv2.VideoCapture(str(video)); decoded = 0
        while True:
            ok, _ = reader.read()
            if not ok: break
            decoded += 1
        reader.release(); report['decoded_frames'] = decoded
        if decoded != len(times): raise RuntimeError('camera decode mismatch; no further candidate')
        print('Camera evidence saved; runner exit=' + str(process.returncode), flush=True)
        if process.returncode: raise RuntimeError('runner did not complete recovery; inspect runner.log and reconcile')
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        if process is not None and process.poll() is None:
            process.terminate(); process.wait(timeout=15)
        if writer is not None: writer.release()
        if log is not None: log.close()
        cap.release()
        if report['device_runner_started']:
            state = json.loads((ROOT / 'out/device-tests/current.local.json').read_text())
            if state.get('candidate_sha256') == q['image_sha256'] and state.get('issued_at'):
                report['boot_issued'] = True
                write(ROOT / 'out/device-tests' / ('consumed-' + q['image_sha256'] + '.local.json'),
                      dict(image_sha256=q['image_sha256'], evidence=out.relative_to(ROOT).as_posix(), phase=state['phase']))
        write(out / 'observation.json', report)
        write(ROOT / 'reports/enuma-system-trial-camera.json', report)


if __name__ == '__main__':
    main()
