# 新强停规则执行与 R-002 标记存活试验

2026-10-23（Asia/Shanghai）。用户要求修改强停规则后继续主线，并随后澄清“黑屏和定时复位是可以的，因为你可以确保能回到可控的状态”。项目AGENTS.md已按最终要求更新：生成镜像不硬停；优先过程日志和恢复保障；已有可控返回证据的有界临时探针，不因黑屏/缺完整早期日志单独停；无法恢复、越权操作和原内存/verified审查仍停。

这项指令恢复了设备工作范围，取代前几轮“暂不操作实机”的当前限制；不删除历史文档中的当时事实。未将例外扩张为flash/erase/改槽或无限试错。TWRP没有测试，不作为已验证恢复路径。

## 本轮结果

**正常ABI加载/卸载与受保护16字节回读均实机通过；标记同次启动匹配，经Bootloader进入不写标记的保留Android后不再匹配。按R-002批准的失败即停边界，停止跨复位软件日志路线，没有换地址或启用SEC/DXE持久日志。**

最后设备为Android，sys.boot_completed=1、root正常、boot_a/vendor_boot_a摘要与备份一致；两种模块均卸载、临时上传文件删除。没有flash/erase/改槽或验证标记置true。只在批准的0x9fff7000起16字节写入一次固定标记，未扩大32KiB区域。

## 前置与ABI实测

先只读识别唯一在线enuma，匹配实际4.19.157-perf-gf8cf95f4dc15内核、root、当前槽位和原分区摘要。新采集的活动FDT SHA256仍为6e88ca4a3bfaf8823da9bcf44defdd5ad7a3f8eec671223675076fd5457a0d09，唯一reserve tuple为0x9fff7000/0x8000，8页KPF_RESERVED全true。旧报告只作对照，新采集结果见enuma-log-reservation-preflight-20261023.json；其中issued_at/boot返回时序来自上次启动记录，不是新启动。

先启动dmesg -w流且确认进程存活/有输出，再normal insmod无物理访问ABI模块：返回0、proc/modules实际出现模块、日志出现新的ENUMA_R002 ABI_OK；随后normal rmmod返回0且模块消失。vermagic/CRC正常被内核接受，没有force-load。继而在同一保护条件下加载16字节marker reader，实际日志出现一个完整记录，正常卸载。记录与内容不公开，只提交日志摘要及范围。

在后面的两次Android启动中，scripts/run_log_reader.py每次都重新核对身份/槽位/内核/FDT/8页/分区摘要，先正常加载ABI模块，再加载reader；每个模块都在dmesg流已启动后加载，验证新日志记录数、实际模块出现/消失，完成后清理精确上传路径。它不重启、不写物理区、不强载；未来存活试验须加--require-seed，标记不匹配返回2。默认命令完成仅代表回读动作完成，不能把exit0当存活成功，必须看matches_seed_marker。

## 最小writer与临时镜像

优先复用已经实机通过的stock Android入口FDT保留封装，不新增内存图或偏移。不让未保留的普通Linux经过日志候选区。

- 新diagnostics/enuma_marker_seed.h只提供固定16字节ENUMA-R002-SEED1写入函数；未保留/null目标拒绝，不分配内存、不追加日志、不提供可变物理地址参数。
- build_log_reservation_boot.py新增显式--seed-marker；只有这个模式才在FDT保留成功后、进入原Linux前写入[0x9fff7000,0x9fff7010)，按实际缓存行清理到PoC并dsb。默认不含writer，原先已验证的不写标记镜像保持原样。
- host实际writer函数在ASan/UBSan下验证保留false零写、null拒绝、16字节+两侧canary以及同值重复；实际FDT21组sanitizer重新通过，45项Python通过。
- seed镜像原厂kernel其他字节、ramdisk/v3契约及vendor_boot策略不变，固定AOSP解包回读通过。文件仅out/boot-candidate/r002-android-seed-01.img，116359168字节，SHA256 3b1a685ef8b45a72587b28e58dda3801b685e79d0c91981a9adcfc3116c7f764。构建报告hardware_executed=false仅指构建时状态，后续实际启动看device报告，不能混淆。
- builder仅生成镜像不触发设备命令，符合新规则无需另行申请；写入地址和大小在原R-002批准范围内，board/bringup-plan/512MiB/example不改。

## 控制链与实际结果

| 阶段 | 实际动作与证据 | 结论 |
| --- | --- | --- |
| 写入前基线 | 已保护Android中只读16字节，原值与所选固定marker不相同 | 排除原样本恰好已有该marker；原值私有 |
| seed启动 | 01:56:59临时boot seed镜像；ADB16.061秒、Android完成30.625秒；身份/root/原摘要正常 | 没有刷写分区；FDT保留后才写marker |
| 同次回读 | seed-sameboot-01；活动FDT及8页再核对，ABI/reader正常装卸，读16字节与seed完全一致 | writer与reader在同次启动配合有效，尚无跨复位结论 |
| 经Bootloader | 从该Android由既有helper重启Bootloader，完整enuma/slot/unlocked身份组检查通过后，临时boot已有不写marker镜像e0bd9b25d6e472a52735893dac970bb6f475e6c5394e6d878c615e54d6fc0e42；01:58:14，ADB16.044秒、完成29.605秒 | 不通过普通未保留Linux；第二份镜像没有writer，不能重写出伪阳性 |
| 复位后回读 | seed-after-bootloader-01；FDT与8页仍保护，ABI/reader正常装卸，收到新的完整16字节记录，但matches_seed_marker=false | 当前完整重启/Bootloader/保留Android路径没有保存marker，持久性失败 |

不能从最后一行断言特定ABL/XBL函数“清零”，也未证明所有字节为零；本试验没有观察各中间阶段，可能改写位置仍未知。也不能将其与UEFI固件实际写日志的生命周期等同。批准范围明确要求候选清空/存活不满足就停，因此不再使用该区做跨复位日志，不试其他地址。

公开总证据：reports/enuma-marker-survival-device.json；ABI、初始只读与两次回读分别为enuma-log-abi-device.json、enuma-log-reader-device.json、enuma-log-seed-sameboot-01.json、enuma-log-seed-after-bootloader-01.json。每次回读保存私有dmesg流和SHA，不提交未知物理内容或设备标识。

## 显示来源补查

在原Android只读尝试/sys/kernel/debug/dri/0/state和/d/dri/0/state，两者正文均为cat的No such file or directory，虽然su/ADB返回0，不能当采集成功；报告明确content_contains_cat_error=true、usable_geometry=false。panel enabled节点正文为enabled，只说明此刻Android显示启用，不提供入口base/stride/format。没有挂载debugfs或猜MDP寄存器。

SimpleFb六项入口事实仍缺，alioth/elish只作已固定的同SoC方案来源评估。未接入30-OEM变体、未放宽FD审计、未写显示/DFPS/SMEM。

## 停点与替代方案

这是**R-002存活失败的路线停点**，不是“黑屏一律不许测”。用户最新允许有界可控黑屏/定时返回探针仍有效；无恢复故障、无待按键事项。后续路线候选见NEED-REVIEW/R-003，当前不自动换址、借显示区或刷分区：

1. 在既有可控返回范围继续细分真正Image EntryPoint/构造器/异常门，复用现有完整GUID、Mu计时与PSCI，避免新固定内存。可减少归因范围，但带宽低，仍非完整文本日志，不能承诺一次进入XNU。
2. 核对enuma UART接点/电平和实际GENI serial实现后现场采集完整早期日志；同SoC仓可提供代码参考，不能提供未经证实的本板接点。需要硬件与人在场，当前未安排接线。
3. 同次UEFI内输出到已证实的显示/USB通道，避免跨Bootloader保存；目前GOP仍卡/几何不明，USB device日志传输也未建，属于后续实现方案，不能当现成通道。

推荐先采用方案1继续无新内存的定位，同时准备方案2；不将R-002改为新地址重试。若用户选择其他候选，再固定具体实现、风险与恢复条件。原内存/verified审查规则保持。
