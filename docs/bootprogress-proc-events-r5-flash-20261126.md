# Bootprogress proc events r5: one boot_b flash

- User authorized a one-time D2 exception: at most one `flash boot_b`, no reboot. Permanent D2 and retry rules are unchanged.
- Pre-write review supplied by parent: reviewer `ses_dea076801ffeNAB3ZDn6GUx3gA` final diff PASS; deep reviewer `ses_dea374797ffeU3COiycUn0HPu2` accepted lifecycle sites and recorder/lock protocol, as documented in `bootprogress-proc-events-20261126.md`.
- Previous attempt failed to start host Python, with no device command or claim according to the parent. This attempt used PowerShell without system configuration changes. Host-only fastboot version, parser fixtures, image size and SHA-256 checks succeeded before device enumeration.
- Device gate: one fastboot device, exactly one enuma identified by `getvar product`; `current-slot=b`, `unlocked=yes`, `partition-size:boot_b=0xC000000` (201326592 bytes). The target serial was fixed for subsequent commands.
- Immediately before writing, the specified `out/bootprogress-proc-events-20261126-r5/boot.img` was rechecked: 169951232 bytes, SHA-256 `50bb81c21b0b56e08aad6a1f8a99e3f57d04e3eeea40914efc19baf5f5680fa2`.
- `.cache/bootprogress-proc-events-r5-flash-20261126.claimed` was atomically created with CreateNew at 2026-11-26 12:09:01.558 +08:00; consumed, do not access, delete or replay. No old claim was accessed.
- One `fastboot -s SERIAL flash boot_b IMAGE`, 12:09:01.559–12:09:06.164 +08:00, exit 0: `Sending 'boot_b' (165968 KB) OKAY [ 4.104s ]`, `Writing 'boot_b' OKAY [ 0.382s ]`, fastboot total 4.571 s. During the flash operation there were no retries, reboot, readback, boot, continue or slot change; the later separately authorized reboot is recorded below.
- Host-reported flash success only; device-side contents and boot/runtime behavior not verified. No stage promotion. `self-checked`; no independent verifier rerun.

## Subsequent reboot

- User subsequently authorized one normal reboot, not another flash. Fastboot enumeration returned two devices (exit 0); explicit per-device product queries returned `enuma` and `nuwa` (both exit 0), uniquely identifying enuma. Its `current-slot: b` query exited 0.
- One `fastboot -s SERIAL reboot` at 2026-11-26 12:19:33.010–12:19:33.039 +08:00 exited 0: `Rebooting OKAY [ 0.000s ]`; `Finished. Total time: 0.000s`. No retry, flash, slot change, boot, continue, claim access or post-reboot system access.
- The host reported acceptance of the reboot command; the subsequent two-frame observation is recorded below. No stage promotion. `self-checked`.

## Two-frame screen observation

- User-supplied photographs independently transcribed by vision `ses_de9e7e75affexmwgrHxmuqMxjz`; photographs are not committed. `r5_1.jpg` SHA-256 `6da0c1184efa6aa8ce3b644d9399f98400293d70aaa501333f7146769c8a705d`; `r5_2.jpg` SHA-256 `553d7819d0bbb49f2f406fee2253c82afed1927eee1abae7365bdf05147c64f1`.
- Screen times are 8s and 149s (raw 7658 and 149960 ms); both show `Starting userspace`. The photographs are consistent with the same boot, but cannot independently establish that no reboot occurred between them.
- PROC values below are count followed by hexadecimal `pid:uniqueid:idversion`; “not observed” is limited to the respective frame.

| comm | exec, first → second | exit, first → second |
| --- | --- | --- |
| launchd | `1 1:1:1` → `1 1:1:1` | not observed → `1 2:2:2 rv=1` |
| backboardd | not observed → `1 22:22:b8` | not observed → not observed |
| SpringBoard | not observed → `1 5:5:d` | not observed → not observed |

- The launchd exec and exit identities differ: they cannot be paired, and the exit cannot be interpreted as PID 1 exiting or as a user exit code. `DISPLAY` and `SWAP` are unavailable in both frames.
- These frames support that the r5 page ran and that exec was installed for the three comm values. They do not establish completed userspace initialization, a GUI, a blockage, process survival, or persistence. Evidence is limited to the two frames; no stage promotion. `self-checked`.
