# nuwa 与 sheng 持久 store 对照

状态：self-checked 静态调查；设备观察引用原记录，未独立复核。本轮无构建或设备操作。板级几何不能跨设备复制。

## nuwa

* `nuwa/UniXNU-nuwa/package/nuwa-ramblock/NativeRamBlock.cpp:85-105`：`attachStore()` 先查 mode、seed 和全部 weak provider，再调用 `native_ufs_store_gpt_check()` 与 `native_ufs_store_open(...)`；失败为 state 4。`:113-132` 中 Fresh 和 mode 2 resumed 才走 direct。`:88-91` 指明只有 reset=1/2 才重建旧 overlay；正常启动保留不匹配或损坏的 store。该 fork 来源和版本见同目录 `SOURCE.md:1-7`。
* 当前已记录的 nuwa 链接结果不是无条件开放：`nuwa/worktree-display-dsp/docs/nuwa-session-20261122-findings.md:13-34` 原文：“mode 2 reaches unconditional `mov w0,#0` refusal”以及“`hostStoreOpen` and `hostLogOpen` both unconditionally return false”。这是主控转述的链接内核反汇编，原始反汇编未随该文档提供；不能外推所有 worktree 构建。
* 同记录 `:13-17`：主控转述实机 `DS=4`、store open 失败，RAM overlay 非持久；`:27-34` 称单槽超时隔离后根读不能恢复，保持只读 stub。旧 `nuwa/UniXNU-nuwa/docs/nuwa-userspace-20261119-observation.md:47,139-141` 的“写 overlay”不能当作持久写成功：后来的 `nuwa-session-20261122-findings.md:13-19,53-55` 已纠正这一前提。未找到跨重启 store 保留的实测。
* owner：`nuwa/UniXNU-nuwa/porting.toml:85` 记录 root path 的双 owner-policy 与逐块验证，同时明确 “All media writes/store/log windows refused”。这是根卷认证，不是对 Data store placement 的签名放行；已检查路径未发现使 store 放行的 owner placement 验证。`nuwa/AGENTS.md:15-16,40-42` 保留启动认证 NOT REACHED，不得把 root policy 写成完整启动认证。
* GPT：RamBlock 调用 GPT check 的源码顺序为 `:98-104`，但本轮没有独立读取最终 nuwa provider 的 GPT check 实现，不能声称它是否重读、缓存或不会 poison；主控转述的单槽超时隔离限制见上述 session findings。store open stub 不等于之前 GPT check 一定无 I/O。
* 参数与历史计划：`nuwa/UniXNU-nuwa/docs/nuwa-r35-display-20261120-observation.md:37` 有 `native-ufs-root=1 native-ufs-lun=0 sheng-data-persist=2 sheng-data-reset=1 sheng-log-reserve=1024`。`docs/swap-and-persistent-data-20261123.md:18-23` 记录 8 GiB 逻辑 seed、1024 MiB reserve、4 KiB 块、历史 userdata `[3110976,61850619)`、store 2097217 块 `[59491258,61588475)`；是离线布局而非当前认证几何。`nuwa/.../docs/nuwa-userspace-20261119-observation.md:126-144` 记录 seed 和卷观察；reset 会丢弃旧 overlay。

## sheng 对照

设备仓 `UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e`，gitlink `UniXNU/ShengUfs@9d527ae1a8d36a7ff210f9f4c9b429549c34c991`；源文件 [NativeUfs.cpp](https://github.com/UniXNU/ShengUfs/blob/9d527ae1a8d36a7ff210f9f4c9b429549c34c991/NativeUfs.cpp)、[RootCommands.h](https://github.com/UniXNU/ShengUfs/blob/9d527ae1a8d36a7ff210f9f4c9b429549c34c991/RootCommands.h)，源码 SPDX BSD-2-Clause-Patent。设备仓本地参考仅有 Git 对象，文件以 `git show` 读取。

* 门控：`NativeUfs.cpp:2949-2966` 中 `findRootLayout` 成功且 `manifestStatus == 0` 后直接 `gStoreGeometry = { true, ... }`，这里没有 enuma 的 `storeBound` owner-placement 门。`:1515-1523,1530-1553` 解析 `data-persist`，检查 mode、geometry、host ready、size、root 末尾 1024 块 guard，mode 2 调 `hostStoreOpen`。`RootCommands.h` 的 `hostStoreOpen` 再拒绝重复打开、越界及与 log 重叠；这不是无条件打开。
* 认证：上述有效 root manifest 与几何检查不等于 store placement 的 owner 签名认证；`UniXNU-sheng@c8f92b20:porting.toml:234` 区分 root-policy signed headers 和 Data store。此处未发现 owner key 对 store 起止 LBA 的签名绑定，不应拿 sheng 的条件替代 enuma 门禁。
* GPT 与 poisoning：`NativeUfs.cpp:1863-1875` 明确 `hostRead4k(0, 1, 1, block)` 后再读 entries 并比较 CRC；这是重读，不是只用缓存。nuwa fork `NativeRamBlock.cpp:98-104` 有 GPT check 在 store open 之前，sheng 对应 RamBlock 具体版本调用顺序本轮未独立核对。`RootCommands.h` 的 `hostAwait` 在 timeout/fatal 时设置 `gHost.poisoned = true; gHost.ready = false`，共享 host 并无已证明的超时隔离；多槽不代表超时后根读可继续。不能说 sheng 已避免该问题。
* 实测边界：`UniXNU-sheng@c8f92b20:porting.toml:281` 原文 “On sheng, macOS 27.3 mounted Data as writable APFS.” `:289` 原文 “the validated integration mounts its sealed root and persistent Data volumes.” 这是 macOS 记录，不是 iPadOS 17 mode 2 的跨重启保留证明；`:235` 的 “writes survive reboot” 是 completion 目标，不是实测结果。本轮未找到对应 iPadOS 17 的跨重启数据比对。
* 参数：设备仓 `board.toml:184-185` 的 iPadOS 17 profile 用 `native-ufs-root=1 ... data-persist=2`，不是 nuwa 的 `sheng-data-persist`。`:13-15` 给 userdata 3094592..64007162、4096 B 块；`NativeUfs.cpp:1494-1510` 默认 reserve 1024 MiB，log 32 MiB、export 256 MiB 位于 reserve。`:1538-1547` 给窗口按 seed 页数与 reserve 定位。`board.toml:67` 的 215 GiB 是顶层 runtime 值，而 `:192` 对 iPadOS 17 移除 `payload.runtime`，因此不能把 215 GiB 断言为该 profile 的 seed 或计算实际 store；实际 seed/window 大小未核实。

## 对 enuma 的意义

nuwa 的失败关闭比 sheng 的无 owner-placement 绑定更符合 enuma 现有门禁；两者均未证明共享 host 超时后根读可恢复。可借鉴的是区分 root 认证和 store placement 认证，以及不把 GPT CRC/seed hash 当 owner 授权；不复制板值或直接放行写入。
