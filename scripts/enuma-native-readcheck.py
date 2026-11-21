#!/usr/bin/env python3
"""Offline fixture-only model; no device I/O, runtime admission or hardware claims."""
import hashlib


def evaluate(profile, observations, expected, actual):
    """Return first failure or fixture comparison, never a runtime readiness decision."""
    def result(stage, reason):
        return {"scope": "host-fixture-only", "stage": stage, "result": reason}

    if profile.get("enabled") is not True:
        return result("profile", "blocked: disabled")
    for field in ("hc_resource", "sid", "context_bank", "mapping_contract", "lun"):
        if profile.get(field) is None:
            return result("profile", "blocked: unknown " + field)
    for field in ("old_backing_excluded", "producer_excluded", "mapping_compatible"):
        if observations.get(field) is not True:
            return result("preallocation", "blocked: " + field)
    for field in ("tr_empty", "tm_empty", "tr_stop_readback"):
        if observations.get(field) is not True:
            return result("queue", "blocked: " + field)
    if observations.get("command_ok") is not True:
        return result("command", "failed: first command")
    lun, size, capacity, lba = (profile.get(k) for k in ("lun", "block_size", "capacity_blocks", "lba"))
    if type(lun) is not int or not 0 <= lun <= 255 or observations.get("lun") != lun:
        return result("geometry", "failed: lun")
    if type(size) is not int or size <= 0 or observations.get("block_size") != size:
        return result("geometry", "failed: block_size")
    if type(capacity) is not int or capacity <= 0 or observations.get("capacity_blocks") != capacity:
        return result("geometry", "failed: capacity")
    if type(lba) is not int or not 0 <= lba < capacity or lba > 0xffffffff:
        return result("geometry", "failed: range")
    if not isinstance(expected, bytes) or not isinstance(actual, bytes) or len(expected) != size or len(actual) != size:
        return result("compare", "failed: block length")
    if actual != expected:
        return result("compare", "failed: mismatch")
    return {**result("compare", "fixture-match"), "lba": lba,
            "sha256": hashlib.sha256(actual).hexdigest()}
