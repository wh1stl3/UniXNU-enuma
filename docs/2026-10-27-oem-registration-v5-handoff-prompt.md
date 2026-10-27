> 2026-10-28 00:09 v7本次单次准备：用户明确“v7开始 正在拍摄”，按已说明的本次现场/在场恢复条件和既有恢复安排，仅新v7一次临时boot。即时只读前检enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。未claim/发送；准备文档发布及远端核对后由runner重复即时门禁。精确镜像c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d，trial 61c29945-1399-49eb-8133-d11d465bb6c4。75秒无合格返回先恢复，不自动重试，不flash/erase/改槽；R027冻结，共享主线只读。证据out/oem-far-chain-live-20261028；媒体Media-enuma/OEM-far-chain-v7-20261028-61c29945本地保留。以下旧就绪状态不复用，实际执行/恢复随后更新。

> 2026-10-28当前候选为far-chain-v7，完整镜像和qualification2已完成但未claim/上机。先读STATUS/HANDOFF及operations/2026-10-27-oem-far-chain-v7.md；本文件余下为历史，不能复用任何旧录像就绪或旧未消费状态。

> 2026-10-27已由后续main-entry-v6推进取代当前候选入口。v5已经消费且真实安装返回已确认；最新候选/资格/卡点/边界请先读STATUS、HANDOFF和operations/2026-10-27-oem-main-entry-v6.md。以下为保留的v5交接历史，不能据其未claim/录像状态启动。

# 接续 enuma OEM DisplayDxe：registration-v5 已编出，尚未上机

继续现有成果，不从零重做。首先阅读并遵守以下文件，核对 git status/log 后再行动。

## 工作区与边界

唯一写入根：D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display；实际固件是此目录的 firmware 子模块。
D:/Code/PortingiOS/enuma/UniXNU-enuma 由另一会话维护，本会话只读；独立 uefi-enuma 不是当前源码。不要 reset/clean、切换共享仓、改权限、操作 nuwa 或另开写入者。R027 和旧镜像/资格/媒体保持冻结，不改历史字节。

先读：AGENTS.md、firmware/AGENTS.md、docs/STATUS.md、docs/HANDOFF.md、docs/NEED-REVIEW.md、docs/PENDING-HUMAN.md；随后读 docs/operations/2026-10-27-oem-registration-v5.md、docs/operations/official-development-guide.md 和 official-adaptation-rules.md。旧交接中的“尚未接线/不推送/待确认照片”是历史状态，以新入口为准。

## 最新事实

固件提交 fd94b265d1b0112c4a60d36a058d7b91efbb250d；设备仓功能提交 a68983a、最终资格/文档提交 0dd5db3，后续本次交接提交以 git log 为准。工作树在本次交接前干净。构建为基于 f82039e 的工作树快照，保留 build1/source-manifest.json；不能称提交后重编。

v4 原始 trial f5854414-b040-49ff-9291-3007c5c3f560 和用户明确授权的手机重试 7e4ec36d-755e-440a-8f47-3c98ae38dbdc 均 consumed，不重试。手机两张照片已由助手独立保存完整判读，用户确认两组一致、现场只有这两组：

s1：
E01C0000000000000004
Q0000000000000008
O0000000000003ABC
E
G2DBEF5F2F2DA5EA9

s2：
S02C0000000000000004
Q0000000000000009
O0000000000003ABC
S0000000000000000
G2DBEF5F2F2DA5EA9

这证明 call4 进入并以 EFI_SUCCESS 返回，不证明 SID 或 CoreStartImage 返回。用户明确没有按键，设备自行回 Android；独立核验 enuma、boot_completed=1、root、A 槽、解锁与 boot_a/vendor_boot_a 原摘要通过。此后没有设备操作，当前在线状态未知。

原始照片仅在本地 D:/Code/PortingiOS/enuma/Media-enuma/OEM-v4-phone-retry-20261027-7e4ec36d/s1.jpg、s2.jpg。证据在 out/device-tests/oem-retry-7e4ec36d-755e-440a-8f47-3c98ae38dbdc：phone-independent-read.json、phone-decoded.json、phone-human-confirmation.json、android-return-verification.json。原 runner 仅等 fastboot 的误报和原状态已保留并纠正，不能称该笔超时挂住或人工恢复。

## 代码归因与新版本目的

最大可操作嫌疑是 call4 之后的 guided-section 注册区间，对区间置信中等、唯一指令置信低；S02 取证窗口恢复仍为竞争解释。精确原厂 PE SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425。0x3abc 成功后取分配指针，0x3ba8 尾调 0x411c 复制16字节，0x5cc4 调用 gBS->InstallConfigurationTable，返回地址 0x5cc8；OEM 随后忽略该安装状态并使构造函数返回0。Kernel/HOB/cache 已在此笔到达call4的路径上经过，不能据此反推early-v3窗口清理通过。缺少后续画面不构成确定死锁。

新 scope oem-registration-v5，只在私有 BootServices 中包装来自 0x5cc8 的配置表安装，其他配置表调用原样转发且不记录、不改变原序号；目标保存GUID、转发原始指针及真实状态。call0..4不绘制；E01/S02 为 call5 安装前/返回（RVA必须5cc8），E03/S04 为第一次 SID LocateProtocol 前/后，S05 为真实 CoreStartImage 返回。原厂PE和既有私有SystemTable同步修复保留，ROI(64,96)320×160，每窗8秒，最多五窗40秒。

有E01支持该次通过复制到安装入口，有S02支持安装真实返回；后续无页仍需区分后段代码与出口拒绝。仅E01不能直接判安装内部挂住，因为入口页恢复也可能有影响。全无页不能区分未到目标和出口失败。无独立看门狗或持久崩溃日志。

## 新固件与资格（唯一当前候选）

out/oem-registration-20261027/qualification3/image.img，3153920字节；SHA256 f9bd10078db5b049e7ad0cd050300c872cdcd1d0d975b6ed3065e4b03dac650d。
FD：out/oem-registration-20261027/build1/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd；SHA256 f83b1869f65377ec2b4af4bdc69f1f64f0fcf41a3a296c6ea795a76d3b7fe6d5。
资格：out/oem-registration-20261027/qualification3/qualification.json；SHA256 9b532a16587cec5ce2c96f7085ec5c73aeed2aaec0a06bf23bcb4b7e739e31ed。
trial 4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e，session 15050556181532298825，selected_call=5，oem-control。尚未claim/启动，执行账本应不存在。

完整FD、原厂模块审计、Boot v3封包和解包回读通过。check3/result.json 含 ASan/UBSan 状态机/转发/失败验证和真实Core配置表扩容/通知及两处删除负测；binding1/result.json 含精确PE重定位、错PE拒绝、AArch64板级对象；python-tests.json 为31项WSL测试。最终机器码拒绝32处原运行路径删除、52处同步/选择/注册删除和1处GUID变异。qualification1失败保留，qualification2已通过，清理宿主测试末尾空行后qualification3重新绑定且FD/image字节相同。

新版 scripts/run_oem_runtime_trial.py 已补齐直接返回Android的观察和独立核验；不再用fastboot-only误报判设备挂住。模拟错误Android身份和fastboot残留会拒绝，且始终只boot一次、无flash/erase/改槽。ADB终点不推断人是否按键，仍按现场事实记录。

## 接续动作

先核对文件/摘要、git状态及候选未消费。可在工作区运行下面默认离线入口（不带execute，不触碰设备）：

wsl --cd /mnt/d/Code/PortingiOS/enuma/worktrees/enuma-oem-display /usr/bin/python3 -B scripts/run_oem_runtime_trial.py --qualification out/oem-registration-20261027/qualification3

本次用户要求是落地文档、本地提交和换会话交接，不是启动新试验。用户此前允许推送；固件 fd94b26 推送无进展后中止，固件和设备仓最新提交远端均未确认，不能称已发布。后续如继续发布，先固件后设备仓，显式GitHub URL/分支 oem-progress-20261027，不force、不改main；firmware的origin是本地共享主线，绝不向origin推送。避免无界网络等待拖慢交接。

未来实机沿已有部署授权准备，无需重复申请已授范围；仍须当前文档发布、精确单次绑定、即时 enuma身份/原备份/恢复核验，以及当次手机拍摄和人在场可长按恢复。上一轮录像/在场状态不得沿用。不复活v4，不自动轮测MMU候选或R027，不flash/erase/改槽，不改内存base/size或verified。75秒未回可控终点则停止追加，先恢复并核验；依据AGENTS当轮落文档，然后离线归因。此prompt本身不满足当次拍摄门禁。

先向用户简述实际最大嫌疑与候选区分力，再按其最新指令推进。能独立完成的代码、失败验证、完整构建、机器码和来源绑定同轮做完；任何修改导致旧admission失效时另建资格，不回写旧产物。媒体先独立判读落盘，展示完整字符串供用户核对后再精确归因，禁止按预期补猜。原始影音/二进制/备份/设备标识/out不入Git或云端。

运行环境：Windows PowerShell；构建/运行器用 WSL /usr/bin/python3、clang、llvm-objdump。Windows python是Store占位符；需原生Python时用 C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe，文档显式UTF-8。参照官网规则按依赖推进；上次在线重读官网403，已保存指南仍适用，不声称取得了新网页内容。主线仍可靠取证→OEM真实返回/生产GOP分别验收→DarwinBoot/EBS→XNU；不把临时菜单或自动返回当OEM/GOP/用户态成功。


## 新会话接续增量（2026-10-27 21:55）

设备仓9f98d3e/固件fd94b26起点已核验；默认离线入口及2446项源绑定通过，现成image/FD/qualification摘要和未claim状态匹配，R027冻结摘要只读复核通过。无代码修改、重新构建或设备命令，当前设备状态未知，当次手机拍摄/人在场恢复未确认。

两个GitHub分支有界查询及随后显式固件URL非force补推遇连接失败，发布仍未确认；因先固件后设备仓顺序未继续设备仓推送。下一步网络可达后补齐发布及远端核验，再协调本次现场条件，不复用上一轮就绪。证据out/oem-registration-takeover-20261027；最新状态以STATUS/HANDOFF为准。此为准备条件未齐，未发生设备硬停。


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
