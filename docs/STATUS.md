# 当前状态：D-194，继承扫描输出解码适配已实现，GOP尚未恢复

用户要求优先恢复真实GOP/可见错误通道。本轮已实现固件InheritedScanoutLib（源e6d1867（组件首笔0080640）），仅纯解码和回调采集，未接入DSC/FDF、未发布GOP、未构建新FD/boot或上机。旧S-007 consumed，最近完整Android/root/A槽/解锁/原分区与备份摘要核验为16:06:22。当前无人工或审批待办，原始影音本地。

已明确关键板差：enuma保存FDT的默认K81双CPHY为video模式、每链路800x2560；本机只读Android DRM记录1600x2560视频模式，不是当前UEFI扫描输出证明。cas命令模式/CTL_START策略不直接采用。新解码器使用显式宽高/splash边界/mode及每pipe局部→全局原点，未知原点拒绝，支持分块完整覆盖与严格格式/范围检查。成功仍保留活动性、混合/遮挡、CPU地址关系、刷新、拓扑五项要求，不允许清标志换协议。

生产代码28个ASan/UBSan解码场景、267个回调失败位置通过；freestanding AArch64对象无外部未定义符号。Capture最多267回调、最大偏移0x73830，无direct MMIO/pixel指针及任何硬件写入。测试是合成快照，不是实机寄存器、完整UEFI链接或GOP通过。来源、SHA、许可均固定，未复制cas平台内存/面板/物理Blt/刷新逻辑。firmware源e6d1867（组件首笔0080640）已推送，源锁/gitlink同步，原board/plan未改。

下一步接真实GOP后端及同次UEFI快照/双链路原点判定：复用FrameBufferBltLib，核活动和稳定路由、混合、splash访问与视频刷新条件，再生成可审查完整载荷候选；不得发布假成功GOP或重复失败旧镜像。R-004映射仍为staging精确补丁，未来实际FD必须重新审核，原迁移表缺MDP不能当新映像已具备映射。当前尚无可直接填入OriginMask的实机拓扑记录，且五项运行条件仍未闭合。

详见operations/2026-10-25-inherited-gop-offline.md、reports/enuma-inherited-scanout-host.json、enuma-inherited-scanout-inputs.json。本轮只做Android身份/DRM只读查询，没有新boot/像素/MMIO/分区写入。D-193官网复审主线保持：真实GOP/可见错误优先，OEM深层早停转备用，通用RAM驱动/QR与schema2迁移分开评估。构建基线尚无0080640对应新完整镜像，既有cb9e568实测归档仅历史且均consumed。

没有board/bringup-plan内存字段、verified、flash/erase/改槽变化，R-002/R-015/像素硬边界保持。仍无13项运输/GOP/XNU/iPadOS实机通过，PMGR/UFS/root/Data未闭合。本阶段离线完成不等于最终目标完成。
