# enuma 全屏 BootProgress 隔离候选

`build-full.py` 从可追溯的 r65 link recipe 重链接，只写指定的新 `out/`。
不改默认 defconfig、series、r4、r5 或冻结包，也不假定 r69d 使用 r65 的显示
后端。`boot-progress=2` 且初始 GOP 映射通过检查时，renderer 使用 XNU
自带 `iso_font` 绘制整屏，展示内核、BSD、启动用户态三段进度。缺省、
`=1`、格式或几何拒绝均不准入 BP，保留 stock VC。

## r6 控制契约

* **映射转换**：`BP_STOP`（永久禁 BP）、`BP_GUI`（已完成 GUI
  release）、`BP_TRANSITION`（临时排他）、`BP_VC_PAUSED`（VC 控制
  状态）相互独立。导入新映射前用 CAS 关闭双方准入，再等完在途 BP 行
  和 VC lease。旧映射 retire 后，转换线程才可执行 stock clear/cursor
  写新映射；其他线程、IRQ 或 panic 无此权限。转换完成后按操作归还
  VC，后续 renderer 不因 reacquire 而恢复。ARM PE 先取得转换资格，
  再调整来参 scale、初始化首次 progress、执行 stock screen、发布
  `PE_state.video` 和路由；资格直到最后一步之后才释放。繁忙返回
  不执行上述任一项。
* **等待上下文**：runtime 入口在取得 `VCPUTC_LOCK` / `vc_progress_lock`
  之前检查中断开启、非 IRQ 且 preemption level 为零；持这两种
  spin/ticket lock 的入口不能等待。字符/PID1 及进度刷新先取得其原锁
  再计 lease；已准入 ARM 像素体不等待转换，不依赖 GUI workloop gate。
  BP 行退出和 VC lease 退出都在 `dsb st` 后发布。正常线程用 1 ms
  scheduler timeout 让在途写者完成，不在 IRQ 自旋。IRQ、禁中断或
  禁抢占的 runtime 调用失败且不退役映射；初期和 `vcattach` 的两个
  stock 调用只走 CAS 已排空路径。`vcattach` 的 release/acquire 均仍跑
  原 `initialize_screen` 实现及 `ep_console_enter/leave`；只有该次
  BP 启动前内部 release 不设置永久停止。release 拒绝则不发 acquire；
  acquire 拒绝则不回放日志、不启动 BP。`PE_init_printf(TRUE)` 的
  void 回调返回后继续 IOKit 初始化，不消费 screen 成功；startup
  独立的 `initialize_screen(NULL, TextMode/AcquireScreen)` 不回放或启动
  BP，随后 `vm_commpage_init` 等非显示路径不依赖其结果。
* **进度图层**：已准入的 progress 任务将同一个 lease 传给私有 blit
  dispatcher。四个像素叶只由该 dispatcher 调用，不重新申请 lease；
  外层转换即使开始等排空，本帧也能完整画完。只有实际执行支持的
  blit 才清 `vc_needsave`；普通 blit 入口仍须自己获得 lease。
* **panic**：未写行时可归还原 VC；写行中禁止新 BP 和 VC，行退出才
  可恢复 VC；如果转换在途，panic 及行退出均不能打开 VC。GUI 已接管
  时 panic 不打开 VC。panic 本身不等被中断的写者。
* **首帧**：CPU-only blank、half、BGRA/diff 分支先核目标范围；half、
  BGRA/diff 还先成功取得源映射和通过布局检查，half 预建转换表。
  然后才进入 `native_legacy_prepare_scanout`，核 PE 参数仍与稳定
  的 VC 映射一致，等待两类 lease，执行 stock pixel release 并发布
  `BP_GUI`。不读取 `disableConsoleOutput` 来判断取权成功；串口路由
  不需关闭。上下文、布局或源映射失败不消耗 GUI 所有权。
* **格式与 ABI**：DarwinBoot `3c757340` 的 `BootVideo.h` 拒绝非 GOP
  BGRX；XNU 检查 boot args、PE 格式和实际映射可用长度
  `newMapSize - v_offset`。iPad7,1 / 21H461 donor SHA-256
  `f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7`。
  UniXNU `693f5d9c` 的 XnuPrelink 配对 image/JSON 验证 donor、原
  IOMobileGraphicsFamily/IOSurface 指令及导出。私有槽位比绝对地址，
  重链接后正常移动的原生槽位按最终导出名验证。不用旧目录猜偏移。

## 复跑与证据

WSL 从设备仓执行，root 用于读取既有本地输入；每次选一个新输出目录。
recipe 自动运行 ASan/UBSan 主机测试（含新生成的 Legacy 布局及像素
helpers）、重编五个内核单元及 Legacy archive、最终链接和 ABI 复核。
第二组测试编译从本次实际生成的 PE/VC 源提取的未改函数，并运行 PE
B/C 交错、首次 release 拒绝、attach 两项拒绝、缺省/`=1`/坏几何，
以及 progress 持 lease 时转换开始后取消。pmap/调度/串口为主机
fixture；progress dispatcher 和像素叶实跑。`generated-test-inputs.json`
记录输入和提取片段哈希。
打包后从 `boot.img` 提取 ramdisk 和 Mach-O，核对哈希、`boot-progress=2`
及 PE/VC、progress→实写 blit、checkpoint、renderer、panic、原 GUI
copy/fill/half/diff 调用边。

`self-checked`：`out/bootprogress-full-link-20261125-r6/boot.img`
（169951232 B，SHA-256 `8e09f44fee2ab2526eec5f0a41bc9d98a04660ab21347bebc780243e223e75a2`）。
`commands.json` 记录两组主机测试、native/prelink 零 undefined 与提取复核；
`final-abi.json` 记录 31 项指令检查、358 个槽位复核。

```sh
c=candidates/bootprogress-20261125
u=../../UniXNU/out/enuma/ipados-17.7.11-21H461/enuma
r=out/ufs-sm8250-fp-20261124-r65
v=out/bootprogress-r6-verifier-20261125
/home/wh1stl3/.local/bin/python3.11 "$c/build-full.py" \
    --tree "$u/tree" --abi-image "$u/kernel/kernel.macho" --abi-plan "$u/kernel/kernel.json" \
    --display-source out/bootprogress-display-source-20261125 \
    --link-record "$r/commands.json" --kernel-source out/ufs-sm8250-ustack-20261124-r64/source \
    --reference-payload "$r/payload.img" --reference-boot-report "$r/boot.json" \
    --board "$r/device" --local out/ufs-sm8250-launchd-data-20261119-r1/self-check/packaging/local-build.toml \
    --uefi ../uefi-enuma --fd ../uefi-enuma/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd \
    --dtb /root/enuma-step10/inputs/enuma.dtb --output "$v"
```

主机测试不证明实机像素、GUI 首帧或 panic 的运行时顺序。启动及并发改动
须重新交 `deep_reviewer`，最终构建/测试须 `verifier` 独立重跑。

## 历史输入与候选

* r5 已退回并保留，`out/bootprogress-full-link-20261125-r5-reviewed-fixes/boot.img`
  SHA-256 `18f544f19f7105df5f76e71c4753df946b77822fe307e544b744362897836a3c`。
  r6 沿用其已审的 GUI backend 与排空逻辑，不部署 r5。
* r4 被退回并保留，`out/bootprogress-full-link-20261125-r4/boot.img`
  SHA-256 `4251b83a45c9b61e9ba10fb7798f6137ca3b8d1d2fcb323f1f7ef3b20712f3a9`。
  r4 不能作为合并或部署输入。
* `build-archive.py`、`build-recorder.py`、`recorder.c` 及本目录
  `enuma_defconfig` 属历史试验，不是全屏配方。上游绘制设计参考
  `UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e:package/BootProgressDisplay.h`
  （MIT），不移植 sheng renderer/硬件钩子或外置字模。字体复用固定
  XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f` 已编入的 `iso_font`。
