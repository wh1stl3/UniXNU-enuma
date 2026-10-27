# 当前：DisplayDxe离线归因推进，实机暂停

2026-10-27。当前设备模式未知；最后设备查询仍为D320的01:48未以已授权ADB在线，本轮没有设备查询/启动/部署、录像申请或nuwa操作。

本轮新增精确OEM PE返回RVA归因工具scripts/map_oem_trace_rva.py：强制315392字节和SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425，校验可执行section及真实BL/BLR；不猜函数名或动态目标。6项测试通过，5处静态指令与旧审计一致。已核对CoreStartImage同句柄LoadedImage来源，以及EntryPoint实际传入Image->Info.SystemTable；这仍是源码检查，不是新Core机器码或原厂执行资格。

新证据out/oem-rva-20261027-session-c999/mappings.json及trace-regression/result.json。原追踪5条资格命令重跑通过：ASan/UBSan、C到Python往返、7项Python测试（320模型快照）、AArch64对象/服务偏移/LR检查。历史trust-check2原字节保留。

追踪仍只覆盖LocateProtocol/HandleProtocol/AllocatePool，私有表/context必须持久。尚未接Core/profile/FV，未运行OEM PE。协议方法/MMIO/SMC/锁/SMP未验收。缺失返回仅称“本快照未观察到返回”，deadlock_established=false。

当前阻塞：现有同步像素窗口不能保证OEM不返回或改变scanout后的恢复和窗口所有权；每次服务入口回放也不能自动继承单次总预算。可靠的调用前取证出口、同句柄/精确打包PE绑定和失败状态机仍待落实。未生成新原厂实测候选。下一步先实现出口生命周期与故障验证，再接独立默认关闭profile，不能将RAM存在称已取得真实日志。

R027/S055仍paused-by-user、未执行/未消费，冻结镜像out/deferred-menu-20261027/qualification1/image.img的SHA256复核为0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a。旧preparation已过期，未来恢复须用户明确恢复实机、本次精确单次放行和当前录像条件；没有当前录像/按键待办。R022—R026已消费，不复用。

S054完整UniXNU应用单张照片人工确认保持有效；它是SimpleFb临时私有有界GOP路径，不证明OEM初始化、生产GOP、ConOut、完整BDS或实体输入。原厂嫌疑仍在构造器/主入口调用区间，未确定死锁或具体故障函数。

本轮仅新增工具/测试/文档，本地提交号由git log查询；未推送。设备仓此前交接e71a86e、主成果0c4284c和firmware 7a5c920不冒充新构建资格；原始out/影音/OEM二进制/备份不入库。共享工作区未启动第二写入者，实际firmware未修改。

详细实现、复现命令、竞争假设和反证条件见[本轮记录](operations/2026-10-27-oem-rva-and-entry-binding.md)。此前阶段记录见[追踪可信性](operations/2026-10-27-oem-trace-trust-validation.md)、[后置菜单](operations/2026-10-27-deferred-menu-firmware.md)和WORKLOG/DECISIONS。接续任务入口为[DisplayDxe交接](2026-10-27-displaydxe-handoff-prompt.md)。
