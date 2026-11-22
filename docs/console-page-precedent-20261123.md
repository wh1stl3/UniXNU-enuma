# Sheng boot-progress 与控制台页面先例

结论：**部分是**：有拦截并抑制原控制台输出的先例，但页面不是通过控制台打印，而是自绘 framebuffer。仅静态审查；无构建、设备操作或运行时证明。

来源：`UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e`（以下简称 sheng），以及本地官方基座 `UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241` 的 `patches/xnu-12377/zzz-boot-progress.patch`（以下称基座补丁）。这是基座源码层面的接线，不声称已核验某个 sheng 成品二进制。sheng 代码标记 MIT。

1. **通道与钩子**。基座补丁 `:233-239,250-263,373-379` 的原始摘录：
   ```c
   _cnputc(char c, bool poll) {
       if (boot_progress_active()) { boot_progress_putc(c); return; }
   vcputc_options(char c, __unused bool poll) {
       if (boot_progress_active()) { boot_progress_putc(c); return; }
   boot_progress_bind(vinfo.v_baseaddr, vinfo.v_width, vinfo.v_height,
       vinfo.v_rowbytes, vinfo.v_depth);
   if (boot_progress_active()) { PE_kputc = boot_progress_putc; return; }
   ```
   分别截取 `_cnputc`、`vcputc_options` 和 `PE_init_kprintf`；`initialize_screen` 提供 XNU 已映射的 framebuffer，`boot_progress_bind` 在 sheng `package/BootProgress.c:584-602` 检查几何后绑定。字符用于采集，不是页面输出 API。

2. **抑制、丢失、恢复**。上述前两个钩子在 active 时直接 `return`，绕过原 console ops（包含所选串行/视频通道），`PE_kputc` 则替换函数指针。`package/BootProgress.c:541,606-611`：
   ```c
   int boot_progress_active(void) { return enabled != 0; }
   if (!enabled || !take()) return;
   bp_char(&state,c);
   ```
   `package/BootProgressCore.h:5-6,26-33`：
   ```c
   #define BP_COLS 120
   #define BP_LOGS 14
   if (s->frozen || c == '\r') return;
   if (c != '\n' && (c < 32 || c > 126)) return;
   s->log_row = (s->log_row + 1) % BP_LOGS;
   s->log_col = 0; s->logs[s->log_row][0] = 0;
   ```
   因此不是清空原 console 缓冲：是拦截后的有限环形记录，锁未取得、冻结、过滤字符或环覆盖均可丢失。`package/BootProgress.c:573-581` 设置 `enabled=opt`；所查文件中没有恢复为零的路径。`package/BootProgress.c:550-568` 的 `display.bound=0` 是向 scanout 让出自绘，注释明确 `Recording remains active so console fallback cannot start drawing over the system frame`；不是恢复普通控制台。`:519-525` 的 `boot-diag-resume` 在配置且满足时间条件时恢复**诊断自绘**，也不是恢复 console。冻结同样不退出 active。

3. **panic**。基座补丁 `_cnputc` 的 active 判断在 debugger 检查之前（`:233-239`），没有 panic 例外，因此普通 panic 字符路径可能被重定向/丢弃，不可假设 panic 前自动恢复。另有独立可选 panic framebuffer 路径：sheng `scripts/patch-xnu-entry-probe.py:410-432`：
   ```python
   if args.panic_screen:
       ...
       struct.pack_into('<I', data, file_offset(PANIC_VA), branch(PANIC_VA, entry))
       common = kernel_names.get('_panic_trap_to_debugger')
       ...
       struct.pack_into('<I', data, file_offset(common), branch(common, common_entry))
   ```
   `scripts/xnu-panic-screen.c:222-235,251-265` 直接取得 `VINFO` 地址并在 framebuffer 上绘图，`format (&g, fmt, args)`；它不是恢复 console。`package/BootProgress.c:96-98,396-405,1056-1061` 指出其他核心 panic 后 monitor/swap 可覆盖 panic 画面，并将首条 panic 文本供 banner 显示；后者不是无条件永久保留。`board.toml:60,185` 分别配置 `panic_screen = true`、`boot-progress=2`；独立 panic 路径需对应打包选项，不能泛化到其他构建。

4. **清屏**。`package/BootProgressDisplay.h:13-20`：
   ```c
   for(unsigned y=0;y<d->height;++y) {
     if (__atomic_load_n(&d->yield_requested,__ATOMIC_ACQUIRE)) return;
     for(unsigned x=0;x<d->width;++x)
       *(volatile uint32_t *)(d->frame+(uintptr_t)y*d->stride+x*4)=0;
   }
   ```
   这是逐像素清零 framebuffer，不是换行顶出，也不是调用控制台清屏 API；可因 yield 提前中止。`BootProgress.c:601-602` 绑定后调用 `bp_clear` 再 `draw`。

5. **自绘及共存**。`package/BootProgressDisplay.h:40-53` 从 `font[c-32]` 取字形，按行列计算 `at` 并写 `*(volatile uint32_t *)at = ... ? color : background;`；`BootProgress.c:308-311` 从截取的环中选最近七行交给 `line` 自绘。原 vc 渲染在 active 时被短路，而非和它并行绘制。正常 scanout 的显式让出见 `:550-568`；`refresh` 的 `:527-535` 每 15 秒强制重绘以覆盖其他早期画面，说明共享 framebuffer 的覆盖问题没有因截取而消失。

6. **默认开关**。基座补丁 `:301-320` 以 `XNU_BOOT_PROGRESS` 控制编译接线；未开启时 `boot_progress_active() 0`。sheng `package/BootProgress.c:573-580`：
   ```c
   if (!PE_parse_boot_argn("boot-progress",&opt,sizeof(opt)) || (opt != 1 && opt != 2)) return;
   if (!boot_progress_frequency) return;
   ... state.continuous=opt==2; enabled=opt;
   ```
   没有有效 boot-arg 时本功能不激活、这些钩子不拦截，普通 console 走原分支；不代表其他独立补丁都不存在。sheng `board.toml:185` 的一个配置明确加了 `boot-progress=2`；不能称该配置默认未开启。

**与拟议“直接用 console 输出固定页然后抑制后续输出”比较**：sheng 抑制的是普通字符输出，同时另行保留有限最近日志、自绘整页，并为可选 panic 做独立 framebuffer 入口；它没有证明页面结束后恢复普通输出。拟议方案额外的首要风险是抑制开关覆盖 panic 或恢复失败，导致关键故障信息不可见；还需单独验证页面被清除/覆盖及输出路径范围。
