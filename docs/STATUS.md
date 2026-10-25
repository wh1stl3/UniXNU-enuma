# 当前状态：D-223，显示优先分析与独立双路观察器完成离线验证

2026-10-25T21:32:30+08:00。用户要求继续显示侧分析、尽快搞通UEFI。已将显示恢复为首要交付：相机可确认的固件色条/阶段字及受控恢复。当前仅完成离线分析、未接线观察器与主机/对象验证，没有新增设备命令/构建候选/映射/写入/上机，不把“构建通过或注册GOP”当点屏成功。原始影音仅本地，本轮无新增拍摄/录音/上传。

当前主判断（中等置信）：S-013/014时序只支持首样本Enable门先拒绝，后续路由/稳定性按该分类尚未执行，不证明管线停止。小米原生setup确实写Enable=3，但v1 get_status用STATUS bit0后读FrameCount、不以精确3阻断状态观察；故先独立观察，不直接删完整资格门。布局/地址与双DSI下游关系仍未闭合；KTZ8866背光的UEFI I2C ABI/应答资格仍缺，不能单凭黑屏认定背光故障。

新增NativeObserve.c/.h：两路三样本、<=26读/两次100ms等待、inactive不读Frame，分别记录活动、非零稳定Timing、Enable稳定、两窗Frame递增1..64、精确Enable3。采集完成可包含负mask，不是GOP准入。48项ASan/UBSan与边界测试、AArch64无undefined对象通过；原完整Evidence/VideoCapture/Topology/Decode/Result/INF均未变。实际Mu Blt、拓扑、330失败边界oracle及164结果选择回归通过。

固件pin `bbe30f697e1683e5e1621c26c85b88b9431ac7bc`已推送，仅新增未绑定源/说明；最近实际构建/实测固件仍5cfcd4c，不能把新pin叫已构建镜像。观察器未进入任何INF/DSC/provider，尚无新FD/实际PE/打包资格。源锁和迁移检查通过，board.toml/bringup-plan/内存/verified及完整GOP准入均不改。

下一步候选：沿已有R-004显示窗口把NativeObserve绑定为独立诊断前缀，保留cold终止与原GOP门；先完整源/PE/宏/映射/完整载荷审计和当前文档发布/即时恢复相机门禁，再谈设备动作。取得真实双路观测后才判资格修正或转查活动性/稳定性，随后闭合CTL/SSPP/LM布局和CPU/SMMU地址关系。背光并行优先核原厂I2C协议ABI和有界应答，沿R-012原最小范围；没有发布新执行方案或扩大旧像素批准。可见小图案→阶段文字→GOP/menu为显示交付顺序，不拿日志通道替代。

报告reports/enuma-display-frontier-analysis.json、reports/enuma-native-display-observe-host.json、reports/enuma-inherited-gop-host.json；复现scripts/check_native_display_observe.py及check_inherited_gop.py；分析docs/operations/2026-10-25-display-frontier-analysis.md。固定小米52a2f18源码已复核SHA/Git blob，原代码作为行为参考未导入GPL。

设备边界：最后S-018无console访问warm在20:57:13单次发出，75秒未受控返回触发硬停；用户恢复，21:01:29独立Android完成/root/A槽/解锁/设备与本地备份双分区摘要通过。录像1090/1090帧与恢复画面已确认，原失败记录保留。S-016映射/cold和S-017三读/cold已自动返回；这仅使warm链成为优先嫌疑，未证明writer安全/留存。所有S-001..018及旧R-005/R-007失败图consumed，不重试。原日志专项仍无新硬件动作，本轮不操作设备；无人工按键或新增审批待办。

前一7873237同型仓离线研究已推送，本里程碑提交显示分析与未接线源码进展。真实可见GOP、XNU/iPadOS、完整链运行和存储仍未实机闭合。
