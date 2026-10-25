# 完整输入 PE 入口前隔离（设计与资格记录）

S-003调用后point13超时且已恢复，S-004调用前point15自动返回并恢复核验通过。优先使用已有point20：Image.c中Image->Started置位后、Image->EntryPoint间接调用前。此门受EnumaStartingImage/EnumaStartingFile及完整DisplayDxe GUID约束，嵌套的其他StartImage句柄不能冒充目标。保持完整96MiB FAT、同固件cb9e568/UniXNU5fdbd5d、display-thread0和fallback0；不改原厂PE、内存、verified或分区。

主判断仍为CoreStartImage至PE入口/其返回处理区间，非已证明显示驱动挂死。固定Core源码中前置部分含句柄检查、跳转缓冲分配和SetJump，后置部分还含CoreExit/LongJump及CoreConnectHandlesByKey。UEFI规范也规定驱动改变句柄时StartImage返回前须连接相关控制器，因此入口直接返回与StartImage返回不能混同。来源：[UEFI 2.10 StartImage](https://uefi.org/specs/UEFI/2.10/07_Services_Boot_Services.html#efi-boot-services-startimage)。

point20若自动返回，支持入口前可达性但不证明PE入口执行；下一步才检查直接返回/包装器及真实依赖。若无返回，提升CoreStartImage前置、门桥接或复位路径的嫌疑。自动返回的时间和USB仍不是唯一门命中证明。旧小载荷结果不能替代完整输入候选。

实际资格需绑定新FD/raw/boot-v3、编译宏、Core/map、桥接句柄/GUID条件和紧邻间接入口调用，含破坏调用/门控的拒绝负例；原厂32PE/DEPEX及SEC配置、AOSP完整FAT回读不变。出现clock-skew警告时检查实际包装代码及当前编译宏，不单凭构建退出码或文件时间通过。

本节初写时正在构建，尚无point20实机结果。最新资格和实测在后续追加；当前唯一状态以STATUS/HANDOFF为准。文档和代码提交推送、即时设备/备份/相机/恢复门禁满足后沿现有授权执行一笔。超时停止追加、先恢复、同轮记录，恢复核验后自动离线分析，不原样重试。

## D-184：point20完整输入资格

S-003调用后point13超时并于15:24:33恢复核验通过；S-004调用前point15自动返回，ADB21.172秒、Android完成36.672秒，15:31:36再次独立root/A槽/解锁/原分区及备份摘要通过。所有已执行镜像均consumed，不重试。当前无人工或审批待办；本轮15:34即时Android/root/原槽/解锁/设备与备份摘要复核通过，相机1920x1080实际画面已核为Android桌面。

新point20保持完整96MiB FAT、固件cb9e568/UniXNU5fdbd5d、display-thread0、精确DisplayDxe GUID-only/fallback0，无新源配置/原厂PE/内存/verified/分区改变。镜像SHA256 d2de38822ec27ee2b7ebcfc4328eea4a8c6ab192ab72b396a09f89952ab7830a，103817216字节，out/full-boot/transport/enuma-pe-entry-full-input-v3.img；FD93dd586bb0b6f546164547e94975b34b4855df07b3c4758a396d5cca23debf65；冻结归档pe-entry-boundary-cb9e568。尚未上机或consumed。

完整构建/32OEM PE与DEPEX/AOSP完整FAT回读/SEC配置0通过。实际Core将GUID过滤内联到EnumaImageEntryCheckpoint；审核器新增只接受具体编译形态的point20模式：global scheduled handle非空、等于调用句柄、file非空、point20条件、两半GUID、2秒专门化延时/ResetCold/死循环，以及CoreStartImage内检查点之后的EntryPoint读取、相同句柄/SystemTable参数和blr。审核调用点0xc418、间接PE入口调用0xc428，门先于入口。这里是静态调用边界，非已执行证明，不泛化为其他编译结果自动通过。

删除间接入口调用、改GUID、错point、去掉空句柄门/句柄比较及改纳秒参数共六负例拒绝；旧13/15审核负例回归通过，冻结清单绑定的wrapper离线通过。构建有clock-skew警告，实际FD/PE/map/编译宏已核并未仅凭退出码；不能因此宣称任意旧输出均有效。

主判断（中等置信）仍是CoreStartImage到PE入口/返回处理区间；StartImage后置还有CoreConnectHandlesByKey，不能仅将调用后超时归为驱动内部。现有point20复用原实现，未造stub或补canary。若新门自动返回，支持入口前可达，随后优先查PE包装层/真实依赖及直接返回路径；若超时，提升StartImage前置/门桥接/复位问题。任何自动返回或时间仍不能唯一证明门命中，不声称GOP/XNU/iPadOS通过。

当前文档与代码推送后，沿用户无需逐笔批准授权，用run_system_transport_trial.py --qualification reports/enuma-full-input-pe-entry-boundary.json --execute执行单笔；相机先开启，再即时身份/备份/恢复守卫。75秒无返回立即停止追加并先恢复；恢复核验后自动离线分析，不重试失败镜像。无flash/erase/改槽/内存字段/verified变更，R-001/R-002/R-015及旧像素边界保持。

详见operations/2026-10-25-pe-entry-boundary.md，机器证据enuma-full-input-pe-entry-boundary/core/negative.json。UEFI StartImage来源：https://uefi.org/specs/UEFI/2.10/07_Services_Boot_Services.html#efi-boot-services-startimage 。当前尚无point20实测，PMGR/UFS/root/Data/GOP及系统运行待闭合。

## D-185：S-005自动返回与构造器路径审计

2026-10-25（Asia/Shanghai）S-005于15:39:52发出。fastboot返回0/2.641秒，5.110秒断开，21.141秒观察ADB，35.219秒完成Android/root/原分区摘要核验；15:40:47再次独立enuma/Android完成/root/A槽/解锁/boot_a与vendor_boot_a及本地备份摘要一致。bootreason=bootloader；253/253录像帧可解码，抽样Android→fastboot→黑屏→MI/HyperOS→Android，未请求人工恢复，抽样未见按键。当前Android正常，无人工或审批待办。

镜像d2de38822ec27ee2b7ebcfc4328eea4a8c6ab192ab72b396a09f89952ab7830a，103817216字节；FD93dd586bb0b6f546164547e94975b34b4855df07b3c4758a396d5cca23debf65；归档out/full-boot/transport/pe-entry-boundary-cb9e568，已consumed，不重试。源码仍firmwarecb9e568/UniXNU5fdbd5d，相同96MiB FAT/display-thread0/GUID-only/fallback0；执行前230cc9f已推送。新point20在实际Core 0xc418门调用后0xc428才间接调用PE入口；桥接句柄/文件/point/GUID、2秒延时、reset/deadloop及参数顺序静态审核通过。六项破坏负例拒绝，旧13/15回归通过，OEM32PE/DEPEX/AOSP/SEC配置0通过。clock-skew警告已记录，实际包装PE/map/编译宏绑定，不以构建退出码代替资格。

结合S-004（调用前自动返回）与S-003（调用后超时且已人工恢复），主判断（中等置信）进一步偏向PE调用区间、原厂包装层/构造器/主函数或其返回后处理，降低CoreStartImage入口前分配等路径的优先级。自动返回/时序不唯一证明门命中，不能称PE入口已执行或显示驱动挂死。S-003/004/005不是只差一个字节或严格全PE相同的样本；S-003/004配对配置仅point不同且PE差异已审，S-005有真实新增桥接编译形态单独资格。没有13项运输、GOP、XNU或iPadOS运行通过证据。

本轮继续只读逆向，复用已锁定OEM DisplayDxe 6c6351c3…347f425：入口包装器0x114c在0x1190先调构造器列表0x123c，再于0x120c调0x1508→主函数0x16e8。列表含十个有序调用5848/5888/5918/59f8/5b60/5d70/5e5c/612c/6628/6ffc；实际DXE服务表GUID05ad34ba-6f02-4214-952e-4da0398e2bb9与HOB表GUID7739f24c-93d7-11d4-9a3a-0090273fc14d已读出。新增audit_display_constructor_path.py绑定原XBL/PE摘要和具体调用顺序，删除构造调用负例拒绝，报告enuma-display-constructor-path.json。此为静态调用路径，未证明任一构造器运行/失败；不把正常UEFI表要求当成已缺失。

下一步优先顺序：一，沿这十个真实构造器，把标准gRT/gBS/gDS/HOB、内核接口及后续库初始化与现有Mu/同SoC提供者的ABI和实际来源逐项对应，复用已有实现，不造stub或补常量canary；历史D-040匹配前缀存在仅历史支持，不等于当前完整表/值。二，使用已有point21直接PE返回边界或对目标活动映像的真实UEFI服务调用/返回取证，区分构造/主函数与CoreExit/LongJump/CoreConnectHandlesByKey；具体候选需先审适用性和实际PE。UEFI StartImage在相关句柄变化时返回前还要连接控制器，故不能将point13超时直接等同于PE没有返回。新21/服务候选尚未实现资格或上机，不套旧小载荷结果。三，有具体缺口后做真实适配并回完整链错误采集，避免无限单点复位。

本轮仅S-005一笔；未发point21、未修改OEM字节或运行新服务探针。所有已执行镜像consumed，S-001/002/003此前恢复事实保留。主证据out/device-tests/20261025T153938-dxe-driver-return，录像out/camera-capture/20261025T153935-system-transport，独立核验out/device-tests/20261025T154047-recovery-reconciliation.json，公开结果enuma-system-transport-S005-result.json；原result.json未被独立核验重写。

下一笔沿用户无需逐笔批准授权，仍先来源/构建/实际产物资格、当前文档提交推送及即时设备/备份/采集/恢复守卫。超时停止追加优先恢复，同轮落实文档；恢复核验后自动离线分析。不flash/erase/改槽，不改board/plan内存字段/512MiB，不置verified；R-002/R-015/旧像素硬边界保持。
