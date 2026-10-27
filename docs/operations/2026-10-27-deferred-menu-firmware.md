# D-319：驱动正常返回后启动完整菜单（R027离线开发）

S054独立照片判读已获用户“正确”确认；新增 reports/enuma-full-menu-S-054-confirmed.json，历史结果、原媒体与资格不回写。R026已消费。

本版将菜单从SimpleFb驱动入口移至DXE调度器的CoreStartImage返回之后。驱动仅保存静态拥有的帧描述、在自身加载句柄注册私有单次服务并返回EFI_SUCCESS。Core原point13先记录真实驱动返回；新的调度调用核对完整SimpleFb GUID、实际句柄、ABI/Owner和快照末条真实成功记录后才调用服务。子应用此时已不处于EnumaStartingImage桥接窗口，不能冒充父驱动状态。菜单结果写point28，不能称为SimpleFb StartImage返回。当前通用文本回放仍将未知point28作为checkpoint，尚未接入该结果的屏幕数值显示。

服务保存静态帧副本，后续同步调用才建立回调上下文，没有驱动入口栈地址逃逸；先重验EL1/整帧identity-WT，再沿原生路由重验和同一800×600窗口事务。配置中的可见标题为Driver returned - Return to firmware，只在真实返回证据门控后显示。保持8秒、scale1、原MDP/像素/屏障预算、requirements22、只读私有配置、exit唯一动作、应用host与ConnectAll关闭。

这是正常驱动生命周期的一个推进，不是已打通全部DXE/BDS：仍在精确SimpleFb边界停止，未启用OEM DisplayDxe/UFSDxe/CPRDxe，未接实体输入、XNU、QR或生产GOP。Core正常驱动返回会先执行既有CoreConnectHandlesByKey；此处仅新增私有协议到实际驱动句柄，不主动调用全局ConnectAll。如该段在实机阻塞，应按超时恢复并记录，不能把无菜单推断成显示故障。

离线过程：qemu1因新类型名与编译开关同名失败，已改为ENUMA_DEFERRED_MENU_PROTOCOL；qemu2通过并保存完整图像。host1的ASan可执行程序退出-11且无诊断，不记为通过；host2改为与其他宿主测试一致的非PIE链接后，ASan/UBSan 46案例及24通道排列通过。原失败目录保留。新Provider测试验证离开注册栈后可运行、无提前绘制、坏返回/CPU策略拒绝、单次消费和注册失败不重试；Core测试验证精确owner/快照、单独point28、失败时不继续调度。

01:48只读前检：之前绑定的enuma未以已授权ADB在线，未启动或改写设备。继续离线工作，实测时必须重新核对当前身份/备份/恢复条件与录像。

构建、最终应用QEMU、机器码、包资格和单次绑定尚在完成中，不预写通过；最终状态以STATUS/HANDOFF及后续本节追加证据为准。无提交推送、权限变化、旧资格覆盖或nuwa操作。


## D-320最终离线结果（取代本页开发中的待验证项）

S054照片独立判读已获用户“正确”确认，reports/enuma-full-menu-S-054-confirmed.json新增保存。R026/S054已消费，Android恢复及原分区核验已于01:28通过；照片不证明8秒时长或逐字像素恢复。

R027/S055新候选已构建并打包：out/deferred-menu-20261027/qualification1/image.img，SHA256 0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a。FD SHA256 be202be3a041e59cf7062ba9ef6e698066aa10b0bcf3ffc93763db2bad095d28；资格e82028edad3baf06c3a4fd919d61c650da79e09b1d1bd5056402acb198a02af9。来源为当前未提交工作树的显式快照，基准8680ea79d6fd14d4526d314f430e9812955cb78a不能冒充本镜像干净提交。

行为：SimpleFb先在自身加载句柄发布拥有静态帧描述的私有单次服务，真正返回EFI_SUCCESS；Core记录原point13并清空当前驱动桥接身份后，核对完整GUID/实际句柄/Owner/ABI/末条成功快照，再启动完整UniXNU应用。菜单结果单独写point28，不冒充驱动返回。可见项Driver returned - Return to firmware。继承原(64,96)800×600、8秒、scale1、全部物理预算及保存/恢复/反读，仍为应用host、只读私有配置和唯一exit动作。

离线已完成：完整FD编译01:51:23完成（编译2分06秒）；最终新应用QEMU 27命令通过，真实配置/菜单/退出及VM全窗恢复通过；host ASan/UBSan 46案例、24通道排列；入口/范围/单次绑定79测试；实际DxeCore/SimpleFb机器码审查和5项删除指令负测通过；新旧物理访问回调584字节一致；Boot v3+AOSP往返/96MiB FAT通过。R022—R026旧资格及文件摘要通过保护校验。源码、机器码、测试及包绑定见out/deferred-menu-20261027/execution-review.json，准备入口scripts/r027_preparation.py和scripts/run_deferred_menu_trial.py默认仅离线。

当前实际条件：01:48只读检查发现之前绑定enuma未以已授权ADB状态在线。之后未重启、推送、刷写、改槽或查询其他设备。新R027未消费、未获当前单次实机放行或录像确认。机器应连接并进入Android、允许此电脑USB调试；届时重跑身份/root/A槽/解锁和分区/备份检查，仅在明确R027一次临时boot及当前录像就绪后执行。75秒观察，无返回停止追加并沿原恢复路径处理，不复用任何旧授权，不套旧R024返回码时间窗口。

尚未完成：全部DXE/正常BDS、实体按键、生产GOP、XNU、QR与全局DEBUG/ConOut实机日志。R027推进的是驱动返回与菜单启动的生命周期边界，不能称完整BDS已通。point28目前留在RAM日志，尚未接到屏幕数值回放。服务前CPU策略与原生路由重验保留；requirements22不变，stage2/SMMU/alpha仍未证明。

下一步只剩现场门禁和拍摄本次新候选。录像覆盖完整屏幕及后续恢复；媒体保存D:/Code/PortingiOS/enuma/Media-enuma/S-055-R027。助手先独立保存并公布判读，用户核对后再归因。不自动提交推送；迁移改动和历史证据原字节保留。详细实现、失败测试及风险见docs/operations/2026-10-27-deferred-menu-firmware.md；报告reports/enuma-deferred-menu-development.json。
