# enuma r45：单次进程表与 exec 结果报告

`self-checked`，仅主机；候选 `out/ufs-sm8250-ps-20261123-r45/`，
沿用 r44 `a27dd22`。不改 ADT、原 `enuma-mt:`/`enuma-fx:`、
定时、exec 结果或安全策略。生成源码行号均相对于候选 `source/bsd/kern/`。

## 进程表

`EnumaBbScan.inc:135–140` 的原单次分支在 IOKit 和 text-fixup
报告之后调用 census 与 exec 报告。构建树 `bsd/sys/proc_internal.h:965–970,1008–1016`
支持在 `proc_list_lock` 下用 `ALLPROC_FOREACH`。`EnumaProcExecReport.inc:47–74`
持锁遍历，只读取 PID（`kern_proc.c:1065` 的 `proc_getpid`）和结构内联的
`p_comm`（`proc_internal.h:395`）。固定缓冲 138 项，最大堆
保留最小的 138 个 PID；计入列表中每个节点，不跟随 task/vnode 指针，
不把 `proc_t` 带出锁。锁内不分配、不打印；解锁后按 PID 升序、每行
六项输出。名字截断到 16 字节，空名打印 `-`，分隔符/非打印字符转 `_`。
最多 1 表头 + 23 数据行 + 1 `+Nmore` 行。只有单次回调触碰缓冲，
不在进程创建、退出或调度热路径上采样。

`n` 是当时 `allproc` 节点数，不是 CPU 上运行数；可能包含 fork/exec
过渡条目。链表锁保护对象生命期，不把并发 exec 重命名变成原子快照。
不嵌套 proc 锁；持锁工作量为一次列表扫描、每次替换最多
`log2(138)` 级堆操作。实机锁延迟、屏幕物理折行及回调可达未验证。

| 快照对象 | 可读结论 |
| --- | --- |
| `launchd`、`SpringBoard`、`backboardd` | 用作启动/采样对照；存在不证明已完成初始化或能接收 IPC。 |
| `cfprefsd`、`securityd` | 应核对偏好与安全服务是否有存活进程；没见到不等于服务从未启动或就是等待目标。 |
| `runningboardd`、`launchservicesd`（以本机 comm 为准）、`distnoted` | 用来核对进程管理、LaunchServices 和分布式通知服务；可能按需启动、重启、曾退出或以其他 comm 出现。 |
| 任一项目缺失且有 `+Nmore` | 只排除它出现在低 PID 已显示部分；不能排除存在于截断部分。 |

r44 的 Mach IPC 发送和接收总数不能逐条配对；两者差 30 不证明
恰有 30 条请求未回复，也不识别等待的服务。

## exec 失败观测设计

原 `enuma-exec:` 位于 Mach-O 激活通过处，早于最终签名与策略检查。
它不打印失败，而且该行本身也不证明最终成功。`kern_exec.c:2135`
记录 `badtoolate` 的原始 reason（原返回码可能随后改为 0），`:2399`
在释放 lookup 数据前记录激活失败，`:9021` 在签名拒绝的 reason
交给信号路径前复制其 namespace/code。`:4837–4840`（`posix_spawn`）、
`:5448–5451`（`__mac_execve`）捕获其余 errno 并各提交一次结果。
每次调用使用私有、栈上的观测结构；首个失败胜出，后续 cleanup
不重复计数。内部 activator 表和签名函数只传递此观测指针；原调用
顺序、返回值、信号与 reason 所有权不变。不读用户态路径；只有
已拥有 basename 或已识别目标 `p_comm` 时才显示名字。

`EnumaProcExecReport.inc:142–164` 的成功计数是到达原激活通过点、且
没有命中已监测失败分支并走到汇合处的累计值；不是 syscall 返回 0
的数量，也不是成功进入 `main()` 的数量。失败计数、原因桶和最近三条
由独立 spin lock 维护，锁内仅更新数值/复制固定结构，报告取副本后解锁
再打印，与进程表锁不嵌套。最近三条按汇合提交顺序显示，最新在前。
失败原因在已捕获的范围内有效；未走到锚点或进程启动后退出不算这里的
exec 失败。缺名只显示原因。

| 缩写 | XNU 原始原因 |
| --- | --- |
| `sp` | `OS_REASON_EXEC / EXEC_EXIT_REASON_SECURITY_POLICY` (8) |
| `dyld` | `OS_REASON_EXEC / EXEC_EXIT_REASON_COPYOUT_DYNLINKER` (7) 或 `EXEC_EXIT_REASON_SET_DYLD_INFO` (17) |
| `noent` | 无结构化 reason 的 `ENOENT` |
| `perm` | 无结构化 reason 的 `EPERM` 或 `EACCES`，不能等同 `sp` |
| `oth` | 其余 `EXEC_EXIT_REASON_*`、其他 namespace 或 errno；`last` 保留原值 |

`last` 的 `tag/ns.code` 均为十进制 namespace/code；`ns=0` 时 code
是 errno。映射依据为构建树 `bsd/sys/reason.h:47–48,248–266`。
`EnumaBbScan.inc:139` 在四块都打印后 release 置位；
`kern_exec.c:2124–2130` 在 legacy 打印前 acquire 检查。`reached`
与该分支无关，`enuma_ex_finish` 继续累计后来的成功。
屏幕上的 `ok` 只是报告当时的值，不会反映将来的成功；旧 `enuma-exec`
行数只能作激活日志对照。已经通过检查的在途 legacy 日志，以及其他
内核或原有周期日志，不受该开关约束。

```c
"enuma-ps: n=%u\n"
"enuma-ps: %s\n"          /* 拼接格式 "%s%d:%s" */
"enuma-ps: +%umore\n"
"enuma-ex: ok=%u fail=%u\n"
"enuma-ex: %s\n"          /* 拼接格式 "%sr%s=%u" */
"enuma-ex: last %s\n"     /* 拼接格式 "%s%s%s%s/%u.%llu" */
```

最多 25 行 `ps` + 3 行 `ex` + 8 行原报告 = **36 个逻辑行**。

## 机械证据

WSL root：`PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r42-matchcnt.py --r45`
exit 0；独立复跑加 `--out out/ufs-sm8250-ps-20261123-r45-verify`。
只替换 `kern_exec.o`；其余 1005 个 filelist 条目、15 个直链归档、
prelink donor 及 r44 冻结文件哈希不变。两张 Mach-O 中六个新增格式
各唯一，两个 dump 在同一单次分支各调用一次，两个 syscall 各一个
提交点；反汇编显示列表锁的取得和解锁块在 printf 之前。两张图
通过 `llvm-nm -u` 和原始 nlist 检查（含 weak）。完整哈希/调用证据在
`candidate-manifest.json` 及 `logs/calls-*.macho.log`。
FAT 只改变 kernel；外置与 FAT 里的 ADT 逐字节同 r44。两份 boot 的
ramdisk 各等于其 FAT，ramdisk 之前只有镜像 ID 改变。

| 文件 | r44 SHA-256 | r45 SHA-256 | r45 字节 / Δ |
| --- | --- | --- | ---: |
| `kern_exec.o` | `92298b1105b52e3c463a7f5cef885d5ebee33134c2cbc9666e6ea9acfff86c0a` | `e72d8acb03c6f2b77ac3d23254efd0d70bbefd7ef5e2e84b00d530afde029f7a` | 559240 / +20824 |
| `native.macho` | `00ecb1a2ff72fed7b8a25d7739d185bfbf366b81b99a686f449dd88097c097da` | `b8002c317cb968999e3840ca2be2e5d302b9ec0b2b775162f30f870bd5c28dd4` | 91911608 / +1848 |
| `prelink.macho` | `98f16cda0a77fdec183f4f5c3618e6e4f7c00c8ca2af73a8768d158d720737a9` | `cd8cfa207cdabc4c6a4ca7568523035c8d2228e1a36105cea71e63a11dad9735` | 124755968 / +4096 |
| `kernel.macho.adt` | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | 同 r44 | 14128 / 0 |
| `payload.img` | `caab11ce6726170ed35106124175db4ab743d13ab94111f41fdd816e4e7a8f6b` | `8bb0a8f1b9e9b96f6d646775ad352a9c79fb0f1b55bc7450a7d61985dbb8c9e0` | 167772160 / 0 |
| `boot.img` | `b997b33af1d85f67da89cf5b3817f53ef5545a41605b856882288bb322601b4e` | `d0e02c1c2ddfcc09f7c922e98b60ae246b6a571fb8c87c8a8403af769b2c34fd` | 169951232 / 0 |

UBSan smoke 用真实片段及模拟锁：300 个乱序 PID 保留 0–137、余
162，锁内打印断言未触发；另覆盖原因桶、一次结果、最近三条和置位后计数。
未上机；没有实机进程缺失或拒绝结论，尚未独立 verifier/deep review。
