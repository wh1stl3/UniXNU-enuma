"""Bound a Linux boot-clock origin with host monotonic request intervals.

This removes Android userspace readiness from timing. It does not by itself
calibrate firmware delays or prove a unique UEFI execution path.
"""
import hashlib
import math
import re
import time

COMMAND='cat /proc/uptime /proc/sys/kernel/random/boot_id'

def bound(samples,issued_monotonic=None,previous_boot_id_sha256=None):
    if len(samples)!=3:raise ValueError('require exactly three boot-clock samples')
    ids=set();lo=-math.inf;hi=math.inf;last_uptime=-1;last_host=-math.inf
    for s in samples:
        start,end=float(s['start']),float(s['end'])
        lines=s['stdout'].strip().splitlines()
        if len(lines)!=2 or not re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',lines[1]):raise ValueError('invalid boot-clock response')
        values=lines[0].split()
        if len(values)!=2 or not all(re.fullmatch(r'\d+\.\d{2}',v) for v in values):raise ValueError('invalid uptime precision')
        uptime=float(values[0]);ids.add(hashlib.sha256(lines[1].encode()).hexdigest())
        if not all(math.isfinite(v) for v in [start,end,uptime]) or end<start or start<last_host or uptime<last_uptime:raise ValueError('invalid sample order')
        lo=max(lo,start-uptime-.01);hi=min(hi,end-uptime)
        last_host=end;last_uptime=uptime
    if len(ids)!=1 or lo>hi or hi-lo>.25:raise ValueError('boot-clock bounds inconsistent or too broad')
    boot_id=ids.pop()
    if previous_boot_id_sha256 and boot_id==previous_boot_id_sha256:raise ValueError('old boot observed')
    result=dict(method='host request interval minus quantized Linux uptime; 3-sample intersection',
                boot_id_sha256=boot_id,origin_monotonic_lower=lo,origin_monotonic_upper=hi,
                uncertainty_seconds=hi-lo,calibrated_firmware_delay=False)
    if issued_monotonic is not None:
        if not math.isfinite(issued_monotonic) or lo<issued_monotonic:raise ValueError('boot origin precedes issue')
        result.update(origin_after_issue_lower=lo-issued_monotonic,origin_after_issue_upper=hi-issued_monotonic)
    return result

def capture(shell,issued_monotonic=None,previous_boot_id_sha256=None):
    samples=[]
    for _ in range(3):
        start=time.monotonic();r=shell(COMMAND);end=time.monotonic()
        if r.returncode:raise ValueError('boot-clock read failed')
        samples.append(dict(start=start,end=end,stdout=r.stdout.decode('ascii')))
    return bound(samples,issued_monotonic,previous_boot_id_sha256),samples
