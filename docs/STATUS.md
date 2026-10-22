# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相；历史见WORKLOG。

## 当前结论

**enuma平台配置、原厂驱动接入及完整UEFI构建已完成，已生成首阶段boot v3候选；尚未启动候选或运行XNU。** 目标保持iPadOS 17.7.11 / 21H461、iPad7,1 / j120ap、XNU 10063.141.1、4 KiB。R-001的owned-memory请求仍为512 MiB。

## 已完成

- 本轮只读确认当前设备为enuma，BL解锁、root uid0、Android boot_completed=1。当前FDT与历史摘要完全一致，触控绑定NVT-ts，DRM为1600×2560的120/60/30Hz模式。
- 从本机XBL生成45项内存/MMIO区域及31项数值配置，提供MemoryMapLib、ConfigurationMapLib、DDR/栈/FD配置。保留本机EnableUfsIOC=0，未加入board.toml总DRAM/物理基址。
- 提取33个AArch64原厂驱动与原始DEPEX/APRIORI、K81面板资源；GOP选择本机DisplayDxe/CPRDxe。跳过SEC清空含DFPS的显示保留区，早期SerialPortLib使用Null，Kona保留显示SMMU映射。
- 独立工作区内BaseTools与完整enuma UEFI构建通过；补齐架构协议/变量/磁盘/控制台以及runtime二进制打包规则。复核发现并修复GIC补丁根目录问题后重新构建成功。
- 最终3 MiB FD经解析确认：33个原厂PE和DEPEX逐字节一致，UniXNU、UniXNUDxe、DarwinBoot已入卷；未使用SimpleFb。源码/补丁图检查、8项反向测试、6项v3打包测试通过。
- 192字节参考BootShim+FD使用固定AOSP工具打为raw Android boot v3，官方unpack逐字节回读通过，保留原厂vendor_boot。候选不带XNU/ADT/iPadOS payload，先用于固件入口实验。
- 首轮donor摘要、4 KiB配置、GENI/UFS支持核心与512 MiB真实DarwinBoot主机检查继续有效；不等于实机驱动结果。

## 当前唯一候选

- 路径：`out/boot-candidate/enuma-uefi-gic-boot-v3.img`
- 大小：3153920 bytes；SHA256：`2c9d14dcdff12a00fb7bf606249a944a60f4b311d6c50905a3bc3725ea76e423`。
- 前一份enuma-uefi-boot-v3.img遗漏GIC补丁，仅留历史记录，不用于设备测试。
- 构建与内容审计：reports/enuma-firmware-build.json、reports/enuma-fd-audit.json、reports/enuma-boot-candidate.json。

## 下一步与必须实机确认的内容

1. 在A-002授权范围，核对enuma身份和回fastboot条件后，进行首次可恢复的临时启动，观察ABL/BootShim/UEFI入口。
2. 获取自制UEFI的GetMemoryMap、RAM Partition协议、实际512 MiB连续分配；Android内存图只能提供旁证。
3. 确认原厂DisplayDxe初始化、真实GOP base/stride/format及ExitBootServices后的显示；验证Env/SCM/Clock/PMIC依赖调度、UFS只读和复位。
4. 之后再接XNU/ADT/预链接与iPadOS payload，验证中断、定时器、多核、NT36523和用户态。当前GENI板级核心尚未注册IOKit，SM8550 NativeUfs分支继续关闭。

完整实机待测表与复现命令见[本机平台固件报告](operations/2026-10-22-native-platform-firmware.md)。

## 授权与限制

- A-002已授权生成镜像及可恢复推送/启动，以能恢复fastboot为前提；不重复请求同范围确认。本轮只做Android读取，未重启、flash、erase、改槽或临时启动。
- 固件构建通过与Android采集不等于自制UEFI/QEMU/XNU/iPadOS实机通过；未设置任何*_verified=true。
- 原厂模块来自本机XBL，未独立校验厂商签名或与官方ROM逐字节匹配。原始镜像/二进制/序列号均在忽略目录。
- board.toml仍为example=true。完整固件走独立脚本，通用UniXNU旧打包入口不直接用于本板。源仓只读，全部构建输出在本仓out/，仅本地main提交，未推送远端。
