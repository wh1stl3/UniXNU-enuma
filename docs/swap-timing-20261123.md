# r39 swap open 与 Data 挂载的时序

状态：self-checked，静态分析；无构建、无设备访问。r39 的错误为主控转录，未附调用栈、路径或挂载表。下述 XNU 行号指本地主机 `UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/tree/.cache/xnu-work/`（工作树 HEAD `d8b80295118ef25ac3a784134bcf95cd8e88109f`），并非 r39 最终对象的源码映射证明；r39 复用 r34 `kern_exec.o` 的限制见 `docs/data-mount-flags-20261123.md:26-29`。

## 1. 谁打开 swap 文件

`osfmk/kern/startup.c:571,600,814,839`：`kernel_bootstrap_thread` 先调用 `bsd_init()`，返回后自身转为 `vm_pageout()`；`osfmk/vm/vm_pageout.c:5285-5287` 在 compressor present 时调用 `vm_compressor_init`，后者在 swap present 时调用 `vm_compressor_swap_init`（`osfmk/vm/vm_compressor.c:1201-1212`）。该初始化创建独立内核线程 `VM_swapfile_create`，并非 bootstrap 线程直接建文件（`osfmk/vm/vm_compressor_backing_store.c:464-498`）。

创建线程首次运行即检查，而不是必须等用户态 dynamic pager：`:765-831` 在未 hibernate/停止 compaction、文件数低于上限、空余 segment 低于高水位、距上次失败超过延迟（`:162-163`；非 macOS 分支）时调用 `vm_swap_create_file`。该函数 `:1491-1507,1527-1545` 构造前缀加数字并调用 `vm_swapfile_open`。另外，`vm_compaction_swapper_do_init` 在 compressor-with-swap 模式下本身也会直接打开 `swapfile0`（`:546-570`）；它可由创建函数调用，也可由 compressor 的 compaction 路径调用（`osfmk/vm/vm_compressor.c:3464`）。所以单行日志不能区分两条调用路径。`bsd/vm/vm_compressor_backing_file.c:59-67` 打印的是 `vnode_open` 错误；30 为 `EROFS`（`bsd/sys/errno.h:122`）。默认非 macOS 前缀和可写 sysctl 见 `docs/data-mount-flags-20261123.md:61-70`。

## 2–3. Data、IOKit 与 swap 的偏序

`startup.c:695-696,814,839` 先 `PE_init_iokit`，再 `bsd_init`，返回后进入 pageout；`iokit/Kernel/IOStartIOKit.cpp:93-104` 的 IOKit 构造后初始化包括 `IOService::initialize`。`bsd/kern/bsd_init.c:1195-1196,1349-1358,1377-1384` 在 `bsd_init` 中创建并释放 PID 1 的任务等待；PID 1 的 `bsdinit_task` 调用 `load_init_program`（`:1250-1276`，`bsd/kern/kern_sig.c:3412`）。`UniXNU/patches/xnu/offline-owner-systemos-mount.patch:201,236-257,282-290` 在启用相关宏时于 load-init 内先将 Data 挂至 `/private/var`，校验设备、APFS 及非 `MNT_RDONLY`，失败则 panic。

关键是 PID 1 和 bootstrap/pageout 是**不同线程**：创建 PID 1 之后，Data 挂载与 `bsd_init` 的尾部和其后 swap 线程启动没有这里可见的完成等待关系。Data 可以先完成，swap open 也可以先发生；仅凭源代码不能确定 r39 那一次失败的先后，更不能认定该路径当时必然落在 union 根。PID 1 真正进入 launchd 则在 Data prepare 返回之后，条件是该宏在 r39 实际对象启用且未走异常路径；这些运行时及对象身份尚未证实。内核的 IOService 初始化早于上述两条路径，不等于所有异步服务均已启动完成。

## 4–5. 判别与可能修法

时序假设为可行竞态，**尚未成立也未被排除**。需要同一次失败的 open 时刻、完整路径、调用方、路径解析结果及其 mount/device/flags，与 Data mount 成功时刻和校验结果作对照；仅比较后来的 mount 表不足以证明失败时状态。也需核对 r39 对象和编译宏。若 open 早于 Data 且落只读层，才有依据选择在 Data 成功后唤醒或允许全部相关 swap open 的门控；仅延迟创建线程不覆盖 `vm_compaction_swapper_do_init` 的直接 open。门控要处理失败及唤醒、启动期间内存压力和并发，属启动链/并发改动，需专项审查；整体推迟 swap 初始化影响 pageout 的初始化契约。临时更改 `vm.swapfileprefix` 需要在首次 open 前已有合适的可写且支持 swap 的位置，并处理后续文件生命周期，单独改变前缀不保证修复。

其他候选：有效前缀不是默认值；`/private/var` 被其他挂载或 union 路径遮蔽；Data 后续变为只读；APFS 或下层对该操作返回 EROFS。用失败瞬间的路径、每层 mount/device 与 flags 和文件系统返回点区分；挂载参数为 0、当时的非只读检查只是设计，不证明 r39 失败时实际可写。缺失 `vm` 目录通常是 ENOENT，不能单独解释 EROFS（同前文档 :31-37,48-59）。服务起来却无动作与 swap 失败之间没有依赖链或压力证据，不能归因。
