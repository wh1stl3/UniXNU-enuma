# lite 21 项来源与 SIGKILL 证据（2026-11-23）

状态：self-checked；只读既有源码及文档，无构建、无设备操作。结论：21 项是从 sirius 整表继承的假设性裁剪；未找到任何一项在 enuma 杀其他进程或导致重启的强证据，也未证实际禁用生效。不能据此判定恢复安全。

## 原始记录与边界

* `docs/enuma-r19-watchdog-lite-host-20261122.md:8-14` 原文：“保留其两开关、21 个 job 和 VFS 写入机制”及“`sheng-lite=1` 对下表 21 个 label 写入 `true`”。来源 `HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503`，文件 SPDX MIT；不是逐项由 enuma 故障导出的列表。
* `docs/repo-diff-adt-bootargs-20261123.md:175` 原文：“the same policy also disables the network/iCloud/photo daemons this phone has no use”。这是 sirius 的裁剪理由，不是 enuma 杀进程证据，不能逐项扩展为功能已核实。
* `docs/enuma-r22-memory-window-host-20261122.md:8-13` 原文：“约 180 秒起成批 `st=9 sig=9`，包括 nfcd、tccd、homed、backupd、corespeechd、mobiletimerd、routined、securityd，且反复起落。录像未见 watchdogd、jetsam/memorystatus 杀进程日志或 `comm=SpringBoard`，无图形。`sig=9` 不标识发送者”。这些是受害者而非发送者；列出的八个名字均非 21 项。该记录是 r21 派单转录，“包括”不代表完整列表。
* `docs/enuma-r17-exit-probe-host-20261122.md:23` 原文：“单凭信号不能区分 watchdog、jetsam、服务管理器或显式终止。”发送者未知，不能说 watchdogd 或名单中的任何 job 杀了它们。
* `docs/enuma-r19-watchdog-lite-host-20261122.md:58-60` 原文：“双开不能单独归因 SIGKILL 降幅”，“用 watchdogd-only 对照确认”，“未确认 override 消费时不能排除”。`:62-65` 原文：“不拦截 SIGKILL”；“SIGKILL 来源”未验证。引入策略是同时测试 watchdog 与 lite 的假说，不是证明这 21 项导致 SIGKILL 或重启。
* `docs/enuma-r22-device-20261122.md:15,23-24` 原文：“12 个采样帧（59.5–449.5 s）……未见 `sig=9`”；“本轮同时改变 `sleep-disabled`，无法归因于单一变量”。只涵盖可见采样，不证明消失由禁用列表造成。
* `docs/launchd-disable-list-20261123.md:69-71` 原文：“该代码不杀进程、不拦截后续 spawn，也不证明 launchd 已消费或强制执行”；“未找到设备上直接读取完整 disabled.plist、launchd 消费该文件、或对指定 job 禁用/启用做正反对照的证据”。且它截断重写已有 plist，实验时须控制 Data 初始状态，不能仅改变参数。
* `docs/pipa-reference-20261123.md:143` 原文：“pipa `:17-21` 描述 identityservicesd/contextstored/locationd 同步 XPC 等待环”；“这是**间接依赖**”。跨设备报告既不是 enuma 复现，也不是杀进程或重启证据。
* `docs/launchd-disable-list-20261123.md:53-60` 列出 sheng 四项是 identityservicesd、locationd、CommCenter、bluetoothd；这是配置对照，不是 enuma 安全认证。另行关闭 watchdogd 不算 21 项之一。

## 逐项判定

判据：强 = 有证据该 job 在 enuma 杀进程或导致重启；弱 = 有整表继承的加入证据，但无该 job 的上述因果证据；查不到 = 连加入记录也找不到。弱不等于该 job 确实无害或在任何录像中从未被杀。全部 label 前缀均为 `com.apple.`。表中行号指 `package/BootWatchdogPolicy.c`；各项的整表加入证据均为 r19 文档 :8-29。

| job | 分类 | 依据 |
|---|---|---|
| identityservicesd | 弱 | :20；sheng 四项之一；pipa 跨机 XPC 等待环，非 enuma 杀进程证据 |
| locationd | 弱 | :20；sheng 四项之一；同上 pipa 等待环仅跨机报告 |
| CommCenter | 弱 | :20；sheng 四项之一，缺本板因果 |
| bluetoothd | 弱 | :20；sheng 四项之一，缺本板因果 |
| photoanalysisd | 弱 | :21；整表继承，缺本板因果 |
| mediaanalysisd | 弱 | :21；整表继承，缺本板因果 |
| mediastream.mstreamd | 弱 | :21；整表继承，缺本板因果 |
| icloud.searchpartyd | 弱 | :21；整表继承，缺本板因果 |
| findmy.findmybeaconingd | 弱 | :22；整表继承，缺本板因果 |
| familycircled | 弱 | :22；整表继承，缺本板因果 |
| financed | 弱 | :22；整表继承，缺本板因果 |
| softwareupdateservicesd | 弱 | :22；整表继承，缺本板因果 |
| ndoagent | 弱 | :23；整表继承，缺本板因果 |
| biomesyncd | 弱 | :23；整表继承，缺本板因果 |
| email.maild | 弱 | :23；整表继承，缺本板因果 |
| amsengagementd | 弱 | :23；整表继承，缺本板因果 |
| adid | 弱 | :23；整表继承，缺本板因果 |
| eyereliefd | 弱 | :23；整表继承，缺本板因果 |
| fairplayd.A2 | 弱 | :24；未找到本板杀进程/重启证据，安全服务依赖未查明 |
| passd | 弱 | :24；未找到本板杀进程/重启证据，恢复后的依赖和行为未查明 |
| mobile.obliteration | 弱 | :24；整表继承，缺本板因果 |

统计：强 0、弱 21、查不到加入来源 0；21 项均无本板因果强证据，但不是 21 项已验证安全。

## 精简决定

**需先实验**，不能宣布安全地一次精简至 sheng 四项。没有任何一项已由 enuma 证据证明“必须保留”，也不能反过来断言任一项可以无风险恢复。保留现有 21 项作为对照基线；sheng 四项先保留是为缩小变量而非证明必要。后续若获授权，使用相同且全新初始 Data、确认 disabled.plist 实际内容及 launchd 消费，逐组恢复其余 17 项并对照相同墙钟区间的 spawn/exit、发送者/kill reason 和用户态进展；恢复 fairplayd.A2、passd 等应观察相关依赖。仅缺强证据不足以直接部署或声称安全。无本轮设备实验。
