当前增量：输入包导入及28项合成宿主测试通过；已授权独立CI分支推送，待真实macOS构建。详见operations/2026-10-27-driver-input-import-ci.md。

# 交接：继续离线storage/PMGR/RamBlock集成

2026-10-27。用户明确OEM候选继续保留等待，继续离线内核/用户态/桌面开发；暂不上机；用户现已允许独立CI分支推送。使用D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display，原共享主线只读。R027及OEM镜像17d0169e6bd1…冻结，未boot或消费ledger。

前轮已完成：生产RootWindowRead与EnumaUfsRead桥接、ARM64 Mach-O archive、失败返回与校验测试；真实目录型APFS Data seed；带Data的96MiB FAT及真实DarwinBoot解析验证。新证据out/kernel-userland-20261027-2；明细及摘要见[专项](operations/2026-10-27-root-data-offline.md)和reports/enuma-root-data-offline.json。

上轮新增EnumaRamDisk易失Data后端及iOS17 ARM64归档f9f357d0…；完整512MiB读回、23处实际导入分配失败、预算/短写/并发停止验证通过。详见[后端集成边界](operations/2026-10-27-volatile-data-backend.md)，证据out/kernel-userland-20261027-3/ram2。下一节点为匹配的XNU生成头/编译记录、storage/PMGR ABI及真实IOKit服务接线。

本轮确认CI未留实际编译记录/生成头，已接入driver_inputs导出与14项负测；尚未运行macOS构建取得包。当前候选PMGR静态契约及3项篡改拒绝通过，参考地址需+2MiB，不能直接复用。见[输入与ABI依赖](operations/2026-10-27-driver-inputs-pmgr.md)，证据kernel-userland-20261027-4/pmgr4。下一步仍须真实匹配编译输入及运行期ABI，不能将静态结果填live_native_4k。

内核仍是前轮30组件e879b2f0…，新archive没有接入XNU；没有IOKit/MMIO、实际Data挂载或桌面结果。下一步补UFS stream/排他/队列生命周期、同donor PMGR ABI、IOKit初始化与归档、RamBlock及Root/Owner/Data策略，再接显示/HID和用户态。不能把结构验证或原始Apple图形组件当成硬件驱动。

Linux APFS路线已实际验证，取代“必须等待Mac才能构造Data”的宽泛阻塞；seed只取参考目录，不取SetupDone/ForceNoBuddy等偏好。512MiB仅离线文件系统容量，新UUID只在产物报告，没有写board或内存字段。

复现须用专项脚本并指定新out目录；旧bridge1编译失败和bridge2通过证据都保留。每项遵守[官网具体方法](operations/official-adaptation-rules.md)，区分实现/集成/运行。状态以STATUS为准，下一轮仍无设备授权恢复。
