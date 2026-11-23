# sheng iPadOS 17 实现对照：未完成（2026-11-23）

状态：self-checked，静态调查；未构建、未操作设备。**不是补丁闭包或逐 hunk 等效性结论。**

## 首个阻塞：实际应用闭包和桌面构建身份未绑定

`UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e`
的 `board.toml:178-182` 为 21H461 选择 arch、soc、os、device 四个
series；`patches/xnu/series:2-4` 只列 device 的三个条目。这证明的是
配置选择，不证明四个 series 已应用或已经参与一次桌面启动。
同仓 `0c2046b84dbee545e7e3923eb74d7bb1ce020978` 的 README
报告同 donor 到 Home Screen、Settings，且由 Adreno 740 合成；但没有该次
实际构建哈希或补丁应用记录（详见 `sheng-donor-branches-20261123.md:107-113`）。
因此不能把 c8 的选择集合称为那次 UI 的实际应用集合。

enuma `scripts/build-enuma-r49-bp2.py:22-24,39-41,78-79,96` 继承
r46 编译命令、r47 链接对象和源文件及 r48 payload；不是从 series
重新应用的构建。仅按当前 `patches/xnu/series` 列名不能闭合 r49。
需逐对象追溯继承链和当时的应用记录；如果记录不存在，只能标记不可恢复。
旧文件名扫描 `repo-diff-patches-20261123.md` 也明确不是实际应用证明。

## 已证实的局部信息（不是集合差分）

| 范围 | 条目或配置 | 意义 |
|---|---|---|
| sheng c8 iPadOS 17 device series | `zzyd-sheng-audio-addon-mount.patch`、`zzye-sheng-cpu-idle.patch`、`zzyf-sheng-amp.patch` | 分别涉及音频插件挂载、CPU idle 统计、AMP 调度；逐项静态内容见 `sheng-only-patches-analysis-20261123.md:39-47`。不证明仅 sheng 实际应用。 |
| enuma 当前 device series | `enuma-pid1-observer.patch`、`enuma-pmgr-publisher.patch` | 当前配置选择，不足以证明 r49 对应对象来源。 |
| sheng c8 iPadOS 17 | `board.toml:185,189` | 配置含 `fb-gpu=1`；OS UUID 与目标一致。 |
| sheng da9 | `package/LegacyDisplayProbe.cpp:23,506-550` | phase 4 的 GPU handoff 与 display nub 分别初始化；不能据 boot 参数单独证明运行成功。 |
| enuma r44 | `enuma-r44-device-20261123.md` | 报告 `parsed=4 applied=1`；不是 r49 的运行结果。 |

## 尚未完成

缺实际应用记录与完整对象溯源，不能填写“仅 sheng / 仅 enuma / 共有”
的实际集合，也不能判定签名 fast/slow、text-fixup 门禁与逐 hunk 等效性。
sheng 历史 README 报告的 GPU 合成路径是值得优先比较的候选，不证明
它是 enuma 无像素的原因；SM8550 Adreno 740 路径不能直接当作
SM8250-AC 硬件实现照搬。还需逐项比较 provider 生命周期、scanout、
签名和 fixup 的最终源及链接归属，再以已有观测检验可区分性。
