# enuma r25：周期进程 census

候选目录：`out/ufs-sm8250-launchd-census-20261122-r25/`。仅供主机诊断；不改默认 recipe/series，不提升阶段。

## 实现

- `bsd/kern/kern_exec.c`：在 `exec_mach_imgact()` 原 `enuma-exec` 点、`goto done` 前记一次成功路径命中。仅 PID 1、`p_comm == "launchd"` 首次命中启动定时。
- `bsd/kern/kern_exit.c`：在 `proc_prepareexit()` 原 `enuma-exit` 点、保留 `!proc_is_shadow(p)`，进入 critical-exit 判定前计数；`last_st` 是原始 wait status，不是 errno，`last_sig` 由同一状态解出。
- 一张 64 项静态表共用，`comm` 按既有 16 字节上限截断；每项用一个完整的 128-bit 原子键、32-bit exec 计数、一个 64-bit 原子 exit 计数/状态对。无分配、无新增进程锁；同名 CAS 竞争不会产生重复槽。暂停在更新中间的生产者可能让该事件进下一份快照；`n` 是本次实际输出条数，不承诺所有行同一时刻取样。满表后既有名字继续计数，新名字不再加入；首份发现溢出的清单之后追加一次 `enuma-census: table-full`。
- 本轮放弃逐条日志与 PID 关联，换取可读性。重启线索改由累计 exec/exit 计数提供；计数大于 1 不等于同一个 launchd job 在重启。同一截断名合并，不保留事件顺序或历史退出原因。
- 用 XNU 的 `thread_call_allocate_with_options(..., THREAD_CALL_PRIORITY_KERNEL, THREAD_CALL_OPTIONS_ONCE)` 和 `thread_call_enter_delayed()`，不选 `SIGNAL`。BSD 编译单元不可见静态 callout 类型；仅 PID 1 的启动点分配一次 callout，表仍不分配。`osfmk/kern/thread_call.c:1804-1808` 在工作线程里先恢复中断、释放组锁再调用回调；`ONCE` 串行回调，第 20 次不再排队并通过允许在回调中调用的 `thread_call_free()` 释放。原 exec/exit 事件不打印，也不移动既有锁或进程状态。
- 首报为 PID 1 激活点之后 30 秒 XNU absolute time；后续以各次回调开始时计算下一次 30 秒 deadline。时基、调度或屏幕输出会令墙钟间隔不同。每块最多 66 行，首次满表另 1 行；按 [r13](enuma-r13-device-20261122.md) 的 11.64 ms/行估算约 0.78 s/满块，不是 r25 实测。先保留 30 秒；若实测占用明显，改用 60 秒。后台回调仍与其他日志共享控制台，不能保证无插行或最后一块不被冲走。

```text
enuma-census: begin n=%u
enuma-census: %s exec=%u exit=%u last_st=%d last_sig=%d
enuma-census: end
```

## 录像判读

以同一对 `begin`/`end` 内 census 行数与 `n` 相等为完整快照；中间允许普通日志插行。

| 名字 / 指标 | 正向证据 |
|---|---|
| `backboardd`，`exec>0` | 命中其 exec 探针；不等于成功初始化或提交 swap。 |
| `SpringBoard`，`exec>0` | 命中其 exec 探针；不等于显示桌面。 |
| `watchdogd`，`exec>0` | 命中其 exec 探针；不等于 watchdog 已启用。 |
| `xpcproxy`，`exec>0` | 命中其 exec 探针；不识别代理的 job，不证明后续目标 exec。 |
| 任一名字，`exit>0` | 至少一次非 shadow 的 exit 路径命中；`last_st`/`last_sig` 仅为最后一次，不能判定退出原因。 |

完整且未饱和快照中的缺项，只表示截至该快照未计到；满表、缺帧或停止后的事件不能用缺项作否定证据。计数出现也不证明用户态开始执行指令、进程存活、首次 GUI swap、阶段通过或持久化。

## 主机证据（`self-checked`）

在 WSL Ubuntu-22.04 root 下，从设备仓执行；复跑用 `--out` 指向同一 `out/` 下新目录，不覆盖候选：

```sh
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r25-census.py \
  --dtb /root/enuma-step10/inputs/enuma.dtb
```

最终构建 exit 0；基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241` 前后相同。`candidate-manifest.json` 保存逐项哈希和 `logs/` 反汇编。源插入点为生成副本 `kern_exec.c:2123`、`kern_exit.c:1904`。下表哈希皆 SHA-256。

| 文件 | r23 | r25 | r25 bytes / 增量 |
|---|---|---|---:|
| `kern_exec.o` | `304bc5c75a2045082b537db57e5b154631e8ea4a7a9610fd65827da4b70f3ff2` | `d30151db40eb073879e183d61bf1bcedad4511f6ccb6bdfe0a49095b0811f017` | 488600 / +7888 |
| `kern_exit.o` | `2481cac19e4b7919e3099db51059f8d0fca40bdcb16c3bbe417e04e333eea64d` | `5d835b92c8ad849908f5f4f7a849bc781108ecbd2ef0289c49a51e3052aa9f5e` | 232528 / −664 |
| `native.macho` | `306b71f131c9814ea97e5daac7055546f1fc03327d8647ad8bb7426d8fe1f1a9` | `5fc1703ac22fbb5ed18ab038c51a006bf9755ae7c156ca84f9b22908b3ab9855` | 91888992 / +720 |
| `prelink.macho` | `edbb9422c9ae53f486aa540482aaa5f9b0b2489cc7428abfbbcfc76543ca1062` | `3cd0ad54614733d85a0efb05b9b5ffeea728467406fdc2ae2cd4b736bbce6b7f` | 124731392 / 0 |
| `payload.img` | `72723451bd753ab40ad4ab999b68046addf7fbc8b495ff8be9da22ca2b8f3dba` | `ae5404269090e7aca54a02d77e214c6d641d764d27583c7c620b4daffc01665c` | 167772160 / 0 |
| `boot.img` | `f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b` | `bb08d2290e6937d70959a37e9de09cf7d3a9b970ec89fda4ee9e658679d23727` | 169951232 / 0 |

- 只替换上述两个 TU 对象；其余 1,004 条 filelist 路径与哈希一致，另检查同参数引用的直接对象/归档和强制加载归档，共 1,024 项复用输入构建前后哈希未变。r23 目录下 170 个文件构建前后哈希未变。prelink 组件/codeless 列表与 donor 原始可执行区哈希不变。
- 三条块格式加满表格式：`kern_exec.o`、native、prelink 内各出现 1 次，`kern_exit.o` 内 0 次；旧 `enuma-exec`/`enuma-exit` 格式均为 0。native、prelink 分别证实原 exec/exit hook 各 1 个 recorder 调用点；recorder 无 `printf`；exec recorder 有 1 个 allocate 和 1 个首排点；dump 有 4 个打印点、1 个再排点和 1 个释放点。prelink 指令有 `ldaxp/stlxp` 全名 CAS；native/prelink 均无未定义符号（含 weak）。原 watchdog 后的 HID stand-in 调用仍为 1。
- FAT 目录结构不变，五个封装成员仅 `Payloads/kernel.macho` 改变且同 r25 prelink。r23 的 `unixnu.toml` 与 `device/board.toml` 保留完整 HID、watchdog/lite、AMFI、显示参数；ADT 仍为 r23 注入字节（`memory-size=0xaa000000`、`sleep-disabled=1`）。

| FAT 内不变成员 | bytes | SHA-256 |
|---|---:|---|
| `Payloads/kernel.macho.adt` | 14088 | `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5` |
| `Payloads/scratch-data.img`（initrd） | 1142976 | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` |
| `Payloads/kernel.macho.trustcache` | 61356 | `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` |
| `unixnu.toml` | 804 | `272e2ed556a51d5706f60fcc5daa33c045fcd5d99f03d71cd1b88138d101afee` |

boot 内读回 payload（offset 2179072）哈希等于独立 payload，前缀仅 header ID 改变；FD 和 Android DTB 与 r23 pin 一致。基座目录内运行 `python3 -B scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`：exit 0，15 个区域。未执行设备命令，不访问 claim；回调实机节奏、屏幕留存、满表与实际计数未验证，最终构建未由独立 verifier 复跑。
