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
