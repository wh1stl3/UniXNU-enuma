# 当前进度：冷启动未清除挂死，显示窗口访问不可靠

2026-10-24 Asia/Shanghai。**第二次硬停中**：完全断电冷启动后（关机 → 直接进 bootloader，不经 Android），同一份 `exit14-minimal`（step14，两次只读 `0x0ae6b800`/`0x0ae6c000`）仍然 75 秒无返回。相机快照 `out/camera-capture/20261024T174026/` 全黑。

## 待用户执行

长按电源恢复，然后主机核验：enuma 身份、`sys.boot_completed=1`、root、原槽、解锁、匹配备份、`boot_a`/`vendor_boot_a` 原摘要。

## 两次硬停

| 次 | 时间 | 坐标 | 结果 |
| --- | --- | --- | --- |
| 1 | 17:31:23 | 热（Android `adb reboot bootloader`） | 75 秒无返回 |
| 2 | 17:38:51 | **冷**（关机后直接进 bootloader） | 75 秒无返回 |

两笔都带 7 秒 completion fallback，PASS/FAIL 都会回 Android，故无返回只能是挂死。第 2 次 fastboot 身份已核验 `product=enuma`/`current-slot=a`/`unlocked=yes`。

## 读显示窗口的账本

| 时段 | 碰窗口笔数 | 挂死 |
| --- | --- | --- |
| 15:06–16:02 | 7 | 0 |
| 16:03–17:38 | 5 | 3 |
| 17:15–17:24（不碰窗口） | 0（5 笔 stage10） | 0 |

## 判断

主判断（高置信）：16:03 之后该设备对显示窗口的读取变得不可靠，完全断电冷启动不能恢复；读 2 个寄存器即挂。

推论：恢复可靠访问之前，任何"读到什么"的显示结论都不可信（含 23 个 step 的布局/几何/混合判断），继续加深探针没有意义。

D-128 的"启动序列"假设作为挂死原因已证伪（冷启动同样挂）。

## 恢复后按序

1. 断电静置 10 分钟以上再上电，同一镜像单笔。
2. 离线核实 XBL/ABL 在 fastboot boot 前是否初始化显示域，以及固件读 MDP 的既有假设是否成立。
3. 仍不能解释时，再评估"读窗口前显式确认域上电"（读 PMIC/GDSC 或写寄存器 → 需 NEED-REVIEW 批准）。

## 边界

R-005 consumed；禁像素/MMIO 写、新映射、内存字段、verified、分区写；51MiB heap、512MiB owned、example=true、Boot v3 保持。TWRP/UART 未验证；无可见日志；未进 XNU。冻结镜像不重试。

证据 `reports/enuma-exit14-device.json`、`out/device-tests/20261024T173123-*`、`out/device-tests/20261024T173851-fastboot-coldstart`、`out/camera-capture/20261024T174026`。

新增工具：`scripts/run_enuma_fastboot_probe.py`（从 fastboot 冷启动坐标起的一次性临时 boot，含身份核验与 75 秒观察；分区摘要需在断电前从 Android 侧核验，bootloader 里读不到）。

接手顺序 AGENTS/STATUS/DECISIONS/NEED-REVIEW。
