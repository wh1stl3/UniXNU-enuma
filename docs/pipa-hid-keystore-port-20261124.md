# pipa HID / AppleKeyStore 与 enuma 对照

状态：self-checked，仅静态源码和既有构建记录；未构建、未访问设备，未验证当前运行时。
基准：pipa `xVanTuring/UniXNU-pipa@cdb3d62771e31d48d832853ee0c90964346d78da`
（`.cache/ref-pipa`）；enuma `ec4a45ed4802298dfebb476250c61e368507c8b6` 的板级源码、
UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241` 的
`AppleKeyStoreState@8c70daf814aafdf4a3d35e40dde0322655fd0a83`，以及 r23
`ShengHidInput@71a40e76daeae1bb4127546f96ffa7339c7a06ff`。
组件许可 BSD-2-Clause-Patent。pipa 的 HID gitlink 为 `5f3a37ce...`，
子模块未检出，因此其具体描述符不能与 r23 源码逐字节比对；
pipa 实际 keystore 组件版本也须结合其构建基座确定。

## 三个参数

* pipa `package/HidInputProbe.cpp:145-153`：
  `if(!PE_parse_boot_argn("offline-hid-input",&enabled,sizeof(enabled)) || enabled!=1)return;`
  使能一次性 HID probe，加载 `com.apple.iokit.IOHIDFamily`，成功后加载
  `com.apple.iokit.IOHIDEventDriver`；`:155-165` 记录类大小并等待 IOHIDResource。
* `HidInputProbe.cpp:166-178`：
  `if(resource && sendHome==1 && native_hid_class_sizes[4]==208)` 才注册类并
  `native_hid_input_allocate()`，init/attach/start 一个组合 `IOHIDDevice`，
  不是直接生成 Home 按下；`:184-191` 的独立 digitizer 还需 split 和 touch 开关。
* `package/KeyStoreProbe.cpp:76-107,125-126`：
  `offline-key-events=1` 才尝试启动 AppleKeyStore 软件服务；还须
  `/chosen/ephemeral-storage=1`、`offline-keystore` 为零、类未存在、provider 可用。
  不是物理按键。该 probe 调用外部 `native_keyevents_allocate()`，并不自身实现方法；
  另需 `sheng-aks=1` 才允许 user client（同文件 `:27-33`，官方组件
  `NativeKeyStoreEvents.cpp:280-311`）。pipa 构建脚本
  `scripts/build-gop-legacy-display.py:385-396` 从构建基座引入该官方组件，
  但没有固定此处所查基座为 pipa 实际构建的证明。

## HID 比较

| 维度 | pipa | enuma | 判断 |
|---|---|---|---|
| 发布 | `HidInputProbe.cpp:145-178` 两级 input/home 门控和 IOHIDDevice ABI 大小检查；`:184-191` 可选 split digitizer | `package/EnumaHidStandin.cpp:72-103,105-120` 一个 `sheng-touch-hid=1` 门控、相同大小检查、发布组合对象；无 split 发布 | 组合对象近似；门控不同，split enuma 更弱 |
| 描述符 | 此 checkout 子模块 `5f3a37ce...` 未检出，不能断言字节一致 | r23 上游 `NativeHidInput.cpp:32-60,395-415` 键盘 report 1、consumer report 2（Home/电源/音量）、开关开启加十指 digitizer report 3 | 不可比：pipa 精确版本未核 |
| 属性 | `HidInputProbe.cpp:109-133` 对已带 Built-In 的设备在 event driver 与 interface 设置 Built-In、DisplayIntegrated、usage `(0x0d,4)` | `EnumaHidStandin.cpp:48-68` 为两者设置相同四项；r23 组件 `:409-430` 在触摸启用时设置设备属性 | 大体相近；触发条件不完全相同 |
| 事件 | pipa `HidInputProbe.cpp:30-51` 支持第二帧后定时 Home 或 mailbox 命令；`package/Buttons.c:1-2` 有独立实体按键 producer | `EnumaHidStandin.cpp:18-24` 两个 sink 是空函数，`native_hid_input_requested()` 永远 false；r23 组件 `:270-345,369-388` 虽有报告路径却收不到上述源 | enuma 更弱：既无注入 Home，也无该 stand-in 的真实触摸/实体按键源 |

这些维度不能笼统称 HID 等效或 enuma 更强。组合设备发布与 digitizer 属性
不需要再移植 pipa probe；若目标是真实交互，缺的是经本板证据支持的输入源，
不是照搬 pipa 板级驱动或增加无消费者参数。r23 的属性成功观察见
`docs/enuma-r23-hid-device-20261122.md`，不证明后续版本实际产生输入。

## AppleKeyStore：空回调不等于空服务

enuma `package/EnumaKeyStoreProbe.cpp:18-29` 的 `native_aks_opened()` 和
`native_aks_call()` 确实为空，但官方组件 `NativeKeyStoreEvents.cpp:274,291`
只把它们作为调用计数/观测回调；真正的 `AppleKeyStoreUserClient::externalMethod`
在 `:229-276`，`AppleKeyStore::newUserClient` 在 `:280-311`。
`scripts/build-enuma-r11-keystore.py:117-151,173-176` 编译并打包该组件；
`docs/enuma-r11-keystore-host-20261121.md:17,54-55` 记录构建对象和 vtable。
`scripts/build-enuma-r39-aksid.py:66-68` 重用 r11 组件对象，换板级回调。
这些是特定构建链的证据，不等于所有内核均含该对象。

组件 `:151-175,229-275` 提供 selector 10 wrap、11 unwrap，14 system handle，
7 lock state，17/35 device state，23 bag UUID，40 generation；握手/部分通知和
bookkeeping selector 返回成功，无通用 keybag 或 reference-key 实现，未知 selector
返回 unsupported。不存在可据此声称的任意 key/value get/set 方法。
wrap/unwrap 使用 `:103-119` 的板级 ID 派生软件密钥；ID 缺失则返回错误。
enuma 当前 `EnumaKeyStoreProbe.cpp:31-51` 取 chosen 的非零 unique-chip-id，
退回 chip-id；历史 r11 ID 为零，wrap/unwrap 失败关闭，见
`docs/enuma-r11-keystore-host-20261121.md:26`；不能把历史 r11 推为当前源码。
该软件机制没有硬件密钥保护，也不证明密钥持久性或用户态调用成功。

若目标构建未链接服务、无有效 ID 或 user client 不可用，则对应调用可失败，
上层如何等待或重试须看实际调用栈和日志；不能据此断定 akd/securityd 或
backboardd/SpringBoard 已被卡住。对当前 bb/SB 卡住的相关性为低强度假设：
缺同轮 selector 返回值、有效 ID、调用栈和单变量对照。

## 移植决定与判据

不需要移植 pipa 的 keystore 方法：已存在官方组件的相应方法；先确认目标
最终镜像链接的是该组件、`sheng-aks=1`、服务发布成功、ID 非零，再观察
selector 10/11 的返回与调用方。若不满足，优先修目标构建接线或输入，
而不是因空的计数回调重写服务。若上述均成立但调用仍失败，按实际 selector、
参数及返回码定位；软件密钥无硬件保护、以及兼容性/重启持续性验证是代价。
HID 仅组合发布不需移植；真实输入仍缺 enuma 证据和 producer，判据是该板
输入来源产生对应 report、用户态收到事件并完成交互，不能以服务匹配代替。
