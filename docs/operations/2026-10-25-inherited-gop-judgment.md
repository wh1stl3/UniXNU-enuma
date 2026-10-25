# D-199：S-008/S-009之后的主判断与路线修正

用户要求结合现状与公开资料给出更有力的判断。本文把已确认事实、主假设和能推翻它的结果分开；不是把未知写成硬件通过。

## 主判断：先修继承态寄存器采集，通用GOP不是当前第一故障对象

S-008的采样正文在75秒观察期内未返回；替换为同INF/GUID/构造器的S-009常量正文后，ADB21.156秒、完成35.219秒自动回Android，独立核验原分区与备份通过。实际两FD比较72个PE，70完全相同，目标正文为唯一运行时代码变化，PcdDxe另8字节只是RSDS GUID；Core、AutoGen/库、BootShim和FAT相同。

这是优先收敛到正文的有力因果对照。S-008没有发布GOP、调用Blt或解引用帧缓冲，所以不能把此次超时归因于Mu绘制函数、像素alpha、Display Reserved缓存属性或iPadOS/XNU。OEM DisplayDxe在该FD中被明示省略，也不是这笔试验直接执行的故障对象。镜像/PE大小及分配布局变化仍是替代解释，因此“具体哪一次读阻塞”尚未确认。

首位工作假设是：把适用于cas的全量寄存器采集搬到enuma继承态，触碰了不需要或未确保供电/时钟的银行，造成MMIO等待或异常；置信度中高，机制未实证。源码可确定的问题是video分支虽不使用命令刷新字段，旧采集仍无条件读两组INTF命令字段和六个PP，并读全部SSPP/CTL。这些读对本次video布局判定没有必要。

固定小米/高通`sde_dbg.c`的普通寄存器转储先`pm_runtime_get_sync`，仅已知clock-enabled/IRQ上下文跳过取电源引用；取电源失败即不读。这支持“地址落在已映射范围，不足以证明可安全读取”，不直接证明S-008某个PP关闭。不能因此盲目启全部时钟或复用原生debug-bus寄存器写操作。[厂商转储代码](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde_dbg.c)

可推翻/改写主判断的观测：同入口在首次MMIO之前仍失败；有ESR/FAR/ELR指向栈、普通RAM或重定位；或确认所有所读银行可达而故障仍严格跟随PE分配布局。反之，删去无关银行后恢复可控返回，会支持采集范围判断，但不定位唯一寄存器。

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
