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

## 当前阻塞（含解除条件）

- **deep 审查不可用**：Gemini 侧预付额度耗尽、`deepseek` 侧余额不足。probe 候选的两个 deep 项未关——SMMU 旁路系统级边界、`reserved-memory`/`UfsDxe` backing 退役 ⇒ **阻塞上机**。解除：通道恢复后送 deep；其中 backing 一项离线不可闭合，需 deep 接受残余风险，或设备侧读固件 `GetMemoryMap`。
- **probe 未上机**：需当轮授权 + 全新 claim（r5 无 claim 机制；warmcap 的 claim 已消耗，不可复用）。
- **`startRoot` / `gHost.ready` / `gStoreGeometry` 零实机证据** ⇒ 阻塞刷 `userdata`（D2 前置）。
- **载荷装不进槽**：`boot.img` 203,505,664 B > `boot_a` 201,326,592 B，超 2,179,072 B；ramdisk 槽为 192 MiB 圆形分配，而载荷内容仅约 124,596,682 B（`docs/persistent-boot-slot-plan.md:16,324` 注 1：该值取自采集轮汇报，仓库内无清单文件）⇒ 缩载荷可行，但需重打包并重封存。
- **触摸 NT36523 无实现**（`docs/nt36523-touch-survey.md` 仅调研）。
- **UFS 持续 ownership / vendor DMA 退役未证**（用户 2026-11-14 已接受残余风险，不作当前主机实现前置）；**SM8250-AC CPU 无 `opp-table`**（频率走 EPSS 硬件 LUT，取证对象不是 DT）。

## 下一步顺序（每步判据）

1. **deep 审查 probe 候选最终 diff**（通道恢复后）：不通过不上机。
2. **授权一次只读 `native-ufs-probe=10` 的 `fastboot boot`**，走全新 claim。判据：`NATIVE_UFS root check`、`userdata first=290000 last=3b037fa`、`block0 magic …`、`manifest status=…`；命中 `bring-up failed:` / `root check:` / SError / 重启 即判失败，不重试。取证建议录像（要证明「没有某行」时截图不够）。
3. 若 probe 通过 ⇒ 进 `startRoot`（GPT 与 `userdata` 首块已读，转为挂根路径）。
4. 缩载荷到 `boot_a` 容量内（内容约 124,596,682 B），重打包并重封存。
5. 只有 2–4 都有证据后，才谈刷 `userdata`（D2 + 当轮授权 + `verifier` 独立复跑最终构建/测试）。

## 纪律

- claim/marker 一旦消耗禁止访问/删除/重放；21r–24r、cp25r/cp26r、warmcap-r2 的 claim 均永久封存。
- 设备动作当轮授权；红线分区 `xbl*`/`abl*`/`tz*`/`hyp*`/`modem*`/`persist*`/RPMB 不碰。
- 默认 `NoAccessPolicy`/`NoContract` 不变；正式阶段不提升。
- 图像/录像不进库；serial/ECID/GUID 不入库。
- 通道：Gemini 与 `deepseek` 两侧额度均曾耗尽；`opencode-go` 可用，但切换需用户明确同意。
