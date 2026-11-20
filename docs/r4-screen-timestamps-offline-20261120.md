# r4 屏上时间戳：离线证据链（2026-11-20）

状态：`self-checked`，仅源码、现有二进制和既有观察的离线分析；没有新上机、构建或独立 verifier 复核。观测转录和取样限制见 [r4 observation](ufs-launchd-data-20261119-observation.md) 与 [handoff](SESSION-HANDOFF-20261120.md)。157.3 s 外部时间对应屏上时间戳推进 0.646 s（整体约 1/243），不是精确固定倍数；分段约 0.00005–0.026，一次倒退 7.45 ms，一条 `Flushed 52 logs` 比邻行约超前 60 s；另一组 31 µs 对约 5 s（约 1/161,000）。这些只描述屏上时间戳，不证明内核时钟的真实速率。

## 输入与地址

- r4 `out/ufs-sm8250-launchd-data-20261119-r1/self-check/prelink.macho`，SHA-256 `3ba758425282ff99777b66baf6f283f811c6b0a9d327bdefe5aacc27d9179746`；封包提取的 `kernel.macho` 同哈希。下列内核地址为其链接虚拟地址，非实机 KASLR 回读。
- 封包 ADT `self-check/extracted/kernel.macho.adt` 的 `/cpus/cpu0` 为 `running`，`timebase-frequency` 为四字节 `00 f8 24 01`，小端 19,200,000；其他 CPU 为 `waiting`。`arm-io/ranges` 对应 SoC 基址 `0x1000000`，不会触发 `pe_identify_machine` 的零基址提前返回。
- OS 卷 `out/userdata-clean-20261112/OS.raw` 内 `/sbin/launchd` 只读解码到内存作反汇编，没有入库。解码结果 561,856 字节，SHA-256 `8cec9a3c44a443b08e977ccc5d577850316ad428c575dc01f09b018dbd5b6a25`，Mach-O UUID `4B525992-8C69-315E-A51A-CC9433E45B51`。下列用户态地址为该映像未滑移虚拟地址；该二进制无本轮可用源码行，函数名按行为描述，不将未导出符号冒称官方符号。

## launchd 前缀与内核前缀

launchd 日志条目构造函数 `0x10003fdcc` 在 `0x10003fe70` 调 `_gettimeofday`，把 `timeval` 写入条目偏移 `+0x20`；`0x10003fe80` 另取 `_os_log_simple_now` 保存到 `+0x40`，但屏上前缀格式器不使用这份值。格式器 `0x1000402c4` 使用条目的 `timeval`，在 `0x100040310` 调 `_localtime_r`，`0x100040338` 引用 `%04d-%02d-%02d %02d:%02d:%02d.%06d`，然后 `0x100040378` / `0x10004038c` 选取带域或不带域的日志行格式。输出例程 `0x10000dc54` 引用 `/dev/console`，`0x10000dc88` 调 `_write`。因此已转录的 launchd 行的时分秒前缀来自**用户态采样的日历时间**，不是 `PE_init_kprintf` 或串口输出端生成。

对照 r4 XNU：`PE_init_kprintf`（`pexpert/arm/pe_kprintf.c:59–69`，`0xfffffff00bfea46c`）只选择串口或无缓冲控制台；`kprintf`（同文件 `:98–150`，`0xfffffff00bf9dc3c`）与 `vprintf_internal`（`osfmk/kern/printf.c:873–888`，`0xfffffff00b895ec4`）输出调用方文本。另一条内核 msgbuf 路径 `_os_log_to_msgbuf_internal`（`libkern/os/log.c:703–714`，在 `0xfffffff00beb384c` 调 `absolutetime_to_microtime`）格式化的是 `[%5lu.%06u]:`，不能把它当作这批 launchd `HH:MM:SS.ffffff` 前缀。

`gettimeofday` 的 syscall 参考路径为 XNU `bsd/kern/kern_time.c:117–138` `_gettimeofday`（`0xfffffff00bd4da40`）→ `osfmk/kern/clock.c:690–707` `_clock_gettimeofday_and_absolute_time`（`0xfffffff00b864030`），后者从 `mach_absolute_time` 和日历基准计算并更新 commpage 快照。用户态可走 commpage 快路径；未记录 r4 该次调用实际走哪条。

## 19.2 MHz 的静态链路

1. `osfmk/arm/arm_init.c:371,473` 的 `PE_init_platform` 和 `rtclock_early_init` 调用点依次是 `0xfffffff00bfe47b8`、`0xfffffff00bfe48d4`。
2. `pexpert/arm/pe_identify_machine.c:43–82`，`_pe_identify_machine` `0xfffffff00bf9c558`：先设默认 24,000,000 Hz，再查找 `running` CPU 的 ADT 属性；`0xfffffff00bf9c6f0–0xfffffff00bf9c6f8` 读取四字节并写入 19,200,000。
3. `pexpert/arm/pe_init.c:568–585`，`_PE_register_timebase_callback` `0xfffffff00bf9d670` / `_PE_call_timebase_callback` `0xfffffff00bf9d6b0`：回调参数为 timebase 字段和分母 1，不是 bus/FSB。
4. `osfmk/arm/rtclock.c:106–141`，`_timebase_callback` `0xfffffff00ba16390`：`NSEC_PER_SEC=1,000,000,000`，`rtclock_sec_divisor=19,200,000`，整数 `rtclock_usec_divisor=19`，`rtclock_timebase_const.numer/denom = 625/12`，即约 52.083333 ns/tick。`RTClockData` `0xfffffff00c0056b8` 在文件中初值为零；这些是从该 ADT、初始化顺序与机器指令推导的启动写入值，**不是实机内存回读**。
5. `absolutetime_to_nanoseconds`（同文件 `:475–482`，`0xfffffff00ba16aa0`）将整秒与余 tick 分别按除数和 `10^9` 换算；`clock_get_system_nanotime`（`:290–300`，`0xfffffff00ba166c0`）同样用该除数。`0xfffffff00ba16aac–0xfffffff00ba16ad0` 可见除法、乘 `10^9` 和余数项，未见固定漏乘或漏除。`clock_initialize_calendar`（`osfmk/kern/clock.c:1109–1119`，调用点 `0xfffffff00b864bcc`）用反向换算设置 `ticks_per_sec` 并派生日历比例。
6. `mach_absolute_time`（`osfmk/arm/rtclock.c:166–260`，`0xfffffff00ba16478`）经 `ml_get_timebase`（`osfmk/arm64/machine_routines.c:2188,2221–2234`，`0xfffffff00ba1227c`）读取 `CNTVCT_EL0` 并加 `cpu_base_timebase`；`mrs` 在 `0xfffffff00ba12290`，无额外 tick 分频。计数器真实推进率未实测。

## 固定倍数不能单独解释现象

`243=3^5`，`161000=2^3×5^3×7×23`。24 MHz 默认与 19.2 MHz 之比为 `5/4`；19.2 MHz 与供对照的 16.5 MHz 之比为 `64/55`；实际纳秒比例为 `625/12`。这些均不能对应上述两个观测比例；本路径未见 16.5 MHz、`DEFAULT_FSB` 或额外分频。若假设真实计数为 19.2 MHz 且仅除数增大，两个比例分别要求 4,665,600,000 和 3,091,200,000,000，均超出该 32 位除数字段。

更重要的是，单一正的固定比例只缩放斜率，本身无法造成分段波动、倒退和单行超前。因此 24 MHz 默认误选、单一固定除数或固定漏乘漏除，不能作为**整组现象的唯一解释**；不排除它们与其他机制叠加。内核 `usec_divisor=19` 的截断也不能直接解释 launchd 前缀，因为后者不走该 msgbuf 格式器。

## A：取时与输出分离；Flush 重新取时

launchd 普通条目在 `0x10003fa14` 调构造函数取时，随后 `0x10003fac0–0x10003fafc` 入队并通知 drain；另有 `0x10003fa34` 起的直接格式化分支。drain 函数 `0x10003fb60` 摘取一批后，在 `0x10003fcc4` 输出已有条目；它在 `0x10003fd5c` 引用 `Flushed %lld logs [limit: %d]`，在 `0x10003fd78` 调**同一个**构造函数重新取时并输出汇总。因此汇总行和普通行并非已证明的不同时间源：它使用同一 `gettimeofday` 和格式器，但时间是在 drain 阶段新取的。

较新的汇总行与旧条目混排，可解释超前后再回到旧时间的形式；普通条目取时在入队加锁之前，不同线程的取时顺序也不必等于入队顺序。这些是代码允许的机制，不能指定本次 60 s 超前或 7.45 ms 倒退的具体触发点，也不能证明本次跨线程顺序。

按同一日志条目对齐 `Δ条目取时` 与 `Δ外部首现时间`：队列可使两者解耦。只有同一生产者且顺序保持的子序列才有单调预期；不能仅剔除汇总行就认定全局单调。现有 r4 转录缺逐条日志身份、首次上屏外部时间与前缀的完整配对列，不能直接完成两曲线检验。

## B：可变延迟的代码条件

launchd drain 的控制台输出可经过同步 dispatch 与写操作（`0x10000dc14`、`0x10000dc88`）。XNU `console_write`（`osfmk/console/serial_console.c:524–590`，`0xfffffff00b9d3508`）在 ring 满时可在写者路径等待并 drain；`console_ring_try_empty`（`:394–479`，`0xfffffff00b9d31cc`）可等待锁并下发字符。`uart_putc_options`（`pexpert/arm/pe_serial.c:1077–1121`，`0xfffffff00bf9e0c4`）可等待 TX-ready；直接 `kprintf` 输出分支持锁时关闭中断（`pe_kprintf.c:109–124`）。

这些是潜在可变延迟的源码和二进制条件，**不是**该次屏幕输出实际经过 UART、IRQ 或调度饥饿发生、或者 B 占多大比例的实测证据。若延迟发生在产生下一条日志之前，条目时间差和外部间隔可同向拉长；若阻塞发生在取时后、写出之前，即使属 B，两曲线也会解耦，不能单靠视频与队列现象区分。

## IOSleep、超时与已知时长

`IOSleep`（`iokit/Kernel/IOLib.cpp:1513–1515`，`0xfffffff00bedc78c`）经 `delay_for_interval`（`osfmk/kern/clock.c:1605–1613`，`0xfffffff00b865710`）将请求时长转换为 tick 并设置绝对 deadline。`IOService::waitForMatchingServiceWithToken`（`iokit/Kernel/IOService.cpp:6564–6587`，`0xfffffff00bef4eb0`）同样先 `nanoseconds_to_absolutetime`（调用点 `0xfffffff00bef5188`），再等待 deadline（`0xfffffff00bef51a8`）。它们不调用正向 `absolutetime_to_nanoseconds`；仅正向换算或屏上格式错误不会自动把等待拉长。真实计数速率、共用除数或 deadline 唤醒路径异常才可能影响实际等待。

r4 记录未给出同一次 `waitForMatchingService(5s)` 的入口、返回和确实超时；该函数也可立即匹配或提前唤醒。未记录同一 kext 加载的外部起止时间且其无固定预期时长。两域 `SOURCE_ATTACH` 只有顺序与 PID，没有按域配对的外部首末帧时刻和固定耗时契约。故无法从已有转录计算这些操作的真实耗时，也不能把 157.3 s 分配给任一操作。

## 最小判别方法

**仅为未来构建的候选改动，本轮未实施、未审查。** 在 `IOService.cpp:6585` 的一次已知无匹配、必然超时的 5 s 等待前后，用绕过 launchd 队列的同一路径打标记，字段 `phase, CNTVCT, abstime_ns, calendar_us, result`，再用外部时钟量间隔。判据为约 5 s、约 96,000,000 tick：两者均正常支持该等待正常；tick 与换算正常但返回迟则需查唤醒/调度；tick 或换算偏离则不能归为纯日志缓冲。候选涉及内核等待路径，实施前须按项目规则审查。

## 不能证明什么

静态推导不证明实机 tick 速率、运行时回调及日历状态；不能证明 B 类真实延迟的占比或一次倒退的跨线程实际顺序，也不能证明服务稳定。既有观察应表述为：外部观察的数分钟内屏上未见 panic；两域发生 attach、启动有推进迹象，服务稳定与初始化完成未成立。没有新设备操作，也没有更改正式阶段结论。
