# Session handoff — 2026-11-17

当前任务停在交接；新会话不要自动恢复实现或设备操作。以下状态由 2026-11-16/17 两轮工作提供，早期候选叙述不覆盖本交接。本文件只收录已有路径可查的事实；未带的推论不写。

## 定位

- 官方 **step 6（驱动适配）** / bring-up **阶段 6（存储与根卷）**；正式验收记录仍是 **阶段 1–2**（固件 → UniXNU 菜单），后续单次观察不提升阶段。
- 目标不变：真实 UFS `userdata` 上的持久根 + 载荷在设备内 + 界面可交互 + 断电重启仍可交互。持久根必须在真实 UFS；ramdisk / RamBlock / 内存根只作诊断或临时绕行。

## 已完成（逐条带证据）

1. **warm capacity r2 单次实机观察**（`docs/ufs-warm-capacity-r2-diagnostic.md`，commit `2844c39`）：NOP + LUN0 READ CAPACITY(10) 成功，几何 `4096 × 61880320`，判据全中。claim `.cache/ufs-warm-capacity-r2-enumacp2-device-attempt.claimed` 已消耗，**禁止访问/删除/重放**。
2. **GOP r5 封存 + 正名**（commits `e35e3e8`、`89be960`，证据 `out/enuma-gop-production-20261114-r5/HANDOFF.md`、`out/enuma-gop-r5-preseal-manifest-20261116/`）：`seal.py` + manifest 重建 + `audit.py --verify` 均 exit 0，429 项，五件产物哈希未变（`boot.img` `fd97c135…`）。正名：被拒的是 **SM8250 上刻意拒绝的 native UFS takeover**（`out/owner-data-query-20261113-r3/source-ufs/UfsPlatformResources.h:110` 仅 `Soc::Sm8550` 给 policy，`NativeUfs.cpp:2259` 据此 `return false`），与显示侧无关。
3. **GOP r5 首次上机 + 立即冻结**（`docs/enuma-gop-r5-device-observation.md`，commit `4ae3d43`）：四条显示失败判据全未命中；`enuma_legacy_stage==4` 为**静态推断**；无 render server ⇒ 无 swap ⇒ 无像素输出。deep reviewer 决定冻结：显示代码不进 tracked 默认 recipe/series，不本线再上机。
4. **SM8250 warm policy 只读 probe 候选**（`out/ufs-sm8250-policy-20261116-r1/`，`self-checked`，未上机）：新增 `Policy::Sm8250Warm`（仅 `xiaomi,enuma` 精确匹配放行）；`hostBringUp` 走 `0xe0`/`0x4e0` 双流只读校验 → 停队列 → 自有连续 DMA → QUERY/SSU/TUR → `gHost.ready`；`NativeUfs.cpp` 默认排除 SM8550 `0x60` 流与全部 SMMU 写指令。产物：`libShengUfs.a` `0bd6f531…`、`native.macho` `fd5d3b67…`、`prelink.macho` `81cfca98…`、`payload.img` `517bda75…`、`boot.img` `6f3e0e92…`；boot-args `-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-probe=10`（无 `sheng-data-persist`、无 `native-ufs-root=1`、无 initrd）。**reviewer 级审查判「可进入只读上机」，但未做独立 deep 审查**（deep 通道额度不可用，用户授权降级）。
5. **离线审计文档**（均 `self-checked`、离线只读）：
   - `docs/ufs-reserved-memory-audit.md`：34 条 `reserved-memory`、24 张表、12 项静态不可判（U1–U12）；`UFSDxe.efi` 是厂商预编译二进制，请求列表/UCD/PRDT/数据缓冲均为运行时分配 ⇒ 该 deep 项**离线不可能闭合**（只有反汇编或设备侧 `GetMemoryMap` trace 两条路）。
   - `docs/data-store-2gib-analysis.md`：阈值 `0x80000000` 判的是逻辑磁盘字节数；>2 GiB 写路径在 `isBig && !direct` 被拒（`kIOReturnNotReady`）且**无易失回退**；分卷 store **不支持**（单窗口 + 单头 + 版本 1）；持久化只有直连 store（`sheng-data-persist=2` + 已发布 root）一条路。
   - `docs/persistent-boot-slot-plan.md`（含 2026-11-17 设备采集）、`docs/sm8250-ac-opp-thermal-diff.md`、`docs/nt36523-touch-survey.md`。
6. **设备只读采集**（`enuma/.cache/android-slot-probe-20261117/`，51 个文件 + `RECORD.md`，**不在本仓内**；零写入、未 reboot）：LUN4（`sde`）有完整 GPT（主备 CRC 相符，65 分区与 by-name 一一对应）；`boot_a→sde12` 201,326,592 B、`vendor_boot_a→sde25` 100,663,296 B；`boot_a` = `ANDROID!`，`vendor_boot_a` = **`VNDRBOOT` header v3**；`super` 内 **7 个逻辑分区、metadata 10.2，无 `boot`/`vendor_boot`**；AVB `orange` / `flash.locked=0`；`/data` 为 **FBE 加密 f2fs**（`/dev/block/dm-40`）。
7. **记录与 CI**：CI 自 `e35e3e8` 起因 18 条 evidence 指向未入库文件而红，已修（`8ecd7fb`/`ff8d2d4`：13 个文件入库 + owner area findings）；`verify-audit.json` 与上游 HEAD 不再钉死（`16084e3`），改以 `candidate-manifest.json` 429 项哈希为准。当前 CI 全绿（run `44039152215`）。
8. **D7**（`docs/decisions.md`）：用户确认 Android `/data` 数据可弃。**不是刷写授权**，只是 D2 的一项目前置。
9. **SM8250 warm UFS policy r2 只读 probe 单次上机**（`docs/ufs-sm8250-policy-r2-device-observation.md`，`self-checked`，阶段不提升）：确认机型后授权**一次** `fastboot boot`（`out/ufs-sm8250-policy-20261117-r2/boot.img`，203505664 B `c756ef82…20a595`，23:15:33，exit 0，无刷写/continue/重试；另一台 nuwa 只出现在 `fastboot devices` 清单、未发命令）；claim `.cache/ufs-sm8250-policy-r2-probe-device-attempt.claimed` 于 boot 前 4.5 秒（23:15:28.531 +08:00）以 `CreateNew` 原子创建并已消耗，禁止访问/删除/重放。**判据全中**：`NATIVE_UFS root check`、`dma=0xc8e10000 len=0x22000 contig=0x22000 owned=0xc007c000+0x20000000 usable=0xc8700000 check=PASS`、`old_utrl=0x99ff3000 old_utmrl=0x99ff4000 excl=4`、`userdata first=290000 last=3b037fa`、`block0 magic 2d3bcf96 0b0631bb ext4magic=4b26 ext4blocks=3772222880`、`manifest status=1 windows=0`、设计内 `panic(… caller 0xfffffff00bfc1484) … @NativeUfs.cpp:2597` + `MACH Reboot`；未命中 `bring-up failed:`/SError/无设计内 panic 的重启。`owned` 与 2026-11-09 阶段 4 实测 `DARWINBOOT pa 0xC007C000 / window 0x20000000` 三源一致；`first/last` 折算 59,193,339 块 = 242,455,916,544 B，与既有 Android 几何吻合；`ext4magic/ext4blocks` 是加密 f2fs 首块按 ext4 偏移解码的密文，无文件系统含义。**三个不能证明项**：① 持久根卷/Data/store 与 `SHNGROOT` 窗口语义（`manifestStatus=1` 表示根本没有 manifest 被检查）；② `startRoot` 路径（`probe=10` 从不调用 `startRoot`/`gStoreGeometry`/`IOFindBSDRoot`）；③ 跨 EBS 的长期 DMA ownership 与 `UfsDxe` 硬件退役完整性（2026-11-14 已接受的残余风险不变）。证据两源逐字一致（主控转录 + `vision` 独立核读 1:1 与 2× 裁图，主控先前 `ext4blocks` 与 caller 末两位转录错误已按 vision 更正），无录像、三张图未入库。

## 当前阻塞（含解除条件）

- **deep 审查已到位**：probe 候选最终 diff 已完成 deep 审查，结论 **PASS WITH CONDITIONS**；`reserved-memory`/`UfsDxe` backing 退役一项离线不可闭合，按 2026-11-14 用户既定决策作为已接受残余风险（见本文件「已完成」第 9 条的不能证明项 ③）。
- **probe 已上机通过**：判据全中，claim `.cache/ufs-sm8250-policy-r2-probe-device-attempt.claimed` 已消耗，不可复用；任何新的设备动作需当轮授权 + 全新 claim。
- **`startRoot` / `gStoreGeometry` 零实机证据** ⇒ 阻塞刷 `userdata`（D2 前置）；`gHost.ready` 已由 r2 probe 的 warm 成功终态坐实（见「已完成」第 9 条）。
- **载荷装不进槽**：`boot.img` 203,505,664 B > `boot_a` 201,326,592 B，超 2,179,072 B；ramdisk 槽为 192 MiB 圆形分配，而载荷内容仅约 124,596,682 B（`docs/persistent-boot-slot-plan.md:16,324` 注 1：该值取自采集轮汇报，仓库内无清单文件）⇒ 缩载荷可行，但需重打包并重封存。
- **触摸 NT36523 无实现**（`docs/nt36523-touch-survey.md` 仅调研）。
- **UFS 持续 ownership / vendor DMA 退役未证**（用户 2026-11-14 已接受残余风险，不作当前主机实现前置）；**SM8250-AC CPU 无 `opp-table`**（频率走 EPSS 硬件 LUT，取证对象不是 DT）。

## 下一步顺序（每步判据）

1. **缩载荷到 `boot_a` 容量内**（内容约 124,596,682 B），重打包并重封存：持久化必经槽位，且 probe 已把「GPT 与 `userdata` 首块可读」这块前提坐实，载荷尺寸成为下一步唯一前置。
2. **准备 `startRoot` 路径**：probe 只走到只读校验并设计内 panic，`startRoot`/`gStoreGeometry`/manifest 窗口从未执行；下一步是把已读到的几何接到挂根路径，仍按「先只读、失败即停」的口径准备，不引入写。
3. 只有 1–2 都有证据后，才谈刷 `userdata`（D2 + 当轮授权 + `verifier` 独立复跑最终构建/测试）。

## 纪律

- claim/marker 一旦消耗禁止访问/删除/重放；21r–24r、cp25r/cp26r、warmcap-r2 及 `ufs-sm8250-policy-r2-probe` 的 claim 均永久封存。
- 设备动作当轮授权；红线分区 `xbl*`/`abl*`/`tz*`/`hyp*`/`modem*`/`persist*`/RPMB 不碰。
- 默认 `NoAccessPolicy`/`NoContract` 不变；正式阶段不提升。
- 图像/录像不进库；serial/ECID/GUID 不入库。
- 通道：Gemini 与 `deepseek` 两侧额度均曾耗尽；`opencode-go` 可用，但切换需用户明确同意。
