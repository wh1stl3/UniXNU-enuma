# 0x320 bootstrap：离线证据与边界

状态：self-checked，纯离线；未构建、未接触设备。r65 FP 链及 donor 缓存一致性假设见 `fp-symbols-r65-20261124.md`。当前没有目标请求内容、接收端栈或对应 reply；不能从调用方等回复推断 launchd 已收到或进入某个 handler。

## 1. 请求

该文档第 64 行记录 donor `__xpc_bootstrap_services` 中 `mov w0,#0x320`、随后的 `__xpc_interface_routine` 调用，调用者为 `__xpc_uncork_pid_domain_locked`；这证明调用点编号，不证明字典内容或所发送路径。

第三方 [LaunchControl.h](https://github.com/haltepunkt/LaunchControl/blob/master/LaunchControl.h) 称 0x320 为 LOAD；[LaunchControl.m](https://github.com/haltepunkt/LaunchControl/blob/master/LaunchControl.m) 的 bootstrap 例子创建 `handle`、`paths`、`type`：分别表示域标识、路径数组、域类型；该例 `paths` 是路径字符串数组，type 5 为 PID domain，handle 是 PID。它是另一客户端，不是 donor 函数；不能把该例的具体字段值视作本次消息。另一个 macOS 25G76 的[独立逆向记录](https://github.com/cenobyte-vincit/xspawn/blob/main/ARCHITECTURE.md)明确观察到同一 800 也用于大型 dylib path 字典，故不能仅由编号断言 `paths` 必为 plist 数组。以上第三方链接为未固定版本的辅助对照。

## 2. 接收路径与阻塞

Apple 公开 [launchd-842.92.1，commit 49a9c79b2949192dfca697b1054245cdfb645788](https://github.com/apple-oss-distributions/launchd/tree/49a9c79b2949192dfca697b1054245cdfb645788) 是历史实现，不能当成 iPadOS 17 私有 0x320 handler；未找到该版本对应现代 handler，不能给出伪造的 handler 行号。以下是历史 **launchctl 客户端**对比，不是 launchd 接收端：

* [`support/launchctl.c:1309-1321`](https://github.com/apple-oss-distributions/launchd/blob/49a9c79b2949192dfca697b1054245cdfb645788/support/launchctl.c#L1309-L1321)：`stat(what, &sb)`、普通文件 `readfile(what, lus)`、目录 `opendir(what)` 和 `while ((de = readdir(d)))`；`:1331` 逐条 `readfile(buf, lus)`。
* 同文件 [`1049-1051`](https://github.com/apple-oss-distributions/launchd/blob/49a9c79b2949192dfca697b1054245cdfb645788/support/launchctl.c#L1049-L1051)：`thejob = read_plist_file(what, lus->editondisk, lus->load)`，失败时记录 `no plist was returned`。
* 同文件 [`2695-2709`](https://github.com/apple-oss-distributions/launchd/blob/49a9c79b2949192dfca697b1054245cdfb645788/support/launchctl.c#L2695-L2709)：历史客户端查询 overrides 路径后 `open(..., O_RDONLY | O_EXLOCK | O_CREAT, ...)`；这是历史客户端的排他文件锁与可能阻塞点，不证明现代 launchd 对该请求加锁或写数据库。

目录/文件 I/O、plist 解析、等待锁或其它服务理论上可延迟回复，但对本次目标 handler 均未证实；同样可能请求尚未被调度、收到后未回复或 reply 投递异常。缺现代接收端代码或栈，无法排序这些机制。

## 3. 本板依赖

* `/private/var/db/com.apple.xpc.launchd/`：未证实该 PID-domain 请求必须写此路径。scratch Data 的实际挂载与写成功未被正向 I/O 验证；历史 r4 的挂载只属强推断，见 `ufs-launchd-data-20261119-observation.md`。
* `/System/Library/XPCServices`、`/usr/lib/xpc`：未采到请求路径，也未检查本次根镜像对应目录；不能断言使用或缺失。PID-domain XPC bundle 可与应用/框架相关，不能默认等同全局目录。
* `containermanagerd`、`cfprefsd`、`keybagd`：没有现代 handler 调用链证明任一者是同步依赖，也不能排除间接依赖。

## 4. 现有屏幕日志的使用

按同一次运行与进程/服务名关联，先查 `launchd` 的具体路径及 `No such file or directory`/`Read-only file system`/`Permission denied`，并保留完整数字、上下文与前后日志；只有明确同一请求或目标路径时才可归因。`SOURCE_ATTACH, code = 0` 只说明该事件成功，不证明本请求处理或 reply 完成；全局 `exiting bootstrap mode` 也不能证明 PID 34 的请求完成。缺日志不是无失败，更不能据此定位锁或某 daemon。历史 `opendir() failed`、`no plist was returned` 是旧客户端日志，不保证现代屏幕出现。

最省事的验证：重看现有同次屏幕记录，检索 PID 34/backboardd 附近的 launchd 路径及具体 errno；没有关联行则结论仍为未知，不追加设备操作。
