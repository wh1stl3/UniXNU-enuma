# enuma 独立摘要渲染器接入设计（2026-11-23）

状态：仅静态审查；未构建、未访问设备。范围仅设计，不改变默认 recipe、冻结的 GOP 包或启动路径。

## 来源与许可

首选可作为**实现参考**：`UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e:package/BootProgressDisplay.h`，文件首行原文 `// SPDX-License-Identifier: MIT`。仓根 LICENSE 为 BSD-2-Clause-Patent；字体单独核实。`git ls-remote --heads ... main` 实测 main 指向上述 commit。GitHub commits API 对该 pin 和该路径返回最后修改提交 `fb2d4ed7ae02aa3fb53688c3d70bfaefd5c1b8f5`，author bluseliu50，2026-10-19 10:48:38Z，主题 `Initial import`，等价于路径限定的 `git log -1` 信息；本轮没有本地 sheng 检出，**未运行 git log**。

不是 macOS 专线：该 pin 的 `board.toml` 默认 profile 是 iPadOS 27，但 `[os_overrides.ipados-17.7.11-21H461.kernel]` 明确选择 `build-boot-progress.py`、`sheng_defconfig`，同名 payload override 明确 `boot-progress=2`。即同 donor 的 iPadOS 17 配置引用本实现，并非证明该 pin 在该 profile 实机运行。候选来源与对照见 `docs/bootprogress-candidates-20261123.md`；不需要切换 tb128fu。

## 上游实现：具体机制

以下行号均指上述 sheng pin，官方补丁指基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。

* **映射**：官方 `patches/xnu/zzz-boot-progress.patch:84-88,99-104` 在 XNU 建立/更新 console mapping 后把 `vinfo.v_baseaddr, v_width, v_height, v_rowbytes, v_depth` 传入 `boot_progress_bind`；不是通过 IOMobileFramebuffer 取得句柄。`package/BootProgress.c:584-605` 要求高地址 kernel VA、depth 32、宽 720..4096、高 560..4096、`rb >= w*4 && rb <= 65536` 和地址加 `h*rb` 不溢出；以 `h*rb` 推算边界，并未传入/独立证明 mapping 长度。32bpp 不能证明通道次序。
* **绘制**：`package/BootProgressDisplay.h:4-5` 的 `font[] = GLYPH_FONT` 来自外部 `Font.h`；它不是内嵌于该头的可独立许可字模，来源/许可待核。`:24-55` 对 ASCII 32..126 解码每字 5×12 位图、使用 6×14 单元及空白边缘，写 `frame + y*stride + x*4` 的 32 位像素，scale 为 1 或 3（`BootProgress.c:592`）。`:28-45` 对比上一行文字和颜色，仅改变化单元；颜色变化重绘行；`:13-20` 清全屏。减少重写不是双缓冲或无撕裂保证。
* **刷新和 vc**：`BootProgress.c:516-538` 拍状态快照，不持 recorder 锁画像素，每 15 秒失效颜色缓存强制重绘；`:606-625` 初期字符/阶段触发绘制；`:1161-1183` monitor 约一秒刷新。官方补丁 `video_console.c` 的 `vcputc_options` 在 active 时调用 `boot_progress_putc(c); return`，`serial_console.c` / `pe_kprintf.c` 也有重定向：捕获日志内容并显示自己的页面，而**不是**与原生滚动 vc 分区共存。`boot-progress=1` 会按 stall/limit 冻结，`=2` 持续运行（`BootProgress.c:573-581,748-761`）；不适合原样直接接入。
* **交接**：`BootProgress.c:550-569` 的 `boot_progress_prepare_scanout()` 请求 writer 停止，获取 render/pulse 排他后置 `display.bound=0`、关闭 pulse，失败返回 0；由受控 scanout 路径调用，不是 kernel 自动完成的通用所有权协议。`:516-525` 可选 `boot-diag-resume` 会在超时后重新绑定/清屏，`:933-940` crash banner 也可能重绘。全屏 GUI swap 可覆盖；这里没有通用的线程销毁/映射 teardown 证明，不能假设交接后不会重入。

## enuma 当前事实与数据

`docs/enuma-gop-r5-device-observation.md` 记录 `EnumaGOPFramebuffer` 是 legacy 的 `IOPlatformDevice` provider；r5 的 start 进入但未观察到有效 swap、像素输出；屏幕文字为 vc。该结论不建立独立渲染器和 legacy mapping 相同、并发安全或交接已完成。该 GOP 线冻结。

* `package/EnumaMatchCount2.inc:9-17,56-65,86-112` 有静态原子计数与 `enuma-mt:` 报告；`all/other/bb/sb` 可复用现有快照语义，但 bb(34)/sb(5) 仅固定 PID 桶，不证明进程身份。
* `package/EnumaFixupReport.inc:3-18` 的静态 `enuma_fx_bits` 与 `cs_text_fixup_parsed/applied` 在各自编译单元中，按既有 acquire/relaxed 顺序读；不能直接从另一编译单元引用 static。
* 工作树未跟踪的 `package/EnumaProcExecReport.inc:24-27,46-95,135-173` 是 r45 候选，不是已交付基线：`enuma-ps` 在单次 dump 临时枚举进程，`enuma-ex` 计数与 last 使用既有 spin lock。`ps` 的 `total/kept` 是栈局部值；不能假定存在持久可读计数，也不能声称 r44 包含该候选。
* 这些是隔离探针编译单元，不保证同时链接或导出；缺少相应探针时显示 `n/a`，不得用 0 冒充。读取现有计数不新增事件采集；把既有一次性快照暴露出来仍需明确发布及同步设计。

## 最小候选设计（尚未实现）

1. 独立 opt-in `enuma-diag-overlay=1`，缺省不建立线程、不改变 console 几何或写 framebuffer。仅诊断候选设置 boot-arg；不新增 ADT 属性，不改默认 `board.toml`。不要复用 upstream `boot-progress=2`，以免接入其重定向和冻结语义。
2. 在 XNU console 的现有 vinfo 映射完成点绑定，严格核对映射实际长度、rowbytes、深度、通道格式和坐标溢出；不另外映射硬件。先静态查清 console 的行高、初始化/clear/scroll 所有路径，再在 **vc 内部**以行高对齐地将底部 10 个摘要文本行的像素带排除出 vc 的可写矩形，vc 的行数和所有滚动、清屏、重绘的边界一并缩小；光减行数不足以证明安全。高度不足、像素格式未知、映射不可信、无法证明全部路径受限时拒绝启用并保持原 vc。此方案保持 vc 正常打印，不截获其字符；不能用“周期性盖回去”代替隔离。
3. 在已有探针的原编译单元提供**只读快照接口**，以原子/原锁拷贝到固定摘要结构后释放锁，再格式化及绘制；避免在锁内绘图或读取外部 static。首版固定 8 行：标题/有效性；mt 全局、other、bb、sb 四行；fx parsed/applied、bitmap 两行；ex ok/fail 一行。若 ps/ex 未编入，行显示 `n/a`；如确需 ps 数量，仅复用已执行的单次 dump 快照并设计发布，不做新的 proc 枚举。不得更改已有采集次数、锁与顺序来伪造可用性。`enuma-ex` 未被当前 r44 证实可用，按候选处理。
4. 单个低频工作线程每秒取快照、比较文本，只更新变化的字格；失效或重绑定时只重画摘要区域。无频繁 printf、逐行刷屏、全屏清除或刷新整个 framebuffer；并发像素写和 snapshot 发布按实际上下文设计，不在中断或原锁内绘图。无时钟/线程服务时不启动而非轮询。
5. 显示获取/重映射、vc 重新初始化、panic、图形 scanout 等交接必须先识别所有调用者，建立唯一写者状态：先停止新刷新并等待在途写完成，再失效映射，交给下一所有者；不得在 GUI 获得显示后自动恢复、擦屏或抢回。无法可靠通知任何接管/失效事件则拒绝该设计的运行部署。不能以“首次 GUI swap 才停止”掩盖更早的其他接管。panic 保持既有 panic 控制台优先。

**boot-progress 是独立渲染器，不能用来证明 `IOMobileFramebuffer` 路径可用。**

## 文件与工作量估算

中等，约 5–7 个文件，增量约 350–650 行，不含测试或未知 vc 分支：

| 候选文件 | 估算 | 职责 |
|---|---:|---|
| `package/EnumaDiagOverlay.c` + 头 | 150–250 | 生命周期、快照、区域绘制、更新缓存；受许可约束复用字形画法 |
| `package/EnumaMatchCount2.inc`、`package/EnumaFixupReport.inc` | 合计 40–80 | 现有数据的只读快照接口，复用原原子语义 |
| `package/EnumaProcExecReport.inc`（仅若 r45 候选获接入） | 20–50 | 现有 ex 快照，ps 无现成持久统计 |
| `patches/xnu/` 内新增独立候选补丁 | 100–200 | 可开关的 vc 几何、重映射和安全交接 hook；文件名及具体插入点待核 |
| 候选 archive 构建脚本或现有候选脚本 | 40–70 | 可选链接和诊断 boot-arg；不动默认 recipe/series |

这是估算，不是确认好的 ABI 或链接配方。新增启动 hook、显示生命周期、并发及锁修改须先有明确实现 brief 和 deep_reviewer 审查；不得动冻结的 GOP 路径来假装交接已实现。

## 风险、缓解与实施门禁

| 风险 | 缓解 |
|---|---|
| framebuffer 写者争用/映射失效 | 核实全部写者及映射生命周期；接管前排空 writer 后失效，无法证明则不启用 |
| vc 清屏/滚动覆盖 | 在 vc 全部写路径实施受限矩形并测试；不依靠刷新覆盖 |
| 分辨率、stride、scale、通道未知 | 使用实际 vinfo 与 mapping length；边界和格式校验，未知禁用，不使用 sheng 板值 |
| 字体许可 | 单独查 `Font.h` 来源、版本与许可，确定后保留许可；未闭合不得复制字模 |
| kernel/GUI 接管后残留 | 确认接管协议、停止并等待在途写；下个所有者负责自己的完整重绘，禁止恢复 |
| 影响现有显示路径与默认行为 | 编译与运行双门控、默认零行为，失败不修改 vc；候选与已冻结 GOP 隔离 |
| 数据竞争/不一致 | 保留现有原子和锁契约，只复制快照后渲染；记录非事务性与 `n/a`，deep review |

接入前先验证 XNU 17 vc 全路径区域限制、实际 framebuffer mapping 长度/格式和所有接管点；核实字体许可及探针组合/快照发布。然后 deep_reviewer 审查启动 hook、生命周期和并发；独立 verifier 复跑最终测试。任何实机操作另获当轮授权。

推荐：**参考后自写**小型区域渲染和生命周期，保留上游来源与 MIT 声明；其全屏进度、vc 重定向、板级探针及未核字体不适合原样移植。
