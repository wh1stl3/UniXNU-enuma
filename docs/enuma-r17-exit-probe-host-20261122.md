# enuma r17 — 进程退出探针（2026-11-22）

`self-checked`，仅主机候选：`out/ufs-sm8250-launchd-keystore-20261122-r17/`。基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`，iPadOS 17.7.11 / 21H461；补丁不进默认 series。上轮实机标定排除了该 CPU/复制路径的数量级降速；服务间隔约 40 s、SpringBoard 只有 `spawning`，是否存在短命服务反复拉起尚无退出证据。

## 采样位置与上限

`bsd/kern/kern_exit.c:2678`（应用隔离补丁后），在 `proc_exit()` 尾部的 `proc_rele(pp)` 之后。`osfmk/kern/thread.c:603` 只有最后退出的线程调用它；`proc_exit()` 已在离开进程锁后保存 PID 与 `p_xstat`，两条尾部分支都已释放进程列表锁，并完成父进程通知或内核回收。这里不解引用已可被回收的 `p`，也不改变退出状态、信号、锁、父进程通知或 panic 路径。没有把 `printf` 放在 `exit_with_reason()` 持锁提交 `p_xstat` 的位置，也没有放进只覆盖部分调用者的 `exit1()`。

```text
enuma-exit: pid=%d st=%d sig=%d
```

`st` 是原始 wait 状态 `p_xstat`，不是 errno 或已解码退出码；信号用 `WIFSIGNALED` / `WTERMSIG`，否则 `sig=0`。记录正常和信号退出（不能只看崩溃：短命服务也可正常退出）；本树该路径无 `SIGNALHOSTEXIT` 判据。缓存 `proc_is_shadow(p)` 的结果，跳过 exec 的影子进程回收，以免把换映像当成退出。每个真实进程实例最多一行，无全局缓冲或字符串复制，按三个有符号 32 位十进制参数保守计最多 59 字符（含换行，不含控制台前缀）。不同实例仍可刷屏；如实机确认高频，再用时间窗限额并输出省略计数，不在 r17 丢弃干净退出样本。

## 实机判读

| 样本 | 能判断什么 |
|---|---|
| `st=0 sig=0` | wait 状态为 0；常见于 `exit(0)`。不能等同于服务就绪，需结合启动时间和服务类型。 |
| `st=256 sig=0`，或 `st=512 sig=0` | 常见分别为 `exit(1)`、`exit(2)`；按 wait 编码右移 8 位解析本行保存的状态，不解读为 errno。本行不含另存的高位。 |
| `sig=4/5/6` | 分别为 `SIGILL` / `SIGTRAP` / `SIGABRT`：非法指令、陷阱或主动中止的线索；需与 crash report 对照。 |
| `sig=10/11` | `SIGBUS` / `SIGSEGV`：内存访问异常线索；`st=139 sig=11` 的 128 位是 core 标志，不是 `exit(139)`。 |
| `sig=9/15` | `SIGKILL` / `SIGTERM`；单凭信号不能区分 watchdog、jetsam、服务管理器或显式终止。 |
| 同一服务名、不同 PID，短时间退出后按墙钟间隔再次启动 | 支持该服务反复启动/退出。只有将服务名、PID、spawn/exit 与墙钟时序配对，才能检验节流和递增间隔；重复数字 PID 可能是回收复用或重复日志，不能单独证明重启。 |
| 仅 `spawning`，无对应 PID 或退出行 | 不能证明该服务已启动；也不能证明它未退出（如尚在退出清理、panic 或采集缺行）。不同服务的出现间隔不等于同一服务的重启间隔。 |

## 主机证据

相对 r16 只有两个链接对象变更：`kern_exec.o` 换回字节相同的 r15 对象，移除 `enuma_cpu_probe`、原调用、两条 `enuma-cpu` 输出、两个各 8 MiB 的静态数组 `enuma_cpu_src/dst`；保留控制台与共享区诊断。`kern_exit.o` 按原编译数据库的记录重编，补丁 dry-run 与实贴均无 fuzz/offset。保留宏检查 sidecar `kern_exec.o.i`。首轮打包在 `run_packaging.py:337` 因遗漏该 sidecar 失败；保留旧输出为 `…-r17-incomplete-sidecar/`，补齐后使用同一配方。

| 对象 | r16：字节数 / SHA-256 | r17：字节数 / SHA-256 |
|---|---|---|
| `kern_exec.o` | 482200 / `839e36aa038d6882922c823a6d7b423b592d827cd0b79e77edb74ff4c48a93fd` | 479808 / `9c8a1211e2d9c3722f5512519d3dc942164ad56ff0dfe7f94bd811ca0bd6793c` |
| `kern_exit.o` | 232224 / `4e8f51f369da96a000edaf06547301d5dab07ca841ffd422ecbdd086d22e305e` | 232552 / `1f2ab38169cd095e84da9a903dd844cba86f92fa12cd49036ffd4a28c6722761` |

`kern_exit.c` 源文件 SHA-256：`14b85d7f495a4ec9d2af751a2de424ffae43eabfba5494e9f9e4ec904cc9b23c` → `7ece45f0360421de871545ed32ddf675f347ba945cb51454115e43ffcf408507`。1004 个链接表条目、1021 个显式链接输入、9 个保存对象逐个哈希不变（范围重叠）；另核对宏 sidecar。r16 的 28 个冻结条目包括 boot/payload/native/prelink、回读件、配方、对象与 CPU 探针源。

`enuma-exit` 完整格式串在 r17 的 `kern_exit.o`、native 和 prelink 各一处；r16 两个最终 Mach-O 均零处。r17 两个最终 Mach-O 的 `_proc_exit` 各有一处新 `_printf`（r16 均零），均在 `_proc_rele` 和 shadow 分支之后，`0xfffffff00bd17a60` 调用加载 `0xfffffff00b6b4ea7` 的格式串；`llvm-nm -u` 均为空。CPU 探针前缀、静态数组及 helper 符号在 r17 对象和两个最终 Mach-O 中均为零；两条共享区格式串在两个最终 Mach-O 各保留一处。

两个最终 Mach-O 的 `__DATA.vmsize` 均为 r15 **1,310,720 B** → r16 **18,087,936 B** → r17 **1,310,720 B**（−16,777,216 B）；`__DATA` 文件尺寸仍为 278,528 B。

| 产物 | r16：字节数 / SHA-256 | r17：字节数 / SHA-256 |
|---|---|---|
| `native.macho` | 91875296 / `55c6bf61b10fd6a4921941364f88ca0b3a51b6c73a20ffbd9d4f8dc6274465f9` | 91858736 / `ba7909f1706f8c438b28d77bd5b07f4f11932291ac01b97a1d755c3de143b313` |
| `prelink.macho` / FAT `kernel.macho` | 124719104 / `ca68f5abedeb22fb9b71bd096b501e3680b5614dbb103119ec0d87c60644eb34` | 124702720 / `1e783989852fab73013f026b468513ac0b24355d9d0607b3c6f3a593c916b65c` |
| `payload.img` | 167772160 / `9794e97a2aff096c072ff8906573a3e04da708652ec39eebe132b34056b05524` | 167772160 / `6a2f991c19553ccedea144ee3d041d7235fa63bf502e834c7b697637e8269744` |
| `boot.img` | 169951232 / `9e94a06c41e4d1556a2d0c569bfca983e5d3bba0515ee311f37e0800637796a9` | 169951232 / `4fed789b186b0ef478f1f040f5a2b95e3db37c6c7c8f1fed83339d6f3dcc9d2a` |

r16 配方只改候选标签，仍在生成 FAT 前注入同一份 ADT。FAT 回读的 kernel 等于 prelink，boot 的 ramdisk 等于完整 payload；FAT 内容 **125,938,206 → 125,921,822 B**（−16,384 B），固定长度 payload/boot 不变。ADT 14,048 B `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059`；initrd `Payloads/scratch-data.img` 1,142,976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`；trustcache 61,356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`。三者、FD、DTB、菜单和 boot-args 逐字节不变。`root-match` exit 0：`/chosen/root-matching` 匹配签名 OS 窗口 UUID `04769D26-2CA0-4825-B443-E2E5F88300F2`。完整比较见 `delta-vs-r16.json`、`candidate-manifest.json` 与 `self-check/build-final/logs/`；r16 冻结项及链接输入重新核对无变化，基座 HEAD 未变。

### 复跑

独立 verifier 使用 WSL root 和相同冻结输入，在保留现有输出的前提下，以干净 r17 输出目录在设备仓运行 `/home/wh1stl3/.local/bin/python3.11 -B scripts/build-enuma-r17-exit-probe.py kernel`、同脚本的 `package`（预留超过 120 s），比较 `delta-vs-r16.json` 的对象、布局、FAT 回读和冻结输入。此次主机编译、链接、预链接与静态检查通过；Windows 工具等待打包时超时退出 143，WSL 子进程继续完成原包、root-match 和最终差异 JSON，没有再启动一次打包。记录检查从 UniXNU 根运行 `python3.11 -B scripts/porting-record.py check --device <UniXNU-enuma> --base origin/feat/step10-ramblock-probe`，exit 0（15 个 area）。Windows OpenSSL 独立计算 boot/payload 的 SHA-256 与清单一致。

尚未验证：实机加载、退出行覆盖与输出速率、服务退出原因、launchd 节流、SpringBoard 状态及 GUI；无设备操作、阶段不变，独立 verifier 未复跑。
