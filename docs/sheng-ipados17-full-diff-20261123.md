# sheng iPadOS 17 / enuma r49 配置对比（未完成）

状态：self-checked，离线读取；未构建、未上机。此文不是全量 diff。
`[A]` 实际包内 ADT；`[C]` 配置；`[U]` 不可得。配置不等于运行时生效。

## 0. 基线

| 候选 | 证据与边界 |
|---|---|
| `0c2046b84dbee545e7e3923eb74d7bb1ce020978` | 历史分支 `sheng/upstream-main-20261111` 可达；同提交 README 报告 Home Screen、Settings 和 Adreno 740 合成，配置 iPad7,1 / 21H461；缺该次镜像及日志，不能将报告归为该提交构建的实测。见 `sheng-donor-branches-20261123.md:107-111`。 |
| `da9fab96aea0b5dcdb3bef730b10397276514dac` | 同历史分支可达；21H461 board 的完整配置可读，提交说明报告 AW 初始化死锁和 logo 停滞，并配置 text-fixup；未证修复后桌面。此前记录 `git log -1 --format=full` 见同文 `:83-105`。 |
| `3ad65c973caf8f64e5c5f7093c8ac73bf03b4064` | 同历史分支 tip 有 17.7.11 override，但默认线与当年不同；不能当作历史桌面镜像。见同文 `:13-17,80`。 |

暂选 `da9fab9` 为**可核对的历史 21H461 配置快照**，不是已证“该线最后一个配置完整 commit”。缺逐提交历史和配置完整性定义，无法完成要求的最后 commit 判定与 `git log --oneline` 证明。
来源：[固定 board.toml](https://github.com/UniXNU/UniXNU-sheng/blob/da9fab96aea0b5dcdb3bef730b10397276514dac/board.toml)。
sheng 小米平板 6S Pro：SM8550 / Adreno 740；enuma 小米平板 5 Pro 5G：SM8250-AC / Adreno 650。两者配置同 iPad7,1、17.7.11、21H461、OS UUID `04769D26-2CA0-4825-B443-E2E5F88300F2`，但硬件不同，不能照搬硬件值。

本节差异 N 项（A/C）：未定义；基线未最终确定。

## A. 启动参数

enuma r49 实际 FAT payload `EFI/UniXNU/unixnu.toml` 的 xnu entry，非当前 board 推断：

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1 enuma-fx-diag=1 enuma-bp=1
```

sheng 候选配置完整参数见固定 `board.toml` 的 `[payload].kernel_args`；其最终实际 payload 未取得。以下为已确认重点，不是集合全量差分。

| 参数 | sheng 配置 | enuma 实际包 | 作用 / 限制 |
|---|---|---|---|
| `sheng-fb-gpu` | `1` | 未列 | GPU presenter 选择；具体当次链接对象未确定。 |
| `sheng-gpu-metal` | `1` | 未列 | GPU/Metal 策略；当次运行时效果未查证。 |
| `sheng-vsync` | `144` | `60` | 显示同步频率配置；硬件不同。 |
| `offline-legacy-unit-scale` | `2` | 未列 | legacy 显示缩放策略；enuma 另有 ADT scale，不能视作等价。 |
| `offline-mobile-graphics-client` | `1` | 未列 | graphics client 策略；实际消费未查证。 |
| `text-fixup0` | 21H461 AW cache 配置 | 未列 | sheng 的 AW fixup；r49 的 ADT fixup 需另核，不能据命令行缺省断定缺失。 |
| `enuma-fx-diag`, `enuma-bp` | 未列 | 均 `1` | enuma 诊断；r49 host 记录描述周期报告。 |

本节差异 N 项（A/C）：未知；未完成完整逐条集合差分和全部参数作用核查。

## B. board / 组件及打包

| 项 | sheng `da9fab9` | enuma r49 | 等级 / 边界 |
|---|---|---|---|
| GPU | NativeAdreno / accelerator builders | 快照 board 不列同名 builder | C；实际 r49 链接清单仍需核实。 |
| legacy display | `build-native-legacy-display.py` | 快照 board 未列同名 builder | C；不代表实际隔离显示归档缺失。 |
| payload | 192 MiB、firmware loader | 160 MiB、firmware loader | C；r49 实际 payload 167,772,160 bytes。 |
| Data | `sheng-data-persist=2`，packed Data 配置 | scratch-data initrd，mode 0 | C；enuma 暂存 Data 不等于持久 Data，sheng mode 2 的 iPadOS 重启持久性未证。 |
| OS root | OS/SystemOS、UUID 04769D26… | 同 UUID，native UFS root | C；存储所有权与硬件独立。 |

本节差异 N 项（A/C）：未知；版本、完整组件闭包及全部开关未完成。

## C. ADT / 设备树

| 范围 | sheng | enuma r49 | 判断 |
|---|---|---|---|
| `/chosen` 逐键 | [U] 未取得实际 ADT | [A] 包内 `kernel.macho.adt`，host 记录 SHA-256 `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | 全量比较未完成。 |
| `arm-io`、display-subsystem、dart/iommu、aon、disp/dsi、gpio、i2c、spi、hid/digitizer、pmgr、clk、interrupt-controller、gpu/kgsl | [U] 未取得实际 ADT | [A] 包内 ADT 可供离线解析 | 未能逐节点对照，不将未知视作不存在。 |
| root UUID | [C] `04769D26-2CA0-4825-B443-E2E5F88300F2` | [C] 相同 | 配置一致；未核实际 sheng ADT。 |

本节差异 N 项（A/C）：未知；缺 sheng 实际 ADT，亦未完成 r49 节点清点。

## D. kext / closure

| 项 | sheng | enuma |
|---|---|---|
| 实际加载 kext | [U] 缺运行时清单 | [U] 缺运行时清单 |
| prelink closure | [C] board 给出 roots，非运行时加载表 | [U] 本轮未完成从 r49 prelink.json 核查 |

本节差异 N 项（A/C）：未知。roots 不能替代实际加载列表。

## 最小差异集（仅配置层，候选而非因果结论）

| 优先项 | 为什么可能关键 | 验证 | 代价 |
|---|---|---|---|
| 用户态进度 / AW text-fixup | sheng 提交说明报告 AW 死锁；enuma 已记录 cache fixup 未命中，可能影响 UI 之前进度，不能断定是同一死锁。 | 先对 r49 的 fixup 及应用计数做离线核对，结合既有观测；不要照搬机器码。 | 需要有效日志；新上机另行授权。 |
| GPU presenter / Metal | sheng 配 GPU 路径，enuma 不同；决定合成与送帧路径。 | 比较实际链接和 IOSurface swap/呈现证据；先查已有产物。 | 不同 SoC，A740 代码和硬件参数不可直接移植。 |
| graphics client / legacy display 接线 | sheng 启用 client，r49 命令行未列；可能影响显示服务发现。 | 核对 r49 实际调用点、消费者和已编译门控，再定实验。 | 代码及运行时验证成本；GOP 冻结决定仍适用。 |
| Data / 启动服务 | sheng mode 2，enuma scratch Data；服务状态不同可能影响 UI。 | 比较 Data 挂载、服务和 backboardd 正向证据。 | 临时 Data 不提供持久性；不得绕过 store 门禁。 |

## 范围外

macOS 线整体一类，不以其配置或桌面报告作为 iPadOS 17 证据；未枚举该线具体差异项，项数未知。
