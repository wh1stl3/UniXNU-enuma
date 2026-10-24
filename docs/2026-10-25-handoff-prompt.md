# D-167当前：R-016批准A单笔上机，尚未执行

用户明确“批准上机”。仅镜像29b84e1f…8fa72bd4的一次A/detail15临时boot，先读STATUS和NEED-REVIEW R-016。即时Android/备份/相机检查通过，主机新增断开后重连判定与精确时间戳；全部文档/源码发布后运行scripts/capture_display_boundary_trial.py --execute。不得自动发B或重复A。超时停止追加，恢复并更新当前文档。

以下为D-166及更早背景；当前批准和实时状态以STATUS为准。

# enuma交接提示词：D-166新增二进制证据与A候选

优先执行docs/STATUS.md和docs/HANDOFF.md的D-166当前顺序。已完成两份离线审计：docs/operations/2026-10-25-handoff-contract.md与2026-10-25-native-display-abi.md；工具scripts/audit_display_handoff.py，机器证据reports/enuma-display-handoff-audit.json。A/detail15已经离线构建并归档，见reports/enuma-display-boundary-qualification.json，未上机。先发布文档和完成即时门禁，再判断执行；不直接跳到B或补节点/运行时stub。

新增事实：实际DisplayDxe会消费Kernel Protocol/调度HOB，且缺失时可成功返回而不创建显示线程；本机ABL查splash_region而保存DTB只有cont_splash_region，临时入口树未知。原厂PE存在、返回0或局部DSI活动均不代表可见显示。D-165已保留；75秒无返回还不能排除复位/前置/观测问题。

以下D-164/D-163内容作为路线和判读背景；其中“仅方案未构建”“当前不要commit”“本轮未提交”等阶段表述已由D-166及实际发布记录取代，不能覆盖STATUS。

# enuma移植交接提示词（2026-10-25公开资料路线复审）

## D-164：公开资料复审后的当前顺序（2026-10-25）

当前主线改为先离线审计ABL→BootShim→UEFI的continuous-splash交接契约；原厂DisplayDxe保留为有界支线。先输出实际FDT/显示生命周期证据与原厂PE真实调用/ABI清单，再按缺口选择候选，detail15/detail13不再自动排在离线审计之前。详见[公开资料路线复审](operations/2026-10-25-public-source-route-review.md)。

新静态发现（Codex 提出，D-165 已逐条本地核实）：enuma配置EnableMultiThreading/EnableDisplayThread=1（`ConfigurationMapLib.c` 29/34），但当前GetXblHobAddresses只识别FD Reserved/FD_Reserved（`XblProtocols.c` 113/114），板级内存表无此名称（只有Sched Heap/Display Reserved/UEFI FD，见`MemoryMapLib.c` 14/15/19）；以该表调用此路径不会恢复scheduler/DTB扩展HOB地址。`EFIKernelInterface.h` 445/446/622 有真实ThreadCreate/ThreadResume/InitLock，**不可stub替代**。这不证明实机挂点或DisplayDxe必然使用该ABI；需绑定实际PE/SEC证据。不得直接改名、加内存区、关线程或补stub来冒充修复。

同SoC edk2-msm有继承帧缓冲实现，MiCode/LineageOS提供SMMU/split-DSI和KTZ8866依据；这些实现不证明本机scanout有效。暂不重写完整显示栈；若证实仅背光等窄缺口，再复用真实协议实现。D-163四项更正继续有效。此轮仅研究和文档，未构建/访问设备/实测，未提交推送，未扩大授权。

接手enuma（小米平板5 Pro 5G / SM8250）运行iPadOS17.7.11/21H461的移植。设备仓D:/Code/UniXNU-enuma，固件实现仅在固定firmware子模块；D:/Code/uefi-enuma是独立检出。nuwa和PortingiOS等参考只读。

## 必读

1. AGENTS.md全文。
2. docs/STATUS.md、docs/HANDOFF.md。
3. docs/DECISIONS.md，先读D-164路线调整；D-163对D-162的证据更正继续有效，旧观测保留但不继承过强解释。
4. docs/operations/2026-10-25-public-source-route-review.md（当前顺序），再读display-entry-isolation-plan.md（原厂支线工具）。
5. docs/NEED-REVIEW.md；背光/批量传值旧说明中的已过期方案不作为当前指令。

## 已核对的事实与边界

- 本机XBL可枚举149个模块，包括DisplayDxe（315392字节）、CPRDxe、ClockDxe、I2C、SPMI、PmicDxe、DALTLMM和40份面板XML。发现这些组件支持优先复用，不等于完整运行依赖闭包已经成立。PE字符串表明包含背光/面板控制路径，不证明已执行或可用。
- 实测R-014镜像SHA256：922972e61b0e4e3d7b7c931b53b76531a2db2a08504c6794263e5ff3f5ab1a75；内含FD：dbca3fcb2f470807f1fdac8b17e47c6eb604f3be49b1563c42df5bfc020615e0。
- 对该FD直接解析：DisplayDxe在APRIORI第33项，零基索引32。APRIORI与Mu源码会将其排入Scheduled队列，忽略DEPEX；不保证到达、加载成功、PE入口执行或返回。
- 未知GUID a966cc4f-ee6c-424d-a762-8ed3b5a4a501 与47861dff-556f-4269-9b28-062ec3ecb30d没有已证明的DEPEX阻塞作用。PE完整字节搜索不足以证明无提供者、代码不调用或与初始化无关；不发布假协议，R-015暂不执行。
- R-014返回门误指向未打包的SimpleFbDxe GUID dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92，因此目标门不命中。但completion fallback已开启：CoreDispatcher正常返回后仍应等待7秒再尝试复位。75秒无返回不是GUID配错的必然结果；fallback不是watchdog。
- 两笔R-014均75秒无自动返回，第二笔有60帧间隔采样，后续采样未见画面。这不能定位DisplayDxe、证明稳定挂死、排除瞬态画面或确认背光电路状态。
- DSI存活样本仅支持采样期接口活动，不证明完整MDP→双DSI→面板链路正常。小样本12.5%/25%等是样本比例，不是固定独立故障概率，也不支持把每次失败视为正常损耗。

## 当前状态

最新记录的恢复已核验：Android完成/root/A槽/解锁、设备及备份双分区摘要匹配。证据reports/enuma-recovery-reconciliation.json及out/device-tests/20261025T012053-recovery-reconciliation.json；本次文档修改未重新操作设备。旧失败账本保留。

源码锁、设备仓gitlink和firmware检出已对齐aa9ec66；实机前仍实时复核。本文修改后设备仓有文档差异，尚未提交，不能声称工作区干净已发布。原厂GOP/可见画面闭环和XNU入口均未验证。

## 原厂支线候选（完成D-164离线审计后再决定，未构建、未实测）

若离线审计后仍需定位执行边界，使用DisplayDxe完整GUID：4138022f-06c7-4f79-9c94-7e33b511a4e7。当前优先任务是顶部D-164规定的交接契约和真实ABI审计。

1. 候选A：detail15，CoreStartImage调用前。支持已到启动边界，不证明PE入口。
2. A的边界与返回通道得到支持后，再考虑候选B：detail13，CoreStartImage任意返回后。只证明已返回，不报告EFI_STATUS或GOP成功。
3. 若A有响应、B无返回，只能在同源/可重复/观测有效前提下收窄到启动调用及返回区间。后续可用detail20/21/22分开PE入口、构造函数和Exit/LongJump；不能直接归因驱动内部。
4. 如B返回，再用query0的detail16/17区分错误/非错误，另验GOP。若只见7秒fallback，先检查目标发现/加载/过滤；若无返回，先恢复和离线隔离，不做单笔因果判定。

保持原厂PE、派发顺序及模块集合不变；使用without-ufs，SIMPLEFB=0、query0、step0、value-source off，不增加驱动内复位库。完整构建参数、资格和判读表见专项方案。

## 执行纪律

- 本轮用户仅要求修改文档和方案，没有批准新硬件动作。R-014及后续候选授权按原记录核对，本文不扩张范围。
- 先完成源码/编译宏/FD/打包/摘要绑定；适用文档按AGENTS要求提交推送后，才可执行新候选。当前不要主动commit或boot。
- 每笔即时身份/备份/恢复条件检查；原厂驱动可能写硬件，不能因Core探针本身只观察就称整个候选只读。
- 相机取证与返回/阶段证据配合，保存时间戳与原图并按实际方向旋转。超时停止追加、恢复核验并当轮同步文档，不原样重试失败镜像。
- 不新增像素/MMIO写、内存字段/映射、verified或分区操作；新需要按AGENTS和当前批准边界审查。Mock测试，避免单元测试意外操作设备。

本次核心纠偏：APRIORI只保证入队；错误GUID不解释completion fallback失效；detail13不是状态数值通道；未知协议无字节命中不等于无语义。先定位再适配。
