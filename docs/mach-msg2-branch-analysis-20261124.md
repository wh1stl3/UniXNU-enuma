# mach_msg2 阻塞路径离线分析（2026-11-24）

状态：self-checked，纯离线反汇编；未构建、未访问设备。不能判定 backboardd 或 SpringBoard 的等待是 RPC reply 还是事件循环下一消息。

## 输入和地址

donor 为 iPad7,1 / 21H461；读取本地 `out/r56-dyld-cache-20261123/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.23`，按 `docs/pc-resolve-r56-20261123.md` 的缓存映射与 Mach-O export trie 定位 `/usr/lib/system/libsystem_kernel.dylib`。原文件偏移 `0x3dbcb50` 和 `0x3dc01d8`，使用 WSL Python capstone 5.0.7 ARM64 小端解码。未重新解析 export trie；符号归属复用上述历史解析。

| 导出符号 | unslid 起始 | r60 slide `0x12374000` 下 |
|---|---:|---:|
| `mach_msg2_trap` (`_mach_msg2_trap`) | `0x1cb780b50` | `0x1ddaf4b50` |
| `mach_msg2_internal` (`_mach_msg2_internal`) | `0x1cb7841d8` | `0x1ddaf81d8` |

给定 r60 PC `0x1ddaf4b58` 对应 trap `+0x8`；LR `0x1ddaf8224` 对应 internal `+0x4c`。r63 slide 未独立确定；其相对偏移须由各自 slide 或独立符号化确认，不能直接复用 r60 绝对地址。`we=0` 的 `IPC_MQUEUE_RECEIVE` 解释为已提供的先前分析，而非本次重新核验。

## trap 前 0x20 字节

```text
1cb780b50 mov  x16, #-0x2f
1cb780b54 svc  #0x80
1cb780b58 ret
1cb780b5c mov  x16, #-0x30
1cb780b60 svc  #0x80
1cb780b64 ret
1cb780b68 mov  x16, #-0x31
1cb780b6c svc  #0x80
```

`+0x8` 是 `svc` 之后的 `ret`；后续指令已属于其他 trap 入口。

## internal 完整指令

```text
1cb7841d8 stp x28, x27, [sp, #-0x60]!
1cb7841dc stp x26, x25, [sp, #0x10]
1cb7841e0 stp x24, x23, [sp, #0x20]
1cb7841e4 stp x22, x21, [sp, #0x30]
1cb7841e8 stp x20, x19, [sp, #0x40]
1cb7841ec stp x29, x30, [sp, #0x50]
1cb7841f0 add x29, sp, #0x50
1cb7841f4 mov x19, x7
1cb7841f8 mov x20, x6
1cb7841fc mov x21, x5
1cb784200 mov x22, x4
1cb784204 mov x23, x3
1cb784208 mov x25, x2
1cb78420c mov x26, x1
1cb784210 mov x24, x0
1cb784214 mov x8, #-0x441
1cb784218 and x27, x1, x8
1cb78421c mov x1, x27
1cb784220 bl 0x1cb780b50
1cb784224 cbz w0, 0x1cb7842c4
1cb784228 tbnz w26, #6, 0x1cb784264
1cb78422c mov w28, #7
1cb784230 movk w28, #0x1000, lsl #16
1cb784234 cmp w0, w28
1cb784238 b.ne 0x1cb784264
1cb78423c mov x0, x24
1cb784240 mov x1, x27
1cb784244 mov x2, x25
1cb784248 mov x3, x23
1cb78424c mov x4, x22
1cb784250 mov x5, x21
1cb784254 mov x6, x20
1cb784258 mov x7, x19
1cb78425c bl 0x1cb780b50
1cb784260 b 0x1cb784234
1cb784264 tbnz w26, #0xa, 0x1cb7842c4
1cb784268 mov w27, #0x4005
1cb78426c movk w27, #0x1000, lsl #16
1cb784270 cmp w0, w27
1cb784274 b.ne 0x1cb7842c4
1cb784278 mvn w8, w26
1cb78427c mov x9, #-0x4442
1cb784280 and x9, x26, x9
1cb784284 tst x8, #3
1cb784288 csel x8, x9, x26, eq
1cb78428c mov x9, #-0x442
1cb784290 and x26, x8, x9
1cb784294 and x25, x25, #0xffffffff
1cb784298 mov x0, x24
1cb78429c mov x1, x26
1cb7842a0 mov x2, x25
1cb7842a4 mov x3, x23
1cb7842a8 mov x4, x22
1cb7842ac mov x5, x21
1cb7842b0 mov x6, x20
1cb7842b4 mov x7, x19
1cb7842b8 bl 0x1cb780b50
1cb7842bc cmp w0, w27
1cb7842c0 b.eq 0x1cb784298
1cb7842c4 ldp x29, x30, [sp, #0x50]
1cb7842c8 ldp x20, x19, [sp, #0x40]
1cb7842cc ldp x22, x21, [sp, #0x30]
1cb7842d0 ldp x24, x23, [sp, #0x20]
1cb7842d4 ldp x26, x25, [sp, #0x10]
1cb7842d8 ldp x28, x27, [sp], #0x60
1cb7842dc ret
```

## 判读

`+0x4c` 是第一次 `bl mach_msg2_trap` 的返回点，不是一个专属 RPC 或事件循环的分支。调用前保留原始 `x1` 至 `x26`，`x27 = x1 & ~0x440` 并送回 `x1`：该掩码保留 `MACH_SEND_MSG=1` 与 `MACH_RCV_MSG=2` 两位，但它们的**实际值未知**。在这个入口至第一次 trap 之间没有另一次调用；这不说明调用者先前是否单独发送过请求。

trap 返回后先检查返回码 `w0`：为零则直接跳到恢复寄存器并 `ret`，不在此 wrapper 内检查 reply 内容；非零则按原 options 的 bit 6、bit 10 及返回码 `0x10000007` / `0x10004005` 决定返回或重试。`we=0` 仅支持当前正在 receive 等待，不排除同一 syscall 已发送，也不排除此前另一调用发送。

最小补充证据：取得该阻塞线程的用户态调用栈（包含 `mach_msg2_internal` 的调用者及更上层并符号化），确认具体调用语义；同时采集保存的原始 options（此路径 `x26` 或首次 trap 的 `x1`）和接收端口有助判断。仅 options 为 SEND+RCV 可支持同次调用先发后收，但仅 RCV 不能排除之前单独 send，因此 options 单独不足以严格区分两种目标语义。
