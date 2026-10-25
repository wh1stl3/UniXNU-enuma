# D-223：恢复显示优先，拆开资格门与实际管线观测

用户要求“继续推进显示侧分析 尽快搞通uefi固件”。本轮完成离线源审、独立观测核心及主机验证，没有新设备命令、候选启动或物理访问。显示验收始终是相机确认固件绘制的小块色条/阶段字及受控恢复；日志、计数推进、注册GOP、编译成功都不替代它。

## 当前最有把握的判断

第一嫌疑是**现有资格模型在取得完整显示事实之前拒绝**，而非已经定位到面板不工作。S-013/014互补时序支持首样本Enable&3!=3的Reason5，仅为间接证据。按该路径成立，Timing已非零，但拒绝接口实际Active状态、Enable值、后续CTL/SSPP/LM/Decode与稳定性均未知；不能将它写成“稳定性失败”。

这里还有需要同时保留的反证：[固定小米52a2f18源码](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/techpack/display/msm/sde/sde_hw_intf.c)的timing setup确实写INTF_FRAME_LINE_COUNT_EN=3。因此原条件不是凭空编造，不能直接删掉以获取PASS。但同文件v1 get_status使用INTF_STATUS bit0判活动，再读FrameCount，并不以Enable==3作为状态读取门。这支持另做独立观测，不能直接据此放宽GOP。

第二个真实缺口是布局与地址：现有路由选择要求一个CTL同时标记两路DSI、恰好两个单源LM、已知左右标记和稳定局部几何；这些是支持的模型，不是已经观测到的enuma事实。Frame.Requirements仍保留ADDRESS|TOPOLOGY，CPU/SMMU地址关系和下游关联未证明；没过初始Enable时，也没有取得能验证这些模型的本次配置。不能把保留区首地址直接当实际扫描源。

第三条独立支线是KTZ8866背光：已有芯片/总线与窄批准范围，尚无UEFI协议ABI/从地址应答资格，不能将未点亮唯一归因于背光。原始XBL里存在I2C PE不证明运行时已完成初始化；“缺头文件所以必须重写GENI”仍是已撤回的推论。

## 已实现：独立双接口观测核心

新增固件`NativeObserve.c/.h`，未列入INF、DSC、provider或构建选择器。它是原生callback采集器，无物理指针、Boot Services、GOP发布、像素/MMIO写入、复位或内存映射修改。

- 三个样本、两次100ms等待，最多26读：revision；两路Timing、Enable、STATUS；只有STATUS bit0活动时读取Frame；最后复查revision。
- 仅已有R-004内0、0x6b800/0x6c000加0/0xa8/0x26c/0xac；不读CTL/SSPP/LM/PP或闲置银行。Active先于Frame，inactive Frame是未观测占位，明确由FrameReadMask区分，不能解读成硬件0。
- 分别输出ActiveThroughout、非零/稳定Timing、稳定Enable、两窗非回绕Frame增量1..64、ExactEnable3五类mask。Enable0/1/2不阻止采集；Timing0也仅体现在观测mask里，不能称准入成功。
- 回调只接受exact1，任意read/wait失败或revision改变不修改调用者输出。成功仅表示采集完成，包含负观测，不能当显示PASS。
- 原Evidence.c/Evidence.h/VideoCapture.c/Topology.c/Decode.c/VideoResult.h/INF逐字节与5cfcd4c相同，所有完整准入条件及ADDRESS/TOPOLOGY保持。

运行`python3 -B scripts/check_native_display_observe.py`：48项建模/边界用例、ASan/UBSan通过；AArch64 freestanding对象通过且无undefined helpers。覆盖Enable0/1/2/3、所有26个read失败位置、两wait失败、inactive帧读取抑制、停滞/回绕/过大增量、Timing/Enable独立变化、revision和非法回调/参数。

同时运行`check_inherited_gop.py`，实际Mu Blt的24通道排列/4操作、拓扑拒绝与144回调失败、完整采样330个失败位置及旧版本callback序列oracle、164个结果选择用例均通过。完整GOP代码没有被放宽。这些均是host/对象证据；没有新FD、打包候选、实际PE审计、运行时绑定或实机显示资格。报告`reports/enuma-native-display-observe-host.json`、`reports/enuma-inherited-gop-host.json`、`reports/enuma-display-frontier-analysis.json`。

## 同SoC来源对显示的实际意义

- elish的[SimpleFb](https://github.com/edk2-porting/edk2-msm/blob/e1952621f419f8db60ed28271264e1b5184c571d/Silicon/Qualcomm/QcomPkg/Drivers/SimpleFbDxe/SimpleFbDxe.c)将既有PCD framebuffer包装成GOP、SetMode不重建面板链；它不解决enuma扫描源识别。照抄固定地址和清屏会重复旧失败风险。
- umi的固定继承GOP建立在其候选布局上；cas能从显示配置解码，但还包含command手动CTL_START刷新。本机双DSI video不能复制该寄存器写法。
- [Qualcomm公开I2C指南](https://docs.qualcomm.com/bundle/publicresource/topics/80-70015-8SC/i2c.html)说明GpiDxe/I2C加载前置与open→read/write→close顺序。这加强了先核原厂I2C ABI/运行条件的路线，不能证明现代SDK接口与本机BOOT.XF.3.2闭源PE相同，更不拿标准UEFI I2C_IO结构冒充其ABI。

## 缩短到可见输出的推进顺序

1. 首先把上述小观察器绑定为**独立诊断前缀**，实际PE/宏/已有R-004映射/完整FAT/Boot v3/同源cold终止路径审计闭合后取得本机双路观测；不改完整GOP准入。该绑定尚未完成，本轮不把host结果当实际读数。
2. 若实际双路活动且两窗递增、Timing/Enable稳定，而精确Enable3不满足，再审有依据的原生资格修正，并继续同次稳定路由/源地址/stride/format与CPU/SMMU关系。若只有一路、计数不动或状态改变，按mask区分，不冒险读尚未证明安全的后续银行。
3. 背光并行做原厂I2C PE协议提供者、函数表/参数、实例和timeout资格；先从有限目标读回证实通道，再沿R-012最小亮度范围。避免从背光亮推断像素或面板初始化通过。
4. 布局/写入边界成立后实施新的小范围保存/色条/恢复候选，摄像头确认固件自产图案；然后阶段文字和真实GOP/menu。旧R-005/R-007和所有S-001..018不重试，不将过去像素批准默认为新实验资格。

本轮优先级转回显示，不以修通整套warm/ramoops作为显示分析的前置。UEFI“可构建/可受控cold返回”与“可见固件输出”继续分开记录。没有新增执行审批请求；硬停后的最后已知Android恢复仍为21:01:29独立核验结果，未为离线研究重复设备动作。原始影音只留本地，无新拍摄/录音/上传。
