# enuma / nuwa HID stand-in 对比（2026-11-23）

**结论：nuwa 更弱，不等效；enuma r23 的完整实现足以让 IOHIDEventDriver 匹配，限该次已有记录的配置。** `EnumaHidStandin.cpp` 是 publisher，不是完整设备实现；它通过外部 `native_hid_input_allocate()` 使用上游 `NativeHidInput`。单看包装文件会误判 enuma 没有子类和描述符。两者均非可用真实触摸输入。状态：self-checked，离线源码及已有观察记录，无构建或设备操作。

## 来源与范围

* E = `UniXNU-enuma/package/EnumaHidStandin.cpp`，当前仓 HEAD `9217a0698a4d0d09b9142f0da7d8ae2fd9566d70`。
* H = r23 实际构建源 `UniXNU-enuma/out/ufs-sm8250-launchd-hid-20261122-r23/source/NativeHidInput.cpp`；`scripts/build-enuma-r23-hid-standin.py:25,251-253,280-281` 从 [UniXNU/ShengHidInput@71a40e76daeae1bb4127546f96ffa7339c7a06ff](https://github.com/UniXNU/ShengHidInput/blob/71a40e76daeae1bb4127546f96ffa7339c7a06ff/NativeHidInput.cpp) 提取，BSD-2-Clause-Patent。此 ignored 本地文件不是唯一来源，固定上游和构建脚本可定位原文。
* N = `D:/Code/PortingiOS/nuwa/worktree-display-dsp/package/NuwaHidStandin.cpp`，worktree HEAD `2169998a4fe2fae406d8cc4c4f6276adc708ff34`，该文件无工作树改动。两平台 OS 版本和 personality 不同，不能据此认定相同匹配结果。

## 逐项对比

| 项目 | enuma r23 完整路径 | nuwa |
|---|---|---|
| 子类 | E:15-16,87,93 `enuma_hid_static_init();` / `native_hid_input_allocate()`；H:242-243,442-443 `class NativeHidInput : public IOHIDDevice` / `OSDefineMetaClassAndStructors(NativeHidInput,IOHIDDevice)` / `return new NativeHidInput;`。子类不在 E 文件内。 | N:46-47,65 `class NuwaHidStandin : public IOHIDDevice` / `OSDefineMetaClassAndStructors(NuwaHidStandin, IOHIDDevice)`。 |
| 描述符 | H:32-60 `descriptor[]` 73 B：keyboard ID 1 + consumer ID 2；`touchDescriptor[]` 为 8 B 头 + 10 × 61 B finger + 14 B 尾 = 632 B，touch ID 3、10 个逻辑 finger。H:395-407 `if(touchEnabled){memcpy(...touchDescriptor...)}`，`sheng-touch-hid=1` 时合计 705 B；成功返回 `kIOReturnSuccess`，分配失败 `kIOReturnNoMemory`，`out` 为空返回 `kIOReturnBadArgument`。 | N:27-44 `static const uint8_t descriptor[]` 为 127 B；keyboard ID 1 + touch ID 3、单逻辑 finger、contact count，无 consumer。N:60-63 `withBytes(descriptor, sizeof(descriptor), ...)`；成功 `kIOReturnSuccess`，失败 `kIOReturnNoMemory`。 |
| 方法 | H:409-432 覆写 `start`：workloop、`HIDDefaultBehavior`、可选 digitizer 属性、`IOHIDDevice::start(provider)`、timer，成功 true，相关失败 false。H:253-258 `submitReport` 调用继承的 `handleReport(...)` 并返回其结果；H:393-394 返回 transport/product 字符串。H 全文件无 `newDeviceDescription`、`getReport`、`setReport` 覆写；基类返回值未核，不推断。 | N:50-63 覆写 `init`、`free`、`getWorkLoop`、`newReportDescriptor`；`init` 为基类成功且 workloop 与 `setProperty` 成功时 true。N:153-155 `device->start(resource)` 调用继承实现；该文件无 `start`、`newDeviceDescription`、`getReport`、`setReport`、`handleReport` 覆写或报告调用，基类返回值未核。 |
| 发布与匹配 | E:105-120 `sheng-touch-hid=1`，加载 `IOHIDFamily` / `IOHIDEventDriver`，`serviceMatching("IOHIDResource")` 后等待；E:93-96 `device->init()` / `attach(resource)` / `start(resource)`。H:411-413 设置 `HIDDefaultBehavior=true` 请求普通 HID event personality，H:32-35 keyboard-first；本方源码无显式 `registerService()`，基类实现未核。 | N:122-136 `nuwa-hid-standin=1`，加载相同 bundle、检查类，`serviceMatching("IOHIDResource")` 等待；N:153-155 `new NuwaHidStandin` / `init()` / `attach(resource)` / `start(resource)`。N:50-53 `setProperty("HIDDefaultBehavior", true)`；N:27-30 keyboard-first。本文件无显式 `registerService()`，基类实现未核。 |
| 匹配前 device 属性 | H:413 `HIDDefaultBehavior=true`；H:420 对启用触摸设置 `Built-In=true`、`DisplayIntegrated=true`、`DigitizerCollectionDispatch=true`；H:430 `OfflineInputProbe=true`；H:393-394 transport `Virtual`、product `Offline HID input probe`（本次 combined，而非 touch-only）。 | N:53 只显式 `HIDDefaultBehavior=true`；N:46-65 未覆写 transport/product，未在 device 显式设置上述四项。继承默认值未核，不把未设置写成 false。 |
| 匹配后属性 | E:48-53,62-67 对找到的 driver 的父节点和 driver 均写 `Built-In=true`、`DisplayIntegrated=true`、`PrimaryUsagePage=0x0d`、`PrimaryUsage=4`；父节点先写，失败短路。E:58-59 明说键盘优先描述符匹配后分类原为 `(1,6)`。 | N:93-109 对已注册的 `IOHIDInterface` 和 `IOHIDEventDriver` 写同四键同值；driver 先写，失败短路。N:102-107 注明不改变匹配前 usage，最多 500 次、每次 sleep 10 ms 等待子链。 |
| sink、定时与事件 | E:19-24 `native_touch_set_sink(...) {}`、`native_buttons_set_sink(...) {}`，`native_hid_input_requested() { return false; }`，globals 零初始化；H:422-432 启动 timer 并尝试登记 sink，H:369-380 每秒 checkpoint，未请求时不自动发按键；H:253-258,270-280,325-328,331-344 有潜在 `handleReport` 触摸/按钮路径，但空 sink 不保留回调。不是「无 timer」；本配置无真实数据源，也不证明报告实际提交。 | N:2 `no reports, timers, hardware or event hooks`；N:19-21 sink 空、requested false。N:101-119 是启动线程有限轮询与 `IOSleep(10)`，不是 timer 或事件源；无 `handleReport` 调用、无真实数据源。 |
| ADT | E:117-120 匹配已有软件 `IOHIDResource`，E:93-96 直接 attach/start，不查 HID ADT 节点；r23 host 记录 `docs/enuma-r23-hid-standin-host-20261122.md:23-30,63-71` 复用 r22 ADT。此软件路径不要求专用 HID ADT 节点，不等于整个系统无需 ADT。 | N:135-136,153-155 同样匹配软件 `IOHIDResource` 并直接 attach/start，不查 HID ADT 节点；同样只对本软件路径成立。 |

## 匹配证据与边界

匹配之前关键步骤是加载对应 family/personality、获取软件 provider、注册设备类、提供 keyboard-first report descriptor 和 `HIDDefaultBehavior`，然后成功 init/attach/start；具体系统 personality 的全部谓词未从源码证实，不能把键盘描述符单独视为充分条件。双方都有该链的实现，但 descriptor、属性时机、timer 与等待策略不同；本对比不证明差异必然导致某平台匹配失败。后写的 `PrimaryUsage*` 是匹配完成后的分类，不是使初始 driver 匹配的前置。

`docs/enuma-r23-hid-device-20261122.md:13-15` 记录主控转述 vision 核读 `enuma HID stand-in: digitizer properties=1`；E:27-45,56-68 只有找到设备子树中 `IOHIDEventDriver`、取到其父节点并成功设置两节点属性才打印该值。因此 **r23 配置有一次实际匹配的间接日志证据**，不是独立重读，也不证明其他候选自动接线、用户态消费或触摸。不能把 E 文件孤立执行视为足够。

nuwa 的 `docs/nuwa-session-20261122-findings.md:48-50` 只称主控报告 stand-in 已试而 SpringBoard 仍 assert；不证明本次具体匹配链是否成功，亦不证明所有 HID 原因被排除。其仅枚举、没有报告源的实现比 enuma 的完整复用设备更弱；对 SpringBoard 的影响不可跨设备推论。
