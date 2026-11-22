# backboardd / SpringBoard plist 调查（2026-11-22）

`self-checked`，只读；未访问设备、构建或修改卷。结果不足以确定启动阻塞。

## 已有直接观察

- `docs/enuma-r9-device-20261121.md:20` 记录设备侧一次 exec 前查找
  `/System/Library/LaunchDaemons/com.apple.SpringBoard.plist` 返回 `REG`。
  这不证明其内容、当前 r22 路径或 donor 卷归属。
- `docs/enuma-r22-device-20261122.md:15-18` 中 12 个视频采样帧未见两个进程
  exec/exit；采样之外未知。不能把未在采样中出现写成从未启动。

## donor 镜像部分扫描

只读扫描输入 `out/userdata-clean-20261112/OS.raw`（6,077,580,800 B）和
`out/userdata-clean-20261112/044-76034-038.dmg`（3,303,014,400 B）。
按 `docs/ufs-launchd-data-20261119-observation.md:320-327` 的目录记录键结构
（类型 9、name 长度、NUL）搜索。OS 中在名字偏移 `0x11e47a4a` 命中
`com.apple.backboardd.plist`，编码父键低 60 位 `0xfffffff0002f274`；同一编码
父键还命中 `com.apple.logd.plist` 和 `com.apple.mediasetupd.plist`。这只是原始
字节的候选记录；未完成活动 APFS 树、父目录路径及快照归属解析，不能认定它在
LaunchDaemons 或 LaunchAgents，也不能认定运行时使用该记录。扫描未完成，不可
据此断言其他名称或 SystemOS 中不存在。

## 内容与条件

未提取 plist 内容，故两个 job 的 `LimitLoadToSessionType`、
`RequireLoginWindow`、`HideUntilCheckIn`、`RunAtLoad`、`KeepAlive`、
`MachServices`、`Program`、`ProgramArguments`、`RequiredCapabilities` 和
entitlements 均未知；程序路径及可执行体是否存在亦未知。MachServices 通常声明
服务而不自动证明其为启动前置依赖，不能从名称推断依赖关系。未知 backboardd 的
system/user 域或 Aqua 条件，不能断言循环等待或将其列为最可能原因。

替代取证：在允许只读挂载 APFS 的 macOS 环境，分别只读挂载两份副本，确认卷
UUID 和活动快照，枚举上述三个目录及类似名称，用 `plutil -p` 读取两份 plist，
对程序路径只读 `stat`；必要时另从可执行体签名读取 entitlements。比对设备当前
union 视图与 launchd 实际加载/拒绝信息后才能判断运行时阻塞。不要把扫描候选或
设备 r9 查找替代 r22 当前活动树证据。
