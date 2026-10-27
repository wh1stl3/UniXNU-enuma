# D-305：诊断日志字形、故障优先归因与菜单前控制台回放

本轮依据：用户认可真实日志→正式控制台→UniXNU菜单的阶段目标，要求“继续推进，直到编译出下一版固件”“尽可能多的推进进度”。只做离线实现、测试、完整构建和打包，不继承S051录像确认，不自动提交推送。设备仓实际固件源为D:/Code/PortingiOS/enuma/UniXNU-enuma/firmware；独立uefi-enuma及nuwa未操作。

## 本次代码增量

- 新的replay=3使用独立PixelDiagnosticLogPage.h，不改冻结replay1/2字库。25个字形各自唯一，S/5、O/0、C/c、E/e均可由字形独立区分；合成网格反读不再使用字段位置限定字符集合。实拍可读性仍待验证。
- 保留128条日志环，严格验证快照序列、丢失计数和GUID字段；只选择已完成point13 StartImage返回。优先EFI错误，其次警告，再成功；同级取最新。E/W/C仅说明所选返回状态类别，不宣布整个启动失败/成功。正常EFI_UNSUPPORTED等也可能被选出，需结合实际驱动理解。
- 被选记录缺GUID时拒绝绘制，不用更晚的成功记录遮盖它。被环淘汰的故障无法恢复；+继续表示早期记录丢失。全64位status/sequence与规范UUID保留，不能冒充当前显示provider返回。
- 保留R023已避开圆角的(64,96)/320×160/五行20列、3×5字形scale4和8秒；153600 framebuffer读取、102400写入、3次DSB、660 MDP读与4次MDP等待的上限不变。像素保存、二次验证、恢复、读回及code4优先级不变。
- EnumaJournalConsoleDrain统一为有界的loss头+最多128条记录；OutputString任一错误或warning立即停止，accepted只计完整成功行，不自动重试。
- EnumaProbe的普通行输出锁存首次失败；开始前要求可用ConOut，内存图清理后及日志回放后检查错误，不在缺失/部分日志后进入UniXNU。移除双写的既有成果保持。控制台开关现在由DSC全局BuildOptions转交到C编译参数，诊断新profile启用ENUMA_PROBE_JOURNAL_REPLAY=1。

## 已执行离线验证

输出统一为out/diagnostic-log-20261026：

- pixel-tests1：194组生产C页面，9932800像素、64个status位、128个GUID位及完整序号反读；25字形唯一；严重度/最新同级/淘汰/无GUID拒绝；24通道排列、1600行/阶段失败边界及旧replay/像素回归。ASan/UBSan与真实EDK AArch64 wrapper通过，wrapper栈205040字节；不是硬件栈高水位。
- console-tests2：17条编译/执行命令通过；129行完整回放，129个错误位置+129个warning位置都立即停，不重试；首次错误锁存；实际Probe三种AArch64编译路径通过。
- menu-qemu1：21条命令通过；真实AAVMF GraphicsConsole、RAM GOP和固定UniXNU Ui/Menu使用新Drain，800×600和768×1024下日志回放、菜单绘制、选择/取消/确认、文本fallback及无输入默认选择通过。QEMU脚本键盘不是enuma按键驱动；WT软件访问路径不证明实机内存类型/alpha/SMMU。
- policy-tests1：20项新配置及旧R023回归通过，新的replay3必须独立R024声明和原预算，拒绝旧授权/冲突profile/扩大预算。
- decoder-tests1：4项转录检查通过，矛盾严重度、遮挡字符、错误字段宽度或5冒充S均拒绝。

## 构建与产物

完整build3成功，结果见build3/build-result.json。build1因Windows CRLF使DSC补丁上下文不匹配而失败，目录保留；修正工作DSC为LF后，build2又发现INF不能读取该DSC宏，实际cc_resp展开为空导致编译失败。移除INF局部转交并改为既有DSC全局BuildOptions补丁，启动独立build3；console-tests2再次通过。两个失败目录保留。原补丁及冻结资格未改。完整构建采用隔离源码快照、固定依赖和元数据派生，不把基线提交8680ea7称为本次未提交代码的产物。

本profile仍在Core诊断provider终端停止，先于BDS。诊断FD的Probe安全入口返回EFI_UNSUPPORTED，LTO裁掉业务代码；实际晚期控制台/菜单另外独立链接和QEMU验证，不意味着本候选实机将进入ConOut或菜单。正式GOP生产准入、持续Frame验证、alpha/stage2/SMMU和requirements22仍未闭合；全局DEBUG仍为Null SerialPort独立事项。下一步沿“生产GOP准入→BDS GraphicsConsole/ConSplitter→可见ConOut→菜单/输入”推进，不改verified或内存字段。

R024只预留给本次独立候选的离线报告，不是批准，没有设备trial/claim。部署前还需新实际PE指令审查、独立精确范围runner资格、用户单次放行与当前拍摄、即时身份/备份/恢复/时钟门。当前无需用户开始录像。本轮最后已知设备证据仍为S051在20:42:57恢复Android且独立核验通过；未查询当前实时设备。


## 最终产物与实际链接纠正

FD：1179eb69f81f303c0fd6012b3aaa7597aed589366a4dc88462391a389f44d2b7；Boot v3：e789df474e05e4de37f329cc4a1dd623cb1975ede0ae48b134bcf866db9f2969。均在qualification1/。结构/OEM/DEPEX、实际PE、编译宏/字库、固定FAT/BootShim和打包解包通过。Core .text及初始化.data与R022逐字节相同；compiled-code-review.json记录新页严重度选择、64位取值、ROI/8秒/3DSB/读写上限/完整恢复与code4优先的关键指令复核，不冒充完整执行资格。

实际检查发现simplefb-contract.patch在Probe入口保留诊断EFI_UNSUPPORTED安全返回，LTO裁掉晚期实现。完整诊断FD不能声称晚期回放/菜单代码保留。新scripts/check_console_module_link.py只在独立out里用同一实际源/AutoGen/库重新编译链接，唯一覆盖ENUMA_DIAG_SIMPLEFB=0；不修改诊断FD或其安全门。console-link2的PE 210a2b61d816c03f7cb89c1184690f43a608f7fba1e2cfb69885838cbb4f4d94 包含完整日志串、快照GUID、校验/会话存储和真实UniXNU菜单实现，未打包/未执行。console-link1因LTO内联UniXNURun而使过严符号断言失败，已改为检查实际保留的EnumaProbeEntry、UniXNUMenuRun和日志实体；失败报告保留。

冻结复核计数：{'R022': 43, 'R023': 28, 'current_evidence': 8, 'local_media': 2}，与历史资格或本轮文档前快照一致。完整证据入口reports/enuma-diagnostic-log-development.json。console-tests1保留INF修正前测试，console-tests2绑定最终源码。构建日志含WSL/DrvFS时钟偏差警告；未改系统时钟或权限，各次使用全新构建目录，没有复用旧对象，打包PE逐字节匹配实际输出，完整源manifest复核通过。当前无需用户录像、无设备操作或提交推送。

最终完整性核验见final-validation.json：2399份原始源码、2401份快照文件、27份打包资格文件及独立链接/代码审查绑定均匹配。设备仓diff检查通过；固件严格diff检查仅报告EnumaProbe.inf第29行末尾新增空行，未伪称全部格式检查通过。为保持本轮已资格源码原字节未在构建后清理；下次构建前可移除该非功能空行。


## D-306：R024单次批准与录像就绪，S052尚未发图

用户明确“批准实机 录像已就绪”，仅D305镜像e789df474e05e4de37f329cc4a1dd623cb1975ede0ae48b134bcf866db9f2969一次临时boot，内缩(64,96)/320×160/8秒、replay3真实完成返回，仍不进正式GOP/ConOut/菜单。独立execution1元数据派生保持镜像原字节；execution-review和新R024一次性runner测试通过。S052未claim/未发图，立即执行门仍核对enuma身份/root/A槽/解锁/备份/时钟，异常停止追加并恢复。旧consumed保持，不提交推送；本地manifest绑定当前文档与脚本。执行证据out/r024-live-20261026；媒体目录D:/Code/PortingiOS/enuma/Media-enuma/S-052-R024。


## D-307：S052真实日志核对完成与固定人工校验流程

R024已单次消费，21:56:12发图，Android66.234秒，原点40.761..40.818唯一code5；21:58:12独立恢复通过。用户“能对上”确认助手先保存后展示的五行，随后查本镜像目录归因I2C StartImage返回EFI_SUCCESS（ordinal31/sequence185/GUID04de8591-d2b3-4077-bbbe-b12070094eb6）。新字形/完整页面本图可读，不称全部字形/8秒持续或正式GOP/ConOut/DEBUG/菜单通过；requirements22不清。证据reports/enuma-native-route-S-052-result.json、reports/enuma-s052-visible-log.json、out/r024-live-20261026。用户“以后都这样校验”：助手先独立读图落盘→展示五行→用户确认/纠正→精确镜像目录归因；不确定写?，不补猜，不再要求用户先盲抄。媒体本地、旧消费不复活，无追加启动/提交推送。
