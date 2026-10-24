# PENDING-HUMAN

2026-10-24 17:31:23 起硬停：`exit14-minimal` 临时 boot 后 75 秒无 ADB/fastboot，屏幕全黑。

待办（仅差本人按键）：长按电源回 Android 或 fastboot。恢复后由主机独立核验 enuma 身份、`sys.boot_completed=1`、root、原槽、解锁、匹配备份、`boot_a`/`vendor_boot_a` 原摘要。

恢复核验通过后，下一步是**完全断电冷启动**（不是复位）再跑同一份镜像一次，用于判定 D-128 的启动序列假设。
