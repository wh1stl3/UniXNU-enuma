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

2026-10-24 16:05 · 31b405d推送后step22正向429c3c14ec2ee527a554012140049baad1f1ac67fb84bd925c849ce7df64d97e无75秒自动返回，停止追加，反向未执行。用户长按恢复Android；2026-10-24T16:06:02.205849+08:00独立完成/root/原槽/解锁/原boot/vendor_boot摘要通过，未分区写入。当前Android；六类未知，冻结长编码及失败镜像。依用户恢复后持续工作规则继续离线隔离/新软件，不原样重试。证据enuma-scanout-blend-reason-device/preflight和out/reason22-forward-device.log。

2026-10-24 · 0efa313落实step22超时和人工恢复后，按用户规则继续离线隔离，实现c45e52a step23。原step20完整算法只增局部四字staging解码，允许已知border bit24，原字仍每窗稳定；不新增MMIO地址、完全移除LM模式/dim/alpha及长编码等待，最大250读/两次原100ms。69项O1/Oz+ASan/UBSan和精确250读、fixture拒绝blend地址/长等待、AArch64仅gBS、Mu GOP/marker、5项像素/恢复守卫、源锁/workspace通过。三份完整链接/FD/OEM/生成依赖/Boot v3/bundle通过；69项源锁固定，8fd3e62冻结历史。不能称已确定step22根因；新候选非原样重试，完整文档推送和即时恢复后逐笔验证。证据reports/enuma-scanout-sole-stage-{host,bundle,preflight}.json及operations/2026-10-24-scanout-sole-stage.md。

2026-10-24 16:22 · 86adc68推送后c45e52a同源step20对照459961e1675150602631647e6db7760a929bed19f922111dd3bccc606d9f0416也75秒无自动返回，停止追加，step23正互补未执行。用户长按恢复，2026-10-24T16:23:08.877428+08:00独立Android/root/原槽/解锁/原分区摘要通过。离线对比成功/失败step20：79模块中77完全一致，SimpleFb .text/data/pdata/reloc一致，PcdDxe和SimpleFb rdata尚需解析。修正仅step22新增逻辑致超时假设，转启动状态/PCD和早停离线隔离，不重试冻结镜像。

2026-10-24 · daf28ca恢复交接推送后继续离线解析：成功/失败step20的两项差异PE（PcdDxe/SimpleFbDxe）只屏蔽标准COFF/debug时间戳及CodeView GUID/age后均逐字节相同，Boot头和192字节shim相同；PCD逻辑/显示代码差异嫌疑下降。封装FV随调试标识变化，不称全FD相同。根因优先转向设备恢复后启动/ABL状态及早期执行位置，下一软件使用无显示MMIO/等待的更早停止点。原冻结镜像不重试，当前Android独立恢复通过，证据enuma-step20-control-comparison.json。

2026-10-24 16:38:36 · 热状态重跑曾成功的geometry20-control（`20f079b4…`，firmware 012715b），前置与两次超时同构（16:23:08恢复→离线约14分钟→临时boot，未断电），自动返回：adb 16.962秒、完成31.221秒、`boot_reason=bootloader`、分区摘要未变。同一条step20/query1谓词今日4笔为3成功1超时（`459961e1…`）。据此排除"人工恢复后设备残留状态"与step20代码路径；超时必为挂死——DxeCore仅在StartImage返回后按status选门，query1/query2各自的编码都未出现。只剩ResetCold/PSCI出口失效（中高）与SimpleFb `0x0ae00000..0x0ae84207` MMIO读挂死（中）两候选，现1 bit通道不可区分。断电冷启动不再执行；下一步为无显示MMIO/无等待的早期停止点候选并重复多笔。enuma `<target-enuma>`与nuwa `fe5ed56e`同时在线，按`ro.product.device`精确选中enuma。证据reports/enuma-restart-control.json、out/device-tests/20261024T163822-dxe-driver-return及operations/2026-10-24-restart-control.md。

2026-10-24 17:12 · R-006候选A（exit10-early）构建完成：`ENUMA_DIAG_STAGE=10`（`CoreDispatcher()`之前，无显示MMIO、无等待），FD `95cd88f9e2c156f65b23ce640cd521231f1f1b96c2d87505460ead3070e4fd51`，Boot v3 `a90836007b9900350ee52f5d3286b55b33f179c6227f88aa0351ac198cf5c517`（3153920字节）。固件源码未改（仍c45e52a），stage10已在既有`dxe-stage-checkpoints.patch`内。构建/FD审计（30个OEM PE/DEPEX不变、省略CPRDxe/DisplayDxe/UFSDxe）/Boot v3回环通过，尚未实机。构建期修复三处环境问题：WSL缺`tomli`（pip --user装2.5.0）、固件仓三个子模块未初始化（顶层checked out至gitlink b8d46c71/b70b4b7b/cfb93724）、staging `uefi/Common/Mu`与`Mu_OEM_Sample`仍是10-22遗留指向nuwa参考树的符号链接（WSL内删除后由preflight重建）。证据reports/enuma-exit-early-build.json、config/exit-early-probes.json及out/exit10-build.log。下一步逐笔实测，最多5笔。

2026-10-24 17:15:10 · exit10-early（stage10、无显示MMIO、无等待）第1笔自动返回：adb 17.007秒/完成30.223秒/`boot_reason=bootloader`，分区摘要未变，前置为16:38成功后的热状态Android。stage10复位不携带状态编码，且不复位而继续正常启动同样会回到Android，2秒延时远小于启动波动，因此单笔既不能证明checkpoint执行也不能证明复位出口稳定；已计划delay=7对照（预期adb约+5秒）先确认checkpoint确实触发，再累计稳定性。证据reports/enuma-exit-early-device.json及out/device-tests/20261024T171456-dxe-driver-return。

2026-10-24 17:20:49 · exit10-early delay=7 正对照自动返回：adb 21.277秒/完成35.603秒（delay2为17.007/30.223，差值+4.270/+5.380秒），与名义+5秒基本吻合，证明`EnumaStageCheckpoint(10)`确实执行、`MicroSecondDelay`与`ResetCold()`均生效，且返回时间可作为延时是否生效的观测。至此stage10路径（无显示MMIO、无等待）2/2自动返回；仍需累计到5笔才谈稳定性。镜像`667b0ce0128d61e336fb1b758dffa6412bc0ffe8c7de059d5a72e6cf39e89053`，FD`1b34dc5e4605e581cf20337f6623c3fa2154f91f1fcceb40eac4439811058af1`。

2026-10-24 17:22–17:24 · exit10-early 第3–5笔（delay2）全部自动返回：adb 15.918/16.988/16.986秒，完成30.984/33.343/31.112秒，分区摘要均未变。R-006候选A至此5笔完成、0挂死，delay2四笔adb极差1.089秒。按预设判别"5笔全返回"成立，超时推向派发之后的显示路径。统计限制如实记录：15%单笔挂死率下5笔全干净的先验概率为44%，本批只能排除高失败率，不能排除早期出口偶发挂死。主判断转为MDP域未上电首次访问挂AHB（解释历史S-001/250849f/S-002/S-003同现象且与读取寄存器数量无关），下一步做只读1个VERSION字的最小MMIO候选。evidence reports/enuma-exit-early-device.json及out/device-tests/20261024T1722*/1723*/1724*。

2026-10-24 17:29 · R-007最小MMIO候选改用现成step14（`EnumaDsiTimingEnabled`，仅两次只读`0x0ae6b800`/`0x0ae6c000`，不读VERSION/CTL/LM、不等待、不写），未新写step：它与失败笔stage13/GUID/detail16/fallback完全同构，唯一变量是探针深度。FD`6469cd7471a0d1c7d5e732d6de419d9fe7d1eb0c06ea6340b1f0c8d4229e65d7`，Boot v3`9609d2358b5b3d930c73fc4d82ad4913dd46e298e141cd7c4d751e99b730fa5b`，打包PE静态反汇编确认只有两次目标读、零目标写（enuma-fd-audit.json的dsi_timing_code，provider PE e65295af）。构建/FD审计/Boot v3回环通过，尚未实机。同时修复scripts/audit_enuma_fd.py的既有bug：step14分支用`args`做局部变量污染argparse的args，导致写报告AttributeError，已改名operands，审计语义不变。三种结果可按时间分开：PASS立即复位、FAIL走7秒completion fallback、挂死则75秒无返回。证据config/exit14-minimal-probes.json、out/exit14-build.log。

2026-10-24 17:31:23 硬停 · exit14-minimal（step14，仅两次只读0x0ae6b800/0x0ae6c000，无等待无写，镜像9609d2358b5b3d930c73fc4d82ad4913dd46e298e141cd7c4d751e99b730fa5b）第1笔75秒无ADB/fastboot返回，17:32:38停止追加，未执行第2-5笔。相机快照out/camera-capture/20261024T173305全黑，与16:03/16:20两次现场一致。该profile带7秒completion fallback，PASS或FAIL都会回Android，故无返回只能是挂死。对照：同期exit10-early（0次MMIO读）5笔0挂死，本候选（2次读）第1笔即挂——挂死点在首次触碰显示窗口，与读深度无关；主判断升为高置信，并提出状态假设（早期复位使XBL/ABL认为显示已初始化，下次启动跳过初始化，UEFI读落在未上电域挂总线），可解释历史S-001/250849f/S-002/S-003。待用户长按恢复并核验；恢复后先完全断电冷启动再跑同一镜像以判定该假设。证据reports/enuma-exit14-device.json、out/device-tests/20261024T173123-dxe-driver-return。无像素/MMIO/分区写。

2026-10-24 17:36 恢复核验 · 用户长按后确认Android。主机独立核验通过：enuma `<target-enuma>`（同时在线nuwa `fe5ed56e`未参与）、`sys.boot_completed=1`、root(magisk)、槽位`_a`、`ro.boot.flash.locked=0`、`boot_a`=8f40f0c9…与`vendor_boot_a`=3da202d0…均与备份一致。此间无分区写入。下一步按D-128做完全断电冷启动判别：关机后直接按住电源+音量下进fastboot，不经Android，再临时boot同一份exit14-minimal一次。

2026-10-24 17:38:51 第二次硬停 · 完全断电冷启动判别：`adb reboot -p` 关机（enuma从adb消失），用户按电源+音量下直接进bootloader（不经Android），主机核验fastboot身份product=enuma/current-slot=a/unlocked=yes后临时boot同一份exit14-minimal（9609d235…），75秒无ADB/fastboot返回，停止追加。相机快照out/camera-capture/20261024T174026全黑。**D-128启动序列假设作为挂死原因被证伪**：真正断电冷启动同样在两次读处挂死。据此读窗口账本更新：15:06-16:02碰窗口7笔0挂；16:03-17:38碰窗口5笔3挂；17:15-17:24不碰窗口5笔0挂。主判断升为：16:03后该设备对显示窗口0x0ae00000..0x0ae84207的读取不可靠且冷启动不能恢复，读2个寄存器即挂；推论是恢复可靠访问前任何"读到什么"的显示结论都不可信，继续加深探针无意义。下一步按序：断电静置10分钟以上再单笔、离线核实XBL/ABL是否初始化显示域、必要时评估读窗口前显式确认域上电（需NEED-REVIEW）。新增scripts/run_enuma_fastboot_probe.py支持从fastboot冷启动坐标起跑。无像素/MMIO/分区写。

2026-10-24 17:45 · 用户恢复Android并要求查公开资料重新分析。Android侧只读核验全部通过（enuma、boot_completed=1、root、_a、unlocked、boot_a与vendor_boot_a摘要与备份一致）。**关键零风险观察**：`adb reboot bootloader`进fastboot（不加载任何镜像）拍屏可见橙色FASTBOOT字样，说明停在fastboot时显示管线是活的（out/camera-capture/20261024T174400）。据此把三条公开来源接成机制链：①Qualcomm官方bus-hang示例，"unclocked access"读MDP寄存器即挂总线并复位；②BSP实战记录，XBL的Display驱动在EnterFastbootExit时关闭Display并释放framebuffer、不恢复待boot状态，根因为ABL/XBL对fastboot退出后显示资源移交未对齐；③SM8250的dispcc由MMCX电源域供电，Linux经runtime PM+GDSC显式上电，disp_cc_mdss_ahb_clk是寄存器访问开关。叠加本仓事实：simplefb变体排除了OEM DisplayDxe，镜内无任何显示初始化者。故固件读MDP/DSI寄存器属unclocked access→总线挂死，非代码缺陷。**影响**：23个step的scanout判断证据等级从"实测"降为"未知"，含16:38那次唯一成功，须在正确上电后重做。**未解释**：15:06-16:02七笔碰窗口全干净，保留为未知不编理由。下一步按成本A(stage4最早点对照,零写入1笔)/B(固件显式上电,需NEED-REVIEW)/C(转UART或屏上文本)。证据reports/enuma-display-power-sources.json、docs/operations/2026-10-24-display-window-root-cause.md。本轮未boot探针镜像,无像素/MMIO/分区写。

2026-10-24 17:50 · 用户提问8250-AC差异、要求解释B/C、并问nuwa是否在UEFI读MDP。只读核对同项目：UniXNU-nuwa仓grep不到MDP/mdss/0x0ae相关代码；nuwa显示由厂商预编译DisplayDxe承担（Binaries/nuwa/QcomPkg/Drivers/DisplayDxe/DisplayDxe.efi，380928字节，patched版与本版仅差33字节），二进制内部完成初始化并建GOP；nuwa无simplefb路线。enuma原厂路线同理（enuma-overlay.md载明GOP用本机DisplayDxe+CPRDxe+K81），仅诊断simplefb变体故意排除这三个OEM驱动。据此新增候选D（不排除OEM DisplayDxe，由厂商驱动上电后再读），优先级高于B，因为厂商序列经原厂验证且不需自写寄存器；代价是DisplayDxe绘制可能污染待观察屏幕、enuma原厂GOP成功率未实测。D-131记录，STATUS下一步表已更新。

2026-10-24 17:54 · 用户批准D。构建R-008候选oemdisplay-success：**首次保留全部33个OEM驱动**（SIMPLEFB=0、DISABLE_UFS=0，omissions=[]，含CPRDxe/DisplayDxe/UFSDxe），门挂在DisplayDxe的CoreStartImage成功（detail17 + GUID 4138022f-06c7-4f79-9c94-7e33b511a4e7，高低位0x4f7906c74138022f/0xe7a411b5337e949c已核对），带2秒门与7秒completion fallback。三分类按时间：快返回=DisplayDxe成功（显示域已上电，后续读MDP合法）、慢返回=DisplayDxe返回错误（门不命中走fallback）、超时=OEM栈挂死。FD a2b591735a3dbe17cde5afae14da1791372aa2b7f4df09397b8bc6f800c41fd4，Boot v3 c93802790305558f0b7dd267794bafd87d1f740bd4b6a7824de2f19a40f56bf6。构建/33-OEM审计/Boot v3回环通过，尚未实机。这是与前23个step的根本区别：此前所有诊断镜像都排除了唯一会上电的驱动。证据config/display-oem-probes.json、reports/enuma-oemdisplay-build.json、out/oemdisplay-build.log。

2026-10-24 17:56:08 · R-008候选D首测（保留全部33个OEM驱动，门=DisplayDxe成功detail17+GUID4138022f）：**自动返回**，adb 31.924秒/完成45.334秒，分区摘要未变。**关键：不再挂死**——原厂栈在enuma上能跑完并复位，没有重演前面的总线挂死。但摄像头14帧序列显示：帧0-6(Android)mean≈130，帧7起mean≈56且面板呈镜面反光=背光关；对比17:44手动进fastboot时屏幕明明有橙色FASTBOOT字样，本次fastboot窗口到固件全程无任何绘制。故DisplayDxe未点亮面板。时间估算：simplefb基线16.7秒，本次31.9秒多15.2秒，约等于33驱动额外派发(≈8秒)+7秒completion fallback，倾向DisplayDxe返回错误而非成功门命中（成功应在其后2秒复位），但33驱动开销未知，不能据此定论。下一步：同一profile改用detail16失败门对照，两次时间关系可定其返回状态。证据reports/enuma-oemdisplay-device.json、out/camera-capture/20261024T175536-series。

2026-10-24 18:06:19 · R-008三门对照定论：detail17(成功)31.924秒、detail16(失败)30.878秒、detail13(任意返回)33.052秒，**三者无7秒差异→三门均未命中**。detail13在任何status下都命中，故"未命中"不能用DisplayDxe失败解释，只能是CoreStartImage从未对该GUID触发——**DisplayDxe从未被派发**。根因：解析DisplayDxe.depex得8个protocol全AND(157a5c45=Qualcomm EFI_PLATFORMINFO已由PlatformInfoDxeDriver提供、b0760469见于QcomPkg.dec、其余6个未在自带源码中定义)；而33个OEM驱动清单中无MDSS/MDP/DSI/panel类驱动，显示栈正常应发布的protocol缺失，依赖永不满足。故**候选D不能靠"保留DisplayDxe"上电**，屏幕不亮与三门不命中得到同一解释。下一步三选：D1从本机XBL补齐protocol提供者再测三门、B固件自写上电、C1转UART。三次实测均自动返回Android、分区摘要未变、无像素/MMIO由本仓代码执行。证据reports/enuma-oemdisplay-device.json及三次device-tests。

2026-10-24 18:14 · 用户说明无硬件人员支持、无法获取引脚信息。只读核对：enuma原理图+位号图在devicedb.xyz可付费获取(250RUB≈20元，Schematic.PDF+BoardView.PDF)，故硬件资料并非无处可寻；但UART仍需焊接/电平判断/GENI实现核实，属硬件操作，无硬件支持下判定C1暂不具备条件(D-133)。替代通道：enuma已有成熟Linux支持(xiaomi-enuma-dev/droidian:Display、Touchscreen、Brightness、USB Networking均Work；同板WiFi版elish有postmarketOS主线支持，device-xiaomi-elish，内核6.17)，可fastboot boot临时启动Linux并经USB networking取完整dmesg，用于验证MDSS/DSI硬件、取得dispcc/GDSC/MMCX实际上电序列(B所需)、必要时devmem读0x0ae6b800。局限：Linux日志非UEFI日志。该路线不需硬件图不需拆机，优先级高于购图做UART。

2026-10-24 18:35 · 实现A(stage最早点读)时遇到两处固件约束并先恢复到可用状态。①**SEC不继承ENUMA_DIAG_*宏**：Sec.makefile中零个ENUMA_DIAG定义，stage4-8的SEC检查点恒走ENUMA_DIAG_STAGE==0短路，从未生效、历史也无人使用。②**补丁链耦合**：在dxe-stage-checkpoints.patch内插读会破坏后续dxe-dispatch-return的上下文致其apply失败；独立patch因序列位置不同上下文不匹配；另有一次Python写入把patch变成CRLF被git apply判corrupt。已把dxe-stage-checkpoints恢复原样、重算migration与lock、重同步固件子模块，stage10构建重新通过(FD 10bbfbb841ca6ced81c8da38ff5741deff11ee480935e01ab1154cee42e4498c，不含读)。A的下一步实现：改选stage10(DxeCore宏有效、R-004映射已建立)，读操作作为独立patch放在序列末尾、上下文只取两行。本轮未做新实机，设备保持Android。证据out/read10-build.log、out/sec4-build.log。

2026-10-24 18:41 · A第二轮:新建patches/dxe-display-read.patch(上下文只锚三行注释加checkpoint一行),登记migration、board.toml置于dxe-dispatch-details之后,固件仓b9435f8,构建成功(STAGE=10,FD 4a90aa2b3800c1d7d29f19ce569870cd6794c10c600e6a59de3d44a51cafdaf1)。**但离线验证失败**:DxeMain.obj(本次18:40生成)反汇编里搜不到0x0ae6b800/0xb800/0xae6,二进制里也无该常量的literal pool条目,即读代码未编译进去。已知事实:SEC的stage4-8检查点从未生效(Sec.makefile零ENUMA_DIAG宏)。未解矛盾:exit10-early的delay7比delay2慢4.3秒,说明EnumaStageCheckpoint的宏在DxeCore内确实非0,但我的#if ENUMA_DIAG_STAGE==10却没编入。结论:不再在DxeMain上试,改用Dispatcher模块(dxe-driver-checkpoints.patch所在,stage12/13复位已被多次实测证明生效)。本轮未实测、未打包该镜像;设备保持Android。教训:加读的改动必须先在.obj层用objdump确认常量出现再打包,否则"成功返回"与"代码没执行"不可区分。

2026-10-24 18:46 · 按用户要求更新README与docs/README.md:根README在第7段标注"此前探针读到的值受显示窗口可能未上电的污染,不能当显示事实",末段改写为今日收束(unclocked access根因、三条来源、23个step结论降级、候选D证伪、UART关闭改Linux、以及SEC宏与objdump验证的方法教训);docs/README.md同步替换旧的热状态重跑结论。

2026-10-24 18:50 · 按用户指示改用Dispatcher模块。新建patches/dispatcher-display-read.patch(插在EnumaDispatchCheckpoint(12)之前,条件ENUMA_DIAG_STAGE==12),删除DxeMain版,固化仓aaa3c35,构建成功(STAGE=12,FD 1a8f4666fe81f0d1029fef067907b10b508778e97a1439fd772cfeb6a2b342fa)。**构建日志确认该patch apply成功**(check与apply两条都在),但Dispatcher.obj反汇编仍无0xae6/0xb800常量,读未编入。矛盾:EnumaDispatchCheckpoint.h内部依赖ENUMA_DIAG_STAGE==12||==13,而stage13复位被数十次实测证明生效,故宏在该模块应非0;我的#if==12却未成立。由此提出未验证的新怀疑:所有"成功返回"可能并非checkpoint复位而是BDS无启动项后的超时复位(16-22秒分布像固定超时),唯一反证是exit10-early的delay7比delay2慢4.3秒。判定实验:stage12+--stop-delay 30,返回≈17秒说明delay未生效、复位来自BDS(则23个step的时序判据需全部重估),≈45秒说明checkpoint生效。另:用户提供unixnu.com/zh/contributing/repository,官方提交规范为一提交一主题、前缀feat(area)/fix(area)/docs/build(area)/chore,与本仓一直使用的[unixnu-enuma][module]模板不同,后续新提交对齐官方前缀。

2026-10-24 18:56 · delay对照判定BDS超时假设:同一镜像只改ENUMA_DIAG_DELAY_US,各4笔。delay2=15.918/16.986/16.988/17.007(均值16.725,极差1.089);delay7=21.259/21.277/21.284/21.293(均值21.278,**极差0.034**)。均值差4.553秒对名义5秒,且delay7四笔重复性达±0.02秒。**结论:复位确由EnumaStageCheckpoint产生、ENUMA_DIAG_DELAY_US被遵守,BDS固定超时假设排除**;ENUMA_DIAG_STAGE在DxeCore编译单元内确实非0,此前"宏为0"的推测错误。连带:R-006的"0次读干净vs2次读挂死"结论保持效力(其依赖的复位确为checkpoint复位),23个step的时序判据在方法上仍然成立。由此DxeMain.obj/Dispatcher.obj里读数缺失另有原因:要么该编译单元未从打过补丁的源码重建,要么插入块落在编译器丢弃的区域。下一步用"故意在同编译单元引入语法错误,若构建仍成功则证明该单元未重编"来判定。4笔全部自动返回、分区摘要未变、无像素/MMIO/分区写。证据reports/enuma-checkpoint-delay-control.json。

2026-10-24 19:19 · 读数编不进去的排查(仍未解决,已到最后一层):四路皆败——DxeMain独立patch、Dispatcher独立patch、删obj强制重编、把读塞进EnumaStageCheckpoint函数体的运行期分支(681577f)。已确认:①该函数第23行是运行期if而非#if;②dxe-stage-checkpoints.patch确实#include "EnumaStageCheckpoint.h";③preflight对diagnostics/会copyfile;④**staging的头文件确实含读**;⑤但DxeMain.obj二进制里搜不到movz/movk编码,且**obj大小87160与改动前完全相同**(删掉重编也一样)。结论指向编译该单元时用的不是这份含读的头、或include路径指向别处。下一步直接取编译命令行(makefile的CC_FLAGS与include路径)确认,不再靠推断。另记:改migration/extensions登记的任何文件都必须按item.destination重算哈希并同步,否则preflight直接拒绝;按源键算会把LICENSE等条目写坏。

2026-10-24 19:26:55 · A/B对照定案。做法:把两次只读放进EnumaStageCheckpoint的运行期分支(delay对照已证明该分支会执行),A读真实显示寄存器0x0ae6b800/0x0ae6c000,B读未映射的0xdeadbeef作为"代码是否执行"的判别。A(镜像802b1916)19:20:36正常返回16.975秒、分区摘要未变;B(镜像dead10)19:26:55挂死、需长按恢复(现场快照out/camera-capture/20261024T192848全黑)。**B挂死即证明读确实执行,因此A的正常返回证明显示窗口在stage10可访问**。**这推翻了"XBL关闭显示导致域已关"的解释**:域交给我们时是开的,是我们自己的派发过程把它关掉的;unclocked access致总线挂死的机制不变。连带结论:不必补OEM protocol、不必自写MMCX/RPMh序列,方向改为在派发前读取或定位关闭者;23个step的证据等级维持未知但成因已解释;历史间歇性成功与"读落在teardown之前"一致。已把stage11加入同一分支以二分。证据reports/enuma-display-window-access.json。

2026-10-24 19:36:26 · stage11二分实测:读11镜像(592277bc,FD aa6ae70d)正常返回16.984秒、完成31.486秒、分区摘要未变。结合stage10成功(stage11在CoreDispatcher返回后、所有驱动派发完毕),可判定**显示窗口在整个派发过程中始终可读**,本次镜像gop_query=0故SimpleFb未触发该读。**因此"派发期间我们自己关掉了显示域"这一判断不成立**(修正D-135);step14在SimpleFb里读同一地址挂死,原因应归为该读在SimpleFb上下文中不合法,最可能是R-004新增的Display MDP映射属性问题(SEC/早期1:1映射属性正确,SimpleFb走R-004映射;若把Device memory映成Normal cacheable,ARM访问会abort)。下一步改审display-mdp-map.patch的内存属性并与Linux DTS的mdss dma-ranges比对。设备恢复后核验通过(boot_completed/root/_a/两分区摘要与备份一致)。证据out/device-tests/20261024T193626。

2026-10-24 19:47 · 排除法收窄原因。核实:step14读的正是0x0ae6b800/0x0ae6c000(EnumaScanoutAudit.h),与stage10/11读的地址完全相同;EnumaScanoutRead32为`*(volatile UINT32 *)Address`,写法相同;R-004的Display MDP映射属性MMAP_IO/UNCACHEABLE/NS_DEVICE与同表其他MMIO一致且读路径实际未使用它(读走直接虚拟地址)。故地址、读法、映射属性三项排除,原因只能是执行上下文/时序。候选:(a)XBL遗留时钟状态在SimpleFb运行时失效而stage11时又满足;(b)SimpleFbDxe是dispatch ordinal 1(第一个被调度的驱动),其读发生在必要初始化之前;(c)调度期SMM或页表状态差异。已把读扩展到stage12(第一个驱动LoadImage前,EnumaDispatchCheckpoint在ordinal匹配时调用EnumaStageCheckpoint),构建中(固件cc9751f)。stage12成功而stage13挂=锁定SimpleFbDxe的StartImage内部;stage12挂=调度期上下文。

2026-10-24 19:43:23 · stage12二分实测:read12镜像(FD 0432f6e9)正常返回15.939秒、完成30.057秒、分区摘要未变。**三点包围完成**:stage10(派发前)成功、stage11(CoreDispatcher后)成功、stage12(第一个驱动LoadImage前)成功、stage13(SimpleFb StartImage后)挂死 → **挂点锁定在[LoadImage + StartImage]区间内**。地址、读法、映射属性、调度前状态四项全部排除。已在simplefb-gop-query.patch的GOP_QUERY块开头(所有step分支之前)插入一次0x0ae6b800只读,构建中(固件e65a71b),用于区分"读本身在此上下文有问题"与"挂在更早的加载/安装路径"。

2026-10-24 20:00 · early14实测:在SimpleFb的GOP_QUERY块开头(所有step分支之前)插入一次0x0ae6b800只读,镜像early14-v2(3f0136c6,FD 080213cd),**正常返回17.016秒**、完成31.453秒、分区摘要未变。原始step14(同样两次读、无前置读)会挂死,多一次同地址的前置读反而不挂 → 该地址在SimpleFb上下文中的**首次**访问会触发一次性事件并可能挂死总线,第二次访问因状态就绪而安全;而stage10/11/12的同类读均成功。过程中FD审计按设计拦下偏离:目标访问由2次变3次,报"packaged DSI code does not match two read-only target accesses"并拒绝出包,已把审计期望更新为三次,第一次打包因此用的是旧raw、那次实测无效,重打包后才是本结论。固件链路上另修:补丁插入行后hunk头行数需重算(插在第二个hunk)、Python写patch必须保持LF、migration/extensions/锁三处摘要需按destination重算(已加scripts/sync_firmware_digests.py)。

2026-10-24 20:18 · early14稳定性确认(四笔全成功:17.016/17.033/15.956/15.949),step20带预热读三笔全成功(17.004/17.056/18.110),历史两者都会挂死 → 预热读规避有效且稳定。step20(250次完整scanout读取)现在可跑,是自23个step以来第一次能稳定执行完整读取。审计规则已改为更本质的形式:禁止写、必须含预热读、所有读必须落在R-004显示窗口(0x0ae00000..0x0ae85000),不再依赖具体step的精确序列(step20用循环+动态地址,静态序列比对不适用)。像素白条实验被构建脚本拦下(R-005 execution consumed,不可重复使用,需--diagnostic-pixel-preview显式标志),已按纪律提出新的单次申请R-007待用户批准;批准前不执行。同时确认现有1bit通道机制:detail 16/17 + delay 2s/7s 编码PASS/FAIL,若要传出scanout的具体数值需要更细的delay档位或内存传递。

2026-10-24 20:20:53 · 实现并实测"延时编码"取数通道。固件侧:EnumaStageCheckpoint新增ENUMA_DIAG_DELAY_FROM_DISPLAY分支(stage13时预热0x0ae6b800后读0x0ae00000+index*4的低4位,按每bit一档每档一秒编码进复位延时);build脚本--stop-delay新增20档(基础2秒+打开取数模式),gop_step低3位作index。镜像delayenc-idx0(FD 938050ea)。**首笔返回22.365秒,较16秒基线多6.06秒,对应读到的低4位=6** —— 第一次把显示窗口的实际数值传出固件,且1秒档位在主机侧可分辨。**第二笔同镜像挂死(需长按恢复)**,原因待查。设备当前挂起,需人工恢复后继续。

2026-10-24 20:40:52 · R-007像素白条实验执行并挂死(NO AUTOMATIC RETURN),需长按恢复。构建侧先解决两个问题:①staging的Mu基线哈希期望"未打补丁的原始状态",我删掉dispatcher-display-read补丁后残留导致7个基线文件不匹配,按原始态恢复后7/7匹配;②EnumaScanoutRead32定义在#if ENUMA_DIAG_GOP_STEP==13分支内,像素档恰好排除它,预热读改为直接volatile访问(固件a174532)。之后构建成功(FD 86727d1e,镜像ce7f1955),上机前以0.3秒间隔密集摄像220帧。观测:帧0-26为Android桌面mean121.8;帧27骤降33.1;帧28-30过渡;帧31起稳定黑屏mean64.0白像素2.4%(反光)。**全程无白条,无任何帧出现大面积白色**。区分:读路径已被预热修复(step20三笔全成功),写路径仍挂死;step20同样调用EnumaScanoutFindBoundedDescriptor且成功,故描述符查找不是挂死点,挂死落在真正的写动作,疑为framebuffer基址解错导致写到MMIO。证据out/camera-capture/20261024T204042-burst(220帧)、out/device-tests/20261024T204052-dxe-driver-return。

2026-10-24 21:12 · 战略性发现:本仓没有可搬的显示初始化栈,点亮屏幕必须自己写序列。证据:①原厂uefiplat.cfg有EnableDisplayThread=0x1,Qualcomm官方UEFI靠独立显示线程+完整QcomPkg DisplayPkg初始化面板;②本仓QcomPkg为精简版,Library下仅9个库(PlatformBootManager/PlatformPei/RamManager/RfsProtection/SmBiosTable/ArmSmmuDetach/ConfigurationMapHelper/ErrataPatches),**无任何显示组件**;③XBL提取的33个PE里显示相关仅DisplayDxe与CPRDxe,其8个protocol提供者不在其中(候选D已证伪)。XBL能显示是靠它自带的非DXE形态实现,不能当驱动搬。已齐备的信息:MDP窗口0x0ae00000起的寄存器布局、K81两块面板XML(CSOT K81_42_02_0a/BOE K81_35_02_0b)、uefiplat.cfg内存布局("Display Reserved" 0x9C000000+0x02400000为MEM_RES WT_XN;"DBI Dump" 0x9E400000+0x00F00000为MMAP_IO)、Linux主线msm_drm作公开参考。配合延时编码取数通道可实机验证自写序列的每一步。另:SimpleFb的framebuffer取自"Display Reserved"区域基址,FrameBufferSerialPortLib直接写该区域且不依赖GOP(可作为将来的日志显示路径,但当前未挂ConOut,板级SerialPortLib为Null)。

2026-10-24 21:05:55 · 取数通道跨上下文验证:probe0(读0x0ae00000的bit4-7)返回16.975秒,解码nibble 0,结合此前低4位=6即MDP version当前值形如0x?06;**probe1(读0x0ae05014即pipe0的SDE基址寄存器)挂死总线**。关键对比:step20的完整读取在SimpleFb内部读的正是0x0ae00000+Pipes[i]+0x14(含0x0ae05014)且三笔全成功 → **同一地址在SimpleFb上下文可读、在stage检查点上下文读会挂**。故取数逻辑必须下移到SimpleFb内部。另一层含义:MDP顶层可读而SDE寄存器不可读,提示SDE子模块时钟可能未开——这正是自写显示序列要解决的第一件事。设备当前因probe1挂死需长按恢复。

2026-10-24 21:59 · 驱动内取数首轮(vprobe1..3)三笔全部挂死,无返回时间。定位:不是地址问题而是位置问题。证据链:①stage检查点上下文读0x0ae00000成功、读0x0ae05014挂死;②SimpleFb内部(CreateFrameBufferConfig之后、InstallMultipleProtocolInterfaces之前)读0x0ae00000挂死,而这个地址在①里是成功的;③early14与step20在SimpleFb内部(InstallMultipleProtocolInterfaces之后)读同一批地址全部成功。**结论:stage检查点的读发生在SimpleFb的PE入口之前;SimpleFb内部只有协议安装之后的读才安全;CreateFrameBufferConfig与协议安装之间存在一个让显示窗口不可读的窗口期。** 故取数分支必须改插到InstallMultipleProtocolInterfaces之后(与early14的早期读同一位置),此前放在CreateFrameBufferConfig之后是位置选错。另新增scripts/restore_mu_baseline.py(把staging的Mu树幂等恢复到preflight期望的未打补丁基线)与scripts/run_value_probes.py(批量打包+实测+解码);scripts/recount_patch.py按body重算hunk行数,处理git的两处规则(完全空行算空白上下文行、文件末尾换行不算body)。

2026-10-24 21:52 · 收尾。取数分支最终形态见D-145:并入gop-query补丁、放在协议安装之后的预热读之后、只用gBS->Stall编码延时、由既有PASS门复位,故不再需要gRT与INF改动。期间确认并修掉的构建侧问题:hunk行数(工具已代劳)、gBS无ResetSystem(改用PASS门复位)、INF hunk破坏patch reversion断言(撤销)、Mu基线残留(preflight拒绝,已加restore_mu_baseline并接入构建前置)、sync工具把子模块改脏(新增--device-only)。7档镜像step 1、2已构建(step 3-7被终止),**未实测**;设备因21:59那三笔挂死仍需人工长按恢复,最后一笔成功实测是21:43的stage12读(15.939秒)。所有结论已入D-129~D-145、STATUS、README与NEED-REVIEW(R-008待批准)。

2026-10-24 22时后接手 · 独立固件仓快进至b63c9bd并保留递归子模块脏状态；只读恢复核验身份/boot完成/root/A槽/解锁和设备/备份摘要通过，原失败试验保留。固件新74598df已提交推送，常量无MMIO通道、纯reset门、独立寄存器位移完成；主机sanitizer及四份AArch64对象检查通过，共享stage/dispatch门主机检查通过。实际固件构建、FD审计、常量校准未执行；不把静态检查当硬件证据。

2026-10-24 22:26 · 接手复核 codex 的分析。独立验证结果：①编译日志中 ENUMA_DIAG_DELAY_FROM_DISPLAY 完全不出现，而相邻的其它 -DENUMA_DIAG_* 逐项可见，证实旧delay20取数代码从未进编译器，D-140"首次拿到显示寄存器实际值=6"是误判（那5.665秒差值只是启动抖动），D-143/D-144的上下文与位置因果叙述一并失效；②确认唯一真正的编译宏通道是 enuma.dsc 的 [BuildOptions] 里的 *_*_AARCH64_CC_FLAGS，board defines 只提供 $(...) 取值；③确认新固件 74598df 已把 ENUMA_VALUE_* 加进该 CC_FLAGS，并新增构建后守卫（读 GNUmakefile 逐个核对 -D 取值，不符即构建失败），同类错误不会再靠肉眼发现；④新执行链默认离线校验、--execute 一次一笔、0/3/0 校准与0.75秒容差、失败冻结；83个单元测试全部通过。NEED-HUMAN/PENDING-HUMAN 均显示当前无需现场操作与按键。

2026-10-24 22:49 · 新 value transport 通道首轮三笔。构建两档(常量码0/码3),编译日志确认 -DENUMA_VALUE_SOURCE=1/-DENUMA_VALUE_CODE=0|3 真正进了编译器(固件仓74598df的守卫亦记录 actual_defines_checked=true)。期间修掉计划工具的三处接口缺口:capture 未归档镜像、未归档镜像旁的打包报告(探针执行器用它校验镜像,导致zero1在准备阶段失败)、capture 不校验归档产物属于哪个候选(一次把 known3 的产物误归档成 zero,遂加守卫);失败记录保留为reports/enuma-value-transport-device.preflight-failure.json,属接口缺陷非固件失败,故重置账本。实测:zero1=16.991秒、known3=25.503秒(差8.512秒,残差0.49秒在容差内,机制成立)、zero2挂死(同一镜像同一码0,重复性不成立)→ 校准未通过,不得解码,不进入寄存器模式。设备因zero2需人工长按恢复,最后一笔成功实测为22:50:44的known3。83个单元测试仍全过。

2026-10-24 23:04之后 · 用户要求查看最新情况并落实全部文档和提交。本轮无新构建/启动/设备写入，独立只读恢复核验通过：身份/boot完成/root/A槽/解锁及设备与本地备份摘要一致。证据out/device-tests/20261024T230449-recovery-reconciliation.json；原zero2失败result与冻结计划保留。对齐STATUS/HANDOFF/AGENTS/审查/人工待办/README/专项说明，D-149收紧“机制成立”“挂点已定位”等结论，更正目录时间与boot发出时间。firmware三份在途源码及独立Mu递归脏状态保留，不纳入本次提交。此前提交b54bb2b/70cf995已发布；本轮提交与推送结果由Git及后续回执记录，不预写成功。

2026-10-24 23:45之后 · 接手本轮：处置在途代码、修构建环境、取显示规格、提出挂死率基线提案。①**在途三份改动已审并处置**：先提交e5f1ab5（`--value-reset in-driver`，驱动内`ResetCold()+CpuDeadLoop()`并给SimpleFbDxe.inf加ResetSystemLib），WSL首次构建即在`build_enuma_firmware.py:258`断言失败——该处三条守卫刻意禁止ResetSystemLib进入SimpleFbDxe（INF须与源逐字节一致/AutoGen.c不得含ArmPsciResetSystemLibConstructor/库清单不得含pscireset|resetsystemlib），且enuma平台dsc及KonaPkg/UniXNU include无任何ResetSystemLib绑定；审查结论维持守卫，d00c416撤回，保留96d354a。②**Windows原生构建不可用**：alternates经`write_text`写成CRLF致git读作`objects\r`、update-ref全失败（已改`write_bytes`）；`symlink_to`另需符号链接特权报`WinError 1920`（未修）。历史构建均在WSL内完成故未暴露；本轮起构建走`wsl.exe`+Python3.10.12。③**构建不可复现**：同参数重建FD `02f8d31d…` ≠ 已资格`bfb3d6a6…`，故资格只能绑定已归档镜像，本轮重建产物未用于实测。④**显示规格零成本取得**（Android dmesg只读）：面板K81`42 02 0a`dual DSI CPHY、1600x2560、60/120fps、`cmds(117)`/`cmds(115)`、`mdss_core_gdsc`由`pm8150a_s4`供电且DSI PHY无独立GDSC、`dispcc af00000`、DSI PLL 7nm、phy`ae94400/ae96400`、ctrl`ae94000/ae96000`；与仓内`Panel_K81_42_02_0a`XML完全对应。⑤**新增D-152判断**：常量档`Code==0`直接返回、不读不写不Stall，zero1/zero2同镜像同码一成一挂，故挂死不必与显示访问相关；且"0读5笔 vs 2读1挂"在挂死率未知时不构成证据。⑥据此提出R-009（挂死率基线，需批准突破"失败即停"）：本轮未做任何设备动作。证据reports/enuma-firmware-build.json、out/value-transport/indriver-zero-build.log、docs/operations/2026-10-24-takeover-calibration.md。

2026-10-24 23:37 · **事故与修复**。用户批准R-009后实现执行工具`scripts/run_hang_baseline.py`与`tests/test_hang_baseline.py`，单元测试意外真实驱动设备两次：`run_next(..., invoke=subprocess.run)`的默认参数在模块导入时绑定，测试用`patch.object(baseline,'subprocess')`触及不到它，且同时patch掉了`require_published`。后果：23:31:35与23:32:22各临时boot一次baseline候选（f5cf62da0b58…）；第一笔16.031秒正常回Android、双分区摘要未变，第二笔75秒无返回，需人工长按。已按D-154处置：`invoke`改调用时解析（`None→subprocess.run`），测试一律显式传`invoke=Mock()`，测试文件顶部写入警告与原因；同类默认参数缺陷一并修掉`scripts/run_value_probes.py:run_one`与`scripts/reconcile_enuma_recovery.py:reconcile`。新增8个基线测试；全套91个测试17秒通过（原`test_hang_baseline`由94秒真实执行变为0.026秒）。**这三笔（两次意外boot + 前序zero2）均不计入R-009正式ledger**。观察值单独记录：零读常量档2笔1挂，与zero组同形。证据out/device-tests/20261024T233121-dxe-driver-return、20261024T233208-dxe-driver-return。

2026-10-24 23:40 · 用户长按恢复后，主机只读核验通过（enuma/`sys.boot_completed=1`/root/`_a`/unlocked=0/boot_a与vendor_boot_a设备与备份摘要一致），`reconcile_enuma_recovery.py`输出PASS并更新current.local.json。R-009批准记为approved；执行工具与修复、文档随后提交推送，通过后才开始正式统计。

2026-10-24 23:50 · **R-009 执行完成：零读档挂死率 0.125（8 笔 1 挂）**。候选 `out/value-transport/baseline/`（常量0、不读不写不 Stall，FD 02f8d31d，镜像 f5cf62da0b58…），逐笔临时 boot，每笔后提交推送（两次网络瞬断导致 push 失败，被 `require_published` 正确拦下并补推，未跳过门禁）。结果：baseline1 15.943、baseline2 15.966、baseline3 17.001、baseline4 15.914、baseline5 15.952、baseline6 15.945、baseline7 15.947（秒，全部 adb 返回，双分区摘要未变），baseline8 挂死（75 秒无返回，需用户长按）。7 笔返回极差 1.087 秒，零读档时序高度稳定。**合并同口径样本**（zero 组 2 笔 1 挂、D-154 事故组 2 笔 1 挂、R-006 exit10-early 5 笔 0 挂）得 17 笔 3 挂 ≈ 17.6%。据此**修正 D-152**：由 2 笔样本推出"挂死与显示无关"是把基线噪声当信号，本次数据不支持；正确表述为存在 12–18% 与显示无关的基础挂死率，它使单笔对照失去判别力，但不能否定读档挂死率更高（见 D-155）。设备因 baseline8 挂起，待恢复核验。证据 reports/enuma-hang-baseline-device.json、out/device-tests/20261024T234358/234457/234555/234655/234756。

2026-10-24 23:58 · **R-010 读档对照臂实现**。新增 `--value-source raw`（Source 3）：地址表/index/shift/码编码/wait 与 Source 2 完全相同，**仅去掉 `Read(0x0ae6b800)` 预热**——这是唯一能分离"读不安全"与"首次触碰不安全"的对照。改动：`firmware/diagnostics/EnumaValueProbe.h` 加 Source 3 分支；patch 的 `ENUMA_VALUE_SOURCE` 范围放宽到 3；构建脚本加 `raw`→3；`audit_value_transport.py` 新增 raw 分支，要求**恰好一次目标读且预热地址不得出现**；`run_value_probes.validate_plan` 的 source 期望值改为按 role 映射；`run_hang_baseline.check_baseline` 允许重复的 constant-0 或 raw 档案（禁止混用）。候选：index 1 → `0x0ae05014`（历史 probe1 读它挂死、step20 带预热读它成功）。构建 `ENUMA_VALUE_SOURCE=3 / INDEX=1`，FD e9c21817，审计 `reads: ['0x0ae05014']`、`stores: []`、**预热地址 0xae6b800 完全不出现**；Boot v3 回环通过；镜像 a1adecd5，4 笔计划已生成。93 个单元测试通过。固件仓 aa9ec66 已推送，设备锁已重固定。尚未实测。

2026-10-25 00:06 · **R-010 执行完成：裸读 0x0ae05014 挂死率 0.25（4 笔 1 挂），与零读基线无显著差异**。raw1 17.000、raw2 16.974、raw3 15.915 秒（均 adb 返回、双分区摘要未变），raw4 挂死需长按。对 R-009 零读档 8 笔 1 挂做 Fisher 检验 p≈0.5，**无差异**。这**修正了 D-155 的方向**：我原预期裸读接近必挂（probe1/vprobe1-3/step14 都挂过），实际 3/4 成功，故历史高挂死不能归因于"读这个寄存器"；剩余变量是位置（stage checkpoint / 协议安装前 / value-probe 位置）、读的个数（step14 连读两地址、step20 读 250 次）与上下文。**可操作结论**：带预热读 7 笔 7 成功（early14 四笔 + step20 三笔），裸读 4 笔 1 挂——预热是当前唯一有实测支撑的规避手段。局限：4 笔统计力弱（只把上界压到约 60%）；三次返回的 nibble 均为 0，读执行只由静态审计与第 4 笔挂死支持。设备因 raw4 挂起待恢复。证据 reports/enuma-hang-baseline-raw-device.json、out/device-tests/20261025T000143/000242/000340/000436。

2026-10-25 00:20 · **R-011 扫描存活判别候选就绪（未实测，设备待恢复）**。用户要求"先判别 再写显示栈"。判别不写新代码：复用既有 step18（`EnumaDsiNativeProgress`，读两 DSI 控制器的 active/enable/帧计数，两窗各 100ms 要求递增），接现有 PASS 门 → 命中约 16 秒返回、未命中走 fallback 约 7 秒，9 秒差远超容差；该路径自带预热读。构建 `--diagnostic-gop-query 1 --diagnostic-gop-step 18`、`VALUE_SOURCE=0`，FD `3f4b06b8`；审计 `dsi_counter_code` 记录 9 个读地址（version + 两控制器 × {base,+0xa8,+0xac,+0x26c}）且无 store；镜像 `8df9616f`，Boot v3 回环通过；单笔计划已生成并通过离线校验。工具改动：计划/校验新增 gated probe 档案（`role='off'`），对 gated 用 `dsi_counter_code` 审计并把 step18 读地址集钉死，落到别的 step 或混入额外读即拒绝；`run_hang_baseline` 接受 constant/raw/off 且仍禁止混用。93 个测试通过。判读纪律见 D-157：只买一个 bit，不宣布显示可用。设备因 raw4 挂起，恢复后执行。证据 reports/enuma-scanout-liveness-*.json、out/value-transport/alive/。

2026-10-25 00:32 · **R-011 判别实测：DSI 帧计数在跑，扫描没停**。①`alive`（step18 + PASS 门，FD 3f4b06b8 / 镜像 8df9616f）**16.981 秒返回**；②`alivefail`（同 step18 翻成 FAIL 门，FD c0ab4571 / 镜像 d8bdf014）**挂死**需恢复。判读：PASS 命中 ⇒ `EnumaDsiNativeProgress` 返回 SUCCESS ⇒ major6 下至少一个 DSI 接口 active 且帧计数两窗非回绕递增。负对照用历史补齐：10-24 03:05 同配置 query1=16.969 秒（本次差 0.012）、03:08 query2=22.265 秒，而 delay2/delay7 对照给出"adb≈复位延时+14.7 秒固定开销"，故 22.265 即 7 秒 fallback，与"帧在跑、FAIL 门不命中"一致；本次 query2 挂死按 12–18% 基础率解释，不作反证、不原样重试。含义：屏幕不亮**不是缺数据流**，剩余嫌疑收窄为背光未开 / SSPP 源地址未指向 Display Reserved / 内容为黑。下一步先只读绑定 SSPP `SRC0_ADDR` 与 LM/INTF 路由；开背光是写操作须另立批准。设备因 alivefail 挂起待恢复。证据 reports/enuma-scanout-liveness-device.json、-fail-device.json、out/device-tests/20261025T002309、20261025T003045。

2026-10-25 00:43 · `srcaddr`（register 模式读 `0x0ae05014` 高 4 位，FD 168283a4 / 镜像 1ec5f795）×1 **挂死**（75 秒无返回），连续第二挂。本轮累计 **15 笔 4 挂 ≈ 0.267**（零读 8/1、裸读 4/1、alive 1/0、alivefail 1/1、srcaddr 1/1）。**同时 adb 与 fastboot 均为空列表，参考机 nuwa 也不在**，至少一次是 USB 层掉枚举，不能全记在固件。判断与转向见 D-159：单笔 4 bit 在 15–27% 挂死率下信息成本比不可接受，转 R-008（保留内存 + warm reset + Android 侧读回）以一笔带出数十个 32 位值。背光路线同轮明确：KTZ8866 独立 I2C（`i2c@a8c000`/0x11/11bit/372-of-2047），镜像内虽有 XBL 的 I2C/DALTLMM/GpiDxe，但源码树无对应 protocol 头文件，属驱动开发而非一次实验；另有 `KTZ8866_LCD_DRV_HW_EN` 引脚需核实。证据 reports/enuma-srcaddr-device.json、out/device-tests/20261025T004052。

2026-10-25 01:20 · **R-014 执行两次均挂死，屏幕无画面（有拍照证据）**。第一次无拍照；第二次用 `scripts/screen_capture.py`（Osmo UVC 1280×720）拍 60 帧 @2 秒。逐帧判读：frame-000/003/006/008 仍 Android 桌面，frame-010（约 20 秒）起全黑镜面，至 frame-059 全程纯黑。`fastboot boot` 返回 0 但 75 秒无自动回归 → `manual-recovery-needed`。结论：保留原厂 `DisplayDxe` 这一步本身不成立，且**两次同配置挂死非偶发**。PE 分析（`out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi`）：①DisplayDxe 自身承担背光与面板电源（`DisplayBackLightBrightnessLevelControl`、`EFI_DisplayPanelPowerControl`、`Charger power status ... turn off backlight`、`EnableDisplayThread`）；②那两个缺失 GUID **整个 PE 里一次都没出现**，只在 162 字节 DEPEX 中 → 编译期依赖声明、PE 不调用 → 补 stub 即可满足 DEPEX；③`Charger power status` 分支意味着 stub 必须完全被动，否则可能反被关背光。证据 out/screen-probe/oemdisplay-r1/（60 帧）、out/device-tests/20261025T011238-dxe-driver-return。

2026-10-25 01:25 · **文档落地 + 交接提示词**。新增 `scripts/screen_capture.py`（摄像头取证：`--probe`/`--single`/`--burst`，模型可直接读图片）；新增 `docs/2026-10-25-handoff-prompt.md`（自包含交接提示词，含必读清单、已确立事实、明确不要做的事）；更新 STATUS/HANDOFF/PENDING-HUMAN/NEED-REVIEW（新增 R-015：stub protocol 提案，含三项风险，pending 未批准）。设备已由用户长按恢复并只读核验通过。两仓已推送。

2026-10-25 01:35 · **Codex review 纠正 D-160/D-161，D-162 落档**。三点均经本机核实：①DisplayDxe 在 APRIORI 第 32 项（共 39 项），`Mu_Basecore/MdeModulePkg/Core/Dxe/Dispatcher/Dispatcher.c` 1426–1438 显示 APRIORI 驱动被直接置 `Dependent=FALSE; Scheduled=TRUE` 并入 `mScheduledQueue`，调试输出 `RESULT = TRUE (Apriori)`——**DEPEX 被完全绕过**，故"缺 2 个 protocol → 不 dispatch"第一环即错。②把该点与 PE 分析合并：那两个 GUID 不在 PE 内（不调用）且 DEPEX 又被判 TRUE，**两条独立证据说明它们与现象无关，R-015 补 stub 既错又无必要**。③`--dispatch-guid` 用的 `dcfd1e6d-…` 即 audit 脚本中的 `simple_guid`（SimpleFbDxe），而 `--diagnostic-without-ufs` 构建 `SIMPLEFB=0` 镜像内无 SimpleFbDxe → 返回门指向不存在的驱动，75 秒无返回是必然，**R-014 挂死无归因**，D-161"两次同配置均挂死非偶发"一句收回。④gitlink 确曾滞后（`d00c416` vs 检出/远端 `aa9ec66`），已提交修正。R-015 状态改为"动机已推翻，暂不执行"。下一步按 review 方案：以 DisplayDxe GUID `4138022f-06c7-4f79-9c94-7e33b511a4e7` 为目标做 detail15（StartImage 前）/ detail13（StartImage 返回后）两个候选，保持原厂 PE 不变，先定位执行位置。

2026-10-25 01:38 · 用户允许直接修改并给出下一步方案。对齐交接提示词、STATUS/HANDOFF、审核与人工待办、README，新增operations/2026-10-25-display-entry-isolation-plan.md，D-163更正D-162四点：APRIORI零基32/序号33、排队非已执行、fallback仍生效、detail13非具体状态。旧决策/实测账本保留，R-015暂不执行。方案为DisplayDxe GUID的detail15/detail13候选，先离线资格和发布/恢复门禁，再按有效授权逐笔。当前只修改文档，未构建/实机/设备写入/提交。

2026-10-25 · 公开资料路线复审落地：固定MiCode 52a2f18/设备树43b11af、LineageOS 6b34d24、edk2-msm e195262及社区设备树0d41d4d；核对SimpleFb继承行为、splash SMMU生命周期、双DSI C-PHY、KTZ8866板级接线和Android blob适用边界。发现当前源码scheduler/DTB扩展HOB恢复的区域名称缺口，未冒充二进制或实机证据。D-164更新STATUS/HANDOFF/交接词/README及支线方案；新增operations/2026-10-25-public-source-route-review.md。未构建/访问设备/实测，无源码与内存字段变更，文档未提交推送。

2026-10-25 · D-166推进：scripts/audit_display_handoff.py绑定原始XBL/ABL/R-014/vendor_boot/FDT，真实PE和调用审计通过，篡改调用指令/截断PE/截断FDT负例均拒绝。两份专项审计落地。A构建首次reference预检拒绝，改固定firmware检出后通过；Windows AOSP打包/回读通过，scripts/qualify_display_boundary.py核对实际Core宏/常量及产物所有权，另审point15调用先于CoreStartImage、延时/复位出口。镜像29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4，FD776437b5a5eaf1939399fabfc4ec599cb9f58a542de29a2a1f66fc500b10f10d，证据out/display-entry-boundary/pre-entry-aa9ec66及reports/enuma-display-boundary-qualification.json。无新设备动作/硬停/批准；原参考和递归脏状态保留。

2026-10-25 · af913ca已推送且远端一致。用户批准R-016 A单笔；out\device-tests\20261025T020804-recovery-reconciliation.json核验Android/root/A槽/解锁及双分区设备/备份摘要通过。相机原图/旋转图准备通过。主机断开重连守卫四轨迹检查通过，candidate与原厂源码不变；当前等待本轮文档和主机工具发布后执行。

2026-10-25 02:11–02:12 · 实机前b1cf33c已推送。R-016 A镜像29b84e1f…8fa72bd4单笔返回；16.187秒首次ADB、31.312秒结束恢复检查；out\device-tests\20261025T021235-recovery-reconciliation.json独立核验通过。证据out\device-tests\20261025T021107-dxe-driver-return、out\camera-capture\20261025T021104-display-boundary-A、reports/enuma-display-boundary-A-result.json。相机415/415帧解码和50对图像保存通过；无额外boot/分区写入/改槽，无超时或人工恢复请求，R-016 consumed。结果和D-168已同步全部当前文档，发布号由Git后续记录。

2026-10-25 · ada2f3b已推送且A实测证据保持。完成B离线资格及四项Core/元数据破坏负例拒绝，镜像bf6e014d…a03b2e3；未实测。用户随后澄清完整启动链优先，B转备用。prepare_system_prelink.py实际发出54231040字节预链接be83a7ec0c11132c13b9581d8784a1775584bb97ff5c66484bcbb2e7bef0879e，29组件和4K格式复查通过；audit_system_roadmap.py区分真实输出与缺失的完整ADT/FAT/运输/root/错误通道。固定并审查umi源码及测试firmware，config/system-reuse-sources.lock.json和enuma-umi-system-reuse.json落地。无设备动作、内存/verified/分区改动；全部当前文档同步D-169/D-170，新提交号以Git后续记录为准。

2026-10-25 02:45 · 前轮7f8c54c已推送。D-171生成11,024字节ADT与96MiB FAT（49b4d622…6818773），保留内核/原始trust，真实FAT回读一致；扩展check_darwin_adt消费实际输入，ASan/UBSan全截断/损坏trust及既有分配检查通过。旧ADT plan仅刷新board摘要，512MiB/physical_base=null不变；额外1GiB请求负例拒绝。运输审计明确2230字节vendor前缀与whole-initrd FAT契约问题，不选实际偏移。同步当前交接/审查/人工/入口文档，无实机、内存字段、verified或分区改动，新提交号以Git后续记录。

2026-10-25 · D-172：固件01ffaec实现运输/13项报告，336760b统一LF，首轮preflight拒绝DSC补丁上下文后698b7c1修复并完整构建通过，已推送固件main。enuma-abl-v3-concat实际PE原长推进及NOP负例通过；host transport ASan/UBSan正负例通过。FD5a031cd8…1e13f68，32个OEM PE/DEPEX保持仅省略UFS；实际driver/probe宏/PE数组/写保护代码和FAT boot-v3往返通过。103817216字节镜像194fa0f2…00f8b9e独立归档qualified-698b7c1。本次续接核验构建complete=true与归档；无设备动作/新硬停、内存字段/verified/分区变更。同步全部当前文档及AGENTS批量验证偏好，设备发布号以Git后续记录。

2026-10-25 · 前轮1f9088c已推送。D-173重新只读核Android/root/A槽/解锁及两分区设备/备份摘要通过；相机最初不可用，用户连接后14:06:59成功采集。发现报告失败早退绕过cache flush，固件9459426修复并推送，生产尾部故障注入与完整构建/实际PE/AOSP资格通过；镜像d2ab5ef8…7e1db75、归档qualified-9459426。被测payload尾部与staging相等，staging多出的既有SimpleFb保护受实际宏0关闭。新增单笔相机wrapper、记录无需逐笔批准授权并同步全部当前文档；此条为执行前，尚未boot，发布号以Git后续记录。

2026-10-25 14:12:13 · 执行前0fb21cc已推送。S-001镜像d2ab5ef8…7e1db75单笔boot，命令2.625秒返回0、断开5.110秒；75秒无返回，runner退出2，停止追加并consumed。450/450帧可解码，未观察可判读报告。证据out/device-tests/20261025T141158-system-transport、out/camera-capture/20261025T141155-system-transport及enuma-system-transport-result.json。已请求长按恢复并启动恢复录像；当前ADB/fastboot未枚举，恢复核验待完成，所有当前文档同步D-174。无flash/erase/改槽。

2026-10-25 14:15:38 · cf2ae7d超时停点已推送。用户回复已回Android后独立reconcile通过，证据out/device-tests/20261025T141538-recovery-reconciliation.json；恢复739/739帧解码，主录像450/450帧及194截图网格复核未见报告。S-001失败记录保留，current.local.json指向恢复完成；同步D-175全部当前状态/人工/审查文档，继续离线配置ABI隔离，不追加boot或重试失败镜像。

2026-10-25 · 6b1e390恢复文档已推送。D-176核本机DisplayDxe实际字符串/slot0x18/zero分支和shim HOB GUID，固定umi测试配置；新固件cb9e568只变EnableDisplayThread1→0并已推送。主机实际provider ABI测试、实际FD SEC TE配置0和旧值负例、32个OEM PE/DEPEX/新实际PE及AOSP往返通过；5e07e65e…77413327归档qualified-cb9e568。记录clock-skew警告及实际产物证据。此条为S-002执行前，未追加boot，新状态/交接/审查同步。

2026-10-25 14:29:26–14:31:50 · 执行前32a3c63已推送；S-002 5e07e65e…77413327单笔75秒无返回，2.657秒命令返回0/5.125秒断开，451/451帧可解码。已停止追加/consumed，恢复录像在请求前开启；用户报告返回后14:31:50独立reconcile通过，失败result保留。证据enuma-system-transport-S002-result.json，out/camera-capture/20261025T142909-system-transport及20261025T143053。同步D-177全部当前文档，无第三笔boot；继续离线必要边界定位。

2026-10-25 · f98a37f已推送S-002超时/已恢复状态。继续离线构建完整FAT返回边界：cb9e568 stage13/detail13/正确GUID-only/fallback0，FD50bba978…a2bc815，镜像d716e159…47f8304，归档return-boundary-cb9e568。初审因无2M立即数拒绝，复查实际MicroSecondDelay为两次1G纳秒调用后增加精确callee形状审核；新/旧Core破坏负例、错point/fallback/FAT拒绝通过。新wrapper显式资格模式离线通过，无第三笔启动；全当前文档同步D-178并准备发布。

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

2026-10-25 · 固件0080640新增纯组件、e6d1867严格回调状态修复均已推送；本机视频/双链路来源与Android DRM只读核对、28场景/267故障位置和负错误回调测试通过。设备源码锁/gitlink同步，尚无新GOP镜像或上机。


2026-10-25 D-195：真实Mu GOP后端主机及QEMU执行通过（完整链接8d85d39；RAM-only，不安装协议）。firmware bddc5d8实现、8d85d39修正摘要/LF，784a59d接只读入口。29解码/267采集故障、24通道Blt、144 LM故障、1257采样故障和20项固件单测通过。新enuma boot未执行，继续收紧活动LM采集后资格。证据reports/enuma-inherited-gop-*.json，原始媒体本地。


2026-10-25T17:04:20+08:00 D-196：最终898ae25只读双链路入口完成构建/实际FD、PE、编译宏、R-004映射、完整FAT/BootShim boot-v3与不可变资格。镜像f8f14e3b1ec0b5a097d938b55ed85123e913d16392e42cd3f981419e333a4dc8，尚未执行。原活动LM读取511e6cf、计数原生前置898ae25；最终969故障位置/20固件单测通过，QEMU8d85d39 RAM后端通过。当前Android/root/原槽/备份/原分区复核及相机通过，发布后按现有授权S-008单笔，75秒失败停止追加，影音本地。


2026-10-25 17:05:25—17:08:12 D-197：根仓68ddbd8/固件898ae25发布后S-008单笔临时boot，SHA f8f14e3b…33a4dc8。命令2.641s成功、断开5.109s、75秒无自动返回，consumed并停止追加；用户长按恢复，独立Android完成/root/A槽/解锁/原分区与备份核验通过。451主/740恢复帧解码一致，全部本地无音频。无可判读marker，不能归因到某寄存器；继续同入口无MMIO/无查表常量对照。证据reports/enuma-inherited-video-S008-result.json、原失败result.json保留。


2026-10-25T17:21:12+08:00 D-198：S-008恢复后自动离线实现新同入口常量对照c7c29bb，实际PE正常路径只保存UEFI表并return PASS，正文禁MMIO/查表/分配/等待/协议。S-009镜像56eb63dc63bc7e4b76e6746cb42a0f05b25dfa08099b356f63117c8af89a00c7已完整FAT/FD/PE/宏/BootShim/反汇编审查和不可变资格；72PE中70完全同S-008，目标正文变更，Pcd8字节仅RSDS GUID，其余包含Core相同。21固件单测和当前Android/root/槽/解锁/原分区备份、相机通过，发布后单笔，尚未执行。


2026-10-25T17:50:01+08:00 D-199：S-00917:21:50发出，ADB21.156s/完成35.219s自动回Android，独立身份/root/槽/解锁/原分区与备份通过，252帧仅本地。与S-008同Core/构造器/输入的正文对照支持采集正文首嫌；结合厂商dump取电源引用、默认拓扑2/0/2及Mu RGB-only填色，固件d61b6ef修复为330读video-only并拒绝source-alpha格式。主机330故障注入、30解码、21固件单测通过；新全FD构建中，尚无S-010资格/执行。来源、置信度和反证落实judgment文档；旧图consumed。


2026-10-25T18:09:25+08:00 D-200：复核Core发现S-008 FAIL5会继续dispatcher，而S-009 PASS1提前终止，故先前正文因果解释过强。已更正当前judgment/S009派生解释，原试验结果不改。固件1a4b204新增同点PASS2秒/FAIL7秒terminal并禁completion fallback，197头文件场景/22固件单测通过，当前全构建中，无S-010。用户明确授权摘取附件AGENTS适用条目，已合并沟通/证据/逆向交付，不扩大设备或其他授权；原始附件SHA与取舍已记录。


2026-10-25T18:16:36+08:00 D-201：1a4b204新terminal全构建和资格完成，S-010镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386，归档out/inherited-gop/qualified-terminal-1a4b204-q1。实际Core0xf90c..f9b8在hook13/1或5/完整GUID后，两条分支直接2/7秒复位，未回dispatcher。Core/provider宏TERMINAL1/FALLBACK0/实际PE、R-004、完整FAT/BootShim和immutable manifest通过，197头文件/22固件单测通过，当前Android/备份/相机复核通过。附件适用AGENTS已合并，发布后单笔，尚未执行；无原始影音上传。


2026-10-25T18:23+08:00 D-202：根仓563e922已推送，包含适用AGENTS摘取。S-010准备流程fastboot身份检查失败，未发boot、未消耗候选；普通定向reboot后Android/root/A槽/解锁/设备与备份SHA独立通过。首个product正确但后续GetVar失败，is-userspace也未知，不认定fastbootd/固件失败。112帧只本地。证据reports/enuma-inherited-video-S010-preboot-result.json；下一步排查传输身份异常，保留门禁。


D-203（前提交032f069已推送）：

2026-10-25T18:25+08:00。用户明确要求重启fastboot后执行S-010并按结果推进。Android完成/root/A槽/解锁、boot_a/vendor_boot_a设备与本地备份摘要再次独立通过（out/device-tests/20261025T182509-recovery-reconciliation.json）；1920x1080相机通过，不采音频。不可变镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386及1a4b204资格再次通过，尚未消耗。

文档提交推送后由既有runner定向重启选定enuma到bootloader，仍要求product=enuma/current-slot=a/unlocked=yes全部精确通过；再次异常则不发送，保留日志并恢复排查，不用Android结果代替fastboot门禁。通过后仅一笔S-010临时boot，连续本地拍屏及主机时序，75秒观察，无已识别返回立即consumed并停止追加，先恢复核验。2/7秒仅支持terminal分类，不唯一证明内部路径；未发布真实GOP。原始影音仅本地out，不上传Git/Release/CI。无flash/erase/改槽、内存字段或verified变更。此前D-202未发送的原始记录保留。


D-204（执行前文档7d1312b已推送）：

2026-10-25T18:29:27+08:00。S-010已于18:26:07（UTC10:26:07.186360）执行一次临时boot，镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386，固件1a4b20487aa6ac0fbb2973bf508aea1851b61192，FD490fe01ebda7bf8091b3944a54135fb439f73c8c0f05d8ac609e7cdd19b9ba9e。全部执行前文档7d1312b已推送；即时Android/备份/相机门禁及fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过。上次GetVar异常没有重现，根因仍未知，不删除D-202原始中止记录，不放宽身份检查。

命令2.641秒返回，5.110秒观察断开，ADB25.469秒出现、39.438秒完成Android。runner未发恢复reboot；随后独立核验完成/root/A槽/解锁和boot_a/vendor_boot_a设备及本地备份摘要全部通过。270/270拍屏帧解码通过，已目视核对试前桌面、中途小米/Android启动标志及试后桌面；无UEFI/GOP文本证据。原始影音仅out/camera-capture/20261025T182550-system-transport，未录音，不上传Git/Release/CI。

本笔有受控返回，不能记为75秒无报告超时。相对S-009，ADB晚4.313秒、完成晚4.219秒，支持FAIL5/7秒终止的谓词拒绝判断，中等置信；不是直接状态日志，也不是PASS/GOP成功或精确寄存器定位。两个候选Core与采集范围不同、Android时序含噪声，不能仅凭差值确证7秒或S-008根因。S-010已consumed，S-001..010及旧失败图不重试。

按结果推进：主判断转向保守准入模型与实际继承布局不匹配，优先细分首次拒绝阶段/状态，不再默认把本笔当MMIO挂死或盲改缓存。源码要求单CTL/双LM/两个独立SSPP、无border/额外staging、严格dim/blend及RGBX；历史step21保守混合拒绝提供同方向旁证，但不是本笔快照。单源跨LM、border/合法混合、格式/几何/地址边界列为候选；描述表/PCD门禁、双接口前置/稳定性仍不能排除。只有直接取得阶段/状态或同入口对照后才能排序到具体寄存器，不放宽安全准入换通过。

新候选尚未实现/资格/执行。下一步保持同完整输入、完整GUID双结果终止及FALLBACK0，先设计可判读的首拒绝证据（同时区分未到达与已拒绝），主机故障注入和实际Core/provider审查后再构建；不恢复旧长时间编码或失败像素/value计划。若新证据显示采样/解码已全部通过或故障在入口前，则推翻当前拒绝模型主假设。真实GOP/CPU-SMMU/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合；ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更，当前无人工或审批待办。

证据：reports/enuma-inherited-video-S010-result.json；原trial out/device-tests/20261025T182553-system-transport/result.json；独立恢复out\device-tests\20261025T182657-recovery-reconciliation.json。身份解析3项、恢复核验2项、恢复硬门1项回归通过；不可变归档各文件摘要再次匹配。当前源码固件未改动，设备文档/脱敏证据单独提交推送。

D-204发布检查：当前WORKLOG与历史restart-control说明残留的目标标识已脱敏；不改写已推送历史。原始影音未纳入版本控制。


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
