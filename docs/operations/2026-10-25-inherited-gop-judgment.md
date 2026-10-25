# D-212当前判断：首样本计数门禁阻断后续观察

S-013/S-014互补时序支持首样本Enable门禁Reason5，后续稳定性按该路径未执行；两笔Android/root/A槽/解锁/原分区与备份独立核验通过，均consumed。下一步独立验证原生双路计数推进，不放宽GOP准入。

S-013 target1/query1于19:07:50发送1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，命令2.640秒/断开5.109秒/ADB20.078秒/完成34.343秒；S-014 target1/query2于19:09:35发送54f466c1fa0e617af343c237ac65b132d17b68640196f877c474453a86cff523，命令2.641秒/断开5.125秒/ADB26.516秒/完成41.063秒。两笔fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过，无主机恢复reboot，随后分别独立核验Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与本地备份摘要全部通过。248/248与279/279拍屏帧解码，已目视核对恢复桌面；原始影音仅out/camera-capture/20261025T190733-system-transport及190918-system-transport，无音频、未上传。

negative-minus-positive：ADB+6.438秒、完成+6.720秒，均在执行前固定的+3..+7秒窗口。支持Reason5首样本CounterEnable条件先拒绝（中等置信），不是直接原因/寄存器数值日志，也不称GOP/显示成功。跨启动继承变化和Android噪声仍可混淆；S-010/S-011/S-012的历史结果不改写。

源码路径含义：Reason5只在N=0且Timing非零、Enable&3!=3时赋值，随后立即返回；按该分类成立的前提，采样回调最多9读、零等待，完整CTL/SSPP/LM采集、Decode及后续稳定性均未到达。不能称稳定性失败、Frame不递增、某接口不活动或某个bit为零；拒绝接口与实际Enable值未知，Enable检查之后的Active条件也可能尚未执行。实际执行读数仍未知，9为条件路径上限，不当作数字转储。

当前主判断从泛化RefreshMode/稳定性收敛到过强的首样本Enable资格门：它阻断了对实际帧进展的观察。固定小米52a2f18 v1 get_status读取活动接口FrameCount不要求Enable&3==3；旧step15使能复合条件拒绝与step18原生至少一路双窗递增支持只作为同方向历史旁证，不能当本次两路数值。不能直接删条件换PASS，也不修改CounterEnable或时钟。

下一步：实现独立诊断前缀，沿原映射仅观察两路原生活动状态、Timing与Enable稳定值、两窗各1..64非回绕Frame增量；不把Enable是否精确3作为其提前返回条件，不访问尚未证明安全的后续管线银行、不发布GOP。该前缀是新的独立观测，不等于放宽完整EnumaSampleVideo准入；成功后才评估有依据的原生资格修正，失败再细分活动性/稳定性/计数进展。新前缀尚未实现/构建/资格/上机，完整采样所有原条件保持。若新证据显示原因非5、两路不活动/不稳定或CounterEnable实际已满足，应修正当前判断。

新增Detailed接口保留旧入口语义：固定8710ebd oracle覆盖330失败位置和成功的完整回调/等待顺序、返回状态、Out字节；首/后续计数、初始接口、等待、配置变动及Frame停滞原因用例通过，164选择器场景、24固件和4配对解析回归及AArch64对象通过。实际两FD/PE/宏/R-004/完整FAT/BootShim不可变资格通过，实际Core可执行段与已审查S-010相同，provider仅三条映射指令差异已人工审查并摘要绑定，现场运行前提交均已推送（d6c9dfa资格、f399374首笔结果）。

证据reports/enuma-video-counter-S-013-result.json、S-014-result.json、pair-result.json、path-interpretation.json，enuma-video-reason-code.json及pair-code.json；源码b93b3bb已推送。S-001..014及旧失败图不重试，当前无人工/审批待办。

## 以下历史判断的当前性由D-212取代

# D-208当前判断：互补支持非Topology，优先隔离计数前置

S-011与S-012互补两笔均已执行并consumed。S-011(query1)于18:45:34发送4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7，命令2.625秒/断开5.093秒/ADB26.484秒/完成40.547秒；S-012(query2)于18:47:15发送4454dfaa0b00d08d277e921641b51b250850906236770d6514f97cca51f54389，命令2.640秒/断开5.109秒/ADB20.062秒/完成33.781秒。两笔fastboot机型/槽位/解锁首轮精确通过，均无主机恢复reboot、受控回Android，随后各自独立完成/root/A槽/解锁与boot_a/vendor_boot_a设备及本地备份摘要核验通过。278/278与245/245帧解码，已目视核对恢复桌面；全部原始拍屏/视频只留本地out/camera-capture/20261025T184517-system-transport及184658-system-transport，无音频、未上传。

negative-minus-positive的ADB差-6.422秒、完成差-6.766秒，均在执行前固定的-7..-3窗口，支持首个有效状态非Topology13。不是直接状态日志，不能据此称拓扑合格或GOP通过；非Topology集合包含成功状态0和错误1..12，跨启动状态变化仍可混淆。因此D-204“拓扑模型首嫌”优先级下调，不能继续把两个独立SSPP/边框作为已定位故障，更不改相关准入来凑PASS。

进一步固定源码/历史审查：小米52a2f18 sde_hw_intf_v1_get_status仅以INTF_STATUS bit0读FRAME_COUNT，不要求Enable&3==3；历史step15该复合使能前置拒绝，而step18保留使能值稳定并观察至少一路双窗递增获得支持。当前Evidence.c又在首样本和稳定性中对两路强制Enable&3==3，是比原生状态路径和历史成功谓词更强的条件。此为已确认的软件/历史差异，不是本次计数使能数值或确切拒绝点；当前领先假设转为RefreshMode10类的接口/计数前置或稳定性，置信中等。元数据/PCD、revision/mode/格式/几何/地址等拒绝以及成功0仍未排除。

下一步先以新候选区分RefreshMode10及互补，必要时再分首次接口资格和后续等待/稳定性；取得分类后才依据原生status/实际递增评估精确谓词修正。不直接删除Enable门禁、放宽双链路或回旧失败图。若结果非RefreshMode10或直接counter资格已满足/采样成功，应推翻该首嫌排序。新RefreshMode候选尚未实现/构建/资格/执行；本轮新增软件、两份完整资格、互补实测与离线审查均完成，S-001..012不重试，当前无人工/审批待办。

机器证据：reports/enuma-video-topology-S-011-result.json、S-012-result.json、pair-result.json、enuma-video-topology-code.json、enuma-video-topology-pair-code.json，以及enuma-video-counter-gate-review.json。固件8710ebd已推送，实际两Core可执行段与已审查S-010相同，provider仅三条结果指令差异，完整输入保持；55生产选择器场景、330读失败与GOP/拓扑主机和AArch64对象检查、23固件回归与3配对解析回归通过。

## 以下为历史分析，首嫌排序与当前性由D-208取代

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
