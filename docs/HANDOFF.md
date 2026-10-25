# 当前状态：D-199，S-009自动返回支持正文故障，按公开板级事实修正采集

2026-10-25T17:50:01+08:00。S-009（固件c7c29bb、镜像56eb63dc…89a00c7）17:21:50临时启动一次，命令2.641s返回、断开5.110s、ADB21.156s、完成35.219s，自动回Android并独立核验完成/root/A槽/解锁/两个原分区与本地备份摘要通过。252帧主录像/解码一致，原始影音仅本地，无音频。当前无人工/审批待办。S-001..009已执行镜像全部consumed，不重试。

S-008（898ae25、f8f14e3b…33a4dc8）此前75秒超时，用户恢复后17:08独立核验通过，451主/740恢复帧只留本地。两笔实际FD72PE比较70完全相同，目标正文为唯一运行时改变，Pcd另8字节仅RSDS GUID；Core、AutoGen/库、BootShim/FAT相同。当前主判断：继承态采集正文为首要故障对象，过宽MMIO读取/供电时钟前置不足为中高置信机制假设，未定位具体寄存器。S-008未调用Blt或访问帧缓冲，不能把超时归因到GOP绘制、alpha、帧缓冲WT或XNU。

公开原生sde_dbg常规dump先取runtime power引用，cas按完整命令模式字段采集；这不能直接迁到enuma的视频继承态。本机保存默认panel拓扑2/0/2，经固定厂商解析器核为2LM、0压缩编码器、2接口；无DSC双路继承应先于DSC重建/命令CTL_START。该配置没有指定两个独立SSPP，现模型的两SSPP限制仅软件支持范围，不是硬件事实。PP/下游实际连接仍需同次证据，不能清TOPOLOGY。

已修正软件：最新固件d61b6ef6c990eed795910754d34a588d37841d4e已推送，运行采集改为video-only，只读选中CTL/SSPP/LM，去掉命令刷新、全部PP和闲置管线字段；最多330读/两次100ms，最大偏移0x6c26c，显式scope掩码区分未读与硬件零。330故障位置/严格读取白名单、30解码/267旧采集故障、24通道Mu Blt和21固件单测通过。另修正source-alpha与Mu reserved-byte填色不兼容的准入，当前拒绝alpha开启格式，不冒充opaque写入。原内存/verified/分区字段不改。

真实GOP后端已有实际Mu Blt主机、AArch64和固定8d85d39完整UEFI/QEMU RAM执行通过，不是物理GOP成功。当前UC只是后端所选软件契约，原WT并非本轮失败证据，不能为掩盖采集问题随意改缓存属性。CPU/SMMU地址、下游拓扑、物理GOP和可见错误通道仍未闭合。

当前正在为d61b6ef重新完整构建；新330读候选尚无新FD/打包资格，未发出S-010，generic旧c7构建/旧资格仅历史，不可按新pin执行。下一步构建/实际PE/宏/R-004/完整FAT/不可变资格、当前文档发布和即时身份/备份/相机/恢复后直接按授权单笔；75秒超时停止追加先恢复。原始影音只out/本地，不传Git/Release/CI。

详见operations/2026-10-25-inherited-gop-judgment.md、inherited-gop-backend.md，reports/enuma-inherited-video-S008/S009-result.json、enuma-inherited-gop-policy/host/qemu.json。当前Android核验通过，无新硬停/审批。框架pin5fdbd5d和完整96MiB FAT保持，13项运输、XNU/iPadOS及PMGR/UFS/root/Data仍未实机闭合。
