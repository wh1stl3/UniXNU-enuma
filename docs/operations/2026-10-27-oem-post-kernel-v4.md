# early-v3确认后的代码归因与post-kernel-v4（2026-10-27）

用户确认四张照片完整五行字符串一致。保留out/oem-early-20261027/media-review/independent-read.json原始待确认记录，新增confirmed-read.json；公开trial报告更新人工确认。early-v3单次已消费，Android/root/A槽/解锁和原分区摘要独立恢复核验通过。本轮仅离线。

## 当前最大嫌疑与置信边界

最大可操作嫌疑是Kernel查询返回后的未观测构造区间，尤其HOB遍历及随后的缓存维护/注册，而不是LocateProtocol内部挂起。其证据强于直接跳到SID/MMU：现场已确认call3/sequence7、RVA0x616c真实返回EFI_NOT_FOUND，尚没有后续服务或驱动返回证据。对单一根因的置信仍低；S04画面清理/恢复是并列竞争解释，不能以最后一幅图排除它。

**不是“缺Kernel协议必然致命”。** 精确OEM PE SHA256为6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425。0x616c CBNZ在失败时走0x61ac→0x61c0→0x61f4；后者以0x3e418的GUID 8ec2bd8d-56d7-49ef-8796-631778f8ebf8查Scheduler Interface HOB，找到才在0x620c读取HOB+24的指针，未找到返回NULL；0x61b4构造器仍返回0。不能伪造Kernel协议成功或在这里硬填指针。

板级实际来源：PlatformPeiLib/PlatformPei.c初值SchedulerInterfaceAddr=0；XblProtocols.c只按名字FD Reserved/FD_Reserved寻找范围，未找到则直接返回。enuma MemoryMapLib.c没有这两个名字；MemoryMapHelperLib以AsciiStriCmp精确匹配，失败不改输出。故该编译路径不会构造Scheduler HOB，不能把存在Sched Heap区域误作接口已发布。其他运行时生产者和实际HOB内容仍未现场导出，以上是静态来源判断。Xbl解析器另有Target/Source寄存器使用和无界函数扫描问题，但当前无匹配region时并未进入扫描，不能把这些静态风险当作本次故障或为了启用它而改内存表。

## 实际后续执行顺序

1. 0x1400调用Kernel构造器0x612c，失败回退上文HOB查找；0x5d88按HOB length前进直到终止节点，循环没有独立上限。存在坏HOB时的风险，但尚无本次HOB损坏证据。标准HOB表先前已被HobLib取得，不能称标准HOB缺失。
2. 0x1438→0x6628：调用0x374c处理RVA0x6a84起的代码区域；0x6b8c实际数据长度264字节。0x3ca8读取CTR_EL0得cache line大小，0x36bc按行调用0x3d84（DC CVAC），随后DSB/ISB。此路径没有包装服务事件，当前没有这段cache操作完成或异常的现场证据。
3. 0x1470→0x6ffc→0x5b64：注册guided-section handler。通常在0x5ca4→0x3bb8→0x3b30→0x3a9c执行16字节AllocateCopyPool，包装返回RVA仍0x3abc；这是call4的强静态预期，实际以新日志为准。之后0x5cc4调用InstallConfigurationTable，沿已修复Core发布钩子同步私有表。
4. 构造完成才到显示主入口；SID/MMU属于更后阶段。缺少S05不能证明从未到达后段或驱动未返回，因为显示出口可能拒绝，且本次只有四张静态照片。

调查优先级：上述构造区间与S04清理优先；后段OEM/显示出口次之；已经正常返回的Kernel Locate服务内部死锁被本次记录排除。配置表失同步是已修复代码缺陷，但本轮进展不能单独证明它是前次根因。

## 下一版要区分什么

新scope oem-post-kernel-v4，selected_call严格为4。保持原厂PE、现有SystemTable修复、窗口ROI(64,96)/320×160/每窗8秒、最多五窗/40秒。call0..3仅记录并转发，不画窗口；不增加物理读取范围、MMIO写入、内存字段或verified。

- E01/S02：call4转发前/真实返回，预期上述16字节分配。E01可证明新版已经到达下一服务，从而降低该次前段构造挂起嫌疑；不能证明旧版S04清理成功。
- E03/S04：第一次SID LocateProtocol入口/返回（GUID54b6d3b4-5d33-4f91-8600-6c41d5deb19a），明确不再是Kernel。
- S05：真实CoreStartImage返回，仅记录真实状态，不能冒充生产GOP/ConOut/BDS完成。

无E01仍无法区分未到call4和输出拒绝；E01有而S02无需区分服务/窗口问题；S02有而后段无则调查注册、主入口与出口依赖。由于取消前四窗会改变时序，本版是隔离候选，不是同扰动的因果证明。无法从单次进展宣布修复根因。无独立看门狗和持久崩溃记录，未来实测仍需当前人工恢复和录像。

## 离线验证与交付

check2覆盖（增加真实顺序的Kernel NOT_FOUND前缀，确认无旧窗口）v2/v3/v4真实追踪状态机、失败/重入/不返回和配置表真实Core扩容/通知回归及两处删除负测；binding1覆盖精确PE重定位、错PE拒绝和AArch64板级对象。9项admission和9项页面解码测试通过，包括call4误选和跨版本误读拒绝。build1和qualification1已完成，最终结果见下文。旧失败候选不重试，冻结产物不回写，源码改动导致旧在线admission失效属于预期，不重写历史资格。


# 当前：post-kernel-v4完整固件与离线资格完成（2026-10-27）

用户已确认early-v3四组完整字符串一致；旧单次consumed且Android恢复独立核验通过。本轮无设备命令。当前最大可操作嫌疑为Kernel查询返回后的构造未观测区间（HOB遍历、264字节代码缓存维护、guided-section注册），S04窗口清理是并列竞争解释。缺协议本身并非已证根因；详情和推翻条件见operations/2026-10-27-oem-post-kernel-v4.md。

新镜像out/oem-post-kernel-20261027/qualification1/image.img，SHA256 `233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7`；FD SHA256 `1dd0834df9348e3cb97667877cfd8ecece8d8e86024658262e18fdbbbcf8b9f3`。原厂PE、内存配置及同步修复保留。E01/S02改为call4（第五次包装服务），E03/S04改为SID，S05是真实驱动返回；最多五窗/40秒，未上机。

34项Python、check2 ASan/UBSan/真实Core/两处源码删除、binding1、全FD及Boot v3回读通过；最终机器码32处原运行时+23处同步/选择指令删除和一次GUID变异拒绝。Core同步函数及配置表函数与v3机器码完全相同；观察函数只在call选择立即数有一字节差异，另有协议GUID和session数据变化，不等于整份PE相同。

固件提交f82039e；构建是以7c97dc6为基线的工作树快照，不称提交后重编。固件两次GitHub推送分别连接重置/连接超时，设备仓a1c48f2推送同样连接443超时，均未确认远端发布。最终离线admission通过，新trial账本未消费。不得将本轮编出固件当作实机启动授权或故障修复证明；下次仍先满足发布、精确单次、即时设备/备份和当前录像/恢复门禁。R027和已消费旧镜像冻结，媒体仅本地，共享主线只读。当前无人工待办。

以下为历史记录，以本节为当前状态。

精确路径静态校验在out/oem-post-kernel-20261027/path-audit.json，机器码对照在linked-comparison.json；初次对照脚本将CMP差异字节误标为指令起始偏移0x160，实际为该指令第二字节0x161，修正检查后通过，固件未改。最终宿主结果与源码绑定保留在check2/result.json。


# 当前：v4单次已执行，自行返回Android；摄像头日志不可完整解码（2026-10-27）

用户授权摄像头测试并确认当前在场可恢复。镜像233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7、trial f5854414-b040-49ff-9291-3007c5c3f560仅boot一次，发送/启动成功，单次consumed，不重试。源码/本次准备29301e9及固件f82039e均已推送。

摄像头与ADB均观察到Android返回，用户明确未做按键恢复；独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a摘要通过。执行器只等待fastboot，误记manual-recovery-needed；原始state-before-android-reconcile.json和transport保留，追加android-return-observed.json、android-return-verification.json并纠正当前状态为已回Android、manual_recovery=false。此为观察终点缺口，不能写作设备75秒仍挂住或人工恢复，也不能由自动返回证明DisplayDxe成功。

相机0 DSHOW采集1920×1080、2135帧、约428.688秒，原始MJPG视频及每秒JPEG均在out/oem-post-kernel-20261027/camera-live1。录像包含两段五行亮字窗口，但过曝/虚焦使数字连成白块，无法可靠恢复完整stage/call/status/session；未按预期值补猜，未送入严格解码器。检查低饱和候选原视频帧后仍不满足完整字符串验收。日志内容验收未通过，用户无需盲抄此糊图；原始影音仅本地。

AVI写入标称10fps，但实际采集约5fps，播放时长不是现场耗时；时序以UTC状态、原始JPEG文件时间及主机transport为准，不用AVI时码推算真实窗口持续时间。电源键未保证入镜，未从手部画面推断操作，自动返回依据用户明确反馈与设备核验。

当前没有新根因结论。两段文字出现与自动返回不足以验证call4/SID/真实驱动返回，仍按既有HOB/缓存/注册及取证清理竞争解释分析。后续先离线修复执行器Android终点观察，校准摄像头近拍/对焦/曝光并解决真实时间戳，再安排独立新候选；不为改善拍摄原样重启已消费v4。R027及旧候选冻结，共享主线只读，当前无按键待办。

报告reports/enuma-oem-post-kernel-trial-20261027.json；设备证据out/device-tests/oem-f5854414-b040-49ff-9291-3007c5c3f560；相机判读readability.json、review-sheet、video-detail保留本地。

