# Sirius 配置对比：未完成（2026-11-23）

仅静态审查；不是全量差异清单。enuma 基线 `98afba250b69594114eaedd88c9e52e228b1afb7`；sirius 基线 `ac0c900485f3c0cd18de9707579a1cdcd3365503`。sirius Setup 触摸记录使用的是不同源码 revision `fb84613a61cf55e48e30f2e126fd6b3183820def`，不能把当前配置的所有内容直接归因于那次实机运行。

## 第 0 步：可比性

| 项目 | sirius 文件:行及原文 | enuma |
|---|---|---|
| SoC | `board.toml:19`：`soc = "SDM710"` | `board.toml:8`：`soc = "SM8250-AC"` |
| 物理机型 | `board.toml:22`：`description = "Xiaomi Mi 8 SE"` | `AGENTS.md:6`：小米平板 5 Pro 5G |
| donor | `board.toml:38`：`product = "iPad7,1"` | `board.toml:53`：`product = "iPad7,1"` |
| 系统版本 | `board.toml:39-40`：`version = "17.7.11"`、`build = "21H461"` | `board.toml:54-55` 同值 |
| 内核页 | `configs/sirius_defconfig:59`：`this 4 KiB kernel` | `AGENTS.md:6`：`4K` |
| 架构 | `board.toml:33-34`：`ARMv8.2 without pointer authentication, so it runs arm64 userlands only` | ARM64 目标；实际用户态 ABI 未在本次核查 |

两者 donor 和版本相同，不存在跨 iOS 代际因素。SoC、物理机型、显示/触摸及存储硬件不同，硬件地址、驱动、时钟和设备树值不可照抄；同版本用户态、显示闭包与启动策略可作实现对照，但不等于运行时二进制可直接互换。

## 已核配置差异和缺口

| 维度 | 已核事实 | 全量差异数 |
|---|---|---|
| A 启动参数 | 两份 `board.toml` 的 `payload.kernel_args` 精确 token 集合：仅 enuma 5、仅 sirius 45、共有 0；未包含 profile 合成和实际设备覆盖，不能称为完整实际 boot-args。 | 未知 |
| B 组件 | 仅 enuma：RamBlock、ShengUfs、SoftwareAES；仅 sirius：AppleKeyStoreState、GopFramebuffer、ShengHidInput；共有 ArmCpu、ArmDTPlatform、DarwinBoot、XnuPrelink。仅比较组件名，不代表实际版本或加载。 | 未知；组件名差异 6 |
| B 打包 | enuma `board.toml:71,162` 配置 payload 160 MiB、boot 分区 201326592 B；sirius `board.toml:101` 配置 payload 256 MiB，RAM seed 时注释为 512 MiB，`:9-13` 描述从 U-Boot/FAT 启动而非 boot image。 | 未知 |
| C ADT | [C] sirius `board.toml:213,224` 指定 `boot-manifest-hash` 和 `ephemeral-storage`；未核完整生成 ADT，不能断言 enuma 缺失。节点逐项比较 [U]。 | 未知 |
| D 补丁 | sirius `board.toml:52` 包含 arch、soc、os、device 四层 series；enuma `board.toml` 使用 device-local os-series。仅看设备 series 不能代表完整实际闭包。 | 未知 |
| E kext | 未获得同口径实际加载列表；组件 include 不等于加载列表。 | 未知 |

## 候选差异，非复刻结论

以下仅为配置层假说，不含 enuma 运行时证据。

| 候选 | 原因 | 验证 | 代价 |
|---|---|---|---|
| 显示与 CPU present | sirius 声明 GOP 显示组件，enuma 默认组件不含 | 对比实际链接、注册、首个 swap | 需本板 framebuffer 适配 |
| 根卷和 Data | sirius 使用不同存储和 Data 路线 | 对比实际根卷、挂载和服务日志 | 所有权及持久化门禁仍独立存在 |
| 触摸 HID | sirius 有 ShengHidInput 组件 | 核对本板触摸采集、描述符和 HID 匹配 | 板级协议与轴值需取证 |
| dyld text fixup | sirius `board.toml:109-119` 声明五项用户态修补 | 核对实际 cache 哈希、偏移及命中计数 | 强绑定系统构建；错误修补会损坏进程 |

缺少合成后的完整启动参数、实际 ADT 的逐键逐节点清单、四层固定 revision 补丁闭包、实际 kext 列表及 Setup 实测 revision 的完整配置；不能据此报告全量差异或完成本任务。
