# enuma r23 HID 占位实机观察（2026-11-22）

`self-checked`：记录主控提供的刷写、录像及 `vision` 核读；本次未重新访问设备、录像或镜像。主机候选与接线另见 [r23 主机记录](enuma-r23-hid-standin-host-20261122.md)。阶段不提升。

## 操作和审查

- 2026-11-22 15:41:51 +08:00 刷入 `boot_b`，当时活动槽为 `b`：`Sending 'boot_b' OKAY [3.995s]` / `Writing 'boot_b' OKAY [0.389s]`，exit 0；随后 `reboot` exit 0。claim `.cache/enuma-r23-flashboot-20261122.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-hid-20261122-r23/boot.img`，169,951,232 B，SHA-256 `f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b`。
- 主控提供：**刷写前最终 diff 由 `deep_reviewer` 审查，结论 PASS WITH CONDITIONS，对象为 `f8239188…` 候选**。这是 deep 审查，不是「方案 B、未经 deep_reviewer」；具体条件未随本次记录提供。本记录未独立复核审查。此前 [r22 记录](enuma-r22-device-20261122.md) 的刷写前审查身份和结论仍未知，r23 审查不能回填为 r22 审查。
- 此前 r21/r22 刷在 `boot_a`，本次刷在 `boot_b`，活动槽已变为 `b`。回刷 r22 需刷 `boot_a` 或切槽；本次记录不执行设备操作。
- 15:41 起的第一次启动录像 334 s；第二次观察以 15:49:44 为锚点。两次录像均已抽帧，以下判读以第一次为主。

## 结果（主控提供的 `vision` 核读）

1. `enuma HID stand-in: digitizer properties=1` 在 11.75 s（`b_0095`）出现，12.5 s 与 39.75 s 帧仍可见；屏上位置出现在 `enuma-exec: pid=1 comm=launchd` 之后。按主控转述的 `deep_reviewer` 判据，这是内核侧最强的节点证据；不证明触摸事件输入或用户态消费成功。
2. `enuma-exec: pid=5 comm=SpringBoard` 出现于 64.5 s（`p_0130`），这是本项目首次抓到 SpringBoard exec；不证明其持续运行或图形输出。
3. `(system)` 与 `(user/501)` 均有 `entering bootstrap mode`（约 129.5 s 帧可见）；原先抽样未见 `exiting bootstrap mode` 的判断**错误，已撤回**，见下方全帧更正。
4. `(user/501) <Notice>: pending spawn, domain in on-demand-only mode:` 涉及 `com.apple.backboardd`、`configd`、`contextstored`、`dasd`、`driverkitd`、`mobile.keybagd`、`mobiletimerd`、`MobileFileIntegrity`、`PerfPowerServices`、`accessibility.axassetsd`、`lmagent`、`mobile.softwareupdated` 等；另有 `service not yet activated: com.apple.mobile.lockdown`。
5. `failed lookup: com.apple.accessibility.AXSpringBoardServer`（requestor `nfcd[30]`）与 `com.apple.bluetooth.xpc` 持续出现。
6. 所审画面未观察到 `comm=backboardd` exec，只见 `com.apple.backboardd` 的 launchd pending 行；不能排除采样外 exec。
7. 主控报告屏幕全程为文字控制台，无图形、无黑屏。

## 判读边界

- **已观察**：HID 占位的 digitizer 属性成功日志；SpringBoard 首次 exec（pid 5）；用户域进入 bootstrap mode；多个用户域 job 有 on-demand-only pending 日志。
- **待证解释**：SpringBoard 虽 exec 但尚未发布 `AXSpringBoardServer` 与 lookup 失败相容；该日志不足以确认发布状态。原「用户域未退出 bootstrap 导致 pending」假设已被下方全帧更正推翻。
- **UNKNOWN**：SpringBoard 是否退出或卡住；backboardd 是否曾 exec；GUI、稳定用户态及持久交互。后续核读范围见下方更正。
- r21/r22 采样未见 SpringBoard exec，而 r23 出现，与「digitizer 是 SpringBoard 启动前置」假设相容；观察不是控制变量实验，不能证明占位节点导致其 exec，也不能证明该节点是必要条件。

阶段不提升。

## 更正（全帧核读）

主控提供的复核方法：对第一次启动录像去重，669 帧 → 116 张唯一屏，分批逐张核读；快刷窗口另按 30 fps 抽帧并去重。本次仅记录转述，未重做核读。

136.000 秒（`p_0273`）出现 `exiting bootstrap mode` 与 `exiting ondemand mode`，用户域 bootstrap 正常退出。原先「未见 `exiting bootstrap mode`」的结论是**错误**：先前按 2 fps 抽帧且只读部分帧，漏掉了该行；「用户域未退出 bootstrap 导致 pending」的解释同步撤回。

仍成立：HID `digitizer properties=1`；64.5 s 的 `SpringBoard exec pid=5`；`AXSpringBoardServer` 持续 lookup 失败；未观察到 `comm=backboardd` exec；已核读的 136–334 秒区段未见 `pid=5` exit。未见 exit 不证明 SpringBoard 持续正常运行，未观察到 backboardd exec 也不等于证明其从未 exec。阶段不提升。
