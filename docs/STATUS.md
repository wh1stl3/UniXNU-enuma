# 当前进度：热状态重跑成功，超时转为偶发出口嫌疑

2026-10-24 Asia/Shanghai。用户要求做断电冷启动区分实验；实验的"热状态"一半已执行并**排除**了"人工恢复后残留状态"假设，原计划的断电一半因此不再必要。当前不追加显示探针。

## 本轮实测与结论

2026-10-24 16:38:36 临时 boot `geometry20-control`（`20f079b4682e0365f2a3e7a1c1707829446c49d0738857458d89dc13d4ddaefd`，firmware 012715b，15:06:43 曾成功），前置条件与两次失败同构：16:23:08 恢复核验通过 → 离线约 14 分钟 → 临时 boot，全程未断电。结果 `adb_return_seconds` 16.962、`boot_complete_seconds` 31.221、`boot_reason=bootloader`、分区摘要未变。

**成功，故超时不能归因恢复后残留状态。** 同一条 step20/query1 谓词今天 4 笔实机为：`20f079b4` 15:06:43 成功、`9ded5fa6` 16:02:03 成功、`459961e1` 16:20:56 超时、`20f079b4` 16:38:36 成功。三份不同源码、三次成功、一次超时，超时与镜像内容的相关性进一步下降。

## 已排除与剩余嫌疑

已排除：人工恢复后设备残留状态（本轮）；step20 显示代码路径（同谓词三次成功）；新增等待/长编码（step20 不含且同镜像两次成功）。

超时只能是挂死而非谓词拒绝：`EnumaDispatchDetailCheckpoint` 仅在 StartImage **返回**后按 status 选门，query 1/2 各自只命中"通过/拒绝"两种编码；两者都没出现，说明 SimpleFb 没返回预期 status。剩余两个出口：

1. **复位出口失效**（中高）——`EnumaStageCheckpoint` 走 `MicroSecondDelay` → `ResetCold()`（PSCI SYSTEM_RESET）→ `CpuDeadLoop()`；PSCI 既不返回也不复位时永久停住，与两张全黑相机快照吻合。
2. **SimpleFb 内显示 MMIO 读挂死**（中）——探针读 `0x0ae00000..0x0ae84207`，MDP 未上电/映射失效时可能触发未处理异常。

两者在现有 1 bit 通道下原理上不可区分。今天 10 笔里 2 笔超时，历史 S-001/250849f/S-002/S-003 同现象共六次以上，从未定位。

## R-006 候选 A 执行结果（2026-10-24 17:15–17:24）

`exit10-early`（stage 10、`CoreDispatcher()` 之前、无显示 MMIO、无等待）5 笔全部自动返回，0 次挂死：

| 笔 | 变体 | adb 返回 | Android 完成 |
| --- | --- | --- | --- |
| 1 | delay2 | 17.007 | 30.223 |
| 2 | delay7（正对照） | 21.277 | 35.603 |
| 3 | delay2 | 15.918 | 30.984 |
| 4 | delay2 | 16.988 | 33.343 |
| 5 | delay2 | 16.986 | 31.112 |

**正对照成立**：延时从 2 秒加到 7 秒后，adb 返回 +4.270 秒、Android 完成 +5.380 秒，说明 `EnumaStageCheckpoint(10)` 确实执行、`ResetCold()` 确实复位。这一条必须先立住，否则"5 笔都回到 Android"无法与"根本没复位、继续正常启动"区分。

delay2 四笔 adb 极差 1.089 秒，时序高度稳定。

**统计限制（必须如实记）**：若单笔挂死率按 15% 估计，5 笔全干净的先验概率为 0.85⁵ = 44%，因此本批**不能**排除早期出口也有偶发挂死，只能排除很高的单笔失败率。要以约 90% 信心排除 15%，需约 15 笔全干净（0.85¹⁵ = 8.7%）。

## 下一步：R-007 最小 MMIO 候选（已构建，待实测）

按"5 笔全返回"的方向，超时被推向派发之后的显示路径。主判断（中高置信）：两笔超时与历史上 S-001/250849f/S-002/S-003 都发生在 SimpleFbDxe 开始触碰 `0x0ae00000..0x0ae84207` 之后，MDP/DSI 域未上电时首次访问可能挂住总线，这与"黑屏 + 无 USB + 只能长按"吻合，且与探针读多少寄存器无关。

不用新写 step，直接用现成的 **step 14**（`EnumaDsiTimingEnabled`）：只有两次只读加载 `0x0ae6b800`、`0x0ae6c000`，不读 VERSION/CTL/LM、不等待、不写。它与失败笔 stage13/GUID/detail16/fallback 完全同构，唯一变量是探针深度。

已构建：FD `6469cd7471a0d1c7d5e732d6de419d9fe7d1eb0c06ea6340b1f0c8d4229e65d7`，Boot v3 `9609d2358b5b3d930c73fc4d82ad4913dd46e298e141cd7c4d751e99b730fa5b`。打包 PE 静态反汇编确认只有这两次目标读、零目标写（`reports/enuma-fd-audit.json` 的 `dsi_timing_code`）。

三种结果可用时间分开：PASS 立即复位（adb 约 16–18 秒）；FAIL 走 7 秒 completion fallback（adb 明显更晚）；挂死则 75 秒无返回（fallback 明确不能救挂死）。计划 5 笔：任一笔挂死 → "接触 MMIO 即挂"坐实；全数返回 → 失败属于更深偏移或更长读序列，而非首次接触。

**顺带修复工具 bug**：`scripts/audit_enuma_fd.py` 的 step14 分支用 `args` 做局部变量，污染 argparse 的 `args`，导致写报告时 `AttributeError`。已改名为 `operands`，审计语义不变。

断电冷启动那一半不再执行：热状态已证明设备干净。已冻结镜像（step22 正向、stage23-control 及未执行的正互补）不重试。

## 边界

R-005 consumed，禁像素/MMIO/分区写、新映射/内存大小/基址/verified 变更；51MiB heap、512MiB owned、example=true/Boot v3 保持。TWRP/UART 未验证，尚无可见日志/菜单，文本后端未集成，未进入 XNU。enuma 与 nuwa 同时在线，一律按 `ro.product.device` 选定 enuma。

证据 `reports/enuma-restart-control.json`、`out/device-tests/20261024T163822-dxe-driver-return/`、`operations/2026-10-24-restart-control.md`、`enuma-step20-control-comparison.json`。

## 系统与内核现状

目标 enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9 已真实链接源平台内核，21417672 字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是 enuma 运行证据，未预链接 donor 或启动。donor 46415872 字节/237 模块和静态闭包计划通过，未 emit 预链接镜像。

64MiB 配置 FAT 已生成，仅发现 /reset 配置，尚未接 publisher/打包启动；完整 ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs 为 SM8550 参数，当前禁用；未创建系统卷或写 userdata。EnumaScreen 文本后端仅 host/AArch64 对象，未 INF/FDF/调用者集成。

详见 operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。
