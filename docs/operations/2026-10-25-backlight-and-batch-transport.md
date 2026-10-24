# 背光与批量传值的落地规格（2026-10-25 01:15）

取向：用户已批准打开背光（R-012）与 R-008 两项（写保留区、warm reset）。本文只记录**实际硬件事实与落地障碍**，不含未执行的结论。

## 一、背光：KTZ8866，必须自写 I2C

已核实（全部来自设备只读）：

| 项 | 值 | 来源 |
| --- | --- | --- |
| 芯片 | KTZ8866，独立背光控制器 | `/sys/class/backlight/4-0011` driver 名 |
| 总线 | `i2c@a8c000`，reg = `0x00a8c000`，size `0x4000` | DTS |
| 从地址 | `0x11` | DTS `reg=00000011` |
| 亮度 | 11 bit，当前 372 / max 2047 | sysfs |
| 控制器时钟 | `se-clk` / `m-ahb` / `s-ahb`（GENI 标准三时钟） | DTS clock-names |
| 控件 | 另有 `enn-gpio` / `enp-gpio` / `hwen-gpio` / `panelid-gpio` 四个属性（实际为空，使能主要走 pinctrl + I2C） | DTS |
| probe 时寄存器快照 | `0x02=0x33 0x03=0xbd 0x04=0x01 0x05=0x7e 0x08=0x5f 0x09=0x9f 0x0f=0x00` | dmesg |

**UEFI 侧现状（这是关键约束）**：

- 镜像里确实打包了 XBL 的 `I2C`、`DALTLMM`、`GpiDxe`、`ClockDxe`（79 个 packaged 里可见），运行时是活的。
- 但本仓 `QcomPkg/Include/Protocol/` **没有 I2C/SPI/GPIO 的 protocol 头文件**（只有 `EFIClock.h`、`EFIPlatformInfo.h`、`EFIDisplayPwr.h`、`EFIDisplayUtils.h`、`EFIScm.h` 等）。所以能用的现成协议是**时钟**和 **SCM**，I2C 协议接口未知。
- `EFI_DISPLAY_POWER_PROTOCOL`（能直接 SetDisplayPowerState）与 `EFI_QCOM_DISPLAY_UTILS_PROTOCOL` 的提供者都是 `DisplayDxe`，而它正是被 `--diagnostic-simplefb` 刻意省略的三个模块之一 → **这两个协议在本镜像里不存在**，靠它们点屏不可行。

**结论**：开背光 = 自写 GENI I2C（用 Clock protocol 配 se-clk/m-ahb/s-ahb + 直接操作 `0xa8c000` 的 SE/GENI 寄存器 + 单次 I2C 写 KTZ8866）。预估 **4–8 小时**，风险在于 pinctrl（SDA/SCL 是否仍处于 I2C 功能）与 GENI 固件握手。

## 二、R-008：warm reset 可用，但"谁读回"是硬障碍

- 好消息：`EFIScm.h` 提供 `QCOM_SCM_PROTOCOL`（`SysCall`/`FastCall2`/`SendCommand`），PSCI warm reset 有现成通道，不必再碰 `ResetSystemLib`（也就绕开了 D-150 那条守卫）。
- **硬障碍**：warm reset 之后设备会走完整 XBL→ABL→正常 Android 启动，我们的 UEFI 不会再次运行；而 `fastboot boot` 每次都是 cold boot，DRAM 必清。所以数据必须由 **Android 侧读回**。
- 而 Android 能安全读到 `0x9fff7000` 的前提是这块内存在 FDT 里被保留（`PageReserved`），也就是 **boot 分区里必须是 R-002 那个带保留区的 boot.img**。当前 A 槽是原厂 boot，没有保留区，内核会把这块内存分给别人、数据随即被覆盖。
- 因此 R-008 完整落地需要一个额外批准：**把 A 槽 boot_a 写成 R-002 的保留区镜像**（或改 misc 让 warm reset 后停在 fastboot，再用 `fastboot boot` 加载 reader 镜像）。两者都是写分区，不在现有批准范围内。

**可先做的降级验证（不写分区）**：只验证 "warm reset 是否保留 DRAM" 这一个二值事实——UEFI 写 magic → SCM warm reset → 若设备重新走到 UEFI（需再次 fastboot boot）则读回。但重新 fastboot boot 本身会 cold boot，该验证在逻辑上不成立，故**不建议**；直接接受"需要写 boot_a"更省时间。

## 三、建议顺序

1. **背光（用户目标是看到屏幕，优先）**：先写 GENI I2C 最小实现，只做"读 KTZ8866 某个寄存器"来验证通道，再写使能与亮度。通道打通前不碰亮度值。
2. **R-008**：等 boot_a 写分区的批准，再一次性做"写批量 dump + warm reset + Android 读回"，避免半成品占用设备时间。
3. 两者都不需要设备的部分（代码、审计、测试）可在离线并行推进。

## 四、不可承诺项

- 不承诺"写两个寄存器就能亮"：KTZ8866 有 ENN/ENP/HWEN 三个使能维度，且面板本身是否已完成初始化尚未独立确认（D-158 只证明 DSI 有帧在跑，不证明面板收到了有效时序）。
- 不承诺 warm reset 一定能保留 DRAM：Qualcomm 平台 warm reset 的实际行为需实测，可能在 XBL 阶段被重新初始化。
