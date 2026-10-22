# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相；历史见 WORKLOG。

## 当前结论

**黑屏定位取得执行阶段证据：BootShim 入口 2/7 秒门、复制/缓存维护后的门、SEC C 入口、DXE Core C 入口，以及 CoreDispatcher 前的门，六次临时启动均自动回到 Android。最后一次 20:57:59 发出，32.018 秒后确认 sys.boot_completed=1、root 和 boot/vendor_boot 摘要不变。** 未 flash/erase/改槽；没有运行 XNU/iPadOS payload。GOP 仍未得到。

诊断构建能走到 DXE 驱动调度前，后续重点是驱动调度、原厂显示依赖及 BDS/Probe 启动路径。各构建有插桩和链接布局变化，不能倒推最初 Probe 01 r2 黑屏镜像停在完全相同的位置，也不能把门之前所有硬件都标为 verified。

目标保持 iPadOS 17.7.11 / 21H461、iPad7,1 / j120ap、XNU 10063.141.1、4 KiB。owned-memory 请求保持已批准的 512 MiB；board.toml example=true，物理内存字段及 *_verified 标记未改。

## 当前候选与证据

- 当前构建为 **诊断 stage 10，到 CoreDispatcher 前延迟 2 秒并复位**，不能当作正常固件使用。镜像 out/boot-candidate/enuma-dxe-dispatch-stage10-boot-v3.img，3153920 bytes，SHA256 fe97cac064925e430e4b2d4c8f058aa1cf8a0a05fb051e1c7c1b484b1eadc43b。
- 实测镜像内 FD 为 3 MiB，SHA256 da56498bcb5f8ce804bc9d1719d9be8cf2c4d7ed35113ec18bce70d654aeaabe。stage 3 / 9 / 10 的实际构建报告与 raw 保存在 out/entry-probe/ 对应子目录。随后仅规范补丁的空白上下文行并重建，当前 reports/enuma-firmware-build.json / enuma-fd-audit.json 对应未启动的重建 FD d6bf6bb203cd71da4b049db7f8a259c9d702be05180060e3b259c2c2d6c05d8c；完整构建和 81 文件/33 OEM 字节审计通过，但重建摘要不一致尚未归因，不能把旧实测结论转移给新二进制。未覆盖已测镜像/raw。
- stage 0 恢复正常路径；3..10 是可选择的 SEC/DXE 门，复用 Mu TimerLib / ResetCold。BootShim 门复用固定上游编译函数与复制逻辑，不猜 framebuffer/MMIO 日志地址。
- 六次实测命令、镜像摘要、定时与恢复结果：reports/enuma-entry-device-tests.json。2/7 秒入口门的 ADB 返回差 5.422 秒；用户明确确认 2 秒实验未按键。
- 原 Probe 01 r2 黑屏历史保留在 reports/enuma-probe01-device-test.json，不原样重试。更早遗漏 GIC 的候选继续禁用。boot v3 保留原厂 vendor_boot、空 ramdisk，不含完整 ADT/XNU/用户态。

## 仍有效的基础适配

- 本机 XBL 的 45 项内存/MMIO 配置、31 项数值配置、33 个 OEM 驱动和 K81 面板资源已接入。实际 GOP format/base/stride、UEFI GetMemoryMap、连续 512 MiB 分配和 EBS 显示保持仍未观察。
- 本板硬件 ADT 片段包含 8 核 affinity、19.2 MHz、SMC PSCI、GIC 及 stride/ranges；缺 /chosen、DRAM、GOP、根卷和 donor/product，不能作为完整 ADT。
- GENI 复用通用 NativeGeniSpi；NT36523 解码核心有主机证据。FWINFO/轴向、固件上传、IRQ/IOKit/HID 和笔输入仍缺；sheng 坐标常量及 SM8550 UFS/A740 驱动不能照用。

## 验证层次

30 项 Python 检查在 Windows Python 通过；共享检查点头部的 stage 0/3..10 主机 ASan/UBSan 通过。BootShim 门和 SEC 入口门有 QEMU virt/SMC 执行证据，仅代表该平台。stage 3/9/10 的固件构建、OEM 字节审计和 boot v3 往返通过；上述六个点有实机返回证据。没有宣称完整 DXE、GOP、XNU 或触控运行通过。

## 下一步与远端

1. 在 CoreDispatcher 内及其返回处补观察，区分具体驱动、厂商显示协议闭包、BDS 与 Probe 入口。优先复用已有 TimerLib/ResetCold 门，保持恢复路径；新内存字段及验证标记仍需审查。
2. 取得实际 GOP 和 UEFI map 后再推进 owned-window / XNU 基础平台；完整内核链接、预链接及 ADT 仍未闭合。
3. 用户已批准公开建仓：origin=https://github.com/wh1stl3/UniXNU-enuma.git，main 已推送，CI 配置提交 2312231。macOS preflight 实际通过：run 39784132935，Apple Silicon、macOS 15.7.9 / image 20260907.0337.1、Xcode 16.4 / SDK 18.5、arm64 对象编译成功；见 reports/enuma-macos-preflight.json。通用 4 KiB XNU bootstrap 已启动，run 39784240390 仍在运行，尚无构建成功结论；实时状态见 https://github.com/wh1stl3/UniXNU-enuma/actions/runs/39784240390 。该模式关闭本板功能，只验证工具链/基线，不是完整 enuma 内核或预链接，板级 archives / prelink 输入仍缺。SDK 18.5 不改变 donor 17.7.11。
4. 设备已恢复 Android，当前无待按键事项。

重建差异进一步检查：SEC 含 __TIME__ 字符串（20:56:24 → 21:02:55）与相应常量池变化；PcdDxe 仅 CodeView RSDS 标识中的 8 字节改变。其余解码文件除承载它们的压缩容器外一致。见 reports/enuma-fd-rebuild-comparison.json；不是完整语义等价或新镜像实测证明，仍分别绑定摘要。

详见 [入口定位报告](operations/2026-10-22-entry-checkpoints.md) 与 [构建环境核对](operations/2026-10-22-build-environments.md)。上游和 nuwa 只读，二进制与私有设备标识仅在忽略的 out/ 中。
