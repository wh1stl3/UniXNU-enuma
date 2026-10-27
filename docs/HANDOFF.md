# OEM progress-v2 实测结果（2026-10-27）

一次临时启动已消费，75秒观察内未见合格fastboot返回，已停止追加启动。用户人工恢复Android后，独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a摘要均通过。当前设备恢复完成；不能原样重试本镜像。

候选SHA256：adbb2c41216bc0c934af4046fe8c0127ce40a6c22c12bfc3f2c7880eee80679f。源码设备仓61eacd1、固件3adfb77；首次连接失败的前检未启动，重新连接后仅一次实际boot。单次ledger保留consumed，R027及旧OEM候选冻结。

两张本地照片独立判读：E01/C0/Q0与S02/C0/Q1，均为返回RVA 0x3abc、session 0x1c2e8da897800e00；S02状态0（EFI_SUCCESS）。精确原厂PE在0x3ab8执行BLR x8，前序从表偏移0x40取函数，对应AllocatePool。0x3a8c前序不是调用，与照片B字形也不符。无符号，不能断言上层调用函数名称或分配用途。

主判断：首个AllocatePool已经成功返回，优先缩小S02取证清理至后续OEM执行之间的区间。S02可见发生在等待/恢复完成之前，因此清理/复位失败仍是第一组待排除项；其次是后续服务或未包装协议/MMIO执行，另有后段显示出口因路由变化被拒绝的可能。两张静态照片不能证明E03/S04/S05从未发生，不能判定SID死锁或完整驱动返回，更未验证GOP/BDS/XNU。此排序是下一步诊断优先级，不是故障概率结论。

下一软件方案：以独立有界探针观察后续选定服务调用入口/返回，并区分取证清理与OEM继续执行；不先套用MMU补丁。新镜像须重新构建/失败路径/机器码/单次绑定审核，不沿用本次ledger或在场状态。原始媒体仅本地，文字判读待用户核对。

证据：reports/enuma-oem-progress-trial-20261027.json；out/oem-progress-20261027/media-review/（转录、解码、精确PE RVA映射）；out/device-tests/oem-b78f01e4-35ff-4113-890d-251a1d51d106/（transport、超时快照、恢复核验）。媒体位于D:/Code/PortingiOS/enuma/Media-enuma/OEM-progress-v2-20261027-b78f01e4。只收到stage1.jpg和stage2.jpg，未收到连续录像。

以下内核输入及集成交接仍有效：

# 交接：从已验收真实输入继续 storage/PMGR 服务集成

2026-10-27。用户允许推送；本次progress-v2已消费且人工恢复，停止追加实机。R027冻结，旧OEM候选17d0169e6bd1继续保留。共享D:/Code/PortingiOS/enuma/UniXNU-enuma只读。

1. 主开发树D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display保留完整离线历史。最小CI树D:/Code/PortingiOS/enuma/worktrees/enuma-xnu-input-ci，分支ci/enuma-driver-inputs-20261027已推送，最新文档e81f73c；远端main未变。
2. 最终平台运行40478893674成功，代码cdfb7ae；原始包在CI树out/ci-runs/40478893674/enuma-macos-platform-40478893674，验收副本在同级imported。2259文件/2记录绑定通过，manifest和内核摘要见reports/enuma-driver-input-ci.json。不要重用上传缺失的40477385983，也不要覆盖旧失败证据。
3. 已取得真实IOPMGR/IOService及生成头/命令；下一步仍须IOKit/storage接口和同donor私有ABI。IOKitUser下同名头不能替代。随后接入现有RootRead/RamDisk的provider、start/stop、注册及归档链接，验证失败生命周期。
4. 新平台内核be17abfc…未做donor预链接或设备启动，旧e879b2f0实验内核及静态PMGR结果不自动转移。没有用户态或桌面运行证据。
5. 32项宿主测试通过，最终真实包导入通过；详细失败/修复链见operations/2026-10-27-driver-input-import-ci.md及CI分支同名文档。按官网具体规则继续；内存/verified/分区门禁不变。

2026-10-27代码归因更新：用户已确认E01/S02判读。宿主ASan/UBSan复现私有SystemTable配置表指针/数量陈旧缺陷；这是当前最强代码缺陷证据，尚未证实为本次根因。已核对首分配后的构造链与实际Core返回/清理指令，下一验证先隔离追踪器并覆盖call1/2及Kernel协议，暂不跳到SID/MMU补丁。详见operations/2026-10-27-oem-post-s02-analysis.md。新候选未生成，本轮无追加实机；7d74ce9文字取证已推送oem-progress-20261027。
