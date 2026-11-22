# pipa iPadOS 17 参考调查

`self-checked`，离线源码与上游自述；未访问设备、未构建、未独立复核上游运行结果。

## 版本与证据

浅克隆 `https://github.com/xVanTuring/UniXNU-pipa`，HEAD
`cdb3d62771e31d48d832853ee0c90964346d78da`；`git ls-remote --heads`
仅有 main。GitHub commits API 提供浅克隆之外的历史：`1f426c04`
迁移组件命名，`07e13712` 记录 GPU 性能与页面操作，`cdb3d627`
更新 AdrenoMetal。当前 main 的 `board.toml:12-20,281` 明确
iPad7,1 / 17.7.11 / 21H461 / OS UUID `04769D26-2CA0-4825-B443-E2E5F88300F2`；
上述历史提交属于当前主线，但未逐一检查各历史版本 donor，不能断言全部历史均为 17。
仓库无 `docs/` 或 `porting.toml`，以下为 README 与 board 原文摘录。

| 级别 | 原文和位置 |
|---|---|
| 上游报告实测像素 | `README.md:66`: “iPadOS 17.7.11 runs to the home screen … from the UFS root, with the display on the firmware frame buffer.” |
| 上游报告实测像素 | `README.md:66`: “Without the plugin's publish file the UI renders on the CPU as before.” |
| 上游报告实测像素和服务 | `README.md:86`: “with the publish file backboardd renders the lock screen through Metal: the GPU's first copy to the scanout reads back equal, and the kernel's frame buffer sample is the same as the CPU-rendered lock screen's (13 of 1536 points lit, the same sum).” |
| 上游报告实测像素 | `README.md:87`: “Such rounds (2026-10-24) unlock and turn pages with every frame copied to the scanout by the GPU (1257 copies and more, no failure).” |
| 上游报告实测像素 | `README.md:88`: “the user's photo” 和 “with `sysmem,nocb` the corners are right (the user saw it).” |
| 上游报告实测服务 | `board.toml:225`: “launchd at +1 s, SpringBoard at +50 s, its first crash at +94 s.” |
| 上游报告实测服务 | `README.md:86`: “the Metal bridge's self-test and frontend checks pass in SpringBoard” |
| 上游报告失败 | `board.toml:202`: “SpringBoard traps on "failed to find the main CADisplay" (pipa, 2026-10-23: 16 times in 420 s).” |
| 推断/配置意图，非运行证据 | `board.toml:199-202`: “IOMobileGraphicsFamily loaded from bsd_init, NativeLegacyDisplay on the firmware frame buffer as the system display (phase 4), CPU presentation” |

上游声称的 backboardd 绘制锁屏及读回是**间接支持**其使用显示 IOKit；
未找到带 PID、`IOServiceOpen`/`newUserClient` 成功及返回值的直接日志，
所以“backboardd 打开 IOKit 的直接证据”为**无**。不可将路径推断冒充调用跟踪。
这些是上游作者的实机报告，并非本项目独立验收；`README.md:89` 同时报告
约 20 次中 2 次 render server 停止提交，非稳定性证明。

## 显示链

`README.md:75` 指向 tb128fu 系列 `drivers/GopFramebuffer` 和
`package/LegacyDisplayProbe.cpp`；子模块固定
`xVanTuring/GopFramebuffer@14c7dffb09703e5749bb89af2fdd33ebaf8aa659`
（源码标注 BSD-2-Clause-Patent）。它不是只有 GPU handoff：
`board.toml:199-218,262-267` 同时配置 CPU presentation 与可选 GPU handoff。

| 步骤 | pipa | enuma |
|---|---|---|
| 创建与 parent | `LegacyDisplayProbe.cpp:579-600` 加载 IOSurface、取 PE_Video；`new IOPlatformDevice`，GOP 内存描述符，parent `getResourceService`，init→attach→start | `out/enuma-gop-legacy-20261114-r2/package/EnumaLegacyDisplay.cpp:63-92` 同类 IOPlatformDevice、resource parent、GOP memory、init→attach→start |
| DT | `:602-612` phase 4 把 nub 以 display-subsystem 接到 DT `/arm-io` | 封存源码 `:95-105` 同样设置 display-subsystem 并接入 `/arm-io`，DT 名称不同 |
| display | `:622-625` **probe→attach→start**；`NativeLegacyDisplay` 继承 `IOMobileFramebufferLegacy` | `:105-115` **attach→probe→start→显式 registerService**；display 类由独立工厂提供，不是 nub 的类 |
| register | pipa probe 文件没有在该位置显式 register；子模块 `NativeLegacyDisplay.cpp` 重写 registerService，调用 `IOService::registerService`；不能仅凭此推定 family 内确切调用时序 | 显式调用，见上；两者不能因最终类相似而忽略顺序 |
| CPU 拷贝 | 子模块 `NativeLegacyDisplay.cpp` 的 `kickOnce` 从 swap 的 IOSurface 取得 descriptor、只读 map、copy pixels 到 GOP，屏障后完成 swap；CPU 渲染由用户态 render server 完成，内核负责呈现 | enuma 有 legacy 显示候选，是否接到用户态 swap 须另证 |
| GPU | `LegacyDisplayProbe.cpp:628-637` handoff presenter 接 resource 而非 display nub，避免影响原 display 子节点枚举；README:85-87 描述 Metal→Turnip→GPU copy | r40 未声明 pipa GPU addon 或 A650 bring-up；不可因此断言所有 GPU 源码不存在 |

上游子模块源码引用：
https://github.com/xVanTuring/GopFramebuffer/blob/14c7dffb09703e5749bb89af2fdd33ebaf8aa659/NativeLegacyDisplay.cpp
（`kickOnce`、`registerService`、`startHardware`）；该文件本次通过固定 commit 原始 URL 阅读。

## 配置对照：pipa HEAD 对 enuma r40 包内配置

基准不是工作树默认值：enuma `out/ufs-sm8250-storegeom-20261123-r40/device/board.toml:1-96`；r40 ADT 哈希与 r39 一致（`docs/enuma-r40-storegeom-host-20261123.md:89,96`）。此处是相关字段对照，**不是最终二进制全部继承字段或完整 ADT 解码**。

| 范围 | pipa | enuma r40 |
|---|---|---|
| OS | `board.toml:12-25,76,170-173,281` 同 donor、同 OS UUID、同两份生产 trust cache | 包内 `:52-64,72-75,96` 同 donor 与 UUID，额外 restore trust cache |
| UFS/Data | `:27-37,49-50,186-192` PipaUfs、userdata 首末 `0x293000..0x1d387fa`、root、persist=2 | r40 `:41,72` ShengUfs、root、未设 persist=2；设备主 GPT `[0x290000,0x3b037fa]` 见 r40 device 文档；Data mount-complete 是主控转录，不证明持久 |
| 显示 | `:199-218` legacy phase 4、CPU present、HID、keystore、unit-scale=2 | `:72` 已有 graphics load/phase4/gop/PM/validate/transfer/cpu-present、vsync=60、aks；**不是完全缺 CPU 显示配置** |
| UI 额外项 | `:167,197-198,209,214,216-222` no-auto-dim/plain framebuffer、明确禁用 jobs、unit-scale、key events、HID input/home、fixed vsync | r40 `:72` 无上述同名参数；有 sheng-lite、sheng-touch-hid；配置缺项不等于相应功能缺失，需看构建对象和 Data seed |
| GPU/GMU | `:62-69,243-267` Adreno650、mode12、addon、GPU handoff | r40 组件 `:14-16` 无 Adreno650/GopFramebuffer 规范 ID；不能据此否认隔离链接中的显示实现 |
| CPU/电源 | `:228-242` 八核、IPI、pipa-cpufreq、触摸/按键；`README:81-83` GPU 供电 GMU | `:72` 未列同名 CPU/触摸/GMU 参数；enuma AC 频点、电源票与板级触摸不能照搬 |
| ADT | `:270-289` 5.75 GiB owned、八核、packed seed、iPad identity；`make-pipa-adt.py:125-174` chosen 安全状态、root match、ephemeral、NVRAM、memory-map、sleep-disabled | r40 包内 `:83-96` 2.656 GiB owned、packed seed、iPad identity、同 OS UUID；完整实际 chosen 差集尚未解码；工作树 `board.toml:106-107` sleep-disabled 不证明 r40 每个继承项 |
| 固件与镜像 | `:113-146,153-162` pipaPkg、secureboot=1、192 MiB、16GB 设备的 DRAM span | enuma 包内 `:66-80,98-119` enumaPkg、secureboot=0、160 MiB、8 GiB span；不可互抄内存布局 |
| 组件 | `:43-70,79-111` PipaUfs、Adreno650、Gop legacy、prelink 图形/HID | r40 规范组件有 ArmDTPlatform/ArmCpu/SoftwareAES/XnuPrelink/DarwinBoot/RamBlock/ShengUfs/AppleKeyStoreState；构建对象与 prelink 完整闭包未做逐项差集 |

参数缺失的优先调查项是 pipa 的 HID input/home 和 SpringBoard 依赖链、
`sheng-disable-jobs` 的具体策略及 Data seed 中设置；这些只作为对照线索，
不是建议直接开启或证明造成 enuma backboardd 卡点。
单位 scale 与 fixed-vsync 主要影响已出现的画面和节奏，不应当成打开 IOKit 的已证修复。

## 判断

同 SoC、同 GPU、同 donor、同 OS UUID 使 pipa 优先于 SM8550 sheng 作为
**机制和 iPadOS 17 用户态依赖参照**；其 GopFramebuffer 又源于 tb128fu 系列，
可沿共享 lineage 对比。pipa 的 provider 生命周期和 CPU surface→GOP 拷贝
可研究，现有 enuma 已有对应机制，不应盲目覆盖。
屏幕、触摸、内存、UFS 几何与 owner 策略、时钟/电源/GMU/SMMU
不能按同 SoC 直接移植；驱动初始化和 DMA 改动需专项审查。
下一项先做无设备的 HID/keystore/launchd job 依赖与实际 r40 链接差集，
定位 backboardd 为何未到 IOKit，再决定是否实施。

## launchd、HID、keystore 前置补充

静态对照 pipa `cdb3d62771e31d48d832853ee0c90964346d78da` 与 enuma r40；pipa 子模块未检出，不能据此断言组件内部没有某实现。

1. **launchd**：pipa `board.toml:193-198` 的 `sheng-disable-jobs` 列出 `com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.bluetoothd,com.apple.PerfPowerServices,com.apple.iomfb_fdr_loader`，另有 `sheng-disable-watchdogd=1`。`package/BootWatchdogPolicy.c:17-21,43-49,60-75,81-83,103-111` 生成 `<key>标签</key><true/>`，写 `/private/var/db/com.apple.xpc.launchd/disabled.plist`，创建 `disabled.migrated`；不是修改系统 launchd.plist，也不是白名单。注释称同步 XPC 等待环和无硬件服务反复重启是裁剪缘由。r40 `device/board.toml:72` 同有 watchdogd 开关，无该六项参数；Data 的既存 overrides 与运行时生效情况未核。
2. **HID**：pipa `board.toml:109-110,214-218` 纳入 IOHIDFamily/IOHIDEventDriver，开启 `offline-key-events=1`、`offline-hid-input=1`、`offline-hid-home=1`、`sheng-touch-hid=1`。`package/HidInputProbe.cpp:145-153,163-178` 显式加载两 kext、查 IOHIDResource 并按 home 开关创建设备；`:184-191` 的独立 digitizer 还须 `sheng-touch-split=1`，不是默认独立设备；`:113-127` 记录 digitizer 分类属性。`scripts/make-pipa-adt.py:125-155` 的所查生成部分没有 digitizer 节点，未穷举最终 ADT。r40 `board.toml:72` 有 `sheng-touch-hid=1`，无 input/home 两参数；运行时 HID 及对应组件门控尚未完整核对。
3. **keystore**：pipa `board.toml:200-202,214-215` 声称 keybag 依赖 keystore，开启 `offline-key-events=1`、`sheng-aks=1`。`package/KeyStoreProbe.cpp:21-43,76-107,125-133` 的 stand-in 和可选原厂 AppleSEPKeyStore 是不同路径；通知服务有 ephemeral-storage 条件，不能仅凭开关断言成功。`scripts/make-pipa-adt.py:80-81,99-101,135-139` 生成配对软件 identity，注释称否则 `gethostuuid()` 会阻塞；`scripts/kernel-round.sh:64` 提供本地 seed。主仓未找到 `native_aks_device_id` 定义，子模块未检出，整个构建的实现未知。enuma `package/EnumaKeyStoreProbe.cpp:20-23,26,31-51,54-71` 已有 stand-in，ID 优先取 chosen `unique-chip-id`、回退 `chip-id`；r40 同有 `sheng-aks=1`，不能称其 pipa 独有。r40 运行时 ID 与 keybag 成功未核。
4. **上游原文**：pipa `board.toml:201-202`：“liveactivitiesd's Keybag needs AppleKeyStore, or SpringBoard waits on chronod forever”；“Without it SpringBoard traps on "failed to find the main CADisplay" (pipa, 2026-10-23: 16 times in 420 s).” 此处 it 位于一组显示/keystore/HID 描述之后，不能证明单一开关导致错误。`package/LegacyDisplayProbe.cpp:630-632`：“SpringBoard found no display and crashed with the presenter attached there, registered or not”。`README.md:89`：“The render server stopped committing after its first frames in 2 of about 20 rounds, without a crash and with nothing outstanding on the GPU”。均为上游报告，不是 enuma 实测。

与到桌面相关的**配置级差集**：六项 job 禁用列表、HID input/home 开关、key-events 开关、`--no-auto-dim` Data seed 设置；是否缺对应运行时行为须看实际组件、Data 和观测。`--plain-framebuffer` 与 enuma Data seed 的差集未核。不要把同为 `sheng-aks=1` 或 `sheng-disable-watchdogd=1` 列为独有。

## display 调用顺序与可观测性补充

5. pipa `package/LegacyDisplayProbe.cpp:595,600,609-610,622-624`，phase 4：

```cpp
IOService *parent=IOService::getResourceService();
nubAttached=nub->attach(parent);if(nubAttached)nubStarted=nub->start(parent);
if(displayTreeParent && data && nub->setProperty("device_type",data)) {
    nub->setName("gop-display",gIODTPlane);dtAttached=nub->attachToParent(displayTreeParent,gIODTPlane);
}
SInt32 score=0;native_legacy_probe_match=(phase!=4 || dtAttached) && display->probe(nub,&score)==display;
if(native_legacy_probe_match)attached=display->attach(nub);
if(attached){native_legacy_stage=5;started=display->start(nub);native_legacy_start_result=started;}
```

attach/start 和 DT attachToParent 的接收者是 **nub**；后三行接收者是 **display**，provider 参数是 nub。此文件该路径无显式 display registerService；不能排除 display 或其父类 start 内注册。

6. enuma 留存源码 `out/enuma-gop-legacy-20261114-r2/package/EnumaLegacyDisplay.cpp:76,92-93,103-109,114-115`：

```cpp
IOService *resource = IOService::getResourceService();
if (!(nubAttached = nub->attach(resource)) || !(nubStarted = nub->start(resource))) {
    failure(10); goto finish;
}
nub->setName("enuma-gop-display", gIODTPlane);
if (!(dtAttached = nub->attachToParent(parentDT, gIODTPlane)) ||
    !(displayAttached = displayObject->attach(nub))) { failure(12); goto finish; }
{
    SInt32 score = 0;
    if (displayObject->probe(nub, &score) != displayObject || !displayObject->start(nub)) {
        failure(13); goto finish;
    }
}
displayNub = nub;
displayObject->registerService();
```

nub attach/start 和 DT attach 的接收者均为 nub；display attach/probe/start/registerService 的接收者为 `displayObject`。r40 文档 `docs/enuma-r40-storegeom-host-20261123.md:93-96` 说明与 r39 大部分链接输入相同；`docs/enuma-r35-scale-host-20261123.md:50` 记录旧显示对象哈希，但本次未建立 r35→r40 每代对象哈希链，因此以上是留存候选源码，**不是已证明 r40 实际链接源码**。

7. **是否真的不同：是，按上述两份源码**。nub 均先 attach 再 start；display 则 pipa probe→attach→start，enuma attach→probe→start→显式 register。两边都要求 probe 返回原对象后才 start；enuma attach 失败走 failure 12，probe/start 失败走 failure 13。register 调用点差异不等于最终可见性必然不同：pipa 可能由继承代码注册，须核目标 family 和运行时状态。
8. 若实际链接源码确认相同，需把 display probe 移到 attach 前并调整失败及清理标记，保留 nub 生命周期和 DT 条件；此时 display 尚无 attach 建立的 provider，若 probe 调用 `getProvider()` 可能改变结果，须先读实际 probe 实现。probe 失败不应 detach 未附着对象，start 失败仍须按契约清理；不能推断调整能解决 backboardd 零 open。本轮不实施启动链改动。
9. 可观测：分别记录 display probe 返回指针、score、attach/start 返回、register 前后 registry 名称/类、`IOServiceMatching` 命中和目标服务 open；命中不证明 open 成功。r43 `docs/enuma-r43-matchcnt2-host-20261123.md:8-18,62-74` 的 M/N/O/P/I 分别覆盖匹配查询、通知、open、属性匹配、interest，均为入口计数而非成功计数；全零需同轮身份、时序和全局阳性对照。注册及特定类匹配需额外测量，不能从聚合计数倒推。缺 r40 对象链与运行时对照，优先补证，不建议仅凭 pipa 顺序改动。
