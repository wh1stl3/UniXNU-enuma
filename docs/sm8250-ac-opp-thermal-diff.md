# enuma（SM8250-AC）OPP / 热区 / 电源票：本板 DTB 与共享仓逐项差异

状态：**`self-checked`**（纯离线只读静态提取；未上机，未读任何寄存器，未做独立 verifier 复跑）
整理日期：2026-11-17
范围：`enuma/UniXNU-enuma`（本板 DTB）、`enuma/UniXNU-sm8250-common@166235ec`（共享仓）、`UniXNU`（只读基线）
本文只列事实、差异、缺口与未确定项，不含判断或建议。

---

## 0. 方法与复跑命令

全部命令在 WSL Ubuntu-22.04 中执行（工作目录 `/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma`），退出码均为 0。

| # | 命令 | 用途 |
| --- | --- | --- |
| A1 | `dtc -I dtb -O dts -o /tmp/e1.dts .cache/firmware/dtb/sm8250-xiaomi-enuma.dtb` | 反编译本板固件 DTB（`DTC 1.6.1`） |
| A2 | `cmp -s /tmp/e1.dts .cache/firmware/dtb/sm8250-xiaomi-enuma.dts` | 退出 0：仓库内已存反编译文本与 A1 输出**逐字节相同**，故下文行号可直接引用该 `.dts` |
| A3 | `sha256sum .cache/firmware/dtb/sm8250-xiaomi-enuma.dtb` | `42d36a005024e1a7c55cb5da077a13bb17e9fb9a79dc9dfac8a61cf1e182f698`（977523 B） |
| A4 | `sha256sum .cache/firmware/dtb/sm8250-xiaomi-enuma.dts` | `1dd9a06aec6a7af677026c3c1dbbd4f05944b6dea4ad2583f26654f469f408b9`（1593058 B / 42325 行） |
| A5 | 树解析脚本 `dtsx.py`（仓库外，临时目录 `%TEMP%/opencode/`） | 按缩进建树、解析 phandle、导出 OPP 表 / thermal-zones / 电源节点 |
| A6 | `grep -c 'thermal-sensors =' .cache/firmware/dtb/sm8250-xiaomi-enuma.dts` | `87`（90 个 zone 中 3 个无 `thermal-sensors`） |
| A7 | `grep -c 'gpu-opp-table_v2'`（`.dts` 与 `fdt-live.dts` 各一次） | 均为 `2`（定义 + 一处引用） |
| A8 | 交叉源：`fdt-live.dts` 统计 | `thermal-sensors =` 87 处、`gpu-opp-table_v2` 2 处，与 A6/A7 一致 |

**DTB 身份**：本表数据来自 `.cache/firmware/dtb/sm8250-xiaomi-enuma.dtb`，生成方式为 `fdtoverlay`（vendor_boot `dtb` blob0 + `dtbo-entry07.dtbo`），来源与哈希见 `docs/ufs-reserved-memory-audit.md` §1.1。它**不是** `dts/enuma.dts` 编译出的 XNU ADT（两者用途区分见同文 §1.2）。

---

## 1. 本板 DTB 事实

### 1.1 CPU：DTB 中不存在 CPU `opp-table`

| 事实 | 值 | 出处 |
| --- | --- | --- |
| `/cpus` 下的 `opp-hz` / `opp-microvolt` / `operating-points-v2` | **不存在**（全树 9 个 OPP 表全部在 `/soc` 下，无一个挂在 `/cpus`） | A5 `opps`；§1.3 表 |
| CPU 节点（8 个，affinity `0x0/0x100/…/0x700`） | `compatible = "qcom,kryo"`、`enable-method = "psci"`、`cpu-release-addr = <0 0x90000000>` | `.dts:41-288` |
| `qcom,freq-domain` | cpu@0-@300 → `<0x04 0x00 0x04>`；cpu@400-@600 → `<0x04 0x01 0x04>`；cpu@700 → `<0x04 0x02 0x04>` | `.dts:48,85,115,145,175,206,236,266` |
| `capacity-dmips-mhz` | 小核 `0x400`(1024)；cpu@400-@700 全部 `0x766`(1894) | `.dts:49,86,116,146,176,207,237,267` |
| `dynamic-power-coefficient` | 小核 `0x64`(100)；cpu@400-@600 `0x215`(533)；cpu@700 `0x282`(642) | `.dts:50,87,117,147,177,208,238,268` |
| `#cooling-cells` | 仅 cpu@0(`0x0d`)、cpu@400(`0x11`)、cpu@700(`0x14`) 三个节点有 `<0x02>` | `.dts:51,178,269` |
| `cpu-map` | cluster0=4×cpu（`0x0d-0x10`），cluster1=3×cpu（`0x11-0x13`），cluster2=1×cpu（`0x14`） | `.dts:290-332` |

频率/电压来源节点（phandle `0x04`）：

| 属性 | 值 | 出处 |
| --- | --- | --- |
| 节点 | `/soc/qcom,cpufreq-hw`，`compatible = "qcom,cpufreq-hw-epss"` | `.dts:1262-1263` |
| `reg` / `reg-names` | `<0x18591000 0x1000 0x18592000 0x1000 0x18593000 0x1000>` / `freq-domain0,freq-domain1,freq-domain2` | `.dts:1264-1265` |
| `qcom,lut-row-size` / `qcom,skip-enable-check` | `<0x04>` / 存在 | `.dts:1268-1269` |
| `interrupts` / `interrupt-names` | `<0 0x1e 4 0 0x1f 4 0 0x13 4>` / `dcvsh0_int,dcvsh1_int,dcvsh2_int`（GIC SPI 30 / 31 / 19） | `.dts:1271-1272` |
| `clocks` | `<0x15 0x00 0x16 0xd1>` = `rpmhclk` xo + `gcc` 0xd1（`clock-names = "xo","alternate"`） | `.dts:1266-1267` |
| 子节点 | `cpu7-notify`（`#cooling-cells`，`qcom,cooling-cpu = <0x14>`）、`qcom,cpu-isolation`（cpu0-7-isolate，各 `#cooling-cells`）、`qcom,limits-dcvs`（`compatible = "qcom,msm-hw-limits"`，`isens_vref_0p8/1p8-supply` + `*-settings`） | `.dts:1275-1339` |

即：CPU 频率与电压在 DT 中只表现为 **EPSS 硬件 freq-domain**（每域一个 MMIO 窗口 + `lut-row-size`），具体档位/电压/level 需要读硬件 LUT 或设备侧软件接口；DT 内没有任何数值表。

已记录的设备侧观测（非本文提取，供核对）：`porting.toml:45` 记一次 rooted 只读 sysfs 采样——cpu0-3 共 18 档（300000–1804800 kHz）、cpu4-6 共 18 档（710400–2419200 kHz）、cpu7 共 21 档（844800–3187200 kHz），并记「live FDT 无 OPP 表，AC prime 步进 3187200 kHz 属板级数据」。本文 A1-A8 与该条「无 OPP 表」的结论一致；本文未重跑该设备采样。

### 1.2 GPU（A650）与 GMU

| 事实 | 值 | 出处 |
| --- | --- | --- |
| GPU 节点 | `/soc/qcom,kgsl-3d0@3d00000`，`compatible = "qcom,kgsl-3d0","qcom,kgsl-3d"`，`label = "kgsl-3d0"`，`status = "ok"` | `.dts:39128-39131` |
| `reg` / `reg-names` | `0x3d00000+0x40000`、`0x3d61000+0x800`、`0x3de0000+0x10000`、`0x3d8b000+0x2000`、`0x6900000+0x80000` / `kgsl_3d0_reg_memory,cx_dbgc,rscc,isense_cntl,qdss_gfx` | `.dts:39132-39133` |
| `interrupts` | `<0 0x12c 4>` = GIC SPI 300，`interrupt-names = "kgsl_3d0_irq"` | `.dts:39134-39135` |
| `qcom,chipid` / `qcom,ubwc-mode` / `qcom,highest-bank-bit` / `qcom,min-access-length` | `0x6050002` / `<0x04>` / `<0x10>` / `<0x20>` | `.dts:39137-39142` |
| `qcom,gpu-qdss-stm` | `<0x161c0000 0x40000>` | `.dts:39144` |
| `qcom,tzone-names` | `"gpuss-0-usr","gpuss-1-usr"` | `.dts:39146` |
| `regulator-names` / supply | `vddcx`=`<0x17d>` → `/soc/qcom,gdsc@3d9106c`（`regulator-name = "gpu_cx_gdsc"`）；`vdd`=`<0x1b0>` → `/soc/qcom,gdsc@3d9100c`（`gpu_gx_gdsc`） | `.dts:39153-39155`、`4934`、`4960` |
| `operating-points-v2` | `<0x340>` → `/soc/gpu-opp-table_v2` | `.dts:39156` |
| `nvmem-cells` / `nvmem-cell-names` | `<0x342 0x343>` / `isense_slope,speed_bin` | `.dts:39157-39158` |
| bus 表 | `qcom,gpu-bus-table-0`(ddr7)/`-1`(ddr8)，各 `num-cases = <0x0c>`（12 档 KBps） | `.dts:39163-39177` |
| `qcom,l3-pwrlevels` | level0 `l3-freq = 0`；level1 `0x337f9800`(864 MHz)；level2 `0x501bd000`(1344 MHz) | `.dts:39179-39198` |
| `qcom,gpu-mempools` | 4 个池：page 4 KiB×`0x800`（allocate）、8 KiB×`0x400`（allocate）、64 KiB×`0x100`、1 MiB×`0x20` | `.dts:39200-39230` |

两个 GPU OPP 表（`opp-microvolt` 原文为小整数，语义未在 DT 内声明）：

| 表 | phandle | 条目（`opp-hz` 原文 → Hz / `opp-microvolt` 原文） | 引用方 |
| --- | --- | --- | --- |
| `/soc/gpu-opp-table`（`.dts:39108`） | `0x635` | `0x1c9c3800`/480000000/`0xc0`；`0x16b59940`/381000000/`0x80`；`0x11490c80`/290000000/`0x40` | **无节点引用**（`refs 0x635` 无输出）；仅 `__symbols__` 别名 `gpu_opp_table`（`.dts:42274`） |
| `/soc/gpu-opp-table_v2`（`.dts:39807`） | `0x340` | 670000000/`0x140`；587000000/`0x100`；525000000/`0xe0`；490000000/`0xc0`；441600000/`0x90`；400000000/`0x80`；305000000/`0x40` | `kgsl-3d0`（`39156`）、`kgsl-busmon`（`39096`） |

GPU speed-bin 表（`qcom,gpu-pwrlevel-bins`，`.dts:39232-39700`）：

| bin 节点 | `qcom,speed-bin` | `initial-pwrlevel` | `throttle-pwrlevel` | 档数 | 频率序列（MHz，末档为 off=0） |
| --- | --- | --- | --- | --- | --- |
| `gpu-pwrlevels-0` | `0x00` | `0x05` | `0x00` | 7 | 587, 525, 490, 441.6, 400, 305, 0 |
| `gpu-pwrlevels-1` | `0x01` | `0x06` | `0x01` | 8 | 670, 587, 525, 490, 441.6, 400, 305, 0 |
| `gpu-pwrlevels-2` | `0x03` | `0x04` | 无 | 6 | 525, 490, 441.6, 400, 305, 0 |
| `gpu-pwrlevels-3` | `0x02` | `0x06` | `0x01` | 8 | 670, 587, 525, 490, 441.6, 400, 305, 0 |
| `gpu-pwrlevels-4` | `0x04` | `0x06` | `0x01` | 8 | 670, 587, 525, 490, 441.6, 400, 305, 0 |

每档另有 `qcom,bus-freq-ddr7/-ddr8`、`bus-min-*`、`bus-max-*`（总线档索引，0x00–0x0b）与 `qcom,acd-level`（`0x802b5ffd` 用于高两档、`0xa02b5ffd` 用于其余档；`gpu-pwrlevel@N` 为 off 档时无这些属性）。speed-bin 来自 efuse：`/soc/qfprom@780000/gpu_speed_bin@419b`，`reg = <0x419b 0x01>`、`bits = <0x05 0x03>`（bit 5 起 3 位）。

GMU 与 GPU SMMU：

| 事实 | 值 | 出处 |
| --- | --- | --- |
| GMU 节点 | `/soc/qcom,gmu@3d6a000`，`compatible = "qcom,gpu-gmu"`，`label = "kgsl-gmu"` | `.dts:39731-39733` |
| GMU `reg` | `0x3d6a000+0x30000`、`0xb290000+0x10000`、`0xb490000+0x10000` / `kgsl_gmu_reg,kgsl_gmu_pdc_cfg,kgsl_gmu_pdc_seq` | `.dts:39734-39735` |
| GMU 中断 | `<0 0x130 4 0 0x131 4>` = SPI 304/305，`kgsl_hfi_irq,kgsl_gmu_irq` | `.dts:39736-39737` |
| GMU 电源 | `vddcx`=`<0x17d>`、`vdd`=`<0x1b0>`；`clocks` = gmu_clk/cxo_clk/axi_clk/memnoc_clk/gpu_cc_ahb/apb_pclk；`mboxes = <0x02 0x00>`（`mbox-names = "aop"`） | `.dts:39742-39748` |
| GMU OPP 表 | **DTB 内不存在**（GMU 节点无 `operating-points-v2`） | A5；`refs` 无命中 |
| GPU SMMU（context bank 定义） | `/soc/qcom,kgsl-iommu@3da0000`，`compatible = "qcom,kgsl-smmu-v2"`；`gfx3d_user` `iommus = <0x182 0 0x401>`、`gfx3d_secure` `<0x182 2 0x400>`、`gmu_user` `<0x182 4 0x400>`、`gmu_kernel` `<0x182 5 0x400>` | `.dts:39702-39764` |
| GPU SMMU（硬件） | `/soc/kgsl-smmu@3da0000`，`compatible = "qcom,qsmmu-v500"`，`reg = <0x3da0000 0x10000 0x3dc2000 0x20>`，`#global-interrupts = <0x02>`，10 条中断（SPI 0x2a0/0x2a1/0x2a6-0x2ad），`qcom,actlr = <2 0x400 0x32b 4 0x400 0x32b 5 0x400 0x32b 7 0x400 0x32b 0 0x401 0x32b>`，TBU `gfx_0_tbu@3dc5000`(SID 0x00-0x3ff)、`gfx_1_tbu@3dc9000`(SID 0x400-0x7ff) | `.dts:12728-12765` |

### 1.3 全树 OPP 表清单（9 个，全部在 `/soc`）

| 表 | phandle | 条目数 | 取值 |
| --- | --- | --- | --- |
| `keepalive-opp-table` | `0x49` | 1 | `opp-hz = <0 1>` |
| `llcc-bw-opp-table` | `0x4a` | 7 | 150/300/466/600/806/933/1000（MB/s，`opp-hz` 原值 `0x8f0…0x3b9a`） |
| `suspendable-llcc-bw-opp-table` | `0x4e` | 8 | 0 + 上述 7 档 |
| `ddr-bw-opp-table` | `0x4c` | 12 | 200/300/451/547/681/768/1017/1353/1555/1804/2092/2736；`opp-supported-hw` 分别为 `0x180`×10、`0x80`(1353)、`0x100`(2736) |
| `suspendable-ddr-bw-opp-table` | `0x50` | 13 | 0 + 上述 12 档（`opp-supported-hw` 同步） |
| `qoslat-opp-table` | `0x55` | 2 | `opp-hz = <0 1>`、`<0 2>` |
| `gpu-opp-table` | `0x635` | 3 | 480/381/290 MHz（无引用，见 §1.2） |
| `gpu-opp-table_v2` | `0x340` | 7 | 305–670 MHz（见 §1.2） |

消费方：`qcom,devbw-ddr`（`qcom,gpubw`，`operating-points-v2 = <0x50>`，`.dts:39100-39106`）、DDR/LLCC 带宽投票节点（`.dts:4127-4291` 一段）、`kgsl-busmon`（`<0x340>`）。全部表均无 `opp-level`、无 `opp-peak-kBps`、无 `opp-microamp`。

### 1.4 `thermal-zones`

容器：`/soc/thermal-zones`（`.dts:1342`）——**90 个 zone**，`129` 条 trip，`76` 条 cooling map；governor 分布 `user_space 49 / step_wise 34 / low_limits_cap 7`。三处 zone 无 `thermal-sensors`（`gpuss-max-step`、`apc-0-max-step`、`apc-1-max-step`），故全树 `thermal-sensors =` 只有 87 处（A6/A8）。

传感器实例：

| 传感器节点 | `compatible` | `reg` / `reg-names` | 中断 | `#thermal-sensor-cells` | 出处 |
| --- | --- | --- | --- | --- | --- |
| `/soc/tsens@c222000` | `qcom,tsens24xx` | `0xc222000+0x4`、`0xc263000+0x1ff` / `tsens_srot_physical,tsens_tm_physical` | SPI 506/508（`tsens-upper-lower,tsens-critical`） | 1 | `.dts:8954` |
| `/soc/tsens@c223000` | `qcom,tsens24xx` | `0xc223000+0x4`、`0xc265000+0x1ff` | SPI 507/509 | 1 | `.dts:8965` |
| `/soc/qcom,spmi@c440000/qcom,pm8150@0/adc_tm@3500` | — | — | — | 1 | 被 3 个 zone 引用 |
| `…/qcom,pm8150b@2/adc_tm@3500` | — | — | — | 1 | 被 2 个 zone 引用 |
| `…/qcom,pm8150l@4/adc_tm@3500` | — | — | — | 1 | 被 4 个 zone 引用 |
| `…/qcom,pm8150@0/qcom,temp-alarm@2400` | `qcom,spmi-temp-alarm` | `0x2400+0x100`，`io-channels = <0x64d 0x06>`，`io-channel-names = "thermal"`，`qcom,temperature-threshold-set = <0x01>` | `.dts:74-77` 区域 | 0 | `.dts`（pm8150/8150b/8150l 三份） |
| `…/qcom,pm8150b@2/bcl@1d00`、`…/pm8150l@4/bcl@3d00` | `qcom,bcl-v5` | `0x1d00+0x100` / `0x3d00+0x100`，`interrupts = <2 0x1d 0 0> …`（`bcl-lvl0/1/2`） | — | 1 | `.dts:5504`、`5950` |
| `…/qcom,pm8150b@2/bcl-soc` | `qcom,msm-bcl-soc` | — | — | 0 | `.dts:5943`，**`status = "disabled"`** |
| `/soc/qmi-ts-sensors` | — | — | — | 1 | 16 个 modem zone |

完整 90 个 zone（`trips` 为 `temperature` 属性原值；`user_space`/`temp-alarm` 的值为毫摄氏度，`bcl`/`vbat`/`vph`/`ibat`/`soc` 的值为 BCL 电平或 mV/mA，DT 内无单位声明；PMIC 子节点均在 `/soc/qcom,spmi@c440000/` 之下）：

| # | zone | sensor | governor | trips (raw) | cooling map 目标 |
| --- | --- | --- | --- | --- | --- |
| 1 | `flash_therm` | `qcom,pm8150l@4/adc_tm@3500 0x52` | user_space | active-config0=`0x1e848` | - |
| 2 | `backlight_therm` | `qcom,pm8150l@4/adc_tm@3500 0x4f` | user_space | active-config0=`0x1e848` | - |
| 3 | `pa_therm0` | `qcom,pm8150l@4/adc_tm@3500 0x4e` | user_space | active-config0=`0x1e848` | - |
| 4 | `pa_therm1` | `qcom,pm8150l@4/adc_tm@3500 0x4d` | user_space | active-config0=`0x1e848` | - |
| 5 | `quiet_therm` | `qcom,pm8150@0/adc_tm@3500 0x4e` | user_space | active-config0=`0x1e848` | - |
| 6 | `cpu_therm` | `qcom,pm8150@0/adc_tm@3500 0x4d` | user_space | active-config0=`0x1e848` | - |
| 7 | `conn_therm` | `qcom,pm8150b@2/adc_tm@3500 0x4f` | user_space | active-config0=`0x1e848` | - |
| 8 | `charger_therm0` | `qcom,pm8150b@2/adc_tm@3500 0x4d` | user_space | active-config0=`0x1e848` | - |
| 9 | `pm8150l-bcl-lvl2` | `pm8150l@4/bcl@3d00 0x07` | step_wise | l-bcl-lvl2=`0x01` | vph_gpu2→`kgsl-3d0`(state -2) |
| 10 | `pm8150l-bcl-lvl1` | `pm8150l@4/bcl@3d00 0x06` | step_wise | l-bcl-lvl1=`0x01` | vph_gpu1→`kgsl-3d0`(4)、vph_cpu7→`cpu7-isolate`(1)、vph_cpu6→`cpu6-isolate`(1) |
| 11 | `pm8150l-bcl-lvl0` | `pm8150l@4/bcl@3d00 0x05` | step_wise | l-bcl-lvl0=`0x01` | vph_gpu0→`kgsl-3d0`(2)、vph_cpu5→`cpu5-isolate`、vph_cpu4→`cpu4-isolate` |
| 12 | `pm8150l-vph-lvl2` | `pm8150l@4/bcl@3d00 0x04` | low_limits_cap | vph-lvl2=`0x9c4` | - |
| 13 | `pm8150l-vph-lvl1` | `pm8150l@4/bcl@3d00 0x03` | low_limits_cap | vph-lvl1=`0xabe` | - |
| 14 | `pm8150l-vph-lvl0` | `pm8150l@4/bcl@3d00 0x02` | low_limits_cap | vph-lvl0=`0xbb8` | - |
| 15 | `pm8150l_tz` | `pm8150l@4/qcom,temp-alarm@2400` | step_wise | trip2=`0x23668`, trip1=`0x1c138`, trip0=`0x17318` | - |
| 16 | `soc` | `pm8150b@2/bcl-soc` | low_limits_cap | soc-trip=`0x0a` | soc_cpu7/6/5/4→`cpu7/6/5/4-isolate` |
| 17 | `pm8150b-bcl-lvl2` | `pm8150b@2/bcl@1d00 0x07` | step_wise | b-bcl-lvl2=`0x01` | vbat_gpu2→`kgsl-3d0`(-2) |
| 18 | `pm8150b-bcl-lvl1` | `pm8150b@2/bcl@1d00 0x06` | step_wise | b-bcl-lvl1=`0x01` | vbat_gpu1→`kgsl-3d0`(4)、vbat_cpu7→`cpu7-isolate`、vbat_cpu6→`cpu6-isolate` |
| 19 | `pm8150b-bcl-lvl0` | `pm8150b@2/bcl@1d00 0x05` | step_wise | b-bcl-lvl0=`0x01` | vbat_gpu0→`kgsl-3d0`(2)、vbat_cpu5/cpu4→`cpu5/4-isolate` |
| 20 | `pm8150b-vbat-lvl2` | `pm8150b@2/bcl@1d00 0x04` | low_limits_cap | vbat-lvl2=`0xa28` | - |
| 21 | `pm8150b-vbat-lvl1` | `pm8150b@2/bcl@1d00 0x03` | low_limits_cap | vbat-lvl1=`0xaf0` | - |
| 22 | `pm8150b-vbat-lvl0` | `pm8150b@2/bcl@1d00 0x02` | low_limits_cap | vbat-lvl0=`0xbb8` | - |
| 23 | `pm8150b-ibat-lvl1` | `pm8150b@2/bcl@1d00 0x01` | step_wise | ibat-lvl1=`0x251c` | - |
| 24 | `pm8150b-ibat-lvl0` | `pm8150b@2/bcl@1d00 0x00` | step_wise | ibat-lvl0=`0x157c` | - |
| 25 | `pm8150b_tz` | `pm8150b@2/qcom,temp-alarm@2400` | step_wise | trip2=`0x23668`, trip1=`0x1c138`, trip0=`0x17318` | - |
| 26 | `pm8150_tz` | `pm8150@0/qcom,temp-alarm@2400` | step_wise | trip2=`0x23668`, trip1=`0x1c138`, trip0=`0x17318` | - |
| 27 | `aoss0-usr` | `tsens@c222000 0x00` | user_space | active-config0=`0x1e848`, active-config1=`0x1c138` | - |
| 28-31 | `cpu-0-0-usr` … `cpu-0-3-usr` | `tsens@c222000 0x01-0x04` | user_space | 同上两条 | - |
| 32-33 | `cpuss-0-usr`、`cpuss-1-usr` | `tsens@c222000 0x05-0x06` | user_space | 同上 | - |
| 34-41 | `cpu-1-0-usr` … `cpu-1-7-usr` | `tsens@c222000 0x07-0x0e` | user_space | 同上 | - |
| 42 | `gpuss-0-usr` | `tsens@c222000 0x0f` | user_space | 同上 | - |
| 43 | `aoss-1-usr` | `tsens@c223000 0x00` | user_space | 同上 | - |
| 44-50 | `cwlan-usr`,`video-usr`,`ddr-usr`,`q6-hvx-usr`,`camera-usr`,`cmpss-usr`,`npu-usr` | `tsens@c223000 0x01-0x07` | user_space | 同上 | - |
| 51 | `gpuss-1-usr` | `tsens@c223000 0x08` | user_space | 同上 | - |
| 52 | `gpuss-max-step` | （无） | step_wise | gpu-trip0=`0x17318` | gpu_cdev→`kgsl-3d0`(-1) |
| 53 | `apc-0-max-step` | （无） | step_wise | silver-trip=`0x1d4c0` | - |
| 54 | `apc-1-max-step` | （无） | step_wise | gold-trip=`0x1d4c0` | - |
| 55 | `pop-mem-step` | `tsens@c223000 0x03` | step_wise | pop-trip=`0x17318` | pop_cdev4→`cpus/cpu@400`(-1)、pop_cdev7→`cpus/cpu@700`(-1) |
| 56-59 | `cpu-0-0-step` … `cpu-0-3-step` | `tsens@c222000 0x01-0x04` | step_wise | cpu0N-config=`0x1adb0` | cpu0N_cdev→`cpuN-isolate`(1) |
| 60-67 | `cpu-1-0-step` … `cpu-1-7-step` | `tsens@c222000 0x07-0x0e` | step_wise | cpufreq-1N-config=`0x124f8`；cpu1N-config=`0x1adb0` | cpufreq_cdev→`cpu7-notify`(1)；cpu1N_cdev→`cpu4/5/6/7-isolate` |
| 68-74 | `cwlan-step`,`video-step`,`ddr-step`,`q6-hvx-step`,`camera-step`,`cmpss-step`,`npu-step` | `tsens@c223000 0x01-0x07` | step_wise | 各自 `*-trip0`=`0x186a0` | 每条 5 个：cdsp-cdev→`msm_cdsp_rm`(3)、gpu-cdev→`kgsl-3d0`(-3)、modem-pa/tj-cdev→`modem_pa`/`modem_tj`(3)、npu_cdev→`msm_npu@9800000`(-5) |
| 75-90 | `modem1_pa0/1`、`modem-mmw0-3-usr`、`modem1_xo/wifi/quiet`、`modem-0/1-usr`、`modem-streamer-usr`、`modem-mmw0-3-mod-usr` | `qmi-ts-sensors 0x64/0x65/0x6a-0x6d/0x6e/0x7b/0x7c/0x69/0x7d/0x71/0x72-0x75` | user_space | active-config0=`0x1e848` | - |

说明：本表 27–74 行是按连续相同取值合并的行，未合并的逐行数据见 A5 输出（90 行全表）。`active-config0=0x1e848` 对应 125000（毫摄氏度），`0x1c138` = 115000，`0x17318` = 95000，`0x1adb0` = 110000，`0x186a0` = 100000，`0x1d4c0` = 120000，`0x124f8` = 75000，`0x2710` = 10000（hysteresis）。

### 1.5 电源域 / 电源票

| 组 | 节点与取值 | 出处 |
| --- | --- | --- |
| RPMh ARC level 调节器（7 个） | `rpmh-regulator-mxlvl`(`mx.lvl`)、`cxlvl`(`cx.lvl`)、`lmx.lvl`、`lcx.lvl`、`gfxlvl`(`gfx.lvl`)、`mmcxlvl`(`mmcx.lvl`)、`ebi.lvl`，`compatible = "qcom,rpmh-arc-regulator"` | `.dts:6846,6879,6997,7127,7289,7303,7342` |
| ARC 子调节器取值 | 例：`regulator-pm8150a-s3-level`（MX）`regulator-min-microvolt = <0x10>`、`max = <0xffff>`、`qcom,init-voltage-level = <0x10>`（另含 `-ao` 变体 `qcom,set = <0x01>` 与 `mmcx-sup` 变体）；CX 为 `pm8150_s3_level` 系列，GFX 为 `pm8150a_s1_level`，MMCX 为 `pm8150a_s4_level` | `.dts:6851-6876`、`40849-40906` |
| `proxy-supply` / parent 链 | `cxlvl` 下 `proxy-supply = <0x7c>`（= `cx` 的 mmcx-sup level）；`mxlvl` 的 `pm8150a_s3_mmcx_sup_level-parent-supply = <0x7c>`；`cxlvl` parent 为 `<0x69>`(MX level) | `.dts:6849,6882-6884` |
| GDSC（25 个） | `gpu_cx_gdsc`(`0x3d9106c`, `hw-ctrl-addr = <0x71>`, `vdd_parent` = CX level)、`gpu_gx_gdsc`(`0x3d9100c`, `domain-addr = <0x72>`, `sw-reset = <0x73>`, `vdd_parent` = GFX level)、`mdss_core_gdsc`、`ufs_phy_gdsc`、`ufs_card_gdsc`、`pcie_0/1/2_gdsc`、`usb30_prim/sec_gdsc`、4× `hlos1_vote_mmnoc_mmu_tbu_*_gdsc`、`bps/ife_0/ife_1/ipe_0/sbi/titan_top`、`npu_core_gdsc`、`mvs0/mvs0c/mvs1/mvs1c_gdsc` | `.dts:4934,4960` 及其余 23 处 `compatible = "qcom,gdsc"` |
| 显示 power domain | `/soc/qcom,mdss_mdp@ae00000` `#power-domain-cells = <0x00>`、`#cooling-cells = <0x02>`、`mmcx-supply = <0x68>`（= `pm8150a_s4_level`）；`/soc/qcom,mdss_rotator@aea8800` `power-domains = <0x24d>` | `.dts:23000-23014`、`40802` 区 |
| 低功耗模式（L3/LLCC 电源） | `/soc/qcom,lpm-levels`：`pm-cluster@0`（`label = "L3"`，`qcom,psci-mode-mask = <0xfff>`）两级——`l3-wfi`（`psci-mode = 1`，entry 48 µs / exit 51 µs / min-residency 99 µs）、`llcc-off`（`psci-mode = 0xc24`，entry 0xcbf / exit 0x19a2 / min-residency 0x2703，`qcom,is-reset`、`qcom,notify-rpm`） | `.dts:32284-32317` |
| RPMh RSC | `/soc/rsc@18200000`，`qcom,tcs-offset = <0xd00>`、`qcom,drv-id = <0x02>`、`qcom,tcs-config = <2 2 0 3 1 3 3 1>`；子 `qcom,rpmhclk`(`kona-rpmh-clk`)、`system_pm`、`msm_bus_apps_rsc` | `.dts:6820-6844` |
| 电源票消费者（CPU） | `qcom,cpu-isolation/cpuN-isolate` ×8、`cpu7-notify`、`qcom,limits-dcvs`（`isens_vref_0p8-supply = <0x17>` = `pm8150-l5-ao`，`isens_vref_1p8-supply = <0x18>` = `pm8150-l12-ao`，`settings = <0xd6d80 0xd6d80 0x4e20>` / `<0x1b7740 0x1b7740 0x4e20>`） | `.dts:1281-1339` |
| 电源票消费者（GPU） | `kgsl-3d0`/`gmu`/`kgsl-smmu` 的 `vddcx` = `gpu_cx_gdsc`、`vdd` = `gpu_gx_gdsc`；GMU 向 AOP 的 `mboxes = <0x02 0x00>`；`qcom,kgsl-busmon`/`qcom,gpubw` 的 DDR 带宽 OPP 投票 | `.dts:39151-39155`、`39742-39748`、`12732-12733` |

---

## 2. 与共享仓 `dts/sm8250.dtsi` 的逐项 diff

共享仓取值均取自 `enuma/UniXNU-sm8250-common/dts/sm8250.dtsi`（4300 B，110 行，`5b0764a53235…` 主线的子集）。该文件**不含任何** `opp`、`thermal`、`power-domain`、`gdsc`、`tsens`、`rpmh` 字符串（`Select-String` 无命中）。

| # | 节点 / 属性 | 本板 DTB 值 | 共享仓值 | 差异 | 出处（本板 / 共享仓） |
| --- | --- | --- | --- | --- | --- |
| 1 | `/cpus` CPU 数 | 8（0x000–0x700） | 8（0x000–0x700） | 相同 | `.dts:37-333` / `sm8250.dtsi:15-31` |
| 2 | CPU `compatible` | `"qcom,kryo"`（8 个相同） | `"arm,cortex-a55"`（0–300）、`"arm,cortex-a77"`（400–700） | **不同** | `.dts:43,80,110,140,170,201,231,261` / `:21-30` |
| 3 | `capacity-dmips-mhz` | 1024 / 1894 / 1894 | 无 | 共享仓缺 | `.dts:49…267` / — |
| 4 | `dynamic-power-coefficient` | 100 / 533 / 642 | 无 | 共享仓缺 | `.dts:50…268` / — |
| 5 | `#cooling-cells`（CPU） | cpu@0/@400/@700 各 `<2>` | 无 | 共享仓缺 | `.dts:51,178,269` / — |
| 6 | `qcom,freq-domain` | 8 个 CPU 全部有（三域） | 无 | 共享仓缺 | `.dts:48…266` / — |
| 7 | CPU OPP 表 | **不存在**（频率在 EPSS 硬件） | 不存在 | 两侧都无（非差异项，但两侧都缺数值表） | §1.1 / — |
| 8 | `/soc/qcom,cpufreq-hw`（EPSS 3 域） | 有：`0x18591000/0x18592000/0x18593000` 各 `0x1000` | 无 | 共享仓缺 | `.dts:1262-1340` / — |
| 9 | `timebase-frequency` | `cpus` 节点无该属性（timer 节点另有 `clock-frequency = <0x124f800>`） | `cpus/timebase-frequency = <19200000>` | **不同**（共享仓提供 ADT 需要的 24 MHz） | `.dts:37-39` / `:18` |
| 10 | GPU 节点 | `/soc/qcom,kgsl-3d0@3d00000`，`compatible = "qcom,kgsl-3d0","qcom,kgsl-3d"`，5 段 `reg` | `/soc/gpu@3d00000`，`compatible = "qcom,adreno-650.2","qcom,adreno"`，3 段 `reg`（`kgsl_3d0_reg_memory`,`cx_mem`,`cx_dbgc`） | **不同**（节点名、compatible、reg 段落集合；共享仓第二段 `0x3d9e000+0x1000` 在本板为 `rscc 0x3de0000`，本板另有 `isense_cntl 0x3d8b000`、`qdss_gfx 0x6900000`） | `.dts:39128-39133` / `:71-78` |
| 11 | GPU 中断 | `<0 0x12c 4>` | `<0 300 4 0>` | 相同（0x12c=300） | `.dts:39134` / `:75` |
| 12 | GPU `iommus` | `kgsl-iommu` 下 4 个 context bank（`0x182`=`kgsl-smmu`，SID 0/2/4/5） | `<&gpu_smmu 0 0x401>`（单条） | **不同**（表达方式与 bank 集合） | `.dts:39702-39764` / `:76` |
| 13 | GPU OPP 表 | `gpu-opp-table_v2` 7 档（305–670 MHz）+ `gpu-opp-table` 3 档（290–480，无引用） | 无 | 共享仓缺 | `.dts:39108,39807` / — |
| 14 | GPU speed-bin 表 | 5 个 bin（0–4），含 `initial-pwrlevel`/`throttle-pwrlevel`/`bus-freq-*`/`acd-level` | 无 | 共享仓缺 | `.dts:39232-39700` / — |
| 15 | GPU GDSC 供电 | `vddcx`=`gpu_cx_gdsc`(0x3d9106c)、`vdd`=`gpu_gx_gdsc`(0x3d9100c) | 无（`status = "disabled"`，无 regulator 属性） | 共享仓缺 | `.dts:39153-39155,4934,4960` / `:71-78` |
| 16 | GPU efuse | `gpu_lm_efuse@45c8`、`gpu_speed_bin@419b`(`bits = <5 3>`) | 无 | 共享仓缺 | `.dts` qfprom 区 / — |
| 17 | GMU 节点 | `qcom,gmu@3d6a000`，`compatible = "qcom,gpu-gmu"`，3 段 `reg`（`kgsl_gmu_reg`,`kgsl_gmu_pdc_cfg`,`kgsl_gmu_pdc_seq`） | `gmu@3d6a000`，`compatible = "qcom,adreno-gmu-650.2","qcom,adreno-gmu"`，4 段 `reg`（`gmu`,`rscc`,`gmu_pdc`,`gmu_pdc_seq`） | **不同**（compatible 与 reg 段落；共享仓的 `rscc 0x3de0000` 在本板属 GPU 节点） | `.dts:39731-39735` / `:80-89` |
| 18 | GMU 中断 | `kgsl_hfi_irq`=`0x130`(304)、`kgsl_gmu_irq`=`0x131`(305) | `hfi`=304、`gmu`=305 | 相同取值，名称不同 | `.dts:39736-39737` / `:85-86` |
| 19 | GMU OPP | 无 | 无（共享仓 `dts/sm8250.dtsi` 无 OPP；`kits/Sm8250Platform/A650Gmu.c:368-369` 以代码常量硬编码 200 MHz / level 48） | 两侧 DT 均缺；kit 在代码里给值 | `.dts:39731-39764` / `A650Gmu.c:364-369` |
| 20 | GPU SMMU | `kgsl-smmu@3da0000`（`qcom,qsmmu-v500`，`0x3da0000+0x10000`+`0x3dc2000+0x20`，10 中断，`qcom,actlr`，2 TBU）+ 独立 `qcom,kgsl-iommu@3da0000` | `iommu@3da0000`（`qcom,sm8250-smmu-500`,`qcom,adreno-smmu`,`arm,mmu-500`，`0x3da0000+0x10000`，`#global-interrupts = <2>`） | **不同**（compatible 与寄存器/中断集合） | `.dts:12728-12765,39702` / `:91-97` |
| 21 | `thermal-zones` | 90 个 zone、129 trip、76 cooling map | 无 | 共享仓缺 | §1.4 / — |
| 22 | TSENS | `tsens@c222000`、`tsens@c223000`（`qcom,tsens24xx`，各 2 reg + 2 中断） | 无 | 共享仓缺 | `.dts:8954,8965` / — |
| 23 | PMIC 温度/BCL | `adc_tm@3500`×3、`qcom,temp-alarm@2400`×3、`bcl@1d00`/`bcl@3d00`、`bcl-soc`(disabled) | 无 | 共享仓缺 | §1.4 / — |
| 24 | RPMh ARC 调节器 | 7 个 ARC level 域 + `proxy-supply`/parent 链 | 无 | 共享仓缺 | §1.5 / — |
| 25 | GDSC | 25 个（含 GPU 2 个、`mdss_core_gdsc`） | 无 | 共享仓缺 | `.dts:4934` 等 / — |
| 26 | 显示 power domain / MMCX | `mdss_mdp` `#power-domain-cells = <0>`、`mmcx-supply = <0x68>` | 无 | 共享仓缺 | `.dts:23000-23014` / — |
| 27 | `qcom,lpm-levels` | L3 两级（`l3-wfi`、`llcc-off`）+ PSCI 模式掩码 | 无 | 共享仓缺 | `.dts:32284-32317` / — |
| 28 | 带宽 OPP 表 | LLCC/DDR + suspendable 变体 + `qoslat` + `keepalive`（7 张） | 无 | 共享仓缺 | §1.3 / — |
| 29 | 其他共享仓已有、本板也有但取值不同 | UFS `reg = <0x1d84000 0x3000 0x1d90000 0x8000>`（两条 `ufs_mem`,`ufs_ice`） | `reg = <0 0x1d84000 0 0x3000>`（单条） | **不同**（本板多 ICE 窗口） | `.dts:6667` 起 / `:55-60` |
| 30 | QUPv3 wrapper 0 | `reg = <0x9c0000 0x2000>` | `reg = <0 0x9c0000 0 0x6000>` | **不同**（长度 `0x2000` vs `0x6000`） | `.dts:33913` / `:101-108` |
| 31 | `unixnu,adt-name` | 不适用（厂商 DTB 无此属性） | 仅 `intc`、`ufshc`、`ufsphy`（3 个） | 共享仓选择性导出 | — / `:45,57,64` |

计数（31 行，逐行归类，互斥）：

| 类别 | 行数 | 行号 |
| --- | --- | --- |
| 取值或结构不同 | 8 | #2、#9、#10、#12、#17、#20、#29、#30 |
| 取值相同、名称不同 | 1 | #18 |
| 相同 | 2 | #1、#11 |
| 本板有、共享仓缺 | 17 | #3、#4、#5、#6、#8、#13、#14、#15、#16、#21、#22、#23、#24、#25、#26、#27、#28 |
| 两侧 DT 均缺（#19 由共享仓代码常量补足） | 2 | #7、#19 |
| 仅共享仓有（`unixnu,adt-name` 导出选择） | 1 | #31 |

即：OPP/热区/电源票相关的 25 行（#3–#6、#8、#13–#16、#19、#21–#28）中，**共享仓缺 17 行 + 两侧 DT 均缺 2 行**，没有一行是本板与共享仓都给出数值表且取值一致的。

---

## 3. 共享仓覆盖不到、必须本板取证的项

以下各项在共享仓 `dts/sm8250.dtsi`、`configs/sm8250.config`、`patches/xnu/*`、`kits/Sm8250Platform/*` 中**没有对应数值**，只能来自本板（DTB、寄存器或设备侧取证）：

1. **CPU 频率/电压档**：DTB 无 OPP 表；EPSS 三域 LUT 内容是硬件状态（§1.1）。共享仓只给 8 个 CPU 节点与 `timebase-frequency`。
2. **CPU 域划分与 prime 步进**：`qcom,freq-domain` 的 3 域归属（0-3 / 4-6 / 7）与 3.19 GHz prime 档不在共享仓。
3. **`capacity-dmips-mhz` / `dynamic-power-coefficient`**：调度与 EAS 输入，共享仓无。
4. **CPU cooling 绑定**：`cpu-isolate`、`cpu7-notify`、`qcom,limits-dcvs` 的 isens 供电与阈值。
5. **GPU OPP 表与 speed-bin 表**：含 670 MHz 档、`initial-pwrlevel`/`throttle-pwrlevel`、每档总线档索引与 `acd-level`。
6. **GPU speed bin 的实际取值**：efuse `0x419b` bit5 起 3 位（`bits = <5 3>`）。
7. **GPU/GMU 寄存器段落差异**：本板 `cx_dbgc 0x3d61000+0x800`、`rscc 0x3de0000+0x10000`、`isense_cntl 0x3d8b000+0x2000`、`qdss_gfx 0x6900000+0x80000` vs 共享仓 `cx_mem 0x3d9e000+0x1000`。
8. **GMU 频率档**：DTB 无 GMU OPP；共享仓 kit 以常量 `{0, 200 MHz}` / level `{0, 48}` 提供（`A650Gmu.c:368-369`），不是 DT 来源。
9. **GPU 供电域**：`gpu_cx_gdsc`/`gpu_gx_gdsc` 地址、`hw-ctrl-addr`/`domain-addr`/`sw-reset` 与父级 ARC 域。
10. **GPU SMMU**：`qcom,actlr` 表、10 条中断、2 个 TBU 的 SID 区间。
11. **热区全集**：90 个 zone、129 trip、76 cooling map（含 CPU/GPU/CDSP/Modem/NPU 联动）。
12. **TSENS 实例与传感器索引**：`c222000`/`c223000` 两实例、25 个片上传感器 + 3 个 PMIC ADC 通道组。
13. **PMIC 温度与 BCL 阈值**：`temp-alarm` 三份 trip（95/115/145 °C）、BCL 电平与 mV/mA 阈值。
14. **RPMh ARC 域初值与依赖**：MX/CX/GFX/MMCX 的 `init-voltage-level`、`-ao` 集合、`proxy-supply` 链。
15. **显示电源域**：`mdss_mdp` power domain、`mmcx-supply`、`mdss_core_gdsc`。
16. **L3/LLCC 低功耗档**：`lpm-levels` 的 PSCI 模式码与延迟。
17. **带宽 OPP 表**：LLCC/DDR 档位与 `opp-supported-hw` 掩码。

## 4. 未确定项

| # | 未确定项 | 为什么静态得不出 | 需要的证据 |
| --- | --- | --- | --- |
| U1 | CPU 各档频率与电压（EPSS LUT 内容） | DTB 只有 3 个 freq-domain 窗口与 `lut-row-size = 4`；无任何数值表 | 读 EPSS LUT 寄存器，或设备侧 `cpufreq` 表（`porting.toml:45` 已录一次 sysfs 频率序列，但无电压/level） |
| U2 | 本机 GPU speed bin | efuse 位段已声明，取值是芯片个体状态 | 读 `0x419b` bit5-7，或设备侧 kgsl sysfs（`porting.toml:175` 记「选定 bin 未被树打印」） |
| U3 | `opp-microvolt` 的单位 | DTB 取值为 `0x40…0x140`(64…320)，未声明单位 | 厂商 cpufreq/OPP 解析语义；共享仓 `A650Gmu.c:367` 按 RPMh level 使用，但该解释不是 DT 内声明 |
| U4 | `gpu-opp-table`（480/381/290 MHz，phandle `0x635`）的用途 | 无设备节点引用，仅 `__symbols__` 别名 | 使用方源码或运行期引用证据 |
| U5 | GMU 200 MHz / level 48 档是否适用于 670 MHz 的 AC 单元 | DTB 无 GMU OPP；kit 常量为通用 A650 值 | GMU 频率回读或厂商 GMU 配置 |
| U6 | 各 tsens zone 的 trip 是否为本板标定 | 全树 trip 是统一 vendor 默认（125 °C / 115 °C / 95 °C / 110 °C…） | 厂商 thermal 配置或实机温升数据；DT 无 `nvmem-cells` 校准引用 |
| U7 | `soc` zone 引用 `bcl-soc`，而该节点 `status = "disabled"` | 两处独立声明 | 启用方证据或该 zone 实际不生效的确认 |
| U8 | ARC `init-voltage-level = 0x10` 与运行期实际票值的关系 | DT 只给下限/初值，运行期由 RPMh 命令决定 | RPMh 命令 trace |
| U9 | 本板 DTB 与活动 FDT 在 OPP/热区块上是否逐字节一致 | 本文只比了计数（A6-A8：87 处 sensor、2 处 v2 表），未做区块 diff | 两棵树的对应子树 diff |
| U10 | CPU 21 档 prime 序列（至 3187200 kHz）在 AC 与 865 之间的差异归属 | 该数据来自设备 sysfs 观测，不在 DT；共享仓不区分子型号 | 同 SoC 参考设备对照或厂商 OPP 源 |
| U11 | XNU/ADT 侧是否有任何消费方 | ADT 生成器对 CPU 只复制 `reg`/`state`/`device_type`/`compatible`/`timebase-frequency`/`unixnu,cluster-type`（`UniXNU/scripts/unixnu/devicetree.py:351-360`），`arm-io` 只导出带 `unixnu,adt-name` 的节点（同文 `:370-377`；共享仓仅 `intc`/`ufshc`/`ufsphy`） | 目标 OS 侧 PMGR/CPUFreq 消费方源码；本文未查证 |

---

## 5. 引用文件

| 文件 | 用途 |
| --- | --- |
| `enuma/UniXNU-enuma/.cache/firmware/dtb/sm8250-xiaomi-enuma.dtb` / `.dts` | §1 全部数据（A1-A4） |
| `enuma/UniXNU-enuma/.cache/firmware/fdt-live.dts` | A8 交叉计数 |
| `enuma/UniXNU-sm8250-common/dts/sm8250.dtsi` | §2 共享仓列 |
| `enuma/UniXNU-sm8250-common/kits/Sm8250Platform/A650Gmu.c`（`:361-394`）、`A650GmuPower.c`（`:301-302`）、`A650GmuPower.h`（`:132-141`） | §2 #19、§3 #8 |
| `enuma/UniXNU-sm8250-common/configs/sm8250.config`、`soc.toml` | 共享仓范围（`CONFIG_XNU_NATIVE_ADRENO` 未启用） |
| `enuma/UniXNU-enuma/porting.toml`（`:45` cpu 区、`:175` gpu 区、`:217` power 区） | 已有设备侧观测记录（本文未重跑） |
| `UniXNU/scripts/unixnu/devicetree.py` | U11：ADT 只复制哪些 CPU/硬件属性 |
| `enuma/UniXNU-enuma/docs/ufs-reserved-memory-audit.md` §1 | DTB 身份与「固件 DTB ≠ XNU ADT」的既有记录 |

`self-checked`：§1/§2 的数值均由 A1-A8 直接从本板 DTB 文本与共享仓源文件读出；未上机、未读寄存器、未做区块级 DTB↔活 FDT diff（U9）、未查目标 OS 侧消费方（U11）、未做独立 verifier 复跑。
