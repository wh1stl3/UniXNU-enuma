# enuma 全程复盘（2026-11-23）

来源：`sonnet_analyzer`。依据强度：**仅静态审查 / INSUFFICIENT EVIDENCE**；以下为对既有记录的复盘与推断，不是新增实机证据或阶段验收。

## 1. 推进与浪费

- 推进：从 launchd 推进到 SpringBoard 与 backboardd 均 exec；按现有记录排除时基、缓存页大小、framebuffer 与窗口重叠、显示适配器挡路四类假设作为当前阻塞的解释；将 `sig=9` 消失区间定位在 r19–r22。上述排除只适用于已观察的现象和候选，不证明相关机制在所有情况下正确。
- 浪费：r8/r13 反复量控制台与 IOSleep，对主链没有增量；r19/r20/r22 连续叠加改动，没有分离 `sig=9` 消失的归因。

## 2. 反复出现的方法学问题

- **以未见当未发生**：抽样漏行、读图漏读和 `calls=0` 均不能证明相应事件未发生。
- **零计数缺阳性对照**：r29 只统计 `comm==backboardd`，无全局总数，无法区分钩子未触发与 backboardd 未调用。
- **一次改多处**：因果不可分离。
- **观察窗未绑定 exec 后的经过时间**：慢与卡无法区分。

## 3. 当前事实链

按记录的推进顺序排列，不将相邻事件自动视为因果：

1. UFS OS 根卷挂载有条件成立；SystemOS 的发布不等于挂载，当前挂载状态仍须核实。
2. launchd 进入 bootstrap，约 136 s 后退出 bootstrap。
3. 共享区返回 `kr=0`。
4. 加入窗口与 `sleep-disabled` 后观察到 `sig=9` 消失；两项及其他叠加改动的作用未分离。
5. 加入 HID 占位后，SpringBoard 和 backboardd 均 exec；不证明占位提供真实触摸。
6. 显示服务可达但观察中无人使用，`AXSpringBoardServer` lookup 失败；r29 观察窗口内未统计到 backboardd 打开 IOKit，缺阳性对照，不能证明其从未调用。

## 4. 最大卡点定位

`sonnet_analyzer` 判断：backboardd 与 SpringBoard 很可能在到达 IOKit 打开之前停在用户态，或等待 mach/XPC 服务，或被单核与控制台拖得极慢；**显示链不是当前瓶颈**。依据强度：**中低**；这是假设而非已验证因果。

## 5. 下一步行动（排序）

1. **离线服务依赖清单，零设备成本**：静态分析 21H461 根卷 plist 与二进制中 backboardd/SpringBoard 启动早期 lookup 的 mach 服务，对照已有 launchd 输出；核实 `CommCenter` ENOENT 的性质及当前 SystemOS 挂载状态。
2. **一次合并观测镜像**：以 exec 为时间原点，在 30/60/120/240 s 采集 task 快照：CPU 时间、线程数与等待状态、mach 消息计数、faults/pageins、全进程 pid/comm；同时采集带**阳性对照**的 IOKit 入口计数（全局总数及按 comm），以及 `IOServiceGetMatchingService(s)` 计数。字段和入口须实施前核实。CPU 时间持续增长且 faults 增长指向慢；CPU 不动且线程在 mach_msg 等待指向等待；入口 > 0 而 `calls=0` 指向内核提前拒绝，须按返回点确认。均为待验证的判读条件。
3. 按第 2 条结果走单一分支，不预先实现；连续两轮无推进则升级 `deep_reviewer`。

## 6. 风险

- AMFI 放宽可能掩盖签名或 entitlement 故障。
- 禁用 watchdogd 与 `sheng-lite=1` 去掉暴露挂死的机制，也可能跳过 SpringBoard 依赖的服务，尚未排除。
- `sleep-disabled=1` 与 2720 MiB 窗口压缩真实内存预算，jetsam 行为未测。
- scratch Data 使首次开机配置、偏好及 keybag 路径与真实情况不同。
- keystore stand-in 与 HID 占位只让进程起得来，不提供可工作的锁屏、数据保护或真实触摸。
- 叠加改动使单项效果不可归因。

## 结论

- 当前最该做：先做第 1 条离线清单，再用第 2 条一次合并观测区分「慢」与「卡」，所有零计数带阳性对照。
- 最不该做：在未区分「慢」与「卡」前，继续堆伪造服务、绕开 backboardd，或再放宽安全/看门狗参数。
