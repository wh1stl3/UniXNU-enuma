# nuwa SystemGroup seed 与 enuma 的关联（2026-11-23）

结论：现阶段不建议 enuma 复刻 nuwa 的 seed 改动。用户提供的新事实是 nuwa 重出该批 dbr 后 Apple logo 阶段一直没有 crash；本轮没有对应设备日志、精确包身份、观察窗口及单变量对照，不能据此确定 crash 类型或 seed 因果。nuwa 的增量针对用户态 SystemGroup / mobileactivationd migration，不是已证明的解封或显示修复。本轮只读分析，设备未访问，未构建；`self-checked`。

## 1. nuwa 此前的记录

以下均是主控转述，非本轮独立复核。路径相对 `D:/Code/PortingiOS/nuwa/worktree-display-dsp/`：

- `docs/nuwa-logo-milestone-20261122.md:5–9`：Apple logo 保持至少 560 秒；“CRASH 全为 `mobileactivationd`，`status=5 sig=5 ns=2 sub=5`，约每 13 秒一次”。这是用户态进程崩溃计数，不等于内核 panic。
- `docs/nuwa-mobileactivation-migration-20261122.md:9–12`：`crashes` / `exits` 递增，崩溃在 mobileactivationd、lsd、suggestd 间轮换，mobileactivationd 反复出现相同 `status=5 sig=5 ns=2 sub=5`。`:17–20` 的静态候选路径引用 `"Migration failed."` 并调用 `_os_crash`、`brk #1`，但完整实机 PC/slide 和 migration 内失败点未确定；`:32–35` 不确定其与 SpringBoard 的因果，认证 NOT REACHED。
- `docs/nuwa-logo-milestone-20261122.md:6` 还记录更早 SpringBoard `FBSDisplayMode` 崩溃，补 ADT `display-scale` 后不再出现；这是另一改动，不能归因于 dbr。
- 更早的 `docs/nuwa-launchd-reached-20261115.md:90–92` 记录 `rootvp not authenticated after mounting` 和 `OS_REASON_EXEC` / `EXEC_EXIT_REASON_SECURITY_POLICY=8`，分别靠实验绕过继续；不是已证与上述 logo 阶段崩溃同因。`docs/nuwa-ci-evidence-20261120.md:31,59` 对当时 r34 记录 SpringBoard/mobileactivationd SIGTRAP、认证 NOT REACHED。未发现可关联新 dbr 前后对照的 nuwa `libSystem`、keybag 或 keystore 错误原文。

## 2. 原 seed 和新 seed 的逻辑块差异

只读输入：`D:/vmshare/data-8g-keybag.dbr`，1,896,608 B，SHA-256 `2c95d15be323eeb336c58aa1d9cc35bc72c0923942e76a702ab24c0a858c8110`；`D:/Code/PortingiOS/nuwa/worktree-display-dsp/out/nuwa-systemgroup-seed-20261122/data-8g-sg.dbr`，2,121,888 B，SHA-256 `692355638b31d347ced5983a5910491f0556156f79675c2e371ebe9987683247`。原 seed 的哈希与 nuwa `out/nuwa-systemgroup-seed-20261122/apply.log:1–4` 一致。

使用固定上游 `UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241` 的 `drivers/DarwinBoot/Test/packed_ramdisk.py:14–35` 中 `regions` 解码，缺页视为全零，只比较两者页索引的并集，未写展开文件。两者逻辑容量均 8,589,934,592 B；原/新非零页分别 463/518；56 个 4096 B 页不同，页内实际不同字节共 26,096。逻辑偏移与覆盖长度如下；长度是完整差异页覆盖范围，不是每个字节均不同：

| 块号（含端点） | 逻辑字节偏移 | 覆盖长度 B |
|---|---:|---:|
| 0–0 | `0x0` | 4096 |
| 415–426 | `0x19f000` | 49152 |
| 6556–6562 | `0x199c000` | 28672 |
| 6747–6752 | `0x1a5b000` | 24576 |
| 6803–6805 | `0x1a93000` | 12288 |
| 65630–65654 | `0x1005e000` | 102400 |
| 131084–131085 | `0x2000c000` | 8192 |

块 0 等发生字节变化不等于指定字段被改变；未解析各块 APFS 对象、字段或前后十六进制内容，不把块号解释为需要手工修补的地址。复现算法：对每个 `(offset, data)` extent 切成 4096 B 页并按 `offset/4096` 建字典；遍历两字典键并集，缺页取 `bytes(4096)`，比较各页并累计逐字节差异。不要直接比较编码文件偏移，因为 extent 表及数据位置会变化。

生成日志 `out/nuwa-systemgroup-seed-20261122/apply.log:7–13,48–68` 记录读写挂载旧 raw、SystemGroup 由 0 增至 34、再卸载打包；`:50–54` 记录 mobileactivationd 的 Library、ucrt、dcrt、internal 和假定所有权。`docs/nuwa-systemgroup-seed-20261122.md:37,39,142–161` 描述保留原镜像及未执行的参考流程；它不是实际脚本逐命令执行日志。`repack-seed-only.py:20–22,35–54` 将新 seed 与相同预期卷 UUID `B0E0F71F-A265-4038-8F5C-6D3632859DEF` 绑定检查；这不证明角色、keybag 内容或所有元数据未改变。

## 3. 机制判断

| 假说 | 判断 |
|---|---|
| SystemGroup/keybag 与 keystore 身份匹配、解封成功从而消除 crash | 日志支持创建目录、权限为假设；没有解封成功、身份匹配或 crash 因果证据。mobileactivationd migration 是候选问题类别，不等于已解决认证。 |
| 卷 UUID 或 role 被修正 | 新包使用旧 UUID；未见 role 被修改的证据。不能说 UUID/role 修复了 crash。 |
| APFS 字段更符合内核 | 比较显示若干逻辑页变化，但未解析字段且没有内核消费证据，仅可能性。 |
| 重新格式化使结构更干净 | 与记录的旧 raw 挂载增补路径不符；不是本次已记录的做法。 |

用户的无 crash 观察是重要的后续现象，但缺同一 crash 指标、产物与改动单变量绑定；无法从时间先后断言具体机制。

## 4. enuma 对应与区别

- `docs/data-seed-20261119-generation.md:3–11,57–66,104–117`：enuma seed 是小于 2 GiB 的临时 RAM scratch，Data role 0；无法证明持久 Data。不是 nuwa 的 8 GiB seed。
- `docs/ufs-root-mount-20261118-observation.md` 和 `AGENTS.md:19`：历史一次出现 device-tree `system-volume-auth-blob` ENOENT、SystemOS 未挂载、`Library not loaded: /usr/lib/libSystem.B.dylib` 后 panic。这是早期特定包的真实失败，不能称 enuma 历史从未 panic，也不能把其归因于 keybag。
- `docs/sharedcache-fixup-gap-20261123.md:65` 记录 `Need authenticator (81)`、named root snapshot 和认证层与页签名层的区别；`docs/aks-device-id-20261123.md:48` 将设备身份缺失视为 stand-in wrap/unwrap 的源码前置缺失，但 GUI 因果未证。用户提供 `aksid=8`；本次未找到足以独立定义或归因该值的记录，不把它当解封失败的证明。
- `docs/enuma-r44-device-20261123.md:20–33` 限定窗口内 backboardd 对四类受测 IOKit 入口均为零，偏向尚未走到受测路径；不证明整个 IOKit 未进入。当前没有可比的 nuwa logo 阶段 crash 证据，也未证明 GUI 像素输出。复刻 SystemGroup 补丁因此可能完全无效；同类 migration/解封问题是否存在尚无法判定。

## 5–6. 是否复刻、代价和验证

当前不建议重格式化 seed、手工改 APFS 块、改变 UUID/role 或直接照搬 34 个目录。它们分别会改变身份/绑定、破坏文件系统一致性、改变挂载或信任合同、引入未证权限语义；上述动作都没有对应 enuma 运行时故障证据。方法层可参考在本机型原 seed 副本上做有据的文件系统修改、保留和核对 UUID/seed identity、打包后只读检查；不能跨用 nuwa 资产（`docs/context-brief.md:23,29`）。

任何声称某 seed 修改消除 enuma 运行时故障，都需对应受控设备观察；主机检查只能证明字节和结构，不能证明用户态执行、解封、显示或持久性。新设备动作须单独授权。本次不提出上机或构建操作。
