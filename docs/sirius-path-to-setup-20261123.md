# sirius 到可触摸 Setup 的运行时路径（2026-11-23）

仅离线分析，未构建、未操作设备；来源固定 `HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503`，以下 sirius 路径均相对该仓。各轮是不同 kernel/payload，不把跨轮迹象拼成一次完整 trace。原始图像不在所查仓中，屏幕现象来自作者设备记录；结论 self-checked。

## 1. 到达阶段

`docs/evidence/sirius-touch-hid-20261029-combined.log:1-12` 原文：`SPAWN 141s exec 26 SpringBoard`、`SPAWN 146s exec 56 backboardd`、`SPAWN 216s exec 200 Setup`，又有 `SPAWN 345s exec 312 SpringBoard` 和 `SPAWN 376s exec 335 Setup`。同文件 `:73-75,92` 记录新 SpringBoard 启动及旧 Setup/SpringBoard 的 signal 9 退出。故进程确实 exec，而不仅是根据画面推测；不等于 SpringBoard 全部初始化完成。

`porting.toml:385-386` 原文 `Setup reacts to touch`；作者指出应用某选择可能是语言，**尚未从屏幕确认**。`:410` 的 `applies a choice` 比同文件详细说明更强，不能仅凭重启确定选择内容或因果。`porting.toml:646` 另一轮记录 `iOS reaches the Setup welcome screen ("hei", status bar, clock, battery icon) ... without a GPU driver`。这是可见 Setup 的作者报告，非本代理核读照片，也不是持久重启交互验收。

## 2. 显示 provider、来源与 GPU

`package/LegacyDisplayProbe.cpp:590-605` 加载 IOSurface、等待 `IOCoreSurfaceRoot`，经 `PE_current_console(&video)` 获取固件控制台，再 `new IOPlatformDevice`；`:610-628,647-659` 把 framebuffer memory 绑在该 nub，以资源服务为 IOKit parent，并在 DT plane 把 `display-subsystem` 接到 `/arm-io`，最后对该 nub `display->start(nub)`。不是 AppleARMIODevice；实测 `docs/evidence/sirius-usb-console-20261028-display.log:5-7`：`provider was not AppleARMIODevice.`，随后 `GOP display registered (1080x2240 at 0x9c000000, rowBytes 4320)`。`porting.toml:310-316,353-354` 指明 U-Boot GOP splash 缓冲、Legacy 子类，无内核 DSI/backlight/modeset 驱动。

`AGENTS.md:35-37` 称 CPU 拷贝、无 Metal，Adreno 616 仅 GMU phase 2、GPU core 未启动；`porting.toml:646` 的 Setup 轮甚至明确 `without a GPU driver`。不能把 GPU 可选代码或后续 GMU probe 当成 Setup 的渲染依赖。`:335-336` 记录 cached source + WC scanout 改善 CPU copy；这是呈现拷贝，不单独证明每个图层由哪个进程的软件栅格化。

`docs/evidence/sirius-usb-console-20261028-display.log:12` 在 189.2 秒记录 `IOMobileFramebufferUserClient::s_map_display_type ... UserClient display type is 0`，证明某 client 到达该方法；日志未标 PID，**不能证明打开者必为 backboardd**，也不是触摸成功那一轮。同文件 `:16` 的 `No Default FB Surface found` 不等于无法随后出图。

## 3. 输入实现

真实触摸硬件不是 ADT 软件占位或 SPI：`package/sirius_touch.c:3,113-116,134-144` 是 FTS521、QUP1 SE1 I2C 地址 `0x49`、读取事件 FIFO、`native_touch_set_sink`；`porting.toml:376,393,396` 记录 GPIO/供电、I2C 和实际读到坐标及 enter/motion/leave。`porting.toml:391` 明确 catalog 的 Novatek/SPI 依赖仅 source-only，未编译链接，不能将 sirius 误认作 SPI 路线。

`package/LegacyDisplayProbe.cpp:581-585` 的 late probe 调用硬件和 HID 启动；`package/SiriusHidProbe.cpp:7-12,69-88,91-122` 加载 IOHIDFamily/IOHIDEventDriver，等待 IOHIDResource，注册 combined keyboard+touch，并在 event driver/interface 发布 `Built-In`、`DisplayIntegrated`、`PrimaryUsagePage=0x0d`、`PrimaryUsage=4`。`:7-11` 说明键盘 personality 使内核 IOHIDEventDriver 匹配并分发 digitizer；`porting.toml:387-390` 记录 touch-only 在 `dk=0` 不匹配、DriverKit server 超时，combined + `dk=0` 绕过，代价是禁用所有 dext；硬件按钮 sink 仍为空。`docs/evidence/sirius-touch-hid-20261029-combined.log:2-4`：`31072` transitions、`keyboard+touch device started on IOHIDResource`、`IOHIDEventDriver published as the built-in touch screen`。这与用户观察 Setup 有反应相互支持，但不是逐次 input-to-UI 事件关联 trace。

## 4. 渲染与时间顺序

静态链是用户态 compositor 的 surface/swap → Legacy 验证 → CPU 拷贝固件 GOP → 既有固件 scanout。`package/LegacyDisplayProbe.cpp:590-592` 是内核加载/等待 IOSurface 服务，不是第一帧或进程归属证据。早期显示轮 `docs/evidence/sirius-usb-console-20261028-display.log:5-16` 顺序是 51.1 s display 注册、189.2 s 未署名 client 的 map-display-type、224.9 s default surface miss；未提供首个 swap 的时间或 PID。`docs/evidence/sirius-panel-20261028-display.log:13-22` 记录 `SWAP calls=8 accepted=8 ... gpu offers=0`、6 次 CPU 拷贝及 `p56 backboardd` 工作区间；两者并列而非每次 swap 的 PID 追踪。`:22` 作者解释 `8 swaps validated and accepted, 6 full frames ... CPU-copied to the GOP buffer`。因此仅可说作者将 backboardd 视为 compositor（`porting.toml:355`：`surfaces backboardd presents`），未见能独立证明首个 swap 由哪个 PID 发起的日志；更不能断言具体软件栅格化进程。

## 5. 既有卡点和绕行

* 有进程无画面：`porting.toml:365` 原文 `SWAP calls=8 accepted=8 ... FB total=6 copies ... the screen above the panel is black ... backboardd (pid 56) creates work intervals`；属于 **有 swap 但黑帧**，不能等同 enuma 的未观察到 swap。
* SpringBoard 曾反复崩溃：`porting.toml:348` 称 display-subsystem 发布后 `SpringBoard stops crash-looping`；`:362` 称前一轮 202.8 s 崩溃。`:546,560` 记录 keystore stand-in 后首次 OS Apple logo；它是跨轮关联，不证明唯一因果。
* 用户态另一卡点：`:331-333,646` 记录 iconservicesagent CoreUI/GL 路径 fixup，和 DataMigrator 长等后用 `ephemeral-storage=1` 绕过；`AGENTS.md:33-34` 明确代价是 staged system apps 不安装。
* 搜索所检出仓 tracked 文本：未见 `AXSpringBoardServer`；未见明确记录「backboardd 不打开 IOKit」。早期 client map 事件不标 PID，不能反推没有发生此症状。

## 6. 与 enuma 对比：代码级实现及缺口

以下是 sirius 的实现，**不是建议照搬跨板寄存器或断言 enuma 从未有类似组件**：

* `package/LegacyDisplayProbe.cpp:590-659`：合成 IOPlatformDevice、GOP memory 和 phase-4 display-subsystem；enuma 已有冻结的 GOP r5，`docs/enuma-gop-r5-device-observation.md` 仅 rootwait 轮无 render server/swap，运行像素未证。
* `drivers/GopFramebuffer/NativeLegacyDisplay.cpp` + `porting.toml:316,335-336`：Legacy 的 surface CPU copy、WC/cached 映射及 cache 维护；enuma GOP 候选非默认接入，未证明当前组合能呈现像素。
* `package/sirius_touch.c:3,134-144`：板级 FTS521 I2C 读和 `native_touch_*`；enuma 的 `docs/touch-evidence-inventory-20261122.md` §6 只确认 NVT-ts SPI 等只读事实，轴范围、触点及固件本体未确认，完整输入路径未证。
* `package/SiriusHidProbe.cpp:69-122` + `scripts/build-sheng-hid-input.py` + `scripts/data/hid-device-abi.json`：combined HID 匹配、event 属性、原始内核 ABI 绑定；enuma HID 运行时接通未证，不能复用板级实现而不核对 ABI/硬件。
* `package/LegacyDisplayProbe.cpp:581-585` + `porting.toml:339,344`：late 注册显示、触摸和 AppleKeyStore stand-in；enuma 有 stand-in 调查，`docs/aks-device-id-20261123.md:48` 称 identity 机制缺失，尚无运行时因果。
* `board.toml` 的 payload CoreUI fixup（`porting.toml:331-332`）避开无 GL 路径崩溃；enuma r44 的 fixup 未命中，见 `docs/enuma-r44-device-20261123.md`，不能推定该 fixup 是 enuma 当前卡点。

关键条件按路径顺序：① 足够完整的 OS/SystemOS、Data 和能推进至 SpringBoard/backboardd/Setup 的用户态（sirius 对迁移的绕过及 keystore/fixup 为其特定路径，不证明各项独立必要）；② firmware GOP + 可用 Legacy client/surface/swap/CPU-copy；③ 实际可工作的板级触摸链 + 匹配并发布给用户态的 HID。enuma 的 OS 根曾有条件成立、Data 仅强推断；`docs/backboardd-offline-20261123.md:121` 的 `entry_bb=0` 仅限定采样窗口，用户态阻塞原因未知。② GUI swap/像素未证，③ 板级触摸输入端到端未证；不把“未证”说成硬件必然缺失。以上不是持久根、重启后界面或正式阶段通过的证明。
