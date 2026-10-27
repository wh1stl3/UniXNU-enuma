# 当前：v8本次拍摄/在场恢复已确认，单次准备

2026-10-28 00:47 v8本次单次准备：用户明确“v8上机，正在拍摄，我在场可以恢复”，当前拍摄/在场条件独立记录，不复用v7。即时只读enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，trial a35583f7-e92d-4999-96d2-116793825026，未claim/发送。当前准备提交发布与远端核对后，由原runner重复即时门禁，仅一次临时boot；75秒无合格返回停止追加、先恢复，不flash/erase/改槽。共享主线只读、R027冻结。证据out/oem-far-event-live-20261028；媒体Media-enuma/OEM-far-event-v8-20261028-a35583f7本地保留。v8仅修复已复现的通知竞态，不预写OEM/Core/DXE/GOP/BDS成功；无页仍有异常、返回门、末端显示拒绝等竞争解释。

# 当前：far-event-v8镜像及离线资格完成，未上机（2026-10-28）

用户要求继续直至编出镜像。本轮已完成v8，scope oem-far-event-v8；不增加早期绘制，保留OEM期间RAM-only、真实Core返回后继续DXE、整轮分派结束才一次汇总及BDS前恢复出口。

本轮最大可操作嫌疑有了具体代码复现：v7的Begin/End在RestoreTPL之后再读取环尾，待处理通知可嵌套追加追踪事件，导致外层OemProgressObserve误判Call/Returned并主动ResetCold。固定Mu CoreRestoreTpl确会在返回前运行通知；冻结v7头文件/真实TPL_CALLBACK夹具复现“原始查询尚未转发即主动终止”。这是已复现的追踪缺陷，仍未证明是v7实机唯一根因。

v8在既有TPL_HIGH_LEVEL记录临界区，直接把刚完成的事件交给有界RAM观察器，不复制/验证整环、不再次Raise/RestoreTPL、不持有事件指针，无分配/协议/等待/设备访问。原始服务参数、调用者TPL、真实状态和序号保持；BeforeForward/AfterForward在新scope为空。目标point13仍保存真实日志后继续后续DXE，不合成驱动成功。下一步按真实Core状态→GOP/Mode/显示所有权→控制台连接→BDS/存储配置→DarwinBoot/EBS/XNU分层推进。

- 镜像：out/oem-far-event-20261028/qualification1/image.img，3153920字节；SHA256 197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29。
- FD：out/oem-far-event-20261028/build1/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd；SHA256 ade5dfcc4f3d383372f6f9a0331ab685bd6b8ceb0c5d8ac3ee0f4635b5d17936。
- 资格：out/oem-far-event-20261028/qualification1/qualification.json；SHA256 b42faaa664c7613f147cf16dabec5b914550c64a013661b358039c992a66e8ff。
- trial a35583f7-e92d-4999-96d2-116793825026；session 4736432023589023138；selected_call=0为配置占位，实际RAM-only直到DXE完成。未claim/未消费、hardware_executed=false。
- 固件源码49affe73f48f5b22dd1256efa25dd5576c438daa；build1是1f05eef基线加本轮代码的工作树快照，source-manifest保留，不称提交后重编。固件已正常发布到显式GitHub URL/oem-progress-20261027；设备仓及远端精确核验以git log、out/oem-far-event-20261028/publication.json为准。

验证：check3为最终ASan/UBSan真实状态、ring覆盖、无早期UI、末端TPL/sink拒绝、point13继续/completion顺序及真实Core配置表扩容/同步负测；race2为冻结v7复现、新v8通过、删除Recorded钩子拒绝。binding1精确PE重定位/错PE/ARM64板级，path1真实ChipInfo ABI与精确PE路径通过；44项Python通过。机器码30处运行路径+152处事件/后移路径删除、3处GUID变异全部拒绝，包含在RestoreTPL之前调用记录、同一事件指针/钩子地址、无旧环尾观察器、真实状态和末端恢复。完整FD OEM审计、Boot v3封包/解包回读及2459来源绑定通过。check1缺SID声明失败保留；check2后将夹具改为真实通知TPL，最终采用check3/race2。无设备命令，R027/v6/v7冻结镜像和资格摘要不变。

若v8有汇总，仅能证明该笔真实Core与本次分派返回，GOP/Mode/ConOut位仅存在性；不能回推v7根因或生产显示/BDS通过。若仍无页，OEM/后续DXE异常提前复位、返回身份门不满足、末端GOP访问或继承路由/CPU窗口拒绝仍是竞争解释；无独立看门狗和持久日志，不判ChipInfo/SID死锁。详见[实际代码与修复依据](operations/2026-10-28-oem-far-event-v8.md)。

v7已单次消费，用户报告无页且自行返回；00:16独立enuma Android完成/root/A槽/解锁与原分区/备份摘要核验通过。其原runner pending快照、原资格/镜像不回写，人工确认另存；原视频尚未独立判读。当前没有恢复或字符串核对欠项，本次即时身份与恢复前检已通过，当前拍摄/在场条件已重新确认，启动前仍须当前发布、精确单次、即时身份/备份/恢复及当次拍摄/在场条件，75秒无合格返回先恢复、不自动重试。共享主线只读，R027冻结，无flash/erase/改槽、内存base/size或verified变更；out/原始媒体/二进制/备份/设备标识只留本地。
