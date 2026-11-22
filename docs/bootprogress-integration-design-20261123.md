# enuma 全屏 boot-progress 接入设计（2026-11-23）

状态：仅静态审查；未构建、未访问设备。范围仅设计，不改变默认 recipe、冻结的 GOP 包或启动路径。

## 来源与许可

首选可作为**实现参考**：`UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e:package/BootProgressDisplay.h`，文件首行原文 `// SPDX-License-Identifier: MIT`。仓根 LICENSE 为 BSD-2-Clause-Patent；本设计不引用 sheng 字模。`git ls-remote --heads ... main` 实测 main 指向上述 commit。GitHub commits API 对该 pin 和该路径返回最后修改提交 `fb2d4ed7ae02aa3fb53688c3d70bfaefd5c1b8f5`，author bluseliu50，2026-10-19 10:48:38Z，主题 `Initial import`，等价于路径限定的 `git log -1` 信息；本轮没有本地 sheng 检出，**未运行 git log**。

不是 macOS 专线：该 pin 的 `board.toml` 默认 profile 是 iPadOS 27，但 `[os_overrides.ipados-17.7.11-21H461.kernel]` 明确选择 `build-boot-progress.py`、`sheng_defconfig`，同名 payload override 明确 `boot-progress=2`。即同 donor 的 iPadOS 17 配置引用本实现，并非证明该 pin 在该 profile 实机运行。候选来源与对照见 `docs/bootprogress-candidates-20261123.md`；不需要切换 tb128fu。

## 上游实现：具体机制

以下行号均指上述 sheng pin，官方补丁指基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。

* **映射**：官方 `patches/xnu/zzz-boot-progress.patch:84-88,99-104` 在 XNU 建立/更新 console mapping 后把 `vinfo.v_baseaddr, v_width, v_height, v_rowbytes, v_depth` 传入 `boot_progress_bind`；不是通过 IOMobileFramebuffer 取得句柄。`package/BootProgress.c:584-605` 要求高地址 kernel VA、depth 32、宽 720..4096、高 560..4096、`rb >= w*4 && rb <= 65536` 和地址加 `h*rb` 不溢出；以 `h*rb` 推算边界，并未传入/独立证明 mapping 长度。32bpp 不能证明通道次序。
* **绘制**：`package/BootProgressDisplay.h:4-5` 的 `font[] = GLYPH_FONT` 来自外部 `Font.h`；它不是内嵌于该头的可独立许可字模，来源/许可待核。`:24-55` 对 ASCII 32..126 解码每字 5×12 位图、使用 6×14 单元及空白边缘，写 `frame + y*stride + x*4` 的 32 位像素，scale 为 1 或 3（`BootProgress.c:592`）。`:28-45` 对比上一行文字和颜色，仅改变化单元；颜色变化重绘行；`:13-20` 清全屏。减少重写不是双缓冲或无撕裂保证。
* **刷新和 vc**：`BootProgress.c:516-538` 拍状态快照，不持 recorder 锁画像素，每 15 秒失效颜色缓存强制重绘；`:606-625` 初期字符/阶段触发绘制；`:1161-1183` monitor 约一秒刷新。官方补丁 `video_console.c` 的 `vcputc_options` 在 active 时调用 `boot_progress_putc(c); return`，`serial_console.c` / `pe_kprintf.c` 也有重定向：捕获日志内容并显示自己的页面。`boot-progress=1` 会按 stall/limit 冻结，`=2` 持续运行（`BootProgress.c:573-581,748-761`）；不适合原样直接接入。
* **交接**：`BootProgress.c:550-569` 的 `boot_progress_prepare_scanout()` 请求 writer 停止，获取 render/pulse 排他后置 `display.bound=0`、关闭 pulse，失败返回 0；由受控 scanout 路径调用，不是 kernel 自动完成的通用所有权协议。`:516-525` 可选 `boot-diag-resume` 会在超时后重新绑定/清屏，`:933-940` crash banner 也可能重绘。全屏 GUI swap 可覆盖；这里没有通用的线程销毁/映射 teardown 证明，不能假设交接后不会重入。

## enuma 当前事实与数据

`docs/enuma-gop-r5-device-observation.md` 记录 `EnumaGOPFramebuffer` 是 legacy 的 `IOPlatformDevice` provider；r5 的 start 进入但未观察到有效 swap、像素输出；屏幕文字为 vc。该结论不建立独立渲染器和 legacy mapping 相同、并发安全或交接已完成。该 GOP 线冻结。

* `package/EnumaMatchCount2.inc:9-17,56-65,86-112` 有静态原子计数与 `enuma-mt:` 报告；`all/other/bb/sb` 可复用现有快照语义，但 bb(34)/sb(5) 仅固定 PID 桶，不证明进程身份。
* `package/EnumaFixupReport.inc:3-18` 的静态 `enuma_fx_bits` 与 `cs_text_fixup_parsed/applied` 在各自编译单元中，按既有 acquire/relaxed 顺序读；不能直接从另一编译单元引用 static。
* 工作树未跟踪的 `package/EnumaProcExecReport.inc:24-27,46-95,135-173` 是 r45 候选，不是已交付基线：`enuma-ps` 在单次 dump 临时枚举进程，`enuma-ex` 计数与 last 使用既有 spin lock。`ps` 的 `total/kept` 是栈局部值；不能假定存在持久可读计数，也不能声称 r44 包含该候选。
* 这些是隔离探针编译单元，不保证同时链接或导出；缺少相应探针时显示 `n/a`，不得用 0 冒充。读取现有计数不新增事件采集；把既有一次性快照暴露出来仍需明确发布及同步设计。

## 最小候选设计（尚未实现）

1. **启动二选一**：缺省不加参数时完全沿用现有 vc 路径，屏幕输出一行不变；不创建工作线程，不写 framebuffer，不改变默认 `board.toml`。仅诊断候选加 `enuma-bp=1`，有效绑定后整屏交给 boot-progress，拦截 vc 的屏幕绘制，原 vc 字符可丢弃；不引入上游的冻结语义。此时屏上不再有原 vc 滚动日志，故不能以它观察普通控制台输出；保留其他日志通路须逐一核实，不承诺串口或 msgbuf 行为改变。未完成绑定或几何校验失败时不接管，原 vc 继续。
2. 在 XNU console 的现有 vinfo 映射完成点绑定，严格核对映射实际长度、rowbytes、深度、通道格式和坐标溢出；不另外映射硬件。确认所有 vc 写 framebuffer 的入口及初始化、清屏等路径均在接管期间停止写屏，并验证切换顺序：先停止/排空 vc 写入，再让渲染器清屏一次并绘制。不能只拦截字符而忽略 vc 其他像素写入口；无法证明排他时不得启用。
3. **字体**：直接引用已链接在 XNU 中的 `iso_font`，不包含或复制外部字模，也不再次 `#include "iso_font.c"` 产生重复定义。固定 XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f` 的 `osfmk/console/iso_font.c:32-47` 声明 `unsigned char iso_font[256 * 16]`；`video_console.c:106,1379-1410` 包含该文件并以 `iso_font + ch * 16` 寻址，每行一字节，mask 从 1 左移到最高位。可在同一 XNU 编译单元直接使用该定义；跨单元则以匹配声明引用已有符号，实际可见性与链接先验证。原文件头 Apple Public Source License 2.0，字体注释为 Ka-Ping Yee、`This font may be freely used for any purpose.`；沿用原文件，不另引入字模。
4. 每格为 `8*scale` × `16*scale` 像素，列数 `width/(8*scale)`、行数 `height/(16*scale)`，整数向下取整并按缓存容量截断。`iso_font[(unsigned char)ch*16+y] & (1u<<x)` 决定该像素，倍数缩放复制像素，逐行按实际 stride 寻址；字符边界、相乘溢出及 mapping 长度必须检查。按实际几何选可读的整数 scale，至少容纳 8 行，不满足时拒绝启用；不假定本板尺寸或像素通道。
5. 在已有探针的原编译单元提供**只读快照接口**，以原子/原锁拷贝后释放锁，再格式化及绘制。首版 8 行：标题/有效性；mt 全局、other、bb、sb 四行；fx parsed/applied、bitmap 两行；ex ok/fail 一行。若 ex 未编入则显示 `n/a`；当前 r44 不证明 ex 可用。ps 临时枚举不转为额外采集；不改已有采集次数、锁与顺序。单一低频线程每秒采样一次，只重绘变化的字格，首次绑定和必要重绑定可整屏清一次；不逐行 printf 或逐帧重绘。无时钟/线程服务时不启动而非忙等。
6. **退出与接管**：先识别 framebuffer 重映射、vc 重新初始化、panic、其他图形渲染器取得写权的所有入口，建立唯一写者状态；其他渲染器写入或旧 mapping 失效前，先禁止新刷新、等待在途像素写结束、解除绑定，再交接；无法安全等待时接管调用方不得继续并发写。接管后的新所有者负责完整重绘，boot-progress 不自动恢复或擦屏。panic 保持既有 panic 路径优先，具体同步待核。无法可靠覆盖接管通知与失效入口则禁止部署；没有现成通用交接 API 可假定。**运行中不提供切回控制台功能，只能靠下次启动的 boot-arg 选择模式**；显示被其他渲染器接管是停止绘制，不等于切回 vc。

**boot-progress 是独立渲染器，不能用来证明 `IOMobileFramebuffer` 路径可用。**

## 文件与工作量估算

中等，首版预计 **4 个文件、约 250–450 行**，不含测试和尚未核实的额外接管路径。为减少文件数，渲染器和 XNU 接线一起放进隔离补丁；不包括可选 r45 `ex` 快照实现：

| 候选文件 | 估算 | 职责 |
|---|---:|---|
| `patches/isolated/enuma-boot-progress.patch`（新增，1 个） | 170–290 | XNU 内全屏绘制、`iso_font` 引用、opt-in、停止 vc 写屏及接管 hook；具体插入点待核 |
| `package/EnumaMatchCount2.inc`、`package/EnumaFixupReport.inc`（2 个） | 合计 40–90 | 现有数据只读快照接口，复用原原子语义 |
| 候选构建脚本（新增或现有隔离脚本，1 个） | 40–70 | 按诊断候选应用补丁及提供可选 boot-arg；不动默认 recipe/series |

这是估算，不是确认好的 ABI 或链接配方。新增启动 hook、显示生命周期、并发及锁修改须先有明确实现 brief 和 deep_reviewer 审查；不得动冻结的 GOP 路径来假装交接已实现。

## 风险、缓解与实施门禁

| 风险 | 缓解 |
|---|---|
| framebuffer 写者争用/映射失效 | 核实全部写者及映射生命周期；接管前排空 writer 后失效，无法证明则不启用 |
| 旧 vc 或 panic 写屏与全屏接管竞争 | 启用前识别并排空既有写者；panic 获得优先权后停止渲染，未证明排他则不启用 |
| 分辨率、stride、scale、通道未知 | 使用实际 vinfo 与 mapping length；边界和格式校验，未知禁用，不使用 sheng 板值 |
| 字体链接或布局不符 | 复用该 XNU 现有 `iso_font` 定义，不重复编译字模；确认符号可见性、位序及 APSL 2.0 文件许可 |
| kernel/GUI 接管后残留 | 确认接管协议、停止并等待在途写；下个所有者负责自己的完整重绘，禁止恢复 |
| 影响现有显示路径与默认行为 | 编译与运行双门控、默认零行为，失败不修改 vc；候选与已冻结 GOP 隔离 |
| 数据竞争/不一致 | 保留现有原子和锁契约，只复制快照后渲染；记录非事务性与 `n/a`，deep review |

接入前先验证 XNU 17 全部 framebuffer 写者、实际 mapping 长度/格式、所有接管点和 `iso_font` 链接方式；核实探针组合/快照发布。然后 deep_reviewer 审查启动 hook、生命周期和并发；独立 verifier 复跑最终测试。任何实机操作另获当轮授权。

推荐：**参考后自写**全屏摘要绘制和生命周期，参考上游接管思路并保留来源；使用 XNU 自带字体，不移植上游板级探针和冻结机制。
