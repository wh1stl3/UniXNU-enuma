# nuwa SMP 状态对照（2026-11-23）

仅离线阅读；设备结果为既有记录转述，未构建、未访问设备。路径均相对 `D:/Code/PortingiOS/nuwa/`。

## 参数

- 默认配置 `UniXNU-nuwa/board.toml:133` 原文：`kernel_args = ["-v", "serial=3", "sheng-platform-stage=5"]`。这是默认配置，不等同各实验包的实载参数。
- 一份较新实验包的完整参数，`worktree-display-dsp/docs/nuwa-sb-stack3-20261123.md:43`：

  `-v serial=3 native-ufs-root=1 native-ufs-lun=0 nuwa-pmgr=2 rd=uuid boot-uuid=DADD93F8-DBBF-4B17-A1DF-0F11E64172F7 boot-progress=2 aks=1 disable-watchdogd=1 build-tag=nuwa-r35 boot-progress-scale=3 sheng-data-persist=2 sheng-log-reserve=1024 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-phase=4 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 nuwa-lite=1 nuwa-mg-reset=1 nuwa-hid-standin=1 nuwa-sb-stack=360`

  不含 `sheng-smp=1`、`cpus=`、`max_cpus=`、`smp=`；该包不是下面 logo 载荷的实测参数回读，不能代替它。`worktree-display-dsp/docs/nuwa-resume-display-scale-20261122.md:19` 只说 logo 候选的 outer 配置与 rotation 一致，本次未取得其完整参数及设备端回读。

## SMP 组件与运行证据

- `UniXNU-sm8550-common/patches/xnu/series:1` 选择 `native-smp-secondary.patch`；该补丁第 7–8 行将 `MAX_CPUS` 从 4 改为 8，第 17–21 行允许 secondary 启动时从 MPIDR Affinity1 取编号。它提供支持，不证明从核已运行；本次未证明 logo 包最终链接了此补丁或 IPI 运行正常。
- `worktree-display-dsp/docs/nuwa-r35l-candidate-inventory-20261121.md:61` 原文：`cpu0–cpu7 均有 reg/state/device_type/compatible/timebase-frequency；SMP 未证`。ADT 拓扑不是在线 CPU 数量。
- `UniXNU-nuwa/docs/nuwa-userspace-20261119-observation.md:188-189` 原文：`页面 armcpu_smp_* 全程 req=0 run=0 cond=0 boot=0（r16 读数），即从未请求启动从核；到 r35 未改。` 该记录第 191 行引用录像转录；设备读数为主控转述。
- 同文件 `:200` 原文：`SMP 未启用：armcpu_smp_requested 从未置位，用户态只有单核调度。` `UniXNU-nuwa/docs/nuwa-r34-page-evidence-20261120.md:16` 原文：`SMP 未开，仅 boot CPU。`
- 缺 logo 轮次独立在线 CPU 数量或从核执行读数；旧 r16/r34 的证据不能单独证明 11-22/23 载荷仍单核运行。也未发现对应 logo 轮次的 IOSleep 并发测试。

## 到达位置

- launchd：`AGENTS.md:17` 记载原生 UFS 根卷挂载并进入用户态，设备侧为主控转述；是否完成初始化未由该轮证明。
- Apple logo：`worktree-display-dsp/docs/nuwa-logo-milestone-20261122.md:5` 原文：`约 290 秒诊断页消失，出现 Apple logo 并保持至少 560 秒；底部横幅仍在且持续刷新。` 来源为用户实机观察、主控转述；不独立识别提交者。
- SpringBoard/backboardd：`worktree-display-dsp/docs/nuwa-mobileactivation-migration-20261122.md:9-10` 记录 `SB=26 bb=54` 等进程在采样中在场，以及 `SC n=12 r=0 o=12`；按用户/主控提供帧归属，backboardd 显示 logo，SpringBoard 当轮未提交帧。进程在场不等于初始化完成。
- 较新观察 `worktree-display-dsp/docs/nuwa-sb-stall-20261123.md:9-11,21` 记录 SpringBoard 重启后存活、两次 SC 均为 10、无新帧；只证 backboardd CPU 拷贝的 logo，不证 SB → swap。不是「完全无像素」，而是有 logo 像素、无已证 SpringBoard 帧。
- Setup、桌面与交互：本次检索未找到实测达到的证据；`AGENTS.md:22` 将早期一次 `Launcher` 用户观察与本次区分，不能当作当前桌面验收。断电重启交互亦未证。

## 判断

r16 至 r35 单核结论有中等强度证据（现场计数经转述，加配置/文档印证）；logo 及较新 SpringBoard 轮次没有同轮 CPU 计数，是否多核运行仍无证据。单核不妨碍 nuwa 历史版本进入 launchd 和 SpringBoard 进程，但不能据此证明单核不阻碍 enuma 出帧，也不能声称 logo 必定在单核运行时出现。状态：self-checked，未独立复核。
