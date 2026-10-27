# v4手机重试明确授权（2026-10-27）

用户在已告知v4消费后明确“立刻重试”，随后指定手机拍摄并确认录像已开始、可人工恢复。此为本镜像一次明确重试授权，优先于历史不重试约束；没有复活/删除旧ledger。原trial f5854414-b040-49ff-9291-3007c5c3f560，新retry 7e4ec36d-755e-440a-8f47-3c98ae38dbdc，镜像SHA256 233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7，仅临时boot一次。

摄像头已退出本次门禁，手机媒体目录D:/Code/PortingiOS/enuma/Media-enuma/OEM-v4-phone-retry-20261027-7e4ec36d。独立out内retry runner沿原qualification validate、身份/备份/恢复和75秒门，仅把claim改为验证明确重试授权并在独立oem-runtime-retries中独占记账。旧执行器fastboot-only限制保持，若自行回Android则独立核验纠正，不因其误报要求人工再按键。原镜像/源码绑定/旧资格未改，脚本摘要另存。最大嫌疑与解释边界沿post-kernel-v4专项，不从模糊或缺失输出猜根因。

# 当前：v4单次已执行，自行返回Android；摄像头日志不可完整解码（2026-10-27）

用户授权摄像头测试并确认当前在场可恢复。镜像233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7、trial f5854414-b040-49ff-9291-3007c5c3f560仅boot一次，发送/启动成功，单次consumed，不重试。源码/本次准备29301e9及固件f82039e均已推送。

摄像头与ADB均观察到Android返回，用户明确未做按键恢复；独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a摘要通过。执行器只等待fastboot，误记manual-recovery-needed；原始state-before-android-reconcile.json和transport保留，追加android-return-observed.json、android-return-verification.json并纠正当前状态为已回Android、manual_recovery=false。此为观察终点缺口，不能写作设备75秒仍挂住或人工恢复，也不能由自动返回证明DisplayDxe成功。

相机0 DSHOW采集1920×1080、2135帧、约428.688秒，原始MJPG视频及每秒JPEG均在out/oem-post-kernel-20261027/camera-live1。录像包含两段五行亮字窗口，但过曝/虚焦使数字连成白块，无法可靠恢复完整stage/call/status/session；未按预期值补猜，未送入严格解码器。检查低饱和候选原视频帧后仍不满足完整字符串验收。日志内容验收未通过，用户无需盲抄此糊图；原始影音仅本地。

AVI写入标称10fps，但实际采集约5fps，播放时长不是现场耗时；时序以UTC状态、原始JPEG文件时间及主机transport为准，不用AVI时码推算真实窗口持续时间。电源键未保证入镜，未从手部画面推断操作，自动返回依据用户明确反馈与设备核验。

当前没有新根因结论。两段文字出现与自动返回不足以验证call4/SID/真实驱动返回，仍按既有HOB/缓存/注册及取证清理竞争解释分析。后续先离线修复执行器Android终点观察，校准摄像头近拍/对焦/曝光并解决真实时间戳，再安排独立新候选；不为改善拍摄原样重启已消费v4。R027及旧候选冻结，共享主线只读，当前无按键待办。

报告reports/enuma-oem-post-kernel-trial-20261027.json；设备证据out/device-tests/oem-f5854414-b040-49ff-9291-3007c5c3f560；相机判读readability.json、review-sheet、video-detail保留本地。

以下为历史记录。

# v4 摄像头单次启动准备（2026-10-27）

用户授权一次v4以核验新摄像头日志可读性，并确认当前在场可立即长按恢复。镜像233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7，trial f5854414-b040-49ff-9291-3007c5c3f560；尚未发图。两仓已补推固件f82039e/设备仓d5bc3d9，后文网络失败为历史状态。

相机0 DSHOW持续采集1920×1080至out/oem-post-kernel-20261027/camera-live1（本地MJPG视频、带UTC状态与每秒截图，无音频）。初始虚焦经用户调整，时间/日期可辨，HEX细字尚待本次实际图像检验，不预写清晰或通过。电源键动作未保证入镜，不从遮挡画面推断按键，人工恢复以用户反馈加独立设备核验。默认不上传任何影音。

最大可操作嫌疑仍为Kernel返回后构造区间及旧S04清理，详见operations/2026-10-27-oem-post-kernel-v4.md。E01/S02观察call4，E03/S04观察SID，S05真实驱动返回。无图不等于死锁。即时身份/备份/恢复、精确镜像与单次门禁通过后仅临时boot一次；75秒未确认返回即停止追加并恢复。R027和旧消费镜像不动。

# 当前：post-kernel-v4完整固件与离线资格完成（2026-10-27）

用户已确认early-v3四组完整字符串一致；旧单次consumed且Android恢复独立核验通过。本轮无设备命令。当前最大可操作嫌疑为Kernel查询返回后的构造未观测区间（HOB遍历、264字节代码缓存维护、guided-section注册），S04窗口清理是并列竞争解释。缺协议本身并非已证根因；详情和推翻条件见operations/2026-10-27-oem-post-kernel-v4.md。

新镜像out/oem-post-kernel-20261027/qualification1/image.img，SHA256 `233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7`；FD SHA256 `1dd0834df9348e3cb97667877cfd8ecece8d8e86024658262e18fdbbbcf8b9f3`。原厂PE、内存配置及同步修复保留。E01/S02改为call4（第五次包装服务），E03/S04改为SID，S05是真实驱动返回；最多五窗/40秒，未上机。

34项Python、check2 ASan/UBSan/真实Core/两处源码删除、binding1、全FD及Boot v3回读通过；最终机器码32处原运行时+23处同步/选择指令删除和一次GUID变异拒绝。Core同步函数及配置表函数与v3机器码完全相同；观察函数只在call选择立即数有一字节差异，另有协议GUID和session数据变化，不等于整份PE相同。

固件提交f82039e；构建是以7c97dc6为基线的工作树快照，不称提交后重编。固件两次GitHub推送分别连接重置/连接超时，设备仓a1c48f2推送同样连接443超时，均未确认远端发布。最终离线admission通过，新trial账本未消费。不得将本轮编出固件当作实机启动授权或故障修复证明；下次仍先满足发布、精确单次、即时设备/备份和当前录像/恢复门禁。R027和已消费旧镜像冻结，媒体仅本地，共享主线只读。当前无人工待办。

以下为历史记录，以本节为当前状态。

# early-v3 单次实测结束，Android已恢复（2026-10-27）

镜像3d263b531074c483fb96c60954ac52d139c7342b8e7bf561d31ea64f25af1628、trial 5052a582-523a-4a70-a7fd-2af21a95d496已执行一次并consumed。75秒未观察到合格fastboot返回，已停止追加。用户长按恢复后，独立核验Android完成/root/A槽/解锁及boot_a/vendor_boot_a摘要通过。不得原样重试；R027保持冻结。

已收到本地s1.jpg至s4.jpg；助手独立保存判读E01/C1/Q2、S02/C1/Q3/status0、E03/C3/Q6、S04/C3/Q7/status800000000000000e；前两图RVA3abc，后两图RVA616c，session b53a9560064a37d8。用户要求展示完整五行字符串，人工确认仍pending；未收到连续录像，不推断S05从未发生。

初步代码归因：Kernel LocateProtocol已返回EFI_NOT_FOUND，不是已证实的协议调用内部死锁。精确PE的616c非零分支到61ac→61c0→61f4，以Scheduler Interface HOB GUID 8ec2bd8d-56d7-49ef-8796-631778f8ebf8回退；620c读取HOB+24指针，构造器61b4仍返回0。因此不能把NOT_FOUND直接认定为致命错误。当前最大可操作调查方向是调度接口回退及后续使用，置信度有限；S04窗口清理、后续OEM执行及显示出口拒绝仍是竞争解释。先核对真实HOB产生/指针生命周期与下游调用，再设计新候选，不伪造协议成功或跳过错误。

四图支持本版已越过前两窗并到达Kernel查询返回，但S04画出不等于其等待/恢复完成，也不能从跨版本进展证明配置表修复解决旧根因。原始媒体仅本地D:/Code/PortingiOS/enuma/Media-enuma/OEM-early-v3-20261027-5052a582。证据reports/enuma-oem-early-trial-20261027.json、out/oem-early-20261027/media-review、out/device-tests/oem-5052a582-523a-4a70-a7fd-2af21a95d496。

以下为历史记录，以本节为当前状态。

## early-v3 本次启动准备（2026-10-27）

用户已明确允许启动early-v3，并确认在场、连续录像及人工恢复就绪。仅镜像3d263b531074c483fb96c60954ac52d139c7342b8e7bf561d31ea64f25af1628、trial 5052a582-523a-4a70-a7fd-2af21a95d496一次临时boot；尚未发图。固件7c97dc6已推送，设备仓本次记录提交发布后进入即时身份/备份门。无flash/erase/改槽，75秒未观察到合格返回则停止追加并人工恢复。

最大可操作嫌疑：追踪环境与OEM构造早期兼容性；配置表动态一致性缺陷已复现修复，但本次根因置信度低至中等。竞争解释依次为旧第二窗清理/恢复问题、后续OEM构造/依赖执行、显示出口因路由变化被拒绝；SID/MMU尚无直接现场证据。具体代码与路径见operations/2026-10-27-oem-post-s02-analysis.md及early-v3记录。

E01/S02观察call1入口/返回；E03/S04观察Kernel LocateProtocol入口/返回；S05是真实CoreStartImage返回。若前四窗正常，降低前段构造嫌疑；缺图不能区分执行未到达与取证拒绝。新版call0不绘图，E01不能证明旧版S02清理完成；修复与观测时序同时变化，单次进展也不能单独证实配置表缺陷为旧故障根因。下一步只按现场实际图像独立判读，不补猜。

媒体目录D:/Code/PortingiOS/enuma/Media-enuma/OEM-early-v3-20261027-5052a582；原始媒体仅本地。R027/旧候选冻结，旧progress-v2已消费且恢复。此节取代此前网络失败导致的准备停点；最终发布及即时门禁仍须真实通过。

# OEM early-v3 新候选已编出（2026-10-27）

已完成配置表生命周期修复、完整FD构建及qualification3离线资格。固件提交7c97dc6；构建为以3adfb77为基线的工作树快照，精确输入由source-manifest绑定，不称干净提交构建。报告见reports/enuma-oem-early-candidate.json，细节见operations/2026-10-27-oem-early-v3.md。

启动镜像：out/oem-early-20261027/qualification3/image.img；SHA256 `3d263b531074c483fb96c60954ac52d139c7342b8e7bf561d31ea64f25af1628`。FD SHA256 `361c67d72b5f34ed6b4e2d7364b8fc55ab155404e5d752d4b6344160d828a5bd`。修复在旧配置表释放及通知前同步私有SystemTable指针/数量/CRC；新窗口观察call1和首次Kernel协议查询，S05仍仅代表真实CoreStartImage返回。最多五个8秒窗口，范围不扩大。

32项Python测试、真实Core ASan/UBSan回归与两处同步删除负测通过；实际PE新增23处指令删除和一次GUID变异均被拒绝，原运行时检查及Boot v3封装回读通过。软件资格不证明实机根因已解决，也不代表GOP/BDS/XNU/桌面验收。

本轮未连接、查询或启动设备；最后独立核验状态为progress-v2人工恢复后的Android完成。旧progress-v2仍consumed，不重试；R027及旧OEM冻结，原始媒体只在本地。下一步如进入实测，重新核对当前身份/备份/录像/人工恢复及新候选单次门禁。本轮无人工待办。共享主线未改，未合并main；本地设备仓提交4ca8be4、固件7c97dc6；两仓向oem-progress-20261027推送均因github.com:443连接失败，未确认发布成功。暂不部署，待网络恢复后补推并重新核对资格。

以下为此前状态与其他依赖记录，新OEM当前状态以上文为准。

# OEM progress-v2 实测结果（2026-10-27）

一次临时启动已消费，75秒观察内未见合格fastboot返回，已停止追加启动。用户人工恢复Android后，独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a摘要均通过。当前设备恢复完成；不能原样重试本镜像。

候选SHA256：adbb2c41216bc0c934af4046fe8c0127ce40a6c22c12bfc3f2c7880eee80679f。源码设备仓61eacd1、固件3adfb77；首次连接失败的前检未启动，重新连接后仅一次实际boot。单次ledger保留consumed，R027及旧OEM候选冻结。

两张本地照片独立判读：E01/C0/Q0与S02/C0/Q1，均为返回RVA 0x3abc、session 0x1c2e8da897800e00；S02状态0（EFI_SUCCESS）。精确原厂PE在0x3ab8执行BLR x8，前序从表偏移0x40取函数，对应AllocatePool。0x3a8c前序不是调用，与照片B字形也不符。无符号，不能断言上层调用函数名称或分配用途。

主判断：首个AllocatePool已经成功返回，优先缩小S02取证清理至后续OEM执行之间的区间。S02可见发生在等待/恢复完成之前，因此清理/复位失败仍是第一组待排除项；其次是后续服务或未包装协议/MMIO执行，另有后段显示出口因路由变化被拒绝的可能。两张静态照片不能证明E03/S04/S05从未发生，不能判定SID死锁或完整驱动返回，更未验证GOP/BDS/XNU。此排序是下一步诊断优先级，不是故障概率结论。

下一软件方案：以独立有界探针观察后续选定服务调用入口/返回，并区分取证清理与OEM继续执行；不先套用MMU补丁。新镜像须重新构建/失败路径/机器码/单次绑定审核，不沿用本次ledger或在场状态。原始媒体仅本地，文字判读待用户核对。

证据：reports/enuma-oem-progress-trial-20261027.json；out/oem-progress-20261027/media-review/（转录、解码、精确PE RVA映射）；out/device-tests/oem-b78f01e4-35ff-4113-890d-251a1d51d106/（transport、超时快照、恢复核验）。媒体位于D:/Code/PortingiOS/enuma/Media-enuma/OEM-progress-v2-20261027-b78f01e4。只收到stage1.jpg和stage2.jpg，未收到连续录像。

以下内核输入及集成交接仍有效：

# 交接：从已验收真实输入继续 storage/PMGR 服务集成

2026-10-27。用户允许推送；本次progress-v2已消费且人工恢复，停止追加实机。R027冻结，旧OEM候选17d0169e6bd1继续保留。共享D:/Code/PortingiOS/enuma/UniXNU-enuma只读。

1. 主开发树D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display保留完整离线历史。最小CI树D:/Code/PortingiOS/enuma/worktrees/enuma-xnu-input-ci，分支ci/enuma-driver-inputs-20261027已推送，最新文档e81f73c；远端main未变。
2. 最终平台运行40478893674成功，代码cdfb7ae；原始包在CI树out/ci-runs/40478893674/enuma-macos-platform-40478893674，验收副本在同级imported。2259文件/2记录绑定通过，manifest和内核摘要见reports/enuma-driver-input-ci.json。不要重用上传缺失的40477385983，也不要覆盖旧失败证据。
3. 已取得真实IOPMGR/IOService及生成头/命令；下一步仍须IOKit/storage接口和同donor私有ABI。IOKitUser下同名头不能替代。随后接入现有RootRead/RamDisk的provider、start/stop、注册及归档链接，验证失败生命周期。
4. 新平台内核be17abfc…未做donor预链接或设备启动，旧e879b2f0实验内核及静态PMGR结果不自动转移。没有用户态或桌面运行证据。
5. 32项宿主测试通过，最终真实包导入通过；详细失败/修复链见operations/2026-10-27-driver-input-import-ci.md及CI分支同名文档。按官网具体规则继续；内存/verified/分区门禁不变。

2026-10-27代码归因更新：用户已确认E01/S02判读。宿主ASan/UBSan复现私有SystemTable配置表指针/数量陈旧缺陷；这是当前最强代码缺陷证据，尚未证实为本次根因。已核对首分配后的构造链与实际Core返回/清理指令，下一验证先隔离追踪器并覆盖call1/2及Kernel协议，暂不跳到SID/MMU补丁。详见operations/2026-10-27-oem-post-s02-analysis.md。新候选未生成，本轮无追加实机；7d74ce9文字取证已推送oem-progress-20261027。
