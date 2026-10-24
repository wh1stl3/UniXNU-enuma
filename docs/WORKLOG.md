# WORKLOG（只追加）

- 2026-10-22 Asia/Shanghai · 建立独立仓库纪律，用户选择 iPadOS 17.7.11 · 提交号见下一里程碑记录 · AGENTS.md、docs/DECISIONS.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑提交 ee52c26；六组件摘要、FDT/ADT 计划、Kona/NT36523 来源、9 项测试和四组 UFS 主机检查完成；修正 ipad_identity · 本里程碑提交号由 Git 日志定位 · reports/、docs/operations/2026-10-22-offline-bringup.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 b34ecba；离线接入既有 Kona/UniXNU 固件源码，新增 GENI FIFO 适配和 Kona UFS 只读时钟支持；主机 sanitizer、AArch64 对象及固件图/补丁检查通过；提出 R-001，内存字段未修改 · 本里程碑提交号由后续记录/Git 日志定位 · reports/enuma-driver-check.json、reports/firmware-overlay-check.json、docs/operations/2026-10-22-kona-platform.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 3249989；用户批准 R-001，512 MiB 请求已写入，更新精确配置保护并通过 source pins/上游 defconfig/example 检查；未生成镜像或访问设备 · 本次提交号见后续记录/Git · board.toml、reports/workspace-check.json、docs/NEED-REVIEW.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 982dcc0；将已批准预算接入 ADT JSON 计划，复用真实 DarwinBoot 解析/窗口选择函数完成主机 sanitizer 检查；最初测试夹具低估对齐余量，修正预期并新增拒绝用例后通过，未改上游 · 本次提交号见后续记录/Git · reports/darwin-adt-contract.json、docs/operations/2026-10-22-owned-memory.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑5a86159；用户放开镜像生成和可恢复推送/启动，已只读采集当前enuma并从本机XBL补齐平台表、原厂驱动及K81资源；v3打包往返测试和完整EDK构建完成，复核并修正GIC补丁根目录后重建；未启动候选 · 本次提交号见后续记录/Git · reports/enuma-platform-observations.json、enuma-firmware-build.json、enuma-fd-audit.json、enuma-boot-candidate.json、docs/operations/2026-10-22-native-platform-firmware.md。

- 2026-10-22 Asia/Shanghai · 上一里程碑 5d84d7b；用户暂时不能配合按键，保持设备状态。新增复用 DarwinBoot 的 EnumaProbe 01，完整 UEFI/81 文件/33 OEM 字节审计及 boot v3 往返通过；生成 enuma 硬件 ADT 片段与 NT36523 解码核心，27 项 Python/主机 sanitizer/4 个 AArch64 对象通过。未实机启动、未改内存字段及验证标记 · 本里程碑提交号由后续记录/Git 日志定位 · docs/operations/2026-10-22-probe-platform-touch.md、reports/。

- 2026-10-22 Asia/Shanghai · 上一里程碑 940ef77；首次 Probe 01 r2 临时启动发送/boot 命令被接受，但用户报告黑屏；按键回 fastboot 后正常重启，20:18:24 确认 Android boot_completed=1/root、槽 A 与 boot/vendor_boot 摘要不变，pstore 空。无刷写或改槽，不宣称 UEFI/GOP 通过 · 本次提交号由后续记录/Git 日志定位 · reports/enuma-probe01-device-test.json、docs/operations/2026-10-22-first-device-probe.md。

- 2026-10-22 Asia/Shanghai · 上一里程碑 aaff143；核对 BootShim ARM64 头、复制与入口契约，加入复用 Mu 的 SEC/DXE 定时复位门；六次临时启动均回 Android，已走到 CoreDispatcher 前，2/7 秒入口对照差 5.422 秒。30 项 Windows Python、共享门主机 sanitizer、QEMU 入口和完整固件/OEM 字节审计通过；WSL 整套 Python 的环境/路径错误单独记录。未改内存字段或验证标记，未刷写/改槽；核对远端和 macOS 依赖但未创建/推送/触发 CI · 本里程碑提交号由后续记录/Git 日志定位 · reports/enuma-entry-device-tests.json、docs/operations/2026-10-22-entry-checkpoints.md、2026-10-22-build-environments.md。

- 2026-10-22 Asia/Shanghai · 上一里程碑 8aa2d95；用户批准公开建仓，已创建 wh1stl3/UniXNU-enuma 并推送 main。准备手动 macOS preflight/通用 4K bootstrap，固定 Xcode/SDK/来源提交，保存独立证据；修正与未启用 UFS 冲突的 BOOT_PROGRESS 候选开关。完整 enuma 归档/预链接尚未完成 · 本次提交号见后续 Git；远端执行结果随后记录 · .github/workflows/macos-xnu.yml、scripts/ci/macos_xnu.py。

- 2026-10-22 Asia/Shanghai · 上一里程碑 2312231 已推送；macOS preflight run 39784132935 成功，回读 artifact 核对 Xcode 16.4/SDK18.5/arm64 编译；通用 4K bootstrap run 39784240390 已启动，记录时仍运行，不宣称内核通过。另解码比较两次 stage10 FD，定位 SEC 时间字符串及 PcdDxe RSDS 标识差异，保留原实测摘要边界 · 本次提交号见后续 Git · reports/enuma-macos-preflight.json、enuma-macos-bootstrap-run.json、enuma-fd-rebuild-comparison.json。

- 2026-10-22 Asia/Shanghai · 上一里程碑 93acb9e；按用户要求遍历官网144页/3836站内链接并对照144源路由，中文72页逐页审阅，记录1处锚点问题。查明文档源码较固定构建领先89提交/完整509项树差异/新增21模块gitlink，保留原pin。用缓存FDT核对35MiB splash，只列为待核查线索。回读bootstrap CI失败的最终链接证据，修正先前运行中状态。形成分阶段路线/复用矩阵/源码与示例差异清单，未操作设备或改内存/镜像/验证标记 · 本里程碑提交号见后续 Git · docs/operations/2026-10-22-official-docs-route-review.md、2026-10-22-official-site-inventory.md、reports/enuma-official-docs-audit.json。

- 2026-10-22 Asia/Shanghai · 上一里程碑c3d9e67；按用户要求接入实时UniXNU main5fdbd5d及21固定模块，保留enuma固件/平台/v3，实现受锁控制的可选显示编译期修复及CI模块获取。30项Python、主机sanitizer/四个AArch64对象、DarwinBoot新参数契约、完整固件/33OEM与v3回归通过；新候选未启动，新CI结果待运行 · 本次提交号见后续Git · docs/operations/2026-10-22-upstream-integration.md、reports/enuma-upstream-integration.json。

- 2026-10-22 Asia/Shanghai · 底座迁移83f4608已推送；新版macOS run39789234153因匿名头文件API403失败，尚未编译内核。改为固定Git树元数据、固定commit raw下载、复用原恢复器；WSL26个头文件逐blob核对通过，Windows原raw HTTPS首试SSL EOF另记。新版stage10实测已回Android，后续固件延时对照独立里程碑记录 · 本次提交号见后续Git · reports/enuma-macos-upstream-run.json、enuma-ci-header-check.json。

- 2026-10-22 Asia/Shanghai · 上一里程碑d3ce3c4已推送；macOS run39790786938成功，回读21,041,528-byte真实通用4K内核并核hash/TCR，旧legacy链接问题已消除。实机新增底座stage10回归及stage11 2/7对照，差0.005秒不支持命中调度后门；新增实际队列前/入口后诊断，首项加载前实测已回Android/root/摘要不变。一次身份查询在发boot前中止并正常恢复后重试，未放宽匹配。保留原四patch，修正重叠patch复用，31项Python/共享头sanitizer/完整固件33OEM及v3/overlay通过。未改内存或验证标记、未刷写改槽 · 本里程碑提交号见后续Git · docs/operations/2026-10-22-dispatch-checkpoints.md、reports/enuma-macos-upstream-success.json、enuma-entry-device-tests.json。

- 2026-10-22 Asia/Shanghai · 上一里程碑1ab7ee8已推送；按用户要求建立公开uefi-enuma Mu派生仓，迁移25原文件/六patch与诊断，a1215b7及CRLF基线表示修复3376c44已推送。设备firmware改固定子模块并添加官方firmware表，旧表逐项不变。真实官方backend完整构建、Mu补丁恢复、81文件/33OEM字节、boot v3和33测试通过；新候选未启动。源码CI首轮通过，当前3376c44重跑记录时排队，本地当前契约通过。补充输入缺失/暂存保护，更新五件套，无内存或验证标记变更、无USB操作 · 本里程碑提交号见后续Git · docs/operations/2026-10-22-uefi-repository.md、reports/enuma-official-firmware-integration.json、enuma-firmware-source-migration.json。

- 2026-10-22 Asia/Shanghai · 迁移里程碑51f9c0c已推送；当前固件固定3376c44的源码Actions run39796926508完成并通过，回读日志核对PASS行并保存摘要，取代上一条记录时的排队状态。仅补齐源码CI证据，无额外构建/设备动作 · 本提交号见Git · reports/enuma-uefi-source-actions.json。

- 2026-10-22 Asia/Shanghai · 上一里程碑7d6e23e已推送；沿A-002继续主线，官方stage12基线及stage13首项2/7/2秒共四次临时启动均自动恢复Android/root/分区摘要。stage13 ADB15.903/22.308/16.939秒，复测差5.369秒支持首项CoreStartImage返回，不代表返回成功/整个调度完成/GOP。两份完整固件33OEM字节、v3回读与补丁恢复通过，来源/原board表/defconfig/example复查通过；无代码变化未重跑代码单测或CI。无flash/erase/改槽，无内存或验证标记变更 · 本里程碑提交号见后续Git · reports/enuma-entry-device-tests.json、docs/operations/2026-10-22-dispatch-checkpoints.md。

- 2026-10-22 Asia/Shanghai · 上一里程碑e079f2b已推送；按用户要求连续主线，新增第2/4/8项及第8项2/7/2秒共五次临时启动，全部自动恢复Android/root/分区摘要。第8项初对照差1.091秒未认定，复测同一2秒镜像后差5.316秒支持返回后门；保留全部样本。固件源码未改，各构建33OEM字节/v3回读/补丁恢复通过。第16项构建中，无新内存/验证标记/刷写改槽，继续推进 · 本提交号见后续Git · reports/enuma-entry-device-tests.json、DXE实测。

- 2026-10-22 Asia/Shanghai · 第8项里程碑e79a675已推送；第16项首次在完整GetVar校验中止，无boot，正常恢复Android/root/摘要后才重试同一候选，ADB16.953秒/Android30.316秒，恢复核对通过。修复字段子串匹配为恰好一个完整值，拒绝重复/冲突/FAILED/非零，新增私有查询日志及失败阶段；36项Python通过。第32项继续构建，无人工待办、内存/标记/flash/erase/改槽变化 · 本提交号见后续Git · run_enuma_entry_probe.py、test_fastboot_identity.py、查询中止与DXE报告。

- 2026-10-22 Asia/Shanghai · 上一里程碑b9e0a59已推送；旧版第32项ADB32.917秒、第24项16.954秒，均恢复Android/root/摘要。固件新增独立detail补丁/头及extensions锁，原25文件/六patch保留，d6900d2已推送；主机20组真实头sanitizer、40项Python、四core重叠patch+DSC幂等、来源/旧board表/ADT契约通过。Windows无clang改用WSL实测通过。源码CI39807061433回读成功。新版第28项ADB31.877秒，不认定命中；同版第26项构建中。无内存或标记改动/flash/erase/改槽 · 本提交号见后续Git · config/uefi-source.lock.json、enuma-dispatch-details-host.json、DXE实测。

- 2026-10-23 Asia/Shanghai · 上一里程碑8dc4347已推送；之后新增11次临时启动，本次连续主线累计20次均恢复Android/root/boot与vendor_boot摘要，另一次身份预检中止单独保留。完整UFS GUID前门对照5.357秒，后门未观察；Metronome提前281179c未解决UFS。b988fa4显式UFS隔离源/默认完整配置保留，隔离调度后仍长复位，Display完整GUID前门四样本重复差5.277秒，后门未观察。两固件提交/源码CI已推送回读成功；42项Python、32/33OEM/队列引用/v3/负向缺项审计、补丁恢复通过。只读取回内核头与页元数据，证实日志候选区是Linux普通页，准备R-002精确32KiB配置提案与UART备选，未应用。无内存/标记/flash/erase/改槽，设备恢复；按用户要求在需配置确认点停 · 本提交号见后续Git · docs/operations/2026-10-23-ufs-entry-boundary.md、2026-10-23-early-log-review.md、日志内存审计与entry-device-tests。

- 2026-10-23 Asia/Shanghai · 上一里程碑73f34e5已推送；用户批准R-002，新增精确32KiB独立诊断表默认false，原内存/512MiB/example/验证标记不变。两次原厂Android v3临时启动均恢复Android/root/原分区摘要；首版未保留作为失败样本，修正入口前/运行后NOP假设，以相同名称后缀腾空间后第二版活动FDT唯一保留0x9fff7000/0x8000、8页全reserved，节点/属性值与原样本相同。45项Python、21组C sanitizer、来源/board/defconfig/example/AOSP回读通过。实际headers+原厂KO CRC/布局离线ABI探针构建通过但未加载，未读写物理日志/标记、未启用固件日志、未证明跨复位存活。按用户最新要求本轮完成验证后停止，无人工待办；未flash/erase/改槽 · 本提交号见后续Git · docs/operations/2026-10-23-log-reservation-validation.md、reports/enuma-log-reservation-device.json、enuma-log-fdt-host.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑d3d1492已推送；按用户要求仅离线对照alioth/elish完成SimpleFb审计，22个源码Git blob/SHA及本机保存输入核对，记录可复用Mu核心、三处选择/打包差异、缺失ColorDepth/真实base-stride-format、错误路径、DFPS日志尾部冲突及当前DarwinBoot仅BGRX32契约。建议未来显式SimpleFb+no-UFS只缺CPR/Display/UFS、其余30项不变，独立严格FD规则与G0–G6验收，未实现变体。仅文档/JSON校验，不重跑旧测试或CI；未改固件/board/源锁/内存/验证标记，未调用ADB/fastboot或生成镜像。五件套更新，无新增审批/人工待办，保持实机停止 · 本提交号见后续Git · docs/operations/2026-10-23-simplefb-gop-offline-audit.md、reports/enuma-simplefb-reuse-audit.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑ac627bb已推送；按主线继续离线，marker模式实际KO编译4088字节、vermagic/832字节布局/三CRC匹配，反汇编静态检查；未加载。新增实际reader源码ASan/UBSan检查8个未保留位置映射前拒绝/精确16字节读取源不变，45项Python通过。新增保存scanout审计预期exit2，六项入口证据仍缺；保留Android cont_splash提示及旧采集元数据/后来FILE标签样本差异，不推导UEFI几何。用户新增同SoC参考仓评估持久规则写入AGENTS。未操作实机、未读写物理日志/标记、未改固件/board/源锁/内存/验证标记或生成boot镜像；在实测依赖节点交接，无新审批/按键待办 · 本提交号见后续Git · docs/operations/2026-10-23-log-reader-offline-followup.md、enuma-log-reader-marker-build.json、enuma-log-reader-host.json、enuma-scanout-evidence-gap.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑217dd29已推送；按用户最新强停规则恢复主线，生成镜像无需停、有界黑屏/定时返回在可控恢复证据下允许，AGENTS已更新。实际Android/FDT/8页/原摘要预检后normal ABI与16字节reader装卸/日志通过。新增显式FDT保留成功后16字节seed封装，host边界sanitizer/21组FDT/45项Python与AOSP回读通过。seed临时启动同次marker匹配，经Bootloader临时启动原不写marker保留镜像后不匹配；两次均Android/root/原摘要正常，模块与上传清理。按R-002停止跨复位日志，不换址/扩大；无flash/erase/改槽/内存或verified变更。列出细分入口门/UART/同次输出备选及R-003，无按键待办 · 本提交号见后续Git · docs/operations/2026-10-23-runtime-abi-marker-survival.md、reports/enuma-marker-survival-device.json及ABI/reader报告。

- 2026-10-23 Asia/Shanghai · 上一里程碑f97a91c已推送；用户选择R-003推荐A，新增真实PE调用前20/直接返回21/Exit代码块后22与共享handle-GUID-ordinal桥。固件0924fbd/a927ca1已推送，首次Image.c CRLF在patch前拒绝，补LF基线后官方backend/32OEM/BootShim/v3及还原通过。35组实际头sanitizer、45项Python/重复patch、两源CI回读成功。point20 Display/no-UFS 2/7/2 ADB16.977/22.272/16.367秒，差5.295/5.905支持调用前门，全部Android/root/原摘要正常；point21构建中。无新内存/verified/flash/erase/改槽，R-002持久日志仍停，无人工待办 · 本提交号见后续Git · docs/operations/2026-10-23-direct-pe-entry-gates.md、reports/enuma-entry-device-tests.json、enuma-dispatch-details-host.json及源CI报告。

- 2026-10-23 Asia/Shanghai · 上一设备里程碑df705f6已推送；point21/22分别ADB33.063/32.894秒未观察短门。固件903ffed独立全局默认异常门2/7 ADB30.766/30.772秒，无5秒响应；同版point20正对照15.951秒。继续d3a0972只读canary配置表前缀门，2/7/2 ADB17.298/21.464/16.058秒，差4.166/5.406秒支持调用前存在，全部样本与原2秒镜像复测保留。没有完整GUID/值、包装器/构造器/驱动主体/GOP/XNU证明，不排除其他SMC/异常。全部临时启动自动Android/root/原分区摘要正常，无flash/erase/改槽/新内存/verified变化；R-002持久日志仍停，无人工待办。两新源已推送，源码CI39834543624/39882096705成功回读；47组分发/桥头与6组异常门sanitizer、45项Python/重复patch、44项源锁/workspace和每候选官方backend/core还原/32OEM/BootShim/v3通过。静态33OEM canary GUID/构造器与固定同SoC参考评估已记录 · 本提交号见后续Git · docs/operations/2026-10-23-direct-pe-entry-gates.md、reports/enuma-entry-device-tests.json、enuma-exception-gate-host.json、enuma-oem-canary-static.json、enuma-uefi-source-actions.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑11bd36f已推送。按用户要求只读核对nuwa@436c557：R-010已实测DXE分配耗尽，R-011实际SEC209.75MiB/单行表变更构建通过；新未提交恢复记录Android完成1、三分区摘要不变，但无足够的新堆运行改善结论。确认两边Mu cfb93724相同，nuwa0008在本仓私有原字节暂存严格apply --check -p2通过、未应用；复用只读解析器从enuma已测FD的实际SEC读出51MiB Heap，与本机XBL一致。将分配失败观测提升为下一轮优先项，保留Display构造器/服务定位，不改堆/内存/verified/OEM/固件源锁，不操作设备或CI、不写参考仓 · 本提交号见后续Git · docs/operations/2026-10-23-nuwa-progress-reuse-audit.md、reports/enuma-nuwa-progress-audit.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑f696da3已推送。沿用户继续指令接入固件7276dcd全局pool后备页搜索26失败/27成功门，45项源锁；17组实际pool与51组桥头sanitizer、46项Python/重复patch/CLI、workspace及源码CI39885298128通过。四候选完整backend/core还原（含Page.c）/32OEM/BootShim/v3审计通过；成功门2/7 ADB16.108/21.478秒，差5.370支持hook执行；失败门2/7 ADB31.129/32.248秒未观察预期延时响应。全部自动Android/root/原摘要恢复，不把负向门当零失败或容量证据，未改51MiB/512MiB/内存/verified/OEM或flash/erase/槽。用户追加同设备方案借鉴，正在离线准备alioth/elish式SimpleFb诊断，尚未启用或实测 · 本提交号见后续Git · docs/operations/2026-10-23-pool-search-gates.md、reports/enuma-pool-gate-host.json、reports/enuma-entry-device-tests.json及源码CI。

- 2026-10-23 Asia/Shanghai · 上一里程碑e4a40fb已推送。按用户要求借鉴alioth/elish独立SimpleFb路线，233a9d8接通DSC/FDF/APRIORI与严格30-OEM诊断，原生默认不变，补查找/模式/mask/分配/配置/安装/清理/64位溢出，Blt禁像素。整驱动host检查、实际AArch64/core还原/30OEM/BootShim/v3与源码CI39888162938通过。10:16:30入口前2秒候选92b11e7d…接受后75秒未回目标端点，后续只读检查仍无，用户暂不能按键；已硬停，Android/root/试后摘要未确认，不称GOP或XNU成功。实际序号32未在新布局校准，静态APR位33不替代运行计数。仅离线继续7479da1补Probe直接绘制入口守卫、上一试验未恢复时拒绝新命令、私有SimpleFb只构建；48项Python/整驱动sanitizer/Probe守卫宏0/1/组合patch/49源锁与源码CI39889743071通过，新守卫未生成固件或实测。无flash/erase/改槽/内存/verified/OEM改动，R-002仍停，H-001待实体恢复 · 本提交号见后续Git · docs/operations/2026-10-23-simplefb-metadata-variant.md、reports/enuma-simplefb-bringup.json、enuma-simplefb-contract-host.json、enuma-entry-device-tests.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑e197e02已推送。用户确认按键恢复；12:11:03核对Android完成1/root/槽_a/BL解锁/原boot及vendor_boot摘要通过，清除私有manual-recovery-needed门但不改写233首测未自动返回。7479da1早期队列对照实际构建打包未启动；用户随后要求离线推进，零新设备试验。固件6bc5b81增加完整GUID-only及默认关闭的正常分派完成7秒兜底，后者不覆盖卡死、非异步看门狗；147组真实头sanitizer、三组完成门/非法组合、50项Python、重复patch/50源锁和AArch64/backend还原通过，FD 8f2c6f8a00a311ee63b1c9ca16db7b1b4d5bd501819193aa6875edb7be051ff7。30 OEM/BootShim/v3审计通过、源码CI39911281252回读PASS；不改内存/verified/OEM，不重启R-002；后续实机先早期对照再GUID-only时序，参考仓只读 · 本提交号见后续Git · docs/operations/2026-10-23-guid-only-dispatch-offline.md、reports/enuma-simplefb-recovery.json、enuma-dispatch-selection-offline.json、enuma-dispatch-details-host.json及当前构建/FD/BootShim/v3报告。

- 2026-10-23 Asia/Shanghai · 上一设备里程碑00505f8已推送。沿离线范围用固定Mu真实configure前缀复现两项基线断言：静态配置大小跨失败残留、跨度超过描述符仍被接受。82ce8a5修复，真实库+完整SimpleFb+BootVideo三组合及原整驱动sanitizer/组合patch、50项Python/50源锁通过；build/workspace qualification曾并发瞬时失败，构建后串行重查通过，后续明确串行。实际AutoGen两构造器/Null串口已审计；AArch64/core还原/30OEM/BootShim/v3通过，FD 75c34141a785d4dc38f1475e6ce1a60b894f30db98c18b58926958c6e2bd203f，源码CI39912601757回读PASS，全部候选归档未启动。零设备查询/写入，不改内存/verified/OEM或重启R-002；未证明GOP/XNU或首测黑屏根因。用户问进入内核时间，已说明还需实机GOP→内存/loader/EBS→入口，不能承诺轮数 · 本提交号见后续Git · docs/operations/2026-10-23-simplefb-loader-handoff.md、reports/enuma-simplefb-loader-bringup.json、enuma-simplefb-handoff-regressions.json、enuma-simplefb-handoff-host.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑6b8545b已推送。用户要求晚上一起实测，离线在同82ce8a5源新构建早期加载前2秒与目标GUID前7秒，复用上轮目标2秒，三候选全部backend/core还原/30OEM/FD/BootShim/v3及源/宏/摘要交叉审计通过，四次计划早期→2/7/2，零设备查询/启动。新增只读bundle检查器与清单。用固定NativePrelink2b6ffb5实际解析已保存CI普通ARM64/4K内核，六种篡改拒绝，确认通用baseline设备功能全关，当前归档/预链接/ADT尚缺，不作为enuma可启动内核。无固件源码/内存/verified变更或重启R-002；build/workspace保持串行，晚间须重新核对连接与恢复条件 · 本提交号见后续Git · docs/operations/2026-10-23-evening-validation-plan.md、reports/enuma-evening-probe-bundle.json、enuma-kernel-baseline-audit.json及当前构建/打包报告。

- 2026-10-23 Asia/Shanghai · 上一里程碑a1b2b01已推送。用户授权从当前设备获取UART配置，条件不够则屏幕。15:18 root只读核对enuma/完成1/槽_a，命令行115200n8、serial0指988000，console disabled，GPIO117/118，活动console仅pstore，998000是另一绑定；实物接点/TX-RX/电平和UEFI输出未闭合，按条件选屏幕主线。保留metadata绘制守卫和晚间逐次门禁，未重启/启动镜像/写设备，未重读分区摘要、未改内存/verified/R-002；原始FDT/日志私有out，结构化报告脱敏 · 本提交号见后续Git · docs/operations/2026-10-23-uart-or-screen.md、reports/enuma-uart-discovery.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑a1322b9已推送。按用户继续屏幕诊断，新增独立EnumaScreen后端与十二行快照页，复用固定DarwinBoot/AOSP字模，仅GOP Blt、不解引用FB；显式禁写/矩形scratch边界/模式与错误锁存/回调重入/完整EFI64位字形比较及页面失败停止测试通过。使用固定Mu归档真实头host ASan/UBSan、AArch64 COFF编译通过；生成并目视检查合成预览，不是实机截图。对象仍需memset运行时与全固件链接验证，尚未INF/FDF/调用者集成或启用写屏。冻结82ce8a5三候选bundle复查通过，零设备查询/启动，无固件源码/内存/verified或R-002变化；接入仍待唯一GOP与真实几何/像素范围 · 本提交号见后续Git · docs/operations/2026-10-23-bounded-screen-renderer.md、diagnostics/screen/、reports/enuma-screen-diagnostics-host.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑15125ea已推送。按用户要求预研系统卷/内核/iPadOS用户态；核对官方文档、固定UniXNU/sheng/NativeUfs/NativeRamBlock与只读nuwa发现审查。新增离线审计器，12份Git blob/SHA核对通过，明确FAT运输与APFS根卷分层、内核归档/prelink/ADT缺口、SM8550硬件不可直接复用、PMGR根卷依赖及userdata dry-run容量盲区。形成分阶段离线与实机验收/数据写入边界，未查询或操作设备、未改固件/board/内存/verified、未下载大DMG或构建系统卷。Git跨用户所有权初次拒绝后改成仅命令级精确safe.directory，无全局设置修改 · 本提交号见后续Git · docs/operations/2026-10-23-system-kernel-userland-roadmap.md、scripts/audit_system_roadmap.py、reports/enuma-system-roadmap-audit.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑9c85a6b已推送。新增仅reset配置FAT32，复用固定上游函数，发现尾部空闲簇非确定字节后增加双FAT/几何校验的空闲簇清理，双构建一致/mcopy回读通过；53项Python通过。固定六份归档配方，复用sheng通用builder，macOS新增platform模式真实构建四归档并按既有defconfig链接，结果待运行。未接initrd publisher/打包boot，未改固件/board/内存/verified/设备；今晚三候选不变 · 本提交号见后续Git · docs/operations/2026-10-23-discovery-volume-platform-link.md、reports/enuma-discovery-volume.json、config/kernel-archives.lock.json。

- 2026-10-23 Asia/Shanghai · 上一里程碑a801314已推送。首轮platform CI39926725474通用bootstrap与前三归档步骤通过，ArmDTPlatform遇Apple Clang不识别-Wno-unnecessary-virtual-specifier且-Werror而失败，尚未平台链接。补仅移除该开关的固定补丁，原sheng不变，严格apply/输出hash本地通过，保留其余warning/Werror。另完成历史enuma启动头/FDT离线运输审查：initrd50124652B=generic50122422+vendor2230，mod512364，不能推导临时候选。无设备动作/板参改变，后续CI待重跑 · 本提交号见后续Git · reports/enuma-platform-kernel-first-failure.json、reports/enuma-initrd-transport.json、patches/kernel/0001-apple-clang-driver-warning.patch。

- 2026-10-23 Asia/Shanghai · 上一里程碑250cdf9已推送。第二轮CI39927966148/head250cdf9成功，五个真实归档步骤、四归档、按既有defconfig的源平台内核链接通过。下载21417672B内核/b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d，本地固定NativePrelink独立解析普通ARM64、可执行入口、双4K/iOS17与平台/CPU/pthread三定义，通过run/head/recipe patch/feature核对；首轮失败产物负向拒绝。完整重写STATUS，仍明确正式board归档/预链接/完整ADT/硬件初始化缺口。无设备动作/内存或verified改变，晚间三候选不变 · 本提交号见后续Git · reports/enuma-platform-kernel-ci.json、scripts/audit_enuma_platform_kernel.py及operations/2026-10-23-discovery-volume-platform-link.md。

- 2026-10-23 Asia/Shanghai · 上一里程碑976a57d已推送。依用户启动授权，在摄像头正常录制后先做early-control-2s一笔临时boot；18:24:02接受，ADB16.134s/Android完成30.613s，root及原boot/vendor_boot摘要通过。用户确认无按键、自行返回。录像完整解码，抽查黑屏/小米/HyperOS/锁屏，无UEFI诊断文字；不当SimpleFb/GOP或入口门命中证明。不flash/erase/改槽，未追加目标候选；相机/原录像仅out不入Git · 本提交号见后续Git · reports/enuma-evening-early-control.json、operations/2026-10-23-evening-early-control-result.md。

- 2026-10-23 Asia/Shanghai · 上一里程碑1e1ab25已推送。依用户继续实机/录像授权完成SimpleFb point20完整GUID 2/7/2，ADB16.065/21.482/16.069s，差5.417/5.413且2秒重复差0.004；三笔Android/root/原摘要通过，用户确认无按键。中途7秒准备fastboot身份五组查询失败，未发镜像；普通reboot恢复核验后新会话全门禁通过再执行，未弱化校验。四段录像完整解码，抽查无UEFI文字需手机补录；不证明主体/协议返回，继续构建point21。无flash/erase/改槽/内存/verified变化 · 本提交号见后续Git · reports/enuma-evening-simplefb-first-pass.json、operations/2026-10-23-simplefb-guid-timing-result.md。

- 2026-10-23 Asia/Shanghai · 上一里程碑3f288f1已推送。复用既有point21生成GUID-only2/7候选，实际AArch64/core还原/30OEM/FD/BootShim/v3与同源检查通过，依持续实机授权再做2/7/2。ADB16.102/22.565/16.081s，差6.463/6.484s、2秒重复差-0.021，三笔Android/root/原摘要通过，用户确认无按键。支持直接PE返回，不证明EFI成功/GOP，差额不称精确5s。三录像完整解码、抽查无UEFI文字，暂不需手机；workspace串行通过。保持metadata/Probe守卫，无代码/内存/verified/分区写入变化 · 本提交号见后续Git · reports/enuma-simplefb-return-timing.json、operations/2026-10-23-simplefb-return-timing-result.md。

- 2026-10-23 Asia/Shanghai · 上一里程碑12c4e74已推送。复用既有16/17门构建同源30OEM候选并做17/16/17实机分类，ADB16.057/22.524/16.082s、全部Android/root/原摘要；三录像完整解码。支持最终非错误返回而非数值EFI零或实际GOP快照；warning保留。147实际诊断头/桥接/完成门host回归重跑及workspace串行通过，无代码/内存/verified/分区写入。按键用户确认待补充，暂无手机补录需求。下一步只读GOP协议与模式，不撤绘制守卫 · 本提交号见后续Git · reports/enuma-simplefb-status-classification.json、operations/2026-10-23-simplefb-status-classification.md。

- 2026-10-23 Asia/Shanghai · 上一里程碑f214eb0已推送。用户补充确认18:52—18:59三笔状态分类均无按键，补入报告/STATUS，排除本组人工按键恢复；不扩展为数值EFI状态/GOP已验证。本轮无设备查询/启动 · 本提交号见后续Git · reports/enuma-simplefb-status-classification.json。

2026-10-23 · 上一里程碑22768a6已推送。新增只读GOP审计与默认关闭门禁；固件019191f首次INF解析失败，250849f修正后两份候选全链接/30OEM/FD/BootShim/v3通过。36元数据参数+6谓词+6CLI、155诊断门及串行workspace通过。2026-10-23 19:45:38首笔临时boot无自动返回，硬停追加；用户恢复Android，2026-10-23 19:48:15核验原状态/摘要通过。互补镜像未启动，GOP结果未知。证据：reports/enuma-gop-query-device.json、reports/enuma-gop-audit-host.json、docs/operations/2026-10-23-readonly-gop-query.md。用户更新无渲染时的录像策略并写入AGENTS。当前提交号下一条补记。

2026-10-23 · 上一里程碑7b7a789已推送。按用户要求继续离线拆分GOP与复位，固件e286834已推送/54输入锁；提供者INF回基线，移除本地复位依赖，以非错误标记回既有Core门。137阶段/参数、30标记、6实际Mu传输、7CLI、177 Core回归及四个AArch64对象通过；step0/1两候选实际全链接/30OEM/FD/BootShim/v3与嵌入FD/源一致审计通过，均未启动。串行workspace通过，旧超时根因未定，下一轮先安装后返回对照。证据：reports/enuma-gop-core-split.json、reports/enuma-gop-audit-host.json、docs/operations/2026-10-23-gop-core-return-split.md。当前提交号下轮补记。

2026-10-23 Asia/Shanghai · 上一实现里程碑595d6a6已推送。按用户要求补齐HANDOFF交接入口，记录两仓固定版本、失败/人工恢复事实、两候选路径与摘要、逐笔验证顺序和执行器未自动处理的停点标志；本次重新计算两镜像SHA均匹配报告。未重跑构建测试、未操作实机，无新增决策或审批项，PENDING-HUMAN仍无按键待办。证据：docs/HANDOFF.md、docs/STATUS.md、reports/enuma-gop-core-split.json。本文档提交号见后续Git。

2026-10-23 Asia/Shanghai · 上一交接090e20a已确认远端main一致，固件e286834一致。本轮新授权与在场确认后重跑bundle审计，顺序临时启动step0/step1；ADB16.906/15.844秒，完成/root/原摘要通过，用户分别确认全程未按键。最后身份/原槽/解锁复核通过，无flash/erase/改槽或源码/内存/verified变化；仅前后截图，无持续录像。旧超时根因未定，单次时序不唯一证明门命中。证据reports/enuma-gop-split-device.json、docs/operations/2026-10-23-gop-split-device.md；本提交号见后续Git。

2026-10-23 Asia/Shanghai · 上一里程碑990d225已推送。本轮按继续至XNU请求完成step2/3全链接与打包审计；step2于21:20:06接受，ADB16.923秒、完成31.178秒，用户确认无按键；step3于21:24:57接受，75秒无返回，停止追加，用户人工恢复后21:27:29核验Android/root/原槽/解锁/原摘要通过。step4未构建/启动；实际链接反汇编保留但根因未定。donor解压摘要匹配固定同版本pin、三组闭包/绑定计划通过，未emit预链接镜像。无内存/verified/flash变化。证据reports/enuma-gop-step23-device.json、reports/enuma-gop-step3-offline-boundary.json、reports/enuma-donor-decompression.json、reports/enuma-donor-closure-audit.json；本提交号见后续Git。

2026-10-23 21:47 · 按人工恢复后持续工作规则完成Mode拆分，固件26b1f99已推送；设备前序b0376ce已推送。两新镜像审计/主机/负例/workspace通过，新step2 Android核验通过、无按键确认待答。证据operations/2026-10-23-gop-mode-split.md、reports/enuma-gop-mode-split.json；step5未测。

2026-10-23 21:58 · 编译入口归属迁移：固件00ddc01已推送，设备前序1b92a58已推送。两档重建、bundle/四负例/workspace、三ownership及10兼容测试通过；差异记录为SEC时间/引用与Pcd调试标识，不称字节复现。旧step2/5及迁移step2无按键返回已确认；step6构建中。证据reports/enuma-firmware-build-ownership.json、reports/enuma-gop-mode-device.json。

2026-10-23 · Mode头step6实测自行返回，用户确认无按键；ADB15.879秒，Android/root/原摘要通过。设备前序04a2b34已推送。证据reports/enuma-gop-mode-device.json和enuma-gop-mode-header-boundary.json；step7构建中。

2026-10-23 · step7无按键自行返回，Android/root/原摘要通过，ADB15.871秒。前序edb2be4已推送；当前构建00ddc01完整跨度step3新候选。

2026-10-23 · 当前00ddc01完整跨度step3临时boot后ADB15.926秒、完整核验32.396秒，用户确认全程无按键。step6/7/新step3均受控返回；旧失败原因未知。前序acd11d7已推送。证据reports/enuma-gop-mode-device.json。

2026-10-23 · 只读实机显示发现：确认splash范围、DRM模式、MDP与八管线偏移，固定SDE来源。新增可重放audit_live_framebuffer.py。前序4e72d12已推送；未写屏/MMIO/新boot。

2026-10-23 · 固定表MDP覆盖审计及无交叠检查通过，R-004最小映射提案dry-run通过但未应用；前序9433465已推送。新增scanout设备动作停止待批准，未访问MMIO/像素或新boot。证据reports/enuma-display-mmio-coverage.json、patches/proposals/r004-display-mdp-map.patch。

2026-10-23 · R-004已批准；固件9f50890已推送，设备前序83d0fe1已推送。25 host/对象/240 GOP、两实构建/bundle负例/workspace/staging唯一差异通过；对照与step8无按键返回，后者慢5.309秒，互补构建中。证据operations/2026-10-23-r004-scanout-device.md。

2026-10-23 · R-004互补候选22:45:27自行回Android，ADB15.876秒/核验31.930秒，root/原摘要通过且用户确认无按键；较selector1快5.311秒。三份全链接/审计与同源互补差异校验通过。前序33159d2已推送，源固件9f50890。

2026-10-23 · 落实用户硬停文档规则并刷新HANDOFF/STATUS为当前进度：17aa47a地址探针40主机用例通过，同源对照构建中，step9未全链接/实测。前序设备0d85928已推送；当前无新硬停。

2026-10-23 · 23:16:54 838b38f linear-control step3临时boot后75秒无返回，23:18硬停追加并落实HANDOFF/STATUS，当前待人工恢复；step10未执行。证据reports/enuma-linear-control-timeout.json。

2026-10-23 · 人工恢复核验完成：2026-10-23 23:20:44 Android/root/原槽/解锁/原摘要通过；已同步刷新HANDOFF/STATUS，不再等待按键。step10离线审计通过但未实测，继续离线SEC布局稳定化与新基线。


2026-10-23 · 23:40 · f15d520双构建/全链接/打包/候选资格通过，SEC载荷一致，Pcd仅RSDS八字节变化。历史源锁审计与五负例/workspace通过。下一步新step0门禁，不是硬件通过。


2026-10-23 · 23:41:10 · f15d520 epoch-control-b step0：ADB15.856秒/完成31.445秒，身份/root/原摘要通过，用户无按键确认；新step9/10待构建。


2026-10-23 23:46:56 · f15d520 step9：ADB16.964秒/启动完成30.109秒，root/原摘要通过，用户确认无按键。image9a1cd385f7b7ecb77543db442acb71adf9167506346dbb24d12d8795c61d7864，FDe1f907465cd8d5b1908b4a3d9fb4e1515051fd975faa0773ff4b77fb40b44463。短返回支持splash地址存在性；step10正在离线构建，尚未实测。


2026-10-23 23:50:53 · f15d520 step10：ADB16.947秒/启动完成30.745秒，root/原摘要通过，用户确认无按键。image3364f1726954f246ef3f7f82f52f69fc3aa75e50c2eced8ec62566558b639473，FDea1fb90a73dfe0ecf1413e9d7dfdb2c989bafab0b40c9e1b693d6450ffe795bc。仅格式/压缩谓词时序证据；不能证明活动性、唯一性、几何、pitch或像素安全。


固件ab0cb79已推送并更新当前gitlink/源锁：新增step11几何/跨度只读谓词，84主机用例O1/Oz+ASan/UBSan及AArch64对象通过，无新映射/像素/寄存器写入。当前正在完整构建同源step10对照，随后构建step11；ab0cb79尚未实测。f15d520 step9/10实测里程碑a50d0fb已推送。


2026-10-23 23:59:30 · ab0cb79 step10：ADB16.919秒/完成31.082秒，用户无按键确认，root/原摘要通过。image5f303d1d2d4586597a34adc0a98b512a5454f0786d5bcbb5eab7eb47a176822b，FDb026f96806723c9a28e540034f3139fb5492892a704ae035985927209cfc3367。格式层对照受控返回，step11仍待单独资格/实测。


2026-10-24 00:02:48 · ab0cb79 step11：ADB21.196秒/完成36.695秒，用户无按键确认，root/原摘要通过。image2cf0b95911aa7d6b0b066382656304163482f54e133f8c556e9a0fbfd9e1ea4c，FD1ebfd9e7808df6bfba8a70c9349e76927d342f668a048081b2540612505f5c1c。几何/stride/完整跨度仅有谓词时序证据；唯一性、裁剪、额外平面、活动性和写屏仍未证明。


2026-10-24 00:08:19 · step11 selector2互补探针ADB15.866秒/完成30.310秒，用户无按键确认，root/原摘要通过；与selector1约21.196秒共同支持固定几何/stride/跨度条件拒绝，具体字段未知，不是硬停。YSTRIDE0按固定SDE源码610..634行包含两个16位pitch字段。下一软件step12解码实际源矩形/裁剪/stride低半字和较小保留区边界，只读，不认定唯一/活动或物理-IOVA一致。


2026-10-24 · 设备085deac已推送ab0cb79格式对照及step11互补受控拒绝。固件7dc3bf1已推送实际描述只读解码，60项源锁工作树已固定，10000样本/O1/Oz/ASan/UBSan/AArch64与GOP回归通过；同源对照完整构建中，step12未构建/实测。遵用户新规则，清理STATUS/PENDING/README旧状态并落实全套交接，文档提交推送前不追加实机。


固件文档主分支2b3849a已推送，修正README/构建归属和历史说明；设备代码有意固定7dc3bf1以完成同源重建，子模块中的README/AGENTS属于该提交历史快照，当前工作规则与状态以本仓及固件主分支文档为准。


2026-10-24 · 全套当前文档7c6e1c6及固件文档2b3849a已推送。7dc3bf1 step10/step12完整构建/AutoGen与静态库/原OEM/FD/Boot v3/候选资格/同源bundle均通过，尚未上机。先提交本次资格状态再同源step10门禁，见operations/2026-10-24-bounded-descriptor.md。


2026-10-24 00:24:06 · 7dc3bf1 step10，ADB15.877秒/完成30.799秒，用户确认无按键，Android/root/原槽/解锁及boot/vendor_boot原摘要通过。image93a787117d8b72bf24c9397141b13b95332e694f2ef8c055b9a3eca29abc6b21，FDde159ec291cdfb30cabc083757eb4e755c059fc5eb37d756d32212ba3b4b29d4。
同源格式对照已完成。下一步先提交推送当前文档，再以完整新设备门禁运行step12。step12已离线资格通过、尚未实测。


2026-10-24 00:27:02 · 7dc3bf1 step12，ADB16.927秒/完成30.978秒，用户确认无按键，Android/root/原槽/解锁及boot/vendor_boot原摘要通过。image3770151e19731745d253cff397f16cb16da752f389dcf321ba8fe3e0e92f09b7，FD602449c0598f1513dd12f546590653eced359fa5094b755f293d1e848b9ca982。
step12已受控返回；只能结合时序评估描述谓词，不认证活动/唯一性或物理-IOVA一致。尚未写屏，不扩大R-004。


2026-10-24 · 6f07283已推送step12实测及全套当前文档。固件d8a8c1f像素提案加4db47e7保存前缓存同步修正均已推送，62项源锁工作树已固定；33假显存场景/本地scratch AArch64对象及6审查门禁/1恢复门禁/3身份/7v3/5错误构建组合通过。旧d8对照仅构建未测，新源对照重建中，像素镜像尚未构建或执行。R-005 preparing，未请求审批；原固件导入文档注释移动经0296ed8恢复固定摘要，设备从未使用坏文档头。

2026-10-24 · 按用户“下一轮实机验证之前落实所有文档”完成当前状态对账。固件c73eb6e已推送，显式像素旗标传入C编译，62项源锁更新；4db旧只读对照已完整构建/资格通过但从未上机（image d0b371e42b7c72c2f3046656a65d98a2c0651bf12fe8b14c41389286fbeb8361，FD 93a256eb7677117d4a1ba3fb72f0f7f6ec3eaddae798559936e346c1e20ee67b）。当前源码两候选均待重建，保护FD审计代码正向运行仍待新pixel FD；策略4个测试通过。STATUS/HANDOFF/审核/人工/入口/操作记录同步，最近实际设备结果仍7dc3bf1 step12，未新增设备动作，R-005仍未请求批准。当前设备仓文档提交号与推送结果在本轮完成后由Git记录，不预写成功。

2026-10-24 · 接手用户明确“批准R005”，记录为上述128x8/500000us保存恢复实验批准；精确摘要待新同源构建资格后绑定，不重复申请。当前未新增设备动作，不扩大内存/verified/分区范围。

2026-10-24 · c73eb6e同源step12/step13完成完整链接、30OEM、FD/Boot v3/实际像素指令、AutoGen/库归档及bundle资格。控制image d656b861d4054c7165bfbfc370818776266cea5930942b803434e883ccf7b0d5；像素image c81def7defd58f55beb7b3c22161b3314fb20b49d98057279074d0ea385df534。用户批准R005并确认在场，精确摘要已绑定；只读预检Android/root/原槽/备份摘要通过。固件文档71cd5cb已推送，运行gitlink仍c73eb6e。未新增临时启动；全套当前文档提交推送后才运行对照。证据reports/enuma-pixel-preview-bundle.json、enuma-r005-preflight.json及out/pixel-r005-*-build.log。

2026-10-24 01:20:42 · 已推送资格80df13a后临时启动c73eb6e step12，image d656b861…f7b0d5，ADB15.875秒/完成32.281秒；用户明确全程没有按键，Android/root/原槽/解锁与原分区摘要通过。未执行step13；下一笔前先提交推送当前文档。证据reports/enuma-r005-device.json及out/pixel-r005-control-device.log。

2026-10-24 01:22:45 · 文档/对照eeee7da已推送后，连续录像执行c73eb6e R-005 step13唯一一次；image c81def7d…5df534，ADB16.953秒/完成30.312秒，Android/root/原槽/原摘要通过，用户确认全程无按键。245帧全部解码、最大间隔0.219秒，早期15.98..22.78秒逐帧检查未确认白条；用户说明白点为键盘反光。视频SHA3d18a250…c470c。账本consumed阻止重复使用，无恢复硬停；继续离线同SoC显示handoff/活动路由分析。证据reports/enuma-r005-device.json及out/camera-capture/20261024T012224-pixel-preview-r005。

2026-10-24 · 设备实测f99330c及固件结果文档f79e07c已推送。继续离线固定五份Qualcomm SDE源文件、elish/SM8250 SimpleFb与保存enuma FDT，审计通过并形成现有映射内两读DSI时序使能计划；无像素/寄存器/设备动作，无内存/verified变更，尚未生成新固件。证据reports/enuma-display-activity-plan.json及operations/2026-10-24-display-activity-plan.md。

2026-10-24 · 用户要求DSI时序使能只读实现、构建审计/全套文档后直接实测，确认在场恢复和按需摄像。固件338db59已推送，设备62项源锁/gitlink固定。8项DSI O1/Oz+ASan/UBSan、AArch64两加载无存储/调用/依赖、84旧scanout/GOP/源锁/workspace/像素旗标及恢复身份v3门禁通过；step12与step14/query1/query2三份全链接、30OEM、实际FD两目标只读、AutoGen/库、Boot v3/bundle通过，未新增设备启动。证据reports/enuma-dsi-timing-host.json、enuma-dsi-timing-bundle.json，out/dsi-*-build.log。先提交推送全部文档再实测。

2026-10-24 01:59:48 · 资格/全套文档bbecc2d已推送后运行338db59同源step12，image9671a059…5a0e5b，ADB15.906秒/完成29.797秒；用户确认全程无按键，独立核验Android/root/原槽/解锁/boot及vendor_boot原摘要通过。step14尚未运行；本笔结果与全部当前文档提交推送后继续正向两读。证据reports/enuma-dsi-timing-device.json、enuma-dsi-timing-preflight.json，out/dsi-control-device.log。

2026-10-24 02:03:18 · 对照/全套文档9bb31f2已推送后运行338db59 step14/query1，image11311dfc…b2dbcd3，ADB15.906秒/完成29.516秒；用户确认全程无按键，独立Android/root/原槽/解锁/原摘要核验通过。互补query2未执行，不能仅短返回宣称数值或活动输出；本笔全套文档推送后继续。证据reports/enuma-dsi-timing-device.json及out/dsi-enabled-device.log。

2026-10-24 02:05:38 · 正向及全套文档e254234已推送后运行338db59 step14/query2，image25662b78…053b466，ADB22.281秒/完成36.625秒；用户确认全程无按键，独立Android/root/原槽/解锁/原摘要核验通过。与query1 15.906秒差6.375秒，非精确名义5秒，时序支持至少一DSI时序使能非零；不是寄存器数值/活动/路由/面板/IOVA证明。三笔全部完成，无恢复硬停/人工待办，无写入。证据reports/enuma-dsi-timing-device.json和out/dsi-disabled-device.log。

2026-10-24 · 固件f6c59ba已提交推送；step15计数前置4读、step16最多12读/一次既有Stall(100000)/模差1..64只读实现。33项O1/Oz+ASan/UBSan、真实AArch64仅gBS、240项GOP及真实Mu传输、非法像素旗标/身份恢复/源锁/workspace通过。五份同源step14对照及step15/16正互补全链接/补丁回退、30OEM、AutoGen库/实际FD/Boot v3/bundle通过；尚未新增设备启动。完整文档先提交推送再直接实测。证据reports/enuma-dsi-counters-{host,bundle}.json与operations/2026-10-24-dsi-counters-probe.md。

2026-10-24 · 按用户提供链接只读评估Tlrenhb/UniXNU-enuma b5e9984，固定14份文件摘要与CI元数据；未执行对方脚本/导入参数。保留当前已受控实测Boot v3；对方v1来自umi/pipa，显式DTB输入/持续显示交接应独立核对，未发现当前显示问题由v3引起的证据。证据reports/enuma-tlrenhb-reference-audit.json及operations/2026-10-24-tlrenhb-reference-evaluation.md。

2026-10-24 · 用户要求结合具体情况与公开资料明确判断。只读固定已锁小米内核52a2f18的6份显示源码；首查候选SSPP未关联活动LM/CTL，次查持续显示交接与实际状态，Boot头格式低优先级。发现对应小米驱动含INTF_STATUS状态版本路径，不能把旧TIMING_ENGINE_EN谓词升级为完整活动证明；KMS splash一对一映射降低把IOVA直接定为主因的依据。证据operations/2026-10-24-display-fault-hypotheses.md及reports/enuma-native-display-diagnosis-sources.json；均为可推翻工作假设，不是新增实测结论。

2026-10-24 · step16首次完整链接已成功，但线性反汇编审计器未追踪编译器冷分支，资格阶段拒绝打包；未执行设备。修正为PE入口直接分支CFG常量/表数据流并保持间接调用证明范围限制，实际PE确认6个可能目标、一次100000等待和64比较；错误基址/MMIO存储/错误等待三项审计输入负向变异均拒绝。相同FD重新审计打包通过，无固件代码修改或失败实机重试。证据out/counter-progress-build.log、counter-progress-package.log及reports/enuma-dsi-code-auditor-tests.json。

2026-10-24 02:35:38 · 全套文档/资格a1387b2推送后执行f6c59ba counter-control（step14/query1），image 5f75763ae804b976765e2d81655f17e31c3fb9bf142824ae5b4c7b087b42028c；ADB15.875秒/Android完成29.828秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-dsi-counters-device.json、enuma-dsi-counters-preflight.json及out/counter-control-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 02:37:25 · 全套文档/资格e8b91b1推送后执行f6c59ba counter-ready（step15/query1），image 09f5a287791ab2a4b1c6b9e539b66ae28e72116f246fbc5a8aa9c86046d9b327；ADB21.219秒/Android完成36.047秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-dsi-counters-device.json、enuma-dsi-counters-preflight.json及out/counter-ready-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 02:39:01 · 全套文档/资格0cce2fc推送后执行f6c59ba counter-not-ready（step15/query2），image 4458d6d6c7f4d8f7e5a657b209975b97eea021da1c2835767620fd5e7c8685fc；ADB15.922秒/Android完成31.407秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-dsi-counters-device.json、enuma-dsi-counters-preflight.json及out/counter-not-ready-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 02:40:24 · 全套文档/资格8fe9ef3推送后执行f6c59ba counter-progress（step16/query1），image 467fa418d6615b59af8cccf32a8e29b77c948a3389abb4198b90d9369be6c321；ADB21.187秒/Android完成35.312秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-dsi-counters-device.json、enuma-dsi-counters-preflight.json及out/counter-progress-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 02:41:48 · 全套文档/资格e3975ad推送后执行f6c59ba counter-no-progress（step16/query2），image 36ad981a3f40c12b77f186c41a24f76523660103c64fccfcf267763090c3b508；ADB16.938秒/Android完成31.125秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-dsi-counters-device.json、enuma-dsi-counters-preflight.json及out/counter-no-progress-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 · 用户要求沿判断继续并取得有效增量，可在场恢复和按需摄像。固件60f38e9已推送，64项源锁/gitlink固定；新step17/18使用对应小米52a2f18原生INTF_STATUS和get_status计数读路径，major6+同一活动接口两窗各1..64非回绕递增，最多26读/两次Stall，不写计数使能。27项O1/Oz+ASan/UBSan、真实AArch64仅gBS、GOP/Mu回归、像素禁旗标与恢复/源锁/workspace通过，三份全链接/补丁回退、30OEM、AutoGen/库/实际FD/Boot v3与同源bundle离线资格通过。新候选尚未实测，先全部文档提交推送。证据reports/enuma-dsi-native-{host,bundle,source-contract}.json及operations/2026-10-24-dsi-native-progress.md。

2026-10-24 03:04:04 · 全套文档/资格48b5651推送后执行60f38e9 native-active（step17/query1），image 9068815fc7d5eb5862686aae1500404bf0c5e7f0a8ef9221ba66a1c190bf1fc4；ADB16.063秒/Android完成29.266秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-dsi-native-device.json、enuma-dsi-native-preflight.json及out/native-active-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 · 用户再次明确要求将“基于具体情况、结合公开资料，对故障原因做大胆判断”计入规则。已写入AGENTS持久规则：给出主判断/嫌疑排序/可推翻条件并据此验证，区分推断与已证实事实，不绕过门禁。当前step18/query1已无按键受控返回并独立恢复核验，互补尚未执行。

2026-10-24 03:05:34 · 全套文档/资格3a686b7推送后执行60f38e9 native-progress（step18/query1），image f1fb4d377744ba7aa69162aa7998a18e51c12cb0575d961208219843b58203a3；ADB16.969秒/Android完成32.266秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-dsi-native-device.json、enuma-dsi-native-preflight.json及out/native-progress-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 03:08:41 · 全套文档/资格6cc7639推送后执行60f38e9 native-no-progress（step18/query2），image cc3a698fcbaa53a6249cd04a7b1150a357743f44beb39768325c58ec30f4d8d1；ADB22.265秒/Android完成34.344秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-dsi-native-device.json、enuma-dsi-native-preflight.json及out/native-no-progress-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 · 用户继续后沿“首候选SSPP/图层路由”主判断实施f0cef6f step19，65项源锁/gitlink固定。固定小米52a2f18 CTL/catalog/SSPP与原enuma FDT，确认本机CTL从0x2000开始，保留第一个有界描述，关联非virtual staging与所选DSI两窗各1..64递增，复查配置/描述不变；最多241读/两次既有Stall，禁写不变。51项O1/Oz+ASan/UBSan（含精确241上界）、真实AArch64仅gBS、GOP/Mu/源锁/workspace/像素及恢复守卫通过；三份完整全链接/补丁回退、30OEM、AutoGen/库、实际FD受限审计、Boot v3/bundle通过。尚未新实测，先全部文档提交推送。证据reports/enuma-scanout-route-{sources,host,bundle}.json和operations/2026-10-24-scanout-route.md。

2026-10-24 03:30:35 · 全套文档/资格8034133推送后执行f0cef6f route-control（step18/query1），image 0c0700b7565d2cc54cb9b2ef41ac954e3181df294a50d812ac75b3d3134a1936；ADB16.937秒/Android完成31.14秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-route-device.json、enuma-scanout-route-preflight.json及out/route-control-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 03:32:02 · 全套文档/资格9eb9ce4推送后执行f0cef6f route-associated（step19/query1），image 4faec747aa34c4d084fcff1a089ac9373957ece07aff4c77d43a18cbdeb7aebb；ADB16.938秒/Android完成32.422秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-route-device.json、enuma-scanout-route-preflight.json及out/route-associated-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 03:35:18 · 全套文档/资格11fb20b推送后执行f0cef6f route-unproven（step19/query2），image d01bd6e3d1f66c7eff5a36563dd5c8a79c20c27ee1845f3b4a6d09e0fc0a4d32；ADB21.235秒/Android完成33.781秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-route-device.json、enuma-scanout-route-preflight.json及out/route-unproven-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 · 用户更换摄像头后要求自行旋转，并明确可以开始实机工作。主机原图保留，顺时针90度旋转后已确认Android桌面；即时enuma/root/原槽/解锁及匹配备份、boot/vendor_boot原摘要通过。沿既有授权实现012715b step20，保留step19首候选staging及所选DSI两窗推进，增加源/输出尺寸相等、至少128x8和完整矩形包含于关联LM的稳定三字检查。66项源锁及gitlink固定，旧f0cef6f沿历史锁保留。63项O1/Oz+ASan/UBSan、精确250读、AArch64仅gBS、固定小米52a2f18/FDT、真实Mu GOP补丁和5项像素/恢复守卫通过；三份完整链接/实际FD/OEM/依赖/Boot v3及bundle通过。尚未新实测，先全部当前文档提交推送。证据reports/enuma-scanout-geometry-{sources,host,bundle,preflight}.json及operations/2026-10-24-scanout-geometry.md。

2026-10-24 15:06:43 · 全套文档/资格ddbd2b0推送后执行012715b geometry20-control（step19/query1），image 20f079b4682e0365f2a3e7a1c1707829446c49d0738857458d89dc13d4ddaefd；ADB18.188秒/Android完成32.984秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-geometry-device.json、enuma-scanout-geometry-preflight.json及out/geometry20-control-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 15:08:19 · 全套文档/资格d721f3e推送后执行012715b geometry20-contained（step20/query1），image dfa50d73be6a856202f238901d2308a60fbc3bb94a09e4dfd2009b5ce568b28f；ADB17.141秒/Android完成29.609秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-geometry-device.json、enuma-scanout-geometry-preflight.json及out/geometry20-contained-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 15:10:01 · 全套文档/资格4e4fed9推送后执行012715b geometry20-unproven（step20/query2），image b2964a650722ca57184188210fb5f272eed91e038dec9296c0a5b131c0e5c50d；ADB22.531秒/Android完成37.015秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-geometry-device.json、enuma-scanout-geometry-preflight.json及out/geometry20-unproven-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 · 用户继续推进主线，沿已获支持的staging/几何/所选DSI条件实施ff3db30 step21：严格选中同一首候选及首LM，检查只有该源字段、无其他/未知/边框staging，全部11个dim bit16清零，BASE或精确FG255/BG0常量不透明混合配置，新增字每窗稳定。最多289读/两次既有Stall；禁写及R-005 consumed保持。固定小米52a2f18 CTL/LM/MDSS/CRTC源码和保存enuma FDT的11偏移通过；174项O1/Oz+ASan/UBSan及精确289上界、真实AArch64仅gBS、Mu GOP回归、源锁/workspace和5项像素/恢复守卫通过。67项源锁固定，012715b资格沿历史锁保留；三份完整链接/FD/OEM/依赖/Boot v3/bundle通过。独立即时Android/root/原槽/解锁/匹配备份及原分区摘要通过，相机保留原图并自行旋转。尚未新实测，全部当前文档提交推送后逐笔推进。证据reports/enuma-scanout-blend-{sources,host,bundle,preflight}.json及operations/2026-10-24-scanout-blend.md。

2026-10-24 15:28:59 · 全套文档/资格3a5689e推送后执行ff3db30 blend21-control（step20/query1），image c8722cc15e81561b29cd7bf325a5a45f7a5d30a0580c73de5be799cfdc6ed8ec；ADB17.141秒/Android完成32.688秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-blend-device.json、enuma-scanout-blend-preflight.json及out/blend21-control-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 15:30:40 · 全套文档/资格6c5c1ff推送后执行ff3db30 blend21-single（step21/query1），image 0a2b8544c806fdd960d0fdf35a94b94a19055a90bc5e940d5496d3c8467c7c39；ADB21.5秒/Android完成35.953秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-blend-device.json、enuma-scanout-blend-preflight.json及out/blend21-single-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 15:32:36 · 全套文档/资格67d51ab推送后执行ff3db30 blend21-unproven（step21/query2），image a2cc5cb6583df89e580f26b53911d875783473e0b74f66554c4cbe62c88d8de0；ADB17.141秒/Android完成32.344秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-blend-device.json、enuma-scanout-blend-preflight.json及out/blend21-unproven-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。

2026-10-24 · 用户要求“继续 进度决策稍微大胆一点”，决定改进证据吞吐而非堆复合谓词：8fd3e62 step22保留完整首候选/关联/几何/DSI双窗门控，采样同类<=289读并六类区分严格模式、border-only、其他staging、dim、alpha、继承失败。正反以class×4秒与(5-class)×4秒编码，额外<=20秒/总等待20.2秒，原Core warning与75秒期限不变，编码期间不再读MMIO。194项O1/Oz+ASan/UBSan、两方向AArch64仅gBS、Mu回归、10项解码/像素/恢复守卫、固定源/FDT及源锁/workspace通过；三份完整链接/实际FD/OEM/依赖/Boot v3/bundle通过。68项源锁固定，ff3db30历史锁保留。新实测前先全部当前文档提交推送。无像素/MMIO/分区写或新映射/内存/verified，R-005 consumed。证据reports/enuma-scanout-blend-reason-{host,bundle,preflight}.json和operations/2026-10-24-scanout-blend-reason.md。

2026-10-24 16:02:03 · 全套文档/资格fa98d7e推送后执行8fd3e62 reason22-control（step20/query1），image 9ded5fa6f8e27878d75face87bd473b207e5124652493272640145aab18c304a；ADB16.079秒/Android完成32.829秒。用户确认全程无按键，独立Android/root/原槽/解锁/boot和vendor_boot原摘要通过；无MMIO/像素/分区写入或恢复故障。证据reports/enuma-scanout-blend-reason-device.json、enuma-scanout-blend-reason-preflight.json及out/reason22-control-device.log。下一动作见当前STATUS，继续前先提交推送全部文档。
