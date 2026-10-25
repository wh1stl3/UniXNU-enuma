# D-215：原生 ramoops 兼容审计与最小写入候选

2026-10-25。用户支持继续后完成离线实现；没有新 boot、物理 RAM 访问、模块加载或分区写入。

主判断：原生 ramoops 是目前最值得优先闭合的批量日志路线。Android 已负责保留目标区域和提供标准读取端，绕开旧 R-002 需要修改 Android boot 保留区的前置。但 UEFI 映射和跨复位存活仍需独立验证，不能把布局相同当成日志通了。

## 已核对的链路

- 本机只读证据见 `reports/enuma-ramoops-route-discovery.json`：backend=ramoops、B0000000/4MiB、console/pmsg 各2MiB、record/ftrace/ECC=0、1024页元数据 Reserved。只查元数据，没有读取物理内容。
- 固定 [MiCode 52a2f18 ram.c](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/fs/pstore/ram.c) 的 `ramoops_memreserve` 硬编码相同地址及对半布局。运行内核为4.19.157-perf-gf8cf95f4dc15，尚未证明就是这份源码构建。
- [同提交 ram_core.c](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/fs/pstore/ram_core.c) 的ECC0、sig XOR0路径使用12字节DBGC/start/size头；容量0x1ffff4。有效范围size<=capacity、start<=size，允许满环start==capacity。旧日志按data[start:size]+data[0:start]复制。console初始化先保存old_log再zap，不能把zap当成旧日志必丢失。
- 固定 umi 3eb7257 的 BSD-2-Clause-Patent writer 与上述 ABI 相合；新核心保留许可和来源。MiCode GPL文件仅作参考，未导入固件。逐文件URL/SHA见 `reports/enuma-ramoops-kernel-sources.json`。
- 当前 `MemoryMapLib.c` 的Kernel段结束于B0000000，没有覆盖console。`MemoryInitPei.c` 只为显式记录建立identity mapping，不能假设整个DDR已映射。`MEM_RES`配合`Reserv`不进入普通可分配SYSTEM_MEMORY路径。
- 现有构建导出的ArmMmuLib将UNCACHED_UNBUFFERED映射为Normal Non-cacheable；板级`UNCACHED_UNBUFFERED_XN`只是该枚举的别名，未额外设置XN。拟采用准确的UNCACHED_UNBUFFERED名称，不声称XN，也不扩大修改MMU实现。
- 同构建导出的ResetWarm先查PSCI_FEATURES，再调用SYSTEM_RESET2 type0；不支持时回退ResetCold。接口名不保证DRAM保留，数据可能被固件、引导器或复位链清掉。

## 已实现与验证

`firmware/diagnostics/EnumaRamoopsBuffer.h`为地址无关、未接线核心。调用者传对齐区域/大小及非重叠输入；必须单核、禁中断/无并发写、reserved normal uncached。无物理地址、构造器、SerialPort绑定、分配、DEBUG或复位。有效旧环保留，无效头重新初始化；一次超长输入只保留最新capacity字节，返回完整输入长度。payload先于size/start发布，不能保证复位中断写入的原子性。

运行 `python3 -B scripts/test_ramoops_buffer.py`：51,210个环形队列独立oracle/边界用例通过，含1..256容量、重复回绕/超长/空写、坏签名/大小/start、start==capacity、越界保护和非法参数；ASan/UBSan通过。另使用现有固定构建导出的实际EDK头文件完成AArch64 freestanding对象编译。不是完整FD构建或实机证明。摘要与命令见 `reports/enuma-ramoops-buffer-tests.json`。

`scripts/collect_enuma_pstore.py`已实现有界只读ADB收集：显式serial、每轮核对enuma后root读固定console文件，不reboot/mount/unlink/清pstore/读物理内存；原始字节和采集报告只写本地out，公开仅脱敏状态/SHA。输入32位小写hex随机nonce，对应44字节`ENUMA-R017:<nonce>\n`，匹配本次完整标记。5个主机测试通过，未在本轮实际采集pstore内容。未检出只说明链路未闭合，不唯一归因于写入或复位。Android早期消费者、清理时机仍未知，ADB上线可能来不及；首笔失败后先隔离，不重复同图或直接扩区。

## R-017 待决的具体最小范围

候选A（推荐）：仅新增B0000000/0x200000 console映射，拟记录为`{"Ramoops Console", 0xb0000000ULL, 0x200000ULL, AddMem, MEM_RES, UNCACHEABLE, Reserv, UNCACHED_UNBUFFERED}`。pmsg B0200000..B03fffff不映射、不写。仅在MMU成功建立后的已资格Core有界入口追加一次44字节nonce；有效旧头保留，坏头仅初始化12字节元数据。写入最多44个payload字节和头字段，地址始终限制在该console内。先不接全局SerialPort，避免SEC/MMU之前写入和日志量干扰。

既有短延时后请求ResetWarm，PSCI不支持则沿cold fallback；不将回退或返回时序当存活证明。只允许一笔新资格镜像的临时fastboot boot，75秒主机观察；无法返回立即停止追加、沿既有人工恢复并核验。不写Android boot/FDT或任何分区，不改槽、verified、显示寄存器或旧失败账本。源码/实际PE/宏/映射/产物摘要及全部当前文档推送、即时身份/备份/恢复门禁是执行前置，当前还没有接线/FD/打包资格。

候选B：保持现有内存表，继续独立原生计数观察和软件日志后端审计。无需新增RAM权限，但继续依赖低带宽时序，不能验证本路线保留链。

不选全4MiB/全局SerialPort作为首笔：没有必要触及pmsg，且全局后端在MMU之前就可能被调用。首笔只回答“指定Core位置写入的本次标记能否经复位进入原生pstore”。读回成功后再独立扩大到结构化多值日志/全局后端；无标记不能直接宣布该路线无效。

**停点与规则**：`firmware/AGENTS.md`明确“New memory size/base changes or *_verified=true still require the companion review process.” 因而本轮仅提交未接线核心、收集器和审计，内存表/board.toml/bringup-plan/Null后端均未改。R-017 pending，需明确批准A的地址/大小/标记写入/一次复位临时启动范围后，才能接线、完整构建审计并直接上机。用户一般性的“支持继续”不被代填成新地址的精确批准；既有R-002/R-008不扩张到此区域。

本轮最终只读核验Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与本地备份摘要均通过，见 `reports/enuma-recovery-reconciliation.json`。未录音、未产生或上传新影音。S-001..014 consumed；真实GOP/XNU/iPadOS仍未实机闭合。
