# nuwa / enuma / sirius HID 对照（2026-11-23）

纯离线调查，self-checked；无构建或设备操作。nuwa 下文 `W` 指
`D:/Code/PortingiOS/nuwa/worktree-display-dsp`，HEAD
`2169998a4fe2fae406d8cc4c4f6276adc708ff34`；与 nuwa 主检出区分。

## 实现与类型

nuwa **是软件占位**，不是硬件触摸驱动。`W/package/NuwaHidStandin.cpp:2`
原文 `Software enumeration only; no reports, timers, hardware or event hooks.`；
`:17-21` 的接触点数组为零初始化，`native_touch_set_sink(...) {}`、
`native_buttons_set_sink(...) {}`，`native_hid_input_requested() { return false; }`。
`:60-63` 返回静态报告描述符，不读取 I2C/SPI 或发送事件。
`W/porting.toml:246` 同样明确 `No input reports, no hardware support, and no evidence of runtime matching.`。

文件清单（行号为物理行；按功能而非逐一罗列通用构建工具）：
* `W/package/NuwaHidStandin.cpp`：165 行，全部占位实现。
* `W/patches/xnu/8796-offline-legacy-display-late.patch`：27 行，`:10-16` 在 `IOKitBSDInit()` 成功后、开发宏开启时调用占位 probe。
* `W/board.toml`：`:76-77` 预链接 `IOHIDFamily` / `IOHIDEventDriver`；并非启用真实触摸驱动或默认启用 stand-in。
* `W/scripts/derive-nuwa-hid-abi.py`：ABI 派生及审计；`W/scripts/build-nuwa-display-native.py:546,571-578` 为构建选项；`W/scripts/build-ufs-apfs-root-chmh-r35-display.py:51-52,105-107` 控制启动参数。
* `W/package/boot-progress/BootProgress.c:150-156` 仅引用可选触摸观测符号；`W/package/boot-progress-r12/nuwa_boot_progress_stubs.c:115-118,221-232` 为零地址占位，不能当作事件源。

## 发布与属性

`NuwaHidStandin.cpp:27-43` 是 keyboard-first + 单个逻辑 finger 的 combined 描述符；
`:46-63` 是 `IOHIDDevice` 子类，设置 `HIDDefaultBehavior=true`。
`:122-161` 在 `nuwa-hid-standin=1` 时加载 family 和 codeless event-driver personality，
等待 `IOHIDResource`，init/attach/start 软件设备。`:101-119` 等待该设备自己的
`IOHIDInterface` → `IOHIDEventDriver` 已注册子链；匹配后在两者设置
`:93-97` 的 `Built-In=true`、`DisplayIntegrated=true`、
`PrimaryUsagePage=0x0d`、`PrimaryUsage=4`。这是设计路径，不是本轮观察到的匹配。
`W/docs/nuwa-hid-standin-20261122.md:3-16,40-43` 记录默认关闭、无事件、
运行时匹配未证明及需审查；后续上机记录见下。

## ADT

只读使用 `W/scripts/check-nuwa-adt.py:31-97` 解码
`nuwa/out/nuwa-systemgroup-flash-20261122/derived.adt`，SHA-256
`ac47d3931349fed38579851ed8a414f47bd7c88dbfb8c0b80a13e85924017f01`：
按节点路径和属性名搜索 `hid`、`touch`、`digitizer` 均无命中；`/device-tree/arm-io`
只有 `intc` 子节点。结论限于该一个实际产物及该键名搜索，不代表所有 nuwa ADT。
`W/dts/nuwa.dts:8-32` 为 FDT 源而非 ADT，亦无板级触摸节点。
enuma 的已解析键清单 `docs/enuma-adt-properties-20261123.txt` 同样无这些键名；
不以此否认设备物理触摸硬件。

## 实测和对照

`W/docs/nuwa-session-20261122-findings.md:48-50` 原文：
“parent reports the HID stand-in was tried and SpringBoard still asserted.
This excludes that experiment as a sufficient fix, not all HID causes.”
这是主控转述的实机尝试，不证明该链成功匹配、更不证明有触摸事件。
同目录 `docs/nuwa-hid-standin-20261122.md:40-43` 的 host 候选记录写
`device execution remain pending`，时间范围早于/不同于上述后续会话汇总，
不能据此抹去后者的尝试。所查记录无 nuwa 触摸可用、HID 事件产生或
Setup 可交互的正向证据；`nuwa/AGENTS.md:13-14` 仍称交互目标未达成。

enuma `package/EnumaHidStandin.cpp:19-24,48-68,106-115` 同为无硬件事件的软件占位；
`docs/enuma-r23-hid-device-20261122.md` 的 `digitizer properties=1` 是属性发布观察，
不是输入或 GUI 证明。sirius 则在固定来源
`HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503`
有 FTS521 的 QUP1 SE1 I2C FIFO 读取和真实事件 sink，另加 combined HID
发布；触摸响应 Setup 是作者报告，详见本仓
`docs/sirius-path-to-setup-20261123.md:7-9,19-23`。

结论：两台占位都不能证明 HID 用户态链完整成立，更不产生物理输入。
enuma 面向真实交互缺板级 SPI 触控读出、协议和事件到 HID 的端到端接线及验证；
不能仅说缺接线，也不能凭 nuwa 占位推出足以解锁 SpringBoard。
enuma 的已采集 NVT-ts SPI 事实及轴范围、触点数、固件等缺口见
`docs/touch-evidence-inventory-20261122.md` §6；板值不可跨机照抄。
