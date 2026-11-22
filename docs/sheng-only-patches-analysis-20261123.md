# sheng 独有补丁：按 iPadOS 17 profile 筛选（2026-11-23）

状态：self-checked，纯主机静态调查；未构建、未上机。源 `UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e`，本地 Git 副本 `C:/Users/Administrator/AppData/Local/Temp/unixnu-sheng`。基准是该提交的 profile 和 series，不是历史全部分支的实际应用闭包。

## 筛选方法与限制

`board.toml` 的默认 profile 是 iPadOS 27，kernel 的 `patch_series` 指向 `device:patches/xnu-12377/series`；iPadOS 17.7.11/21H461 的 kernel override 明确指向 `device:patches/xnu/series`；macOS 27.3 override 未替换 patch_series。后者因此也是配置级继承，未核对实际构建。两条 series 中分别有 25 和 3 个本清单 basename；3 个 basename 跨线，但两版文件有差异，应读 `patches/xnu/` 版本。文件名在 series 内不等于实际已经成功应用或运行。iPadOS 27 不是 iPadOS 17，也不应误称 macOS 专属。

下表“无法判定”表示**不属于该 pin 的 iPadOS 17 device series**，且仅凭 series 不能确定它是 macOS 专用还是 iPadOS 27/macOS 共用，也不排除历史 iPadOS 17 分支以其他路径或不同名字实现。这里“跨线”特指同名在 iPadOS 17 与 xnu-12377 series 中均存在，不代表代码字节相同。

| 文件名 | 线别 |
|---|---|
| sheng-appsync-runtime.patch | 无法判定（xnu-12377，非此 pin 的 iPadOS 17 series） |
| sheng-appsync-user-trust.patch | 无法判定（同上） |
| sheng-bluetooth-exit-diagnostic.patch | 无法判定（同上） |
| sheng-bluetooth-runtime.patch | 无法判定（同上） |
| sheng-bootstrap-checkpoints.patch | 无法判定（同上） |
| sheng-cache-input-diagnostic.patch | 无法判定（同上） |
| sheng-headless-startup-checkpoints.patch | 无法判定（同上） |
| sheng-main-thread-profile.patch | 无法判定（同上） |
| sheng-platform-sleep.patch | 无法判定（同上） |
| sheng-process-exit-log.patch | 无法判定（同上） |
| sheng-startup-failure-log.patch | 无法判定（同上） |
| sheng-wifi-association-event.patch | 无法判定（同上） |
| sheng-wifi-launchd-cache.patch | 无法判定（同上） |
| source-storage-runtime.patch | 无法判定（同上） |
| vmwait-dyld-pager-source-release.patch | 无法判定（同上） |
| zzyd-sheng-audio-addon-mount.patch | 跨线：iPadOS 17 / xnu-12377 |
| zzye-sheng-cpu-idle.patch | 跨线：iPadOS 17 / xnu-12377 |
| zzyf-sheng-amp.patch | 跨线：iPadOS 17 / xnu-12377 |
| zzzz-sheng-ipados27-bringup.patch | 无法判定（xnu-12377，非此 pin 的 iPadOS 17 series） |
| zzzzzz-sheng-bsd-checkpoints.patch | 无法判定（同上） |
| zzzzzz-sheng-latency-trace.patch | 无法判定（同上） |
| zzzzzzzz-sheng-exit-latency.patch | 无法判定（同上） |
| zzzzzzzzz-sheng-unnest-trace.patch | 无法判定（同上） |
| zzzzzzzzzz-sheng-sigp-reinit-assert.patch | 无法判定（同上） |
| zzzzzzzzzzz-sheng-edge-matrix.patch | 无法判定（同上） |

## iPadOS 17 内容结论

行号均指固定提交的 `patches/xnu/<文件>` 补丁文本，不是运行时源码行号。

| 补丁 | 问题、触发与症状 | enuma 等价性 | 与现象相关性 |
|---|---|---|---|
| zzye-sheng-cpu-idle.patch | 行 7–25：`sheng_cpu_idle_mach` 查处理器、用 `recount_processor_usage` 取得 idle 累计给板级 governor；不存在 processor 返回 0。没有说明未补时的启动停滞症状；只能推断影响调用者按负载调频，不是直接修复线程阻塞。 | `package/`、`patches/` 和 r40 `source/` 未命中 `sheng_cpu_idle_mach`、`recount_processor_usage` 特征组合；r40 `source/` 仅包含部分重编源码，复用对象未证明，等价性不确定。 | 低：不能由低 IPC 推定 governor 被调用或时钟不足。 |
| zzyf-sheng-amp.patch | 行 1–18 增加 AMP 与两 cluster，行 20 起对 Edge bucket 选择 P cluster、保护 UI 任务不被迁到 E、允许空闲 P 窃取 E 工作；仅 `CONFIG_SCHED_EDGE` 等条件下生效，且是 SM8550 A510/P 核拓扑。注释描述 UI 线程落在慢核降低帧处理能力；永久阻塞/无 IPC 是推断且未证明。 | `patches/` 和 r40 局部 `source/` 未命中 `sched_edge_ui_bucket_stays_on_p`；enuma 已有独立 SMP/cluster 补丁但不能据此认定调度策略等价；r40 实际复用对象不全，等价性不确定。 | 低：解释性能分配，不证明进入 IOKit 前停滞；不得移植 SM8550 板值。 |
| zzyd-sheng-audio-addon-mount.patch | 行 5–10 增加挂载状态变量，行 12–22 在 `native_gpu_addon_prepare` 把音频插件目录挂到 HAL 插件目录，供音频服务发现；未挂载的音频症状为推断。 | r40 局部 `source/` 未命中 `native_gpu_addon4_stage`；未证明整个最终链接闭包。 | 无关：音频插件不解释目标显示服务启动停滞。 |

同 donor 的 iPadOS 17 可选 CPU 调频与多核策略是本表中唯一与“进程推进”间接相关的项；**没有在这 25 个 basename 的 iPadOS 17 device series 中找到直接修复 pager 等待或添加启动检查点的项目**。显示接入本身可能在 `package/`、其他仓或其他文件，不能从此表推断不存在。

## 范围外：xnu-12377，非 iPadOS 17 series

下列 22 个只出现在该 pin 的 xnu-12377 device series，按范围修正不做内容机制分析：`sheng-appsync-runtime.patch`、`sheng-appsync-user-trust.patch`、`sheng-bluetooth-exit-diagnostic.patch`、`sheng-bluetooth-runtime.patch`、`sheng-bootstrap-checkpoints.patch`、`sheng-cache-input-diagnostic.patch`、`sheng-headless-startup-checkpoints.patch`、`sheng-main-thread-profile.patch`、`sheng-platform-sleep.patch`、`sheng-process-exit-log.patch`、`sheng-startup-failure-log.patch`、`sheng-wifi-association-event.patch`、`sheng-wifi-launchd-cache.patch`、`source-storage-runtime.patch`、`vmwait-dyld-pager-source-release.patch`、`zzzz-sheng-ipados27-bringup.patch`、`zzzzzz-sheng-bsd-checkpoints.patch`、`zzzzzz-sheng-latency-trace.patch`、`zzzzzzzz-sheng-exit-latency.patch`、`zzzzzzzzz-sheng-unnest-trace.patch`、`zzzzzzzzzz-sheng-sigp-reinit-assert.patch`、`zzzzzzzzzzz-sheng-edge-matrix.patch`。其中包含 macOS profile 继承的 series，但不能把全部称为 macOS 专属：默认 profile 是 iPadOS 27。**已证实 macOS 专属的文件名列表：无；未逐项追溯引入提交，不能证明不存在。**

`vmwait` 的 xnu-12377 补丁内容在收到范围修正前已读，故不据此在本报告给出 iPadOS 17 适用性或相关性结论；不能把同名未选入当成等价实现缺失的证明。

## 下一步

最小纯主机动作：针对 iPadOS 17 profile 的完整实际内核对象链和上游同版本 `vm_dyld_pager.c`/shared-region pager 做源码及链接对象归属对照，先确定 4K/16K 拼页实现与相应释放路径；不得以 xnu-12377 内容直接推定 10063 的行为。若完整对象来源不可恢复，结果保持不确定。当前运行时是否在 pager 等待未获证据，也不据“未进 IOKit”的计数零值证明完全没有 IOKit 调用。
