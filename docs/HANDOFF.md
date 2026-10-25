# 当前状态：D-185，S-005入口前自动返回，转向原厂包装层/构造器的真实缺口

2026-10-25（Asia/Shanghai）S-005于15:39:52发出。fastboot返回0/2.641秒，5.110秒断开，21.141秒观察ADB，35.219秒完成Android/root/原分区摘要核验；15:40:47再次独立enuma/Android完成/root/A槽/解锁/boot_a与vendor_boot_a及本地备份摘要一致。bootreason=bootloader；253/253录像帧可解码，抽样Android→fastboot→黑屏→MI/HyperOS→Android，未请求人工恢复，抽样未见按键。当前Android正常，无人工或审批待办。

镜像d2de38822ec27ee2b7ebcfc4328eea4a8c6ab192ab72b396a09f89952ab7830a，103817216字节；FD93dd586bb0b6f546164547e94975b34b4855df07b3c4758a396d5cca23debf65；归档out/full-boot/transport/pe-entry-boundary-cb9e568，已consumed，不重试。源码仍firmwarecb9e568/UniXNU5fdbd5d，相同96MiB FAT/display-thread0/GUID-only/fallback0；执行前230cc9f已推送。新point20在实际Core 0xc418门调用后0xc428才间接调用PE入口；桥接句柄/文件/point/GUID、2秒延时、reset/deadloop及参数顺序静态审核通过。六项破坏负例拒绝，旧13/15回归通过，OEM32PE/DEPEX/AOSP/SEC配置0通过。clock-skew警告已记录，实际包装PE/map/编译宏绑定，不以构建退出码代替资格。

结合S-004（调用前自动返回）与S-003（调用后超时且已人工恢复），主判断（中等置信）进一步偏向PE调用区间、原厂包装层/构造器/主函数或其返回后处理，降低CoreStartImage入口前分配等路径的优先级。自动返回/时序不唯一证明门命中，不能称PE入口已执行或显示驱动挂死。S-003/004/005不是只差一个字节或严格全PE相同的样本；S-003/004配对配置仅point不同且PE差异已审，S-005有真实新增桥接编译形态单独资格。没有13项运输、GOP、XNU或iPadOS运行通过证据。

本轮继续只读逆向，复用已锁定OEM DisplayDxe 6c6351c3…347f425：入口包装器0x114c在0x1190先调构造器列表0x123c，再于0x120c调0x1508→主函数0x16e8。列表含十个有序调用5848/5888/5918/59f8/5b60/5d70/5e5c/612c/6628/6ffc；实际DXE服务表GUID05ad34ba-6f02-4214-952e-4da0398e2bb9与HOB表GUID7739f24c-93d7-11d4-9a3a-0090273fc14d已读出。新增audit_display_constructor_path.py绑定原XBL/PE摘要和具体调用顺序，删除构造调用负例拒绝，报告enuma-display-constructor-path.json。此为静态调用路径，未证明任一构造器运行/失败；不把正常UEFI表要求当成已缺失。

下一步优先顺序：一，沿这十个真实构造器，把标准gRT/gBS/gDS/HOB、内核接口及后续库初始化与现有Mu/同SoC提供者的ABI和实际来源逐项对应，复用已有实现，不造stub或补常量canary；历史D-040匹配前缀存在仅历史支持，不等于当前完整表/值。二，使用已有point21直接PE返回边界或对目标活动映像的真实UEFI服务调用/返回取证，区分构造/主函数与CoreExit/LongJump/CoreConnectHandlesByKey；具体候选需先审适用性和实际PE。UEFI StartImage在相关句柄变化时返回前还要连接控制器，故不能将point13超时直接等同于PE没有返回。新21/服务候选尚未实现资格或上机，不套旧小载荷结果。三，有具体缺口后做真实适配并回完整链错误采集，避免无限单点复位。

本轮仅S-005一笔；未发point21、未修改OEM字节或运行新服务探针。所有已执行镜像consumed，S-001/002/003此前恢复事实保留。主证据out/device-tests/20261025T153938-dxe-driver-return，录像out/camera-capture/20261025T153935-system-transport，独立核验out/device-tests/20261025T154047-recovery-reconciliation.json，公开结果enuma-system-transport-S005-result.json；原result.json未被独立核验重写。

下一笔沿用户无需逐笔批准授权，仍先来源/构建/实际产物资格、当前文档提交推送及即时设备/备份/采集/恢复守卫。超时停止追加优先恢复，同轮落实文档；恢复核验后自动离线分析。不flash/erase/改槽，不改board/plan内存字段/512MiB，不置verified；R-002/R-015/旧像素硬边界保持。
