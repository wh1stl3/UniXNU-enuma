# 当前进度：step14 两次读即挂死，硬停待人工恢复

2026-10-24 Asia/Shanghai。**当前为硬停状态**：设备 17:31:23 临时 boot `exit14-minimal` 后 75 秒无 ADB/fastboot 返回，17:32:38 判定超时，已停止追加任何镜像，等待用户长按电源恢复。相机快照 `out/camera-capture/20261024T173305/camera-snapshot.jpg` 为全黑+反光，与 16:03、16:20 两次超时现场一致。

## 硬停记录

- 触发时间与原因：2026-10-24 17:32:38，AGENTS"执行中无法返回即停止追加镜像/写入、优先恢复"。
- 最后候选及摘要：`exit14-minimal`（step14，仅两次只读 `0x0ae6b800`/`0x0ae6c000`，无等待、无写），镜像 `9609d2358b5b3d930c73fc4d82ad4913dd46e298e141cd7c4d751e99b730fa5b`，FD `6469cd7471a0d1c7d5e732d6de419d9fe7d1eb0c06ea6340b1f0c8d4229e65d7`。
- 实际设备状态：未知（黑屏、无 ADB、无 fastboot 枚举），未确认 Android。
- 未执行项：该候选的第 2–5 笔、任何新镜像。
- 待执行恢复动作：用户长按电源回 Android/fastboot，然后独立核验 enuma 身份、`sys.boot_completed=1`、root、原槽、解锁、匹配备份及 `boot_a`/`vendor_boot_a` 原摘要。
- 继续条件：恢复核验通过后，先做**断电冷启动**（完全断电再上电，不是复位），再跑同一份 step14 镜像一次。

## 本轮关键结果（同一台设备、同一小时）

| 候选 | 探针深度 | 笔数 | 挂死 |
| --- | --- | --- | --- |
| `exit10-early`（stage10，派发前复位） | **0 次 MMIO 读** | 5 | **0** |
| `exit14-minimal`（step14） | **2 次 MMIO 读** | 1 | **1** |
| step20 完整只读（今日） | 250 次读 | 4 | 1（最后一次成功 16:38:36） |

`exit10-early` 五笔 adb 15.918–17.007（极差 1.089 秒），delay7 正对照 21.277 证明 checkpoint 确实执行并复位。`exit14-minimal` 第一笔即挂。

## 判断

**主判断（高置信）：挂死点在第一次触碰显示窗口（`0x0ae00000..0x0ae84207`），与探针读多少寄存器无关。** 依据是"0 读 5 笔全干净、2 读第 1 笔即挂"这一组对照；`exit14-minimal` 带 7 秒 completion fallback，探针返回 PASS 或 FAIL 都会回到 Android，只有真正挂住才可能 75 秒无返回。

**状态假设（中高）：显示窗口的可访问性随启动序列变化，而不随镜像变化。** 16:38 同一窗口读 250 次成功，之后五笔 stage10 在显示驱动执行前就复位，17:31 同一窗口读 2 次即挂。可解释的机制是：早期复位让 XBL/ABL 认为显示已完成初始化，下一次启动跳过该初始化，UEFI 的读落在未上电/无时钟的域上，挂住总线。这也解释了历史 S-001/250849f/S-002/S-003 反复出现却查不到代码原因。

**已排除**：探针代码内容（0 读 5 笔干净）、读深度（2 读即挂）、人工恢复后残留（本轮 stage10 五笔干净）、长等待（本候选无等待）。

## 下一步

1. 用户恢复并核验通过。
2. **完全断电冷启动**后跑同一份 `exit14-minimal` 一次：干净返回 → 启动序列假设成立，转查 XBL/ABL 显示初始化与 UEFI 早期复位的交互；同样点位挂死 → 假设回落，问题在镜像侧需重新分解。
3. 若假设成立，后续所有显示探针都必须先建立"冷启动前置"纪律，或在读 MDP 前显式确认域上电（需新映射/时钟读取，届时按 NEED-REVIEW 申请）。

冻结镜像（step22 正向、stage23-control 及未执行正互补）不重试。

## 边界

R-005 consumed，禁像素/MMIO/分区写、新映射/内存大小/基址/verified 变更；51MiB heap、512MiB owned、example=true/Boot v3 保持。TWRP/UART 未验证，尚无可见日志/菜单，文本后端未集成，未进入 XNU。enuma 与 nuwa 同时在线，一律按 `ro.product.device` 选定 enuma。

证据 `reports/enuma-exit-early-device.json`、`reports/enuma-exit14-device.json`、`out/device-tests/20261024T173123-dxe-driver-return/`、`out/camera-capture/20261024T173305/`。

## 系统与内核现状

目标 enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9 已真实链接源平台内核，21417672 字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是 enuma 运行证据，未预链接 donor 或启动。donor 46415872 字节/237 模块和静态闭包计划通过，未 emit 预链接镜像。

64MiB 配置 FAT 已生成，仅发现 /reset 配置，尚未接 publisher/打包启动；完整 ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs 为 SM8550 参数，当前禁用；未创建系统卷或写 userdata。EnumaScreen 文本后端仅 host/AArch64 对象，未 INF/FDF/调用者集成。

详见 operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。
