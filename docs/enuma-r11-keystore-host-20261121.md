# enuma r11 — AppleKeyStore 状态探针（2026-11-21）

主机候选；`self-checked`，未部署。唯一目录：
`out/ufs-sm8250-launchd-keystore-20261121-r11/`。

## 适配判断

**晚期注册须走锁序修正路径，不能照抄 PMGR 的手动注册。** 这不是用户态匹配依赖 kext personality：官方 `NativeKeyStoreEvents.cpp:280–315` 中 `AppleKeyStore::start` 自行 `registerService()`，`newUserClient()` 直接分配、初始化并 attach/start `AppleKeyStoreUserClient`。XNU `iokit/Kernel/IOService.cpp:1031–1084,6704–6722` 将服务发布和类匹配分开；一旦注册构造成功，调用者看的是 IORegistry 里的服务类，不是 kext 标识。

PMGR 由 `scripts/build-enuma-platform-power.py:135–155` 去除自动初始化入口并导出单个构造符号，`package/ShengPlatformPower.cpp:82–106` 先装载原版父类，再手动注册；mode 2 在 `:150–166` 注册 provider/nub 并由**内核**匹配 `ApplePMGRNub`，不依赖用户态打开客户端。它比 r11 的位置早（r10 `bsd_init.c:779–780` vs `:924–925,1338–1344`），其已有路径不能证明 IOBSD 发布后的类锁顺序安全。

参考 `UniXNU/docs/zh/drivers/apple-key-store-state.md:3–15`、`docs/zh/porting/platform.md:69–79` 和 `docs/zh/devices/asteroids.md:237`。旧顺序在 `OSMetaClass::postModLoad` 等 kext 锁，同时 IOKit 配置线程持 kext 锁等 class lock。r10 的 native/prelink 中没有 `OSKextRegisterBoardClasses`。

## 移植范围和来源

- `rootstockos/UniXNU-asteroids@6370e66c` 的 `patches/xnu/zzyg-board-class-registration.patch` 和 `package/KeyStoreProbe.cpp`：BSD-2-Clause-Patent（[许可证全文](enuma-r11-keystore-asteroids-license.md)）。没有拷入单独标 MIT 的 `BoardClasses.h`。
- `UniXNU/AppleKeyStoreState@8c70daf814aafdf4a3d35e40dde0322655fd0a83`：BSD-2-Clause-Patent；从 Git blob 直接编译原始 `NativeKeyStoreEvents.cpp`，未改组件源码。组件目录见 `UniXNU@693f5d9c:components.toml:251–271`。

两个单 hunk 都使用 `--fuzz=0`、无 offset，只应用到 r11 临时源：

1. `enuma-r11-board-classes.patch`：`libkern/c++/OSKext.cpp:1715`，`OSKextResetAfterUserspaceReboot` 后新增 helper。顺序为 **`sKextLock` → `preModLoad`/class lock → 构造器 → `postModLoad` → 释放 `sKextLock`**。相对参考补丁改动：即使没有 handle 也调用 `postModLoad(NULL)` 清理，然后返回原本的内存错误。基座 `OSMetaClass.cpp:780–793` 的分配失败返回 NULL 仍持锁；`:824–826,957–977` 处理空 handle 并释放类锁。没有改 `OSMetaClass` 或旧调用方。
2. `enuma-r11-keystore-probe.patch`：`bsd/kern/bsd_init.c:1336`，`IOKitBSDInit()` 成功后、r10 已有的晚期显示 probe 之前调用。`XNU_ENUMA_KEYSTORE=1` 只给此候选的 `bsd_init.o`；该位置早于 launchd exec。板级 probe 复用检查重复类、IOResources provider、类注册、init/attach/start 顺序；不导入 asteroids 的屏幕扩展计数或原版 AppleSEPKeyStore 加载路径。

**唯一新增 boot-arg `sheng-aks=1`**：显式启用 stand-in 用户客户端。`offline-keystore=1` 不加入且与 stand-in 互斥。保留 r10 的预注入 ADT、内核参数其余项、资源以及 Data mount；`/private/var` 仍为 initrd scratch APFS 卷，`/chosen:ephemeral-storage=1`，无持久存储。只能验证当次启动的状态查询，不能证明重启后 keychain 可读。

板级 `native_aks_device_id` 是 C 回调（官方组件 `NativeKeyStoreEvents.cpp:28,103–115`），不是自动读取 ADT、卷 UUID、chip ID 或构建参数。r11 未取得可信板级身份，明确的占位为 **0 字节，无字节写入**；使用组件原有缺身份行为使派生密钥、wrap/unwrap 和 bag UUID 失败关闭，不影响独立的状态查询 selector。组件仍设置自己的通用 `KeyOperationsAvailable` 属性；不要将该属性当作本候选支持封装的证据。

## 自报状态与判读

所有行都在一次探针入口执行期间由 `printf` 输出，非 `kprintf`；类名限定为 52 字符，总行宽小于 80。匹配只在 attach/start 成功后执行，超时是 **1 s 内核时钟**，不声明真实墙钟耗时。`pub 1` 表示 probe 的 init/attach/start 成功，`start` 已调用无返回值的 `registerService()`；是否实际可匹配由下一行独立判定。`match 1` 要求找到的实例就是 r11 刚发布的实例。板级 probe 的失败分支只报告，未添加 panic。

| 格式串 | 源码 / native 和 prelink 中各自的调用点 |
|---|---|
| `enuma-aks: reg %#x\n` | 1 / 2，helper 或前置检查的状态 |
| `enuma-aks: pub %d\n` | 1 / 2，init/attach/start |
| `enuma-aks: match %d %.52s\n` | 1 / 3，类匹配 |
| `enuma-aks: aksid %zu %s\n` | 1 / 1，调用同一板级回调（探针侧被编译器内联为 0），最多格式化前 8 字节；r11 输出 `0 -` |

三组预期样例（不是实机记录）：

| 输出到达 | 判读 / 下一步 |
|---|---|
| `reg <零>`、`pub 1`、`match 1 AppleKeyStore`、`aksid 0 -` | 类已注册、服务可匹配；下一步确认真实用户态 open 与状态 selector，不能据此称 keychain 正常。 |
| `reg <非零>`、`pub 0`、`match 0 -`、`aksid 0 -` | 未注册或拒绝重复类；按状态查 IOResources、同名类和 helper 返回，不追 launchd。 |
| `reg <零>`、`pub 1`、`match 0 -`、`aksid 0 -` | attach/start 返回成功，但 1 秒内未匹配到本实例；查 IOService 注册状态、provider 和匹配进度。`match 0` 若带类名，先核对是否为另一实例。 |

## 主机机械证据

编译/链接/预链接/官方 payload 和 bootimg 都 exit 0。native、prelink 的 `llvm-nm -u` 均无输出，`-m` 中无 `(undefined)`，含 weak。最终两个镜像中要求的每个符号恰好一处定义：

| native 链接归属 | 符号 |
|---|---|
| `OSKext.cpo` | `_OSKextRegisterBoardClasses` `0xFFFFFFF00BE8DDC0` |
| `libAppleKeyStoreState.a(EnumaKeyStoreProbe.o)` | `_enuma_keystore_probe` `0xFFFFFFF00BFE38EC`、`_native_aks_device_id` `0xFFFFFFF00BFE38E4` |
| `libAppleKeyStoreState.a(NativeKeyStoreEvents.late.o)` | AppleKeyStore / AppleKeyStoreUserClient vtable `0xFFFFFFF00B7F7B58` / `0xFFFFFFF00B7F74D8`、分配函数 `0xFFFFFFF00BFE1A90`、初始化函数 `0xFFFFFFF00BFE380C` |

状态组件对象 `__DATA,__mod_init_func` 8 → 0 B，按 enuma PMGR 的方法只将具名初始化函数的 `N_EXT` 位置 1。native/prelink 的初始化段尺寸均不变：`__DATA_CONST` 792 B、`__LASTDATA_CONST` 8 B、`__KLDDATA` 8 B。对象 `BR26` 和最终两个镜像反汇编均确认：启动对象到探针 2 处（`_bsd_init` 内联副本 `0xFFFFFFF00BCE0EDC`、独立 `bsd_autoconf` `0xFFFFFFF00BCE13D8`，是一个源码调用点）；板级对象到注册 helper 1 处，到 `printf` 8 处（4 个源码格式调用，优化器复制控制流）。probe 内没有 `kprintf` 调用；未接到用户态生成后回调。

| 文件 | bytes | SHA-256 |
|---|---:|---|
| `bsd_init.o` | 180016 | `cd54914a7be410887172aedde462d9648f6c7eaebf84fd9c67aca5b8ecfce656` |
| `OSKext.cpo` | 1179088 | `e739162099834ec736410cf615d270923f598d463808aa9397f1ae8a34d80d7e` |
| `EnumaKeyStoreProbe.o` | 141344 | `e7d5910b79926faeab1da4fed6c6a4e2b39aef6ffd57e930c20f98ea0a12018e` |
| `NativeKeyStoreEvents.o` | 276472 | `964f793c0075574b2aeb97bd14f2a06838b4be920e9e86e014139a825694c03f` |
| `NativeKeyStoreEvents.late.o` | 276350 | `0387cee85f7b738092d38ccb6ab03e9b33356f78b1fdf8efb5d916cff2a29867` |
| `libAppleKeyStoreState.a` | 419840 | `78335b9b7f4ee11daa04fbd3240afbb989a9a2aa7f6f22ef1478b065c533b71b` |
| native | 91858112 | `1840995570c14fe0bb00caf183e9b9384423fa70e45e9e998d1516285bff5399` |
| prelink / FAT `kernel.macho` | 124702720 | `42de0fbb24c186399c2a453598dd6eadd315f333a74851e79293a7a12604fd79` |
| FAT ADT | 14048 | `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059` |
| FAT initrd `scratch-data.img` | 1142976 | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` |
| `payload.img` | 167772160 | `80e93cc0973a2d4c534865826ffa3abeeebb494e328e333b5eeb9d55506b8a3f` |
| `boot.img` | 169951232 | `a7350441829bfbaac5886b1aaec04e2b6fb55d72476ba6154603e9b366d1f269` |

**相对 r10**：链接输入替换 `bsd_init.o`、`OSKext.cpo` 并追加一个 force-loaded 归档，其余输入保持旧路径，四个上轮独立对象 `IOKitBSDInit.cpo`、`IOUserClient.cpo`、`EnumaUfsOwnerQuery.o`、`kern_exec.o` 比对相同。prelink 增 16384 B；菜单增 12 B（仅 `sheng-aks=1`）；ADT、initrd、trustcache、FD 和 DTB 不变。payload 五项小计从 125905426 增至 125921822 B；160 MiB FAT 尺寸不变。ADT 和 initrd 是 FAT 中独立成员，不是 boot header 的 ramdisk 各自字段；boot 的 ramdisk 与 FAT 逐字节相同。boot 仍为 2179072 B 头和固件区 + 167772160 B payload，比槽上限少 31375360 B。本地 `delta-vs-r10.json` 列出前后全量哈希；`candidate-manifest.json` 的历史 r4/r5 项只用于重用 r10 断言，本轮 delta 以 `r11_delta` 和 `delta-vs-r10.json` 为准。

## 复跑与未验证项

在同一 WSL 22.04、root、Python 3.11 和固定 r10 输入环境下，依次运行
`python3.11 -B scripts/build-enuma-r11-keystore.py kernel`、
`python3.11 -B scripts/build-enuma-r11-keystore.py package`（先确保 r11 输出位置为空；不动 r10），及从 UniXNU 运行 `python3 -B scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`。
独立 verifier 和 `deep_reviewer` 尚未复核；不得以此次构建证明实际类注册、屏幕可读、用户态 ABI、真实时限或持久 Data。
