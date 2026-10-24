"""One authorized A trial with timestamped external-camera evidence. Default: camera only.

No flash/erase/slot changes. The existing guarded runner owns device operations.
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
IMAGE_SHA = '29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4'
ARCHIVE = ROOT / 'out/display-entry-boundary/pre-entry-aa9ec66'


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--camera-index', type=int, default=0)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT / 'out/camera-tools-py312'))
    import cv2
    from reconcile_enuma_recovery import atomic_json
    qualification = json.loads((ARCHIVE / 'qualification.json').read_text())
    for name, meta in qualification['files'].items():
        if hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest() != meta['sha256']:
            raise ValueError('Archived artifact changed: ' + name)
    image = ROOT / 'out/boot-candidate/display-pre-entry-aa9ec66-boot-v3.img'
    package = json.loads(image.with_suffix('.json').read_text())
    if (qualification['detail_point'] != 15 or package['image_sha256'] != IMAGE_SHA or
            hashlib.sha256(image.read_bytes()).hexdigest() != IMAGE_SHA):
        raise ValueError('Only the approved A image is accepted')
    ledger = ROOT / 'reports/enuma-display-boundary-device.json'
    if args.execute:
        from run_value_probes import require_published
        require_published(ROOT)
        pin = json.loads((ROOT / 'config/uefi-source.lock.json').read_text())
        if qualification['firmware_commit'] != pin['commit']:
            raise ValueError('Firmware pin changed')
        for name, wanted in pin['file_sha256'].items():
            if hashlib.sha256((ROOT / 'firmware' / name).read_bytes()).hexdigest() != wanted:
                raise ValueError('Firmware source changed')
        if ledger.exists():
            raise ValueError('A trial ledger already exists; never repeat this image')
        for path in (ROOT / 'out/device-tests').glob('*/result.json'):
            trial = json.loads(path.read_text())
            if trial.get('candidate_sha256') == IMAGE_SHA and trial.get('issued_at'):
                raise ValueError('A image has already been issued')
    out = ROOT / 'out/camera-capture' / (datetime.now().strftime('%Y%m%dT%H%M%S') + '-display-boundary-A')
    out.mkdir(parents=True)
    camera = cv2.VideoCapture(args.camera_index, cv2.CAP_DSHOW)
    writer = None
    process = None
    log = None
    summary = {'scope': 'host camera only' if not args.execute else 'single approved A temporary boot with camera',
               'started_at_utc': stamp(), 'directory': str(out.relative_to(ROOT)),
               'candidate_sha256': IMAGE_SHA, 'runner_started': False, 'frame_samples': []}
    try:
        if not camera.isOpened():
            raise RuntimeError('Camera unavailable; no device action')
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        frame = None
        for _ in range(10):
            ok, sample = camera.read()
            if ok:
                frame = sample
        if frame is None:
            raise RuntimeError('No camera frame; no device action')
        cv2.imwrite(str(out / 'before-raw.jpg'), frame)
        cv2.imwrite(str(out / 'before-rotated.jpg'), cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE))
        summary.update(width=frame.shape[1], height=frame.shape[0], rotation='90 degrees clockwise; raw preserved')
        atomic_json(ROOT / 'out/camera-capture/display-boundary-active.local.json', {'directory': str(out)})
        if not args.execute:
            print('PASS: camera and immutable candidate; camera-only snapshot ' + str(out), flush=True)
            return
        writer = cv2.VideoWriter(str(out / 'raw.avi'), cv2.VideoWriter_fourcc(*'MJPG'), 10,
                                 (frame.shape[1], frame.shape[0]))
        if not writer.isOpened():
            raise RuntimeError('Video writer unavailable; no device action')
        row = {'status': 'runner-starting', 'image_sha256': IMAGE_SHA,
               'started_at_utc': stamp(), 'camera_directory': str(out.relative_to(ROOT)),
               'device_boot_command_issued': False}
        atomic_json(ledger, row)
        log = (out / 'runner.log').open('w', encoding='utf-8')
        process = subprocess.Popen([sys.executable, '-X', 'utf8', '-u', '-B',
                                   str(ROOT / 'scripts/run_enuma_entry_probe.py'), '--image', str(image),
                                   '--label', 'dxe-driver-return'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        summary['runner_started'] = True
        summary['runner_started_at_utc'] = stamp()
        start = time.monotonic()
        next_video = next_sample = 0.0
        finished = None
        print('Camera active; exactly one guarded A trial started', flush=True)
        while time.monotonic() - start < 205:
            ok, frame = camera.read()
            now = time.monotonic() - start
            if not ok:
                summary['camera_error_at_utc'] = stamp()
                # Do not kill the recovery runner. Continue its bounded observation.
                if process.poll() is not None:
                    break
                time.sleep(0.1)
                continue
            if now >= next_video:
                writer.write(frame)
                summary.setdefault('video_frame_times_seconds', []).append(now)
                next_video = now + 0.1
            if now >= next_sample:
                name = f'frame-{len(summary["frame_samples"]):03d}'
                cv2.imwrite(str(out / (name + '-raw.jpg')), frame)
                cv2.imwrite(str(out / (name + '-rotated.jpg')), cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE))
                summary['frame_samples'].append({'stem': name, 'at_utc': stamp(), 'relative_seconds': now})
                next_sample = now + 1.0
            if process.poll() is not None:
                if finished is None:
                    finished = time.monotonic()
                if time.monotonic() - finished > 3:
                    break
        if process.poll() is None:
            summary['host_bound_reached'] = True
            # No follow-up device commands; preserve the running recovery observer.
            raise RuntimeError('Host observation bound reached; inspect state, no extra boots')
        summary['runner_exit'] = process.returncode
        state = json.loads((ROOT / 'out/device-tests/current.local.json').read_text())
        owned = state.get('candidate_sha256') == IMAGE_SHA
        row.update(status='returned' if owned and process.returncode == 0 and state.get('phase') == 'recovered-android-boot-complete'
                   else 'failed-or-not-issued', runner_exit=process.returncode,
                   phase=state.get('phase'), candidate_state_matches=owned,
                   device_boot_command_issued=bool(owned and state.get('issued_at')),
                   evidence=str(Path(state['directory']).relative_to(ROOT)) if owned else None)
        if owned:
            for name in ['issued_at_utc', 'issued_monotonic', 'boot_command_return_seconds',
                         'fastboot_disconnect_observed_seconds', 'fastboot_return_seconds',
                         'adb_return_seconds', 'boot_complete_seconds', 'partition_digests_unchanged']:
                if name in state:
                    row[name] = state[name]
        atomic_json(ledger, row)
        print(json.dumps(row, indent=2), flush=True)
    finally:
        if writer is not None:
            writer.release()
            video = out / 'raw.avi'
            if video.exists():
                summary['video_sha256'] = hashlib.sha256(video.read_bytes()).hexdigest()
        camera.release()
        if log is not None:
            log.close()
        summary['finished_at_utc'] = stamp()
        atomic_json(out / 'observation.json', summary)
    if process is not None and process.returncode:
        raise SystemExit(process.returncode)


if __name__ == '__main__':
    main()
