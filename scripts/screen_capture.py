"""Capture the physical screen with the host camera so trials are not judged by eye.

Usage:
  screen_capture.py --probe            # list cameras and their first frame
  screen_capture.py --single OUT.jpg   # one frame
  screen_capture.py --burst DIR --count N --interval S
"""
import argparse
import sys
import time
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]


def open_camera(index):
    # MSMF first: it handles the Osmo UVC device more reliably than DSHOW.
    cap = cv2.VideoCapture(index, cv2.CAP_MSMF)
    if not cap.isOpened():
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    return cap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', action='store_true', help='list cameras and grab one frame each')
    parser.add_argument('--single', type=Path, help='write one frame to this path')
    parser.add_argument('--burst', type=Path, help='directory for a burst sequence')
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--interval', type=float, default=2.0)
    parser.add_argument('--index', type=int, default=0)
    args = parser.parse_args()

    if args.probe:
        for index in range(4):
            cap = open_camera(index)
            if not cap.isOpened():
                continue
            ok, frame = cap.read()
            print(f'camera {index}: opened, first_frame={ok}, '
                  f'shape={tuple(frame.shape) if ok else None}')
            cap.release()
        return 0

    if args.single is None and args.burst is None:
        parser.error('choose --probe, --single or --burst')

    cap = open_camera(args.index)
    if not cap.isOpened():
        print('ERROR: no camera opened', file=sys.stderr)
        return 1
    # Let auto-exposure settle; the first frames of a UVC device are often black.
    for _ in range(8):
        cap.read()
        time.sleep(0.1)

    if args.single:
        args.single.parent.mkdir(parents=True, exist_ok=True)
        ok, frame = cap.read()
        if not ok:
            print('ERROR: frame grab failed', file=sys.stderr)
            return 1
        cv2.imwrite(str(args.single), frame)
        print(f'PASS: wrote {args.single} {frame.shape[1]}x{frame.shape[0]}')
        cap.release()
        return 0

    args.burst.mkdir(parents=True, exist_ok=True)
    written = 0
    for step in range(args.count):
        ok, frame = cap.read()
        if ok:
            path = args.burst / f'frame-{step:03d}.jpg'
            cv2.imwrite(str(path), frame)
            written += 1
        time.sleep(args.interval)
    cap.release()
    print(f'PASS: wrote {written}/{args.count} frames to {args.burst}')
    return 0 if written else 1


if __name__ == '__main__':
    sys.exit(main())
