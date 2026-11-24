# enuma 内核插桩审计 — 2026-11-24

状态：self-checked，源码级估计，未测耗时；未构建、未访问设备。基线为 r62 主机候选 `out/ufs-sm8250-smpobs-20261124-r62/link.filelist`，不是默认配方，也不是已运行内核。r62 沿用 r58 的 IPC、r47 的 VM/UBC、r43 的 IOUserClient，重编 r62 的 kern_exec 与 video_console。以下 `out/` 行号指这些本地产物源码；`package/` 指设备仓源码。r62 boot args 开启 bp，但关闭 fx-diag、th、txpeer、fb-fill；下列“禁用”指各自参数关闭，**不是从二进制移除**。

| 钩子 | 位置（文件:行） | 触发频率 | 禁用时开销 | 建议 | 理由 |
|---|---|---|---|---|---|
| ipc | `out/ufs-sm8250-launchd-ipc-20261123-r34/source/osfmk/ipc/mach_msg.c:668,767`; `package/EnumaIpc.inc:6-15` | 每次进入 trap send/receive helper；不是 mach_msg2_trap 入口，组合消息可两次 | 无开关：每 helper 调 current_proc、1 次 relaxed 原子加、进程名首字节读取，bb/sb 多一次原子加及可能 strcmp | 撤掉 | r44 已有 send/recv 结果；全局最热路径持续共享原子写 |
| txpeer | `out/ufs-sm8250-rxpid-20261123-r58/source/ipc_kmsg.c:5263-5269`; `package/EnumaTxPeer58.inc:29-53` | 每次走到 ipc_kmsg_send 指定位置 | 读 tunable + 分支、随后 sender 比较；**不调用 proc_selfpid**、不写 ring；原有 port lock 仍执行 | 可保留 | 关闭成本小；发送端/接收端快照仍可能有诊断价值 |
| fxd | `out/ufs-sm8250-fxdiag-20261123-r47/source/osfmk/vm/vm_fault.c:7755-7768,7808-7810`; 同目录 `bsd/kern/ubc_subr.c:6171,6219-6234`; `package/EnumaFixupDiag.inc:9-12` | 签名验证及 fixup 的各对应分支 | 每命中计数点读取 enabled + 分支；关闭时**不原子递增**，不是每一次 vm_fault 都命中这些点 | 可保留 | fixup 未命中仍待查，关闭时写零 |
| fx bitmap | `out/ufs-sm8250-fxdiag-20261123-r47/source/bsd/kern/ubc_subr.c:6241`; `package/EnumaFixupReport.inc:8-20` | 命中 fixup 条件时 | 无 fxd 门控；匹配记录后 relaxed/release 原子 OR 仍执行；报告时额外读取 | 保留 | 原始 fixup 命中仍未解；与 fxd 开关不同 |
| match M/N/O/P/I | `out/ufs-sm8250-matchcnt2-20261123-r43/source/iokit/Kernel/IOUserClient.cpp:2627,2709,2793,2881,3157,4382`; `package/EnumaMatchCount2.inc:20-47` | 各 IOKit matching/open 调用；M 有两个入口 | 无开关；每点 `proc_selfpid()`、固定 PID 比较，其他 PID 最多 28 次原子读及可能 CAS，最终 1 次原子加 | 撤掉 | 全局计数，即使 bp 关闭仍运行；旧数据仅为单次观察，不能宣称后续状态不变 |
| exec | `out/ufs-sm8250-smpobs-20261124-r62/source/bsd/kern/kern_exec.c:2125-2135,3565,4837-4840,5191,5448-5451`; `package/EnumaProcExecReport.inc:108-158` | 每次 exec/spawn 路径 | 无 bp 门控；成功 reached 时一次原子加；失败分类并持 spin lock 记录；初始化和调用仍在 | 可保留 | 频率低，失败证据有用；不能称零开销 |
| th | `out/ufs-sm8250-smpobs-20261124-r62/source/bsd/kern/EnumaBootProgress2.inc:30-55`; `package/EnumaThreadSnapshot56.c:157-163` | bp 第 2 轮才调度一次 | bp 关闭则不调用 alloc；bp 开且 th 关闭则只解析一次 boot arg，无线程扫描 | 可保留 | 需要时可按需取线程快照，非调用热路径 |
| bp / cpu / ps | `out/ufs-sm8250-smpobs-20261124-r62/source/bsd/kern/EnumaBootProgress2.inc:12-55`; `package/EnumaBootProgress62Cpu.inc:10-17`; `package/EnumaProcExecReport.inc:47-93` | backboardd 触发延迟报告；开启后初次及每 60 秒最多 10 次 | 一次参数解析后返回，无周期 worker；bp 开则有输出及进程扫描 | 保留 | r62 CPU 观测所需；bp 独立于底层计数开关 |
| fb-fill | `out/ufs-sm8250-smpobs-20261124-r62/source/osfmk/console/video_console.c:1250`; `package/EnumaFbFill54.inc:10-20` | 控制台启用时每个字符，已有控制台锁内 | r62 首次解析参数、设置 done；后续每字符读 done + 分支，不绘制；r61 旧对象每字符重复解析 | 撤掉 | 当前关闭但字符路径仍执行；无须为非像素实验付费 |
| sg | `package/EnumaStoreGeometry.inc:24-63`; `scripts/build-enuma-r40-storegeom.py:123-124` | 启动路径单次报告及几何准备时发布 | 无独立开关；一次 acquire 读取和打印，非 UFS 每 I/O；不新增 UFS I/O | 可保留 | 非热路径，保留几何可见性；不是 bp 子报告 |
| att / ctl / bb | `out/ufs-sm8250-matchcnt2-20261123-r43/source/iokit/Kernel/IOUserClient.cpp:4382-4410,4444-4447`; `out/ufs-sm8250-smpobs-20261124-r62/source/bsd/kern/EnumaBbScan.inc:48-74`; `package/EnumaAttempt.inc:15-43`, `package/EnumaControl.inc:11-40` | user client open 入口、拒绝及实际创建 | 无 bp 开关；att 做 current_proc 和 1–2 次原子加，部分名字表读/CAS；bb 先调用 ctl，ctl 做进程名表原子读/CAS/加，bb 仅 backboardd 多加/CAS | 撤掉 | 实际 open 路径仍累计，已有历史观测；影响低于全局 IPC |
| fb 计数 | `out/ufs-sm8250-smpobs-20261124-r62/source/bsd/kern/EnumaBbScan.inc:78-121,133-181` | start/open/refresh/kick/scanout/swap 的已插入调用点 | 不受 fb-fill/bp 参数控制；每次先原子读 finished，未完成还读取进程名、原子 store/add；完成后仍有读与分支 | 可保留 | GUI swap 尚未证明；不得与 fb-fill 混同 |
| rx | `out/ufs-sm8250-rx-20261123-r51/source/osfmk/ipc/mach_msg.c:937-944,1067`; `package/EnumaRx.inc:6-25` | 若链接 r51：每次 mach_msg2_trap 入/出 | 无开关；current_proc/PID 比较，PID 5/34 各入口和出口各一次原子加 | 本基线不适用 | r62 link.filelist 使用 **r34** mach_msg.o 而非 r51，不能把 r51 源码视为当前已链接 |
| path / PID1 observer | `out/ufs-sm8250-smpobs-20261124-r62/source/bsd/kern/kern_exec.c:8203-8297,8323-8327`; `out/ufs-sm8250-smpobs-20261124-r62/source/osfmk/console/video_console.c:1295-1365` | path 为编译期开关限定的启动探针；PID1 observer 为 PID1 相关事件 | path 禁用是否编进对象须核编译参数；PID1 是独立机制，不受 bp 控制 | 保留 | 非单纯 bp 报告；不能凭名称拆除，尚未完成事件频率核验 |

## 输出依赖与优先级

建议撤除顺序：ipc → match → fb-fill → att/ctl/bb；按源代码频率估计，未做性能实测。修复 hook 属启动链、驱动初始化或锁/并发改动时须按项目规则另行 deep review；本审计不是实施授权。

真实 r62 `EnumaBootProgress2.inc:22-28` 直接输出 `enuma-fbfill`，调用 `enuma_matchcnt_dump`（`enuma-mt: t/all/other/bb/sb/A/B`，A/B 依数据条件）、`enuma_fixup_report`（`enuma-fx: parsed/applied`、`bits`，fxd 开启时另两行 `enuma-fxd`）、`enuma_ps_dump`（`enuma-ps`）、`enuma_ex_dump`（`enuma-ex`），以及 CPU 两行。**上述建议仅直接减少 bp 中的 `enuma-mt` 和 `enuma-fbfill`；若保留兼容空报告则实际输出由实现决定。** `enuma-ipc` 四行与 `enuma-att`、`enuma-ctl`、`enuma-bb` 属 `EnumaBbScan.inc:145-176` 的另一组 framebuffer 定时报告，不是 bp 直接输出。th 的 `enuma-tx` 由 worker 调用（`scripts/build-enuma-r57-txpeer.py:162-172`），也不是 bp 同步输出。fx/fxd、ps/ex 和 cpu 在建议中保留。

范围限制：仅以 r62 链接清单与上述保留源码核对，未完成全二进制符号/全部归档驱动的穷举；历史候选与源码目录中同名但未链接的钩子不能自动算入 r62。未独立测量设备频率、锁竞争及实际输出；不能据此断言全部 `enuma_` 功能均已覆盖。
