# enuma 会话交接（2026-11-23）

## 指针与候选

- 最新候选 r29：`out/ufs-sm8250-launchd-bbscan-20261123-r29/boot.img`，SHA-256 `2a74b3e1c76df21b7da561b4cf6d8a45b2b5311819f37ad7ea3ce4443dab920b`，设备槽位 `b`；见 [r29](enuma-r29-device-20261123.md)、[r28](enuma-r28-device-20261123.md)、[r26](enuma-r26-device-20261123.md)、[r23 更正](enuma-r24-census-20261122.md#更正r23-backboardd-读图漏读)。
- 当前共同现象：SpringBoard 与 backboardd 均 exec，`com.apple.accessibility.AXSpringBoardServer` 持续 lookup 失败，屏幕无像素；`AXSpringBoardServerInstance` 是另见 [服务调查](springboard-service-declaration-20261122.md) 的框架名称，不是已记录的失败服务名。

## claim

以下均已消耗，禁止访问、删除或重放（通配符仅为名称指针）：`.cache/enuma-r21-flashboot-20261122.claimed`、`.cache/enuma-r22-flashboot-*`、`.cache/enuma-r23-flashboot-*`、`.cache/enuma-r24-nodisplay-*`、`.cache/enuma-r26-fbcount-*`、`.cache/enuma-r28-fbchain-*`、`.cache/enuma-r29-bbscan-*`、`.cache/enuma-twrp-touch-20261122*`、`.cache/enuma-getevent-20261122*`。

## 回刷来源

- r23：`out/ufs-sm8250-launchd-hid-20261122-r23/boot.img`
- r24：`out/ufs-sm8250-launchd-hid-20261122-r24/boot.img`
- r26：`out/ufs-sm8250-launchd-fbcount-20261122-r26/boot.img`
- r28：`out/ufs-sm8250-launchd-fbcount-20261123-r28/boot.img`
- 原始备份：路径未确认；历史 `8f40f0c9…` 记录及缺整分区副本的边界见 [槽位计划](persistent-boot-slot-plan.md)。不得猜路径。

回刷命令模板（仅记录，须当轮授权并按型号重新识别目标、确认槽位及镜像）：`fastboot -s <enuma-serial> flash boot_b <已核验镜像路径>`，随后 `fastboot -s <enuma-serial> reboot`。不自动执行。

## 下一步

以下均为 **sonnet_analyzer 推断，需实测**；字段名、接口和判读须实施前核实，不能将相关性直接当成确定因果。

1. **观测 A（首选）**：周期 dump 打印 backboardd（按 pid 34 或 comm）的 task 计数 `messages_sent`/`messages_received`/`faults`/`pageins`/`syscalls_mach`/`syscalls_unix`，各线程状态与等待原因，同次列出全部进程 pid/comm。计数全不动且线程等待，候选为用户态 mach/XPC 阻塞；`faults`/`pageins` 增长而 `messages` 不动，候选为 dyld/页入问题；`messages` 增长但 `calls=0`，候选为启动极慢；同 dump 进程清单辅助排除 comm 未命中。字段名尚未源码核对；单次清单不能排除整个观察期内的身份变化。
2. **观测 B（次选）**：在 `is_io_service_open_extended` 入口单独计数 `comm==backboardd`，记录第一个提前返回点与返回码。入口 >0 而 `calls=0`，候选为内核提前拒绝（sandbox/AMFI/inactive），须按实际返回点确认；入口也是 0，候选为尚未经该入口发出请求。
3. **不建议绕开 backboardd**：伪造整套 BKS/HID 服务代价和风险大；现有证据不支持 SpringBoard 注册只卡在这一步。
