# r58 Mach 发送端接收者 PID — 2026-11-23

r58 是 r57 的隔离主机候选；保留 `enuma-txpeer=1` 和 `enuma-th=1`，不改默认配方。PID 指采样时目的端口的接收权持有者，不是消息交付结果或服务名。

## 采集与发布

- `source/ipc_kmsg.c:5265–5268` 的 `ipc_kmsg_send()` 在原有 `ip_mq_lock(port)` 之前识别发送者 PID 5/34，锁之后在 `retry:` 标签之前调用 `enuma_tx_record()` 一次。记录函数（`package/EnumaTxPeer58.inc:37–38`）检查 `ip_active(port)`；只有活动目的端口才调用 `ipc_port_get_receiver_task_locked(port, NULL)`，非活动端口仍保留 ID/端口 token，接收者标记 `NA`。这保留 r57 的发送尝试范围，包括随后被拒绝的尝试；不重复记录 importance retry 或本次调用内部生成的 kernel reply。
- helper 签名为 `pid_t ipc_port_get_receiver_task_locked(ipc_port_t port, uintptr_t *task)`（`osfmk/ipc/ipc_port.c:2486–2507`）。它要求这同一把端口锁：无锁包装器也正是用 `ip_mq_lock(port)`（`:2530–2532`）；`ipc_port.h:301–302,490–500` 表明此锁保护 receiver 状态和访问。helper 排除不在 space 内、kernel space 和 reply space；`task_pid()` 读 task audit token（`osfmk/kern/task.c:7631–7635,7787–7794`；`bsd/kern/kern_prot.c:1718–1724`），不另取锁。传 `NULL`，不请求 task 地址。复用 UniXNU 补丁树 XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f`（APSL 2.0），不原地编辑。
- 每个发送 PID 保留 8 槽；128 位无锁槽一次原子发布 32 位票、32 位消息 ID、44 位端口低位和 20 位 receiver PID。端口高位从目标内核 VA 窗口的固定前缀恢复；编译检查该窗口不跨前缀，运行时不匹配则丢槽而不是截断。PID 字段的零编码 `-1`/`NA`；本树 `PID_MAX=99999`（`bsd/sys/proc_internal.h:758`）可无损编码。
- 发布只按首次读到的槽值做一次 compare-exchange，不对变化后的值重新尝试；ARM64 编译结果的独占指令在 store-exclusive 失败时仍会重试，不是 wait-free。读者核验低 32 位票，不匹配则全部打印 `NA`。沿用 r57 的票序约束：比较的同槽票相差小于半个 32 位票空间。发送路径不打印、不分配、不取进程名、不修改端口和原有返回路径。原 r57 报告 worker 只读取整数并格式化，报告不是两个环和进程列表的原子快照。

## 交叉查表

从 `enuma-tx` 行取十进制 `rxpid`，不取行首的发送 PID；在**同一次启动、同一次报告**的 `enuma-ps:` 行里找精确的 `<pid>:<comm>`。例如 `rxpid=77` 和 `77:someprocess` 得到「PID 77 在进程列表快照中名为 `someprocess`」。记录相符条目和报告位置。若列表缺失、截断（`+Nmore`）或没有该 PID，同一次启动中较早的 `enuma-exec: pid=77 comm=…` 可作候选线索；若有多次 exec、名称冲突或 PID 重用迹象，不强行归名。若只在历史**其他启动**见到同 PID 的 `enuma-exec`，只列候选，不能作为本次进程身份。`comm` 是短进程名，不能据此当作 launchd service label。

| 观察 | 判读 |
| --- | --- |
| 数字 `rxpid`，同报 `enuma-ps` 命中 | 发送时接收权持有者的 PID；该 PID 在报告进程快照中的名称。跨采样间隔仍可能发生 exec、退出、PID 重用。 |
| 数字 `rxpid`，无同报名称 | 保留数字；不证明进程不存在。 |
| 有 ID 和端口，`rxpid=NA` | 该次未取得用户态 PID：非活动、limbo/transit、kernel/reply space、无 task 或 helper 未返回可表示的正 PID。 |
| ID、端口、`rxpid` 均为 `NA` | 票不符或空槽：未完成/争用丢弃/覆盖或 token 不可表示；不能用于归因。 |
| 两发送者的 ID/port/rxpid 相同 | 可关联同次启动观察，不能证明同一个端口生存期、已经投递/应答或造成当前等待。 |

新增工作会延长该诊断选项下目标发送的持锁时间；保留八槽及原报告调度，争用可丢槽。实机时序、PID/端口样本、实际控制台显示和关闭选项后的运行行为未验证；实机前需 `deep_reviewer` 审查实际锁区间和并发发布。

## 主机证据（self-checked）

产物：`out/ufs-sm8250-rxpid-20261123-r58/`；详细机械证据为 `candidate-manifest.json`、`commands.json`、`logs/`。UniXNU HEAD 构建前后同为 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。下表字节差相对于 r57：

| 产物 | 字节数 | 字节差 | SHA-256 |
| --- | ---: | ---: | --- |
| `boot.img` | 169951232 | 0 | `e65ad679a1f13adb22012cb825e85deacb741be7cddd8cdc46737e7d838ea285` |
| `payload.img` | 167772160 | 0 | `83bb0b58c8058f76f2774b8be9a38ddb2c4fc37c4880e72001d681bd266064c1` |
| `native.macho` | 91931584 | +80 | `6d375ae562d34e21e18cf21ff5018399cbb773032c5e573ff01306be8ba42a9d` |
| `prelink.macho` | 124776448 | 0 | `efe29d1405477dab01b98c5f1a3012f823760fbdcd395f661cdefe55eba71dd5` |
| `kernel.macho.adt` | 14128 | 0 | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` |

- 只重编 `ipc_kmsg.o`：`200c19f3349b66b30878903de25396e907742c34708f44bf4430bad8965b8b71` → `ea7696a6fbb6f47b9e945bcc7fcaac60885b593b88c8cb2625ddd7ea5271865f`。其余 1006 个 filelist 输入（含报告 worker）、15 个直接链接归档及 prelink donor 的哈希不变。
- native/prelink 内三种新格式串各一份；发送 → recorder、recorder → `_locked` helper、报告 worker → dump 均各一个调用点。反汇编核对 helper 前的 active 分支和第二参数 `NULL`，发布使用内联 ARM64 独占指令，不调用原子库。`llvm-nm -u` 与原始 nlist 都无 undefined（含 weak）。
- r57 五个基准产物在构建前后哈希相同，其中 `boot.img` 为 `e669e3bdf2f7f5315d9eb28e1231bdd02fe5f6245c2a961b88e0fa1ebf071169`。r58 的 ADT 和 r57 逐字节相同，FAT 内只变 `Payloads/kernel.macho`，`unixnu.toml`、trustcache、scratch image 不变；FD/DTB 哈希和 boot header ID 之外的载荷前缀不变。
- 从 `boot.img` 偏移 `2179072` 提取并校验 FAT 后，读取 XNU entry 的完整启动参数，与 r57 相同：

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1 enuma-fb-fill=1 dk=0 enuma-th=1 enuma-txpeer=1
```

独立复跑（WSL root，设备仓目录，使用不存在的输出路径；链接/调试元数据的哈希可因路径变化而变）：

```sh
/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r57-txpeer.py --r58 --out out/r58-verifier
```
