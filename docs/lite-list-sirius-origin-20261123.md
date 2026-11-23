# sirius lite 列表来源与界面证据（2026-11-23）

状态：self-checked；只读源码与历史记录，未构建、未访问设备。sirius 源固定为 [HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503](https://github.com/HuajiFruit/UniXNU-sirius/tree/ac0c900485f3c0cd18de9707579a1cdcd3365503)，本地检出 HEAD 相同。以下 sirius 路径均相对该仓。

## 逐项对照

enuma 已提交基线 `d5075ca60e0bf757d37b63f8a0dc6ec2499a98c0` 的 `package/BootWatchdogPolicy.c:2-3` 明确标注直接来源为 sirius 指定 commit 的同名文件；`:19-24` 与 sirius `package/BootWatchdogPolicy.c:24-32` 的 lite_jobs 逐项、顺序完全一致，均 21 项。下表前缀均为 `com.apple.`；差集双向均为空。调查期间该文件出现并发、尚未提交的工作树改动：当前仅保留前四项，与 sirius 的差集为后 17 项；下表 enuma 行号仅适用于上述已提交基线，不代表当前工作树。

| label 后缀 | sirius 行 | enuma 行 |
|---|---:|---:|
| identityservicesd | 25 | 20 |
| locationd | 25 | 20 |
| CommCenter | 25 | 20 |
| bluetoothd | 25 | 20 |
| photoanalysisd | 26 | 21 |
| mediaanalysisd | 26 | 21 |
| mediastream.mstreamd | 26 | 21 |
| icloud.searchpartyd | 26 | 21 |
| findmy.findmybeaconingd | 27 | 22 |
| familycircled | 27 | 22 |
| financed | 27 | 22 |
| softwareupdateservicesd | 27 | 22 |
| ndoagent | 28 | 23 |
| biomesyncd | 28 | 23 |
| email.maild | 28 | 23 |
| amsengagementd | 28 | 23 |
| adid | 28 | 23 |
| eyereliefd | 28 | 23 |
| fairplayd.A2 | 32 | 24 |
| passd | 32 | 24 |
| mobile.obliteration | 32 | 24 |

两者另有独立开关对应的 `com.apple.watchdogd`，不是 21 项之一。sirius `:21-23` 称列表面向无无线与账户的设备、减少资源竞争；`:29-31` 描述 fairplayd 反复启动和 passd 崩溃等硬件观察。这些不是 enuma 的因果或安全证据。

## 启动证据：原文与判读

* **实测记录、非 GUI**：`porting.toml:289`：“launchd runs every boot task through mount-phase-2 and logs 'Early boot complete' at 161.5 s; driverkitd, MobileGestaltHelper, mobileassetd and SpringBoard start ... watchdogd's brk #1 exit panics the boot at 191.9 s.” 这是更早一次运行，不能证明图形界面。
* **实测记录、曾黑屏**：`porting.toml:365`：“SWAP calls=8 accepted=8 rejected=0, gpu offers=0; FB total=6 copies ... the screen above the panel is black”; “backboardd (pid 56) creates work intervals without error”。sirius 确有进程运行而显示黑屏的阶段；但它已有 swap 和黑帧，不能认定与 enuma 当前无已证实 swap 的具体阻塞机制相同。
* **实测记录、非完整界面**：`porting.toml:560`：“the screen went on to iOS's Apple logo with a moving progress bar, the first picture the OS has drawn on this phone.” 同一记录还报告 `pmap.c:3514 Assertion failed: not_in_kdp` 出现在 panic buffer，但心跳继续；不能把该次当作无异常运行。
* **实测记录、用户态界面**：`docs/evidence/sirius-gpu-20261029-phase1.log:2`：“Panel photo at t=389 s: Setup 'hello', no panic.” 这是仓内照片描述而非本次独立核读图像。
* **实测记录、交互**：`porting.toml:410`：“Setup reacts to touch (confirmed on the phone) and applies a choice (SpringBoard restart at 345 s).” 对应 `docs/evidence/sirius-touch-hid-20261029-combined.log:1-12` 记录 kernel `67b65eb`、payload `1611d2a`、SpringBoard、backboardd 和 Setup 的 exec；日志本身不直接证明触摸动作，其效果来自 porting 记录的屏幕确认。
* **项目汇总**：`AGENTS.md:34-38`：“iOS reaches the Setup assistant ("hello", status bar, clock) ... CPU-rendered”；“Setup reacts to touch”；同时列有 wallpaper 扩展 crash-loop 等问题。这是有交互的 Setup，不等于桌面、完整功能或稳定生产系统。

## 21 项与 GUI 运行的联系

GUI/触摸证据的源码 revision 为 `fb84613a61cf55e48e30f2e126fd6b3183820def`（`porting.toml:410`）。`git show fb84613:board.toml` 可见 `sheng-lite=1` 和 `sheng-disable-watchdogd=1`；同 revision 的 `package/BootWatchdogPolicy.c` 含与当前相同的全部 21 项且 lite 分支写入策略。因此有**同一源码 revision 的配置与设备界面正面关联**，不是无正面证据。不过未取得该次设备上的完整 disabled.plist、launchd 消费或 21 项逐一生效证据，也没有仅切换此列表的 A/B；不能据此证明每项被禁用、每项无害或在 enuma 上不致命。

## 再追一层

固定 [UniXNU/UniXNU-sheng@da9fab96aea0b5dcdb3bef730b10397276514dac](https://github.com/UniXNU/UniXNU-sheng/blob/da9fab96aea0b5dcdb3bef730b10397276514dac/board.toml) 的配置仅有前四项，见本仓 `docs/launchd-disable-list-20261123.md:53-60`；故不是该 sheng 配置的 21 项整表。官方 UniXNU 本地固定基座文档 `docs/zh/guide/skip-setup.md:91` 仅示例 identityservicesd 和 locationd。sirius `68cb281b730233ce3953edee0a793f28e71961b1` 是当前可见历史根，其提交信息称 `package/` 原样迁自 legacy 分支；该根提交已包含完整 21 项。未取得 legacy 起源历史，因此不能判定列表最初由 sirius 创作还是从其他仓扩展，尤其不能把四项重合作为复制方向的证明。

## 结论

直接来源 sirius：是，21/21 同序一致。sirius 到达过用户态 Setup 且记录过触摸反应；也曾有 SpringBoard/backboardd 运行但黑屏的早期阶段，之后才出现画面。按“设备曾运行到可交互用户界面”的窄义，继承自能跑的设备成立；按“这 21 项逐项生效且不致命，能直接用于 enuma”的强义无法判定。无桌面或完整系统稳定性结论。
