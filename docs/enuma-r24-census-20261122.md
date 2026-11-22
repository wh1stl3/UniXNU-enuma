# enuma r24 对照与 r23 复核（2026-11-22）

`self-checked`：记录主控提供的操作及录像核读，本次未重新访问设备或核读录像；阶段不提升。

## 操作和方法

- 2026-11-22 16:13:45 +08:00，r24 刷入 `boot_b`：`Sending 'boot_b' OKAY [4.072s]` / `Writing 'boot_b' OKAY [0.402s]`，exit 0；16:13:45 `reboot` exit 0。claim `.cache/enuma-r24-nodisplay-20261122.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-hid-20261122-r24/boot.img`，169,951,232 B，SHA-256 `058090e9a3c63335b3ebc59f05d1b6c2a8ba0e7365219e6dd2ad69ee0c315d7d`。
- 录像 272.6 s；2 fps 抽帧 545 张，阈值 16.85 去重为 89 张，已核读集合覆盖 0–230 s。录像和抽帧不入库。
- 刷写前最终 diff 审查的 agent、结论及 deep / 方案 B 状态未随本次材料提供，审查状态 **UNKNOWN**；不推定已审查。

## r24 核读结果

1. 62.5 s 可见 `enuma-exec: pid=5 comm=SpringBoard`。
2. 73.0/73.5 s 可见 `enuma-exec: pid=34 comm=backboardd`。
3. 76.5 s 屏显 `(system)` 与 `(user/501) entering bootstrap mode`，行内时间戳分别为 `00:01:11.042419`、`00:01:11.042430`。
4. 135.5 s 屏显 `exiting bootstrap mode`，行内时间戳 `00:01:12.374634`（显示时间约 72.4 s）。
5. 自 159 s 屏显起持续出现 `AXSpringBoardServer` 的 `failed lookup`，最早行内时间戳 `00:02:02.511787`（显示时间约 122.5 s），requestor `nfcd[30]`。
6. 所审帧未见 `comm=SpringBoard` / `pid=5` 的 exit。屏显时间与行内时间戳是不同观测，不据此推定运行时时钟与外部时间的关系。

## r23 复核

- 快刷段 130–220 s，30 fps 抽取 1,800 帧，去重为 155 帧后分 6 批逐张核读；未见 `enuma-exec: … comm=backboardd`，也未见 `comm=SpringBoard`。
- 此前全片 0–334 s、阈值 12 的 116 张唯一帧核读报未见 backboardd；此结论因读图漏读被下方更正推翻。此前已观察到 64.5 s 的 SpringBoard exec，见 [r23 记录](enuma-r23-hid-device-20261122.md)。
- 两次去重以整块区域平均差判定，可能丢弃仅新增一行的帧；但本次 79.5 秒帧曾入选，旧「已核读帧集合中未出现」属于漏读，见下方更正。

## 判读边界

- **已观察**：r23 与 r24 均出现 backboardd、SpringBoard exec，也都出现 `AXSpringBoardServer` lookup 失败；原先 r23 未读到 backboardd 的结论见下方更正。lookup 失败不证明服务从未注册或两版的全部时间均不可用。
- **已撤回**：r23 legacy 显示适配器阻止 backboardd 启动的推断，见下方更正；这些帧也不能证明 SpringBoard 未注册 XMP 服务或其因果。
- **共同边界**：目前没有两版已具备可用图形显示服务的证据；SpringBoard 等待 framebuffer 是候选解释，未观察到具体阻塞调用，不能定论。
- **UNKNOWN**：SpringBoard 究竟阻塞在哪个调用；显示适配器的运行时效果；GUI 与用户态稳定性。

阶段不提升。

## 更正：r23 backboardd 读图漏读

用户提供第一次启动录像 `VID_20261122_154135.mp4` 的 79.8 秒截图（时间码 `00:01:19.824`），明确可见 `enuma-exec: pid=34 comm=backboardd`。此前 116 张唯一帧包含 79.5 秒那张却报「无」，这是**读图漏读，不是抽样漏帧**。截图未入库，本次按用户提供信息记录，未独立复核。

因此撤回「r23 未启动 backboardd」「显示适配器阻止 backboardd」「窗口大小与 backboardd 相关」三条推断。修正后的对照：r23 与 r24 **都有** SpringBoard exec 和 backboardd exec，两版均持续出现 `AXSpringBoardServer` lookup 失败。

当前稳定可见的共同现象是 SpringBoard exec 后该服务 lookup 失败；仅凭 lookup 失败不能确证服务从未注册。两版未证明有 GUI 像素输出，显示相关阻塞可作为候选，但不是已证明或唯一的解释。

方法教训：`vision` 对唯一帧也会漏读，单次「未见」不得作为「未发生」的证据；关键结论需用户侧或第二种方法交叉确认。阶段不提升。
