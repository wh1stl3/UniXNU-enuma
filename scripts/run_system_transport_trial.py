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
import re

ROOT = Path(__file__).resolve().parents[1]


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def qualification(published=False, report=None):
    report = (report or ROOT / 'reports/enuma-ram-payload-qualification.json').resolve()
    if not any(report.is_relative_to(ROOT / folder) for folder in ['out', 'reports']):
        raise ValueError('qualification must stay inside repository out/ or reports/')
    q = json.loads(report.read_text())
    if q.get('trial_kind') in ('ramoops-canary','ramoops-map-control','ramoops-header-read','ramoops-warm-control'):
        control = q['trial_kind'] in ('ramoops-map-control','ramoops-header-read','ramoops-warm-control')
        frozen = (ROOT / q['archive'] / 'qualification.json').resolve()
        if not frozen.is_relative_to((ROOT/'out').resolve()) or json.loads(frozen.read_text()) != q:
            raise ValueError('ramoops candidate differs from frozen qualification')
        nonce = q.get('nonce', '')
        expected = dict(base='0xB0000000', size='0x200000', marker_bytes=0 if control else 44, stage=10,
                        delay_seconds=2, reset='cold' if control else 'warm-with-cold-fallback', pmsg_access=False)
        if q['trial_kind']=='ramoops-header-read':expected['header_read_offsets']=[0,4,8]
        if q['trial_kind']=='ramoops-warm-control':expected['reset']='warm-with-cold-fallback'
        bad_nonce = nonce is not None if control else (not isinstance(nonce,str) or re.fullmatch('[0-9a-f]{32}', nonce) is None)
        if (bad_nonce or q.get('ramoops_scope') != expected or
            q.get('review_required') is not False or q.get('pixel_access') is not False):
            raise ValueError('R-017 exact console scope or actual code qualification missing')
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
        target=q.get('reason_target',0);reason_query=q.get('reason_query',0)
        if (type(target) is not int or target not in range(5) or type(reason_query) is not int or reason_query not in (0,1,2) or
            bool(target)!=bool(reason_query) or (target and (query or expected!=330))):
            raise ValueError('unsupported first-reason classification')
        if expected==0 and q.get('control_actual_code',{}).get('review_required') is not False:
            raise ValueError('actual control PE disassembly still needs review')
    if q.get('trial_kind')=='native-display-observe':
        frozen=(ROOT/q['archive']/'qualification.json').resolve()
        if not frozen.is_relative_to((ROOT/'out').resolve()) or json.loads(frozen.read_text())!=q:
            raise ValueError('native observer differs from frozen qualification')
        control=q.get('native_control',False)
        if (type(control) is not bool or (control and q.get('boot_clock_capture') is not True) or
            type(q.get('native_query')) is not int or q.get('native_query') not in (1,2) or q.get('maximum_reads')!=(0 if control else 26) or
            q.get('maximum_wait_calls')!=(0 if control else 2) or q.get('maximum_mmio_offset')!=(None if control else '0x6c26c') or
            q.get('pixel_access') is not False or q.get('gop_published') is not False or
            q.get('terminal_return')!={'pass':2,'fail':7,'completion_fallback':False}):
            raise ValueError('native observer scope invalid')
        if published:
            review=json.loads((ROOT/'reports/enuma-native-display-code.json').read_text())
            matching=[x for x in review.get('queries',[]) if x.get('image_sha256')==q['image_sha256'] and
                      x.get('native_query')==q['native_query'] and
                      x.get('provider_sha256')==q['files']['SimpleFbDxe.efi']['sha256'] and
                      x.get('core_sha256')==q['files']['DxeCore.efi']['sha256']]
            if q.get('review_required') is not False or review.get('review_required') is not False or review.get('firmware_commit')!=q['firmware_commit'] or len(matching)!=1:
                raise ValueError('native actual PE code review missing or mismatched')
    if q.get('trial_kind')=='native-display-mask':
        from native_mask_decode import make_plan
        frozen=(ROOT/q['archive']/'qualification.json').resolve()
        if not frozen.is_relative_to((ROOT/'out').resolve()) or json.loads(frozen.read_text())!=q:
            raise ValueError('native mask differs from frozen qualification')
        expected={'native_query':1,'native_control':False,'boot_clock_capture':True,
                  'maximum_reads':26,'maximum_wait_calls':2,'maximum_mmio_offset':'0x6c26c',
                  'pixel_access':False,'gop_published':False,
                  'terminal_return':{'code_delays_seconds':[2,7,12,17,22],'completion_fallback':False}}
        if any(type(q.get(k)) is not type(v) or q.get(k)!=v for k,v in expected.items()):
            raise ValueError('native mask scope invalid')
        if type(q.get('native_mask_field')) is not int or q['native_mask_field'] not in range(1,8):
            raise ValueError('invalid native mask field')
        calibration=ROOT/'reports/enuma-boot-clock-calibration.json'
        if q.get('decode_plan')!=make_plan(ROOT) or q.get('calibration_sha256')!=digest(calibration) or json.loads(calibration.read_text()).get('calibration_passed') is not True:
            raise ValueError('fixed boot clock calibration/plan differs')
        if published:
            review=json.loads((ROOT/'reports/enuma-native-mask-code.json').read_text())
            if (q.get('review_required') is not False or review.get('review_required') is not False or
                review.get('firmware_commit')!=q['firmware_commit'] or review.get('image_sha256')!=q['image_sha256'] or
                review.get('provider_sha256')!=q['files']['SimpleFbDxe.efi']['sha256'] or
                review.get('core_sha256')!=q['files']['DxeCore.efi']['sha256']):
                raise ValueError('actual mask/Core code review missing or mismatched')
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
        if q.get('trial_kind') in ('ramoops-canary','ramoops-map-control','ramoops-header-read','ramoops-warm-control'):
            from run_enuma_entry_probe import require_hardware_review
            require_hardware_review(json.loads(image.with_suffix('.json').read_text()),
                json.loads((ROOT/'config/hardware-review-approvals.json').read_text(encoding='utf-8')))
        if q.get('reason_target'):
            review=json.loads((ROOT/'reports/enuma-video-reason-code.json').read_text())
            matching=[x for x in review.get('queries',[]) if x.get('image_sha256')==q['image_sha256'] and x.get('query')==q['reason_query'] and x.get('reason_target')==q['reason_target'] and x.get('provider_sha256')==q['files']['SimpleFbDxe.efi']['sha256'] and x.get('core_sha256')==q['files']['DxeCore.efi']['sha256']]
            if review.get('review_required') is not False or review.get('firmware_commit')!=q['firmware_commit'] or len(matching)!=1:
                raise ValueError('actual first-reason provider code review missing or mismatched')
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
    writer = process = log = collector = collector_log = None
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
        command = [sys.executable, '-X', 'utf8', '-u', '-B', str(ROOT / 'scripts/run_enuma_entry_probe.py'),
                   '--image', str(image), '--label', label]
        if q.get('boot_clock_capture') is True:
            command += ['--boot-clock']
        if q.get('trial_kind') == 'ramoops-canary':
            previous = json.loads((ROOT/'out/device-tests/current.local.json').read_text())
            target = json.loads((Path(previous['directory'])/'target.local.json').read_text())
            command += ['--expected-serial', target['serial']]
            collector_log = (out/'collector.log').open('w', encoding='utf-8')
            collector = subprocess.Popen([sys.executable, '-X', 'utf8', '-u', '-B',
                str(ROOT/'scripts/collect_enuma_pstore.py'), '--adb', target['adb'],
                '--serial', target['serial'], '--nonce', q['nonce'], '--seconds', '120',
                '--output', str(out/'pstore')], cwd=ROOT, stdout=collector_log, stderr=subprocess.STDOUT)
            report['pstore_collection'] = (out/'pstore').relative_to(ROOT).as_posix()
        process = subprocess.Popen(command, cwd=ROOT,
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
                if time.monotonic() - finished >= 3 and (collector is None or collector.poll() is not None):
                    if process.returncode == 0:
                        break
                    # Keep filming the user's recovery after a timeout. An
                    # independent reconciliation updates only local state;
                    # this camera loop issues no extra device commands.
                    try:
                        recovered = json.loads((ROOT/'out/device-tests/current.local.json').read_text())
                    except (OSError,json.JSONDecodeError):
                        recovered = {}
                    if (recovered.get('phase')=='recovered-android-boot-complete' and
                        recovered.get('candidate_sha256')==q['image_sha256']):
                        break
                    if now >= 235:
                        break
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
        if collector is not None:
            report['collector_exit'] = collector.returncode
            collection_path = out/'pstore/collection.json'
            if collector.returncode != 0 or not collection_path.is_file():
                raise RuntimeError('pstore collection failed; no additional trial')
            report['pstore_marker_present'] = json.loads(collection_path.read_text())['marker_present']
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        if process is not None and process.poll() is None:
            process.terminate(); process.wait(timeout=15)
        if writer is not None: writer.release()
        if log is not None: log.close()
        if collector is not None and collector.poll() is None:
            collector.terminate(); collector.wait(timeout=10)
        if collector_log is not None: collector_log.close()
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
