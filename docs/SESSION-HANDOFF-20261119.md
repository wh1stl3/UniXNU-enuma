# Session handoff — 2026-11-19

**已被 [`SESSION-HANDOFF-20261120.md`](SESSION-HANDOFF-20261120.md) 取代（2026-11-20）；本文件保留为历史快照。**

当前任务停在交接；新会话不要自动恢复实现或设备操作。本文件取代 `docs/SESSION-HANDOFF-20261118.md`（该文件保留为历史快照）；只收录已有路径可查的事实，未带的推论不写。本文件记录的是 2026-11-18 晚间那一轮设备动作之后的现场。

## 定位

- 官方 **step 6（驱动适配）** / bring-up **阶段 6（存储与根卷）**；正式验收记录仍是 **阶段 1–2**（固件 → UniXNU 菜单），后续单次观察不提升阶段。
- 目标不变：真实 UFS `userdata` 上的持久根 + 载荷在设备内 + 界面可交互 + 断电重启仍可交互。持久根必须在真实 UFS；ramdisk / RamBlock / 内存根只作诊断或临时绕行。
- 相对上一份交接的进展：**OS 根卷第一次真正挂载**（`disk3s1 mount-complete`），启动第一次推进到 `Load_init_program`。

## 本轮新增（相对 2026-11-18 版）

1. **授权一次 `userdata` 写入 + 一次 mode 0 boot**（`docs/ufs-root-mount-20261118-observation.md`，`self-checked`，**无 `vision` 核读、无录像、无图像入库**）：
   - 写入：`fastboot flash userdata <sparse>`，22:42:50→22:46:41，12/12 段 `OKAY`、`Finished`、exit 0、230.396 s；sparse 8,811,031,268 B `ee3bb0eb…f7095ae`，展开 9,382,658,048 B、内容哈希 `fd43ee70…cbe03093`，与 `out/userdata-prepare-20261112-b/run-1/userdata/userdata-root.json` 一致；**只写 `userdata`，无主机回读**。写入范围只覆盖分区起点，尾部 233,073,258,496 B（mode 2 store 窗口所在）未写。
   - boot：22:46:54 一次 `fastboot boot` `out/ufs-sm8250-startroot-mode0-20261118-r2/boot.img`（169,951,232 B `7819c2ab…ff4ee66`，exit 0，boot-args `-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2`，store mode 0）。r2 相对 r1 只改 ADT `root_match_volume_uuid` 为 `04769D26-…`。
   - 末屏：warm bring-up ready（`dma=0xc8e0b000`，基址仍不固定）→ `published SystemOS` → `disk0 806400`（= 3,303,014,400 B）→ `system-volume-auth-blob` ENOENT（device tree）→ `SystemOS volume 8846FE78-… ready`（**非挂载**）→ `published OS` → `disk3 1483776` → `disk3s1 mount-complete` + `vol-uuid 04769D26-2CA0-4825-B443-E2E5F88300F2` → `Load_init_program` → `failed to lookup preboot: 2` / `ignition failed: 2` → `Library not loaded: /usr/lib/libSystem.B.dylib` → panic。
   - **判读**：OS 根挂载子判据**有条件成立**；**阶段 6 整体不通过**（launchd 未启动）；**SystemOS 未挂载**；`0x18` = `VM|PREBOOT` 是 reviewer 对标准常量的判读，私有函数语义未确认；`system-volume-auth-blob` ENOENT 是**设备树输入缺失**，与 `userdata` 布局无关。
   - `vol-uuid` 第 3 组 `4825` 由**用户放大屏上确认**；**未经独立图像核读**（`vision` 通道不可用），早前裁图读到的 `8443` 已退回。
2. **TWRP 路线在硬门禁停止**：`boot_enuma.img`（134,217,728 B `69a4dd43…ff0e0`，TWRP `3.7.1_12-15.0`）进入成功，identity / by-name / 242,455,916,544 B 尺寸 / 卸载清空门禁全过，但 `dm-7`（name=`userdata`、slaves=`sda34`）在 `umount` 后仍是 holder 且镜像无 `dmsetup`，按硬门禁停止：**未写入、未建 claim、未 `dd`、未回读、未 reboot**。证据 `.cache/ufs-userdata-twrp-write-20261118/STOPPED-gate1-dm-mapping.log`。
3. **两次 raw `fastboot flash` 客户端失败**：含 `-S 64M`，1.8 s、`std::bad_alloc`、无 `Sending` 行，**从未开始传输**，`userdata` 未受影响；随后改走 sparse 并成功。

## 当前阻塞（含解除条件）

- **SystemOS 未挂载**：只有 `published SystemOS` + `disk0 checkpoint search` + `volume … ready`，无 `disk0s1 … mount volume` / `mount-complete`，也无其 `handle_mount` 行。解除条件：出现 `disk0` 下卷的 mount 行，或明确记录该窗口本就不需要挂载。
- **preboot 不可解析**：`libignition!: failed to lookup preboot: 2` → `preadboot: failed to get preboot device: 2`，ENOENT；`0x18` 的具体消费函数语义未确认。解除条件：定位 preboot 卷/设备的来源与失败点。
- **`system-volume-auth-blob` 来源不明**：从 device tree 取不到（ENOENT），`import_iboot_forwarded_roothash` 随之失败；该 DT 输入由谁生成未追。解除条件：查出该节点应由哪个构建/组件提供并确认其内容格式。
- **launchd 起不来**：`Library not loaded: /usr/lib/libSystem.B.dylib` 后 PID 1 失败 panic；与 preboot ENOENT 的因果关系目前只是 reviewer 判读，未证。**明确不做**：手工补 `libSystem.B.dylib`（会掩盖 ignition/preboot 失败并污染归因）。
- **持久化未开始**：本轮仍是主机 `fastboot boot`，未写任何启动槽、未做冷启动；`userdata` 已写不等于持久根可用。
- **独立审查缺位**：候选（r2 打包）与本次观察均无独立 reviewer/verifier 复核；`vision` 通道不可用，屏幕只有主控转录 + 用户放大确认。reviewer 建议**升 deep 审查**。
- **其余历史阻塞不变**：mode 1 / mode 2 未放行；UFS 持续 ownership 与 vendor DMA 退役未证（2026-11-14 已接受残余风险）；备份 GPT 未验；Data/store 与写能力无证据。

## 下一步顺序（每步判据）

1. **让 SystemOS/cryptex 真正挂载**：本轮唯一最优先项。判据：`disk0` 下出现卷级 mount 与 `mount-complete`（或给出该窗口无需挂载的明确依据）。
2. **追 `system-volume-auth-blob` 来源**：与第 1 步同线。判据：指出提供该 device-tree 节点的构建步骤/组件，并说明其内容格式；在此之前不改根镜像布局。
3. **修 preboot 解析**：判据：`failed to lookup preboot` 不再出现，且能指出 preboot 设备/卷的实际落点。
4. **launchd 启动**：只有 1–3 有证据后才看 `libSystem` 是否自然可加载。判据：`Load_init_program` 之后 launchd 存活、不再出现 `Library not loaded` panic。这条通了，才算阶段 6 的启动半边有证据。
5. **持久化**：载荷进设备（`boot`/`vendor_boot` 槽或等价方案）+ 冷启动仍进系统。须 D2 前置 + 当轮授权 + `verifier` 独立复跑最终构建/测试；`fastboot boot` 不能替代。

## claim / marker 状态（全部）

| marker | 状态 |
| --- | --- |
| `.cache/ufs-userdata-sparse-flash-20261118.claimed` | 22:42:45 创建、**已消耗**；保留不删，禁止访问/删除/重放 |
| `.cache/ufs-userdata-root-write-20261118.claimed` | 更早的污染尝试，**未动**；禁止复用/删除/重放 |
| `.cache/ufs-userdata-root-write-20261118-retry1.claimed` | 更早的污染尝试，**未动**；禁止复用/删除/重放 |
| `.cache/ufs-userdata-root-write-20261118-retry2-sparse.claimed` | **从未创建** |
| `.cache/ufs-sm8250-startroot-mode0-probe-device-attempt.claimed` | 2026-11-18 r1 轮，已消耗；禁止重放 |
| `.cache/ufs-sm8250-policy-r2-probe-device-attempt.claimed`、`ufs-warm-capacity-r2-enumacp2-device-attempt.claimed`、`cp21r`–`cp27r`、`smmu-route-contexts-r2` | 历史轮次，均永久封存；禁止访问/删除/重放 |

TWRP 尝试按自身日志未创建任何 claim。

## 纪律

- 设备动作当轮授权；一次写入一次授权，不重放已消耗轮次。
- 红线分区 `xbl*`/`abl*`/`tz*`/`hyp*`/`modem*`/`persist*`/RPMB 不碰。
- 默认 `NoAccessPolicy`/`NoContract` 不变；正式阶段不提升；mode 1/2 未放行。
- 图像/录像/截帧不进库；serial/ECID/GUID 不入库。
- `userdata` 现已含本轮写入的自有布局（覆盖 Android `/data`，D7 已确认数据可弃，但那不是刷写授权）。
