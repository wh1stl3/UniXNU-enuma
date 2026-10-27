# 当前：far-chain-v7镜像与离线资格完成，未上机（2026-10-28）

用户要求“不是更细，而是更远”，本轮继续到可上机镜像。v7取消全部OEM内部前置/返回绘制，只在RAM锁存粗粒度阶段和真实状态；目标驱动point13保存真实日志后继续，不再提前2秒复位。真实CoreDispatcher返回后才查询GOP/Mode/ConOut存在性并输出一次汇总页（最多8秒），再沿既有7秒恢复出口复位。本版覆盖目标为OEM真实返回及后续DXE分派完成，仍在BDS前停止；不是正常BDS/XNU启动包。

- 镜像：out/oem-far-chain-20261027/qualification2/image.img，3153920字节，SHA256 c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d。
- FD：out/oem-far-chain-20261027/build2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd，SHA256 e16748c382248cdfddd4514ea6e274032ec3c987fc96bcd11ad01a3117610a2f。
- 资格：out/oem-far-chain-20261027/qualification2/qualification.json，SHA256 a1cdb2c1fbb1e4c7aacd0f6862db68c45275297f643e0241d092c7a622612823；software_ready=true、hardware_executed=false。
- scope oem-far-chain-v7；trial 61c29945-1399-49eb-8133-d11d465bb6c4；session 9369882057737620086；selected_call=0仅配置占位，实际选择是ram-only-until-dxe-complete；未claim、未消费。
- 固件源码提交1f05eef62b62fc6f57b805e1cb346e3643457db7。build2为d393211基线加本轮源码的工作树快照，source-manifest保留；不是提交后重编。固件已非force发布并精确核对远端oem-progress-20261027，设备仓提交/发布以git log及out/oem-far-chain-20261027/device-publication.json为准。

ASan/UBSan状态机、真实失败状态、无前段UI、缺失里程碑不补写、末端TPL/sink失败、point13继续和completion导出→7秒→复位、实际页面格式检查通过；精确OEM PE路径/真实ARM64 ChipInfo ABI及重定位/错PE拒绝/板级绑定通过。44项Python（含模拟传输）通过；链接机器码30处运行路径+108处后移路径删除与3处GUID变异全部拒绝；完整FD审计、Boot v3封包/解包回读和默认离线2456项绑定通过。本轮没有设备命令。失败build1（补丁CRLF）/qualification1及check1..4保留，成功为build2/check5/qualification2，不覆盖旧记录。

最大可操作嫌疑仍是v6 E01窗口收尾/转发对后续执行的影响（诊断优先级中等，唯一根因置信低），v7直接移除该前段干扰并允许后续DXE继续。竞争解释为ChipInfo查询/接口方法及条件事件、OEM后段或后续其他DXE不返回，以及末端显示路线变化导致出口拒绝。v7取得S05汇总时才能确认本次真实Core和分派返回；全无页不能区分上述解释，无独立看门狗/持久崩溃日志。S行是原始Core状态，C是里程碑位图而非call号。GOP/Mode/ConOut位只证明存在性，不能当生产显示、控制台或实体输入通过。

下一步：以新v7单次实测取得远端汇总；Core失败按真实状态与阶段修复，Core成功无GOP则查协议发布/依赖，有GOP无可用控制台则检查模式几何/显示所有权及控制台连接。继续到BDS之前须核对CoreAllEfiServicesAvailable/gBds及实际PlatformBootManager、配置/存储发现，不能只删除诊断复位就宣称完整启动。详见[far-chain-v7实现、位图与下一卡点](operations/2026-10-27-oem-far-chain-v7.md)。

实机条件尚未准备：本轮仅离线，不沿用v6拍摄/在场状态；未来启动前须当前文档发布、精确新单次、即时enuma身份/原备份/恢复核验与本次拍摄/人在场恢复。75秒无合格返回停止追加，先恢复核验，不自动重试。设备最后已知为v6后23:06独立Android完成/root/A槽/解锁与原双分区摘要通过，当前在线状态未知。v6 consumed且单页E01/C6/Qc/RVA3608人工确认，不复活。共享主线只读，R027及历史镜像/资格冻结；无flash/erase/改槽、内存base/size或verified变更。媒体/out/二进制/备份/设备标识只留本地。
