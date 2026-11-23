# r60 launchd 等待状态离线解析（2026-11-24）

状态：self-checked；输入是主控提供的 r60 单次快照及 slide `0x12374000`，未独立核读原始设备记录；本次不构建、不访问设备。下述地址映射假设这些进程实际使用该 slide 和既有 donor System 缓存；逐进程 slide 未在本次材料中独立确认。saved user state 与内核线程状态非原子采样，可能陈旧，见 `docs/pc-resolve-r56-20261123.md`。

## 输入

launchd 1/235 `TH_WAIT` PC `0x1ddaf9128` LR `0x1a1910ce0`；1/239 与 1/993 为 `TH_WAIT`，PC `0x1ddaf48e8` LR `0x1ef996580`；1/1071 `TH_WAIT`，PC/LR 不可用。amfid 26/302 PC/LR 与 1/235 完全相同。SpringBoard 5/242 与 backboardd 34/319 的 PC `0x1ddaf4b58`，LR `0x1ddaf8224`；5/451、34/454 的 PC/LR 与上述 workq 线程相同。后两进程状态本次输入未列出，不能补填。已知前者 PC 对应 `mach_msg2_trap+0x8`，后者对应 `__workq_kernreturn+0x8`。

## 地址解析

使用 `out/r56-dyld-cache-20261123/root/System/Library/Caches/com.apple.dyld/` 下 donor `dyld_shared_cache_arm64` 文件，主缓存 image 表和 mapping 参见 `docs/pc-resolve-r56-20261123.md`。文件偏移 = unslid 地址 − 对应子缓存 mapping 起点；符号偏移从符号入口计算。导出名为 Mach-O 原名，C 名省略 Mach-O 前导下划线。

| 输入 | 减 slide | 子缓存 / 文件偏移 | image | 符号 |
|---|---|---|---|---|
| PC `0x1ddaf9128` | `0x1cb785128` | `.23` / `0x3dc1128` | `/usr/lib/system/libsystem_kernel.dylib` | `__sigsuspend_nocancel+0x8`（导出 `___sigsuspend_nocancel`，入口 `0x1cb785120`） |
| LR `0x1a1910ce0` | `0x18f59cce0` | `.05` / `0x1b04ce0` | `/usr/lib/system/libdispatch.dylib` | 最近 local 符号 `__dispatch_sigsuspend+0x2c`（nlist 原名；入口 `0x18f59ccb4`） |

PC 符号来自该 image 的 `LC_DYLD_EXPORTS_TRIE`；LR 符号来自 `.symbols` local nlist，最近符号本身不单独证明函数边界。相应缓存指令：

```text
1cb785120 mov x16, #0x19a
1cb785124 svc #0x80
1cb785128 b.lo 0x1cb785144
...
18f59ccd8 mov x0, x19
18f59ccdc bl 0x194883c08
18f59cce0 b 0x18f59ccd8
```

PC 在系统调用后的返回点，不是用户态忙循环。LR 在 libdispatch 的循环调用返回点；该 `bl` 指向缓存 stub，未独立解析其间接绑定，不能仅凭 LR 断言直接调用关系。`out/owner-data-config-20261113-final/source-xnu/bsd/kern/syscalls.master:615` 的 410（`0x19a`）是 `sigsuspend_nocancel`；同树 `bsd/kern/kern_sig.c:868-887` 保存旧 signal mask、设置新 mask，并在进程地址上以 `"pause"`、`PCATCH` 进入 `tsleep0` 等待信号。

## 判读

这类等待是 **signal mask + 信号等待（sigsuspend）**，不是所列 semaphore、ulock、psynch 条件变量或 kevent；也不是 `mach_msg2_trap` 消息接收。`TH_WAIT` 与该 syscall 阻塞一致，但由于采样非原子，并不证明采样瞬间的内核等待栈。235 是给定的 launchd 主线程：其 saved PC/LR 支持 libdispatch 的 sigsuspend 信号等待路径，而非已证的锁等待或主线程直接 Mach 消息接收；不能据此证明它正在正常完成工作或永久停滞。

两个 workq 线程的位置与空闲 worker 停放相符，但未取得 syscall 参数及内核栈，不能当成实证；第四线程无寄存器，无法分类。四个 `TH_WAIT` 在某一时点均可见于正常空闲，也可见于等待永不发生的信号、事件或依赖；本次更像 signal wait 加 worker 停放的**空闲形态**，但缺少唤醒/进展证据，不能判定正常空闲而非卡住，也不能推定锁死。

launchd 与 amfid 相同 PC/LR 最自然的解释是各进程映射了相同 slide 的共享系统库并进入同一 libdispatch 信号等待路径，而非必须来自不同调用者；同一 wrapper 和同一调用点即可产生相同 PC/LR。代码地址不标识等待对象：`sigsuspend_nocancel` 使用当前进程 `p` 和当前线程 mask，两个不同进程的等待上下文各自独立；即使地址相同也不能说等待同一对象。上层调用栈、mask、待处理信号及 syscall 实际状态均未采集。

## 下一步

最优先查 launchd 235 的信号等待能否被预期事件唤醒并产生进展：最小证据是在同一启动中两个有时间间隔的采样，记录该线程内核 continuation/等待原因、signal mask 与 pending 信号，以及中间一次已知预期事件的投递和唤醒/进展；仅比较两次相同 PC 不足以证明死锁。任何新设备观察仍须另行授权。
