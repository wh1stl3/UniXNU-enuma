# enuma 与 sheng 功能差集（2026-11-22，部分静态调查）

**结论：有条件，不能仅凭补板级差别就断言效果等价。** 杀进程的发送者和原因尚未观察到。以下是部分差集，不是完整构建清单，也不是因果结论。`self-checked`；没有新设备操作或构建。

sheng 引用均为 `UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e` Git 对象；该检出工作树为空、索引记录大量删除，本调查只读 HEAD，不恢复工作树。enuma 引用为本设备仓；UniXNU 引用固定基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。用户提供 r17 的 SIGKILL 循环、共享区、CPU 与 keystore 数值作为本次对照输入；本调查未独立复核实机画面。已存 `docs/enuma-r17-exit-probe-host-20261122.md:3` 是实机观察前的主机候选记录，不能拿它否定后来的用户观察。

## 1. 内核补丁

sheng 的默认 27 profile 选择 `device:patches/xnu-12377/series`；其 17 override 选择 `device:patches/xnu/series`（sheng `board.toml:9,22,182`）。enuma 默认选择 arch、soc、本地 os-series 和 device series（`board.toml:20-24`），r17 另施加独立退出探针（`scripts/build-enuma-r17-exit-probe.py:145-147`）。arch series 本身包括 4K、owner mount、cryptex 和其他公共补丁（UniXNU `profiles/arch/arm64/patches/xnu/series:14-16,37-42,55`）。**series 列表不等于最终宏开启或二进制实际执行**；仅按文件名不等于功能缺失。

| sheng device series 项目 | 作用及用户态相关性 | 来源 |
|---|---|---|
| `zzyd-sheng-audio-addon-mount.patch` | 音频 addon 挂载；与用户态服务间接相关 | `patches/xnu/series:2`；`patches/xnu-12377/series:4` |
| `zzye-sheng-cpu-idle.patch` | CPU idle；间接相关 | `patches/xnu/series:3`；`patches/xnu-12377/series:2` |
| `zzyf-sheng-amp.patch` | CPU 集群调度；间接相关 | `patches/xnu/series:4`；`patches/xnu-12377/series:3` |
| `source-storage-runtime.patch` | source storage 启动路径；直接相关 | `patches/xnu-12377/series:5` |
| `zzzz-sheng-ipados27-bringup.patch` | 多子系统 27 bring-up，含启动与 dyld pager 变更；直接相关，但不能直接应用到 10063 | `patches/xnu-12377/series:6` |
| `vmwait-dyld-pager-source-release.patch` | dyld pager 等待/源释放，直接相关；具体语义未逐行核实 | `patches/xnu-12377/series:7` |
| `zzzzzz-sheng-latency-trace.patch`、`zzzzzzzz-sheng-exit-latency.patch`、`zzzzzzzzz-sheng-unnest-trace.patch` | 时延、退出、unnest 诊断，用户态间接相关 | `patches/xnu-12377/series:8-10` |
| `sheng-wifi-launchd-cache.patch`、`sheng-bluetooth-runtime.patch`、`sheng-wifi-association-event.patch` | Wi-Fi launchd cache / 蓝牙运行时 / Wi-Fi 事件；特定服务相关 | `patches/xnu-12377/series:11-13` |
| `sheng-main-thread-profile.patch`、`sheng-cache-input-diagnostic.patch`、`sheng-bluetooth-exit-diagnostic.patch` | 主线程、cache 输入与蓝牙退出诊断；相关但不是已证修复 | `patches/xnu-12377/series:14-16` |
| `zzzzzzzzzz-sheng-sigp-reinit-assert.patch` | SIGP 重初始化断言；用户态间接相关 | `patches/xnu-12377/series:17` |
| `sheng-appsync-runtime.patch`、`sheng-appsync-user-trust.patch` | AppSync 启动与用户 trust；直接相关于特定应用，非 SIGKILL 证据 | `patches/xnu-12377/series:18-19` |
| `zzzzzzzzzzz-sheng-edge-matrix.patch` | 调度边矩阵；用户态间接相关 | `patches/xnu-12377/series:20` |
| `zzzzzz-sheng-bsd-checkpoints.patch`、`sheng-bootstrap-checkpoints.patch`、`sheng-headless-startup-checkpoints.patch` | BSD/bootstrap/headless 启动检查点；用户态启动诊断 | `patches/xnu-12377/series:21-23` |
| `sheng-startup-failure-log.patch`、`sheng-process-exit-log.patch` | 启动失败及进程退出日志；直接诊断相关 | `patches/xnu-12377/series:24-25` |
| `sheng-platform-sleep.patch` | 平台休眠；用户态间接相关 | `patches/xnu-12377/series:26` |

这些名字不在 enuma 的默认 device series（`patches/xnu/series:3-4`），但 **尚未对所有 arch/soc/os 项、r17 的祖先增量和补丁内容逐一做等价性核对**，因此不能把上表称为已证明的「sheng 有、enuma 功能无」。尤其进程退出记录在 r17 已有独立实现。

## 2. 配置差集

| 项 | sheng | enuma | 边界 |
|---|---|---|---|
| profile | 默认 27.0.1，另有 17.7.11 override | 17.7.11 / 21H461 | `sheng board.toml:9,172-185`；enuma `board.toml:5-11,51-59` |
| owner/Data | 17 defconfig 的 OWNER_ROOT_AUDIT/TRUST、CACHE_MOUNT/STARTUP、BOOT_MANIFEST、DATA_MOUNT、UNION_SYSTEMOS 均 y；默认 27 配置 persistent_data=true | 默认 defconfig 未显式列上述宏；r17 是单独候选，不能以默认值代替其编译结果；r11 文档记载 scratch Data | sheng `configs/sheng_defconfig:5-16`、`board.toml:96-98`；enuma `configs/enuma_defconfig:1-22`、`docs/enuma-r11-keystore-host-20261121.md:24` |
| trust cache | 默认 27 声明 Static、System、App 三项；17 override 删除 runtime | 默认 board 声明三哈希，IPSW fetch 为 Static 和 System；r17 的实际合成输入未在此复核 | sheng `board.toml:69,190-191`；enuma `board.toml:51-59,76-78` |
| keystore | 17 组件清单含 AppleKeyStoreState；启动参数 `aks=1` | r11 独立 stand-in `sheng-aks=1`；用户提供 r17 `reg 0/pub 1/match 1/aksid 0` | sheng `board.toml:176,185`；enuma `docs/enuma-r11-keystore-host-20261121.md:24`；不代表完整 keybag/持久 keychain |
| watchdog | `disable-watchdogd=1` 与 `lite=1`；对应源码构造 launchd policy | 用户给出的 r17 参数无这两项；未证最终内建参数与实现 | sheng `board.toml:61,185`、`package/BootWatchdogPolicy.c:104-127` |
| vnode/jetsam | ADT `kern.maxvnodes=78848`，源码注释指出 vnode jetsam 杀 daemon | 默认 board 无此项；r17 实际 ADT/计数/kill reason 未核 | sheng `board.toml:140-143`；数值不可直接照搬 |
| persona | 未查到明确对应配置 | 旧记录 persona type 6 ESRCH，影响未定 | enuma `porting.toml:82` |
| 多核 | `smp=1` 和 SPI IPI | 用户给出的 r17 参数无此项；实际 CPU online 数未在此核查 | sheng `board.toml:185` |
| 4K | 17 defconfig 未显式列 4K 宏，具体合并结果未核 | 目标 4K，公共 series 含 3 项 4K 补丁；r17 的完整编译宏未核 | enuma `AGENTS.md:6`；UniXNU arch series `:14-16` |
| 内存 | 默认 27 owned window `0x130000000` | 默认 board `0x20000000`；r17 实际窗口未在此核查 | sheng `board.toml:96`；enuma `board.toml:90-91`；不是物理总 RAM |

## 3. boot-args

sheng 17 的完整参数是 `board.toml:185`，sheng 27 默认是 `board.toml:61`；本比较优先 17 override 而非混同 27。r17 列表来自用户题面，`offline-legacy-*=1` 是通配简写，无法据此逐个核对其实际值。

| 参数/组 | sheng 17 | r17 题面 | 可能影响 |
|---|---|---|---|
| `-v serial=3 native-ufs-root=1 pmgr=2 offline-mobile-graphics-load=1` | 有 | 有 | 名称相同不证明实际路径相同 |
| `rd=md0-ramblock`、`sheng-pmgr=2` | 未列 | 有 | 内存盘与板级 PMGR 路径不同 |
| `disable-watchdogd=1 lite=1` | 有 | 未列 | 前者禁 watchdogd，后者裁掉指定 jobs；不证明这就是 killer |
| `data-persist=2 -apfs_shared_datavolume` | 有 | 未列 | Data 配置和持久化路径不同 |
| `aks=1` / `sheng-aks=1` | 前者 | 后者 | 不可假定两个名字等效 |
| `smp=1 armcpu-spi-ipi=1 cpufreq=4` | 有 | 未列 | 并发与速度差异，不直接证明 SIGKILL |
| `offline-mobile-graphics-client=1`、`offline-apfs-load=1`、`offline-legacy-*` | 精确值见 sheng `board.toml:185` | graphics-load 有，legacy 为简写 | 客户端、APFS、显示路径不能按简写判定等价 |
| `vsync=120` / `sheng-vsync=60` | 前者 | 后者 | 帧节奏及参数消费者不同 |
| `debug=0x14e kt_fixed_zones=120 -no_slto_panic ml-timeout-lock-panic-scale=40` | 有 | 未列 | 诊断、区域及超时策略不同；不推断具体杀进程效果 |
| `offline-hid-home=1 offline-hid-input=1 offline-key-events=1 touch=4 touch-hid=1 buttons=1 backlight=1` | 有 | 未列 | 输入和背光不同 |
| `gpu-power=9 gpu-metal=1 fb-gpu=1 gpu-dcvs=1 gpu-addon=1` | 有 | 未列 | GPU/图形能力不同，可能影响 SpringBoard，不证明 SIGKILL 来源 |
| `boot-progress=2 boot-ui-focus4=SpringBoard banner=0 staged-apps=1 wifi=5` | 有 | 未列 | 启动 UI、应用 staging 与 Wi-Fi 差异 |

## 4. SIGKILL 候选（排序仅为调查优先级）

1. **资源压力/vnode jetsam**：sheng 源码明确记录 vnode 上限不足造成 daemon 被 jetsam 连续杀死，且设置 `kern.maxvnodes`；enuma 当前缺 killer、jetsam reason、vnode 水位，不能断言同因。
2. **watchdog 或 launchd policy**：sheng 关闭 watchdogd 并精简服务，enuma 题面没列这两项；但没有信号发送者和超时记录，watchdog、其他内核路径与用户态显式 kill 都未区分。
3. **Data/keystore/服务依赖不完整**：临时 Data 与 stand-in 的注册/匹配不代表密钥、权限和 Data 属性完整，可令服务卡住或失败，但缺日志证明它导致 SIGKILL；也不能把普通退出直接认作 SIGKILL。

persona ESRCH、4K/cache 的潜在 ABI 差异属于未定候选；已有 shared-region 成功与 cache 可解析不证明所有共享页/签名/运行时路径正常。CPU 测速不能排除所有调度等待，但削弱笼统「CPU 数量级慢」解释。

## 5. 不可直接类比

sheng 默认 27 的 xnu-12377 补丁与其 17 override 是不同组合；题目未提供 sheng 成功实测所用的精确 profile、commit、构建与部署清单。enuma 是 iPad7,1、iPadOS 17.7.11、xnu-10063、4K；不同 donor 的 arm64 与 arm64e、实际页粒度、信任与 cryptex 格式不能推定相同；sheng SM8550 与 enuma SM8250-AC 的内存、显示、存储、CPU 与设备树亦不同。相同启动参数不证明相同消费者或行为。

缺完整 r17 最终对象/宏/ADT、sheng 实测 profile 和逐补丁内容对照，因此此文不宣称全量差集；未复核的项明确标为未定。
