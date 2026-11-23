# 共享缓存签名与 launchd 配置离线核对

状态：self-checked；无构建、设备访问或运行时验证。本地 donor 不等于设备回读。

## CodeDirectory

以 `sgan81/apfs-fuse@66b86bd525e8cb90f9012543be89b1f092b75cf3` 的本机编译版 `-o ro` 挂载 `out/userdata-clean-20261112/044-76034-038.dmg`，从 `root/System/Library/Caches/com.apple.dyld/` 的两个文件读取 dyld header 中的 codeSignatureOffset/Size，再按大端解析其 superblob 索引与 CodeDirectory；卸载。未复制 Apple 文件。

| 字段 | arm64.13 | arm64.15 |
|---|---:|---:|
| 文件字节数 | 113868800 | 104628224 |
| signature offset / reserved size | 0x6c60000 / 0x38000 | 0x6394000 / 0x34000 |
| superblob magic / length / count | 0xfade0cc0 / 222197 / 3 | 0xfade0cc0 / 204181 / 3 |
| CD magic / length / version | 0xfade0c02 / 222141 / 0x20400 | 0xfade0c02 / 204125 / 0x20400 |
| flags | 0x2 | 0x2 |
| hashOffset / identOffset | 189 / 88 | 189 / 88 |
| nSpecialSlots / nCodeSlots | 2 / 6936 | 2 / 6373 |
| codeLimit / codeLimit64 | 113639424 / 0 | 104415232 / 0 |
| hashSize / hashType / platform | 32 / 2 (SHA-256) / 0 | 32 / 2 (SHA-256) / 0 |
| pageSize log2 | 14 (16 KiB) | 14 (16 KiB) |
| scatterOffset / teamOffset | 0 / 0 | 0 / 0 |
| execSegBase / Limit / Flags | 0 / 113639424 / 0 | 0 / 104415232 / 0 |

`CS_SUPPORTSSCATTER`、`CS_SUPPORTSTEAMID` 是 CodeDirectory **version 门槛**而非 flags；version 0x20400 达到两个门槛，但 scatterOffset 与 teamOffset 均为零，没有 scatter 或 team ID 数据。flags 0x2 不能用作这两个门槛的位掩码。

每个 signature 都恰有三个索引项：slot 0 CodeDirectory `0xfade0c02`；slot 2 Requirements `0xfade0c01`，长度 12；slot 0x10000 blob wrapper `0xfade0b01`，长度 8。没有 entitlement blob 或额外 CodeDirectory。`.13` 三项 superblob 内偏移依次为 0x24、0x363e1、0x363ed；`.15` 为 0x24、0x31d81、0x31d8d。这里只枚举这两个文件签名 superblob 的子项，不声称枚举所有 dyld subcache 文件。

`UniXNU/patches/xnu/native-4k-signature-hash-cache.patch:118-132` 与 r45 生成树 `out/ufs-sm8250-ps-20261123-r45/source/bsd/kern/ubc_subr.c:5776` 起的实现：已读头字段满足 16K 签名页、非零 codeLimit、零 scatter、codeLimit64 为零或一致、slot 数等于 ceil(codeLimit/16384) 的条件。因此**已读头字段不会触发这些拒绝条件**；但最终是否拒绝无法判定，还依赖运行时 base offset/first-level hash、内存分配、文件读入、每个原始 16K 哈希比较与保护操作（patch:121-126,134-142,155-190,204-207），本次未计算验证所有哈希。调用方 r45 `ubc_subr.c:4877-4882` 在 prepare 失败时直接退出、未发布该临时 blob；不能仅从失败推断它仍被发布并随后以空缓存验页。已发布 blob 的空缓存验页路径见同文件 5956-5961。

共享缓存 fixup 由页 fault 惰性触发；三处未命中也可能是对应页未 fault，不能据此证明修补机制失败。

## launchd 配置

对同批本地 `out/userdata-clean-20261112/OS.raw` 用上述工具只读挂载，`plistlib` 解析 `root/System/Library/LaunchDaemons/` 下两个 plist。运行时是否加载或注册未证。

SpringBoard `com.apple.SpringBoard.plist`：
- `ProgramArguments = ["/System/Library/CoreServices/SpringBoard.app/SpringBoard"]`
- `LimitLoadToSessionType`：无此键。
- `EnvironmentVariables = {CA_ASSERT_MAIN_THREAD_TRANSACTIONS = "1"}`。
- `MachServices`（未标注值均为 true）：`com.apple.springboard.carditemscontroller`, `com.apple.notificationcenter.widgetcontrollerconnection`, `com.apple.usernotifications.usernotificationsettingsservice`, `com.apple.UIKit.KeyboardManagement.hosted`, `com.apple.UIKit.statusbarserver`, `com.apple.springboard.statusbarservices`（空字典）, `com.apple.controlcenter.remoteservice`, `com.apple.proactive.UserEducationSuggestion.client-listener.xpc`, `com.apple.springboard.blockableservices`（ResetAtClose=true）, `com.apple.frontboard.systemappservices`, `com.apple.systemstatus.publisher`（#Then=true, #IfFeatureFlagDisabled=SystemStatus/EmbeddedDaemon）, `com.apple.usernotifications.usernotificationservice`, `com.apple.bulletinboard.dataproviderconnection`, `com.apple.pegasus`, `com.apple.bulletinboard.settingsconnection`, `com.apple.springboard.backgroundappservices`（HideUntilCheckIn=true, ResetAtClose=true）, `com.apple.SBUserNotification`, `PurpleSystemAppPort`（ResetAtClose=true）, `com.apple.usernotifications.remotenotificationservice`, `com.apple.DragUI.druid.system`, `com.apple.siri.activation`, `com.apple.springboard.services`（HideUntilCheckIn=true, ResetAtClose=true）, `com.apple.aps.usernotifications`, `com.apple.siri.activation.service`, `com.apple.springboard.oswatchdog`, `com.apple.bulletinboard.serverconduitconnection`, `com.apple.systemstatus`（#Then=true, #IfFeatureFlagDisabled=SystemStatus/EmbeddedDaemon）, `com.apple.posterboardui.services`, `com.apple.systemstatus.activityattribution`（#Then=true, #IfFeatureFlagDisabled=SystemStatus/EmbeddedDaemon）, `com.apple.usernotifications.delegate.com.apple.donotdisturb`, `com.apple.aps.usernotifications.dev`, `com.apple.siri.assessment-mode-restriction`, `com.apple.bulletinboard.observerconnection`, `com.apple.pencilkit.pktouchdetection`, `com.apple.hangtracermonitor`, `com.apple.proactive.HomeScreenSuggestion.xpc`。

`MachServices.com.apple.accessibility.AXSpringBoardServer` **不在该 SpringBoard plist**。以 plistlib 搜索 OS 卷 `System/Library/LaunchDaemons` 与 `LaunchAgents` 各 plist 的同一键，也未发现提供者；不能排除其他位置、动态注册或其他进程，提供者未定。

backboardd `com.apple.backboardd.plist`：`ProgramArguments = ["/usr/libexec/backboardd"]`，`LimitLoadToSessionType`、`EnvironmentVariables` 均缺。`MachServices` 全部键及值见 `docs/backboardd-offline-20261123.md:187-210`；其中 `com.apple.iohideventsystem`、`com.apple.CARenderServer`、`com.apple.backboard.display.services` 三者均有 `ResetAtClose=true`。

## r45 OCR 对账

`docs/enuma-r45-ps-host-20261123.md:25-30` 是预期核对清单，不是实测进程表；该文档末尾明确未上机。对 `.cache/frames-r45-ocr/text/*.txt` 不区分大小写搜索，OCR 原文：

| 项 | 结果 |
|---|---|
| cfprefsd | `last0021.txt:40` `Successfully spawned cfprefsd(62) because (pc (mach)`；OCR 噪声，非进程表快照 |
| containermanagerd | 未见 |
| UserEventAgent | `last0005.txt:125` `(user /581/coa .epple .UserEventAgent -Systes) (otice>: service state: spam scheduled`；服务状态不证明进程存活 |
| trustd | 未见 |
| watchdogd | 未见 |
| runningboardd | `last0021.txt:90` `(pid/6 (runningboardd)) otice>: qresthfing exec source upfrant`；另 `last0011.txt:59` 为服务状态 |
| iomfb | `last0072.txt:19` `eruma-ctt: (com) IOMFB_FOR_Loader=1`；配置文本，不是进程 |

未见只限定 OCR 文本，OCR 可能漏识，不能推出进程不存在；运行时进程表及页面触发仍未核实。
