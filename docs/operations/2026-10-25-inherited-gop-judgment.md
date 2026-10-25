# D-199：S-008/S-009之后的主判断与路线修正

用户要求结合现状与公开资料给出更有力的判断。本文把已确认事实、主假设和能推翻它的结果分开；不是把未知写成硬件通过。

## 当前主判断：先修返回路径的观测缺口，再区分采集拒绝与未返回

S-008的采样正文在75秒观察期内未返回；替换为同INF/GUID/构造器的S-009常量正文后，ADB21.156秒、完成35.219秒自动回Android，独立核验原分区与备份通过。实际两FD比较72个PE，70完全相同，目标正文为唯一运行时代码变化，PcdDxe另8字节只是RSDS GUID；Core、AutoGen/库、BootShim和FAT相同。

进一步检查Core控制流后，原“正文首嫌”的因果解释需要下调：S-009仅验证了PASS返回路径。旧query1只拦PASS1，FAIL5继续dispatcher；7秒fallback只有初始CoreDispatcher正常返回后才执行。S-008也可能是谓词已拒绝，随后其他驱动挂住。这是已确认的对照混杂，不是寄存器故障证据。新源把两种精确marker都在同一完整GUID过滤的返回点结束（2/7秒），并关闭completion fallback；新模式尚待完整构建/产物资格。

S-008没有发布GOP、调用Blt或解引用帧缓冲，因此Mu绘制函数、像素alpha、Display Reserved的WT属性、XNU不是该正文直接执行的故障对象。OEM DisplayDxe在该FD中也被省略。不能仅凭两笔时序排除后续dispatcher或镜像分配布局问题，更不能定位具体寄存器。

采集层工作假设是：全量采集触碰了不需要或未确保供电/时钟的银行，造成等待或异常；目前置信度中等，须先排除“拒绝后继续dispatch”的解释。源码可确定的问题是video分支虽不使用命令刷新字段，旧采集仍无条件读两组INTF命令字段、六个PP、全部SSPP/CTL。这些读对video布局判定没有必要，330读修复因此仍应保留，但不能宣称已修好S-008根因。

固定小米/高通`sde_dbg.c`的普通寄存器转储先`pm_runtime_get_sync`，仅已知clock-enabled/IRQ上下文跳过取电源引用；取电源失败即不读。这支持“地址落在已映射范围，不足以证明可安全读取”，不直接证明S-008某个PP关闭。不能因此盲目启全部时钟或复用原生debug-bus寄存器写操作。[厂商转储代码](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde_dbg.c)

下一笔最有区分力的结果是对称返回点的FAIL报告：它将支持“前置/拓扑/格式被拒绝”，与无marker区分。对称模式仍无返回，才进一步查到达该hook之前的加载/执行、MMIO或异常。首次MMIO之前失败、ESR/FAR/ELR指向普通RAM或重定位，或故障严格跟随分配布局，也会改写寄存器假设。删除无关银行后返回只支持该修复方向，不定位唯一读。

## 默认路线有具体板级依据：2 LM、0压缩编码器、2接口

保存FDT SHA643aa3ec…34c62，primary默认K81_42_02_0a_dual_cphy_video的timing@0：`qcom,display-topology=<2 0 2>`，default-topology-index0。固定厂商`dsi_panel.c`逐项解析为num_lm、num_enc、num_intf。因此当前先核**无DSC的双LM/双INTF视频继承路径**，不应把重建DSC或复制cas的命令CTL_START置于首位。[厂商拓扑解析器](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/dsi/dsi_panel.c)

这不是当前UEFI硬件快照，不能据此宣布PP_DSC_MODE已为0；后续只对已关联的活动PP做必要验证。设备FDT明确支持source split，拓扑元组没有指定SSPP数量。现模型“两个LM必须来自两个独立SSPP”是软件支持范围，不是已确认硬件事实；源共享/跨LM矩形等情况被拒绝时不能记为设备不支持。应补有厂商依据的布局模型，不能任意把OriginMask补齐或清TOPOLOGY标志。

## 发现并修正一处真实GOP适配遗漏

cas的物理像素写入会OR上ReservedMask，使第四字节不透明；Mu FrameBufferBltLib的VideoFill只组合RGB三组掩码。原解码器沿用“允许source-alpha，GOP会写opaque”的注释，与当前Mu后端不一致。该错误可能造成未来可见性问题，不能解释尚未写像素的S-008超时。[cas实际物理写入](https://github.com/ht94911/uefi-cas/blob/893f5025cea91a121f2566730779cb34955325fb/Platforms/Xiaomi/casPkg/Library/CasDisplayLib/DisplayHardware.c)

当前修复为只准入source-alpha关闭的RGBX格式，新增回归测试；在独立实现/验证opaque适配前，拒绝alpha开启的格式。原WT映射也不是本轮失败证据，因为S-008没访问帧缓冲；UC是当前软件后端选用的准入契约，不是“板上WT配置错误”的结论。不应为掩盖当前采集问题而改缓存属性。

## 已执行的路线修正

固件d61b6ef已将运行采集改为video-only：先revision/两路timing、计数使能与active，再选活动CTL/路由，只读选中SSPP和LM。三次样本最多330读、两次100ms，最大相对偏移0x6c26c；无命令刷新、PP、闲置SSPP/CTL配置和瞬态START/FLUSH读取。显式scope掩码标出未观察字段，零占位不当硬件零值。旧全量Capture仅保留离线分析，不再由实机入口调用。

主机白名单禁止回到无关银行，330个读失败位置、等待失败、右路停滞、配置变动、前置拒绝均通过；30解码场景/267旧采集故障位置、24通道Blt和21固件单测通过。接下来完整构建/打包/资格、当前文档推送和即时恢复门禁后按授权验证新源，旧S-008/S-009 consumed，不重试。当前仍无真实GOP、可见运输报告或XNU/iPadOS启动通过，ADDRESS/TOPOLOGY保持未闭合。

原始现场影音全部只留本地。公开仅固定来源、脱敏JSON、文字和摘要。来源锁config/inherited-gop-sources.lock.json，机器审计reports/enuma-inherited-gop-policy.json，实机结果reports/enuma-inherited-video-S008-result.json、S009-result.json。


## D-204当前结果（取代前文未上机与故障排序的当前性）

2026-10-25T18:29:27+08:00。S-010已于18:26:07（UTC10:26:07.186360）执行一次临时boot，镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386，固件1a4b20487aa6ac0fbb2973bf508aea1851b61192，FD490fe01ebda7bf8091b3944a54135fb439f73c8c0f05d8ac609e7cdd19b9ba9e。全部执行前文档7d1312b已推送；即时Android/备份/相机门禁及fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过。上次GetVar异常没有重现，根因仍未知，不删除D-202原始中止记录，不放宽身份检查。

命令2.641秒返回，5.110秒观察断开，ADB25.469秒出现、39.438秒完成Android。runner未发恢复reboot；随后独立核验完成/root/A槽/解锁和boot_a/vendor_boot_a设备及本地备份摘要全部通过。270/270拍屏帧解码通过，已目视核对试前桌面、中途小米/Android启动标志及试后桌面；无UEFI/GOP文本证据。原始影音仅out/camera-capture/20261025T182550-system-transport，未录音，不上传Git/Release/CI。

本笔有受控返回，不能记为75秒无报告超时。相对S-009，ADB晚4.313秒、完成晚4.219秒，支持FAIL5/7秒终止的谓词拒绝判断，中等置信；不是直接状态日志，也不是PASS/GOP成功或精确寄存器定位。两个候选Core与采集范围不同、Android时序含噪声，不能仅凭差值确证7秒或S-008根因。S-010已consumed，S-001..010及旧失败图不重试。

按结果推进：主判断转向保守准入模型与实际继承布局不匹配，优先细分首次拒绝阶段/状态，不再默认把本笔当MMIO挂死或盲改缓存。源码要求单CTL/双LM/两个独立SSPP、无border/额外staging、严格dim/blend及RGBX；历史step21保守混合拒绝提供同方向旁证，但不是本笔快照。单源跨LM、border/合法混合、格式/几何/地址边界列为候选；描述表/PCD门禁、双接口前置/稳定性仍不能排除。只有直接取得阶段/状态或同入口对照后才能排序到具体寄存器，不放宽安全准入换通过。

新候选尚未实现/资格/执行。下一步保持同完整输入、完整GUID双结果终止及FALLBACK0，先设计可判读的首拒绝证据（同时区分未到达与已拒绝），主机故障注入和实际Core/provider审查后再构建；不恢复旧长时间编码或失败像素/value计划。若新证据显示采样/解码已全部通过或故障在入口前，则推翻当前拒绝模型主假设。真实GOP/CPU-SMMU/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合；ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更，当前无人工或审批待办。

证据：reports/enuma-inherited-video-S010-result.json；原trial out/device-tests/20261025T182553-system-transport/result.json；独立恢复out\device-tests\20261025T182657-recovery-reconciliation.json。身份解析3项、恢复核验2项、恢复硬门1项回归通过；不可变归档各文件摘要再次匹配。当前源码固件未改动，设备文档/脱敏证据单独提交推送。
