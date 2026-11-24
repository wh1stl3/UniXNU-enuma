# nuwa 差异与 enuma 对照（2026-11-25）

结论：没有找到 nuwa 已确认的「同 donor 全量对比得到高置信解决方案」；找到的是 Data seed 目录和服务禁用清单差异，因果未证。enuma 不能据此认定同一问题或直接套修。仅离线审阅 / self-checked，未构建、未碰设备。

## 搜索与最近十项

2026-11-25 按文件修改时间倒序，在 `D:/Code/PortingiOS/nuwa` 递归搜索 `.md`/`.txt` 中任务列出的关键词；包括 worktree、out，排除 `.git`、`.cache`、`node_modules` 和大于 5 MB 的文件，因此不是整个目录所有格式的穷尽搜索。最近十项及各自结论：

| 修改时间（本地） | `nuwa/` 下文件 | 结论 |
|---|---|---|
| 11-25 00:33:45 | `worktree-display-dsp/docs/nuwa-open-deltas-20261125.md` | 旧 seed 对 merlinx 规格的差异不证明因果；运行态与对端未知。 |
| 00:31:03 | `worktree-display-dsp/README.md` | 指向差异清单；8 目录包未上机。 |
| 00:31:03 | `worktree-display-dsp/AGENTS.md` | 8 目录包未上机，待 deep review。 |
| 00:30:31 | `worktree-display-dsp/out/seed-full-20261125/HANDOFF.txt` | 30 目录仅主机/VM 候选，未制包、未上机。 |
| 00:30:31 | `worktree-display-dsp/docs/nuwa-seed-full-20261125.md` | 补目录及两个权限偏离仅主机 self-checked，不创建 plist。 |
| 00:09:54 | `worktree-display-dsp/docs/nuwa-iconservices-survey-20261125.md` | 未找到同完整栈的公开修复；各替代手段在 nuwa 未验证。 |
| 00:05:23 | `worktree-display-dsp/docs/nuwa-lsd-stack-20261124-symbols.md` | lsd 栈到 IconServices 同步 XPC，缺对端和 selector；候选缓存的运行时 UUID 未观察。 |
| 11-24 23:47:59 | `worktree-display-dsp/docs/nuwa-seed-containers-20261124.md` | 八目录主机候选未上机；无 plist；变更与探针混合，不能隔离因果。 |
| 22:32:26 | `worktree-display-dsp/docs/nuwa-seed-diff-merlinx-20261124.md` | 旧 seed 对另一项目规格有 37 缺目录、10 元数据差异，未证因果。 |
| 22:23:39 | `worktree-display-dsp/docs/nuwa-macos-vm-pipeline-20261124.md` | 该时点 pipeline 未完成；后续状态以 full seed 记录为准。 |

最新相关提交 `UniXNU-nuwa` worktree `a268f9f`（差异清单）、`bebe192`（完整目录主机交接）。

## 一至四：实际找到什么

1. 具体差异：`UniXNU-nuwa` 的 `worktree-display-dsp/docs/nuwa-seed-diff-merlinx-20261124.md:25-67` 记录，旧 Data seed 缺 `containers/Data/Application`、`containers/Data/PluginKitPlugin`、`mobile/Containers/Shared/AppGroup`、`mobile/Library/Caches/com.apple.LaunchServices` 等；`:229-247` 记录缺 `db/com.apple.xpc.launchd/disabled.plist` 和 `disabled.501.plist`。对比源是 [Dracen-W/UniXNU-merlinx@fb616afa1231b0ad2b6a6f4832a299b76b64031c `data-seed.json`](https://github.com/Dracen-W/UniXNU-merlinx/blob/fb616afa1231b0ad2b6a6f4832a299b76b64031c/data-seed.json)：`com.apple.iconservices.iconservicesagent: true` 出现在两份 disabled 规格（nuwa `docs/nuwa-iconservices-survey-20261125.md:13` 原文）。merlinx 使用 iPadOS 17，不是 nuwa 的 iPhone10,3 iOS 16.7.16 donor（nuwa `AGENTS.md:6`）；不是同 donor 的证实修复。
2. 为何以前忽略：未找到作者解释，不能虚构。可确认官方生成器从 donor 动态复制 var，显式路径列表不是完整卷清单（nuwa `docs/nuwa-seed-full-comparison-20261124.md:9-12,24`）；对比旧 inventory 才识别缺项，不证明以往的具体调查经过。
3. 机制仅为候选：预建应用容器/LaunchServices 缓存父目录或消除目录权限阻挡，可能影响服务初始化；另一个思路是在正确 domain 禁用 iconservicesagent，使等待请求失败并回退，但 nuwa 未确定 XPC 对端。其他平台回退图标不证明 iOS 同效；禁用 agent 有图标缺失代价（nuwa `docs/nuwa-iconservices-survey-20261125.md:12-15,21-34`）。`docs/nuwa-seed-full-20261125.md:3-9` 明确候选未上机且不创建 plist，不能称 nuwa 认为已解决。
4. 证据：旧镜像与规格的路径差异为离线 self-checked；修复卡点的因果为弱推断、运行效果未验证。nuwa 设备栈经 vision 转录且运行时缓存 UUID 未观察（`docs/nuwa-lsd-stack-20261124-symbols.md:44-49,93-105`），不能把其他项目的锁屏结果归因到单一 seed 项。

## 五至七：enuma

5. 无法判定是否同样问题。enuma `docs/seed-vs-donor-var-20261124.md:16-22,40-42` 对旧 seed 的离线检查发现 `disabled.plist` 不存在；未查 `disabled.501.plist` 和上述每个目录，也未查当前运行卷；同一文件 `:79-85` 明确无法归因。enuma 的参考 seed donor 与 merlinx 同为 iPadOS 17.7.11 / 21H461 的事实尚未由本次独立查证，不因同大版本认定同 donor。
6. 不建议直接修改 seed 或批量创建 disabled plist；缺同轮实际卷的路径、权限和客户端/对端证据，无法确定最小修复。nuwa 资产不得跨用。
7. 两者可见卡点不同：nuwa 是候选 `ISIconManager` 同步 XPC 栈；enuma `docs/launchd-0320-handler-20261124.md:3-9,19-25` 是 backboardd 的 PID-domain 0x320 请求等回复，接收端、请求内容和 Data 实际 I/O 均未证。不能据此证明底层原因必然不同。下一步只读复核 enuma 同次记录中 PID 34/backboardd 相关 launchd 路径、errno 和 reply；无关联则继续保留未知，不因 nuwa 的候选关闭服务或补目录。
