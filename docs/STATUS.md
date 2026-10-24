# 当前状态：D-166二进制审计完成，A候选离线资格通过

2026-10-25。本轮按D-164/D-165推进，完成真实ABL/原厂DisplayDxe/保存DTB的离线审计，以及A/detail15候选构建、FD/打包/编译参数和Core机器码检查。未访问设备，未执行新临时boot或分区写入。当前结论以D-166为准；D-163证据更正和D-164路线顺序维持。

## 新增证据

1. 从R-014实际镜像和原厂XBL分别解出DisplayDxe，PE逐字节相同，SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425。真实代码读取EnableDisplayThread，调用Kernel Protocol、scheduler HOB回退、InitLock和ThreadCreate/Resume，线程入口调用SetMode。缺Kernel的明确分支可清线程标志并返回0，因此驱动成功返回不证明模式设置，也不能用缺Kernel单独解释75秒无返回。
2. 本机ABL的LinuxLoader真实查找/reserved-memory/splash_region；保存的vendor_boot三份完整DTB和历史Android FDT只有cont_splash_region@9c000000（0x02300000）与DFPS（0x00100000），无该目标名称。这是具体交接缺口；实际所选DTB/DTBO和临时入口FDT未知，未证明该分支直接关闭面板。
3. 当前源码的FD Reserved/FD_Reserved名称缺口仍成立。不能据此断言没有其他Kernel Protocol提供者或直接改内存表/关线程/补stub。enuma尚无EntryArg HOB的板级消费者证据，上游ShengBootMemoryDxe的实现可参考，内存增补不能直接搬用。

专项文档：[交接契约](operations/2026-10-25-handoff-contract.md)、[原厂ABI](operations/2026-10-25-native-display-abi.md)。机器证据reports/enuma-display-handoff-audit.json，可复现工具scripts/audit_display_handoff.py。实际输入摘要和摘录已绑定，原始二进制/FDT仅在out/。

## 新A候选：已离线归档，未上机

- 固件固定aa9ec666abadfeacda608870ecfb4e7179c7ecc3；stage13/detail15，GUID4138022f-06c7-4f79-9c94-7e33b511a4e7，GUID-only、delay2、fallback7、without-ufs、query0/step0/value-off。未改固件源码或OEM PE。
- 镜像SHA256：29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4；FD：776437b5a5eaf1939399fabfc4ec599cb9f58a542de29a2a1f66fc500b10f10d；raw：2c9ca77319115f9aa2b5ef75363dd78fe4953d19bf656f22c99996ffe5884b7e。
- 独立归档out/display-entry-boundary/pre-entry-aa9ec66/，含FD/raw/image及相邻报告、实际Core PE/编译参数、资格和机器码摘录。总报告reports/enuma-display-boundary-qualification.json。
- FD审计32个原厂PE/DEPEX不变，仅省略UFSDxe，无SimpleFb。打包Boot v3、空ramdisk，AOSP官方解包回读一致。实际Core在RVA0x10474调point15门，0x10490才调CoreStartImage；门比较point15和GUID两半，再MicroSecondDelay(2000000)/ResetCold/CpuDeadLoop。fallback不是watchdog，前序驱动仍可能操作硬件。
- 首次构建因旧reference与现有Common/Mu链接不匹配被预检拒绝；改用固定firmware检出重跑成功，未改参考仓。WSL打包被Windows路径锁拒绝后，换Windows Python通过。make有clock-skew警告，记录约20秒主机/WSL差；已检查实际Core新GUID/point/delay，不能扩张为通用固件稳定性证明。

## 下一步

先完成此次文档和工具的提交推送，再按AGENTS对A做即时enuma身份、匹配备份、恢复与观测门禁及有效执行范围核对；未满足不得boot。A仅用于验证是否到达DisplayDxe启动边界，不能证明PE运行/线程/可见显示。根据A的有效阶段证据再决定B或更早定位，不把单次耗时当可靠寄存器通道。

A到达后优先取得真实入口FDT、Kernel Protocol/scheduler HOB和模式设置条件，按缺口选择显示继承或原厂适配；本轮没有节点修补、内存字段/映射改变、verified、像素/背光写入或新批准。R-015暂停，R-005/R-007旧像素授权不复活；R-008/R-012/R-013/R-014按原始范围核对。

## 实机记录与系统里程碑

R-014旧镜像922972e6两笔75秒无返回，仍未定位；不能升级为已证明派发挂死，复位失效/前置路径/观测失败仍可能。最新已有恢复证据reports/enuma-recovery-reconciliation.json、out/device-tests/20261025T012053-recovery-reconciliation.json仅证明当时Android完成/root/A槽/解锁及分区摘要通过，本轮实时模式未知。没有新实机硬停。

目标仍为iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB，UniXNU5fdbd5d。未验收可见GOP、PE_Video、XNU入口、UFS根或用户态。超时仍停止追加、先恢复并当轮同步文档，不原样重试失败镜像。

## 发布状态

当前新增工具、证据及D-166文档已落地；提交/远端发布结果以本轮Git记录为准。另一会话已有87c5347/8d38c34的D-165复核保留，不改写其历史；其中过强超时解释由D-166收窄。
