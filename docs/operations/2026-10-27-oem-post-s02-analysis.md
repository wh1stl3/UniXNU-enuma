# OEM progress-v2：代码归因与下一验证范围

2026-10-27，用户确认E01/S02判读一致，要求充分代码分析后再实机。本轮未追加设备动作，旧单次不可复用。

## 当前最大嫌疑

最大可操作嫌疑是追踪环境与OEM构造/早期依赖的兼容性，尤其私有SystemTable失去动态一致性。置信度分开：此代码缺陷已宿主复现；它是否触发本次停机仍低至中等，不能称已定位根因。当前没有足够现场证据给某一个具体指令赋予最高故障概率。SID/面板重初始化暂降为后续嫌疑。

EnumaOemServiceTrace.h的Prepare复制整个SystemTable，替换BootServices并重新计算CRC，却没有保留原SystemTable指针或同步ConfigurationTable/NumberOfTableEntries。其他BootServices（含InstallConfigurationTable）直接沿用原函数。真实CoreInstallConfigurationTable只操作gDxeCoreST：添加改变数量，扩容替换指针并释放旧表，删除减少数量。于是OEM仍可能读旧数量、遗漏新表，扩容后甚至访问已释放存储。只在InstallConfigurationTable返回后同步也不完整：通知回调可在服务返回前发生；必须覆盖更新完成且通知发出之前的时点或改造追踪架构。

tests/oem_system_table_lifetime.c调用实际Prepare和私有服务入口，模拟Core更新全局表的确切语义，复现成功状态下增长/删除均留下旧副本。ASan/UBSan运行通过是“成功复现缺陷”，不是修复通过；模型没有释放旧存储，不声称实际发生UAF。实际OEM在0x5cc4调用InstallConfigurationTable，0x5920读取私有SystemTable的数量/指针；存在相关路径，但没有本次表容量、是否扩容或该调用实际到达证据。

## 精确OEM路径

原厂PE SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425。

入口0x114c → 构造器调度0x123c → 0x1350调用0x5b60 → 0x5a84扩展数组 → 0x3c88/0x3bd0/0x3aec → 0x3a9c → 0x3ab8 AllocatePool，返回0x3abc。结合初始零状态与无此前包装服务，此为首调用的强静态解释；照片只证明最内层RVA，未记录完整栈或分配长度。

成功后0x3ac0取返回Buffer，0x3aec转ZeroMem（0x4078→0x41b4），再回到0x5a84。静态预期先申请256字节GUID数组，再两次128字节指针数组；三者均经0x3abc。之后0x5d70初始化HobLib，0x5e5c初始化ArmArchTimerLib，0x612c查找Qualcomm Kernel协议b5062be7-170b-4a32-be21-689262ff4399（返回RVA0x616c）。不是SID协议。最终0x6ffc注册guided-section handler，经0x5b64可能调用配置表安装，之后才进入0x16e8显示入口。SID调用在更后面的0x16bc0→0x1bca4→0x1bcdc。

HOB GUID是标准7739f24c-93d7-11d4-9a3a-0090273fc14d，Core源码实际安装此表，不能无证据断言缺HOB。OEM ZeroMem使用SIMD，但SEC明确ArmEnableVFP且CPACR_DEFAULT=CPACR_FPEN_FULL，暂不把“必然SIMD异常”列为主因。定时器可用性判断0x3de0恒返回1，随后仍检查频率；照片的8秒等待依赖本机TimerLib，不能直接证明原厂构造器所有检查均通过。

## 追踪清理及机器码复核

已编译Core的EnumaTraceAllocatePool在0x11f54将原始返回值存x19，0x11f70调用记录/AfterForward，0x11f74恢复x0；保存/恢复x19–x23，未发现返回值被取证回调覆盖的指令证据。OemProgressEmit的Active在Present成功后清零；第二窗前只有前窗Result=5才能继续。两张图支持第一窗恢复完成并成功转发，第二窗仅证明已画出，尚不证明其Hold/恢复/读回/DAIF恢复完成。

像素每窗预算是3N读、2N写、3次屏障及一次8秒Hold；重置计数后正常全路径恰好落在预算内，未发现必然第二窗超额。失败路径调用ResetCold，实际Core链接到PSCI SYSTEM_RESET（0x84000009），返回后死循环；没有独立看门狗，不能以超时区分未到复位与复位请求无效。

## 下一次实机前的具体方案

1. 先解决或隔离私有表动态一致性，并以真实Core配置表实现做增长、删除、扩容、通知重入测试；保留原调用结果、TPL与CRC语义。不得仅加一次返回后CopyMem就称修复完整。
2. 新的有界观测以call1入口/返回和call2或Qualcomm Kernel LocateProtocol为优先目标，记录服务号、大小/实际状态、RVA与session。看到call1入口即可证明S02取证返回后OEM至少继续到下一服务；没有图仍须区分取证拒绝与执行未到达。
3. 每个窗必须有明确失败原因记录与恢复路径；不增加全局硬件写入或扩大窗口。新候选独立构建、机器码、失败测试、单次绑定。此次不启用MMU-only补丁、不原样重试progress-v2。

若call1/2均正常且Kernel协议前后通过，构造早期嫌疑降低；若配置表同步前后行为不同，才提升该缺陷为现场根因；若SID前有新证据，再测试SID/MMU假设。原始图像、二进制、完整反汇编仅本地out；公开只保留此说明、复现源码和脱敏报告。

本地证据：out/oem-progress-20261027/media-review/oem-disassembly.txt、rva-map.json、system-table-lifetime；编译Core反汇编在qualification1/Core.disassembly.txt，符号映射在build2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/AARCH64/MdeModulePkg/Core/Dxe/DxeMain/DEBUG/DxeCore.map。
