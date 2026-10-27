# 当前：新OEM追踪固件已编出，仍为stage10离线构建

2026-10-27。本轮目标“继续推进直至编出新固件”已完成。仅写入 D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display，原共享主线及其firmware保持不改。R027冻结未消费，未查询或操作设备、未推送。

两份新3MiB固件均在本worktree：

- 原版对照：out/oem-control-trace-build-20261027-2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd，SHA256 e856368faa31690518cea62f6212d536dd13c82941910f9cf6825c9450ad1786。
- MMU-only：out/oem-mmu-only-trace-build-20261027-2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd，SHA256 984aa8cf15f6358ce5eb5c6743a67a94a050f1dd0cfc7c3b4df9361ac5e37ef6。

## 实际新增

显式--oem-trace-build把Core同句柄/FV/LoadedImage指针绑定、已重定位.text完整性指纹、持久三服务追踪、调用前快照和板级有界像素适配器接入完整FD。嵌套其他句柄透明跳过；错误目标绑定锁存失败，沿CoreExit返回实际StartImage错误，若CoreExit意外返回则停在CpuPause循环，不能冒充OEM入口执行或OEM返回。

运行态指纹在精确原PE基础上归一化756个DIR64文本重定位；它是诊断误配检查，不是密码学认证。nabu路线仍只改enuma DisplayDxe 0x1994的参数2→0，保留构造器和面板/管线初始化；elish路线保留原生K81双链命令与等待契约。

板级适配器实际接上既有内存区检查、路由采样、EL1/整帧identity-WT检查、单次320×160/8秒事务及恢复未确认时的复位/停止路径。静态上下文跨驱动返回保留，没有把约200KiB保存区放在OEM栈上。它只显示所选事件五行摘要；CPU恢复/写读回不等于可见、相机采集或完整文本持久导出。

## 验证

两份完整构建均通过源码/快照一致性和Core补丁回退检查。最终FD审计核对各32个OEM PE/DEPEX、39项APRIORI、两份K81 RAW，实际抽取PE重算生成指纹并匹配构建头；包装器、观察器、板级sink及终止函数均在最终Core。stage10实际序列与8项删除调用负测通过；绑定失败CoreExit/Pause/回跳序列与6项删除指令负测通过。宿主ASan/UBSan覆盖重定位、损坏、错入口/大小、嵌套句柄、FV/LoadedImage身份、CRC失败、单次锁存、交叉变体拒绝；板级适配器AArch64对象编译通过。

原调用前出口回归通过749种损坏拒绝、宿主不返回服务后的外部快照保留、像素事务失败路径和6项旧组件机器码删除检查。修复后的构建入口8项回归通过，非OEM使用trace选项被CLI拒绝且不创建输出。总报告：[新固件证据](../reports/enuma-oem-core-trace-development.json)。

第一组trace-build-1因新patch未进入旧preflight清单而在编译前失败，目录保留。builder已显式复制此patch，新trace-build-2成功。组件早期check1/3是声明/include开发错误，最终check5有效。固件本地提交b6fe1a2；构建时基点322f427加本轮未提交快照，不冒充干净提交构建。设备仓本轮提交号见git log。

## 当前限制与下一步

两profile强制stage10派发前停止，不能执行OEM或物理回调；未生成可上机资格或Boot.img。session=1/call=0仅是编译选择，不是实机trial nonce。板级窗口独占、异常退出、可见采集及恢复路径尚未验收；普通sink拒绝保持原服务转发语义，不能据此承诺一定得到外部证据。后续须完成运行态单次选择、板级所有权/异常终止策略和独立资格，才考虑移除停止门。未观察到return仍不能判死锁。

R027/S055保持paused-by-user/未消费；原镜像0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a及原始OEM摘要本轮复核一致。旧准备过期，没有当前录像或按键待办。用户此前报告ADB恢复，本轮未独立验证，不扩大为实机放行。

完整实现、命令、边界：[Core追踪固件记录](operations/2026-10-27-oem-core-trace-firmware.md)。原stage10无追踪构建仍保留在上一轮目录，不覆盖；原主线和冻结资格不合入本轮代码，不推送，不改内存字段或verified。
