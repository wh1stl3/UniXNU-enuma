# 双路活动与帧推进：当前显示判断

S-023在固定boot-origin窗口间接支持ActiveThroughoutMask=3；S-024支持MovingMask=3。二者均自动回到Android、独立核验原分区、相机确认桌面。S-024首次fastboot查询失败发生在发图之前，按用户指令恢复并重新进入后才执行，不算两次固件启动。

当前最强工作判断：UEFI接管位置并非两个DSI接口都停止。S-024的MovingMask只有各接口三个样本均STATUS bit0活动、两个100ms窗口均非回绕递增1..64时才保留该位；因此这笔观测自身也包含采样时的活动条件。仍只是时间编码的间接推断，不能证明下游面板接收、背光、扫描地址或可见像素。

下一项信息价值最高的是ExactEnable3。若它拒绝而实际帧递增成立，结合固定小米原生v1 STATUS门控的实现，旧完整Evidence.c在计数进展之前强制Enable低两位为3就成为值得修正的准入模型；不应写寄存器强行满足该模型。若ExactEnable3成立，需保留跨启动状态变化或旧Reason5时序归因偏差的解释，不硬凑预期。

Timing非零且稳定、Enable完整字稳定仍需本机隔离；不同启动的mask不能拼成一次全条件通过。完成后再决定最小的同次稳定路由/源布局观测。完整GOP的ADDRESS与TOPOLOGY要求继续保留，旧像素试验批准不复活。固件自产图案和阶段文字才是点屏交付，计数结果不替代它。

证据：reports/enuma-native-mask-S-023-result.json、reports/enuma-native-mask-S-024-result.json；实际采集/返回指令审计见2026-10-25-native-mask-code-audit.md。原始影音仅本地out。

## S-025/S-026增量

S-025 ExactEnable3掩码0，表示两路均未在全部三个样本满足低两位==3，不是完整寄存器值0。S-026合并ActiveThroughout、非零TimingStable、EnableStable和Moving，掩码1：第一路在同次观测满足四项，第二路至少一项不足。两笔均自动回Android、独立摘要/身份核验和相机桌面通过。S-026有效负结果不是硬停，不能在此基础上进入“已证明双路完整前置”的路由采集。

下一优先假设是第二路Timing条件，而非直接宣布第二路停止。固定小米52a2f18 `sde_hw_intf.c` 399–413行的v1 get_status使用STATUS bit0并读取帧计数；389行以TIMING_ENGINE_EN判断活动的是另一实现。源SHA256仍为7b02d0b3c116279f0b4ee891cc9267d676942855d3dc58a5b263ad2f10e332da。本次只据此提出Timing条件可能过严，不能从源码证明本机Timing为0、slave角色或硬件状态。S-027拟隔离非零TimingStable，若拒绝仍需区分0与变化，不能跳过稳定性或地址/拓扑边界。
