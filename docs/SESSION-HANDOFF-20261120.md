# Session handoff — 2026-11-20

当前停在交接；新会话不要自动恢复实现或设备操作。本文件取代 `docs/SESSION-HANDOFF-20261119.md`（旧文件保留为历史快照）。一行状态：**OS 根卷 + 临时 scratch Data 走到 launchd 早期启动（`Early boot complete`，bootstrap/ondemand 两域起来，观察窗口内无 panic），阶段 6/7 仍未通过，下一步先接显示（r5 候选未经审查）再开多核。**

## 定位

- 官方 **step 6** / bring-up **阶段 6**；正式验收记录仍是 **阶段 1–2**。OS 根挂载"有条件成立"、launchd 早期启动"成立"，都不等于阶段 6 通过。
- 目标不变：真实 UFS `userdata` 上的持久根 + 载荷在设备内 + 界面可交互 + 断电重启仍可交互。ramdisk / RamBlock / 内存根（含本轮 scratch Data）只作诊断或临时绕行。
- 细节只在各 observation 文档里，本文件只放指针、claim 与顺序。

## 本轮（11-19 → 11-20）新增

1. **Data seed 生成**：macOS 15 VM 上用官方 `make-data-seed.py --gib 3` 建 3 GiB，再 `diskutil apfs resizeContainer … 2147m` 缩到 2,146,996,224 B（524,169 块），`data.dbr` 1,142,976 B `c89592f8…0470`。**临时 seed**：initrd 交付 + ADT `ephemeral-storage = 1` + 无 store 窗口，重启不保留。见 [`data-seed-20261119-generation.md`](data-seed-20261119-generation.md)。
2. **r4 单次实机 boot**：`out/ufs-sm8250-launchd-data-20261119-r1/boot.img`（169,951,232 B `202597ce…1e6900`），22:09:26，exit 0，单次无重试/刷写。屏上首次出现 `Early boot complete`、`entering bootstrap mode`、user/501 与 system 两域服务逐个 `SOURCE_ATTACH, code = 0`、`exiting bootstrap mode`；无 panic 至少数分钟；11-18 的 `Library not loaded: /usr/lib/libSystem.B.dylib` 本轮未出现（**不归因**到 vmm-present / DATA_MOUNT / seed 中任何一项）。见 [`ufs-launchd-data-20261119-observation.md`](ufs-launchd-data-20261119-observation.md)。
3. **方向决定（用户 2026-11-19）**：**先接显示，再开多核**。官方没要求早期多核，只把"每核进入入口并收到 IPI"列为验收项。r5 显示候选（r4 + `libEnumaGopLegacy.a` + 9 个 `offline-legacy-*` + `sheng-vsync=60`，store mode 0 不变）**正在构建，尚未经任何 review**。

## claim / marker 状态（全部）

除注明者外全部已消耗；**全部禁止访问、删除、重放**。`.cache/` 下实际文件名与创建时间（只读列目录所得）：

| marker | 轮次 / 创建时间 | 状态 |
| --- | --- | --- |
| `cp21r-device-attempt.claimed` … `cp27r-device-attempt.claimed` | 2026-11-10 → 11-13 | 已消耗 |
| `smmu-route-contexts-r2-device-attempt.claimed` | 2026-11-14 19:28:50 | 已消耗 |
| `ufs-warm-capacity-r2-enumacp2-device-attempt.claimed` | 2026-11-16 21:49:58 | 已消耗 |
| `ufs-sm8250-policy-r2-probe-device-attempt.claimed` | 2026-11-17 23:15:28 | 已消耗 |
| `ufs-sm8250-startroot-mode0-probe-device-attempt.claimed` | 2026-11-18 19:44:04（mode 0 r1） | 已消耗；r2 是紧随 sparse 写入的那次 boot，未另建 marker |
| `ufs-userdata-root-write-20261118.claimed`、`…-retry1.claimed` | 2026-11-18 21:55:38 / 22:01:21 | 污染的早期尝试，未动；禁止复用 |
| `ufs-userdata-sparse-flash-20261118.claimed` | 2026-11-18 22:42:45 | 已消耗 |
| `ufs-launchd-cache-mode0-20261119.claimed` | 2026-11-19 00:28:15 | 已消耗 |
| `ufs-launchd-cache-r2-20261119.claimed` | 2026-11-19 01:08:55 | 已消耗 |
| `ufs-launchd-cache-r3-20261119.claimed` | 2026-11-19 18:09:52 | 已消耗 |
| `ufs-launchd-data-r4-20261119.claimed` | 2026-11-19 22:09:23 | 已消耗 |
| `ufs-userdata-root-write-20261118-retry2-sparse.claimed` | — | **从未创建** |
| TWRP 写入尝试（2026-11-18） | — | 在设备映射硬门禁停止，自身日志显示未创建任何 claim、未写入、未 `dd` |
| GOP r5 boot（2026-11-16 23:35） | — | 目录列表中未见对应 marker 文件名；按既有记录是一次 boot、无刷写。不据此推断当时是否存在其它形式的标记 |

## 下一步顺序

1. **显示（最先）**：r5 候选完成构建后先走 review，再另申请**一次** boot 授权。判据：出现像素输出 / 控制台被释放 / 首个 `IOSurface` swap（`native_legacy_prepare_scanout` 全部在 `pendingSwapRequest()/isValidated()` 之后，见 `docs/enuma-gop-r5-device-observation.md`）。注意 2026-11-16 的 deep 决定是"GOP 冻结、等用户态"，与本轮顺序相反；以用户 2026-11-19 的当轮决定为准，旧冻结记录保留为历史。
2. **时钟偏慢**：先测屏幕时间戳与真实时间的比例；若比例显著，先查时基（ADT `/cpus` 的 `timebase-frequency`，`devicetree.py:354`），再判断是不是单核被占满。两者结论不同，不要混。
3. **Data 持久化仍阻塞**：r4 的 scratch Data 是临时的；持久化要 mode 2 的 owner-authenticated 几何绑定（store 窗口在 `userdata` 尾部），mode 1/2 未放行，需当轮授权 + D2 前置。
4. **SMP（验收项，不是前置）**：`sheng-smp=1` + `armcpu-spi-ipi=1`（`armcpu-self-ipi=1` 是组件参数，不是文档 boot-arg），先在 `dts/enuma.dts` 补 CPU 项与 `unixnu,cluster-type`（E/P，`devicetree.py:355-360` 只在该属性存在时写入）。当前载荷没有这些参数，ADT `/cpus` 是一 running + 七 waiting、无 cluster-type。

## 待定项（都不是阻塞，但没有结论）

- **persona type 6**：`kpersona_find_by_type()` 失败（ESRCH）/`Unable to find persona with type 6` 在 user/501 与 system 两域都出现，服务仍 spawn 成功；既不证明阻塞，也不证明无害。
- **`ephemeral-storage = 1`**：除"跳过首次迁移"之外的实际语义未验证，后续若做持久化要注意它与 store 的相互作用。
- **三条 `Failed to bootstrap path`**（`NanoLaunchDaemons`、`com.apple.tombf.bits_daemon.plist`、`/usr/AppleInternal/LaunchDaemons`）：可能是本机型本就缺失，也可能是卷内容缺失；**不要**手工补这些路径。
- **`decmprs.c:1894/1922: cluster_copy_upl_data err 14`**：调用点与失败流未定位。
- **11-18 的两个未解项**（`system-volume-auth-blob` ENOENT、preboot ENOENT）本轮没有追，仍无结论。

## 指针

- 本轮 r4：[`ufs-launchd-data-20261119-observation.md`](ufs-launchd-data-20261119-observation.md)
- seed：[`data-seed-20261119-generation.md`](data-seed-20261119-generation.md)
- 上一轮 `vmm-present`：[`launchd-vmm-present-20261119-observation.md`](launchd-vmm-present-20261119-observation.md)
- 首次根挂载：[`ufs-root-mount-20261118-observation.md`](ufs-root-mount-20261118-observation.md)
- GOP 冻结记录：[`enuma-gop-r5-device-observation.md`](enuma-gop-r5-device-observation.md)

## 纪律（不变）

- 设备动作当轮授权；一次写入一次授权；已消耗轮次不重放。
- 红线分区 `xbl*`/`abl*`/`tz*`/`hyp*`/`modem*`/`persist*`/RPMB 不碰；图像/录像/截帧与 serial/ECID/GUID 不入库。
- 默认 `NoAccessPolicy`/`NoContract` 不变；正式阶段不提升；mode 1/2 未放行。
