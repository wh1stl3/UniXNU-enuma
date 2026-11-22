# backboardd 跨仓差异索引

## 问题

用户提供的观察：backboardd 与 SpringBoard 已 exec、IPC 活跃，`entry_bb=0`；显示服务可被其他进程打开，但未观察到渲染，屏幕无像素。计数边界见 [r32 探针记录](enuma-r32-attempt-host-20261123.md) 第 7–21 行和 [r30 观察](enuma-r30-device-20261123.md)。

## 已确证事实

- backboardd 的直接导入表包含 `IOServiceMatching`、`IOServiceGetMatchingServices`、`IOServiceOpen`、`IOMobileFramebufferOpen` 和 `IOSurfaceCreate`；导入不证明运行时调用。来源：[离线分析](backboardd-offline-20261123.md)，第 141–146 行。
- donor 的 backboardd launchd job 将 `com.apple.iohideventsystem` 声明为该进程提供的服务；运行时注册未验证。来源：[离线分析](backboardd-offline-20261123.md)，第 90–100、148 行。
- enuma r40 prelink 包含 IOHIDFamily 和 IOHIDEventDriver，nuwa 默认 board roots 同样列出两者；不是这两个 bundle 名称缺失。来源：[HID 比较](hid-stack-backboardd-20261123.md)，第 8、35 行；两者分别是 closure 和 roots，不能视为等价运行时证明。
- sheng 的像素参照是 macOS 27.3；未找到 iPadOS 17 像素证据，因此 sheng 不是已证的同版本像素参照。来源：[补丁比较](repo-diff-patches-20261123.md)，第 16–20 行；`UniXNU/UniXNU-sheng@c8f92b20:reports/macos-unattended-desktop.md:1-3,55`。

## 拆分去向

- [补丁、构建开关与基线](repo-diff-patches-20261123.md)：补丁序列、编译开关和版本基线。
- [ADT、启动参数与策略](repo-diff-adt-bootargs-20261123.md)：ADT、设备节点、boot-args 和策略。
- [实现等效性](repo-diff-implementation-20261123.md)：同名或同职责代码的实现比较。

## 未验证项

- 未验证：各实际候选的完整补丁闭包（缺最终输入与展开记录）。
- 未验证：各仓完整实际 ADT（缺对应候选的最终 ADT）。
- 未验证：各仓实际 boot-args 全量集差（缺对应候选的最终参数）。
- 未验证：各仓逐项实测证据（缺对应版本、候选和设备观察记录）。
