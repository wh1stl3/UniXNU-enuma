# 当前状态：D-202，S-010身份门禁中止，未发送镜像；Android已核验恢复

2026-10-25T18:23+08:00。S-010准备流程在fastboot身份门禁中止：首个product查询返回enuma，current-slot/unlocked及后续完整查询失败，部分remote FAILED仍返回主机退出码0，精确值检查正确拒绝。未执行fastboot boot，镜像24aed9e0…ae9e2386未消耗；不能记为固件超时、PASS或FAIL。is-userspace也未返回有效值，不能据此认定fastbootd。已向先前选定的enuma执行普通reboot，随后独立核验Android完成/root/A槽/解锁及两个设备分区与本地备份摘要全部通过。112帧拍屏仅本地，无音频；原始中止result.json保留。当前无人工或审批待办。

2026-10-25T18:09:25+08:00。最后实机S-009（c7c29bb，56eb63dc…89a00c7）17:21:50发出，命令2.641s、断开5.110s、ADB21.156s、完成35.219s，自动回Android并独立核验完成/root/A槽/解锁/两个原分区与备份摘要通过。252帧仅本地无音频。S-008此前75秒超时，用户恢复后已独立通过，451主/740恢复帧仅本地。S-001..009均consumed，不重试；当前无人工/审批待办。

更正D-199归因：S-009只验证旧PASS返回路径。旧query1只在PASS1终止，FAIL5继续dispatcher，7秒completion fallback必须等待初始dispatcher正常返回。S-008可能是谓词拒绝后由后续驱动挂住，不能从两笔对照直接定位采集正文或某个寄存器。这是已确认的观测控制流缺陷，优先级高于进一步猜MMIO。全量采集触碰未确保供电/时钟的银行仍为中等置信候选，不是定论。

最新固件1a4b20487aa6ac0fbb2973bf508aea1851b61192已推送：可选inherited-video-terminal让完整GUID过滤后的同一Core驱动返回点处理PASS1/FAIL5，分别2/7秒结束；该模式禁止completion fallback。错误hook、错误/空GUID、意外状态不计为结果。真实头文件197个主机场景（20个terminal组合及旧入口/返回/canary回归）通过，22个固件单测通过。当前新模式已完成完整构建、实际Core/provider PE与编译宏、R-004、BootShim/完整FAT打包和不可变资格，尚未发出S-010。d61b6ef旧非对称330读FD即使构建通过也不作下笔实机候选；资格脚本和runner已拒绝旧fallback模式。

已保留有依据的采集修复：video-only最多330读/两次100ms，最大偏移0x6c26c，只读选中CTL/SSPP/LM，去掉命令刷新、PP、闲置管线和瞬态字段；scope掩码区分未读与硬件零。330故障/白名单、30解码/267原采集故障、24通道Mu Blt通过。source-alpha与Mu保留字节不兼容已收紧准入。默认保存panel2/0/2经厂商解析器核为2LM/0压缩/2接口，优先无DSC继承；两独立SSPP仍只是当前软件范围。原生普通dump要runtime-power或已知clock上下文，R-004映射不自动证明所有银行可读。

真实GOP后端的主机/AArch64和固定8d85d39完整UEFI/QEMU RAM执行通过，不等于物理GOP。S-008没触碰帧缓冲，WT或alpha不能作为本次超时原因；UC只是当前后端选用契约，不能据此改板上缓存。CPU/SMMU地址、下游拓扑、物理GOP和可见错误通道仍未闭合，ADDRESS/TOPOLOGY不清零。

用户提供Downloads/AGENTS.md并明确授权摘取适用条目：已在根AGENTS补充简明沟通、执行顺序/状态区分、逆向流程、固定来源与板差、事实/假设/反证、对照控制流检查、完整可执行交付。未复制整份附件，未导入通用授权/其他场景模板，不改恢复、内存/verified/分区、提交推送、影音本地规则。来源摘要与取舍在operations/2026-10-25-agents-applicable-merge.md。

S-010资格：镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386，103817216字节；FD 490fe01ebda7bf8091b3944a54135fb439f73c8c0f05d8ac609e7cdd19b9ba9e；归档out/inherited-gop/qualified-terminal-1a4b204-q1。两级实际编译宏均含TERMINAL1/FALLBACK0，实际FD Core和provider与产物一致。Core函数0xf90c..0xf9b8已审查：hook13与状态1/5过滤、两半GUID匹配后，FAIL直接7秒/ResetCold/CpuDeadLoop，PASS直接2秒结束，不回dispatcher。报告enuma-video-terminal-core-code.json。当前Android/root/A槽/解锁/原分区和备份摘要、1920x1080相机再次通过；D-201资格保持；当前实机入口由D-202身份异常排查取代。

对称模式时序仍只支持分类，不唯一证明内部路径；75秒无返回记为未得到已识别terminal报告，立即consumed、停止追加并先恢复。拒绝与无报告必须区分，不再套用旧fallback推断。S-008/S-009不重试，d61非对称FD不用。原始影音只out/本地，禁止Git/Release/CI；无board/bringup-plan内存、verified、flash/erase/改槽变更。

详见operations/2026-10-25-inherited-gop-judgment.md（已更正归因）、inherited-gop-backend.md、AGENTS合并记录，以及S008/S009实测、host/qemu/policy/dispatch-details报告。框架pin5fdbd5d和96MiB FAT保持，13项运输、XNU/iPadOS/PMGR/UFS/root/Data尚未实机闭合。


下一步先排查fastboot GetVar异常与设备/主机交互，保留精确机型/槽位/解锁门禁；不得将Android检查替代fastboot检查，也不把此次未发送当失败镜像重试。S-010仍只有离线资格，尚无新固件实机结果。修正并落实文档、通过即时身份/备份/采集/恢复门禁后，再按已有授权单笔。当前不追加启动。
