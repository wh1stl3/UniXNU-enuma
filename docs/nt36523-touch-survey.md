# enuma NT36523 触摸：本板 DTB 接口事实与官方实现缺口

状态：**`self-checked`**（纯离线只读静态提取；未上机，未读寄存器，未做独立 verifier 复跑）
整理日期：2026-11-17
范围：`enuma/UniXNU-enuma`（本板 DTB、board.toml、porting.toml、scripts）、`UniXNU@693f5d9c`（只读基线：`components.toml`、`docs/zh/**`、`devices.toml`）
本文只列事实、差异、缺口与未确定项，不含实现建议。

---

## 0. 方法与复跑命令

命令在 WSL Ubuntu-22.04 执行（工作目录 `/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma`），退出码 0。

| # | 命令 | 用途 |
| --- | --- | --- |
| B1 | `dtc -I dtb -O dts -o /tmp/e1.dts .cache/firmware/dtb/sm8250-xiaomi-enuma.dtb` + `cmp -s /tmp/e1.dts .cache/firmware/dtb/sm8250-xiaomi-enuma.dts` | 反编译本板固件 DTB；仓库内 `.dts` 与输出逐字节相同（`cmp` 退出 0），行号引用该 `.dts` |
| B2 | `.dts` 行号直接读取 | `/soc/spi@990000`(.dts:34429)、`novatek@0`(.dts:34449)、`/soc/qcom,qupv3_0_geni_se@9c0000`(.dts:33913)、`/soc/qcom,gpi-dma@900000`、`/soc/xiaomi_touch`(.dts:444)、`touch_vddio_vreg`(.dts:661)、`ts_mux`(.dts:13201)、`pmx_ts_*`(.dts:14361-14430) |
| B3 | 临时脚本 `dtsx.py`（仓库外 `%TEMP%/opencode/`） | 解析 phandle：`0x6f0`→`pinctrl@f000000/ts_mux/ts_cs_active`、`0x6f1`→`ts_cs_suspend`、`0x29a/0x29b`→`qupv3_se4_spi_active/sleep`、`0x65`→`pinctrl@f000000`、`0x275`→`qupv3_0_geni_se`、`0x281`→`gpi-dma`、`0x16`→`gcc@100000`、`0x47`→`apps-smmu@15000000` |
| B4 | `Select-String` 统计 | `pmx_ts_*`/`ts_mux` 的引用方；`gpio33` 出现位置 |
| B5 | DTB 身份与哈希 | 见 `docs/sm8250-ac-opp-thermal-diff.md` §0（同一份 DTB：`42d36a00…f698`） |

**公开来源用量**：0 个社区仓、0 次外网抓取。本节全部事实来自本板 DTB 与官方 UniXNU 仓内文件（未触及「上限 2 个公开来源 / 1 个检查点」）。

---

## 1. 本板 DTB 中的触摸控制器节点

### 1.1 定位与身份

| 项 | 值 | 出处 |
| --- | --- | --- |
| 节点路径 | `/soc/spi@990000/novatek@0` | `.dts:34449-34475` |
| `compatible` | `"novatek,NVT-ts-spi"` | `.dts:34466` |
| `reg` | `<0x00>`（SE4 片选 0） | `.dts:34465` |
| `status` | `"ok"` | `.dts:34464` |
| 厂商胶水节点 | `/soc/xiaomi_touch`：`compatible = "xiaomi-touch"`、`touch,name = "xiaomi-touch"`、`status = "ok"`（**无其他属性、无资源、无 phandle 引用**） | `.dts:444-448` |

即控制器在 DT 中只有一个 SPI 从设备节点 + 一个无资源的厂商节点；芯片型号 NT36523 不在 DT 中，来自 `porting.toml:161` 记录的厂商内核配置（`CONFIG_TOUCHSCREEN_NT36523_HOSTDL_SPI`、`drivers/input/touchscreen/nt36523`）与固件文件名（`novatek_nt36523_k81_fw01.bin`，`.dts:34472`）。

### 1.2 总线：QUPv3 wrapper 0 / SE4 / GENI SPI

| 层 | 属性 | 值 | 出处 |
| --- | --- | --- | --- |
| Wrapper | 节点 | `/soc/qcom,qupv3_0_geni_se@9c0000`，`compatible = "qcom,qupv3-geni-se"` | `.dts:33913-33914` |
| Wrapper | `reg` | `<0x9c0000 0x2000>` | `.dts:33915` |
| Wrapper | `iommus` | `<0x47 0x5a3 0x00>`（`0x47` = `/soc/apps-smmu@15000000`，SID `0x5a3`） | `.dts:33918` |
| Wrapper | SMMU/DMA 属性 | `qcom,iommu-dma-addr-pool = <0x40000000 0xc0000000>`、`qcom,iommu-dma = "fastmap"` | `.dts:33919-33920` |
| Wrapper | bus 端口 | `qcom,bus-mas-id = <0x97>`、`qcom,bus-slv-id = <0x200>` | `.dts:33916-33917` |
| SPI SE | 节点 | `/soc/spi@990000`，`compatible = "qcom,spi-geni"`，`qcom,rt` | `.dts:34429-34431` |
| SPI SE | `reg` / `reg-names` | `<0x990000 0x4000>` / `se_phys` | `.dts:34434-34435` |
| SPI SE | 中断 | `<0 0x25d 4>` = GIC SPI 605 | `.dts:34441` |
| SPI SE | 时钟 | `se-clk`=`<0x16 0x60>`、`m-ahb`=`<0x16 0x84>`、`s-ahb`=`<0x16 0x85>`（`0x16` = `/soc/qcom,gcc@100000`） | `.dts:34436-34437` |
| SPI SE | 速率上限 | `spi-max-frequency = <0x2faf080>` = 50 MHz | `.dts:34442` |
| SPI SE | DMA | `dmas = <0x281 0 4 1 0x40 0>, <0x281 1 4 1 0x40 0>`、`dma-names = "tx","rx"`（`0x281` = `/soc/qcom,gpi-dma@900000`，GPII 4） | `.dts:34444-34445` |
| SPI SE | 上层 | `qcom,wrapper-core = <0x275>`（= wrapper 节点） | `.dts:34443` |
| GPI DMA | 节点 | `/soc/qcom,gpi-dma@900000`，`compatible = "qcom,gpi-dma"`，`reg = <0x900000 0x70000>`，`status = "ok"` | `.dts` gpi 区 |
| GPI DMA | SMMU 与配置 | `iommus = <0x47 0x5b6 0x00>`、`qcom,smmu-cfg = <0x01>`、`qcom,iommu-dma-addr-pool = <0x100000 0x100000>`、`qcom,max-num-gpii = <0x0f>`、`qcom,gpii-mask = <0x7ff>`、`qcom,ev-factor = <0x02>`、`qcom,gpi-ee-offset = <0x1000>`、`#dma-cells = <0x05>` | 同上 |
| 从设备 | 速率 | `spi-max-frequency = <0x124f800>` = 19.2 MHz（低于 SE 上限 50 MHz） | `.dts:34460` |

SPI 引脚（`pinctrl@f000000/qupv3_se4_spi_pins`，phandle `0x4dd`）：

| 组 | phandle | 引脚 | function | 驱动强度 |
| --- | --- | --- | --- | --- |
| `qupv3_se4_spi_active` | `0x29a` | `gpio8,gpio9,gpio10` | `qup4` | 6 |
| `qupv3_se4_spi_sleep` | `0x29b` | `gpio8,gpio9,gpio10` | `gpio` | 6 |

片选引脚（`pinctrl@f000000/ts_mux`，`.dts:13201`）：

| 组 | phandle | 引脚 | function | 驱动强度 / 其它 |
| --- | --- | --- | --- | --- |
| `ts_cs_active` | `0x6f0` | `gpio11` | `qup4` | 6；`bias-disable` |
| `ts_cs_suspend` | `0x6f1` | `gpio11` | `gpio` | 6；`output-low`、`bias-pull-down` |

`novatek@0` 的 `pinctrl-names = "pmx_ts_active","pmx_ts_suspend"`，`pinctrl-0 = <0x6f0>`（CS active）、`pinctrl-1 = <0x6f1>`（CS suspend），`.dts:34461-34463`。

### 1.3 中断

| 项 | 值 | 出处 |
| --- | --- | --- |
| 属性 | `novatek,irq-gpio = <0x65 0x27 0x2001>` | `.dts:34459` |
| 解码 | `<&tlmm gpio39 flags 0x2001>`；`0x65` = `/soc/pinctrl@f000000`，`0x27` = 39 | B3 |
| 节点内 `interrupts` / `interrupt-parent` | **均不存在**（中断只经 GPIO 描述符表达） | `.dts:34449-34475` 全属性 |

### 1.4 复位与供电

| 项 | 事实 | 出处 |
| --- | --- | --- |
| `novatek,reset-gpio` / `reset-gpios` | 节点中**不存在** | `.dts:34449-34475` |
| `vdd`/`vcc`/`vddio` supply 属性 | 节点中**不存在** | 同上 |
| `touch_vddio_vreg` | `/soc/touch_vddio_vreg`：`compatible = "regulator-fixed"`、`gpio = <0x65 0x45 0x00>`（tlmm 69）、`enable-active-high`、`regulator-name = "disp_vddio_vreg"`、**`status = "disabled"`**；**无任何节点以 supply 引用它** | `.dts:661-668` |

### 1.5 pinctrl 状态与引用情况

| 组 | phandle | 引脚 / 配置 | 引用方 |
| --- | --- | --- | --- |
| `pmx_ts_active/ts_active` | `0x40d` | `gpio33,gpio39`，function `gpio`，drive 8，`bias-pull-up` | **无** |
| `pmx_ts_int_suspend/ts_int_suspend` | `0x40e` | `gpio39`，function `gpio`，drive 2，`bias-pull-down` | **无** |
| `pmx_ts_reset_suspend/ts_reset_suspend` | `0x40f` | `gpio33`，function `gpio`，drive 2，`bias-pull-down` | **无** |
| `pmx_ts_release/pmx_ts_release` | `0x410` | `gpio33,gpio39`，function `gpio`（`.dts:14415-14430`） | **无** |

出处：`.dts:14361-14430`；引用检查（B4）：`<0x40d>`、`<0x40e>`、`<0x40f>` 在全树除自身 `phandle` 行外 **0 次**出现；`<0x410>` 另有一处无关属性 `hyplog-address-offset = <0x410>`（`.dts:8906`）。四个组均无设备节点引用；`__symbols__` 中只有 `pmx_ts_release = "/soc/pinctrl@f000000/pmx_ts_release/pmx_ts_release"` 一条（`.dts:41295`），其余三组连别名也没有。`gpio33` 在整棵树中除上述 pinctrl 组外只出现在 `gpio32/gpio33` 的其它外设引脚组（`.dts:18630-18854`，与触摸无关）。

### 1.6 vendor 专有属性全表

`novatek@0` 除标准属性外的全部属性（`.dts:34450-34474`）：

| 属性 | 值 | 备注 |
| --- | --- | --- |
| `novatek,config-array-size` | `<0x01>` | 配置数组 1 项 |
| `novatek,touch-game-param-config1/2/3` | `<2 2 1 2 1>` / `<2 2 2 2 1>` / `<2 2 3 2 1>` | 三档横屏/游戏参数 |
| `novatek,mp-support-dt` | 存在（布尔） | MP 测试参数走 DT |
| `novatek,spi-rd-fast-addr` | `<0x3f310>` | 快速读寄存器地址 |
| `novatek,swrst-n8-addr` | `<0x3f0fe>` | 软复位 N8 地址 |
| `novatek,wgp-stylus` | 存在（布尔） | 手写笔（WGP）支持 |
| `novatek,pen-support` | 存在（布尔） | 笔输入支持 |
| `novatek,irq-gpio` | `<0x65 0x27 0x2001>` | 见 §1.3 |
| `novatek,cfg_0`（子节点） | `novatek,fw-name = "novatek_nt36523_k81_fw01.bin"`；`novatek,fw-pen-name = "novatek_nt36523_k81_fw01_pen.bin"`；`novatek,mp-name = "novatek_nt36523_k81_mp01.bin"`；`novatek,mp-pen-name = "novatek_nt36523_k81_mp01_pen.bin"`；`novatek,display-maker = <0x42>` | 固件/MP 文件名与面板厂商代码 |

DT 内**没有**：芯片 ID 常量、矩阵尺寸、行/列数、固件版本号、SPI 模式（CPOL/CPHA）、字节序、中断极性/类型语义、复位时序。

---

## 2. 官方 UniXNU 现有的输入/触摸实现

### 2.1 组件（`UniXNU/components.toml`）

| 组件 | 行 | 功能声明 | 硬件声明 | 依赖 | 源码 / 输出 | 已验证设备 |
| --- | --- | --- | --- | --- | --- | --- |
| `ShengHidInput` | 145-163 | `sheng touch input through IOHIDDevice`；scope `board` | `sheng touch event source` | `ShengNovatekTouch` | `NativeHidInput.cpp`；`build/sheng-hid-input/libShengHidInput.a`、`NativeHidInput.late.o`；stage `kernel` | `["sheng"]` |
| `ShengNovatekTouch` | 166-184 | `NT36532 touch protocol and sheng sensor configuration` | `Novatek NT36532/NT36532E` | `QcomGeniSpi` | `NvtTouchCore.c`；stage `embedded`；`build = []`、`outputs = []` | `["sheng"]` |
| `QcomGeniSpi` | 186-205 | `Qualcomm GENI SPI controller operations`；scope `controller` | `Qualcomm GENI SPI` | 无 | `GeniSpi.c`；stage `embedded` | `[]`（空） |

三个组件的仓库固定版本：`ShengHidInput@71a40e76daeae1bb4127546f96ffa7339c7a06ff`、`ShengNovatekTouch@3b44b1b7603eaadae942ea44ddc51bdcc48ad060`、`QcomGeniSpi@eac47baefe6a5d2368a70351e6ad1b6361bedbe2`（`components.toml:151,172,193`）。

本地检出情况：`UniXNU/drivers/` 下 14 个目录中**有** `QcomGeniSpi`（`GeniSpi.c` 15884 B、`GeniSpi.h` 9375 B、`AGENTS.md`、`LICENSE`、`README.md`），**没有** `ShengNovatekTouch` 与 `ShengHidInput`（两者在构建时按组件仓库拉取，本地不可读，见 U13）。三者的 `os_abi` 均为 `ipados-17.7.11-21H461`，与本板目标 OS 版本一致。

### 2.2 接口形态（官方文档所述）

| 接口 | 形态 | 出处 |
| --- | --- | --- |
| 总线抽象 | `struct nvt_bus { void *ctx; int (*xfer)(void *ctx, const uint8_t *tx, uint8_t *rx, size_t len); void (*delay)(void *ctx, unsigned ms); }` | `docs/zh/drivers/sheng-novatek-touch.md:29-37` |
| 传输约束 | 整次全双工传输期间保持片选有效；缓冲区由调用方持有 | `docs/zh/porting/input.md:30` |
| 协议层 | `nvt_identify`、`nvt_fw_parse`、`nvt_download_firmware`、`nvt_start_scanning`、`nvt_peek_frame_header`、`nvt_read_frame`、`nvt_frame_header_valid`、`nvt_frame_matrix` | 同上 `:64-73` |
| 触点核心 | 40 × 60 的 16 位矩阵；72 帧启动数据、中值参考、blob、加权质心、边缘补偿、跨帧跟踪；不分配内存（临时数组在 `struct nvt_touch_core`，因内核线程栈 16 KiB） | 同上 `:43-58` |
| 板级常量 | `TouchBoard.h` 分 QUP wrapper / SE、SMMU stream ID、GCC vote 与 halt、TLMM 引脚、SPI 模式与上限；`tb_choose_clock` 选 DFS 级与分频 | 同上 `:77-89` |
| 硬件路径 | vote GCC 分支 → 等时钟 → 配 TLMM → 映射 wrapper/SE → 初始化 GENI SPI → 选 DFS/分频 → 分配物理连续 DMA → apps SMMU bypass 映射 → 每传输前后维护缓存 | 同上 `:104-118` |
| 触点发布 | 全局 `volatile uint32_t native_touch_seq`、`native_touch_count`、`volatile int native_touch_xs/ys/ids[NVT_SLOTS]`；写方前后递增序号，读方检测撕裂 | 同上 `:120-132` |
| HID 层 | `ShengHidInput` 读该快照并发出 digitizer 报告；实现针对 IOHIDFamily `2031.120.4` ABI | `docs/zh/drivers/sheng-hid-input.md:9`；`components.toml:154` |
| 板级集成要素 | 控制器窗口、总线模式/速率、GPIO、中断、SMMU stream；电源/复位；DMA 寻址与缓存维护；芯片 ID → 固件 → 几何；坐标变换 | `docs/zh/porting/input.md:37-43` |
| 固件管理 | 由设备仓 `scripts/gen-touch-firmware.py` + 私有文件清单提取 | 同上 `:46` |
| 启动参数 | `sheng-touch=1..4`（分阶段探针）、`sheng-touch-hid=1`（HID 发布路径） | 同上 `:48,61` |

**`QcomGeniSpi` 的实际函数接口**（本地源码 `UniXNU/drivers/QcomGeniSpi/`，revision `eac47bae`）：

| 项 | 内容 | 出处 |
| --- | --- | --- |
| 寄存器访问抽象 | `struct geni_io { void *ctx; uint32_t (*rd)(void *ctx, uint32_t reg); void (*wr)(void *ctx, uint32_t reg, uint32_t value); void (*delay_us)(void *ctx, unsigned us); }` —— 板级提供全部 MMIO 与延时 | `GeniSpi.h:166-171` |
| 控制器对象 | `struct geni_spi { geni_io se; geni_io wrapper; geni_spi_info info; use_dma; dma{clean,clean_inval,inval,tx_virt,rx_virt,tx_phys,rx_phys,size}; … }`；DMA 缓冲由调用方提供并负责 SMMU 翻译与缓存策略 | `GeniSpi.h:180-209` |
| 只读探测 | `geni_spi_read_info()`：读 `GENI_FW_REVISION_RO`(0x68)、`GENI_IF_DISABLE_RO`(0x64)、`SE_HW_PARAM_0`(0xe24)、`QUPV3_HW_VER_REG`(0x4)；注释要求 SE 时钟已在运行 | `GeniSpi.h:211-213`、`GeniSpi.c:20-37` |
| 初始化 | `geni_spi_init()`：FIFO(PIO) 模式初始化；`fifo_disabled && !allow_fifo_disabled && !use_dma` 返回 `GENI_ERR_NOTSUP`（注释：GPI DMA 路径未实现）；显式清 `SE_SPI_TRANS_CFG` 的 `GENI_CS_TOGGLE`——**片选不由软件驱动** | `GeniSpi.c:74-121`（`:80`、`:107`） |
| 模式 | `geni_spi_setup(struct geni_spi *, unsigned mode, unsigned chip_select)`（CPOL/CPHA 位） | `GeniSpi.c:123-137` |
| 时钟 | `geni_spi_set_clock(struct geni_spi *, unsigned speed_hz, unsigned sclk_hz, unsigned clk_sel)`：按 SE 源时钟算分频 | `GeniSpi.c:139-154` |
| 传输 | `geni_spi_transfer(struct geni_spi *, const uint8_t *tx, uint8_t *rx, size_t len, int keep_cs)`：全双工/TX-only/RX-only，8 位字，轮询完成；`keep_cs` 映射为 `GENI_M_PARAM_FRAGMENTATION`（整次传输保持片选） | `GeniSpi.h:221-222`、`GeniSpi.c:295-320`（`:241`） |
| DMA 模式 | `use_dma` 时走 SE DMA 引擎（`SE_DMA_{TX,RX}_*`，`0xc30-0xd58`），搬运前后调用 `dma.clean/clean_inval/inval` | `GeniSpi.c:219-293`、`GeniSpi.h:195-207` |
| 常量面 | SE 寄存器偏移 `0x20-0xe30`、DMA 寄存器 `0xc30-0xd58`、wrapper `QUPV3_HW_VER_REG = 0x4`；错误码 `GENI_ERR_NOTSUP(-95)` 等 | `GeniSpi.h:10-77,159-164` |

### 2.3 DT/ADT 绑定形态

| 事实 | 出处 |
| --- | --- |
| 驱动 personality 以 `IONameMatch` 匹配 provider 名称或 `compatible`；provider 类为 `IOPlatformDevice`（`ArmDTPlatform` 为每个 `arm-io` 子节点发布） | `docs/zh/drivers/device-tree-matching.md:32,41-52` |
| 只有带 `unixnu,adt-name` 且启用的节点会被导出到 ADT 的 `/arm-io` 之下，`reg` 以相对 `arm-io` 基址的 u64 编码 | `UniXNU/scripts/unixnu/devicetree.py:370-377`；`device-tree-matching.md:90-93` |
| 共享仓 `dts/sm8250.dtsi` 目前只给 `intc`、`ufshc`、`ufsphy` 三个节点 `unixnu,adt-name` | `UniXNU-sm8250-common/dts/sm8250.dtsi:45,57,64` |

### 2.4 官方仓内的同 SoC / 同族先例（事实摘录）

| 设备 | 记录 | 出处 |
| --- | --- | --- |
| `alioth`（SM8250） | 组件 `QcomGeniSpi`、`ShengHidInput`、`ShengNovatekTouch` 全部接入；触控为 FocalTech FT5652，挂在 **GENI SE4 / QUPv3 wrapper 0**，`spi-max-frequency 6000000`、`interrupts <39 0x2008>`、reset GPIO 33、irq GPIO 39 | `docs/devices/alioth.md:43,349,353,357` |
| `erhai`（NT36536） | 厂商 DT 的 `compatible` 为 `novatek,nf_nt36536`；官方 `ShengNovatekTouch` 被明确记为「NT36532E 驱动，是范例而不是本板驱动」，该板另写 `drivers/ErhaiNovatekTouch`（NT36536 头部解析 + 内存映射 + 厂商校验） | `docs/devices/erhai-xingxing19035.md:135,468` |
| `asteroids` | `ShengNovatekTouch` 仅作为 `ShengHidInput` 的依赖被链接，**未使用** | `docs/devices/asteroids.md:365` |

### 2.5 本仓（enuma）已有的相关资产

| 项 | 事实 | 出处 |
| --- | --- | --- |
| `board.toml [components] include` | `ArmDTPlatform`、`ArmCpu`、`SoftwareAES`、`XnuPrelink`、`DarwinBoot`、`RamBlock`、`ShengUfs` —— **不含** `ShengHidInput` / `ShengNovatekTouch` / `QcomGeniSpi` | `UniXNU-enuma/board.toml`（components 段） |
| 触摸/输入 kernel 参数 | 无（`board.toml` 无 `sheng-touch` / `sheng-touch-hid` / `native-touch` 字样） | 同上 |
| 已有记录 | `porting.toml:161`：厂商内核 `MiCode/Xiaomi_Kernel_OpenSource elish-r-oss@52a2f180…` 启用 `CONFIG_TOUCHSCREEN_NT36523_HOSTDL_SPI`、`TOUCHSCREEN_XIAOMI_TOUCHFEATURE`，源码 `drivers/input/touchscreen/nt36523`、`drivers/misc/spi-xiaomi-tp.c`；出厂三种固件变体（fw01-03）；**该分支无板级 DTS**，引脚/SPI 控制器/中断当时未核实；另有「Touch is untested」记录 | `porting.toml:161` |
| 遗留脚本（format 1，当前不可运行） | `scripts/plan_adt.py`（读 `novatek,NVT-ts-spi` 节点、`novatek,irq-gpio` cells、`novatek,fw-name` 列表 → 计划 JSON；默认 FDT 路径为 `D:/Code/PortingiOSLegacy/...`，该路径不存在） | `scripts/plan_adt.py:40-55,72` |
| 同上 | `scripts/check_enuma_drivers.py`（对 `out/references/Xiaomi_Kernel_OpenSource/.../nt36523/nt36xxx.c/.h`、`config/porting-sources.lock.json`、`drivers/EnumaPlatform/sources.json` 做哈希/pin 校验，并核对 `TOUCH_MAX_FINGER_NUM=10`、`TOUCH_FORCE_NUM=1000`、`POINT_DATA_CHECKSUM_LEN=65`、`DUMMY_BYTES=1`）——上述三个输入当前**均不存在** | `scripts/check_enuma_drivers.py:30-67`；实测 `out/references` 与 `config/porting-sources.lock.json` 不存在 |
| 同上 | `scripts/audit_inputs.py`（白名单含 `novatek,fw-name`、`novatek,irq-gpio`、`novatek,reset-gpio`）、`scripts/audit_reuse.py`（期望存在 `nt36523/nt36xxx.c/.h/nt36xxx_mem_map.h`） | `audit_inputs.py:97-106`、`audit_reuse.py:17-19` |
| 官方设备索引 | `enuma` 在 `devices.toml` 中记 `format = 1`、`legacy_page = "preserve"`、summary `Host image checks and EL1 read diagnostics; visible menu pending` | `UniXNU/devices.toml:616-627` |
| ADT 侧 | `dts/enuma.dts`（本板 ADT 源）无触摸节点、无 QUP 节点，仅启用 `&ufs` | `UniXNU-enuma/dts/enuma.dts:32-41` |

---

## 3. 缺口表

口径：「本板已有」= 本板 DTB/记录/仓内文件中存在的静态事实；「官方已有」= 官方仓内可查的实现或文档条目；「缺」= 上两列都不提供。

| # | 项 | 本板已有 | 官方已有 | 缺 |
| --- | --- | --- | --- | --- |
| 1 | 控制器身份 | `compatible = "novatek,NVT-ts-spi"`、固件名含 `nt36523_k81`、`porting.toml` 记 NT36523 与厂商内核开关 | `ShengNovatekTouch` 面向 **NT36532/NT36532E**（`components.toml:174`）；`erhai` 记录同为「范例非本板驱动」的处置 | NT36523 的芯片 ID 常量、内存映射、固件格式、帧格式 |
| 2 | 总线控制器 | SE4：`0x990000+0x4000`、GIC SPI 605、50 MHz 上限、GCC `0x60/0x84/0x85`、GPII 4 | `QcomGeniSpi`（本地 `drivers/QcomGeniSpi/GeniSpi.c`，revision `eac47bae`）提供 `geni_spi_read_info/init/setup/set_clock/transfer`；调用方提供 MMIO/DMA 回调与时钟/引脚（`components.toml:197`、`GeniSpi.h:166-171`） | 把 SE4 接成 `geni_io` 回调（MMIO 映射 + `delay_us`）与时钟票/`clk_sel` 的板级代码；本板 SE4 的 FIFO 可用性未知（U16） |
| 3 | 传输层实现 | `nvt_bus` 所需的 SPI 全双工与片选保持——DT 只给速率与引脚 | `nvt_bus` 契约（`input.md:30`）；`geni_spi_transfer(…, keep_cs=1)` 提供全双工 + 片选保持，片选由 SE 硬件驱动（`GeniSpi.c:107,241`） | `nvt_bus.xfer/delay` 到 `geni_spi_transfer` 的绑定（同 #2 的板级回调） |
| 4 | 中断 | `novatek,irq-gpio = <&tlmm 39 0x2001>`；无 `interrupts` 属性 | 文档要求「中断处理」与「GPIO/中断」板级要素（`input.md:18,37`） | 39 的触发类型/极性语义、去抖、应答方式；中断到读帧的绑定 |
| 5 | 复位 | 仅 `pmx_ts_reset_suspend`（gpio33）**未被任何节点引用**；无 `novatek,reset-gpio` | 文档要求板级实现电源/复位（`input.md:39`） | 复位引脚归属与复位时序 |
| 6 | 供电 | `touch_vddio_vreg`（tlmm 69、`disp_vddio_vreg`、**disabled**、无引用）；触摸节点无 supply | 文档要求电源控制（`input.md:39`） | 实际供电轨/开关与使能顺序 |
| 7 | pinctrl | `qupv3_se4_spi_active/sleep`（gpio8-10）、`ts_cs_active/suspend`（gpio11）已接；`pmx_ts_active/int_suspend/reset_suspend/release`（gpio33/39）无引用 | 文档要求「TLMM 引脚」板级常量（`sheng-novatek-touch.md:86`） | 中断/复位引脚的实际 pinctrl 状态选择 |
| 8 | 协议层 | 无 | `ShengNovatekTouch` 的 8 个 `nvt_*` 函数（`sheng-novatek-touch.md:64-73`） | 对 NT36523 的识别与协议适配（官方实现按 NT36532E 常量） |
| 9 | 触点处理 | 无 | `NvtTouchCore.c`：40×60 矩阵、blob/跟踪/边缘补偿（`:43-58`） | 本板矩阵尺寸与几何（来自固件回报，DT 未给） |
| 10 | 固件 | 文件名 4 个（fw/fw-pen/mp/mp-pen，`display-maker = 0x42`） | 提取脚本约定 `scripts/gen-touch-firmware.py` + 私有文件清单（`input.md:46`） | 固件二进制本体、提取来源（分区/容器）、版本选择（厂商分支有 fw01-03） |
| 11 | SMMU | QUP SID `0x5a3`、GPI DMA SID `0x5b6`（均指 `apps-smmu@15000000`），DMA 地址池与 `fastmap` | 文档要求「按目标 SMMU context 设置 DMA 寻址和缓存维护」，并记 Novatek 使用 apps SMMU bypass 路径（`four-k-page-tables.md:158`） | XNU 侧实际映射方式（bypass 还是同 SID 上下文）与缓存维护实现 |
| 12 | HID 发布 | 无 | `ShengHidInput`（`NativeHidInput.cpp`，IOHIDDevice，读 `native_touch_*` 快照） | 板级 `native_touch_*` 生产者模块；报告描述符与几何（分辨率、方向、触点上限） |
| 13 | DT/ADT 绑定 | 厂商 DTB 有节点，但 `dts/enuma.dts` 无触摸/QUP 节点 | ADT 只导出带 `unixnu,adt-name` 的节点（`devicetree.py:370-377`）；共享仓只导出 `intc/ufshc/ufsphy` | 本板 DTS 侧节点与 `unixnu,adt-name`；共享仓 QUP SE 节点（`sm8250.dtsi` 只有 `geniqup@9c0000` 且 `status = "disabled"`，`reg = <0 0x9c0000 0 0x6000>`，无 SE 子节点） |
| 14 | 组件选择 | `board.toml` 未含三者 | 三者作为组件可选（`components.toml`）；`ShengNovatekTouch.build/outputs` 为空（stage `embedded`） | 本板选型与归档配方接线 |
| 15 | 时钟票/DFS | SE4 `se-clk`=GCC `0x60`、`m-ahb`=`0x84`、`s-ahb`=`0x85`（数值来自 DT） | `TouchBoard.h` 的 GCC vote/halt 与 `tb_choose_clock` DFS 选择（`:86-89`） | 本板 GCC 寄存器偏移与 DFS 级（DT 只给 clock id） |
| 16 | 中断线程/时序 | 无 | 分阶段探针 `sheng-touch=1..4`（`input.md:48`） | 本板按阶段落地的探针与可观测点 |

缺口计数：上表 16 行中，**本板与官方都缺**（即缺口列非空且无法由前两列直接满足）为 **16 行全部**；其中 6 行属于「官方有接口/范例、缺 NT36523 或本板适配」（#2、#3、#8、#9、#11、#15），10 行属于「官方只给要求、缺板级事实或实现」（#1、#4、#5、#6、#7、#10、#12、#13、#14、#16）。

---

## 4. 未确定项

| # | 未确定项 | 为什么静态得不出 | 需要的证据 |
| --- | --- | --- | --- |
| U1 | 是否有第二条（I2C）触摸路径 | DT 只有 SPI 节点；`compatible` 明确为 `NVT-ts-spi` | 其余 dtbo 变体或实机总线枚举 |
| U2 | `novatek,irq-gpio` 第三格 `0x2001` 的语义 | 该值同时含 `0x2000` 与 `0x1`；DT 未声明编码，厂商驱动解析方式未在仓内 | 厂商 `nt36xxx.c` 的 `of_get_named_gpio_flags` 用法或实机中断观测 |
| U3 | 中断触发类型/极性 | 同上；节点无 `interrupts` 属性 | 同上 |
| U4 | 复位引脚与极性 | 节点无 `novatek,reset-gpio`；仅有一个未被引用的 pinctrl 组提到 gpio33 | 厂商 SPI 胶水（`spi-xiaomi-tp.c`）或实机测点 |
| U5 | 本板 SE4 的片选由谁驱动 | DT 的 `ts_cs_active`（gpio11，function `qup4`）与 `QcomGeniSpi` 的「片选不由软件驱动」（`GeniSpi.c:107`）在结构上一致，但 DT 仍保留 `ts_cs_suspend`（function `gpio`） | 读 `SE_SPI_TRANS_CFG` 与实机 CS 波形 |
| U6 | 实际供电轨 | `touch_vddio_vreg` 被禁用且无人引用；节点无 supply | 原理图/厂商 DTS 变体或实机电压 |
| U7 | 矩阵尺寸与坐标映射 | DT 无几何属性；固件回报才是来源 | 固件扫描启动后的几何回报（`nvt_start_scanning` 路径） |
| U8 | 出厂固件版本与三变体归属 | DT 的 `cfg_0` 只列 fw01/pen；`porting.toml` 记厂商分支有 fw01-03 | 固件容器/分区读取或厂商发布说明 |
| U9 | `novatek,swrst-n8-addr = 0x3f0fe`、`spi-rd-fast-addr = 0x3f310` 的地址空间归属 | DT 只给数值，未声明基址/页 | 厂商驱动常量表 |
| U10 | `novatek,display-maker = 0x42` 的用途 | DT 只给数值 | 厂商驱动或面板配对表 |
| U11 | `xiaomi_touch` 节点的作用 | 该节点只有 `touch,name="xiaomi-touch"` 与 compatible，无资源 | 厂商 `TOUCHSCREEN_XIAOMI_TOUCHFEATURE` 源码 |
| U12 | XNU 侧 QUP/GPI 的 SMMU 使用方式 | DTB 给了 SID 与 `fastmap`/地址池，但 XNU 侧实现不在本地可读代码中 | 目标 OS 侧驱动或本项目已实现的 bypass 路径证据 |
| U13 | 官方两个触摸组件的接口细节 | `drivers/ShengNovatekTouch`、`drivers/ShengHidInput` 本地均未检出（`QcomGeniSpi` 已检出），只能引用文档与 `components.toml` | 按 revision 拉取后的源码核对 |
| U14 | `qcom,rt` 对 SE4 的实际效果 | DT 只给布尔属性 | GENI SPI 驱动实现 |
| U15 | 中断 GPIO 39 与面板/其它外设是否共用 | 树内 `gpio39` 也出现在未引用的 `pmx_ts_*` 组 | `gpio` 汇总表或实机冲突观测 |
| U16 | 本板 SE4 的 FIFO 接口是否可用 | `GENI_IF_DISABLE_RO`(0x64) 是寄存器状态；`geni_spi_init` 在 FIFO 被禁用且未走 DMA 时返回 `GENI_ERR_NOTSUP`（`GeniSpi.c:80`） | 读 `0x64`（SE4 基址 + 0x64）与 `SE_HW_PARAM_0`（+0xe24） |

---

## 5. 引用文件

| 文件 | 用途 |
| --- | --- |
| `enuma/UniXNU-enuma/.cache/firmware/dtb/sm8250-xiaomi-enuma.dts` | §1 全部数据（B1-B4） |
| `enuma/UniXNU-enuma/dts/enuma.dts` | §2.5 ADT 源现状 |
| `enuma/UniXNU-enuma/board.toml`、`porting.toml:161` | §2.5 组件与既有记录 |
| `enuma/UniXNU-enuma/scripts/{plan_adt,check_enuma_drivers,audit_inputs,audit_reuse}.py` | §2.5 遗留脚本（format 1） |
| `UniXNU/components.toml`（`:144-205`）、`UniXNU/devices.toml`（`:616-627`） | §2.1、§2.5 |
| `UniXNU/docs/zh/drivers/{sheng-novatek-touch,sheng-hid-input,qcom-geni-spi,device-tree-matching}.md`、`UniXNU/docs/zh/porting/input.md`、`UniXNU/docs/zh/xnu/four-k-page-tables.md:158` | §2.2、§2.3、§3 |
| `UniXNU/docs/devices/{alioth,erhai-xingxing19035,asteroids}.md` | §2.4 先例 |
| `UniXNU/scripts/unixnu/devicetree.py:370-377` | ADT 导出条件 |
| `UniXNU/drivers/QcomGeniSpi/{GeniSpi.h,GeniSpi.c}` | §2.2 实际函数接口（本地已检出） |
| `enuma/UniXNU-sm8250-common/dts/sm8250.dtsi:99-108` | 共享仓 QUP 节点现状 |

`self-checked`：§1 数值全部由 B1-B4 直接从本板 DTB 文本读出；§2/§3 的官方侧条目全部引自上述仓内文件的行号（`QcomGeniSpi` 为本地源码，`ShengNovatekTouch`/`ShengHidInput` 未检出，见 U13）；未上机、未读寄存器（U16 等）、未查社区仓、未做独立 verifier 复跑。
