# 交接：继续离线storage/PMGR/RamBlock集成

2026-10-27。用户明确OEM候选继续保留等待，继续离线内核/用户态/桌面开发；暂不上机、不推送。使用D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display，原共享主线只读。R027及OEM镜像17d0169e6bd1…冻结，未boot或消费ledger。

前轮已完成：生产RootWindowRead与EnumaUfsRead桥接、ARM64 Mach-O archive、失败返回与校验测试；真实目录型APFS Data seed；带Data的96MiB FAT及真实DarwinBoot解析验证。新证据out/kernel-userland-20261027-2；明细及摘要见[专项](operations/2026-10-27-root-data-offline.md)和reports/enuma-root-data-offline.json。

本轮新增EnumaRamDisk易失Data后端及iOS17 ARM64归档f9f357d0…；完整512MiB读回、23处实际导入分配失败、预算/短写/并发停止验证通过。详见[后端集成边界](operations/2026-10-27-volatile-data-backend.md)，证据out/kernel-userland-20261027-3/ram2。下一节点为匹配的XNU生成头/编译记录、storage/PMGR ABI及真实IOKit服务接线。

内核仍是前轮30组件e879b2f0…，新archive没有接入XNU；没有IOKit/MMIO、实际Data挂载或桌面结果。下一步补UFS stream/排他/队列生命周期、同donor PMGR ABI、IOKit初始化与归档、RamBlock及Root/Owner/Data策略，再接显示/HID和用户态。不能把结构验证或原始Apple图形组件当成硬件驱动。

Linux APFS路线已实际验证，取代“必须等待Mac才能构造Data”的宽泛阻塞；seed只取参考目录，不取SetupDone/ForceNoBuddy等偏好。512MiB仅离线文件系统容量，新UUID只在产物报告，没有写board或内存字段。

复现须用专项脚本并指定新out目录；旧bridge1编译失败和bridge2通过证据都保留。每项遵守[官网具体方法](operations/official-adaptation-rules.md)，区分实现/集成/运行。状态以STATUS为准，下一轮仍无设备授权恢复。
