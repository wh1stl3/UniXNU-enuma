# Bootprogress run-state r9 boot_b flash — 2026-11-26

- 当轮授权仅此包的 D2 诊断例外，单次刷写 `boot_b`，成功且身份不变后单次正常重启。最终 reviewer `ses_de982660fffeNLe5rUQwibJHxm` PASS；deep_reviewer 最终审查未提供。
- 先前预检未唯一识别 enuma 时已停止，无 claim、无刷写。本次 fastboot 枚举一台，显式查询 `product: enuma`、exit 0；adb 另见 nuwa recovery，未向其发送设备命令。无需 adb 重启转换。
- 预检 `current-slot: b`、`unlocked: yes`、`partition-size:boot_b: 0xC000000`（201326592 B），均 exit 0。镜像 `out/bootprogress-run-state-20261126-r9/boot.img` 169951232 B，SHA-256 `0a7df79d01478eb96ccf5932a3e13891deb8ca886e855a000527491bb25994e0`；刷写前再次校验身份、门禁与镜像。
- 原子 CreateNew `.cache/bootprogress-run-state-r9-flash-20261126.claimed` 成功，已消耗，禁止访问、删除或重放；未访问旧 claim。
- 18:21:56.503 +08:00 开始一次 `fastboot -s SERIAL flash boot_b IMAGE`，exit 0，墙钟 4.367 s：
  - `Sending 'boot_b' (165968 KB) OKAY [  3.842s]`
  - `Writing 'boot_b' OKAY [  0.371s]`
  - `Finished. Total time: 4.324s`
- 刷写后再次枚举连接未变，显式 product 仍为 enuma；同设备一次 `fastboot -s SERIAL reboot` exit 0，墙钟 0.033 s，输出 `Rebooting OKAY [  0.000s]`、`Finished. Total time: 0.000s`。
- 无切槽、临时 boot、continue、其他写入或重试；重启后无设备命令。未回读设备内容，不提升阶段。`self-checked`，未由独立 verifier 复核。

## 单帧观察

- 原图 `media/r9.jpg`（工作区本地，不入库），SHA-256 `5f48178adb2199999a046dfe03c1f9799067f48d2c7bb9e58ad4e7f1f288d803`；vision `ses_de89bf3a9ffebHl5sGNmGqcxBe` 核读，Astra reviewer `ses_de89b6f9cffeYMxx4K55YrQ6Ps` PASS。
- 页面显示 169s。backboardd 和 SpringBoard 的 exec 初始线程在各自按顺序执行的一次查询中均为 `run_state=3`（`TH_STATE_WAITING`，普通等待）；两次查询非同时，也不是 169s 时刻的实时状态，不能证明持续等待或死锁。PC samples unavailable。
- `PROC exec`：backboardd `22:22:b7`，SpringBoard `5:5:f`；画面未见 exit。
- `registered=1`、`legacy4.enter=1`、`parent.ok=1`、`parent.err=0`，validate 和 prep 各为 0。
- `TOUCH HID reports=0` 是板级空 sink 计数，不能证明触摸匹配。
- 单帧不证明持续运行或交互，阶段不提升。`self-checked`。
