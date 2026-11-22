# enuma r26：显示使用计数

候选：`out/ufs-sm8250-launchd-fbcount-20261122-r26/`。r26 从 r23 重放，不叠加 r25 的进程 census；保留 r23 的 exec/exit 记录、显示参数、HID、keystore、AMFI 与 watchdog/lite。不接入默认 recipe 或 series。

## 三个计数点

以下行号相对于候选 `source/display/NativeLegacyDisplay.cpp`：

| 输出 | 行号及入口 | 含义 |
|---|---|---|
| `start` | `:477` `NativeLegacyDisplay::startDisplay` | 在板级子类调用原版 `IOMobileFramebufferLegacy::start` 前记录；原版为二进制，未插桩。计调用，不计成功。 |
| `userclient` | `:834` `NativeLegacyDisplay::newUserClient` | 进入板级 override 时记录，覆盖打到该 framebuffer 的打开请求，含被拒绝的请求。 |
| `swap` | `:761` `NativeLegacyDisplay::validateSwap` | 记录到达板级校验的提交，包括被拒绝的提交。不选 `kickSwapQueue`，因为注册 vsync 也会调用它；`native_legacy_prepare_scanout` 更晚，同一请求在不同分支可多次调用。 |

三个探针不改参数、返回值、队列或像素处理。只在周期回调打印：

```text
enuma-fb: begin
enuma-fb: start=%llu userclient=%llu swap=%llu last_comm=%s
enuma-fb: end
```

`last_comm` 取最后发布名字的探针所在上下文的 `p_comm`（最多 16 字节，内核上下文或空名为 `-`）。它不是异步 workloop 上原始提交者的身份。计数为 64 位原子加，名字为 128 位原子读写，不会读到撕裂的名字；四项不是事务快照，并发时名字可来自另一条计数事件。只根据同一完整 `begin`/`end` 组读数；背景日志可以穿插。

调度复用本仓 r25（`f27a68879eb8cdd5aa7987e57adf9418ad06361f`，BSD-2-Clause-Patent）的 `THREAD_CALL_OPTIONS_ONCE` 模式：在 `source/bsd/kern/kern_exec.c:2129` 的 PID 1 `launchd` 成功 exec 后 30 秒（XNU absolute time）首次输出，每次回调以本次进入时刻计算下一次 deadline，至多 20 次；然后停止记录并释放 callout。每批只三行，不缩短至 15 秒。保留 GOP r5 已封存的 CPU-only 路径和 late-init 处理（UniXNU `drivers/GopFramebuffer` `e47c1b8de169cd2bd0b885c7d85e433010e3cdf2`，BSD-2-Clause-Patent，见 `out/enuma-gop-production-20261114-r5/display/result.json`）。

## 判读

| 观察值 | 能得出的结论 |
|---|---|
| `userclient=0` | 截至该快照，无打开请求到达该板级 framebuffer；不排除发现或打开请求在到达之前就失败。 |
| `userclient>0 swap=0` | 有进程试开该 framebuffer，但没有呈现请求到达板级校验；打开是否成功未计。 |
| `swap>0` | 已有呈现请求到达板级校验；若仍无像素，方向改为查提交结果、校验和后续 scanout，而不是「没人提交」。不表示呈现成功。 |

`last_comm=backboardd` 或 `SpringBoard` 是该调用上下文的正向证据；单一末次值不能证明其他进程从未调用，也不能把该名字绑定到累计计数中的每一次事件。

## 主机机械证据（`self-checked`）

WSL Ubuntu-22.04 root，设备仓根目录执行；复跑可用 `--out` 指定同一 `out/` 下尚不存在的新目录：

```sh
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r26-fbcount.py \
  --dtb /root/enuma-step10/inputs/enuma.dtb
```

最终构建 exit 0，基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241` 前后不变。`candidate-manifest.json` 记录全部 SHA-256，`logs/` 保留编译、链接、反汇编证据。

| 文件 | r23 SHA-256 | r26 SHA-256 | r26 bytes / delta |
|---|---|---|---:|
| `kern_exec.o` | `304bc5c75a2045082b537db57e5b154631e8ea4a7a9610fd65827da4b70f3ff2` | `b78ba80cbacf7cb2b723ff7c8389528dd9f26ed490de6f7b45d651da2dafc801` | 488768 / +8056 |
| `NativeLegacyDisplay.late.o` | `9b144368d4b11a79c09b09a3b4fa5d1620f89b8ca54a75c5e5e4bbab0f33b05e` | `1dc8ebfc30afc18c8ec80acc81dac7b0cdac78257225967221f5ffcbe25980c1` | 348522 / +351 |
| `libEnumaGopLegacy.a` | `c88510ae599cd678d2b0f83a98034d61a5e5e167e05295cb9c58085672cbb1b5` | `73c5a2bf86b82a449bf79fed5623501580514b799c435ee86012498ee80875c1` | 599144 / +352 |
| `native.macho` | `306b71f131c9814ea97e5daac7055546f1fc03327d8647ad8bb7426d8fe1f1a9` | `9738e8b30d3b9ab4456b76e6c84be5316b1690775fb85868d02459a3287b86e9` | 91889376 / +1104 |
| `prelink.macho` | `edbb9422c9ae53f486aa540482aaa5f9b0b2489cc7428abfbbcfc76543ca1062` | `3552500b69a268357f083ce93871b0a761c4491cf6c0c83eb611ac8e03711884` | 124731392 / 0 |
| `payload.img` | `72723451bd753ab40ad4ab999b68046addf7fbc8b495ff8be9da22ca2b8f3dba` | `91675ca1757ca762a3f8fb92785a2523ef593c027678b2083ce883e849a0fb77` | 167772160 / 0 |
| `boot.img` | `f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b` | `a60d634bb92e9be03af29df71d09634a543f924c9b27281a299d33a2b139bd92` | 169951232 / 0 |

- 1,005 个 filelist 条目保持原路径和哈希；含直接链接输入和强制加载归档在内，复用 1,024 项。显示归档仅替换 `NativeLegacyDisplay.late.o`；`EnumaLegacyDisplay.o`（`612b2f98bfd89669066b365391159c6bcba89372f4f0208e5321259b34847101`）与 `original-bindings.o`（`3650732909f83fc31951f9dfea24eae435e89004d7a5c391ee2888f11fad5773`）两成员提取字节未变。r23 目录 170 个文件及其外部链接输入构建前后哈希不变。
- native/prelink 各有三个格式串各一份、三个探针各一个调用点、一个 exec→arm 调用点、一个分配点、两个排程点、一个释放点和三个 `printf` 调用点。两份 Mach-O 都无未定义符号（含 weak）；watchdog 后的 HID 调用保持一个；prelink 组件列表、codeless 列表和 donor executable 哈希不变。
- 复用 r23 的 FAT 布局、设备配置和注入后的 ADT；只有 FAT 成员 `Payloads/kernel.macho` 变化，与新 prelink 逐字节匹配。原 ADT `/chosen/darwinboot-memory-size=0xaa000000`、`sleep-disabled=1`。boot 内嵌 payload 在 offset 2179072，前缀仅 header ID 改变；原 FD 和 Android DTB 哈希仍匹配。

| 复用 FAT 成员 | bytes | r23 = r26 SHA-256 |
|---|---:|---|
| ADT `Payloads/kernel.macho.adt` | 14088 | `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5` |
| initrd `Payloads/scratch-data.img` | 1142976 | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` |
| `Payloads/kernel.macho.trustcache` | 61356 | `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` |
| `unixnu.toml`（完整 r23 boot-args） | 804 | `272e2ed556a51d5706f60fcc5daa33c045fcd5d99f03d71cd1b88138d101afee` |

记录检查（在 UniXNU 目录运行 `python3 -B scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`）：15 个 area，exit 0。

实机周期、计数流、进程归属、显示输出与阶段验收均未验证；无设备动作。最终构建未由独立 verifier 复跑。
