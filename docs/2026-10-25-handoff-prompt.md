# 当前状态：D-197，S-008超时后Android恢复核验通过，继续离线隔离

2026-10-25。S-008于17:05:25临时boot一次，镜像f8f14e3b1ec0b5a097d938b55ed85123e913d16392e42cd3f981419e333a4dc8，固件898ae25。命令2.641s返回0，USB断开5.109s；75秒观察期没有自动返回，停止追加并consumed。用户长按恢复Android，17:08:12左右独立核验sys.boot_completed/root/A槽/解锁、原boot_a/vendor_boot_a和本地备份摘要一致，恢复停点解除。失败原始result.json未改写。原S-001..008均不重试。

451帧主录像/451解码一致，740帧恢复录像/740解码一致，均仅本地out/，OpenCV未采音。末帧无可读固件文字（强反光暗屏）；没有可判读marker、GOP或XNU结果，不能证明已进入采样正文，更不能把超时定位为某寄存器或GOP失败。公开证据reports/enuma-inherited-video-S008-result.json，含本地影音路径/摘要及独立恢复核验；不上传原始影音。

真实InheritedGopLib后端软件仍有效：实际Mu FrameBufferBltLib主机ASan/UBSan、24字节排列/四Blt/清屏/溢出/失败清理通过；固定8d85d39完整UEFI链接与QEMU RAM执行输出ENUMA_GOP_SELFTEST PASS RAM ONLY。它不发布协议、不触碰物理显示，不是enuma GOP成功。29解码场景/267原采集故障、144全LM离线适配器故障、最终969运行采样故障及20固件单测通过。硬件下游和CPU地址关系仍未闭合。

S-008只读入口使用现有SimpleFb INF/GUID/Core-warning传输，但正文不发布GOP、不调用像素后端。三个快照、两路计数、两个活动LM、两次100ms、969读在离线通过；实际FD/PE/编译宏/R-004映射/完整96MiB FAT和boot-v3不可变资格通过。实机超时不能推翻软件单测，也不能把离线输入当实机快照。成功仍保留ADDRESS/TOPOLOGY；原Display Reserved为WT，不满足当前UC后端契约，不能清标记发布协议。

主判断：当前最值得先排除的是入口/返回通道与正文访问之间的边界（中等置信度）。实际构造器仅BaseDebugLibSerialPortConstructor和UefiBootServicesTableLibConstructor，SerialPortLibNull已核；无PSCI/reset构造器。源码正文还包括内存表查询、所有SSPP/CTL/PP快照及两个选中LM读取，所以不能只归因于OEM DisplayDxe或某个LM寄存器。寄存器银行/未活动PP等读取导致异常或等待是有根据的候选，但尚未被隔离。

下一步自动离线实现同一入口、同INF/构造器/完整输入的无MMIO、无内存表查询常量PASS对照；检查实际PE指令，完成新源构建/打包/资格和全部文档发布后再按即时门禁单笔。该对照是新的故障隔离，不复活旧value/R-005或重试S-008。若仍失败，优先查构造器/Core返回/早于入口的执行；若对照可控返回，再收缩最早读取集合，不能扩读或像素写入。

当前无人工/审批待办，符合用户恢复后继续离线规则。所有新boot仍须源码/资格/当前文档推送、即时身份/备份/相机/恢复门禁；75秒超时立即停止追加。无board/bringup-plan内存字段、verified、flash/erase/改槽变化。框架pin5fdbd5d/完整系统输入保持，13项运输/GOP/XNU/iPadOS可见实机结果与PMGR/UFS/root/Data仍未闭合。

详见operations/2026-10-25-inherited-gop-backend.md与GOP host/qemu/policy/video-qualification报告。最后已发布根仓68ddbd8、固件898ae25；本记录随后独立提交推送。
