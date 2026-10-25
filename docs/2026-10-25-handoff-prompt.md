# 当前状态：D-196，S-008只读双链路候选已资格，文档发布后执行

更新时间2026-10-25T17:04:20+08:00。用户授权条件满足直接上机，原始影音本地。固件源898ae255e95cb53733250b26b647bb59757f86aa已推送，根仓source lock/gitlink同步。当前S-008尚未发出；旧S-001..007均consumed，不重试。当前Android完成/root/A槽/解锁和原boot_a/vendor_boot_a及本地备份摘要刚经独立复核通过（reports/enuma-recovery-reconciliation.json）；相机1920x1080可用，旋转后已核屏幕。

真实InheritedGopLib后端已实现并通过主机ASan/UBSan、AArch64编译、实际UEFI链接及QEMU RAM自测。QEMU固定源8d85d39、EFI cc320e24…dadbd93，输出ENUMA_GOP_SELFTEST PASS RAM ONLY；不安装协议、不访问物理显示，不是enuma GOP通过。主机实际复用Mu FrameBufferBltLib，24通道排列、四类Blt、清屏/guard/溢出/分配失败/归属失效通过。29纯解码场景、267原采集故障、144全LM离线适配器故障和最终969运行采样故障位置通过，20项固件单测通过。

S-008是完整96MiB FAT输入的只读取证，不发布GOP、不调用像素后端。固定新入口代替metadata SimpleFb正文，原INF/GUID/Core-warning路径保留；OEM CPR/Display/UFS按明示诊断模式省略。实际PE与staging/source/编译宏相同，实际FD含精确R-004映射表记录。先核活动video CTL/两路计数使能，再读两个选中LM；闲置LM混合不读。三个同次快照、两窗100ms、最多969读、最大偏移0x73830；要求两路无回绕进展、布局/staging/blend稳定、完整覆盖。按LM right bit判角色，不按编号猜。

候选镜像SHA256：f8f14e3b1ec0b5a097d938b55ed85123e913d16392e42cd3f981419e333a4dc8，103817216字节；FD：fe052cda49df0113c92d883479ad0841fcb1bc1191a4727083a20f59bbf7b9b3；BootShim+FD：870d793c6f52aed371311dff2a1a4c80081259effb495bd62f86ee97bfb0a8b1；FAT：49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773。不可变归档out/inherited-gop/qualified-video-898ae25-q1，资格reports/enuma-inherited-video-qualification.json；离线runner检查通过。中间构建不用于上机，898ae25最终重新构建已通过staged-source相等性。

本次文档提交推送后，重新即时核身份/备份/恢复并按已有授权单笔临时fastboot boot。PASS warning选2秒Core gate，拒绝可能7秒dispatcher fallback；单笔时序只是支持，不唯一证明命中或具体值。75秒主机超时立即consumed、停止追加并优先既有长按恢复；不是固件保证自动返回。恢复后核Android/root/原槽/解锁/原分区摘要，自动离线分析，不重试同图。

物理GOP尚未恢复：新采样成功仍保留ADDRESS/TOPOLOGY，CPU/SMMU地址关系、UC缓存政策和LM→PP/DSC→INTF下游关联未闭合；原Display Reserved仍WT，不能清标记发布协议。无board/bringup-plan内存字段、verified、flash/erase/改槽变更。当前无新人工或审批待办；原始影音只out/本地，不上传Git/Release/CI。

详见operations/2026-10-25-inherited-gop-backend.md、enuma-inherited-gop-host/qemu/policy与video-qualification报告。框架pin5fdbd5d及完整系统输入保持；13项运输/GOP/XNU/iPadOS实机可见结果仍未闭合，PMGR/UFS/root/Data仍开放。
