# 当前：单 worktree 双 OEM profile 已完成完整 FD 构建与抽取审计

2026-10-27。本对话仅写入 D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display（原生 Git worktree，基点97ef242）。原主线 D:/Code/PortingiOS/enuma/UniXNU-enuma 及其 firmware 保持不改；R027继续冻结。未查询设备、启动、打包Boot.img或推送。用户此前报告ADB恢复，不等于本轮核验设备状态或恢复实机授权。

## 本轮完成

- 隔离固定依赖已从本地来源准备完毕；两个profile各使用独占vendor/source/work目录。沿开发快照manifest构建，旧发布源锁及原vendor锁不改。
- oem-control完整3MiB FD：out/oem-control-build-20261027-2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd，SHA256 409edc8914a16fbafb80d497e3b48e2a87912aa38a285c3419bf24df6f593f84。
- oem-mmu-only完整3MiB FD：out/oem-mmu-only-build-20261027-2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd，SHA256 f4ee1be1f10ec48561c1910152d9f2fe195bd9481c0f7e0f814f3c9476c39fd6。
- 最终FD抽取核对通过：每组32个OEM PE及DEPEX、39项APRIORI、两份K81 RAW；UFSDxe未包含，SimpleFb和GOP selftest未混入。实际DxeCore/EnumaProbe与编译输出一致，stage10/SimpleFb0实际编译宏已核对。证据out/oem-{control,mmu-only}-fd-audit-20261027-1/result.json。
- Core实际调用序列为0x3c90延时、0x3c94 ResetCold、0x3c98 CpuDeadLoop、0x3c9c CoreDispatcher；每组4项删除调用负测通过，两组Core .text摘要相同。这是静态序列检查，不是完整控制流证明或硬件复位保证。证据out/oem-{control,mmu-only}-stage10-code-20261027-1。
- 第一组build-1在编译前因WSL Git发现Windows worktree的gitfile失败，保留全部失败输出。修复仅在新构建临时Mu_Basecore执行git init；build-2通过，源码/快照摘要及Core补丁回退复核通过。构建入口修复后8项profile检查通过（out/oem-build-profile-check-20261027-2）。

## 两条研究路线与主线边界

nabu路线当前只移植精确enuma PE的0x1994指令参数2→0，原版摘要6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425，实验版ed37a4e137cca2fcf4d5fa5718e18a319c2aa1b7a1cfab480693325bfbe2b5e3。保留构造器、MDPSetupPipe/MDPPanelInit和错误检查。它是MMU/SID初始化假设的实验，尚非修复证明。

elish路线保留enuma原生K81双链各188条数据和原等待契约；没有把分链发送的11误删，也没有直接替换为Android等待值。本轮确认这些原生资源确实进入两份FD。

两profile目前强制stage10派发前停止，SimpleFb=0、GOP_SELFTEST=0、菜单关闭、UFS关闭。没有激活OEM追踪，也没有执行OEM PE；本轮不是生产GOP、ConOut、BDS或实体输入验收。旧S054只证明临时私有GOP的菜单画面，不与OEM路径合并论证。

## 下一步

在本worktree继续接精确CoreStartImage句柄、实际PE/FV身份和持久追踪上下文，再接调用前冻结快照与板级取证后端。重点核对LocateProtocol返回RVA0x1bce0及后续协议方法覆盖；三项Boot Services包装不能覆盖所有MMIO/SMC/锁/首次调用前失效。现有host出口已验证非返回后外部快照保留及恢复失败Stop，但尚未连接真实板级物理回调、窗口所有权和终止恢复策略。缺失return只说明快照未观察到，不能判定死锁。

R027/S055 paused-by-user、未消费；镜像SHA256 0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a本轮复核一致。旧准备已过期，没有当前录像或按键待办。后续可运行profile须独立完成出口与资格；当前不部署、不推送，不改内存基址/大小、verified或旧资格。

详见[隔离工作区及构建记录](operations/2026-10-27-oem-display-worktree.md)、[应用方案](operations/2026-10-27-enuma-display-application-plan.md)及[调用前出口](operations/2026-10-27-oem-precall-capture.md)。源码只作本地里程碑提交，提交号以git log为准；生成产物、OEM二进制和媒体仅留out。

最终总报告：[OEM双FD离线检查](../reports/enuma-oem-fd-pair-development.json)。两组negative-2合计14项拒绝检查、8项Core删除调用负测、8项profile检查及双组同源比较全部通过；本地固件修复提交322f427，设备仓提交号见git log。
