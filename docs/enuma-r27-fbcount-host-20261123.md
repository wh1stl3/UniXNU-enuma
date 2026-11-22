# enuma r27：IOKit framebuffer 打开尝试计数

候选：`out/ufs-sm8250-launchd-fbcount-20261123-r27/`。相对 r23 只替换 `IOUserClient.cpo` 与 `kern_exec.o`，不修改默认 recipe、patch series 或阶段状态。

## 观测边界

- `iokit/Kernel/IOUserClient.cpp:4445–4447`（候选源码）的 `is_io_service_open_extended()` 在参数、MACF 和 properties 检查之后、调用五参数虚函数 `service->newUserClient(…, propertiesDict, &client)` 之前计数。该点由 `osfmk/device/device.defs` 中的 `io_service_open_extended` MIG 请求进入。五参数基类实现可进入 DriverKit 或派发到四参数 override，再尝试属性驱动的 user client 创建；另有 `OSSharedPtr` 包装。基类打点会漏掉对应 override，两个重载都打点则可对一次请求重复计数。选虚派发前的共同用户态入口，不受目标 override 影响；不会计到绕过该入口的内核直接调用，也不会计到此前被检查拒绝的请求。
- 从服务元类向上沿 `getSuperClass()` 精确比较 `IOMobileFramebufferLegacy`、`IOMobileFramebuffer`、`IOFramebuffer`。冻结归档的 `NativeLegacyDisplay` 明确登记 `IOMobileFramebufferLegacy` 为父类，因此不会因实例类名不以 framebuffer 开头而漏计。每次走到 dispatch 仅付出遍历短继承链、每级最多三次字符串比较，不分配、不查全局符号表，也不新引用显示元类定义。
- `fb_client` 是所有调用者合计的**入口计数，不等于成功，不分调用者统计**。`last_comm` 是从 `current_proc()->p_comm` 保存的最后一份进程短名，不是 PID、调用者清单或成功证据。并发下按原子短名发布顺序定义「最后」；总数与整名分别原子读写，两者不是同一事务快照。打开路径不印日志、不改变返回值、不添加 panic。
- 复用本仓 r25 census 的 XNU `thread_call` 模式（`UniXNU-enuma@f27a68879eb8cdd5aa7987e57adf9418ad06361f`，`package/EnumaProcessCensus.inc`，BSD-2-Clause-Patent）：`bsd/kern/kern_exec.c:2129` 的 PID 1 `launchd` 成功 exec 路径一次性挂起 `THREAD_CALL_OPTIONS_ONCE`，首报 30 XNU 秒后，每次以回调起始时刻算下个 30 秒 deadline，最多 20 次，末次释放；不是墙钟 30 秒保证。三行分别打印，可能夹入别的日志。
- **本版不测 swap。** 通用 IOSurface 操作不能区分共享表面创建/使用和冻结 legacy framebuffer 的 swap/scanout；若要用通用 external method 路径作替代，必须先证明类、selector 和实际调用链绑定，再区分方法请求、提交和显示，r27 没有把它当作替代计数。
- `r26-late-link-failed/logs/link.log` 的首个未解析符号为 `__GLOBAL__sub_I_NativeLegacyDisplay.cpp`，来自归档 `EnumaLegacyDisplay.o` 的 `_native_legacy_display_probe` 对 late init 的引用。r27 不重编、转写或重归档任何显示单元，沿用 r23 链接参数的原始 `-force_load` 归档。

```text
enuma-fb: begin
enuma-fb: fb_client=<n> last_comm=<短名或->
enuma-fb: end
```

| 观察 | 判读 |
|---|---|
| 一组完整 dump 中 `fb_client=0 last_comm=-` | 截至该次采样，未统计到匹配服务的派发入口；不排除前置拒绝或绕过此入口的路径。 |
| `fb_client>0` 或两组之间上升 | 至少一次或新增匹配服务的打开尝试；不证明 open 成功、swap 或像素输出。 |
| `last_comm=backboardd` | 最近发布的探针短名为该名字；不能把累计计数分配给 `backboardd`。 |
| 未见完整 dump | 不能推断计数为零；未区分未到 arm、未到 deadline、日志缺失及 20 次采样已完。 |

## 主机复跑

```sh
/home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r27-fbcount.py \
  --out "$PWD/out/ufs-sm8250-launchd-fbcount-20261123-r27-verify" \
  --dtb /root/enuma-step10/inputs/enuma.dtb
```

从 UniXNU 基座目录复跑记录检查：`python3 -B scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`（15 个 area，exit 0）。

## 机械证据（self-checked）

最终构建、native link、prelink 和打包 exit 0；`logs/link.log` 末尾只有以下三条（第二行以 `…` 缩写路径）：

```text
clang: warning: argument unused during compilation: '-mllvm -disable-atexit-based-global-dtor-lowering' [-Wunused-command-line-argument]
ld: warning: directory not found for option '-L…/.cache/fakeroot/usr/local/lib/kernel/platform'
ld: warning: directory not found for option '-F/System/Library/Frameworks/'
```

`boot.img` 已生成。以下 SHA-256 与逐输入核对见候选 `candidate-manifest.json`。1,004 个其余 filelist 项沿用 r23 原路径及哈希；含直接输入和归档共 1,024 个复用项。r23 目录 170 个文件构建前后哈希不变。

| 文件 | r23 SHA-256 | r27 SHA-256 | r27 bytes / Δ |
|---|---|---|---:|
| `IOUserClient.cpo` | `da268498fdd2d14b9b105525bcbf07de09be436a94288d11c32fecb780fbdf7a` | `a6609c5ec0aff6d95d86903f99c8630ec755c51d9c4801ed23c80dd533d9f2e5` | 703320 / +1616 |
| `kern_exec.o` | `304bc5c75a2045082b537db57e5b154631e8ea4a7a9610fd65827da4b70f3ff2` | `bd9f1c0d677f79c41aecb2e5cbdfccc617473858d470e590a4da8b4d8e7f1508` | 485992 / +5280 |
| `native.macho` | `306b71f131c9814ea97e5daac7055546f1fc03327d8647ad8bb7426d8fe1f1a9` | `b57f64a51c7d42c68c75967791deed0a776e34183b4688c3cf493af8a4396c6a` | 91889048 / +776 |
| `prelink.macho` | `edbb9422c9ae53f486aa540482aaa5f9b0b2489cc7428abfbbcfc76543ca1062` | `ca55d0e3ae20a2f520ca61f1547d00ba26c6a1f2a5f38fe8de7df795ba01dc81` | 124731392 / 0 |
| `payload.img` | `72723451bd753ab40ad4ab999b68046addf7fbc8b495ff8be9da22ca2b8f3dba` | `7d4504e5a98dfb03c302e17396528744bc397ac25e8a2082e7e608850680e6fd` | 167772160 / 0 |
| `boot.img` | `f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b` | `12daec0b116134fcbfd7e8a4d90067e4ab57f9d77421397855094ba03cf7627f` | 169951232 / 0 |

- 原归档 `libEnumaGopLegacy.a` 598792 B，SHA-256 `c88510ae599cd678d2b0f83a98034d61a5e5e167e05295cb9c58085672cbb1b5`。两镜像均有一个非调试的外部定义 `__GLOBAL__sub_I_NativeLegacyDisplay.cpp`（`0xfffffff00bfe0c74`），native map 归属 `[1038] NativeLegacyDisplay.late.o`，均无未定义符号，含 weak。prelink 组件、codeless 组件和原始 executable 哈希不变。
- 两镜像的三条日志格式各 1 份；open dispatch → record 1，exec → arm 1，首次排程 1、重排程 1、释放 1、`printf` 3；原 watchdog 后 HID 启动调用仍为 1。
- r23 payload 仅替换 `Payloads/kernel.macho`，回读与 prelink 一致。FAT 目录结构、`unixnu.toml` 和 boot args 原样；FD、Android DTB 与 r23 pin 相同。boot 偏移 2179072 起为新 payload，前缀只变 header ID。

| 保留的 FAT 成员 | bytes | r23 = r27 SHA-256 |
|---|---:|---|
| ADT `Payloads/kernel.macho.adt` | 14088 | `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5` |
| initrd `Payloads/scratch-data.img` | 1142976 | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` |
| trustcache `Payloads/kernel.macho.trustcache` | 61356 | `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` |
| `unixnu.toml` | 804 | `272e2ed556a51d5706f60fcc5daa33c045fcd5d99f03d71cd1b88138d101afee` |

ADT 保留 `darwinboot-memory-size=0xaa000000`、`sleep-disabled=1`。构建前后 UniXNU 基座 HEAD 同为 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。

未上机；运行时打点与定时输出、打开结果、swap、scanout、用户态稳定性及持久化均未验证。不提升阶段。
