# r64 用户栈候选地址离线符号化

状态：self-checked；用户提供的 pid 5/34 栈字与 slide，未独立核对原始采样；未构建、未访问设备。

## 方法与边界

使用本地 `out/r56-dyld-cache-20261123/root/System/Library/Caches/com.apple.dyld/` 的 `dyld_shared_cache_arm64` 主缓存、`.03`、`.05`、`.23`、`.29`、`.52.dyldlinkedit` 和 `.symbols`。主缓存 UUID `9a830d59-82d2-30f1-a17d-0cc053420f73`；其符号文件 UUID 与主头符号 UUID 一致（`a259a8a1-9c47-9931-8a34-f4afbd808cf5`）。**缺 r64 运行时 cache UUID，使用该缓存是待证假设**；下述映射、符号和反汇编仅在缓存版本一致时适用于 r64。

每个地址减 `0x1dc18000`；查各子缓存 mapping 表，文件偏移为 `mapping.fileOffset + unslid - mapping.address`。镜像按主缓存 images 表和 Mach-O 头匹配；符号取 Mach-O 符号表和本镜像 `.symbols` local symbols 中最近地址，若同地址的 symtab 为 `<redacted>` 则展示 local 名称。偏移是**子缓存文件内偏移**，不是镜像内偏移。mapping 均为初始与最大权限 `r-x`，子缓存 `.03/.05/.23/.29` 的 mapping 起点分别为 `0x186dac000/0x18da98000/0x1c79c4000/0x1db614000`，文件起点均为零。

| pid | 运行时地址 | unslid | 子缓存 | 文件偏移 | 镜像 | 最近符号 + 偏移 |
|---|---|---|---|---|---|---|
| 5 | `0x1ad1bab58` | `0x18f5a2b58` | `.05` | `0x1b0ab58` | libdispatch | `__dispatch_event_loop_poke$VARIANT$armv81+0x98` |
| 5 | `0x1a5b5bd78` | `0x187f43d78` | `.03` | `0x1197d78` | CoreFoundation | `_CFMachPortIsValid+0x6c` |
| 5 | `0x1a5b5bc78` | `0x187f43c78` | `.03` | `0x1197c78` | CoreFoundation | `__CFMachPortCreateWithPort4+0x370` |
| 5 | `0x1a5bbf0d4` | `0x187fa70d4` | `.03` | `0x11fb0d4` | CoreFoundation | `____CFMachPortCreateWithPort4_block_invoke_2+0x0` |
| 5 | `0x1ad274cac` | `0x18f65ccac` | `.05` | `0x1bc4cac` | BackBoardServices | `__BKSDisplayGetMainScreenInfo+0xa4` |
| 5, 34 | `0x1e939c1b0` | `0x1cb7841b0` | `.23` | `0x3dc01b0` | libsystem_kernel | `_mach_msg_overwrite+0x1ec` |
| 5 | `0x1e939bfb8` | `0x1cb783fb8` | `.23` | `0x3dbffb8` | libsystem_kernel | `_mach_msg+0x14` |
| 34 | `0x1e939876c` | `0x1cb78076c` | `.23` | `0x3dbc76c` | libsystem_kernel | `_kdebug_trace+0x2c` |
| 34 | `0x1fb299edc` | `0x1dd681edc` | `.29` | `0x206dedc` | libxpc | `__xpc_serializer_pack+0x380` |
| 34 | `0x1fb2a37ec` | `0x1dd68b7ec` | `.29` | `0x20777ec` | libxpc | `__xpc_pipe_mach_msg+0x34` |
| 34 | `0x1fb2a2c9c` | `0x1dd68ac9c` | `.29` | `0x2076c9c` | libxpc | `__xpc_pipe_routine+0x184` |
| 34 | `0x1fb2994b8` | `0x1dd6814b8` | `.29` | `0x206d4b8` | libxpc | `____xpc_uncork_pid_domain_locked_block_invoke+0x0` |

## 指令与判断

Capstone 5.0.7 的关键 unslid 指令（地址为栈字本身或其前一条）：

```text
1cb7841ac  bl  0x1cb7841d8
1cb7841b0  ldp x29, x30, [sp, #0x110]
1cb783fb4  bl  0x1cb783fc4
1cb783fb8  ldp x29, x30, [sp, #0x10]
1dd68ac98  bl  0x1dd68b7b8
1dd68ac9c  mov x19, x0
1dd68b7e8  bl  0x1e21ed008
1dd68b7ec  mov x19, x0
187f43c74  bl  0x187f43d0c
187f43c78  cbnz w0, 0x187f43c9c
```

`0x1e939c1b0` 是 `mach_msg_overwrite` 返回地址附近，不是单独的等待函数或 syscall 指令；pid 5 同时含 `mach_msg+0x14`，符合 `mach_msg → mach_msg_overwrite`，但纯栈字不证明其为有效帧。pid 34 有 `xpc_pipe_routine → xpc_pipe_mach_msg` 的直接静态 BL（高置信度），并有共同的 `mach_msg_overwrite` 候选；将它们串成实际动态调用链、认定发送还是接收、同步等待回复均缺栈帧展开/参数（低置信度）。pid 5 有 `BKSDisplayGetMainScreenInfo`、CoreFoundation Mach port 及 dispatch event-loop poke 候选，不足以判断调用先后或事件循环空等。

候选中没有 `CFRunLoop*`、`__CFRunLoopServiceMachPort`、`__pthread_*`、`_pthread_cond_wait`、`semaphore_wait`，也没有所举 `xpc_connection_send_message_with_reply_sync` 或 `_dispatch_mach_msg_send`；并不排除它们出现在未列出栈字或寄存器中。`block_invoke+0` 可是函数指针而非返回地址；原始栈扫描不能替代帧链 unwind。不能以此断言两进程已经休眠、死锁、正常空闲或同一 RPC。
