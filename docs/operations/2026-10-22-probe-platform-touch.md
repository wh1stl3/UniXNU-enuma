# enuma Probe、基础平台和 NT36523 离线推进

2026-10-22，Asia/Shanghai。用户暂时无法配合恢复按键，明确先离线；本轮没有 ADB、重启、临时启动、flash、erase 或改槽操作。

## UEFI/GOP 诊断候选

新增 enumaPkg/Application/EnumaProbe，通过 PcdUniXNUApplicationFile 复用原 UniXNUDxe 的启动项注册，保留原 UniXNU、DarwinBoot 与 UniXNULib。FD 审计要求 Probe 已入卷，且 UniXNUDxe 的实际 PE 含 Probe GUID，避免仅打包却未选择入口。

构建时校验固定 UniXNU 75bc13dd 的来源摘要，原样提取 GetMap、RunEnd、DiagDraw 和 BootVideo.h/DiagFont.h 到 out/。上游只读，不将其源码放入 Git；字体保留 Android 原始版权/许可。

若能进入 Probe，显示 EL、CNTFRQ、MIDR/MPIDR、4K TGran4 字段、GOP/loader 视频检查结果、分辨率、格式、stride、framebuffer base/size，以及最大连续 conventional run 和 2 MiB 对齐后空间。大字停留 60 秒供拍照，然后调用原 UniXNULib。

观察阶段不写文件或变量、不触碰猜测 MMIO、不分配 512 MiB、不 ExitBootServices、不自动复位；绘制会写 framebuffer。完整固件仍有原 UniXNUDxe 的启动项注册与菜单行为。内存摘要是应用时刻快照，对齐空间也未包含真实内核 Base 余量，不等于分配测试成功。GOP 若不符合原 BootVideo 的 BGRA32 约定，不强行用猜测格式画大字；文本控制台是否可见待实测。

完整 AARCH64 CLANGPDB 构建退出码 0；81 个固件文件，33 个原厂 PE/DEPEX 字节一致。FD SHA256：a169c9dbb894dfacc5d421779a2e855639bc1d0b4e4c0c224602a582b7471dc2。上游 HwResetSystemLib 声明和 make 时间偏差警告仍存在。

候选 out/boot-candidate/enuma-uefi-probe01-r2-boot-v3.img，3153920 bytes，SHA256 3db695db10c1114352994ab64e551abc74391c2e50bbabfd48be0b37acec790a。192-byte BootShim + 3 MiB FD、raw boot v3、空 ramdisk，官方 unpack 回读一致。保留 vendor_boot；没有 XNU/完整 ADT/iPadOS payload。旧 GIC 候选保留为基线，遗漏 GIC 的最早候选继续禁用。

证据：reports/enuma-firmware-build.json、enuma-fd-audit.json、firmware-overlay-check.json、enuma-boot-payload.json、enuma-boot-candidate.json。

## XNU 基础输入

prepare_enuma_adt_fragment.py 调用固定 sheng 生成器的 node 编码器，只序列化硬件节点。核对 FDT 与 ArmCpu/ArmDTPlatform/NativeHidInput 来源摘要。

| 项 | enuma 输入 |
| --- | --- |
| CPU | 8 个 qcom,kryo；reg 0/0x100…0x700；只标 boot CPU running |
| Timer | 19.2 MHz；virtual PPI cell 11 对应固定 ArmCpu 的 INTID 27 |
| PSCI | arm,psci-1.0，SMC；不继承 sheng SMP/GIC/IPI workaround |
| GIC | Distributor 0x17a00000/0x10000，redistributor 0x17a60000/0x100000，stride 0x20000 |
| arm-io | 实际 SoC identity ranges 转为三个 little-endian uint64，保持 span 0xffffffff；reg 落在该范围 |

hardware.adt-fragment 为 2956 bytes，SHA256 5771d95333672ed494ad1692dca43d43107505628790b16fdfcfe12a3061cee9。三项测试独立解析二进制并检查 CPU/GIC 布局及无外国板/猜测 DRAM。没有 /chosen/NVRAM、身份、DRAM/video/root，不能当完整 ADT；没有内核链接、预链接或执行。

## NT36523 核心及接入缺口

固定来源：MiCode/Xiaomi_Kernel_OpenSource 52a2f180 的 nt36523/nt36xxx.c/.h。协议事实对应 CTP_SPI_READ（一个 dummy、rx+2）、nvt_ts_point_data_checksum（bytes 1..65）、nvt_ts_work_func（10×6-byte 记录、ID/state、12-bit X/Y、前两槽压力高字节）。头文件的 contacts=10、pressure=1000、checksum index=65、dummy=1 亦检查来源。

EnumaNvt 不含 Linux input/SPI 实现。接受 66-byte touch 或 80-byte pen-extended 规范包，仅解码触控前缀；可从完整 67/81-byte SPI 响应去 dummy。坐标最大值由未来 FWINFO 调用方提供，按闭区间归一化，不以屏幕尺寸替代传感器范围。坏校验、非法活跃 ID、重复 ID 或越界不交付部分帧；0x77 和 FD/FE 返回恢复分类，不自动复位或下载。只有有效空帧才代表零接触，错误不得直接发布成新帧。

固定 NativeHidInput 的 touchTick 仍写死 sheng 的 30480×20320，还依赖 native_touch_* seqlock 和探针符号。因此不能直接打开配置完成接入；后续需要独立 digitizer、按 ID 的抬手处理和真实轴向。没有发出 SPI 事务、读取 FWINFO、上传固件、接 IRQ/IOKit 或实现笔输入。固件名 _k81_ 与源码候选差异仍待核对。

主机 ASan/UBSan 检查真实 decoder；固定厂商原 checksum 函数仅提取至忽略的 out/ 作 envelope 对照，保留 GPL 说明，不链接入产品。覆盖十点乱序 ID、压力边界、65 个坏校验、79 个截断、dummy/in-place、重复/非法 ID、坐标范围、ESD/WDT、零接触和归一化端点。四个 AArch64 freestanding 对象编译成功，GENI/UFS 只读时钟测试仍通过。27 项 Python 检查通过，未设置 *_verified=true。

## 复现入口

```powershell
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/prepare_enuma_adt_fragment.py --sheng D:/Code/PortingiOSLegacy/common/sources/UniXNU-sheng --unixnu D:/Code/PortingiOSLegacy/common/sources/UniXNU
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B -m unittest discover -s tests -p 'test_*.py'
wsl -d Ubuntu-22.04 -- python3 -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_enuma_drivers.py --unixnu /mnt/d/Code/PortingiOSLegacy/common/sources/UniXNU
wsl -d Ubuntu-22.04 -- python3 -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/build_enuma_firmware.py --reference /mnt/d/Code/PortingiOSLegacy/common/sources/mu-nuwa-firmware --unixnu /mnt/d/Code/PortingiOSLegacy/common/sources/UniXNU
wsl -d Ubuntu-22.04 -- /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/audit_enuma_fd.py
wsl -d Ubuntu-22.04 -- python3 -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_firmware_overlay.py --unixnu /mnt/d/Code/PortingiOSLegacy/common/sources/UniXNU --firmware-root /mnt/d/Code/PortingiOSLegacy/common/sources/uefi-sheng --require-image-ready
```

最初在 Windows 直接跑补丁预处理检查缺 clang，已改用 WSL 成功，没有跳过。BootShim/打包沿用上一报告脚本；新输出名不得覆盖现存候选。

下一次先核对在旁按键能力、唯一 enuma 身份、匹配备份和回 fastboot 条件，再执行 A-002 范围内临时启动。先观察 Probe，再测厂商协议/UFS 只读，之后验证实际分配和 EBS。当前等待的是按键可用性，没有新增审批项。
