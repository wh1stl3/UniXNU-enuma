# Session handoff — 2026-11-18

当前任务停在交接；新会话不要自动恢复实现或设备操作。本文件取代 `docs/SESSION-HANDOFF-20261117.md`（该文件保留为历史快照）；只收录已有路径可查的事实，未带的推论不写。

> 取代声明（2026-11-19）：本文件已由 `docs/SESSION-HANDOFF-20261119.md` 取代（当晚随后完成了 `userdata` 写入与首次 UFS 根卷挂载）。正文保留为 2026-11-18 当日快照，不重写。

## 定位

- 官方 **step 6（驱动适配）** / bring-up **阶段 6（存储与根卷）**；正式验收记录仍是 **阶段 1–2**（固件 → UniXNU 菜单），后续单次观察不提升阶段。
- 目标不变：真实 UFS `userdata` 上的持久根 + 载荷在设备内 + 界面可交互 + 断电重启仍可交互。持久根必须在真实 UFS；ramdisk / RamBlock / 内存根只作诊断或临时绕行。

## 本轮新增（相对 2026-11-17）

1. **mode 0 `startRoot` 单次实机观察**（`docs/ufs-sm8250-startroot-mode0-observation.md`，`self-checked`，**候选与观察均未经独立审查/复核**）：19:44:09 对 `out/ufs-sm8250-startroot-mode0-20261118-r1/boot.img`（169,951,232 B `28746ac9…2654bf4`）执行**一次** `fastboot boot`，exit 0，无重试/刷写/continue；nuwa 未出现在任何清单。claim `.cache/ufs-sm8250-startroot-mode0-probe-device-attempt.claimed` 于 boot 前 5.3 秒原子创建并已消耗，**禁止访问/删除/重放**。boot-args `-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2`（store mode 0、无 `sheng-data-persist`、无 `native-ufs-probe`、无 initrd）；本系列**首次真正进入 `startRoot`**。
   - 末屏：`warm bring-up ready (dma=0xc8a10000 len=0x22000 contig=0x22000 owned=0xc007c000+0x20000000 usable=0xc8700000 check=PASS old_utrl=0x99ff3000 old_utmrl=0x99ff4000 excl=4 …)` / `no valid root manifest in userdata (first=0x290000 last=0x3b037fa status 1, magic 2d3bcf96 0b0631bb)` / `Still waiting for root device`。
   - **能证明**：warm 接管到 `gHost.ready`（`native-ufs-root=1` 生效下）；DMA 通过 owned/usable/DRAM/保留区/前任队列/排除区检查（`dma` 与 11-17 的 `0xc8e10000` 不同属分配基址不固定，`dma_end=0xc8a32000 ≤ owned_end=0xe007c000`）；**主** LUN 0 GPT 解析、`userdata` 首块读取、manifest 闸按序触发并以 `status 1` 拒绝。
   - **不能证明**：`SystemOS`/`OS` 发布、volume ready、根挂载、持久根、Data/store、写能力、备份 GPT 有效、跨 EBS DMA ownership 与 `UfsDxe` 退役完整性、重复启动一致性。
2. **载荷档位 160 MiB**（`docs/payload-shrink-plan.md` §7，`self-checked`，仅打包参数）：`board.toml [payload] size_mib` 192 → 160，新增 `[package] boot_partition_bytes = 201326592`；r3 实建 `boot.img` 169,951,232 B `d51a9ac8…ac7623`，余 31,375,360 B。**只对下次构建生效，不证明槽写入可行**；r3 未封存未部署。
3. **两条纠正**（本轮新结论，替代 2026-11-17 交接里的相应表述）：
   - **mode 2 的 store 窗口在 `userdata` 尾部，不能用于写首块 root manifest。** 「写 `SHNGROOT` 需要 mode 2」不成立；下一步**不是**开 mode 2。
   - **本次 `9071148B-B025-402D-AD7A-48464D8B5FFF` 的 rootwait 不能用来主张 UFS OS root 已匹配。** 工作树 `board.toml:97` / ADT `root-matching` 的 907 是 restore ramdisk 的 APFS UUID；已记录的 OS window UUID 是 `04769D26-2CA0-4825-B443-E2E5F88300F2`（`scripts/enuma-production-recipe.py:17`）。`startRoot` 拒绝在前，未发布任何卷，故 rootwait 只说明在等配置的 UUID。未来必须让 root-match UUID 与签名 OS UUID 对齐。
4. **无需升级 deep**（主控 reviewer 判读：warm 范围检查命中、`status 1` 为预期输入、rootwait 为预期终点）。

## 当前阻塞（含解除条件）

- **首根镜像缺失**：`userdata` 首块不是 `SHNGROOT`（`status 1`），因此 `startRoot` 在 manifest 闸即返回 false，窗口准备/发布路径从未执行。解除条件：产出一个带合法 root manifest 与匹配 owner policies 的**诊断**根镜像（不绕过 D2），并在运行中看到 `manifestStatus == 0` 与 distinct OS/SystemOS。
- **UUID 错配**：root-match（907，restore ramdisk）≠ 签名 OS UUID（`04769D26-…`）。解除条件：ADT/`board.toml` 的 root-match UUID 与签名 OS UUID 对齐后再上机。
- **mode 1 / mode 2 仍未放行**：mode 2 的 F1/F3 同步缺口未闭合；mode 1 本轮仅修复 big-seed 空指针（fail-closed），未申请放行。解除条件：各自独立 review 后单独申请。
- **独立审查缺位**：mode 0 候选（含 `ramblock-mode1.patch`、打包）与本次观察均未经独立 reviewer/verifier 复核（通道不可用）；证据仅主控单次转录，无 `vision` 核读、无录像、无图像入库。
- **槽写入未验证**：160 MiB 档位只把 `boot.img` 压到 `boot_a`（201,326,592 B）以内，`fastboot flash boot` 是否被 ABL 接受未知；`fastboot boot` 不写槽，不能替代。
- **UFS 持续 ownership / vendor DMA 退役未证**（2026-11-14 用户已接受残余风险，不作当前主机实现前置）。
- **`startRoot` 之外的其余前置**：`gStoreGeometry`/`IOFindBSDRoot` 仍无发布后的实机证据（本轮未走到）。

## 下一步顺序（每步判据）

1. **首个诊断根镜像 provisioning**：在不绕过 D2 的前提下，产出带合法 `SHNGROOT` manifest 与匹配 owner policies 的镜像，并做一次新的单次授权 boot。判据：`native-ufs-root=1` 下 manifest 闸不再以 `status 1` 拒绝，`ufsBuildRootPlan` 得到 distinct OS 与 SystemOS，窗口准备/发布路径被执行（仍不写槽、不写 `userdata`）。
2. **root-match UUID 与签名 OS UUID 对齐**：让 `Waiting on …` 的 UUID 与 `04769D26-2CA0-4825-B443-E2E5F88300F2`（或最终签名 OS 的 UUID）逐字符一致。判据：对齐后仍由第 1 步的镜像复跑；在此之前任何 rootwait 都不构成 OS root 匹配证据。
3. **Data store 的 owner-authenticated placement binding**：store 窗口位于 `userdata` 尾部、与首块 manifest 不冲突；`docs/data-store-2gib-analysis.md` 的 >2 GiB 与非直接路径限制仍适用。判据：placement 绑定由 owner policy 认证，而不是默认/无认证窗口。
4. 只有 1–3 都有证据后，才谈刷 `userdata`（D2 + 当轮授权 + `verifier` 独立复跑最终构建/测试）。

## 纪律

- claim/marker 一旦消耗禁止访问/删除/重放；21r–24r、cp25r/cp26r、warmcap-r2、`ufs-sm8250-policy-r2-probe` 及本轮 `ufs-sm8250-startroot-mode0-probe` 的 claim 均永久封存。
- 设备动作当轮授权；红线分区 `xbl*`/`abl*`/`tz*`/`hyp*`/`modem*`/`persist*`/RPMB 不碰。
- 默认 `NoAccessPolicy`/`NoContract` 不变；正式阶段不提升。
- 图像/录像不进库；serial/ECID/GUID 不入库。
- 通道：Gemini 与 `deepseek` 两侧额度均曾耗尽；`opencode-go` 可用，但切换需用户明确同意。本轮独立审查通道不可用，故候选与观察均只标 `self-checked`。
