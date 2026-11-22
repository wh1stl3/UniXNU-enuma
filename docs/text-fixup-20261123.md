# iPadOS 17 text-fixup 与 enuma r40

状态：self-checked；离线静态分析，未构建、未访问设备。

## 线别边界

仅采用 sheng `da9fab96aea0b5dcdb3bef730b10397276514dac` 的 iPad7,1 / iPadOS 17.7.11 / 21H461 配置，OS UUID 同为 `04769D26-2CA0-4825-B443-E2E5F88300F2`；排除 macOS 27.3。该提交报告 SpringBoard 主线程与 Siri `SASMyriadController` 线程分别初始化 `AWClientPreferences` 和 `AWAttentionAwarenessConfiguration` 时相互等待，停留 logo；缺原始线程栈及修复前后实测。原文和配置引述见 `sheng-donor-branches-20261123.md:83-105,121-125,359-361`。

## 机制及 r40 实际链接

这是 XNU 内核补丁，不是用户态工具。`UniXNU/patches/xnu/native-text-fixup.patch:1-17,71-101` 定义格式 `<文件名>,<十六进制文件偏移>,<原字节hex>,<替换字节hex>`；原/替换同长度，1–16 字节，不能跨页。`profiles/arch/arm64/patches/xnu/series:23` 引用该补丁。

补丁 `:103-144` 早期启动先解析 ADT `/chosen/text-fixups` 的 NUL 分隔表，再解析 `text-fixup0` 至 `text-fixup7`，最多 32 条；有效条数存 `cs_text_fixup_parsed`。`:150-172` 按 vnode 文件名、文件偏移和原字节匹配后 `memcpy`，原子递增 applied，前 16 次打印 `text-fixup: %s+0x%llx (%u bytes) applied`。`:192-202` 的 `vm_page_validate_cs_mapped_slow` 仅在代码签名页验证通过且未 tainted 后、映射前写页并同步指令缓存。范围由表指定文件和偏移，而非符号名；同名文件也受原字节匹配约束。计数为写页次数，并非必然等于唯一配置条数。

sheng `package/BootLog.c`（同提交，[原始文件](https://raw.githubusercontent.com/UniXNU/UniXNU-sheng/da9fab96aea0b5dcdb3bef730b10397276514dac/package/BootLog.c)）weak-import 两计数，parsed 非零时在日志槽输出 `[text fixup] parsed=%u applied=%u`；额外输出依赖日志 writer 启动，格式存在不证明运行时已打印。

enuma r40 `native-link.map:657` 将相关符号归属 `ubc_subr.o`；实际构建树 `.cache/xnu-work/bsd/kern/ubc_subr.c:6087-6098,6134-6206,6213-6230` 有解析与应用实现，`osfmk/vm/vm_fault.c` 有调用。r40 `native.macho` 和 `prelink.macho` ASCII 扫描均命中 `text-fixup` 13 次、`text_fixup` 82 次（含符号名，不是应用次数）及实际应用/错误格式串。r40 `kernel.macho.adt` 也包含四条具体配置；因此能力存在且已编入，设备上是否解析和应用尚未观察。

## 同 donor AW 条目及其他表项

sheng `board.toml:190-192`：

`text-fixup0=dyld_shared_cache_arm64.15,421e8bc,28ad1bb0008544f9,c0035fd6008544f9`

sheng 注释说明：在 cache 文件偏移 `0x421e8bc`，匹配八字节 `28 ad 1b b0 00 85 44 f9`，改为 `c0 03 5f d6 00 85 44 f9`，首条 ARM64 指令变为 `ret`，使 `+[AWAttentionAwarenessConfiguration initialize]` 即时返回；第二条指令字节保持原样，不是强制返回某个数值。函数定位未独立反汇编验证。

**enuma r40 ADT 已包含完全相同的 AW 条目**，不需再加。它也在公共 iPadOS 17 profile `UniXNU/profiles/os/ipados-17.7.11-21H461/profile.toml:40-41`；同表还有 `dyld_shared_cache_arm64.13` 偏移 `1b05bec` 和 `1b05b08` 的两条 4 字节替换，以及 `BTAudioHALPlugin` 偏移 `38bec` 的一条 8 字节替换，具体函数和作用未核实。r40 ADT 字符串扫描确认四条全部存在；同 donor 配置不证明运行镜像相同、目标页命中或修复实际生效。sheng iPadOS 17 其他独有用户态补丁未完成全仓闭包核查，不声称清单穷尽。

## enuma 死锁证据与回退

在 `docs/enuma-r*-device-*.md` 和 `docs/*observation*.md` 现有文字中搜索上述 AW 类名、Myriad 未见命中。`enuma-gop-r5-device-observation.md:70` 的 `Waiting on <dict ... IOMedia ...>` 是根设备匹配等待，不是 AW 锁；`ufs-sm8250-startroot-mode0-observation.md:77` 的 `Still waiting for root device` 亦然。`enuma-r30-device-20261123.md:40,43` 记录 `bb=0` 和其他调用 `all=70`，不足以证明 backboardd 已卡住或其具体等待对象。

用户提供 SpringBoard IPC 116/86 与 backboardd 未进入指定 IOKit 插桩路径的观察：进程级累计 IPC 可以由其他线程发生，也可能发生在主线程阻塞之前，因此不排除两个初始化线程死锁；这些计数无线程归属或等待链，不能证明死锁，也不能证明 backboardd 等待由它造成。机制上相容，具体实例无证据。

若真存在同一死锁而修复未应用，sheng 报告的后果是 SpringBoard 启动停在 logo；enuma 后果未证实。不要重复添加相同条目：先查目标页是否应用以及 SpringBoard 线程堆栈/等待链。错误偏移或目标函数会改变匹配页的用户态行为；原字节校验不证明语义正确。回退应恢复不含该条目的独立配置并重新生成载荷，保留其他三条；具体生效和操作需另行授权及验证，不能把仅移除 boot-arg 当作移除已存在的 ADT 条目。

## 应用记录与 donor 原字节复核

### 历史文字和媒体

对 `docs/` 内文件名含 `device`、`observation` 或 `transcri` 的文件及 README 搜索 `fixup`、`applied`、`解析`、`应用` 和其组合。与关键词有关的设备记录原文：

* `enuma-r14-device-20261122.md:35`：「传统 Caches 路径的 `dyld_shared_cache_arm64` 与 `.symbols` 可解析为 `0 REG`」；该路径检查不是 `.15` 的打开或应用日志。
* `enuma-r14-device-20261122.md:38`：「`osfmk/vm/vm_dyld_pager.c` 的 `fixup_page()` 按 `PAGE_SIZE` 索引……既不证明运行时走到 fixup」；这里是另一种 dyld pager fixup，非本补丁应用行。
* `enuma-r15-device-20261122.md:38`：「`<fixup-mobile-tap>         Doing boot task → /private/var/mobile/tmp already exists, skipping`」；这是 launchd boot task，不是签名文本替换。
* `enuma-r40-device-20261123.md:28`：「既有启动路径读入并解析的主 GPT 快照报告 `userdata` ...」；这是 GPT 解析。
* `enuma-r9-device-20261121.md:34,37` 的「CommCenter plist 在 exec 前视图解析为 `0 REG`」「路径解析为 REG 不证明文件内容」是文件路径检查；`ufs-launchd-data-20261119-observation.md:297,303,344` 的「解析失败」「目录项」「没有解析」分别讨论 libSystem、目录项和路径表，不是 text-fixup。
* `README.md:226`：「OS profile 补丁 ... `text_fixups` ... 清点」是待办配置说明，不是设备日志。

其余检索文档中，`repo-diff-adt-bootargs-20261123.md:39,214,219,225` 是 ADT 表和未观察应用结果；`sheng-donor-branches-20261123.md:96-102,359-361` 是 sheng 提交描述及参数。**历史转录中未见 `text-fixup: dyld_shared_cache_arm64.15+0x421e8bc (8 bytes) applied` 或实际 parsed/applied 数字。**可能未打印、打印但未转录、或照片未拍到；没有完整启动串口日志，不能区分。

`../media/微信图片_20261122212227_509_25.jpg` 仍在，文件名时间为 11-22 21:22:27，未找到与该文件名直接绑定的轮次，不能猜测；可供后续 vision 核读。其他保留影像包括 `.cache/media/stage6-ramblock-20261109T232127718/微信图片_20261109232224_361_25.jpg`（stage6 轮次，非 r40），以及 `.cache/media/stage5-20261109T185128/微信视频2026-11-09_185314_663.mp4`（stage5）。没有据此声称影像包含目标行；禁止访问的 21r–24r 旧媒体未读取。

### 匹配失败与实际原字节

`native-text-fixup.patch:156-165`：不含目标偏移的页、vnode 名不同/为空、原字节不符均直接 `continue`，**静默**。`:196-200`：页验证不是 `VMP_CS_ALL_TRUE` 或 tainted 不是 `VMP_CS_ALL_FALSE` 时不调用修补，补丁本身不打印原因；不排除其他签名代码另行打印。条目格式错误或表满则分别按 `:115-123,136-140` 打印，空参数静默。

使用本机 `sgan81/apfs-fuse@66b86bd525e8cb90f9012543be89b1f092b75cf3` 将 `out/userdata-clean-20261112/044-76034-038.dmg` 以 `-o ro` 只读挂载，`find` 命中卷内 `root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.15`（104,628,224 字节），随后 `od -An -tx1 -j 69331132 -N 8 <文件>` 结果为：

```text
28 ad 1b b0 00 85 44 f9
```

`69331132 = 0x421e8bc`。该文件 basename 与 r40 ADT 的目标完全一致，八字节与表项完全一致；只读挂载后已卸载。这是本地 SystemOS 镜像文件的确定结果，不证明运行时已映射该文件、设备上镜像完全一致或代码签名页校验成功。镜像和 donor 关联见 `ufs-launchd-data-20261119-observation.md:318`，仍不是设备实际文件回读。

### 后果和最小验证

未命中并不必然发生死锁：死锁还需要相关初始化路径、时序及线程等待成立，enuma 尚无等待链证据。**最小正向证据**是在授权的后续运行日志中捕获带精确文件名、偏移和长度的 `text-fixup: ... applied` 行；只有首次 16 次页写会打印，丢行或超过上限时无此行不证明没命中。现有内核每次成功打印并非 parsed/applied 总计行；sheng `BootLog.c` 的汇总输出依赖其 writer，不能假设 enuma 带有相同 writer。

即使有全局 parsed/applied 总数，也只能说明总解析条数及总页写次数；其他三条、重复页写均会影响总数，无法单独证明 AW 条目命中。`parsed=0` 和 `parsed>0, applied=0` 在可靠且同次的计数捕获下可分别区分全表未解析及有条目解析但没有任何页写；不能据此确定具体条目被解析、为何未命中或是否后来才命中。要诊断静默失败原因，需有同次、针对 AW 条目的额外观测；具体实现及设备运行须另行授权。
