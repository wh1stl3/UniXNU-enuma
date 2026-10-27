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
