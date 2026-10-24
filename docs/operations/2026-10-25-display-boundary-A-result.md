# A/detail15单笔实机结果（2026-10-25，D-168）

结论：精确A镜像本次返回Android，恢复和分区摘要核验通过；R-016已消耗。不追加B，不重复A。本次未触发75秒超时或人工恢复请求。固件aa9ec66、实机前发布b1cf33c，镜像SHA256 29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4。

## 精确主机记录

| 事件 | 主机记录 |
| --- | --- |
| 发出fastboot boot | 2026-10-24T18:11:21.751570+00:00（北京时间02:11:21.751570） |
| 命令成功返回 | 相对发出0.390秒 |
| 首次观察fastboot断开 | 0.953秒 |
| 首次观察ADB device | 16.187秒 |
| Android完成并结束root/分区核验 | 31.312秒 |

相对时间采用本机monotonic。数字表示轮询首次观测/检查结束时间，不是硬件内部事件的毫秒精度测量。本次没有观察到返回fastboot，runner没有执行后续fastboot reboot；直接观察到Android。issued_monotonic=104832.453。证据out\device-tests\20261025T021107-dxe-driver-return/result.json及camera runner.log。

## 恢复和相机

runner确认Android完成/root/分区摘要不变；随后独立执行reconcile_enuma_recovery.py再次确认enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a设备/备份摘要匹配。证据out\device-tests\20261025T021235-recovery-reconciliation.json，不覆盖原试验result.json。

相机目录out\camera-capture\20261025T021104-display-boundary-A：保留原始MJPG录像415帧，逐帧解码计数415/415，50份每秒原图和50份顺时针90度图；无采集错误。已查看before、frame-031和frame-049旋转图，分别为Android桌面、小米/Android启动画面、恢复后的Android桌面。录像SHA256 89872124f096d1e8646dcd3784d9a5f6a7170e54b1a5696296999dcc620f3cd6。

画面中的小米启动标志属于Android回归证据，不能当原厂DisplayDxe或UEFI画面成功。抽样截图不排除未抽到的瞬态固件内容；编码视频fps头不作墙钟，时序取observation.json记录。没有对不可见的物理按键动作作独立断言。

## 判断与下一步

已确认：这份A本次可返回并恢复核验通过，且fastboot曾被观察到断开，避免了残留枚举误判。设计和打包Core审计表明A的目标门在CoreStartImage前；16.187秒回ADB与2秒门相容，因此**工作判断更支持已到达原厂启动调用前**。

仍非唯一归因：只有单笔样本，没有本轮同源目标/兜底门独立校准标记；不能排除7秒完成兜底加不同Android开销、其他复位路径等原因。也不能据此定位R-014两次超时位于DisplayDxe内部，历史公共路径亦有偶发超时。

下一步有区分力的是B/detail13（其余配置及OEM PE保持同源）及必要的状态/模式审计，用于观察CoreStartImage返回。若继续可先离线构建资格，但R-016仅A一次，不能从本结果自动扩张实机授权；不再重复A。入口FDT、Kernel Protocol/调度HOB、模式设置和可见GOP仍需闭合。不补stub、不直接改线程/内存/DTB，不复活旧像素授权。

机器汇总：reports/enuma-display-boundary-A-result.json；单笔账本reports/enuma-display-boundary-device.json；归档资格reports/enuma-display-boundary-qualification.json。没有分区写入、改槽、新映射、verified或XNU启动验收。
