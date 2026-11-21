# enuma r13 — 控制台吞吐探针（2026-11-22）

`self-checked`，构建与打包完成，未部署。输出目录：
`out/ufs-sm8250-launchd-keystore-20261122-r13/`。

## 设计与判读

`bsd/kern/kern_exec.c:8286–8292`（r13 临时源）的 `load_init_program()` 挂载 Data 后、exec 前进入原路径探针；`enuma_path_probe()` 保留原子序号门，只在 `seq=0` 完成原有 12 条路径检查及文件系统报告后调用 `enuma_console_probe()`（`:8265`）。不改原门控、挂载或 exec 状态，不加 panic。

两组均用 `printf`，各自首个调用之前和最后一个调用返回时读一次 `mach_absolute_time()`，以 `absolutetime_to_nanoseconds()` 将 tick 差换算为 ns。摘要在各自计时区外；长组摘要先于短组，短组是已热路径对照，不单独分离启动开销。字符数含 LF，不含控制台层插入的字节或附加前缀。格式如下，长行的 `A` 恰为 61 个：

```text
enuma-con: %04u AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n
enuma-con: lines=20 chars=1560 ns=%llu ns_per_line=%llu ns_per_char=%llu\n
enuma-con: %04u B\n
enuma-con: lines=5 chars=90 ns=%llu\n
```

| 长组每行时间 | 判读 |
|---|---|
| >100 ms | 同步控制台成本足以成为可见吞吐的解释之一；须将总成本与 25 s 比较，不能仅据此归因整个间隔。 |
| <1 ms | 此处同步 `printf` 不是数量级匹配的瓶颈；转查 page-in、dyld、单核推进，并保留异步显示队列仍可限速的区别。 |
| 1–100 ms | 与短组的 `ns / 5` 及外部逐帧间隔对照；不归因。 |

主控转述 reviewer 判断：25 s 是日志可见间隔／吞吐，不是一次调用延迟。这个探针测调用者侧的 `printf` 成本（含调用时被抢占或等待），不测用户态日志队列到屏幕、异步刷新或 PID 1 进度本身。XNU 时基和墙钟的一致性仍需外部计时比对。

## 主机机械检查

- `UniXNU` HEAD `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；补丁 dry-run 及实贴成功，零 fuzz、零 offset。
- 第一次编译因临时目录缺少 `kern_exec_internal.h` 失败；现复制 r10 编译源的完整 `bsd/kern/`，保留相对包含关系。第二次 native/prelink 成功，但原 `llvm-objdump --macho --dis-symname` 只检索 `__TEXT,__text`，漏掉真正的 `__TEXT_EXEC,__text`；更正为 `llvm-objdump -d --disassemble-symbols` 后完成复建与审计。
- clang `-###` 实际展开的 cc1 `-I` **14/14 项逐项、顺序一致**，完整两列在 `self-check/build-final/cc1-includes.json`；为 `.`、`xnu-work/bsd`、`EXPORT_HDRS/{bsd,osfmk,libkern,iokit,pexpert,libsa,security,san}`、`xnu-work/EXTERNAL_HEADERS`、`fakeroot/usr/local/include/kernel`、`fakeroot/usr/local/include`、`fakeroot/.../Kernel.framework/Versions/A/PrivateHeaders/platform`。绝对前缀见 JSON；有一项 libsa 目录不存在警告，r11 与 r13 相同。
- r11 `kern_exec.o` 473984 B `d58fca68e970324f80b91ca8b4ba042073b1e521e69738617b47e68804ee5d29`；r13 477720 B `9d1941370d5cc240d771276f0a410b71f9ca8884e6db1eec8f7c6d76fb6afb9a`。其余 8 个保存的对象逐个相同；`kern_exec.o.i` 是宏表且也相同。另有 1022 个其他显式链接输入构建前后哈希相同并复用 r11 路径；该前后比较不独立证明这些外部路径从 r11 当时至今未变化。r11 的 AKS 归档与 12 路径源保留。
- 4 个 `enuma-con:` 格式串在对象、native、prelink 中各出现一次；native/prelink 各 1 个 probe 符号、`load_init_program` 中各 1 个调用点。编译器将两循环展开：probe 内各有 27 条 `printf`、4 条 `mach_absolute_time`、2 条 `absolutetime_to_nanoseconds` 调用指令；27 = 20 长行 + 摘要 + 5 短行 + 摘要。native/prelink 零 undefined（含 weak）；r11 keystore 相关符号均唯一。
- 固定 r6 ADT 在官方 FAT 生成**之前**由 wrapper 注入；FAT 回读 ADT 14048 B `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059`、initrd 1142976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`、trustcache 61356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` 均与 r11 相同。FAT 中 kernel 与新 prelink 一致；boot header 的 ramdisk 范围与整个 payload 逐字节相同。菜单、boot-args、FD、DTB 和 payload/boot 长度与 r11 相同。

| 产物 | bytes | SHA-256 |
|---|---:|---|
| native | 91858224 | `90284ff1e42686323932f917a50cca5403e450365dedbdb12c7400f0b1572e02` |
| prelink | 124702720 | `5f7df3bdf7111c44536e3d2eb3d89401541adfd4fb5b90bce992a7c6060dfd5a` |
| payload.img | 167772160 | `ee2d0aabf66ba1e8a769df03953da7bfad929fa88f39e49cde4f9cfabc4d4e66` |
| boot.img | 169951232 | `0fc6fd9536be414e420d4dedae48494e6ad10c257b7e824a4b7bcfb0a25e5ae4` |

相对 r11 native 增 112 B、prelink 同长度；payload/boot 同长度但哈希变化，除 kernel、payload、boot 外回读的 ADT、initrd、菜单不变。完整对照为 `delta-vs-r11.json`。历史 `candidate-manifest.json` 内 `delta_vs_r4/r5` 的旧字段沿用 r11，不是本轮的实际差异证据。

复跑：WSL root，空的新 r13 输出目录，`python3.11 -B scripts/build-enuma-r13-console-throughput.py kernel` 然后同脚本 `package`；`UniXNU` 目录执行 `python3.11 -B scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`。没有实机、独立 verifier 或 deep review 结果；时钟真实速率、异步输出瓶颈和控制台吞吐均尚未测得。
