# enuma 软件 HID 设备候选设计（2026-11-23）

> 状态：部分调查，未完成；运行时状态及候选方案尚未验证。

状态：self-checked，离线设计，无构建、设备操作或新运行时结论。**不建议优先新造 HID nub**：任务的「enuma 没有任何内核 HID 设备」前提与 r23 记录冲突。r23 屏幕出现 `enuma HID stand-in: digitizer properties=1`，该行只能在 `findEventDriver` 找到设备子树中的 `IOHIDEventDriver` 且其父接口和 driver 四项属性都设置成功时打印（`package/EnumaHidStandin.cpp:27-68`；设备记录 `docs/enuma-r23-hid-device-20261122.md:13-16`，主控转述 vision）。这是 r23 的实际软件设备及匹配证据，不是 r40/r43 等其他构建必然仍成功的证据。目标轮应先核对包内调用点、实机同轮日志及采样时间；若已有匹配设备，新发一个同类设备不能检验「从无到有」。

## sirius 实际做法

源码基准 [HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503](https://github.com/HuajiFruit/UniXNU-sirius/tree/ac0c900485f3c0cd18de9707579a1cdcd3365503)，`package/SiriusHidProbe.cpp:1-12,55-122`，BSD-2-Clause-Patent；通用实现 [UniXNU/ShengHidInput@71a40e76daeae1bb4127546f96ffa7339c7a06ff](https://github.com/UniXNU/ShengHidInput/tree/71a40e76daeae1bb4127546f96ffa7339c7a06ff)，BSD-2-Clause-Patent。sirius 引用的自身构建版本须实施前单独核对，不能将不同 revision 视为同一二进制。

* `sirius-touch-hid=1` 在 late display probe 启动线程，加载 `com.apple.iokit.IOHIDFamily` 和 `com.apple.iokit.IOHIDEventDriver`，等待现成 `IOHIDResource`；检查原版 `IOHIDDevice` 类大小 208，延迟注册 metaclass，分配 `NativeHidInput : IOHIDDevice`，对 resource 执行 init/attach/start。资源是软件 provider，**该方案需要真实 IOKit IOHIDDevice 软件对象，不需要 ADT HID 节点**；不是说整个 IOKit 运行无需 ADT。
* 描述符以 Generic Desktop Keyboard `(1,6)` 开头，后有 consumer 和由 `sheng-touch-hid=1` 加入的 Digitizer Touch Screen `(0x0d,4)`。设备 start 设 `HIDDefaultBehavior=true`；组合匹配 donor 的 `HID Keyboard Driver` personality，再分发同一设备的 digitizer collection。sirius 源码列出的 donor personality 无通用 digitizer 项，touch-only 在其路径未匹配内核 driver；具体当前目标 donor 的 personality 仍应查包，不能只凭同 donor 推断运行成功。
* 设备自身设置 `Built-In=true`、`DisplayIntegrated=true`、`DigitizerCollectionDispatch=true`；tick 找到 driver 后，给 driver 和其 parent interface 各设 `Built-In=true`、`DisplayIntegrated=true`、32 位 `PrimaryUsagePage=0x0d`、`PrimaryUsage=4`。这四项发生在匹配之后，用于上层分类，不是让键盘 personality 初次匹配的前提。`OfflineInputProbe=true` 为软件探针标记；transport `Virtual`、product `Offline HID input probe` 为字符串。具体属性依所用 pinned 源码核对。
* sirius 真正坐标来自 `package/sirius_touch.c` 的 FTS521 I2C 和 sink；**创建和匹配 nub 不依赖真实读事件**。无事件时不能声称触摸可用。组合设备有工作循环和定时器；无 sink、`native_hid_input_requested=false` 时不主动提交按键/触点，但仍有定时回调和匹配后属性通知，不能称为零活动。

## 最小方案与落点

优先**复用既有 enuma 实现**：`package/EnumaHidStandin.cpp:18-25` 已提供零触点、空 sink 和 false；`:72-103` 已实际分配、init、attach、start `IOHIDDevice`，`:105-123` 在 `sheng-touch-hid=1` 下加载并启动。`:48-68` 只是整个实现中的属性部分。r23 使用同一上游组件和独立 host recipe，见 `docs/enuma-r23-hid-standin-host-20261122.md:6-30,51-60`；原版 ABI 校验包含 207 vtable 槽与 52 bindings，**208 字节检查本身不足以保证 ABI 正确**。不照搬 sirius 板级资源、I2C、GPIO、按钮或其 ABI 表。

若目标包未接入该既有路径，才做隔离候选：

1. `package/EnumaHidStandin.cpp` 约 10–25 行：复用 publisher，新增默认关闭 `enuma-hid-dev=1` 门控并明确互斥：新旧门控均启用时**只调用一次**同一个 publisher；无两个对象、无重复 metaclass 注册。`sheng-touch-hid=1` 仍为上游 combined 描述符开关；新开关本身不自动使上游加 digitizer。为保持单变量，候选相对同基线仅增新 publisher 门控，描述符参数固定相同；不能把旧 publisher 已开启的基线称为关闭组。若目标已开启旧门控，新参数是 no-op，须先比较已有记录或设计有明确关闭控制的对照，不得制造重复设备。
2. 约 1 个隔离 recipe/脚本 20–60 行（具体依目标最终基线）：复用 r23 的 archive、目标 kernel ABI 绑定、prelink roots、受控调用点和采样探针；核对 final binary 真正链接和调用，ADT 不变。不得默认改 `board.toml` 或官方 series。若已有调用点与 archive，改动规模更小。
3. 保留组合描述符及启动所需工作循环、metaclass 生命周期和报告接口；仅用空 sink / 零触点 / 禁止自动 Home，省去真实硬件读取与合成事件。是否移除 timer/edge 代码须以目标 revision 控制流与 ABI 验证；当前复用不主张它们不存在。四个属性对「仅 driver 匹配」非必需，但保留既有路径以复现 r23 分类，并以成功日志辨别；`DigitizerCollectionDispatch` 对真实多触点分发有意义，不能证明对本试验必需。

预计未来实现 **1–2 文件、30–85 行增改**，不含已有复用代码；不是已实现。启动链 hook 或驱动初始化变更需明确 brief、deep_reviewer 审查后再实施；最终 ABI、计时器和生命周期需复审。

## 风险与控制

* 假设备可能使上层误判为可交互触摸屏，或等待输入/初始化，实际是否卡住未知；不发假触点、不声称触摸能力，比较同基线无设备与有设备的同轮存活、采样和时间。无事件并不必然令系统阻塞。
* `sheng-touch-hid=1` 在 enuma 现有文件同时控制 publisher、在组件内控制描述符；盲加新开关会重复发布或产生键盘-only。保持参数矩阵、单一启动路径和 exactly-once；核查实际目标包而非仅看 board 参数。r40 包带旧参数及字符串不证明调用成功（`docs/hid-stack-backboardd-20261123.md:18`）。
* 加载、延迟 metaclass、ABI 错配、attach 及 timer 可能 panic 或卡启动；现有 publisher 在 `load_init_program` 上同步最多等待资源，限制窗口并记录失败、保留原检查，失败不宣称实验已执行。不要未经审查改锁、并发、启动顺序；设备操作须另获授权。

## 上机判读表（设计，尚未上机）

比较必须固定镜像其余内容、参数、探针、用户态和时长；记录实际 backboardd PID/身份、exec 及是否早于采样。r43 `enuma-mt: bb(34)=M/N/O/P/I` 是 PID 34 固定槽、十六进制、累计值，非任意 PID 自动识别；`enuma-att: ... entry_bb=` 为受测 open 入口 comm 计数。核对同轮 `all` 的各项阳性、PID 复用/窗口；r43 的 M/N/O/P/I 不是题设 M/N/O/I 四项，不能混淆。`enuma-fb: ... swap=` 是已有 display 探针调用计数（`docs/enuma-r30-device-20261123.md:13-42`），不单独证明 backboardd 所有权或像素。

| 同轮观察 | 判读 |
|---|---|
| `IOHIDResource=found`、`init=1 attach=1 start=1`、`digitizer properties=1` | 找到软件 nub 后代 `IOHIDEventDriver` 且两节点属性写成功；不是用户态消费或触摸证明。缺任一前提、日志不可见或采样早于发布，实验无结论。 |
| 已确认对照无 driver、候选有 driver，且 backboardd 身份/阳性对照成立，M/N/O/P/I 或 `entry_bb` 从 0 变非 0 | 支持 HID 发布与推进相关；计数不含服务名称、返回码，不能证明访问 HID 或唯一因果。 |
| 匹配成功，计数仍全零（同等窗口、进程存活及对照成立） | 不支持「只需发布此类设备即可越过当前受测入口」；不能排除其他 HID 属性、异步时序或其他前置。 |
| 匹配成功，`enuma-fb ... swap>0` | 观察到受测 swap 调用，结合后续返回、呈现/屏幕证据才判读 GUI；不证明触摸或持久交互。 |
| panic、无报告、进程退出或阳性对照不成立 | 记录失败/不可判定，不以零值否定假设。 |

若同轮已存在 r23 同类 driver，优先检查其确实存在及其后背板线程等待点；再发布同类 nub 即使无效果也不能排除更复杂的 HID 依赖。若缺当前设备状态和实际等待 PC/栈，不能将 `entry_bb=0` 归因为 HID（`docs/backboardd-offline-20261123.md:121`）。该实验最多检验充分性，不证明 HID 是必要条件；因此**现阶段不值得优先重新实现**。
