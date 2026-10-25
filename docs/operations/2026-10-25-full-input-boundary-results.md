# 当前状态：D-183，完整输入调用前候选自动返回，故障范围收窄

2026-10-25（Asia/Shanghai）本轮执行S-003/S-004各一次，未flash/erase/改槽。S-003返回边界point13于15:21:51发出，命令2.640秒返回、5.109秒断开，随后75秒无自动返回；人工恢复后15:24:33独立Android完成/root/A槽/解锁/原boot_a和vendor_boot_a及备份摘要通过。453/453主录像、742/742恢复录像可解码。该镜像d716e159…47f8304已consumed，原失败记录不改写。

S-004调用前point15于15:30:15发出，命令2.641秒返回、5.110秒断开，21.172秒观察到ADB，36.672秒完成Android/root/原分区摘要核验；15:31:36再次独立核验Android完成/root/A槽/解锁和设备备份摘要通过，bootreason=bootloader。258/258录像帧可解码，时间线抽样Android→fastboot→黑屏→MI/HyperOS→Android，未请求人工恢复，抽样帧未见人工按键。当前是已恢复Android，无人工或审批待办。

S-004镜像a21682ca083acf6bb6cb5e6c8ef021d7172c308a44855b12f82cf6237aa3c42e，103817216字节，out/full-boot/transport/enuma-display-precall-full-input-v3.img；FD10abab47280f13c78082e94a77a0a7bae398b23302274a57b6bbda50747599ba；归档precall-boundary-cb9e568，已consumed不重试。执行前9bdee97已推送，源码firmwarecb9e568/UniXNU5fdbd5d。两份保持相同96MiB FAT/display-thread0/GUID-only/fallback0，配对构建配置仅detail15/13，73个PE中71个逐字节一致，Core运行时代码不同，PcdDxe仅审核允许的debug GUID字段不同；不宣称整个FD只变一个字节。

主判断（中等置信）：完整载荷的调用前候选可自动返回，而调用后候选超时，支持目标调用前可达性，把CoreStartImage内部、PE入口和其原厂依赖路径提升为首要嫌疑；降低“完整载荷一律无法进入此前路径”及“RAM驱动先执行卡住”的优先级。时间/USB/自动返回不能唯一证明门命中，其他复位来源尚未排尽，不能据此证明DisplayDxe入口已执行、成功或内部挂死。没有13项运输结果、GOP/XNU/iPadOS实机通过证据。

静态佐证：S-003实际FD的APRIORI包含DisplayDxe而不含RAM载荷驱动；固定Core源码先排空Scheduled队列再处理普通依赖，与UEFI PI强顺序规则一致。该驱动不是此FV中DisplayDxe的调度前置，仍不排除更早体积/布局影响。公开来源：https://uefi.org/specs/PI/1.8/V2_DXE_Dispatcher.html 。审核与原厂32PE/DEPEX/AOSP往返/实际SEC TE配置0、Core/map/延时/负例和冻结清单绑定均通过；静态资格与上述实测分开。

下一步：复用已存在point20（Image.c在Image->EntryPoint调用前、受scheduled handle/GUID桥接约束）构建新的完整载荷精确门，禁fallback，核真实Core PE/map和间接调用顺序及负例后才可上机。若可自动返回，进一步提高PE入口/原厂包装层及其依赖嫌疑；若不返回，优先CoreStartImage前置处理/映像保护/路径或复位原因。先审现有上游和同SoC实现，不造stub、不引入canary值、不换内存地址。当前point20尚未构建/资格/上机，不能复用旧小载荷或旧审批结论。仅缺乏直接错误时作必要隔离，取得边界后回到完整链实修。

证据：reports/enuma-system-transport-S003-result.json、S004-result.json、enuma-full-input-boundary-pair.json、enuma-full-input-dispatch-order.json；S-004原始out/device-tests/20261025T153001-dxe-driver-return、录像out/camera-capture/20261025T152958-system-transport、独立核验out/device-tests/20261025T153136-recovery-reconciliation.json。S-001/S-002同样保持consumed和恢复事实。原失败镜像不重试，后续新软件按用户现有无需逐笔批准授权及源码/资格/文档推送/即时设备备份采集恢复门禁推进。board/plan内存字段/512MiB/verified/破坏性分区及R-002/R-015/旧像素硬边界不变。
