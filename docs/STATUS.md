# 当前状态：D-167 / R-016批准A单笔上机，实机前门禁准备

用户于本轮明确“批准上机”。最小执行范围为D-166已归档A/detail15镜像29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4的一次临时fastboot boot；不包含B/detail13、重复同一镜像、节点修补、线程开关/内存映射变化、像素/背光写入或分区操作。原厂前序驱动可能写硬件，不能称整镜像只读。

## 已完成的即时检查

- out\device-tests\20261025T020804-recovery-reconciliation.json：enuma唯一在线，Android完成/root/A槽/解锁；boot_a/vendor_boot_a设备与匹配备份摘要一致。本轮尚未发出新临时启动。
- A不可变归档全部摘要复核通过；固件固定aa9ec66，原源码/候选未改。D-166构建、FD和Core机器码证据保持，详见reports/enuma-display-boundary-qualification.json。
- 相机0/DSHOW可用，已观察out/camera-capture/20261025T020928-display-boundary-A/before-rotated.jpg中的Android桌面；原图保留。执行将连续录像、逐帧记录时间、每秒保存原图及顺时针90度图。按键画面不确定时不推断。
- 主机runner新增issued_at_utc/monotonic及boot命令返回时间；fastboot返回必须先观察断开再重连，残留枚举不再触发“返回”判断。四条无设备状态轨迹测试通过。
- 新capture_display_boundary_trial.py默认仅相机检查；--execute仅接受此精确A摘要，核对已发布源码/归档，建立一次性账本后调用现有身份/备份守卫。图像采集失败不杀恢复观察器，不发额外启动。

## 单笔执行及停止规则

本轮只A。启动前发布本页、HANDOFF、审批、人工与来源记录；核对仓库干净和origin/main一致后执行。runner再次做即时身份/备份/fastboot身份核验。不改槽、不flash/erase，若自动回fastboot则核验身份后正常reboot Android并校验分区。

观察期限维持runner既有75秒窗口（在fastboot boot命令成功返回后开始），实际全程以issued_monotonic及命令返回偏移记录。若超时停止追加，优先既有恢复；必要时请求在场长按并继续录像。失败结果不覆盖，恢复后独立核验并当轮更新全部文档；不原样重试，不自动发B。

A即使自动返回，也只记录返回和边界支持程度；2秒目标门/7秒fallback的主机时间叠加bootloader与Android开销，不能仅凭一笔耗时宣布命中。无完整早期日志时按已允许的有界临时探针规则判读，不把黑屏/fastboot发送成功当运行证据。

## 技术背景与后续

D-166真实PE审计确认线程/锁/Kernel Protocol与调度HOB调用，缺失时有成功返回但不建显示线程的路径；ABL查splash_region，保存DTB只有cont_splash_region。实际入口FDT、运行时闭包、GOP可见输出、PE_Video和XNU入口仍未知。见两份2026-10-25专项审计。

新实机结果尚未产生；D-167当前为批准及门禁阶段。D-166提交af913ca已推送；本轮授权、主机观测和最新核验将另提交推送后再执行。既有参考仓/递归修改保留，R-015及旧像素授权不复活。
