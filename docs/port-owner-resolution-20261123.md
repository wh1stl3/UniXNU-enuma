# r57 Mach 端口接收者解析（2026-11-23）

状态：仅静态审查；未构建、未上机。r57 观测由主控提供：SpringBoard(5) 和 backboardd(34) 发往同一地址 `0xfffffff3bda9d380`，消息 ID 为 `0x400002c8`、`0x40000320`、`0x40000324`，两者在 `mach_msg2_trap` 接收等待。地址相等不证明同一生存期内的同一对象，亦不证明哪个进程应答、服务名或卡住的根因。

源码基准：本机 enuma 构建树 `UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree/.cache/xnu-work`，git HEAD `d8b80295118ef25ac3a784134bcf95cd8e88109f`；以下行号相对此树。r57 隔离源码为设备仓 ignored `out/ufs-sm8250-txpeer-20261123-r57/source/EnumaTxPeer57.inc`，当前环只保存整数端口地址，不持引用。

## 1. 字段与服务端口

* `osfmk/ipc/ipc_port.h:119-173`：`ip_receiver` / `ip_destination` / `ip_timestamp` 是同一 union；`ip_kobject` 又与 importance/sync inheritor 字段共用 union，且指针手动 PAC，不能把普通端口的原始 union 当 kobject。
* `ipc_port.h:468-493,526-551`：活动端口且 receiver name 非空才处于一个 space，union 为接收权所在的 `ip_receiver`；活动但 name 为空则为 `ip_destination`，NULL 表示 limbo，非 NULL 表示传输途中并引用目标端口；非活动时不能按上述解释。`osfmk/ipc/ipc_space.h:129` 的 `is_task` 为关联 task。
* 普通用户态 launchd 注册服务不是必然的 task kobject。接收权在 launchd 时 receiver 为 launchd 的 space；check-in/转移给服务进程后为服务进程的 space；转移中为 limbo/transit；服务死亡或重新登记时状态也可变化。以上是一般状态模型，不是对 r57 端口实际类型或服务归属的断言。`ip_destination` 不是接收者进程指针，`ip_kobject` 也不保证为 NULL（union 可能另有用途）。

## 2. 两条路径与锁

* A：只有确认活动及匹配 kobject type 后才能用正规 accessor 解码；`osfmk/kern/ipc_tt.c:2551-2579,2601-2627` 展示 task port 类型检查、持 `ip_mq_lock` 的 `ipc_kobject_get_locked`，以及跨锁使用 task 时获取引用。`IKOT_PSET` 转换为 processor set 而不是 task（`osfmk/kern/ipc_host.c:319-330`），不能强转成 task；task port 指向的是被表示的 task，不等于任意服务的接收者。普通服务端口因此不能依赖 A。不能裸读 PAC 字段或将 `bsd_info`/`p_comm` 当作受端口引用保护；proc 生命周期和名称读取还需各自契约。
* B：源码已有准确实现：`osfmk/ipc/ipc_port.c:2478-2534` 的 `ipc_port_get_receiver_task_locked` 在已持端口锁时检查 `ip_in_a_space` 并排除 kernel/reply space，读取 `is_task`，直接以 `task_pid()` 取 PID；其无锁包装器自己取得 `ip_mq_lock`。`osfmk/kern/task.c:7787-7794` 表明 `task_pid` 读 task audit token，不要求调用者另取 `task_lock`。此 helper 返回的 task 指针是未附带引用的快照，解锁后不可解引用；只保存整数 PID。PID 是采样时接收权持有者，不一定是服务最终处理者；PID 可重用，不能单靠稍后的 PID→名字查询证明身份。
* 端口引用仅确保端口对象不被释放，不能保证 active、receiver 不变或 task/proc 指针解锁后有效。锁内 PID 快照可遵循上述 helper；若要跨锁拿 task/proc 或可靠名称，需要额外有证据的引用和锁顺序设计，不在此方案中。`ip_mq_lock` 是本版端口对象锁的实际名称（`ipc_port.h:300-304`），不是额外再加一把 `ip_lock`。

## 3. 采集点和 UAF

`ipc_kmsg_send` 是热路径，但已有锁：`osfmk/ipc/ipc_kmsg.c:5262-5264,5291-5315` 在取出 destination 后持 `ip_mq_lock` 并检查 active。若后续另行授权实现，优先在该已有锁区间、且 active 检查成功后，针对两个 PID 和目标 ID 做有界整数快照，调用 `_locked` 版本；不能调用会再次加同一锁的包装器。不得在锁内打印、睡眠或查进程名；保存 PID 与端口 token 的同一个采样记录，异步打印。注意这会改动 IPC 锁区间的工作量，必须审查具体 hook、发布一致性、重入和时序，不能仅凭本说明部署。

报告 `thread_call` 可睡眠并适合格式化，但现有 r57 ring 中的地址是无引用整数，可能释放或复用，绝不能在 worker 强转解引用；也不能根据旧地址事后补引用。若选择报告时解析，必须在发送时对象仍有合法引用的范围内获取端口引用，再以有界且并发安全的所有权协议交给 worker，并在覆盖、丢弃、禁用和结束路径各恰好释放一次；锁定后仍要重新检查 active。它改变对象生存期，且得到的是报告时接收者，未必是发送时接收者；现有无锁环的覆盖竞争使此方案显著复杂，不推荐。

## 4. 建议

优先复用发送路径已有 `ip_mq_lock`，调用 `ipc_port_get_receiver_task_locked(port, NULL)` 采样 PID，与 ID、port token 原子一致发布；worker 只读取数值。最小新增锁集合为空，依赖原已有的一把端口锁；不取 task lock，不持有跨回调引用。检查 inactive、kernel/reply、limbo/transit、无 task 或 helper 返回负值时输出 `owner=NA`，不得从 NA 推断服务不存在；时间标记语义为“发送时接收权持有人快照”，并保留 port token 与 ID。进程名先不采集，防止 PID 复用错误归名。须确认最终源码中 hook 确实在正确锁区间、调用/链接可用、过滤与记录不会引入递归；失败则不部署。估计隔离候选约 30–80 行及配套测试，属高风险：IPC 热路径、锁和并发代码；需要明确实现 brief 与 `deep_reviewer`，本次不实施。

## 5. 替代

若不接受 IPC 热路径改动，保留 r57 已有 ID 和地址的纯数值记录，离线反查已公开 MIG `.defs` / 生成表中的 ID，并核对目标系统版本；ID 空间可重叠或为私有接口，不能单靠 ID 断言服务名。普通端口的 `ip_kobject` 是 union 且可能 PAC，不建议盲采其原始值代替身份；现有 port token 只能作同次、同生存期限定的相关性线索。r57 的阻塞发生在接收阶段，不能仅据此确定发送失败或目标进程身份。
