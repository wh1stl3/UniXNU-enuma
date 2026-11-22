# backboardd / SpringBoard 可执行体依赖调查（2026-11-23）

`self-checked`，只读主机调查；未操作设备、修改卷或构建。**没有提取出两个
Mach-O，因此不能给出它们各自的字符串清单、实际 bootstrap lookup、服务提供者，
也没有足够证据点名强等待候选。**

## 定位与提取限制

只读 mmap 扫描 `out/userdata-clean-20261112/OS.raw`（6,077,580,800 B）及
`044-76034-038.dmg`（3,303,014,400 B），搜索以 NUL 结尾的精确字节序列：

| 镜像 | 字节序列 | 次数及示例偏移（十六进制，相对文件起始） |
| --- | --- | --- |
| OS.raw | `backboardd\0` | 4：`0x11e1cccd`, `0x16377248`, `0x18e70248`, `0x18e718f5` |
| OS.raw | `SpringBoard\0` | 4：`0x11e10af5`, `0x11e24739`, `0x133c363a`, `0x133c39f4` |
| SystemOS DMG | `backboardd\0` | 25；首个 `0x99f4f83` |
| SystemOS DMG | `SpringBoard\0` | 358；首个 `0x17e5efb` |
| SystemOS DMG | `SpringBoard.app/SpringBoard\0` | 2：`0x99e06c8`, `0x9a6ab2e` |

`/usr/libexec/backboardd\0` 两镜像均 0 次；OS.raw 的
`SpringBoard.app/SpringBoard\0` 也为 0 次。这些是原始字节搜索，不是目录树
遍历：偏移指向字符串而非可执行文件起始或 extent；可能是其他文件、旧快照、
路径或 metadata，无法定位目标 Mach-O。未命中也不能证明文件不存在。
本机 WSL 未发现 `apfs-fuse`、`fls`、`apfsutil` 或 `7z`；未解析 APFS 活动树、
extent、快照或压缩。设备 r14 对 SpringBoard 可执行路径的 `REG` 是设备
路径查找结果，不是提取或供体卷归属证明（`enuma-r14-device-20261122.md`）。
此前 OS 的 backboardd plist 名称候选偏移和限制见
`backboardd-springboard-plist-20261122.md`。

因此没有对目标 Mach-O 运行 `strings`：**两程序去重服务字符串清单均未知**，
不是空集。先前 `mach-service-dependency-inventory-20261123.md` 是整卷扫描，
其中的 `com.apple.backboard.hid-services.xpc`、`com.apple.CARenderServer`、
`com.apple.accessibility.AXSpringBoardServer` 等仅是原始 token，不可归属两程序、
不可作为已提取的依赖清单，也不能单凭名称认定是 Mach 服务。

## 观察对照（不是提取清单的交集）

缺目标字符串清单，因此下列仅列已入库观察能确认的相关名称；不能将其误称
目标程序查找过的服务，也不能把未记录视为从未出现。

| 类别 | 精确名称或作业 | 观察及边界 |
| --- | --- | --- |
| 出现过，非服务就绪证据 | `com.apple.backboardd` | r23 user/501 作业 pending spawn；r23、r24 有 backboardd exec；作业名/exec 不证明同名 Mach 服务已注册或可用。见 `enuma-r23-hid-device-20261122.md`、`enuma-r24-census-20261122.md`。 |
| 出现过，非服务就绪证据 | `com.apple.SpringBoard` | r9 plist 路径 REG，r23、r24 SpringBoard exec；不证明同名服务注册或存续。见 `backboardd-springboard-plist-20261122.md`、r23/r24 记录。 |
| 记录中仅见 failed lookup | `com.apple.accessibility.AXSpringBoardServer` | r23/r24 记录 requestor `nfcd[30]` 失败；r22 亦记载失败。不是 backboardd/SpringBoard 发起或等待的证据，也不能断定一直未注册。 |
| 记录中仅见 failed lookup | `com.apple.bluetooth.xpc` | r22/r23 记录失败；请求者、两目标程序依赖及提供者未由这些记录确立。 |
| 未出现 | 无法形成可信名单 | 尚无目标 Mach-O 字符串，无法计算与观察的差集；不能称任何目标依赖从未出现。 |

这里的“仅见”限于引用记录的可观察内容，不是全时段结论。
指定 r32/r34 未找到对应 `*-device-*` 入库观察文档；不能用 host 候选文档
替代设备日志。r4/r9/r11/r21/r23/r24/r26/r28/r30 的相关记录不是连续
全量 bootstrap 日志，不能以未出现推断缺席。

## 结论与缺失证据

r23/r24 两程序均曾 exec，`AXSpringBoardServer` lookup 失败由 nfcd 发起；
r28/r30 的有限观察不能定位 backboardd 的线程等待点。显示相关路径可作为
待调查方向，但没有证据把某个 Mach 服务列为强等待候选。提供者是否存在、
注册于哪个 bootstrap 域、是否对请求者可见、进程是否阻塞均未知。

需要在有只读 APFS 解析能力的环境恢复活动快照中两个可执行文件及其完整
extents，确认 Mach-O 身份后按文件提取字符串、分析调用点及共享缓存中的
间接调用；同时读取对应 launchd MachServices 声明，并取得目标进程线程栈、
lookup 请求者/域/返回值及服务注册状态。字符串或 plist 声明单独均不证明
运行时服务可用。无独立 verifier 复跑。
