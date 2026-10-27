# OEM registration-v5：call4 之后的真实配置表安装

2026-10-27，本轮离线推进。v4手机重试完整字符串已人工确认，call4/Q8→Q9、RVA3abc、status0；现场仅两组，设备未按键自行回Android且独立核验通过。旧图和两个consumed账本保留。

## 最大嫌疑、实际代码与推翻条件

最大可操作嫌疑是call4后的guided-section配置注册区间，置信中等（对唯一故障指令置信低）；S02取证事务的恢复/读回/退出为竞争解释。原厂PE SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425：0x3abc成功后从栈读分配指针，0x3b94检查非NULL，0x3ba8尾调0x411c复制16字节；0x5ca8取复制结果，0x5cbc读gBS，0x5cc0读取BootServices+192即InstallConfigurationTable，0x5cc4 BLR，真实返回地址0x5cc8，随后构造函数返回0。调用后的状态被OEM忽略，不能把配置表安装失败等同原厂构造函数返回失败。

前置Kernel/HOB/cache路径在本次已达call4的运行中经过；这不反推early-v3窗口清理通过。没有SID或驱动返回照片不等于确定挂在最后可见事件。16字节复制的源为OEM传入的GUID；尚未导出运行时分配地址/实际表内容，不能凭EFI_SUCCESS排除指针内容问题。私有SystemTable动态同步保留，配置表扩容时必须先同步再释放旧表、再通知；v5继续运行真实Core扩容/通知测试和删除负测。

如果v5出现安装前页，则本次已通过未绘制的call4及复制，降低这些路径的嫌疑；出现安装返回页，则缩小到其后的构造/主入口、SID和输出可达性。仅安装前页时仍需区分真实服务内部、入口窗口清理和后续输出拒绝；全无输出仍无法区分未到目标和出口失败。没有独立硬件看门狗或持久异常日志。

## 实现与范围

新scope oem-registration-v5，selected_call=5；只有本scope替换私有BootServices.InstallConfigurationTable。包装器按精确原厂调用返回地址0x5cc8过滤，其他调用原样直接转发且不改变旧三个服务的计数。目标调用保存GUID，调用前记录、转发原始Guid/Table指针、记录真实状态；TPL仅包围日志写入，原始服务在原TPL执行，转发不因失败而重试。原厂二进制和配置表同步实现不改。

call0..4不画窗口。E01/S02为目标安装前/真实返回，严格要求call5和RVA5cc8；E03/S04为首次SID LocateProtocol前后；S05为真实CoreStartImage返回。保持ROI(64,96)320×160、每窗8秒、最多五窗40秒，继承路由每次重验；输出拒绝终止，不伪造状态，不扩张MMIO、内存base/size或verified。

真实控制器已补齐Android返回终点：先观察fastboot断开，再接受绑定enuma的Android完成；随后核验root/原槽/解锁/原分区摘要。设备自行返回与人工按键仍需现场事实，不能仅据ADB出现推断按键行为。模拟传输检查直接Android返回、错误身份、fastboot残留拒绝，均确保只boot一次且无flash/erase/改槽。

本轮复查仓内官网开发指南/具体方法与固定源码。官网bring-up/log-capture在线重读被403拒绝，未声称已取得新网页内容；按已保存流程继续真实代码→失败路径→完整FD→实际机器码→Boot v3打包，宿主结果不升级为实机结论。R027冻结，共享主线只读，原始媒体仅本地。

## 构建与资格

输出out/oem-registration-20261027。构建入口firmware/Resources/Scripts/build_enuma_development.py，独立工作树快照，固定依赖和原厂oem-control。完整构建及最终摘要/机器码检查结果在完成后追加。本轮没有设备命令。


# 当前：registration-v5 新固件与离线资格完成（2026-10-27）

本轮离线，未查询/操作设备。v4两组完整字符串已确认，仅观察到call4成功返回；用户确认设备无按键自行回Android，恢复独立核验通过。v4原始trial及手机retry均consumed，R027和旧候选冻结，共享主线只读。

最大可操作嫌疑为call4之后的guided-section注册区间：16字节复制→0x5cc4 InstallConfigurationTable→后续构造/主入口；对该区间置信中等，对唯一故障指令置信低，S02窗口清理仍为竞争解释。具体指令、边界、推翻条件及新候选观测解释见[registration-v5分析](operations/2026-10-27-oem-registration-v5.md)。缺少SID/返回画面不证明最后可见位置死锁。

新镜像out/oem-registration-20261027/qualification3/image.img，3153920字节，SHA256 `f9bd10078db5b049e7ad0cd050300c872cdcd1d0d975b6ed3065e4b03dac650d`。完整FD：out/oem-registration-20261027/build1/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd，SHA256 `f83b1869f65377ec2b4af4bdc69f1f64f0fcf41a3a296c6ea795a76d3b7fe6d5`。

新scope oem-registration-v5，trial 4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e，尚未claim或上机。只在此scope包装原厂返回地址0x5cc8的InstallConfigurationTable，其他配置表调用原样转发、不占追踪序号。call0..4不画窗；E01/S02=call5配置安装前/真实返回，E03/S04=SID前/后，S05=真实CoreStartImage返回。原厂DisplayDxe不改，私有SystemTable同步修复保留；ROI(64,96)320×160/每窗8秒/最多五窗40秒保持。

完整FD、原厂模块审计、Boot v3打包/解包回读通过。31项WSL Python、check3 ASan/UBSan与真实Core扩容/通知及两处删除负测、binding1精确PE重定位/错PE拒绝和AArch64板级对象通过；最终机器码32处原运行路径+52处同步/选择/注册删除负测及一处GUID变异均拒绝。qualification1保留其旧分支布局检查失败，qualification2按实际新增指令审查后通过，未为满足检查重写FD。

执行器已修复只等fastboot：观察断开后也接受绑定enuma Android完成，并完整核验root/槽/解锁/双分区摘要；直接返回、错误身份、fastboot残留模拟验证均只boot一次且无分区操作。ADB终点不推断用户是否按键，人工恢复事实继续按现场反馈记录。

固件提交fd94b26；构建是以f82039e为基线的工作树快照，保留manifest，不称提交后重编。脱敏报告reports/enuma-oem-registration-candidate.json。尚未确认本轮远端发布；最后设备状态沿上一笔Android恢复核验，本轮没有重新观测。下一实测须完成当前文档发布及即时身份/备份、当次手机拍摄与人工恢复条件；本轮任务到编出新固件，不追加实机。原始媒体仅本地，无新内存base/size、verified或分区范围变更。

最终资格为qualification3：仅清理宿主测试文件尾部空行后重新绑定，FD/image字节与qualification2完全相同；WSL 31项重验通过。固件推送无进展后有界中止，远端发布尚未确认；没有设备动作。


## 2026-10-27 registration-v5完整文档交接

用户因会话变慢要求全部文档落地、本地提交和新prompt。本轮仅文档与只读产物核验：image/FD/qualification SHA256匹配、v5账本不存在；证据out/oem-registration-20261027/handoff-audit.json。源码fd94b26、设备仓a68983a/0dd5db3已提交；当前文档、README/索引、旧prompt替代标记、审查及人工事项和最新授权同步完成，新prompt为docs/2026-10-27-oem-registration-v5-handoff-prompt.md。未上机、未重构建、未重试消费候选、未改共享主线，远端发布仍未确认。交接提交号见后续git log与回复，不写自引用。


## 2026-10-27 21:55 接续 registration-v5：现成资格有效，发布连接失败

从设备仓9f98d3e、固件fd94b26干净状态接续，完整读取prompt及适用规则。默认离线runner通过，2446项源绑定有效；image/FD/qualification摘要与交接相同，v5账本不存在。只读核验共享树R027冻结image/qualification摘要通过。未改源码、重构建、回写历史产物或查询设备；当前设备状态未知，当前手机拍摄/人在场恢复未确认。

有界查询两个GitHub分支失败；显式固件URL向oem-progress-20261027非force补推亦因443连接失败，未向本地origin/main推送，未继续设备仓发布。网络恢复后先固件后设备仓并核验，之后重新协调当次现场条件，单次runner执行即时身份/备份/恢复门禁。当前准备条件未齐，不称设备硬停。源码/资格/试验范围不变；不复活v4或R027。证据out/oem-registration-takeover-20261027/takeover-audit.json、remote-before.json、firmware-publication.json。STATUS/HANDOFF、审查与人工事项已同步；本轮本地文档提交号见git log。


## 2026-10-27 22:01 v5本次拍照就绪与即时前检

用户“随时准备拍照 可以开始了”放行本次registration-v5精确镜像一次临时启动，沿已有在场长按恢复安排，本次就绪独立记录。网络恢复，固件fd94b26已向显式GitHub URL/oem-progress-20261027正常推送；设备仓本准备提交发布并核验远端后才发图。只读前检确认enuma/Android完成/root/A槽/解锁及原双分区和本地备份摘要通过。trial仍4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e、镜像f9bd10078db5b049e7ad0cd050300c872cdcd1d0d975b6ed3065e4b03dac650d，未claim/启动，runner仍即时复核且只boot一次。证据out/oem-registration-live-20261027/authorization.json、preflight.json、firmware-push.json。R027冻结、共享主线只读，不flash/erase/改槽；75秒无返回先恢复并记录，媒体先独立判读再人工核对。
