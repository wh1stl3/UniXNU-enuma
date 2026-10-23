# enuma 系统卷、内核与 iPadOS 用户态预研

日期：2026-10-23。范围：离线源码审查与后续路线，不启动设备、不生成系统镜像、不修改分区或内存配置。当前屏幕诊断和晚间三候选保持。下文“系统”专指既定 iPadOS 17.7.11/21H461；不切换为 nuwa 的 iOS16 路线。

## 结论与三层卷

优先保持官方链路：UEFI/菜单 → FAT 载荷发现 → DarwinBoot → 4K XNU/基础平台 → 原生存储 → APFS 根卷 → launchd → 图形用户态。先进入 XNU 不需要把完整 iPadOS 系统预先塞进 RAM；看到菜单也不代表已经发现载荷或挂载 APFS。

| 层 | 内容与消费者 | enuma 当前状态 |
| --- | --- | --- |
| FAT 启动载荷卷 | unixnu.toml、kernel.macho、完整 ADT、trust cache、可选 Data seed；UEFI/UniXNU/DarwinBoot 读取 | 尚未建立本机 initrd→BlockIo→SimpleFileSystem 发现闭环；当前三诊断镜像 ramdisk 为空 |
| OS/SystemOS 根镜像 | IPSW 的 OS 与 Cryptex1,SystemOS；SHNGROOT 描述两个只读窗口，XNU 块驱动/APFS 消费 | 未构建；缺 enuma GPT 几何、卷 UUID 和可用 XNU 存储路径 |
| 可写 Data | 独立 APFS seed，经 NativeRamBlock 提供；以后可接持久 overlay | seed 来源/生成配方、身份、大小与持久区域未审查；默认不启用落盘 |

参考官方 [载荷](https://unixnu.com/concepts/payload)、[userdata](https://unixnu.com/zh/guide/userdata)、[预链接](https://unixnu.com/concepts/prelink)。网页可能随主线变化，实施以本仓固定源码及审计报告为准。

## 来源与复用边界

可重放命令：

```powershell
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/audit_system_roadmap.py
```

[源审计报告](../../reports/enuma-system-roadmap-audit.json)记录12份文件的实际 Git blob 比对与 SHA256。顶层 UniXNU 固定5fdbd5d08518bc2d5c196264c56a377dd80cf5ca；NativeUfs af785c1777161a62931425c2faaa536ce0bebd5b、NativeRamBlock d4d22d9819b0162eda49f6402235dddc2279410d；sheng a599a1a8a92093b5077543e071b72130769eb325。同名脚本不是新 builder，审计仅检查现存契约。

| 来源 | 适合复用 | 不可直接继承 |
| --- | --- | --- |
| 固定 UniXNU 通用代码，BSD-2-Clause-Patent；NativeUfs 自带 BSD-2-Clause | userdata manifest/对齐/摘要、FAT 构建、NativePrelink、RAM 块设备、UFS root layout/publication 的算法与测试 | 当前驱动中嵌入的 sheng 控制器、GCC、SMMU、平台假设；模块级许可在真正移植前逐项保留 |
| UniXNU-sheng，与本板相同 IPSW 身份但 SM8550 | OS/SystemOS 的组件选择、预链接依赖闭包审计方法、身份/信任输入契约 | root UUID、GPT、slide、AMFI 地址、CPU 参数、内存预算、PMGR/GPU/电源参数 |
| 同 SM8250 alioth/elish UEFI 参考 | 既有 [SimpleFb 审查](2026-10-23-simplefb-metadata-variant.md) 已确认可用于固件显示路径排查；后续可评估同 SoC UFS/时钟/PHY 的具体实现 | UEFI 驱动不能作为 XNU IOKit 驱动链接；没有据此证明 enuma APFS、XNU UFS 或用户态可用。本轮未发现/核验新的同 SoC 完整 XNU 根卷移植 |
| 本机 MiCode kernel/devicetree，固定版本见 sources.lock | SM8250/enuma 的 UFS PHY、时钟、regulator、SMMU、IRQ、复位依赖来源；Linux GPL 源作事实/行为参考，代码移植另核许可 | 不能把 Linux API 或 Android 已挂载存储当 XNU 可用证据 |
| nuwa bd218816a833ab8f3f617399b6583b933a319f68 的系统卷审查 | 发现链审计方法、安装 ABL 的 initrd 组合风险提醒 | SM8550、Android v4/init_boot 长度与地址、Darwin22接口和其设备授权；参考仓本轮只读 |

## A. 先闭合载荷卷运输

UniXNU Config 从自身 DeviceHandle 和 SimpleFileSystem 查找 `\EFI\UniXNU\unixnu.toml`。无配置也可能显示默认菜单，故“菜单出现”和“FAT 被发现”应分别验收。

enuma 使用本仓已审计 raw BootShim+FD / Android boot v3 打包器，保留原厂 vendor_boot；不能直接改用通用 bootimg.py 的 gzip/v0 头验收。仅向 v3 ramdisk 字段写一个 FAT 不能证明安装版 ABL 会把纯 FAT 范围交给 UEFI。Android 的 chosen/initrd 也不能替代候选的实际 x0/FDT：vendor ramdisk 可能参与组合；不猜偏移、不向上取整越界映射。

首选评估已有 sheng BootMemoryDxe 的“有界 initrd →只读 BlockIo”机制，仅移植卷发布部分，不带 DRAM/GCD 策略；同一来源固定329b473df1e53a3bfa64b2b39b79670c4c02279b，原先 nuwa 审查记录SHA 060a248a…1171bd4。该机制要求整段长度为512倍数，不能剥除 vendor/cpio 前缀。本轮未重新移植或验证其 enuma 适用性。

下一步独立制作小型、无内核自动启动项的 FAT 发现测试：配置带唯一构建标签，记录发布范围来源、实际长度/扇区、BlockIo/文件系统句柄、配置打开结果。必须先有实际范围和可控返回，再做临时启动；不能从已填头字段直接推出运行范围。USB 大容量载荷是备选，但先证明 UEFI USB host/块设备可用，不默认支持。

## B. 板级内核与 donor 闭包

目标 XNU10063.141.1、普通 ARM64、4KiB。已保存 macOS bootstrap 格式/入口/TCR 检查通过，但全部设备功能关闭；[内核报告](../../reports/enuma-kernel-baseline-audit.json)明确它不是 enuma 启动候选。

1. 审查固定上游 corecrypto14、pthread builders 与 ArmDTPlatform/ArmCpu 工程，按真实依赖顺序生成归档；闭合 board 的 kernel.archives 和构建 opt-in。现有 enuma_defconfig 已请求上述功能，不能用空服务或关掉功能冒充板级构建。
2. macOS CI 做实际 iPhoneOS SDK 编译、归档链接、未解析符号/普通ARM64/4K/平台入口检查。SDK18.5工具链与 iOS17.0 deployment 是现有构建组合，不等于 donor 改为 iOS18。
3. 按唯一 j120ap / iPad7,1 /21H461 BuildIdentity 取得 donor KernelCache，解 IM4P/LZFSE 并固定解压后 Mach-O 哈希。现存13b97fa2…bf7b是容器哈希，不能冒充解压哈希。
4. 复用 NativePrelink2b6ffb50117eee820b98aca9bd51b5c7dfb2970e，对 roots、导入闭包、可执行 AMFI early initializer、slide及目标容量逐项审查，记录所有绑定/入口。sheng 的 roots 可作为待核清单，不能直接复制地址或把 Apple ARM CPU/GPU驱动当 Qualcomm 驱动。
5. 补完整 enuma ADT：身份、chosen/defaults/options、NVRAM proxy、种子/熵和所有 loader 输入占位符。现有2956B硬件片段不够；512MiB是入口请求，最终能否容纳kernel/ADT/cache/seed还需实际输入尺寸和实时UEFI map。
6. 实机验收分开记录 DarwinBoot加载、内存窗口、ExitBootServices、XNU入口、平台专家/CPU/GIC/定时器。先单核最小平台；SMP/调频/用户态另验，不能因入口出现就宣布系统能启动。

生成完整ADT或payload前仍不填猜测物理地址，不改变example/verified。新内存字段按现有编号审查规则办理；本轮没有形成需要批准的新数值。

## C. OS/SystemOS 镜像与存储

目标 IPSW 与两个 DMG 成员的 pin 已在 board.toml：044-76040-038.dmg /044-76034-038.dmg。角色以该 BuildIdentity 的 OS/Cryptex1,SystemOS 映射为准，不能按文件名顺序猜；pin 存在不代表本轮已经下载/验证两大镜像。

复用 userdata.py：macOS hdiutil 只读 attach DMG，复制展开后的 whole-disk 字节，前加4096B SHNGROOT manifest并补到1MiB，各窗口1MiB对齐。DMG压缩文件哈希、展开raw窗口哈希、APFS卷UUID、整体 userdata-root.img 哈希分别记录。传输 manifest 的SHA256不能代替APFS/代码签名信任策略。

实际容量验收应读取本机LUN/GPT、逻辑扇区和userdata边界，再比较展开后大小及计划的Data/log保留空间；当前没有在 board 声明几何。**固定 userdata.py 的 dry_run 分支只列组件成员大小，未调用 image_size，也没有 total > capacity 比较。** 不能将 dry-run 成功当容量通过；正式生成路径才做展开尺寸比较。应先补独立只读计划/容量检查，再跑大文件构建。官方192MiB payload及sheng的GPT/UUID均非本板配置。

主要难点在 XNU 块驱动：NativeUfs/GccUfs.h明确是 SM8550，NativeUfs.cpp也嵌入sheng的GCC/UFS/SMMU行为。应保留通用队列、描述符、root-window校验/发布及测试方法，将SM8250硬件部分从实际enuma资料逐项适配：电源/时钟/复位→PHY/链路→LUN/容量→SMMU/DMA→只读块校验→窗口/IOMedia发布→UUID/APFS。UEFI UFSDxe可读不代表EBS后仍可通过UEFI服务访问，必须有XNU自己的驱动与接管证据。

还有显式平台依赖：payload.py/check_native_root 在 native-ufs-root=1 时要求恰好一个 sheng-pmgr=2，以及内核定义 _sheng_pmgr_run，注释指出原版AMFI缺PMGR会panic；enuma_defconfig目前 XNU_SHENG_PMGR=n。后续必须审查原始安全组件所需的服务接口和本板实现，不盲加sheng参数、删除检查或用空PMGR服务过关。

首次存储实测只读：设备/LUN/逻辑块正确→固定已知块摘要→GPT与manifest边界→OS/SystemOS只读窗口→原始APFS识别与卷UUID→按UUID挂根。复用RootPublication对SystemOS/OS的有序发布，源码指出owner信任路径在挂root后立即解析SystemOS。原userdata写入属于破坏Android数据的独立决策，需先有恢复/备份与具体审查；此前“可推镜像”不自动授权覆盖userdata。

## D. Data、信任与 iPadOS 用户态

Data seed不是本轮已存在的输出。需固定其来源/生成配方、APFS格式、卷UUID、目录/权限、版本匹配、packed/dense编码和哈希。NativeRamBlock及DBRDISK1可优先复用；packed仅减少载荷中的非零数据，不能据此声称总RAM占用为零或512MiB足够完整用户态。

第一阶段用可丢弃RAM Data，把落盘功能关闭；正式持久化前单独审查尾部窗口、root镜像间距、store位图/header、日志保留、断电与FUA语义。sheng的默认日志保留和grow参数不直接用作本板数值；不得借此重启已停止的R-002日志方案。

信任输入按同一donor取StaticTrustCache和Cryptex1,SystemTrustCache，审查bundle格式/hash pin与ADT占位符，保持原Apple安全组件与4K签名桥接契约。root镜像存在、内核预链接成功、AMFI/CoreTrust/AppleImage4可用和launchd执行成功是不同验收点；owner trust/VerifiedRoot需要自己的来源和策略审查。

iPad7,1/j120ap、ADT product/target/model、安全属性、Data中的MobileGestalt身份需一致；不能把随机平台seed当Apple设备ECID或继承外板私有值。skip-setup只改Data副本偏好，不代表激活、联网或所有系统服务可用。

用户态按 launchd→最小可观察服务→backboardd/图形服务→触控事件→SpringBoard 分层。固定source有显示/NativeAdreno/Metal/输入实现可评估，但SM8250 GPU固件/电源/SMMU、面板及NT36523都需本机适配。GOP文本不等于用户态图形加速；看到界面也不等于Wi-Fi/声音/充电/休眠正常。NT36523仍按已定主线推进，不让系统卷大下载阻塞当前UEFI诊断。

## 下一轮顺序与实机门槛

| 顺序 | 可先离线完成 | 需要实机的事实/停点 |
| --- | --- | --- |
| 1 | 晚间已归档三候选、屏幕后端接入审查 | SimpleFb入口/返回、真实GOP/矩形、复位恢复；无返回停追加 |
| 2 | 小FAT配置/发现探针与initrd契约 | 当前候选x0/FDT范围、BlockIo/SFS/配置；不是Android历史chosen |
| 3 | 归档builders、板级内核CI、donor闭包/ADT | 实时UEFI map、窗口/EBS、XNU入口及基础平台 |
| 4 | DMG只读清单/UUID/容量计划、SM8250存储差异表 | 本机GPT/LUN/扇区与只读UFS接管；破坏性userdata写入先审查 |
| 5 | seed与信任输入审计、最小服务配置 | APFS root/SystemOS、Data、launchd及图形/输入，持久写入单独验收 |

本轮不请求换系统版本、扩内存或刷userdata批准，不触发新人工待办。后续若出现实际需要改变内存/verified或破坏性分区动作，先提出具体方案；暂不能给进入桌面的日期。
