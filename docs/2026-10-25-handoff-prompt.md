# enuma UEFI 显示栈 — 交接提示词（2026-10-25 01:25）

> 给下一次会话的自包含提示词。原文可直接粘贴使用。

---

## 你在做什么

设备 **enuma**（小米平板 5，SM8250/kona，1600×2560 双 DSI CPHY LCD）上运行 UniXNU/XNU。工作区 `D:\Code\UniXNU-enuma`（设备仓）+ 子模块 `firmware`（UEFI 源码，remote `wh1stl3/uefi-enuma`）。**目标：让 UEFI 阶段点亮面板，使 XNU 的 `NativeMobileDisplay` 能拿到 `PE_Video`。**

## 必读（按顺序）

1. `D:\Code\UniXNU-enuma\AGENTS.md` — 项目硬约束，先读完再动手
2. `docs/STATUS.md` — 当前状态
3. `docs/DECISIONS.md` — 全史决策。**重点：D-131、D-142（结论已错，被 D-160 推翻）、D-155、D-156、D-159、D-160、D-161**
4. `docs/operations/2026-10-25-backlight-and-batch-transport.md` — 背光与批量传值规格

## 已确立的事实（不要重新发现）

- **原厂显示栈完整存在于本机 XBL**：`out/device/xbl_a.bin`（FV 在 `0x888b0`）共 **149 个模块**，含 `DisplayDxe`（315392 字节）、`CPRDxe`、`ClockDxe`、`I2C`、`SPMI`、`PmicDxe`、`DALTLMM`，以及 **40 个 Panel XML**（含本机 `Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml`）。枚举脚本：`scripts/investigate_xbl_display.py`
- **本仓 `QcomPkg` 的裁剪是某位移植者的选择，不是硬件事实。** 判断"能不能复用"必须查原始固件里有什么，不是查当前仓库里留了什么——D-142 正是在这里出错，把路线带偏到从零重写
- 守卫（`scripts/firmware_audit_policy.py`）本就允许 `--diagnostic-without-ufs` 只省略 `UFSDxe` 而**合法保留** `DisplayDxe`/`CPRDxe`
- DisplayDxe **自身负责背光**（PE 字符串实证）：`DisplayBackLightBrightnessLevelControl`、`EFI_DisplayPanelPowerControl`、`Charger power status is not okay or at off mode charging, so turn off backlight`、`EnableDisplayThread`
- DisplayDxe 的 DEPEX = 9 个 protocol 全 AND，其中 **2 个无任何提供者**：
  `a966cc4f-ee6c-424d-a762-8ed3b5a4a501`、`47861dff-556f-4269-9b28-062ec3ecb30d`
  公开资料搜不到，本仓所有 `.dec/.h/.dsc/.inc` 也没有
- **这 2 个 GUID 在整个 DisplayDxe PE 里一次都没出现**，只存在于 162 字节的 DEPEX 中 → 属编译期依赖声明，PE 代码不调用 → **提供 stub 即可满足 DEPEX**
- **挂死率基线**：零读档 12.5%（8 笔 1 挂，合并 17 笔 3 挂 ≈ 17.6%），裸读 25%（4 笔 1 挂）。**任何单笔挂死都不构成归因证据**（D-155/D-156）
- DSI 扫描仍在跑（16.981 秒 PASS 门，D-158），所以"屏幕不亮"不是因为没有数据流
- **摄像头取证可用**：`scripts/screen_capture.py`（Osmo UVC，1280×720，支持 `--single` / `--burst`）。模型能直接读图片，所以显示实验**必须带连续拍照**，不许再用肉眼当唯一证据

## 当前状态

R-014（保留原厂 `DisplayDxe`，`FD dbca3fcb` / 镜像 `922972e6`）已执行 **两次，均挂死且屏幕全黑镜面**：frame-008 还是 Android 桌面，frame-010（约 20 秒）已全黑，此后 100 秒无任何内容。原厂显示栈未产出画面。设备已恢复并核验。

## 下一步（已立 R-015，尚未批准）

写一个**最小 stub 驱动**发布那 2 个 GUID（空接口、**完全被动**、不报告任何具体状态），与 `--diagnostic-without-ufs` 组合使 DEPEX 满足，判据用连续拍照。

**风险必须说清**：DisplayDxe 被 dispatch 后可能走任何分支，包括再次挂死；且 PE 字符串里有 `Charger power status is not okay ... turn off backlight`，stub 若让它误判电源状态，可能**反而去关背光**，所以 stub 绝不能主动报告"异常"。

## 明确不要做的事

- **不要自写 GENI I2C / KTZ8866 驱动**——原厂栈已内含背光控制，那是 D-142 错误结论的产物
- 不要用单笔挂死做归因；先有基础率再谈对比
- 不要在没有连续拍照的情况下做显示实验
- 不要主动 `git commit`（仅在被明确要求时）
- 不要试图放宽 AGENTS.md 的硬约束，特别是：每次 boot 前自动备份 `boot_a`/`vendor_boot_a` 并逐字节核对、探针只读+摘要验证、`ENUMA_DIAG_SIMPLEFB=1` 必须同时省略 CPR/Display/UFS 三者
- 不要在未核验设备恢复状态时就追加镜像

## 设备与工具状态

- enuma 已恢复并核验（Android / root / `_a` / unlocked / 双分区摘要一致）
- 挂死时需**用户长按电源**，恢复后跑 `python scripts/reconcile_enuma_recovery.py` 做只读核验
- 两仓均已推送，HEAD 与远端一致（`require_published` 会强制检查，工作树脏则拒绝执行）
- 计划/执行工具：`scripts/prepare_value_transport_plan.py`（capture/baseline 计划）、`scripts/run_hang_baseline.py`（逐笔执行+门禁）、`scripts/run_enuma_entry_probe.py`（底层 runner，`--label` 白名单写死 12 个值）
- `--label` 白名单只影响归档目录名与 `result.json` 字段，不影响行为；新实验类型目前只能借用既有 label

## 一句话现状

原厂显示栈找回来了、依赖缺口定位到 2 个 protocol、确认它们只是 DEPEX 声明所以可用 stub 满足；**阻塞在"写 stub 并验证"这一步，尚未批准**。
