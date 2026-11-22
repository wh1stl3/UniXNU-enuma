# backboardd 离线分析（2026-11-23）

状态：self-checked；无设备操作、构建或镜像写入。不能确定 `entry_bb=0` 的阻塞项，更不能把 HID 缺失当成已证根因。

## 提取与边界

WSL 用本机 `sgan81/apfs-fuse@66b86bd525e8cb90f9012543be89b1f092b75cf3` 对 `out/userdata-clean-20261112/OS.raw` 执行 `apfs-fuse -o ro`。首次挂载成功，但卷内实际为 `root/usr/libexec/backboardd`，预期路径少了 `root/`，脚本退出 3 并卸载成功；修正后再次只读挂载、复制并卸载成功。另一次只读挂载读取 launchd plist，卸载成功；未挂载 DMG。三次卸载均 exit 0。

```
stat -c '%n %s bytes' out/bb-offline-20261123/backboardd
# out/bb-offline-20261123/backboardd 1220560 bytes
sha256sum out/bb-offline-20261123/backboardd
# 6e362a46a2b46eb2741ecc6fcb50ffecb2fbc299641159045475361e62b34634
file out/bb-offline-20261123/backboardd
# Mach-O 64-bit arm64 executable, flags:<NOUNDEFS|DYLDLINK|TWOLEVEL|PIE>
git check-ignore -v out/bb-offline-20261123/backboardd
# .gitignore:2:/out/ ...
git status --porcelain -- out/bb-offline-20261123
# 无输出；git ls-files 同目录无输出
```

提取物只在本地 ignored `out/`，不作为项目依赖。单次脚本首行打印并校验非空挂载点和 fuse 路径，EXIT trap 执行 `fusermount -u`。

## 字符串、接口及服务

`strings "$b" | grep -Ei 'IOHIDSystem|IOHIDEventSystem|IOHIDEventDriver|IOMobileFramebuffer|IOSurfaceRoot|IOFramebuffer|IOGraphics|IOAccelerator' | sort -u` 的命中：

```
<key>com.apple.iohideventsystem.server</key>
!com.apple.iohideventsystem.server
/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer
_IOMobileFramebufferOpen
_IOMobileFramebufferSetDebugFlags
```

大小写不敏感搜索中，其余列出的类名无命中；`iohideventsystem.server` 实为签名 entitlement 键，不是已证明的匹配类名。`llvm-nm -m "$b" | grep -E 'IOServiceMatching|IOServiceOpen|xpc_connection_create_mach_service'` 确认三个 undefined imports；未解析实参，故没有确认任何具体 `IOServiceMatching` 类名。框架或动态拼接的字符串不在此搜索范围内。

`strings "$b" | grep -i 'com\.apple\.' | grep -Ei 'hid|backboard|springboard|xpc|launchd' | sort -u` 命中很多通知名、队列名和 entitlement，不能将其直接认作连接。代表项：

```
com.apple.backboard.hid.services
com.apple.backboard.display.services
com.apple.backboard.watchdog
com.apple.backboard.oswatchdog
com.apple.springboard
<key>com.apple.private.xpc.launchd.app-server</key>
<key>com.apple.iohideventsystem.server</key>
<string>com.apple.backboard.hid-services.xpc</string>
<string>com.apple.backboard.system-app-server</string>
```

字符串不能确认连接方向、顺序或是否早期连接。如下 plist 明确其中多项是本进程提供的服务，而非已证的客户端依赖。

## 直接动态库

`llvm-objdump --macho --dylibs-used "$b"` 输出如下；`liblinkguard` 标为 weak，其余为直接加载项。框架简称均指相应系统 framework，同名可在命令输出取得完整路径：

```
StudyLog, liblinkguard.dylib (weak), ButtonResolver, Haptics,
BiometricKit, CarKit, AppleHIDFeedback, libsp.dylib,
CrashReporterSupport, liblockdown.dylib, IOMobileFramebuffer,
HangTracer, WatchdogClient, CoreAccessories, SystemWake,
RunningBoardServices, QuartzCore, BackBoardHIDEventFoundation,
BackBoardHIDEventProcessors, BoardServices, Metal,
AggregateDictionary, AVFoundation, BackBoardServices, BaseBoard,
CoreBrightness, CoreAnalytics, CoreGraphics, CoreMotion, CoreText,
DataMigration, Foundation, GraphicsServices, ImageIO, CoreServices,
IOKit, IOSurface, libAccessibility.dylib, libMobileGestalt.dylib,
ProgressUI, Security, SystemConfiguration, libobjc.A.dylib,
libc++.1.dylib, libSystem.B.dylib, CoreFoundation, SoftLinking.
```

HID 相关为 AppleHIDFeedback 和两个 BackBoardHIDEvent 框架；显示相关包括 IOMobileFramebuffer、QuartzCore、Metal、CoreGraphics、GraphicsServices、IOSurface；IOKit 和 libSystem 分别承载本文件导入的 IOKit 和 XPC 符号。加载命令不证明动态加载完成，也不证明这些库先于某个具体 IOKit open 被调用。

## 入口与权限

`llvm-objdump --macho --private-headers "$b"` 显示 `LC_MAIN entryoff 141996`（0x22aac）及 `LC_CODE_SIGNATURE dataoff 1178592 datasize 41968`。使用 `llvm-objdump -d --start-address=0x100022aac --stop-address=0x100022b2c "$b"`，配合 `llvm-objdump --macho --indirect-symbols "$b"` 得到入口局部：

```
100022aac  sub sp, sp, #416     ; 保存寄存器、栈保护
100022afc  bl 0x1000977a0      ; _kdebug_trace
100022b08  bl 0x1000975b4      ; __set_user_dir_suffix
100022b0c  bl 0x100097bf0      ; _pthread_set_fixedpriority_self
```

这仅是可执行文件入口的局部直接调用，不能排除 dyld/初始化器及被调函数内部先发 Mach/IOKit；未确定整个进程首个相关调用。注意本机 LLVM 14 的 `--macho --disassemble` 没有遵守所试的 start/stop 限制，首次误产生了全量反汇编输出；以上是改用不带 `--macho` 的范围结果。

只读解析签名 superblob（大端 header `fade0cc0`，slot 5 `fade7171` XML，经 Python `plistlib`，共 90 个 entitlement）确认 `com.apple.iohideventsystem.server=true`、`com.apple.hid.system.user-access-service=true`、`com.apple.private.hid.client.event-{dispatch,filter,monitor}=true`、`com.apple.private.xpc.launchd.app-server=true` 等。它们是授权声明，不证明运行时已使用或获满足。

只读 `plistlib.load` 读取 OS 卷 `root/System/Library/LaunchDaemons/com.apple.backboardd.plist`：

```
Label = com.apple.backboardd
ProgramArguments = ['/usr/libexec/backboardd']
RunAtLoad = True; KeepAlive = True; UserName = mobile
MachServices = {
  com.apple.iohideventsystem: {ResetAtClose: True},
  com.apple.backboard.hid.services: {ResetAtClose: True},
  com.apple.backboard.display.services: {ResetAtClose: True},
  com.apple.backboard.hid-services.xpc: True,
  com.apple.backboard.system-app-server: True,
  com.apple.CARenderServer: {ResetAtClose: True}, ...
}
```

这证明 donor job 声明这些服务，不证明 enuma 的 job 已加载、服务被注册或 backboardd 在等待它们。

## r40 对账与判定

r40 prelink/ADT 的已有本地复核命令、组件清单与证据边界见 `docs/hid-stack-backboardd-20261123.md` §1；这里区分用户态框架、Mach 服务与 kext，不混称：

| 依赖名 | backboardd 需要的证据 | enuma 提供（r40） | 判定 |
|---|---|---|---|
| IOHIDFamily | HID 框架及权限存在；具体最早依赖未知 | prelink 组件实体 | 存在不等于运行时发布 |
| IOHIDEventDriver | 未证明本程序直接匹配 | codeless 组件；软件 stand-in 路径，ADT 未见 HID 节点名或属性名 | 发布与用户态使用未证 |
| IOHIDSystem | 未发现目标类名；权限键存在 | 唯一命中是日志字符串 | 不能推断具体实体或缺失导致阻塞 |
| IOHIDEventSystem | entitlement 和本 job `com.apple.iohideventsystem` 服务声明 | prelink 名称零命中；Mach 服务是否注册未知 | 用户态服务与内核实体不是同一事物 |
| IOMobileFramebuffer / IOSurface | 有框架 load/import；具体首次调用未知 | r40 的运行时发布和本次匹配未证 | 不能由符号推断成功 open |
| XPC/launchd | XPC import，donor job 声明服务 | enuma 是否成功注册和通信未知 | 方向及等待目标未证 |

`entry_bb=0` 仅说明采样窗口没有观察到该进程进入 `is_io_service_open_extended`；它不排除用户态更早失败、等待、未执行、调用其他路径或匹配未成功。用户提供的 IPC 25/25 也不标识消息目的与阻塞目标。**没有足够依据给出最可能缺失项（置信度：无法评定）**；缺 backboardd 当前线程 PC/栈或能将实际请求关联到服务名、返回值及等待点的证据。下一步唯一优先项是离线追踪入口直接调用及初始化器/框架的调用链以定位可识别的首次服务请求；仍不能以静态调用链替代运行时等待证据。
