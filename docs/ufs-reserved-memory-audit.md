# enuma `reserved-memory` 与 `UfsDxe` DMA backing 事实整理

状态：**`self-checked`**（纯离线只读静态提取；未做独立复核，未上机，未与运行时内存图交叉验证）
整理日期：2026-11-17
范围：`UniXNU-enuma`（设备仓）、`uefi-enuma`（固件仓）、基线 `UniXNU`（只读）与 `out/ufs-sm8250-policy-20261116-r1/`
本文只列事实与未确定项，不含安全判定、建议或风险结论。

---

## 0. 复跑命令与退出码

全部命令在 WSL Ubuntu-22.04 中执行，工作目录 `/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma`。

| # | 命令 | 退出码 | 用途 |
| --- | --- | --- | --- |
| C1 | `dtc -I dtb -O dts -o /tmp/e1.dts .cache/firmware/dtb/sm8250-xiaomi-enuma.dtb` | 0 | 反编译固件 DTB（`Version: DTC 1.6.1`，仅有 `unit_address_vs_reg`/`graph_port` 等 warning） |
| C2 | `dtc -I dtb -O dts -o /tmp/e2.dts .cache/firmware/fdt.stdout` | 0 | 反编译 pre-root 实机活动 FDT |
| C3 | `cmp -s /tmp/e1.dts .cache/firmware/dtb/sm8250-xiaomi-enuma.dts` | 0 | 仓库内已存的反编译文本与 C1 输出**逐字节相同**，故 §2 行号可直接引用该文件 |
| C4 | `cmp -s /tmp/e2.dts .cache/firmware/fdt-live.dts` | 0 | 同上，活动 FDT 文本一致 |
| C5 | `dtc -I dtb -O dts .cache/firmware/dtb/sm8250-xiaomi-enuma.dtb 2>/dev/null \| sed -n "/^\treserved-memory {$/,/^\t};$/p" \| wc -l` | 0 | 得到 262 行，即 `reserved-memory` 块全文（`.dts` 第 39883–40144 行） |
| C6 | `python3 rm_extract.py /tmp/e1.dts`（临时脚本，见 §0.1） | 0 | 逐子节点导出 `reg`/`no-map`/`reusable`/`compatible`/`size`/`alignment` |
| C7 | `python3 rm_extract.py /tmp/e2.dts` 与 `diff -q` 对比 C6 输出 | 0 / 0 | 固件 DTB 与活动 FDT 的 `reserved-memory` 表**完全相同**（34 条、字段逐项一致） |
| C8 | `python3 dtsinfo.py /tmp/e1.dts` | 0 | 解析 `memory-region` 引用（26 条）与 phandle 目标 |
| C9 | `python3 adt_dump.py .../self-check/extracted/kernel.macho.adt` | 0 | 导出 ADT 结构（§1.3） |
| C10 | `python3 overlap.py`（表内数据来自 C6/MemoryMapLib 源码） | 0 | §4.1 区间重叠计算 |
| C11 | `sha256sum` / `stat`（见各表“字节/SHA-256”列） | 0 | 哈希与大小 |
| C12 | `python3 mdcheck2.py docs/ufs-reserved-memory-audit.md` | 0 | 本文 24 张表的列数一致性（`blocks=24 problems=0`） |
| C13 | `python3 xcheck2.py /tmp/t1.txt docs/ufs-reserved-memory-audit.md` | 0 | §2.1 表逐行与 C6 输出比对（`markdown rows=34 extract names=34 problems=0 missing=[]`） |

### 0.1 临时脚本（仓库外，仅本轮使用，不随报告入库）
- `C:\Users\Administrator\AppData\Local\Temp\opencode\rm_extract.py`：按缩进解析 `dtc -O dts` 文本，输出每个 `reserved-memory` 子节点的 `reg` 对、属性、`compatible`、`size`/`alignment`/`alloc-ranges`。
- `.../dtsinfo.py`：解析整棵 DTS 文本建树，建立 phandle→节点路径映射，导出全部 `memory-region` 引用方与目标。
- `.../adt_dump.py`：按 ADT 节点记录格式（`numProps`,`numChildren`,32 B 属性名,`len`,数据）遍历。
- `.../overlap.py`：把固件 `MemoryMapLib` DDR 行与 DT 固定区间做两两交集。
- `.../mdcheck2.py`（C12）、`.../xcheck2.py`（C13）：表格列数一致性与 §2.1 表数据逐行比对。

---

## 1. DTB 来源与哈希

下表哈希、字节与行号均取自**当前工作区**（2026-11-17）。`dts/enuma.dts`、`board.toml` 在工作区相对 `HEAD` 有未提交改动（`git diff --stat`：`board.toml 8+/-`、`dts/enuma.dts 4+`），本报告引用的是工作区内容。

### 1.1 产物清单

| 路径（相对 `enuma/`） | 字节 | SHA-256 | 生成方式 / 来源 |
| --- | --- | --- | --- |
| `UniXNU-enuma/.cache/firmware/dtb/sm8250-xiaomi-enuma.dtb` | 977523 | `42d36a005024e1a7c55cb5da077a13bb17e9fb9a79dc9dfac8a61cf1e182f698` | `fdtoverlay`：vendor_boot DTB blob0（`324049d7…`，kona v2.1）+ `dtbo-entry07.dtbo`（board-id `0x2e`）。来源记录 `UniXNU-enuma/proprietary-files.txt:23`、`UniXNU-enuma/README.md:115` |
| `UniXNU-enuma/.cache/firmware/dtb/sm8250-xiaomi-enuma.dts` | 1593058 | `1dd9a06aec6a7af677026c3c1dbbd4f05944b6dea4ad2583f26654f469f408b9` | 上者的 `dtc -O dts` 文本；与 C1 输出逐字节相同 |
| `UniXNU-enuma/.cache/firmware/dtbs/blob0.dtb` | 540195 | `324049d746aaa16ada3b425ea5eed30f6d49a90c9d63d5e57ea5a632c27becb8` | vendor_boot_a.img `dtb` 段候选 0（`dtb-report.json`：kona v2.1，`msm-id 356/131073`，board-id `0/0`）；作为叠加基座 |
| `UniXNU-enuma/.cache/firmware/dtbs/blob1.dtb` | 540191 | `0bd93f077080a6e3bedff5cf384ff97fc863667c59e3379cbbe5bbc165c4168e` | 候选 1（kona v2，`msm-id 356/131072`），未参与叠加 |
| `UniXNU-enuma/.cache/firmware/dtbs/blob2.dtb` | 533273 | `afc3540645e5a11351532ce2b5384f27acfb412ee0780ff5a57d72301d5ddb52` | 候选 2（kona v1），未参与叠加 |
| `UniXNU-enuma/.cache/firmware/dtbs/blob3.dtb` | 173 | `8361d34a65c460e64cb6888b6f48f0a337284a47e1c456dd0c02792423585941` | 候选 3（空），未参与叠加 |
| `UniXNU-enuma/.cache/firmware/dtb/dtbo-entry07.dtbo` | 497805 | `ba188a895780a100fa8be3bb9622b0b5d8e1a4b6ad3821260476029251c6362f` | dtbo 表第 7 项（索引方式见 `.cache/firmware/dtb/parse_dtbo.py:23-30`）；overlay 自身文本 `dtbo-entry07.dts:4,6` 为 `model = "Qualcomm Technologies, Inc. xiaomi enuma"`、`qcom,board-id = <0x2e 0x00>` |
| `UniXNU-enuma/.cache/firmware/fdt.stdout` | 941659 | `45a04e08f47245ca5ec4145faf35346e36c014e8425b7cad470a299a98f12472` | pre-root 实机活动 FDT（`adb exec-out cat /sys/firmware/fdt`，见 `.cache/firmware/fdt.stdout.provenance.json`） |
| `UniXNU-enuma/.cache/firmware/fdt-live.dts` | 1558525 | `db567ce4d5fdf0805a5351a3fd65ceb68bbe1fb1a508f78039dd5e30c382f7a8` | 上者的反编译文本 |
| `UniXNU-enuma/dts/enuma.dts` | 1502 | `5ba134685e8442d1f7d7842625ae9786021b4e0e62f475f8f671dfdf285f8111` | 设备 DTS（`board.toml:47-49`：`source = "device:dts/enuma.dts"`，`include_dirs = ["soc:dts"]`）；**无 `reserved-memory` 节点**（第 32-36 行为 TODO 注释） |
| `UniXNU/out/enuma/ipados-17.7.11-21H461/enuma/device-tree/hardware.dtb` | 2776 | `520c4dec8cf0b28346de2f3ac7416f7cc88ec771455ca58a55d2675e2747a7cc` | `dts/enuma.dts` 的 dtc 编译产物（`UniXNU/scripts/unixnu/devicetree.py:392-402`） |
| `UniXNU-enuma/out/ufs-sm8250-policy-20261116-r1/self-check/packaging/out/enuma/ipados-17.7.11-21H461/enuma/device-tree/hardware.dtb` | 2772 | `3191a89547adeed19202190f62f25b35b3d1fc0b44efe6dd87d086676581a3d9` | 该候选自检时同一步的产物；与上一行**不同哈希**（构建时点/源码不同，本轮未逐字节比对差异） |
| `…/ufs-sm8250-policy-20261116-r1/self-check/extracted/kernel.macho.adt` | 13916 | `47a07f11ca86ad3d0baf5b5e0e1947754f78bcc05541e4e95bf4e66c41244e28` | XNU 输入设备树（ADT），见 §1.3 |

### 1.2 用途划分

| 消费者 | 使用的 DTB | 证据 |
| --- | --- | --- |
| UEFI 固件（`UFSDxe`/`HALIOMMU`/`DisplayDxe` 等运行时） | `.cache/firmware/dtb/sm8250-xiaomi-enuma.dtb`，以 `bootimg --dtb` 追加在 `Image-dtb` 里 | `UniXNU/scripts/unixnu/bootimg.py:83,93,104`（`combined = shim + firmware`，`kernel = … + tree`）；`bootimg.py:93` 的 `patch_dtb(..., ctx.board.get('bootimg',{}).get('dtb_node',[]))`，而 `board.toml` 无 `[bootimg]`，故无节点改写 |
| UEFI FD 内嵌 DTB（`FdtBlob`） | **未使用**：`enuma.fdf:105-110` 整段被注释 | `uefi-enuma/Platforms/Xiaomi/enumaPkg/enuma.fdf:105-110` |
| XNU ADT | `device:dts/enuma.dts`（+`soc:dts`）经 dtc 编译后由 `generate()` 转成 ADT；**不是** 42d36a00 那份 | `UniXNU/scripts/unixnu/payload.py:191-196`、`devicetree.py:290-389,392-402`；`board.toml:47-49` |

`proprietary-files.txt:23` 记录该固件 DTB「differs from the live FDT only in root board-id/model, /memory and vendor fstab status」；本轮实测与之相符（§1.3）。

### 1.3 三棵树的根身份与内存节点（实测）

| 项 | 42d36a00 固件 DTB | 活动 FDT（fdt.stdout） | ADT（kernel.macho.adt） |
| --- | --- | --- | --- |
| `model` | `Qualcomm Technologies, Inc. kona v2.1 SoC`（`.dts:4`） | `Qualcomm Technologies, Inc. xiaomi enuma`（`fdt-live.dts:4`） | `iPad7,1` |
| `qcom,msm-id` | `<0x164 0x20001>`（`.dts:6`） | `<0x164 0x20001>`（`fdt-live.dts:6`） | 无 |
| `qcom,board-id` | `<0x00 0x00>`（`.dts:10`） | `<0x2e 0x00>`（`fdt-live.dts:10`） | 无 |
| 根 `compatible` | `qcom,kona`（`dtb-report.json` candidates[0]） | `qcom,kona-mtp`,`qcom,kona`,`qcom,mtp` | `xiaomi,enuma\0qcom,sm8250\0` |
| `/memory` | `reg = <0x00 0x00 0x00 0x00>`（空，`.dts:12-15`） | `reg = <0x00 0x80000000 0x00 0x3bb00000 0x01 0x80000000 0x01 0x00 0x00 0xc0000000 0x00 0xc0000000>`（`fdt-live.dts:12-15`，三段） | 无 `/memory`；DRAM 走 `/chosen/dram-base=0x80000000`、`/chosen/dram-size=0x200000000` |
| `reserved-memory` | 34 个子节点（§2.1） | 34 个子节点，逐项与左列相同（C7） | **无 `reserved-memory` 节点**（C9 导出只有 `/chosen`、`/cpus`、`/psci`、`/arm-io`、`/defaults`、`/options`、`/product`） |
| `/chosen` 关键属性 | — | — | `darwinboot-memory-size = 0x0000002000000000`（`struct.pack('<Q', 0x20000000)`，即 512 MiB，见 `devicetree.py:319-323` 与 `board.toml:87`）、`dram-base=0x80000000`、`dram-size=0x200000000`、`root-matching`（UUID `9071148B-B025-402D-AD7A-48464D8B5FFF`，`board.toml:93`）、`chip-id`/`unique-chip-id`、`text-fixups`、manifest 与 AMFI 相关属性 |
| `/arm-io` | — | — | `ranges = <0x0 0x01000000 0x17000000>`（窗口 base `0x01000000`、size `0x17000000`）；子节点 `intc`、`ufshc` |

ADT 结构（C9）：`/chosen/{memory-map(TrustCache), manifest-properties}`、`/cpus/cpu0..cpu7`、`/psci`、`/arm-io/{intc,ufshc}`、`/defaults`、`/options`、`/product`。`generate()` 不复制源 DTB 的 `reserved-memory`（`devicetree.py:290-389` 无该分支）。

---

## 2. `reserved-memory` 全表

节点容器属性（`.dts:39883-39887`，第 39888 行为空行）：`#address-cells = <0x02>`、`#size-cells = <0x02>`、`ranges`、`phandle = <0x642>`。

### 2.1 全部 34 个子节点

来源：C5/C6 + `.cache/firmware/dtb/sm8250-xiaomi-enuma.dts` 行号（下表「行」列）。`no-map`/`reusable` 列内 `-` 表示无该属性。

| 行 | 节点名 | `reg` base | `reg` size | 区间 `[start,end)` | base(dec) | size(dec) | no-map | reusable | compatible | 其他属性 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39889 | `hyp_region@80000000` | `0x80000000` | `0x600000` | `[0x80000000,0x80600000)` | 2147483648 | 6291456 | yes | - | - | - |
| 39895 | `xbl_aop_region@80700000` | `0x80600000` | `0x260000` | `[0x80600000,0x80860000)` | 2153775104 | 2490368 | yes | - | - | 节点名带 `@80700000`，`reg` base 为 `0x80600000`（见 §2.3） |
| 39901 | `reserved-memory@80860000` | `0x80860000` | `0x20000` | `[0x80860000,0x80880000)` | 2156265472 | 131072 | yes | - | `qcom,cmd-db` | - |
| 39908 | `res_xbl_uefi_log_region@80880000` | `0x80880000` | `0x14000` | `[0x80880000,0x80894000)` | 2156396544 | 81920 | yes | - | `removed-dma-pool` | - |
| 39915 | `smem_region@80900000` | `0x80900000` | `0x200000` | `[0x80900000,0x80b00000)` | 2156920832 | 2097152 | yes | - | - | phandle `0x84` |
| 39921 | `removed_region@80b00000` | `0x80b00000` | `0x5300000` | `[0x80b00000,0x85e00000)` | 2159017984 | 87031808 | yes | - | - | - |
| 39927 | `pil_camera_region@86200000` | `0x86200000` | `0x500000` | `[0x86200000,0x86700000)` | 2250244096 | 5242880 | yes | - | `removed-dma-pool` | - |
| 39934 | `pil_wlan_fw_region@86700000` | `0x86700000` | `0x100000` | `[0x86700000,0x86800000)` | 2255486976 | 1048576 | yes | - | `removed-dma-pool` | - |
| 39941 | `pil_ipa_fw_region@86800000` | `0x86800000` | `0x10000` | `[0x86800000,0x86810000)` | 2256535552 | 65536 | yes | - | `removed-dma-pool` | - |
| 39948 | `pil_ipa_gsi_region@86810000` | `0x86810000` | `0xa000` | `[0x86810000,0x8681a000)` | 2256601088 | 40960 | yes | - | `removed-dma-pool` | - |
| 39955 | `pil_gpu_region@8681a000` | `0x8681a000` | `0x2000` | `[0x8681a000,0x8681c000)` | 2256642048 | 8192 | yes | - | `removed-dma-pool` | - |
| 39962 | `pil_npu_region@86900000` | `0x86900000` | `0x500000` | `[0x86900000,0x86e00000)` | 2257584128 | 5242880 | yes | - | `removed-dma-pool` | - |
| 39969 | `pil_video_region@86e00000` | `0x86e00000` | `0x500000` | `[0x86e00000,0x87300000)` | 2262827008 | 5242880 | yes | - | `removed-dma-pool` | - |
| 39976 | `pil_cvp_region@87300000` | `0x87300000` | `0x500000` | `[0x87300000,0x87800000)` | 2268069888 | 5242880 | yes | - | `removed-dma-pool` | - |
| 39983 | `pil_cdsp_region@87800000` | `0x87800000` | `0x1400000` | `[0x87800000,0x88c00000)` | 2273312768 | 20971520 | yes | - | `removed-dma-pool` | - |
| 39990 | `pil_slpi_region@88c00000` | `0x88c00000` | `0x2f00000` | `[0x88c00000,0x8bb00000)` | 2294284288 | 49283072 | yes | - | `removed-dma-pool` | - |
| 39997 | `pil_adsp_region@8bb00000` | `0x8bb00000` | `0x2500000` | `[0x8bb00000,0x8e000000)` | 2343567360 | 38797312 | yes | - | `removed-dma-pool` | - |
| 40004 | `pil_spss_region@8e000000` | `0x8e000000` | `0x100000` | `[0x8e000000,0x8e100000)` | 2382364672 | 1048576 | yes | - | `removed-dma-pool` | - |
| 40011 | `cdsp_secure_heap@8e100000` | `0x8e100000` | `0x4600000` | `[0x8e100000,0x92700000)` | 2383413248 | 73400320 | yes | - | `removed-dma-pool` | - |
| 40018 | `adsp_region` | 无 `reg` | `0xc00000`(size) | 运行时放置 | - | 12582912 | - | yes | `shared-dma-pool` | `alloc-ranges = <0x0 0x0 0x0 0xffffffff>`、`alignment = 0x400000` |
| 40027 | `sdsp_region` | 无 `reg` | `0x800000`(size) | 运行时放置 | - | 8388608 | - | yes | `shared-dma-pool` | 同上 |
| 40036 | `cdsp_region` | 无 `reg` | `0x400000`(size) | 运行时放置 | - | 4194304 | - | yes | `shared-dma-pool` | 同上 |
| 40045 | `cont_splash_region@9c000000` | `0x9c000000` | `0x2300000` | `[0x9c000000,0x9e300000)` | 2617245696 | 36700160 | - | - | - | `label = "cont_splash_region"` |
| 40051 | `disp_rdump_region@9c000000` | `0xb0400000` | `0x1000000` | `[0xb0400000,0xb1400000)` | 2956984320 | 16777216 | yes | - | `removed-dma-pool` | `label = "disp_rdump_region"`；节点名 `@9c000000` 与 `reg` base 不符（§2.3） |
| 40059 | `dfps_data_region@9e300000` | `0x9e300000` | `0x100000` | `[0x9e300000,0x9e400000)` | 2653945856 | 1048576 | - | - | - | `label = "dfps_data_region"` |
| 40065 | `mem_dump_region` | 无 `reg` | `0x2800000`(size) | 运行时放置 | - | 41943040 | - | yes | `shared-dma-pool` | `alloc-ranges = 同 0..0xffffffff`，无 `alignment` |
| 40073 | `sp_region` | 无 `reg` | `0x1000000`(size) | 运行时放置 | - | 16777216 | - | yes | `shared-dma-pool` | `alignment = 0x400000` |
| 40082 | `user_contig_region` | 无 `reg` | `0x1000000`(size) | 运行时放置 | - | 16777216 | - | yes | `shared-dma-pool` | `alignment = 0x400000` |
| 40091 | `qseecom_region` | 无 `reg` | `0x1400000`(size) | 运行时放置 | - | 20971520 | - | yes | `shared-dma-pool` | `alignment = 0x400000` |
| 40100 | `qseecom_ta_region` | 无 `reg` | `0x1000000`(size) | 运行时放置 | - | 16777216 | - | yes | `shared-dma-pool` | `alignment = 0x400000` |
| 40109 | `secure_display_region` | 无 `reg` | `0xa400000`(size) | 运行时放置 | - | 171966464 | - | yes | `shared-dma-pool` | `alignment = 0x400000` |
| 40118 | `cnss_wlan_region` | 无 `reg` | `0x1400000`(size) | 运行时放置 | - | 20971520 | - | yes | `shared-dma-pool` | `alignment = 0x400000` |
| 40127 | `linux,cma` | 无 `reg` | `0x2000000`(size) | 运行时放置 | - | 33554432 | - | yes | `shared-dma-pool` | `alignment = 0x400000`、`linux,cma-default` |
| 40136 | `mailbox_region` | 无 `reg` | `0x20000`(size) | 运行时放置 | - | 131072 | yes | - | `shared-dma-pool` | `alloc-ranges = 同 0..0xffffffff`、`alignment = 0x400000` |

计数：固定 `reg` 节点 22 个；仅有 `size`（+ 可选 `alignment`/`alloc-ranges`）节点 12 个；`compatible` 为 `removed-dma-pool` 的 15 个、`shared-dma-pool` 的 12 个（C6，与 `dtb-report.json` 全树计数 15/12 一致）。

### 2.2 `memory-region` 引用（26 条，全部 `status=okay`）

来源：C8（引用关系）+ `grep -n 'memory-region' .cache/firmware/dtb/sm8250-xiaomi-enuma.dts`（「行」列为该 `memory-region` 属性所在行）。

| 引用节点 | 行 | phandle | → `reserved-memory` 目标 |
| --- | --- | --- | --- |
| `/soc/qseecom@82400000` | 9232 | `0x5f` | `qseecom_region` |
| `/soc/qcom,smem` | 7800 | `0x84` | `smem_region@80900000` |
| `/soc/qcom,ipa_fws` | 7895 | `0x89` | `pil_ipa_gsi_region@86810000` |
| `/soc/qcom,ipa_uc` | 7903 | `0x8a` | `pil_ipa_fw_region@86800000` |
| `/soc/qcom,lpass@17300000` | 8202 | `0x95` | `pil_adsp_region@8bb00000` |
| `/soc/qcom,turing@8300000` | 8228 | `0x98` | `pil_cdsp_region@87800000` |
| `/soc/qcom,venus@aab0000` | 8261 | `0x9c` | `pil_video_region@86e00000` |
| `/soc/qcom,spss@1880000` | 8284 | `0x88` | `pil_spss_region@8e000000` |
| `/soc/qcom,cvpss@abb0000` | 8297 | `0x9d` | `pil_cvp_region@87300000` |
| `/soc/qcom,npu@9800000` | 8306 | `0x9e` | `pil_npu_region@86900000` |
| `/soc/qcom,msm-adsprpc-mem` | 8326 | `0xa2` | `adsp_region`（动态） |
| `/soc/mem_dump` | 8549 | `0xa3` | `mem_dump_region`（动态） |
| `/soc/qcom,ssc@5c00000` | 8929 | `0xa4` | `pil_slpi_region@88c00000` |
| `/soc/msm_tspp@8880000` | 4514 | `0x5f` | `qseecom_region` |
| `/soc/qcom,ion/qcom,ion-heap@22` | 11663 | `0x160` | `sdsp_region`（动态） |
| `/soc/qcom,ion/qcom,ion-heap@26` | 11676 | `0x161` | `user_contig_region`（动态） |
| `/soc/qcom,ion/qcom,ion-heap@27` | 11682 | `0x5f` | `qseecom_region` |
| `/soc/qcom,ion/qcom,ion-heap@19` | 11688 | `0x162` | `qseecom_ta_region`（动态） |
| `/soc/qcom,ion/qcom,ion-heap@13` | 11694 | `0x163` | `sp_region`（动态） |
| `/soc/qcom,ion/qcom,ion-heap@10` | 11700 | `0x164` | `secure_display_region`（动态） |
| `/soc/qcom,ion/qcom,ion-heap@14/cdsp` | 11709 | `0x165` | `cdsp_secure_heap@8e100000` |
| `/soc/qcom,pcie@1c00000/pcie0_rp/cnss_pci` | 11782 | `0x16e` | `cnss_wlan_region`（动态） |
| `/soc/qcom,mdss_dsi_pll@ae94900` | 32226 | `0x24f` | `dfps_data_region@9e300000` |
| `/soc/qcom,cam_smmu/msm_cam_icp_fw` | 32953 | `0x25d` | `pil_camera_region@86200000` |
| `/soc/qcom,msm-audio-apr/qcom,voice-mhi-audio` | 38308 | `0x33b` | `mailbox_region`（动态） |
| `/soc/qcom,cvp@ab00000/qcom,msm-cvp,mem_cdsp` | 39012 | `0x33f` | `cdsp_region`（动态） |

未出现在任何 `memory-region` 引用中（但仍被保留）的固定区间：`hyp_region@80000000`、`xbl_aop_region@80700000`、`reserved-memory@80860000`、`res_xbl_uefi_log_region@80880000`、`removed_region@80b00000`、`cont_splash_region@9c000000`、`disp_rdump_region@9c000000`、`pil_gpu_region@8681a000`。

### 2.3 节点名与 `reg` 不一致的两处（原文事实）

| 节点 | 节点名后缀 | `reg` base | 说明 |
| --- | --- | --- | --- |
| `xbl_aop_region@80700000` | `80700000` | `0x80600000`（`.dts:39897`） | 区间覆盖 `0x80600000–0x80860000`，跨越固件图的 `MPSS EFS` 与 `BOOT INFO` 两行（§2.5） |
| `disp_rdump_region@9c000000` | `9c000000` | `0xb0400000`（`.dts:40054`） | 实际区间 `0xb0400000–0xb1400000`；与 `cont_splash_region`/`dfps_data_region`（`0x9c000000–0x9e400000`）无交集 |

### 2.4 UFS / SMMU 相关 DT 节点（事实摘录）

来源：C5 + `.dts` 行号。

| 节点 | 行 | 关键属性 |
| --- | --- | --- |
| `/soc/ufshc@1d84000` | 6667 | `compatible = "qcom,ufshc"`；`reg = <0x1d84000 0x3000 0x1d90000 0x8000>`、`reg-names = "ufs_mem","ufs_ice"`；`interrupts = <0x00 0x109 0x04>`；`phys`/`phy-names = "ufsphy"`；9 个 clock；`lanes-per-direction = <0x02>`；`status = "ok"`。**无 `iommus`、无 `memory-region`** |
| `/soc/ufsphy_mem@1d87000` | 6650 | `compatible = "qcom,ufs-phy-qmp-v4"`；`reg = <0x1d87000 0xe00 0x1d90000 0x8000>`；`status = "ok"` |
| `/soc/ufscardice@1db0000` | 6748 | `compatible = "qcom,ice"`；`reg = <0x1db0000 0x8000>` |
| `/soc/ufsphy_card@1da7000`、`/soc/ufshc_card@1da4000` | 6765 / 6777 | `status = "disabled"` |
| `/soc/apps-smmu@15000000` | 12766 | `compatible = "qcom,qsmmu-v500"`；`reg = <0x15000000 0x100000 0x15182000 0x20>`、`reg-names = "base","tcu-base"`；`#iommu-cells = <0x02>`；`#global-interrupts = <0x02>`；`qcom,skip-init`；`qcom,use-3-lvl-tables` |

`ufshc` 的 `iommus` 缺席在固件 DTB 与活动 FDT 中都成立（C2/C5 同一 `reserved-memory`、同一节点属性集合，见 C7 与 §1.3）。

### 2.5 固件侧 XBL 内存图（`MemoryMapLib` DDR 行，静态声明）

来源：`uefi-enuma/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c:48-75`；文件头注释（同文件 `:5-7`）声明 DDR 行逐行取自 enuma `xbl_a`（sha256 `7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057`）内 `uefiplat.cfg [MemoryMap]`。

| 行 | 名称 | base | length | 区间 | MemoryType / 属性 |
| --- | --- | --- | --- | --- | --- |
| 48 | HYP | `0x80000000` | `0x005D0000` | `[0x80000000,0x805D0000)` | Reserv / UNCACHED_UNBUFFERED_XN |
| 49 | IPC SHM | `0x805D0000` | `0x00020000` | `[0x805D0000,0x805F0000)` | BsData / WRITE_BACK_XN |
| 50 | MPSS EFS | `0x80600000` | `0x00100000` | `[0x80600000,0x80700000)` | Reserv |
| 51 | BOOT INFO | `0x80700000` | `0x00100000` | `[0x80700000,0x80800000)` | BsData |
| 52 | AOP CMD DB | `0x80860000` | `0x00020000` | `[0x80860000,0x80880000)` | Reserv / UNCACHEABLE |
| 53 | XBL Log Buffer | `0x80884000` | `0x00010000` | `[0x80884000,0x80894000)` | Reserv |
| 54 | SMEM | `0x80900000` | `0x00200000` | `[0x80900000,0x80B00000)` | Reserv / UNCACHEABLE |
| 55 | TZApps | `0x82400000` | `0x03A00000` | `[0x82400000,0x85E00000)` | Reserv / UNCACHEABLE |
| 56 | PIL Reserved | `0x86000000` | `0x0D200000` | `[0x86000000,0x93200000)` | Reserv / UNCACHEABLE |
| 57 | DXE Heap 2 | `0x93200000` | `0x05700000` | `[0x93200000,0x98900000)` | Conv（`MemoryMapLib.c:22-30` 记为实验性新增） |
| 58 | DXE Heap | `0x98900000` | `0x03300000` | `[0x98900000,0x9BC00000)` | Conv |
| 59 | Sched Heap | `0x9BC00000` | `0x00400000` | `[0x9BC00000,0x9C000000)` | BsData |
| 60 | Display Reserved | `0x9C000000` | `0x02400000` | `[0x9C000000,0x9E400000)` | Reserv / WRITE_THROUGH_XN |
| 61 | DBI Dump | `0x9E400000` | `0x00F00000` | `[0x9E400000,0x9F300000)` | MMAP_IO |
| 62 | FV Region | `0x9F800000` | `0x00200000` | `[0x9F800000,0x9FA00000)` | BsData |
| 63 | ABOOT FV | `0x9FA00000` | `0x00200000` | `[0x9FA00000,0x9FC00000)` | Reserv |
| 64 | UEFI FD | `0x9FC00000` | `0x00300000` | `[0x9FC00000,0x9FF00000)` | BsData |
| 65 | SEC Heap | `0x9FF00000` | `0x0008C000` | `[0x9FF00000,0x9FF8C000)` | BsData |
| 66 | CPU Vectors | `0x9FF8C000` | `0x00001000` | `[0x9FF8C000,0x9FF8D000)` | BsData |
| 67 | MMU PageTables | `0x9FF8D000` | `0x00003000` | `[0x9FF8D000,0x9FF90000)` | BsData |
| 68 | UEFI Stack | `0x9FF90000` | `0x00040000` | `[0x9FF90000,0x9FFD0000)` | BsData |
| 69 | Log Buffer | `0x9FFF7000` | `0x00008000` | `[0x9FFF7000,0x9FFFF000)` | RtData |
| 70 | Info Blk | `0x9FFFF000` | `0x00001000` | `[0x9FFFF000,0xA0000000)` | RtData |
| 71 | Kernel | `0xA0000000` | `0x10000000` | `[0xA0000000,0xB0000000)` | Reserv |
| 75 | RAMOOPS | `0xB0000000` | `0x00400000` | `[0xB0000000,0xB0400000)` | Reserv / UNCACHEABLE（`:72-75` 注释：stock ramoops 4 MiB，console zone `0xB0000000/0x200000`） |

MMIO 行（同文件 `:78-102`）与本报告无关区间计算，其中与 UFS/SMMU 相关两条：`SMMU 0x15000000 / 0x000D0000`（`:101`）、`APSS_HM 0x17800000 / 0x0d981000`（`:102`）。

### 2.6 DT 与固件内存图的逐项差异（仅列差异，不下判断）

| 项 | DT（§2.1） | 固件 `MemoryMapLib`（§2.5） |
| --- | --- | --- |
| HYP 长度 | `0x600000`（`0x80000000–0x80600000`） | `0x005D0000`（`0x80000000–0x805D0000`）；`MemoryMapLib.c:13-17` 记录该缩短为用户 2026-11-07 选定、`0x805D0000–0x80600000` 归 IPC SHM |
| IPC SHM `0x805D0000/0x20000` | 无对应节点（落在 DT `hyp_region` 内） | 有独立行（`:49`） |
| XBL log | `res_xbl_uefi_log_region@80880000 [0x80880000,0x80894000)` | `XBL Log Buffer 0x80884000/0x10000`（低 4 KiB 差异） |
| BOOT INFO `0x80700000/0x100000` | 落在 `xbl_aop_region@80700000` 的 `reg` 区间内（无独立节点） | 有独立行 |
| Display 预留 | `cont_splash_region 0x9C000000+0x2300000` + `dfps_data_region 0x9E300000+0x100000` | `Display Reserved 0x9C000000+0x02400000`（连续 36 MiB，`0x9C000000–0x9E400000`） |
| `disp_rdump_region` `0xB0400000+0x1000000` | 有 | 无对应行（固件 `RAMOOPS` 止于 `0xB0400000`） |
| SMMU 窗口 | `apps-smmu@15000000` `reg base 0x15000000 len 0x100000` | `SMMU 0x15000000/0x000D0000`；候选 `UfsWarmTarget` 用 `0x15000000/0xd0000`（`RootWarmTarget.h:15`） |

---

## 3. `UfsDxe` / 固件 DMA backing 范围

### 3.1 固件 UFS 驱动本体

| 事实 | 值 | 来源 |
| --- | --- | --- |
| 模块 | `Binaries/enuma/UFSDxe/UFSDxe.efi`（**厂商预编译二进制，仓库无源码**；`Binaries/enuma/` 在 `.gitignore` 内） | `uefi-enuma/Binaries/enuma/UFSDxe/UFSDxe.inf`、`uefi-enuma/.gitignore` |
| 大小 / SHA-256 | 118784 B / `ffeaed467f8251b7e30a45075da84a1c563e2bac7dc4be0f79f0ed49a88b8dc9` | `Get-FileHash`（C11） |
| 模块类型 / FILE_GUID | `DXE_RUNTIME_DRIVER` / `0d35cd8e-97ea-4f9a-96af-0f0d89f76567` | `UFSDxe.inf:5-6` |
| 依赖表达式 | `UFSDxe.depex` 36 B：`PUSH GUID f4e5c7d0-39d2-47cb-aacd-7f66ef763802`、`PUSH GUID fa5f306b-7df4-4ac4-a47d-882f8204ec30`、`AND`、`END` | `Format-Hex` 结果 + EDK2 depex 操作码（协议名本轮未映射） |
| 打包路径 | FDF `!include Include/DXE.inc` → `DXE.inc:80 INF Binaries/enuma/UFSDxe/UFSDxe.inf`；`APRIORI.inc:69` 同项；`Vendor.fdf.inc:42` 同项 | `enuma.fdf:83` |
| DSC | `enuma.dsc [Components]`（`:129-141`）**不含** UFSDxe，也无 `!include EnumaInputs/Vendor.dsc.inc`（全仓 grep `Vendor.dsc.inc`/`ENUMA_VENDOR_DSC` 无命中）；`Vendor.dsc.inc:43` 仍列有 `Binaries/enuma/UFSDxe/UFSDxe.inf` | 本表命令 |
| 构建产物 | `Build/enumaPkg/RELEASE_CLANGPDB/FV/Ffs/0d35cd8e-…UFSDxe/` 内有 `.ffs`(118870 B)、`SEC2.1.pe32`(118788 B)、`.dpx`(40 B)、`.ui`(18 B)；`ls -l` 显示 `Nov 8 15:26`（未显示年份） | 目录列举 |
| 缓冲区 / 请求列表 / PRDT 地址 | **运行时分配、静态不可得**：无源码、无 DTB 固定窗口可引用，本轮未反汇编该二进制 | 见 §3.3、§6 |
| `[Configs]` 中 UFS 调参 | `uefi-enuma/Resources/Configs/enuma.toml` 只有 `[boot_shim]`/`[uefi_fd] 0x9FC00000/0x300000`/`[boot_image*]`，无 UFS 缓冲或预留项 | 该文件全文 |

同一厂商目录下另有 `Binaries/enuma/HALIOMMU/HALIOMMU.inf`（`Vendor.dsc.inc:17`、`APRIORI.inc:46`、`DXE.inc:73`、`Vendor.fdf.inc:16`），同为无源码二进制；`UFSDxe` 是否经该 IOMMU 协议取映射，本轮未取得证据。

### 3.2 仓库内可得源码中的固件分配调用点

| 组件 | 是否在当前 enuma 构建中 | 分配调用点 | 大小/上限（源码常量） |
| --- | --- | --- | --- |
| `EnumaSmmu4KIoMmuDxe` | **否**：`enumaPkg` 内除自身目录外无任何 DSC/FDF/`.inc` 引用（全仓 grep 命中仅 `Drivers/EnumaSmmu4KIoMmuDxe/` 下的 `.inf` / `.c` / `.h` 自身） | `EnumaSmmu4KIoMmuDxe.c:376` `gBS->AllocatePages(AllocateMaxAddress, MemoryType, Pages, &Physical)`；上限 `Physical = MAX_UINT32`，若带 `EDKII_IOMMU_ATTRIBUTE_DUAL_ADDRESS_CYCLE` 则为 `(1ULL << S->Arena.config.output_bits) - 1`（`:374-375`）；另 `:220` `AllocatePool(Count * sizeof(*Before))`（token 快照，非 DMA 缓冲） | `Pages` 由调用方给出；`Host` 指针回填 `B->Host`（`:381`） |
| `EnumaSmmu4KTableLib` | **否**（同上，仅被未构建的 IoMmu 驱动使用） | `EnumaSmmu4KTableLib.c:93` `gBS->AllocatePages(AllocateMaxAddress, EfiBootServicesData, Pages, &Base)`，`Base` 初值 `(1ULL << 36) - 1`（`:71`）；参数校验 `Pages <= PageBudget`、`Bytes <= 1<<36`（`:85-91`） | 页表池；`Memory->pools[0].physical = Base`（`:102`） |
| `EnumaUfsIdentityDxe` | **否**（`enuma.dsc` 无引用；仅 `HostTest.c` 内为宿主测试提供 `malloc` 包装，`QrHost.c:13-15`） | 无 `gBS->Allocate*` | — |
| `RamoopsLogLib` | 是（AdvancedLoggerLib 体系） | 使用固定 `RAMOOPS 0xB0000000/0x00400000` 区间（`MemoryMapLib.c:75`），非 UFS | — |

即：当前 enuma 固件里没有任何**开源源码**能给出 UFS 请求列表/PRDT 的静态地址；唯一的 UFS 驱动是 §3.1 的预编译二进制。

### 3.3 DTB 中是否存在给 UFS 的固定内存窗口

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| `/soc/ufshc@1d84000` 的 `memory-region` | 不存在 | §2.4；C8 的 26 条引用清单里无该节点 |
| `/soc/ufshc@1d84000` 的 `iommus` | 不存在 | §2.4 |
| `/soc/ufsphy_mem@1d87000` 的 `memory-region`/`iommus` | 不存在 | 同文件 6650-6665 行属性列表 |
| 任何以 UFS 命名的 `reserved-memory` 子节点 | 无（34 条见 §2.1） | C5 |

### 3.4 UFS/SMMU 的静态地址窗口（MMIO，非 DMA）

| 项 | 值 | 来源 |
| --- | --- | --- |
| UFS HC（DT） | `ufs_mem 0x1d84000+0x3000`、`ufs_ice 0x1d90000+0x8000` | `.dts:6683-6684` |
| UFS PHY（DT） | `phy_mem 0x1d87000+0xe00`、`ufs_ice 0x1d90000+0x8000` | `.dts:6657-6658` |
| UFS HC（ADT，XNU 视角） | `/arm-io/ufshc`：`compatible = "qcom,sm8250-ufshc","qcom,ufshc"`，`reg = <0xd84000 0x3000>`；`/arm-io.ranges = <0x0 0x01000000 0x17000000>`，故物理 `0x01000000+0xd84000 = 0x1d84000` | C9 |
| `apps-smmu`（DT） | `base 0x15000000+0x100000`、`tcu-base 0x15182000+0x20` | `.dts:12768-12769` |
| `apps-smmu`（固件图） | `0x15000000/0x000D0000` | `MemoryMapLib.c:101` |
| `apps-smmu`（候选驱动绑定值） | `smmuBase 0x15000000`、`smmuSize 0xd0000`；同结构另有 `gccBase 0x100000`、`gccSize 0x78000` | `RootWarmTarget.h:15` + `UfsReuseAdmission.h:25-27`（字段顺序 `valid,hcBase,hcSize,gccBase,gccSize,smmuBase,smmuSize`） |

---

## 4. 重叠判定表

### 4.1 静态可判定区间（DT `reserved-memory` × 固件 `MemoryMapLib` DDR 行）

计算：`overlap = max(start) .. min(end)`，仅列非空交集（C10，退出码 0）。

| 固件行 | 固件区间 | DT 节点 | DT 区间 | 是否重叠 | 重叠字节 |
| --- | --- | --- | --- | --- | --- |
| HYP | `0x80000000+0x5D0000` | `hyp_region@80000000` | `0x80000000+0x600000` | 是 | `0x5D0000` |
| IPC SHM | `0x805D0000+0x20000` | `hyp_region@80000000` | `0x80000000+0x600000` | 是 | `0x20000` |
| MPSS EFS | `0x80600000+0x100000` | `xbl_aop_region@80700000` | `0x80600000+0x260000` | 是 | `0x100000` |
| BOOT INFO | `0x80700000+0x100000` | `xbl_aop_region@80700000` | 同上 | 是 | `0x100000` |
| AOP CMD DB | `0x80860000+0x20000` | `reserved-memory@80860000` | `0x80860000+0x20000` | 是 | `0x20000` |
| XBL Log Buffer | `0x80884000+0x10000` | `res_xbl_uefi_log_region@80880000` | `0x80880000+0x14000` | 是 | `0x10000` |
| SMEM | `0x80900000+0x200000` | `smem_region@80900000` | `0x80900000+0x200000` | 是 | `0x200000` |
| TZApps | `0x82400000+0x3A00000` | `removed_region@80b00000` | `0x80b00000+0x5300000` | 是 | `0x3A00000` |
| PIL Reserved | `0x86000000+0xD200000` | `pil_camera_region@86200000` | `0x86200000+0x500000` | 是 | `0x500000` |
| PIL Reserved | 同上 | `pil_wlan_fw_region@86700000` | `0x86700000+0x100000` | 是 | `0x100000` |
| PIL Reserved | 同上 | `pil_ipa_fw_region@86800000` | `0x86800000+0x10000` | 是 | `0x10000` |
| PIL Reserved | 同上 | `pil_ipa_gsi_region@86810000` | `0x86810000+0xa000` | 是 | `0xA000` |
| PIL Reserved | 同上 | `pil_gpu_region@8681a000` | `0x8681a000+0x2000` | 是 | `0x2000` |
| PIL Reserved | 同上 | `pil_npu_region@86900000` | `0x86900000+0x500000` | 是 | `0x500000` |
| PIL Reserved | 同上 | `pil_video_region@86e00000` | `0x86e00000+0x500000` | 是 | `0x500000` |
| PIL Reserved | 同上 | `pil_cvp_region@87300000` | `0x87300000+0x500000` | 是 | `0x500000` |
| PIL Reserved | 同上 | `pil_cdsp_region@87800000` | `0x87800000+0x1400000` | 是 | `0x1400000` |
| PIL Reserved | 同上 | `pil_slpi_region@88c00000` | `0x88c00000+0x2f00000` | 是 | `0x2F00000` |
| PIL Reserved | 同上 | `pil_adsp_region@8bb00000` | `0x8bb00000+0x2500000` | 是 | `0x2500000` |
| PIL Reserved | 同上 | `pil_spss_region@8e000000` | `0x8e000000+0x100000` | 是 | `0x100000` |
| PIL Reserved | 同上 | `cdsp_secure_heap@8e100000` | `0x8e100000+0x4600000` | 是 | `0x4600000` |
| Display Reserved | `0x9C000000+0x2400000` | `cont_splash_region@9c000000` | `0x9c000000+0x2300000` | 是 | `0x2300000` |
| Display Reserved | 同上 | `dfps_data_region@9e300000` | `0x9e300000+0x100000` | 是 | `0x100000` |
| RAMOOPS | `0xB0000000+0x400000` | （无） | — | 否 | — |

DT 固定区间中**不被任何固件 DDR 行覆盖**的只有：`disp_rdump_region@9c000000`（`0xB0400000+0x1000000`）。其余 21 个固定区间全部落在固件行内（上表已逐条列出）。

### 4.2 无法静态判定的项

| 范围 A | 范围 B | 判定 | 原因 |
| --- | --- | --- | --- |
| `UFSDxe.efi` 的请求列表 / PRDT / UCD / 数据缓冲 | §2.1 全部 34 条 | **无法静态判定** | 无源码、无 DTB 窗口、本轮未反汇编（§3.1/§3.3） |
| `HALIOMMU.efi` 的映射表/缓冲 | 同上 | **无法静态判定** | 无源码二进制（`Vendor.dsc.inc:17`） |
| `EnumaSmmu4KIoMmuDxe` / `EnumaSmmu4KTableLib` 的 `AllocatePages` 结果 | 同上 | **无法静态判定**（且这两个组件不在当前构建中） | 地址由 `AllocateMaxAddress` 运行时决定，上界见 §3.2 |
| 候选驱动 `gHost.dma`（`kDmaBytes=139264`） | 同上 | **无法静态判定** | `IOBufferMemoryDescriptor::inTaskWithOptions` 运行时分配（§5） |
| 候选诊断路径 `enumaReadExecute` 的 `Layout`（139264 B） | 同上 | **无法静态判定** | 同上 |
| 12 个 `shared-dma-pool` 节点（`adsp/sdsp/cdsp/mem_dump/sp/user_contig/qseecom/qseecom_ta/secure_display/cnss_wlan/linux,cma/mailbox`）的落点 | 固件 DDR 行 | **无法静态判定** | 只有 `size`/`alignment`/`alloc-ranges <0 0 0 0xffffffff>`，无 `reg`（§2.1） |
| `removed_region@80b00000` 内部构成（ATF/XBL 实际占用） | — | **无法静态判定** | DT 只给整体区间；无 ATF/XBL 侧映射表证据 |

### 4.3 区间关系（同一棵树内部，供对照）

| 关系 | 数值 |
| --- | --- |
| `cont_splash_region` 与 `dfps_data_region` | 首尾相接，无重叠（`0x9C000000+0x2300000 == 0x9E300000`） |
| `hyp_region` 与 `xbl_aop_region` | 首尾相接（`0x80000000+0x600000 == 0x80600000`） |
| `smem_region` 与 `removed_region` | 首尾相接（`0x80900000+0x200000 == 0x80B00000`） |
| `pil_adsp_region` 与 `pil_spss_region` | 首尾相接（`0x8bb00000+0x2500000 == 0x8E000000`） |
| `pil_spss_region` 与 `cdsp_secure_heap` | 首尾相接（`0x8E000000+0x100000 == 0x8E100000`） |
| `RAMOOPS`（固件）与 `disp_rdump_region`（DT） | 首尾相接（`0xB0000000+0x400000 == 0xB0400000`） |
| DT `memory`（活动 FDT 三段）与上述固定区间 | `0x9C000000`、`0x9E300000` 位于第一段 `0x80000000–0xBBB00000` 内；`0xB0400000` 位于 DTS 注释所指的保留空洞 `0xBBB00000–0xC0000000` 内（`dts/enuma.dts:21-25`） |

---

## 5. 本候选（`out/ufs-sm8250-policy-20261116-r1/`）自有 DMA 页分配方式

### 5.1 分配 API 与参数

| 事实 | 值 | 来源 |
| --- | --- | --- |
| API | `IOBufferMemoryDescriptor::inTaskWithOptions(kernel_task, options, kDmaBytes, 4096)` | `out/ufs-sm8250-policy-20261116-r1/source/RootWarmTarget.h:41-44` |
| options | `kIODirectionInOut \| kIOMemoryPhysicallyContiguous \| kIOMemoryMapperNone` | 同上 `:42-44` |
| 大小 | `kDmaBytes = kDataOffset + kDataMax = 8192 + 131072 = 139264` | `self-check/merged-source/RootTransportLayout.h:1-9` |
| 对齐 | `4096`（`maxAddress`/`alignment` 实参） | `RootWarmTarget.h:44` |
| 调用时机 | 仅在 `TR/TM` 停止且回读通过之后；`port.allocate()` | `source/RootWarmAdopt.h:120-122` |
| 取物理地址 | `getPhysicalSegment(0, &physicalBytes, kIOMemoryMapperNone)` → 保存 `gHost.phys`/`physicalBytes` | `RootWarmTarget.h:48-52` |
| 保留语义 | `gHost.dma` 在每条路径（含 fatal `IS` poison）永久保留，失败也不释放；`gHost.lock` 失败同样保留 | `RootWarmTarget.h:38-47` 注释与代码 |
| 同类另一处 | `NativeUfs.cpp:1425-1428`：诊断路径 `enumaReadExecute` 分配 `sizeof(UfsEnumaPacket::Layout)`（`UfsEnumaReadPackets.h:10-11` 静态断言 = `139264`），同样 `4096` 对齐 + `kIOMemoryPhysicallyContiguous\|kIOMemoryMapperNone` | 对应文件行号 |

### 5.2 缓冲区内部布局（同一块 139264 B）

| 偏移 | 大小 | 用途 | 来源 |
| --- | --- | --- | --- |
| `0` | 32 | UTRD（`uint32_t words[0..7]`：`words[0]=0x10000000\|(direction<<25)`、`words[4..5]=UCD 物理地址`、`words[6]=512/4 \| (kRspOffset/4)<<16`、`words[7]=(有数据)\|((kPrdtOffset>>2)<<16)`） | `RootCommands.h:58-69` |
| `kUcdOffset = 4096` | 4096 | UCD（UPIU 命令/响应区）；区内 `kRspOffset = 512`（响应）、`kPrdtOffset = 1024`（PRDT） | `RootTransportLayout.h:3-6` |
| `+kPrdtOffset`（绝对 `5120`） | 16 | PRDT 单条：`prd[0..1]=data 物理地址`、`prd[2]=0`、`prd[3]=dataBytes-1` | `RootCommands.h:72-77` |
| `kDataOffset = 8192` | `kDataMax = 131072` | 数据缓冲；`kDmaBytes = kDataOffset + kDataMax = 139264` | `RootTransportLayout.h:6-8` |
| UTRD 区（extent 视角） | 整块 `kDmaBytes` | `DmaExtents.utrl = {phys, kDmaBytes}`，第四项 `{phys + kDataOffset, kDataMax}`、第二项 `{phys + kUcdOffset, 4096}`、第三项 `{phys + kUcdOffset + kPrdtOffset, 16}` | `RootWarmAdopt.h:130-133` |
| `Layout` 对照 | 整块 139264 | `struct Layout { uint8_t utrd[32], padding[4064], ucd[4096], data[131072]; }`，`sizeof==139264`、`offsetof(ucd)==4096`、`offsetof(data)==8192` | `UfsEnumaReadPackets.h:10-12` |

### 5.3 代码中出现的地址约束（全部为事实列举，不含评价）

| 约束 | 依据 |
| --- | --- |
| 虚拟地址与物理地址均 `& 4095 == 0` | `RootWarmAdopt.h:126` |
| 连续段长度 `>= kDmaBytes` | `RootWarmAdopt.h:127` |
| 若 `HCS` 未置 bit24（`0x01000000`），则 `phys + kDmaBytes < 4 GiB`（`phys >= 0x100000000` 或越界即失败） | `RootWarmAdopt.h:128`；legacy 分支同式 `NativeUfs.cpp:1563` |
| `phys > UINT64_MAX - kDmaBytes` 判溢出 | `RootWarmAdopt.h:132` |
| 四个 extent（整块 / `+kUcdOffset` 4096 / `+kUcdOffset+kPrdtOffset` 16 / `+kDataOffset` `kDataMax`）必须落在 SMMU 观测到的三组地址宽度（32..48 bit）内 | `UfsObservedSmmu.h:132-142`；`RootWarmAdopt.h:130-133` |
| 诊断路径要求 `pa >= profile.mapping.physical.base` | `NativeUfs.cpp:1434` |

状态记录（非地址约束）：分配成功后任一校验失败时 `gWarmState` 保持 `Allocated`、`gRootDiagnostic.dma` 已记录物理地址；分配本身失败则停在 `Stopped`（`RootWarmAdopt.h:118-129`）。

### 5.4 是否落入任何已知 `reserved-memory` 区间

| 检查 | 结果 |
| --- | --- |
| 源码中是否读取/比较 DT `reserved-memory`（或任何保留区间） | 无：`grep -E "reserved-memory\|reservedMemory\|ReservedMemory\|resv"` 在 `out/ufs-sm8250-policy-20261116-r1/source/*.{h,cpp}` **0 命中** |
| 是否存在硬编码保留区列表 | 无；地址约束仅 §5.3 的宽度/对齐/4 GiB 与 SMMU 观测值 |
| 因此静态上能否判定 `gHost.phys` 与 §2.1 区间的交集 | **不能**：分配在运行时由 `IOBufferMemoryDescriptor` 决定 |
| `owned_memory_size`（`board.toml:87` = `0x20000000`）与 DMA 的关系 | ADT 只把该值写成 `/chosen/darwinboot-memory-size`（§1.3），是窗口**大小**，不是基址；源码无该值参与 DMA 计算的路径 |

### 5.5 同文件内的其他分配点（事实列举）

| 位置 | API | 大小 | 状态 |
| --- | --- | --- | --- |
| `NativeUfs.cpp:1548-1551` | `IOBufferMemoryDescriptor::inTaskWithOptions(kernel_task, kIODirectionInOut\|kIOMemoryPhysicallyContiguous\|kIOMemoryMapperNone, kDmaBytes, 4096)` | 139264 | 位于 `#elif NATIVE_UFS_ENABLE_SM8550_LEGACY` 分支（`:1527` 起）；按 `NATIVE_UFS_ENABLE_SM8550_LEGACY` 默认 0 排除 |
| `NativeUfs.cpp:1572` | `smmuBypassStream(0x60, gHost.smmuMap, report, gHost.phys, kDmaBytes)` | 同上块 | 同 legacy 分支 |
| `NativeUfs.cpp:1425-1428` | 同 API，`sizeof(UfsEnumaPacket::Layout)` | 139264 | 诊断路径（`enumaReadExecute`，`noreturn`，`:1408`） |
| `NativeUfs.cpp:1957` | `IOMalloc(kDataMax)` | 131072 | bounce 缓冲；`:2213` 对应 `IOFree(bounce, kDataMax)` |
| `NativeUfs.cpp:2502/2520/2601` | `IOMalloc(sizeof(RootLayout))` | `sizeof(RootLayout)` | 根布局对象（非 DMA） |

---

## 6. 未确定项清单

| # | 未确定项 | 为什么静态得不出 | 需要什么证据 |
| --- | --- | --- | --- |
| U1 | `UFSDxe.efi` 的请求列表、UCD、PRDT、数据缓冲的物理地址 | 厂商预编译、无源码；FDF 只声明二进制；DTB 无 `memory-region`/`iommus` | 该二进制的反汇编/导入分析，或运行期在 DXE 中打印 `gBS->AllocatePages` 返回值的 trace |
| U2 | `UFSDxe` 是否经 `HALIOMMU` 的 `EDKII_IOMMU_PROTOCOL` 取映射（SID/CB 归属） | 两个模块都是二进制；`UFSDxe.depex` 的 2 个 GUID 本轮未映射到协议名 | depex GUID 查表；运行期 `LocateProtocol` 记录 |
| U3 | 固件 `AllocatePages`（若 UFS 驱动使用）实际落点是否与 §2.1 任一区间相交 | 地址运行期决定 | 固件启动日志中的分配记录，或内存图 dump（`GetMemoryMap` 输出） |
| U4 | 候选驱动 `gHost.phys` 的落点 | 运行时由 `IOBufferMemoryDescriptor` 决定 | 设备侧 `gRootDiagnostic.dma` 的实际取值（`RootWarmAdopt.h:123` 已记录到该字段，但需要一次实机运行才有值） |
| U5 | 12 个 `shared-dma-pool` 节点（`adsp/sdsp/cdsp/mem_dump/sp/user_contig/qseecom/qseecom_ta/secure_display/cnss_wlan/linux,cma/mailbox`）的运行时落点 | 只有 `size`/`alignment`/`alloc-ranges 0..0xffffffff` | Linux/内核侧 ION 分配日志或 `meminfo`/`iommu` 转储；本板 XNU 侧无等价记录 |
| U6 | `removed_region@80b00000`（`0x5300000`）内部各 ATF/XBL 子区间 | DT 只给整块；XBL cfg 的 HYP/TZApps 行只覆盖其中一部分 | ATF/XBL 的完整内存表（`xbl_a` `uefiplat.cfg` 全文或 ATF 映像的段表） |
| U7 | `hyp_region` 长度差异（DT `0x600000` vs 固件 `0x5D0000`）中 `0x805D0000–0x80600000` 的实际归属 | 两侧都是静态声明，DT 未拆出 IPC SHM | 运行期该 192 KiB 的内容/使用方证据 |
| U8 | `disp_rdump_region@9c000000`（实际 `0xB0400000`）的用途与写入方 | 本仓与固件源码均无引用方 | 使用该 region 的驱动侧源码或运行期写入记录 |
| U9 | `apps-smmu` 窗口长度差异（DT `0x100000` vs 固件 `0xd0000` vs 候选 `0xd0000`） | 三处独立声明 | 以 SMMU 实际寄存器回读/`IDR` 观测为准（候选已具备 `readSmmu` 只读路径） |
| U10 | ADT 生成时 `hardware.dtb` 两份不同哈希（`520c4dec…` / `3191a895…`）的具体差异 | 本轮只算哈希，未 diff | `dtc -I dtb -O dts` 两份对比 |
| U11 | `Build/…/UFSDxe/…SEC2.1.pe32`（118788 B）与源 `UFSDxe.efi`（118784 B）是否同字节 | 未比对 | 二进制 diff（FFS 打包填充差异待核） |
| U12 | `/arm-io/intc` 的 `reg`（`0x16a00000`）等 GIC 值与 §2.1/§2.5 的关系 | 属 MMIO，不在 `reserved-memory` 范围 | 已超本报告范围，仅记录存在 |

---

## 附：本文引用的文件清单

| 文件 | 用途 |
| --- | --- |
| `enuma/UniXNU-enuma/.cache/firmware/dtb/sm8250-xiaomi-enuma.dtb` / `.dts` | §1、§2 主数据 |
| `enuma/UniXNU-enuma/.cache/firmware/fdt.stdout` / `fdt-live.dts` / `fdt.stdout.provenance.json` / `dtb-report.json` | §1、§2 交叉源 |
| `enuma/UniXNU-enuma/dts/enuma.dts`、`board.toml`、`proprietary-files.txt` | §1、§5.4 |
| `enuma/UniXNU-enuma/out/ufs-sm8250-policy-20261116-r1/{source,self-check/merged-source,self-check/extracted,candidate-manifest.json}` | §3.4、§4、§5 |
| `enuma/uefi-enuma/Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c` | §2.5、§2.6 |
| `enuma/uefi-enuma/Platforms/Xiaomi/enumaPkg/{enuma.dsc,enuma.fdf,Include/DXE.inc,Include/APRIORI.inc,EnumaInputs/*.inc}` | §3.1 |
| `enuma/uefi-enuma/Binaries/enuma/UFSDxe/*`、`Build/enumaPkg/RELEASE_CLANGPDB/FV/Ffs/0d35cd8e-…UFSDxe/` | §3.1 |
| `enuma/uefi-enuma/Platforms/Xiaomi/enumaPkg/{Drivers/EnumaSmmu4KIoMmuDxe,Library/EnumaSmmu4KTableLib}` | §3.2 |
| `UniXNU/scripts/unixnu/{payload.py,devicetree.py,bootimg.py}` | §1.2、§1.3 |

`self-checked`：上表事实均由 C1–C13 命令直接产生（§2.1 表经 C13 逐行核对 34/34，表格结构经 C12 校验）；未做的复核项：未上机、未在固件中 dump `GetMemoryMap`、未反汇编 `UFSDxe.efi`/`HALIOMMU.efi`、未比对两份 `hardware.dtb` 的差异、未做独立 verifier 复跑。
