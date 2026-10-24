# enuma交接：D-168，A已执行且返回，禁止重跑

设备仓D:/Code/UniXNU-enuma；firmware固定aa9ec66，独立固件检出/参考仓不清理。目标iPadOS17.7.11/21H461、iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。

先读AGENTS、STATUS、HANDOFF、DECISIONS D-166/D-167/D-168、NEED-REVIEW R-016，以及docs/operations/2026-10-25-display-boundary-A-result.md。当前记录取代旧“待执行A”阶段，不重复实机。

用户已批准上机，最小范围R-016仅A/detail15一次。镜像29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4，于02:11已执行，16.187秒观察ADB，31.312秒结束Android/root/分区核验，之后独立确认A槽/解锁/备份一致。无超时或人工恢复请求。R-016 consumed，本轮未执行B。

A具正确DisplayDxe GUID，point15/2秒、fallback7、without-ufs、query0/step0/value-off；打包Core在CoreStartImage前执行门，归档out/display-entry-boundary/pre-entry-aa9ec66。原厂32个PE/DEPEX不变，仅省略UFS。实机前工具/文档发布b1cf33c。

结论：本次可返回与恢复检查通过；时序支持到达启动边界，但单笔不唯一证明门命中，更不证明PE入口/状态/SetMode/GOP。小米/Android标志只是恢复画面。不要将A通过升级为R-014挂点已定位。

若继续，先离线构建同源B/detail13并完成资格；不从已消耗的A批准自动推出B执行授权。真实入口FDT、Kernel Protocol/scheduler HOB及模式设置仍未知。已审计发现：DisplayDxe确实消费线程/锁和HOB，缺失时可返回0却不建线程；本机ABL查splash_region，保存DTB只有cont_splash_region。两份专项ABI/交接契约保留证据层级，不直接补stub、关线程或改内存/DTB。

主机runner记录UTC/monotonic并要求fastboot先断开再重连；capture_display_boundary_trial.py默认仅相机，--execute受一次性账本锁定A，不可删除账本重试。相机415帧解码通过，50对原图和顺时针90度图在out/camera-capture/20261025T021104-display-boundary-A；时序取显式时间戳，不取视频fps或目录名。

结果机器证据reports/enuma-display-boundary-A-result.json、enuma-display-boundary-device.json和enuma-recovery-reconciliation.json。原图/录像/OEM二进制/标识仅out/，不提交。所有未来门禁遵守AGENTS；参考仓只读，失败停止追加、先恢复并当轮更新文档。
