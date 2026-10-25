# D-195 / D-196：真实GOP后端与同次双链路取证

2026-10-25，Asia/Shanghai。用户要求继续真实GOP后端与双链路验证，条件满足直接上机，按结果推进，文档和提交推送，原始影音只留本地。软件后端完成不代表物理GOP恢复。

## 已完成的软件与实际执行

固件后端实现最初bddc5d8，摘要/LF修正8d85d39；只读入口784a59d；活动LM读取收紧511e6cf；最终原生计数前置898ae25。设备source lock/gitlink按最终源同步。没有board/bringup-plan内存字段或verified变更。

InheritedGopLib使用实际Mu FrameBufferBltLib，不拷贝cas物理Blt/CTL_START。QueryMode校验模式并分配完整信息副本；SetMode模式0清黑、未知模式拒绝；四种Blt实现矩形和溢出检查、TPL保护及每次操作前的归属复核。创建不触碰帧缓冲；分配/配置失败完整释放。板级调用者仍须提供同次真实资格和协议/DriverBinding生命周期，库不自行注册协议，也不做猜测性缓存维护。

主机实际链接生产后端、Mu Blt和真实UEFI头文件，仅分配/TPL/BaseLib内存基本函数用主机模型：24种RGBA字节排列、四操作、重叠移动、独立QueryMode副本、SetMode清黑、padding/guard、参数溢出、归属失效、分配失败均ASan/UBSan通过。AArch64对象编译通过；主机和完整UEFI构建使用的Mu Blt源码SHA均3c4ef872faa7e042bcd2199a225c28ae50afe6768363734210f73645e683fb53。

8d85d39已由固定官方固件后端实际完整链接。选择非自动执行EnumaGopSelfTest，使用分配RAM、不注册GOP、不访问显示MMIO。抽出的实际AArch64 EFI在QEMU/AAVMF执行，串口实际输出`ENUMA_GOP_SELFTEST PASS RAM ONLY`且正常shutdown。FD b20a4e4bfab5be6097f0763dbf647b39332f0ad6b19caf343402528695cde5b6；不可变本地归档out/inherited-gop/qualified-qemu-8d85d39。报告reports/enuma-inherited-gop-qemu.json包含EFI/QEMU固件/日志摘要和命令。这个FD不是enuma物理显示候选。

## 双链路判定与边界

固定小米52a2f18的`sde_hw_lm.c`把LM_OP_MODE bit31设置为right_mixer；`sde_crtc.c`依据实际水平角色设置它。新Topology按该字段判左右，反向LM编号的合成快照通过。支持一个video CTL、两个DSI active位、两个完整高度LM、不同全tile源、严格单staging/无dim/BASE或精确常量FG255/BG0；source split/shared pipe、多CTL、partial update、border/虚拟/未知字段或未审处理均拒绝。这是当前支持范围，不是已确认本机实际采用它。

sampler最终源898ae25：三个同次快照，每窗100ms；上限969回调读、两次等待、最大SDE相对偏移0x73830。先检查原生两计数使能位为3、timing和active，再只读取活动CTL选择的两个LM，闲置LM的blend不读。两个接口每窗须无回绕增长1..64，管线/路由/混合字段稳定。START/FLUSH作为瞬态保留于快照但不要求恒定。失败不输出部分证据，前置不足停止依赖读取，不写寄存器/像素。

主机覆盖144个全LM适配器失败位置（该全LM API仅离线）、最终969个运行采样失败位置、两次等待失败、右接口不动、配置变更、仅一个计数使能位时在LM读取之前拒绝。真实decoder修正staging扩展到bit3、未知stage>12及OriginY覆盖边界；29场景/267原始采集失败通过。成功仍保留ADDRESS/TOPOLOGY要求，禁止清这些标志发布GOP。

公开依据与本地SHA在config/inherited-gop-sources.lock.json、reports/enuma-inherited-gop-policy.json；GPL源只读参考寄存器事实，不导入实现。保存FDT的显示非安全IOMMU绑定为apps-smmu，SID/mask为0x820/0x402，不能从该配置或地址落在splash范围推断UEFI实际bypass/identity。原Display Reserved仍WRITE_THROUGH；当前后端要求UC，尚未做缓存属性转换。LM左右角色也不等于PP/DSC/INTF下游连接证明。

## 下一笔只读候选与执行规则

`--inherited-video-audit`在既有精确SimpleFb INF/GUID与Core-warning入口物化新只读源，不执行旧metadata发布函数，也不调用GOP后端。源码/全部采样文件与staging相等性、原INF/无reset构造器检查由构建器绑定。R-004运行时精确表记录（0xae00000/0x85000/AddDev/MMIO/UC/NS_DEVICE）先验；实际FD还须检出同一表记录。完整96MiB FAT保持原输入，生成全链输入boot v3，但取证入口会在必要位置早停。

精确PASS warning选择2秒Core gate；拒绝可能走7秒dispatcher fallback。主机时序只是支持，单笔不能唯一证明门命中/具体寄存器值，不能据此宣称实际面板显示或清ADDRESS/TOPOLOGY。若75秒无返回，立即consumed、停止追加，优先按既有长按恢复；主机观察期限不是固件自动返回保证。恢复通过后自动离线分析，不原样重试。旧S-001..007、像素/R-005及冻结value计划不复活。

最终898ae25需新构建/实际FD/PE/宏/BootShim/FAT打包资格及不可变归档；所有当前文档先提交推送，然后即时身份/备份/相机/恢复检查，按现有授权单笔临时fastboot boot。中间784a59d/511e6cf构建不进入实机；511构建在最终源收紧后被staged-source比对拒绝，不绕过检查复用。

当轮实际试验前后的精确镜像摘要、时间、恢复和结果另追加到本记录及当前STATUS/HANDOFF；资格尚未完成时不写“已上机”。原始拍屏/恢复影音和照片只保留本地out/，不上传Git、Release或CI。公开仅脱敏JSON/文字/摘要。

参考：[小米LM实现](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_lm.c)、[UEFI GOP契约](https://uefi.org/specs/UEFI/2.10/12_Protocols_Console_Support.html#graphics-output-protocol)。


## D-196执行前资格（2026-10-25T17:04:20+08:00）

最终固件898ae255e95cb53733250b26b647bb59757f86aa。新镜像f8f14e3b1ec0b5a097d938b55ed85123e913d16392e42cd3f981419e333a4dc8；FD fe052cda49df0113c92d883479ad0841fcb1bc1191a4727083a20f59bbf7b9b3。归档out/inherited-gop/qualified-video-898ae25-q1，完整FAT49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773。实际30个保留OEM PE/DEPEX未改，CPR/Display/UFS明示省略，SimpleFb同GUID仅只读新代码。源/编译宏/PE、R-004记录、boot-v3/FAT roundtrip和离线runner通过。S-008尚未发出，当前文档发布后即时门禁再单笔。


## D-197实测与恢复

S-008于17:05:25发出，命令2.641s返回0、断开5.109s；75秒观察无自动返回，停止追加、consumed，S-008未解码，不重试。用户长按恢复Android，17:08:12独立完成/root/A槽/解锁/原boot_a/vendor_boot_a及备份摘要通过。451主/740恢复帧解码一致，全部原始影音仅本地，未采音。末帧强反光暗屏，无可读固件文本；不据此定位寄存器或断言入口命中。

实际SimpleFb AutoGen只有BaseDebugLibSerialPortConstructor、UefiBootServicesTableLibConstructor，实际库为BaseSerialPortLibNull，无PSCI/reset构造器。现中等置信度主判断是先分清入口/返回通道与正文访存；正文包含内存表查询及SSPP/CTL/PP/选中LM取数，未活动银行读为候选而非结论。下一步新的同INF/GUID/完整输入常量PASS正文，对照禁MMIO/查表/协议，实际PE指令资格后再按发布/即时恢复门禁单笔。若它失败，转构造器/Core/前驱路径；若它可控返回，进一步收缩读取，不扩读或写像素。


## D-198：同入口常量对照资格（2026-10-25T17:21:12+08:00）

固件c7c29bb0fe8f2bbf6f8128689b7f423da7dcc72c，S-009镜像56eb63dc63bc7e4b76e6746cb42a0f05b25dfa08099b356f63117c8af89a00c7，FD c87f3d1d296ef09679acf6c6887f34c9c892fbb720fc8005d3562fce35c4b28e；归档out/inherited-gop/qualified-control-c7c29bb-q1。实际入口RVA0x1050..0x10dc正常路径只有栈/UEFI全局指针保存、从ST+0x60取BootServices、非空断言分支以及mov w0,#1/ret；无查表/MMIO/像素/等待/分配/协议。DebugAssert非空失败路径保留，不假设异常输入会返回。反汇编使用skipdata覆盖文本中的0xcc链接填充并绑定完整SHA 401ebe34396c099a60c8a2e9fe0d0bf031c706da714d11870f6071e277763d9e；最初在填充处截断的inspection产物不获资格。

与S-008实际FD比较72PE，70完全相同，只有目标正文运行时代码改变；PcdDxe仅8字节RSDS GUID，包含其余代码/路径/age全部相同，Core完全相同。AutoGen/库清单、固件配置、BootShim和完整FAT相同。报告enuma-inherited-control-pair.json。实际反汇编/源码/打包资格、21固件单测、当前Android备份和相机门禁通过，文档推送后单笔；尚未发出。


## D-199：S-009实测与按资料修复

S-00917:21:50发出，命令2.641s、断开5.110s、ADB21.156s、完成35.219s，自动回Android，独立完成/root/A槽/解锁/原分区和备份一致，252帧只留本地，无音频。S-008正文访问为首嫌，具体寄存器未确定。固定厂商dump电源前置、默认拓扑2/0/2与alpha差异促成d61b6ef：仅video选中路径、330读/最大0x6c26c、未读scope显式、source-alpha格式拒绝。主机30解码/330故障及21固件单测通过，新完整FD/实机资格正在重做，尚未S-010。详见单独judgment文档的证据、置信度与可推翻观测。


## D-200：归因修正与对称返回

D-199的正文首嫌强度下调。旧query1仅PASS1触发返回点2秒终止；FAIL5继续dispatcher，completion7秒仅在dispatcher返回后执行。故S-008也可能已拒绝而后续驱动挂住。新1a4b204可选terminal在同一完整GUID返回点识别PASS1/FAIL5并2/7秒终止，禁止completion fallback，未知状态/hook/GUID不认。197头文件场景（含20 terminal组合）及22固件单测通过，实际新全构建/产物资格尚待完成，未S-010；旧d61非对称FD不投入新试验。当前judgment与S009派生解释已同步更正，原始实测保留。


## D-201执行前资格（2026-10-25T18:16:36+08:00）

新terminal FD 490fe01ebda7bf8091b3944a54135fb439f73c8c0f05d8ac609e7cdd19b9ba9e，镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386，归档out/inherited-gop/qualified-terminal-1a4b204-q1。实际Core0xf90c..f9b8的AND~4/compare1精确识别1和5，hook13及两半GUID之后，分别MicroSecondDelay2m/7m、ResetCold和CpuDeadLoop，FAIL无dispatcher继续路径。实际Core/provider宏均TERMINAL1/FALLBACK0、PE均在实际FD，R-004/BootShim/完整FAT/immutable资格通过。197主机场景/22固件单测和当前Android备份相机通过；文档发布后S-010单笔，当前未发出。


## D-202：S-010准备中止

2026-10-25T18:23+08:00。S-010准备流程在fastboot身份门禁中止：首个product查询返回enuma，current-slot/unlocked及后续完整查询失败，部分remote FAILED仍返回主机退出码0，精确值检查正确拒绝。未执行fastboot boot，镜像24aed9e0…ae9e2386未消耗；不能记为固件超时、PASS或FAIL。is-userspace也未返回有效值，不能据此认定fastbootd。已向先前选定的enuma执行普通reboot，随后独立核验Android完成/root/A槽/解锁及两个设备分区与本地备份摘要全部通过。112帧拍屏仅本地，无音频；原始中止result.json保留。当前无人工或审批待办。

下一步先排查fastboot GetVar异常与设备/主机交互，保留精确机型/槽位/解锁门禁；不得将Android检查替代fastboot检查，也不把此次未发送当失败镜像重试。S-010仍只有离线资格，尚无新固件实机结果。修正并落实文档、通过即时身份/备份/采集/恢复门禁后，再按已有授权单笔。当前不追加启动。

证据：reports/enuma-inherited-video-S010-preboot-result.json。


## D-204当前结果（取代前文未上机与故障排序的当前性）

2026-10-25T18:29:27+08:00。S-010已于18:26:07（UTC10:26:07.186360）执行一次临时boot，镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386，固件1a4b20487aa6ac0fbb2973bf508aea1851b61192，FD490fe01ebda7bf8091b3944a54135fb439f73c8c0f05d8ac609e7cdd19b9ba9e。全部执行前文档7d1312b已推送；即时Android/备份/相机门禁及fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过。上次GetVar异常没有重现，根因仍未知，不删除D-202原始中止记录，不放宽身份检查。

命令2.641秒返回，5.110秒观察断开，ADB25.469秒出现、39.438秒完成Android。runner未发恢复reboot；随后独立核验完成/root/A槽/解锁和boot_a/vendor_boot_a设备及本地备份摘要全部通过。270/270拍屏帧解码通过，已目视核对试前桌面、中途小米/Android启动标志及试后桌面；无UEFI/GOP文本证据。原始影音仅out/camera-capture/20261025T182550-system-transport，未录音，不上传Git/Release/CI。

本笔有受控返回，不能记为75秒无报告超时。相对S-009，ADB晚4.313秒、完成晚4.219秒，支持FAIL5/7秒终止的谓词拒绝判断，中等置信；不是直接状态日志，也不是PASS/GOP成功或精确寄存器定位。两个候选Core与采集范围不同、Android时序含噪声，不能仅凭差值确证7秒或S-008根因。S-010已consumed，S-001..010及旧失败图不重试。

按结果推进：主判断转向保守准入模型与实际继承布局不匹配，优先细分首次拒绝阶段/状态，不再默认把本笔当MMIO挂死或盲改缓存。源码要求单CTL/双LM/两个独立SSPP、无border/额外staging、严格dim/blend及RGBX；历史step21保守混合拒绝提供同方向旁证，但不是本笔快照。单源跨LM、border/合法混合、格式/几何/地址边界列为候选；描述表/PCD门禁、双接口前置/稳定性仍不能排除。只有直接取得阶段/状态或同入口对照后才能排序到具体寄存器，不放宽安全准入换通过。

新候选尚未实现/资格/执行。下一步保持同完整输入、完整GUID双结果终止及FALLBACK0，先设计可判读的首拒绝证据（同时区分未到达与已拒绝），主机故障注入和实际Core/provider审查后再构建；不恢复旧长时间编码或失败像素/value计划。若新证据显示采样/解码已全部通过或故障在入口前，则推翻当前拒绝模型主假设。真实GOP/CPU-SMMU/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合；ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更，当前无人工或审批待办。

证据：reports/enuma-inherited-video-S010-result.json；原trial out/device-tests/20261025T182553-system-transport/result.json；独立恢复out\device-tests\20261025T182657-recovery-reconciliation.json。身份解析3项、恢复核验2项、恢复硬门1项回归通过；不可变归档各文件摘要再次匹配。当前源码固件未改动，设备文档/脱敏证据单独提交推送。
