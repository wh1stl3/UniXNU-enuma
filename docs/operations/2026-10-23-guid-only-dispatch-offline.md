# SimpleFb完整GUID筛选与正常分派结束兜底

2026-10-23（Asia/Shanghai）。本轮先按用户实机许可核验恢复，随后用户要求“继续进行离线分析 推进主线”，因此仅继续源码、主机测试、固件构建与打包，没有启动新候选。

## 恢复事实

12:11:03 +08:00确认enuma Android完成1、root、BL解锁、槽_a；boot_a与vendor_boot_a SHA均与原备份一致。用户确认按过键、人工恢复到Android。原233a9d8首测75秒无自动返回的历史结果不改写；当前人工恢复不补成原候选自动复位成功。证据见[恢复报告](../../reports/enuma-simplefb-recovery.json)。

## 漏门风险及实际改动

原诊断把`EnumaDispatchOrdinal == 32`与完整SimpleFb文件GUID作AND。计数在真实Dispatcher取出scheduled entry时增加，APRIORI是文件表，两者没有天然一一映射。新组合同时删除CPR/Display/UFS，不能沿用旧Display的运行序号。实际序号仍未知，漏门只是原因候选；不能据此认定SimpleFb运行过、成功或崩溃。

固件6bc5b81的扩展头增加`ENUMA_DIAG_GUID_ONLY`：仍核对完整GUID的两段64位、实际StartImage句柄及detail/status，仅跳过序号比较。默认0保留旧行为。构建接口`--dispatch-guid-only --dispatch-guid <UUID>`只允许stage13的驱动细节，ordinal1明确为不参与选择的占位；拒绝无GUID、stage12及全局异常/pool点。没有更改原25份迁移文件或六个原补丁。

可选`--dispatch-completion-fallback`只与GUID-only一起启用：在DxeMain首次CoreDispatcher返回后、缺失架构协议检查及BDS前，固定延迟7秒并调用既有ResetCold，若返回则CpuDeadLoop。默认关闭，不新增内存、协议、像素输出或驱动替换。既有SimpleFb metadata/Blt拒绝绘制及Probe早退守卫保持。

这是同步兜底，**不是看门狗，不能保证任何卡死都返回**。若目标不存在/DEPEX未满足/加载失败而Dispatcher正常结束，可避免继续进入BDS；若卡在更早驱动、构造器、异常循环或分派器本身，兜底根本不会运行。旧首测也不能追溯获得该保护。

## 验证与构建

147组真实detail/bridge头ASan/UBSan覆盖旧序号模式、GUID-only全部四个计数、完整GUID两半不匹配/NULL、返回状态与嵌套句柄隔离。完成兜底的默认关闭/旧stage13关闭/明确启用三种配置及非法配置拒绝通过。50项Python、重叠patch两次重放、50项源锁/原内存/example/verified检查通过。主机mock不代表UEFI ABI或硬件通过。

7479da1早期队列对照已实际构建并打包，FD df7eaae26726ee9f705ff4683e3a9558425d196355e17b90f1992f8cba14b049，停在stage12/ordinal1加载前，尚未实测。它证明该源码能构建，不证明运行复位。

6bc5b81的GUID-only point20/2秒加完成兜底已实际AArch64构建，FD 8f2c6f8a00a311ee63b1c9ca16db7b1b4d5bd501819193aa6875edb7be051ff7；DxeMain.c与Dispatcher.c实际clang命令均含两项启用宏，官方backend回退Mu补丁通过。后续FD/30 OEM/BootShim/v3证据见当前构建与打包报告；镜像仅保存out，不推送设备。

## 下一次实测顺序与判读

1. 恢复实机工作时重新核对设备身份、root、完成1、槽与原摘要，先用已归档早期stage12/ordinal1对照确认当前SimpleFb布局的早期复位能力。
2. 对完整SimpleFb GUID的point20进行2/7/2目标延时对照，完成兜底固定7秒。有随目标延时变化的响应才支持到达该调用前门；固定约7秒不能声称目标命中。启动/USB/Android时间有噪声，所有样本保留。
3. 调用前门确认后才安排point21/成功状态等返回路径；返回门不等于可见GOP或真实scanout参数正确。若无返回，立即停止追加启动，按既有实体恢复路径处理。

目标门7秒与完成兜底7秒单次时序不可区分；即使2/7有响应也只是检查点证据，不是完整日志。UART仍是完整早期过程观测的备选，尚未核对接点/电平，不猜接线。R-002跨复位RAM日志保持停止，不换址/扩堆/借显示内存。

来源与机器证据：[选择与构建审计](../../reports/enuma-dispatch-selection-offline.json)、[真实头测试](../../reports/enuma-dispatch-details-host.json)、[原首测交接](2026-10-23-simplefb-metadata-variant.md)。未验证GOP可见/实时UEFI map/BDS/XNU/触控。

发布核验：固件6bc5b81已推送；源码CI39911281252成功并回读PASS（仅源码契约）。GUID-only候选FD审计30个原厂PE/DEPEX逐字节、192字节BootShim+3MiB FD及AOSP v3打包回读通过；全部新镜像未启动。编译宏取自实际DxeCore clang响应文件并随私有归档保存。
