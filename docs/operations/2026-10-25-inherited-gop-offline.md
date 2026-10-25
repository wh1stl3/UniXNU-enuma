# D-194：继承扫描输出GOP的首个离线实现

日期：2026-10-25，Asia/Shanghai。用户要求优先恢复真实GOP与可见错误通道。本轮已实现和验证纯解码/采集组件，**尚未恢复真实GOP**：没有驱动协议发布、DSC/FDF接入、新FD/boot镜像或上机。旧S-007保持consumed；最近完整恢复核验仍为16:06:22 Android/root/A槽/解锁/原分区及备份摘要一致。

## 重要板级发现

保存的enuma FDT643aa3ec…34c62中，primary默认panel phandle指向K81_42_02_0a_dual_cphy_video，panel-type为dsi_video_mode，phy编号0/1，时序字段为每链路800x2560。只读Android DRM模式文件实际返回1600x2560的120/60/30Hz视频模式条目；标准fb0 sysfs不可用。这些不能代替UEFI当时的活动管线快照，也不从800x2直接断言mixer左右顺序。

cas纯解码仅接受CTL_TOP bit17置位的命令模式，且它的完整GOP会清屏并可能写CTL_START。enuma不能直接复制这条策略。当前实现显式区分video/command；video分支忽略旧command auto-refresh字段，不产生手动kick需求。模式依据固定SDE v1源的bit17语义核对，GPL源只读作寄存器事实参考，未复制代码。见reports/enuma-inherited-scanout-inputs.json和config/display-activity-sources.lock.json。

## 已实现的软件

固件源e6d1867（组件首笔0080640）：Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib。

- Decode.c只复用cas的纯快照算法，保留出处、SPDX、原许可文本和选取源码SHA。宽高、splash边界、video/command及每pipe局部坐标原点全部显式输入，没有cas面板、日志/堆或FD地址常量。
- 支持完整面板的连续分块矩形、源裁剪偏移、stride、像素通道顺序、一致底层分配和完整覆盖检查；拒绝secure/virtual/压缩或不支持格式、越界、不一致、覆盖缺口、模式不符和未知原点。OutXy局部空间必须有OriginMask；不猜LM0/1就是左右屏。外部原点信息仍需实际拓扑佐证。
- 成功只输出候选布局，activity、blend/occlusion、CPU地址关系、refresh、topology五项Requirements保持置位。**不能为了发布GOP手工清零这些要求。** 本组件未证明当前扫描输出归属或物理/IOVA等价。
- Capture.c通过带上下文的受限回调读寄存器偏移，最多267次，最大相对偏移0x73830；无direct volatile MMIO/pixel指针、无寄存器/像素写入、定时刷新、分配或协议操作。回调失败立即终止并完整保留调用者快照，错误版本只读一次即拒绝。未来调用者须另外建立并检查R-004 staging映射及DT有效范围。
- 采集器最初的C结构体初始化/赋值引入memcpy/memset，已改为明确本地字节操作；两个AArch64对象现无外部未定义符号。不是依赖一个未链接的运行库碰巧工作。

## 验证与证据

scripts/check_inherited_scanout.py实际编译生产Decode/Capture：28个解码场景涵盖视频/命令、手动/自动刷新分类、完整帧与局部双tile、未知/错误原点、覆盖缺口、格式/secure/virtual、范围和溢出；ASan/UBSan通过。对267个采集回调位置逐一注入失败，均立即终止且输出快照不变。AArch64 freestanding编译及llvm-nm未定义符号检查通过。

命令（WSL，输出均out/）：

```text
python -B scripts/check_inherited_scanout.py
python -B scripts/audit_inherited_scanout_inputs.py
python -B scripts/check_firmware_source.py
```

机器报告enuma-inherited-scanout-host.json、enuma-inherited-scanout-inputs.json和enuma-firmware-source-migration.json。合成快照不是本机实际寄存器；主机/AArch64对象编译不是完整UEFI链接、QEMU或实机GOP通过。

来源：ht94911/uefi-cas@a491522d（casPkg与实测893f5025相同）的DisplayDecode.c；只引入选取的纯算法，不复制CasPlatform、DisplayHardware、SetMode/refresh或物理Blt。新来源/许可和差异在固件组件sources.json、NOTICE.md、LICENSE.upstream。源码扩展清单、设备锁与gitlink已同步，新固件源无设备动作。

## 下一步具体接入点与约束

1. 在新组件基础上接真实GOP后端，优先复用现有FrameBufferBltLib，补完整QueryMode/SetMode/Blt和错误清理的主机验证，不拷cas物理写入函数。
2. 形成同次UEFI快照与双链路局部→全局坐标的取证/判定路径；核实际route稳定、输出mode/格式、混合/遮挡、CPU可访问的splash交集及刷新条件。Android模式和旧探针时序不代替这些字段。当前仍无可供直接填入OriginMask的实机拓扑记录。
3. 仅元数据/谓词满足后才形成真实GOP固件候选；不得先注册假成功协议、把Requirements清零、放宽secure/压缩/边界，或原样重试旧SimpleFb/R-005。video模式先不写CTL_START，command策略不默认继承。
4. R-004已批准映射按旧精确补丁在构建staging应用，原XBL迁移表未改。新GOP接入时必须核实际FD是否含该映射，不把旧批准或原始表的缺项当当前新映像已映射。
5. 真实GOP会涉及像素访问，新增具体读写范围与必要门禁需随完整可审查候选说明；本轮未申请新授权，未执行像素/MMIO写入或新临时boot。内存字段/verified/flash/erase/改槽边界不变。

本轮只有Android身份/DRM只读查询，无重启、分区或寄存器操作。原始影音只留本地。主线仍是恢复GOP后复用AdvancedLogger/QR，观察完整载荷13项报告和真实DarwinBoot/XNU失败；本离线库不是系统启动成功或新的硬停。
