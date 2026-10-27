# D-301 / R-023：内缩归因日志候选，离线准备完成，尚未上机

2026-10-26，唯一写入会话。用户要求准备下一次实机、避开圆角并尽可能推进真实UEFI日志。本轮仅离线代码、测试、构建、资格和门禁，不自动提交推送；R-023 pending，计划 S-051 未执行、未 claim。此前 S-050/R-022 consumed 和原始照片不变。

## 实质代码与选择

S-050 的 ordinal31/status0/+ 可读，但左侧 C 被圆角遮住，也没有 GUID/sequence。选择新独立 replay=2：日志区 x=64..383、y=96..255，320×160，五行20列，原3×5字形、scale4、行距32和8秒单次停留。相对旧256×96，读写面积增加25/12倍。选择一页完整归因信息，避免轮播增加停留和拍摄负担；内缩是待实测的布局改进，不能据合成预览宣称物理圆角已通过。

五行：`C0d Oxxxxxxxx+`（无丢失时无+）、`S`+完整16位状态、`Q`+完整16位序号、`G0`+GUID前16位、`G1`+GUID后16位。GUID采用canonical字节顺序去连字符，不是内存LE字节序。显示最新已完成point13/start-return；快照序号、数量、丢失计数、HasGuid全部校验；最新point13无GUID则拒绝显示，不偷偷选更早记录。没有当前provider返回值、boot ID或全局DEBUG；只显示一个归因记录，未声称128条全部上屏。

代码：firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/PixelAttributedLogPage.h；PixelTransaction.h 和 EnumaPixelTransactionArm.h 分别使用同一新坐标。旧 PixelLogPage.h 原字节未改。私有快照v1不变，不改内存基址/大小、verified、requirements22、页表、寄存器写入或GOP准入。

## 新事务的精确范围

正常路径保存51200字，第二次完整Native6复核，再绘制/读回/8秒停留/全区域恢复/读回。最大153600次帧缓冲读取、102400次写入、3次DSB；原660次MDP读取、4×100ms等待保持。任何开始写入后的失败都尝试全区恢复，code4最高优先；code1无存储、code2图案失败已尝试恢复、code3停留失败已尝试恢复、code5仅CPU事务及恢复读回。

实际PE入口栈205328字节；嵌套Native6采样器8880字节，现有主栈262144字节未改。代码检查不是实际栈高水位测量。更大区域的额外执行时间仍未实测；使用事前固定8秒窗口，唯一code5窗39.252..41.748秒，失败/重叠/时钟歧义停止追加，不根据新观测放宽。R023主机观察截止从发出boot前计75秒；设备返回后独立恢复核验仍必需。

## 真实产物与验证

- FD：`0db8b750bc1fdfa90fa0b1fce15c7a52889aa90653fe40378bda5a58920f6a8f`。
- 完整Boot v3镜像：`360b5ec7eeb26f76858069fba78d3f69bbe90d40f125730dfcd324dbe69fbd8a`；路径 out/attributed-log-20261026/qualification3/image.img。
- FD构建：out/attributed-log-20261026/build2/build-result.json，完整3MiB，source-manifest f9f8d2a6d9e19616d71d922fe3a8b10caf14d4aa117ecd6a020ff0d5eede4c78；固定依赖和现有未提交源码快照，不能称基线提交自身产物。
- full FAT原摘要49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773；实际契约生成和四文件mtype读回，BootShim+FD及FAT的AOSP打包解包逐字节通过。
- 194组生产C页面/9932800像素严格反读，64位状态、128位GUID、全宽序号；损坏像素/遮挡字符拒绝。24通道排列、1600行/阶段读写失败边界及其他故障路径、旧日志和像素测试通过；真实EDK ARM wrapper栈205040字节。out/attributed-log-20261026/tests2/result.json。
- 真实FD 80文件/30 OEM PE与DEPEX审计；实际Core/provider及Probe/BDS/UniXNU/GraphicsConsole PE、编译宏、打包GUID/PE目录和字形表绑定。qualification3/qualification.json 为结构与打包阶段证据，其pending列表记录该阶段尚未完成项；后续 code-review.json 和 preparation1/preparation.json 分别关闭代码审查与本地准备，不改旧阶段报告。
- 实际PE人工控制流审查及指令复核：code-review.json。Core整PE不同，但.text及初始化.data与冻结R022逐字节相同；不把整PE说成相同。新provider逐项检查协议ABI、序号/归因、坐标、预算、停留、恢复和无缓存/映射设置指令。
- 解码入口 scripts/decode_attributed_pixel_log.py，--qualification 可绑定本镜像实际打包GUID/PE目录；名字不是按ordinal猜测。输入仍需从真实画面完整抄录，不能把合成内容当设备证据。

完整构建首次build1失败：开发入口未转交ENUMA_RAM_PAYLOAD，缺PayloadContract.h。已补全固定FAT契约和独立报告路径；build2成功。qualification1因Python3.10缺tomllib兼容失败；qualification2因禁止指令正则误匹配原始机器码字节dc失败；修复解析列后qualification3通过。失败目录保留，未伪称通过。历史报告未覆盖。

## 执行准备与验收

R-023是全新待批准范围，不继承S050单次或旧录像确认。A方案：精确本镜像单次S051，当前人工录像、即时enuma身份/root/A槽/解锁/设备及本地备份/时钟门均通过后临时boot；B方案：继续离线，不发图。推荐A作为下一次可检查结果的候选，但必须用户明确放行并确认当前拍摄就绪。

入口脚本新增精确R023本地绑定和原子claim；未知镜像、范围变化、pending/consumed、缺当前拍摄、旧尝试UUID、旧issue记录、过时文档绑定均拒绝。只查询此前绑定enuma；不查询其他连接设备。不会自动删claim或重发。R022独立冻结路径保留，旧授权不复活。39项相关Python mock回归的最终输出见runner-tests2.json。

离线准备命令：Windows真实Python `scripts/r023_preparation.py --output out/attributed-log-20261026/preparation1`；然后 `scripts/run_system_transport_trial.py --qualification out/attributed-log-20261026/qualification3/qualification.json --local-preparation out/attributed-log-20261026/preparation1/preparation.json --human-camera-only`（无--execute）。授权/文档改变后生成新的preparation目录，不能覆盖旧绑定。

拍摄应包含整块五行日志及其出现/消失，锁定焦点并压低曝光，保存到 D:/Code/PortingiOS/enuma/Media-enuma/S-051-R023；合成预览 tests2/synthetic-preview.png 仅辅助构图，不是实机证据。首次结果需完整C0d、ordinal、status、sequence、G0/G1和+，关联本次执行UUID/镜像/媒体原始SHA，再查询打包GUID目录。缺字保留未知，不能补猜；无法读清、code4、歧义或恢复失败立即停止追加。

## 菜单距离与保留边界

本镜像仍在诊断provider返回的Core终端停止，未进入BDS/ConOut/菜单。D295归因ConOut、D296/297真实UniXNU菜单QEMU和WT后端成果保留并参与完整开发构建。下一条生产链仍是合格Frame/alpha与持续验证 → 同handle GOP+DevicePath → BDS连接GraphicsConsole/ConSplitter → 可见ConOut → UniXNU菜单及实际输入；不能清requirements22或夹带全屏/菜单实测。全局DEBUG的Null SerialPort独立未接通。

最后实机证据仍为18:23 S050恢复Android/root/A槽/解锁/备份核验；本轮未读设备，当前实时状态未知，无已知恢复按键欠项。R022原归档全绑定、原媒体及当前设备状态文件保留。设备HEAD89b609e、固件base8680ea7，迁移和本轮改动均未提交/推送；独立uefi-enuma和nuwa未操作。


## D-302：R-023单次放行及当前录像就绪

2026-10-26T12:41:22.383347+00:00，用户明确“录像就绪 开始推送”，仅镜像360b5ec7eeb26f76858069fba78d3f69bbe90d40f125730dfcd324dbe69fbd8a一次S051临时boot。R023 approved，当前人工拍摄就绪；即时身份/备份/恢复/时钟门由原guarded runner核验，未发图前不称通过。不得自动重试，旧consumed不变，无Git推送/分区刷写。执行证据入口out/r023-live-20261026。


## D-303：S051已恢复，内容待用户核对

R023一次已consumed，20:41:44发图，Android65.062秒，原点40.729..40.802唯一code5；20:42:57独立恢复通过。原始照片五行在屏内；用户要求人工逐字核对，独立判读已保存且未查询GUID目录，当前全文验收pending，不追加实机、不提交推送。证据reports/enuma-native-route-S-051-result.json与out/r023-live-20261026/postcheck.json。


## D-304：S051内容交叉核对及I2C归因

用户提供五行人工转录，与此前独立保存的助手判读按字段上下文/hex大小写规范化后逐字一致：ordinal31、status0、sequence185、GUID04de8591-d2b3-4077-bbbe-b12070094eb6。绑定本镜像实际PE目录唯一I2C；仅证明此前I2C StartImage返回EFI_SUCCESS，不证明总线/外设功能。照片中五行完整避开圆角；S/5、O/0字形相同确有辨识缺陷，依靠标签位置区分，后续新候选改善，不覆盖冻结图。原S051结果报告保存当时pending事实；新证据reports/enuma-s051-visible-log.json关闭人工核对项。R023已consumed，不再启动，无新实机授权、无提交推送。
