# 实现差分：部分核对，未完成

状态：仅静态审查，**不是完整的逐 hunk 比较**。本记录不对当前症状作因果结论。
enuma 对象取 `out/enuma-gop-legacy-20261114-r2/package/` 的历史候选，
不是默认 recipe 或当前运行包；sirius `.cache/ref-sirius` HEAD
`ac0c900485f3c0cd18de9707579a1cdcd3365503`；OPi5
`.cache/ref-orangepi5` HEAD `729ba25f4d67225ff3853ba1e435b95af97e59e3`；
共用 UniXNU HEAD `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。
路径相对 `UniXNU-enuma/`，UniXNU 在 `../../UniXNU/`。

| 主题 | 涉及仓 | 判定档位 | 差异摘要（≤2 行） | 是否可解释当前症状 |
|---|---|---|---|---|
| 显示 provider | enuma / sirius / OPi5 | 不同实现 | 三者都是 `IOPlatformDevice`，但 attach/probe 次序、phase 分支与发布不同；见下。 | 未定 |
| 显示 provider | sheng / enuma | 不同实现 | sheng 的两个指定 commit 均为 `IOService`；enuma 历史候选为 `IOPlatformDevice`。类、探针顺序和显式发布不同。 | 未定 |
| Legacy 子类及四个方法 | 四仓 | 不可比 | enuma 的 `LegacyABI.in.h:15` 声明原版 ABI，`EnumaLegacyDisplay.cpp:55-58` 检查实例 metaclass；未完成实际子类及方法逐项比对。 | 未定 |
| offline-owner-systemos-mount | 四仓 | 不可比 | 共用 UniXNU 有该 patch；未解析各仓实际 patch 生成、选择和 hunk，不能以文件存在代替等效。 | 未定 |
| offline-legacy-* | 四仓 | 不可比 | 同上；需逐版本展开和比对实际 patch body，不能推定调用点已编译。 | 未定 |
| offline-mobile-graphics-* | 四仓 | 不可比 | 尚未找到各实际版本的完整补丁体；不推定缺失或相同。 | 未定 |
| kern_exec / bsd_init | 四仓 | 不可比 | sirius `sirius-skip-exec-policy.patch` 在 `process_signature` 条件清除 MAC/CS 结果；其他仓及挂载、探针、环境、retry 未完成比对。 | 未定 |
| IOKit matching / 通知 | 四仓 | 不可比 | enuma、sirius、OPi5 的显示探针均等待 `IOCoreSurfaceRoot`；全局 matching helper / notification hook 未比对。 | 未定 |
| AMFI / MAC / sandbox | 四仓 | 不可比 | sirius `sirius-skip-cs` 非零才清除 `ip_mac_return` 和 `ip_cs_error`；其余检查点及条件未比对。 | 未定 |
| store / UFS 六符号 | enuma / sheng / 其他 | 不可比 | 未定位各实际链接版本及六个实现，版本和等效性未核。 | 未定 |

## 不同实现：显示 provider

* enuma 历史候选 `EnumaLegacyDisplay.cpp:80-115`：等待 IOSurface root；
  分配 `IOPlatformDevice`，设内存范围和服务名，先 attach/start 到 resource，
  必须设 `device_type=display-subsystem` 并挂到 `/arm-io` 的 DT plane；
  再 attach display、probe、start，最后显式对 **display** `registerService()`。
  失败记录 stage/reason 并按已完成步骤清理（同文件 119 行起）。
* sirius `LegacyDisplayProbe.cpp:605-680`：相同设备类和内存范围；
  `offline-legacy-phase=4` 才设置同一属性并挂 DT plane；phase 3 改用 presenter。
  非 presenter 路径先 probe 再 attach，再 start；phase 4 成功保留对象，
  失败按 started/attached 状态 stop/detach；该段没有显式 registerService。
* OPi5 `LegacyDisplayProbe.cpp:836-880` 相同的 phase 结构和 probe-before-attach；
  额外可按 `sheng-fb-gpu=1` 创建挂到 resource 的 handoff presenter。
  `device_type` 是所列三段中显式设置的属性；内存范围和名称另设，
  并非已穷尽各对象继承或其他函数设置的属性。
* attach 与 probe 次序、DT plane 及注册差异可改变 probe 时可见的 provider
  关系和随后服务匹配；不能仅凭类名推定一定匹配或一定不匹配。
  sheng 的 `IOService` 与 `IOPlatformDevice` 的类匹配不同；不能仅凭此
  判定实际匹配结果或当前症状原因。
* 最小区分：对现有已采集材料核对 display 的 probe/start/register 和
  `IOCoreSurfaceRoot` / framebuffer 匹配计数；没有此类材料则缺正向证据。
  不要求设备操作，不把无渲染直接归因于 provider。

## sheng 的两个 commit：裁定

来源均为公开仓 `UniXNU/UniXNU-sheng` 的
`package/LegacyDisplayProbe.cpp`，本地镜像
`nuwa/UniXNU-nuwa/out/sheng-display-reference` 直接 `git show` 核对。
`git branch -a --contains` 的分支是该镜像目前持有的引用，不是历史上所有分支。

| commit | 当前本地镜像中包含它的分支 | 创建类及行号 | 关键调用 |
|---|---|---|---|
| `5ae8b4876a378a5104330a5ae514ec9d6deae373` | `origin/archive/pre-message-format-20261117/main` 等归档及功能分支 | `new IOService`，666 | resource 上 attach/start 683；phase 4 的 DT 属性与挂接 688–695；display probe/attach/start 705–707 |
| `c8f92b208068eeaa4cd2b0f592671f04ee70076e` | `main`、`origin/main`、`origin/fix/enable-touch-reference-tracking` | `new IOService`，668 | resource 上 attach/start 685；DT 690–697；display probe/attach/start 707–709 |

两段均给 nub 设内存范围和服务名、按 phase 选择 presenter 或 display；
所列两份文件均无显式 `registerService()` 调用，不能据此推断原版
display 的 `start()` 内部是否注册。失败后依已完成步骤 stop/detach。
两版本之间对该文件的 diff 仅添加 sleep probe 声明和调用，后者行号整体偏移。
`5ae8b487` 的 663–707 引文正确；**上一轮 B 将另一历史参考文件
`out/gop-cpu-consumer-20261114-r1/reference/LegacyDisplayProbe.cpp:1092`
误归给 `c8f92b20`，这一归属错误**，不是两个指定 commit 类不同。

历史变更 `0ebf192adac51ad951c3afb7b375fd8c6c5930b4` 的该文件 diff
明确从 `IOPlatformDevice` 改为 `IOService`，而非相反。其相邻注释给出的
动机是 `IOPlatformDevice` 的 `compareName` 期待 platform expert 而非
resource service 作为 provider；提交标题是宽泛的 display binding / telemetry，
不能仅据此断言某个设备症状已被修复。
enuma 历史候选与 **改动前的旧实现**类相同，与上述两个 sheng commit 不同；
enuma 还在 display attach 后 probe 并显式注册，不能把旧版类相同视为等效。
该比较不证明当前运行包已接入该候选或实际 matching 结果。

## 待补

仍需完成七项的逐 hunk、六符号版本比对及各子类完整方法表。
现有材料不足以排序哪一项最可能解释 backboardd 未打开 IOKit 或无渲染。
