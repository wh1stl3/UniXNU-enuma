# enuma UEFI 显示栈 — 交接提示词（2026-10-25 01:40）

> 给下一次会话的自包含提示词。原文可直接粘贴使用。

---

## 你在做什么

设备 **enuma**（小米平板 5，SM8250/kona，1600×2560 双 DSI CPHY LCD）上运行 UniXNU/XNU。工作区 `D:\Code\UniXNU-enuma`（设备仓）+ 子模块 `firmware`（UEFI 源码，remote `wh1stl3/uefi-enuma`）。**目标：让 UEFI 阶段点亮面板，使 XNU 的 `NativeMobileDisplay` 能拿到 `PE_Video`。**

## 必读（按顺序）

1. `D:\Code\UniXNU-enuma\AGENTS.md` — 项目硬约束，先读完再动手
2. `docs/STATUS.md` — 当前状态
3. `docs/DECISIONS.md` — 全史决策。**重点 D-131、D-142（结论已错，被 D-160 推翻）、D-155、D-156、D-159、D-160、D-161、D-162**
4. `docs/operations/2026-10-25-backlight-and-batch-transport.md` — 背光与批量传值规格
5. `docs/NEED-REVIEW.md` — 各 R 编号提案与状态

## 已确立的事实（不要重新发现）

- **原厂显示栈完整存在于本机 XBL**：`out/device/xbl_a.bin`（FV 在 `0x888b0`）共 **149 个模块**，含 `DisplayDxe`（315392 字节）、`CPRDxe`、`ClockDxe`、`I2C`、`SPMI`、`PmicDxe`、`DALTLMM`，以及 **40 个 Panel XML**（含本机 `Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml`）。枚举脚本：`scripts/investigate_xbl_display.py`
- **本仓 `QcomPkg` 的裁剪是某位移植者的选择，不是硬件事实。** 判断"能不能复用"必须查原始固件里有什么，不是查当前仓库里留了什么——D-142 正是在这里出错，把路线带偏到从零重写
- 守卫（`scripts/firmware_audit_policy.py`）本就允许 `--diagnostic-without-ufs` 只省略 `UFSDxe` 而**合法保留** `DisplayDxe`/`CPRDxe`
- DisplayDxe **自身负责背光**（PE 字符串实证）：`DisplayBackLightBrightnessLevelControl`、`EFI_DisplayPanelPowerControl`、`Charger power status is not okay or at off mode charging, so turn off backlight`、`EnableDisplayThread`
- **APRIORI 绕过 DEPEX（D-162，源码实证）**：`firmware/Mu_Basecore/MdeModulePkg/Core/Dxe/Dispatcher/Dispatcher.c` 1426–1438 中，APRIORI 列表内的驱动被直接置 `Dependent = FALSE; Scheduled = TRUE;` 并入 `mScheduledQueue`，调试输出 `RESULT = TRUE (Apriori)`。DisplayDxe 位于 **APRIORI 第 32 项（共 39 项）**，因此**它一定会被 dispatch，与 DEPEX 无关**
- **那两个 GUID（`a966cc4f-ee6c-424d-a762-8ed3b5a4a501`、`47861dff-556f-4269-9b28-062ec3ecb30d`）与现象无关**：它们不在 DisplayDxe 的 PE 内（代码不调用），其 DEPEX 又被 APRIORI 判 TRUE。两条独立证据同一结论。**不要再补 stub**
- **R-014 的挂死没有归因**：`--dispatch-guid` 用的 `dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92` 在 `scripts/audit_enuma_fd.py` 中即命名为 `simple_guid`，是 **SimpleFbDxe 的 GUID**；而 `--diagnostic-without-ufs` 构建 `ENUMA_DIAG_SIMPLEFB=0`，镜像里没有 SimpleFbDxe → 返回门指向不存在的驱动，`--dispatch-guid-only` 永不命中，75 秒无返回是必然。**不能据此说"DisplayDxe 挂死"或"稳定挂死"**
- **挂死率基线**：零读档 12.5%（8 笔 1 挂，合并 17 笔 3 挂 ≈ 17.6%），裸读 25%（4 笔 1 挂）。**任何单笔挂死都不构成归因证据**（D-155/D-156）
- DSI 扫描仍在跑（16.981 秒 PASS 门，D-158），所以"屏幕不亮"不是因为没有数据流
- **摄像头取证可用**：`scripts/screen_capture.py`（Osmo UVC，1280×720，支持 `--probe`/`--single`/`--burst`）。模型能直接读图片，显示实验**必须带连续拍照**

## 当前状态

R-014（保留原厂 `DisplayDxe`，`FD dbca3fcb` / 镜像 `922972e6`）执行两次，均 75 秒无自动回归，第二次带 60 帧拍照：frame-008 仍是 Android 桌面，frame-010（约 20 秒）起全黑镜面，至 frame-059 全程纯黑。**但这些观测不能定位到 DisplayDxe**（原因见上）。设备已恢复并核验。gitlink 已修正为 `aa9ec66`，两仓 HEAD 与远端一致。

## 下一步（采纳 review 方案，未上机）

**先证明执行到哪里，再决定查什么。** 以 DisplayDxe GUID `4138022f-06c7-4f79-9c94-7e33b511a4e7` 为目标，复用现有 Core 检查点制作两个候选：

- **detail15**：StartImage **前**（证明队列轮到它、即将调用）
- **detail13**：StartImage **返回后**（证明它执行完并返回了什么）

保持原厂 PE 不变；判据用连续拍照 + 返回时间。若 detail15 命中而 detail13 不命中 → 挂在 DisplayDxe 内部，再查更早驱动、PE 构造函数、真实协议调用或面板初始化。若 detail15 都不命中 → 问题在派发阶段，查 APRIORI/FV/更早驱动。

## 明确不要做的事

- **不要再补 stub protocol**（R-015 动机已被 D-162 推翻，且无必要）
- **不要自写 GENI I2C / KTZ8866 驱动**——原厂栈已内含背光控制，那是 D-142 错误结论的产物
- **不要把 R-014 的挂死归因于 DisplayDxe**——返回门指向的是 SimpleFbDxe，那个镜像里没有它
- 不要用单笔挂死做归因；先有基础率再谈对比
- 不要在没有连续拍照的情况下做显示实验
- 不要主动 `git commit`（仅在被明确要求时）；提交后注意同步 firmware 子模块指针
- 不要试图放宽 AGENTS.md 的硬约束，特别是：每次 boot 前自动备份 `boot_a`/`vendor_boot_a` 并逐字节核对、探针只读+摘要验证、`ENUMA_DIAG_SIMPLEFB=1` 必须同时省略 CPR/Display/UFS 三者
- 不要在未核验设备恢复状态时就追加镜像

## 设备与工具状态

- enuma 已恢复并核验（Android / root / `_a` / unlocked / 双分区摘要一致）
- 挂死时需**用户长按电源**，恢复后跑 `python scripts/reconcile_enuma_recovery.py` 做只读核验
- 两仓 HEAD 与远端一致（`require_published` 会强制检查，工作树脏则拒绝执行）
- 计划/执行工具：`scripts/prepare_value_transport_plan.py`、`scripts/run_hang_baseline.py`（逐笔执行+门禁）、`scripts/run_enuma_entry_probe.py`（底层 runner，`--label` 白名单写死 12 个值，只影响归档名不影响行为）
- `scripts/investigate_xbl_display.py` — 枚举 XBL 全部模块并解析 DisplayDxe 的 DEPEX

## 一句话现状

原厂显示栈找回来了、背光确认由它自己管、那两个"缺失 protocol"被证明无关；**当前真正未知的是"DisplayDxe 被 dispatch 之后执行到哪里"**，下一步是用 detail15/detail13 两个候选把这一点定位出来。
