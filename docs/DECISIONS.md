# DECISIONS

## D-001 · 独立设备仓，继承 nuwa 的管理规则

状态：accepted，2026-10-22。用户明确要求仓库、版本管理、交接文档规则沿用 UniXNU-nuwa。来源 `D:/Code/PortingiOS/nuwa/UniXNU-nuwa/AGENTS.md`；本仓仅改目标名与只读边界，不继承 nuwa 的硬件事实或单次设备授权。

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

## D-026 · 首项返回采用2/7/2秒对照，保留返回状态未知

状态：accepted，2026-10-22。沿A-002与既有Mu计时/PSCI诊断，官方backend的stage13/ordinal1两份镜像及一次相同2秒镜像复测ADB15.903/22.308/16.939秒；7秒与复测2秒差5.369秒，支持到达CoreStartImage返回后门。2秒自身波动1.036秒，完整样本保留，不将其记为精确芯片计时。EFI_STATUS/GUID未采集，不声称驱动初始化成功、协议安装或整个调度完成；stage11反例仍有效。四次含新stage12基线均已恢复Android/root/分区摘要，无新的硬停项。后续从真实ordinal2及后续队列边界推进。证据见DXE实测与entry-device-tests。

## D-027 · 指数扩大队列范围并复核第8项

状态：accepted，2026-10-22。用户要求持续推进至需人工节点。第2/4项单点恢复与短门一致；第8项初次2/7差1.091秒不认定成功，复测原2秒镜像后7秒差5.316秒支持第8项返回后门。所有时序样本保留。继续向16扩大，发现边界再回查，不以队列序号替代GUID或以入口返回替代EFI_SUCCESS/协议闭包。五次均恢复Android/root/分区摘要，A-002范围不变。

## D-028 · 身份查询失败继续完整组拒绝，补齐精确解析与日志

状态：accepted，2026-10-22。第16项推送前再次连续缺失product/current-slot/unlocked，未发boot，正常重启并核对Android/root/槽位/摘要后重试成功。原因未知。保留五次完整组校验，不放宽字段；修复子串可能误接受enuma后缀的问题，要求恰好一个完整值并拒绝重复/冲突/FAILED/非零。查询日志仅在out/，公开报告不含设备标识；失败阶段明确区分推送前与启动后。36项Python通过，重试首轮身份成功，ADB16.953秒，未有人工干预。

## D-029 · 保留原迁移字节，以扩展补丁细分加载/入口/状态

状态：accepted，2026-10-22。第32项长复位与第24项短门提示需细分边界；新增独立扩展，不改原25迁移文件/六patch。新增加载返回、入口前、错误/非错误返回及完整GUID条件，复用原计数/计时/PSCI。DSC仅在out打补丁，core由官方backend应用恢复。源锁38项，固件d6900d2已推送，源码CI/20组sanitizer/40项Python通过。新版第28项长复位不作成功证明；继续同版第26项，避免跨插桩布局作精确故障认定。A-002范围不变，无内存/验证标记变更。

## D-030 · 提前真实Metronome，但不认定其解决UFS

状态：accepted，2026-10-23。原厂APRIORI中Metronome早于UFS；固定Mu CoreStall缺该协议时返回NOT_AVAILABLE_YET，故以独立暂存patch调度已有真实模块，所有既有INF相对顺序保留。281179c源码CI通过，完整33OEM固件构建审计通过；同完整UFS GUID返回后仍长复位，未解决UFS边界。新序号用完整GUID限定，不跨布局推断根因。

## D-031 · 用显式缺UFS变体隔离显示，默认完整模式不删驱动

状态：accepted，2026-10-23。沿用户GOP优先路线，b988fa4增加默认0的ENUMA_DIAG_DISABLE_UFS。仅显式诊断模式从三处排除UFSDxe，无空协议。构建必须声明唯一缺项、完成FD摘要匹配，审计验证UFS文件/队列引用缺席及其他32OEM字节；普通33模块及伪造缺项负向检查通过，42项Python通过。隔离整个调度仍长复位，但Display完整GUID入口前7/2/2/7秒重复对照差5.277秒支持其前门，后门仍未观察到。不是GOP/存储或完整平台验证。

## D-032 · 日志保留配置等待R-002，不向普通Linux页写日志

状态：proposed/pending，2026-10-23。现有OEM Log Buffer不是Android保留区，FDT两类保留表均无覆盖，实际8页KPF_RESERVED全false。只读收集匹配内核头及元数据，未读物理内容/加载模块/写标记。新增board诊断地址/大小与临时FDT保留触发AGENTS第1类，R-002列出候选32KiB软件路线与UART；先等选择，不使用现有512MiB授权代替新地址配置批准。

## D-033 · R-002 批准，先落实临时 FDT 保留，按用户要求停止

状态：accepted，2026-10-23。用户明确批准 R-002 软件日志路线，取代 D-032 的待决状态，保留其历史理由。只增加候选 0x9fff7000/0x8000、enabled=false，旧内存/512MiB/example/验证标记不变。首版运行后 NOP 假设未让保留生效；只改编码复用相同名称后缀后，第二次实测唯一 reserve tuple 与 8 页 reserved 通过，节点/属性值相同。该结论只适用当前诊断 Android，不能继承到普通重启或当作持久日志/GOP/UEFI map 证明。匹配头/原厂 CRC 的 ABI 探针仅离线构建，正常加载及标记存活未执行。用户随后要求本轮实机验证完成就停下并写文档，故停止新镜像/模块动作，不自动恢复。无新待批准项，R-002 原有失败即停/不得换址或刷分区边界保留。

## D-034 · SimpleFb优先复用Mu核心，以独立诊断和真实scanout门禁接入

状态：accepted（审计与后续设计，不是变体实现/硬件批准），2026-10-23。用户要求对照alioth/elish离线审计、记录复用/差异/实机条件且暂不操作实机。固定22个源码及已有FDT/OEM事实，优先现有Mu SimpleFb/FrameBufferBltLib与EnumaProbe，不能只改显示开关或把elish地址/32位当本机事实。未来SimpleFb诊断需精确排除CPR/Display/UFS、其余30项不变及唯一GOP，默认33/现有32审计不放宽；补真实几何/范围和错误路径。显示区尾部metadata落DFPS，保持Null serial，不借用R-002日志授权。协议注册、可见scanout、DarwinBoot BGRX32接受分层验收，EBS/XNU另验。本轮只写审计/交接，无代码、镜像、内存/验证标记变化或设备操作。

## D-035 · 同SoC参考评估持久化，离线补齐回读后停在实测依赖

状态：accepted，2026-10-23。用户明确要求遇难题评估同SoC设备UniXNU/UEFI仓库，已写AGENTS；固定来源/依赖/板级差异后决定复用，不继承别机参数或授权。主线补齐实际16字节reader编译与mock内核API下源码保护检查，运行ABI/物理读取/标记存活仍未知。SimpleFb保存输入仍缺六项入口事实，旧cont_splash日志不足，暂不修改驱动选择/FD策略或填几何。保持先前暂不操作实机限制，在需活动FDT/页/ABI与真实scanout观测节点停下；没有新的内存变更或verified审批项。

## D-036 · 更新强停规则并接受有界可控黑屏/定时探针

状态：accepted，2026-10-23。用户明确生成镜像无需硬停，无法监测/无法回Android-fastboot-TWRP时须停，并随后澄清黑屏与定时复位允许，只要可回可控状态。AGENTS记录最终例外，恢复主线设备范围；不把USB/定时返回视为实际驱动日志或成功，不扩成任意分区刷写。原内存/verified及R-002失败即停边界保持。

## D-037 · R-002回读已通，但跨Bootloader标记失败，停止该持久日志路线

状态：accepted，2026-10-23。实际normal ABI及reader均有dmesg日志、模块出现/卸载与恢复核对。已保护范围内seed写16字节，同次Android回读匹配；经Bootloader临时boot不写marker保留镜像后不匹配，8页仍保护、ABI与reader仍通过。不能归因单一清零函数，但路径不保持已足以触发R-002停，不换址/扩大/借DFPS或SMEM；继续方案需围绕有界入口门/UART或同次输出评估，详见R-003。未设置verified标记、未启用SEC/DXE持久日志。

## D-038 · 共享Dispatcher上下文细分真实PE调用，先以完整GUID对照验证

状态：accepted，2026-10-23。用户选择R-003推荐A。固件0924fbd扩展detail20/21/22，通过DxeCore-local bridge使用同一Dispatcher序号/GUID及当前handle，嵌套其他handle/NULL不匹配；原迁移字节不变。首构建因Image.c CRLF上下文拒绝，a927ca1仅在out规范化并加固定基线后真实构建通过。35组实际头/bridge sanitizer、45项Python及源CI通过。Display/no-UFS的point20 2/7/2三样本差5.295/5.905秒支持到达PE调用前，不证明PE内包装器/构造器/主体；point21/22待测。R-002停用、内存与验证标记不变，恢复保障沿A-005。

## D-039 · 真实PE返回与默认异常门分别记录，负向结果不越级归因

状态：accepted，2026-10-23。a927ca1的Display/no-UFS point21/22未观察短返回，均自动恢复；903ffed全局默认DumpCpuContext point23的2/7秒ADB30.766/30.772秒，差0.006秒，无预期5秒响应，未观察默认异常门。同source point20正对照ADB15.951秒，恢复正常。不能排除已注册handler、进入hook前栈/CPU故障或其他复位源；不能把全局门归因Display。依赖复用真实Timer/Reset，core AARCH64 INF显式依赖及还原核对完整，6组header sanitizer、45项Python和源码CI通过。R-002持久日志仍停，不加地址。

## D-040 · 先观察实际canary配置表分支，不以静态SMC线索替代根因

状态：accepted，2026-10-23。锁定33个enuma OEM PE均含同canary GUID；Display包装器前64位匹配/缺省SMC分支只读核对，并与一手研究对应。不能因此把问题归为Display特有RNG失败或用常量canary替代实现。固件d3a0972新增只读point24/25，沿同一Dispatcher上下文和完整文件GUID观察调用前匹配前缀存在/缺失；坏表/超4096诊断上限不产生缺失结论，不读VendorTable、不写表、不调用SMC。47组实际header检查与45项Python/补丁重放通过，源码CI成功；实机结果单独交接。无内存/verified/OEM字节变更，仍按A-005进行可恢复临时boot。

D-040实测补充：d3a0972 point24 2/7/2 ADB17.298/21.464/16.058秒，全部样本差4.166/5.406秒，第三次复用原2秒镜像；支持调用前匹配前缀存在，全部恢复核对正常。降低缺表初始化分支嫌疑，不验证完整GUID/值或包装器执行，不排除其他SMC。point25未实测。下一层应优先真实UEFI服务边界及调用归属，不改OEM PE；没有新内存或验证标记批准需求。

## D-041 · 借鉴nuwa实测分配诊断，先查分配器状态再讨论堆调整

状态：accepted（审计及排查优先级，非新门实现或扩堆），2026-10-23。用户要求查看同级nuwa进展。固定436c557及输入哈希；nuwa有R-010实际资源耗尽证据，R-011新堆构建/实际表通过，但新运行改善未有足够证据。两边Mu cfb93724相同，0008在本仓私有归档两目标严格dry-run通过、未应用；实际enuma SEC为51MiB且与本机XBL一致。优先新增真实分配失败/free/largest/type受控观测，与Display构造器/服务归属一起定位；不能直接拷贝209.75MiB、SM8550地址、帧缓冲尾部日志或Darwin22接口。未改变任何内存/verified/OEM/源锁或操作实机，R-002日志仍停；下一层具体插桩仍需本仓组合重放、编译与实测。

## D-042 · 先用真实pool搜索结果的成功/失败全局门验证分配路径

状态：accepted，2026-10-23。用户要求继续，固件7276dcd沿现有扩展在CoreAllocatePoolPages的FindFreePages结果处加入26失败/27非零正对照，复用Timer/直接PSCI，不取新锁或进行map遍历/分配/日志。全局、无驱动归因，拒绝GUID/非占位ordinal；不把失败等同容量耗尽或成功等同完整分配。45项源锁、17组pool及51组分发头/46项Python通过，实测另记。保持内存/verified/OEM与R-002停止边界，不复制nuwa扩堆或日志地址。

D-042实测补充：7276dcd成功门27的2/7 ADB16.108/21.478秒，差5.370秒支持hook执行；失败门26的2/7 ADB31.129/32.248秒，差1.119秒，无预期延时响应。四次完整审计和Android/root/原摘要恢复通过。只记录未观察失败门，不声称零失败或排除所有内存错误；无扩堆依据，继续同SM8250 SimpleFb独立诊断方案。

## D-043 · 借鉴同SM8250显示切换形成独立SimpleFb诊断，首测未恢复即停

状态：accepted（代码/静态构建，非GOP实机通过），2026-10-23。用户要求从其他设备借鉴；233a9d8复用alioth/elish路线和真实Mu SimpleFb/BltLib，原生默认不变，显式30-OEM诊断排除CPR/Display/UFS并保留其余字节，补通用错误/清理/模式/溢出检查，诊断Blt拒绝绘制。实际AArch64/30OEM/FD/BootShim/v3与源码CI通过；10:16:30首测75秒未回ADB/fastboot，runner已停止，用户无法按键，状态manual-recovery-needed。静态APRIORI位33不是实机计数32的证明；漏门/更早停点/仍在UEFI运行等未知，不归因SimpleFb成功或故障。

7479da1仅离线补EnumaProbe直接绘制入口守卫；公共runner拒绝上一轮未恢复，私有SimpleFb编排只构建不自动启动。整份SimpleFb host ASan/UBSan、Probe早期守卫宏0/1、48项Python及49源锁/sourceCI通过，新守卫未构建或实测，不能追溯保护233镜像。不改内存/verified/OEM，不重启R-002。设备恢复后先校准实际计数或评估GUID-only及成功/失败/加载错误/BDS均有界返回，再谈新试验。

## D-044 · 人工恢复后离线解除GUID与未知序号耦合，正常分派结束先复位

状态：accepted（离线实现/构建，非新设备通过），2026-10-23。用户确认人工按键恢复Android，主机核验完成1/root/槽/解锁/原摘要；随后用户要求离线推进，本轮没有新启动。6bc5b81显式GUID-only保留完整文件GUID、真实句柄/detail/status守卫，序号1仅占位；默认旧模式不变。显式正常完成兜底在首次CoreDispatcher返回后、架构协议检查及BDS前固定7秒PSCI复位，默认关闭，不称异步看门狗，不能覆盖更早卡死。目标7秒与兜底7秒单次不可区分，未来需早期对照与2/7/2时序。147组detail/bridge sanitizer、三组完成配置/非法组合、50项Python、重复patch/50源锁和实际AArch64构建通过；FD/OEM/打包报告独立保存，不推导GOP/XNU成功。原迁移字节、内存/verified/OEM和R-002停用边界保持。

## D-045 · 用真实Mu配置库复现重试缺陷，并联测视频交接

状态：accepted（离线修复/构建，非实机通过），2026-10-23。继续主线时用固定Mu cfb93724配置前缀替代过度宽松mock，复现静态size导致清理后NULL sizing query失败；另复现未约束描述符跨度。82ce8a5改为每次局部零大小并约束Span/Length与端点溢出，不改内存值。真实库/完整SimpleFb/BootVideo三组合sanitizer、原完整驱动/组合patch、50项Python/50源锁/串行workspace及实际AArch64/30OEM/BootShim/v3通过，源码CI39912601757回读PASS。构造器/as-built/Null串口为静态证据；不把合成视频元组当实际GOP，不把重试缺陷当首次黑屏根因。全程无设备查询/启动，保持GUID-only及同步兜底局限、R-002停止与内存/verified边界。

## D-046 · 同版三候选留待晚间实测，并明确通用内核不等于板级候选

状态：accepted（离线准备，非运行结果），2026-10-23。用户要求留晚上集中实测；固定82ce8a5备齐早期加载前2秒、完整GUID调用前2/7秒，计划四次早期→2/7/2，末次严格复用同镜像。交叉核对源锁/宏/FD/OEM/BootShim/v3，不自动执行USB。任次不返回先恢复停追加，正常完成兜底不称看门狗/命中证明。复用NativePrelink固定解析器核验保存的普通ARM64/4K通用内核及六种篡改拒绝；确认设备功能全关，归档/预链接/ADT构建缺口仍存在，不把它当enuma内核。无板级/内存/verified更改、设备查询或R-002重启。

## D-047 · UART配置可取但物理接入条件未闭合，主线采用屏幕诊断

状态：accepted（用户条件选择与只读发现，非屏幕实机通过），2026-10-23。15:18明确enuma/root只读核对：命令行ttyMSM0/115200n8，serial0/988000/qup2 GPIO117/118，但console节点disabled、/proc/consoles无ttyMSM；另一个998000串口绑定不等同调试口。软件不能给出可靠实物测试点/TX-RX/实测电平，现有ADB不是UART链路，故按用户选择继续GOP/屏幕路线。现有metadata/Blt/Probe守卫保持，先确认真实几何和像素子范围再小标记/阶段/EFI状态输出，早期黑屏仍需可控复位。无UART启用/寄存器写/镜像启动/内存或verified变化；R-002保持停止。

## D-048 · 独立实现受控GOP Blt后端，先编译验证不绕过写屏守卫

状态：accepted（host/目标对象，非固件集成或实机），2026-10-23。用户继续屏幕诊断；复用锁定DarwinBoot字模，独立EnumaScreen文本/hex/十二行快照，caller提供矩形、scratch及显式默认关闭写开关；单行一次Blt，不直接访问帧缓冲。范围/模式/错误锁存/重入及EFI64位显示等真实UEFI头sanitizer、AArch64 COFF通过。仅对象编译，memset运行时及全固件链接待接入验证；不放宽GOP/实际几何/像素范围前置条件，不撤SimpleFb/Probe守卫。今晚82ce8a5三候选不改，未查设备或启动，无新地址/内存/verified/R-002变化。

## D-049 · 系统卷采用官方分层路线，先闭合发现与板级内核，再只读存储和用户态

状态：accepted（预研，非分区写入或系统可启动证明），2026-10-23。用户要求预研系统卷、内核和iOS系统；保持iPadOS17.7.11/iPad7,1。固定12份源码Git blob和SHA审查，分清FAT载荷、SHNGROOT OS/SystemOS与Data；发现userdata dry-run未比较展开容量，NativeUfs硬件路径含SM8550、原生root还有PMGR集成检查。先复用工具/算法/测试，SM8250时钟/PHY/SMMU/驱动和本机GPT/UUID另验；nuwa仅提供initrd组合风险思路，不继承v4/地址。内核归档/prelink/完整ADT与Data seed来源仍缺，不把通用bootstrap或菜单当系统通过。未下载大镜像/构建系统卷/改board/操作设备，无新增审批；持久Data/覆盖userdata仍须具体审查。见operations/2026-10-23-system-kernel-userland-roadmap.md及reports/enuma-system-roadmap-audit.json。

## D-050 · 配置专用FAT与真实源平台链接

状态：accepted（离线产物/CI实现，非实机或macOS结果），2026-10-23。用户要求按推荐继续；复用固定write_volume生成64MiB仅reset配置卷，双FAT校验后清空空闲簇解决已观察尾部非确定字节，双构建及mcopy回读通过。未接publisher/打包boot，输入可取消倒计时故不称看门狗。以固定sheng通用build-arm-driver配方补两平台归档，CI platform模式先generic编译记录再crypto/pthread/平台归档及defconfig真实链接；不带sheng板参，不改board归档opt-in/prelink或内存/verified。53项Python/六份配方通过，实际CI另记；无设备操作，晚间候选不变。见operations/2026-10-23-discovery-volume-platform-link.md。

D-050补充：实际CI39926725474停在第4步ArmDTPlatform的未知warning选项，不是源码ABI失败或完整链接失败。允许对本仓临时构建副本应用精确hash锁定兼容补丁，仅移除不受Apple Clang支持的-Wno-unnecessary-virtual-specifier，保留-Werror/其余选项；原参考源码不变，严格apply及输出hash通过。前三步真实通过，四归档/平台链接仍待重跑，不提前宣称通过。

D-050实证补充：修复后CI39927966148/head250cdf9实际success，五步骤/四归档和既有defconfig源平台链接通过。下载kernel21417672B/b940f550…c6052d经本地固定NativePrelink复核普通ARM64、入口文件支撑、4K TCR与三平台符号；run/head/patch/feature一致。只证明源链接，非provider初始化/crypto自检/预链接/硬件或用户态；正式board archives/opt-in后续接回。设备零动作、内存/example/verified不变。报告reports/enuma-platform-kernel-ci.json。

## D-051 · 外置摄像头留证，先单笔早期对照并核实自行恢复

状态：accepted/首笔实机恢复通过，2026-10-23。用户授权本机USB相机读取后又授权启动；只执行既有early-control-2s，录像先于runner/设备动作。独立核对身份/root/槽/解锁/原摘要和备份，临时boot后自行回Android/root/原摘要，用户确认无按键。摄像头证明抽查时的显示状态，不替代SEC/DXE执行日志；定时返回不等同目标门命中或SimpleFb/GOP成功。目标2/7/2未开始，逐笔门禁保持，原始录像不公开。

## D-052 · 依据完整GUID的2/7/2延时响应推进返回层探针

状态：accepted/point20时序证据，2026-10-23。用户继续实机并要求自行录像，三笔ADB16.065/21.482/16.069s、Android/root/原摘要恢复通过，明确无按键；5.417/5.413s差支持目标PE调用前到达，不外推构造器/主体/GOP。一次启动前身份拦截独立计数，普通reboot恢复后新会话完整门禁通过才重试，无校验放宽。下一层复用point21，不改metadata/Probe守卫或内存；无返回即停追加先恢复。手机录像仅实际出现看不清日志时请求。

## D-053 · 用直接PE返回时序推进状态与GOP检查，保持绘制守卫

状态：accepted/point21时序支持，2026-10-23。两份同82ce8a5/同源候选仅改detail21与2/7延时，实际构建/FD/30OEM/v3通过；2/7/2 ADB16.102/22.565/16.081s，三笔Android/root/原摘要且用户确认无按键。直接入口返回门接受任意EFI状态，响应支持包装器返回但不证明EFI_SUCCESS/GOP。差6.463/6.484不是精确5s，保留噪声。下一层先16/17成功失败或明确状态/实际GOP元数据，不直接放行菜单，不撤Blt/Probe守卫；无内存/verified/OEM/源码变化。

## D-054 · 以互补状态门确认最终非错误返回，再直接观察GOP协议

状态：accepted/状态分类时序支持，2026-10-23。17/16/17同源候选ADB16.057/22.524/16.082s，三笔恢复Android/root/原摘要。17语义为非错误而非数值0，16长返回仅支持未观察命中/完成兜底；不称精确5秒差。固定源码正常路径在GOP安装后返回，故有间接安装路径支持，但实际句柄/provider/QueryMode与scanout均缺，下一步只读协议审计，不撤禁绘制/Probe守卫。147 host回归/实际构建与串行workspace通过，无新内存/verified/OEM变更。

D-054用户补充确认：三次状态分类均未按电源或音量键，结合既有Android/root/原摘要证据记为自行返回；不改变GOP运行时快照及数值EFI状态仍缺的限制。

## D-055 · 只读GOP变体未返回，隔离新增调用与依赖后再试

状态：accepted/实机失败并已人工恢复，2026-10-23。查询变体安装后只读枚举/核对/QueryMode，保持禁绘制和驱动成功返回；Core状态门隔离避免误判。但第一笔未自动返回，不能从主机/对象/完整构建通过推出GOP运行结果。依硬停规则不启动互补镜像；恢复Android/root/原摘要已核验。下一步离线拆分新增库/构造器、调用前、枚举/查询/释放与复位路径；优先复用已验证Core门，尚未生成新拆分候选。

用户指出无渲染时无需持续录像，采用必要截图/主机时序；恢复动作或实际屏幕变化再录像。右上角电源键清晰可见动作可直接作证，不从遮挡/无画面推断，不重复询问已有证据的按键事实。

## D-056 · 用非错误阶段标记复用Core门，先恢复返回基线

状态：accepted/离线实现，2026-10-23。用户要求离线拆分并优先复用已验证Core门；完整根因尚未知，先取消SimpleFb新增本地Timer/Reset依赖，warning1/5标记到最终Core返回门精确匹配，保留已发布驱动驻留及安装前原错误路径。拆为安装后控制、枚举/释放、句柄、Mode、QueryMode五层；首两层已实际构建打包，所有新层均未实测。137/30/6/7主机检查、四对象、177 Core回归和串行workspace通过；elish同SoC来源仅借鉴职责分离，不移植写屏/地址。D-055故障事实与恢复证据保留，其“尚未生成拆分候选”阶段已由本轮实现取代。

未来先step0受控返回再考虑step1；任何无返回停追加，不把同步兜底当异步看门狗，不把warning传输主机通过当实机证明。

## D-057 · GOP拆分前两层受控返回，保留目标门证据边界

2026-10-23。用户明确授权先核验、step0受控返回后step1，并确认在场。两次ADB16.906/15.844秒、完成/root/原摘要通过，分别确认全程未按键。支持新Core返回路径和枚举/释放整体返回，不以单次短时序唯一确认目标门或数值GOP成功。旧250849f根因仍未定，step2及后续未运行，写屏/内存/verified边界不变。证据：operations/2026-10-23-gop-split-device.md、reports/enuma-gop-split-device.json。

## D-058 · step2受控返回，step3超时后停止追加并恢复

2026-10-23。用户要求继续直到进入XNU；依既有规则完成step2/3逐笔构建和测试。step2无按键自行回Android，step3在75秒内无返回，立即停止追加，人工恢复后21:27:29主机核验通过。先离线细分Mode/Info与后续路径，不以短返回或静态反汇编证明具体字段正确。step4未启动，内存/verified/写屏门禁保持。donor解压及三组绑定计划通过，仅离线比较参考slide，不采用板级放置或emit镜像。证据operations/2026-10-23-gop-step23-device.md。

## D-059 · 人工恢复后持续离线迭代，按读取边界拆分 Mode

2026-10-23，用户明确要求人工恢复后无需整轮硬停，直接离线分析并出新软件；取代 D-058 中将恢复后作为工作停止点的解释。保留超时立即停止追加启动、先恢复和原摘要核验，不原样重试失败镜像。固件26b1f99新增step5（指针存在）、step6（Mode头）、step7（Info字段）；旧0–4语义不变。先构建同源step2对照和step5；两者仅阶段宏不同。240主机用例在O1/Oz和ASan/UBSan通过，含不可访问Mode/Info指针的提前退出检查；七对象、48标记及六Mu传输检查通过。不能据此证明实机读址安全。无QueryMode调用、显存写入、新内存字段或verified变更。

## D-060 · 固件仓维护编译入口，设备仓保留契约与设备操作

2026-10-23，用户询问应将固件编译移到uefi-enuma。实际编译实现和preflight桥迁入固件仓Resources/Scripts，设备同名脚本仅在核验固定提交、清洁状态和所有锁定文件摘要后加载。显式device-root提供board、依赖锁、上游资格检查和out输出位置；不声称脱离设备契约独立构建。Android boot打包、实机/备份/恢复仍归设备仓。迁移前后用相同step2/5全链接对照核验，不把目录迁移当硬件修复。

2026-10-23 · D-061：step6仅新增Mode头读取，实际链接在Info解引用前退出；实机无按键返回。支持继续单独Info字段探针，不外推数值GOP或scanout正确。

2026-10-23 · D-062：step6/7逐层无按键返回后，在当前00ddc01源码构建完整跨度step3，用于隔离剩余检查与布局差异；不是重试原失败镜像。仍不解引用显存、不写屏，原故障PC未知。

2026-10-23 · D-063：完整跨度新候选受控返回后，优先核实显存映射和最小写屏/直接日志通道，不将完整QueryMode当所有早期绘制的必经条件；nuwa仅复用设计，板级参数须独立验证。

2026-10-23 · D-064：32bpp诊断PCD不视为scanout证据。新只读管线描述先确认地址/pitch/格式/压缩；亮条须在较小splash范围内保存恢复，不直接打开整屏日志。

2026-10-23 · D-065：静态内存表不覆盖MDP寄存器，scanout动作前停止；完成离线覆盖审计和未应用最小映射补丁，以R-004申请精确范围。没有用实际故障启动代替映射核验。

2026-10-23 · D-066：用户明确批准R-004后，仅staging加一条MDP设备映射，保持迁移表及所有RAM字段。映射对照和step8均无按键返回；step8长时序仅提示兜底，先同源互补返回门分类，不外推活动管线/颜色或写屏。

2026-10-23 · D-067：R-004互补selector2短返回、selector1长返回，三笔均无按键恢复。时序支持严格描述拒绝，不将其当MMIO故障或真实scanout证明。下一步先拆分候选存在性与几何/格式，保持只读范围。

2026-10-23 · D-068：用户明确指出受控恢复的条件拒绝不需硬停；继续只读step9。它仅检查八个SRC0_ADDR的splash区间存在性，最多八读，不读尺寸/pitch/格式；不证明唯一性、活动性或完整跨度安全。R-004映射/内存/verified不变。

2026-10-23 · D-069：用户要求每次硬停当轮落实文档，尤其HANDOFF和STATUS。已固化为AGENTS持久规则；停点需包含原因/状态/进度/证据/继续条件，恢复后及时更新。条件拒绝正常恢复不虚构为硬停。

2026-10-23 · D-070：本次失败在不读MDP的step3对照，停止所有新实机候选并先恢复，不能跳过对照直接跑step10。恢复后继续离线隔离，不原样重试；不得从构建通过推定运行成功。

2026-10-23 · D-071：恢复核验通过后立即持续离线工作；实际FD解包差异不足以认定新增格式代码回归，先控制编译时间/布局变量，准备新step0基线，不原样重试失败镜像。


2026-10-23 · D-072：同输入双构建验证SEC载荷一致后，使用新f15d520的step0隔离安装/返回路径；根因未知，不原样重试step3或绕过对照执行step10。


2026-10-23 · D-073：新step0受控无按键返回后，以同源step9作为step10的MMIO对照。两者编译路径均不执行EnumaGopAudit，避免把无关的完整Mode审计设为必经条件；失败step3仍未修复，不隐去失败。


2026-10-23 · D-074：step10无按键短返回后，新增step11仅核对1600x2560/pitch6400/四字节对齐和完整跨度边界，最多24读。既有格式/严格描述语义不变；先构建同源格式对照再step11。拒绝受控返回不硬停，实际超时按AGENTS落实恢复和交接。


D-075：互补时序支持固定几何假设拒绝后，采用只读实际描述解码，正确区分stride低半字及裁剪；保持旧step11语义，不把放宽假设写成旧测试通过。新step12仅证明存在自洽有界候选，不证明活动性或允许像素写入。


2026-10-24 · D-076：用户要求“下一次硬停前落实所有文档”。即日起下一笔实测前先更新并提交推送AGENTS、STATUS、HANDOFF、WORKLOG、DECISIONS、NEED-REVIEW、PENDING-HUMAN及适用的NEED-HUMAN/入口文档。当前事实全文重写，不用追加旧状态代替对账；历史仅在WORKLOG/operations保留。实际硬停仍须同轮记录并恢复后刷新。


2026-10-24 · D-077：step12支持有界描述后，准备小白条事务以取得屏幕观测，但R-004明确仅只读，像素实验单列R-005。先完成假显存/对象/CLI/保护启动门禁与完整候选资格，再给出精确摘要请求批准；审批tag不等于许可，pending或摘要不匹配必须在任何设备命令前拒绝。

2026-10-24 · D-078：用户再次明确“下一轮实机验证之前落实所有文档”。本轮只完成离线核对与文档发布，不运行设备。所有当前入口必须区分最近实测7dc3bf1、旧4db离线对照以及当前c73eb6e待重建候选；旧镜像不能替代新源码同源对照，R-005仍pending。编译旗标接线与保护FD审核策略修正不产生执行批准。

2026-10-24 · D-079：接手用户明确“批准R005”，记录为上述128x8/500000us保存恢复实验批准；精确摘要待新同源构建资格后绑定，不重复申请。当前未新增设备动作，不扩大内存/verified/分区范围。

2026-10-24 · D-080：两候选以相同c73eb6e与62项源锁完成完整离线资格，批准绑定唯一step13镜像c81def7d…5df534；先实测同源只读step12，再按已批准范围单次像素事务。固件主分支71cd5cb仅更新批准文档，运行子模块保留c73eb6e，避免把文档提交当新固件实测。

2026-10-24 · D-081：当前c73eb6e同源step12已无按键受控返回，满足R-005对照前置；继续已批准step13一次，启动前连续摄像并逐笔即时门禁，不把对照返回当像素成功。

2026-10-24 · D-082：单次R-005受控返回但视频未确认白条，键盘反光不作设备输出。批准已消耗，明确账本consumed并回归拒绝重放；不把返回时序当像素或读回成功证明。设备恢复正常不虚构硬停；继续离线同SoC显示活动/面板状态分析，未来像素操作须新的明确范围。

2026-10-24 · D-083：白条未确认后先分离DSI时序使能与SSPP描述/路由；固定同SoC elish仅提供元数据/缓存思路，SetMode无实际显示初始化，不引入其整屏清零。后续只读两接口使能，计数须先验证count-enable；没有数值活动证据前不选定IOVA或面板根因。

2026-10-24 · D-084：按用户明确指令实施338db59 step14，复用既有R-004映射和Core warning门，严格两读/nonzero谓词；不启用counter/像素/新库。三份同源候选仅step/query不同，step12对照后正/互补逐笔核验，完整文档提交推送后直接临时boot。R-005历史资格源锁冻结c73eb6e且consumed不变。

2026-10-24 · D-085：338db59同源step12无按键受控返回且独立恢复门禁通过，按用户既有授权继续step14/query1，两读范围与禁写保持；每笔前对齐提交推送当前文档。

2026-10-24 · D-086：step14/query1短返回且恢复核验/无按键证据通过后，继续同源query2互补分类；单笔短时序不当作两个寄存器数值或活动scanout证明，不扩大读取或任何写入范围。

2026-10-24 · D-087：三笔同源对照/正/互补均无按键恢复并后置核验；query1短/query2长支持至少一接口时序使能非零。差6.375秒包含启动路径噪声，不称精确5秒、直接数值或活动scanout；下一步离线核对count-enable/有界计数增量与路由，不扩大到像素或寄存器写入，R-005仍consumed。

2026-10-24 · D-088：按用户明确授权实施计数配置与有界计数增量只读探针，保留既有映射/内存/verified和consumed账本。只读成功仅支持谓词，拒绝不证明不活动；存在非原子/近回绕复位歧义。五份同源候选逐笔文档推送、即时门禁、受控返回与独立恢复/无按键核验后推进，超时停追加先恢复。

2026-10-24 · D-089：当前不切换Tlrenhb的Boot v1路线；保留已实测v3作为单变量计数探针载体。启动格式被接受不等于持续显示交接已证实，后续单独核对实际DTB/vendor_boot/cont_splash路径；只有格式相关或可对照因果证据才另设计v1比较。评估其ADT/trust/prelink与同SoC索引，不借用板级内存/分区/verified或实测结论。

2026-10-24 · D-090：采用明确的显示故障优先级与可推翻条件。完成当前计数验证后优先活动路由/实际状态，逐项区分SSPP描述合法、挂接、进展和面板可见性；不因返回正常或CI绿色推断显示成功，不直接切Boot v1试错。

2026-10-24 · D-091：counter-control无按键受控返回及独立恢复核验通过；按D-088范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-092：counter-ready无按键受控返回及独立恢复核验通过；按D-088范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-093：counter-not-ready无按键受控返回及独立恢复核验通过；按D-088范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-094：counter-progress无按键受控返回及独立恢复核验通过；按D-088范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-095：counter-no-progress无按键受控返回及独立恢复核验通过；按D-088范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-096：按用户指令继续取得有效增量，固定小米原生v1 get_status而非重复旧Linux完整配置判据。D-083关于计数前置的实施解释更新：读取enable并核对稳定性，不把低两位必须等于3当所有原生观测的先决条件；原生驱动在INTF_STATUS bit0活动时读计数。旧step15/16保持原义和拒绝证据。新step17/18只读现有映射，major6门、两窗同接口严格递增/不回绕/稳定配置，不放宽成功标准迎合目标；全部审计/文档推送后直接临时boot，恢复和R-005 consumed边界保持。

2026-10-24 · D-097：native-active无按键受控返回及独立恢复核验通过；按D-096原生状态/双窗范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-098：按用户明确指令，把结合本机证据和公开源码进行较大胆、可推翻的故障主判断列入AGENTS持久规则；保持事实/假设和置信范围区分，按最有区分力的观测推进，不因大胆判断扩张设备授权。

2026-10-24 · D-099：native-progress无按键受控返回及独立恢复核验通过；按D-096原生状态/双窗范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-100：native-no-progress无按键受控返回及独立恢复核验通过；按D-096原生状态/双窗范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-101：双窗推进后优先检验首个合法描述是否在DSI-selected CTL/LM中staged，并把推进绑定到该CTL选择的同一活动DSI。使用本机FDT偏移与固定小米位表，拒绝换候选以迎合通过。staging/接口选择可能残留/shadow，不把关联冒充完整LM/pingpong/DSC/fetch/可见路由；正互补只判综合谓词，失败后仍拆分拒绝条件。禁写/consumed/内存/verified与逐笔文档/恢复门禁保持。

2026-10-24 · D-102：route-control无按键受控返回及独立恢复核验通过；按D-101候选staging/所选DSI范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-103：route-associated无按键受控返回及独立恢复核验通过；按D-101候选staging/所选DSI范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-104：route-unproven无按键受控返回及独立恢复核验通过；按D-101候选staging/所选DSI范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-105：按用户“可以开始实机工作了”，优先拆分首候选源/输出尺寸和关联LM矩形包含关系；step20严格保留step19关联/递增/稳定门控，只增三字读取及每窗复查，上界250读/两次Stall。配置几何通过不称scaler/decimator、排除区、遮挡或物理输出/fetch/可见性证明；拒绝需拆分条件。R-005 consumed、禁写/内存/verified边界和逐笔文档推送不变；摄像头由代理自行旋转后判读。

2026-10-24 · D-106：geometry20-control无按键受控返回及独立恢复核验通过；按D-105配置输出矩形/所选DSI范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-107：geometry20-contained无按键受控返回及独立恢复核验通过；按D-105配置输出矩形/所选DSI范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-108：geometry20-unproven无按键受控返回及独立恢复核验通过；按D-105配置输出矩形/所选DSI范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-109：几何获支持后优先用保守单源/无dim/BASE或精确常量opaque模式区分局部混合配置；不能只查其他SSPP，因为dim/color-fill可在无SSPP时遮挡。沿固定小米major6 packed alpha和enuma11偏移，step21上界289读/两次Stall、首候选/首关联不替换。拒绝可能为合法其他alpha模式或未知/边框字段，不直接称透明/遮挡；通过也不称真实路由/fetch/可见性证明。旧资格、consumed账本、内存/verified/分区及逐笔文档/恢复门禁保持。

2026-10-24 · D-110：blend21-control无按键受控返回及独立恢复核验通过；按D-109保守单源/无dim混合范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-111：blend21-single无按键受控返回及独立恢复核验通过；按D-109保守单源/无dim混合范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-112：blend21-unproven无按键受控返回及独立恢复核验通过；按D-109保守单源/无dim混合范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-113：用户要求更大胆推进后，优先提高取证区分力：一步六类采样+正反编码，保持既有Core marker、源选择和只读范围。每笔<=289读、两次100ms采样等待加一次<=20秒编码等待，原75秒观察不变；正反8秒间距残差<=2秒/各自对照预测<=2秒/合计20秒残差<=3秒且无按键和独立恢复才接收，否则unknown。边框单独偏离视为可推翻step21观察器过严的证据，不等于屏幕修复；dim/alpha/其他字段均直接推进具体解码，不称可见性。R-005 consumed和全部原内存/verified/禁写/逐笔文档恢复边界保持。

2026-10-24 · D-114：reason22-control无按键受控返回及独立恢复核验通过；按D-113六类正反编码范围推进或完成本轮互补分类，单笔时序不当数值/可见输出证明。R-005 consumed和禁写边界保持。

2026-10-24 · D-117：step22新通道超时，旧短等待同源基线正常；先隔离新增长Stall和完整采样路径，不把失败归因面板。正向冻结不原样重试，反向取消，类别unknown。人工恢复及独立核验后自动继续离线修复，恢复已完成不是整轮结束；回到已验证两次短等待并拆单一staging门控，新资格/文档/恢复条件后再测。

2026-10-24 · D-118：恢复独立核验通过后不结束工作，采用最小隔离新软件：从已验证step20只增sole-staging本地解码（允许原生border位），不读取任何新显示地址、不长等待、不采样dim/alpha。独立验证观察器过严/额外staging假设，<=250读/两次100ms。step22正向与未执行反向冻结，超时原因仍未知。三份资格/逐笔文档推送/即时恢复门禁不变，R-005 consumed及内存/verified/禁写边界保持。

2026-10-24 · D-122：隔离新软件的同源step20也超时且SimpleFb .text与成功基线一致，撤销把step22新增逻辑视为唯一故障因子的假设。新证据优先转向恢复后启动状态/PCD/有效载荷差异和更早执行定位；先完成离线差异解析，不追加显示探针。用户两次恢复独立核验通过，恢复后继续离线规则有效；当前所有未执行候选冻结，不原样重试失败镜像。

2026-10-24 · D-123：标准调试字段规范化后两项差异PE完全一致、头/shim相同，进一步下调构建有效代码/PCD回归；优先运行启动状态/ABL及早期执行位置定位。保留FD容器原字节差异与无早期执行日志限制，不把二进制近等价当整机确定性保证。两次人工恢复后均继续完成离线新软件/审计及分析，无新显示启动、所有取消候选冻结。

2026-10-24 · D-124：热状态重跑曾成功的geometry20-control（`20f079b4…`）在未断电、恢复后约14分钟的同构前置下自动返回（adb 16.962秒/完成31.221秒），排除"人工恢复后设备残留状态"；同一条step20/query1谓词今日为3成功1超时。超时必为挂死——DxeCore仅在StartImage返回后按status选门，query1/query2各自编码都未出现。只剩ResetCold/PSCI出口失效（中高）与SimpleFb MMIO读挂死（中）两候选，现1 bit通道不可区分。取消断电冷启动那一半；下一步以无显示MMIO、无等待的早期停止点候选重复多笔区分，不追加显示探针，不重试冻结镜像。

2026-10-24 · D-125：R-006候选A落地为exit10-early，`ENUMA_DIAG_STAGE=10`（`CoreDispatcher()`之前）——该点尚未派发任何DXE驱动，SimpleFbDxe虽打包但永不执行，`0x0ae00000..0x0ae84207`一次不读，故本笔只检验`MicroSecondDelay`加`ResetCold()`出口。固件源码不变（仍c45e52a）。因backend对stage!=13的互斥，detail point退化到13且去掉GUID/完成兜底/GOP查询，但这些路径全部在stage13之后才可达，不构成运行期变量——不称其为step20同源对照。构建/FD审计/Boot v3回环通过，30个OEM PE/DEPEX不变。doc/环境修复（tomli、固件仓子模块、staging旧symlink指向nuwa）不改变固件内容。

2026-10-24 · D-126：R-006候选A执行完毕，exit10-early（stage10、无显示MMIO、无等待）5笔全部自动返回、0挂死；delay2四笔adb 15.918–17.007（极差1.089秒），delay7正对照21.277，延时+5秒对应adb+4.270秒，先把"checkpoint确实执行并复位"立住，否则"回到Android"与"根本没复位继续启动"不可区分。统计限制：15%单笔挂死率下5笔全干净先验概率44%，本批只排除高失败率，不排除早期出口偶发挂死。据此超时推向派发之后的显示路径，主判断为MDP域未上电时首次访问挂AHB（可解释历史S-001/250849f/S-002/S-003同现象且与读取寄存器数无关），下一步做只读1个VERSION字的最小MMIO候选。

2026-10-24 · D-127：R-007最小MMIO候选不新写step，改用现成step14（仅两次只读0x0ae6b800/0x0ae6c000），因为它与失败笔的stage13/GUID/detail16/fallback完全同构，唯一变量是探针深度，比新写step24更干净且无需新资格链。打包PE静态反汇编确认两次目标读、零目标写。判据三分类按时间：PASS立即复位、FAIL走7秒completion fallback、挂死75秒无返回。同时修复audit_enuma_fd.py的args变量污染bug（step14分支），审计语义不变。

2026-10-24 · D-128：exit14-minimal（step14，两次读）第1笔即挂死，与同期exit10-early（0次MMIO读）5笔全干净构成强对照，故挂死点定在首次触碰显示窗口而非读深度，主判断升为高置信。此profile带7秒completion fallback，PASS/FAIL都会回Android，无返回只能是挂死。新增状态假设：早期复位使XBL/ABL认为显示已初始化、下次启动跳过初始化，UEFI读落入未上电域并挂总线；该假设可解释S-001/250849f/S-002/S-003反复出现。恢复后以完全断电冷启动+同一镜像单笔作为判别实验。当前硬停，未执行第2-5笔。

2026-10-24 · D-129：完全断电冷启动（关机后直接进bootloader、不经Android）仍使step14两次读在原点位挂死，D-128的启动序列假设作为挂死原因被证伪。全天读窗口账本：15:06-16:02七笔0挂，16:03-17:38五笔3挂，17:15-17:24不碰窗口五笔0挂。主判断改为：16:03后该设备对显示窗口的读取不可靠且冷启动不能恢复，读2个寄存器即挂。推论：恢复可靠访问前不得再以"读到什么"作为显示结论，23个step的布局/几何/混合判断需标记为受此污染；暂停增加读取型探针。下一步按序断电静置、离线核实XBL/ABL显示初始化、必要时申请显式上电确认。

2026-10-24 · D-130：读显示窗口挂死定位为unclocked access而非代码缺陷。现场证据:停在fastboot时屏幕显示橙色FASTBOOT字样,显示域为on;`fastboot boot`后固件读同一窗口即挂,两者只差"退出fastboot移交控制权"这一步。公开来源三条吻合:Qualcomm官方bus-hang示例(unclocked MDP read即挂总线并复位)、BSP记录(XBL在EnterFastbootExit关闭Display并释放framebuffer、不恢复待boot状态)、SM8250 dispcc属MMCX电源域需显式上电(disp_cc_mdss_ahb_clk为访问开关)。本仓simplefb变体还排除了唯一可能初始化显示的OEM DisplayDxe。故固件读MDP前无人上电,读本身非法。**据此23个step的scanout结论证据等级降为未知**,含16:38唯一成功,需在正确上电后重做;15:06-16:02七笔干净仍无法解释,保留未知。暂停读取型探针,下一步A(stage4最早点对照)/B(固件显式上电,需新授权)/C(转日志通道)。

2026-10-24 · D-131：核对同项目nuwa的做法后新增候选D并调整优先级。nuwa的UEFI不在项目代码里读MDP：UniXNU-nuwa仓grep不到MDP/mdss/0x0ae相关代码，显示全部由厂商预编译DisplayDxe承担（Binaries/nuwa/QcomPkg/Drivers/DisplayDxe/DisplayDxe.efi 380928字节，patched版与之仅差33字节），该二进制内部完成MMCX/GDSC/时钟/DSI初始化并建立GOP。enuma原厂路线亦然（firmware/docs/enuma-overlay.md载明GOP使用本机DisplayDxe、CPRDxe与K81 XML）；只有诊断simplefb变体故意排除CPRDxe/DisplayDxe/UFSDxe、换metadata-only SimpleFbDxe，正是探针读MDP挂死的环境。故新增候选D：不排除OEM DisplayDxe（连同CPRDxe一起放回），由厂商驱动完成上电后再读，不需自写任何寄存器写序列。D优先于B（自写上电），因为厂商序列已知且经过原厂验证；代价是DisplayDxe会建GOP并可能绘制、污染待观察屏幕，且enuma原厂GOP成功率未实测，需先验证其能否起来。

2026-10-24 · D-132：候选D三门对照(成功detail17/失败detail16/任意返回detail13)返回时间31.924/30.878/33.052秒,无7秒差异,三门均未命中;因detail13对任何status都命中,故只能是CoreStartImage从未对该GUID触发——DisplayDxe从未被派发。解析其depex为8个protocol全AND,其中157a5c45为Qualcomm EFI_PLATFORMINFO、b0760469见QcomPkg.dec,其余6个未在自带源码定义;而33个OEM驱动中无MDSS/MDP/DSI/panel类驱动。结论:靠保留OEM DisplayDxe无法上电,依赖永不满足,屏幕不亮与三门不命中同一原因。下一步D1(从XBL补齐protocol提供者)/B(固件自写上电)/C1(UART)。

2026-10-24 · D-133：UART路线判定为不具备条件，改以Linux作为信息通道。公开资料核对：enuma原理图与位号图确实存在(devicedb.xyz,250RUB付费,约20元,含Schematic.PDF与BoardView.PDF)，故"完全查不到硬件资料"不成立；但即便购得，UART仍需焊接、判断电平并核实GENI实现，属硬件操作，无硬件人员支持时不建议推进，C1(原R-003的B路线)据此判定暂不具备条件。替代：enuma已有成熟Linux支持(xiaomi-enuma-dev/droidian状态表Display/Touchscreen/Brightness/USB Networking均Work；同板WiFi版elish有postmarketOS主线支持，device-xiaomi-elish，内核6.17)，可用fastboot boot临时启动Linux并以USB networking取完整dmesg，从而(1)验证MDSS/DSI硬件完好、(2)取得dispcc/GDSC/MMCX实际上电序列(即B方案所需信息)、(3)必要时以devmem现场读0x0ae6b800。局限须写明：那是Linux日志而非UEFI日志，UEFI阶段早期黑屏原因仍须靠stage4读或跨复位内存日志判定。Linux方案不需硬件图、不需拆机，优先级高于购置原理图做UART。

2026-10-24 · D-134：A实验的实现受两处固件约束，本轮先恢复到可用状态。①SEC模块不继承ENUMA_DIAG_*宏：实测SiliciumPkg/Sec/Sec/Sec.makefile中不含任何ENUMA_DIAG定义，故stage4-8的EnumaStageCheckpoint在SEC内恒为ENUMA_DIAG_STAGE==0的短路路径，历史上从未生效，也无人用过——这也解释了为何早期停止点实验一直从stage13起。②补丁链耦合：在dxe-stage-checkpoints.patch内插入读操作会改变后续dxe-dispatch-return.patch的上下文，导致其apply失败；独立patch又因在补丁序列中位置不同而上下文不匹配；另有一次因Python write_text把patch写成CRLF被git apply判为corrupt。结论：A改为stage10（DxeCore宏有效、stage13复位多次成功、此时R-004设备映射已建立故挂死不能归因未映射），读操作以独立patch放在补丁序列末尾（dxe-dispatch-details之后），上下文只取EnumaStageCheckpoint(10)与CoreDispatcher()两行。当前dxe-stage-checkpoints已恢复原样、migration/lock/子模块已重同步，stage10构建通过(FD 10bbfbb8)，不含读操作。

2026-10-24 · D-135：A/B两笔对照闭合,读窗口时机定案。**A**(读0x0ae6b800/0x0ae6c000,置于EnumaStageCheckpoint分支内)19:20:36正常返回16.975秒;**B**(同位置读0xdeadbeef)19:26:55挂死。B挂死证明读确实执行,故A的正常返回证明**显示窗口在stage10仍可访问**。**推翻了此前"XBL在EnterFastbootExit关闭显示、域在我们接手时已关"的解释**;unclocked access致挂的机制仍成立,但时钟被关掉的原因是本固件内部。连带:不需要补OEM protocol提供者、不需要自写MMCX/RPMh上电序列——域交给我们时本来就是开的;方向改为在派发前读取,或定位派发中关域的那个驱动;23个step在派发后读,证据等级维持未知但成因已解释;历史上的间歇性成功与"读恰好落在teardown之前"一致。下一步用同样两读在stage11(CoreDispatcher返回后)二分。

2026-10-24 · D-136：stage11二分成功(16.984秒),故"派发期间关掉显示域"这一判断亦不成立。stage10(派发前)成功、stage11(CoreDispatcher返回后、即所有驱动派发完毕)也成功,说明显示窗口在整个派发过程中始终可读;派发中唯一会读该窗口的SimpleFb并未被启用读取(本次镜像gop_query=0)。故域从未被关闭,step14在SimpleFb中读0x0ae6b800挂死的原因不能归为"域被关",而应归为**该读在SimpleFb上下文里本身不合法**。最可能的具体原因:stage10/11的访问走SEC/早期1:1映射(属性正确),而SimpleFb走R-004新增的Display MDP映射,若该映射把Device memory映成Normal cacheable,ARM上访问会abort/挂死;另一候选是派发期某驱动改写了内存映射使R-004失效。下一步:审display-mdp-map.patch的内存属性并与Linux DTS的mdss dma-ranges/bus-range比对。上一条D-135的"域是我们自己关的"据此修正为"域一直可读,问题在读取方式"。

2026-10-24 · D-137：逐项排除后,把"读挂死"的原因从地址/读法/映射属性收窄到执行上下文。已核实:①step14读的正是0x0ae6b800与0x0ae6c000,与stage10/11读的两个地址完全相同;②EnumaScanoutRead32的实现是`*(volatile UINT32 *)Address`,与stage10/11的写法完全相同;③R-004新增的Display MDP映射属性为MMAP_IO/UNCACHEABLE/NS_DEVICE,与同表其他MMIO一致,属性无误;④R-004的映射实际未被读路径使用(读走的是直接虚拟地址)。故地址、读法、映射属性三项均被排除,剩下的只能是执行上下文/时序。具体机制候选:(a)XBL遗留的显示时钟状态在SimpleFbDxe运行时已失效,而stage11(全部驱动派发完)时又满足;(b)SimpleFbDxe的StartImage内部顺序问题——它是dispatch ordinal 1即第一个被调度的驱动,其读发生在某些必要初始化之前;(c)调度期的SMM或页表状态差异。判别实验:stage12(第一个驱动LoadImage之前)也读同一对寄存器——stage12成功而stage13挂死即锁定到SimpleFbDxe的StartImage内部,stage12即挂则属调度期上下文。依据:EnumaDispatchCheckpoint在ordinal匹配时调用EnumaStageCheckpoint,故stage12可触发同一分支。

2026-10-24 · D-138：stage12实测成功(15.939秒),挂点锁定到SimpleFbDxe的StartImage。三个探针点构成完整包围:stage10(派发前)成功、stage12(第一个驱动LoadImage之前,Dispatcher里)成功、stage13(dispatch ordinal 1即SimpleFb StartImage之后)挂死。故挂点落在[LoadImage + StartImage]区间内,而非地址、读法、映射或调度前状态。下一步在SimpleFb的ENUMA_DIAG_GOP_QUERY块开头(step分支之前)插入一次0x0ae6b800只读:该读挂=读本身在此上下文有问题;不挂=挂在更早的加载或安装路径、根本到不了step的读。

2026-10-24 · D-139：把读放在SimpleFb的所有step分支之前,原始step14(2次访问)挂死变为3次访问(early14)正常返回17.016秒。现象要点:同一地址0x0ae6b800在同一次StartImage里被访问一次会挂、访问两次(前置一次)不挂;而stage10/11/12的同类读都成功。说明该地址在本上下文中的**首次**访问会触发一次性事件(缺页由EDK2异常处理器建立映射、或安全世界切换等),该事件在某些时机下挂死总线;第二次访问因状态已就绪而安全。实用推论:把需要的读整体前移、或在读之前补一次同地址的预热读,可绕开该一次性事件;同时说明"首次访问"是此前23个step反复异常的共同嫌疑点。另记:FD审计按设计抓到了本次偏离(目标访问由2次变3次,报packaged DSI code does not match two read-only target accesses并拒绝出包),据此把审计期望更新为三次,该偏离不是绕过检查而是检查生效的证据。

2026-10-24 · D-140：建立"延时编码"取数通道,首次把显示窗口的寄存器值传出固件。做法:EnumaStageCheckpoint在stage13时先预热访问0x0ae6b800,再读0x0ae00000+index*4的低4位,把该值按每bit一档、每档一秒编码进复位延时(基础2秒);build新增--stop-delay 20档启用该模式,gop_step低3位作index。实测首笔返回22.365秒,相对16秒基线多出6.06秒,对应读到的低4位=6,证明通道可用且主机侧1秒档位可分辨。第二笔同一镜像挂死,需长按恢复,原因待查(不排除与预热读同类的首次访问偶发有关)。这是自23个step以来第一次拿到显示窗口的实际数值,后续可按index 0..7逐个取出8个寄存器(需各一次构建)。

2026-10-24 · D-141：R-007像素白条实验已执行并挂死,画面全程无白条,但读与写的失败模式不同。做法:构建gop_step=13+像素预览+预热读的镜像(FD 86727d1e,镜像ce7f1955),上机前以0.3秒间隔密集摄像220帧。观测:帧0-26为Android桌面(mean121.8,白像素7.0%);帧27骤降至33.1;帧28-30过渡(49.0/58.2/61.5,白像素5.9%/6.9%/4.4%);帧31起稳定为黑屏镜面(mean64.0,白像素2.4%,为反光而非白条)。**全程无白条,且无任何帧出现大面积白色**。关键区分:预热读已修复读路径(early14四笔、step20三笔全成功),但像素写路径仍挂死;而step20同样调用EnumaScanoutFindBoundedDescriptor并成功,故描述符查找本身不是挂死点,挂死落在真正的写动作上,且写目标很可能是错误基址(描述符解出的framebuffer地址若指向MMIO,写它即挂总线)。另记两处构建侧修复:①staging的Mu基线期望是"未打补丁的原始状态",此前我删掉dispatcher-display-read补丁后残留导致7个基线文件不匹配,手工恢复原始态后全部匹配;②EnumaScanoutRead32的定义位于#if ENUMA_DIAG_GOP_STEP==13分支内,像素预览这一档恰好把它排除,预热读因此改为直接volatile访问。

2026-10-24 · D-142：确认本仓没有可搬的显示初始化栈，"点亮屏幕"必须自己写序列。依据三条：①原厂uefiplat.cfg里有EnableDisplayThread=0x1，Qualcomm官方UEFI是开一个独立显示线程并行初始化面板，其实现依赖完整QcomPkg的DisplayPkg(MDP/DSI/panel时序)；②本仓带的QcomPkg是精简版，Library下只有ArmSmmuDetachLib/ConfigurationMapHelperLib/ErrataPatchesLib/PlatformBootManagerLib/PlatformBootOptionsLib/PlatformPeiLib/RamManagerLib/RfsProtectionLib/SmBiosTableLib，**没有任何显示初始化组件**；③从本机XBL提取的33个PE驱动里显示相关只有DisplayDxe与CPRDxe，而DisplayDxe的DEpex要求8个protocol全AND，其提供者不在33个之内(候选D已证伪)。结论：XBL能显示是因为它自带非DXE形态的显示实现，不能直接当驱动搬；因此自己上电(B)必须自行实现MDP/DSI初始化序列。好消息是所需信息已齐备：MDP寄存器窗口0x0ae00000起的布局、两块K81面板XML(CSOT K81_42_02_0a与BOE K81_35_02_0b)、uefiplat.cfg的内存布局("Display Reserved" 0x9C000000+0x02400000，"DBI Dump" 0x9E400000+0x00F00000为MMAP_IO)、以及Linux主线msm_drm/dispcc作为公开参考。配合本次新建的延时编码取数通道(可把寄存器实际值读出)，自写序列的每一步都能被实机验证。另记：SEC侧已有跳过清空显示保留区与跳过MDP SMMU detach的补丁，故MDP的SMMU上下文在固件侧是被刻意保留的。

2026-10-24 · D-143：延时编码取数通道首次给出跨上下文差异。probe0读0x0ae00000的bit4-7成功(返回16.975秒,解码nibble 0,配合此前低4位=6);probe1读0x0ae05014(pipe0的SDE基址寄存器)则直接挂死总线。但step20的完整读取在SimpleFb内部读的正是0x0ae00000+Pipes[i]+0x14(即0x0ae05014)且三笔全部成功。**同一地址在SimpleFb的StartImage上下文里可读,在EnumaStageCheckpoint(stage 13,Dispatcher内)上下文里读会挂总线**,故取数通道不能放在stage检查点里,必须下移到SimpleFb内部(那里读display寄存器已被step20验证安全)。附带确认:0x0ae00000的低4位为6、bit4-7为0,即MDP version寄存器当前值形如0x?06;SDE基址寄存器所在地址在stage检查点上下文不可访问,这既解释了早期"读挂死"的部分现象,也说明MDP的SDE子模块时钟可能未开(MDP顶层可读而SDE不可读),这是自写显示序列要解决的第一件事。

2026-10-24 · D-144：取数点位置决定读是否安全,与地址本身无关。三次实测对比:①stage检查点上下文(EnumaStageCheckpoint,stage13)读0x0ae00000成功(16.975秒),读0x0ae05014挂死;②SimpleFb内部、位置在CreateFrameBufferConfig之后且在InstallMultipleProtocolInterfaces之前,读0x0ae00000(同一个在①里成功的地址)同样挂死;③但early14与step20在SimpleFb内部、位置在InstallMultipleProtocolInterfaces**之后**,读同一批地址全部成功。**规律:stage检查点的读发生在SimpleFb的PE入口之前(detail 16的检查点在PE entry call之前),而SimpleFb内部只有跑过InstallMultipleProtocolInterfaces之后的读才安全**,即CreateFrameBufferConfig与协议安装之间存在一个让显示窗口不可读的窗口期。因此取数分支必须插在InstallMultipleProtocolInterfaces之后,而不是CreateFrameBufferConfig之后——此前把分支放在后者是位置选错。附带:这也解释了为何同一地址在不同上下文表现相反,以及为何"预热读"能救(它把危险窗口之后的读变成安全窗口之后的读)。设备因三次挂死需人工恢复。

2026-10-24 · D-145：取数分支的最终形态与实现过程中确认的构建侧约束。形态：取数分支并入 simplefb-gop-query.patch，位置在协议安装之后、紧跟那条已验证安全的预热读；gop_step 1..7 各读一个地址（MDP version 与前六个 pipe 的 SDE 基址寄存器）的 bit 4-7，用 gBS->Stall(2秒+code秒) 把值编码进额外延时，随后驱动正常返回，由既有的 PASS 门（detail 16）完成复位——**不再自己复位**，因此不需要 gRT->ResetSystem，也就不需要给 SimpleFbDxe 的 INF 加 UefiRuntimeServicesTableLib。基线不变：gop_step=0 时返回 16.7 秒，取数档为 16.7+code 秒，code 即寄存器该 4 位。实现过程中确认的构建侧约束：①hunk 头行数必须与 body 一致，且 git 把完全空行当作"空白上下文行"、把文件末尾换行当作 body 之外的内容（已由 scripts/recount_patch.py 承担）；②gBS 里没有 ResetSystem，只有 gRT 有；③给 INF 加 hunk 会让构建末尾的"patch reversion"断言失败，因为 staging 的 INF 与固件仓不再逐字节一致；④staged 的 Mu 树必须处于"所有诊断补丁已 reverse"的状态，否则 preflight 拒绝（已由 scripts/restore_mu_baseline.py 承担并接入构建前置）。7 档镜像中 step 1 与 step 2 已构建完成，step 3-7 在收尾时被终止，尚未实测。

2026-10-24 · D-146：按接手审计修复诊断证据链。旧delay20宏未进入CC_FLAGS、header默认关闭，历史数值解释失效；GOP_QUERY/detail16是CoreStartImage后返回marker门，旧PE入口前/安全窗口因果解释失效；像素路径Sync/Read在Write前，不能归因为store。D-130至D-145中相应硬件因果/寄存器数值结论superseded，原始观测和失败账本保留。恢复只读核验通过并保留失败result.json。新74598df独立value source/index/shift/code、常量无MMIO、三秒码间距、0/3/0校准与单笔失败冻结；未启用像素/日志/new map/verified/分区。用户确认本轮可在场恢复。证据reports/enuma-legacy-value-contract.json、enuma-recovery-reconciliation.json、enuma-value-transport-host.json和operations/2026-10-24-takeover-calibration.md。

2026-10-24 · D-147：接手复核确认 D-146 的全部指控，并给出独立实证与后续守卫的确切位置。①宏未生效已用编译日志实证：`grep -o "ENUMA_DIAG_DELAY_FROM_DISPLAY" out/firmware-build/logs/firmware.log` 无任何命中，而同一日志里 `-DENUMA_DIAG_DELAY_US=2000000`、`-DENUMA_DIAG_GOP_STEP=0` 等逐项可见，证明旧delay20确实没有取数代码进编译器。②真正传给C编译器的通道是 `Platforms/Xiaomi/enumaPkg/enuma.dsc` 的 `[BuildOptions]` 里的 `*_*_AARCH64_CC_FLAGS`；board 的 `firmware.defines` 只提供 `$(...)` 变量的取值，不构成编译选项本身——此前把新宏只加进 defines 因而永远到不了编译器，这是旧取数结论失效的机制。③新通道 74598df 把 `ENUMA_VALUE_SOURCE/INDEX/SHIFT/CODE` 加进了该 CC_FLAGS，且在 `Resources/Scripts/build_enuma_firmware.py` 里新增构建后守卫：读 EDK2 生成的 `GNUmakefile`，用正则逐个核对 `-D` 的实际取值与 board defines 是否一致，不一致即抛 "value define absent from actual compiler flags"，并把 GNUmakefile、SimpleFb.c、EnumaValueProbe.h 的 sha256 记入 `value_probe_compiled_contract`——同类错误由此不能再靠肉眼发现。④新执行链默认离线校验， `--execute` 一次只跑一笔，0/3/0 校准要求两笔零码漂移与已知码残差都不超过 0.75 秒且三笔同源同 metric，否则拒绝解码并冻结计划；`scripts/run_value_probes.py` 与 `tests/test_recovery_reconciliation.py` 的 83 个单元测试本轮全部通过。结论：接受 D-146 的 supersede 判断，按新通道推进，本棒不再追加显示读点。

2026-10-24 · D-148：新的 value transport 通道机制成立但重复性不成立,校准未通过,不得解码。实测三笔(常量档,全程不读显示MMIO、不做像素或cache访问):zero1 返回 16.991 秒、known3 返回 25.503 秒、zero2 挂死(runner_returncode 2,phase 转 manual-recovery-needed,需人工恢复)。**正面结论**:码3比码0多 8.512 秒,对 3 码×3 秒=9 秒的残差 0.49 秒,在 0.75 秒容差内——"把值编码进复位延时再由主机反解"这条机制本身是通的,且这一条不依赖任何显示访问。**负面结论**:同一候选(zero,同一镜像同一常量码)两次运行一次成功一次挂死,零码重复性不成立,因此按既定判据不能解码,也不能进入寄存器模式。**方法论确认**:上一棒"单笔 22.365 秒即读出寄存器值 6"的误判,根源正是只跑一笔就解读数据而未做重复性验证;codex 坚持先做 0/3/0 校准并要求两笔零码漂移与已知码残差都在容差内,本次三笔立刻暴露了重复性问题,证明该门槛是必要的。附带:为跑通本轮,修掉了 codex 计划工具与现有打包/执行脚本之间的三处接口缺口(capture 未归档镜像、未归档镜像旁的打包报告、capture 不校验归档产物是否属于本候选),并给 capture 加了"归档的 value_probe 必须与本候选常量码一致"的守卫——本次正是该缺口导致一次把 known3 的产物误归档为 zero。

2026-10-24 23:04之后 · D-149：本轮文档/恢复对账取代D-148和b54bb2b中过强结论。8.512秒差值仅为符合预期的延时响应证据；零码第二笔超时使完整0/3/0校准失败，不能解码或宣布通道可靠。75秒无返回未定位到驱动返回、某指令或复位出口；历史公共stage成功不证明一直安全，三类嫌疑非互斥穷尽。目录名非issued_at；zero2发出22:52:12，无返回期限约22:53:27，精确硬停时刻未记录。不能认定此前停fastboot或恢复动作已知。本轮只读恢复核验Android完成/root/A槽/解锁及设备/备份双分区摘要通过，原失败result和计划账本保留；current只通过新证据更新。冻结计划不原样重试，未来用经审新隔离候选。firmware三份在途源码未提交/未资格，本轮保留，不混入文档提交；新增驱动内复位的库依赖/constructor副作用需独立审查，不能直接推断因果。证据reports/enuma-recovery-reconciliation.json、value-transport-device.json及STATUS。

2026-10-24 23:40 · D-150：驱动内复位隔离方案已实验性提交后撤回，理由是现有守卫刻意禁止它。处置：先提交 e5f1ab5（`--value-reset in-driver`，EnumaValueProbe 之后 `ResetCold()+CpuDeadLoop()`，并给 SimpleFbDxe.inf 加 ResetSystemLib），随后 d00c416 撤回，保留同批的 96d354a（Windows 换行修复）。**撤回依据是构建实测而非推断**：WSL 构建跑到 `Resources/Scripts/build_enuma_firmware.py:258` 的断言失败，该断言位于 `if args.diagnostic_gop_query` 分支内，与本驱动绑定三条刻意的守卫——①staging 的 SimpleFbDxe.inf 必须与固件仓源逐字节一致（加 hunk 即失败）；②AutoGen.c 不得含 `ArmPsciResetSystemLibConstructor`；③静态库清单不得含 `pscireset`/`resetsystemlib`。另核：enuma 平台的 dsc（Platforms/Xiaomi/enumaPkg/enuma.dsc 及其 include 的 KonaPkg.dsc.inc/UniXNU.dsc.inc）**没有任何 ResetSystemLib 绑定**，故该方案还需改平台配置。结论：守卫是刻意的——它把 ARM PSCI 复位库及其 FDT 依赖挡在"第一个被派发的驱动"之外；D-145 已因同一约束撤回过一次，D-149 要求独立审查，本次审查结论为维持守卫。**并记**：in-driver 复位本想区分的"驱动返回路径"，用不改守卫的手段（调 marker 门参数、换更早检查点）同样可及，故不构成破守卫的正当理由。撤回后用原参数重建成功（FD 02f8d31d），链路可用。

2026-10-24 23:40 · D-151：本仓固件构建只能在 WSL 下进行，Windows 原生路径不可用，且此前从未被验证。本轮首次在 Windows 原生 Python 下构建，连续撞到两个缺陷：①`(info/'alternates').write_text(...)` 在 Windows 上把 `\n` 转成 `\r\n`，git 读到对象库路径 `.../objects\r`，`update-ref` 报 "object directory ... does not exist"——已修为 `write_bytes`（96d354a），该修改在 WSL 下行为等价；②`link.symlink_to(..., target_is_directory=True)` 需要创建符号链接特权，普通权限报 `OSError: [WinError 1920]`，**未修**。历史上所有"构建成功"记录（含 18:41/18:50/19:19 等）均在 WSL 内完成，故这类缺陷此前不会暴露。本轮改在 `wsl.exe -e bash -lc "cd /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma && python3 ..."` 下构建，环境为 Python 3.10.12 + tomli 已装。附带观察：**同一组参数重建的 FD 与已资格的 zero 候选不一致**（本轮 02f8d31d 对已资格 bfb3d6a6），说明 EDK2 产物在此配置下不可复现，"资格"因此只能绑定到具体已归档镜像（`out/value-transport/zero/candidate.img`，sha256 9b3c1df3…），不能靠重建取得；本轮未把重建产物用于任何实测。

2026-10-24 23:40 · D-152：zero2 的挂死不能归因于显示访问，且当前所有"读挂死"结论都缺一个挂死率基线。机制事实：`EnumaValueProbe` 在 Source==1（constant）时只取 `Code=Constant`，`Code==0` 直接 `return EFI_SUCCESS`，**不调用 Read、不调用 Wait、不写任何寄存器**；zero1 与 zero2 是同一镜像（9b3c1df3…）、同一常量码 0，零读零写零 Stall。既然同一段"什么都不做"的代码一次返回一次挂死，则挂死发生在零读路径上，与 MDP/DSI 显示窗口无因果关系。因此 D-149 的表述（挂死点未定位）应再进一步：**挂死不是读操作的特征**，剩余嫌疑至少包括 fastboot 临时 boot 载体、XBL 侧对临时镜像的处理、以及设备连接/供电的时序差异；这些嫌疑与显示无关。同时必须指出方法论缺口：R-006 自算过 15% 单笔挂死率下 5 笔全干净的先验概率仅 44%，而"0 读 5 笔干净 vs 2 读首笔挂"这一对照由 5+1 笔构成，在挂死率未知时**不构成证据**；unclocked access 主判断（17:45）与 23 个 step 的证据降级都建立在该对照上。旧结论保留为历史观测，不再作为当前判断依据。**下一步实验（不改任何固件）**：用已资格的 zero 镜像（常量 0、零读、marker 门）重复至 8 笔，只统计"返回/挂死"，不解读任何数值、不做校准；目的是给出粗略挂死率，并回答"零读档是否也会挂"。执行仍按既有门禁逐笔核验身份/备份/恢复，失败即停不原样重试。若零读档挂死率与历史"读档挂死"同量级，则以显示为因的整条归因链作废，需按载体/XBL 方向重开；若零读档 8 笔全干净，则只能把挂死率上界压到 ~25%，届时再谈是否需要更多笔数。

2026-10-24 23:40 · D-153：显示初始化所需规格可直接从在连的 Android 内核取到，不需要先 boot 一台 Linux。此前 D-133 把"取 dmesg"表述为需要 fastboot boot 一个 droidian/postmarketOS 镜像，实际上设备常态就是 Android（Linux），`su -c dmesg` 即可，且本轮已取得：面板 `xiaomi 42 02 0a video mode dual dsi cphy panel`、`mi,panel-id = 0x4b383100420200`（K81 + 42 02 0a，与仓内 `Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml` 完全对应，面板型号由此确定不必猜）；时序 `hactive=1600 / vactive=2560`，60/120fps 动态切换；面板初始化量级 `dsi_panel_tx_cmd_set cmds(117)`（60fps）/ `cmds(115)`（120fps）；电源域 `mdss_core_gdsc: supplied by pm8150a_s4_level`，`dsi_phy … supply gdsc not found, using dummy regulator`（即 DSI PHY 电由 mdss_core_gdsc 统管，自身无独立 GDSC）；时钟 `disp_cc-kona af00000.qcom,dispcc`、DSI PLL 0/1 为 7nm 实现、`sde_rsc af20000.qcom,sde_rscc`；地址 dsi_phy `ae94400`/`ae96400`、dsi_ctrl `ae94000`/`ae96000`。未取到：`/sys/kernel/debug/pm_genpd`、`/sys/kernel/debug/dri/0`（本机 debugfs 未暴露）。定位：这些是**自写 UEFI 显示序列的规格输入**，不是设备执行授权，也不改变"固件内不能凭此访问未上电寄存器"的判据。

2026-10-24 23:37 · D-154：单元测试缺陷导致两次非授权设备 boot，记为事故，不作为 R-009 数据。**根因**：`run_next(..., invoke=subprocess.run)` 的默认参数在模块**导入时**求值并绑定；测试用 `patch.object(baseline,'subprocess')` 只替换模块属性，触及不到已绑定的默认值，于是测试真实调用了设备执行器，并同时 patch 掉 `require_published`，使"必须已发布"的门禁也没生效。**后果**：23:31:35 与 23:32:22 各临时 boot 一次 baseline 候选（f5cf62da0b58…）。第一笔正常返回 Android、adb 16.031 秒、双分区摘要未变；第二笔过 75 秒观察期无返回，23:34:54 仍不在 adb/fastboot，需人工长按。**处置**：①`invoke` 改为调用时解析（`None → subprocess.run`），该类 patch 从此有效；②测试一律显式传 `invoke=Mock()`；③测试文件顶部写入"禁止 patch baseline.subprocess"的警告与原因；④8 个测试由（错误地）94 秒真实执行变为 0.026 秒通过，`runner.assert_not_called()` 覆盖离线与拒绝路径。**定位**：这两笔**不是 R-009 数据**——R-009 明确要求逐笔身份/备份/恢复门禁与文档前置，这两笔是在测试中意外发出、且跳过了发布检查。但作为观察值必须记录：零读常量档 2 笔 1 挂，与 zero 组（zero1 成、zero2 挂）完全同形，独立地再次支持"挂死与显示访问无关，量级约 50%"。**教训**：可执行设备动作的函数，其默认参数绝不能绑定真实执行器；测试里"patch 成功但没生效"是静默失败，后果直接落到硬件上。**风险状态**：设备挂起，恢复核验前不追加任何镜像。

2026-10-24 23:50 · D-155：R-009 基线建立——零读档挂死率 12.5%，并据此**修正 D-152 的过度推断**。执行：同一 zero-read 候选（常量0、不读不写不 Stall，FD 02f8d31d，镜像 f5cf62da）临时 boot 8 笔，逐笔提交推送，全部通过身份/双分区摘要核验。结果 7 笔返回、1 笔挂死（第 8 笔），**挂死率 0.125**；7 笔返回时间为 15.943 / 15.966 / 17.001 / 15.914 / 15.952 / 15.945 / 15.947 秒，极差 1.087 秒，零读档时序高度稳定。证据 reports/enuma-hang-baseline-device.json 与 out/device-tests/20261024T234*. **合并同口径历史样本**（zero 组 2 笔 1 挂、D-154 事故组 2 笔 1 挂、R-006 exit10-early 5 笔 0 挂）：17 笔 3 挂 ≈ 17.6%。**对 D-152 的修正**：D-152 由"同一零读镜像一成一挂"推出"挂死与显示访问无因果关系"，这是**在小样本上把基线噪声读成了信号**，本次 8 笔数据不支持该结论——零读档确实会挂，但那是**基础挂死率**，不等于"读显示不会额外提高挂死率"。因此 D-152 中"以显示为因的整条归因链作废""unclocked access 主判断不再成立"两句**supersede**为：存在约 12–18% 的、与显示访问无关的基础挂死率；该基础率**足以让单笔对照失去判别力**（R-006 的"0 读 5 笔干净 vs 2 读首笔挂"在 17.6% 基础率下，5 笔全干净的先验约 38%，仍不构成证据），但**不能**用来否定"读档挂死率更高"。历史观测中读档侧样本（exit14 首笔挂、vprobe 三笔全挂、probe1 挂、step22 挂、R-005 像素挂）挂死比例明显高于基础率，方向仍与 unclocked access 一致，只是尚未用同规模统计证实。**因此下一步不是宣布归因作废，而是**：若要判定"读显示是否显著提高挂死率"，须给某一读档配置同样跑 6–8 笔统计，与 12.5% 基础率做对照；在此之前所有读档结论维持"未证实"。**方法论收敛**（本次真正立住的一条）：任何单笔挂死都不构成归因证据，必须先有基础率；这条同时适用于本仓过去与将来的所有探针。

2026-10-25 00:06 · D-156：R-010 读档对照完成——裸读单寄存器挂死率 25%，**与零读基线无显著差异**，据此再次修正预期。执行：`--value-source raw`（Source 3）读 `0x0ae05014`（index 1），与常量档同一位置、同一镜像链路，4 笔全部单笔提交推送并核验双分区摘要。结果 3 笔返回（17.000 / 16.974 / 15.915 秒）、1 笔挂死（第 4 笔），**挂死率 0.25**。对比 R-009 零读档 8 笔 1 挂（0.125，合并 17 笔 3 挂 ≈ 17.6%）：Fisher 精确检验 p≈0.5，**无显著差异**。**修正的预期**：D-155 末尾写"历史读档侧比例明显高于基础率、方向与 unclocked access 一致"，本次数据不支持这个方向——我原以为裸读会接近必挂（毕竟 probe1、vprobe1..3、step14 全挂过），实际 3/4 成功。**因此历史高挂死不能归因于"读这个寄存器"**。剩余变量是：位置（probe1 在 stage checkpoint、vprobe 在协议安装之前，本次在 value-probe 位置）、读的个数（step14 连读 `0x0ae6b800` 与 `0x0ae6c000` 两个、step20 读 250 次）、以及上下文。**可操作结论**：带预热读的配置在本仓是 7 笔 7 成功（early14 四笔 17.016/17.033/15.956/15.949，step20 三笔 17.004/17.056/18.110），而裸读 4 笔 1 挂——**预热是当前唯一有实测支撑的规避手段**，自写显示栈应对所有首次触碰加预热读。**局限必须写明**：①4 笔统计力弱，只把读档挂死率上界压到约 60%，不能宣布"读与零读等价"；②三次返回的编码 nibble 均为 0（无 3 秒倍数延时），因此"读确实执行"只由静态审计（PE 内唯一 `ldr 0xae05014`、无预热地址）与第 4 笔挂死支持，不由数值支持；若要数值自证，需读一个已知非零的地址或换 shift。设备因第 4 笔挂起，待恢复核验。证据 reports/enuma-hang-baseline-raw-device.json、out/device-tests/20261025T000143/000242/000340/000436。

2026-10-25 00:20 · D-157：写显示栈之前先用一笔判别"MDP/DSI 扫描是否仍在跑"，判据 16 秒 vs 7 秒。用户要求"先判别 再写显示栈"。**为什么先判别**：点屏的最小工作量取决于这个答案——若 XBL 设的扫描输出仍在跑、源地址仍指向 `Display Reserved`（0x9C000000+0x02400000），那么只缺背光与被改掉的路由，工作量从"半个显示驱动"降到"修交接"；若扫描已停，才需要自写 dispcc/DSI PHY/panel init 全套。**方法不写新代码**：项目已有 step18（`EnumaDsiNativeProgress`），它读两个 DSI 控制器基址 `0x0ae6b800`/`0x0ae6c000` 的 `+0x26c` bit0（接口 active）、`+0xa8`（enable）、`+0xac`（帧计数，两窗各 100ms，要求至少一个接口递增且不回绕、timing/enable 不变），直接返回 SUCCESS/NOT_READY。把它接在既有 PASS 门上即得 1 bit：**命中 PASS → 延迟 2 秒复位 → 约 16 秒返回；未命中走 completion fallback → 约 7 秒返回**，9 秒差远超 0.75 秒容差。该路径自带预热读（`(VOID)*(volatile UINT32*)0x0ae6b800`），比裸读安全。**资格**：`--diagnostic-gop-query 1 --diagnostic-gop-step 18`、`ENUMA_VALUE_SOURCE=0`，FD `3f4b06b8`，审计 `dsi_counter_code` 记录 9 个读地址（version + 两控制器 × {base,+0xa8,+0xac,+0x26c}）且 `static_target_stores` 为空；镜像 `8df9616f`，Boot v3 回环通过。**工具改动**：计划工具与校验新增 gated probe 档案（`role='off'`），对 gated 用 `dsi_counter_code` 而非 `value_transport_code` 做审计，并把 step18 的读地址集**钉死**在 `run_value_probes.validate_plan` 里，落到别的 step 或混入额外读即拒绝；`run_hang_baseline` 相应接受 constant/raw/off 三种可重复档案，仍禁止混用。93 个测试通过。**判读纪律**：无论 16 秒还是 7 秒都只是"扫描在跑/没跑"的一个 bit，不据此宣布显示可用；若 16 秒（扫描在跑），下一步是背光与路由（写操作，须另立批准）；若 7 秒，则确认必须自写整栈。设备因 raw4 挂起，待恢复后执行。证据 reports/enuma-scanout-liveness-*.json、out/value-transport/alive/。

2026-10-25 00:32 · D-158：扫描存活判别实测——**DSI 帧计数在跑，扫描没停**；负对照本次挂死但历史同源数据补齐。执行两笔：①`alive`（step18 + PASS 门，FD 3f4b06b8，镜像 8df9616f）**16.981 秒返回**，落在 PASS 命中区间；②`alivefail`（同一 step18 只把门极性翻成 FAIL，FD c0ab4571，镜像 d8bdf014）**挂死**（75 秒无返回，需人工恢复）。**判读**：PASS 门命中意味着 `EnumaDsiNativeProgress` 返回 `EFI_SUCCESS`，即 major6 下至少一个 DSI 接口 active、且 `+0xac` 帧计数在两窗 100ms 内非回绕递增、timing/enable 未变——**XBL 设的 MDP→DSI 数据流仍在跑**。**负对照的缺口用历史补上**：2026-10-24 03:05 同配置 query1 = **16.969 秒**（本次 16.981，差 0.012 秒，等于同一行为），03:08 query2 = **22.265 秒**；而 delay2/delay7 对照给出"adb 返回 ≈ 复位前延时 + 14.7 秒固定开销"，故 22.265 秒正好是 **7 秒 completion fallback** 的体现，与"帧在跑所以 FAIL 门不命中"一致。本次 query2 挂死按 12–18% 基础挂死率解释（D-155/D-156），不作为反证，也不原样重试。**这条结论的实际含义**：点不亮屏幕**不是因为没有数据流**，剩余嫌疑收窄到三处——背光未开（17:45 摄像头实测面板呈镜面、背光关）、MDP 的 SSPP 源地址没有指向我们写过的 `Display Reserved`、或扫描内容本身为黑。**下一步优先级**：先只读绑定 SSPP `SRC0_ADDR` 与 LM/INTF 路由（沿用 R-004 只读，1–2 笔），确认扫描到底在读哪块内存；再决定是否需要开背光——开背光是**写操作**，须另立批准，不随本结论自动获得。设备因 alivefail 挂起待恢复。证据 reports/enuma-scanout-liveness-device.json、reports/enuma-scanout-liveness-fail-device.json、out/device-tests/20261025T002309、20261025T003045。

2026-10-25 00:43 · D-159：源地址读取出师未捷，**本轮挂死率 26.7%（15 笔 4 挂）已高到必须换工具，而不是继续单笔试探**。执行 `srcaddr`（register 模式、index 1 → `0x0ae05014`、shift 28，读地址高 4 位，FD 168283a4、镜像 1ec5f795）**挂死**（75 秒无返回），这是连续第二次挂死（前一次 alivefail）。本轮累计：零读 8 笔 1 挂（0.125）、裸读 4 笔 1 挂（0.25）、alive 1 笔成功、alivefail 1 笔挂、srcaddr 1 笔挂，合计 **15 笔 4 挂 ≈ 0.267**；连续两挂若按 0.176 独立估算约 3% 概率，提示要么该读配置更危险、要么设备/连接状态在反复 boot 后劣化。**同一时刻 adb 与 fastboot 均为空列表**——经用户确认，参考机 nuwa 当时被用于并行的 XNU 内核实机验证，属主动占用，**不是 USB 掉枚举**；故"两台都消失"不能作为设备侧异常的证据，但 enuma 自身的挂死是真实的。**此条更正 D-159 初稿中"USB 层掉枚举"的推测**。**结论：单笔 4 bit 的通道在 15–27% 挂死率下效率不可接受**——每笔只买 4 位，却要用户长按恢复，信息成本比过高。**换工具方向**：启用 R-008（保留内存 `0x9fff7000` + warm reset + Android 侧 `enuma_log_reader` 读回），一笔可带出数十个 32 位寄存器值，代码骨架已在仓内（`diagnostics/enuma_log_reader.c`、R-002 的 `--seed-marker` 写入先例），只缺 R-008 那两项批准（启用保留区写、复位方式 cold→warm）。**背光路线同时明确**：背光是 KTZ8866 独立 I2C 芯片（`i2c@a8c000`、addr 0x11、11 bit、当前 372/2047），并非 PMIC WLED；UEFI 镜像里虽有 XBL 的 `I2C`/`DALTLMM`/`GpiDxe` 在运行，但本仓源码树**没有这些 protocol 的头文件**（QcomPkg.dec 被裁剪到只剩两个 PMIC GUID），故开背光要么逆向出 I2C protocol、要么自写 GENI I2C，属**驱动开发（约半天到一天）**，不是一次实验。另有 `KTZ8866_LCD_DRV_HW_EN` 硬件使能引脚，可能还需配合 GPIO，进一步确认前不能承诺"写两个 I2C 寄存器就能亮"。证据 reports/enuma-srcaddr-device.json、out/device-tests/20261025T004052。

2026-10-25 01:30 · D-160：**路径纠偏——原厂显示栈一直都在 XBL 里，D-142 的"必须自写"结论是错的**。用户质疑"不应该这么复杂，基于公开资料重新审视"，重新枚举 `out/device/xbl_a.bin` 得到决定性事实：XBL 的 **149 个模块**中包含完整的原厂显示栈——`DisplayDxe`（PE 315392 字节，GUID `4138022f-06c7-4f79-9c94-7e33b511a4e7`）、`CPRDxe`、`ClockDxe`、`I2C`、`SPMI`、`PmicDxe`、`DALTLMM`，以及 **40 个 Panel XML 模块**（含本机 `Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml`，GUID `2962bfba-d7e7-4f37-a4c6-e28f7b5a685a`）。也就是说点屏所需的全部东西原厂都做好了，并以 PE 形式存在于我们已经在用的 XBL 里。**错在哪里**：D-131 当时就已提出"候选 D：不排除 OEM DisplayDxe（连同 CPRDxe 一起放回），由厂商驱动完成上电，优先于自写上电"，判断正确；但后续 D-142 在**裁剪后的本仓**（QcomPkg 只剩 9 个内存/引导库 + DisplayReEnablerDxe）上得出"没有可搬的显示初始化栈、必须自写"，把候选 D 覆盖掉了。本轮又沿着这条错线走去自写 GENI I2C，越走越重。**本仓 QcomPkg 的裁剪是转述者的选择，不是硬件事实**。**合规开关已存在**：`firmware_audit_policy.py` 明确规定 `ENUMA_DIAG_SIMPLEFB=0` + `ENUMA_DIAG_DISABLE_UFS=1` 时只省略 `UFSDxe`，即 **DisplayDxe 与 CPRDxe 合法保留**；构建脚本对应参数就是 `--diagnostic-without-ufs`（帮助文本原文 "GOP isolation only; default firmware retains OEM UFSDxe"）。所以候选 D 从不需要改守卫、也不需要写任何新驱动。**DisplayDxe 的 DEPEX 实测**：9 个 protocol 全 AND（162 字节，以 8 个 AND 结尾），逐 GUID 在 149 个模块的 PE 里找引用者，**只有 2 个无任何引用**：`a966cc4f-ee6c-424d-a762-8ed3b5a4a501` 与 `47861dff-556f-4269-9b28-062ec3ecb30d`；其余 7 个分别由 PmicDxe / DALTLMM / I2C / CPRDxe+ClockDxe 等引用。这 2 个 GUID 不在本仓任何 `.dec`/`.h`/`.dsc`/`.inc` 里，`grep a966cc4f|47861dff` 全树为空，也不匹配 `EFI_DISPLAYUTILS_PROTOCOL_GUID`(c0dd69ac…) 与 `EFI_DISPLAY_POWER_PROTOCOL_GUID`(f352021d…)，故其身份待定；**但 DEPEX 不满足只会让 DXE Core 不 dispatch（不崩溃）**，因此存在两种可能：若二者由 Mu 核心在运行时发布，DisplayDxe 就会真正起来并点屏；若确实缺失，则屏幕照旧黑而系统正常启动。两种情况都不写入任何寄存器以外的新风险。**本轮处置**：用 `--diagnostic-without-ufs` 构建保留原厂显示栈的镜像（不带 `--diagnostic-simplefb`），先看 DXE Core 是否 dispatch DisplayDxe、屏幕是否出现内容——这是候选 D 的第一次真实执行。**执行边界必须先说清**：原厂 DisplayDxe 一旦运行，会自行写 MDP/DSI/PMIC/背光，远超 R-012"只写 KTZ8866 使能与亮度"的范围，故上机前需单独批准（不因 R-012 自动覆盖）。**教训（写给自己）**：判断"能不能复用"必须查**原始固件里有什么**，而不是查**当前仓库里留了什么**；后者只是某个移植者的选择集，把它当硬件事实会直接把路线带偏到从零重写。

2026-10-25 01:20 · D-161：R-014 首次执行——**屏幕在 16–20 秒内熄灭并保持全黑镜面，原厂显示栈没有产出任何画面**；同时 PE 分析给出下一个可执行方向。**执行与证据**：用户批准 R-014 后，用 `vt-oemdisplay.img`（FD dbca3fcb、`SIMPLEFB=0`+`DISABLE_UFS=1`、只省略 UFSDxe）临时 boot，**首次带连续拍照**（`scripts/screen_capture.py`，Osmo UVC 摄像头 1280×720，60 帧 @2 秒 = 120 秒）。结果：`fastboot boot` 返回 0，75 秒无自动回归 → `manual-recovery-needed`，与第一次 R-014 相同（**两次同配置均挂死，非偶发**）。**逐帧判读**：frame-000/003/006/008 仍是 Android 桌面；frame-010（约 20 秒）已是**全黑镜面**（可见房间倒影、无任何画面）；frame-012 至 frame-059 全程纯黑镜面。即屏幕在 **16–20 秒**之间熄灭，此后 100 秒无任何内容。**结论**：原厂 DisplayDxe 未产出画面（既非 boot logo 也非白屏），"保留原厂栈即可点屏"这一步未成立；两次同配置挂死说明该镜像会稳定挂起，不能当作可用显示方案。**PE 分析的关键发现**（`out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi`，315392 字节）：①字符串显示 DisplayDxe 自身承担背光与面板电源——`EFI_DisplayPanelPowerControl() failed to turn on/off display`、`DisplayBackLightBrightnessLevelControl`、`Charger power status is not okay or at off mode charging, so turn off backlight`，并有 `EnableDisplayThread`（对应 uefiplat.cfg 的 `EnableDisplayThread=0x1`）。②**那两个缺失 GUID 在整个 DisplayDxe PE 里一次都没出现**，只存在于 162 字节的 DEPEX 中——说明它们是**编译期依赖声明**（.inf 的 [Depex]/PROTOCOLES 消费），PE 代码并不调用，因此**补 stub 提供者即可让 DEPEX 满足**，不需要实现真实功能。③但 `Charger power status ... turn off backlight` 这条路径提示：stub 若让 DisplayDxe 误判电源状态，可能反而关背光，故 stub 必须保守（不干预任何状态）并逐项验证。**下一步**：写一个只发布这两个 GUID 的最小 stub 驱动（空接口、不干预状态），与 `--diagnostic-without-ufs` 组合使 DEPEX 满足；判据仍用连续拍照。**设备状态**：因本笔挂起待恢复。证据 out/screen-probe/oemdisplay-r1/（60 帧）、out/device-tests/20261025T011238-dxe-driver-return。


2026-10-25 01:35 · D-162：**Codex review 推翻 D-160/D-161 的核心诊断链，R-015 动机不成立且无必要**。review 指出三点，均已在本机核实：

**① DisplayDxe 在 APRIORI 第 32 项（共 39 项），缺 GUID 不会阻止派发。** 源码实证（`firmware/Mu_Basecore/MdeModulePkg/Core/Dxe/Dispatcher/Dispatcher.c` 1426–1438）：APRIORI 中的驱动被直接置 `Dependent = FALSE; Scheduled = TRUE;` 并入 `mScheduledQueue`，调试输出原文 `RESULT = TRUE (Apriori)`——**DEPEX 被完全绕过**。故 D-161 中"DEPEX 缺 2 个 protocol → DXE Core 不 dispatch → 屏幕无画面"这条推理链**第一环即错**。

**② 把 ① 与 PE 分析合起来，结论比 review 更彻底：那 2 个缺失 GUID 对 DisplayDxe 根本不重要。** 它们既不在 DisplayDxe 的 PE 内（代码不 `LocateProtocol`），其 DEPEX 又被 APRIORI 判定为 TRUE。两条独立的证据都指向同一结论——**这 2 个 protocol 与本次现象无关**。因此 R-015"补 stub 使 DEPEX 满足"不仅是动机错误，而且**没有必要**。review 同时指出：GUID 字节搜索只能证明"没有模块以完整 GUID 字面量引用它"，不能证明无提供者、更不能证明空实现足够；若驱动把该协议当"初始化完成"信号，发布假信号反而会让它跳过真正的初始化。此点接受。

**③ R-014 的观测没有定位到 DisplayDxe。** `--dispatch-guid` 用的 `dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92` 在 `scripts/audit_enuma_fd.py` 中即命名为 `simple_guid`，是 **SimpleFbDxe 的 GUID**；而 `--diagnostic-without-ufs` 构建 `ENUMA_DIAG_SIMPLEFB=0`，**镜像里根本没有 SimpleFbDxe**。所以返回门指向一个不存在的驱动：`--dispatch-guid-only` 永不命中，75 秒无返回是必然，**不能据此判定"DisplayDxe 挂死"或"稳定挂死"**。D-161 中"两次同配置均挂死，非偶发"这句话**越过了证据**，收回。

**④ 来源与状态文档确有冲突（已修）**：设备仓 gitlink 停在 `d00c416`，而锁文件、固件检出与远端均为 `aa9ec66`，工作区显示 `M firmware`。已提交 `Bump the firmware submodule pointer to aa9ec66` 修正，"两仓固定且干净"此前不成立。

**修正后的正确图景**：DisplayDxe **已被 dispatch**（APRIORI 强制），那 2 个 protocol 无关；真正未知的是"dispatch 之后发生了什么"——可能运行到某处失败、可能挂在内部某个 `LocateProtocol`/硬件访问上，也可能根本没被执行到（APRIORI 只保证入队，不保证 StartImage 成功）。**在没有定位证据前，不得把 R-014 的挂死归因于 DisplayDxe，也不得把任何归因写在结论里。**

**下一步采纳 review 方案**（先证明执行到哪里，再决定查什么）：复用现有 Core 检查点，以 DisplayDxe GUID `4138022f-06c7-4f79-9c94-7e33b511a4e7` 为目标，制作"StartImage 前（detail15）"与"StartImage 返回后（detail13）"两个候选，**保持原厂 PE 不变**；现场连续取证继续保留。在此之前**暂不执行 stub**。

2026-10-25 01:38 · D-163：进一步更正D-162，保留其APRIORI绕过DEPEX及退回stub方案的有效部分，其余过强推断superseded。直接解析R-014镜像922972e6内FD dbca3fcb，DisplayDxe为APRIORI第33项（零基32）；仅保证入队，不能证明已dispatch/进入PE。R-014目标GUID不存在，但completion fallback=1，CoreDispatcher正常返回后仍应等待7秒复位，故“75秒无返回是必然”错误。GUID字节未命中不证明代码不调用或初始化无关。detail13只证明CoreStartImage返回，不输出状态；A detail15有响应而B detail13无响应不能直接定位驱动内部。后续按新专项方案，用目标GUID和实际编译/FD/时间证据细分启动区间。本轮仅修正文档，无构建、设备动作或新批准；不主动提交。

2026-10-25 · D-164：结合固定MiCode设备树/内核、LineageOS内核、edk2-msm及UniXNU公开资料，主线调整为先审ABL→BootShim→UEFI continuous-splash契约，原厂DisplayDxe作为有界支线，最小真实初始化为条件后备。新静态缺口：线程开关为1，而enuma内存表无GetXblHobAddresses所需FD Reserved/FD_Reserved名称，该路径不能恢复scheduler/DTB扩展地址；不等于已定位实机根因，不直接添加内存区/改名/关闭线程。先做FDT/显示生命周期与原厂PE真实调用图，再选最有区分力候选。D-163证据更正及所有设备门禁维持。本轮仅研究/文档，无新设备动作或批准，未提交。来源与可推翻条件见operations/2026-10-25-public-source-route-review.md。

2026-10-25 02:10 · D-165：逐条核实 Codex 本轮复审的静态发现与它对我的一处纠正，**全部成立，并据此采纳其优先级调整**。核实均在本地源码完成，未构建、未上机。

**① 线程开关与 HOB 名称缺口（Codex 发现，已核实）**：`Platforms/Xiaomi/enumaPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c` 第 29/34 行，`EnableMultiThreading` 与 `EnableDisplayThread` **均为 `0x1ULL`**；`Silicon/Qualcomm/QcomPkg/Library/PlatformPeiLib/XblProtocols.c` 第 113/114 行只调 `LocateMemoryRegionByName ("FD Reserved")` 与 `("FD_Reserved")`；而 `Platforms/Xiaomi/enumaPkg/Library/MemoryMapLib/MemoryMapLib.c` 的内存表只有 `Sched Heap`(0x9bc00000)、`Display Reserved`(0x9c000000/0x2400000)、`UEFI FD`(0x9fc00000)，**没有上述两个名称**（`Sched Heap`/`UEFI FD` 不是同名替代）。`PlatformPeiLib/PlatformPei.c` 中 `SchedulerInterfaceAddr`/`DtbExtensionAddr` 初始化为 0 后交给 `GetXblHobAddresses`，再进 `BuildXblHobs`。结论：**以当前内存表走该路径，scheduler 与 DTB 扩展地址不会被恢复**。这是确定的源码路径缺口，**不等于已定位实机根因**。

**② 线程 ABI 不可 stub（已核实）**：`QcomPkg/Include/Protocol/EFIKernelInterface.h` 第 445/446/622 行分别有 `THREAD_CREATE ThreadCreate`、`THREAD_RESUME ThreadResume`、`INIT_LOCK InitLock`。真实 ABI，接受 Codex 的判断：**不能用一个成功返回的 stub 替代**。

**③ 我 D-162 的一处过强推断被 Codex 纠正，已核实为其正确**：我在 D-162 写"返回门指向不存在的驱动，75 秒无返回是必然"。实际 `diagnostics/EnumaDispatchCompletionCheckpoint.h` 原文为 `// If a target is absent/skipped or LoadImage fails, do not enter BDS.` / `// Cannot recover a hung driver, exception loop or dispatcher deadlock.`，随后 `MicroSecondDelay (7000000); ResetCold ();`。即**目标缺失时同样会 7 秒后冷复位**，故 75 秒无返回**不是必然**，它表示派发过程中发生了挂死/异常循环/派发器死锁；但该注释同时说明它**无法区分**挂在哪，因此**仍然不能归因于 DisplayDxe**。D-162 中"75 秒无返回是必然"一句 supersede 为此表述。

**④ 采纳 D-164 的优先级调整**（Codex 提出）：主线改为先审 `ABL→BootShim→SEC/DXE→ExitBootServices→XNU` 的 continuous-splash 继承契约；原厂 DisplayDxe 降为**有界支线**（保留 detail15/detail13 作为定位工具，但须先完成离线审计）；完整显示栈重写仅作**条件后备**。三条公开依据中，与本地证据直接相关的是 UniXNU sheng 记录的"stock ABL 在没有 splash region 时关闭面板"——这为本机"boot 后 16–20 秒屏幕熄灭"提供了一个**待验证**的解释方向，但 sheng 是 SM8550，其地址/大小/节点策略不可复制，须先追踪本机 ABL 实际收到与修改的 FDT。

**⑤ 明确不做的事（承接 Codex 的两条警告，均已接受）**：不因线程缺口就把 `EnableDisplayThread` 改 0（同步路径可能同样依赖锁/事件/TPL/XBL 服务）；不给 `UEFI FD` 改名或添加 `FD Reserved` 区域（该扫描器按机器码模式寻找函数、解析循环直到 RET、无明确长度上限，且原 XBL 指针在 ABL 退出/BootShim 重定位后可能已失效）。任何内存表/映射改动仍走 AGENTS 审批。

**下一步**（与 D-164 一致）：先产出两份离线证据——`handoff-contract`（Boot v3 实际选用的 DTB/DTBO、splash base/size、stride/格式、SMMU、双 DSI、ExitBootServices 生命周期，逐项标注"已知/源码推导/待实测"）与 `native-display-abi`（固定本机 DisplayDxe 摘要与入口，对线程开关字符串做交叉引用，建立协议查找/HOB 查找/Thread/Lock/SetMode 的真实调用图）。在此之前不上机。

2026-10-25 · D-166：完成固定实际R-014/XBL DisplayDxe、ABL LinuxLoader和保存vendor_boot/Android FDT的可复现离线审计。确认真实Kernel Protocol/调度HOB/线程/锁调用，以及缺Kernel可清线程标志并返回0的降级分支；不能以返回0当SetMode成功，也不能以缺Kernel单独解释超时。ABL真实查splash_region，而保存三份完整DTB只有cont_splash_region；实际临时入口/DTBO未知，不直接补节点或判关闭面板。D-165复核保留，其“超时表示派发挂死”等穷尽解释收窄，复位/前置/观测失败仍可能。A正确GUID/detail15候选完成离线构建和机器码/FD/打包资格，未上机；固定aa9ec66、仅省略UFS，不更改固件源码/内存/verified/授权。新增两份专项审计、两个离线工具和机器报告，提交号由后续Git记录。

2026-10-25 · D-167：用户批准上机，登记R-016，仅D-166 A/detail15镜像29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4单笔临时boot。已做即时恢复/备份和相机准备；主机观测补充UTC/monotonic及先断开再重连守卫，四条模拟轨迹通过，无额外设备动作。当前未执行，发布后上机；超时停止追加并恢复，不自动发B。

2026-10-25 · D-168：R-016 A已执行一笔并返回Android；boot命令0.390s、fastboot断开0.953s、首次ADB16.187s、Android完成/root/摘要检查结束31.312s。独立out\device-tests\20261025T021235-recovery-reconciliation.json确认enuma/root/A槽/解锁与匹配备份。相机415/415帧可解码、50对原图/旋转图，无采集错误；观察到的MI/Android标志只作恢复证据。本次可返回性实机通过，单笔时序仅支持而不唯一证明DisplayDxe调用前门命中，不定位R-014内部挂点。R-016 consumed，本轮不重复A、不发B，后续若继续先离线资格B并核对执行范围。无新硬停、人工恢复请求、固件/映射/verified/分区变化。

2026-10-25 · D-169：B/detail13已离线构建、AOSP打包、归档和真实Core/map检查；镜像bf6e014dbda4fc64ea00762034b5107ffd617e5ae24752b708c143bfca03b2e3。A/B配置仅point15→13，70/72 PE逐字节不变；Core运行代码变化，PcdDxe另8字节仅RSDS GUID，明确记录不宣称所有PE仅Core不同。四项破坏输入负例拒绝；未上机。

2026-10-25 · D-170：用户澄清“一次性做到iPadOS 然后分析启动的报错 每次启动解决一些”，主线改为补齐完整链/真实错误/每轮修复一批，减少孤立早停，B降为备用。已复用固定上游实际发出54,231,040字节、29组件实验预链接，ARM64/4K/原始代码保持检查通过但非可boot包。发现并固定同SM8250同donor的UniXNU-umi 3eb7257/测试uefi 48bc412，核到真实ADT/RAM载荷/PMGR/UFS/CPU显示源码；先做ABI/板差迁移，不从零重写或拷其内存/GPT/触控。新物理数值/verified/分区门禁不变，无新增实机；完整方案见operations/2026-10-25-full-boot-mainline.md。

2026-10-25 · D-171：复用固定umi编码器和当前UniXNU payload.build实际生成完整结构ADT与96MiB FAT，原始系统trust两模块保持，FAT回读及真实DarwinBoot解析器ASan/UBSan正负例通过；不等于实机启动。三段DRAM仅作历史信息，board内存字段/512MiB请求/verified不变。stock vendor ramdisk2230字节，两种前缀组合均不满足umi whole-initrd FAT契约，下一步核实际v3范围/映射、适配有界只读SFS与错误输出，不猜偏移或搬umi窗口。本轮无设备动作/硬停，详见operations/2026-10-25-full-adt-fat.md。

2026-10-25 · D-172：用户推进boot v3运输并要求尽量一次验证多个点。复用umi只读BlockIO/FDT模式和本机既有Kernel映射，实际ABL PE确认原长vendor推进后接generic；runtime仍须范围/前缀/BPB/完整FAT检查。新增13项同次报告，SFS/文件延后BDS，失败停依赖项，payload模式移除60秒暂停。firmware698b7c1完整构建及实际PE/编译宏/常量/写保护机器码资格、AOSP真实96MiB FAT打包往返通过，镜像194fa0f2…00f8b9e；host ASan/UBSan正负例通过。CRC只作传输损坏检查。未上机，输出可见性/FDT/SFS、PMGR/UFS/root/Data仍未闭合；无新映射/内存字段/verified/分区或硬停。详见operations/2026-10-25-boot-v3-payload-transport.md。

2026-10-25 · D-173：用户明确上机无需批准，满足资格/发布/身份/备份/采集/恢复后直接单笔临时boot。9459426修复payload失败绕过cache flush/Map清理，13行同屏并展示2秒再继续；主机生产尾部故障注入及完整构建/实际PE/AOSP资格通过，新镜像d2ab5ef8…7e1db75。初始相机未枚举而未发设备动作，用户连接后14:06:59采集恢复。S-001发布后由新相机wrapper执行一笔，75秒观察/240秒总上限不构成自动返回保证；异常停止追加、恢复核验后继续离线，无内存字段/verified/分区扩张。

2026-10-25 · D-174：0fb21cc发布后S-001单笔于14:12:13发出，2.625秒命令返回0、5.110秒fastboot断开，命令后75秒无Android/fastboot返回，执行端标manual-recovery-needed并停止追加。相机450/450帧可解码，抽样黑屏，无可判读报告，13项均未观察，不认定DisplayDxe/UEFI/XNU阶段。候选consumed，不重试；请求既有长按恢复、独立核验后自动离线分析。当前恢复未确认，按AGENTS同轮落实所有停点文件。

2026-10-25 · D-175：用户报告Android返回，14:15:38独立核验enuma/完成/root/A槽/解锁/原boot与vendor_boot摘要一致，解除D-174恢复待办并按用户规则继续离线隔离。450主录像帧、194对截图和739恢复录像帧保留，无13项可判读报告；不以黑屏定因。优先核同SoC umi禁用显示线程策略与本机真实cfg消费者，最小新候选仍保留完整FAT，不重试S-001。

2026-10-25 · D-176：恢复后继续完成实际DisplayDxe配置slot0x18/shim HOB/生产provider链审计，固定umi tested48bc412配置Blob；只改EnableDisplayThread1→0。真实配置/helper host ASan/UBSan、语义单值delta、实际SEC TE值0与旧1破坏负例及完整构建/PE/AOSP资格通过，firmwarecb9e568，新镜像5e07e65e…77413327。无内存字段/verified/分区变化，不声称已同步初始化或修复根因；计划发布后S-002新SHA单笔，不重复S-001。

2026-10-25 · D-177：32a3c63发布后S-002新SHA单笔于14:29:26发出，2.657秒命令返回0、5.125秒断开，75秒无返回，451/451帧可解码、无可判读报告。停止追加/consumed，用户恢复后14:31:50独立Android/root/A槽/解锁/原摘要通过。单一display-thread0未带来可观察改善，降低其优先级，转离线必要Core返回边界定位；不宣称根因或运行阶段，不重试两份失败镜像，不继续盲调配置。

2026-10-25 · D-178：两次整链无报告后不继续盲调配置，按必要定位例外构建保持96MiB完整载荷的正确DisplayDxe point13返回门，明确关闭completion fallback。镜像d716e159…47f8304及独立Core/map/编译宏/调用顺序/延时资格完成，未执行第三笔。LTO把2秒专门化为两个1秒纳秒调用，审核只接受逐条固定形状并以参数篡改负例拒绝；旧A/B回归、错误point/fallback/FAT拒绝通过。返回只支持门命中，缺失不证明到达或挂死，任何返回不等于驱动/GOP成功。无新固件源码或内存字段/verified/分区变化。

## D-179执行前状态（2026-10-25 15:21，Asia/Shanghai）

用户继续授权；15:21:02只读核验enuma Android完成/root/A槽/解锁、boot_a与vendor_boot_a及本地备份摘要一致，相机1920x1080画面已人工判读为Android桌面，原图及90度旋转保留。d716e159…47f8304不可变完整输入候选离线复核通过，尚未发出。本轮在文档提交推送后直接执行一次point13精确DisplayDxe返回门，fallback关闭；相机先于设备，75秒观察期限，异常先恢复且不原样重试。无新增内存/verified/分区操作。当前无人工或审批待办，运行中状态以out/device-tests/current.local.json为准。

## D-180：S-003返回边界超时，恢复优先

2026-10-25（Asia/Shanghai）15:21:51发出完整输入DisplayDxe返回边界S-003，镜像SHA256 d716e159d6852b398d1b8a999b17852c4affd8318123cbd61e8afe27047f8304，103817216字节；固件cb9e568/UniXNU5fdbd5d。执行前93f325a已推送，15:21:02独立Android完成/root/A槽/解锁/设备与备份分区摘要及相机检查通过。

fastboot命令返回0，2.640秒；5.109秒观察断开，随后75秒无Android/fastboot返回。已停止追加，镜像consumed，不原样重试。拍屏所查帧为黑屏，无可读阶段报告，不能据此确认DisplayDxe已到达、未返回或挂死，也不能称GOP/XNU/iPadOS通过。完整96MiB FAT、精确GUID返回point13和禁fallback的离线资格保持，只是实机未得到预期受控返回。

当前最后观测为未枚举/黑屏，Android恢复未确认。恢复录像已开启，已请求用户沿既有长按方式恢复；这不是新启动审批。先恢复再独立核验完成/root/槽/解锁及两分区摘要，未核验前不得新boot。硬停依据AGENTS异常停止追加/恢复优先规则。恢复通过后自动继续离线分析、新软件，不原样重试。

证据：out/device-tests/20261025T152136-dxe-driver-return，out/camera-capture/20261025T152134-system-transport及reports/enuma-system-transport-S003-result.json。S-001/S-002此前均人工恢复核验通过且consumed。未flash/erase/改槽、未改board/plan内存字段或verified，R-001/R-002/R-015及旧像素限制保持。

下一步判断：把完整载荷条件下的更早交接/派发可达性与目标StartImage内部阻塞列为竞争假设；当前证据不允许只归咎显示线程。先核完整与旧小载荷路径的实际ABL装载布局、早期配置/派发差异及固定同SoC实现，再选能区分两者的新软件；不盲调配置、不用新内存地址绕过门禁。

## D-181：S-003恢复核验通过，自动继续离线调用前隔离

S-003在2026-10-25 15:21:51发出，fastboot返回0/2.640秒、5.109秒断开，75秒无自动返回；d716e159…47f8304已consumed，不重试。453/453帧录像可解码，已查画面黑屏，无阶段报告。用户长按恢复后，15:24:33独立核验enuma Android完成/root/A槽/解锁/原boot_a与vendor_boot_a及本地备份摘要一致，恢复停点解除。首次核验在Android启动收尾时未满足条件，未误报通过；后续完整核验通过才解除。

完整FAT/精确DisplayDxe返回门/fallback0并未带来受控返回；不能据此证明DisplayDxe曾到达或内部挂死。当前主判断是调用前可达性尚未闭合，优先区分更早交接/派发问题与调用内部阻塞，而非继续盲调显示策略。源APRIORI把DisplayDxe放在OEM列表中，RAM载荷驱动不在该APRIORI列表；在UEFI实际调度行为核定前不把RAM驱动当作其必然前置。

按恢复后自动离线规则，正在构建同源cb9e568/同完整96MiB FAT/display-thread0的point15候选：门在目标CoreStartImage调用前，禁completion fallback，仅detail13→15。构建/打包/实际Core资格未完成，不得上机；本轮此后尚无新boot。旧小载荷R-016 A仅历史，不替代新完整输入资格。新候选若受控返回也不能以耗时唯一证明门命中；若超时，更早路径/复位异常仍竞争。

失败原始记录保留于out/device-tests/20261025T152136-dxe-driver-return，主录像out/camera-capture/20261025T152134-system-transport，恢复录像out/camera-capture/20261025T152332，独立恢复out/device-tests/20261025T152433-recovery-reconciliation.json，公开结果reports/enuma-system-transport-S003-result.json。S-001/S-002均已恢复且consumed。当前无人工或批准待办；无需重复询问恢复或逐笔批准。没有flash/erase/改槽、内存字段或verified变化；原硬边界保持。root/PMGR/UFS/Data/GOP/XNU/iPadOS实机未闭合。

## D-182：完整输入调用前配对候选资格

S-003完整输入返回边界在15:21:51发出，2.640秒命令返回/5.109秒断开，75秒无自动返回，453/453主录像帧可解码，无可读阶段报告。用户恢复后15:24:33独立核验Android完成/root/A槽/解锁/原boot_a与vendor_boot_a及备份摘要通过，742/742恢复录像可解码且末帧Android桌面。三份已执行失败镜像均consumed，禁止重试；当前无人工或审批待办。

新point15调用前候选已构建资格：a21682ca083acf6bb6cb5e6c8ef021d7172c308a44855b12f82cf6237aa3c42e，103817216字节；out/full-boot/transport/enuma-display-precall-full-input-v3.img；FD10abab47280f13c78082e94a77a0a7bae398b23302274a57b6bbda50747599ba；冻结归档precall-boundary-cb9e568。源码仍firmwarecb9e568/UniXNU5fdbd5d，完整96MiB FAT不变，display-thread0，精确DisplayDxe GUID-only/fallback0。配对比较确认相对S-003构建配置仅detail13→15，PE清单差异按审核器核定，非整FD字节只有一处变化。

32原厂PE/DEPEX、AOSP打包往返、实际Core/map在CoreStartImage调用前的GUID/point/2秒延时/复位路径、SEC TE配置0及篡改负例通过。wrapper绑定冻结清单并接受13/15，修改清单point/GUID策略不能混用归档，四个清单负例通过。所有检查仅离线，不声称门已执行。该候选未消耗；文档推送后沿用户现有无需逐笔批准授权，按即时设备/备份/相机/恢复守卫直接执行一笔。

主判断：当前既不能确认DisplayDxe到达，也不能定位其内部挂死。新门区分调用前可达性与StartImage内/后续问题；返回只能提供支持，时间/USB不能唯一证明门命中，超时也不证明阶段。若新门返回而S-003不返回，优先沿真实CoreStartImage/映像保护/入口/原厂依赖排查；若也超时，提升更早交接/派发或复位路径问题优先级。异常停止追加，先恢复核验，再自动离线修复。

实际S-003 FD的APRIORI已解码：含DisplayDxe，不含RAM载荷驱动。结合固定Core调度源码和UEFI PI强顺序规则，降低RAM驱动作为DisplayDxe前置执行者的嫌疑；不排除载荷体积/布局的更早影响，不宣称实机任何驱动执行。证据enuma-full-input-dispatch-order.json，公开资料https://uefi.org/specs/PI/1.8/V2_DXE_Dispatcher.html。

详细方案operations/2026-10-25-full-input-precall-boundary.md。S-003结果和独立恢复保持在enuma-system-transport-S003-result.json，原失败result.json未重写。无flash/erase/改槽、内存字段或verified变化；R-001/R-002/R-015及像素旧限制保持。PMGR/UFS/root/Data/GOP/XNU/iPadOS尚无闭合实机证据。

## D-183：S-004自动返回及下一处入口隔离

2026-10-25（Asia/Shanghai）本轮执行S-003/S-004各一次，未flash/erase/改槽。S-003返回边界point13于15:21:51发出，命令2.640秒返回、5.109秒断开，随后75秒无自动返回；人工恢复后15:24:33独立Android完成/root/A槽/解锁/原boot_a和vendor_boot_a及备份摘要通过。453/453主录像、742/742恢复录像可解码。该镜像d716e159…47f8304已consumed，原失败记录不改写。

S-004调用前point15于15:30:15发出，命令2.641秒返回、5.110秒断开，21.172秒观察到ADB，36.672秒完成Android/root/原分区摘要核验；15:31:36再次独立核验Android完成/root/A槽/解锁和设备备份摘要通过，bootreason=bootloader。258/258录像帧可解码，时间线抽样Android→fastboot→黑屏→MI/HyperOS→Android，未请求人工恢复，抽样帧未见人工按键。当前是已恢复Android，无人工或审批待办。

S-004镜像a21682ca083acf6bb6cb5e6c8ef021d7172c308a44855b12f82cf6237aa3c42e，103817216字节，out/full-boot/transport/enuma-display-precall-full-input-v3.img；FD10abab47280f13c78082e94a77a0a7bae398b23302274a57b6bbda50747599ba；归档precall-boundary-cb9e568，已consumed不重试。执行前9bdee97已推送，源码firmwarecb9e568/UniXNU5fdbd5d。两份保持相同96MiB FAT/display-thread0/GUID-only/fallback0，配对构建配置仅detail15/13，73个PE中71个逐字节一致，Core运行时代码不同，PcdDxe仅审核允许的debug GUID字段不同；不宣称整个FD只变一个字节。

主判断（中等置信）：完整载荷的调用前候选可自动返回，而调用后候选超时，支持目标调用前可达性，把CoreStartImage内部、PE入口和其原厂依赖路径提升为首要嫌疑；降低“完整载荷一律无法进入此前路径”及“RAM驱动先执行卡住”的优先级。时间/USB/自动返回不能唯一证明门命中，其他复位来源尚未排尽，不能据此证明DisplayDxe入口已执行、成功或内部挂死。没有13项运输结果、GOP/XNU/iPadOS实机通过证据。

静态佐证：S-003实际FD的APRIORI包含DisplayDxe而不含RAM载荷驱动；固定Core源码先排空Scheduled队列再处理普通依赖，与UEFI PI强顺序规则一致。该驱动不是此FV中DisplayDxe的调度前置，仍不排除更早体积/布局影响。公开来源：https://uefi.org/specs/PI/1.8/V2_DXE_Dispatcher.html 。审核与原厂32PE/DEPEX/AOSP往返/实际SEC TE配置0、Core/map/延时/负例和冻结清单绑定均通过；静态资格与上述实测分开。

下一步：复用已存在point20（Image.c在Image->EntryPoint调用前、受scheduled handle/GUID桥接约束）构建新的完整载荷精确门，禁fallback，核真实Core PE/map和间接调用顺序及负例后才可上机。若可自动返回，进一步提高PE入口/原厂包装层及其依赖嫌疑；若不返回，优先CoreStartImage前置处理/映像保护/路径或复位原因。先审现有上游和同SoC实现，不造stub、不引入canary值、不换内存地址。当前point20尚未构建/资格/上机，不能复用旧小载荷或旧审批结论。仅缺乏直接错误时作必要隔离，取得边界后回到完整链实修。

证据：reports/enuma-system-transport-S003-result.json、S004-result.json、enuma-full-input-boundary-pair.json、enuma-full-input-dispatch-order.json；S-004原始out/device-tests/20261025T153001-dxe-driver-return、录像out/camera-capture/20261025T152958-system-transport、独立核验out/device-tests/20261025T153136-recovery-reconciliation.json。S-001/S-002同样保持consumed和恢复事实。原失败镜像不重试，后续新软件按用户现有无需逐笔批准授权及源码/资格/文档推送/即时设备备份采集恢复门禁推进。board/plan内存字段/512MiB/verified/破坏性分区及R-002/R-015/旧像素硬边界不变。

## D-184：point20完整输入资格

S-003调用后point13超时并于15:24:33恢复核验通过；S-004调用前point15自动返回，ADB21.172秒、Android完成36.672秒，15:31:36再次独立root/A槽/解锁/原分区及备份摘要通过。所有已执行镜像均consumed，不重试。当前无人工或审批待办；本轮15:34即时Android/root/原槽/解锁/设备与备份摘要复核通过，相机1920x1080实际画面已核为Android桌面。

新point20保持完整96MiB FAT、固件cb9e568/UniXNU5fdbd5d、display-thread0、精确DisplayDxe GUID-only/fallback0，无新源配置/原厂PE/内存/verified/分区改变。镜像SHA256 d2de38822ec27ee2b7ebcfc4328eea4a8c6ab192ab72b396a09f89952ab7830a，103817216字节，out/full-boot/transport/enuma-pe-entry-full-input-v3.img；FD93dd586bb0b6f546164547e94975b34b4855df07b3c4758a396d5cca23debf65；冻结归档pe-entry-boundary-cb9e568。尚未上机或consumed。

完整构建/32OEM PE与DEPEX/AOSP完整FAT回读/SEC配置0通过。实际Core将GUID过滤内联到EnumaImageEntryCheckpoint；审核器新增只接受具体编译形态的point20模式：global scheduled handle非空、等于调用句柄、file非空、point20条件、两半GUID、2秒专门化延时/ResetCold/死循环，以及CoreStartImage内检查点之后的EntryPoint读取、相同句柄/SystemTable参数和blr。审核调用点0xc418、间接PE入口调用0xc428，门先于入口。这里是静态调用边界，非已执行证明，不泛化为其他编译结果自动通过。

删除间接入口调用、改GUID、错point、去掉空句柄门/句柄比较及改纳秒参数共六负例拒绝；旧13/15审核负例回归通过，冻结清单绑定的wrapper离线通过。构建有clock-skew警告，实际FD/PE/map/编译宏已核并未仅凭退出码；不能因此宣称任意旧输出均有效。

主判断（中等置信）仍是CoreStartImage到PE入口/返回处理区间；StartImage后置还有CoreConnectHandlesByKey，不能仅将调用后超时归为驱动内部。现有point20复用原实现，未造stub或补canary。若新门自动返回，支持入口前可达，随后优先查PE包装层/真实依赖及直接返回路径；若超时，提升StartImage前置/门桥接/复位问题。任何自动返回或时间仍不能唯一证明门命中，不声称GOP/XNU/iPadOS通过。

当前文档与代码推送后，沿用户无需逐笔批准授权，用run_system_transport_trial.py --qualification reports/enuma-full-input-pe-entry-boundary.json --execute执行单笔；相机先开启，再即时身份/备份/恢复守卫。75秒无返回立即停止追加并先恢复；恢复核验后自动离线分析，不重试失败镜像。无flash/erase/改槽/内存字段/verified变更，R-001/R-002/R-015及旧像素边界保持。

详见operations/2026-10-25-pe-entry-boundary.md，机器证据enuma-full-input-pe-entry-boundary/core/negative.json。UEFI StartImage来源：https://uefi.org/specs/UEFI/2.10/07_Services_Boot_Services.html#efi-boot-services-startimage 。当前尚无point20实测，PMGR/UFS/root/Data/GOP及系统运行待闭合。

## D-185：S-005自动返回与构造器路径审计

2026-10-25（Asia/Shanghai）S-005于15:39:52发出。fastboot返回0/2.641秒，5.110秒断开，21.141秒观察ADB，35.219秒完成Android/root/原分区摘要核验；15:40:47再次独立enuma/Android完成/root/A槽/解锁/boot_a与vendor_boot_a及本地备份摘要一致。bootreason=bootloader；253/253录像帧可解码，抽样Android→fastboot→黑屏→MI/HyperOS→Android，未请求人工恢复，抽样未见按键。当前Android正常，无人工或审批待办。

镜像d2de38822ec27ee2b7ebcfc4328eea4a8c6ab192ab72b396a09f89952ab7830a，103817216字节；FD93dd586bb0b6f546164547e94975b34b4855df07b3c4758a396d5cca23debf65；归档out/full-boot/transport/pe-entry-boundary-cb9e568，已consumed，不重试。源码仍firmwarecb9e568/UniXNU5fdbd5d，相同96MiB FAT/display-thread0/GUID-only/fallback0；执行前230cc9f已推送。新point20在实际Core 0xc418门调用后0xc428才间接调用PE入口；桥接句柄/文件/point/GUID、2秒延时、reset/deadloop及参数顺序静态审核通过。六项破坏负例拒绝，旧13/15回归通过，OEM32PE/DEPEX/AOSP/SEC配置0通过。clock-skew警告已记录，实际包装PE/map/编译宏绑定，不以构建退出码代替资格。

结合S-004（调用前自动返回）与S-003（调用后超时且已人工恢复），主判断（中等置信）进一步偏向PE调用区间、原厂包装层/构造器/主函数或其返回后处理，降低CoreStartImage入口前分配等路径的优先级。自动返回/时序不唯一证明门命中，不能称PE入口已执行或显示驱动挂死。S-003/004/005不是只差一个字节或严格全PE相同的样本；S-003/004配对配置仅point不同且PE差异已审，S-005有真实新增桥接编译形态单独资格。没有13项运输、GOP、XNU或iPadOS运行通过证据。

本轮继续只读逆向，复用已锁定OEM DisplayDxe 6c6351c3…347f425：入口包装器0x114c在0x1190先调构造器列表0x123c，再于0x120c调0x1508→主函数0x16e8。列表含十个有序调用5848/5888/5918/59f8/5b60/5d70/5e5c/612c/6628/6ffc；实际DXE服务表GUID05ad34ba-6f02-4214-952e-4da0398e2bb9与HOB表GUID7739f24c-93d7-11d4-9a3a-0090273fc14d已读出。新增audit_display_constructor_path.py绑定原XBL/PE摘要和具体调用顺序，删除构造调用负例拒绝，报告enuma-display-constructor-path.json。此为静态调用路径，未证明任一构造器运行/失败；不把正常UEFI表要求当成已缺失。

下一步优先顺序：一，沿这十个真实构造器，把标准gRT/gBS/gDS/HOB、内核接口及后续库初始化与现有Mu/同SoC提供者的ABI和实际来源逐项对应，复用已有实现，不造stub或补常量canary；历史D-040匹配前缀存在仅历史支持，不等于当前完整表/值。二，使用已有point21直接PE返回边界或对目标活动映像的真实UEFI服务调用/返回取证，区分构造/主函数与CoreExit/LongJump/CoreConnectHandlesByKey；具体候选需先审适用性和实际PE。UEFI StartImage在相关句柄变化时返回前还要连接控制器，故不能将point13超时直接等同于PE没有返回。新21/服务候选尚未实现资格或上机，不套旧小载荷结果。三，有具体缺口后做真实适配并回完整链错误采集，避免无限单点复位。

本轮仅S-005一笔；未发point21、未修改OEM字节或运行新服务探针。所有已执行镜像consumed，S-001/002/003此前恢复事实保留。主证据out/device-tests/20261025T153938-dxe-driver-return，录像out/camera-capture/20261025T153935-system-transport，独立核验out/device-tests/20261025T154047-recovery-reconciliation.json，公开结果enuma-system-transport-S005-result.json；原result.json未被独立核验重写。

下一笔沿用户无需逐笔批准授权，仍先来源/构建/实际产物资格、当前文档提交推送及即时设备/备份/采集/恢复守卫。超时停止追加优先恢复，同轮落实文档；恢复核验后自动离线分析。不flash/erase/改槽，不改board/plan内存字段/512MiB，不置verified；R-002/R-015/旧像素硬边界保持。

## D-186：PE直接返回资格及构造器来源审计

S-005入口前point20已自动返回并于15:40:47独立Android完成/root/A槽/解锁/原两分区及备份摘要通过，已consumed。S-004调用前自动返回、S-003调用后超时后人工恢复事实保持；不重复任何已执行镜像。当前无人工/审批待办，本轮15:47 Android和相机门禁复核通过，实测runner仍即时重验。

新point21镜像76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节，out/full-boot/transport/enuma-pe-return-full-input-v3.img；FD6d4aa5f5f050e88a0faff7608bf3a03b2009963a70ac9c776795534d3b5c40d3；归档out/full-boot/transport/pe-return-boundary-cb9e568。仍firmwarecb9e568/UniXNU5fdbd5d/完整96MiB FAT/display-thread0/精确DisplayDxe GUID-only/fallback0。尚未上机或consumed，无OEM修改、内存字段、verified或分区操作。

实际Core/map审核：0xc428间接PE调用直接返回后，0xc43c执行point21，之后才CoreExit。完整句柄/文件/GUID/point桥接、两次1秒专门化延时及ResetCold/死循环均审核；point21六项破坏负例拒绝、旧20/15/13回归通过，32OEM PE/DEPEX、SEC配置0、AOSP完整FAT往返和冻结清单绑定通过。机器证据enuma-full-input-pe-return-boundary/core/negative.json。静态资格不等于实机门命中。

重要判读：point21只覆盖入口直接return，驱动主动Exit会绕过本门。若返回，支持直接PE返回并提高CoreExit/LongJump/句柄连接阶段嫌疑；若超时，构造器/主函数未返回、直接Exit、异常及复位等仍竞争，不能证明显示内部挂死。自动返回/USB时序不是唯一门命中证明。仍无13项运输/GOP/XNU/iPadOS运行成功证据。

本轮构造器提供者核对：Mu Core在派发前安装标准gDS和HOB配置表，不把原厂查询误当已缺失。内核协议b5062be7-170b-4a32-be21-689262ff4399的查询失败时可走HOB8ec2bd8d-56d7-49ef-8796-631778f8ebf8回退；PlatformPei仅发现调度器地址后发布。当前map无FD Reserved/FD_Reserved，源码发现路径返回，故该来源存在具体缺口；其他OEM提供者未排除，构造器允许空回退，不认定根因或拷外机地址修复。enuma-display-constructor-providers.json记录来源摘要与限制。

发布本次代码和文档后，沿用户现有无需逐笔批准授权执行一笔S-006；run_system_transport_trial.py --qualification reports/enuma-full-input-pe-return-boundary.json --execute。先相机后即时设备身份/备份检查，75秒期限；超时立即停止追加、优先恢复、同轮文档，恢复核验后自动继续离线。所有旧镜像保持consumed，内存/verified/破坏性分区和R-002/R-015/像素旧边界保持。

## D-187：S-006超时恢复优先

2026-10-25（Asia/Shanghai）15:52:23发出S-006 point21完整输入候选76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节；执行前74ad907已推送，原源码cb9e568/UniXNU5fdbd5d/96MiB FAT不变。即时身份、Android/root/原槽/解锁及设备/备份摘要、相机守卫通过。fastboot命令返回0/2.625秒，5.110秒断开，随后75秒没有Android或fastboot返回。已停止追加并consumed，禁止原样重试。

当前为manual-recovery-needed，最后观测未枚举，Android恢复未确认。恢复录像已开启并请求用户沿此前长按方式恢复，非新启动审批；恢复后必须独立核验Android完成/root/A槽/解锁/原boot_a与vendor_boot_a及备份摘要，未通过前不发新候选。触发依据AGENTS异常停止追加/恢复优先和当轮交接规则。记录452/452主录像可解码，未得到可读阶段报告。

结合S-005入口前自动返回而S-006直接PE返回门不返回，主判断提升PE包装层/构造器/主函数调用区间嫌疑；但point21不覆盖主动Exit，异常/复位及观测原因未排除，不能称DisplayDxe内部挂死或门已到达。point13超时同样保留。下一步先离线审主动Exit/CoreExit与已存在point22路径，再选真实服务取证或Exit后边界，避免继续盲调显示配置。标准gDS/HOB来源已核；调度器HOB发现路径缺名称仅源码缺口，不直接归因，不添加外机地址或stub。

主证据reports/enuma-system-transport-S006-result.json及其evidence/camera_evidence路径；原trial result保留，current.local.json为实时恢复状态。S-001/002/003此前人工恢复、S-004/005自动恢复均核验通过且consumed。没有flash/erase/改槽、内存字段或verified变更，R-002/R-015/像素硬边界保持。恢复通过后自动继续离线分析/新软件，无需重复批准或结束推进；当前只差恢复状态和独立核验。

## D-188：S-006恢复与影音本地规则

S-006 point21于2026-10-25 15:52:23（Asia/Shanghai）发出，命令返回0/2.625秒，5.110秒断开，75秒无Android/fastboot返回。已consumed且停止追加。用户长按恢复后反馈Android，15:55:30独立enuma Android完成/root/A槽/解锁/boot_a与vendor_boot_a及本地备份摘要一致，恢复停点解除。452/452主录像、740/740恢复录像可解码；抽样黑屏无可读报告。当前Android，无人工或审批待办。

镜像76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节；执行前74ad907已推送。firmwarecb9e568/UniXNU5fdbd5d、同96MiB FAT/display-thread0/GUID-only/fallback0保持。原trial result不重写；公开结果reports/enuma-system-transport-S006-result.json，独立恢复out/device-tests/20261025T155530-recovery-reconciliation.json。所有已执行镜像不重试，旧恢复事实保留，无flash/erase/改槽、内存字段/verified变更。

按结果推进：S-005入口前能自动返回、S-006直接PE返回门无返回，继续将PE包装层/构造器/主函数调用区间列首要嫌疑，但直接Exit会绕过point21，异常/复位也未排除，不能写成显示内部挂死。已审CoreExit源码：有效当前映像Exit经LongJump回StartImage；现有point22在该汇合后、TPL检查/释放JumpBuffer/句柄连接前，可覆盖直接return经CoreExit及成功主动Exit。源码证据reports/enuma-pe-exit-source-review.json。正结果也不证明GOP成功；负结果不能区分PE卡住、无效Exit、ExitData分配失败、异常或reset失败。

恢复等待期已开始同源/完整载荷point22/fallback0离线构建，产物/实际Core资格尚未完成，本轮不追加设备启动。先审实际桥接和LongJump汇合点以及负例，再发布新候选。标准gDS/HOB在Mu派发前安装；调度器源码发现缺映射名称是具体来源缺口，但其他OEM提供者未排除、构造器允许空回退，不按猜测改地址或造stub。PMGR/UFS/root/Data/GOP/XNU/iPadOS仍未闭合。

用户本轮强调原始影音不要上传GitHub：已核对设备仓main、固件main/sheng的影音扩展名历史无媒体文件，两仓GitHub Release无附件；本地out/camera-capture被忽略，CI证据路径不包含它。本轮OpenCV只采画面无音频，不推断其他历史录像是否有音轨。规则已写AGENTS并增加影音扩展名忽略：原始视频/音频/现场图片仅本地，不force-add、不传Release或CI附件，只提交检查后的文字/JSON摘要。审计不覆盖无关第三方或手工其他渠道上传。

后续新启动仍沿现有无需逐笔批准授权，满足资格/当前文档提交推送/即时身份备份采集恢复门禁才执行。异常先停追加/恢复，当轮文档；恢复核验后自动离线分析。R-002/R-015/像素及内存/verified/分区硬边界不变。

## D-189：Exit汇合点候选离线资格完成

2026-10-25（Asia/Shanghai）S-006 point21于15:52:23发出；命令返回0/2.625秒、5.110秒断开，75秒无自动返回，已consumed，不重试。用户长按恢复Android，15:55:30独立核验enuma/Android完成/root/A槽/解锁/boot_a与vendor_boot_a及本地备份摘要一致。452/452主录像、740/740恢复录像可解码；抽样黑屏无可读阶段报告。当前Android恢复完成，无人工或审批待办。

S-006镜像76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节；执行前74ad907已推送，失败停点6b061e2和恢复/影音规则a787f0e也已推送。公开结果reports/enuma-system-transport-S006-result.json保留原phase和timeout事实，并追加独立恢复；原trial result不改写。当前状态见current.local.json/本页，不能把原失败phase当仍未恢复。

主判断（中等置信）：S-005入口前能自动返回，S-006入口直接返回门不返回，PE包装层/构造器/主函数调用区间仍列首要嫌疑。但主动Exit绕过point21，异常/复位等尚未排除，不能证明显示驱动挂死。CoreExit有效当前映像经LongJump回StartImage；已存在point22在该汇合后、TPL清理/释放JumpBuffer/控制器连接前，优先用它排除主动Exit解释。正结果支持到达退出后上下文，不证明GOP或状态成功；负结果仍不能区分PE未返回、无效Exit、ExitData分配失败、异常或复位失败。

已完成同源完整输入point22离线软件：dedd87a68a005817d8ee2d95c60d7949b244bdc31c974e1bd4c760d817c25361，103817216字节；out/full-boot/transport/enuma-pe-exit-full-input-v3.img；FDcc7a39d8b2f181eae341203130566fdbc6cb8778ecc3e3fbe31beeb09f330fdb；冻结归档out/full-boot/transport/pe-exit-boundary-cb9e568。firmware仍cb9e568/UniXNU5fdbd5d、相同96MiB FAT/display-thread0/GUID-only/fallback0。此新镜像尚未consumed或上机，本轮只有S-006一笔，未追加S-007。

实际Core/map审核：SetJump调用0xc3fc，非零分支到point22参数准备；CoreExit转移0xc450；检查点0xc460在TPL检查前。同一scheduled handle/file非空及匹配、精确point/GUID、专门化两次1秒延时/ResetCold/deadloop均按具体编译形态审计。删除SetJump、CoreExit、非零分支、句柄门、GUID/point或延时参数等八负例拒绝，旧21/20/15/13负例回归通过。32OEM PE/DEPEX、SEC配置0、AOSP完整FAT回读及冻结清单绑定通过。机器证据enuma-full-input-pe-exit-boundary/core/negative.json；这些是静态资格，不是point22实机通过。

构造器来源审计继续保留：Mu派发前安装gDS/HOB标准配置表；内核协议失败可走调度器HOB回退。当前map无FD Reserved/FD_Reserved使源码发现路径不能从此来源发布调度器HOB，但其他OEM提供者未排除，构造器可容许空回退，不能拿该缺口直接当黑屏根因或复制外机地址修复。未造stub、未改原厂PE、未补canary值。

用户明确原始影音不要上传GitHub：设备仓main及固件main/sheng可见历史中未发现影音扩展名文件，两仓GitHub Release无附件；本地out/camera-capture被忽略，CI上传目录不含它。本轮OpenCV不采音频，不推断其他历史录像音轨；审计不覆盖无关第三方或其他手工渠道。AGENTS已禁止把原始视频/音频/现场图片force-add或传Git/Release/CI，影音扩展名也加入忽略，仅提交检查后的文字/JSON摘要。原始录像始终本地，未随本轮提交上传。

下一步：新point22候选按现有无需逐笔批准授权、完整源码/产物/文档发布及即时身份备份采集恢复守卫后可单笔验证；入口run_system_transport_trial.py --qualification reports/enuma-full-input-pe-exit-boundary.json默认离线，加--execute才操作设备。本轮没有执行。若它也无返回，不继续无限早停，优先在目标活动映像范围内评估真实UEFI服务调用/返回与原厂构造链ABI取证，或复用已证实同SoC实现的具体缺口适配；不再盲调显示开关。若返回则聚焦后置TPL/清理/控制器连接。

所有已执行镜像consumed；S-001/002/003/006已人工恢复核验，S-004/005自动恢复核验。没有flash/erase/改槽、board/plan内存字段或verified变化，R-002/R-015/像素及其他硬边界保持。仍无13项RAM运输、GOP、XNU或iPadOS运行通过证据，PMGR/UFS/root/Data契约未闭合。

## D-190执行前（2026-10-25 16:03，Asia/Shanghai）

用户明确要求执行point22。16:03:16即时enuma Android完成/root/A槽/解锁/原boot_a与vendor_boot_a及本地备份摘要一致；冻结point22完整载荷dedd87a6…17c25361离线复核通过，相机1920x1080画面可用，尚未发出。本次文档发布后S-007仅一笔临时boot，75秒观察，禁fallback；异常先停止追加并恢复。原始影音只留本地，不上传Git/Release/CI。无内存/verified/分区变更，无人工/审批待办。

## D-191：S-007超时恢复优先

2026-10-25（Asia/Shanghai）16:03:54发出S-007，镜像dedd87a68a005817d8ee2d95c60d7949b244bdc31c974e1bd4c760d817c25361，103817216字节；执行前2036dfc已推送，16:03:16 Android/root/原槽/解锁/设备和备份摘要及相机通过。fastboot命令返回0/2.640秒、5.109秒断开，随后75秒没有Android/fastboot返回。镜像consumed，停止追加且不原样重试。453/453主录像帧可解码，无可读阶段报告。

当前manual-recovery-needed，最后观测未枚举，Android恢复未确认。已开启仅本地恢复录像并请求用户沿此前长按恢复反馈，非新启动审批。恢复后独立核验Android完成/root/A槽/解锁/原boot_a和vendor_boot_a及备份摘要；通过前不发任何新boot。依据AGENTS异常停止追加/恢复优先和当轮交接规则。

主判断：S-005入口前返回，S-006直接PE返回及本次S-007退出汇合门均无返回，继续提高PE包装层/构造器/主函数未完成的优先级，降低“主动Exit成功汇合，仅TPL清理/连接停住”的解释；但未证明门已到达，错误Exit/异常/复位路径仍未排除，不能称DisplayDxe已执行或内部挂死。下一步不再追加同类早停，转原厂构造链及目标活动映像范围的真实UEFI服务调用/返回取证，先离线设计来源/边界/脱敏采集和恢复，选择能定位具体服务的方案。

源码firmwarecb9e568/UniXNU5fdbd5d/完整96MiB FAT/display-thread0/GUID-only/fallback0不变；无flash/erase/改槽、内存字段或verified变化。原trial result保留，公开结果reports/enuma-system-transport-S007-result.json含本地证据路径。原始影音只留本地，不传Git/Release/CI。旧实验均consumed，恢复核验后自动继续离线分析和新软件；R-002/R-015/像素硬边界保持。没有13项运输/GOP/XNU/iPadOS成功证据。

## D-192当前：S-007已恢复，下一步决策先复审官网与其他设备

用户确认Android恢复，16:06:22独立完成/root/A槽/解锁/原分区及备份摘要核验通过，恢复停点解除，无人工/审批待办。S-007 consumed，不重试。用户最新要求：下一步决策之前先查看UniXNU官网最新移植界面、其他设备和仓库；现暂停新设备动作与新取证实现，先核官网及最新固定提交、与本仓pin的变化和板级适用性，再给方案。旧D-191恢复未确认仅历史，当前Android。原始影音始终本地。

## D-193：最新上游复审后优先恢复真实GOP

2026-10-25（Asia/Shanghai）S-007 point22于16:03:54发出，命令2.640秒返回/5.109秒断开，75秒无Android/fastboot返回；镜像dedd87a68a005817d8ee2d95c60d7949b244bdc31c974e1bd4c760d817c25361已consumed，不重试。用户反馈Android，16:06:22独立完成/root/A槽/解锁/原boot_a与vendor_boot_a及备份摘要通过，453/453主录像、739/739恢复录像可解码。当前Android恢复完成，无人工或审批待办。原始影音仅本地，不上传Git/Release/CI。

按用户“下一步决策前看最新官网、其他设备及仓库”完成复审。官网已是schema2/SoC+OS profiles/组件目录及porting.toml路线；最新框架16e592abee8a550dec8154ed1f38b5ebc4f16213与本仓pin为diverged，不作整体快进或换底座。最新审查源另放out/sources，固定config/upstream-route-review-20261025.lock.json；8仓40文件资格和cas纯显示解码/Blt16项主机测试通过。没有修改构建依赖锁/board/plan。

新主线建议：先离线评估同SM8250且有UEFI菜单/EFI返回记录的cas继承扫描输出GOP，取得可见错误通道；OEM构造器真实服务取证降为备用，不再默认追加同类更深早停。cas当前casPkg与实测893f5025目录无差异，但其固定内存/1080x2340面板/像素和CTL_START写入不适用于直接复制，也未获新写入资格。仅复用纯快照解码和边界方法，先对enuma本机FDT/固定SDE定义/几何、分块、格式、secure/UBWC和刷新条件做离线适配审计；若条件不满足则拒绝或回备用，不放宽判据。新GOP尚未实现、构建或上机。

共享UniXNURamDiskDxe已在最新上游实现，应优先复用通用代码；但它要求整个initrd是512倍数，本机2230字节vendor前缀+96MiB FAT的预测范围余182字节，不能无适配替换当前精确前缀/范围/CRC保护。运行时FDT仍未知。AdvancedLogger/QR可复用但依赖可用GOP/菜单、输入与日志生产者，不能直接修复当前菜单前黑屏；恢复可见菜单后再接。主机debug_terminal没有匹配设备端CDC后端也不会新增enuma早期日志，不复活R-002。

umi仍是同SM8250/同donor系统、UFS/root/Data的首要参考，审查HEAD未变化，手机地址不复用。elish和Tlrenhb另一enuma仍是骨架而非新实机基线；官网wh1stl3段落转述本仓旧记录，不作独立证据。fajita SDM845的特殊槽/分区命令不继承。sheng最新源码可选OEM或继承SimpleFb，但SM8550驱动/内存不复制。

详见operations/2026-10-25-latest-porting-route-review.md（固定版本、源码行为、网站链接、适用边界及新推进顺序），机器证据reports/enuma-latest-porting-review.json。审查器audit_latest_porting_review.py不访问设备。S-007后无新boot、固件功能实现、像素/MMIO写入。后续先完成可审查离线适配，再满足源码/产物资格/文档推送/即时恢复门禁；有具体新增像素/MMIO范围时按AGENTS精确规则处理，当前不请求批准。

构建仍锁firmwarecb9e568/UniXNU5fdbd5d，完整96MiB系统FAT保持。所有已执行镜像consumed；没有flash/erase/改槽、内存字段或verified变化，R-002/R-015/旧像素硬边界不变。仍无13项RAM运输、GOP/XNU/iPadOS运行通过证据，PMGR/UFS/root/Data契约未闭合。

## D-194：视频模式继承扫描输出纯组件

用户要求优先恢复真实GOP/可见错误通道。本轮已实现固件InheritedScanoutLib（源0080640），仅纯解码和回调采集，未接入DSC/FDF、未发布GOP、未构建新FD/boot或上机。旧S-007 consumed，最近完整Android/root/A槽/解锁/原分区与备份摘要核验为16:06:22。当前无人工或审批待办，原始影音本地。

已明确关键板差：enuma保存FDT的默认K81双CPHY为video模式、每链路800x2560；本机只读Android DRM记录1600x2560视频模式，不是当前UEFI扫描输出证明。cas命令模式/CTL_START策略不直接采用。新解码器使用显式宽高/splash边界/mode及每pipe局部→全局原点，未知原点拒绝，支持分块完整覆盖与严格格式/范围检查。成功仍保留活动性、混合/遮挡、CPU地址关系、刷新、拓扑五项要求，不允许清标志换协议。

生产代码28个ASan/UBSan解码场景、267个回调失败位置通过；freestanding AArch64对象无外部未定义符号。Capture最多267回调、最大偏移0x73830，无direct MMIO/pixel指针及任何硬件写入。测试是合成快照，不是实机寄存器、完整UEFI链接或GOP通过。来源、SHA、许可均固定，未复制cas平台内存/面板/物理Blt/刷新逻辑。firmware源0080640已推送，源锁/gitlink同步，原board/plan未改。

下一步接真实GOP后端及同次UEFI快照/双链路原点判定：复用FrameBufferBltLib，核活动和稳定路由、混合、splash访问与视频刷新条件，再生成可审查完整载荷候选；不得发布假成功GOP或重复失败旧镜像。R-004映射仍为staging精确补丁，未来实际FD必须重新审核，原迁移表缺MDP不能当新映像已具备映射。当前尚无可直接填入OriginMask的实机拓扑记录，且五项运行条件仍未闭合。

详见operations/2026-10-25-inherited-gop-offline.md、reports/enuma-inherited-scanout-host.json、enuma-inherited-scanout-inputs.json。本轮只做Android身份/DRM只读查询，没有新boot/像素/MMIO/分区写入。D-193官网复审主线保持：真实GOP/可见错误优先，OEM深层早停转备用，通用RAM驱动/QR与schema2迁移分开评估。构建基线尚无0080640对应新完整镜像，既有cb9e568实测归档仅历史且均consumed。

没有board/bringup-plan内存字段、verified、flash/erase/改槽变化，R-002/R-015/像素硬边界保持。仍无13项运输/GOP/XNU/iPadOS实机通过，PMGR/UFS/root/Data未闭合。本阶段离线完成不等于最终目标完成。


## D-195：真实GOP后端先完成UEFI/QEMU，再采同次板级证据

来源：用户本轮指令、UEFI GOP契约及固定小米52a2f18 LM/CTL实现。复用Mu FrameBufferBltLib，不复制cas物理写入/CTL_START；按LM right bit推局部原点。三个快照/两路计数只清配置/活动/刷新要求，ADDRESS/TOPOLOGY保留。原WT映射不满足当前UC后端契约；用新只读候选补证。旧R-005/value计划及S-007不复活。8d85d39 UEFI RAM自测QEMU通过，不是enuma/GOP成功。当前先避免闲置LM混合读取，资格和全部文档发布后沿已有授权单笔。


## D-196：先单笔同次双链路只读资格，不发布未证实GOP

活动CTL限定两个LM，969读/两次100ms；先原生counter-enable3/timing/active再读混合，避免默认读取闲置LM。真实后端已QEMU执行，CPU/SMMU/缓存和下游关联仍未知。S-008完整FAT只读取证与旧消耗计划分离；实际产物绑定、全部文档推送和即时恢复条件后直接单笔，不再次审批。2/7秒时序只作支持，超时优先恢复、同图不重试。


## D-197：S-008恢复后先隔离同入口常量返回

只读同次采样超时而入口尚未实证；不能称GOP/某MMIO失败。实际AutoGen构造器仅SerialPortNull debug与BootServices表，禁用reset构造器检查保持。新对照应保留同INF/GUID/构造器/完整FAT，只把正文替换为常量PASS，不查内存表、不读寄存器、不发布协议。它能推翻正文访问主嫌疑，或支持进一步最小读隔离。旧value计划及失败S-008不复活。恢复独立通过后按用户规则自动离线实现/资格，所有文档推送后才新单笔。


## D-198：S-009同INF/GUID/构造器常量正文对照资格

新c7c29bb保持Core/配置/AutoGen/库/完整输入；实际72PE比较限制仅正文运行时代码变化，Pcd差异精确RSDS GUID。实际入口0x1050..10dc正常路径无调用/硬件读取，保存UEFI表并返回1；非空断言支路保留，不能把它当硬件无条件返回保证。新反汇编完整覆盖text及填充，digest绑定，未审查控制报告runner拒绝。符合当前文档发布与即时恢复门禁后单笔，不继承旧value或S-008消费资格。


## D-199：以实测因果对照和厂商电源/拓扑事实修正路线（归因强度由D-200取代，范围/拓扑/alpha修复保留）

S-009常量正文自动返回且实际Core/构造器/输入不变，S-008正文访存升为首嫌；未读帧缓冲，WT/alpha/GOP Blt不解释本轮超时。厂商普通dump先runtime-power引用，video不需要命令字段；删除无关银行，运行上限969→330并标明观察掩码。默认panel2/0/2明确双LM/零压缩/双接口，优先无DSC继承；两独立SSPP是假定软件范围，待有依据扩展。Mu填色不写opaque alpha，先拒绝source-alpha开启格式。新源全FD/实机资格另做，不把主机通过当硬件通过，也不为掩盖采集问题改缓存或写clock。


## D-200：先修同点双结果终止，撤回过强正文定位；摘取适用AGENTS

Core明确只拦旧query1 PASS，FAIL继续dispatcher，completion fallback不是watchdog。S-009与S-008返回处理并不对称，不能据此确证正文挂点。新terminal只认同一完整GUID返回点的1/5，2/7秒终止，不走后续dispatcher且禁completion fallback；不识别的结果仍未知。197真实头文件场景通过，实际新Core/镜像还需资格。用户授权摘取Downloads附件适用条目，根AGENTS增加简明沟通、证据/假设/反证、逆向交付和对照流检查；不替换既有门禁、不导入通用授权或其他场景模板。


## D-201：实际同点双结果Core产物资格后再验证video-only

新Core实际函数0xf90c..f9b8已核hook13、状态1/5和完整GUID，然后FAIL7秒/PASS2秒直接复位。两级宏和实际FD/Core/provider、完整输入和归档绑定；旧非对称profile被新qualifier/runner拒绝。197头文件及22固件单测、当前恢复采集门禁通过，当前文档发布后S-010一笔。分类仍限时序支持；超时只表示没有识别的terminal报告，不直接称寄存器挂点。


## D-202：未发送的身份拒绝不算固件结果

2026-10-25T18:23+08:00。S-010准备流程在fastboot身份门禁中止：首个product查询返回enuma，current-slot/unlocked及后续完整查询失败，部分remote FAILED仍返回主机退出码0，精确值检查正确拒绝。未执行fastboot boot，镜像24aed9e0…ae9e2386未消耗；不能记为固件超时、PASS或FAIL。is-userspace也未返回有效值，不能据此认定fastbootd。已向先前选定的enuma执行普通reboot，随后独立核验Android完成/root/A槽/解锁及两个设备分区与本地备份摘要全部通过。112帧拍屏仅本地，无音频；原始中止result.json保留。当前无人工或审批待办。

下一步先排查fastboot GetVar异常与设备/主机交互，保留精确机型/槽位/解锁门禁；不得将Android检查替代fastboot检查，也不把此次未发送当失败镜像重试。S-010仍只有离线资格，尚无新固件实机结果。修正并落实文档、通过即时身份/备份/采集/恢复门禁后，再按已有授权单笔。当前不追加启动。


## D-203：重新核验后按新指令执行S-010

2026-10-25T18:25+08:00。用户明确要求重启fastboot后执行S-010并按结果推进。Android完成/root/A槽/解锁、boot_a/vendor_boot_a设备与本地备份摘要再次独立通过（out/device-tests/20261025T182509-recovery-reconciliation.json）；1920x1080相机通过，不采音频。不可变镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386及1a4b204资格再次通过，尚未消耗。

文档提交推送后由既有runner定向重启选定enuma到bootloader，仍要求product=enuma/current-slot=a/unlocked=yes全部精确通过；再次异常则不发送，保留日志并恢复排查，不用Android结果代替fastboot门禁。通过后仅一笔S-010临时boot，连续本地拍屏及主机时序，75秒观察，无已识别返回立即consumed并停止追加，先恢复核验。2/7秒仅支持terminal分类，不唯一证明内部路径；未发布真实GOP。原始影音仅本地out，不上传Git/Release/CI。无flash/erase/改槽、内存字段或verified变更。此前D-202未发送的原始记录保留。


## D-204：S-010受控返回后优先拆分拒绝原因

2026-10-25T18:29:27+08:00。S-010已于18:26:07（UTC10:26:07.186360）执行一次临时boot，镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386，固件1a4b20487aa6ac0fbb2973bf508aea1851b61192，FD490fe01ebda7bf8091b3944a54135fb439f73c8c0f05d8ac609e7cdd19b9ba9e。全部执行前文档7d1312b已推送；即时Android/备份/相机门禁及fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过。上次GetVar异常没有重现，根因仍未知，不删除D-202原始中止记录，不放宽身份检查。

命令2.641秒返回，5.110秒观察断开，ADB25.469秒出现、39.438秒完成Android。runner未发恢复reboot；随后独立核验完成/root/A槽/解锁和boot_a/vendor_boot_a设备及本地备份摘要全部通过。270/270拍屏帧解码通过，已目视核对试前桌面、中途小米/Android启动标志及试后桌面；无UEFI/GOP文本证据。原始影音仅out/camera-capture/20261025T182550-system-transport，未录音，不上传Git/Release/CI。

本笔有受控返回，不能记为75秒无报告超时。相对S-009，ADB晚4.313秒、完成晚4.219秒，支持FAIL5/7秒终止的谓词拒绝判断，中等置信；不是直接状态日志，也不是PASS/GOP成功或精确寄存器定位。两个候选Core与采集范围不同、Android时序含噪声，不能仅凭差值确证7秒或S-008根因。S-010已consumed，S-001..010及旧失败图不重试。

按结果推进：主判断转向保守准入模型与实际继承布局不匹配，优先细分首次拒绝阶段/状态，不再默认把本笔当MMIO挂死或盲改缓存。源码要求单CTL/双LM/两个独立SSPP、无border/额外staging、严格dim/blend及RGBX；历史step21保守混合拒绝提供同方向旁证，但不是本笔快照。单源跨LM、border/合法混合、格式/几何/地址边界列为候选；描述表/PCD门禁、双接口前置/稳定性仍不能排除。只有直接取得阶段/状态或同入口对照后才能排序到具体寄存器，不放宽安全准入换通过。

新候选尚未实现/资格/执行。下一步保持同完整输入、完整GUID双结果终止及FALLBACK0，先设计可判读的首拒绝证据（同时区分未到达与已拒绝），主机故障注入和实际Core/provider审查后再构建；不恢复旧长时间编码或失败像素/value计划。若新证据显示采样/解码已全部通过或故障在入口前，则推翻当前拒绝模型主假设。真实GOP/CPU-SMMU/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合；ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更，当前无人工或审批待办。

证据：reports/enuma-inherited-video-S010-result.json；原trial out/device-tests/20261025T182553-system-transport/result.json；独立恢复out\device-tests\20261025T182657-recovery-reconciliation.json。身份解析3项、恢复核验2项、恢复硬门1项回归通过；不可变归档各文件摘要再次匹配。当前源码固件未改动，设备文档/脱敏证据单独提交推送。


## D-205，互补首拒绝分类源码/主机通过，完整构建进行中

2026-10-25T18:39:28+08:00。用户要求继续推进。S-010已consumed，最后独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要通过，原结果D-204保留。当前固件8710ebd93da7b19bb7ffd0e388f6925399231153新增互补首状态查询，未改采样/拓扑/格式/地址准入、Core双结果终止和完整FAT，不发布GOP、不访问像素、不新增硬件读写。新入口把首个有效status==Topology13映射query1的marker1（2秒），其余有效状态marker5（7秒）；query2精确反转。描述表/PCD拒绝作为Arguments11。无效状态、成功但错误Requirements不发已识别marker；诊断match不能称完整采样/GOP成功。

55个生产选择器用例、原GOP/拓扑/330读失败及等待失败主机回归通过，23个固件相关Python回归及3个双时序解析回归通过。源码已提交推送；实际两FD/PE/编译宏、归档和完整打包资格另核。只允许固件-owned构建和设备-owned打包/恢复，原内存/verified/分区边界不变。

预先固定两笔计划：S-011=query1，受控回Android且独立恢复通过后，文档再次推送才S-012=query2。任一身份/采集/恢复异常、超时或单笔明显不受控则停止后续；失败图不重试。两笔均完整同源同输入，同Core及构造器，唯运行代码差异限provider选择结果。配对比较negative-minus-positive的ADB出现和Android完成两指标：均在+3..+7秒只支持Topology状态；均在-7..-3秒只支持非Topology；任何其他组合记ambiguous并冻结该对。该容差是预先采用的判读窗口，不是硬件标定精度；跨启动状态变化和Android噪声仍可混淆，不声称直接读到状态。75秒无已识别返回仍立即consumed并先恢复。保留必要的完整输入和现场恢复条件，原始影音仅本地out且不采音频。

当前没有S-011/S-012设备动作，两候选完整产物资格尚未完成；当前无人工或新增审批待办。新资格完成并落实全部文档推送、即时身份/备份/相机/恢复后才逐笔执行。


## D-206，互补分类实际产物资格通过，先单笔S-011

2026-10-25T18:44:56+08:00。用户要求继续推进。S-010已consumed，其试后独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要通过，原结果D-204保留。当前固件8710ebd93da7b19bb7ffd0e388f6925399231153新增互补首状态查询，未改采样/拓扑/格式/地址准入、Core双结果终止和完整FAT，不发布GOP、不访问像素、不新增硬件读写。新入口把首个有效status==Topology13映射query1的marker1（2秒），其余有效状态marker5（7秒）；query2精确反转。描述表/PCD拒绝作为Arguments11。无效状态、成功但错误Requirements不发已识别marker；诊断match不能称完整采样/GOP成功。

55个生产选择器用例、原GOP/拓扑/330读失败及等待失败主机回归通过，23个固件相关Python回归及3个双时序解析回归通过。源码已提交推送；实际两FD/PE/编译宏、归档和完整打包资格另核。只允许固件-owned构建和设备-owned打包/恢复，原内存/verified/分区边界不变。

预先固定两笔计划：S-011=query1，受控回Android且独立恢复通过后，文档再次推送才S-012=query2。任一身份/采集/恢复异常、超时或单笔明显不受控则停止后续；失败图不重试。两笔均完整同源同输入，同Core及构造器，唯运行代码差异限provider选择结果。配对比较negative-minus-positive的ADB出现和Android完成两指标：均在+3..+7秒只支持Topology状态；均在-7..-3秒只支持非Topology；任何其他组合记ambiguous并冻结该对。该容差是预先采用的判读窗口，不是硬件标定精度；跨启动状态变化和Android噪声仍可混淆，不声称直接读到状态。75秒无已识别返回仍立即consumed并先恢复。保留必要的完整输入和现场恢复条件，原始影音仅本地out且不采音频。

两份完整不可变资格已完成，无新boot。S-011(query1)镜像4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7，FDfa02b3a0ed300f4876c2f2b7a691efb1dbe2abbab17279e8c4f4b317245451d4；S-012(query2)镜像4454dfaa0b00d08d277e921641b51b250850906236770d6514f97cca51f54389，FDd82cf752f0d6e7d6831a49878b05cb100c2dbbca76a0d75c30986013d22dd57c。每份103817216字节、完整96MiB FAT。归档out/inherited-gop/qualified-topology-8710ebd-q1和q2。实际Core可执行段均等于已审查S-010；实际两provider只有两处前置拒绝返回常量与一处status13选择条件三条指令不同，其他实际PE只允许已精确核对的CodeView GUID变化。Core/provider实际宏均TERMINAL1/FALLBACK0，TOPOLOGY_QUERY分别1/2，R-004记录/实际PE/入口与所有采集源码/BootShim/完整FAT摘要通过。

Android/root/A槽/解锁/设备和备份摘要及1920x1080相机再次通过。源码8710ebd已推送。当前文档与资格提交推送后，S-011一笔；S-012仍待S-011有界返回、独立恢复核验及结果文档推送，不批量连发。预先窗口见上文，不更改观测判据。实际代码证据reports/enuma-video-topology-code.json与enuma-video-topology-pair-code.json；正反资格分别enuma-video-topology-positive-qualification.json和negative-qualification.json。当前无人工/审批待办。


## D-207，S-011受控返回并独立恢复，准备互补S-012

2026-10-25T18:46:54+08:00。用户要求继续推进。S-010已consumed，其试后独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要通过，原结果D-204保留。当前固件8710ebd93da7b19bb7ffd0e388f6925399231153新增互补首状态查询，未改采样/拓扑/格式/地址准入、Core双结果终止和完整FAT，不发布GOP、不访问像素、不新增硬件读写。新入口把首个有效status==Topology13映射query1的marker1（2秒），其余有效状态marker5（7秒）；query2精确反转。描述表/PCD拒绝作为Arguments11。无效状态、成功但错误Requirements不发已识别marker；诊断match不能称完整采样/GOP成功。

55个生产选择器用例、原GOP/拓扑/330读失败及等待失败主机回归通过，23个固件相关Python回归及3个双时序解析回归通过。源码已提交推送；实际两FD/PE/编译宏、归档和完整打包资格另核。只允许固件-owned构建和设备-owned打包/恢复，原内存/verified/分区边界不变。

预先固定两笔计划：S-011=query1，受控回Android且独立恢复通过后，文档再次推送才S-012=query2。任一身份/采集/恢复异常、超时或单笔明显不受控则停止后续；失败图不重试。两笔均完整同源同输入，同Core及构造器，唯运行代码差异限provider选择结果。配对比较negative-minus-positive的ADB出现和Android完成两指标：均在+3..+7秒只支持Topology状态；均在-7..-3秒只支持非Topology；任何其他组合记ambiguous并冻结该对。该容差是预先采用的判读窗口，不是硬件标定精度；跨启动状态变化和Android噪声仍可混淆，不声称直接读到状态。75秒无已识别返回仍立即consumed并先恢复。保留必要的完整输入和现场恢复条件，原始影音仅本地out且不采音频。

S-011(query1)于18:45:34发出，镜像4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7已consumed。命令2.625秒、断开5.093秒，ADB26.484秒/完成40.547秒受控回Android，无主机恢复reboot。独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要全部通过，278/278帧解码，原始影音仅本地无音频。证据reports/enuma-video-topology-S-011-result.json，原trial out/device-tests/20261025T184520-system-transport/result.json。

单笔时序接近长返回，仅初步支持首次状态非Topology，不据此确证。按预先计划，当前文档提交推送后执行S-012(query2)一次，仍保持即时Android/备份/fastboot/相机/恢复门禁及75秒期限，完成互补核对后才分类。S-011与S-010及旧图不重试；当前无人工/审批待办。


## D-208，互补支持非Topology，Android核验通过，转查计数前置

2026-10-25T18:50:24+08:00。用户要求继续推进。S-010已consumed，其试后独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要通过，原结果D-204保留。当前固件8710ebd93da7b19bb7ffd0e388f6925399231153新增互补首状态查询，未改采样/拓扑/格式/地址准入、Core双结果终止和完整FAT，不发布GOP、不访问像素、不新增硬件读写。新入口把首个有效status==Topology13映射query1的marker1（2秒），其余有效状态marker5（7秒）；query2精确反转。描述表/PCD拒绝作为Arguments11。无效状态、成功但错误Requirements不发已识别marker；诊断match不能称完整采样/GOP成功。

55个生产选择器用例、原GOP/拓扑/330读失败及等待失败主机回归通过，23个固件相关Python回归及3个双时序解析回归通过。源码已提交推送；实际两FD/PE/编译宏、归档和完整打包资格另核。只允许固件-owned构建和设备-owned打包/恢复，原内存/verified/分区边界不变。

预先固定两笔计划：S-011=query1，受控回Android且独立恢复通过后，文档再次推送才S-012=query2。任一身份/采集/恢复异常、超时或单笔明显不受控则停止后续；失败图不重试。两笔均完整同源同输入，同Core及构造器，唯运行代码差异限provider选择结果。配对比较negative-minus-positive的ADB出现和Android完成两指标：均在+3..+7秒只支持Topology状态；均在-7..-3秒只支持非Topology；任何其他组合记ambiguous并冻结该对。该容差是预先采用的判读窗口，不是硬件标定精度；跨启动状态变化和Android噪声仍可混淆，不声称直接读到状态。75秒无已识别返回仍立即consumed并先恢复。保留必要的完整输入和现场恢复条件，原始影音仅本地out且不采音频。

S-011与S-012互补两笔均已执行并consumed。S-011(query1)于18:45:34发送4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7，命令2.625秒/断开5.093秒/ADB26.484秒/完成40.547秒；S-012(query2)于18:47:15发送4454dfaa0b00d08d277e921641b51b250850906236770d6514f97cca51f54389，命令2.640秒/断开5.109秒/ADB20.062秒/完成33.781秒。两笔fastboot机型/槽位/解锁首轮精确通过，均无主机恢复reboot、受控回Android，随后各自独立完成/root/A槽/解锁与boot_a/vendor_boot_a设备及本地备份摘要核验通过。278/278与245/245帧解码，已目视核对恢复桌面；全部原始拍屏/视频只留本地out/camera-capture/20261025T184517-system-transport及184658-system-transport，无音频、未上传。

negative-minus-positive的ADB差-6.422秒、完成差-6.766秒，均在执行前固定的-7..-3窗口，支持首个有效状态非Topology13。不是直接状态日志，不能据此称拓扑合格或GOP通过；非Topology集合包含成功状态0和错误1..12，跨启动状态变化仍可混淆。因此D-204“拓扑模型首嫌”优先级下调，不能继续把两个独立SSPP/边框作为已定位故障，更不改相关准入来凑PASS。

进一步固定源码/历史审查：小米52a2f18 sde_hw_intf_v1_get_status仅以INTF_STATUS bit0读FRAME_COUNT，不要求Enable&3==3；历史step15该复合使能前置拒绝，而step18保留使能值稳定并观察至少一路双窗递增获得支持。当前Evidence.c又在首样本和稳定性中对两路强制Enable&3==3，是比原生状态路径和历史成功谓词更强的条件。此为已确认的软件/历史差异，不是本次计数使能数值或确切拒绝点；当前领先假设转为RefreshMode10类的接口/计数前置或稳定性，置信中等。元数据/PCD、revision/mode/格式/几何/地址等拒绝以及成功0仍未排除。

下一步先以新候选区分RefreshMode10及互补，必要时再分首次接口资格和后续等待/稳定性；取得分类后才依据原生status/实际递增评估精确谓词修正。不直接删除Enable门禁、放宽双链路或回旧失败图。若结果非RefreshMode10或直接counter资格已满足/采样成功，应推翻该首嫌排序。新RefreshMode候选尚未实现/构建/资格/执行；本轮新增软件、两份完整资格、互补实测与离线审查均完成，S-001..012不重试，当前无人工/审批待办。

机器证据：reports/enuma-video-topology-S-011-result.json、S-012-result.json、pair-result.json、enuma-video-topology-code.json、enuma-video-topology-pair-code.json，以及enuma-video-counter-gate-review.json。固件8710ebd已推送，实际两Core可执行段与已审查S-010相同，provider仅三条结果指令差异，完整输入保持；55生产选择器场景、330读失败与GOP/拓扑主机和AArch64对象检查、23固件回归与3配对解析回归通过。


## D-209，首计数门禁与后续稳定性分类源码通过，完整构建中

2026-10-25T18:59:20+08:00。首返回原因记录及计数/稳定性互补选择器主机通过，完整构建中，无S-013/S-014。设备最后S-012独立Android/root/A槽/解锁/原分区与备份核验通过；S-001..012均consumed。

用户明确要求隔离计数使能和稳定性，完成审计后直接上机。新Detailed采样只记录首个返回原因；保留旧版完整谓词、短路优先级、原330读/两次100ms/最大0x6c26c、失败Out不变，不在拒绝后继续。原因枚举区分首样本Timing/Active、首样本Enable、后续Enable/接口变化、等待失败、配置变化、接口稳定性、Frame不推进和其他流水线/参数失败。counter-enable target1只匹配首样本Enable&3!=3（reason5）；stability target2匹配后续资格/配置/接口/帧失败reason6/9/10/11/13。首样本计数门禁先失败时，后续稳定性未执行，不把未执行写失败。

实际生产选择器164场景通过；固定旧8710ebd源码作为oracle，对330读失败位置及成功路径逐一比较完整回调/等待顺序、返回值和Out字节一致；新增首/后续计数、Timing/Active、等待、配置变动和计数停滞原因用例通过，原GOP/拓扑及AArch64对象保持。24固件Python回归、4配对解析回归通过。固件源码已提交推送，新完整FD/PE/编译宏/打包/归档资格正在完成；当前无新boot。

预先计划：S-013 target1/query1，受控回Android并独立核验、当前文档再次提交推送后才S-014 target1/query2。不沿用旧已消耗镜像。两笔同源/同完整FAT/同Core终止点，query1匹配原因2秒、其他有效原因7秒，query2精确反转；不增加旧长延时编码。配对negative-minus-positive的ADB出现和Android完成两指标均+3..+7秒仅支持选中原因，均-7..-3秒仅支持其他原因；其余ambiguous。分类不等于直接状态数值，未匹配集合含成功完成，跨重启继承变化和Android噪声仍是限制。75秒无已识别返回立即consumed、停追加并先恢复。若target1不支持，再按实际结果选首次接口或后续稳定性，不能盲删Enable门禁或放宽显示准入。

执行前必须通过所有源码/实际产物资格、当前文档提交推送及即时唯一enuma身份/备份/fastboot精确机型槽位解锁/相机/恢复门禁。历史S-011/S-012支持非Topology（包含成功0），仍不能定位本次确切拒绝点。

固件b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107；真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。


## D-210，计数首拒绝互补产物已审查，准备S-013

2026-10-25T19:07:27+08:00。首样本计数门禁互补候选已完成实际产物审查，当前文档推送后先S-013一笔；S-014待前笔受控返回、独立恢复及文档再次推送。当前Android核验通过，无新boot、无人工/审批待办。

S-013 target1/query1镜像1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，FD54f057e2306d27d7e77f658472fc89a3de63339886afbfd4b1601f839a7b3d6a；S-014 target1/query2镜像54f466c1fa0e617af343c237ac65b132d17b68640196f877c474453a86cff523，FD835147420761982c133e90f5d943f047c78e6de18fe414edf6f8e630ba1da139。均103817216字节、完整96MiB FAT，归档out/inherited-gop/qualified-counter-b93b3bb-q1/q2。实际Core可执行段均与已审查S-010完全一致；两provider全指令比较仅0x112c、0x1188两处元数据拒绝返回常量5/1和0x2874一处csinc条件eq/ne不同；该三条完整差异已逐条审查并绑定SHA40e0c19e8f6a9e2bd1a5ab417f6d2eda64bc46ddf4a9b969a9409144df673552。Core/其余模块、构造器、库、BootShim、完整FAT不变，非provider差异只精确CodeView GUID，实际PE/源码/两级编译宏/FD中R-004记录和不可变资格通过。

Reason5只表示首样本Timing已非零后Enable&3!=3首先拒绝；仍不能给出接口编号、缺失哪一bit或该接口Active值（原条件优先级保持，Enable失败后Active检查不再执行）。此时最多首样本9读，无等待、无管线/Decode、无后续稳定性。stability target2覆盖后续资格和稳定性原因6/9/10/11/13，尚未执行。所有原始判据、读/等待顺序和失败Out保持旧8710ebd，callback oracle覆盖330失败位置及成功/多类原因；164选择器、24固件回归和4配对解析回归通过。

预先固定配对negative-minus-positive：ADB出现和完成两项均+3..+7秒仅支持Reason5，均-7..-3秒仅支持其他原因（含成功Complete），否则ambiguous。两次跨重启状态可能变化，时序不当作直接原因日志。若首门禁匹配，后续稳定性记未执行，不把它写失败；若不匹配，继续选初始Timing/Active或后续稳定性，不能为PASS盲删准入。任何身份、采集、恢复异常或75秒无已识别返回立即consumed、停追加并先恢复。S-001..012及旧失败图不重试。

即时独立Android完成/root/A槽/解锁/设备与备份摘要及1920x1080相机再次通过，现场恢复路径沿已示范受控/长按恢复，不声称75秒是固件自动返回保证。两笔分别完整文档提交推送和门禁后临时fastboot boot，无分区操作。证据reports/enuma-video-reason-code.json、enuma-video-reason-pair-code.json及counter正反资格。

固件b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107；真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。


## D-211，S-013受控返回已核验，准备互补S-014

2026-10-25T19:09:12+08:00。S-013已受控回Android并独立核验完成/root/A槽/解锁/原分区与备份摘要通过，已consumed；当前文档推送后按原计划执行互补S-014一笔。

S-013 target1/query1于19:07:50发送1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，命令2.640秒/断开5.109秒/ADB20.078秒/完成34.343秒，无主机恢复reboot。248/248帧解码，已目视确认恢复桌面；原始影音只本地out/camera-capture/20261025T190733-system-transport，无音频。证据reports/enuma-video-counter-S-013-result.json，原始trial out/device-tests/20261025T190736-system-transport/result.json，独立恢复out\device-tests\20261025T190837-recovery-reconciliation.json。

短返回初步支持首样本Enable门禁Reason5，尚未完成互补，不能确证原因或位值；后续稳定性仍未获证据。当前未执行S-014，文档提交推送后沿原固定资格执行target1/query2。保持source b93b3bb、实际Core/provider审查、完整FAT和既有精确身份/备份/采集/恢复门禁；75秒无已识别返回停止追加并先恢复，所有已执行镜像不重试。

配对预先窗口不变：negative-minus-positive的ADB出现和完成均+3..+7秒才支持选中Reason5，均-7..-3秒支持其他有效原因（含成功Complete），其他记ambiguous。此为间接分类；先拒绝条件后的项记未执行。当前无人工或新增审批待办。

固件b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107；真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。


## D-212，互补支持首计数门禁拒绝，后续稳定性未到达，Android已核验

2026-10-25T19:12:38+08:00。S-013/S-014互补时序支持首样本Enable门禁Reason5，后续稳定性按该路径未执行；两笔Android/root/A槽/解锁/原分区与备份独立核验通过，均consumed。下一步独立验证原生双路计数推进，不放宽GOP准入。

S-013 target1/query1于19:07:50发送1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，命令2.640秒/断开5.109秒/ADB20.078秒/完成34.343秒；S-014 target1/query2于19:09:35发送54f466c1fa0e617af343c237ac65b132d17b68640196f877c474453a86cff523，命令2.641秒/断开5.125秒/ADB26.516秒/完成41.063秒。两笔fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过，无主机恢复reboot，随后分别独立核验Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与本地备份摘要全部通过。248/248与279/279拍屏帧解码，已目视核对恢复桌面；原始影音仅out/camera-capture/20261025T190733-system-transport及190918-system-transport，无音频、未上传。

negative-minus-positive：ADB+6.438秒、完成+6.720秒，均在执行前固定的+3..+7秒窗口。支持Reason5首样本CounterEnable条件先拒绝（中等置信），不是直接原因/寄存器数值日志，也不称GOP/显示成功。跨启动继承变化和Android噪声仍可混淆；S-010/S-011/S-012的历史结果不改写。

源码路径含义：Reason5只在N=0且Timing非零、Enable&3!=3时赋值，随后立即返回；按该分类成立的前提，采样回调最多9读、零等待，完整CTL/SSPP/LM采集、Decode及后续稳定性均未到达。不能称稳定性失败、Frame不递增、某接口不活动或某个bit为零；拒绝接口与实际Enable值未知，Enable检查之后的Active条件也可能尚未执行。实际执行读数仍未知，9为条件路径上限，不当作数字转储。

当前主判断从泛化RefreshMode/稳定性收敛到过强的首样本Enable资格门：它阻断了对实际帧进展的观察。固定小米52a2f18 v1 get_status读取活动接口FrameCount不要求Enable&3==3；旧step15使能复合条件拒绝与step18原生至少一路双窗递增支持只作为同方向历史旁证，不能当本次两路数值。不能直接删条件换PASS，也不修改CounterEnable或时钟。

下一步：实现独立诊断前缀，沿原映射仅观察两路原生活动状态、Timing与Enable稳定值、两窗各1..64非回绕Frame增量；不把Enable是否精确3作为其提前返回条件，不访问尚未证明安全的后续管线银行、不发布GOP。该前缀是新的独立观测，不等于放宽完整EnumaSampleVideo准入；成功后才评估有依据的原生资格修正，失败再细分活动性/稳定性/计数进展。新前缀尚未实现/构建/资格/上机，完整采样所有原条件保持。若新证据显示原因非5、两路不活动/不稳定或CounterEnable实际已满足，应修正当前判断。

新增Detailed接口保留旧入口语义：固定8710ebd oracle覆盖330失败位置和成功的完整回调/等待顺序、返回状态、Out字节；首/后续计数、初始接口、等待、配置变动及Frame停滞原因用例通过，164选择器场景、24固件和4配对解析回归及AArch64对象通过。实际两FD/PE/宏/R-004/完整FAT/BootShim不可变资格通过，实际Core可执行段与已审查S-010相同，provider仅三条映射指令差异已人工审查并摘要绑定，现场运行前提交均已推送（d6c9dfa资格、f399374首笔结果）。

证据reports/enuma-video-counter-S-013-result.json、S-014-result.json、pair-result.json、path-interpretation.json，enuma-video-reason-code.json及pair-code.json；源码b93b3bb已推送。S-001..014及旧失败图不重试，当前无人工/审批待办。

固件b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107；真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。


## D-213：替代显示/日志路线实测账本复核

2026-10-25T19:19:31+08:00。D-213替代路线对账：已核原厂显示栈/线程关闭、R-005/R-007像素及R-002跨bootloader标记的已执行结果，区分UART只读发现、独立背光未资格、warm/USB/QR未实机闭合。缺头文件不等于必须自写I2C，缺DEPEX GUID不解释APRIORI驱动黑屏。无新设备动作，D-212计数隔离结论与下一步独立原生计数观察不变；详情operations/2026-10-25-display-log-route-ledger.md和reports/enuma-display-log-route-ledger.json。 前一实测结果dea611f已提交推送；固件b93b3bb不变。无新审批请求或媒体上传。


## D-214：固定公开实现与原生ramoops只读发现

2026-10-25T19:28:32+08:00。D-214公开实现复审新增：选定enuma当前pstore后端为ramoops，0xB0000000/4MiB、console/pmsg各2MiB、ECC0，1024页元数据均报告Reserved；这与umi RamoopsSerialPortLib布局相合。此前FDT无节点不能排除厂商硬编码后端。日志优先审原生ramoops兼容/映射/缓存/保留链，显示继续cas式继承和独立原生活动/计数观察，I2C背光为独立支线。当前没有UEFI写入/跨复位读回资格，不更改内存表或写RAM。详见operations/2026-10-25-public-route-priorities.md及reports/enuma-ramoops-route-discovery.json。 仅root sysfs/命令行/pstore目录/页标志元数据查询，无新boot、物理内容读取、模块加载、写入或审批扩张。前次59d74d0已推送，固件b93b3bb未变。


## D-215：原生ramoops未接线实现与新映射审查

2026-10-25T19:45:02+08:00。用户支持继续后，完成固定umi来源的地址无关console writer、许可、源摘要和只读收集器；51,210项oracle/边界/ASan/UBSan及实际EDK头文件AArch64对象、5项收集器主机测试通过。当前页表确实缺少B0000000，XN别名不设置XN，warm可能cold回退；无物理访问/新boot/映射修改。固件91a8a7c56d327e30262765548e2cd98bd5107037已提交推送，设备仓随本里程碑pin；之前设备c0ab5d7已推送。完整新FD/接线需R-017精确A范围（console2MiB、44字节一次标记、MMU后有界Core、warm/cold及单笔新资格临时boot）审查后继续，B保留旧表继续计数。最终只读恢复核验通过，证据out/device-tests/20261025T194122-recovery-reconciliation.json。详见operations/2026-10-25-ramoops-compatibility-audit.md及三个ramoops审计报告；原始影音仍仅本地，无新媒体上传。


## D-216：R-017 A直接执行授权与S-015实际产物资格

2026-10-25T20:01:26+08:00。用户在精确提案后要求“上机无需批准 直接进行 注意使用摄像头记录关键节点”；批准A最小范围，不再重复询问。固件10a546ee9a6b352ec4e2bcf2b9510dad5fc48fb6已推送，conditional console map与独立DxeMain stage10 variant保留旧迁移基线/Null后端。完整构建、FD、实际Core/宏/nonce/描述符、完整FAT及Boot v3通过，镜像2583de23dbf426692e4edc573faeadb0a383147f8fa82d3f01aff1fb73abbd1e，归档out/ramoops-audit/S-015-qualified。主机canary模拟和实际反汇编复核通过；相机已目视桌面，最新只读恢复核验通过。此记录尚未上机，下一步文档提交推送及即时门禁后执行单笔S-015。具体代码与资格见reports/enuma-ramoops-canary-code.json及qualification.json。原始影音仅本地。


## D-217：S-015超时、恢复与采集证据更正

2026-10-25T20:11:30+08:00。S-015于20:04:30单次发送，命令0/2.641秒，5.110秒断开，75秒无自动回归，停止追加。用户报告恢复，20:07:27Android完成/root/A槽/解锁/设备双分区与备份摘要独立核验通过；559/559帧、最后黑屏及恢复后桌面目视，按键未获连续录像确认。65字节快照是exec-out的缺文件cat诊断，不是pstore；无有效nonce，原证据保留。镜像2583de23dbf426692e4edc573faeadb0a383147f8fa82d3f01aff1fb73abbd1e与R-017 writer单笔consumed，不重试。f17af47资格在执行前已推送。继续离线准备同范围map-only/原stage10-cold新候选，尚未构建/资格/上机，不从本次结果直接认定写入或warm是根因。详见reports/enuma-ramoops-S-015-result.json。原始影音仍仅本地，无分区/verified/pmsg扩张。


## D-218：恢复后的S-016 map-only/cold独立对照资格

2026-10-25T20:21:00+08:00。23d5538已推送S-015超时/独立恢复与采集器修复。固件a657b79018a47a0b4a6af4fe9c4b14a8f490cd12拆分map/writer，默认关闭，map-control保留原迁移header和stage10/delay2/ResetCold，不访问console内容。新镜像1fcb56736b7fbae40cf3250691c1e70b67866d375ff741bb43423f96471d1513，实际Core无writer/ResetWarm、描述符及完整FAT/Boot v3/归档资格通过；已绑定R-017-MAP独立图，不重授权consumed writer，无内存范围/分区/verified扩张。当前未上机，所有当前文档发布与即时身份/备份/相机/恢复后沿用户直接推进规则执行单笔。证据reports/enuma-ramoops-map-control-qualification.json与code.json。原始影音仅本地。


## D-219：S-016自动返回与独立恢复，问题收敛到访问/写入和warm差异

2026-10-25T20:25:27+08:00。S-016于20:21:48单次发出1fcb56736b7fbae40cf3250691c1e70b67866d375ff741bb43423f96471d1513，命令0/2.641秒、断开5.110秒、ADB20.063秒、完成35.406秒，无主机恢复reboot。251/251帧解码，目视Android重启logo和桌面，独立完成/root/A槽/解锁/设备双分区与本地备份摘要通过。e2b6ea5资格此前已推送；S-016与R-017-MAP单笔consumed。支持同范围map-only+原cold路径可控，不能称console物理访问/留存或GOP已验证；S-015物理writer访问与warm差异仍未分离，单独映射不再首嫌但未完全排除。下一步最小头只读/cold隔离，尚未实现/资格/执行。证据reports/enuma-ramoops-S-016-result.json与out\device-tests\20261025T202334-recovery-reconciliation.json，原始影音仅本地。


## D-220：S-017头部三读/cold隔离

2026-10-25T20:49:39+08:00。自动返回Android并独立核验。固件89e6491626ed0edbc48dc7fb41a6902e8ce7eb4c，图0586196e4666f9e119cca0afd984901b635084237a30a29e82d9450e2a3ca43a，实际三load/无console store/warm审查与完整载荷归档资格通过。沿用户继续及直接上机授权，同已批准范围，无pmsg/分区/verified扩张。本笔结果见reports/enuma-ramoops-S-017-result.json。原始影音只留本地。


## D-221：S-018无访问warm独立隔离

2026-10-25T20:56:03+08:00。构建/实际产物资格完成，尚未发出。固件5cfcd4cc68c0c37ffb322322efc256760d9389e3，图6b145fd370bb67a5db16112764701d8a4234b27c0eabc5d9e043bb7d92d843a5，仅同映射stage10/delay2/ResetWarm无console访问，实际PE/宏/描述符/完整FAT/Boot v3已资格；用户继续至硬停，不重复一般批准。执行状态见STATUS，consumed图不重试。原始影音仅本地。


## D-221：S-018无访问warm独立隔离

2026-10-25T21:00:18+08:00。触发75秒无返回硬停，停止追加镜像，恢复状态待核验。固件5cfcd4cc68c0c37ffb322322efc256760d9389e3，图6b145fd370bb67a5db16112764701d8a4234b27c0eabc5d9e043bb7d92d843a5，仅同映射stage10/delay2/ResetWarm无console访问，实际PE/宏/描述符/完整FAT/Boot v3已资格；用户继续至硬停，不重复一般批准。执行状态见STATUS，consumed图不重试。原始影音仅本地。


## D-221：S-018无访问warm独立隔离

2026-10-25T21:01:06+08:00。超时硬停，仍待恢复核验；停止追加镜像。固件5cfcd4cc68c0c37ffb322322efc256760d9389e3，图6b145fd370bb67a5db16112764701d8a4234b27c0eabc5d9e043bb7d92d843a5，仅同映射stage10/delay2/ResetWarm无console访问，实际PE/宏/描述符/完整FAT/Boot v3已资格；用户继续至硬停，不重复一般批准。结果见reports/enuma-ramoops-S-018-result.json；触发超时后不追加设备启动。原始影音仅本地。


## D-221：S-018无访问warm独立隔离

2026-10-25T21:02:06+08:00。超时硬停后Android已独立恢复；按用户要求停在此处。固件5cfcd4cc68c0c37ffb322322efc256760d9389e3，图6b145fd370bb67a5db16112764701d8a4234b27c0eabc5d9e043bb7d92d843a5，仅同映射stage10/delay2/ResetWarm无console访问，实际PE/宏/描述符/完整FAT/Boot v3已资格；用户继续至硬停，不重复一般批准。结果见reports/enuma-ramoops-S-018-result.json；触发超时后不追加设备启动。原始影音仅本地。


## D-221补充：S-018硬停后独立恢复与最终停止

2026-10-25T21:03:20+08:00。a3870d3已推送超时/恢复待核验记录；用户报告Android恢复后，21:01:29独立完成/root/A槽/解锁及设备/备份双分区摘要通过。1090/1090帧，录像尾部Android重启logo及独立补拍桌面目视，按键动作未明确核对。原失败记录保持，S-018/R-017-WARM consumed，无后续boot。无console访问的warm对照仍超时，相对两个已返回cold对照，warm请求链为优先嫌疑但未定位FEATURES/reset2/回退，不能证明writer安全。按用户触发硬停再停，本轮完成交接推送后停止；下一最小写入+cold候选尚未实现/构建/执行。原始影音仅本地。


## D-222：用户要求的同型enuma/elish公开源码离线研究

2026-10-25T21:17:35+08:00。D-221后用户只要求参考同型仓及Wi-Fi版elish；本轮固定9仓40文件并SHA256/Git blob校验、9组源码事实通过，无新设备命令/重复恢复核验/构建/上机。Tlrenhb/enuma日志引用pipa PMIC/SPMI/PS_HOLD链但仍TODO；elish UniXNU未形成闭环，edk2-msm仍通用PSCI。新增优先方案来源为umi板级reset和pipa早期Linux reader，不把同地址/ECC参数或对方运行报告当enuma通过。下一步先离线匹配原生PON/SCM，writer+cold与持久化分开，reader移植去pmsg自测；未实施，不请求未准备好的批准。详细operations/2026-10-25-enuma-elish-reset-reference-review.md，config/enuma-elish-reset-sources.lock.json及reports/enuma-elish-reset-route-review.json。固件pin与设备硬停边界保持；原始影音仅本地，前一82430d4已推送。


## D-223：显示侧分析及独立原生观察器离线增量

2026-10-25T21:32:30+08:00。用户要求推进显示分析和UEFI，已完成NativeObserve核心（两路三样本<=26读/两次100ms、inactive-frame抑制、活动/Timing/Enable/帧进展/精确Enable3独立mask），48项ASan/UBSan与AArch64对象通过；完整GOP源/准入未变，Mu Blt/拓扑/330失败oracle/164选择回归通过。原生setup写3与status不以前者阻断读取分别保留，不简单删门。固件bbe30f697e1683e5e1621c26c85b88b9431ac7bc已推送并pin，只有未接线源，无新FD/运行时/设备动作；前一7873237研究已推送。显示验收色条/文字/恢复，背光优先原厂I2C ABI/应答，日志不再作显示分析前置。详见operations/2026-10-25-display-frontier-analysis.md和reports/enuma-display-frontier-analysis.json。原始影音仅本地。


## D-224，独立双路观测完整资格通过，准备S-019

2026-10-25T21:52:10+08:00。前一87f188b已推送离线显示观察器。固定新固件57ae4ffb136f5330d6e9b759f21202f1d12cebc5、完整FD/PE/宏/映射/载荷与cold同hook资格闭合。S-019/S-020尚未发出。先S-019 query1单笔；仅受控返回、独立恢复核验及当前文档再次推送后执行S-020 query2。证据reports/enuma-native-display-code.json、q1/q2-qualification及对应result；全部原始影音本地，禁写/内存/verified/分区边界保持。


## D-225，S-019受控返回，准备互补S-020

2026-10-25T21:54:38+08:00。前一87f188b已推送离线显示观察器。固定新固件57ae4ffb136f5330d6e9b759f21202f1d12cebc5、完整FD/PE/宏/映射/载荷与cold同hook资格闭合。S-019 query1已单次发出并受控回Android、独立恢复通过；S-019 consumed。单笔时序不分类，当前文档推送与即时门禁后继续S-020 query2；S-020尚未发出。时序：{"issued_at": "2026-10-25 21:53:31", "issued_at_utc": "2026-10-25T13:53:31.737879+00:00", "boot_command_return_seconds": 2.625, "fastboot_disconnect_observed_seconds": 5.093, "fastboot_return_seconds": null, "adb_return_seconds": 25.422, "boot_complete_seconds": 39.531}。证据reports/enuma-native-display-code.json、q1/q2-qualification及对应result；全部原始影音本地，禁写/内存/verified/分区边界保持。


## D-226，独立双路显示观测配对完成，按结果隔离

2026-10-25T21:58:11+08:00。前一87f188b已推送离线显示观察器。固定新固件57ae4ffb136f5330d6e9b759f21202f1d12cebc5、完整FD/PE/宏/映射/载荷与cold同hook资格闭合。S-019/S-020均consumed，均受控返回并独立恢复。配对结果：{"scope": "indirect same-source paired timing, not direct native register log", "conclusion": "ambiguous", "negative_minus_positive_seconds": {"adb_return_seconds": -4.281, "boot_complete_seconds": -1.359}, "predeclared_absolute_delta_window_seconds": [3, 7], "predicate": "collection success AND both active throughout AND both nonzero stable Timing AND both stable Enable AND both two-window Frame increments1..64", "exact_enable3_not_required": true, "complement_includes": ["metadata/PCD rejection", "read/wait/revision rejection", "one or both inactive", "Timing/Enable instability", "one or both nonmoving/wrapped/over64 frames"], "exact_values_observed": false, "gop_verified": false, "pixel_access": false, "limitation": "Android boot noise and inherited state changes across boots remain confounders; complement does not uniquely identify which mask failed"}。后续按实际结果选新候选，不重复本对镜像。证据reports/enuma-native-display-code.json、q1/q2-qualification及对应result；全部原始影音本地，禁写/内存/verified/分区边界保持。


## D-227，内核启动时钟常量校准资格通过，准备S-021

2026-10-25T22:13:12+08:00。80290f4已推送S-019/020模糊结果与受控恢复。新固件ed1d894eb3b8dc611d37e3cb5e7ec21583ccede5，同INF常量1/5且cold Core可执行段不变，host Linux启动原点采集/资格及精确图已绑定。新S-021/S-022均未发出；先query1/warning1/2秒，独立恢复、文档再推送后才query2/warning5/7秒。无显示读写/新映射/verified/分区变化，原始影音仅本地。


## D-228，S-021已受控返回，准备S-022七秒常量

2026-10-25T22:16:21+08:00。80290f4已推送S-019/020模糊结果与受控恢复。新固件ed1d894eb3b8dc611d37e3cb5e7ec21583ccede5，同INF常量1/5且cold Core可执行段不变，host Linux启动原点采集/资格及精确图已绑定。S-021已单次发出、受控回Android并独立恢复核验，已consumed；S-022尚未发出。当前时钟界限：{"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "9107737f47587883261dd4e628610a32b0ce06c886dd3804452cf7fc34b44505", "origin_monotonic_lower": 177088.955, "origin_monotonic_upper": 177089.025, "uncertainty_seconds": 0.07000000000698492, "calibrated_firmware_delay": false, "origin_after_issue_lower": 12.25199999997858, "origin_after_issue_upper": 12.321999999985565}。无显示读写/新映射/verified/分区变化，原始影音仅本地。


## D-229，启动时钟常量校准通过，继续显示隔离

2026-10-25T22:19:40+08:00。80290f4已推送S-019/020模糊结果与受控恢复。新固件ed1d894eb3b8dc611d37e3cb5e7ec21583ccede5，同INF常量1/5且cold Core可执行段不变，host Linux启动原点采集/资格及精确图已绑定。S-021/S-022均受控返回且consumed；仅校准通过：{"scope": "indirect calibration of known2/7 second same-Core constants, not display/GOP evidence", "calibration_passed": true, "negative_minus_positive_origin_interval_seconds": [4.956999999994878, 5.096000000019558], "predeclared_acceptance_interval_seconds": [4, 6], "individual_uncertainty_seconds": [0.07000000000698492, 0.06900000001769513], "adb_delta": 5.343999999999998, "android_complete_delta": 4.3289999999999935, "both_new_boot_ids": true, "both_independent_recoveries": true, "old_S019_S020_reclassified": false, "limitation": "Controlled known-delay difference calibrates this host/boot-clock path only; no unique instruction-path or display proof. Hardware state can still change across boots."}。后续仍用全新资格/精确图和当前文档/即时设备相机门禁，不重试旧图。无显示读写/新映射/verified/分区变化，原始影音仅本地。


## D-230，S-023 独立显示掩码资格完成，准备单笔实测

2026-10-25T22:36:02+08:00。前里程碑c1698ec已发布校准通过，固件2bb165fa0dd882da1f79b9919435f00f3a4e36d8已推送。本候选尚未发出，源/资格/文档发布及即时身份、备份、恢复与摄像门禁后直接单笔临时boot。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-231，S-023 独立显示掩码结果与交接

2026-10-25T22:38:27+08:00。前里程碑c1698ec已发布校准通过，固件2bb165fa0dd882da1f79b9919435f00f3a4e36d8已推送。{"scope": "indirect native-mask classification using predeclared calibrated boot-origin windows", "trial": "S-023", "native_mask_field": 1, "firmware_commit": "2bb165fa0dd882da1f79b9919435f00f3a4e36d8", "image_sha256": "21f07fd2df74d0e049a1fe2a677542a49c68a5315b263de2346acf19961b8396", "fd_sha256": "1f622a9ac973aa91dba5fc78981b3037f56a365793e7143556217995aed71937", "consumed": true, "automatic_android_return": true, "observation_valid": true, "boot_returncode": 0, "evidence": "out/device-tests/20261025T223633-system-transport/result.json", "timing": {"issued_at": "2026-10-25 22:36:47", "issued_at_utc": "2026-10-25T14:36:47.948005+00:00", "boot_command_return_seconds": 2.64, "fastboot_disconnect_observed_seconds": 5.109, "fastboot_return_seconds": null, "adb_return_seconds": 36.125, "boot_complete_seconds": 49.25}, "post_boot_clock": {"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "142d41df7e0bbb961909767920fb0eda6c2d913af86757c49680c864a9e1054e", "origin_monotonic_lower": 178386.106, "origin_monotonic_upper": 178386.179, "uncertainty_seconds": 0.07300000000395812, "calibrated_firmware_delay": false, "origin_after_issue_lower": 27.45000000001164, "origin_after_issue_upper": 27.5230000000156}, "boot_clock_error": null, "decode_plan": {"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}, "result": {"conclusion": "mask-inferred", "mask": 3, "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}, "boot_id_changed": true, "recovery": {"scope": "read-only recovery reconciliation; no boot, flash or device writes", "time_zone": "Asia/Shanghai", "checks": {"device": "enuma", "boot_completed": "1", "slot": "_a", "flash_locked": "0", "root_available": true}, "partitions": [{"partition": "boot_a", "sha256": "8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959", "device_and_backup_match": true}, {"partition": "vendor_boot_a", "sha256": "3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba", "device_and_backup_match": true}], "prior_phase": "recovered-android-boot-complete", "prior_state_sha256": "e526d4ef6ed0a4cb1d4eb6acca729c5ca55f8cbe2c9fcfd7cdf90135f896c449", "failed_trial_preserved": true, "evidence": "out\\device-tests\\20261025T223815-recovery-reconciliation.json"}, "camera": {"frames": 318, "decoded_frames": 318, "video": "out/camera-capture/20261025T223630-system-transport/system-transport.avi", "sha256": "4206e57ef4bfcd91ee6e0dbf85a350f4d30a304d5f0adb65977a8b62f56b3d64", "raw_media_local_only": true, "audio_recorded": false}, "gop_verified": false, "display_maximum_reads": 26, "display_writes": 0}。按结果继续新字段隔离。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-232，S-024 独立显示掩码资格完成，准备单笔实测

2026-10-25T22:43:49+08:00。前里程碑c1698ec已发布校准通过，固件2bb165fa0dd882da1f79b9919435f00f3a4e36d8已推送。本候选尚未发出，源/资格/文档发布及即时身份、备份、恢复与摄像门禁后直接单笔临时boot。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


# D-233：S-024首次进入fastboot查询异常，已恢复，按用户新规则重新进入一次

2026-10-25T22:49:37+08:00。S-024字段4镜像尚未发出、未consumed。22:44:23首轮fastboot身份门禁拦截：最初product=enuma，current-slot返回unknown command、unlocked返回Variable Not found；随后整组查询仍失败，尽管工具退出码为0，严格正文检查正确拒绝，没有fastboot boot。相机确认FASTBOOT。

已对原选定目标执行fastboot reboot（OKAY），独立恢复核验out\device-tests\20261025T224737-recovery-reconciliation.json通过：Android完成/root/A槽/解锁、boot_a及vendor_boot_a设备与备份摘要相等；相机frame0431确认Android桌面。视频1009帧/解码1009帧仅本地。相机runner_exit=1保留首次门禁失败事实，不能改写成固件启动成功。

用户新指令：“这种情况不需要硬停 只需要重新进入一次fastboot 进入规则 继续”。因此这次预启动查询故障不是本轮停止点；当前文档推送后从已验证Android重新进入一次fastboot，继续原product/slot/unlocked完整检查，通过才执行原S-024精确镜像。不是重试已启动/consumed固件，也不放宽查询接受条件。若再次无法满足身份/恢复门禁仍不发图，按实际情况处理；真正固件75秒超时/恢复失败、观测模糊等原规则保持。

固件2bb165fa0dd882da1f79b9919435f00f3a4e36d8；S-024图a50f11765285ca1b9a7cd1ac6d41b1648767cc0c2170036a41ee8141e0e84dc4，FDe98eb9bad37f8ad59db3cb33c5d9c4276811bb7f7f17e9c2d58c5104bfbb218f，归档out/inherited-gop/qualified-native-mask-2bb165f-field4。构建/实际PE/宏/FD/完整FAT/Boot v3均已审，字段4相对S-023只有RVA14d4的结果LDR偏移改变，Core PE相同。原R-004最多26读/two100ms、无像素或MMIO写、无新地址/verified/分区变化，固定五码cold2/7/12/17/22秒及boot-origin窗口不变。

有效增量仍是S-023活动掩码3间接支持，两路在三个样本均活动，启动原点27.450..27.523秒、自动Android49.250秒，恢复核验已发布909ad77。S-024帧递增尚未观测，完整GOP/点屏仍未成功。S-019/020保持ambiguous，S-021/022仅时基校准，S-001..023已consumed。后续根据S-024实际结果继续隔离Enable/Timing/布局，跨boot不拼接同时成立证据。

资格reports/enuma-native-mask-qualification.json、代码reports/enuma-native-mask-code.json、此次门禁reports/enuma-native-mask-S-024-preflight-attempt1.json。全部原始影音仅本地out，不录音/上传。无人工待办或新增范围审批。


## D-234，S-024 独立显示掩码结果与交接

2026-10-25T22:51:41+08:00。前里程碑c1698ec已发布校准通过，固件2bb165fa0dd882da1f79b9919435f00f3a4e36d8已推送。{"scope": "indirect native-mask classification using predeclared calibrated boot-origin windows", "trial": "S-024", "native_mask_field": 4, "firmware_commit": "2bb165fa0dd882da1f79b9919435f00f3a4e36d8", "image_sha256": "a50f11765285ca1b9a7cd1ac6d41b1648767cc0c2170036a41ee8141e0e84dc4", "fd_sha256": "e98eb9bad37f8ad59db3cb33c5d9c4276811bb7f7f17e9c2d58c5104bfbb218f", "consumed": true, "automatic_android_return": true, "observation_valid": true, "boot_returncode": 0, "evidence": "out/device-tests/20261025T224953-system-transport/result.json", "timing": {"issued_at": "2026-10-25 22:50:07", "issued_at_utc": "2026-10-25T14:50:07.420013+00:00", "boot_command_return_seconds": 2.64, "fastboot_disconnect_observed_seconds": 5.109, "fastboot_return_seconds": null, "adb_return_seconds": 35.015, "boot_complete_seconds": 50.75}, "post_boot_clock": {"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "c8833a29657902075305bd846ac8d68ad778cf2610cf702957a4978934a2ac47", "origin_monotonic_lower": 179185.58599999998, "origin_monotonic_upper": 179185.67599999998, "uncertainty_seconds": 0.08999999999650754, "calibrated_firmware_delay": false, "origin_after_issue_lower": 27.46099999998114, "origin_after_issue_upper": 27.55099999997765}, "boot_clock_error": null, "decode_plan": {"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}, "result": {"conclusion": "mask-inferred", "mask": 3, "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}, "boot_id_changed": true, "recovery": {"scope": "read-only recovery reconciliation; no boot, flash or device writes", "time_zone": "Asia/Shanghai", "checks": {"device": "enuma", "boot_completed": "1", "slot": "_a", "flash_locked": "0", "root_available": true}, "partitions": [{"partition": "boot_a", "sha256": "8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959", "device_and_backup_match": true}, {"partition": "vendor_boot_a", "sha256": "3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba", "device_and_backup_match": true}], "prior_phase": "recovered-android-boot-complete", "prior_state_sha256": "9b031339a559e0f637ed106540081aab0392c728cc75a0aeb3fab6007f4ea1a3", "failed_trial_preserved": true, "evidence": "out\\device-tests\\20261025T225117-recovery-reconciliation.json"}, "camera": {"frames": 327, "decoded_frames": 327, "video": "out/camera-capture/20261025T224950-system-transport/system-transport.avi", "sha256": "d3eaf518ca335c91182b08fcb4faf394da18ffd8ef580e946f15b4310670b3a1", "raw_media_local_only": true, "audio_recorded": false}, "gop_verified": false, "display_maximum_reads": 26, "display_writes": 0}。按结果继续新字段隔离。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-235，S-025 独立显示掩码资格完成，准备单笔实测

2026-10-25T22:55:58+08:00。前里程碑c1698ec已发布校准通过，固件2bb165fa0dd882da1f79b9919435f00f3a4e36d8已推送。本候选尚未发出，源/资格/文档发布及即时身份、备份、恢复与摄像门禁后直接单笔临时boot。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-236，S-025 独立显示掩码结果与交接

2026-10-25T22:58:19+08:00。前里程碑c1698ec已发布校准通过，固件2bb165fa0dd882da1f79b9919435f00f3a4e36d8已推送。{"scope": "indirect native-mask classification using predeclared calibrated boot-origin windows", "trial": "S-025", "native_mask_field": 5, "firmware_commit": "2bb165fa0dd882da1f79b9919435f00f3a4e36d8", "image_sha256": "5f68293c3d69719cf96e14282dff55582cedc37e5131b93d6965809a583de12f", "fd_sha256": "a1d22697ea740bca80f73ddb07fe29ce1b23a0a115a7c680e03d03ef77d5f088", "consumed": true, "automatic_android_return": true, "observation_valid": true, "boot_returncode": 0, "evidence": "out/device-tests/20261025T225617-system-transport/result.json", "timing": {"issued_at": "2026-10-25 22:56:31", "issued_at_utc": "2026-10-25T14:56:31.704516+00:00", "boot_command_return_seconds": 2.64, "fastboot_disconnect_observed_seconds": 5.125, "fastboot_return_seconds": null, "adb_return_seconds": 22.219, "boot_complete_seconds": 36.25}, "post_boot_clock": {"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "0f5612b436a05c6fac878797c111f9ed61750408acf71614450e6513a80f497e", "origin_monotonic_lower": 179554.872, "origin_monotonic_upper": 179554.95200000002, "uncertainty_seconds": 0.08000000001629815, "calibrated_firmware_delay": false, "origin_after_issue_lower": 12.466000000014901, "origin_after_issue_upper": 12.5460000000312}, "boot_clock_error": null, "decode_plan": {"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}, "result": {"conclusion": "mask-inferred", "mask": 0, "warning_code": 1, "stop_additional_trials": false, "direct_register_log": false}, "boot_id_changed": true, "recovery": {"scope": "read-only recovery reconciliation; no boot, flash or device writes", "time_zone": "Asia/Shanghai", "checks": {"device": "enuma", "boot_completed": "1", "slot": "_a", "flash_locked": "0", "root_available": true}, "partitions": [{"partition": "boot_a", "sha256": "8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959", "device_and_backup_match": true}, {"partition": "vendor_boot_a", "sha256": "3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba", "device_and_backup_match": true}], "prior_phase": "recovered-android-boot-complete", "prior_state_sha256": "2098995216227b190e58f3f7862e5f1e147407f589bf19260c61e8f25e38582e", "failed_trial_preserved": true, "evidence": "out\\device-tests\\20261025T225806-recovery-reconciliation.json"}, "camera": {"frames": 257, "decoded_frames": 257, "video": "out/camera-capture/20261025T225614-system-transport/system-transport.avi", "sha256": "fed122c875b4bfa35ab7981164013720518dc85b02f561725a24c6fc4b77d7ec", "raw_media_local_only": true, "audio_recorded": false}, "gop_verified": false, "display_maximum_reads": 26, "display_writes": 0}。按结果继续新字段隔离。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-237，S-026 独立显示掩码资格完成，准备单笔实测

2026-10-25T23:09:20+08:00。前里程碑c1698ec已发布校准通过，固件9600b1900d4b175cedb4158c1b53cd6b21d3044c已推送。本候选尚未发出，源/资格/文档发布及即时身份、备份、恢复与摄像门禁后直接单笔临时boot。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-238，S-026 独立显示掩码结果与交接

2026-10-25T23:13:25+08:00。前里程碑c1698ec已发布校准通过，固件9600b1900d4b175cedb4158c1b53cd6b21d3044c已推送。{"scope": "indirect native-mask classification using predeclared calibrated boot-origin windows", "trial": "S-026", "native_mask_field": 6, "firmware_commit": "9600b1900d4b175cedb4158c1b53cd6b21d3044c", "image_sha256": "1ff66e2cb4fb8e9c820f43506d555031adf1bf332a232b574d02140cb77f6845", "fd_sha256": "ed501fd19eb65a52ec875c126b79646869fecbe6d3da25fc541cffb09c3f5601", "consumed": true, "automatic_android_return": true, "observation_valid": true, "boot_returncode": 0, "evidence": "out/device-tests/20261025T230956-system-transport/result.json", "timing": {"issued_at": "2026-10-25 23:10:10", "issued_at_utc": "2026-10-25T15:10:10.472461+00:00", "boot_command_return_seconds": 2.625, "fastboot_disconnect_observed_seconds": 5.094, "fastboot_return_seconds": null, "adb_return_seconds": 25.406, "boot_complete_seconds": 40.938}, "post_boot_clock": {"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "d3e6f3d0008db285be5bc270cbc8db71c5c23e982876402485bf074d3cdf5b24", "origin_monotonic_lower": 180378.625, "origin_monotonic_upper": 180378.70500000002, "uncertainty_seconds": 0.08000000001629815, "calibrated_firmware_delay": false, "origin_after_issue_lower": 17.437999999994645, "origin_after_issue_upper": 17.518000000010943}, "boot_clock_error": null, "decode_plan": {"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}, "result": {"conclusion": "mask-inferred", "mask": 1, "warning_code": 2, "stop_additional_trials": false, "direct_register_log": false}, "boot_id_changed": true, "recovery": {"scope": "read-only recovery reconciliation; no boot, flash or device writes", "time_zone": "Asia/Shanghai", "checks": {"device": "enuma", "boot_completed": "1", "slot": "_a", "flash_locked": "0", "root_available": true}, "partitions": [{"partition": "boot_a", "sha256": "8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959", "device_and_backup_match": true}, {"partition": "vendor_boot_a", "sha256": "3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba", "device_and_backup_match": true}], "prior_phase": "recovered-android-boot-complete", "prior_state_sha256": "1d6c31c4ca65402047b1cea68c7e9cee7209f046c16352f801ce1b70e7b999b9", "failed_trial_preserved": true, "evidence": "out\\device-tests\\20261025T231303-recovery-reconciliation.json"}, "camera": {"frames": 280, "decoded_frames": 280, "video": "out/camera-capture/20261025T230953-system-transport/system-transport.avi", "sha256": "660a01ab2432f466a317b6ac16688dd14b61928049cccfc699f5a8736272dd0b", "raw_media_local_only": true, "audio_recorded": false}, "gop_verified": false, "display_maximum_reads": 26, "display_writes": 0}。按结果继续新字段隔离。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-239，S-027 独立显示掩码资格完成，准备单笔实测

2026-10-25T23:18:01+08:00。前里程碑c1698ec已发布校准通过，固件9600b1900d4b175cedb4158c1b53cd6b21d3044c已推送。本候选尚未发出，源/资格/文档发布及即时身份、备份、恢复与摄像门禁后直接单笔临时boot。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-240，S-027 独立显示掩码结果与交接

2026-10-25T23:20:15+08:00。前里程碑c1698ec已发布校准通过，固件9600b1900d4b175cedb4158c1b53cd6b21d3044c已推送。{"scope": "indirect native-mask classification using predeclared calibrated boot-origin windows", "trial": "S-027", "native_mask_field": 2, "firmware_commit": "9600b1900d4b175cedb4158c1b53cd6b21d3044c", "image_sha256": "e07a2af1563981dfed6130d15ca568725780923e7b44d32093d8cd114425b31d", "fd_sha256": "9af2262dd5f5eaefeea53228f67f7b1ab8ae9e001c4ead109397a75a9c1f7d0e", "consumed": true, "automatic_android_return": true, "observation_valid": true, "boot_returncode": 0, "evidence": "out/device-tests/20261025T231822-system-transport/result.json", "timing": {"issued_at": "2026-10-25 23:18:36", "issued_at_utc": "2026-10-25T15:18:36.506655+00:00", "boot_command_return_seconds": 2.625, "fastboot_disconnect_observed_seconds": 5.11, "fastboot_return_seconds": null, "adb_return_seconds": 25.391, "boot_complete_seconds": 40.235}, "post_boot_clock": {"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "5df00bce8043c290b244f77dcd91fc553a2a1b9fd4bf8453f6a6bde2cf464c44", "origin_monotonic_lower": 180884.67500000002, "origin_monotonic_upper": 180884.74800000002, "uncertainty_seconds": 0.07300000000395812, "calibrated_firmware_delay": false, "origin_after_issue_lower": 17.45700000002398, "origin_after_issue_upper": 17.53000000002794}, "boot_clock_error": null, "decode_plan": {"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}, "result": {"conclusion": "mask-inferred", "mask": 1, "warning_code": 2, "stop_additional_trials": false, "direct_register_log": false}, "boot_id_changed": true, "recovery": {"scope": "read-only recovery reconciliation; no boot, flash or device writes", "time_zone": "Asia/Shanghai", "checks": {"device": "enuma", "boot_completed": "1", "slot": "_a", "flash_locked": "0", "root_available": true}, "partitions": [{"partition": "boot_a", "sha256": "8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959", "device_and_backup_match": true}, {"partition": "vendor_boot_a", "sha256": "3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba", "device_and_backup_match": true}], "prior_phase": "recovered-android-boot-complete", "prior_state_sha256": "e0a93cebba5ce840ac099784709012b3858f4bab30af7e51edcd95043d7f0339", "failed_trial_preserved": true, "evidence": "out\\device-tests\\20261025T232006-recovery-reconciliation.json"}, "camera": {"frames": 276, "decoded_frames": 276, "video": "out/camera-capture/20261025T231819-system-transport/system-transport.avi", "sha256": "701905a3c24fa059d9bc6b76af4cede59cfea53ac2bdeba026e0d031873488c5", "raw_media_local_only": true, "audio_recorded": false}, "gop_verified": false, "display_maximum_reads": 26, "display_writes": 0}。按结果继续新字段隔离。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-241，S-028 独立显示掩码资格完成，准备单笔实测

2026-10-25T23:27:01+08:00。前里程碑c1698ec已发布校准通过，固件5712c00bbd48947b8e5b1db2c610c04890511e21已推送。本候选尚未发出，源/资格/文档发布及即时身份、备份、恢复与摄像门禁后直接单笔临时boot。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-242，S-028 独立显示掩码结果与交接

2026-10-25T23:28:51+08:00。前里程碑c1698ec已发布校准通过，固件5712c00bbd48947b8e5b1db2c610c04890511e21已推送。{"scope": "indirect native-mask classification using predeclared calibrated boot-origin windows", "trial": "S-028", "native_mask_field": 7, "firmware_commit": "5712c00bbd48947b8e5b1db2c610c04890511e21", "image_sha256": "1e47f6856beaa95e74869060b9b28c067ca9ed20a8c3bad247996b973b283e31", "fd_sha256": "a3767884c3efac6621073069dc1c47275278a6596ded2f7f648998cf1041b28c", "consumed": true, "automatic_android_return": true, "observation_valid": true, "boot_returncode": 0, "evidence": "out/device-tests/20261025T232709-system-transport/result.json", "timing": {"issued_at": "2026-10-25 23:27:24", "issued_at_utc": "2026-10-25T15:27:24.143815+00:00", "boot_command_return_seconds": 2.625, "fastboot_disconnect_observed_seconds": 5.094, "fastboot_return_seconds": null, "adb_return_seconds": 30.719, "boot_complete_seconds": 43.469}, "post_boot_clock": {"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "f71c598a74b17a37582a3f3d840804b0b86f6cb78e829f970e497fc70d863501", "origin_monotonic_lower": 181417.30399999997, "origin_monotonic_upper": 181417.374, "uncertainty_seconds": 0.07000000003608875, "calibrated_firmware_delay": false, "origin_after_issue_lower": 22.44499999997788, "origin_after_issue_upper": 22.51500000001397}, "boot_clock_error": null, "decode_plan": {"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}, "result": {"conclusion": "mask-inferred", "mask": 2, "warning_code": 3, "stop_additional_trials": false, "direct_register_log": false}, "boot_id_changed": true, "recovery": {"scope": "read-only recovery reconciliation; no boot, flash or device writes", "time_zone": "Asia/Shanghai", "checks": {"device": "enuma", "boot_completed": "1", "slot": "_a", "flash_locked": "0", "root_available": true}, "partitions": [{"partition": "boot_a", "sha256": "8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959", "device_and_backup_match": true}, {"partition": "vendor_boot_a", "sha256": "3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba", "device_and_backup_match": true}], "prior_phase": "recovered-android-boot-complete", "prior_state_sha256": "b4e4222d44ff52f46454a646524239bbc8bcd2f054d47495dbce551736a5e5a1", "failed_trial_preserved": true, "evidence": "out\\device-tests\\20261025T232840-recovery-reconciliation.json"}, "camera": {"frames": 290, "decoded_frames": 290, "video": "out/camera-capture/20261025T232706-system-transport/system-transport.avi", "sha256": "66800b89ac9317e1f4a302e40eb0f78e4564f377d7ef49a27333729a4486757c", "raw_media_local_only": true, "audio_recorded": false}, "gop_verified": false, "display_maximum_reads": 26, "display_writes": 0}。按结果继续新字段隔离。资格与上机图摘要见reports/enuma-native-mask-qualification.json。原R-004最多26读/two100ms，无新写入；五码cold最大22秒，预定窗口不得后调。


## D-243，S-029 原生显示管线合并审计资格完成，准备实测

2026-10-25T23:44:25+08:00，前里程碑ad6fb8a，固件fafb8a388837d002a51e7723f643058e74180548。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和相机门禁通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-244，S-029 原生显示管线合并审计结果与交接

2026-10-25T23:47:10+08:00，前里程碑909d84b，固件fafb8a388837d002a51e7723f643058e74180548。实测结果：{"conclusion": "route-category-inferred", "category": "topology-rejected", "warning_code": 3, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-029-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-245，S-030 原生显示管线合并审计资格完成，准备实测

2026-10-25T23:55:21+08:00，前里程碑d63636b，固件876d151ad40a9abf14ff4a43a2e9bb1ffe03ef71。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和相机门禁通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-246，S-030 原生显示管线合并审计结果与交接

2026-10-25T23:57:44+08:00，前里程碑42bc0b5，固件876d151ad40a9abf14ff4a43a2e9bb1ffe03ef71。实测结果：{"conclusion": "route-category-inferred", "category": "source-staging-topology-rejected", "warning_code": 3, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-030-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-247，S-031 原生显示管线合并审计资格完成，准备实测

2026-10-26T00:09:57+08:00，前里程碑0ebb328，固件5d2d3d26c868a5753ae0c25a22b892e29dbc663f。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和相机门禁通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-248，S-031 原生显示管线合并审计结果与交接

2026-10-26T00:11:41+08:00，前里程碑f8e0ec5，固件5d2d3d26c868a5753ae0c25a22b892e29dbc663f。实测结果：{"conclusion": "route-category-inferred", "category": "border-only-normalized-two-source-route", "warning_code": 2, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-031-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-249，S-032 原生显示管线合并审计资格完成，准备实测

2026-10-26T00:20:20+08:00，前里程碑a05e337，固件c45191c00100634ba6cfa09ee06986edaafe8d53。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和相机门禁通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-250，S-032 原生显示管线合并审计结果与交接

2026-10-26T00:22:41+08:00，前里程碑3e247de，固件c45191c00100634ba6cfa09ee06986edaafe8d53。实测结果：{"conclusion": "route-category-inferred", "category": "mixer-or-layout-topology-rejected", "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-032-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-251，S-033 原生显示管线合并审计资格完成，准备实测

2026-10-26T00:31:44+08:00，前里程碑bea3a9a，固件60dd3d9da2010150a26b497ad43dbd09f704e70c。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和相机门禁通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-252，S-033 原生显示管线合并审计结果与交接

2026-10-26T00:34:13+08:00，前里程碑8cc8c0d，固件60dd3d9da2010150a26b497ad43dbd09f704e70c。实测结果：{"conclusion": "route-category-inferred", "category": "mixer-dim-or-blend-rejected", "warning_code": 2, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-033-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-253，S-034 原生显示管线合并审计资格完成，准备实测

2026-10-26T00:45:55+08:00，前里程碑8880b77，固件b915308fbaaeb1c0cce92649040bde8a2ced51e6。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和相机门禁通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


2026-10-26 00:48：S-034首次预启动五组product/current-slot/unlocked查询均未通过，镜像未发出、未consumed。选定目标fastboot reboot正常返回Android；独立身份/root/A槽/解锁和两分区/备份摘要通过，相机384帧全部可解码，末帧桌面已人工查看。D-233允许重新进入一次fastboot并完整重做门禁；不是重试已发镜像。原始影音仅本地out/camera-capture/20261026T004622-system-transport。


## D-254，S-034 原生显示管线合并审计结果与交接

2026-10-26T00:49:47+08:00，前里程碑5653979，固件b915308fbaaeb1c0cce92649040bde8a2ced51e6。实测结果：{"conclusion": "route-category-inferred", "category": "selected-blend-operation-rejected", "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-034-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-255，S-035 原生显示管线合并审计资格完成，准备实测

2026-10-26T01:04:43+08:00，前里程碑76e5eac，固件6da0a2a3f4cec385b3eec9b558a81ea9cb742685。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-256，S-035 原生显示管线合并审计结果与交接

2026-10-26T01:06:46+08:00，前里程碑ae5f67f，固件6da0a2a3f4cec385b3eec9b558a81ea9cb742685。实测结果：{"conclusion": "route-category-inferred", "category": "route-or-geometry-rejected", "warning_code": 3, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-035-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-257，S-036 原生显示管线合并审计资格完成，准备实测

2026-10-26T01:17:20+08:00，前里程碑a18bf7f，固件7ea366fb39927afbaa20735a54322e9b81b676db。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-258，S-036 原生显示管线合并审计结果与交接

2026-10-26T01:19:44+08:00，前里程碑259ce2e，固件7ea366fb39927afbaa20735a54322e9b81b676db。实测结果：{"conclusion": "route-category-inferred", "category": "stable-source-local-output-rejected", "warning_code": 3, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-036-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-259，S-037 原生显示管线合并审计资格完成，准备实测

2026-10-26T01:29:02+08:00，前里程碑ea19572，固件b37e2ccb94fa4f8ea37fbc79137121764ec9e454。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-260，S-037 原生显示管线合并审计结果与交接

2026-10-26T01:31:39+08:00，前里程碑43b3b1c，固件b37e2ccb94fa4f8ea37fbc79137121764ec9e454。实测结果：{"conclusion": "route-category-inferred", "category": "source-capture-or-layout-rejected", "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-037-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-261，S-038 原生显示管线合并审计资格完成，准备实测

2026-10-26T01:40:16+08:00，前里程碑60d6ddf，固件f0c6a5dd42c57de9e8002cc07f2001eaf48fff2d。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-262，S-038 原生显示管线合并审计结果与交接

2026-10-26T01:42:39+08:00，前里程碑b01de61，固件f0c6a5dd42c57de9e8002cc07f2001eaf48fff2d。实测结果：{"conclusion": "route-category-inferred", "category": "source-format-or-encoding-rejected", "warning_code": 3, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-038-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-263，S-039 原生显示管线合并审计资格完成，准备实测

2026-10-26T01:53:54+08:00，前里程碑5fec651，固件29992292b8f46daf40bd09c9fc1baaeb32a01219。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-264，S-039 原生显示管线合并审计结果与交接

2026-10-26T01:58:04+08:00，前里程碑6008039，固件29992292b8f46daf40bd09c9fc1baaeb32a01219。实测结果：{"conclusion": "route-category-inferred", "category": "stable-8888-logical-structure-alpha-blend-address-and-downstream-unproven", "warning_code": 5, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-039-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-265，S-040 原生显示管线合并审计资格完成，准备实测

2026-10-26T02:17:23+08:00，前里程碑d515a2a，固件d7e6969348810ef27fc51782fd2d79be70ebe2ee。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-266，S-040 原生显示管线合并审计结果与交接

2026-10-26T02:20:23+08:00，前里程碑b0b230b，固件d7e6969348810ef27fc51782fd2d79be70ebe2ee。实测结果：{"conclusion": "route-category-inferred", "category": "cpu-stage1-memory-attribute-not-write-through", "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-040-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-267，S-041 原生显示管线合并审计资格完成，准备实测

2026-10-26T02:27:37+08:00，前里程碑c95a9a3，固件beebc41d5a4c66d65469aa193239069598b3da35。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-268，S-041 原生显示管线合并审计结果与交接

2026-10-26T02:31:01+08:00，前里程碑fffe9ad，固件beebc41d5a4c66d65469aa193239069598b3da35。实测结果：{"conclusion": "route-category-inferred", "category": "first-non-wt-attribute-other-encoding", "warning_code": 5, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-041-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-269，S-042 原生显示管线合并审计资格完成，准备实测

2026-10-26T02:40:19+08:00，前里程碑6f29e50，固件44f8a66569202cb53e3a6a88b0acae9b45d917df。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-270，S-042 原生显示管线合并审计结果与交接

2026-10-26T02:43:17+08:00，前里程碑b4bc4c1，固件44f8a66569202cb53e3a6a88b0acae9b45d917df。实测结果：{"conclusion": "route-category-inferred", "category": "all-pages-stage1-rw-identity-normal-wt", "warning_code": 3, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-042-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-271，S-043 原生显示管线合并审计资格完成，准备实测

2026-10-26T03:03:27+08:00，前里程碑1871892，固件f745fb1d7997303380467731bb8d02e70970e225。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无像素/MMIO/页表写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-272，S-043 原生显示管线合并审计结果与交接

2026-10-26T03:07:25+08:00，前里程碑0a2dc4b，固件f745fb1d7997303380467731bb8d02e70970e225。实测结果：{"conclusion": "route-category-inferred", "category": "single-aligned-cpu-word-read-completed-no-data-export", "warning_code": 5, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-043-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无像素/MMIO/页表写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-273，S-044 原生显示管线合并审计资格完成，准备实测

2026-10-26T03:24:42+08:00，前里程碑3f5f00e，固件93820068e213114d6eef7bf96c7c27e8d242cac8。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无像素/MMIO/页表写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-274，S-044 原生显示管线合并审计结果与交接

2026-10-26T03:27:38+08:00，前里程碑3ecde27，固件93820068e213114d6eef7bf96c7c27e8d242cac8。实测结果：{"conclusion": "route-category-inferred", "category": "single-dsb-sy-and-aligned-cpu-read-completed-no-data-export", "warning_code": 5, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-044-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无像素/MMIO/页表写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-275，S-045 原生显示管线合并审计资格完成，准备实测

2026-10-26T03:45:41+08:00，前里程碑668aca7，固件431f0a819e6b9705aebb24e4f6dae0603a7aeaad。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无像素/MMIO/页表写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-276，S-045 原生显示管线合并审计资格完成，准备实测

2026-10-26T03:53:33+08:00，前里程碑455a3f9，固件431f0a819e6b9705aebb24e4f6dae0603a7aeaad。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和观测门禁（当前无相机）通过后直接单次临时boot。沿R-004最多330读/two100ms，五种首结果分类，无像素/MMIO/页表写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


D-276预启动补充：S-045首次发图前fastboot身份门禁拒绝，镜像未发出、未consumed，无硬件运行结果。选定目标fastboot reboot后Android完成，独立root/A槽/解锁及设备与本地备份两分区摘要通过；本轮无相机。按D-233允许重新进入一次fastboot并完整重做product/slot/unlocked门禁，不能忽略FAILED正文；若再次失败不继续重入。候选315f5daa及资格/源码不变，不是重试已发图。证据reports/enuma-native-route-S-045-preissue.json。


## D-277，S-045 原生显示管线合并审计结果与交接

2026-10-26T04:03:32+08:00，前里程碑795a008，固件431f0a819e6b9705aebb24e4f6dae0603a7aeaad。实测结果：{"conclusion": "route-category-inferred", "category": "roi-128x8-reads-and-one-dsb-completed-at-el1", "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}。自动Android返回=True，观察有效=True。本图已consumed，不重试。详见reports/enuma-native-route-S-045-result.json。有效分类不是硬停，按首个拒绝位置继续隔离或推进地址与下游证据。沿R-004最多330读/two100ms，五种首结果分类，无像素/MMIO/页表写入；源码/实际代码/资格/镜像和固定时基见reports/enuma-native-route-qualification.json。原始影音仅本地。


## D-278，R-018离线资格与相机适用范围

2026-10-26T04:30:24+08:00，前里程碑9795871，固件c9530a746dbf6efbd7b1d55c020ce63477b8c198。S-045已consumed；新像素候选743335d25d8cbd4b590acc462081fd992e5d4b32c0bcb234386033d13af08b56未执行，R-018 pending。只读前置继续无相机，ADB/fastboot和固定boot-clock判分类与恢复；真正图案/背光/画面验收才采摄像头，原始影音只留本地。主机/实际构建审查完成，零新增设备动作；不是硬件硬停。R-005 consumed不复用，新事务精确范围及A/B/C选项见docs/operations/2026-10-26-r018-bounded-pixel-transaction.md。恢复后状态和下一步已同步STATUS/HANDOFF；批准前不运行新像素候选。


## D-279，R-018用户批准与S-046上机门禁

2026-10-26T09:47:31+08:00，前里程碑3be6fbf，固件c9530a7。用户明确批准R-018并要求直接上机，实际像素用相机、原始影音仅本地、按结果继续至硬停。精确镜像743335d25d8cbd4b590acc462081fd992e5d4b32c0bcb234386033d13af08b56和既有scope记录approved，仅一次临时boot的128x8保存/复核/500ms不透明对比色/恢复读回；尚未发图。独立Android/root/A槽/解锁/分区及备份摘要通过，证据out\device-tests\20261026T094641-recovery-reconciliation.json；摄像头预检1920x1080，完整屏幕和原点已查看。当前文档提交推送且即时门通过后直接执行，不再申请本图批准。无MMIO/页表/缓存属性写、新映射、GOP发布、分区操作或verified改变。code4/超时/恢复或必需观测失败即硬停并当轮记录；已发图consumed不重试。


## D-280，S-046 CPU事务恢复完成且小白条可见

2026-10-26T09:54:54+08:00，前里程碑e17167d，固件c9530a7。S-046唯一批准R-018镜像743335d2已consumed；origin33.136..33.246秒唯一code5，Android55.875秒自动返回且独立身份/root/A槽/解锁、两分区/备份摘要通过。AVI350帧全部解码，原点白条在frame103/104/105连续出现，102前/106后消失；支持最小区域可见输出，不称UEFI文字/GOP/全屏/菜单或解除22。原始影音仅本地。证据reports/enuma-native-route-S-046-result.json、reports/enuma-s046-visible-output.json、out\device-tests\20261026T095008-recovery-reconciliation.json。无硬停，继续离线安全文字/控制台工作；不重试已发图。


## D-281，R-019固定UEFI文字候选离线资格完成

2026-10-26T10:11:25+08:00，前里程碑f823ac8，固件bb60fb0500f2565cc05cbfd0a20067cae14aecd8。在S-046白条/恢复有效结果后继续实现128x32/4倍固定UEFI文字，最多12288读/8192写/3DSB/500ms，保持两Native6复核、EL1全页WT和Frame/原R-004范围。源码已推送，完整构建、FD/Boot v3/完整FAT、实际PE字形/界限/恢复审查通过，15项native/12项历史pixel/10项FD策略及故障注入通过。镜像5e189f4ed32fa9b25a5b07bc974d950fd48929cc19818a12c7c982379ab42f60，R-019 pending，尚未执行S-047；旧R-018 consumed不复用。新高度和字形范围见docs/operations/2026-10-26-r019-bounded-uefi-text.md。当前无硬停，最近设备独立核验Android，本轮后续全为离线；原始影音仅本地。


## D-282，R-019明确批准与S-047即时门

2026-10-26T10:16:28+08:00，前里程碑96606e1，固件bb60fb0。用户明确批准R-019并要求直接上机，文字摄像头记录、原始影音仅本地，按结果继续至硬停。精确镜像5e189f4ed32fa9b25a5b07bc974d950fd48929cc19818a12c7c982379ab42f60及原TEXT_SCOPE记录approved，仅一次128x32固定UEFI/500ms/保存复核恢复事务。独立核验out\device-tests\20261026T101540-recovery-reconciliation.json通过，Android完成/root/A槽/解锁/两分区及备份摘要一致；相机1920x1080完整屏幕与原点已查看。S-047未发图，文档提交推送且即时门通过后直接执行，不再询问本图批准。code4/超时/恢复或所需观测失败即硬停，停止追加并当轮落地恢复和提交推送；不重复已发图。


## D-283，S-047固定UEFI文字可见与恢复完成

2026-10-26T10:25:23+08:00，前里程碑3a2358a，固件bb60fb0。R-019唯一批准镜像5e189f4e已由S-047执行并consumed。origin33.130..33.238秒唯一code5，Android55.625秒；独立身份/root/A槽/解锁及设备/备份摘要通过。352帧全解码；frame104/105可辨认UEFI，103前/106后消失，末帧Android。固定四字位图/小区域该次事务证据，不称全局DEBUG/Print/GOP/菜单或清除22、通用alpha/SMMU。原始影音仅本地，证据reports/enuma-native-route-S-047-result.json、reports/enuma-s047-visible-text.json、out\device-tests\20261026T101839-recovery-reconciliation.json。无硬停，继续有界真实日志/控制台离线工作；已发图不重试。


## D-284，用户主线纠偏与安全交接结束写入

2026-10-26T10:37:59+08:00，前里程碑afbfa49，固件bb60fb0。S-047固定UEFI字样正常显示后，用户明确不再继续该功能验证，转向UEFI固件开发和真实日志打印。随后用户授权安全收尾、保存证据/状态/完整交接，不开启新实验或实现，交出写入权等待唯一接续会话。最终只读核验out\device-tests\20261026T103544-recovery-reconciliation.json通过，Android完成/root/A槽/解锁/设备与本地备份摘要一致；无活动设备操作/相机/恢复/构建，无设备硬停。没有R-020候选、没有日志源码实现或新镜像；后续仅只读审查。现有S-047证据、consumed授权、未验证边界和源码入口写入STATUS/HANDOFF/交接词。收尾只提交文档与脱敏恢复报告，nuwa不动、原始影音仅本地。提交推送且确认清洁后本会话结束，不再写入。


## D-285，真实DXE状态记录离线里程碑与当前授权边界

2026-10-26T03:04:58.537652+00:00，基线fecd938，固件b2ce0befab9d7938a52b5c381bc4a9e5d93b29c0。用户委派唯一新写入会话，目标日志上屏与后续菜单，本轮先离线。新增默认关闭128条DXE RAM状态日志、完整status/GUID、快照/逐行可拒绝回放；接过滤前真实检查点，不动终端与Null SerialPort。主机和AArch64验证、完整FD真实宏/staging绑定通过。首次缺C宏构建不计资格；修复加入后断言并用volatile防LTO消除未消费日志。非PIE ASan/UBSan通过，PIE间歇SIGSEGV根因未定。无新设备命令/摄像头/镜像打包，实际模式未新鲜核验；S-001..047/R-018/R-019 consumed。屏幕sink/跨模块协议/全局DEBUG/ConOut/GOP/菜单未通过，不提升22/alpha/SMMU/verified。后续先离线完成真实快照有界回放及精确预算，再提出新批准；不把本轮一般开发授权当新硬件批准。证据reports/enuma-boot-journal-tests.json、reports/enuma-boot-journal-build.json及operations/2026-10-26-dxe-status-journal.md。本轮仅本地提交，未推送，无设备硬停。

## D-286，用户新实机授权与R-020真实状态回放资格

2026-10-26T03:33:49.136994+00:00。用户明确继续/授权本项目所需实机，且无需反复询问恢复；依据实际门禁直接推进，非豁免硬停。固件962f8208a9d2eca3bc626db67090e28519e088e6、图c75b6c863d294d7b3e2772ddb7f46a239c7915685b9c7309f11310049945d8bf、归档out/inherited-gop/qualified-dxe-log-r020-962f820。新私有只读Core journal Snapshot，取最新实际point13返回状态；原点256x96/2s/保存复核绘制验证恢复读回，73728load/49152store/3DSB，原Native6/EL1/全帧WT及660MDP保持，无新映射/MMIO/页表/分区写、GOP/verified变化。资格及实际代码审查完成，尚未执行S-048。当前恢复证据out\device-tests\20261026T111629-recovery-reconciliation.json；相机已取帧/旋转查看，仅本地。全部当前文档和源码发布及即时门后一次临时boot，code4/75秒/观测时钟恢复等失败立即停追加并落实当轮交接。旧consumed图不重试，缓存回放不称全局DEBUG/ConOut/菜单。详见operations/2026-10-26-r020-cached-dxe-log-replay.md。

## D-287，S-048恢复完成但必需日志内容判读不足，停止追加

2026-10-26T03:47:26.368711+00:00，前里程碑182b302，固件962f8208a9d2eca3bc626db67090e28519e088e6。S-048于2026-10-26T03:37:41.132213+00:00单次发图c75b6c863d294d7b3e2772ddb7f46a239c7915685b9c7309f11310049945d8bf，已consumed；自动Android57.594s，独立完成/root/A槽/解锁/两分区设备及备份摘要通过，证据out\device-tests\20261026T113926-recovery-reconciliation.json。原点34.668..34.740s唯一code5，主机时钟有效；360帧完整解码，105..114连续三行/104前115后消失、末帧Android。但status/ordinal不能独立读清，按本轮D-286/用户委派的观测失败/歧义门禁于内容审查证据2026-10-26T03:43:31.579475+00:00停止追加。不是计时代码歧义、超时或恢复失败；当前无需按键。R-020及S-001..048 consumed，不重试；硬停后仅既有媒体取证和交接，不构建/发新图。工作假设优先3x5细孔与焦点/高亮叠加，保留渲染/通道等替代及推翻条件；后续先主机可读性/离线字形评估，新候选完整资格发布与即时门后再推进。未提任何verified/GOP/DEBUG/ConOut/菜单结论。证据reports/enuma-native-route-S-048-result.json、reports/enuma-s048-visible-log.json；原始影音仅本地。

## D-288，用户提出重跑并自行拍屏；原图禁重试例外待明确

2026-10-26T04:07:32.415801+00:00。用户原文“重跑enuma 我来拍摄屏幕”。新拍摄安排是可改善D-287内容观测的新条件，尚无清晰实片，也未确认拍摄已经开始。当前AGENTS/HANDOFF明确S-001..048 consumed不重试；不能仅凭一般重跑请求推断覆盖该条。已提出精确问题：是否明确授权原图c75b6c863d294d7b3e2772ddb7f46a239c7915685b9c7309f11310049945d8bf只补拍一次，覆盖禁重试；或保留规则，先做有实质软件改进的新候选。等待答复，不启动/重包/改scope/删除消耗标记，不把当前请求当已取得例外授权。

A推荐用于用户仅补拍的目的：明确同图一次例外，完整保留S-048/R-020 consumed历史和原图字节/资格，独立记录新授权/试验身份；执行工具需显式、默认关闭且仅对该摘要/原范围生效的一次观察补拍例外，并测试错误图、范围扩大、非观测类故障及二次使用均拒绝。不能仅重命名/重打包或清除consumed文件。代价是同一有界像素事务再执行一次，仍须完整发布和即时门禁。当前工具没有该例外，仍会拒绝原图；尚未修改工具。

B：保留禁重试，做实质字形/可读性改进并重新完成源/PE/栈/预算/镜像资格。代价是更多离线时间及可能新像素范围；不能仅改编号或包头。当前未实现/构建新候选。

原图保持256x96/2s、73728读/49152写/3DSB、660MDP只读/四100ms、EL1/全帧WT，图像和写入范围不扩张；一般项目授权不豁免内存字段/verified/破坏性分区规则。新鲜只读预检out\device-tests\20261026T120445-recovery-reconciliation.json通过Android完成/root/A槽/解锁/两分区设备及本地备份摘要，未操作fastboot或临时启动。nuwa未改。

拍摄安排：用户近拍物理左上原点区域并保留屏边定位，锁焦/压低曝光以分开白字内孔，关闭录音；需读清C… O…行、S后8位和第三行8位十六进制，不能把预期值补入照片。收到拍摄就绪/开始明确确认后才启动，拍摄从启动前覆盖返回Android，原片本地不传GitHub。当前未通知可以启动拍摄，未收到就绪确认；不突然发图。75秒/恢复/时钟/观测失败继续停止追加，恢复落档。

## D-289，明确一次观察复跑授权覆盖D-288歧义

2026-10-26T04:13:39.440910+00:00，前里程碑3a1ac7b，固件962f8208a9d2eca3bc626db67090e28519e088e6。用户精确答复“明确授权原镜像仅补拍一次”，R021/S049为原图c75b6c863d294d7b3e2772ddb7f46a239c7915685b9c7309f11310049945d8bf同软件一次观察复跑，非新包；保留S048/R020 consumed和旧结果/标记摘要。新增默认关闭精确例外门禁、独立UUID/单次claim、拒绝旧S048状态冒充新启动，8项新测试/5项scope/11项保护审批通过。恢复预检out\device-tests\20261026T120445-recovery-reconciliation.json通过，未启动、未重包/构建，用户拍摄尚未确认已开始。先发布工具/全部文档，再告知准备状态并等待明确拍摄开始；其他硬停不豁免。详情R021方案及当前STATUS/HANDOFF。

## D-290，主机相机已由用户断开；首次门前退出，例外未消耗

2026-10-26T12:27:12.637384+08:00，前里程碑019e390。用户首次报告拍摄已开始后调用原准备流程，DirectShow摄像头0未打开；device_runner_started=false、boot_issued=false，未执行设备命令，原状态仍S048，R021未claim/未消耗。已立即告知暂停拍摄。随后用户明确“主机摄像头清晰度不足已断开”，因此本次按其原“我来拍摄屏幕”安排采用人手唯一画面通道，主机采USB/boot-clock/恢复日志，不尝试重连主机摄像头。

仅R021可用--human-camera-only，仍须显式同图一次例外、--human-camera-ready和独立执行ID/单次claim；普通无相机像素模式继续拒绝。11项新门禁/人手路径模拟、5项scope和11项审批回归通过，模拟检查成功后仍human_media_pending，发图前失败不会把旧S048误记新启动。代码未更改镜像/固件/写入scope，也未执行任何实际boot。

用户首次开始确认后已被通知暂停，因此准备发布后重新通知并取得当前拍摄已开始/就绪确认，再启动。准备不等于清晰实片；人手照片/视频尚未取得，完整status/ordinal未知。原图c75b6c863d294d7b3e2772ddb7f46a239c7915685b9c7309f11310049945d8bf不重包，S048/R020 consumed和原标记不变，R021仍approved待一次执行；75秒/时钟/恢复/观测门禁保持，原始媒体本地、关闭录音。

## D-291，S049恢复闭环但用户报告2秒对焦不足

2026-10-26T12:36:34.613333+08:00，前里程碑313c212，固件962f820。S049/R021于2026-10-26T04:28:25.785364+00:00一次发出，Android56.859s及独立root/A槽/解锁/设备与备份摘要通过；新原点34.701..34.758s唯一code5。旧S048消耗文件未改，R021单次claim和授权consumed。用户报告虚焦/白字粘连、2秒不足以对焦，内容仍不通过，停止原图追加并保存新请求“重跑”作为离线实质改进依据。下一方向仅2→8s，面积/读写预算不变，需新源/PE/时序/完整载荷资格及具体新授权、拍摄开始和即时门。当前未实现/构建新候选，未再发图，无恢复按键待办。证据reports/enuma-native-route-S-049-result.json及out\device-tests\20261026T123411-recovery-reconciliation.json；主机无视频，用户原片尚未取得。


## D-292：S049观测失败后的实际8秒改进及离线资格

2026-10-26T04:54:45.695706+00:00；前里程碑8aa23b5；固件8680ea79d6fd14d4526d314f430e9812955cb78a。用户2秒对焦不足是本次改变依据。见 [docs/operations/2026-10-26-r022-eight-second-log-observation.md](operations/2026-10-26-r022-eight-second-log-observation.md)；新镜像f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b，R022 pending/计划S050未执行。仅增加6秒，不改面积和I/O；机器码两指令差异、Core相同、模型/Arm/全FD/FAT/Boot v3通过。旧补拍授权不复活，当前观测硬停必须按精确新范围确认后再协调拍摄；75秒/恢复/时钟门禁与所有verified限制保持。


## D-293：实机延后，增加主机格式反读与依赖证据

2026-10-26T05:49:29.611853+00:00；前设备里程碑fafe890，固件仍8680ea7。用户要求晚间才能实机、本轮仅离线；R022 pending不自动启动。新增96组C页面/2359296像素/64bit反读与严格转录测试、6模块链接/源码顺序审计通过，固件/归档/镜像未改。当前页只能含此前已完成point13，不能归为当前provider返回；GUID/sequence未显示。详见operations/2026-10-26-offline-log-readability-and-console-readiness.md；实际值和菜单/ConOut/GOP仍未实测。


## D-294：迁移后证据绑定与离线失败回归

2026-10-26（Asia/Shanghai），接手设备仓89b609e/固件子模块8680ea7，独立固件仓74598df不混用。用户仅授权离线并禁止自动提交推送/重置清理改权限；实机暂停，R-022 pending、S-050未执行，消费与拍摄就绪门保持。新增只读审计脚本和独立out证据：118项归档/源/链接绑定、122源码锁摘要、7项负向拒绝、ASan/UBSan journal/协议/8秒故障路径/96页反读及3组转录测试通过。原资格/镜像/报告不刷新，完整FD/Arm/QEMU/实机未执行；当前固件文档脏树使构建适配器前置不满足，没有调用会修改staging的入口。完整记录见operations/2026-10-26-migrated-log-evidence-audit.md，证据out/migration-log-audit-20261026/。无新增硬件硬停，无当前恢复按键欠项；状态/交接已对齐，本轮新增未提交，未检查远端。


## D-295：真实归因日志与晚期ConOut消费者实现

2026-10-26（Asia/Shanghai），用户要求继续离线且优先代码。新增canonical GUID/sequence/phase/status日志视图、严格归因decoder及INF来源摘要、真实ConOut单行sink与Probe可选回放（默认关闭）、菜单文本依赖保护；去掉Probe的Print/DiagDraw双写、raw framebuffer cache flush及生成依赖中的直接绘字代码。run4共17项命令：ASan/UBSan故障与C→ConOut→parser、AArch64三分支对象/非法selector/依赖、旧journal/8秒事务回归通过；run2测试类型编译失败已修正且旧结果保留。未构建FD/重包/QEMU/上机，未提交推送。3份原锁定固件源码改变及3新增头不冒充8680ea7资格，旧锁/metadata不刷新；R-022原镜像/归档/报告/审批保持冻结pending，S-050未执行、消费规则不变。详见operations/2026-10-26-attributed-journal-and-console-code.md；本地证据out/journal-console-dev-20261026/。没有新硬件硬停或恢复按键欠项，实机继续暂停；全局DEBUG、GOP、实际ConOut及菜单仍分别未验收。


## D-296：同handle GOP发布、BDS借用与QEMU实际菜单链

2026-10-26（Asia/Shanghai）。用户要求继续离线且可检查实机结果时尽量一笔多推进。本轮新代码补GOP+匹配BDS路径成对发布/失败生命周期、PostGopSetup借用而不另装别名、GraphicsConsole最小尺寸预检。run8共21项命令通过：ASan/UBSan发布/借用故障、真实BDS AArch64对象、新RAM EFI实际连接AAVMF GraphicsConsole并运行固定UniXNU横竖Ui/Menu、ConOut日志、无输入超时/脚本选择/取消确认/文本回退/撤销清理；CRC绑定的截图已目视检查。17项日志/Probe/旧journal/8秒回归通过。600宽VM异常、后处理及迁移include失败保留并独立修复，不写成设备硬停。完整记录operations/2026-10-26-qemu-menu-chain-and-gop-publication.md；证据out/menu-chain-dev-20261026/。实际设备未启动，没有新完整设备FD/Boot v3资格，requirements22/alpha/SMMU/UNCACHED契约不降级；R-022/旧报告/审批冻结pending、S-050未执行。未来合并独立结果不复活consumed或替代单次放行/当前拍摄就绪。本轮没有提交推送、权限变更、旧staging修复或nuwa操作，原迁移改动保留。


## D-297：WT／不透明GOP与部署前停点

2026-10-26（Asia/Shanghai），用户要求打通实机阻塞、部署前停。实现独立WT/不透明GOP访问/发布、ARM volatile/DSB、IO/Validate首故障锁停、四类Blt与opaque clear，旧Mu入口保留且22仍拒绝；新增固定寄存器事实的保存字混合系数分析，不将数学结论当当前硬件事实。10项主机/ARM/旧Mu及131072系数验证、21项WT软件profile实际QEMU菜单链通过；初次菜单读计数断言失败保留，后用显式读回覆盖并通过。原始CRC/导出闭环，RGB输出与旧Mu一致。完整记录operations/2026-10-26-wt-opaque-gop-predeployment.md，证据out/wt-opaque-dev-20261026/。当前deployment_ready=false、无新enuma Boot v3菜单镜像；同启动blend/address/SMMU/downstream及完整新构建资格未伪造闭合。按用户要求停部署前，未上机/提交推送/改权限/清理重置/旧staging修复，R022/原报告配置/消费事实冻结保持，STATUS/HANDOFF已对齐。没有新增硬件硬停或恢复按键欠项。


## D-298：完整开发构建与 R-022 本地准备分开绑定

来源：用户要求继续推进至需要录像，保护冻结产物和迁移改动、不自动提交推送。选择独立 out 当前源码快照/明确 metadata 派生/固定嵌套依赖/官方后端，原源锁与旧 staging 不覆盖，不伪造 clean commit；完整 FD 与 Boot v3 资格不解除实机 GOP/菜单准入。下一录像候选仍为原字节 R-022。为适应 no-auto-publish，新增仅限固定 R-022 的本地脚本/文档绑定选项，替代该路径旧 clean/pushed 条件，其余授权与实机条件照旧。精确路径解析修复迁移后备份定位；新 R-022 UUID 与原子 claim 保证中断不自动重发。R-022 尚 pending，local manifest 不是授权。详见 operations/2026-10-26-development-fd-and-r022-preparation.md。


## D-299：R-022单次放行与录像前预检

依据用户“可以开始实机”及紧邻的R-022精确单次计划，记录该图approved；不重复询问已有放行，当前拍摄就绪单独等待。只读预检仅访问历史已绑定enuma，不探测其他设备；保留历史current/恢复报告字节。媒体使用用户指定Media-enuma；原字节R-022经本地清单校验后才可能一次临时启动，不部署开发stage10包。


## D-300：S-050数值可读、圆角遮挡与停止追加

本次区分可读数值和完整页面：ordinal31与status0及+确实可读，左侧C不可完整观察，因此数值验收通过、全页验收失败。status0只归属此前完成point13，不能归于当前provider或猜测驱动名。根据用户圆角遮挡反馈停止追加实机，下一方向是有依据的内缩布局离线实现；不原图重试、不清requirements22、不直接接入正式GOP/菜单。


## D-301：内缩归因真实日志新候选

2026-10-26，用户要求准备下一次并尽可能推进。已完成R023 replay2五行/320×160/(64,96)/8秒和严格GUID序号归因、失败测试、完整FD/FAT/Boot v3及实际PE审查；镜像360b5ec7eeb26f76858069fba78d3f69bbe90d40f125730dfcd324dbe69fbd8a。R023 pending/计划S051未发图；新原子claim/本地绑定，不复用R022或旧录像确认。最后设备证据S050 Android恢复，本轮纯离线；不提交推送，保留迁移/冻结产物/媒体，requirements22与GOP/DEBUG/菜单未提升。详见docs/operations/2026-10-26-r023-attributed-inset-log.md。


## D-302：R-023单次放行及当前录像就绪

2026-10-26T12:41:22.383347+00:00，用户明确“录像就绪 开始推送”，仅镜像360b5ec7eeb26f76858069fba78d3f69bbe90d40f125730dfcd324dbe69fbd8a一次S051临时boot。R023 approved，当前人工拍摄就绪；即时身份/备份/恢复/时钟门由原guarded runner核验，未发图前不称通过。不得自动重试，旧consumed不变，无Git推送/分区刷写。执行证据入口out/r023-live-20261026。


## D-303：S051已恢复，内容待用户核对

R023一次已consumed，20:41:44发图，Android65.062秒，原点40.729..40.802唯一code5；20:42:57独立恢复通过。原始照片五行在屏内；用户要求人工逐字核对，独立判读已保存且未查询GUID目录，当前全文验收pending，不追加实机、不提交推送。证据reports/enuma-native-route-S-051-result.json与out/r023-live-20261026/postcheck.json。


## D-304：S051内容交叉核对及I2C归因

用户提供五行人工转录，与此前独立保存的助手判读按字段上下文/hex大小写规范化后逐字一致：ordinal31、status0、sequence185、GUID04de8591-d2b3-4077-bbbe-b12070094eb6。绑定本镜像实际PE目录唯一I2C；仅证明此前I2C StartImage返回EFI_SUCCESS，不证明总线/外设功能。照片中五行完整避开圆角；S/5、O/0字形相同确有辨识缺陷，依靠标签位置区分，后续新候选改善，不覆盖冻结图。原S051结果报告保存当时pending事实；新证据reports/enuma-s051-visible-log.json关闭人工核对项。R023已consumed，不再启动，无新实机授权、无提交推送。


## D-305：诊断日志与菜单前控制台的新完整构建

2026-10-26，用户要求继续直到编译下一版。replay3故障优先归因/25独立字形、有界129行ConOut回放/首错锁存及DSC宏传递已实现；主机/ARM/QEMU真实菜单链和独立晚期Probe PE链接通过。完整FD 1179eb69f81f303c0fd6012b3aaa7597aed589366a4dc88462391a389f44d2b7，Boot v3 e789df474e05e4de37f329cc4a1dd623cb1975ede0ae48b134bcf866db9f2969。完整诊断FD保留EFI_UNSUPPORTED Probe安全入口，晚期代码只在独立console-link2模块中链接，不能混为实机菜单镜像。build1/2失败保留，build3成功。证据reports/enuma-diagnostic-log-development.json、out/diagnostic-log-20261026及docs/operations/2026-10-26-diagnostic-log-and-console-drain.md。R024仅离线未批准，无设备动作、提交推送或verified/requirements提升；旧冻结/消费证据及媒体未改。设备HEAD89b609e、固件基线8680ea7，实际源以新manifest为准。


## D-306：R024单次批准与录像就绪，S052尚未发图

用户明确“批准实机 录像已就绪”，仅D305镜像e789df474e05e4de37f329cc4a1dd623cb1975ede0ae48b134bcf866db9f2969一次临时boot，内缩(64,96)/320×160/8秒、replay3真实完成返回，仍不进正式GOP/ConOut/菜单。独立execution1元数据派生保持镜像原字节；execution-review和新R024一次性runner测试通过。S052未claim/未发图，立即执行门仍核对enuma身份/root/A槽/解锁/备份/时钟，异常停止追加并恢复。旧consumed保持，不提交推送；本地manifest绑定当前文档与脚本。执行证据out/r024-live-20261026；媒体目录D:/Code/PortingiOS/enuma/Media-enuma/S-052-R024。


## D-307：S052真实日志核对完成与固定人工校验流程

R024已单次消费，21:56:12发图，Android66.234秒，原点40.761..40.818唯一code5；21:58:12独立恢复通过。用户“能对上”确认助手先保存后展示的五行，随后查本镜像目录归因I2C StartImage返回EFI_SUCCESS（ordinal31/sequence185/GUID04de8591-d2b3-4077-bbbe-b12070094eb6）。新字形/完整页面本图可读，不称全部字形/8秒持续或正式GOP/ConOut/DEBUG/菜单通过；requirements22不清。证据reports/enuma-native-route-S-052-result.json、reports/enuma-s052-visible-log.json、out/r024-live-20261026。用户“以后都这样校验”：助手先独立读图落盘→展示五行→用户确认/纠正→精确镜像目录归因；不确定写?，不补猜，不再要求用户先盲抄。媒体本地、旧消费不复活，无追加启动/提交推送。

## D-308：用户要求菜单优先，直达入口与无ConOut图形菜单验证

用户明确优先最快进入真实UniXNU菜单。新增默认关闭ENUMA_DIRECT_MENU，选择真实UniXNU应用GUID，独立stage10开发构建可用--direct-menu，拒绝与旧日志实验profile混用，原诊断早停/requirements22保持。QEMU横竖实际Ui/Menu在ConOut=NULL期间绘制和模拟按键/取消/确认通过（21命令），不将其称为整个UniXNURun或物理显示/按键通过。新版本地固定16e592a已有QR AdvancedLogDxe，但当前5fdbd5d没有；QR依赖菜单/GOP及AdvancedLogger，后置而不升级框架阻塞菜单。真实UniXNURun关闭BDS watchdog，下一物理菜单候选须独立可控返回。记录docs/operations/2026-10-26-menu-first-and-qr-log.md，构建及证据out/menu-priority-20261026；无新设备动作、提交推送或冻结产物覆盖。最新完整构建状态以该目录build1/build-result.json及direct-entry.json为准。

## D-309：纠正自动返回前置要求

用户指出nuwa菜单可手动回fastboot或Android。重新核对本仓AGENTS的设备门禁与既有人工恢复规则：要求有可用恢复路径，不要求菜单固件必须自动返回。D308及对话中“必须单独实现菜单阶段自动/受控返回”作为新增软件前置的解释撤回；它是本轮过度收紧，不是原规则。菜单可沿本机已有证据支持的人工按键恢复路径，在人在场、当前条件核对及精确新候选资格满足时验证。UniXNURun关闭BDS watchdog这一源码事实仍成立，旧探针自动复位和75秒观察窗不能冒充菜单自动返回保证。无需为此另实现自动复位功能。当前实际GOP/配置发现/实体输入仍待接通，新镜像资格与单次范围/录像条件不跳过，R024消费记录不复活；未做任何新设备动作或提交推送。nuwa本次未核验，不将其行为当enuma恢复证据。

历史D308构建和报告保持原字节；其中remaining内的自动/独立返回任务由本条纠正，后续以STATUS/HANDOFF为准。

## D-310：原厂DisplayDxe支线卡点复核

用户要求检查第二条GOP路线。仅离线核对历史S005/006/007、实际源码和原始二进制，并重跑audit_display_handoff到独立out/oem-display-recheck-20261026/handoff-audit.json，退出0。原厂驱动/面板资源齐备；调用前可返回而直接PE返回/Exit汇合未观察到返回，嫌疑集中PE调用区间，具体函数/状态尚未定位。FD Reserved/FD_Reserved调度器发现来源缺口仍在，但缺scheduler有降级路径，关闭线程S002也未改善，不能判为根因。APRIORI绕过DEPEX，补未知GUID stub不是有效修复。当前128条Core日志不能显示闭源PE内部服务，且S052候选排除了原厂DisplayDxe/CPRDxe，不能作为原厂路线验收。完整分析docs/operations/2026-10-26-oem-display-route-recheck.md。无设备动作、原始资格覆盖、候选构建、提交推送或内存/verified变更。

## D-311：实现R025有界真实菜单窗口，向实机资格推进

用户要求推进到实机验证。新增独立800×600/(64,96)/8秒真实UniXNU Ui/Menu窗口，使用临时PixelBltOnly GOP、RAM渲染、物理写读回和完整保存恢复；requirements22和生产GOP拒绝条件保持。host2 46组/24通道故障检查、qemu3 19命令真实菜单运行与恢复通过。完整build1因旧PixelArmProbe未使用-Werror失败，已互斥include修复，独立ARM编译通过，build2进行中。新scope/qualifier/R025一次性guard及独立human-camera runner已实现，31项R022..025准备器测试通过。无设备动作、旧授权复用、提交推送或内存/verified变更。新窗口只验证实际菜单引擎/GOP绘图/倒计时，不声称整个UniXNURun/BDS/配置发现/实体输入。新范围最终资格后需精确本次放行及当前录像条件。入口docs/operations/2026-10-26-r025-bounded-menu-window.md和out/menu-window-20261026。

D311最终资格：build3、qualification2通过；镜像 17a18ace93a002ac394ef4727148e893d7defe420496b4d3e8df7dde115be0cd，FD 275ce57a02b7c33393eeb5d63a9c9817ec527951a3dd4f2982e311a997caf46e。最终qemu4、compiled-code-review3通过；临时GOP在卸载前先禁止写入。资格1与旧code-review结果保留。物理回调584字节相同，Core.text/.data相同；新的菜单时序不套旧日志code5窗。23:48:33独立只读设备核验通过，尚未claim/boot，当前R025单次与录像确认pending。旧冻结绑定复核通过，无提交推送。原EnumaInheritedVideoAudit顶部NO GOP注释仅适用于默认/旧profile；ENUMA_BOUNDED_MENU=1通过新helper临时发布并撤销GOP，当前实现和范围以本记录为准。



## D-312：R025本次单次批准和录像确认

用户明确“批准 录像已经就绪”。仅R025/S053镜像17a18ace93a002ac394ef4727148e893d7defe420496b4d3e8df7dde115be0cd、(64,96)800×600真实菜单窗口一次临时boot获批准，当前录像就绪。此前D311待确认已关闭；尚未发图，即时身份/备份/恢复门由runner核对。无自动重试、分区刷写或提交推送；75秒无返回停止追加并恢复。执行授权记录out/r025-live-20261027/authorization.json。


# D-313：S053菜单窗口已实测并恢复Android，画面待用户核对

2026-10-27 00:09:34，R025精确镜像17a18ace93a002ac394ef4727148e893d7defe420496b4d3e8df7dde115be0cd仅执行一次临时fastboot boot，授权已consumed。发送返回0，ADB49.812秒，Android完成64.406秒；00:11:06开始的独立复核确认enuma/root/A槽/解锁、boot_a/vendor_boot_a和本地备份一致。用户也报告回到Android。无分区刷写、追加启动、提交推送。

助手已独立查看本地视频16/21/23秒帧并保存判读：UniXNU标题、版本0.1.0、enuma - bounded GOP experiment、Return to Android和GOP window test两项清晰可见；倒计时8/3/1秒，蓝色高亮由第一项变为第二项。文字避开圆角，底部No input device提示在the后截断。此为助手画面观察，等待用户核对后关闭视觉验收，不能提前写人工核对通过。

这是实际Ui/Menu经临时PixelBltOnly GOP的800×600内缩窗口显示证据；全UniXNURun/BDS/配置发现、实体输入、正式生产GOP、QR日志仍未验收。返回码未知，不套旧R024 code5时序，不从Android恢复推断窗口逐字恢复通过。requirements22保持；旧R022/R023/R024冻结产物未改。

证据：reports/enuma-menu-window-S-053-result.json；out/r025-live-20261027/authorization.json、postcheck.json、independent-visual-read.json；原媒体在D:/Code/PortingiOS/enuma/Media-enuma/S-053-R025，仅本地保留。最终镜像仍为out/menu-window-20261026/qualification2，execution-review.json和preparation2保存发图前绑定；它们是历史资格，发图后文档变化不追写旧资格。

下一步：向用户展示已保存判读并核对；然后离线接通完整菜单启动链、持久GOP生命周期及输入依赖。R025不得重试；新镜像另行资格和实机范围评估，不把本次批准扩张到下一次。


D-314：用户“对的”确认S053菜单文字/高亮/倒计时独立判读。原始证据保留，增量确认reports/enuma-menu-window-S-053-confirmed.json。R025 consumed，Android独立核验已通过；无待恢复或待人工转录事项。继续完整应用入口离线工作，不启动设备。


D-315：完整UniXNU独立应用入口离线通过，新增EnumaMenuApplication.h子系统表/GOP绑定与清理，真实磁盘TOML/UniXNURun/exit动作在application和firmware两入口通过，9种失败场景/22条命令通过。当前尚未接入板级profile、未生成新板级镜像；ConnectAll前置及GOP生命周期仍须处理。详见docs/operations/2026-10-27-full-menu-application-entry.md和reports/enuma-menu-application-development.json。S053已人工确认，R025 consumed，无设备动作、提交推送，冻结资格文件哈希一致。


# D-316：完整UniXNU应用固件已编译，离线资格通过

用户“继续推进直至编出固件”的本轮目标已完成。新full-menu完整FD及Boot v3启动镜像已生成，未上机、未提交推送。R025/S053保持consumed；S053菜单独立判读已由用户确认，设备最后经独立核验恢复Android/root/A槽/解锁且原分区摘要一致。本轮没有设备命令。

## 当前产物

- 镜像：out/full-menu-20261027/qualification1/image.img（103817216字节）。SHA256 d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce。
- FD：out/full-menu-20261027/qualification1/SILICIUM_UEFI.fd（3MiB）。SHA256 9d513b79c98662977d77acdc5c4984bf131bc10f4fe2b0c89e21e688e5c56ca8。
- build2于2026-10-27 00:58:56编译完成，完整编译2分11秒；独立工作区快照，不是干净提交构建。
- 软件资格：out/full-menu-20261027/qualification1/qualification.json，通过，execution_ready=false。新候选范围标识R026，尚未请求/登记单次实机批准。

## 本版实际运行路径

保留原DXE stage13诊断入口，从固件卷加载真实UniXNU EFI，给子应用绑定私有GOP系统表和仅含exit动作的只读内存配置卷，实际运行完整UniXNURun/配置解析/菜单/动作返回。application host避免配置加载前无条件ConnectAll。GOP覆盖整个子应用执行期，退出后先关闭子应用与配置卷，再撤销GOP并释放内存；故障停止present、恢复窗口、卸载失败保留引用存储。

仍是(64,96)800×600/8秒有界窗口，scale1修复底部文字截断；物理读写/屏障/MDP预算不增加，requirements22/verified/内存参数不改。不是正常BDS链完成、实体按键或生产GOP准入；尚无XNU启动或QR日志。菜单返回后沿现有Core诊断复位，自动复位不作为未来菜单的额外前置要求。

## 已完成验证

本次实际UniXNU PE经qemu3端到端23条命令通过，完整真实配置/菜单/exit、模拟像素恢复、读1687441/写1207441/屏障30，CRC69F91C2A。包含只读卷读/写拒绝/EOF/seek/句柄/分配失败及9种子镜像生命周期场景；host1另46组/24通道事务故障检查通过，策略及旧R025回归23项通过。FD内30个OEM PE/DEPEX一致、宏与配置实际字节正确、完整96MiB FAT和Boot v3反解一致。

build1因本轮DSC CRLF导致旧LF补丁不匹配失败，修复为LF后独立build2成功，失败证据保留。新旧资格文件哈希复核一致；没有覆盖旧镜像/资格或媒体。

## 下一步与边界

本轮停在用户要求的编译完成点。实机之前还需针对新的完整应用路径做编译后指令/嵌套分派复核、新单次执行器和来源/文档绑定，再确认此镜像单次批准与当前录像/即时设备门禁。不得沿用R025或把本软件资格当作实机通过。不需现在按恢复键或开始录像。

详细实现、失败过程和复现入口：docs/operations/2026-10-27-full-menu-firmware.md。总报告：reports/enuma-full-menu-development.json。历史完整应用单独VM验证D315和S053确认报告保持原字节。


# D-317：R026准备完成，本次录像已开始，S054待发图

R026镜像d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce，资格10d3564a3cd5d4fce35b7b597098a0de31a546d9186d5cbe74da7d9a60d77221，冻结qualification1不改。584字节物理回调与R025一致，Core.text/.data一致，子应用加载/系统表/卸载/只读拒写/首错与清理门逐条核对，删除关键指令3种变异拒绝。嵌套应用不能冒充调度驱动的ASan/UBSan检查通过；应用类型跳过Core自动连接，application host无隐式ConnectAll。60项执行器/策略/旧准备器回归通过。

01:12:03独立只读核验enuma Android完成/root/A槽/解锁及设备与本地备份摘要通过。用户明确要求机器码复核、失败路径、单次绑定与构建同轮完成，只差录像时停；以后遵守此工作方式。用户随后“我开始录像了”，绑定当前R026一次临时启动与当前拍摄，授权记录out/r026-live-20261027/authorization.json。尚未claim或发图，将再做即时门禁，不自动重试。

范围：真实FV UniXNU EFI→只读exit配置→完整UniXNURun→800×600内缩/scale1/8秒→应用退出、窗口恢复与原诊断终止。正常BDS、实体按键、生产GOP、XNU/QR未验收，requirements22保持。旧R025/S053 consumed，画面已确认且Android已恢复。

执行绑定out/full-menu-20261027/execution-review.json；preparation1仅为空目录（首次只读验证因Windows无法读取WSL链接而退出，未发图），有效准备将写preparation2。入口scripts/run_full_menu_trial.py默认离线，显式--execute --human-camera-ready和独立UUID才启动。75秒无返回停止追加并恢复，不套旧日志code5时序。媒体D:/Code/PortingiOS/enuma/Media-enuma/S-054-R026仅本地；助手先独立保存判读再给用户核对。无提交推送、分区刷写、改槽或nuwa操作。


# D-318：S054完整应用菜单已拍到，Android恢复通过，画面待用户核对

R026/S054已单次消费。2026-10-27 01:25:32发送镜像d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce，fastboot返回0/2.641秒，ADB49.797秒，Android完成66.000秒。01:28:03独立检查enuma/root/A槽/解锁、boot_a/vendor_boot_a及本地备份摘要通过。无分区刷写、追加启动、提交推送或nuwa操作。

实际落地媒体为单张照片（不是完整视频）。助手已独立查看并保存判读：UniXNU标志/标题，版本0.1.0，config路径\EFI\UniXNU\unixnu.toml，第一项Return to firmware蓝色高亮，Booting Return to firmware in 1 s，完整No input device提示，drivers 0 loaded / 0 failed、kits 0、acpi 0。无圆角遮挡，底部提示未出现上一版截断。当前等待用户核对，不预写人工验收通过；单张照片不证明8秒持续或完整倒计时过程。

结合精确已绑定镜像，此画面对应独立UniXNU应用的真实配置/菜单路径。底部drivers计数是UniXNU配置注入驱动统计，不是全部UEFI DXE驱动数量。当前仍为DXE早期显式应用加载+有界GOP/内存配置，非正常完整BDS；实体输入、生产GOP、XNU/QR未验收。返回码未知，不套旧R024 code5窗口，不以Android返回推断窗口每字恢复通过。

用户问为何比nuwa快：当前enuma省略正常BDS/全控制器连接，未启用OEM DisplayDxe/UFSDxe，使用继承显示和私有内存配置，工作量明显不同；这是对enuma当前路径的解释，不是nuwa耗时分布已核验，也不称enuma完整固件性能领先。

用户持久要求：构建、机器码复核、失败路径和单次绑定同轮完成，只差当前录像时才停，不再把离线步骤拆成多轮停点。当前单次已结束，先完成媒体人工核对，后续新软件离线继续；不得重复R026。

证据：reports/enuma-full-menu-S-054-result.json；out/r026-live-20261027/authorization.json、postcheck.json、independent-visual-read.json。原媒体D:/Code/PortingiOS/enuma/Media-enuma/S-054-R026，仅本地。冻结qualification1、execution-review和preparation2保存当时绑定，不回写旧资格。剩余工作是正常入口/持续显示与输入依赖，下一次候选仍独立资格及单次/录像门禁。


## D-319/D-320：S054人工确认与R027独立后置菜单候选

用户“正确 继续推进”确认S054独立照片判读。已新增confirmed报告，保留原pending结果和独立判读字节。下一版R027/S055将实际驱动StartImage成功记录与菜单回调结果分离；全套离线构建/QEMU/失败路径/机器码/单次源与包绑定完成。镜像0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a。STATUS/HANDOFF及2026-10-27-deferred-menu-firmware.md为当前状态；不再沿用R026未确认或待发图措辞。

01:48绑定enuma未以已授权ADB在线，仅做只读检查，未追加实机动作。等待连接Android/USB授权、本次明确R027单次放行和当前录像；旧R026及此前均consumed不可复用。全DXE/BDS/实体输入/生产GOP/QR仍未验收，不把后置显式应用启动称正常BDS。用户要求离线步骤全部做到录像停点，本轮已落实；按最新指令不提交推送、不重置清理、不开第二写入者、不操作nuwa。


## D-321：用户暂停实机，原厂服务追踪离线推进

用户“暂时不能实机 继续离线推进”，撤下当前录像待办，不执行R027或其他候选。R027冻结且未消费，旧准备因文档更新过期；恢复实机须重新准备和明确当前单次/录像条件。独立OEM三服务追踪、DisplayDxe私有表绑定、文本回放/严格解码已经宿主ASan/UBSan、4项Python测试及AArch64对象检查；未接入Core/profile，未执行OEM驱动，卡死时日志取证出口仍待实现。详见docs/operations/2026-10-27-oem-service-trace.md和out/oem-service-trace-20261027/check3/result.json。R022—R027冻结摘要、R027执行源码绑定保持不变；无提交推送、设备或nuwa操作。


## D-322：先确保OEM追踪记录可信

用户明确禁止把没有返回记录直接判成驱动死锁。已完成透明失败转发、嵌套配对/缺失返回/环形丢失、截断重复乱序拒绝及部分输出不推进/不重试验证；7项Python测试含320个独立模型快照，ASan/UBSan与AArch64对象检查通过。缺失返回仅称快照未观察到，不能定位为确定死锁。新证据out/oem-service-trace-20261027/trust-check2与reports/enuma-oem-trace-trust-validation.json；旧资格保留。仍暂停实机，组件未接入Core/profile，尚需可靠取证出口，无提交推送或设备操作。


## D-323：文档归档与本地提交授权（2026-10-27）

用户明确要求落地全部文档和提交，并提供分析 DisplayDxe 的接续 prompt。本轮允许本地提交，取代此前“不自动提交”的限制；不含远端推送、实机执行或旧授权复用。实机继续暂停，R027 paused-by-user/未消费，旧 preparation 已过期。

最新入口：[DisplayDxe 接续 prompt](2026-10-27-displaydxe-handoff-prompt.md)。追踪可信性证据仍为 trust-check2（7 项测试、320 个模型快照、ASan/UBSan 和 AArch64 对象检查），没有新增原厂驱动执行或固件资格。代码提交不会把历史工作区快照构建变成新提交构建。全部 out、媒体、OEM 二进制、设备标识及备份不入库；本地证据需保留。

提交顺序：实际 firmware 子模块源码及迁移说明，随后设备仓代码/文档/脱敏报告及子模块指针；独立 uefi-enuma 仅提交 AGENTS/README 迁移说明，其 Mu_Basecore 及嵌套依赖既有改动不纳入本轮。提交号由 git log 和最终回复给出，不写自引用哈希。远端未发布。


## 2026-10-27：OEM入口与返回RVA离线增量

已核对Core真实EntryPoint传入Image->Info.SystemTable及同句柄LoadedImage来源；新增精确OEM PE返回RVA校验工具，6项失败/指令测试通过，原追踪5条资格命令独立重跑通过。证据out/oem-rva-20261027-session-c999；详见docs/operations/2026-10-27-oem-rva-and-entry-binding.md。未接Core/profile、未运行OEM或新建固件候选；现有同步像素窗口不能保证OEM非返回时的恢复/所有权，取证出口仍阻塞。实机暂停、R027冻结未消费，无人工录像待办；本轮新增代码/测试/文档准备本地提交，不推送。共享工作区其余文件保持。


## 2026-10-27：OEM调用前单次取证出口离线实现

固件11c6cf1新增默认NULL观察器、单次带身份/完整性快照、持久缓存像素后端；窗口恢复未确认时非返回Stop，不转发OEM或编造状态。final1通过host sanitizer/AArch64/6删除负测、749种文本损坏拒绝和独立进程非返回后的外部文件保存；像素测试含恢复失败、异常、24种通道排列。证据out/oem-precall-20261027-c999，报告reports/enuma-oem-precall-capture-development.json，详见operations/2026-10-27-oem-precall-capture.md。板级物理/窗口所有权/终止恢复和Core精确绑定尚未接入，无新固件构建或硬件资格。R027镜像/资格/2434源绑定保持，实机暂停、无当前人工录像/按键待办。仅本地提交，不推送；设备仓提交号由git log查询。

## 2026-10-27：elish/nabu分析收敛为enuma实验patch与方案

已交付精确PE的MMU/SID参数单指令实验生成器和K81逐控制器契约导出器。check2的16项离线检查通过；独立PE摘要ed37a4e137cca2fcf4d5fa5718e18a319c2aa1b7a1cfab480693325bfbe2b5e3。保留构造器、面板/管线初始化及真实返回，无生产替换、打包或实机。详见operations/2026-10-27-enuma-display-application-plan.md和out/enuma-display-application-20261027-c999。用户报告ADB恢复未扩展为启动授权；R027冻结，不推送。源码与文档准备本地里程碑提交；OEM PE/公开二进制/生成产物仅留out，不入库。

## 2026-10-27：单worktree双profile隔离

按用户方案新建D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display（基点97ef242，detached），firmware从本地初始化11c6cf1。原主线不改。双vendor profile各102文件，仅DisplayDxe差异，8项失败验证通过；证据out/oem-profile-check2-20261027-c999/result.json。构建器尚未接线，旧设备锁8680ea79与当前固件不一致须单独审查，不绕过。未构建、部署、设备查询或推送。详见operations/2026-10-27-oem-display-worktree.md。

2026-10-27 · 隔离固件072251e将两个OEM profile接入开发快照builder；保持原发布锁和原vendor锁。8项直接helper/CLI失败检查通过，report enuma-oem-build-profile-development.json。固定依赖尚未在隔离树准备，全FD/实际FV未验；无设备/推送。原主线保持不改。


2026-10-27 · 隔离worktree完成OEM control/MMU-only两份3MiB FD，实际FV身份/32 OEM模块/39 APRIORI/K81资源及Core编译产物核对通过。14项审计负测、8项Core调用删除负测、8项profile检查与双组同源比较通过。固件修复提交322f427；设备仓上次提交c49623b，本轮提交号由git log查询。总报告reports/enuma-oem-fd-pair-development.json，操作记录operations/2026-10-27-oem-display-worktree.md。保留build-1和negative-1失败记录，最终build-2/negative-2不覆盖旧证据。R027与原vendor摘要复核一致，原主线干净；未查询/操作设备、打包Boot.img或推送。两FD仅stage10编译检查，Core追踪及板级出口待接，不等于OEM运行成功。


2026-10-27 · 隔离固件b6fe1a2接入Core/FV/重定位文本绑定及调用前板级适配器，两个trace-build-2完整FD和最终审计通过。8项stage10删除负测、6项拒绝终止删除负测、两PE sanitizer/交叉身份测试与旧出口749种拒绝回归通过。证据reports/enuma-oem-core-trace-development.json，操作记录operations/2026-10-27-oem-core-trace-firmware.md。保留失败trace-build-1；构建基点322f427+快照，不称干净提交构建。仍stage10派发前停止，板级运行资格未有；R027/原主线不改，无设备、Boot.img或推送。设备仓上次53956f4，本次提交号见git log。

2026-10-27 · 用户明确OEM运行版后部署；隔离worktree构建oem-runtime-build-20261027-1成功，FD d08f338dc49f60eb08ecd25a14c66e0f6e8fe9e5724d19f04684ca2d1fd08345。运行版加入随机会话、首调用取证拒绝终止、本CPU中断屏蔽/直接计时、异常早复位；原始OEM对照先测，不混入MMU改动。12:15/12:16只读Android/root/原槽/解锁/备份摘要核对通过，未重启或boot。最终资格与现场准备继续；旧qualification-1因构建收尾报告尚未落盘提前调用而失败，-2是初步资格，最终采用增加机器码审计的-3。不覆盖失败目录。R027/共享主线/远端保持。详见operations/2026-10-27-oem-runtime-deployment.md。

2026-10-27 · 运行版最终qualification-3通过；Boot v3 17d0169e6bd1447b358d1e91c6af9a8bf6ed368c6c44fea591fa73b970b82f08。20项运行序列删除负测、ArmCpuDxe异常序列、9项门禁/模拟传输测试和最终离线绑定通过。固件本地提交bdfe65f；父仓提交号见git log。当前只差此刻录像/人工恢复准备，未boot；状态与交接已更新，不推送。

2026-10-27 · 用户授权无实机继续内核/用户态/桌面开发。参考固定umi/sheng/fajita，在隔离树实现UFS SMMU规划/接管与只读SCSI准备；生成30组件实验内核e879b2f0、96MiB FAT 31a7defb、9382658048字节根卷组件文件fd43ee70。根卷输入/展开/回读摘要及生产manifest解析通过。未进入XNU/用户态，没有Data seed或IOKit硬件驱动链接。证据out/kernel-userland-20261027-1，详见operations/2026-10-27-kernel-userland-offline.md。OEM候选保留未消费、R027冻结；无设备/推送/内存或verified变更。

2026-10-27 · 用户要求官网作为后续开发指南。在线核对unixnu.com移植/适配/构建/启动/日志入口，新增docs/operations/official-development-guide.md并置于AGENTS前部作为持久执行规则。新方案先读对应章节、核对固定源码和本机事实；来源/集成/宿主/硬件分层记录。未改依赖、镜像、硬件或授权边界，仅本地记录。

2026-10-27 · 依用户要求将官网具体适配方法落位为规则：新增operations/official-adaptation-rules.md，覆盖八阶段的接口、实施顺序、失败清理、验证及enuma差异，并由AGENTS强制引用。规则只在隔离worktree生效，待后续整合；仅文档变更，不改变已有运行结论、冻结候选或设备授权。

2026-10-27 · 采用固定fajita Linux APFS builder和umi打包器构造仅目录的可丢弃Data，排除参考偏好文件；512MiB仅主机文件系统几何，不改内存/分区。生产RootWindowRead通过明确C ABI回调接本仓SCSI准备，IOKit完成回调在解锁后执行；真实transport仍承担DMA隔离。详情operations/2026-10-27-root-data-offline.md。

2026-10-27 · Data先完成独立易失块后端，不等待UFS持久化，也不伪造IOKit类/PMGR ABI来跨过依赖。新库复用固定SparseDisk；锁覆盖导入/读写/停止，失败清理真实分配，OS完成通知在解锁后。后续必须取得匹配编译记录、生成头与ABI再集成XNU。详见operations/2026-10-27-volatile-data-backend.md。

2026-10-27 · 依赖推进必须取得真实XNU编译输入；本地新增导出路径不冒充已有生成头，SDK单独提供。PMGR按当前段映射验证参考契约，不复制固定地址；静态通过不替代storage live元数据资格。详见operations/2026-10-27-driver-inputs-pmgr.md。

2026-10-27 · 用户允许推送，解除本轮不推送限制；仅将CI必要文件发布到独立分支。R027/OEM冻结、暂不上机不变；以同次构建内核/生成头/记录摘要绑定导入。

2026-10-27 · CI可替代本地Mac取得匹配输入，但CI绿色不足以验收。必须下载后校验manifest/内核/编译记录/所有文件；40477385983上传丢失.cache由本地拒绝，40478893674完整通过。缺席-I目录只记录，强制文件仍必需；IOKitUser同名storage头不替代内核接口。

2026-10-27 · 根据用户对主线部署优先级的调整，R027保留回归用途，下一实机优先可靠取证/OEM返回，再分开检查GOP和引导交接。progress-v2保持原OEM，不混入MMU补丁；五个有界窗口导出首服务/SID查找前后及真实Core返回。未覆盖协议方法和MMIO，不从最后可见事件推断根因；新候选只作离线资格，暂不上机。

2026-10-27：用户明确允许progress-v2上机，并确认当前在场、连续录像及人工长按恢复准备完成。仅新镜像adbb2c41216bc0c934af4046fe8c0127ce40a6c22c12bfc3f2c7880eee80679f一次临时fastboot boot；前检由绑定runner即时执行，不flash/erase/改槽，75秒无返回停止追加。R027及旧OEM冻结。


# OEM progress-v2 实测结果（2026-10-27）

一次临时启动已消费，75秒观察内未见合格fastboot返回，已停止追加启动。用户人工恢复Android后，独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a摘要均通过。当前设备恢复完成；不能原样重试本镜像。

候选SHA256：adbb2c41216bc0c934af4046fe8c0127ce40a6c22c12bfc3f2c7880eee80679f。源码设备仓61eacd1、固件3adfb77；首次连接失败的前检未启动，重新连接后仅一次实际boot。单次ledger保留consumed，R027及旧OEM候选冻结。

两张本地照片独立判读：E01/C0/Q0与S02/C0/Q1，均为返回RVA 0x3abc、session 0x1c2e8da897800e00；S02状态0（EFI_SUCCESS）。精确原厂PE在0x3ab8执行BLR x8，前序从表偏移0x40取函数，对应AllocatePool。0x3a8c前序不是调用，与照片B字形也不符。无符号，不能断言上层调用函数名称或分配用途。

主判断：首个AllocatePool已经成功返回，优先缩小S02取证清理至后续OEM执行之间的区间。S02可见发生在等待/恢复完成之前，因此清理/复位失败仍是第一组待排除项；其次是后续服务或未包装协议/MMIO执行，另有后段显示出口因路由变化被拒绝的可能。两张静态照片不能证明E03/S04/S05从未发生，不能判定SID死锁或完整驱动返回，更未验证GOP/BDS/XNU。此排序是下一步诊断优先级，不是故障概率结论。

下一软件方案：以独立有界探针观察后续选定服务调用入口/返回，并区分取证清理与OEM继续执行；不先套用MMU补丁。新镜像须重新构建/失败路径/机器码/单次绑定审核，不沿用本次ledger或在场状态。原始媒体仅本地，文字判读待用户核对。

证据：reports/enuma-oem-progress-trial-20261027.json；out/oem-progress-20261027/media-review/（转录、解码、精确PE RVA映射）；out/device-tests/oem-b78f01e4-35ff-4113-890d-251a1d51d106/（transport、超时快照、恢复核验）。媒体位于D:/Code/PortingiOS/enuma/Media-enuma/OEM-progress-v2-20261027-b78f01e4。只收到stage1.jpg和stage2.jpg，未收到连续录像。


2026-10-27代码归因更新：用户已确认E01/S02判读。宿主ASan/UBSan复现私有SystemTable配置表指针/数量陈旧缺陷；这是当前最强代码缺陷证据，尚未证实为本次根因。已核对首分配后的构造链与实际Core返回/清理指令，下一验证先隔离追踪器并覆盖call1/2及Kernel协议，暂不跳到SID/MMU补丁。详见operations/2026-10-27-oem-post-s02-analysis.md。新候选未生成，本轮无追加实机；7d74ce9文字取证已推送oem-progress-20261027。


## 2026-10-27 OEM early-v3离线交付

采用Core发布时点同步，避免仅服务返回后修复遗漏通知重入。新FD及qualification3通过，32项Python测试、真实Core生命周期测试、两处源码删除负测和23处机器指令删除/一次GUID变异拒绝。未上机；不把已复现的软件缺陷定为实机根因。来源、精确摘要、失败记录及边界见operations/2026-10-27-oem-early-v3.md和reports/enuma-oem-early-candidate.json。R027/旧候选与共享主线保持。


## early-v3 本次启动准备（2026-10-27）

用户已明确允许启动early-v3，并确认在场、连续录像及人工恢复就绪。仅镜像3d263b531074c483fb96c60954ac52d139c7342b8e7bf561d31ea64f25af1628、trial 5052a582-523a-4a70-a7fd-2af21a95d496一次临时boot；尚未发图。固件7c97dc6已推送，设备仓本次记录提交发布后进入即时身份/备份门。无flash/erase/改槽，75秒未观察到合格返回则停止追加并人工恢复。

最大可操作嫌疑：追踪环境与OEM构造早期兼容性；配置表动态一致性缺陷已复现修复，但本次根因置信度低至中等。竞争解释依次为旧第二窗清理/恢复问题、后续OEM构造/依赖执行、显示出口因路由变化被拒绝；SID/MMU尚无直接现场证据。具体代码与路径见operations/2026-10-27-oem-post-s02-analysis.md及early-v3记录。

E01/S02观察call1入口/返回；E03/S04观察Kernel LocateProtocol入口/返回；S05是真实CoreStartImage返回。若前四窗正常，降低前段构造嫌疑；缺图不能区分执行未到达与取证拒绝。新版call0不绘图，E01不能证明旧版S02清理完成；修复与观测时序同时变化，单次进展也不能单独证实配置表缺陷为旧故障根因。下一步只按现场实际图像独立判读，不补猜。

媒体目录D:/Code/PortingiOS/enuma/Media-enuma/OEM-early-v3-20261027-5052a582；原始媒体仅本地。R027/旧候选冻结，旧progress-v2已消费且恢复。此节取代此前网络失败导致的准备停点；最终发布及即时门禁仍须真实通过。



# early-v3 单次实测结束，Android已恢复（2026-10-27）

镜像3d263b531074c483fb96c60954ac52d139c7342b8e7bf561d31ea64f25af1628、trial 5052a582-523a-4a70-a7fd-2af21a95d496已执行一次并consumed。75秒未观察到合格fastboot返回，已停止追加。用户长按恢复后，独立核验Android完成/root/A槽/解锁及boot_a/vendor_boot_a摘要通过。不得原样重试；R027保持冻结。

已收到本地s1.jpg至s4.jpg；助手独立保存判读E01/C1/Q2、S02/C1/Q3/status0、E03/C3/Q6、S04/C3/Q7/status800000000000000e；前两图RVA3abc，后两图RVA616c，session b53a9560064a37d8。用户要求展示完整五行字符串，人工确认仍pending；未收到连续录像，不推断S05从未发生。

初步代码归因：Kernel LocateProtocol已返回EFI_NOT_FOUND，不是已证实的协议调用内部死锁。精确PE的616c非零分支到61ac→61c0→61f4，以Scheduler Interface HOB GUID 8ec2bd8d-56d7-49ef-8796-631778f8ebf8回退；620c读取HOB+24指针，构造器61b4仍返回0。因此不能把NOT_FOUND直接认定为致命错误。当前最大可操作调查方向是调度接口回退及后续使用，置信度有限；S04窗口清理、后续OEM执行及显示出口拒绝仍是竞争解释。先核对真实HOB产生/指针生命周期与下游调用，再设计新候选，不伪造协议成功或跳过错误。

四图支持本版已越过前两窗并到达Kernel查询返回，但S04画出不等于其等待/恢复完成，也不能从跨版本进展证明配置表修复解决旧根因。原始媒体仅本地D:/Code/PortingiOS/enuma/Media-enuma/OEM-early-v3-20261027-5052a582。证据reports/enuma-oem-early-trial-20261027.json、out/oem-early-20261027/media-review、out/device-tests/oem-5052a582-523a-4a70-a7fd-2af21a95d496。



# 当前：post-kernel-v4完整固件与离线资格完成（2026-10-27）

用户已确认early-v3四组完整字符串一致；旧单次consumed且Android恢复独立核验通过。本轮无设备命令。当前最大可操作嫌疑为Kernel查询返回后的构造未观测区间（HOB遍历、264字节代码缓存维护、guided-section注册），S04窗口清理是并列竞争解释。缺协议本身并非已证根因；详情和推翻条件见operations/2026-10-27-oem-post-kernel-v4.md。

新镜像out/oem-post-kernel-20261027/qualification1/image.img，SHA256 `233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7`；FD SHA256 `1dd0834df9348e3cb97667877cfd8ecece8d8e86024658262e18fdbbbcf8b9f3`。原厂PE、内存配置及同步修复保留。E01/S02改为call4（第五次包装服务），E03/S04改为SID，S05是真实驱动返回；最多五窗/40秒，未上机。

34项Python、check2 ASan/UBSan/真实Core/两处源码删除、binding1、全FD及Boot v3回读通过；最终机器码32处原运行时+23处同步/选择指令删除和一次GUID变异拒绝。Core同步函数及配置表函数与v3机器码完全相同；观察函数只在call选择立即数有一字节差异，另有协议GUID和session数据变化，不等于整份PE相同。

固件提交f82039e；构建是以7c97dc6为基线的工作树快照，不称提交后重编。固件两次GitHub推送分别连接重置/连接超时，未确认远端发布。不得将本轮编出固件当作实机启动授权或故障修复证明；下次仍先满足发布、精确单次、即时设备/备份和当前录像/恢复门禁。R027和已消费旧镜像冻结，媒体仅本地，共享主线只读。当前无人工待办。

以下为历史记录，以本节为当前状态。



# v4 摄像头单次启动准备（2026-10-27）

用户授权一次v4以核验新摄像头日志可读性，并确认当前在场可立即长按恢复。镜像233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7，trial f5854414-b040-49ff-9291-3007c5c3f560；尚未发图。两仓已补推固件f82039e/设备仓d5bc3d9，后文网络失败为历史状态。

相机0 DSHOW持续采集1920×1080至out/oem-post-kernel-20261027/camera-live1（本地MJPG视频、带UTC状态与每秒截图，无音频）。初始虚焦经用户调整，时间/日期可辨，HEX细字尚待本次实际图像检验，不预写清晰或通过。电源键动作未保证入镜，不从遮挡画面推断按键，人工恢复以用户反馈加独立设备核验。默认不上传任何影音。

最大可操作嫌疑仍为Kernel返回后构造区间及旧S04清理，详见operations/2026-10-27-oem-post-kernel-v4.md。E01/S02观察call4，E03/S04观察SID，S05真实驱动返回。无图不等于死锁。即时身份/备份/恢复、精确镜像与单次门禁通过后仅临时boot一次；75秒未确认返回即停止追加并恢复。R027和旧消费镜像不动。



# 当前：v4单次已执行，自行返回Android；摄像头日志不可完整解码（2026-10-27）

用户授权摄像头测试并确认当前在场可恢复。镜像233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7、trial f5854414-b040-49ff-9291-3007c5c3f560仅boot一次，发送/启动成功，单次consumed，不重试。源码/本次准备29301e9及固件f82039e均已推送。

摄像头与ADB均观察到Android返回，用户明确未做按键恢复；独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a摘要通过。执行器只等待fastboot，误记manual-recovery-needed；原始state-before-android-reconcile.json和transport保留，追加android-return-observed.json、android-return-verification.json并纠正当前状态为已回Android、manual_recovery=false。此为观察终点缺口，不能写作设备75秒仍挂住或人工恢复，也不能由自动返回证明DisplayDxe成功。

相机0 DSHOW采集1920×1080、2135帧、约428.688秒，原始MJPG视频及每秒JPEG均在out/oem-post-kernel-20261027/camera-live1。录像包含两段五行亮字窗口，但过曝/虚焦使数字连成白块，无法可靠恢复完整stage/call/status/session；未按预期值补猜，未送入严格解码器。检查低饱和候选原视频帧后仍不满足完整字符串验收。日志内容验收未通过，用户无需盲抄此糊图；原始影音仅本地。

AVI写入标称10fps，但实际采集约5fps，播放时长不是现场耗时；时序以UTC状态、原始JPEG文件时间及主机transport为准，不用AVI时码推算真实窗口持续时间。电源键未保证入镜，未从手部画面推断操作，自动返回依据用户明确反馈与设备核验。

当前没有新根因结论。两段文字出现与自动返回不足以验证call4/SID/真实驱动返回，仍按既有HOB/缓存/注册及取证清理竞争解释分析。后续先离线修复执行器Android终点观察，校准摄像头近拍/对焦/曝光并解决真实时间戳，再安排独立新候选；不为改善拍摄原样重启已消费v4。R027及旧候选冻结，共享主线只读，当前无按键待办。

报告reports/enuma-oem-post-kernel-trial-20261027.json；设备证据out/device-tests/oem-f5854414-b040-49ff-9291-3007c5c3f560；相机判读readability.json、review-sheet、video-detail保留本地。



# 当前：v4 手机重试已消费，自动回 Android；两张日志独立解码（2026-10-27）

用户明确授权同图重试一次并确认手机录像和人工恢复就绪。准备提交8533f8b已推送后，仅执行retry 7e4ec36d-755e-440a-8f47-3c98ae38dbdc一次临时boot，镜像SHA256 233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7。旧trial及ledger保留，新retry已consumed，不追加启动。无flash/erase/改槽。

用户确认没有操作，自行返回Android；独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a原摘要通过。旧runner只等fastboot导致误报manual-recovery-needed，原状态保留，当前已纠正；不能据此报告设备挂住或人工恢复。

手机s1/s2已独立保存完整五行及SHA256，严格v4解码/session匹配通过：E01/C4/Q8/RVA3abc，S02/C4/Q9/RVA3abc/status0。完整字符串在本地phone-independent-read.json，现场一致性确认待用户回复。照片只证明call4进入且成功返回，不证明SID或CoreStartImage返回、GOP/ConOut/BDS。

结合既有精确PE路径，观测支持本次运行到达guided-section注册附近的第五次包装服务，前置HOB/cache路径不再是本次未达call4的解释；不能据此反推v3窗口清理通过。下一步重点检查call4返回后的AllocateCopyPool复制、guided-section配置表安装/同步、后续构造器至SID，以及S02窗口恢复；两张照片缺少后续阶段不能独立证明其未执行，更不能宣称确定死锁。

证据out/device-tests/oem-retry-7e4ec36d-755e-440a-8f47-3c98ae38dbdc；原始照片仅本地D:/Code/PortingiOS/enuma/Media-enuma/OEM-v4-phone-retry-20261027-7e4ec36d。R027及原候选冻结，共享主线只读。无恢复按键待办；待现场字符串核对，之后继续离线归因。报告reports/enuma-oem-v4-phone-retry-20261027.json。
用户随后确认两组完整字符串一致、现场仅此两组。独立初读保留pending快照，另存phone-human-confirmation.json闭合确认；不再待人工核对。下一步离线分析call4返回至SID的实际路径与S02窗口清理。


# 当前：registration-v5 新固件与离线资格完成（2026-10-27）

本轮离线，未查询/操作设备。v4两组完整字符串已确认，仅观察到call4成功返回；用户确认设备无按键自行回Android，恢复独立核验通过。v4原始trial及手机retry均consumed，R027和旧候选冻结，共享主线只读。

最大可操作嫌疑为call4之后的guided-section注册区间：16字节复制→0x5cc4 InstallConfigurationTable→后续构造/主入口；对该区间置信中等，对唯一故障指令置信低，S02窗口清理仍为竞争解释。具体指令、边界、推翻条件及新候选观测解释见[registration-v5分析](operations/2026-10-27-oem-registration-v5.md)。缺少SID/返回画面不证明最后可见位置死锁。

新镜像out/oem-registration-20261027/qualification2/image.img，3153920字节，SHA256 `f9bd10078db5b049e7ad0cd050300c872cdcd1d0d975b6ed3065e4b03dac650d`。完整FD：out/oem-registration-20261027/build1/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd，SHA256 `f83b1869f65377ec2b4af4bdc69f1f64f0fcf41a3a296c6ea795a76d3b7fe6d5`。

新scope oem-registration-v5，trial 4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e，尚未claim或上机。只在此scope包装原厂返回地址0x5cc8的InstallConfigurationTable，其他配置表调用原样转发、不占追踪序号。call0..4不画窗；E01/S02=call5配置安装前/真实返回，E03/S04=SID前/后，S05=真实CoreStartImage返回。原厂DisplayDxe不改，私有SystemTable同步修复保留；ROI(64,96)320×160/每窗8秒/最多五窗40秒保持。

完整FD、原厂模块审计、Boot v3打包/解包回读通过。31项WSL Python、check3 ASan/UBSan与真实Core扩容/通知及两处删除负测、binding1精确PE重定位/错PE拒绝和AArch64板级对象通过；最终机器码32处原运行路径+52处同步/选择/注册删除负测及一处GUID变异均拒绝。qualification1保留其旧分支布局检查失败，qualification2按实际新增指令审查后通过，未为满足检查重写FD。

执行器已修复只等fastboot：观察断开后也接受绑定enuma Android完成，并完整核验root/槽/解锁/双分区摘要；直接返回、错误身份、fastboot残留模拟验证均只boot一次且无分区操作。ADB终点不推断用户是否按键，人工恢复事实继续按现场反馈记录。

固件提交fd94b26；构建是以f82039e为基线的工作树快照，保留manifest，不称提交后重编。脱敏报告reports/enuma-oem-registration-candidate.json。尚未确认本轮远端发布；最后设备状态沿上一笔Android恢复核验，本轮没有重新观测。下一实测须完成当前文档发布及即时身份/备份、当次手机拍摄与人工恢复条件；本轮任务到编出新固件，不追加实机。原始媒体仅本地，无新内存base/size、verified或分区范围变更。

registration-v5最终qualification3保留qualification2历史；仅清理宿主测试尾部空行，FD/image摘要相同，31项WSL测试重验通过。主代码a68983a、固件fd94b26；固件网络推送无进展后中止，未确认发布；未上机。


## 2026-10-27 registration-v5完整文档交接

用户因会话变慢要求全部文档落地、本地提交和新prompt。本轮仅文档与只读产物核验：image/FD/qualification SHA256匹配、v5账本不存在；证据out/oem-registration-20261027/handoff-audit.json。源码fd94b26、设备仓a68983a/0dd5db3已提交；当前文档、README/索引、旧prompt替代标记、审查及人工事项和最新授权同步完成，新prompt为docs/2026-10-27-oem-registration-v5-handoff-prompt.md。未上机、未重构建、未重试消费候选、未改共享主线，远端发布仍未确认。交接提交号见后续git log与回复，不写自引用。


## 2026-10-27 21:55 接续 registration-v5：现成资格有效，发布连接失败

从设备仓9f98d3e、固件fd94b26干净状态接续，完整读取prompt及适用规则。默认离线runner通过，2446项源绑定有效；image/FD/qualification摘要与交接相同，v5账本不存在。只读核验共享树R027冻结image/qualification摘要通过。未改源码、重构建、回写历史产物或查询设备；当前设备状态未知，当前手机拍摄/人在场恢复未确认。

有界查询两个GitHub分支失败；显式固件URL向oem-progress-20261027非force补推亦因443连接失败，未向本地origin/main推送，未继续设备仓发布。网络恢复后先固件后设备仓并核验，之后重新协调当次现场条件，单次runner执行即时身份/备份/恢复门禁。当前准备条件未齐，不称设备硬停。源码/资格/试验范围不变；不复活v4或R027。证据out/oem-registration-takeover-20261027/takeover-audit.json、remote-before.json、firmware-publication.json。STATUS/HANDOFF、审查与人工事项已同步；本轮本地文档提交号见git log。


## 2026-10-27 22:01 v5本次拍照就绪与即时前检

用户“随时准备拍照 可以开始了”放行本次registration-v5精确镜像一次临时启动，沿已有在场长按恢复安排，本次就绪独立记录。网络恢复，固件fd94b26已向显式GitHub URL/oem-progress-20261027正常推送；设备仓本准备提交发布并核验远端后才发图。只读前检确认enuma/Android完成/root/A槽/解锁及原双分区和本地备份摘要通过。trial仍4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e、镜像f9bd10078db5b049e7ad0cd050300c872cdcd1d0d975b6ed3065e4b03dac650d，未claim/启动，runner仍即时复核且只boot一次。证据out/oem-registration-live-20261027/authorization.json、preflight.json、firmware-push.json。R027冻结、共享主线只读，不flash/erase/改槽；75秒无返回先恢复并记录，媒体先独立判读再人工核对。


## 2026-10-27 22:05 v5已消费，自行回Android，媒体待判读

固件fd94b26/准备c878c8d已先后发布且执行前远端精确核验；本次即时身份/备份/恢复门禁通过，只boot一次，trial 4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e consumed。fastboot调用0.394秒返回0，执行器观察Android完成；用户确认没有操作、自行返回。22:05独立enuma/完成/root/A槽/解锁及双分区与本地原备份摘要通过，无追加启动/分区操作或硬停。媒体尚未判读，安装/SID/Core返回未知，不以Android终点推断OEM/GOP成功。

用户纠正媒体位置，已在D:/Code/PortingiOS/enuma/Media-enuma/OEM-registration-v5-20261027-4549e5e6建目录；此前误建out/media为空且不使用。下一步原媒体独立判读落盘→展示全文→人工核对→精确代码归因。本次不重试，R027冻结、共享主线只读。结果reports/enuma-oem-registration-v5-trial-20261027.json，恢复/现场确认out/oem-registration-live-20261027；原runner状态不回写，human-return-confirmation独立关闭按键待办。


## 2026-10-27 v5两张照片独立判读、人工确认与归因更新

原图s1.jpg SHA256 7a33dc6c9175dc2ee125e10023b75dc5cf2551b1ef771dfe6124a25eef1cd68e，s2.jpg SHA256 1bf50fdeea1111006b82c10761c1c9bd30b5c571b58601c4f1c04500f8f58731。先独立保存完整五行，再严格解码与资格session匹配；用户确认“两组均一致”“只出现这两组”。s1为E01/C5/Qa/RVA5cc8，s2为S02/C5/Qb/RVA5cc8/status0；session d0de511b184ace49。完整转录、原图摘要、解码和独立人工确认在out/oem-registration-live-20261027/media-review，原始媒体仅在Media-enuma本次目录。

这次证明原始InstallConfigurationTable真实返回EFI_SUCCESS：精确PE 6c6351...在0x5cc0读取BootServices+192，0x5cc4 BLR x10；包装器先调用Original->InstallConfigurationTable，再把真实Status送入EnumaServiceEnd/AfterForward，无合成返回。安装前页支持前序分配及16字节复制已经走过，返回页排除“本次一直未从该安装服务返回”。不能据此验证表中全部内容或消费者后续使用正确。

新主判断是优先隔离S02返回窗口收尾/包装器退出与后续输出准入，诊断优先级置信中等，唯一根因仍低。S02在Hold/像素恢复/读回之前可见；Present返回TRUE和DAIF恢复发生在其后，失败可ResetCold并回Android。因此自行回Android不证明S02恢复成功、已回原厂0x5cc8、SID或Core返回；缺少后页也不排除后段实际执行后出口拒绝。其次检查原厂最后注册构造返回至主入口及未包装BootServices/协议调用，不把SID服务内部当已定位故障。

本轮精确PE反汇编另存新out路径。0x1470 BL 0x6ffc，0x7014尾跳0x5b64进入本注册函数；0x5cc8把x0置零，0x5ccc..5cdc恢复寄存器并RET，返回0x1474处的构造结果检查。它不是先前0x1350调用的0x5b60（该处尾跳0x5a84分配注册表）。之后才经入口后续调用走向0x1508→0x16e8；主入口在SID之前还含内存清理及0x17e0的BootServices+80间接调用，故不能把安装后至SID概括为“只剩一条SID调用”。静态路径不等于这些地址已实机执行。

下一诊断应减少/隔离返回页自身影响并保留真实服务状态与后续到达证据，或提供独立的窗口收尾/出口拒绝区分；不能再用“最后可见服务内部挂住”解释本笔。本轮未生成新候选或追加设备，v5已consumed，R027冻结；新scope/输入仍须完整构建、失败/机器码及来源资格、当次现场与恢复门禁。结果reports/enuma-oem-registration-v5-media-confirmed.json；原pending转录/runner/初次结果字节保留。


## 2026-10-27 main-entry-v6离线编译与启动链定位

按用户要求编出新镜像c372c5e89a25aabe8d025469364c7d160be7c034481f5cec5e0283cc3338036d（3153920字节），FD 37126098fc7804af36cfcafe908f17454fbc9757ded55986462461f13caf4fcc，最终qualification2 7d3575843a9904d4f8b63891aa9143f785cbe934949e1fa868918775daf2e486。固件d393211，fd94b26基线工作树快照；trial cfee120a-a6a4-4b02-bcff-21b1aa82372f未claim/上机。取消注册窗与服务返回绘制，主入口ChipInfo精确RVA3608/GUID、SID入口及真实Core返回最多三窗24秒Hold；不伪造返回或跳过原厂初始化。32+77删除/2 GUID变异负测、42 Python、ASan/UBSan真实Core负测、ARM64 ABI/绑定、完整FD及Boot header v3回读通过，2452项默认离线绑定通过。固件已正常推送指定GitHub分支，设备仓发布见publication.json。

实际代码定位至ChipInfo GetChipFamily(+48)、条件协议方法及事件注册等SID前竞争位置，优先隔离返回窗收尾/出口；不称唯一根因。缩短诊断Hold是实际代码改动，不当作实测OEM/BDS/XNU成功。共享主线只读、R027及v5冻结摘要不变，本轮无设备命令。详情docs/operations/2026-10-27-oem-main-entry-v6.md、reports/enuma-oem-main-entry-v6-candidate.json、out/oem-main-entry-20261027。当前无人工/恢复欠项，未来新试验重做现场条件。


## 2026-10-27 22:58 v6本次单次启动准备

用户最新要求“上机”，并明确本次“拍摄已就绪，在场可恢复”。本次条件独立记录，不复用v5。22:58只读即时前检通过：enuma、Android完成、root、A槽、解锁、原boot_a/vendor_boot_a与本地备份摘要一致。新v6仍未claim/发图；本准备提交发布及远端核验后，由原单次runner再次即时核验并执行一次临时boot。

仅main-entry-v6镜像c372c5e89a25aabe8d025469364c7d160be7c034481f5cec5e0283cc3338036d、trial cfee120a-a6a4-4b02-bcff-21b1aa82372f；E01主入口ChipInfo查询前、E03首次SID前、S05真实Core返回，最多三窗24秒Hold。75秒无合格返回停止追加、优先恢复并同轮记录；不flash/erase/改槽，R027及旧v5不执行。当前观察不能预写OEM/GOP/BDS成功。

本次媒体目录已提前创建D:/Code/PortingiOS/enuma/Media-enuma/OEM-main-entry-v6-20261027-cfee120a；原始媒体只留本地，助手先独立判读落盘、展示完整字符串再请用户核对。准备与前检证据out/oem-main-entry-live-20261027/authorization.json、preflight.json。发布前不发图，无自动重试。


## 2026-10-27 23:08 v6主入口E01确认，自行回Android

准备f7dc965/固件d393211发布及远端精确核验后，trial cfee120a-a6a4-4b02-bcff-21b1aa82372f仅boot一次并consumed，fastboot调用0.401秒返回0，观察到Android完成。用户确认没有操作、自行返回；23:06独立enuma/完成/root/A槽/解锁及原双分区/本地备份摘要通过，无追加启动/分区操作或硬停。

一张本地照片先独立保存完整五行和摘要，再解码及人工核对；用户确认一致且现场只有一页。E01/C6/Qc/RVA3608/session91c9b0ca3369ea72，支持原厂注册后已到主入口ChipInfo查询包装入口；不证明E01窗口恢复或原始查询执行/返回，更未证明GetChipFamily/SID/Core返回。没有S02/S04是本版设计，不可作为缺失返回。下一定位优先E01收尾/转发、ChipInfo查询与+48方法、条件协议/事件至SID及出口；唯一根因未知，不凭最后可见页判死锁。结果reports/enuma-oem-main-entry-v6-trial-20261027.json，out/oem-main-entry-live-20261027保存确认/恢复/发布证据；原图SHA256 7a8f944ea3b53063c339cc34b6cdbf67c7b1fb7a5c4a5005fe176c39106f4b8d仅本地Media-enuma本次目录。R027/旧候选冻结，v6不重试，无人工欠项。

直连GitHub失败后通过系统已有代理的单命令Git参数完成推送，不修改全局配置。有效独立初读为media-review/independent-read1.json，首次写入异常空文件保留；原runner/独立初读pending状态不回写，由新human确认闭合。

## 2026-10-28T00:04:58+08:00 far-chain-v7离线资格与镜像完成

用户要求走得更远，已实现OEM期间RAM-only、目标真实返回后继续全部DXE分派及单张末端汇总，仍保留BDS前恢复出口。固件1f05eef62b62fc6f57b805e1cb346e3643457db7，设备仓前提交cacd246；镜像c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d，资格a1cdb2c1fbb1e4c7aacd0f6862db68c45275297f643e0241d092c7a622612823。ASan/UBSan/ARM64/44 Python、30+108删除与3 GUID变异、完整FD/Boot v3回读和2456绑定通过，未claim/上机。证据out/oem-far-chain-20261027、reports/enuma-oem-far-chain-v7-candidate.json。失败输出保留，R027/旧候选冻结，共享主线只读；旧录像不复用。换行规则纳入AGENTS并加构建前只读检查。固件显式GitHub URL正常推送且远端核对；设备仓发布见device-publication.json。本轮未触碰设备。

## v7本次拍摄与单次准备

2026-10-28 00:09 v7本次单次准备：用户明确“v7开始 正在拍摄”，按已说明的本次现场/在场恢复条件和既有恢复安排，仅新v7一次临时boot。即时只读前检enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。未claim/发送；准备文档发布及远端核对后由runner重复即时门禁。精确镜像c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d，trial 61c29945-1399-49eb-8133-d11d465bb6c4。75秒无合格返回先恢复，不自动重试，不flash/erase/改槽；R027冻结，共享主线只读。证据out/oem-far-chain-live-20261028；媒体Media-enuma/OEM-far-chain-v7-20261028-61c29945本地保留。以下旧就绪状态不复用，实际执行/恢复随后更新。

## 2026-10-28 v7单次结果与无页边界

用户“v7开始 正在拍摄”后，准备提交8f31a71/固件1f05eef均远端精确核验，即时enuma身份、原备份与恢复门禁通过，仅一次临时fastboot boot。trial 61c29945-1399-49eb-8133-d11d465bb6c4已claim/consumed，不重试；镜像SHA256 c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d，qualification2原字节保持。

执行器观察到Android完成并核对原分区；用户确认“设备自行返回 从fastboot到Mi标之间都没有”，记录为自动返回、用户没有观察到日志页。00:16独立只读复核enuma、boot_completed=1、root、A槽、解锁、设备与本地boot_a/vendor_boot_a原摘要均通过。没有追加启动、分区写入、改槽或恢复欠项，没有设备硬停。

当前媒体目录D:/Code/PortingiOS/enuma/Media-enuma/OEM-far-chain-v7-20261028-61c29945为空，尚未独立逐帧核验。本次“无页”依据用户现场陈述，不能冒充助手视频判读，也不生成/解码预期S05。Android恢复仅证明恢复终点，不证明OEM/Core返回、完整DXE分派、GOP或BDS成功。

实际代码的第一排查方向是无页的提前复位/末端拒绝链（诊断优先级中等，唯一根因置信低）：异常入口直接ResetCold；追踪校验/同步失败会终止；若走到DXE末端，Owner/Core返回门不满足则不绘制而走7秒恢复，TPL、路由/CPU策略或窗口准入拒绝也可在显示前复位。其次仍有OEM协议方法/直接访问及后续DXE异常。v7删除了v6 E01窗口，所以这笔不能再归因为该窗口收尾本身，但不排除其他追踪负担或出口问题。没有汇总页无法判ChipInfo/SID死锁，也不能宣称实际走得更远。

下一步只做离线代码归因：优先区分真实Core返回门/后续分派与末端取证出口，并审查是否可在不增加早期UI停顿的前提下提供独立失败归因；需要原视频时先独立落盘逐帧检查，再展示可读全文供人工核对。新软件须新的完整资格和单次门禁，不复活v7，不以未校准USB时长推断执行阶段。BDS/生产GOP/ConOut/实体输入/XNU均未验收。

证据：reports/enuma-oem-far-chain-v7-trial-20261028.json；out/device-tests/oem-61c29945-1399-49eb-8133-d11d465bb6c4；out/oem-far-chain-live-20261028的authorization、publication-verified、preflight、postcheck、human-return-confirmation。runner原pending状态不覆盖，由新人工确认独立闭合。共享主线只读，R027和旧镜像/资格冻结；内存base/size、verified、分区与媒体本地边界保持。当前没有恢复或字符串核对欠项；源码/文档本轮结果发布以git log及result-publication.json为准。

## 2026-10-28T00:44:04.878800+08:00 v8修复追踪通知竞态并完成镜像

冻结v7 RestoreTPL嵌套通知竞态已宿主复现，不认定为实机唯一根因；v8将RAM里程碑捕获移到事件记录临界区，继续保持无前段UI及整轮DXE后一次汇总。固件49affe73f48f5b22dd1256efa25dd5576c438daa；设备仓前提交5f870f9；镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，资格b42faaa664c7613f147cf16dabec5b914550c64a013661b358039c992a66e8ff。check3/race2/binding1/path1、44 Python、30+152删除/3 GUID变异、完整FD/Boot v3回读和2459绑定通过，未claim/上机，无设备命令。证据out/oem-far-event-20261028、reports/enuma-oem-far-event-v8-candidate.json；R027/v6/v7冻结摘要不变。本轮现场就绪不复用，后续仍即时门禁。

## v8本次单次启动准备

2026-10-28 00:47 v8本次单次准备：用户明确“v8上机，正在拍摄，我在场可以恢复”，当前拍摄/在场条件独立记录，不复用v7。即时只读enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，trial a35583f7-e92d-4999-96d2-116793825026，未claim/发送。当前准备提交发布与远端核对后，由原runner重复即时门禁，仅一次临时boot；75秒无合格返回停止追加、先恢复，不flash/erase/改槽。共享主线只读、R027冻结。证据out/oem-far-event-live-20261028；媒体Media-enuma/OEM-far-event-v8-20261028-a35583f7本地保留。v8仅修复已复现的通知竞态，不预写OEM/Core/DXE/GOP/BDS成功；无页仍有异常、返回门、末端显示拒绝等竞争解释。

## 2026-10-28 v8单次结果及判断更新

用户明确“v8上机，正在拍摄，我在场可以恢复”。准备提交6c3d8de、固件49affe7发布及远端精确核验后，执行器再次通过即时enuma/Android/root/A槽/解锁与原双分区/备份门禁，仅一次临时fastboot boot。trial a35583f7-e92d-4999-96d2-116793825026已claim/consumed，不重试；镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，qualification1 b42faaa664c7613f147cf16dabec5b914550c64a013661b358039c992a66e8ff原字节保持。

执行器观察Android完成并复核分区。用户确认“设备自行返回 从fastboot到Mi标之间都没有”；独立00:51只读核验enuma、boot_completed=1、root、A槽、解锁及设备/本地boot_a/vendor_boot_a原摘要全部通过。无追加启动/分区操作/恢复欠项，没有设备硬停。当前媒体目录D:/Code/PortingiOS/enuma/Media-enuma/OEM-far-event-v8-20261028-a35583f7为空，尚未独立逐帧判读；“无页”依据用户现场陈述，不生成预期S05、不冒充独立视频结论。

v8修复了宿主已复现的RestoreTPL后环尾竞态，且实际链接/资格绑定通过，但本次仍未观察到汇总页。因此不能继续把该竞态当作无页的充分/唯一解释，也不能认定修复未执行；本机实际Core/DXE/GOP阶段仍未知。v7/v8相同外部现象不足以证明内部路径相同，Android返回只证明恢复。

下一最大可操作方向转向末端可观测性与提前复位的分离（诊断优先级中等，唯一根因置信低）：EnumaOemFarDispatchComplete在Owner或真实Core返回位不满足时直接不绘制，completion仍沿7秒恢复；OemProgressEmit拒绝非TPL_APPLICATION；OemBoardSink还要求原继承路由、1600×2560几何、Splash范围、CPU策略和窗口恢复准入，任何拒绝都可能在显示前ResetCold。OEM/后续DXE异常入口同样直接ResetCold，仍是竞争解释。优先设计独立于晚期继承显示准入的阶段/拒绝出口，保留远端路径；不再仅凭无页细化ChipInfo，不能通过放宽像素边界、伪造EFI_SUCCESS或删除全部恢复出口来制造进度。新方案须实际代码/失败路径/机器码/完整构建及新单次资格，本图不重试。

证据：reports/enuma-oem-far-event-v8-trial-20261028.json，out/device-tests/oem-a35583f7-e92d-4999-96d2-116793825026，out/oem-far-event-live-20261028（authorization、publication-verified、preflight、postcheck、human-return-confirmation）。原runner pending快照保留，由新人工确认独立闭合。生产GOP/ConOut/BDS/实体输入/XNU未验收，R027/v6/v7/v8镜像资格冻结，共享主线只读；无内存base/size、verified、flash/erase/改槽变化。媒体/out/二进制/备份/设备标识不入Git或云端。当前无恢复/字符串核对欠项，结果发布以git log及result-publication.json为准。


## 2026-10-28 v9移除晚期显示依赖并交付三份软件候选

2026-10-28当前：far-clock-v9目标及2/22秒校准镜像已完成完整build4、qualification1和离线来源校验，三trial均未claim/上机。移除诊断晚期GOP/像素出口，保留真实OEM/Core和整轮DXE路径；52项Python与最终机器码删除负测通过。实际时钟校准未完成，目标execute需新low/high报告与精确计划；v8已consumed且恢复通过，不复用旧拍摄就绪。现行STATUS/HANDOFF及operations/2026-10-28-oem-far-clock-v9.md；以下旧当前/准备文字按历史阅读。

固件edc579d，设备仓前提交e1d5e62。实际五类出口2/7/12/17/22秒、独立2/22秒对照和一小时校准计划门禁已实现；保留原厂/真实状态，先整轮DXE再终止。52项Python、ARM/ASan/UBSan、真实Core绑定与同步/竞态、99/82/90链接删除负测、三份完整FD/Boot v3和每份2470绑定通过。失败构建保留，最终build4使用49affe7工作快照，不称提交后重编。证据out/oem-far-clock-20261028；精确镜像/资格/trial见STATUS与报告。本轮零设备命令，实际校准未完成，GOP等硬件阶段未验收。


## 2026-10-28公开源码与其他设备仓核对补充

本轮只检索/静态对照，无固件修改、重编、设备命令或v9资格/镜像回写。报告reports/enuma-oem-public-research-20261028.json记录17份固定提交公开文本的URL/SHA256，原文仅留out/public-research-20261028-v9；本机原厂PE仍6c6351c3...，14处新增选定指令核对通过。

新增可操作定位：公开ChipInfoTypes把family93定义为SDA865/SM8250。本机0x3620确实比较93，后续0x3640查询Clock GUID 241afae6...，0x3668/0x3694分别调用+8 GetClockID/+16 EnableClock，字符串为gcc_disp_ahb_clk、disp_cc_mdss_rscc_ahb_clk、disp_cc_mdss_rscc_vsync_clk。此为v6最后入口页到后续HAL查询前的一段未包装方法区间，实际执行/返回未知；EnableClock返回后未检查状态，不能把前面的Locate成功当三路时钟已启用。

历史SID简称的54b6d3b4...由公开QcomPkg.dec对应为HAL IOMMU/SMMU。精确本机查询位于0x1bcdc（返回0x1bce0），随后调用协议+8获取函数表，再调表+0/+64/+16，带客户端\_SB_.MDP；旧公开表对应create/configure-bypass/attach，精确本机HAL提供者ABI/返回/资源仍须独立核对。当前Kona源码早期MDP detach不证明OEM后段不重新attach，不复制外机stream IDs或改MMU/内存字段。旧公开HAL样例先发布协议再执行可能失败的dummy初始化，说明Locate成功本身不足证明提供者完全就绪；不推断本机必同实现。

其他仓证据边界：Mu-Silicium nabu=SM8150-AC/custom-display1，pipa=SM8250-AC/custom-display0；早期LonelyFool SM8250使用PCD SimpleFb，不能当enuma原厂DisplayDxe成功样例。公开旧版高通DisplayDxe可能发布GOP但Mode=-1，后续SetMode才填framebuffer；EDK2 GraphicsConsole在DriverBinding Start中QueryMode/SetMode，不能把DXE dispatch完成等同控制台已连接。Aloha DisplayCaller/Silicium ReEnabler有真实显示电源off/stall/on路径，是协议/模式确认后的条件方案，不是当前入口故障的现成修复。ChipInfo头宏61224fbe与DEC b0760469的差异在其他实现也有记录，当前本机原厂查询/追踪已用正确b0760469，不改GUID。

判断更新：尚无唯一根因或可直接套用的enuma修复；下一重点已具体到SM8250显示前置时钟和HAL IOMMU方法链，同时保留“已走远但诊断出口拒绝”的解释。v9三图/校准门禁保持；未来新实测先当次low/high，再target，不沿用旧拍摄就绪。若取得真实Core/DXE完成的合格间接码，再独立推进GOP发布→QueryMode/SetMode→显示电源/ConOut，不把返回成功作为生产GOP验收。


## 2026-10-28 gop-mode-v10交付

2026-10-28当前：gop-mode-v10目标及2/27秒对照已完成完整build1、qualification1和离线来源核验，三trial未消费。本机Clock/HAL ABI核对后未发现可确认的接口错配，保留原始方法，新增真实Core成功及整轮DXE后原厂GOP QueryMode/SetMode/读回检查。55项Python、sanitizer/ARM及224/174/182处链接删除负测通过。v9仅离线对照、不安排上机；旧源码准入已过期但镜像/资格字节冻结。没有本轮设备动作，不沿用旧拍摄/校准。

固件2c18bc6，设备仓前提交2d57059，构建edc579d工作快照，三份qualification1。每份2475绑定、55 Python、GOP sanitizer/ARM/真实Core门、224/174/182删除负测通过；无设备动作。真实Clock/HAL接口无已确认错配，保留原始路径，运行条件满足后推进原厂模式设置；code6不等于物理显示成功。修正校准观察有效期不得续期，现为新low2/high27。旧v9原字节/未消费保留且不安排上机，当前源码准入过期。精确产物见STATUS/报告，来源out/oem-gop-mode-20261028。


2026-10-28T11:29:00.478057+08:00 · 2026-10-28 v10本次实机准备：用户明确“可以部署实机了”，并确认“正在拍摄，在场可恢复”。本轮独立记录现场条件，按low2→恢复/人工确认→high27→恢复/人工确认→精确校准→target顺序，各一次临时boot，不自动轮测。候选尚未claim；即时身份/原备份/恢复与当前文档发布门禁通过后先发low。75秒未回合格终点停止追加、优先恢复。不flash/erase/改槽，不改内存或verified；R027冻结、共享主线只读。证据out/oem-gop-mode-live-20261028；v10原有离线资格和镜像字节保持。


2026-10-28T11:34:07.288944+08:00 · v10低时长对照已消费，用户确认未按键、自行回Android且没有新画面；独立身份/完成/root/A槽/解锁及双分区和本地备份核验通过。启动时钟区间有效。当前准备同族high27一次临时boot；target仍未claim，只有高对照独立恢复/人工确认和精确校准通过后才可启动。 证据reports/enuma-oem-gop-mode-v10-live-20261028.json。
