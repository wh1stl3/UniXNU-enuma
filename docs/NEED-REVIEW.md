# NEED-REVIEW

四类硬停见 AGENTS.md。所有批准必须绑定本仓动作与具体输入；历史 enuma/nuwa 授权不视为新镜像或新配置的授权。

## R-001 · 第一阶段 DarwinBoot owned-memory 预算

状态：approved，2026-10-22；用户明确批准推荐方案 A（512 MiB），已写入 board.toml。

批准原文：“先按推荐配置 512 MiB，批准 R-001，继续离线适配。后续根据实际 UEFI 内存图再调整，生成或启动镜像前另行确认。”仅执行下述最小范围，其他内存值/基址变更仍需新的确认。

背景：固件源码接线和 SM8250 支持核心已可检查，下一阶段要把 enuma ADT 与 DarwinBoot 的内存请求约定接通。该值是 loader 请求的连续窗口大小，不是 enuma 总内存、可用内存结论或固定物理地址。修改 board.toml 内存字段触发 AGENTS.md 硬停第 1 类。

固定 UniXNU 75bc13dd 中 DarwinBootPkg/Driver/WindowSize.h:6 接受 256 MiB～8 GiB，2 MiB 对齐；DarwinBoot.c:392 的 AllocateWindow 从实际 UEFI EfiConventionalMemory 图选择窗口并调用 AllocatePages，失败返回错误。未指定时默认 256 MiB。相关源文件哈希已锁定。旧 Android FDT/iomem 不能保证未来 UEFI 连续窗口。

候选：

| 方案 | 请求值 | 收益与代价 |
| --- | --- | --- |
| A（推荐） | 512 MiB / 0x20000000 | 用于第一阶段内核入口和诊断的明确预算；相比 1 GiB 对连续窗口要求较低。仍可能分配失败，也不承诺能启动完整 iPadOS 用户态 |
| B | 1 GiB / 0x40000000 | 给后续内核/ramdisk 更多预算；对连续可用内存的要求更高，当前缺 UEFI map 证明 |
| C | 暂缓配置 | 保留 example 和默认行为，先等待 UEFI 内存图；不能把默认 256 MiB 当成已审查的 enuma 运行预算 |

推荐 A 是第一阶段工程预算，不是测量结果；后续根据真实 UEFI map 和 payload 尺寸另行审查。

最小批准范围：只在本仓 board.toml 的 [payload.adt] 新增 `owned_memory_size = "0x20000000"`，同步配置检查和交接文档。若选择 B 则只改为对应值。保持 example=true，不写 dram_base/dram_size、FD/栈/显示基址，不设置任何 *_verified=true。

本次批准不包含新建/重写诊断或固件镜像、fastboot boot/flash/erase、改变设备或发布远端。固件内存图、GOP、厂商驱动闭包和打包参数仍是独立未闭合输入；镜像构建待具备具体方案后另列审查。

## A-002 · 后续生成和测试授权

状态：approved，2026-10-22。用户明确“生成镜像无需确认”，随后表示“这个设备日常不需要用 可以随意推送镜像 只要能恢复回fastboot就行”。新增授权取代 R-001 中生成/启动需逐次确认的限制；可恢复的镜像推送/启动按此授权推进。执行前须确认 enuma、备份和恢复 fastboot 条件；不是无恢复保障破坏关键引导链的授权。用户已接入解锁且 root 的 enuma，本轮先做只读采集。

2026-10-22 后续：用户暂时不能配合恢复按键，要求先离线；已生成 Probe 01 候选，未操作设备。无新增待批准项；未更改 board.toml 内存字段或 *_verified 标记。等待按键可用性，不重复申请 A-002。

2026-10-22 首次实机：用户“可以开始实机推送了”后在 A-002 内完成一次临时启动。黑屏后已恢复 Android；没有 flash/erase/改槽、内存字段修改或 *_verified=true。无新增审批项，见 D-016 与首次实机报告。
