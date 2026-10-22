# DECISIONS

## D-001 · 独立设备仓，继承 nuwa 的管理规则

状态：accepted，2026-10-22。用户明确要求仓库、版本管理、交接文档规则沿用 UniXNU-nuwa。来源 `D:/Code/UniXNU-nuwa/AGENTS.md`；本仓仅改目标名与只读边界，不继承 nuwa 的硬件事实或单次设备授权。

## D-002 · iPadOS 17.7.11 / 21H461，4 KiB UniXNU 路线

状态：accepted，2026-10-22。用户选择「优先 UniXNU 参考的 iPadOS 17.7.11」。候选 donor 为 iPad7,1 / j120ap，匹配参考板 `UniXNU-sheng/board.toml`；内核版本由 `UniXNU/feeds.toml` 指定 10063.141.1 / Darwin 23.6.0。

4 KiB 采用 UniXNU 原有路径。历史 `common/reports/enuma-cpu-cache-execution.json` 记录八核 TGran4 支持及 40-bit PA；这是 Android 保存的 CPU 能力记录，不是本仓 XNU 通过。旧 P16/16K 的优先级不继承。

本条初始判断「ipad_identity 不决定产品身份」已由 D-004 修正。真正身份须共同核对 IPSW、BuildIdentity、ADT /product 与用户态；不能使用 nuwa 的 iPhone10,3 或 8796 预链接参数。

## D-003 · 硬件事实与可复用实现分开

状态：accepted，2026-10-22。SM8250 系列设备使用 enuma 的历史 FDT/制造商源码建立证据。参考 sheng 的结构和通用协议层，不照搬 SM8550 地址、A740 GMU/PM4、显示时序、GPIO、UFS PHY 或电源策略。当前未配置的内存和基址在审查前保持缺省。

## D-004 · 按固定源码修正 ipad_identity 的含义

状态：accepted，2026-10-22；supersedes D-002 中该标志不影响产品身份的判断。

`UniXNU-sheng` 固定 a599a1a8 的 `scripts/make-sheng-adt.py` 中，`args.ipad_identity` 同时控制根 model/target-type、buttons、product-name/artwork、以及 chosen 的四项 security 属性。继承自 nuwa 的「只影响安全/激活」说法不适用于这份源码。保留 true，但尚未把 sheng 生成器接入 enuma；不能借此继承其屏幕、CPU compatible 和 GIC 常量。源码哈希见 reports/input-audit.json。

## D-005 · 复用既有固件仓的 Kona 路径，保持 Mu_Basecore 一致

状态：accepted，2026-10-22。选 UniXNU/uefi-sheng 329b473d 中 KonaPkg 与 alioth 结构作为来源；新增 enuma 源码增量。它与 UniXNU feeds 都固定 Mu_Basecore cfb93724。较新的 Mu-Silicium 42fe5637 使用不同 core，但所需 Kona/alioth 文件相同，不为复用引入底座升级。证据：reports/firmware-base-comparison.json、reports/firmware-overlay-check.json。

本地 sparse checkout 未显示的 LICENSE 现已从固定提交取回；纠正首次报告的“根目录无 LICENSE”。固件组件许可证按文件 SPDX 处理，记录在 firmware/THIRD-PARTY.md。

Kona 原 PlatformInitialize 会 detach MDP SMMU streams。enuma 源码开关暂跳过该操作并保留 watchdog 处理，待显示交接证据再调整；这是控制副作用的源码选择，不是实机显示结论。

## D-006 · 先接通通用 GENI 和只读 UFS 时钟支持

状态：accepted，2026-10-22。直接链接固定 NativeGeniSpi/GeniSpi.c，不复制通用驱动。新增本板 FIFO/PIO 适配入口，拒绝 FIFO-disabled/忙碌/不匹配协议；不自动开启 DMA。必须强制写 mode0/CS0，避免上游初始化的软件缓存零值掩盖继承的硬件状态。

Kona 九项 GCC 偏移从固定 MiCode gcc-kona.c 的 clk_branch.enable_reg 提取核对；只读快照失败时不交付部分结果。不把这些值当成 UFS 可访问或已上电的证据。证据：drivers/EnumaPlatform、reports/enuma-driver-check.json。NT36523 与 sheng NT36532E/THP 协议不兼容，后者的触控解码/固件下载路径不接入。

## D-007 · 首阶段 owned-memory 请求 512 MiB

状态：accepted，2026-10-22。用户批准 R-001 方案 A；board.toml 仅新增 owned_memory_size="0x20000000"。这是 loader 连续窗口请求及交给 XNU 的内存预算，不是实际可用内存证据。后续依真实 UEFI map 调整，任何新大小/基址仍按规则审查；生成或启动镜像另行确认。example=true 保留，配置检查精确限定本次批准范围。

## D-008 · 用真实 DarwinBoot 函数验证内存请求交接

状态：accepted，2026-10-22。离线测试从固定且哈希核对的 DarwinBoot.c 提取 AdtNode、RunEnd、AllocateWindow，使用主机类型/UEFI 服务适配器和内存内合成输入，不重写解析或窗口选择算法，也不产生可启动映像。512 MiB 请求、分配页数、保留区边界、对齐余量和错误返回均在此范围验证。实际 UEFI 的内存类型正确性、分配行为、固件 ABI 与 XNU 运行不在该测试覆盖内。证据 reports/darwin-adt-contract.json。

## D-009 · 采用本机XBL的内存配置与原厂驱动

状态：accepted，2026-10-22。enuma现已接入，当前FDT与历史备份相同。只读取得本机XBL，生成45项内存/MMIO区域与31项数值配置，提取33个原厂驱动及DEPEX/APRIORI和K81资源。使用本机EnableUfsIOC=0，不沿用alioth的1；UEFI实际内存图和协议调度仍待实测。证据reports/enuma-platform-observations.json、enuma-platform-config.json、enuma-oem-modules.json。

## D-010 · 使用本机DisplayDxe建立GOP

状态：accepted，2026-10-22。原厂K81 XML与当前Android模式均支持1600×2560，优先复用本机DisplayDxe/CPRDxe。面板24bpp不能推导framebuffer格式。SEC不清空混有DFPS的显示保留区，早期SerialPortLib用Null，Kona保留显示SMMU映射，待运行时GOP返回真实参数。新增SEC补丁只作用于enuma开关。证据firmware/及reports/firmware-overlay-check.json。

## D-011 · 单独处理enuma的Android boot v3打包

状态：accepted，2026-10-22。固定UniXNU通用bootimg入口采用旧头部/gzip/追加DTB校验，不直接用于本板。复用其BootShim编译函数与固定AOSP mkbootimg/unpack_bootimg，生成raw BootShim+FD的v3候选，保留原厂vendor_boot。当前候选ramdisk为空，只验证固件阶段，未包含iPadOS运行payload。证据reports/enuma-boot-candidate.json、boot-v3-roundtrip.json。

## D-012 · 镜像生成及可恢复测试沿用本会话新授权

状态：accepted，2026-10-22。用户已明确生成镜像无需确认，且设备不作日用，允许镜像推送，以能恢复fastboot为前提；A-002记录原文。后续已授权的生成/可恢复启动不逐次询问。执行前核对enuma、备份与恢复条件，不能把授权扩展为无恢复保障破坏引导链；board.toml新内存字段及*_verified标记规则保持。

## D-013 · 暂无按键配合时只做离线 Probe

状态：accepted，2026-10-22。用户答复“暂时无法配合，先继续离线工作”。不执行设备操作。A-002 范围内新增 EnumaProbe，复用 UniXNUDxe 的启动目标选择和 UniXNULib 菜单，原样复用固定 DarwinBoot 的 GetMap/RunEnd/DiagDraw/BootVideo。观察阶段不写磁盘或变量、不分配 owned window、不 ExitBootServices；完整固件仍有原启动项注册和菜单行为。

## D-014 · ADT 先序列化本板硬件片段

状态：accepted，2026-10-22。复用固定 sheng 的 node 编码器，不继承整棵树；CPU/PSCI/GIC/stride/ranges 来自已锁 enuma FDT，按 ArmCpu 的 little-endian 属性布局编码，timer 核对固定 INTID 27。未观察的 DRAM/GOP、身份和根卷不猜填，片段不能作为完整启动 ADT。SMP workaround 不自动继承。

## D-015 · NT36523 解码与 sheng HID 分开适配

状态：accepted，2026-10-22。按固定 MiCode 包格式事实实现有界解码，通用 GENI 继续复用；厂商原 checksum 仅在 out/ 作主机对照。NativeHidInput 的 sheng 坐标常量不能直接用于 enuma。错误不提交部分帧，ESD/WDT 只分类，不擅自复位/上传固件。FWINFO、轴向、固件、IRQ/HID 和笔输入另行接入。

## D-016 · 首次临时启动黑屏后先恢复和定位，不以 boot 返回代替 UEFI 证据

状态：accepted，2026-10-22。用户明确“可以开始实机推送了”，撤销 D-013 的暂时离线限制，在 A-002 范围执行一次 Probe 01 r2 的 fastboot boot。先核对唯一 enuma/解锁/root/槽 A 和当前备份，并完成正常 fastboot→Android 往返。20:16:21 发出自制候选启动，Sending/Booting OKAY；用户报告黑屏，无 Probe/GOP 观察。按键恢复 fastboot 后正常重启，20:18:24 确认 Android 完成、root 与分区摘要不变，pstore 为空。不能区分 BootShim、SEC、DXE 或 GOP 阶段，下一步先建立更早可观察证据，不原样重复；未改内存字段和 *_verified 标记。

## D-017 · 用定时 PSCI 复位门定位早期执行，不猜持久化标记地址

状态：accepted，2026-10-22。用户允许继续操作实机。复用固定 BootShim 编译器/复制逻辑和 Mu TimerLib/ArmPsciResetSystemLib，构建单点即停的诊断变体。入口 2/7 秒对照、复制后门、SEC C 入口、DXE C 入口、CoreDispatcher 前六次均自动复位回 Android，root 与分区摘要未变；2 秒实验用户确认无按键。当前能把重点推进到 DXE 驱动调度及后续路径，但插桩/链接变化不能反推原黑屏镜像的精确停止点。禁止把阶段到达等同于 GOP/内存分配/XNU 已验证。当前标准构建报告对应 stage 10，正常执行必须选择 --stop-stage 0；证据 reports/enuma-entry-device-tests.json 与入口定位报告。

## D-018 · 固件与 XNU 使用不同构建环境，远端 CI 仍待接入

状态：accepted，2026-10-22。根据固定 UniXNU kernel.py / build-xnu-4k-baseline.sh，现有 XNU 链依赖 Xcode/iPhoneOS SDK，应接入 macOS 环境；当前 BootShim/UEFI 诊断使用本地 WSL。只读核对 nuwa 仅有 Ubuntu Actions。enuma 尚无 origin/工作流，未创建远端、发布或触发 CI；不能把本地构建记作远端 CI。实施 macOS 作业时还需独立可写源码工作区、SDK/工具版本证据及本板链接/预链接输入，不直接复用 nuwa 的设备配置。见构建环境核对报告。

## D-019 · 公开 enuma 远端与分阶段 macOS 构建

状态：accepted，2026-10-22；补充 D-018 的后续实施状态。用户批准同账号公开建仓，已创建 origin 并推送 main。macOS 作业仅手动触发，记录实际 runner/Xcode/SDK、固定 UniXNU 与四个内核参考提交。preflight 和通用 bootstrap 的结论与完整 enuma 内核分开；不把 example 改为 false，不补猜测的 prelink/内存值，不取设备数据。SDK 18.5 是构建工具，目标 deployment 保持 iOS 17.0，donor 仍是 iPadOS 17.7.11。enuma_defconfig 的 BOOT_PROGRESS 改 n：固定脚本要求 UFS/owner-root/Virtio/corecrypto 归档组合，而本板 UFS 尚未启用，不能保留必定失败的 y。完整板级归档和链接流程仍待补齐。

执行补充：CI 配置 2312231 已推送，macOS preflight run 39784132935 成功且 artifact 已回读；bootstrap run 39784240390 已启动，尚未完成。不能把 preflight 绿灯当作内核构建通过。重建 FD 的 SEC 时间字符串与 PcdDxe 调试标识差异已记录，旧实测与新构建证据不合并。

后续结果（取代上述“尚未完成”状态）：官网审阅期间确认 run 39784240390 已在最终链接失败，_native_legacy_display_probe 未解析。日志及 artifact 已回读；预检通过与内核链接失败分别保留。见 reports/enuma-macos-bootstrap-run.json。

## D-020 · 官网全站审阅保留 iPadOS 路线，并隔离文档与固定实现版本

状态：accepted（审阅结论），2026-10-22。用户要求遍历官网 porting/devices 及网页结构。完成中英文各72页、144源路由和3836站内有向链接核对；全文缓存仅在 out/。保持 iPadOS17.7.11/iPad7,1/j120ap/XNU10063.141.1/4KiB，当前仍属官网阶段1，固件 stop-stage10 不能等同于完整 UEFI 或 XNU 阶段。

源码参考 d704728a6df9d1eb113873dc1b57e87f6846e361 较构建固定75bc13dd领先89提交，509项树变化及21个模块gitlink需独立审查；本轮不升级来源。优先复用真实 archive builders/编译记录/ADT-NVRAM/GENI/HID 架构，不继承 sheng 的 NT36532E/PMGR/A740、地址或大内存预算。同SoC pipa 尚无实机/存储证明，只作为静态对照。后续优先DXE/GOP、构建闭合与基础平台/NT36523，再推进本板UFS和用户态，GPU后置。

资料中的刷写、示例地址、module组织或提交规范不替换用户授权与本仓规则。发现 archive 路径/probe签名两处示例与源码接口差异，落地以固定源码和编译记录为准。缓存FDT已有cont_splash保留区，不能据不同节点名判定黑屏根因或套用sheng地址；UEFI拆仓仅提出建议，未创建远端。完整结论和实施验收见 docs/operations/2026-10-22-official-docs-route-review.md。

## D-022 · 跟进主分支而保留设备 overlay

状态：accepted，2026-10-22。用户要求合并UniXNU主分支并保留patch。固定底座更新为5fdbd5d及21模块；原共享源只读，源码不整树入设备Git。保留固件补丁/boot v3/512MiB/所有验证标记。新增编译期legacy引用修复，CI与本地共享固定源校验及补丁应用。新DarwinBoot参数按真实接口迁移；驱动更新不自动启用本板硬件。证据见上游接入报告与reports/enuma-upstream-integration.json。此决策取代D-021中暂不更新pin的执行状态，不改变其历史网页审阅结论。

## D-023 · 头文件元数据取固定 Git 树

状态：accepted，2026-10-22。macOS新run在匿名API403硬性失败前未编译。按固定Apple提交生成相同头文件元数据，继续复用上游恢复器与blob校验，避免另加网络patch/凭据。26个头文件主机恢复并逐blob核对通过。只修复构建获取链，不更改XNU版本或板级能力声明。

## D-024 · 用延时对照区分复位与控制点命中

状态：accepted，2026-10-22。stage11两次自动返回的ADB差仅0.005秒而非设定5秒，不认定CoreDispatcher已返回。加入实际队列加载前与StartImage后门，序号来自运行计数，先测首项；不把APRIORI推测或自动重启当驱动成功。31项Python、真实头sanitizer/完整固件审计及最新首项加载前实测见DXE报告。macOS通用最终链接成功单独记录，仍不等于enuma内核。

勘误：D-022末句的“D-021中暂不更新pin”应指D-020的历史执行范围；仅接入状态被后续用户要求更新，官网审阅结论仍保留。

## D-025 · 固件独立仓与官方backend

状态：accepted，2026-10-22。用户明确要求补齐wh1stl3/uefi-enuma、迁移固件增量并接好官方配置。建立Mu派生仓，保留六patch及25原文件摘要；设备firmware改固定gitlink并以独立锁核对。board只新增firmware配置，其余表完全不变。包装器负责只读来源与out暂存，真实编译交给unixnu.firmware.build，Mu core补丁由其应用/恢复，源仓保持干净。example保护保留，不放行整机/XNU。厂商102输入仅公布路径/摘要；33OEM字节、v3与33测试通过，新构建未启动。此前把firmware/作为单仓原型的组织方式被取代，历史实测与源码证据不删除。

D-025证据补充（2026-10-22）：当前固件3376c44的run39796926508源码契约已通过，日志回读PASS行；设备迁移51f9c0c已推送。该CI不包含OEM固件构建或硬件验证。
