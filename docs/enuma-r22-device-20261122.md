# enuma r22 实机观察（2026-11-22）

`self-checked`：记录主控提供的操作、现场观察及 `vision` 核读；本次未重新访问设备、录像或镜像。阶段不提升。

## 操作

- 2026-11-22 15:02:05 +08:00，一次 `fastboot -s <enuma> flash boot`，输出 `Sending 'boot_a' OKAY [4.025s]` / `Writing 'boot_a' OKAY [0.370s]`，exit 0；15:02:14 `fastboot -s <enuma> reboot`，exit 0。claim `.cache/enuma-r22-flashboot-20261122.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-keystore-20261122-r22/boot.img`，169,951,232 B，SHA-256 `646e7d8dd2d1d3e4ae25d02c9b34cced7e1a1e7f20f34506cc9437b34fb360e7`。
- 主控提供回刷源已校验：r21 `cb02ded1…`、原始备份 `8f40f0c9…`；本记录未重新核验或回刷。
- 录像 457.188 s；开头按 8 fps、全片按 2 fps 抽帧至临时目录，影像不入库。
- **刷写前最终 diff 审查留痕**：本次提供的操作记录未包含审查 agent、结论或方案 B / deep 审查状态，故该不可逆写入的审查状态 **UNKNOWN**；不推定已审查。

## 结果

1. `vision` 核读的 12 个采样帧（59.5–449.5 s）里，所有可见退出为 `st=0 sig=0`，唯一异常为 `pid=118 st=19968 sig=0 comm=xpcproxy`（`19968 >> 8 = 78`）；未见 `sig=9`。对照 r21 同区间每帧 20+ 条 `sig=9`。采样范围外及不可见行不能据此断言没有 `sig=9`。
2. 可见 `launchd`、`notifyd`、`logd`、`distnoted`、`fseventsd`、`configd`、`remoted`、`mediasystemd`、`amfid`、`keybagd`、`securityd`、`tccd`、`cdpd`、`assistantd` 等 exec 记录；不证明服务稳定或功能完整。
3. 采样帧中未见 `comm=SpringBoard` 或 `comm=backboardd` 的 exec/exit 行；是否在采样外 exec 未知。
4. 约 5:57–7:28 持续出现 `failed lookup: com.apple.accessibility.AXSpringBoardServer` 与 `com.apple.bluetooth.xpc`，时间戳持续推进，不是画面冻结。前者与 SpringBoard 服务未就绪相容，不能仅凭该行确定其启动失败的原因或结果。
5. 主控现场观察：进入内核后日志打印明显变快，未作定量测量。

## 判读边界

- **已观察**：r22 候选为 2720 MiB 内核窗口加 `sleep-disabled=1`；相对于 r21，所审采样帧中的成批 `sig=9` 不再可见；多项用户态服务出现 exec 记录。刷写和 reboot 命令各 exit 0，不等于断电重启后交互目标达成。
- **待证解释**：此前成批 SIGKILL 可能与 512 MiB 内核窗口造成的内存压力相关；本轮同时改变 `sleep-disabled`，无法归因于单一变量，当前证据不足以排除其他原因。
- **UNKNOWN**：SpringBoard 和 backboardd 是否在采样外 exec、SpringBoard 未见 exec 的原因；固件窗口是否确为 `0xaa000000`（固件段核读尚未返回）；用户态稳定、GUI、持久 Data 与断电后可交互。

阶段不提升。
