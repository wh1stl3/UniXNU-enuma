# 当前：根卷读取桥接与真实Data载荷完成离线验证，OEM继续等待

2026-10-27。仅独立worktrees/enuma-oem-display可写；共享主线不改，R027冻结，不上机、不推送。按AGENTS引用的官网具体适配规则推进。

## 本轮增量

- EnumaRootRead复用固定生产RootWindowRead，接EnumaUfsRead；支持512字节请求到4KiB读转换、同锁校验/复制及真实部分完成。ARM64 Mach-O静态库18f609c4…已生成，尚未链接XNU或接IOKit/MMIO。
- Linux固定参考生成真实可丢弃APFS Data：逻辑512MiB，54个目录，packed 86128字节，SHA256 8a4483bcc910875cbae2cc2ee1090abced93ea8297ef4c346a263ca42a9c5385。apfsck、目录权限/对象校验和回读、解包逐字节一致；没有SetupDone或身份文件。该容量仅主机文件系统大小，不修改板级内存或设备分区。
- 带Data的96MiB FAT：out/kernel-userland-20261027-2/payload-data/payload/payload.img，SHA256 4a9c77df42ef50664618d62be4564bc7056f5de5f4612a35adaecd00e3a69d49。scratch-data、initrd和PackedRAMDisk已接通；真实DarwinBoot ADT/trust解析及截断负测通过。没有EBS或设备执行结论。
- sanitizer覆盖8种对齐、3处传输失败、65处校验失败、短复制及边界；139组packed格式差分和5项CLI拒绝通过。bridge1失败保留，bridge2完成。

## 保留的基础产物

原30组件实验内核e879b2f03f995107ad5b10ea21f48430894cbbf31ead1b62143256e07a7f9e59未重链接。原OS/SystemOS根卷文件fd43ee7035ce185ce4215ac93fdc006fd784a54b3b7442e21457c226cbe03093保留；9.38GB主机组件文件不等于设备分区。正式依赖锁未升级。

## 剩余集成与下一步

实际UFS stream归属、控制器/队列隔离、PMGR ABI、IOKit注册与初始化/XNU归档、Root/Owner/Data UUID策略、RamBlock服务仍未闭环。新Data已经构造，但尚未被目标OS挂载；CPU framebuffer/IOSurface、NT36523 HID、launchd/backboardd/SpringBoard无新运行结论。不能将带Data FAT称为可用桌面或已资格上机镜像。

优先继续真实storage/PMGR/RamBlock服务闭包；独立离线开发继续，硬件缺口保持未知。依据固定umi/fajita/sheng实现逐项核对，不继承其他机型参数或验收结论。

## 冻结候选

OEM out/oem-runtime-qualification-20261027-3/image.img摘要复核仍为17d0169e6bd1447b358d1e91c6af9a8bf6ed368c6c44fea591fa73b970b82f08，用户明确继续等待，未boot、未消费ledger。最后设备只读记录为此前Android/A槽/root，不视为当前在线断言。

详见[本轮实现及复现](operations/2026-10-27-root-data-offline.md)、[前轮基础](operations/2026-10-27-kernel-userland-offline.md)、[执行规则](operations/official-adaptation-rules.md)。总报告reports/enuma-root-data-offline.json；仅本地提交，无推送。
