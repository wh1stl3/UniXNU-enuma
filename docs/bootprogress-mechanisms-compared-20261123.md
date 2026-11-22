# Boot-progress 机制对照（2026-11-23）

结论：nuwa **不是**「控制台 + 周期重打摘要」。它复用 XNU 已建立的 framebuffer 映射，自绘诊断页面，同时截取控制台字符；周期性刷新的是像素而非 printf 行。以下为静态源码分析，未构建、未上机。

## 来源和版本

nuwa `UniXNU-nuwa` 工作树 HEAD `ce0339a8a8ff11e9268f7465dfbced26d3fc329c`；本节路径均相对于 `D:/Code/PortingiOS/nuwa/UniXNU-nuwa/`。`patches/xnu/8796-nuwa-boot-progress.patch:3-5` 写明 `Port of UniXNU/UniXNU-sheng@998d0cc5023d4eff54a1ef40cce6ec89dc10083c`，renderer 也来自同 commit，许可证 MIT；这是来源声明，不证明目前 nuwa 修改后与 sheng 一致。对照仅限这个已记录来源：指定上游原文件 HTTP 404，未独立取得 sheng 源码，不据此断言现版 sheng 行为。

## 输出路径与内容

* `patches/xnu/8796-nuwa-boot-progress.patch:104-108,140-144,155-159`：
  `if (boot_progress_active()) { boot_progress_putc(c); return; }` 插在 `vcputc_options` 和 `_cnputc`；`PE_init_kprintf` 在 active 时 `PE_kputc = boot_progress_putc; return;`。这是截流，不是调用 `printf` 排版。
* 同 patch `:112-129`：`boot_progress_bind(vinfo.v_baseaddr, vinfo.v_width, vinfo.v_height, vinfo.v_rowbytes, vinfo.v_depth)`；`package/boot-progress/BootProgress.c:585-603` 注释明确 `AFTER XNU established its own mapping`，检查高地址、32 位和几何后将 `display.frame=base` 并清屏、绘图。此路径复用映射，不是新建 framebuffer 映射。
* `package/boot-progress/BootProgressDisplay.h:13-18,38-53`：`*(volatile uint32_t *)(d->frame+(uintptr_t)y*d->stride+x*4)=0` 清屏；字体位图经 `*(volatile uint32_t *)at = ... ? color : background` 直接写像素。
* `package/boot-progress/BootProgressCore.h:5-14,26-36`：`BP_LOGS 14`，`bp_char` 把字符收进有限行环；`BootProgress.c:393-408` 用 `snprintf` 生成 `CLK ...`、`PANIC LOG ...` 等行交给 `line` 自绘。页面是多行文字、计数与彩色栏，而非仅控制台换行；不是 GUI 图标进度条。`porting.toml:333` 亦记录页面是 vinfo 绘制的诊断仪器。

## 控制台抑制及 panic

* `BootProgress.c:542,574-580,607-612`：`boot_progress_active()` 返回 `enabled != 0`；开启时 `boot_progress_putc` 调 `bp_char(&state,c)` 收字符。上述三个 hook 的 `return` 跳过原通道；抢锁失败或冻结时字符可丢失，不保证完整日志。`enabled` 在本实现中初始化置位，未找到正常停用赋零路径，故不能声称 panic 前恢复原控制台。显示 handoff `BootProgress.c:548-565` 只让自绘 `display.bound=0`，注释明确 `Recording remains active`，不是恢复控制台。
* panic 可受截流影响：patch 的 active 检查没有 panic 例外。另有单独画面策略，`BootProgress.c:94-97` 声明 `boot_progress_panic_text` 并注释 freestanding panic screen 保存首个消息；`:397-408` 在 debugger 已进入时从 `debug_buf_base` 提取并自绘首段；`:1056-1059` 对已被覆盖的 panic 文本分行。这些不能证明每条 panic 均可见，也不能证明独立串口旁路已接通。历史 `porting.toml:333` 所述 r21 panic 后停止刷新是历史版本；当前 HEAD `:397-398` 明确考虑 monitor 可能覆盖 panic，不能混为一谈。

### panic 截流时序补充

1. **具体层**：`patches/xnu/8796-nuwa-boot-progress.patch:104-108` 在 `vcputc_options` 开头插入 `if (boot_progress_active()) { boot_progress_putc(c); return; }`；`:140-145` 在内部 `_cnputc`（不是仅公开的 `cnputc`）开头同样截流；`:155-161` 的 `PE_init_kprintf` 选择 `PE_kputc = boot_progress_putc; return;`，将早期 kprintf 的函数指针改向。三者是不同入口，非断言所有可能输出路径均经过它们。
2. **判定与丢失**：`package/boot-progress/BootProgress.c:106,542,574-580` 的 `static unsigned enabled` 零初始化；`boot_progress_active() { return enabled != 0; }`；仅解析 `boot-progress=1/2` 且 CNTFRQ 非零才执行 `enabled=opt`。该文件未发现重置 enabled 的赋值。`:607-609` 中 `if (!enabled || !take()) return; bp_char(&state,c);`；`:219-225` 的 `__atomic_exchange_n(&busy, 1, __ATOMIC_ACQUIRE)` 若忙则递增 dropped 并立即返回，`:548-565` 的显示让出只设 `display.bound=0`，明确 `Recording remains active`。所以截流后原输出不继续，锁忙则连字符环也不保留；`BootProgressCore.h:26-29` 的 `if (s->frozen || c == '\\r') return;` 还过滤冻结和部分字符。
3. **panic 的独立旁路是可选独立组件，不是截流层恢复**：`D:/Code/PortingiOS/UniXNU/scripts/patch-xnu-entry-probe.py:407-424` 的 `if args.panic_screen:` 将 `_panic` 与 `_panic_trap_to_debugger` 分支改到 renderer，缺 common funnel 即拒绝；`scripts/xnu-panic-screen.c:285-298` 分别 `b panic_screen_main`。该 renderer 在 `:50-57,79-87,218-230,249-254` 直接格式化并写 framebuffer，满足符号绑定时另复制到 `PANIC_TEXT`；patcher `:199-204` 表明该缓冲地址是可选的，没符号就没有副本。此路径绕过字符截流，但未恢复原控制台；`board.toml:136-144` 默认配置 `panic_screen = true` 不是所有历史或当前包都有它的证据（例如 `scripts/owner_payload.py:406-407` 显式设 false）。画面映射无效、fmt 为空则 `park()`，又会有覆盖及格式范围限制，不能称为所有 panic 文本完整保底。
4. **并发与时序**：hook 只检查 `boot_progress_active()`，没有 `panic_active()` 或 `debugger_current_op` 判断；`:219-225` 的原子 busy 只保护记录器访问，不与 panic 状态联动，不是 panic 恢复屏障。`:397-401` 的 `kernel_debugger_entry_count` 仅用于已经进入 debugger 后提取 `debug_buf_base`，不是截流处判断，也不能覆盖早期窗口。`scripts/xnu-panic-screen.c:233-237,279-280` 的像素 marker 只尝试首个 panic 保留，检查与写入间无原子竞争仲裁。
5. **风险和记录**：没有独立 renderer 的包中，进入上述 hook 的 panic 早期字符会被改投字符环而非原控制台，锁忙或冻结时实际丢弃；不能断言每一次 panic 都会走到这些 hook。启用独立 renderer 的包可以走上述像素旁路，但不保证输出完整可见。`docs/nuwa-userspace-20261119-observation.md:55` 记载 r32 的「实机 panic 清屏把该行抹掉」；这是诊断行被 panic 画面擦除，不是 panic 字符遭截流丢失的实机证明。`BootProgress.c:397-398` 则记录 monitor 可能重画覆盖 panic 屏，属于源码所述现象，非本轮独立观察。

**判定**：截流机制自身对 panic **不安全，不能照搬**。最简选择是不截流，保留原控制台；若坚持截流，须在 panic 最早入口、任何 panic 字符输出前建立可并发观察的永久旁路，并验证现有锁竞争及所有输出入口，不可仅检查在 `console_suspend()` 后才置位的 `panic_active()`。这种启动链/并发改动须另行 brief 和 deep review。

## 事件、周期与开关

* `patches/xnu/8796-nuwa-boot-progress.patch:48-62,73-93,186-193` 把初始化、启动和阶段事件插入启动路径，例如 `boot_progress_stage("arm_vm_init enter")`。`BootProgress.c:614-625` 在事件到来时记录 `bp_stage`，启动 monitor 前可立即绘图；`:607-612` 在早期换行且秒数变化时也可绘图。
* `BootProgress.c:1163-1183` monitor 循环 `refresh(seconds())`，再 `assert_wait_timeout(...,1000,NSEC_PER_MSEC)`；`:527-537` 比较并重绘变化单元，每 15 秒重置颜色强制整行重画。故既有事件更新又有周期像素刷新，不是一次性打印。
* `patch:11,280-307`：必须编译 `XNU_BOOT_PROGRESS=1`，否则接口编译为空操作；`BootProgress.c:574-580`：只有 `boot-progress=1` 或 `=2` 且 CNTFRQ 非零才启用，缺省关闭。`:579-580` 与 `BootProgressCore.h:39-52`：1 为到限冻结的诊断模式，2 为连续模式；`BootProgress.c:747-763` 冻结后停留画面并 WFE。具体包是否启用须核该包的编译参数和 boot-args，不能由源码默认推断。

## 对 enuma 方案的参考

可借鉴**事件计数快照与有限行摘要**，但不能把 nuwa 的 framebuffer 自绘、控制台截流或硬件参数当作纯控制台方案复用。对照的运行时效果尚未验证；独立 verifier 尚未复跑。
