# far-event-v8：去掉恢复TPL后的环尾竞态，继续远端DXE路径

v7已consumed，用户报告FASTBOOT到Mi标之间没有日志、设备自行回Android；独立身份/完成/root/A槽/解锁及原分区/备份核验通过。没有本地原视频独立判读，不能断言Core/DXE返回或GOP存在。

## 最大可操作嫌疑与复现

精确v7追踪器EnumaServiceBegin/End先在TPL_HIGH_LEVEL追加事件，RestoreTPL之后调用OemProgressObserve。Observe再次RaiseTPL复制8224字节环形日志，并把当时最后一条与传入Call/Returned比较，不一致调用OemProgressFail→OemCaptureTerminal→ResetCold。固定Mu源码Event/Tpl.c的CoreRestoreTpl在返回前分派待处理通知，所以恢复TPL不是“无其他代码运行”的间隙；嵌套回调使用OEM保存的私有BootServices即可能追加另一条追踪事件。

本轮以冻结v7 build2/source头文件复现：主查询入口记录后，在RestoreTPL按TPL_CALLBACK执行一次嵌套AllocatePool。嵌套调用正常记录和返回，外层观察器读到嵌套事件后主动终止，原始ChipInfo查询一次也没有转发。ASan/UBSan复现记录race2/result.json；这证明追踪器存在可触发缺陷，不证明v7实机恰好出现此嵌套通知，也不把本机根因写成已确定。

## 实现与边界

新scope oem-far-event-v8，FAR_CHAIN=1、RAM_EVENT=1。EnumaServiceRecord在原始TPL_HIGH_LEVEL锁内完成事件后，将同一事件同步交给OemProgressRecord；仅有界RAM字段锁存和最多两个16字节GUID比较，无分配、协议、等待、打印或设备访问。观察器不保存事件指针，不扫描整环，不二次Raise/RestoreTPL；BeforeForward/AfterForward在此scope保持NULL。原始服务仍在调用者TPL执行，参数/状态/序号保持真实，注册/主查询/SID里程碑不补写。

保留v7完整后段路径：实际CoreStartImage状态只保存，目标point13不提前复位，继续后续DXE，CoreDispatcher返回后一次8秒汇总及原7秒恢复出口。本轮仍不进BDS，不扩大读写地址/预算，不改内存base/size、verified或分区。旧scope使用原接口，旧镜像/资格冻结；R027、共享主线只读。

## 验证与区分力

真实通知TPL的三组验证：冻结v7复现主动终止；新v8继续原始查询并正确锁存阶段；删除新钩子的变异在阶段断言失败。另覆盖日志超过128项后的里程碑保留、真实失败状态、缺失阶段不补写、末端sink/TPL拒绝、point13继续和completion顺序。check1因新观察器缺SID局部声明失败，补齐后重新跑check2；按真实通知TPL调整夹具后最终采用check3和race2，失败输出保留。板级/精确重定位PE、错PE拒绝、ARM64 ChipInfo ABI通过；44项Python通过。最终FD/机器码负测/封包回读完成后追加摘要。

若新图出现汇总，支持该笔已跨过真实Core返回及后续DXE，但不证明v7失败唯一源于此次修复。若仍无页，剩余最大竞争解释是OEM/后续DXE异常提前复位、真实返回身份门未满足、末端GOP读取或继承显示路由/CPU窗口拒绝；无独立看门狗或持久日志，不根据无页认定死锁。GOP/Mode/ConOut仍是存在性而非生产显示验收。未来候选前须本次拍摄/人在场恢复、即时身份备份及当前发布门禁；本轮仅离线构建，不复用v7就绪。

## 最终产物与资格（2026-10-28）

镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，3153920字节；FD ade5dfcc4f3d383372f6f9a0331ab685bd6b8ceb0c5d8ac3ee0f4635b5d17936；资格b42faaa664c7613f147cf16dabec5b914550c64a013661b358039c992a66e8ff。精确路径为out/oem-far-event-20261028/qualification1/image.img及qualification.json，完整FD在build1/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd。固件49affe73f48f5b22dd1256efa25dd5576c438daa，基线1f05eef工作树快照，未在提交后重编。

最终check3/race2/binding1/path1通过；44 Python、30+152条删除及3 GUID变异拒绝、2459绑定、完整FD/Boot v3解包回读通过。关键链接路径EnumaServiceBegin:1375c/End:1381c调用EnumaServiceRecord，记录完成后1398c读取Recorded、13994取同一事件指针、139b8尾跳回调；1376c/13834才恢复TPL。CoreStartImage中ccc4把正确OemProgressRecord地址安装到Recorded；没有OemProgressObserve/Before/After符号。实际Core返回锁存不变，3c38末端导出→3c44七秒→3c48 ResetCold出口保持。编译后复核仅覆盖选定序列，不称全程序或硬件证明。

trial a35583f7-e92d-4999-96d2-116793825026，session 4736432023589023138，未claim/未上机；软件就绪不替代当前拍摄与即时设备/恢复条件。失败check1、初期复现编译缺返回值等输出保留，冻结R027/v6/v7产物摘要复核不变。总报告reports/enuma-oem-far-event-v8-candidate.json，默认离线入口见HANDOFF。

## v8本次单次启动准备

2026-10-28 00:47 v8本次单次准备：用户明确“v8上机，正在拍摄，我在场可以恢复”，当前拍摄/在场条件独立记录，不复用v7。即时只读enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，trial a35583f7-e92d-4999-96d2-116793825026，未claim/发送。当前准备提交发布与远端核对后，由原runner重复即时门禁，仅一次临时boot；75秒无合格返回停止追加、先恢复，不flash/erase/改槽。共享主线只读、R027冻结。证据out/oem-far-event-live-20261028；媒体Media-enuma/OEM-far-event-v8-20261028-a35583f7本地保留。v8仅修复已复现的通知竞态，不预写OEM/Core/DXE/GOP/BDS成功；无页仍有异常、返回门、末端显示拒绝等竞争解释。

## 2026-10-28 v8单次结果及判断更新

用户明确“v8上机，正在拍摄，我在场可以恢复”。准备提交6c3d8de、固件49affe7发布及远端精确核验后，执行器再次通过即时enuma/Android/root/A槽/解锁与原双分区/备份门禁，仅一次临时fastboot boot。trial a35583f7-e92d-4999-96d2-116793825026已claim/consumed，不重试；镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，qualification1 b42faaa664c7613f147cf16dabec5b914550c64a013661b358039c992a66e8ff原字节保持。

执行器观察Android完成并复核分区。用户确认“设备自行返回 从fastboot到Mi标之间都没有”；独立00:51只读核验enuma、boot_completed=1、root、A槽、解锁及设备/本地boot_a/vendor_boot_a原摘要全部通过。无追加启动/分区操作/恢复欠项，没有设备硬停。当前媒体目录D:/Code/PortingiOS/enuma/Media-enuma/OEM-far-event-v8-20261028-a35583f7为空，尚未独立逐帧判读；“无页”依据用户现场陈述，不生成预期S05、不冒充独立视频结论。

v8修复了宿主已复现的RestoreTPL后环尾竞态，且实际链接/资格绑定通过，但本次仍未观察到汇总页。因此不能继续把该竞态当作无页的充分/唯一解释，也不能认定修复未执行；本机实际Core/DXE/GOP阶段仍未知。v7/v8相同外部现象不足以证明内部路径相同，Android返回只证明恢复。

下一最大可操作方向转向末端可观测性与提前复位的分离（诊断优先级中等，唯一根因置信低）：EnumaOemFarDispatchComplete在Owner或真实Core返回位不满足时直接不绘制，completion仍沿7秒恢复；OemProgressEmit拒绝非TPL_APPLICATION；OemBoardSink还要求原继承路由、1600×2560几何、Splash范围、CPU策略和窗口恢复准入，任何拒绝都可能在显示前ResetCold。OEM/后续DXE异常入口同样直接ResetCold，仍是竞争解释。优先设计独立于晚期继承显示准入的阶段/拒绝出口，保留远端路径；不再仅凭无页细化ChipInfo，不能通过放宽像素边界、伪造EFI_SUCCESS或删除全部恢复出口来制造进度。新方案须实际代码/失败路径/机器码/完整构建及新单次资格，本图不重试。

证据：reports/enuma-oem-far-event-v8-trial-20261028.json，out/device-tests/oem-a35583f7-e92d-4999-96d2-116793825026，out/oem-far-event-live-20261028（authorization、publication-verified、preflight、postcheck、human-return-confirmation）。原runner pending快照保留，由新人工确认独立闭合。生产GOP/ConOut/BDS/实体输入/XNU未验收，R027/v6/v7/v8镜像资格冻结，共享主线只读；无内存base/size、verified、flash/erase/改槽变化。媒体/out/二进制/备份/设备标识不入Git或云端。当前无恢复/字符串核对欠项，结果发布以git log及result-publication.json为准。
