# backboardd 入口离线反汇编（self-checked）

输入 `out/bb-offline-20261123/backboardd`，1,220,560 B，SHA-256
`6e362a46a2b46eb2741ecc6fcb50ffecb2fbc299641159045475361e62b34634`。
本地 Apple 文件未入库。无构建、无设备操作；入口来自已知 LC_MAIN `0x100022aac`。

复现（WSL LLVM 14）：

```sh
llvm-objdump -d --start-address=0x100022aac --stop-address=0x100024aac out/bb-offline-20261123/backboardd
llvm-objdump --macho --section-headers out/bb-offline-20261123/backboardd
llvm-objdump --macho --indirect-symbols out/bb-offline-20261123/backboardd
llvm-objdump -d --start-address=0x1000226ac --stop-address=0x1000227e0 out/bb-offline-20261123/backboardd
llvm-objdump -d --start-address=0x1000229e4 --stop-address=0x100022aac out/bb-offline-20261123/backboardd
```

不要信普通 `-d` 输出中 `<_xpc_dictionary_create+...>` 的虚假标签：用
`--indirect-symbols` 的地址映射。`__text` 为 `[0x100004744,0x10009681c)`；
`__stubs` 为 `[0x10009681c,0x100097d40)`，451 项，间接符号表直接映射；
`__objc_stubs` 为 `[0x100097d40,0x1000a6a20)`，是 Objective-C 消息派发
stub，不是普通本地函数，也不能从普通导入表直接推断被调方法。

## 前 40 个静态外部调用点

以下仅按入口函数内指令地址排列、只数普通 `__stubs` 的 `bl`，**不是**
前 40 次运行时调用：分支互斥、局部函数/Objective-C 调用及其内部调用均未展开。
列为 调用点 → stub 符号；stub 地址可由上面的 indirect-symbols 命令复现。

| # | 调用点 | 符号 |
|---:|---|---|
|1|0x100022afc|_kdebug_trace|
|2|0x100022b08|__set_user_dir_suffix|
|3|0x100022b0c|_pthread_set_fixedpriority_self|
|4|0x100022b18|_BKLogCommon|
|5|0x100022b1c|_objc_claimAutoreleasedReturnValue|
|6|0x100022b28|_os_log_type_enabled|
|7|0x100022b30|_objc_release_x21|
|8|0x100022b38|_pthread_self|
|9|0x100022b44|_pthread_get_qos_class_np|
|10|0x100022b54|_pthread_set_qos_class_self_np|
|11|0x100022b5c|_BKLogCommon|
|12|0x100022b60|_objc_claimAutoreleasedReturnValue|
|13|0x100022b6c|_os_log_type_enabled|
|14|0x100022b74|_objc_release_x21|
|15|0x100022b88|_setiopolicy_np|
|16|0x100022b90|_BKLogCommon|
|17|0x100022b94|_objc_claimAutoreleasedReturnValue|
|18|0x100022ba0|_os_log_type_enabled|
|19|0x100022ba8|_objc_release_x21|
|20|0x100022bac|_objc_autoreleasePoolPush|
|21|0x100022bbc|_objc_alloc|
|22|0x100022bd4|_objc_claimAutoreleasedReturnValue|
|23|0x100022bd8|_objc_retain|
|24|0x100022c00|_objc_msgSendSuper2|
|25|0x100022c0c|_BKLogCommon|
|26|0x100022c10|_objc_claimAutoreleasedReturnValue|
|27|0x100022c1c|_os_log_type_enabled|
|28|0x100022c58|__os_log_impl|
|29|0x100022c5c|_objc_release_x24|
|30|0x100022c60|_BSContinuousMachTimeNow|
|31|0x100022c68|_objc_release_x23|
|32|0x100022c6c|_objc_release_x23|
|33|0x100022cb0|_objc_retain_x22|
|34|0x100022cc4|_objc_claimAutoreleasedReturnValue|
|35|0x100022cd4|_objc_release_x23|
|36|0x100022d0c|_objc_claimAutoreleasedReturnValue|
|37|0x100022d28|_objc_claimAutoreleasedReturnValue|
|38|0x100022d48|_objc_retain_x24|
|39|0x100022d74|_objc_release_x8|
|40|0x100022d78|_objc_release_x23|

例如 0x100022b18 的日志分支取决于 0x100022b0c 返回值非零；
0x100022b54 在 0x100022b44 返回零时才到达，错误分支跳出表内顺序。
因此此表不能提供实际的首个 IOKit 次序。

## 控制流与阻塞证据

入口的多处 `bl 0x1000226ac` 调本地包装器：在
0x100022778/0x1000227a0 从 block 偏移 0x10 取函数并 `blr`，同步执行传入
block。调用点例如 0x100022c90、0x100022cac 等；不解析每个 block 及 Objective-C
动态分派就不能排除其中任一处先调用 IOKit、XPC 或同步等待。

0x100022fec 调 `_BSDispatchQueueCreateWithQualityOfService`，0x10002301c
调 `_dispatch_async`；其 block invoke 地址由 0x100022ffc 的 ADR 给出
`0x1000229e4`，再通过 0x100022a10/0x100022a38 调同一 block 包装器。
主线程随后在 0x100023150 起设置 CFRunLoop；0x100023284 调
`_CFRunLoopRunInMode`，按返回值循环（0x100023290），并非已证实调用
`dispatch_main`。这是**可静态观察的事件循环候选**，但不能证明设备抵达此处或
主线程实际正在此等待，更不能排除此前 block 或框架内同步阻塞。

线性窗口内 0x100023bf0、0x100023c04、0x100023c0c、0x100023c2c 分别是
`_xpc_connection_create_mach_service`、`_xpc_connection_set_event_handler`、
`_xpc_connection_activate`、`_xpc_connection_send_message`，但它们位于
入口函数结束后的其他函数，**线性相邻不证明入口可达**，也不是同步 reply 调用。
所检查入口函数直接调用中未见 `IOService*`、`xpc_connection_send_message_with_reply_sync`、
`dispatch_semaphore_wait`、`bootstrap_check_in`；不能将此扩展到被调函数或运行时。
IOService 首次调用的地址、序号和触发条件均未知。窗口内所有直接 `bl`/`b`
可通过上述限界命令和间接符号表逐条分类；`b` 指向 `__text` 可是函数内分支，
不能一概解释成调用。

对照父会话提供的 `send=25 recv=25` 及 IOKit 未命中：**无法判断**，计数对称不标识
调用栈、线程、消息配对或之后的状态；IOKit 采样覆盖范围也不能扩展为所有 API。
缺同一快照的线程 PC/栈，因此不能确定任何一个同步调用是实际阻塞点。
下一步唯一动作：解析 0x1000226ac 各入口调用传入的 block invoke 地址，按控制流追踪
至首个具体 IOKit 或等待点；包含 0x1000229e4 的异步 block。
