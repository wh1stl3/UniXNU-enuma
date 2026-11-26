# Display events r4: one boot_b flash

- User authorized a one-time diagnostic D2 exception: one flash to enuma `boot_b`, without reboot. Permanent D2 rules are unchanged.
- Parent reports final diff PASS from reviewer `ses_de9cb7857ffetXZ1kGqAiYwo8j`; deep reviewer reviewed the design only, not the final diff.
- Image `out/bootprogress-display-events-20261126-r4/boot.img`: 169951232 bytes; SHA-256 `5849e9c67ebce4440544cee96d5d54a37b6c0f9c2705a6389a513e0807086183`. Size and hash checked before enumeration and again immediately before claim creation.
- Fastboot enumerated two devices; per-device product queries identified one `enuma` and one `nuwa`. The unique enuma was fixed for subsequent commands. Its gates were `current-slot=b`, `unlocked=yes`, `partition-size:boot_b=0xC000000` (201326592 bytes).
- Exclusive `.cache/bootprogress-display-events-r4-flash-20261126.claimed` created atomically with CreateNew immediately before flashing; consumed, do not access, delete or replay. No old claim accessed.
- One `fastboot -s SERIAL flash boot_b IMAGE`, 2026-11-26 13:25:33.051–13:25:37.687 +08:00: `Sending 'boot_b' (165968 KB) OKAY [ 4.142s ]`, `Writing 'boot_b' OKAY [ 0.366s ]`, total 4.595 s, exit 0. No retry, post-flash device command, reboot, readback, boot, continue, slot change or other partition write.
- Subsequently, the user separately authorized one normal reboot. At 2026-11-26 13:29:04 +08:00, `fastboot devices` exit 0 listed two devices; individual `fastboot -s SERIAL getvar product` calls exit 0 identified one enuma and one nuwa. On the unique enuma, `fastboot -s SERIAL getvar current-slot` exit 0 returned `b`.
- One `fastboot -s SERIAL reboot`, 2026-11-26 13:29:04.366–13:29:04.395 +08:00, returned `Rebooting OKAY [ 0.000s ]`, `Finished. Total time: 0.000s`, exit 0. No retry, subsequent device command, flash, slot change, boot, continue or claim access.
- Host-reported command success does not establish device-side readback.

## Two-frame observation

- Vision `ses_de998e1aeffeOhdlVAY1rj5wwd` read two local photographs at displayed 13683 ms (~13 s) and 176180 ms (~176 s); Astra assessment PASS, as reported by the parent. Photographs are not committed.
- Host SHA-256 recalculation: `media/r4_1.jpg` `5bb494094d0bb3038ec4457eb357294fd3ec2942847aee16ddabc3d025f8e83e`; `media/r4_2.jpg` `1158f293f0e54d7582f9e76543291876c2376f0500904dbc0146fa6e0a272b2c`. Both are 64 hexadecimal digits; comparison against vision's reported digests remains pending because that report was not provided.
- `registered` was 1 in each frame. Service-wide CLIENT enter/ok/err counters were `000` → `110`; VALIDATE `000` → `000`; PREPARE `00` → `00`. These independently sampled service counters do not attribute the client to backboardd, do not establish a final open, and do not show an affirmative rejection.
- launchd exec `1:1:1`; the later frame shows exit `2:2:2`, `rv=1`. The later frame shows one exec each for backboardd `22:22:b8` and SpringBoard `4:4:15`, with no exit observed for either in that frame.
- The historical shared-region query without a PID had `first=0` / `ret12`; it is not evidence of mapping failure. A deadline is not evidence of deadlock.
- Two frames do not establish continuity or stable userland. No stage promotion. `self-checked`; no independent verifier rerun.
