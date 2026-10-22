# enuma 本机平台配置、原厂驱动和 v3 固件候选

2026-10-22（Asia/Shanghai）。用户允许生成镜像，并允许以能恢复fastboot为前提推送和进行可恢复启动测试；A-002 supersedes早先逐次确认的限制。R-001的512 MiB请求保持。此里程碑完成Android只读采集、平台配置、完整固件构建及打包；没有重启、flash、erase、改槽或启动新镜像。

## 本机输入

设备明确选择 ro.product.device=enuma，Android指纹为 Xiaomi/enuma/enuma:13/TKQ1.221114.001/V816.0.3.0.TKZCNXM:user/release-keys。BL锁值0、verifiedbootstate=orange、root uid0、sys.boot_completed=1。序列号只在忽略目录本地目标文件中保存，不进入报告或Git。

当前FDT SHA256为643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62，与历史941691字节备份相同。实际触控绑定为NVT-ts。DRM报告1600×2560的120/60/30Hz模式；没有fb0，通用debugfs DRM state路径也不存在，因此没有把Android framebuffer地址或格式当成已知量。

只读采集本机xbl_a、xbl_config_a、abl_a至out/device，分别锁定摘要。当前boot_a与已有magisk-patched备份摘要8f40f0c9一致，vendor_boot_a与历史备份摘要3da202d0一致。详细尺寸/摘要见reports/enuma-live-capture.json和reports/enuma-platform-observations.json。所有原始镜像、FDT、日志和厂商二进制均留在忽略目录。

## 平台内存与GOP

使用uefi_firmware 1.16解析本机XBL（SHA256 7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057），校验FV头校验和及边界，取得真实uefiplat.cfg与K81面板资源。

从原厂配置生成45个内存/MMIO区域及31项数值配置。DDR基址0x80000000得到FDT支持；FD=0x9fc00000/0x300000、栈=0x9ff90000/0x40000、DXE Heap等来自本机XBL。虽然部分数值与alioth一致，这次来源是本机，不以相似设备配置替代证据。原厂EnableUfsIOC=0保留；alioth候选为1，不能覆盖。无法表达为UINT64的字符串配置名在报告中列出，原始文本不公开分发。

原厂Display Reserved=0x9c000000/0x2400000；当前FDT将其拆成35 MiB cont_splash和1 MiB DFPS。GOP选择原厂DisplayDxe+CPRDxe及两份K81面板XML，不使用SimpleFb。面板单链路宽800、双控制器、链路24bpp；原厂XML与Android模式均给出总宽1600、高2560。GOP的像素格式、stride与实际framebuffer地址仍需运行时观察。

SEC原实现会在DEBUG启动时清空整个显示保留区。新增按enuma开关跳过清空的补丁，并保留Kona跳过MDP SMMU detach的补丁。早期SerialPortLib使用Null，避免在GOP建立前用猜测格式写屏。两个分支均经真实预处理器检查。

这些配置描述原厂固件布局；自制固件重入后的GetMemoryMap、RAM Partition协议和生命周期仍需实测。不能据此宣称已存在可分配的512 MiB连续窗口。board.toml的总DRAM和物理基址没有新增。

## 原厂依赖与完整构建

提取33个AArch64 PE驱动，包括Env/SMEM、DAL/HWIO、时钟/电源/PMIC、SCM/TZ、DDRInfo、UFS、SPI以及Display/CPR。保留原PE、缺省或显式DEPEX和原APRIORI相对顺序，生成二进制INF与DSC/FDF输入。没有将缺失DEPEX伪造为TRUE，也没有使用alioth/nabu的二进制。

补齐Mu架构协议、变量、时钟、watchdog、安全stub、磁盘/分区和控制台模块。增加DXE_RUNTIME_DRIVER.BINARY打包规则，使原厂runtime PE子系统和依赖表达式完整保留。静态引用/构建成功不证明这些闭源驱动运行时ABI和协议安装顺序正确。

使用固定uefi-sheng和Mu_Basecore归档，在out/firmware-build建立独立可写工作区。Common/Mu与Mu_OEM_Sample只读引用且gitlink与底座一致。归档URL/SHA256、依赖提交固定于config/firmware-build.lock.json。BaseTools在自己的目录编译，未写参考仓。

首次平台解析缺libspdm头文件，补充固定嵌套依赖后继续；随后缺runtime二进制FDF规则，新增规则后完整构建通过。产物复核又发现git在嵌套目录静默跳过GIC补丁，现已让每个patch工作区单独初始化Git并检查补丁实际内容，重新构建。前一候选仅留作历史记录，不用于设备实验。构建中保留了上游HwResetSystemLib类声明警告及make时钟偏差警告，完整链接是否成功以报告退出码及FD审计为准。

最终FD应为3 MiB；实际摘要/退出码见reports/enuma-firmware-build.json。scripts/audit_enuma_fd.py检查最终FD中的33个原厂PE和DEPEX与输入逐字节一致，确认UniXNU、UniXNUDxe、DarwinBoot及原厂显示模块入卷，且未夹带SimpleFb。

## 启动打包

当前boot与vendor_boot都为v3，vendor_boot带DTB，boot分区192 MiB。固定版本UniXNU通用bootimg.py仍按gzip+追加DTB以及旧头字段进行打包校验，不能直接用于本板v3。新入口复用固定AOSP 028bdc06的mkbootimg/unpack_bootimg，明确raw ARM64 BootShim+FD、不追加DTB、不重写vendor_boot。BootShim编译及头部检查复用固定UniXNU实现。

包内ramdisk为空，本候选用于首先验证固件入口/GOP和协议，未附带XNU、ADT或iPadOS用户态。它不代表iPadOS已具备启动条件。镜像头、尺寸、内核/ramdisk字节、对齐、错误版本、损坏/越界和追加数据拒绝检查通过，实际候选另经官方unpack工具逐字节回读。最新路径/摘要见reports/enuma-boot-candidate.json，硬件状态保持待测。

## 复现入口

```powershell
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/collect_enuma_platform.py
wsl -d Ubuntu-22.04 -- python3 -m venv /mnt/d/Code/UniXNU-enuma/out/firmware-tools
wsl -d Ubuntu-22.04 -- /mnt/d/Code/UniXNU-enuma/out/firmware-tools/bin/pip install -r /mnt/d/Code/UniXNU-enuma/config/firmware-tools-requirements.txt
wsl -d Ubuntu-22.04 -- /mnt/d/Code/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/UniXNU-enuma/scripts/extract_enuma_xbl.py
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/prepare_enuma_platform.py
wsl -d Ubuntu-22.04 -- python3 -B /mnt/d/Code/UniXNU-enuma/scripts/build_enuma_firmware.py --reference /mnt/d/Code/PortingiOS/common/sources/mu-nuwa-firmware --unixnu /mnt/d/Code/PortingiOS/common/sources/UniXNU
wsl -d Ubuntu-22.04 -- /mnt/d/Code/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/UniXNU-enuma/scripts/audit_enuma_fd.py
wsl -d Ubuntu-22.04 -- /mnt/d/Code/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/UniXNU-enuma/scripts/prepare_enuma_boot_payload.py --unixnu /mnt/d/Code/PortingiOS/common/sources/UniXNU
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/package_enuma_boot.py --kernel out/boot-candidate/enuma-uefi.raw --ramdisk out/boot-candidate/empty-ramdisk --output out/boot-candidate/enuma-new-run-boot-v3.img
```

打包拒绝覆盖已有镜像，后续每次使用新的输出名。采集也拒绝用不同内容覆盖既有原厂二进制，设备固件变化时须保留新快照并审查来源锁。镜像只在out/生成，Git仅提交配置、代码、摘要和脱敏报告。

## 必须依赖实机的项目

| 项目 | 当前已有证据 | 必须实测的内容 |
| --- | --- | --- |
| BootShim/ABL入口 | 原厂v3布局，shim头部与打包往返检查 | ABL是否接受raw候选、入口EL/MMU/cache与FD跳转 |
| UEFI内存 | 本机原厂配置、Android FDT/iomem、512 MiB主机模型 | 自制UEFI GetMemoryMap、保留区生命周期和实际连续分配 |
| GOP/面板 | 当前1600×2560模式、原厂DisplayDxe与K81 XML | 驱动成功初始化，真实base/stride/格式，ExitBootServices后显示保持 |
| 厂商协议 | 33个原始PE/DEPEX及相对顺序，完整链接 | Env/SCM/Clock/PMIC/RAM Partition协议ABI、调度和失败路径 |
| UFS | 本机UFSDxe和Kona事实、主机边界检查 | PHY/SMMU/时钟状态、LUN/sector、已知数据只读比对 |
| 恢复 | 当前BL解锁/root、匹配备份，原厂ABL/XBL未改 | 实验后的USB状态、硬件按键回fastboot、恢复Android并boot_completed=1 |
| XNU与交互 | 固定iPadOS donor和平台支持代码 | 内核入口、中断/定时器、多核、NT36523输入及真实用户态 |

本里程碑不把Android只读采集或完整固件构建当成自制UEFI/XNU实机通过。下一阶段可在A-002授权范围进行可恢复的临时启动，先核对enuma和恢复条件，再收集第一份实际UEFI/GOP证据。
