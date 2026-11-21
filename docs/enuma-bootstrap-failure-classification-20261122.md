# enuma bootstrap 失败分类

状态：**仅静态审查**。范围为题设报告的 14 条路径；未新增设备观察。执行前 CommCenter 可执行体 ENOENT 来自题设，未在 [P2] 独立核到；这不证明该 plist bootstrap 失败的原因。

缺硬件可以解释运行功能不可用，但不能自动解释 launchd 对路径的 bootstrap 失败，也不能单凭服务名证明不阻塞 SpringBoard。[S4]

| 服务或路径 | 硬件／子系统 | 分类 | 是否预期失败及依据 |
|---|---|---|---|
| `NanoLaunchDaemons` 目录 | Nano／Watch 相关启动项 | `unknown` | 题设称目录不存在；是否为此镜像正常布局未核，失败原因未定。 |
| `AppleInternal/Library/LaunchDaemons` | Apple 内部构建 | `unknown` | 项目记录将出货卷无 AppleInternal 作为预期背景，但缺本卷目录清单；不属于硬件缺失。[P1] |
| `AppleInternal/Library/LaunchAngels` | Apple 内部构建 | `unknown` | 同上。[P1] |
| `SepUpdateTimer` | SEP 更新 | `unknown` | 功能名指向安全协处理器，但没有此版本 plist 或失败码，不能证明导入失败由缺 SEP 引起。 |
| `biometrickitd.mesa` | 生物识别，Mesa／Touch ID | `unknown` | 原型 iPad7,1 使用 Touch ID，不是 Face ID；移植的生物识别实现未证。不能据此解释 bootstrap 失败。[S1] |
| `checkerboardd` | CheckerBoard 相关，具体依赖未核 | `unknown` | 没有本版本依赖或是否可省略的证据。 |
| `dietapplecamerad` | 名称指向相机子系统 | `unknown` | 相机未适配不等于 plist 导入必然失败；具体依赖未核。 |
| `wifid` | Wi-Fi | `unknown` | 服务用途有公开资料，但无 Wi-Fi 驱动不证明 bootstrap 失败是预期行为。[S2] |
| `anomalydetectiond` | 名称指向异常检测 | `unknown` | 具体输入和依赖未核。 |
| `systemstatusd-nonUI` | 名称指向系统状态 | `unknown` | 具体职责和依赖未核，不能归为蜂窝专属。 |
| `safetyalertsd` | 名称指向安全警报 | `unknown` | 具体职责及对蜂窝的依赖未核。 |
| `sysdiagnose.darwinos` | 系统诊断 | `unknown` | macOS 公开日志也出现该 plist 的导入错误，说明不能从名称推断它仅适用于蜂窝设备；不能用该日志证明本次原因相同。[S3] |
| `threadradiod` | 名称指向 Thread 无线电 | `unknown` | 没有本机 Thread 能力、plist 条件或失败码证据，不能将当前失败直接定为硬件缺失。 |
| `CommCenter` | 蜂窝通信等；完整依赖未核 | `path-or-view` | 题设报告执行前 `/usr/libexec/CommCenter` 为 ENOENT，值得核对卷内文件和当前视图；这尚不证明它是该 plist bootstrap 失败的原因。[P2] |

本次没有足够证据将任何条目归为 `hardware-absent`；其余 13 条不是已证实的硬件噪声。

## Wi-Fi 机型与 CommCenter

Wi-Fi 机型并不能证明 CommCenter 文件本来不该存在。`iPad7,1` 对应 A1670、第二代 12.9 英寸 iPad Pro Wi-Fi 版 [S5]；Apple 区分该代 Wi-Fi 与 Wi-Fi + Cellular 硬件 [S6]。本项目 r9 记录中该 plist 在执行前视图解析为 `REG` [P2]，所以不能说这份镜像没有该 plist。尚缺同版本原版 Wi-Fi 设备的执行体清单和启动条件，不能把 ENOENT 或 bootstrap 失败定为预期。

## 五个不确定服务

`checkerboardd` 的具体职责、`anomalydetectiond` 的检测对象、`systemstatusd-nonUI` 的状态源、`safetyalertsd` 的警报来源均未查到足以限定依赖的版本化资料；`sysdiagnose.darwinos` 属系统诊断方向，公开 macOS 日志中也出现该路径 [S3]。五者均不能仅因无基带／蜂窝就判定应缺失，也未证明它们在 Wi-Fi 机型必然存在或必须启动。

**下一步：优先追 CommCenter 的执行体路径与卷视图；其他系统 plist 先保留 `unknown`。**

## 来源

- [P1] `docs/enuma-r8-device-20261121.md`，r8 项目记录。
- [P2] `docs/enuma-r9-device-20261121.md`，r9 项目记录；CommCenter 执行体 ENOENT 是本任务提供的事实，未在该文档独立核到。
- [S1] [Apple：Identify your iPad model](https://support.apple.com/en-us/108043)，现行公开页面。
- [S2] [The Apple Wiki：Services](https://theapplewiki.com/wiki/Services)，版本未固定。
- [S3] [Apple Support Communities：Reading LaunchD log](https://discussions.apple.com/thread/255224451)，2023，macOS 用户日志，非 iPadOS 依赖规范。
- [S4] [Apple：Creating Launch Daemons and Agents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)，归档文档。
- [S5] [AppleDB：iPad7,1](https://appledb.dev/device/identifier/iPad7,1.html)，版本未固定。
- [S6] [Apple：第二代 12.9 英寸 iPad Pro 技术规格](https://support.apple.com/en-us/111964)，现行公开页面。
