# DisplayDxe 执行边界定位方案（2026-10-25）

D-164路线复审：本方案保留为原厂支线工具，先完成[显示交接契约与原厂ABI离线审计](2026-10-25-public-source-route-review.md)，按实际缺口决定候选，不自动进入实机。

状态：设计方案，未构建、未实测。用户本轮仅授权修正文档并给出下一步方案；不是新的硬件执行或分区写批准。

## 事实基础

R-014实测镜像922972e61b0e4e3d7b7c931b53b76531a2db2a08504c6794263e5ff3f5ab1a75，内含FD dbca3fcb2f470807f1fdac8b17e47c6eb604f3be49b1563c42df5bfc020615e0。直接解析该FD确认DisplayDxe在APRIORI第33项（零基索引32）；不能把索引当运行时派发序号。

PI §10.3及Mu Dispatcher.c表明APRIORI驱动直接排队、忽略DEPEX。这不保证实机到达目标、LoadImage成功或PE入口被调用。未知GUID字节没有命中，不能证明无提供者、不被间接使用或与初始化状态无关。R-015按原动机暂不执行，不补未知ABI的stub。

R-014目标GUID误设为不存在的SimpleFbDxe，因此目标门不会命中。但构建开启completion fallback；CoreDispatcher若正常返回，仍会等待7秒再尝试ResetCold。75秒无返回不是GUID配错的必然结果；派发没有返回、异常、复位失败及观测问题均待区分。fallback不是异步watchdog。

## 两个新候选

保持原厂PE、内存/映射、派发顺序与OEM模块集合不变；只保留既有without-ufs隔离。两份均以DisplayDxe完整GUID为目标：4138022f-06c7-4f79-9c94-7e33b511a4e7。

共同参数（构建参数规格，不是boot命令）：

```text
--stop-stage 13 --stop-delay 2 --dispatch-ordinal 1
--dispatch-guid 4138022f-06c7-4f79-9c94-7e33b511a4e7
--dispatch-guid-only --dispatch-completion-fallback
--diagnostic-without-ufs
--diagnostic-gop-query 0 --diagnostic-gop-step 0 --value-source off
```

不得添加diagnostic-simplefb或pixel-preview。ordinal=1只作GUID-only占位，不使用静态APRIORI位置猜实机ordinal。

| 候选 | 唯一差别 | 命中所支持的事实 | 不支持的事实 |
| --- | --- | --- | --- |
| A | --detail-point 15 | 已到目标CoreStartImage调用前，LoadImage已有可用句柄 | 不证明PE入口或驱动代码运行 |
| B | --detail-point 13 | 目标CoreStartImage已经返回 | 不提供返回状态数值，不证明返回EFI_SUCCESS或GOP已安装 |

目标门使用2秒延时；初始CoreDispatcher完成兜底为7秒。主机测到的是bootloader/Android启动等开销加门延时，不能把“约16秒/约21秒”硬编码成永远有效的判据。必须以同源对照/编译审计验证门的可观察差异；如需delay7校准，另做资格与逐笔安排，且目标7秒会与7秒fallback重叠，不能单独判别命中来源。

## 实验先后与判读

先A，确认前置边界及返回通道，再决定是否执行B。单笔75秒无返回不作位置归因。无返回当轮停止追加、落实文档与恢复；不得擅自原样重试失败候选以累计样本，统计重复须有明确有效范围。

| 观测 | 可支持的判断 | 下一步 |
| --- | --- | --- |
| A目标门响应 | 到达目标启动调用前 | 资格/门禁满足后考虑B |
| A只见fallback响应 | Dispatcher完成但目标点未命中；可能目标加载失败/未发现/过滤错误 | 检查FV、认证/LoadImage状态和GUID接线；必要时detail14/18/19 |
| A无返回 | 尚未定位，不能直接断言派发故障 | 先恢复，再离线审更早路径、异常和复位出口 |
| B目标门响应 | CoreStartImage返回 | 后续用query0的detail16/17区分EFI_ERROR/非错误，再单独检查GOP |
| A有响应而B无返回 | 在可重复、同源和观测有效前提下，支持缩小到启动调用及其返回区间 | 必要时detail20/21/22细分CoreStartImage、PE入口、构造函数、CoreExit/LongJump，不能直接称驱动内部挂死 |
| B只见fallback响应 | Dispatcher完成但目标返回门未命中，先核查目标是否实际加载/启动 | 不把fallback当驱动成功或没有运行的充分证明 |

detail16/17在GOP_QUERY=0下分别按EFI_ERROR/非错误判别，不输出精确EFI_STATUS，警告也属非错误。detail20在PE入口调用前，detail21在直接PE入口返回后；PE包装器构造函数也在该调用区间内。detail22的LongJump/Exit路径和异常门适用范围先审源码，不能按名称猜。

## 离线资格及设备门禁

1. 确认设备仓gitlink、锁、firmware检出相同且源码干净；保留他人修改，不reset/clean。保持固定上游，不复制底座实现。
2. 构建后检查真实C编译参数、Core中GUID两半编码、point/ordinal/GUID-only、query0、delay2及fallback=1；检查新FD实际APRIORI、原厂PE/DEPEX摘要和精确省略集仅UFSDxe。
3. 归档独立FD/raw/image与构建/审计/打包报告，摘要逐项绑定；不能用旧R-014报告代替新候选资格。测试必须Mock设备边界，禁止测试触发adb reboot/fastboot boot。
4. 实机前落实全部适用文档及规定的提交推送门禁。当前仅修文档，未提交；不得绕过干净/发布校验。核对R-014及新候选的实际授权范围，不能从R-015或本轮文档修改推导新批准。
5. 即时核验enuma身份、匹配备份、原槽、root/解锁和恢复条件；临时boot不写分区。原厂显示驱动本身可能进行硬件写入，不能把整个候选称为只读探针。
6. 相机连续取证与门/返回证据配合，记录实际时间戳并关联boot发出时间；低频采样无内容不能证明从未出现瞬态画面。保存原图，按实际方向旋转判读。
7. 超时停止追加，按真实端点和恢复核验更新STATUS/HANDOFF/WORKLOG/DECISIONS/审核与人工待办；恢复后继续离线分析。

## 原厂栈优先，按证据分流

149模块和面板资源的发现支持优先评估原厂复用，但不证明依赖闭包、初始化线程、硬件状态或背光全部可用。DSI计数推进仅支持采样期接口活动，不证明双DSI到面板的完整链路。暂不自写GENI I2C/背光，也不补stub；取得具体调用/ABI缺口后再评估真实实现或窄适配。

依据：https://uefi.org/specs/PI/1.8/V2_DXE_Dispatcher.html#the-a-priori-file 。本地参照：firmware/diagnostics/EnumaDispatchDetailCheckpoint.h、EnumaDispatchCompletionCheckpoint.h、EnumaImageEntryCheckpoint.h及reports/enuma-fd-audit.json。
