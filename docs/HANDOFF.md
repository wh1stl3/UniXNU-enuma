# 当前：DisplayDxe离线归因推进，实机暂停

本对话现在仅在D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display写入（从97ef242建立的单个原生Git worktree）。原主线D:/Code/PortingiOS/enuma/UniXNU-enuma留给共享工作区，保持不改。这里已生成两个默认关闭的vendor profile，各102文件且只有精确DisplayDxe不同；8项实际树破坏/身份/输出拒绝检查通过。详见[隔离工作区记录](operations/2026-10-27-oem-display-worktree.md)，最终证据out/oem-profile-check2-20261027-c999/result.json。

尚未接构建器/Core或完成板级出口，未打包/上机。构建锁config/uefi-source.lock.json目前指向8680ea79，固件子模块为11c6cf1；不绕过原适配器，下一步在隔离树审查并建立新的开发锁和默认关闭profile选择。当前profile暂存不是固件构建资格，R027继续冻结。

已收敛为enuma可应用的离线实验补丁与方案：新增prepare_enuma_mmu_experiment.py，仅将精确OEM PE的0x1994参数2改0，保留全部构造器、MDPSetupPipe/MDPPanelInit及错误检查；独立输出PE摘要ed37a4e137cca2fcf4d5fa5718e18a319c2aa1b7a1cfab480693325bfbe2b5e3。新增plan_enuma_panel_handoff.py导出本机K81两链各188条命令及原等待契约，不改原XML。16项静态/宿主检查通过，见out/enuma-display-application-20261027-c999/check2/result.json。没有固件打包或硬件成功结论；新PE尚未接Core/profile/变体认证及板级可靠出口。具体使用、接线、判别与限制见[应用方案](operations/2026-10-27-enuma-display-application-plan.md)。R027仍冻结；此实验PE不替换生产vendor目录。

最新静态推进：按公开Qualcomm解释器展开K81序列，两条控制器各188条相同数据，分链11不能当冗余删除；延迟仍与Android不同。nabu参数2→0关联MMU/SID初始化位，enuma对应LocateProtocol返回RVA为0x1bce0、GUID为54b6d3b4-5d33-4f91-8600-6c41d5deb19a，后续四处协议方法调用尚不在包装器覆盖内。phase2/transport-flags-result.json记录摘要/指令检查和两项模型负例；无硬件执行或补丁应用。

2026-10-27。用户最新报告实机ADB已恢复；本轮未独立查询，不将用户报告扩大为Android完成/root/原分区核验。没有设备启动/部署、录像申请或nuwa操作，R027继续冻结。

新增两路公开实现分析：elish/enuma CSOT同屏有Linux补丁及MiCode来源支持；K81初始化数据归一化后188条顺序相同，XML另有一条11及不同控制/等待记录，未证明执行等价。nabu原版/补丁版DisplayDxe差分36字节；三个初始化调用角色已静态映射至enuma的0x1998、0x176c4、0x176e8。未移植补丁，不代表本机已到达这些函数。详见[两路分析](operations/2026-10-27-elish-nabu-display-paths.md)，二进制及差分仅保留独立out目录。

本轮实现预选call的一次性调用前导出：真实入口记入RAM后恢复TPL，输出带session/call身份与完整性值的冻结快照，再转发原服务。失败/重入/TPL拒绝/计数耗尽/中断分开锁存，无自动重试，不改变原服务返回状态或输出。新增持久缓存的320×160/8秒像素后端，窗口恢复完成才转发；恢复未确认进入非返回Stop，不伪造驱动结果。默认无observer、无Core/profile/FV激活。

证据out/oem-precall-20261027-c999/final1/result.json：两个ASan/UBSan程序、两个AArch64对象，调用顺序及6项删除负测通过，像素函数自身栈帧112字节。宿主进程先fsync完整快照，再进入有独立见证的不返回原服务；终止进程后外部文件仍可解码。749种截断/改字/重复/错身份拒绝。像素故障覆盖写前/写后、保存/恢复/屏障/hold/所有权重验、异常和24种通道排列。原追踪5条命令（7项Python/320快照）新目录回归通过。旧证据不覆盖。

已消除输出必须等待原服务返回的依赖，但板级可靠出口尚未验收：像素回调仍为宿主RAM模型，尚需当前CPU/路由/独占窗口验证、物理回调、异常/非返回终止恢复策略及精确Core句柄/PE/FV接线，之后才能独立profile完整构建。result5只证明CPU事务，不证明实际可见或相机采集；像素页仅含选定事件摘要，不是完整文本快照。没有执行OEM PE、生成新板级候选或新增硬件资格。只覆盖三项Boot Services，首次服务之前/协议方法/MMIO/SMC/锁/SMP未覆盖。预转发入口不证明原服务本体执行，缺失return仍不建立死锁。

上一轮精确PE的BL/BLR归因工具与Core入口源码检查保留，详见2026-10-27-oem-rva-and-entry-binding.md。新preservation.json确认R027镜像、资格及2434项执行源码绑定不变。

R027/S055仍paused-by-user、未执行/未消费，冻结镜像out/deferred-menu-20261027/qualification1/image.img的SHA256复核为0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a。旧preparation已过期，未来恢复须用户明确恢复实机、本次精确单次放行和当前录像条件；没有当前录像/按键待办。R022—R026已消费，不复用。

S054完整UniXNU应用单张照片人工确认保持有效；它是SimpleFb临时私有有界GOP路径，不证明OEM初始化、生产GOP、ConOut、完整BDS或实体输入。原厂嫌疑仍在构造器/主入口调用区间，未确定死锁或具体故障函数。

本轮固件组件本地提交11c6cf1，设备仓提交号由git log查询；未推送。设备仓此前交接e71a86e、主成果0c4284c和firmware 7a5c920不冒充新构建资格；原始out/影音/OEM二进制/备份不入库。共享工作区未启动第二写入者，仅修改本轮三个追踪/出口头文件；旧像素事务和R027执行源未改。

详细实现、复现命令和失败边界见[本轮记录](operations/2026-10-27-oem-precall-capture.md)。此前阶段记录见[追踪可信性](operations/2026-10-27-oem-trace-trust-validation.md)、[后置菜单](operations/2026-10-27-deferred-menu-firmware.md)和WORKLOG/DECISIONS。接续任务入口为[DisplayDxe交接](2026-10-27-displaydxe-handoff-prompt.md)。
