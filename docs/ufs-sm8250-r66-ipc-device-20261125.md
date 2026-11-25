# enuma r66 + IPC 单次实机观察 — 2026-11-25

状态：`self-checked`；阶段不提升。设备动作、照片及 vision 判读由主控提供，本记录未重新访问设备或照片。

## 动作和输入

- 主控报告 enuma 刷写 `boot_b` 后重启；serial 脱敏。未提供命令输出、退出码、设备侧回读或刷写前最终 diff 审查结论。
- 镜像 `out/ufs-sm8250-r66-ipc-20261125/boot.img`：169,951,232 B，SHA-256 `205b4148274714137bcd2e48752b9e8cb310a7b23ffd80bad5fddce9e01a238f`。
- 内核 SHA-256 `5e46e1a460caa89c17bd64a724c4b0e26c23e2acf4af3eb69069743fcc6d557e`；离线封装见 `docs/enuma-r66-ipc-20261125.md`。
- vision 判读 `media/r66+ipc.jpg`、`media/r66+ipc2.jpg`；照片不入 Git。

## IPC 和进程观察

| 采样 | t | launchd(1) send/recv | backboardd(34) send/recv | `sb(5)` send/recv | `enuma-ex` ok/fail |
| --- | ---: | ---: | ---: | ---: | ---: |
| i=1 | 188 | 4347/135 | 36/32 | 639/423 | 291/3 |
| i=2 | 248 | 4499/163 | 36/32 | 639/423 | 297/3 |

进程表为 `1:launchd 4:SpringBoard 5:assistantd 34:backboardd`；`sb(5)` 标签错误，实际采样的是 assistantd，SpringBoard 是 pid 4。

按主控提供的 60 秒采样间隔，launchd send +152、recv +28，仍有活动；backboardd 两项均不变。backboardd 计数差为 4；主控结合既有 FP 链判读为四条已发未回消息、卡在 `__xpc_bootstrap_services` 等 `0x320` 回复，launchd 未完成其请求。仅凭两项总计数之差不能独立证明请求与回复的配对或待回复数量，本次照片也未直接证明该调用栈。

## 边界

照片未见 panic 或 `MACH Reboot`；未证明 GUI、可交互性或持续稳定性。单次观察未重复验证，阶段不提升；本记录工作未操作设备、未重启、未轮询。
