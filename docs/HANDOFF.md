# 当前进度：热状态重跑成功，超时转为偶发出口嫌疑

2026-10-24 Asia/Shanghai。用户要求做断电冷启动区分实验；热状态一半已执行并排除"恢复后残留状态"，断电一半不再必要。

## 本轮已做

2026-10-24 16:38:36 临时 boot `geometry20-control`（`20f079b4682e0365f2a3e7a1c1707829446c49d0738857458d89dc13d4ddaefd`，firmware 012715b），前置与两次失败同构（16:23:08 恢复 → 离线约 14 分钟 → 临时 boot，未断电）。成功：`adb_return_seconds` 16.962、`boot_complete_seconds` 31.221、`boot_reason=bootloader`、分区摘要未变。enuma `d0fd0840` 与 nuwa `fe5ed56e` 同时在线，按 `ro.product.device` 精确选中 enuma。

同一条 step20/query1 今天 4 笔：15:06:43 成功、16:02:03 成功、16:20:56 超时、16:38:36 成功。

## 判断

已排除：恢复后设备残留状态、step20 显示代码路径、新增等待。超时必为挂死——DxeCore 只在 StartImage 返回后按 status 选门，query 1/2 各自只认一种编码，两者都没出现说明没返回预期 status。

剩余两出口：①`EnumaStageCheckpoint` 的 `ResetCold()`（PSCI）既不返回也不复位，停在 `CpuDeadLoop()`，与两张全黑快照吻合（中高）；②SimpleFb 内 `0x0ae00000..0x0ae84207` MMIO 读触发未处理异常（中）。现有 1 bit 通道无法区分。

## 下一步

R-006 候选 A 已批准并落地配置：`config/exit-early-probes.json` 的 `exit10-early`（stage 10、`CoreDispatcher()` 之前、无显示 MMIO、无等待），设计与差异见 `operations/2026-10-24-exit-early-candidate.md`。最多 5 笔重复：5 笔全返回 → 锁 MMIO；任一笔挂死 → 锁复位出口。冻结镜像不重试；断电冷启动不再执行。

**候选已构建（2026-10-24 17:12）**：`ENUMA_DIAG_STAGE=10`，FD `95cd88f9…`，Boot v3 `a90836007b9900350ee52f5d3286b55b33f179c6227f88aa0351ac198cf5c517`，构建/FD 审计/Boot v3 回环通过，尚未实机。构建期修复三处环境问题：WSL 缺 tomli、固件仓三个子模块未初始化、staging 的 `Common/Mu` 仍指向 nuwa 参考树旧链接（已在 WSL 内删除，preflight 重建指向 `firmware/Common/Mu`）。三者都不改变固件内容，但重新出现时按同一路径处理。

## 边界

R-005 consumed；禁像素/MMIO/分区写、新映射/内存字段/verified 变更；51MiB heap、512MiB owned、example=true、Boot v3 保持。TWRP/UART 未验证；无可见日志，文本后端未接 INF/FDF；未进 XNU。当前无人工待办，Android 已完成且各摘要核验通过。

证据 `reports/enuma-restart-control.json`、`out/device-tests/20261024T163822-dxe-driver-return/`、`operations/2026-10-24-restart-control.md`。

## 系统与内核现状

目标 enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9 已真实链接源平台内核（21417672 字节，SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d），非 enuma 运行证据，未预链接 donor 或启动。donor 46415872 字节/237 模块与静态闭包计划通过，未 emit 预链接镜像。64MiB 配置 FAT 已生成但未接 publisher/打包启动；NativeUfs 为 SM8550 参数当前禁用；EnumaScreen 仅 host/AArch64 对象。

接手顺序 AGENTS/STATUS/DECISIONS/NEED-REVIEW。
