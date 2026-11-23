# r56 wait-event 语义与归属探针（2026-11-23）

状态：仅静态审查；未构建、未操作设备。r56 输入及 PC 解析见 `docs/pc-resolve-r56-20261123.md`。以下 XNU 行号对应 `/home/wh1stl3/unixnu-build/.cache/xnu-work` 当前 HEAD `1b191cb58250d0705d8a51287127505aa4bc0789` 的工作树；未核对其与 r56 实际编译输入逐字节相同。PC 是保存的用户态状态，不是当前内核栈；`package/EnumaThreadSnapshot56.c:33-52,82-96` 的 state/event 在 thread lock 下读取，saved PC 是独立 relaxed 读取，不保证与之同步。

## 1. 事件键不是队列指针

`osfmk/kern/thread.h:326-329` 将 `wait_event` 声明为 `event64_t`，与 `waitq` 分开保存；`osfmk/kern/kern_types.h:65-81` 定义 `event64_t` 为 `uint64_t`，事件用于在指定 waitq 上选择唤醒对象，习惯使用相关内存地址作为唯一键。`osfmk/kern/waitq.c:568-570` 分别写入事件和真实 waitq；`:1007` 按 waitq 和事件匹配。因此 KVA 形状的事件键不一定指向 waitq，不能推定它通常是 waitq 首地址：也可以是结构内部字段地址或其他标识。

例如 `osfmk/kern/sched_prim.c:1176-1190` 的 `assert_wait(event, ...)` 按事件哈希选择 global waitq，事件本身另存；`osfmk/kern/waitq.c:386-390` 实现哈希。`waitq.c:585-593` 在唤醒过渡时也清零 event 和 waitq，故零值单独不能判别具体路径。

## 2. Mach receive 的零事件是正常队列事件

`osfmk/ipc/mach_msg.c:898-902,924-932` 对 receive name 拿到 object 引用，将 object 存入线程，再以 `ipc_mqueue_receive(io_waitq(object), ...)` 等待。`osfmk/ipc/ipc_mqueue.c:880-894,1044-1051` 最终调用：

```c
waitq_assert_wait64_locked(waitq, IPC_MQUEUE_RECEIVE,
    interruptible, TIMEOUT_URGENCY_USER_NORMAL, deadline,
    TIMEOUT_NO_LEEWAY, thread);
```

`osfmk/ipc/ipc_mqueue.h:132` 定义 `IPC_MQUEUE_RECEIVE` 为 `NO_EVENT64`，即零；`osfmk/kern/waitq.c:1325-1333` 明确 port/port-set 类型使用零事件。等待成功后可带 `ipc_mqueue_receive_continue` 调用 `thread_block`（`ipc_mqueue.c:889-894`）：continuation 与等待队列并不互斥。故 A 的 `we=0` 完全符合 port 或 port set 的队列等待，不说明“无事件 block”；仅凭用户态 trap PC、零事件和等待状态仍不能证明当前实际走了该 receive 路径，也不能排除快照不一致或其他等待路径。

## 3. workq 的非零事件

`bsd/pthread/pthread_workqueue.c:3416,3428,3502-3505` 的 `workq_kernreturn` 有多个选项；thread-return 分支进入 `workq_thread_return`，后者在 `:3404-3407` 选择请求或 park。park 路径在 `:3662-3668` 对 `workq_parked_wait_event(uth)` 执行 `assert_wait`，再 `thread_block(workq_unpark_continue)`。`:284-287` 精确返回 `(event_t)&uth->uu_workq_stackaddr`：这是**该线程的 uthread 字段地址**，不是 `struct workqueue` 首地址，也不是 ipc mqueue；它作为事件键并经 global waitq 等待。

因此两条 B 的用户态 workq stub PC 加非零 KVA 与 parked worker 高度一致，比 Mach receive 更符合该源码；先前若将 B 判为正在等 Mach 消息，应撤回此断言。但 PC 可能滞后，syscall option、真实内核 continuation、uth 地址及事件相等性均未观测，不能仅凭 PC 和 KVA 排除其他等待。

## 4. 两进程的解释与成立条件

两个非零地址可以都是各线程各自的 `uth->uu_workq_stackaddr`，不是两个进程共享同一对象的证据。若分别确认实际内核路径是上述 park、事件等于各自 uthread 字段地址，且 state/事件/对象快照有效，则两条 B 都是当时停放的空闲 workqueue 线程。若同时确认 A 各自位于 Mach receive 且 waitq 指向有效 port/port set，则每进程有一条消息接收等待线程和一条空闲停放线程；B 仍然在等待调度事件，不能说“只有 A 在等待”，只能说“只有 A 被确认在等消息”。记录中的每进程线程数为两条时，这个结论仅覆盖采样时点，不证明永久空闲、系统死锁或 GUI 状态。

## 5. 反解可行性及最小方案

* 最小先做**分类而非从任意 KVA 反向解引用**：沿用 r56 已引用 task 和 thread 的采集框架（`package/EnumaThreadSnapshot56.c:59-96`），在已验证的同步与生命周期契约下采集同一线程的 state、`wait_event`、`waitq`、block hint 和可证明安全的 continuation；比较已持有线程关联的 uthread 字段地址与 event，只比较地址，不从 event 反推并读取任意地址。当前输出本身已关联等待线程的 pid，非事件对象的拥有者。
* IPC 只在证实 port receive 类型及对象生命周期后处理：`mach_msg.c:898-902,924-932` 的正常路径持有 `ith_object` 引用；`:939-940` 显示结果路径释放。不能因采样时读到原始 `ith_object` 或 `waitq` 就假定引用仍有效，更不能仅按旧 PC 转换。`osfmk/ipc/ipc_object.h:194-200` 有 waitq/object 转换，`ipc_port.h:318`、`ipc_pset.h:86-92` 分别有 port/pset 转换，前提是**已验证类型与存活并遵守锁序/引用契约**。记录 port 还是 port set 及 receive name；port set 不等于单一端口，尚无消息时也不能指定最终发送者。
* 如目标是对象的接收方而非等待者 pid，必须在持引用、正确锁和 IPC space 生命周期规则下读取 port 的 receiver space/receiver name，并通过受支持的 task/proc 引用链取得 pid；发送端/服务端不能从 receive wait 单独推定，port set 也无唯一成员。具体锁序、对象访问和归属映射须在设计探针前逐项核实，不能直接追逐裸指针或在 scheduler 锁下打印、取可能阻塞的锁。
* 风险：采样与唤醒竞态、锁序反转、对象释放或复用、saved user PC 过期、地址暴露及 probe 对调度的扰动。先限量复制已安全取得的数据、解锁后输出；取不到一致快照就标 unknown。该方案只是设计建议，涉及锁/并发及可能的启动诊断接入，实施须明确授权及 deep_reviewer 审查；本轮没有实现或验证探针。
