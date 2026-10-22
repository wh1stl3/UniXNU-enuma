# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相；历史见 WORKLOG。

## 当前结论

**已生成 EnumaProbe 01 UEFI/GOP 诊断候选，完成 XNU 硬件 ADT 片段和 NT36523 解码核心；尚未启动候选或运行 XNU。** 用户暂时不能配合按键，明确先离线，本轮没有操作设备。

目标保持 iPadOS 17.7.11 / 21H461、iPad7,1 / j120ap、XNU 10063.141.1、4 KiB。R-001 请求仍为 512 MiB；board.toml 保持 example=true，没有修改物理内存字段。

## 当前候选

- 下一次测试使用 out/boot-candidate/enuma-uefi-probe01-r2-boot-v3.img，3153920 bytes，SHA256 3db695db10c1114352994ab64e551abc74391c2e50bbabfd48be0b37acec790a。
- FD 为 3 MiB，SHA256 a169c9dbb894dfacc5d421779a2e855639bc1d0b4e4c0c224602a582b7471dc2。完整 CLANGPDB 构建通过，81 个固件文件；33 个本机原厂 PE/DEPEX 仍逐字节一致。实际 UniXNUDxe PE 包含 Probe 启动目标 GUID。
- Probe 原样复用 DarwinBoot 的 GOP 验证、GetMap、RunEnd 和大字诊断绘制，显示 EL/CNTFRQ/4K 字段、GOP base/尺寸/stride/format、连续 free run 摘要；停留 60 秒后进入原 UniXNULib。只观察内存图，不分配 512 MiB，不调用 ExitBootServices。实际显示和协议调度均未验。
- 192-byte 上游 BootShim + FD，raw boot v3，空 ramdisk，官方 unpack 字节回读通过，保留 vendor_boot；不带 XNU/完整 ADT/iPadOS 用户态。
- enuma-uefi-gic-boot-v3.img 保留为无 Probe 的历史基线；遗漏 GIC 的最早 enuma-uefi-boot-v3.img 继续禁用。

## 基础平台与触控

- 用固定 sheng node 编码器生成 2956-byte 硬件片段：8 个 qcom,kryo、affinity 0/100..700、19.2 MHz、PSCI SMC、GIC 0x17a00000/0x17a60000、stride 0x20000。实际 identity ranges 转为 ArmCpu 布局；virtual timer INTID 27 与 FDT 对应。没有 /chosen、DRAM、GOP、根卷、donor/product，不能作为完整启动 ADT。
- EnumaNvt 新增 SPI dummy 去除、66/80-byte 规范包的触控前缀校验、十点 ID/坐标/压力、ESD/WDT 分类与 FWINFO 闭区间归一化；错误不交付部分帧。
- NativeHidInput 坐标仍写死 sheng 的 30480×20320，不能直接喂本板坐标。没有本板 HID 发布、IRQ/IOKit、FWINFO 读取、固件上传、恢复或笔输入支持。
- GENI 继续复用固定 NativeGeniSpi；UFS 只读时钟支持保持。Sheng PMGR、SM8550 NativeUfs 和 A740 NativeAdreno 仍关闭。

## 验证与下一步

27 项 Python 检查通过；GENI/时钟/NT36523 主机 ASan/UBSan 通过，4 个 AArch64 对象编译通过；源码/补丁图和 FD/boot 字节审计通过。这些不等于 QEMU、IOKit 链接或实机通过；未设置 *_verified=true。

1. 等用户方便在旁配合按键，再按 A-002 核对 enuma 身份、备份及回 fastboot 条件后临时启动 Probe；不因 ADB 可见自动重启。
2. 获取真实 GOP/GetMemoryMap/厂商协议证据，再测 512 MiB 实际分配和 EBS 显示保持；board.toml 新内存字段仍需审查。
3. 组合完整 ADT、完成内核链接/预链接，验证首核 timer/GIC，再推进多核。
4. NT36523 补 FWINFO、芯片/固件映射、时钟/pinmux/IRQ 和独立 digitizer。源码固件名与历史 FDT 的 _k81_ 差异尚未闭合。

详见 [本轮离线报告](operations/2026-10-22-probe-platform-touch.md)。上游只读；产物在本仓 out/；仅本地 main 提交，未推送。
