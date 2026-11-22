# enuma r28 framebuffer 链实机观察（2026-11-22）

`self-checked`：记录主控提供的操作和 `vision` 核读，本次未重复访问设备或录像；阶段不提升。

## 操作与审查

- 2026-11-22 17:31:36 +08:00 刷入 `boot_b`：`Sending 'boot_b' OKAY [4.069s]` / `Writing 'boot_b' OKAY [0.371s]`，exit 0；随后 `reboot` exit 0。claim `.cache/enuma-r28-fbchain-20261123.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-fbcount-20261123-r28/boot.img`，169,951,232 B，SHA-256 `44694629826b0b7e7a8dc5332b8891a013fed892a468f7c46e78012796f8ca0d`。
- 主控提供刷写前 `deep_reviewer` **PASS WITH CONDITIONS**：用 `open=N` 判断表未满；`ret` 只是 override 返回码；`scanout` 计调用次数；`kick`/`swap` 不能区分没人提交与提交被拒。为 deep 审查，非「方案 B、未经 deep_reviewer」；本次未独立复核审查。
- 用户录像 307 s，2 fps 抽取 614 帧，`vision` 按每 10 秒读 31 帧定位完整块；影像不入库。

## 结果

早期块（50 s、80 s）：

```text
enuma-fb: start=1 comm=-
enuma-fb: open=0 comm=-
enuma-fb: refresh=0 kick=0 scanout=0 swap=0（各 comm=-）
open[0..7] 全为 -
```

后期块（110 s 起，多帧一致）：

```text
enuma-fb: start=1 comm=-
enuma-fb: open=2 comm=IOMFB_FDR_Loader
enuma-fb: refresh=0 comm=-
enuma-fb: kick=0 comm=-
enuma-fb: scanout=0 comm=-
enuma-fb: swap=0 comm=-
enuma-fb: open[0]=MobileGestaltHel pid=66 type=0 ret=0
enuma-fb: open[1]=IOMFB_FDR_Loader  pid=56 type=0 ret=0
enuma-fb: open[2..7]=-
```

## 判读边界

- **已观察（该次启动、该观察窗）**：板级 `startDisplay` 入口计数 1；板级 `newUserClient` 计数 2，两条已完成表项分别记录 `MobileGestaltHel`（主控识别为 MobileGestaltHelper，pid 66）与 `IOMFB_FDR_Loader`（pid 56），均 type 0、override `ret=0`。名字为最多 16 字节的调用上下文，不扩大为其他路径的全局调用记录。`open=2 < 8`，表未满。
- **已观察**：`refresh`、`kick`、`scanout`、`swap` 均为 0；它们是各自板级入口或调用次数，不证明模式设置、显示成功或全系统无显示请求。`kick`/`swap` 的 0 不能区分没人提交与请求在到达之前被拒。
- **待证解释**：观察到的两条打开表项没有 backboardd，支持其未到达该板级 `newUserClient` 的观察窗判断；不证明它从未尝试打开 framebuffer 或未进入其他显示初始化路径。SpringBoard 是否等待显示能力、具体原因均未建立。
- **UNKNOWN**：backboardd 之后卡在哪一步或等待哪个服务；MobileGestaltHelper 打开该 framebuffer 的原因；父类内部 mode/owner 行为及最终呈现。

阶段不提升。探针语义和非事务快照限制见 [r28 主机记录](enuma-r28-fbchain-host-20261123.md)。
