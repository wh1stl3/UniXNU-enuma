# enuma r66 + IPC 单次实机观察 — 2026-11-25

状态：`self-checked`；阶段不提升。设备动作、照片及 vision 判读由主控提供，本记录未重新访问设备或照片。

## 动作和输入

- 主控报告 enuma 刷写 `boot_b` 后重启；serial 脱敏。未提供命令输出、退出码或设备侧回读。当轮授权及 claim 已消耗，不得访问、删除或重放；不构成新设备操作授权。
- 主控提供实际 reviewer `ses_ded25e8a7ffeY6E0nb8OIP9wq4` 有条件接受；未经 deep_reviewer。基线核对范围仅两路径/宏及抽样五件，不是全部输入哈希，详见离线封装记录。
- 镜像 `out/ufs-sm8250-r66-ipc-20261125/boot.img`：169,951,232 B，SHA-256 `205b4148274714137bcd2e48752b9e8cb310a7b23ffd80bad5fddce9e01a238f`。
- 内核 SHA-256 `5e46e1a460caa89c17bd64a724c4b0e26c23e2acf4af3eb69069743fcc6d557e`；离线封装见 `docs/enuma-r66-ipc-20261125.md`。
- vision 判读 `media/r66+ipc.jpg`、`media/r66+ipc2.jpg`；照片不入 Git。

## IPC 和进程观察

| 采样 | t | launchd(1) send/recv | backboardd(34) send/recv | `sb(5)` send/recv | `enuma-ex` ok/fail |
| --- | ---: | ---: | ---: | ---: | ---: |
| i=1 | 188 | 4347/135 | 36/32 | 639/423 | 291/3 |
| i=2 | 248 | 4499/163 | 36/32 | 639/423 | 297/3 |

进程表为 `1:launchd 4:SpringBoard 5:assistantd 34:backboardd`；`sb(5)` 标签错误，实际采样的是 assistantd，SpringBoard 是 pid 4。

按主控提供的 60 秒采样间隔，launchd send +152、recv +28，仍有活动；backboardd 两项成功计数均不变。send/recv 总数差 4 不是未回复数量，不能配对请求和回复，也不能证明 launchd 收到或未回复 routine 800。历史 FP 链中的 `0x320` 是调用参数，不是已知 Mach `msgh_id`；本次照片也未直接证明该调用栈。

第三帧 `i=3 t=309` 按设计不打印 `enuma-ipc2`（仅 i=1、2 打印），不能把该行缺失解释为异常。AX lookup 的请求者名称被截断，身份未知；注册者调查尚无可确认结果，留待交接。

## 边界

照片未见 panic 或 `MACH Reboot`；未证明 GUI、可交互性或持续稳定性。单次观察未重复验证，阶段不提升；本记录工作未操作设备、未重启、未轮询。
