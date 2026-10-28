> 2026-10-28T11:34:07.288944+08:00 v10低时长对照已消费，用户确认未按键、自行回Android且没有新画面；独立身份/完成/root/A槽/解锁及双分区和本地备份核验通过。启动时钟区间有效。当前准备同族high27一次临时boot；target仍未claim，只有高对照独立恢复/人工确认和精确校准通过后才可启动。 本条为当前，其下旧准备文字按历史阅读。

> 2026-10-28 v10本次实机准备：用户明确“可以部署实机了”，并确认“正在拍摄，在场可恢复”。本轮独立记录现场条件，按low2→恢复/人工确认→high27→恢复/人工确认→精确校准→target顺序，各一次临时boot，不自动轮测。候选尚未claim；即时身份/原备份/恢复与当前文档发布门禁通过后先发low。75秒未回合格终点停止追加、优先恢复。不flash/erase/改槽，不改内存或verified；R027冻结、共享主线只读。证据out/oem-gop-mode-live-20261028；v10原有离线资格和镜像字节保持。

> 2026-10-28当前：gop-mode-v10目标及2/27秒对照已完成完整build1、qualification1和离线来源核验，三trial未消费。本机Clock/HAL ABI核对后未发现可确认的接口错配，保留原始方法，新增真实Core成功及整轮DXE后原厂GOP QueryMode/SetMode/读回检查。55项Python、sanitizer/ARM及224/174/182处链接删除负测通过。v9仅离线对照、不安排上机；旧源码准入已过期但镜像/资格字节冻结。没有本轮设备动作，不沿用旧拍摄/校准。 以下旧当前/准备文字按历史阅读。

> 2026-10-28当前：far-clock-v9目标及2/22秒校准镜像已完成完整build4、qualification1和离线来源校验，三trial均未claim/上机。移除诊断晚期GOP/像素出口，保留真实OEM/Core和整轮DXE路径；52项Python与最终机器码删除负测通过。实际时钟校准未完成，目标execute需新low/high报告与精确计划；v8已consumed且恢复通过，不复用旧拍摄就绪。现行STATUS/HANDOFF及operations/2026-10-28-oem-far-clock-v9.md；以下旧当前/准备文字按历史阅读。

> 2026-10-28当前：v8单次已consumed，用户确认自行回Android且未见日志页，00:51独立恢复与原分区/备份核验通过。本轮没有独立媒体判读，不证明Core/DXE/GOP成功。已复现竞态修复未解决本次报告的无页现象，下一重点为末端可观测性/拒绝与提前复位分离；不重试。现行STATUS/HANDOFF，以下准备/未消费文字为历史。

> 2026-10-28 00:47 v8本次单次准备：用户明确“v8上机，正在拍摄，我在场可以恢复”，当前拍摄/在场条件独立记录，不复用v7。即时只读enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，trial a35583f7-e92d-4999-96d2-116793825026，未claim/发送。当前准备提交发布与远端核对后，由原runner重复即时门禁，仅一次临时boot；75秒无合格返回停止追加、先恢复，不flash/erase/改槽。共享主线只读、R027冻结。证据out/oem-far-event-live-20261028；媒体Media-enuma/OEM-far-event-v8-20261028-a35583f7本地保留。v8仅修复已复现的通知竞态，不预写OEM/Core/DXE/GOP/BDS成功；无页仍有异常、返回门、末端显示拒绝等竞争解释。

> 2026-10-28当前：far-event-v8完整镜像和qualification1已完成，修复可复现的RestoreTPL后环尾串位主动复位；仅离线，未claim/上机。v7已consumed且自动回Android，无页不证明Core/DXE/GOP成功。现行STATUS/HANDOFF及operations/2026-10-28-oem-far-event-v8.md；以下旧当前/拍摄就绪均为历史。

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
