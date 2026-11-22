# HID digitizer 软件占位调查（2026-11-22）

状态：仅静态审查；未构建、未上机。r22 中未观察到 SpringBoard/backboardd，不证明缺 digitizer 是原因。

## 实现和证据

- 基座 UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241` 的 `components.toml:145-162` 登记 `ShengHidInput`，来源 [UniXNU/ShengHidInput@71a40e76daeae1bb4127546f96ffa7339c7a06ff](https://github.com/UniXNU/ShengHidInput/tree/71a40e76daeae1bb4127546f96ffa7339c7a06ff)，源码 SPDX BSD-2-Clause-Patent；当前基座未检出 `drivers/ShengHidInput`。该目录的上游 `NativeHidInput.cpp:24-30,56,242,395-421,443` 定义 `IOHIDDevice` 子类 `NativeHidInput`、键盘加 Touch Screen digitizer 报告描述符和分配函数；`sheng-touch-hid=1` 给默认组合设备加入 digitizer collection。其全局触点数据并非弱符号，需由板级提供。
- Orange Pi 实际不是直接引用该 catalog 组件：它有自带的 [Ken-u/UniXNU-orangepi5@f96d273b526254d700bd42bfeadef0359a1d3c46](https://github.com/Ken-u/UniXNU-orangepi5/tree/f96d273b526254d700bd42bfeadef0359a1d3c46) `package/Evb10Hid/NativeHidInput.cpp:50,130,283-315,329` 与 `package/Evb10HidProbe.cpp:3-9,38-40,101-127`。后者为触点 globals 提供零值、sink 空实现，分配并在 `IOHIDResource` 上 attach/start，故可不接触摸芯片发布软件 HID。该文件 `:136-138` 另有可选 split 设备路径。其仓库许可证为 BSD-2-Clause-Patent，源码复用前仍须核对文件自身许可和来源。
- `UniXNU/docs/zh/devices/orangepi5.md:340-356` 记录没有板载 digitizer，同次软件占位、SpringBoard 运行；`:344` 给出 `opi5-hid=1 opi5-hid-input=1 sheng-touch-hid=1`，以及 `libOpi5Hid.a` force-load。`:360` 明确无真实指针/键盘。没有找到另一设备明确记录「加入同一软件占位后 SpringBoard 从不运行变成运行」；同次共现和文档“enough”不是隔离因果试验。`docs/zh/devices/asteroids.md:695,715` 的前后对照是 **AppleKeyStore** stand-in，不是 HID。
- `components.toml:153-157` 的 catalog 依赖为 `ShengNovatekTouch` 和板级触点 globals；这是组件解析依赖，不等同发布节点必须有实物芯片。`docs/devices/alioth.md:361,367` 记录仅选择组件不保证进入内核，须归档/force-load；`docs/devices/fuxi-oddlylabs.md:379-382` 记录 IOHID ABI、初始化和匹配要求。`offline-hid-input=1` 见 `docs/zh/devices/uke.md:496`，不是本源码或 Orange Pi 路径已证明的通用开关；不能仅加参数期待自动发布。

## enuma 对照与最小必要改动

- `board.toml:14-16,28-45,75` 无 HID 组件、archive 或 HID boot-arg；`configs/enuma_defconfig:1-22` 无 HID 设置；当前 `package/` 无 HID/touch publisher。`porting.toml:169-181` input 仍为 planned；`:177` 的本板 Novatek NT36523 线索不意味着软件占位需要驱动它。
- 最小功能单元不是「组件 + 参数」：复用 `ShengHidInput` 或 Orange Pi 的 EVB10 变体，提供零触点 globals/空 sink、所需回调和目标内核 IOHID ABI 绑定；显式链接并接入板级 publisher，加载 IOHIDFamily/IOHIDEventDriver、等待 IOHIDResource、注册类并 attach/start，按目标匹配需要发布 digitizer 属性；默认组合设备设置 `sheng-touch-hid=1`，再按选定 publisher 实际实现设置其启用参数。Orange Pi 的 `opi5-hid*` 是该板级实现的参数，不是 enuma 已有接口。应审查其启动链接线和 ABI，不能声称现有参数足以使用。
- 可纯软件发布占位节点，不需要触摸 IC；无真实触点事件，不提供可操作触屏。enuma 上能否注册成功、backboardd 是否识别以及 SpringBoard 是否因此启动均尚未验证。
