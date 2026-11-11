# UniXNU-enuma

**24r observation-only实现完成 + deep静态审查（2026-11-11，self-checked，仅主机；无设备授权）**：默认0 `NATIVE_UFS_OBSERVATION_ONLY` 变体已实现（为1须 diagnostic 与 external-provider 均1，非法值/组合 `#error`；入口仅 `native-ufs-observe-reuse=1` 且 root/probe 缺席），o=1 的 `-Werror` unused 阻塞按既有条件编译块处理。官方矩阵 NEW exit0：4 默认格、4 显式 o=0 格、o=1 合法格（archive `82811fc3…`、215 undefined、旧7缺符号零引用）、3 组合拒绝、2 非法值拒绝；组件guard 54/624、host 633/639。交付 ignored `.cache/ufs-observation-only-20261111/`（source-snapshot、`increment.patch` `51c851e1…05321a`、evidence.json、SHA256SUMS）；patch 在 fix2 干净基线 apply 后逐字节重现。**实现只在临时 ShengUfs 工作树与本地 `.cache` 证据中，未进入本仓源码，也未提交/推送远端。** 全部 self-checked，未独立验证；无24r设备授权。deep `ses_e35de8053ffel32m1bGoaREoKE` 判 **CHANGES REQUIRED 仅证据/措辞，源码 completion 正确、无须改源码**：①identity/`explain_default` 只在 external=0 两格（`scripts/build-enuma-ufs-store-matrix.py:114-126`），external=1 与 observation 格仅符号集合（`scripts/build-enuma-ufs-observation-matrix.py:68-73`），不得称四格函数体等价；②o=1 准入后 `ufsReuseDiagnostic`（`NativeUfs.cpp:194-225`）noreturn，异常/摘要失败/正常摘要均经 `ufsReuseFinish`（`:188-192`）IOLog+永久 `wfe` 驻留，不 panic/reboot/正常继续，`:1848-1849` 不可达；诊断仍有 GCC/HC/SMMU `mapPhys` 与 OSSharedPtr 映射分配（`:207/213/218`），写路径是编译期不可达而非“无写代码”，单CPU驻留不阻止其他CPU/固件/DMA，watchdog 仍可能复位（`:185-187`）；③host 测试未启用 o=1，不构成动态覆盖。evidence.json 已按此收窄并重算 SHA256SUMS，源/patch 快照 hash 未变（NativeUfs `3fe914…`、RootCommands `96fe71…`、RootQueue `84d904…`、patch `51c851…`）。无 native/prelink/link-map/payload/boot、无 personality/PMGR-observer 重绑定、无24r候选/入口；不升级等级、不称上机通过。下一步独立 verifier 在 NEW ext4 输出复跑观察矩阵（不得 `--archives-from`）、组件 guard、patch apply 重现及 record/diff。下方为历史检查点。

**24r此前检查点（2026-11-11，self-checked，真实链接阻塞；已由上方 observation-only 结论取代）**：已由成功23r记录定位resolved config，官方defconfig/status/archive-plan闭包完成；仅UFS编译开关变化，Virtio和owner-root仍关闭，storage补官方依赖记录后record check0。实际双宏=1 ShengUfs及PMGR archive已构建，最终native链接首缺`_boot_progress_poll`及6个正常VerifiedRoot路径符号，停止不凑stub/策略/启Virtio。11个真实输入archive强符号无重复、六store唯一EnumaRamBlockStore.o；1010对象+11archive未提供缺失符号，23r原hash不变。完整输入及限定dry-run恢复链接argv、供deep裁定的诊断专用fail-closed裁剪问题见[24r记录](docs/ufs-24r-diagnostic.md)。无新native/prelink/map/payload/boot/入口，不可上机；等待主控/deep明确方案，不升等级。下方是历史检查点。

**24r部分主机准备（历史，2026-11-11，self-checked，未上机）**：设备侧仅启ufs/不启PHY的ADT等价门禁通过，原GIC物理地址/长度与CPU/中断属性保持；真实BCM2837预处理排除pe_fiq的另一GIC路径，ArmCpu从ranges+reg映射intc。ShengUfs组件/双开关wrapper及唯一观察参数已写但未构建；首次隔离准备因runner假定的已解析`.config`路径不存在，在kernel/prelink调用前停止。无24r候选/包装/单次入口，不可上机；当前board/defconfig为未完成集成，不是放行配置。首阻塞、证据与预先判读见[24r记录](docs/ufs-24r-diagnostic.md)。不改基座/pin/共享仓，不触旧claim/23r/22r，等级不升；下一步先只读确定真实配置路径，最终审查/验证及当轮设备授权仍须完成。下方是此前检查点。

**最新：方案D fix2 archive/host范围完成，self-checked，待独立verifier+deep增量审。** 经主控窄许可，同一默认0开关`NATIVE_UFS_EXTERNAL_STORE_PROVIDER`条件编译六个store导出及其专用helper/state，保留RamBlock空后端和共享log/geometry，无target禁警告或transport函数体修改。最终源码四archive实际重编通过（不复用archive）；默认仍87个globals/六store，external为81个/零store，与RamBlock合并的全强符号扫描无重复。真实空后端+RamBlock guard矩阵每诊断设置64组合，633/639原诊断用例同时重跑通过；guard54/624复用未变证据。默认对象差异已精确定位为45处panic源行号MOV和DWARF路径/坐标，不误称仅ar mtime；新实测hash与完整patch `91500f6c…4cdee4d`、旧失败历史见[实现记录](docs/ufs-reuse-diagnostic-implementation.md)。未改RamBlock/archive、活动board/defconfig/DTS、基座/pin；无24r链接/候选/入口或设备操作。候选阶段最终native/prelink/map唯一性仍须另验。

**实际UFS接管仍硬阻塞：INSUFFICIENT EVIDENCE（主控转述一次公开来源核对）。** HCE/doorbell/RSR为0不能据此释放旧页。三项缺口及固定来源见 [短阻塞表](docs/ufs-resource-evidence.md#takeover-hard-stop-insufficient-ownership-evidence-2026-11-11)：唯一提交所有权、完整DMA完成定义、旧资源保留/失败恢复责任。新授权只允许上方默认关闭的观察形态诊断，不改变这些接管硬条件；须可引用契约及适用deep，不靠OBSERVED结果授权接管。未联系维护者/发issue。

**2026-11-11 UFS组件离线交付（独立验证PASS，主控转述；未集成）**：固定 `e2b32cc429e8cf1501161c1d8c517f8994ceb9b2` 上的最终patch `819a4be3…86f1f66` 已在git archive隔离树apply0，5文件逐字节匹配工作树；54场景/624抽取模型拒绝零硬件计数、target archive/exports、nonPIE SmmuTakeover/RootCommands及record/diff独立PASS，TransferPoll复用未变通过。两份492600B archive仅8字节ar mtime不同、成员内容相同；verifier复用构建目录，**不是fresh/clean rebuild可复现性证明**。patch可离线交付，尚未提交/发布/集成；SM8250-AC执行仍拒绝，无prelink/runtime验证。[UFS记录](docs/ufs-resource-evidence.md#component-platform-admission-2026-11-11)列完整hash/路径。Android已恢复、用户在用；无可上机候选。下一实际接管须先闭合并深审所有权，不改活动pin。旧host身份核心/QR代码及自检保留暂停，未接线、无菜单候选，非主线前置。

**主线停在UFS所有权契约，不重验PMGR/启动/显示。** 可选身份工具host分支已保存暂停：注入式C核心13 sanitizer场景、snapshot v2完整性parser23测试、分页模型5测试均为此前self-checked；无DXE/BootServices/GOP接线或候选。组件guard离线交付已完成，活动pin/feeds不动，不继续身份/QR支线。历史音量/电源/Tools/QR已有实机证据可复用，A→B仅enuma DSC新增DebugLevel4、DTB相同的reviewer比对不等模块逐字节同；不增菜单独立里程碑。

**历史离线资源检查点（self-checked，非当前待办）**：身份快照schema/parser此前19测试及示例解析exit0，实例全synthetic，真实UEFI身份仍UNKNOWN；另固定DALSys/HALIOMMU双hash闭合“SMMU/IORT”私有属性两条UFS raw记录，6测试及审核exit0，不称标准系统ACPI IORT已安装/运行已选库或SID/context独占。见 [UFS格式/资源摘要](docs/ufs-resource-evidence.md)。不据此继续采集方案/输出通道工具、hook/候选或启用UFS；当前以上方三项契约硬阻塞为准。Android使用不受影响。

**UFSDxe/HALIOMMU静态证据（前一检查点self-checked）**：本板HALIOMMU安装/共享接口表及资源匹配算法已绑定；共享表不等0x38字节软件ctx，更不等硬件bank独占。其外部属性接口现由上方DALSys增量静态闭合，不再是未知provider。UTRL/UTMRL、SID/context独占、PA/IOVA/coherence/超时缓冲及真实UEFI-LUN仍UNKNOWN。前轮4项provider测试及旧12测试保留，不盲重跑；23r限定推论不变。

**UFS离线输入证据（2026-11-11，self-checked）**：新增 `scripts/check-enuma-ufs-evidence.py`，使用现有dtc/PyYAML解析本板DT/共享DTSI、固件配置与原始GPT，输出ignored `.cache/ufs-evidence/report.json`。已核对4096B块、userdata 2686976–61880314 inclusive；资源长度/页映射、SPI/INTID及provider ID/offset分别记录。纯主机校验，不启用ShengUfs、不配置写窗口、不动设备，Android保留、存储等级不变；SID/所有权/一致性/PA-IOVA-LUN及未来根UUID仍UNKNOWN。命令与脱敏证据见 [UFS摘要](docs/ufs-resource-evidence.md)。

**最新23r观察（2026-11-10，self-checked媒体整理；reviewer结论单列）**：单次boot0绑定下，照片可见launchd Early boot complete/Continuing system boot、restored_external pid3/running/Successfully spawned及NVRAM/registry/cache/ENOENT/ESRCH日志。用户“**一直停在这里**”，未报告后续panic/复位，时长不详；不判hang或稳定活性。顶部裁切未直接见stage23；reviewer据同步hook先于用户启动、唯一pmgr2及成功返回条件，推导“**mode2 publisher检查完成并返回——控制流推导；stage23文本未直接观察**”，非AMFI全部路径或完整runtime通过（22r亦曾PID3后panic）。照片ignored `.cache/media/stage7-pmgr-23r-20261110/微信图片_20261110232546_369_25.jpg`，SHA256 `065a6fec43aa856e71ab201cb7eeb3811cd842c5981306a8ed336b28a490145d`。该目录无早期完整录像；详见 [23r记录及源码引用](docs/pmgr-23r-diagnostic.md)。RAM-root为restore ramdisk，不含完整GUI；未建立UART/USB日志通道，不自动查询设备或重启取证。下一主机动作：只读UFS资源/接口证据准备，不启用驱动、不刷userdata，保留Android，不升完成等级。

**23r执行前准备快照（历史self-checked，实际执行/观察以上方为准）**：冻结prelink `bf9f7e12bb05dc3a09f1a732fbcdb83d7729f6378f65ea7fbe77646514edc072` 的PMGR静态deep、observer人工及完整包装独立PASS，主机工具门禁PASS。deep许可有限诊断，mode1/3/fault仍未验证；mode2 stage23及后续AMFI是目标，不是已有结果。`stage=3`不是`stage=23`，stage23仅publisher自检。入口本轮已授权使用一次，不可重放；未改冻结manifest历史release_allowed=false或自动audit JSON。

QEMU9.2工具已就绪，但原mode1在hook前AppleImage4异常、16字段全0；fixture后续两次平台拒绝无执行结果，保留原证据且不继续/绕过。当前任务仅正常文档与离线入口准备，不将QEMU前置失败或包装PASS扩为runtime/实机/显示验收。

**此前主机适配检查点（历史self-checked，后续结论以上方23r记录为准）**：受guard的原版ApplePMGRNub publisher已完成实际Linux archive/native/prelink构建、340槽指针/205导入符号存在性/hook/late-init静态检查；唯一 `pmgr=2`，原22r观察器保留并重定位。205符号存在性不是完整绑定证明；必要生命周期thunk由deep另行回读。构建阶段证据见 [PMGR主机检查点](docs/pmgr-host-gate.md)，不代表硬件电源功能或阶段验收。

**最新实机记录（2026-11-10，22r，self-checked记录）**：用户报告内核 panic；用户人眼和 terra 对新近照均清晰确认 `AMFI: No PMGR? @ConfigurationSettings.cpp:235`，caller 为 `0xfffffff004ac9420`，无需再拍同样近照。可见 launchd 的 `xpcproxy spawned pid3`、`Successfully spawned restored_external[3] because speculative`、`service running`；新图另见两组 persona type 6 缺失 errno 3、PID3 请求 logd/notification_center/system.logger 的 lookup error 3，仅记可见先后，不作因果结论。这不独立确认完整 exec/syscall 健康，也不证明 panic 的进程为 PID3。PID1 观察器文本未见；`Flushed74` 是 launchd 日志，不是观察器计数。等待 reviewer 最终分析，本任务未定位实现。

用户授权移动的照片现位于 ignored `.cache/media/stage7-pid1-22r-20261110/微信图片_20261110202502_367_25.jpg`，SHA256 `a534193b5dc75e42de300d8c5a9cc378297c21fb04d0c611cf05a57db9c9fa27`；移动前后 hash 一致，保留原名。新近照已在同目录 `微信图片_20261110203216_368_25.jpg`，未移动，SHA256 `887fc1dcc12cc7b3514a7d23272081034eded3be56ba73115fcd86cad6b017d0`。与22r实际执行JSON/已消耗claim的绑定及边界见 [运行态记录](docs/runtime-summary-gate.md)。近照确认已完成，不再要求同样照片；不得为取证再次 boot，不重放任何 claim。

**此前诊断快照（2026-11-10，feat/step10-ramblock-probe，self-checked）**：用户观察
19r 三条色带后自动回 fastboot，证明到达 `_load_init_program` 调用前，不证明 exec；
continue 后 Android `boot_completed=1`、pstore 空。20r 未测回退已取消。
此前候选 `21r-before-first-user-svc`：在 `_sleh_synchronous` 内首个
`_current_cached_proc_cred_update` 直接调用前立即复位；阳性仅证明正常异常
入口下 EL0 执行非 platform SVC，不证明 PID/launchd main/syscall 完成或稳定用户态。
本轮 21r 已获当轮授权单次上机：定向 ADB 重启、同设备 fastboot 身份查询、
既有入口及唯一 boot 均 exit 0；用户口述“三色带后立刻复位”，无新增录像，
不另称已确认回到 fastboot。固定 boot 为 203505664 B，SHA256
`1b2f68ad5febafe60cc7575588812373f7319cfe4608f611a366e9cbacb67e3e`。
候选绑定与既有静态判读支持上述 EL0 非 platform SVC 证据，boot exit 0 本身不证明执行。
脱敏记录：ignored `.cache/cp21r-20261110-android-current-result.json`；
产物在本地 `UniXNU/out/enuma/stage6-ramblock-probe/`。
UUID/ABI/内存/参数不变，board.toml 保持无探针配置；未变 FAT 等沿用 19r 基线。
完整哈希、命令、源码路径与 ABI/trust 假设见 [主机构建记录](docs/ramblock-host-build.md)。
claim 已消耗，禁止删除/重放；设备动作全部停止，未 flash/continue/恢复 Android。
运行态 PID1 摘要 **22r-pid1-runtime-summary 主机候选交付门禁完成，已当轮授权单次 boot 后报告 panic**：deep 五项人工审核 PASS WITH CONDITIONS、verifier 机械/退出码及最终包装检查 PASS 的范围仍仅为绑定主机产物，见 [证据](docs/runtime-summary-gate.md)。自动 audit 仍为 manual-review-required/child exit 2，人工结论另存，不改写 JSON。boot SHA256 `fe9d2bcfa49270d17a20a0e70effbf2e2ad71a599a29f8b751c718dd02afada8`（203505664 B）；包内 kernel 精确匹配已审 prelink `48da5181…cb4d`。新22r入口及唯一boot均返回0，22r claim已消耗且禁止重放；boot返回0本身不证明运行成功，实机现象以上述用户/terra记录为准。
本批记录基于 HEAD `7772f75fef46bfeeff899db25554f555ee27670c` 的未提交工作树；
21r 口述实机现象未独立影像核验；22r 已实机报告 panic，照片有上述 launchd/restored_external 可见日志，但不证明完整 exec/syscall 健康或稳定用户态。不提升区域等级或宣布阶段 7 验收。

Xiaomi Pad 5 Pro 5G（enuma，SM8250-AC / 骁龙 870）的 UniXNU 设备仓。目标：iPadOS 17.7.11 / 21H461，donor 身份 iPad7,1（J120AP）。

**当前阶段**：官方 `porting/steps` 第 5 步**已完成**（固件可构建 + 设备仓 preflight）；第 7 步 bring-up 阶段 1–2 已实机到达 UniXNU 内置菜单。**里程碑（2026-11-08，用户当轮授权并录像）**：`fastboot boot` `stage12-simplefb/boot.img`（sha256 `ef782289…6dca`，固件源码 `1070b371`）走完 SEC→DXE→BDS→UniXNU 菜单（音量键移动、电源键确认、Tools→Advanced Logger 二维码轮播可用）；ramoops 日志通道（`0xB0000000`/4 MiB）读回固件日志，判读见 `docs/firmware-log-capture.md`；日志与视频留本地 `.cache/media`（不入库）。原厂 `vendor_boot_a.img` 的 4 个 DTB 候选与 pre-root 实机 FDT 已按字节取证并记录哈希（`scripts/enuma_firmware_inputs.py`，来源见 `proprietary-files.txt`）：vendor_boot 只有 SoC 基座 DTB（board-id `0x00`），enuma 板级 DTB 由 dtbo_a entry 07（board-id `0x2e`）叠加得 `.cache/firmware/dtb/sm8250-xiaomi-enuma.dtb`（候选 DTB 已被 ABL 接受，但内容未核）。`uefi-enuma` 已按 enuma 实机 XBL 的扁平厂商模块路径接入，`[uefi_fd]` 0x9FC00000/0x300000；厂商 `Binaries/enuma` 与板级 DTB 仍走 `.cache/firmware/`（不入库）。2026-11-08 修复并已做 reviewer 审查（Sol，INSUFFICIENT EVIDENCE→修复→待复核）：复位槽位改回通用 ResetSystemRuntimeDxe、`EnableUfsIOC` 与 enuma cfg 一致；「写入分级」规则已修订（允许厂商固件正常启动的附带写入，不偏离 stock）。

**里程碑（2026-11-09，用户当轮授权并录像）**：bring-up 阶段 3 首次上机通过——`fastboot boot` `out/enuma/stage3/boot.img`（sha256 `141eaa7e…b7bb`，203505664 B，header v1，ramdisk=192 MiB FAT payload，固件源码 `1070b371`）返回 OKAY（推送 4.5 s，未刷任何分区）；ramoops 读回 `UNIXNURAMDISK: device tree at 0xA3DFE000`（980302 B）与 `UNIXNURAMDISK: initrd block device 0xA3FFF000 size 0xC000000 Success`，随后 `[Bds]Booting UniXNU` → UniXNU.efi 加载 → FAT 挂载，无 `no initrd in /chosen`、无 ASSERT、无 NO WINDOW（SPSS/SMBIOS 的 start failed 为已知无害项）。屏幕：菜单出现，**默认项 UniXNU 倒计时 3 s 走完后调用 DarwinBoot，占位内核（32 B）预期 Load Error**（无内核交接）；Tools 项因显示尺寸不可见但可选中，Advanced Logger 导出可用。ABL 已确认把 initrd 写入 `/chosen`（此前未证实项）；ramdisk 实际范围 0xA3FFF000–0xAFFFF000 整块在 Kernel 预留区 0xA0000000/0x10000000 内，与固件 FD(0x9FC00000+0x300000)、DXE Heap2(0x93200000) 无重叠、距 ramoops(0xB0000000) 4 KiB；这 192 MiB 占去 256 MiB Kernel 预留区大部分，阶段 4 DarwinBoot 窗口/`owned_memory_size` 须据此重估（待阶段 4 实机）。证据细节见 `porting.toml`（packaging/firmware/memory/configuration 四区 device 证据）。

**里程碑（2026-11-09，用户当轮授权并录像）**：bring-up 阶段 4（DarwinBoot 交接）首次上机通过——`fastboot boot` `out/enuma/stage4-log/boot.img`（sha256 `056a095f…1ac`，203505664 B，header v1，ramdisk=192 MiB FAT payload，真内核 kernel.macho sha256 `39cecb2e…ac26`/payload.img `4e601ff7…a6bd`；固件源码 `4db39e8f`（`fix/unixnu-debug-level`，PcdUniXNUDebugLevel=0x4），新 FD sha256 `e524988b…bf1e`）返回 OKAY（未刷任何分区）。ramoops 读回（console-ramoops-0.txt，15732 B/279 行）首次出现 8 行 `UNIXNU:`（上轮为 0，证明 debug-level 改动实机有效）与 `DARWINBOOT:` 交接块：`UNIXNU: menu: timeout, booting default 0` → `UNIXNU: boot: entry 'xnu' (UniXNU)` → `DARWINBOOT: hand-off to the kernel`，kernel va 0xFFFFFFF00427C000 pa 0xC007C000、entry pa 0xC321A488（entry words 140006F5）、args pa 0xC40B0000 window 0x20000000 bytes、video base 0x9C000000 1600x2560 row 6400 32 bpp、CurrentEL 1 SCTLR_EL1 0xC0180D、`Exiting boot services`（顶端绿条）。无 NO WINDOW/BIG RUN。屏幕：倒计时后顶端绿条，无蓝/品红条（本镜像未装入口探针）；boot services 已退出无法回 AL（预期），长按电源键手动回 fastboot，pstore 保留。**结论边界**：证明 DarwinBoot 加载内核、分配约 512 MiB 窗口（约 0xC0000000 起，在 0xBBB00000–0xC0000000 空洞之上）、ExitBootServices、绘制绿条；**不证明** XNU 入口指令已执行/MMU 已开（需入口探针，阶段 5）。DARWINBOOT 的 Print 输出会进 ramoops（此前误判为只走 ConOut）。证据细节见 `porting.toml`（firmware/packaging/memory/configuration 四区 device 证据）。

**阶段 5 入口探针（2026-11-09 上机通过，用户授权并录像；录像未拍到复位）**：`fastboot boot` `out/enuma/stage5-probe/boot.img`（sha256 `5ee53cb0…`，`entry_probe_reset_delay=6` 无 panic_screen）返回 OKAY（未刷分区）；屏幕依次出现绿条→蓝条→品红条，约 6 s 后自动复位回 fastboot（品红条后明显 <20 s，非 ~20 s 看门狗），Android 内 bootreason=bootloader——证明 DarwinBoot 交接、XNU 入口指令执行（MMU 关）、到达开 MMU 前、MMU 开启后 6 s 复位；**不证明** `_arm_init` 之后的执行。本次 pstore 无 console-ramoops-0（dmesg 显示 ramoops 仍正常 attached 0xb0000000/4 MiB，阶段 3/4 有），假设 XNU 运行占用/清零了 0xB0000000 或复位路径未保留 RAM（待验证；后续二分自动复位同样无、手动长按回来则有，更可能 PSCI 复位路径不保留该日志）。**阶段 5 二分结果（2026-11-09，用户观察）**：入口探针 16 个检查点（`docs/entry-probe-bisect.md`）从入口一路通过到 `_bsd_init` 内 `_IOFindBSDRoot`（before 探针 15 复位、16 `_vfs_mountroot` 卡住不复位），推断内核停在 IOKit 等根设备处（无存储驱动的预期终点，非直接证据）；等根设备之前内核侧无阻塞，阶段 6 存储/根卷未开始。**下一步**：阶段 6 存储/根卷（ShengUfs + userdata 根，需 `[userdata]` LBA 实测与当轮授权）。

2026-11-08 恢复厂商模块：此前误判为「enuma XBL 无」的 19 个模块（SdccDxe/FeatureEnablerDxe/PILProxyDxe/PILDxe/SPSSDxe/AdcDxe/UsbPwrCtrlDxe/QcomChargerDxeLA/ChargerExDxe/UsbfnDwc3Dxe/XhciPciEmulation/XhciDxe/UsbMsdDxe/UsbDeviceDxe/UsbConfigDxe/UsbInitDxe/ButtonsDxe/TsensDxe/LimitsDxe）实为 enuma 自己 xbl_a 内原件（xbl_a sha256 `7ac67cbf…565057`），只是 `extract_enuma_xbl.py` 的 SELECT 白名单遗漏；已按原件导入恢复，厂商模块总数 52（含 ButtonsDxe 音量/电源键与完整 USB/SDCC/充电栈）。构建通过（FD=3145728 B，self-checked，仅 compiles，无设备证据）；ButtonsDxe 的 DEPEX 能否满足须实机观察。

## 三仓关系

| 仓 | 作用 | 位置 |
| --- | --- | --- |
| `UniXNU-enuma`（本仓） | 板级连接、组件选择、镜像与分区策略、记录 | 本目录 |
| `UniXNU-sm8250-common` | kona（SM8250/SM8250-AC）共享资源、DTSI、SoC 配置与补丁 | `../UniXNU-sm8250-common`（`FFT-infra/UniXNU-sm8250-common` 的检出：origin 为本仓 fork，upstream 指 FFT-infra；`feeds.toml` 钉 `166235ec…`，alioth 实机用的是 `a6e7e36c…`） |
| `uefi-enuma` | Mu-Silicium 固件（`enumaPkg` + `Resources/Configs/enuma.toml`，已可构建；厂商 `Binaries/enuma` 与板级 DTB 走 `.cache/firmware/` 不入库） | `../uefi-enuma` |
| `UniXNU`（基座） | 解析器、package、DarwinBoot、组件 | `../../UniXNU` |

注意：官方设备索引把 enuma 归档为 `SM8250`（系列名），本仓一律写 `SM8250-AC`。alioth（Redmi K40）同为 SM8250-AC（骁龙 870，非 865），其板级 CPU/GPU 频率票不移植到 enuma。

## 前置条件

- 基座检出：`D:/Code/PortingiOS/UniXNU`（`[package] unixnu` 指向它）。
- Python 3.11+、git、`dtc`、`mtools`；内核与 payload 在 Linux/WSL 构建（`scripts/linux/setup-toolchain.py`）。
- `uefi-enuma` 的 `Platforms/Xiaomi/enumaPkg` 与 `Resources/Configs/enuma.toml`（派生自同 SoC 的 pipaPkg）已按 enuma 实机 XBL 接入并可构建；厂商 `Binaries/enuma` 与板级 DTB 走 `.cache/firmware/`（不入库），`[uefi_fd]` 0x9FC00000/0x300000；`scripts/enuma_firmware_preflight.py` 在构建前检查这些输入。
- `scripts/enuma_firmware_inputs.py`（WSL Python 3.11 + `dtc`）用于从只读备份按需单文件取用、校验哈希并把 `vendor_boot` v3 的 DTB 候选做结构化边界解析；原始镜像只留在 Git 忽略的 `.cache/firmware/`，不入库。

## 固件输入取证与第 6 步候选（预备，未选择任何组件）

`scripts/enuma_firmware_inputs.py` 已从备份（`backup-manifest-2026-11-06.md` §E）单文件取用并校验：

- `vendor_boot_a.img`：header v3，page 4096、ramdisk 2230、dtb 1613832 @ offset 8192；结构化边界解析得 **4 个 DTB**（kona v1/v2/v2.1 SoC 基座，msm-id `0x164` 子类型 `0x10000/0x20000/0x20001`，board-id 全 `0x00`；外加 1 个 173 字节 MP_DATA），全部通过 `dtc` 校验。
- `fdt.stdout`（pre-root 实机 FDT）：model `xiaomi enuma`、msm-id `0x164/0x20001`、board-id `0x2e`，与 kona v2.1 基座 msm-id 一致。**board-id `0x2e` 不在任何 vendor_boot 候选内**，故板级 DTB 须来自运行时 overlay（实机 FDT）或板级 DTS，不能直接选用 vendor_boot 内任一 DTB。

按官方 step 6 依赖序的候选矩阵（`board.toml [components] include` 仍只有基线 5 项，未选择任何驱动）：

| 依赖序 | 区域 | 候选方向 | 阻塞输入 |
| --- | --- | --- | --- |
| 1 | 平台与内存 | SoC 共享层 + 板级内存/保留区 | 实测 UEFI 内存图 / `[payload] dram_size` |
| 2 | 存储 | ShengUfs | UFS 寄存器/时钟/SMMU、GPT 几何 |
| 3 | 显示与亮度 | GopFramebuffer | 面板/背光/DSI 证据 |
| 4 | 输入 | ShengHidInput / ShengNovatekTouch | 触控/按键证据 |
| 5 | GPU | Adreno A650（SoC 共享 A650 GMU kit） | enuma GPU OPP/电源票 |
| 6 | Wi-Fi | 待定（enuma 为 QCA6390） | Wi-Fi 寄存器/固件 |
| 7 | DSP/音频/电源 | 待定 | 电源票/热区 |

以上仅记录候选，未改 `[components]`、未选择任何新组件。

## 阶段 3 就绪度分析（kernel/package/payload）

第 7 步 bring-up 阶段 3 首次需要的输入（逐项，缺一不可）：

| 位置 | 内容 | 现状 |
| --- | --- | --- |
| OS profile 补丁 | `ipados-17.7.11-21H461` 的 `patches/xnu/series` 补丁与 TODO（`early_security_init`、`text_fixups`、`product-id`、`artwork-device-subtype`）清点 | 待读 `UniXNU/docs/zh/building` 与 `concepts/payload` 后清点 |
| `[payload] dram_size` | 实机 `/memory` 或 SMEM 取证（RamManagerDxe 映射 `0x80000000-0x280000000` = 8 GiB；已写入 `0x200000000`，2026-11-09 阶段 3 上机通过 ABL 启动，但该单段 span 非连续可分配内存证明） | 已写入，阶段 3 上机通过 |
| `[payload] kernel_args` | `native-ufs-root=1`（路线 B，见 `../../docs/launch-route-2026-11-06.md` §4） | 未加 |
| `[userdata]` 几何 | `first_lba`/`last_lba`/`lba_bytes`（本机 GPT 的 userdata 条目；已有只读取证值，未写入 board.toml） | 未写入 |
| `[payload.adt] root_match_volume_uuid` | 构建 userdata 后取到的 APFS 卷 UUID | 占位 |
| 存储 ABI | 所选 kernelcache + `storage-abi/interface-audit.json` | 未准备 |

以上为第 7 步起的第一批输入清单；`[userdata]` 刷写与持久化验证仍在 bring-up 前五阶段之后（路线 B，须用户当轮授权）。

## 构建

在基座检出目录执行：

```sh
./unixnu defconfig enuma_defconfig -D ../enuma/UniXNU-enuma
./unixnu fetch -D ../enuma/UniXNU-enuma
./unixnu status --json -D ../enuma/UniXNU-enuma
./unixnu tree -D ../enuma/UniXNU-enuma
```

仅在开发共享层的本地改动时，在本仓 `local.toml` 写入（常规构建使用 feeds/lock 的远端 pin）：

```toml
[[source]]
kind = "soc"
name = "sm8250"
local = "../UniXNU-sm8250-common"
```

或使用设备打包脚本：

```sh
scripts/package.sh --check --os ipados-17.7.11-21H461
scripts/package.sh --os ipados-17.7.11-21H461 --uefi ../uefi-enuma
```

## 记录

`porting.toml` 是唯一权威记录（14 个区域）。改动代码后同步对应区域的 findings/evidence，并运行：

```sh
cd ../../UniXNU
python3 scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step3-format2
```

## 文档

- 固件日志抓取（ramoops）：[`docs/firmware-log-capture.md`](docs/firmware-log-capture.md)
- 移植流程：<https://unixnu.com/zh/porting/steps>
- SoC 支持：<https://unixnu.com/zh/porting/soc-support>
- 设备仓规范：<https://unixnu.com/zh/porting/device-repository>
- 设备树：<https://unixnu.com/zh/porting/device-tree>
- 启动验证：<https://unixnu.com/zh/porting/bring-up>

## 约定

治理规则见 `../../docs/governance-2026-11-06.md`（12 条）。Apple 派生产物只留本地 `out/`，不上传 GitHub；ECID 等设备种子只经命令行或 Git 忽略的配置传入。`scripts/` 下的历史审计工具产生于 format 1 布局，其中部分引用已不存在的 `firmware/`、`diagnostics/` 目录，接入前先核对。
