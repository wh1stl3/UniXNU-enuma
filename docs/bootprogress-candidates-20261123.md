# 同 donor boot-progress 候选（2026-11-23）

仅静态调查；未构建、未访问设备。donor 限 iPad7,1 / iPadOS 17.7.11 / 21H461；nuwa 不作为候选。sheng 本地参考为对象库，使用 `git show` / `git grep` 读提交而非使用其工作树。

| 仓 | 有无 | 渲染方式 | 代码量 | 前置 | 许可 |
|---|---|---|---|---|---|
| UniXNU/UniXNU-sheng | 有，`package/BootProgress.c:573-606` | 独立 CPU 写 XNU framebuffer；捕获 console 文本，不是 vc 字形渲染 | 主文件 1311 行 + 4 个头文件共 180 行；另需字体、hook、构建和可选探针 | XNU 映射、32bpp、几何、hook、`boot-progress` | 这 5 个文件各自 SPDX MIT；仓根 BSD-2-Clause-Patent |
| xVanTuring/UniXNU-pipa | 无屏幕 progress 页面；有同名持久日志 hooks | `package/BootRamoops.c:3-4,1351-1358` 明确无页面，stage 写 ramoops，bind/putc 不绘制 | 不是屏幕候选 | 板级 ramoops；不能照搬其重启寄存器逻辑 | 仓根 BSD-2-Clause-Patent，文件许可需单独审查 |
| xVanTuring/UniXNU-tb128fu | 有，`package/BootProgress.c` | sheng 派生的独立 framebuffer 页面 | 主文件约 1214 行，另 4 个同名头；完整依赖未统计 | 同 sheng，板级探针不同 | `BootProgress.c` SPDX MIT，根 BSD-2-Clause-Patent |
| reAAAq/UniXNU-umi | 未确认 | GitHub 默认分支递归树未见同名文件；未逐文件全文搜索 | 未知 | 未知 | 根 LICENSE BSD-2-Clause-Patent |

## sheng 机制和接入

来源：`UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e`，`package/BootProgress.c`、`BootProgress{Core,Display,Lifecycle,Pulse}.h`：各文件 SPDX MIT；`BootProgressDisplay.h:4-5` 的 `Font.h` 来自外部构建树，具体来源与许可尚需单独核对。仓根 `LICENSE` 为 BSD-2-Clause-Patent。21H461 profile 在 `board.toml` 的 `os_overrides.ipados-17.7.11-21H461`，配置 `boot-progress=2`、`build-boot-progress.py`；`configs/sheng_defconfig:16` 打开 CONFIG。

`BootProgressDisplay.h:13-19,24-56` 使用 `*(volatile uint32_t *)(frame + y*stride + x*4)` 和字形直接画；不是 IOSurface 渲染。`BootProgress.c:584-604` 校验已建立的内核虚拟映射、32 位、宽 720..4096、高 560..4096、stride 至少 4*w 且不超过 65536，比例在宽≥2160 且高≥1400 时为 3，否则 1；32bpp 本身不证明 enuma 像素通道顺序兼容。`BootProgress.c:606-625,1161-1183` 捕获字符和阶段，监控线程约每秒刷新；固定行显示启动阶段、历史、最近 console、进程/故障和存储等诊断，不是滚动 vc。`refresh` 在 `:516-538` 每 15 秒强制重画，`boot-progress=1` 在停滞/总时限会冻结，`=2` 连续运行（`:573-581,748-761`）；不是简单无副作用状态栏。

官方 UniXNU 基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241` 的 `patches/xnu/zzz-boot-progress.patch:66-88,104,119` 在启用时把 vc 字符转交 `boot_progress_putc` 并 return，映射完成后 bind；因此是保留日志**内容**并用自己的页面展示最近几行，不是原生滚动 vc 和固定摘要区并行。若两者各自写同一 framebuffer，会互相覆盖；分区必须修改 vc 可滚动边界并协调清屏、重绘、并发与显示交接，不能仅靠周期重画保证固定区。

后续 GUI 全屏 swap 也会覆盖：`BootProgress.c:550-569` 在 scanout 前让出；`:933-940` 的 crash banner 依据 swap/内容变化重画，存在覆盖窗口，非持久合成层。enuma 的 EnumaGOPFramebuffer/legacy 需确定其实际 mapping 生命周期与 swap 交接，不能照搬 sheng 板值。现阶段优先评估抽取 MIT `BootProgressDisplay.h` 的文本行绘制和状态收集，连接官方 XNU 17 hook，替换板级强依赖、配置 archive 与 `CONFIG_XNU_BOOT_PROGRESS`，按需启用 `boot-progress=2`；ADT 不见该绘制器直接要求新属性，但 framebuffer 的既有传递和有效映射必须先核实。整套移植为**大**：涉及启动 hook、ABI、锁/并发、生命周期和 GUI 接管，需 deep_reviewer；只抽取字体/行绘制并非现成完整接入，工作量仍为中，需验证字体许可与 framebuffer ownership。

## 其他候选和检索边界

* `xVanTuring/UniXNU-pipa@cdb3d62771e31d48d832853ee0c90964346d78da`，`board.toml` 指明同 donor；`package/BootRamoops.c:3-4,1351-1358`；仓根 BSD-2-Clause-Patent，文件许可另核。其 `CONFIG_XNU_BOOT_PROGRESS=y` 不代表屏幕页面。
* `xVanTuring/UniXNU-tb128fu@a9c3863dedbee6f319bff16d3b609ec6cef409bf`，`board.toml:11-19` 同 donor，`package/BootProgress.c:1` MIT，根 LICENSE BSD-2-Clause-Patent；同源大体量派生，板级依赖更多，未发现比上游 sheng 更小的完整实现。
* `reAAAq/UniXNU-umi@3eb72578597d2ca16471b172d45eddc096a34a04`，GitHub 递归文件树与 README 项目描述，根 LICENSE BSD-2-Clause-Patent；只检查文件名，不能断言不存在内嵌实现。

sheng 的公开分支通过 `git ls-remote --heads origin` 枚举，main 为上述 pin；本轮详细检查 main，没有逐一全文搜索所有分支，因此不声称其他分支没有更小实现。pipa 对本地 HEAD 全文 `git grep` 指定关键词；其未检出 submodule 不在搜索范围。tb128fu 读默认分支 board、renderer 和递归树；umi 仅枚举文件树。推荐 sheng 原版的**行绘制部分**作为进一步审查候选，非直接移植整套；同 donor 且上游优先，pipa 无页面、tb128fu 为大体量派生。尚未验证 enuma 运行效果。
