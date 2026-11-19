# r6 显示候选构建：把 `XNU_NATIVE_LEGACY_DISPLAY=1` 编进两个启动链单元

状态：`self-checked`（host-only 构建/打包/读回；独立 verifier 未复跑）。**未上机**、未部署、未刷写、
未创建 claim；本轮无任何 adb/fastboot 子命令。产物在 `out/ufs-sm8250-launchd-display-20261119-r6/`
（ignored），本文件是该目录结论的入库载体；逐项记录见该目录 `CHECKPOINT.md`。

## 结论

r5 的 `bsd_init.o` / `IOUserClient.cpo` 是 `XNU_NATIVE_LEGACY_DISPLAY=0` 编的，两个显示入口在
`native.macho` 里 **0 个调用点**，归档是死代码。r6 只翻这一个宏、只重编这两个单元，两个入口变为
**4 个机器级调用点**（2 个源级位置；`IOBSDInit` 是静态函数被内联两次），六显示符号仍唯一归属归档，
零 undefined（含 weak），boot-args / store mode / initrd / payload 档位 / ADT / trust cache 与 r5 逐项相同。

## 为什么只影响两个单元

| 层 | 位置 | 事实 |
| --- | --- | --- |
| 配置 | `configs/enuma_defconfig:18` | `CONFIG_XNU_NATIVE_LEGACY_DISPLAY=n`（本轮不改配置，不重建准备树） |
| 映射 | `UniXNU/scripts/unixnu/kernel.py:17-26` | `CONFIG_XNU_*` → `XNU_*` 环境变量（`n`→0） |
| 构建 | `UniXNU/scripts/build-xnu-4k-baseline.sh:362` | `bsd_init.o_CFLAGS_ADD=… -DXNU_NATIVE_LEGACY_DISPLAY=${XNU_NATIVE_LEGACY_DISPLAY:-0}` |
| 构建 | 同文件 `:368-373`、`:375-377` | `IOUserClient.cpo_CFLAGS_ADD=… -DXNU_NATIVE_LEGACY_DISPLAY=$NATIVE_LEGACY_DISPLAY`，且该值变化时删 `IOUserClient.cpo` |
| 源码 | `bsd_init.c:550`、`bsd_init.c:1304`、`IOUserClient.cpp:6789` | 全树只有这 3 处 `#if … XNU_NATIVE_LEGACY_DISPLAY`（`grep -rn` 于 `.cache/xnu-work`） |
| 调用点 | `bsd_init.c:554-555`、`bsd_init.c:1308-1309`、`IOUserClient.cpp:6790-6791` | 两处 probe、一处 late probe |

脚本里只有这两条 `_CFLAGS_ADD` 提到该宏，因此失败面只有这两个目标文件；本轮没有发现需要改第三处
（链接顺序、force_load 均沿用 r5，归档本身已解析这两个符号）。

## 机械证据

- 目标文件（`sha256sum self-check/objects/<unit>`）：
  - `bsd_init.o` `6c54e226…b8c1c`（177,616 B）≠ r4/r5 的 `8fa75687…`
  - `IOUserClient.cpo` `da268498…fbdf7a`（701,704 B）≠ r5 直接链接的树对象 `e64e26b1…812f45`
  - `IOKitBSDInit.cpo` `09d4a807…`、`kern_exec.o` `dd0612cc…`、`EnumaUfsOwnerQuery.o` `768ba0c3…` 与 r4 逐字节相同
- 调用点（`llvm-objdump -d --no-show-raw-insn` + `bl 0x… <symbol>`；r5 `CHECKPOINT`/`check-r5.py` 用的同一检测器，r6 直接复用）：
  - `_native_legacy_display_probe`：r5 0 → r6 2（`_bsd_init`、`_native_mobile_graphics_client_probe`）
  - `_native_legacy_display_late_probe`：r5 0 → r6 2（`_bsd_init`、`_bsd_autoconf`）
  - `_native_legacy_prepare_scanout`：4 → 4（`NativeLegacyDisplay::kickSwapQueue` 内部）
  - 原样命令实跑：`llvm-objdump -d --no-show-raw-insn native.macho | grep -c '<_native_legacy_display_probe>$'`
    → r6 `2` / r5 `0`；late probe → r6 `2` / r5 `0`；prepare_scanout 两侧均 `4`。
- `prelink.macho` 124,686,336 B `737e402d…`；`native.macho` 91,843,800 B `116a016e…`（比 r5 少 80 B，符号集合相同）。
- 符号：相对 r4 +255 / −0；六符号唯一归属 `libEnumaGopLegacy.a`；`NativeGOPPresenter.o` / `NativeMobileDisplay.o` 零命中。
- `payload.img` 167,772,160 B `4ca318cd…`；`boot.img` 169,951,232 B `3161efc6…`（余 31,375,360 B）；
  载荷内核 `737e402d…`；ADT `099dda97…`（vs r4 确定性差异 0/0/0）；`unixnu.toml` `5576211f…`（= r5）。
- 与 r5 一致项：15 token boot-args（含 8 个 `offline-legacy-*` + `offline-mobile-graphics-load` + `sheng-vsync=60`）、
  store mode 0、seed initrd `c89592f8…`、160 MiB 档位、trust cache `7416ca4f…`。

## 复跑（WSL root，cwd = 产物目录）

```sh
/home/wh1stl3/.local/bin/python3 -B self-check/build_kernel.py   # exit 0
/home/wh1stl3/.local/bin/python3 -B run_packaging.py             # exit 0
/home/wh1stl3/.local/bin/python3 -B check-r6.py                  # exit 0，43/43，failed: []
```

`UniXNU` HEAD 在构建与打包各取一次，均为 `693f5d9c…`；r5 与 GOP r5 的产物在构建/打包前后快照不变。

## 不证明

- 没有任何设备证据：不证明像素输出、`EnumaLegacyDisplay:` 阶段行、GOPSwap/vsync、控制台释放，
  也不证明 `com.apple.iokit.IOMobileGraphicsFamily` 在本内核能被 `OSKextLoadKextWithIdentifier` 加载。
- 不证明 launchd 初始化完成、Data 挂载、持久根卷/Data/store、UFS 所有权或跨 EBS DMA ownership。
- `native.macho` 少 80 B 只记录了大小与符号集合，未逐函数比对布局差异。
- 归档源码级 ABI（GOP `qualify()`）未重跑，沿用 r5 的 extent 字节同一性与 193 个绝对地址比对。
- mode 1/2 未放行；默认 `NoAccessPolicy`/`NoContract` 不变；正式阶段不变。上机需另行当轮授权 + 先审后上。
