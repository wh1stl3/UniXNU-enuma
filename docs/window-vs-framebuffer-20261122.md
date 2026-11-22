# DarwinBoot 窗口与 framebuffer（2026-11-22）

状态：`self-checked`，仅静态分析，无构建、无设备操作。结论：实际重叠及其导致 backboardd 未启动均未证实；固件源码中的保留声明和旧窗口位置反而不支持该嫌疑。缺 r21/r23/r24 分配时 EFI memory map 与各自实际窗口/GOP 交接记录。

## 分配机制

以本地 UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241` 工作树源码为范围：`drivers/DarwinBoot/DarwinBootPkg/Driver/DarwinBoot.c:400-416,419-441,495-529` 从 `GetMemoryMap` 中扫描 `EfiConventionalMemory`，`RunEnd` 只向上合并物理相邻的同类型描述符；其他类型（包括 EFI reserved 和 ACPI）不会作为可用区或跨越段。按 map 遍历顺序，候选 `ALIGN_VALUE(PhysicalStart, 2 MiB) + (Kernel.Base & (2 MiB - 1))`，足够大时 `AllocatePages(AllocateAddress, EfiLoaderCode, ...)`，首个成功者使用；每个描述符均尝试其候选，不是在某一描述符内任意搜索。这里没有按 framebuffer 地址排除区间或指定基址参数；保留依赖 EFI map 正确反映实际占用。

`DarwinBoot.c:720-750` 先读取 GOP，再分配窗口；`ZeroMem` 仅清窗口已使用前缀，不代表全窗立即被覆盖；整个窗口作为 boot args 内存交给 XNU。`BootVideo.h:20-35` 使用 GOP 的 FrameBufferBase 和 mode 计算行距等，并不由其自动排除物理页。`scripts/unixnu/devicetree.py:305-310,319-323` 的 `dram_size` 是 DTS 几何一致性检查，`owned_memory_size` 只形成 `/chosen/darwinboot-memory-size`，均非窗口基址。单纯添加 ADT boot-video 不会让上述 EFI 分配器避开该区。

## enuma 实际证据与边界

`porting.toml:76` 的 2026-11-09 DarwinBoot 交接记录是设备 GOP 地址来源：`video base 0x9c000000 1600x2560 row 6400 32 bpp`，同次窗口 `0xc007c000+0x20000000`，二者不相交。可见扫描像素至少占 `[0x9c000000,0x9cfa0000)`（6400×2560）；GOP 完整 FrameBufferSize 未由该行确定。此为旧次观测，不能当成 r21/r23/r24 的实测值。

`../uefi-enuma/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c:60` 声明 `Display Reserved` 为 `[0x9c000000,0x9e400000)`，类型 `Reserv`；`../uefi-enuma/Silicon/Silicium/SiliciumPkg/Include/Library/MemoryMapLib.h:92` 定义 `Reserv` 为 `EfiReservedMemoryType`。这提供固件源码预留意图，并非这三次分配时 EFI map 的实测证明。另见 `docs/ufs-reserved-memory-audit.md:120,208-209` 的 FDT 和固件对照。

512 MiB 与 2720 MiB 在目标三轮是否覆盖地址：**均无法判定**，因为缺当轮 EFI memory map、实际窗口基址和 GOP 地址。如果 map 在该区域正确为 reserved，则任何成功的连续 conventional 窗口都不可能覆盖它，不论窗口大小；如果错误标为 conventional，几何上两种大小均可覆盖，窗口大小本身不能排除。举例沿用旧观测基址（不是新次证据），512 MiB 为 `[0xc007c000,0xe007c000)`，2720 MiB 为 `[0xc007c000,0x16a07c000)`，都高于 framebuffer，不相交；见 `docs/enuma-r22-memory-window-host-20261122.md:21-28`。两版可能选择不同地址。

`docs/enuma-r24-census-20261122.md:21-30` 指出 r23 去重核读帧未见不等于从未 exec，r24 见 exec 不证明显示关闭导致差异；更不证明内存重叠导致 backboardd 失败。

## 公开参照

- sirius：UniXNU `docs/zh/devices/sirius-huajifruit.md:217-234` 记 framebuffer `0x9c000000`、窗口 `0x9f87c000+0xaa000000`；该次窗口起点在 framebuffer 之上，未重叠。原文报告 UEFI map，窗口为 loader code，低地址有 reserved 和小空隙；窗口 `0xaa000000` 为 2720 MiB。DTS/ADT dram 几何不是窗口选址参数；`darwinboot-efi-map` 占位符是记录 map，不是保留区或选址。源版本见该文 `:253`。
- sheng：UniXNU `docs/zh/devices/sheng.md:203-209` 记 splash reservation `0xb8000000+0x2b00000`，窗口请求 `0x130000000`（4864 MiB），而非小窗口。[固定版本 board.toml](https://github.com/UniXNU/UniXNU-sheng/blob/516a780473a2ac59c8b438e132bb60204dda9e22/board.toml) 的 `[bootimg] dtb_node` 同样写入 splash reg，`[payload] dram_size=0x80000000`、`[payload.adt] owned_memory_size=0x130000000` 都不是基址。该 splash 为保留区地址，不能无交接记录就断言 GOP 精确基址或实际窗口不重叠；本次未查到 sheng 对应实际分配窗口记录。该 DTB `/reserved-memory` 不是 ADT `/chosen/boot-video`，也不能单凭此证明 EFI 分配期排除。

## 官方文字

`docs/zh/porting/display.md:23-24`：“将 GOP 参数和帧缓冲范围与固件内存映射、板级 DTS 对照，在内核交接期间保留当前扫描缓冲区。”

请求的 `docs/zh/porting/boot-chain.md` 在该检出不存在；实际为 `docs/zh/concepts/boot-chain.md:76-80`：“从 GOP 读取 framebuffer 信息。”“分配连续物理窗口。”“复制段、ADT、trust cache 和 ramdisk。”“构造 `DARWIN_BOOT_ARGS`。”“退出 boot services。”该页没有说明 framebuffer 物理保留机制。

## 最小验证与备选

优先离线检查已有三轮日志，寻找同次实际 `owned` 基址/长度、GOP 地址及分配时 EFI map，对半开区间做交集；单靠 ADT 大小不足。若没有记录，候选对照仅改变 `/chosen/darwinboot-memory-size`（r23 同配置从 2720 MiB 改为 512 MiB），并取得同次交接窗口/GOP；改尺寸也改变内存压力及分配位置，观察 backboardd 差异不能单独证明重叠因果。新设备操作需另获授权。

若实测重叠，离线评估：① 缩小窗口，代价是可用内存及运行稳定性下降，且仍须实测落点；② 固件正确将完整 framebuffer 范围标为 EFI reserved，代价是碎片化、可能导致大窗分配失败，须核查固件所有权及启动链并经 deep review；③ 修改加载器选址到已验证的高地址 conventional run，代价是启动链改动及低地址 DMA 约束，须 deep review；现有大小字段不能直接设置基址。仅 ADT 声明不是已证实的 EFI 排除修法。
