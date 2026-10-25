# 当前状态：D-198，S-009同入口无MMIO常量对照已资格，发布后执行

2026-10-25。S-008于17:05:25临时boot一次，镜像f8f14e3b1ec0b5a097d938b55ed85123e913d16392e42cd3f981419e333a4dc8，固件898ae25。命令2.641s返回0，USB断开5.109s；75秒观察期没有自动返回，停止追加并consumed。用户长按恢复Android，17:08:12左右独立核验sys.boot_completed/root/A槽/解锁、原boot_a/vendor_boot_a和本地备份摘要一致，恢复停点解除。失败原始result.json未改写。原S-001..008均不重试。

451帧主录像/451解码一致，740帧恢复录像/740解码一致，均仅本地out/，OpenCV未采音。末帧无可读固件文字（强反光暗屏）；没有可判读marker、GOP或XNU结果，不能证明已进入采样正文，更不能把超时定位为某寄存器或GOP失败。公开证据reports/enuma-inherited-video-S008-result.json，含本地影音路径/摘要及独立恢复核验；不上传原始影音。

真实InheritedGopLib后端软件仍有效：实际Mu FrameBufferBltLib主机ASan/UBSan、24字节排列/四Blt/清屏/溢出/失败清理通过；固定8d85d39完整UEFI链接与QEMU RAM执行输出ENUMA_GOP_SELFTEST PASS RAM ONLY。它不发布协议、不触碰物理显示，不是enuma GOP成功。29解码场景/267原采集故障、144全LM离线适配器故障、最终969运行采样故障及20固件单测通过。硬件下游和CPU地址关系仍未闭合。

S-008只读入口使用现有SimpleFb INF/GUID/Core-warning传输，但正文不发布GOP、不调用像素后端。三个快照、两路计数、两个活动LM、两次100ms、969读在离线通过；实际FD/PE/编译宏/R-004映射/完整96MiB FAT和boot-v3不可变资格通过。实机超时不能推翻软件单测，也不能把离线输入当实机快照。成功仍保留ADDRESS/TOPOLOGY；原Display Reserved为WT，不满足当前UC后端契约，不能清标记发布协议。

主判断：当前最值得先排除的是入口/返回通道与正文访问之间的边界（中等置信度）。实际构造器仅BaseDebugLibSerialPortConstructor和UefiBootServicesTableLibConstructor，SerialPortLibNull已核；无PSCI/reset构造器。源码正文还包括内存表查询、所有SSPP/CTL/PP快照及两个选中LM读取，所以不能只归因于OEM DisplayDxe或某个LM寄存器。寄存器银行/未活动PP等读取导致异常或等待是有根据的候选，但尚未被隔离。

S-009新对照已实现、完整构建和冻结资格，尚未发出。固件c7c29bb0fe8f2bbf6f8128689b7f423da7dcc72c已推送；同INF/GUID/构造器/编译配置/完整输入，仅正文变为常量PASS，无查表/MMIO/像素/分配/等待/协议发布。镜像56eb63dc63bc7e4b76e6746cb42a0f05b25dfa08099b356f63117c8af89a00c7，FD c87f3d1d296ef09679acf6c6887f34c9c892fbb720fc8005d3562fce35c4b28e，103817216字节；归档out/inherited-gop/qualified-control-c7c29bb-q1，报告enuma-inherited-video-control-qualification.json。正常入口PE为0x1050..0x10dc：保存Image/ST/gBS、非空断言、mov w0,#1/ret；审查完整text时已覆盖链接填充，不在第一段无效字节处提前停止。正常路径不调用查表/读取或服务。实际反汇编SHA 401ebe34396c099a60c8a2e9fe0d0bf031c706da714d11870f6071e277763d9e已绑定，runner拒绝未审查控制产物。

与S-008实际FD比较72 PE，70个完全相同；仅SimpleFb正文为运行时代码变化，另PcdDxe8字节仅RSDS GUID，其他字节相同。Core、AutoGen/库清单、BootShim/FAT相同；21项固件单测通过。现在文档推送后，重新即时身份/备份/相机/恢复门禁，按原授权S-009单笔；75秒超时立即停止追加并先恢复，旧S-008不重试。常量PASS应选2秒Core gate，但返回时序只作支持。若它也失败，优先构造器/Core/前驱路径；若可控返回，再收缩最早读取集合，不能直接放宽GOP要求。

当前无人工/审批待办，符合用户恢复后继续离线规则。所有新boot仍须源码/资格/当前文档推送、即时身份/备份/相机/恢复门禁；75秒超时立即停止追加。无board/bringup-plan内存字段、verified、flash/erase/改槽变化。框架pin5fdbd5d/完整系统输入保持，13项运输/GOP/XNU/iPadOS可见实机结果与PMGR/UFS/root/Data仍未闭合。

详见operations/2026-10-25-inherited-gop-backend.md与GOP host/qemu/policy/video-qualification报告。S-008结果已发布根仓ca94361；本次当前文档与S-009资格随后独立提交推送。
