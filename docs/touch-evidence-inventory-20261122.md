# enuma 触摸证据清单（2026-11-22）

状态：`self-checked`，离线证据调查；本轮未访问设备。路径相对于设备仓；`.cache` 是本地证据，不作为入库资产。

## 1. 已有证据

- `.cache/live-capture/20261107T141941555586Z/input_device_names.txt:1-9` 记录 `xiaomi-touch`、`NVTCapacitiveTouchScreen` 和 `NVTCapacitivePen`；也有 `uinput-goodix`，不能据此认定触摸 IC 是 Goodix。`input_names.txt:1-26` 只有 event/input 名单，没有映射。未找到 `/proc/bus/input/devices` 或 `getevent -pl` 转储，VID/PID、轴范围和触点数未取得。
- `.cache/device-evidence/20261109-live-dt/live.dts:9559-9583` 的 `novatek@0` compatible 是 `novatek,NVT-ts-spi`；`porting.toml` 的 input findings 记载厂商 `elish-r-oss@52a2f180865f8368828985d6384130acd093fa93` 启用 NT36523 SPI 驱动。`docs/nt36523-touch-survey.md:30-58` 将本板 DT 解析为 QUPv3 wrapper 0、SE4、片选 0、从设备上限 19.2 MHz；不是 I²C 地址。`.cache/live-capture/20261107T141941555586Z/spi_device_names.txt:1` 有 `spi0.0`，单独不能证明绑定关系。
- `docs/nt36523-touch-survey.md:76-101` 解析 DT 中断 GPIO 为 TLMM 39，flags 原值 `0x2001`，触发语义未定。GPIO33 仅出现在未引用的触摸复位相关 pinctrl 组，不等于已确认复位线；触摸节点无 reset 或 supply 属性。GPIO69 的 `touch_vddio_vreg` 被禁用且无引用，不能认定为实际供电。
- `live.dts:16` 的启动参数指定 `k81_42_02_0a` 面板；`:23204-23239` 的对应面板节点包含 `mi,is-tddi-flag`，`:23276-23278` 有笔模式命令状态及面板高度。触摸配置 `:9578-9583` 的 `display-maker = 0x42` 与面板标识相符，但匹配机制未证实，面板尺寸不是输入轴范围。
- `live.dts:9579-9583` 记录 `novatek_nt36523_k81_fw01.bin`、`novatek_nt36523_k81_fw01_pen.bin`、`novatek_nt36523_k81_mp01.bin`、`novatek_nt36523_k81_mp01_pen.bin` 文件名；厂商源码记录有 fw01–03 变体。`docs/nt36523-touch-survey.md:213` 将固件本体、来源和版本选择列为缺口。本次检索未发现已采集的触摸固件或校准数据。

## 2. 不同目标的缺项

- **软件占位 digitizer**：不需要真实 IC、总线、坐标或校准数据；仍需软件 HID 描述符、publisher、链接和目标 IOHID ABI 接线。占位使 SpringBoard 启动的因果关系未证实，见 `docs/hid-digitizer-standin-20261122.md:7-15`。
- **真实触摸**：缺 Android 设备绑定、轴范围、最大触点、多点事件和坐标方向；缺 NT36523 识别、SPI 模式、初始化与原始帧协议，以及匹配固件和加载方式；缺 GPIO39 中断触发/应答、真实复位与供电时序，以及 XNU 侧 SPI、时钟和资源接管实现。GPIO33 和 GPIO69 均不能直接当成已确认答案。

`getevent` 输出 Linux input 能力及事件，不是控制器原始 SPI 帧，也不是 HID report descriptor；不能假定该控制器提供硬件 HID 描述符。

## 3. 离线可得与需补采

- 已有 `live.dts`、原始 DT、固件 DTB 和 `docs/nt36523-touch-survey.md` 可离线解析 SPI、GPIO、面板与固件文件名；可继续对照上述厂商源码核对协议、flags 和固件选择。DT 本身不能证明实际供电和复位行为。
- 当前未找到输入 VID/PID、轴声明和多点事件转储；需要 Android 运行时只读采集。触摸事件可验证动作和方向，但一次操作不保证覆盖声明范围两端。
- 原始 SPI 帧、实际电源轨/复位时序和固件或校准本体不保证由普通 adb/sysfs 暴露，可能还需厂商源码、可读文件或硬件证据。

## 4. 将来采集命令（未执行）

先按项目设备识别规则确认唯一目标型号 `enuma`，再替换 `<serial>`；均为只读命令，权限不足时记录失败，不修改设备配置。

```sh
# 输入名称、bus/VID/PID、event 映射
adb -s <serial> shell cat /proc/bus/input/devices

# input 能力、ABS 轴声明范围和多点槽位
adb -s <serial> shell getevent -pl

# event 对应名称、sysfs 路径和父总线
adb -s <serial> shell 'for d in /sys/class/input/event*; do echo "=== $d ==="; cat "$d/device/name"; readlink -f "$d/device"; done'

# SPI 设备及运行时驱动绑定
adb -s <serial> shell 'for d in /sys/bus/spi/devices/*; do echo "=== $d ==="; readlink -f "$d/driver"; cat "$d/modalias" 2>/dev/null; done'

# 将 <eventN> 换为已确认的触摸 event；单指、多指、四角滑动后手动结束
adb -s <serial> shell getevent -lt /dev/input/<eventN>

# 只列候选固件文件，不读取或修改内容
adb -s <serial> shell 'ls -l /vendor/firmware/novatek* /vendor/firmware/*nt36523* /odm/firmware/*nt36523* 2>/dev/null'
```
