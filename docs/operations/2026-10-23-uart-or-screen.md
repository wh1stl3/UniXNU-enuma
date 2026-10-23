# UART只读核对与屏幕诊断路线

2026-10-23 Asia/Shanghai。用户要求从当前连接实机获取UART配置，若不能满足接入条件则用屏幕诊断。本轮仅通过明确选中的enuma进行root只读查询，没有reboot、临时启动、flash、pinmux/绑定写入、挂载debugfs、模块加载或MMIO访问。

## 实际取得的配置

15:18:10核验enuma/root，Android完成1、槽_a；本次未重读分区摘要，上一份原摘要核验仍是12:11的恢复记录。原始命令行、FDT、内核配置、绑定、控制台查询仅在out/uart保存，公开[结构化报告](../../reports/enuma-uart-discovery.json)排除了设备标识。

- 命令行请求console=ttyMSM0,115200n8与androidboot.console=ttyMSM0。它是请求值，不能当成线上测得的波特率。
- 活动FDT的serial0别名为/soc/qcom,qup_uart@988000，compatible=qcom,msm-geni-console，reg为0x988000/0x4000；status=disabled，未设置chosen stdout-path。
- 该console关联qupv3_se2的GPIO117/118，default功能qup2，sleep功能gpio。这里只确认SoC引脚组，不知道哪个实物焊盘、哪根线是TX/RX，也没有测电平。
- /proc/consoles只列pstore-1，未见ttyMSM活动控制台。msm_geni_serial绑定的是另一个998000.qcom,qup_uart，不能把它冒充988000调试console。
- 已有固件实际as-built绑定BaseSerialPortLibNull；Android串口节点或命令行不自动为自制UEFI提供早期UART输出。

因此当前USB/ADB可以提供软件配置线索，**不足以完成外接UART接入**。实物测试点/TX-RX映射、电平/地线、外部适配器与采集，以及早期固件串口配置/输出仍缺；不猜接线，不为确认日志而切换当前UART或修改GPIO。留存资料，暂不把UART作为主线依赖。

## 按用户选择推进屏幕诊断

先沿已备同版早期对照及完整GUID 2/7/2确认可恢复的DXE/PE调用前路径；这些只服务于建立GOP，不把它们当最终日志通道。随后准备调用返回/状态与唯一GOP字段观测，核对真实scanout base/偏移、stride、格式、有效像素子范围、缓存及生命周期。Android运行时图形地址不能直接当作ABL进入UEFI时的scanout。

当前SimpleFb仍是metadata模式，Blt拒绝像素、EnumaProbe入口早退；本轮不撤掉这些守卫。只有取得可说明来源的几何并满足原内存/所有权边界后，才在受控范围做可见小标记，再显示构建标签、阶段、EFI_STATUS、GOP信息/内存图摘要，逐步形成同次启动屏幕日志。未建立GOP的SEC/DXE早期黑屏依然不可见，定时复位只作低带宽定位与恢复，不能当完整过程日志。

晚上集中测试仍依[既有计划](2026-10-23-evening-validation-plan.md)逐次核验；本轮只读查询不意味着已经恢复镜像启动。若出现新的地址/大小/verified需求仍按AGENTS处理，不重启R-002的失败跨复位RAM日志路线。
