> 已由 [registration-v5新会话prompt](2026-10-27-oem-registration-v5-handoff-prompt.md) 取代。当前候选已接线、构建并资格完成，v4两组照片已确认；后文“不推送/未接线/旧待办”仅为历史背景，不作为当前操作指令。先读新prompt和STATUS/HANDOFF。

## 历史接续正文

当前更新（2026-10-27）：独立工作区OEM运行版已完成qualification-3，用户已授权补齐后部署，只差当前录像/人工恢复准备。先读本工作区docs/STATUS.md及operations/2026-10-27-oem-runtime-deployment.md；下方旧交接是历史背景。R027继续冻结，不推送，共享主线不改。

最新接续：Core追踪/板级适配器双FD已编出；先读本worktree docs/STATUS.md 和 docs/operations/2026-10-27-oem-core-trace-firmware.md。仍stage10停止、未上机。以下早期prompt仅供背景。

本worktree最新接续：先读 docs/STATUS.md 和 docs/operations/2026-10-27-oem-display-worktree.md。两组OEM stage10完整FD已构建，当前写入根为 D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display；原主线及R027保持不改。以下旧prompt保留为背景，不覆盖最新状态。

# 接续 enuma：定位 OEM DisplayDxe 未观察到返回的区间

继续现有成果，不从零重做。阶段目标是先取得可信、可归因、可观察的原厂驱动调用证据，再缩小 DisplayDxe 的可疑执行区间，最终推进正规显示初始化/GOP 与 UniXNU。临时 SimpleFb 菜单成功不等于原厂显示初始化成功，不伪造驱动成功返回。

## 先读与路径

工作根 D:/Code/PortingiOS/enuma；设备仓 D:/Code/PortingiOS/enuma/UniXNU-enuma；实际固件源码在设备仓 firmware 子模块。独立 D:/Code/PortingiOS/enuma/uefi-enuma 不是当前板级开发树的替代品。旧资料 D:/Code/PortingiOSLegacy 只读追溯。

先读 D:/Code/PortingiOS/PATH-MIGRATION.md、设备仓和 firmware/AGENTS.md、docs/STATUS.md、docs/HANDOFF.md、docs/NEED-REVIEW.md，以及以下设备仓相对路径：
- docs/operations/2026-10-26-oem-display-route-recheck.md
- docs/operations/2026-10-27-oem-service-trace.md
- docs/operations/2026-10-27-oem-trace-trust-validation.md
- docs/operations/2026-10-27-deferred-menu-firmware.md
- docs/operations/2026-10-26-uefi-console-menu-validation.md
- reports/enuma-oem-service-trace-development.json
- reports/enuma-oem-trace-trust-validation.json
- out/oem-service-trace-20261027/trust-check2/result.json

以实际最新文件和 git log/status 为准。先检查工作区，不 reset/clean/改权限、不启动第二写入者、不操作 nuwa。此次交接已授权本地提交，不代表自动推送或未来实机授权。

## 已知事实与证据界限

1. OEM DisplayDxe PE 位于 out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi，315392 字节，SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425；文件 GUID 4138022f-06c7-4f79-9c94-7e33b511a4e7。先复核再反汇编归因，GUID 本身不是 PE 认证。
2. 历史 S005 的调用前 point20 可返回；S006/007 调用后 point21/22 在观察窗内未见返回，均已恢复。只支持构造器/主入口调用区域需要进一步取证，不能直接认定死锁或某条指令卡住。EnableDisplayThread=0 不跳过构造器；FDReserved/调度器来源只是待验证假设，不能凭猜测补地址或成功 stub。
3. 当前组件 firmware/diagnostics/EnumaOemServiceTrace.h、EnumaOemServiceTraceView.h、EnumaOemTraceTarget.h 使用持久私有 SystemTable/BootServices，仅包装 LocateProtocol/HandleProtocol/AllocatePool。128 条 RAM 环形日志记录实际入场/返回、调用 ID、GUID、大小、调用者 RVA；不修改全局表，不改原状态或输出。高 TPL 仅用于日志临界区，调用原服务前恢复 TPL。上下文不能随 StartImage 返回释放。
4. 组件尚未接入 Core/profile/FV，未执行原厂 PE。只覆盖三项 Boot Services，不覆盖协议方法、MMIO、SMC、锁；SMP 未验收。宿主透明转发、嵌套、覆盖/耗尽、错误配对、部分输出失败等验证已通过：7 项 Python 测试，32 组序列×10 快照=320 对照，ASan/UBSan、C 到 Python 往返、AArch64 对象检查。不是 320 次实机。
5. 缺失返回仅称“本快照未观察到返回”；保留 pending、孤立返回、覆盖数、计数耗尽及捕获完整性。不得填补成功、把内层返回配给外层、把最后一条记录当真实卡死位置。解码器 deadlock_established=false。
6. R027 是 SimpleFb 真实返回 point13 后再启动菜单、菜单结果另记 point28 的独立候选；不代表 OEM 初始化/BDS/生产 GOP。冻结镜像 out/deferred-menu-20261027/qualification1/image.img，SHA256 0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a，未执行、未消费、paused-by-user。R022—R026 已消费不可复用。S054 完整 UniXNU 应用菜单照片已人工确认，但仍是私有有界显示路径。

## 下一轮优先落实的代码工作

A. 检查真实 CoreStartImage/调度路径如何传入 SystemTable，证明私有表确实到达同一调度句柄的目标 PE（仅改 LoadedImage 字段不当然证明入口参数已改变）。在独立默认关闭的开发 profile 中设计精确接线：目标 GUID、LoadedImage 来源、PE 摘要/打包目录、映像范围、生命周期和实际 StartImage 状态绑定。不要改变冻结 R027。
B. 同时解决异常时的取证出口。不能只在原服务返回后回放 RAM；若目标不返回，必须说明如何保留并观察调用前记录。选取已有已验证预算内的有界出口，检查重入、TPL、栈、输出失败、窗口所有权、停止记录及捕获中断；不得依赖正在排查的 OEM GOP/ConOut，也不能让日志输出再次调用被包装服务。不能解决时明确阻塞点，不把 RAM 存在当作已经取证。
C. 为接线和出口加入有区分力的失败验证：错句柄/错 PE、嵌套、原调用错误、拒绝输出/部分输出、环形覆盖、计数耗尽、异常或非局部退出、恢复后残留记录。保留现有透明转发判据。调用者 RVA 必须映射到本次精确 PE，区分 BL/BLR 后返回地址和调用点，不能猜减 4 后直接命名函数。
D. 结合精确 OEM 反汇编、构造器和现有依赖给出按证据排序的主假设、反证条件、下一观测能区分什么。优先实现能区分假设的代码，不重复固定字样点屏或仅黑屏/时间差实验。
E. 能独立完成的测试、构建、机器码审核、失败路径及来源绑定同轮做完。复现组件检查：在设备仓用 WSL python3 -B scripts/check_oem_service_trace.py --output out/<全新目录>。核对脚本实际参数及依赖；不覆盖 trust-check2/check3 或旧资格。新候选和报告另存，未运行项目写未运行。

## 授权与交接要求

实机仍暂停：不得 ADB/fastboot、重启、部署、申请录像或消耗 R027。未来恢复须用户明确恢复实机、本次精确单次放行及当前录像条件；旧准备文档已过期，另建绑定，不回写。身份、备份、恢复、硬停规则照旧；不改内存基址/大小或 verified。

保留冻结产物、媒体和历史证据原字节；不提交 OEM 二进制/备份/设备标识/out/影音，不推送远端。构建使用固定依赖；不能把干净提交与旧工作区快照资格等同。原始媒体只在本地，先独立判读保存并展示，用户确认后才做精确镜像归因。

开工简报说明接手结论和最小离线方案，之后实际推进。结束同步 STATUS/HANDOFF、WORKLOG/DECISIONS、NEED-REVIEW 与人工待办，明确已做/未做、证据路径、提交状态、下一卡点。不要把未观察到返回称为已确定死锁。
