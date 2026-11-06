"""Hang-rate baseline: repeat one qualified zero-read candidate and count outcomes.

Approved as R-009. This is the one plan type that deliberately allows a hang
followed by another trial, because a hang rate needs a denominator. It keeps
every artifact check the value transport uses: the same validate_plan() runs, so
the image, raw, build, audit and package bindings and the compiled defines are
all verified before a single device command. It never decodes a value, never
reads a register and never writes anything.

One invocation issues at most one trial and then exits. After a hang the operator
restores the device; the next invocation refuses to start unless the recovery
ledger already shows a verified Android boot.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from reconcile_enuma_recovery import atomic_json
from run_value_probes import require_published, validate_plan

ROOT = Path(__file__).resolve().parents[1]


def check_baseline(plan):
    trials = plan['trials']
    if not trials:
        raise ValueError('empty baseline plan')
    # One profile, repeated. constant-0 measures the floor with no display
    # access; raw measures a single unprimed target read; off is a historical
    # boolean gate (for example the DSI frame-progress step) whose verdict is
    # carried by the PASS/FAIL return timing rather than by a value. Mixing them,
    # or mixing candidates, would wipe out the denominator.
    if len({t.get('role') for t in trials}) != 1 or trials[0].get('role') not in ('constant', 'raw', 'register', 'off'):
        raise ValueError('baseline plan must repeat one constant-0, one raw read, one primed register read, or one gated probe profile')
    if any(t.get('code', 0) != 0 for t in trials):
        raise ValueError('baseline plan must not encode a constant code')
    # A register arm repeats the same index/shift; the returned time is the data.
    if len({(t.get('index', 0), t.get('shift', 0)) for t in trials}) != 1:
        raise ValueError('baseline plan must repeat one register index and shift')
    if len({t['id'] for t in trials}) != len(trials):
        raise ValueError('duplicate trial IDs')
    # One candidate, repeated. A baseline that mixed images would have no
    # denominator.
    if len({tuple(sorted(t['sha256'].items())) for t in trials}) != 1:
        raise ValueError('baseline plan must repeat one identical candidate')
    if len(trials) > 16:
        raise ValueError('baseline plan exceeds the approved trial budget')


def read_state(root):
    path = root / 'out/device-tests/current.local.json'
    if not path.is_file():
        raise ValueError('no device state recorded yet')
    return json.loads(path.read_text())


def device_recovered(root):
    state = read_state(root)
    return (state.get('phase') == 'recovered-android-boot-complete'
            and state.get('partition_digests_unchanged') is True)


def run_next(root, plan, ledger_path, execute=False, invoke=None):
    # Resolve the runner at call time, not as a default argument. A default of
    # subprocess.run binds at import and cannot be stubbed, which let a unit test
    # drive two real fastboot boots once.
    if invoke is None:
        invoke = subprocess.run
    validate_plan(plan, root)
    check_baseline(plan)
    plan_sha = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {'plan_sha256': plan_sha, 'trials': []}
    if ledger['plan_sha256'] != plan_sha:
        raise ValueError('ledger belongs to another plan')
    rows = ledger['trials']
    if len(rows) >= len(plan['trials']):
        raise ValueError('baseline plan already complete')
    trial = plan['trials'][len(rows)]
    if not execute:
        return {'validated': trial['id'], 'device_action': False}
    require_published(root)
    # A hang is allowed to be followed by a trial, but only once the previous
    # one has been reconciled back to a verified Android boot.
    if not device_recovered(root):
        raise ValueError('device is not in a verified recovered state; reconcile before the next trial')
    row = {'id': trial['id'], 'role': 'constant', 'code': 0,
           'image_sha256': trial['sha256']['image'], 'outcome': 'issued'}
    rows.append(row)
    atomic_json(ledger_path, ledger)
    result = invoke([sys.executable, '-B', str(root / 'scripts/run_enuma_entry_probe.py'),
                     '--image', str(root / trial['image']), '--label', 'dxe-driver-return'],
                    cwd=root, capture_output=True, text=True, timeout=240)
    state = read_state(root)
    recovered = (result.returncode == 0
                 and state.get('candidate_sha256') == row['image_sha256']
                 and state.get('phase') == 'recovered-android-boot-complete'
                 and state.get('partition_digests_unchanged') is True)
    if recovered:
        metric = 'fastboot_return_seconds' if 'fastboot_return_seconds' in state else 'adb_return_seconds'
        row.update(outcome='returned', metric=metric, seconds=state[metric],
                   evidence=str(Path(state['directory']).relative_to(root)))
    elif state.get('phase') == 'manual-recovery-needed' and state.get('candidate_sha256') == row['image_sha256']:
        # The observation window expired with no return: this is the measurement.
        directory = state.get('directory')
        row.update(outcome='hung', runner_returncode=result.returncode,
                   evidence=str(Path(directory).relative_to(root)) if directory else None)
    else:
        row.update(outcome='unexpected', runner_returncode=result.returncode, phase=state.get('phase'))
        atomic_json(ledger_path, ledger)
        raise ValueError('trial ended in an unexpected state: stop the whole baseline')
    rows_total = len(rows)
    hung = sum(1 for r in rows if r['outcome'] == 'hung')
    ledger['summary'] = {'issued': rows_total, 'returned': rows_total - hung, 'hung': hung,
                         'hung_rate': round(hung / rows_total, 4)}
    atomic_json(ledger_path, ledger)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--ledger', type=Path, default=ROOT / 'reports/enuma-hang-baseline-device.json')
    args = parser.parse_args()
    print(json.dumps(run_next(ROOT, json.loads(args.plan.read_text()), args.ledger, args.execute), indent=2))


if __name__ == '__main__':
    main()
