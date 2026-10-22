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
