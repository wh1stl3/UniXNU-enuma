# Bootstrap 消息 ID 离线调查（2026-11-23）

状态：仅静态审查；未构建、未操作设备。主控提供的 r58 接收者 PID 为 1；这只确定采样时接收权持有人，不确定消息协议、处理完成或回复状态。r57 的 `out/ufs-sm8250-txpeer-20261123-r57/source/EnumaTxPeer57.inc:31-33,65-66` 确认采集的是 `hdr->msgh_id` 本身，并非 `msgh_bits`；不能把 `0x40000000` 当成 `msgh_bits` 标志去掉。

## 版本和完整例程表

本地 donor 构建树 XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f` 没有 `osfmk/mach/bootstrap.defs`；其 `osfmk/mach/bootstrap.h` 不能证明 launchd RPC 定义。公开 Apple launchd [launchd-842.92.1，commit 49a9c79b2949192dfca697b1054245cdfb645788，src/job.defs](https://github.com/apple-oss-distributions/launchd/blob/49a9c79b2949192dfca697b1054245cdfb645788/src/job.defs) 是历史参考，不是 iPadOS 17.7.11 的 donor 源码。该文件声明 `subsystem job 400`，而非 `subsystem bootstrap`。下表是该文件**全部槽位**，含 skip，序号从 0 开始；前缀 user `vproc_mig_`，server `job_mig_`。

| 序号 | routine 或保留槽 | 请求 ID |
|---:|---|---:|
|0|create_server|400|
|1|reboot2|401|
|2|check_in2|402|
|3|register2|403|
|4|look_up2|404|
|5|send_signal|405|
|6|parent|406|
|7|post_fork_ping|407|
|8|info|408|
|9|subset|409|
|10|skip（setup_shmem）|410|
|11|take_subset|411|
|12|getsocket|412|
|13|skip（spawn）|413|
|14|skip（wait）|414|
|15|skip（uncork_fork）|415|
|16|swap_integer|416|
|17|log|417|
|18|lookup_per_user_context|418|
|19|move_subset|419|
|20|swap_complex|420|
|21|log_drain|421|
|22|log_forward|422|
|23|kickstart|423|
|24|skip（embedded_wait）|424|
|25|lookup_children|425|
|26|switch_to_session|426|
|27|skip（transaction_count_for_pid）|427|
|28|pid_is_managed|428|
|29|port_for_label|429|
|30|init_session|430|
|31|set_security_session|431|
|32|skip（wait2）|432|
|33|skip（event_source_check_in）|433|
|34|skip（event_set_state）|434|
|35|spawn2|435|
|36|get_root_bootstrap|436|
|37|legacy_ipc_request|437|
|38|get_listener_port_rights|438|
|39|register_gui_session|439|

常规 MIG 请求 ID = subsystem base + 顺序槽号（skip 亦占槽）；历史定义对应 check_in2=402、register2=403、look_up2=404，而不是 0x400002c8 等。三个采样值分别为十进制 1073742536、1073742624、1073742628，均不在此表。即使假设高位可剥离，剩余 `0x2c8=712`、`0x320=800`、`0x324=804` 也不在该表。`712/800/804` 是数学候选，不是经证明的 MIG routine；不能凭数值邻近宣称 check-in/register/lookup。Mach 的 `msgh_id` 字段由协议解释而不是内核通用编码（本地 `osfmk/mach/message.h` 的字段说明）。现代私有 XPC/launchd 协议、其他接口、自定义 ID 均是候选；缺 donor 的生成代码/发送调用栈，不能确定高位含义或三个 API 的映射。

## 客户端与等待

历史 Apple [liblaunch/libbootstrap.c](https://github.com/apple-oss-distributions/launchd/blob/49a9c79b2949192dfca697b1054245cdfb645788/liblaunch/libbootstrap.c)：`bootstrap_check_in` 调 `vproc_mig_check_in2`，`bootstrap_register` 经 `bootstrap_register2` 调 `vproc_mig_register2`，`bootstrap_look_up2` 经 `bootstrap_look_up3` 调 `vproc_mig_look_up2`；此为 liblaunch 而非本地 libsyscall 的 donor 实现。该 `job.defs` 中三者均为 `routine`、含输出或返回值，不是 `simpleroutine`；按 MIG RPC 语义客户端需要回复，`look_up2` 明有 `sreplyport`。但未取得 donor 对应生成 stub 或实际 `MACH_SEND_MSG|MACH_RCV_MSG` 调用点，不能声称三个 donor 调用均经组合选项同步等待；也不能将一条发送记录与线程等待自动配对。

## 历史 launchd check-in 的执行与等待边界

以下均为 [Apple launchd 842.92.1 src/core.c](https://github.com/apple-oss-distributions/launchd/blob/49a9c79b2949192dfca697b1054245cdfb645788/src/core.c#L8877) 的**历史参考**，不是 donor 的栈或实现：

* `src/core.c:8877-8900` 按 job/名称查已有 service；`:8902-8911` strict 模式下非法、已激活、缺失时直接返回错误。
* `:8912-8923` 非 strict 且未找到时做 `sandbox_check`、`machservice_new`；创建 service 涉及内存和 Mach 端口操作。若其中调用实际阻塞，回复会被延迟，但本次无证据表明发生。
* `:8937-8951` 检查所有权及 active 状态，失败直接返回错误；`:8954-8960` 调 `job_checkin`、`machservice_request_notifications`、取端口并返回成功。所查函数体未显示在此路径同步读取 plist、等待另一个 job 启动或等待服务自己响应；不应声称这些是 check-in 的已证阻塞点。
* 还有请求尚未被 launchd 处理、调度或 RPC 回复路径卡住等可能；缺同次 launchd 线程栈、请求 payload、reply-port 与时间关联，不能把等待归因于上述某一步，也无法排序哪一步最可能。

下一步只读证据：核对目标 21H461 的 libxpc/libsystem 调用点与 launchd 接收分派表，关联同次发送和回复及 launchd 线程栈；在此之前三条具体映射及 launchd 卡点均未定。
