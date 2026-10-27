> 2026-10-28当前：v7单次已consumed，用户确认自行回Android且FASTBOOT到Mi标未见日志页，独立恢复与原分区/备份核验通过。尚无独立媒体判读，不证明Core/DXE/GOP成功，不重试；现行STATUS/HANDOFF。以下准备/未消费文字为历史。

> 2026-10-28 00:09 v7本次单次准备：用户明确“v7开始 正在拍摄”，按已说明的本次现场/在场恢复条件和既有恢复安排，仅新v7一次临时boot。即时只读前检enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。未claim/发送；准备文档发布及远端核对后由runner重复即时门禁。精确镜像c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d，trial 61c29945-1399-49eb-8133-d11d465bb6c4。75秒无合格返回先恢复，不自动重试，不flash/erase/改槽；R027冻结，共享主线只读。证据out/oem-far-chain-live-20261028；媒体Media-enuma/OEM-far-chain-v7-20261028-61c29945本地保留。以下旧就绪状态不复用，实际执行/恢复随后更新。

> **2026-10-28 当前：** [far-chain-v7镜像与资格](operations/2026-10-27-oem-far-chain-v7.md)已完成，未claim/上机。OEM期间只记RAM，真实返回后继续DXE，整轮分派完成才输出一张汇总，仍在BDS前恢复。旧v6已消费，旧拍摄就绪不复用；以下旧“当前/未上机”文字按历史阅读。现行STATUS/HANDOFF。

> **2026-10-27 最新：** v6已单次消费，原厂主入口ChipInfo查询前E01已人工确认，用户无操作自行回Android且独立核验通过；原始查询/方法/SID/Core返回仍未证实。无人工欠项，不重试v6，现行状态见STATUS/HANDOFF。以下构建/未上机表述保留为历史。

> 当前候选：[main-entry-v6](operations/2026-10-27-oem-main-entry-v6.md)，完整镜像/资格完成，未claim/上机。当前状态见STATUS/HANDOFF；旧v5已消费。

# 当前文档入口（2026-10-27）

- [新会话接续prompt](2026-10-27-oem-registration-v5-handoff-prompt.md)：工作区、候选、提交、完整字符串与下一步。
- [STATUS](STATUS.md)、[HANDOFF](HANDOFF.md)：唯一当前状态与操作边界。
- [registration-v5代码归因与资格](operations/2026-10-27-oem-registration-v5.md)。
- [官网开发指南](operations/official-development-guide.md)、[具体适配方法](operations/official-adaptation-rules.md)。

## 历史文档入口

下文为2026-10-24当时分析，已被后续实测和决策更新，不能作为当前根因或部署指令。

# README

2026-10-24 收束：**读显示窗口本身是不合法访问**。停在 fastboot 不加载镜像时屏幕显示 FASTBOOT 字样（显示域为开），而 `fastboot boot` 后读 `0x0ae6b800` 两次即挂总线；Qualcomm 官方 bus-hang 示例（unclocked MDP read 会挂并复位）、XBL 在 EnterFastbootExit 关闭显示且不恢复的 BSP 记录、SM8250 dispcc 属 MMCX 电源域需显式上电，三者与现场吻合。simplefb 变体恰好排除了唯一会上电的 OEM DisplayDxe，于是固件没有任何上电动作。

由此：**23 个 step 的 scanout 结论证据等级降为未知**，须在正确上电后重做；候选 D（保留 OEM 显示栈）已证伪——成功/失败/任意返回三门返回时间无差异，DisplayDxe 的 DEpex 为 8 个 protocol 全 AND 而 33 个 OEM 驱动中无 MDSS/MDP/DSI，驱动从未派发；UART 因无硬件支持关闭，改以 enuma 的 Linux dmesg 作为上电序列来源。

方法教训：`Sec.makefile` 不含任何 `ENUMA_DIAG_*` 宏，SEC 的 stage 4–8 检查点从未生效；任何新增读操作必须先在本轮 `.obj` 上用 objdump 确认常量确实出现，再打包实测。详见 STATUS、DECISIONS D-129~D-134、[读窗口根因报告](operations/2026-10-24-display-window-root-cause.md)。
