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
- 此前全片 0–334 s、阈值 12 的 116 张唯一帧核读，同样未见 backboardd；此前已观察到 64.5 s 的 SpringBoard exec，见 [r23 记录](enuma-r23-hid-device-20261122.md)。
- 两次去重以整块区域平均差判定，可能丢弃仅新增一行的帧。因此结论仅为**已核读帧集合中未出现**，不能确证 r23 从未 exec backboardd。

## 判读边界

- **已观察**：r24 已核读帧中出现 backboardd exec，r23 已核读帧中未出现；两版均观察到 SpringBoard exec，也都出现 `AXSpringBoardServer` lookup 失败。lookup 失败不证明服务从未注册或两版的全部时间均不可用。
- **待证假设**：r23 legacy 显示适配器可能影响 backboardd 启动；r24 虽观察到 backboardd exec，仍有 `AXSpringBoardServer` lookup 失败。这些帧不能证明适配器阻止启动、SpringBoard 未注册 XMP 服务或其因果。
- **共同边界**：目前没有两版已具备可用图形显示服务的证据；SpringBoard 等待 framebuffer 是候选解释，未观察到具体阻塞调用，不能定论。
- **UNKNOWN**：SpringBoard 究竟阻塞在哪个调用；r23 的 backboardd 是否曾在未核读或被去重帧中 exec；显示适配器是否影响它及其机制；GUI 与用户态稳定性。

阶段不提升。
