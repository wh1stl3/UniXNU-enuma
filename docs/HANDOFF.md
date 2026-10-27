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
