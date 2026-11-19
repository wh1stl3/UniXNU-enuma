# Session handoff — 2026-11-20

当前停在交接；新会话不要自动恢复实现或设备操作。本文件取代 `docs/SESSION-HANDOFF-20261119.md`（旧文件保留为历史快照）。一行状态：**OS 根卷 + 临时 scratch Data 走到 launchd 早期启动（`Early boot complete`，bootstrap/ondemand 两域起来，观察窗口内无 panic），阶段 6/7 仍未通过，下一步先接显示（r5 已构建但显示调用点未编译，接线是 r6）再开多核。**

## 定位

- 官方 **step 6** / bring-up **阶段 6**；正式验收记录仍是 **阶段 1–2**。OS 根挂载"有条件成立"、launchd 早期启动"成立"，都不等于阶段 6 通过。
- 目标不变：真实 UFS `userdata` 上的持久根 + 载荷在设备内 + 界面可交互 + 断电重启仍可交互。ramdisk / RamBlock / 内存根（含本轮 scratch Data）只作诊断或临时绕行。
- 细节只在各 observation 文档里，本文件只放指针、claim 与顺序。

## 本轮（11-19 → 11-20）新增

1. **Data seed 生成**：macOS 15 VM 上用官方 `make-data-seed.py --gib 3` 建 3 GiB，再 `diskutil apfs resizeContainer … 2147m` 缩到 2,146,996,224 B（524,169 块），`data.dbr` 1,142,976 B `c89592f8…0470`。**临时 seed**：initrd 交付 + ADT `ephemeral-storage = 1` + 无 store 窗口，重启不保留。见 [`data-seed-20261119-generation.md`](data-seed-20261119-generation.md)。
2. **r4 单次实机 boot**：`out/ufs-sm8250-launchd-data-20261119-r1/boot.img`（169,951,232 B `202597ce…1e6900`），22:09:26，exit 0，单次无重试/刷写。屏上首次出现 `Early boot complete`、`entering bootstrap mode`、user/501 与 system 两域服务逐个 `SOURCE_ATTACH, code = 0`、`exiting bootstrap mode`；无 panic 至少数分钟；11-18 的 `Library not loaded: /usr/lib/libSystem.B.dylib` 本轮未出现（**不归因**到 vmm-present / DATA_MOUNT / seed 中任何一项）。见 [`ufs-launchd-data-20261119-observation.md`](ufs-launchd-data-20261119-observation.md)。
3. **方向决定（用户 2026-11-19）**：**先接显示，再开多核**。官方没要求早期多核，只把"每核进入入口并收到 IPI"列为验收项。r5 显示候选（r4 + `libEnumaGopLegacy.a` + 9 个 `offline-legacy-*` + `sheng-vsync=60`，store mode 0 不变）已构建，**结论见下条 5**；仍未经任何 review。
4. **屏上时间戳推进比例已量测**（录像逐帧时间戳对照，非上机新增）：同一段录像 217.8 s（1080p@60、竖拍旋转），屏上最后一条完整日志行 t=60 s 为 `03:15:42.448257`、t=217 s 为 `03:15:43.094619`——**157.3 s 真实时间里屏上显示的时间戳只前进 0.646 s，屏上时间戳推进比例 ≈ 0.0041（约 1/243）**。这是**屏上显示时间戳**的推进比例，**不是「XNU 时钟慢 243 倍」**。分段在 `0.00005–0.026` 之间波动，**不恒定**。另有三条异常：① 出现一次**倒退** `42.448257` → `42.440807`（−7.45 ms）；② 一条 `03:16:43.368661 (Notice): Flushed 52 logs [limit: 20]` 的**显示时间比邻行超前约 60 s（`03:15:42.7x`），来源与时基未定**——现有证据不能证明用户态与内核日志异源；③ 无固定步长。另有一组观测 **31 µs 对应约 5 s ≈ 1/161,000**，与整体比例相差三个量级，说明**两次测的不是同一层，不能混用**。**时基结论已收窄**：ADT 的**输入值正确**（`cpu0` `state=running` 且带 `timebase-frequency=19200000`/`0x0124F800`，其余七个 cpu 为 `waiting`，`pe_identify_machine.c:57-82` 会读到它并覆盖 24 MHz 默认），但**运行时回调值、`rtclock_sec_divisor`、输出层换算均未验证**，因此**不能**据此排除时基/换算错误。**机制未定性，在查；不得据此写任何结论性归因。**
5. **r5 显示候选构建完成，但显示调用点未编译**：`out/ufs-sm8250-launchd-display-20261119-r1/` 已构建（`boot.img` 169,951,232 B `91b1e573…`），`libEnumaGopLegacy.a` 已 `-force_load`、六符号唯一归属、零 undefined，`nm` 与 `native-link.map` 可核；**但 r4 的 `bsd_init.o`/`IOUserClient.cpo` 是 `XNU_NATIVE_LEGACY_DISPLAY=0` 编的**——反汇编里 `_native_legacy_display_probe`/`_late_probe` 调用点 **0 处**，`__GLOBAL__sub_I_NativeLegacyDisplay.cpp` **未进** `__mod_init_func`。故 **r5 上机不会产生显示动作**，等价于 r4 + 死符号。接线须按 GOP r5 `build.py:97-108` 用 `XNU_NATIVE_LEGACY_DISPLAY=1` 重编那两个启动链单元（属下一步，**未做**）。
6. **r4 判读二轮离线升级（2026-11-20）**：`_load_init_program` 的两个 `_mount` 只有 panic 出口，故「出现 launchd ⇒ 两卷挂载返回 0」；三条 bootstrap ENOENT 经卷内核对定性为 donor 缺失的噪声；persona type 6 = `PERSONA_SYSTEM_PROXY`。细节只在 [`ufs-launchd-data-20261119-observation.md`](ufs-launchd-data-20261119-observation.md) 的「二进制级判读升级」一节，本节不复述；阶段不提升。

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

1. **显示（最先）**：**r6 = r4 + `XNU_NATIVE_LEGACY_DISPLAY=1` 重编 `bsd_init.o`/`IOUserClient.cpo` + 显示归档 + 9 参数**（其余对象沿用 r4 filelist，做法照 GOP r5 `build.py:97-108`；只这两个单元，未做）。r5 不要上机当显示验证——**无调用点，必不出画面**（见"本轮新增"第 5 条）。r6 构建完成后仍须**先审后上机**，再另申请**一次** boot 授权。判据：出现像素输出 / 控制台被释放 / 首个 `IOSurface` swap（`native_legacy_prepare_scanout` 全部在 `pendingSwapRequest()/isValidated()` 之后，见 `docs/enuma-gop-r5-device-observation.md`）。注意 2026-11-16 的 deep 决定是"GOP 冻结、等用户态"，与本轮顺序相反；以用户 2026-11-19 的当轮决定为准，旧冻结记录保留为历史。
2. **时钟（可选，不阻塞）**：只到「**屏上显示时间戳**推进 ≈ 1/243」，机制未定性，下一步是**一次临时探针 `timebase-probe=1`** 把层次切开：同一次启动输出两条快照（`MPIDR`、`CNTVCT`、`CNTFRQ_EL0`、`ml_get_timebase`、`cpu_base_timebase`、`rtclock_timebase_info` 的 numer/denom、`rtclock_sec_divisor`、calendar microtime、timer IRQ 计数），两条之间以 CNTVCT 增 96,000,000 tick（≈5 s）为准，配录像核对真实时长。判据：原始计数器增量正常而 calendar 只推进约 1/243 → 换算比例问题；计数器/换算正常而 IRQ 计数停滞 → timer/IRQ 路径；全部正常只有屏上时间慢 → 下游格式化/缓冲。**标为可选**：不阻塞显示，也不阻塞 SMP；跑过才能谈"机制"。比例数值与未验证项见"待定项"。
3. **Data 持久化仍阻塞**：r4 的 scratch Data 是临时的；持久化要 mode 2 的 owner-authenticated 几何绑定（store 窗口在 `userdata` 尾部），mode 1/2 未放行，需当轮授权 + D2 前置。
4. **SMP（验收项，不是前置）**：`sheng-smp=1` + `armcpu-spi-ipi=1`（`armcpu-self-ipi=1` 是组件参数，不是文档 boot-arg），先在 `dts/enuma.dts` 补 CPU 项与 `unixnu,cluster-type`（E/P，`devicetree.py:355-360` 只在该属性存在时写入）。当前载荷没有这些参数，ADT `/cpus` 是一 running + 七 waiting、无 cluster-type。

## 待定项（都不是阻塞，但没有结论）

- **瓶颈（2026-11-20）**：launchd 究竟是「在推进」还是「同一批服务反复 respawn」，缺的是一次**带时间戳的捕获**（视频或串口，长到能看出 pid/服务名是否重复、先前服务是否还在）；缺口在**捕获侧**，不在输出侧——内核/launchd 已经在逐服务打印，内核**不需要为此改动**。
- **时钟（已量测、机制待查）**：157.3 s 真实时间里**屏上显示的**时间戳只走 0.646 s，**屏上时间戳推进比例 ≈ 0.0041（约 1/243）**——这是显示层的比例，**不是「XNU 时钟慢 243 倍」**；分段 `0.00005–0.026` 波动、不恒定；一次 **−7.45 ms 倒退**（`42.448257` → `42.440807`）；一条 `Flush 52 logs` 行的显示时间比邻行**超前约 60 s**，**来源与时基未定**，现有证据不能证明用户态与内核日志异源；另一组观测 **31 µs 对应约 5 s ≈ 1/161,000** 与整体比例不一致，**两次测的不是同一层，不能混用**。**未排除**时基/换算：ADT 的**输入值正确**（`cpu0` `state=running` 且 `timebase-frequency=19200000`，`pe_identify_machine.c:57-82` 会读到它；其余七核 `waiting`），但**运行时回调值、`rtclock_sec_divisor`、输出层换算均未验证**，ADT 输入正确不足以排除时基/换算错误。**机制未定性**，在查，不得写成任何结论性归因；分层探针见"下一步顺序"第 2 条。
- **persona type 6**：`kpersona_find_by_type()` 失败（ESRCH）/`Unable to find persona with type 6` 在 user/501 与 system 两域都出现，服务仍 spawn 成功；既不证明阻塞，也不证明无害。**2026-11-20 补充（不是结论）**：type 6 = `PERSONA_SYSTEM_PROXY`（`bsd/sys/persona.h:45`，枚举 `:35-51`），ESRCH 只说明内核里没有该类型的 persona。
- **`ephemeral-storage = 1`**：除"跳过首次迁移"之外的实际语义未验证，后续若做持久化要注意它与 store 的相互作用。
- **三条 `Failed to bootstrap path`**（`NanoLaunchDaemons`、`com.apple.tombf.bits_daemon.plist`、`/usr/AppleInternal/LaunchDaemons`）：**2026-11-20 已定性为 donor 本就缺失的预期噪声**——在两卷（OS `04769D26-…`、SystemOS `8846FE78-…`）按目录记录键结构判据扫过，三条都不存在，卷内也没有任何 plist 引用它们；`tombf`/`tomb` 两种拼写都查，`/usr/AppleInternal` 两卷 0 次。判读与判据见 [`ufs-launchd-data-20261119-observation.md`](ufs-launchd-data-20261119-observation.md) 的「二进制级判读升级」第 5 条。仍然**不要**手工补这些路径。
- **`decmprs.c:1894/1922: cluster_copy_upl_data err 14`**：调用点与失败流未定位。
- **11-18 的两个未解项**（`system-volume-auth-blob` ENOENT、preboot ENOENT）**本轮仍未追**，无结论。2026-11-20 的卷内核对只覆盖上一条的三条 bootstrap 路径，不覆盖这两项；它们与 r4 的 owner 挂载链是否同源也未查。

## 指针

- 本轮 r4：[`ufs-launchd-data-20261119-observation.md`](ufs-launchd-data-20261119-observation.md)
- 显示 r5 候选（`out/`，ignored）：`out/ufs-sm8250-launchd-display-20261119-r1/CHECKPOINT.md`
- seed：[`data-seed-20261119-generation.md`](data-seed-20261119-generation.md)
- 上一轮 `vmm-present`：[`launchd-vmm-present-20261119-observation.md`](launchd-vmm-present-20261119-observation.md)
- 首次根挂载：[`ufs-root-mount-20261118-observation.md`](ufs-root-mount-20261118-observation.md)
- GOP 冻结记录：[`enuma-gop-r5-device-observation.md`](enuma-gop-r5-device-observation.md)

## 纪律（不变）

- 设备动作当轮授权；一次写入一次授权；已消耗轮次不重放。
- 红线分区 `xbl*`/`abl*`/`tz*`/`hyp*`/`modem*`/`persist*`/RPMB 不碰；图像/录像/截帧与 serial/ECID/GUID 不入库。
- 默认 `NoAccessPolicy`/`NoContract` 不变；正式阶段不提升；mode 1/2 未放行。
