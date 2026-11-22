# sheng donor 分支复核（2026-11-23）

状态：self-checked；只读 Git 对象，未操作设备、未构建。

历史提交 `da9fab96aea0b5dcdb3bef730b10397276514dac` 明写 21H461 启动停留 logo；logo 绘制来源未定。但同历史线上更早的 `0c2046b` README 另报告原版 iPadOS 的 Home Screen 和 Settings 已到达及 GPU 合成系统 UI，同提交 board.toml 指定 iPad7,1 / 21H461 / 相同 OS UUID；参见文末详读。该 README 是项目作者汇总，不是该次 logo 卡住的逐次日志。

“只有 macOS 像素证据”也不准确：上游还记录 iPadOS 27 桌面照片，但不能把 27 画面归属到 17。Data UUID 没有找到匹配；OS UUID 是配置，不单独证明每次实测镜像的二进制身份。

## 关键证据（去重）

| 分支 | commit | 文件:行 | 原文摘录 | 类型 |
|---|---|---|---|---|
| sheng/upstream-main-20261111（历史可达） | da9fab96aea0b5dcdb3bef730b10397276514dac | 提交信息（非文件行） | “On 21H461 … boot stays on the logo” | 实测像素描述：启动 logo，非用户态桌面 |
| sheng/upstream-main-20261111（历史可达） | da9fab96aea0b5dcdb3bef730b10397276514dac | board.toml:9-15,199 | “unchanged iPad7,1 iPadOS 17.7.11”; build = “21H461”; root_match_volume_uuid = “04769D26-2CA0-4825-B443-E2E5F88300F2” | donor 配置 |
| sheng/upstream-main-20261111 | 3ad65c973caf8f64e5c5f7093c8ac73bf03b4064 | porting.toml:38；reports/ipados27-touch-frame-gaps.md:23 | “All app icon artwork was missing from the photographed Home Screen and Dock.” | 实测像素：iPadOS 27，非同 donor |
| sheng/upstream-main-20261111 | 3ad65c973caf8f64e5c5f7093c8ac73bf03b4064 | reports/ipados27-startup-repair-2026-11-02.md:51 | “SpringBoard PID 30, backboardd PID 61 … Visual presentation was not verified.” | 实测服务：iPadOS 27，非同 donor |
| sheng/upstream-main-20261111 | 3ad65c973caf8f64e5c5f7093c8ac73bf03b4064 | board.toml:168-184 | “ipados-17.7.11-21H461”; “root_match_volume_uuid” = “04769D26-2CA0-4825-B443-E2E5F88300F2” | donor 配置，非运行证据 |
| sheng/upstream-main-20261111 | 3ad65c973caf8f64e5c5f7093c8ac73bf03b4064 | porting.toml:701 | “The arm64e kernel reaches launchd … then SpringBoard.” | 验收目标（23F84），不是实测 |

共 6 条去重关键命中：像素 2（同 donor logo 1、27 照片 1）；服务 1（27）；目标 1；donor 配置 2。不是所有关键词匹配行的总数。

## 分支清单

远端 `git ls-remote --heads --tags https://github.com/UniXNU/UniXNU-sheng` 成功，54 个 heads、无 tag；本地非浅仓。对 54 个远端跟踪分支分别搜索 donor 关键词及显示关键词，全部均有宽泛关键词命中。以下 17 内容表示文档/TOML 中 donor 关键词命中，不代表运行或出画面。上表只是人工核对的关键命中，未逐条判读全部显示关键词命中；远端与本地引用的逐项 SHA 一致性未机械核对，因此不能声明穷尽全部分支的像素记录。

| branch | commit | iPadOS 17 related |
|---|---|---|
| archive/pre-message-format-20261117/fix/cover-input-and-launch-jobs | 28a7498d6790e1584c7eca72987a6ed4fa8acf5c | yes |
| archive/pre-message-format-20261117/fix/graphics-runtime-stderr | 4386827836044c8877a1c1db25576a93c0ca1458 | yes |
| archive/pre-message-format-20261117/main | 13eb383c75ffd216fa97822916adb89448ebc380 | yes |
| docs/local-build-validation | 3469d199c8ab2243a842c814bd9dcd1ab84a38e6 | yes |
| docs/persistent-desktop-image | 8a853506ab58554a98a86b66142de82bd9264ff6 | yes |
| docs/platform-sleep-wake | 8a9d4c67e91626d4487226903aed2ef64c2ce6f5 | yes |
| docs/runtime2507-results | 0b9af21811592c35486b7f8aecae01f3149796c4 | yes |
| docs/sheng-camera-capture | 13eb383c75ffd216fa97822916adb89448ebc380 | yes |
| docs/sheng-desktop-build | 4d9dcff412af08913e7fd221423d623ec2b36d31 | yes |
| docs/sheng-lab-ownership | 5ae8b4876a378a5104330a5ae514ec9d6deae373 | yes |
| docs/sheng-touch-reference-tracking | 7f269ce619b38706e07f7ff863b1a3babdb0f727 | yes |
| docs/wifi-wake-reconnect | ba6a6c8023725380c9e2fce8b7e5ee4765dec0aa | yes |
| feat/macos | b9223ad4020a669b1e62b11fb46c8fbcbafd9b1d | yes |
| feat/manual-shader-cache-app | 48fbc18c85428f64952cee04d319b8266b8d0c02 | yes |
| feat/novatek-firmware | 6156c8c90e1069144f99132525b0d8b20d0e5c7f | yes |
| feat/platform-sleep-wake | 5d8fedb97a1834db292fdc8f2b09b95c2c9fdb2e | yes |
| feat/quiet-desktop-image | 4d638584fa1fd8959392d386b24a8ff2b545eedf | yes |
| feat/tiling-cost-check | 4e8d27e08ef29d0c24a9d1cbee7bf8517c1e2792 | yes |
| feat/unattended-capture-arguments | 5362ba65d6d8b8d3146f630fdd0ce8b853171c12 | yes |
| fix/boot-transport-main-integration | 22e1f9d315ea8f4f1a4d8dddb3a386e7480beeb4 | yes |
| fix/ci-cache-publish-after-build | d504a8a94833d225ac06029176d026d42994459e | yes |
| fix/cover-input-and-launch-jobs | cedbbb1cade936e70539751b514c5b1d7c024132 | yes |
| fix/cover-lid-and-pointer | 01c2796c96c6e0cd936d1a8255bfd3da18639873 | yes |
| fix/data-menu-main-integration | c20eb68b1a569b4b5f9577e95013e003aeaf0600 | yes |
| fix/enable-touch-reference-tracking | c8f92b208068eeaa4cd2b0f592671f04ee70076e | yes |
| fix/fastboot-load-error-recovery | 19dcbf484c8029194900bc258b36fc5bffa7477d | yes |
| fix/gpu-scheduling-and-metal | 4e6b93c566a56df2e566fe5dbf33b9018c28b704 | yes |
| fix/graphics-priming-override | 275535a47c000375dc5cae0926b6d82a257dd85c | yes |
| fix/graphics-runtime-stderr | 60bcf9ebb4413083e625897ff6667c0873be64af | yes |
| fix/hci-main-integration | f2f5c1590fc723842275f8e6e01a2225f1e7e036 | yes |
| fix/icon-runtime-log-retention | 63354480e52ca4e0e7c93f43d0f6654be7c4f387 | yes |
| fix/internal-storage-selection | e1434cb02ba1b91f674941cdb0ceafb139ec615c | yes |
| fix/isolated-settings-icon-capture | aeeda378f2f224698c5fed29817c925a39a78a97 | yes |
| fix/keyboard-cover-recovery | a30ca291d8d7deead46ed8917d73253ad9d5b743 | yes |
| fix/lab-inline-autologin | dafc149f0a3f18191d075a3ff37e74ec671f92f1 | yes |
| fix/lab-kernel-and-service-controls | d71cd9ad49555777b62430acdb85fabc8c4c01ca | yes |
| fix/macos-lab-core-selection | f940fa725b0943dae98b5b470e08a05523d7ca5f | yes |
| fix/outside-range-main-integration | b8fd9af0660db5dbbe70a6716ac0810d57301995 | yes |
| fix/psci-main-integration | 425f6f4115884a1171cb55c87e153c6ec98254c7 | yes |
| fix/sheng-main-build-parity | 6d885c50661bd3d1b8b385dd15c8cc925ee1e5cf | yes |
| fix/sheng-startup-diagnostics | 66c3cd4fc692a4a4a48867ef0c0ce8dbcdad964f | yes |
| fix/sheng-unattended-desktop | 1e8a33f81b1fce92cfeada5d39532e2f1d2545f2 | yes |
| fix/short-graphics-capture | 3bb1f038079bbd00386796ea82fc3ba9c8b4860d | yes |
| fix/wifi-wake-reconnect | c8f9e6b939c84aa6517aca8f740435fe3d98d846 | yes |
| main | c8f92b208068eeaa4cd2b0f592671f04ee70076e | yes |
| maintenance/conventional-history | c303e21eb9d28c338275fef857192b628cf34f37 | yes |
| merge/qualified-runtime-integration | c1e4bf212724c6b7f8afd7897b1b5f27c0243303 | yes |
| merge/qualified-runtime-stderr | 4c6b9a23a569565e8f75a057559d094945c2fcb4 | yes |
| merge/sheng-sleep-wake | 206171054cd9d5f18767dccc43524cd7ba568001 | yes |
| merge/wifi-wake-reconnect | 6c42e1055ffb3b335fda991190ad221edaa7af3c | yes |
| perf/macos-gpu-pacing | 54e48614b78544e362c52ca25351014a8521a95d | yes |
| rponeawa/macos-memory-diagnostics-run139 | cd73e23f0657c28a6638f165590d04f71ab76419 | yes |
| sheng/upstream-main-20261111 | 3ad65c973caf8f64e5c5f7093c8ac73bf03b4064 | yes |
| validate/runtime-records | bc05635a483d69a6c51cafd44723372b66c941f3 | yes |

## `da9fab9` 详读

### 提交说明原文

`git show da9fab9 --stat`：只改 `board.toml`（+3）与 `package/BootLog.c`（+8），无 docs 文件。`git log -1 --format=full da9fab9` 完整提交说明如下：

```text
commit da9fab96aea0b5dcdb3bef730b10397276514dac
Author: rpone <rponeawa@qq.com>
Commit: Sharky Wang <rponeawa@qq.com>

    fix(package): break the SpringBoard AW initialize deadlock

    On 21H461 SpringBoard's main thread runs +[AWClientPreferences
    initialize] while Siri's SASMyriadController thread runs
    +[AWAttentionAwarenessConfiguration initialize], and each waits for the
    other's class, so the boot stays on the logo. The second initializer only
    calls an empty +[AWClientPreferences initializePreferences]; a text-fixup
    boot argument makes it return at once. The boot log shows how many
    fixups were parsed and applied.
```

`board.toml:190-192` 加入 dyld cache 指令替换参数；`package/BootLog.c` 新增 parsed/applied 计数格式，不是实测输出。提交说明报告 SpringBoard 主线程与 Siri 线程发生初始化死锁：已经进入 XNU 用户态及 SpringBoard 初始化，不是「XNU 未启动」。缺该次原始日志、镜像哈希、fixup 前后运行记录，因此未证明该修改在实机解除死锁。

### 更强的同 donor 显示记录和 logo 边界

先前结论漏查了 `da9fab9~10..da9fab9`。同历史线 `0c2046b84dbee545e7e3923eb74d7bb1ce020978` 的 `README.md:20,52,57` 直接写：“The render server composites the system UI through the Adreno 740”，“The original iPadOS userland runs from the IPSW; the home screen and Settings are reached”，Display 为 ✅。同一提交 `board.toml:9-15,195` 指定 iPad7,1、17.7.11、21H461、OS UUID `04769D26-2CA0-4825-B443-E2E5F88300F2`。这是项目作者对**同 donor 的用户态出画面**的明确汇总，强于 logo 描述；但该文无运行日志、照片、精确构建或实测镜像哈希，donor 关联来自同一提交配置，未独立核实运行时镜像，也不能证明 `da9fab9` 那次死锁启动到了桌面。

另外 `da9fab9:package/GpuPowerProbe.cpp:1552-1554` 注释原文：“int-017 stalled userspace at the logo, int-018 with the probe off reached the desktop”。这是另外的历史运行描述，不是该 commit 死锁修复的后测，也没有在注释中写明两个运行各自的镜像哈希。

**logo 来源无法判定，证据强度低**：死锁说明能定位到用户态，但运行到了 SpringBoard 不表示当前 logo 必由其绘制；画面可能是固件 splash 的遗留，也可能是 XNU 或用户态输出。`board.toml` 的 splash 区只说明为避免 ABL 关闭屏幕而保留区域，并不证明该次 logo 的写入者；`-v`、显示相关参数与预链接清单也都不是该次运行时输出。未见该次截图、显存变更时间线、firmware/XNU 交接日志或 backboardd/IOSurface swap 配对日志。缺这些证据，不应在固件、内核或用户态三者间定性。

此前“sheng 只有 macOS 27.3 像素证据”错误：同 donor iPadOS 17 的 Home Screen/Settings 有历史 README 汇总，iPadOS 27 的照片及 macOS 27.3 的桌面记录分别是其他 donor/另一阶段；它们都不是 `da9fab9` 那次 logo 的来源证据。

### 配置逐项对照

右列为 r40 构建目录中保存的 `out/ufs-sm8250-storegeom-20261123-r40/device/board.toml:5-164`，是该候选输入快照而非对运行时逐项读取；r40 host 记录称 ADT 沿用 r39、只替换 UFS 与 BSD 对象，运行时生效仍须具体日志核对。sheng 全部原始 board 配置见本节末全文。

| 项 | sheng `da9fab9` | enuma r40 | 边界 |
|---|---|---|---|
| 板 / SoC | sheng / SM8550 | enuma / SM8250-AC | 不复制板级硬件值 |
| donor | iPad7,1、17.7.11、21H461、j120ap、同 URL、两 DMG SHA | 同产品、版本、URL 和两 SHA | 配置相同；不等于运行镜像哈希已核 |
| UFS / root | `native-ufs-root=1`，OS/SystemOS，root UUID 04769D26… | 同参数及 UUID，另有 `rd=md0-ramblock` 和 scratch Data | 两板 UFS 策略与数据卷不可混同 |
| kernel / archives | sheng_defconfig；ARM、AES、NativeUfs、Virtio、RamBlock、GPU、GPU bindings、`build-native-legacy-display.py` 等，清单见下方原文 | enuma_defconfig；ArmDTPlatform、ArmCpu、SoftwareAES、RamBlock、ShengUfs、AppleKeyStoreState 等；board 输入未列 legacy display builder | r40 实际链接还包括隔离显示归档；不由 board 清单独自推导 |
| prelink | `IOMobileGraphicsFamily`、`IOSurface`、`IOGPUFamily` 等完整 roots，kernelcache SHA、slide、early init 见下 | r40 board 未逐项列 prelink roots；继承 profile/构建输出 | 不以缺省表断言实际 prelink 缺失 |
| 显示参数 | `offline-legacy-register/gop/pm/validate/transfer/cpu-present=1`、phase=4、unit-scale=2；mobile graphics client/load=1；`sheng-fb-gpu=1`、`sheng-gpu-metal=1`、`sheng-vsync=144` | 同 register/gop/pm/validate/transfer/cpu-present、phase 和 graphics-load；vsync=60；未列 unit-scale、graphics-client、fb-gpu、gpu-metal | 参数存在不证明消费或成功；enuma scale 在 ADT 中另为 2 |
| HID / AKS / 电源 | home/input、`sheng-touch=4`、touch-hid、aks、sheng-pmgr、SMP、cpufreq、GPU power/addon/perf | `sheng-touch-hid=1`、aks、pmgr、sheng-pmgr；上述其余未列 | 驱动与硬件不同，不可照抄 |
| 服务 / 修复 | disable-watchdogd、disable-jobs 列表、SpringBoard/Preferences focus、`text-fixup0` | disable-watchdogd、sheng-lite；未列 text-fixup 或相同焦点列表 | 不证明 enuma 有相同死锁，更不授权二进制补丁 |
| payload / ADT | 192 MiB；firmware loader；owned 0x130000000；packed Data、ipad_identity；8 CPU | 160 MiB；firmware loader；owned 0xaa000000；packed Data、ipad_identity；`vmm-present=1`、`sleep-disabled=1`、`display-scale=2` | Data/身份值及内存布局各板自有 |
| firmware | shengPkg、secureboot=1，splash_region 节点 | enumaPkg、secureboot=0，enuma 专属 diagnostic defines | 两者不能直接比较运行时固件实现 |
| 日志 / trust | `-v serial=3 debug=0x14e boot-progress=2`、两 trust cache | `-v serial=3`，三个 trust cache；boot-progress 未列 | 另核实际生成 payload；不据参数推断输出 |

### 前后显示相关提交

`git log --oneline da9fab9..origin/main -- 'package/*LegacyDisplay*' 'package/*Display*'`，HEAD `c8f92b208068eeaa4cd2b0f592671f04ee70076e`，按输出原序列出全部匹配；是路径匹配，不保证每个提交都专门解决显示问题：

| commit | 提交说明及与显示的关系 |
|---|---|
| 927a458 | sleep/wake；两帧或超时前保持屏幕暗 |
| 9fd662c | VideoToolbox/VPU 解码 |
| 28256b6 | macOS GPU 池等；说明写未上机 |
| 763a74e | macOS 流畅度、8 位 framebuffer 等；说明写未上机 |
| 2e2d9df | macOS 显示 probe、294 dpi、swap 报告 |
| 4aa1bc7 | macOS IOSurface root 名称不同导致 FB Count=0，匹配两种名称 |
| 4d86261 | 删除板级 boot-arg 的 sheng- 前缀 |
| 519889a | 键盘盖；含屏幕键盘相关代码 |
| e7c3697 | iPadOS 27 USB |
| dc01f62 | 蓝牙 UART/电源 |
| 708575f | vsync tick、CPU 和栈采样 |
| 40cc031 | 遥测与 legacy display frame format |
| 04ba6a0 | DPU、swap surfaces、scanout 等日志 |
| 7fe6240 | 合并 audio，解决 LegacyDisplayProbe 冲突 |
| 998c87c | 合并 charging，解决显示构建脚本冲突 |
| 165c5db | 携带触摸、显示及 Safari 诊断 |
| fade3ce | 音频 DSP 就绪 |
| 1bed824 | 电池服务 |
| d381d53 | ADSP 启动与 GLINK |
| 59c2522 | 背光等探针；记录 backlight-control 导致等待 |
| 6dcba7c | 144 Hz、refresh 属性及 vsync 绑定（历史重复提交） |

附近前序 `8a2dd99` 已记录 144 Hz、render server 帧间隔 8–9 ms；它是配置与运行说明，不证明死锁那次 logo 的来源。

### `da9fab9:board.toml` 原文

以下保留该提交完整 board 文件，覆盖全部启动、组件、显示、预链接、固件、载荷和 ADT 配置；不要把任何 sheng 板级地址或参数当作 enuma 授权配置。

`	oml
# Board description of the Xiaomi Pad 6S Pro (sheng, SM8550), read by the unixnu build driver.

[board]
name = "sheng"
soc = "SM8550"
description = "Xiaomi Pad 6S Pro"
kit = "sheng"                      # the package/ of this repository appears as kits/sheng in the build tree

# The target OS image: the unchanged iPad7,1 iPadOS 17.7.11 restore image. Give --ipsw PATH to use a local file; without
# it the remote url is read with range requests, only the members that are needed.
[ipsw]
url = "https://updates.cdn-apple.com/2025SpringFCS/fullrestores/122-77166/DCA6CFE8-90E9-4B92-880D-3DE171798E40/iPad_Pro_HFR_17.7.11_21H461_Restore.ipsw"
product = "iPad7,1"
version = "17.7.11"
build = "21H461"
device_class = "j120ap"
chip_id = 0x8011
board_id = 12
fetch = ["KernelCache", "DeviceTree", "StaticTrustCache", "Cryptex1,SystemTrustCache"]   # the small components

[ipsw.sha256]
"044-76040-038.dmg" = "3f99b859c9728379110b66657c7b15285bcb1925ad8b5726542e2cdcf8b1028d"
"044-76034-038.dmg" = "b4908cde41d23e6bc05e6af51a2c9eeb00cf0f863a6a18b1600c96a3fd70414f"

# The raw image for the userdata partition: the OS and SystemOS disk images of the IPSW behind a manifest.
# first_lba and last_lba are the GPT entry "userdata" of LUN 0, read from the tablet.
[userdata]
first_lba = 0x2f3840
last_lba = 0x3d0abfa
lba_bytes = 4096
windows = [
  { name = "OS", component = "OS" },
  { name = "SystemOS", component = "Cryptex1,SystemOS" },
]

[kernel]
defconfig = "sheng_defconfig"
# Archive builders of the kernel step, in order. Each is a script of the build tree with its arguments. The VerifiedRoot
# and VirtIO verified bundles are not built here; they need the volume policies of the target image.
archives = [
  "build-corecrypto-14.py",
  "build-corecrypto-14.py --namespace",
  "build-arm-driver.py ArmDTPlatform",
  "build-arm-driver.py ArmCpu",
  "build-arm-driver.py NativeAES",
  "build-native-aes-bindings.py",
  "build-arm-driver.py NativeUfs",
  "build-arm-driver.py NativeVirtioBlock",
  "build-arm-driver.py NativeRamBlock",
  "build-native-virtio-bindings.py --component NativeRamBlock --directory build/native-ram-block",
  "build-native-virtio-bindings.py --component NativeVirtioBlock",
  "build-mockfs-fixture.py",
  "build-sheng-platform-power.py",
  "build-boot-progress.py",
  "build-libpthread-kernel.py",
  "build-arm-driver.py NativeAdreno",
  "build-native-adreno-kits.py",
  "build-native-adreno-accelerator.py",
  "build-native-legacy-display.py",
]

[kernel.prelink]
tool = "kits/NativePrelink/emit_prelink.py"
kernel = "build/xnu/ios-obj/DEVELOPMENT_ARM64_BCM2837/mach.development.bcm2837.unstripped.noctf"
kernelcache_sha256 = "f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7"
slide = "-0x1000000"
early_security_init = "com.apple.driver.AppleMobileFileIntegrity=0xfffffff005ab4ae0"
roots = [
  "com.apple.AppleFSCompression.AppleFSCompressionTypeZlib",
  "com.apple.driver.AppleARMPlatform",
  "com.apple.driver.AppleARMWatchdogTimer",
  "com.apple.driver.AppleAudioClockLibs",
  "com.apple.driver.AppleEffaceableStorage",
  "com.apple.driver.AppleIISController",
  "com.apple.driver.AppleM2ScalerCSCDriver",
  "com.apple.driver.AppleMobileFileIntegrity",
  "com.apple.driver.ApplePMGR",
  "com.apple.driver.IODARTFamily",
  "com.apple.filesystems.apfs",
  "com.apple.iokit.CoreAnalyticsFamily",
  "com.apple.iokit.IOAVFamily",
  "com.apple.iokit.IOAudio2Family",
  "com.apple.iokit.IOCECFamily",
  "com.apple.iokit.IOCryptoAcceleratorFamily",
  "com.apple.iokit.IOGPUFamily",
  "com.apple.iokit.IOHDCPFamily",
  "com.apple.iokit.IOMobileGraphicsFamily",
  "com.apple.iokit.IOReportFamily",
  "com.apple.iokit.IOSlowAdaptiveClockingFamily",
  "com.apple.iokit.IOStorageFamily",
  "com.apple.iokit.IOSurface",
  "com.apple.kec.Libm",
  "com.apple.kec.corecrypto",
  "com.apple.kext.AppleMatch",
  "com.apple.kext.CoreTrust",
  "com.apple.security.AppleImage4",
  "com.apple.security.sandbox",
  "com.apple.iokit.IOHIDFamily",
  "com.apple.iokit.IOHIDEventDriver",
]

[firmware]
config = "sheng"                   # Resources/Configs/sheng.toml in the Mu-Silicium checkout (--uefi)
dsc = "Platforms/Xiaomi/shengPkg/sheng.dsc"
fd = "Build/shengPkg/{target}_CLANGPDB/FV/SILICIUM_UEFI.fd"
preflight = ["scripts/check-sheng.py"]
submodules = ["Common/Mu", "Common/Mu_OEM_Sample", "Silicium-ACPI", "Silicon/Silicium/OpensslPkg/Library/OpensslLib/openssl"]
patches = ["Resources/MuPatches/Gic-Spurious.patch"]
packages = [
  "{uefi}",
  "{uefi}/Platforms/Xiaomi",
  "{tree}/package",
  "{tree}/drivers/DarwinBoot",
  "{edk2}",
  "{uefi}/Common/Mu",
  "{uefi}/Common/Mu_OEM_Sample",
  "{uefi}/Silicon/Qualcomm",
  "{uefi}/Silicon/Silicium",
  "{uefi}/Silicium-ACPI",
  "{uefi}/Silicium-ACPI/Platforms/Xiaomi",
  "{uefi}/Silicium-ACPI/Silicon/Qualcomm",
]

[firmware.defines]
ENABLE_SECUREBOOT = "1"
DEVICE_MODEL = "sheng"
MEMORY_PROTECTION = "TRUE"
SHIP_MODE = "FALSE"
BUILDID_STRING = "sheng-research"

# The ramdisk of the boot image: a FAT volume with the UniXNU config, the kernel, its device tree and
# the optional trust cache and Data seed. The loader (DarwinBoot) is part of the firmware volume.
[payload]
volume = "SHENGESP"
size_mib = 192
loader = "firmware"
title = "sheng first boot: source 4K XNU to console"
dram_size = "0x80000000"             # SMEM RAM table observed on the device
skip_setup_tool = "scripts/seed-data-skip-setup.py"   # used by --skip-setup
panic_screen = true                  # patch panic() screen output into the payload copy of the kernel
# The original static/System trust caches, and the owner trust bundle built around them.
trust_cache_sha256 = [
  "7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7",
  "8900d6a93d7a59ce1a872a5c081e559f4240a218f97e12d44d22dda46644d68f",
]
kernel_args = [
  "-v",
  "serial=3",
  "debug=0x14e",
  "kt_fixed_zones=120",
  "offline-legacy-register=1",
  "offline-legacy-gop=1",
  "offline-legacy-unit-scale=2",
  "offline-legacy-pm=1",
  "offline-legacy-validate=1",
  "offline-legacy-transfer=1",
  "offline-legacy-cpu-present=1",
  "offline-hid-home=1",
  "offline-hid-input=1",
  "offline-legacy-phase=4",
  "offline-mobile-graphics-client=1",
  "offline-mobile-graphics-load=1",
  "offline-apfs-load=1",
  "boot-progress=2",
  "-apfs_shared_datavolume",
  "offline-key-events=1",
  "native-ufs-root=1",
  "sheng-pmgr=2",
  "armcpu-diagnostics=1",
  "sheng-disable-watchdogd=1",
  "sheng-disable-jobs=com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.bluetoothd",
  "boot-ui-focus3=Preferences",
  "boot-ui-focus4=SpringBoard",
  "sheng-smp=1",
  "sheng-cpufreq=3",
  "sheng-touch=4",
  "sheng-aks=1",
  "sheng-gpu-power=9",
  "sheng-gpu-metal=1",
  "sheng-fb-gpu=1",
  "sheng-banner=0",
  "sheng-gpu-perf=8",
  "sheng-gpu-addon=1",
  "armcpu-spi-ipi=1",
  "-no_slto_panic",
  "ml-timeout-lock-panic-scale=40",
  "sheng-touch-hid=1",
  "sheng-data-persist=2",
  "sheng-vsync=144",
  # +[AWAttentionAwarenessConfiguration initialize] (21H461) only forces +[AWClientPreferences initialize] and deadlocks
  # SpringBoard startup against it (ABBA between the main thread and Siri's SASMyriadController); it returns at once instead.
  "text-fixup0=dyld_shared_cache_arm64.15,421e8bc,28ad1bb0008544f9,c0035fd6008544f9",
]

[payload.adt]
tool = "scripts/make-sheng-adt.py"
chip_id = "207"
owned_memory_size = "0x130000000"
root_match_volume_uuid = "04769D26-2CA0-4825-B443-E2E5F88300F2"
cpu_regs = "0,0x100,0x200,0x300,0x400,0x500,0x600,0x700"
packed_data_ramdisk = true
ipad_identity = true
unique_chip_id = "required"          # the platform seed is not stored in any repository

# Image parameters come from the Mu-Silicium device config; [bootimg.image] would override them.

# The stock ABL powers the panel off when the device tree has no splash region, so add it.
[[bootimg.dtb_node]]
path = "/reserved-memory/splash_region"
props = [
  { name = "label", type = "s", value = "cont_splash_region" },
  { name = "reg", type = "x", value = ["0x0", "0xb8000000", "0x0", "0x2b00000"] },
]
`
