# 当前进度：冷启动未清除挂死，显示窗口访问不可靠

2026-10-24 Asia/Shanghai。**第二次硬停中**：17:38:51 在**完全断电冷启动**（Android 关机 → 直接进 bootloader，中间不经 Android）后临时 boot `exit14-minimal`（step14，仅两次只读），75 秒无返回，第二次停止追加。相机快照 `out/camera-capture/20261024T174026/` 全黑，与 17:31、16:20、16:03 四次现场一致。等待用户长按恢复。

## 两次硬停记录

| 次 | 时间 | 坐标 | 镜像 | 结果 |
| --- | --- | --- | --- | --- |
| 1 | 17:31:23 | 热：Android `adb reboot bootloader` | `9609d235…` | 75 秒无返回 |
| 2 | 17:38:51 | **冷**：关机后直接进 bootloader | `9609d235…` | 75 秒无返回 |

第 2 次已由主机核验 fastboot 身份 `product=enuma`、`current-slot=a`、`unlocked=yes`，期间无分区写入；两份分区摘要在 17:36 刚从 Android 侧核验过，与备份一致。

两笔都带 7 秒 completion fallback，探针返回 PASS 或 FAIL 都会回到 Android，因此**无返回只能是挂死**。

## 假设被证伪

D-128 原假设：早期复位让 XBL/ABL 认为显示已初始化、下次启动跳过初始化，导致 UEFI 读落入未上电域。**完全断电冷启动同样挂死，该假设作为挂死原因被否定**（它在解释"为什么有时能读"上仍可能有残余价值，但已不能解释挂死本身）。

## 读显示窗口的账本（2026-10-24 全天，同一设备）

| 时段 | 碰显示窗口的笔数 | 挂死 |
| --- | --- | --- |
| 15:06–16:02 | 7（geometry×2、route×2、blend×3、reason22-control） | **0** |
| 16:03–17:38 | 5（step22、stage23-control、geometry20-control、step14×2） | **3** |
| 17:15–17:24（不碰窗口） | 0（`exit10-early` 5 笔） | 0 |

## 判断

**主判断（高置信）：16:03 之后，该设备上对显示窗口 `0x0ae00000..0x0ae84207` 的读取变得不可靠，且完全断电冷启动不能恢复。** 依据：读 2 个寄存器就挂；同一窗口 16:38 还能读 250 次成功、之后两笔 2 读即挂；冷启动无效；同期不读窗口的 5 笔全干净。推翻条件：按同一流程再来一笔干净返回。

**推论（重要）：在恢复可靠访问之前，任何"读到什么"的显示结论都不可信**，包括 23 个 step 里靠读取窗口得出的布局/几何/混合判断，以及 16:03 之后一成功三挂这段里唯一那次"成功"。继续增加探针深度没有意义。

**尚未排除的机制**：设备侧持久状态（挂死时总线 hang 后未被复位清除）、供电/温度相关的不稳定、或显示域在 UEFI 环境下本就需要显式上电而固件一直依赖 XBL 的隐式初始化。

## 下一步（恢复核验后按序）

1. **断电静置**：关机后拔出/保持断电 10 分钟以上再上电，同一镜像单笔。检验"持久状态能否被长时间断电清除"，成本最低。
2. **离线核实 XBL/ABL 是否真的初始化显示域**：固定小米 52a2f18 与 enuma 的 ABL 行为，确认 fastboot boot 前显示域应处于什么状态，以及固件读 MDP 前的既有假设是否成立。纯离线，不触设备。
3. 若 1、2 都不能解释，再评估"读窗口前显式确认域上电"（需要读 PMIC/GDSC 状态，或写寄存器初始化 → 属新映射/写操作，必须先走 NEED-REVIEW 批准）。

**不建议**再加任何读取型的显示探针，直到窗口访问恢复可靠。

## 边界

R-005 consumed，禁像素/MMIO 写、新映射、内存大小/基址、verified、分区写；51MiB heap、512MiB owned、example=true/Boot v3 保持。TWRP/UART 未验证，尚无可见日志/菜单，文本后端未集成，未进入 XNU。enuma 与 nuwa 同时在线，一律按 `ro.product.device` / fastboot `product` 选定 enuma。

证据 `reports/enuma-exit14-device.json`、`reports/enuma-exit-early-device.json`、`out/device-tests/20261024T173123-*`、`out/device-tests/20261024T173851-fastboot-coldstart`、`out/camera-capture/20261024T173305` 与 `20261024T174026`。

## 系统与内核现状

目标 enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9 已真实链接源平台内核，21417672 字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是 enuma 运行证据，未预链接 donor 或启动。donor 46415872 字节/237 模块和静态闭包计划通过，未 emit 预链接镜像。

64MiB 配置 FAT 已生成，仅发现 /reset 配置，尚未接 publisher/打包启动；完整 ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs 为 SM8550 参数，当前禁用；未创建系统卷或写 userdata。EnumaScreen 文本后端仅 host/AArch64 对象，未 INF/FDF/调用者集成。
