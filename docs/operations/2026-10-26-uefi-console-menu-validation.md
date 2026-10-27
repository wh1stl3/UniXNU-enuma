# UEFI 固件日志上屏 → UniXNU 菜单：独立验收矩阵

目标是固件开发用的 UEFI 日志和随后菜单，不以 iPadOS 图形界面作为本阶段验收。2026-10-26 当前纯只读探针不采摄像头，实际像素/可见输出验证再采集；原始影音只留本地。源码、生成库清单的哈希证据见 `reports/enuma-console-path-audit.json`，只读审计脚本 `scripts/audit_enuma_console_path.py`；不是运行证明。

| 可验项 | 依赖 | 当前独立结果 | 验收条件 / 未执行原因 |
|---|---|---|---|
| 两源 staging 与全屏坐标 | 安全路由采集、原始稳定、双路两窗推进 | S-039 间接码5支持精确逻辑坐标模型；三样本原始字保留 | 不等于物理 CTL→PP/DSC→DSI 关联；后者未闭合 |
| 格式和颜色通道 | 仅236ff/237ff，至少一个开启alpha，其他编码不变 | S-039 支持逻辑8888 RGB描述；未输出原始寄存器数值 | alpha语义仍未验证；不能直接套用RGBX绘制策略 |
| 候选地址、步长、范围、覆盖 | Native6完整decode | S-039同次通过4字节对齐、pitch>=1600*4、stride上位约束、bytes=pitch*2560、共同base/stride/unpack、Splash包含、完整几何覆盖 | 只支持解码模型，不能称实际CPU/SMMU地址等价，也不知道具体base/stride数值 |
| CPU stage1每页映射 | 上述同次完整成功/requirements22 | S-040已实现，56000故障注入和18432最大查询主机路径通过，S-040首页属性非bb提前返回；S-041排除精确44/ff/Device；S-042整段每页R/W恒等非fault、内外WT通过，具体提示字节未知 | 每覆盖4KiB页依次R/W AT成功、输出恒等、内外策略NormalWT（分配/Transient提示不同可有不同字节）；仍不证明EL1最终stage2或SMMU |
| CPU真实数据访问与缓存一致性 | 安全映射、恢复、明确像素实验范围 | S-043单字、S-044读前DSB、S-045原点128x8共1024字读取均完成；运行于EL1，最终stage2/SMMU和写入/存储后屏障仍未验证 | 独立区分Sync、只读、保存、写、恢复；不能把AT通过直接升级为可写 |
| alpha/混合语义 | 实际操作字、源alpha、常量alpha及dim | S-034严格操作字门拒绝；Native6有意保留BLEND，且alpha_semantics_unproven=true | 从固定小米实现解释有效混合方式，并验证安全不透明写入；不能直接清requirements |
| 正式GOP发布 | 上述义务及下游闭合 | InheritedGopLib后端已实现并有host/Mu Blt测试；当前诊断无GOP发布，生产接入未完成 | 合格Frame、持续Validate、GOP+匹配DisplayDevicePath在同一handle；拒绝requirements!=0；四种Blt和SetMode单独验证 |
| GraphicsConsole/ConSplitter | 合格GOP及device path、BDS连接 | 两驱动已打包；BdsEntry顺序是BeforeConsole→默认控制台连接→AfterConsole | 静态/链接已核对，当前Core终端早于BDS所以未执行；连接可能调用SetMode/清屏，是像素状态变更，不能夹带到只读试验 |
| UefiLib Print | ConOut已连接且可见 | EnumaProbe的Line调用Print；实现已打包，当前未执行 | 单独一行Print可见且正确换行；“GOP存在”不足以证明ConOut可用 |
| DiagDraw | GOP + DarwinBootVideoFromGop + 安全像素/缓存语义 | 生成DarwinProbe.inc有直接Fb[]写；不是Print或GOP Blt | 当前raw0xff000000/0xffffffff假定alpha位置，不能适配所有unpack；与Print同一个Line会相互遮蔽，应先隔离并补mask/opaque适配，再按像素门禁执行 |
| 全局DEBUG日志 | DebugLib/SerialPortLib有效接收端 | 实际EnumaProbe库清单为BaseDebugLibSerialPort + BaseSerialPortLibNull；板级明确Null覆盖 | 缺失安全屏幕日志接收/重放；仅接GOP或ConOut不会自动修复DEBUG；审计逐模块库清单，不只看DSC默认值 |
| UniXNU菜单入口 | payload检查通过、UniXNURun、显示/输入 | EnumaProbe→UniXNURun已接入；Main连接控制器、加载配置、注入驱动、初始化UI再跑Menu；Ui有GOP Blt和ConOut回退 | 源码/构建已有，当前诊断提前返回因此未执行；先验收菜单画面，再验收音量键选择/取消，不能因编译成功称菜单上机成功 |
| 早期日志 | GOP之前的独立记录通道 | SEC/早期DXE没有已验证的屏幕日志/重放 | 建议有界RAM环形记录、GOP合格后重放；尚未实现。不能为了早期日志恢复猜格式的FrameBufferSerialPortLib或修改映射 |

## 构建与观察的边界

每笔独立冻结源码提交、实际编译宏、provider/Core PE、FD/R-004记录、完整FAT和Boot v3；当前时间码是五类首结果，无法同时提供多个子项的独立结果。S-040只在Native6全部前置满足后检查CPU转换，code1统一表示前置/上下文拒绝，code2..5才属于转换阶段；若code1，应进一步隔离，不把其余检查写成已执行。

S-040历史纯查询配置计划最多18432个AT，没有像素加载/存储、MMIO store、缓存维护或页表setter。只允许EL1/EL2、MMU开启、<=48bit PA；拒绝VHE及硬件AF/dirty更新，逐次保存/恢复DAIF和PAR。仍保留requirements22、alpha和SMMU义务。依据固定Mu `AArch64Mmu.h` 的MAIR write-through0xbb，以及Arm [AT/PAR架构说明](https://documentation-service.arm.com/static/6166bfbaac265639eac59049)和[TCR HA/HD字段](https://documentation-service.arm.com/static/624ff3decaabfd7b3c13e9c7)；架构格式事实不是本机访问结论。

对现有权限内可独立验证的离线项尽量一次完成；同一实机窗口仅合并结果可区分、低风险、原授权覆盖的检查。像素写、页表/缓存属性修改、显示路由切换仍走原门禁。已consumed镜像不重试；时基无效/模糊或75秒无识别恢复立即硬停并当轮更新所有交接。


D-278补充：R-018新候选完成离线构建/实际代码审查，尚未上机，待精确范围批准。它在同次EL1/全页NormalWT/Frame和两次Native6门下尝试128x8保存、500ms对比色、全部恢复读回；最多3072load/2048store/3DSB。此为独立像素事务，不是上表只读查询的隐含扩张。当前14项native、12项历史pixel、10项FD策略测试通过；精确镜像和候选比较见2026-10-26-r018-bounded-pixel-transaction.md。只读前置不采相机；实际像素可见性再采，仅本地保存原始影音。


D-280实机更新：S-046在R-018单图批准下完成128x8保存/重验证/对比色/恢复读回，预声明时间码5；相机frame103..105可见左上白条，102前/106后消失，350帧全解码，独立Android/root/A槽/解锁/两分区及备份核验通过。此为首个最小区域可见输出证据，非文字/完整GOP/全屏/菜单验收，不清requirements22与通用alpha/SMMU义务。R-018 consumed，不重试；原始影音仅本地。后续转安全不透明绘制/文字与控制台离线实现。


D-281离线进展：独立R-019候选提供mask-aware固定UEFI字形4倍放大/128x32/500ms保存恢复，源码、主机故障注入、实际PE字形/边界/栈/恢复、FD/FAT/Boot v3已审查，未执行，pending新镜像/高度范围批准。它不调用旧DiagDraw、不发布GOP、不接全局DEBUG或ConOut；因此原始绘制/FrameBufferBlt alpha适配、日志接收与控制台连接项仍未完成，不能因本候选编译成功更新硬件验收。


D-283实机进展：S-047 R-019一次试验code5与精确恢复完成，352帧全解码，frame104/105可辨认固定UEFI，103前/106后消失；Android55.625秒且独立身份/设备与备份摘要通过。固定字形在左上小区域可见，不是全局DEBUG或Print、全屏GOP、菜单验收，不清22。R-019 consumed，不重试，原始影音仅本地。下一步优先记录并显示已有真实CPU/固件状态，避免再只验静态字符串。


D-284用户主线纠偏与安全交接：固定UEFI字样已正常显示，不再追加字母/图案/重复点屏验证；接续应直接推进UEFI固件开发、真实日志记录/屏幕输出和启动阶段诊断。S-047并未验收全局DEBUG/Print/GOP/菜单，不通过清22或标verified跳过生产接入条件。本会话只做安全收尾，没有日志新实现或R-020候选，等待管理方在旧会话结束后创建唯一接续会话。


D-285接续：新增默认关闭的DXE状态RAM日志与未接屏幕的单行回放接口，主机/AArch64及完整FD宏/staging检查通过。它不接全局DEBUG/SEC、ConOut或菜单；原矩阵中未执行的硬件项维持。独立新矩阵、失败记录、证据和下一步精确条件见2026-10-26-dxe-status-journal.md，不能用新源码覆盖历史FD审计结论。

D-286：新R-020精确候选已完成私有Core真实返回快照与256x96/2s有界缓存回放离线资格，准备S-048；用户新实机授权有效，发布/即时门后直接单笔。尚无新硬件结果，正式DEBUG/SEC/ConOut/GOP/菜单仍独立未验；详见2026-10-26-r020-cached-dxe-log-replay.md。

D-287当前更新：S-048/R-020已执行一次并consumed。唯一间接code5/精确恢复与独立Android后验通过；相机360帧完整、三行回放形态可见，但完整status/ordinal不可辨，内容可读性未通过，按观测歧义门禁停止追加。DXE RAM/私有快照/有界回放已实现，早期SEC、全局DEBUG、ConOut/Print、正式GOP和菜单未通过。当前入口HANDOFF/STATUS及R-020执行记录，不把下方历史矩阵的早期“未实现RAM日志”当当前事实。


## D-292当前补充

S049已恢复但用户反馈2秒对焦不足，精确数值仍未读清；旧图及R021均consumed。新8秒同区域候选已完成离线资格，R022 pending，计划S050未执行。详见2026-10-26-r022-eight-second-log-observation.md；不可把构建/机器码通过当实机日志验收，也不得绕过当前观测硬停。


D293补充：新增独立栅格反读/严格人工转录与输出链顺序审计，见2026-10-26-offline-log-readability-and-console-readiness.md。实机延后，R022保持冻结pending；当前回放不能含提供器自己尚未发生的返回，Print/DiagDraw/DEBUG/ConOut与菜单分别验收。

D295代码更新：开发源新增带canonical GUID/sequence/phase的归因文本回放及ConOut消费者（Probe回放默认关闭），Probe Line已改为仅ConOut，生成helper不再带DiagDraw/raw Fb写，移除对应cache flush；新增实际菜单调用前的文本回调/mode/几何保护。真实C回放→ConOut→主机归因、故障路径、三分支AArch64对象及旧日志/8秒事务回归通过。详见2026-10-26-attributed-journal-and-console-code.md。旧矩阵及console-readiness对Probe双写/旧源码摘要的描述属于历史，不能当新源码状态；旧报告保留原字节。正式GOP/控制台连接、全局DEBUG、实机ConOut及菜单依然未验收，R022冻结不变，新源不冒充旧资格。


D296代码及运行更新：新增同handle GOP/BDS路径发布和失败生命周期，真实BootManager去全局GOP别名、仅借用；新增GraphicsConsole最小尺寸保护。QEMU实际连接AAVMF GraphicsConsole并运行固定UniXNU横/竖Ui/Menu、归因ConOut、默认超时、脚本输入/取消/确认及文本回退通过，导出帧CRC和截图闭环。详见2026-10-26-qemu-menu-chain-and-gop-publication.md。这是RAM/脚本输入的软件证据，设备provider仍未正式准入，requirements22及uncached/alpha/SMMU/实际输入/恢复不提升；原报告、R022和消费规则不改。


D297：新增独立WT/opaque GOP，四类Blt写入ReservedMask并锁存IO/Validate故障，保存字混合系数分析器保持22不清位；主机/ARM及实际WT机制QEMU菜单链通过。当前无可部署的新enuma菜单镜像，地址/SMMU/路由/实际blend与完整设备构建未资格，按用户要求停在部署前。详见2026-10-26-wt-opaque-gop-predeployment.md。旧Mu入口、冻结R022及历史证据保留。


D301当前更新：S050/R022 consumed，ordinal31/status0/+可读但圆角遮挡使整页未过。新R023已完成内缩五行完整GUID/sequence/status回放及完整FD/FAT离线资格，pending/未实测；详情见2026-10-26-r023-attributed-inset-log.md。当前源码已移除Probe双写且有QEMU菜单证据，历史矩阵不代表现状；实际DEBUG/ConOut/正式GOP/菜单仍分别未验收。


## D-304：S051内容交叉核对及I2C归因

用户提供五行人工转录，与此前独立保存的助手判读按字段上下文/hex大小写规范化后逐字一致：ordinal31、status0、sequence185、GUID04de8591-d2b3-4077-bbbe-b12070094eb6。绑定本镜像实际PE目录唯一I2C；仅证明此前I2C StartImage返回EFI_SUCCESS，不证明总线/外设功能。照片中五行完整避开圆角；S/5、O/0字形相同确有辨识缺陷，依靠标签位置区分，后续新候选改善，不覆盖冻结图。原S051结果报告保存当时pending事实；新证据reports/enuma-s051-visible-log.json关闭人工核对项。R023已consumed，不再启动，无新实机授权、无提交推送。


## D-305 当前软件链：有界控制台回放与菜单依赖

本节更新当前实现，不覆盖历史实测。`Line`现在仅走OutputString并锁存首次warning/error；不再调用Print+DiagDraw双写。Probe入口需要可用ConOut，日志回放最多129行，任何部分输出停止且不进入菜单。`ENUMA_PROBE_JOURNAL_REPLAY`通过DSC全局BuildOptions传入实际编译；新完整构建结果见D305操作记录及build-result.json。诊断FD的Probe入口保留EFI_UNSUPPORTED安全返回，晚期业务被LTO裁掉；真实晚期实现另外由console-link2完整链接，不打入诊断FD，不能混称同一镜像可进入菜单。

| 阶段 | 本轮实际证据 | 仍欠的实机证据 |
|---|---|---|
| 早期日志页面 | replay3错误/警告优先及25字形唯一；194组网格独立反读 | 新字形真实拍摄；新选中事件只属于此前完成返回 |
| ConOut回放 | 129行、258失败位置、首错锁存及AArch64对象通过 | 真实板级GOP→BDS→GraphicsConsole/ConSplitter连接及可见输出 |
| UniXNU菜单 | 新Drain接入QEMU，真实GraphicsConsole和固定Ui/Menu横竖屏、选择/取消/确认、文本fallback通过 | 生产GOP准入、持续验证、屏幕及真实输入 |
| 全局DEBUG | 仍为Null SerialPort，未改变 | 独立传输实现和验收 |

R022/R023已consumed；新候选没有自动实机许可，requirements22及alpha/stage2/SMMU边界保持。完整本轮记录：[D305](2026-10-26-diagnostic-log-and-console-drain.md)。


## D-307：S052真实日志核对完成与固定人工校验流程

R024已单次消费，21:56:12发图，Android66.234秒，原点40.761..40.818唯一code5；21:58:12独立恢复通过。用户“能对上”确认助手先保存后展示的五行，随后查本镜像目录归因I2C StartImage返回EFI_SUCCESS（ordinal31/sequence185/GUID04de8591-d2b3-4077-bbbe-b12070094eb6）。新字形/完整页面本图可读，不称全部字形/8秒持续或正式GOP/ConOut/DEBUG/菜单通过；requirements22不清。证据reports/enuma-native-route-S-052-result.json、reports/enuma-s052-visible-log.json、out/r024-live-20261026。用户“以后都这样校验”：助手先独立读图落盘→展示五行→用户确认/纠正→精确镜像目录归因；不确定写?，不补猜，不再要求用户先盲抄。媒体本地、旧消费不复活，无追加启动/提交推送。

## D-308：用户要求菜单优先，直达入口与无ConOut图形菜单验证

用户明确优先最快进入真实UniXNU菜单。新增默认关闭ENUMA_DIRECT_MENU，选择真实UniXNU应用GUID，独立stage10开发构建可用--direct-menu，拒绝与旧日志实验profile混用，原诊断早停/requirements22保持。QEMU横竖实际Ui/Menu在ConOut=NULL期间绘制和模拟按键/取消/确认通过（21命令），不将其称为整个UniXNURun或物理显示/按键通过。新版本地固定16e592a已有QR AdvancedLogDxe，但当前5fdbd5d没有；QR依赖菜单/GOP及AdvancedLogger，后置而不升级框架阻塞菜单。真实UniXNURun关闭BDS watchdog，下一物理菜单候选须独立可控返回。记录docs/operations/2026-10-26-menu-first-and-qr-log.md，构建及证据out/menu-priority-20261026；无新设备动作、提交推送或冻结产物覆盖。最新完整构建状态以该目录build1/build-result.json及direct-entry.json为准。
