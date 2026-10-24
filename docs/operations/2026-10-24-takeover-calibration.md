# 接手后的校准与显示访问隔离

2026-10-24。用户要求按首轮建议及硬停要求推进，全部文档落地。

## 已完成与主判断

独立固件仓fast-forward到b63c9bd基线，递归子模块脏状态未动。恢复脚本只读核验身份/启动/root/槽位/解锁、设备及备份摘要；保存独立证据并更新current.local.json，失败试验原记录不改。

主判断（高置信）：旧取数证据和诊断编排不够可靠，是先要修复的工程问题。低置信硬件嫌疑按CPU映射/属性/cache、显示域状态、构建/代码布局与时序保留；没有依据宣布unclocked access或写指令已经定案。可推翻判据：有效编译宏/确切代码与0/3/0对照闭合可重建数值通道；同步异常ESR/FAR可把映射与外部访问故障区分；电源/时钟状态和读边界需自己的实测。

额外确认：dispatch-detail-options.patch未把ENUMA_DIAG_DELAY_FROM_DISPLAY和ENUMA_DIAG_DISPLAY_VALUE_INDEX传给C编译器；header默认display=0，未启用分支还有STAT typo。旧delay20时序不能作为寄存器读数。GOP_QUERY的detail16是CoreStartImage后精确marker门，不是PE入口前；旧上下文因果叙述失效。旧记录保留并以新决策supersede，不篡改当时观测。

像素函数先Sync，再Read，再二次Snapshot，再Write；需分别定位。SSPP_SRC0_ADDR是显示设备地址，范围过滤不证明CPU物理地址。GCD条目本身不等同页表。DisplayDxe依赖不满足也不能推出必须重写整个显示栈。

## 新通道与校准

--value-source constant/register/off，--value-code 0..15，--value-index 0..6，--value-shift 0..28(4步长)。固定step0/query1/detail16/delay2/GUID-only及completion fallback；旧delay20拒绝，旧step1..7恢复GOP元数据分步语义。

常量0/3不调用任何显示读或cache callback，3码=额外9秒；寄存器模式仅既有R-004映射内一次预读和一次目标读。码间距3秒，避免原一秒粒度与主机抖动重叠；无需更改reset、内存、映射或日志区。

0/3/0每笔均匹配相同源码/编译契约，以fastboot_return_seconds优先、否则adb_return_seconds取时；三笔须同一metric。两笔零码漂移<=0.75秒，已知码残差<=0.75秒后才能解码；未知码也要求<=0.75秒且0..15，模糊不舍入硬解。单笔固定时序并不能证明marker命中，已知码对照是必要证据。每个寄存器片段须记录index/shift，不能把一片nibble称完整地址。

run_value_probes默认离线检查不可变raw/FD/image/构建/审计/源码与C编译宏绑定，不重新打包；--execute最多一笔。issued先落盘，失败/中断/模糊冻结计划，原样失败镜像不重试。每笔后更新文档与结果、提交推送再执行下一笔。无完整资格即不启动；不通过降低验收条件推进。

## 后续里程碑

先校准常量；之后最小显示读，失败则停止追加并恢复，再离线隔离。校准不通过可转更宽可观察通道提案，但R-008仍pending，不启用保留区或warm reset。缓存/CPU读隔离和新像素实验另锁具体构建/摘要，单次像素授权不继承已consumed记录。

FAT publisher/完整ADT/donor预链接可独立离线准备；实际XNU入口、SM8250 UFS、APFS/信任/Data和用户态逐层验收。复用上游通用实现，仅适配板级差异。

## 公开来源（实施锁版本）

- UniXNU固定5fdbd5d，远端新HEAD bd127c仅差异待审：https://github.com/UniXNU/UniXNU
- LineageOS SM8250内核6b34d247：https://github.com/LineageOS/android_kernel_xiaomi_sm8250/tree/6b34d24765327d746074c8e53b5ad0d24a51acc7
- SSPP布局：https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/techpack/display/msm/sde/sde_hw_sspp.c
- DMA/IOMMU：https://github.com/LineageOS/android_kernel_xiaomi_sm8250/blob/6b34d24765327d746074c8e53b5ad0d24a51acc7/drivers/gpu/drm/msm/msm_gem.c
- 社区elish/enuma设备树0d41d4d2，仍有elish专用配置，不能当本机完整事实：https://github.com/xiaomi-enuma-dev/android_device_xiaomi_elish_enuma/tree/0d41d4d29ae7329a454c6bb4e4b8c66331177249
- MiCode原有enuma DTS/kernel锁43b11af4/52a2f18维持。专有firmware/XML按本机来源锁；Android ELF HAL不可直接用作Darwin驱动。仅公开实现缺失接口再逆向PE/ELF，不补空协议冒充实现。

## 接手第二轮（23:45之后）：在途代码、构建环境与显示规格

### 在途隔离方案的审查结论

三份在途改动对应 STATUS 提到的“隔离第 2 条”：驱动内自行复位，绕开返回后的 marker 门。实现为 `--value-reset in-driver`，在 `EnumaValueProbe` 之后 `ResetCold(); CpuDeadLoop();`，并给 `SimpleFbDxe.inf` 补 `ResetSystemLib`。

先提交（e5f1ab5），随即在 WSL 构建中失败于 `Resources/Scripts/build_enuma_firmware.py:258`：

```
assert (uefi/relative).read_bytes()... == (SOURCE/relative).read_bytes()...   # INF 必须与源逐字节一致
assert 'ArmPsciResetSystemLibConstructor' not in autogen
assert not any(name in libraries.lower() for name in ('pscireset','resetsystemlib'))
```

三条断言都在 `if args.diagnostic_gop_query` 分支内，专门约束这个 provider 驱动。另核：`Platforms/Xiaomi/enumaPkg/enuma.dsc`、其 include 的 `KonaPkg.dsc.inc` 与 `enumaPkg/Include/UniXNU.dsc.inc` 中**没有 ResetSystemLib 绑定**，所以即便放开 INF 断言，还要改平台配置。

审查结论：守卫是刻意的，它把 ARM PSCI 复位库及其 FDT 依赖挡在“第一个被派发的驱动”之外——那正是历史上反复出问题的上下文。D-145 已因同一约束撤回过一次，D-149 要求独立审查，本次结论为维持。**关键补记**：in-driver 复位原本要区分的“驱动返回路径”，用不改守卫的手段（调 marker 门参数、换更早检查点）同样可及，因此不构成破守卫的正当理由。处置：d00c416 撤回，保留同批的 96d354a。

### 构建环境：Windows 原生不可用

首次在 Windows 原生 Python 下构建，连续两处失败：

1. `(info/'alternates').write_text(objects.as_posix()+'\n')` → Windows 把 `\n` 写成 `\r\n`，git 读到 `.../objects\r`，`update-ref` 报 `object directory ... does not exist`。修为 `write_bytes`（96d354a），WSL 下等价。
2. `link.symlink_to(..., target_is_directory=True)` → 创建符号链接需特权，普通权限 `OSError: [WinError 1920]`。**未修**。

历史上所有构建记录都在 WSL 内完成，所以这两处缺陷此前不会暴露。本轮起构建命令固定为 `wsl.exe -e bash -lc "cd /mnt/d/Code/UniXNU-enuma && python3 scripts/build_enuma_firmware.py ..."`，环境 Python 3.10.12 + tomli。

**构建不可复现**：撤回到 74598df 等价源码后，用与已资格 zero 完全相同的参数重建，FD 为 `02f8d31d…` 而非 `bfb3d6a6…`。含义是“资格”只能绑定到已归档的镜像文件，不能靠重建复得；本轮重建产物未用于任何实测。

### 显示初始化规格：不需要先 boot 一台 Linux

D-133 曾把“取 dmesg”表述为要 fastboot boot 一个 droidian/postmarketOS。实际上设备常态就是 Android（Linux），`su -c dmesg` 直接可取：

| 项 | 值 |
| --- | --- |
| 面板 | `xiaomi 42 02 0a video mode dual dsi cphy panel`，`mi,panel-id=0x4b383100420200` |
| 对应仓内资产 | `Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml`（完全对上，型号不必猜） |
| 时序 | `hactive=1600`、`vactive=2560`，60/120fps 动态 |
| 初始化命令量 | `dsi_panel_tx_cmd_set cmds(117)` / `cmds(115)` |
| 电源 | `mdss_core_gdsc: supplied by pm8150a_s4_level`；`dsi_phy … supply gdsc not found, using dummy regulator` |
| 时钟 | `disp_cc-kona af00000`、DSI PLL 0/1 为 7nm、`sde_rsc af20000` |
| 地址 | dsi_phy `ae94400`/`ae96400`、dsi_ctrl `ae94000`/`ae96000` |

未取到：`/sys/kernel/debug/pm_genpd`、`/sys/kernel/debug/dri/0`（本机 debugfs 未暴露该路径）。这些是自写 UEFI 显示序列的规格输入，不是设备执行授权。

### 下一步的规则冲突

挂死率基线是当前唯一能给出分母的实验，但它与“失败即停、不原样重试”直接冲突——统计在定义上要求一次失败后继续。故立 R-009 单独申请，不在既有授权内自行突破。若用户不接受，等价路径是直接转自写显示栈，并接受后续显示调试持续被偶发挂死污染。


## 23:04之后的实测/恢复对账（取代早期实施计划中的已过期状态）

实际构建/FD/打包资格已完成，两档固件74598df；zero1/known3分别16.991/25.503秒返回，zero2在22:52:12发出后75秒无自动返回。8.512秒差值仅初步支持延时响应；校准失败，计划冻结，不做寄存器解码。最新独立恢复证据out/device-tests/20261024T230449-recovery-reconciliation.json及reports/enuma-recovery-reconciliation.json确认Android完成/root/A槽/解锁及设备/备份双分区摘要一致。失败记录不改，实际人工动作和时间未知。

Review发现原STATUS/HANDOFF与人工待办未同步硬停、D-148/b54bb2b把初步支持和挂点推断说得过强；本轮D-149更正并对齐全部入口。不能称公共路径已安全或zero2定位到驱动返回；驱动内复位新增依赖有混杂因素。禁止原样重试失败候选，先完成新隔离设计及其来源资格。三份在途firmware改动保留且未资格，不纳入本次文档提交。本轮无新构建/设备启动。
