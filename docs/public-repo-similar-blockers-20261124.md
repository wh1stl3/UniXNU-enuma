# 公开仓相近用户态阻塞：部分检索

2026-11-24，self-checked，纯静态检索；未构建、未访问设备。

## 范围与限制

本地 `.cache/ref-pipa` 和 `UniXNU-sm8250-common` 使用搜索工具检索指定关键词，无匹配。Windows shell 首次调用 `rg` 失败（命令不存在），改用内置搜索工具。还查看了以下公开文件；**尚未逐仓完整检索指定范围，不能断言所有仓没有相同记录**。未查明 `IOMobileFramebuffer` 打不开导致 `backboard.display.services` 初始化失败的公开证据。

## 相近而非同一现象

* [Emilelu/UniXNU-mondrian `docs/engineering/STATUS.md:121`](https://github.com/Emilelu/UniXNU-mondrian/blob/main/docs/engineering/STATUS.md#L121)：原文“`CFPreferencesSetAppValue` 在 `__attribute__((constructor))` 里调用会阻塞主线程 → backboardd 崩溃。移到 `present_home()`（主队列运行时）。”记录移植 `f291b52`；没有给出同样 XPC 栈和两线程证据，不能套用为 enuma 根因。
* [AGXMX666/UniXNU-pong `migration/ipados18/services.md:92`](https://github.com/AGXMX666/UniXNU-pong/blob/main/migration/ipados18/services.md#L92)：原文“backboardd 则反复因 `NSURL initFileURLWithPath:` 接收到 nil 而 SIGABRT”。[同文件:140](https://github.com/AGXMX666/UniXNU-pong/blob/main/migration/ipados18/services.md#L140)记录 services13 原厂 CPU 合成器策略安装后 nil 容器异常未再出现，两个进程创建但未观察到画面；不能单独归因某一变更。
* [Lux12138/unixnu-nabu `README.md:41-46`](https://github.com/Lux12138/unixnu-nabu/blob/main/README.md#L41-L46)：原文“每轮强制重跑数据迁移，SpringBoard 永远不 `finishedStartup`”，保留官方迁移完成态后记录 `Migration not necessary`、`finishedStartup:YES` 和锁屏出现；这是另一个启动阻塞，不是所问同步 XPC 栈。

以上均不证明显示 provider 打不开造成当前卡点；未见同样的组合现象。外部仓运行结果仅转述，未独立复核。
