> 2026-10-28当前：gop-mode-v10目标及2/27秒对照已完成完整build1、qualification1和离线来源核验，三trial未消费。本机Clock/HAL ABI核对后未发现可确认的接口错配，保留原始方法，新增真实Core成功及整轮DXE后原厂GOP QueryMode/SetMode/读回检查。55项Python、sanitizer/ARM及224/174/182处链接删除负测通过。v9仅离线对照、不安排上机；旧源码准入已过期但镜像/资格字节冻结。没有本轮设备动作，不沿用旧拍摄/校准。

## 2026-10-28 用户追加的后续分析与新包优先级

按本机三路显示时钟→HAL IOMMU方法链→生产GOP模式/控制台顺序推进分析和新包制作。先核对实际提供者ABI/指令/状态与本机证据；没有确认缺陷时保留原始调用与真实状态，不因公开平台样例而跳过或合成成功。可在真实前置条件的运行门控后独立接通下一段链路，但离线构建不作硬件验收。代码、失败/清理、实际链接机器码、新完整构建与单次来源资格同轮完成；每次上机重新核对当次现场、恢复和适用校准。v9本轮仅离线对照，不安排消费，当前以STATUS/HANDOFF的v10为准。

> 2026-10-28当前：far-clock-v9目标及2/22秒校准镜像已完成完整build4、qualification1和离线来源校验，三trial均未claim/上机。移除诊断晚期GOP/像素出口，保留真实OEM/Core和整轮DXE路径；52项Python与最终机器码删除负测通过。实际时钟校准未完成，目标execute需新low/high报告与精确计划；v8已consumed且恢复通过，不复用旧拍摄就绪。现行STATUS/HANDOFF及operations/2026-10-28-oem-far-clock-v9.md；以下旧当前/准备文字按历史阅读。

> 2026-10-28当前：v8单次已consumed，用户确认自行回Android且未见日志页，00:51独立恢复与原分区/备份核验通过。本轮没有独立媒体判读，不证明Core/DXE/GOP成功。已复现竞态修复未解决本次报告的无页现象，下一重点为末端可观测性/拒绝与提前复位分离；不重试。现行STATUS/HANDOFF，以下准备/未消费文字为历史。

> 2026-10-28 00:47 v8本次单次准备：用户明确“v8上机，正在拍摄，我在场可以恢复”，当前拍摄/在场条件独立记录，不复用v7。即时只读enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，trial a35583f7-e92d-4999-96d2-116793825026，未claim/发送。当前准备提交发布与远端核对后，由原runner重复即时门禁，仅一次临时boot；75秒无合格返回停止追加、先恢复，不flash/erase/改槽。共享主线只读、R027冻结。证据out/oem-far-event-live-20261028；媒体Media-enuma/OEM-far-event-v8-20261028-a35583f7本地保留。v8仅修复已复现的通知竞态，不预写OEM/Core/DXE/GOP/BDS成功；无页仍有异常、返回门、末端显示拒绝等竞争解释。

> 2026-10-28当前：far-event-v8完整镜像和qualification1已完成，修复可复现的RestoreTPL后环尾串位主动复位；仅离线，未claim/上机。v7已consumed且自动回Android，无页不证明Core/DXE/GOP成功。现行STATUS/HANDOFF及operations/2026-10-28-oem-far-event-v8.md；以下旧当前/拍摄就绪均为历史。

> 2026-10-28当前：v7单次已consumed，用户确认自行回Android且FASTBOOT到Mi标未见日志页，独立恢复与原分区/备份核验通过。尚无独立媒体判读，不证明Core/DXE/GOP成功，不重试；现行STATUS/HANDOFF。以下准备/未消费文字为历史。

> 2026-10-28 00:09 v7本次单次准备：用户明确“v7开始 正在拍摄”，按已说明的本次现场/在场恢复条件和既有恢复安排，仅新v7一次临时boot。即时只读前检enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。未claim/发送；准备文档发布及远端核对后由runner重复即时门禁。精确镜像c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d，trial 61c29945-1399-49eb-8133-d11d465bb6c4。75秒无合格返回先恢复，不自动重试，不flash/erase/改槽；R027冻结，共享主线只读。证据out/oem-far-chain-live-20261028；媒体Media-enuma/OEM-far-chain-v7-20261028-61c29945本地保留。以下旧就绪状态不复用，实际执行/恢复随后更新。

# UniXNU-enuma 工作约定

## 官网开发指南（用户持久要求，2026-10-27）

用户追加要求“具体方法也落位规则”：后续必须执行[官网具体适配方法](docs/operations/official-adaptation-rules.md)的对应子系统条目及共用交付要求，包括初始化/ABI/链接、DMA生命周期、超时清理、失败验证和分层验收。按八阶段依赖顺序推进，允许独立离线开发；完成状态必须有对应证据，不能仅引用官网或参考机结果。

用户明确要求“把官网内容作为开发指南，以后按照此内容执行”。后续以 https://unixnu.com/ 的官方移植、构建、驱动适配、启动和日志文档作为默认开发流程；入口、执行方式及本机对照见 [官网开发指南](docs/operations/official-development-guide.md)。开始新子系统或调整方案前，先读对应官网章节，再核对本仓固定版本的实际源码、接口及 enuma 证据。官网更新不自动升级依赖，不直接复制其他设备的地址、容量、ABI、启动参数或刷写命令。

按官方流程组织源码选择、板级/SoC/OS边界、依赖顺序、构建产物和分层验收。每项工作记录来源、实现、宿主验证、设备证据、未完成依赖及下一步；参考设备的完成状态须区分维护者报告和本机实测。发现旧方案与官网不一致时记录差异并修正后续方案，保留历史证据，不默默绕过正式构建/验收条件。

用户明确的工作区、冻结候选、暂不上机、不推送及内存/verified/分区边界继续有效。官网的发布、刷写、自动测试流程本身不构成执行授权；无实机时完成可独立的源码、构建和模拟验证，硬件结论保持未验证。

操作的账号均为**本人持有的合法账号** - 用途：个人探索研究/自动化 / 内容归档（非他人账号、非批量、非反作弊） - 凭证存 .env，不入库不进对话 - 不需要替我加法律免责声明

<!-- path-migration-policy-2026-10-26 -->
## 路径迁移与后续工作约定（2026-10-26）

本机型统一工作根为 `D:/Code/PortingiOS/enuma`；设备仓为 `D:/Code/PortingiOS/enuma/UniXNU-enuma`，迁入的独立固件仓为 `D:/Code/PortingiOS/enuma/uefi-enuma`。本文件所在仓库为 `D:/Code/PortingiOS/enuma/UniXNU-enuma`。

enuma设备仓实际使用的固件源码仍在 `D:/Code/PortingiOS/enuma/UniXNU-enuma/firmware` 子模块；它与迁入的独立 `uefi-enuma` 检出不得当成同一工作树混用。

所有后续工作、新文档、脚本调用示例及交接统一使用上述新路径；nuwa/enuma必须隔离各自工作目录，不跨机型混用。旧资料库现为 `D:/Code/PortingiOSLegacy`。历史证据中的旧路径只用于追溯，不能作为当前操作位置；用[统一迁移索引](../../PATH-MIGRATION.md)定位。保留的2395份历史/绑定/生成记录并未被统一改写，旧验证不自动覆盖迁移后修改的文件。

目标：以 UniXNU 为底座，让小米平板 5 Pro 5G（enuma / SM8250 系列）运行 **iPadOS 17.7.11**。用户于 2026-10-22 选择该版本；不是 nuwa 的 iPhone/iOS16 路线。

## 目录与只读边界

- `D:\Code\PortingiOS\enuma\UniXNU-enuma` 为设备工作仓；用户于 2026-10-22 明确授权新建 `D:\Code\PortingiOS\enuma\uefi-enuma` 固件仓。两仓可写，设备仓 `firmware/` 为固件仓的固定提交子模块，不再重复维护两份板级源码。
- `D:\Code\PortingiOS\nuwa\UniXNU-nuwa` 只读参考，且有其他会话工作；不得改文件、提交或影响其 CI。
- `D:\Code\PortingiOSLegacy`、`D:\Code\PortingiOSWithUniXNU` 及其中上游源码全部只读。
- 上游源码按固定提交和本地路径引用，不整棵复制进设备仓。WSL 路径大小写须保持真实名称。
- 所有工具输出显式指向本仓 `out/`，不得使用上游默认输出目录。`local.toml` 不提交。
- 固件编译实现由 `uefi-enuma/Resources/Scripts/build_enuma_firmware.py` 维护；设备仓同名脚本仅做版本/摘要校验和兼容调用。设备契约、Android boot打包、实机与恢复留在设备仓，不把编译实现复制回来。

## 版本管理（沿用 UniXNU-nuwa）

- 分支 `main`，每个里程碑一个提交，不攒大提交。
- 格式：`[unixnu-enuma][<area>] <一句话结论>`，正文包含 `[Change]`、`[Evidence]`、`[Risk]`。
- area：docs / build / kernel / firmware / loader / device。
- 不提交构建产物、上游源码树、DTB 原件、凭据、设备序列号或超过约 10 MB 的二进制；实测文本证据经敏感信息检查后提交。
- 不强推、不跳过 hooks、不改写已推送历史。远端发布状态与本地提交分开记录。

## 硬停与设备测试门禁（2026-10-23 更新）

用户最新要求：生成镜像无需硬停；刷写后无法监测具体过程 log，或无法回到 Android / fastboot / TWRP 时必须硬停。此规则优先于历史版本的逐次生成/启动审批和暂不操作实机停点，用户已要求按新规则继续主线。

- 生成或重写诊断/固件/启动镜像本身无需确认；正常完成来源、边界、打包与审计检查后继续。
- 在已有授权内进行可恢复的推送/临时启动不逐次询问，但执行前必须确认 enuma 身份、匹配备份、日志/有界可控探针方案和至少一条已核对的 Android/fastboot/TWRP 恢复路径。定时复位、USB枚举、黑屏或仅fastboot发送成功不是具体执行日志。
- 除下一条明确允许的有界可控临时探针外，若拟执行设备动作后的过程日志不可采集，或没有可用恢复路径，必须在动作前写入 docs/NEED-REVIEW.md 并停；执行中日志失联或无法回到上述任一模式时立即停止追加镜像/写入，优先沿既有授权恢复，记录实际状态。不能等刷写后才评估这些条件。
- 用户随后澄清：黑屏和定时复位允许，只要有证据支持能回到可控状态。已具备身份/备份/可控返回证据的有界临时探针，不因黑屏或缺少完整早期日志单独硬停；仍记录可采集的日志、时序、镜像摘要及恢复检查，不能把定时返回当驱动成功。无法监测且无法保证可控返回、实际恢复失败或超出原授权时仍停；未经验证的分区刷写不继承此例外。
- Android、fastboot、TWRP 是可选恢复终点，不要求三者均可用；未测试TWRP不得视为已验证。到fastboot/TWRP只能记录为该恢复终点，不能称Android启动通过；能够正常恢复Android时继续核对sys.boot_completed=1、root与原分区摘要。
- 这不扩大为任意flash/erase/改槽或破坏关键引导链的授权；优先使用已有备份与临时fastboot boot。

以下变更仍先写 docs/NEED-REVIEW.md 后停等确认，每项包含编号、背景、至少两个候选及代价、推荐理由、最小批准范围：

1. 修改任何 bringup-plan.json / board.toml 中内存大小或基址字段（已批准R-001/R-002的精确范围内按原批准执行，不重复询问）；
2. 把任何 *_verified 置为 true；
3. 超出已有授权的分区破坏性操作。

R-002候选清空、ABI或临时启动契约不满足即停、不换地址/扩大/刷分区的批准边界保持。

历史资料中的验证标记只是来源事实，不等于本仓已验证或获得新的执行授权。旧仓单次授权不得重复使用。

## 人工恢复后的持续工作（2026-10-23 最新用户规则）

用户明确要求：“以后遇到人工恢复的情况后 无需硬停 直接开始离线分析 分析后出新软件”。人工恢复并核验通过后，自动继续离线故障分析、修复、测试、构建和审计新候选，不因此结束工作或等待再次催促；此条取代历史交接中把人工恢复后当作整轮停止点的解释。失败后仍立即停止追加设备启动，先恢复和隔离故障，不原样重试失败镜像。新候选实测前仍核对故障隔离依据、设备身份/备份和当时恢复条件。恢复失败时优先恢复，内存字段、verified和破坏性分区规则不变。

## 硬停当轮必须落实交接（2026-10-23用户补充）

每次真正硬停，必须在当轮同步落实文档，尤其是docs/HANDOFF.md和docs/STATUS.md，不得只在聊天中告知或留待下轮。两份文档要明确：触发时间与原因/规则来源、最后候选及摘要、实际设备状态（Android完成/fastboot/TWRP/离线/未知）、已完成与未执行项、恢复动作及核验结果、当前进度、继续所需条件/批准范围和下一步。未知项明确标未知，不能把未执行写为通过。

同时追加WORKLOG/DECISIONS，更新NEED-REVIEW及PENDING-HUMAN；记录证据路径、源码提交与发布状态。恢复或新证据改变停点时，及时更新STATUS和HANDOFF，保留历史过程。受控恢复的谓词拒绝不应虚构为硬停；正常推进也应让交接文件反映当前进度。

## 人工与设备

- 用户于2026-10-25明确要求原始影音不要上传GitHub。拍屏/恢复视频、音频和原始现场图像仅保留本地out/；不得git add -f、上传Release、CI artifact或其他外部位置。公开证据仅经检查的文字/JSON及必要摘要，不包含影音内容。当前OpenCV采集不采音频；若未来确需音频先说明用途，不默认开启。此要求不妨碍本地取证和源码/脱敏文档正常推送。

- 只差本人按键：记 `docs/PENDING-HUMAN.md`，继续独立工作。
- 会改变设备内容且必须人在场：写 `docs/NEED-HUMAN.md` 并停。
- 恢复操作只在已有授权范围内执行，按上述门禁记录Android/fastboot/TWRP实际恢复终点；Android启动通过须确认 `sys.boot_completed=1`。
- 设备动作必须明确选定 enuma，不能把同时连接的 nuwa 当成目标。
- 用户于2026-10-23补充采集偏好：禁绘制、尚无屏幕日志的探针不必持续录像，采用必要的前后截图和主机日志/时序；出现实际屏幕输出、需要判读显示变化或恢复操作时再录像。相机覆盖屏幕右上角电源键，可从清晰可见的动作判断按键；遮挡、拍摄窗口之外或画面不确定时不推断。已有明确录像或用户反馈时不反复询问同一按键事实。

## 交接五件套

- `docs/STATUS.md`：当前唯一真相，每里程碑全文重写，只保留有效结论、下一步和限制。
- `docs/WORKLOG.md`：只追加，时间 · 结论 · 提交号 · 证据路径；新提交号在后一条记录，避免自引用。
- `docs/DECISIONS.md`：D-xxx 决策、来源和证据，不删除，被取代时标记 superseded。
- `docs/NEED-REVIEW.md`：待决项与批准范围，批准后记录 approved。
- `docs/PENDING-HUMAN.md`：仅人的按键/在场待办。
- 长篇分析放 `docs/operations/`；新会话依次读 AGENTS、STATUS、DECISIONS、NEED-REVIEW。

## 证据与驱动复用

- 用户持久规则（2026-10-24）：故障分析必须结合本机具体实测、现有实现及公开资料，主动给出明确、较大胆的主判断和按证据强弱排列的嫌疑，而不是只罗列未知项或泛泛等待。公开实现须核对固定版本、真实行为与本机适用条件；明确区分已证实事实、工作假设及置信程度，列出能推翻主判断的观测，并据此优先实现最有区分力的验证。大胆判断不等于编造事实、放宽成功判据或绕过已有设备/内存/verified/破坏操作门禁；新证据反对原判断时及时修正并落实文档。
- 固定措辞：静态检查通过 < QEMU 执行通过 < 实机通过，三者不能互换。
- 结论必须有命令、文件行号、日志或提交；未知项写未验证/TODO。
- 上游更新先 diff，跟进另开提交。固定仓库、提交、文件哈希、许可和依赖。
- 优先复用真实通用实现及同 SoC 来源，不使用空实现冒充驱动。
- 用户持久规则（2026-10-23）：遇到难解决的问题时，把同 SoC 设备的 UniXNU 或 UEFI 仓库视为解决方案来源之一并加以评估。核对固定提交、真实实现、依赖、板级差异及适用条件后再决定复用；其他设备的参数和实测结论不能直接当作 enuma 的事实或执行授权。
- enuma 不是 elish/nabu/sheng；SM8250 不是 SM8550。MMIO、IRQ、面板、触控、电源、GPU、UFS PHY 和 SMMU 必须逐项核对。
- iPadOS 身份由匹配的 IPSW、BuildIdentity、ADT 产品节点和用户态共同决定。固定版本 sheng 生成器的 `ipad_identity` 同时控制产品节点和安全属性，不能当成独立的 OS 选择器，也不能说它只控制激活；新工具须按自身实现审查。

## 下一次硬停前先落实文档（2026-10-24用户补充）

用户先要求“下一次硬停前落实所有文档”，2026-10-24再次明确“下一轮实机验证之前落实所有文档”。每次新实机动作前，先把当前AGENTS、STATUS、HANDOFF、WORKLOG、DECISIONS、NEED-REVIEW、PENDING-HUMAN和适用的NEED-HUMAN/入口说明对齐并提交推送，不能只承诺以后补。STATUS/HANDOFF只留当前有效状态，历史阶段的“未执行/待恢复”保留于WORKLOG/operations而不叠加为当前结论。真实硬停仍必须当轮补齐原因/模式/候选摘要/恢复/继续条件，恢复后及时更新。此文档门禁不妨碍独立离线分析、测试和构建。

## R-005接手授权（2026-10-24）

本轮用户明确“批准R005”，随后确认“可以在场恢复 注意在合适时使用摄像头”。按NEED-REVIEW的A方案最小范围执行：c73eb6e完整离线资格、精确镜像摘要绑定、同源step12无按键受控返回及即时身份/备份/恢复门禁通过后，仅step13一次临时boot的128x8/500000us保存/白条/恢复/读回实验。像素全过程连续录像，默认只读对照前后截图。用户已批准，不重复申请；审批不跳过门禁，不扩张到重试失败镜像/寄存器写入/新内存/verified/分区操作。后续固件主分支仅文档修订可独立发布，实测保持已资格的c73eb6e固定快照，不把新文档提交冒充已构建源码。

## DSI只读实施与直接实测授权（2026-10-24）

用户随后要求“继续实现DSI时序使能只读探针，完成构建审计并落实所有文档后直接实机验证，我可以在场恢复，按需使用摄像头”。按现有R-004映射内两读计划实现新step14，采用新源码同源step12对照及step14正/互补候选，完整资格和每笔文档提交推送后直接沿既有临时boot门禁验证，不逐笔再申请授权。上述c73eb6e冻结仅针对已消耗的R-005历史实验，不限制新只读源码固定到338db59及后续经审计提交。R-005仍consumed，不继承像素授权；只读采用前后截图和主机日志/时序，出现实际输出/判读变化/恢复动作时录像。恢复及其他内存/verified/破坏性分区边界不变。

用户再次要求“继续实现DSI计数使能和有界计数增量只读探针，进一步核对显示管线是否活动。完成构建审计并落实所有文档后直接实机验证，我可以在场恢复，按需使用摄像头”。本轮f6c59ba step15/16仅在已有R-004映射内读计数前置及FRAME_COUNT，最多12读和一次既有gBS->Stall(100000)，不写使能；同源step14对照及两组正/互补逐笔门禁后执行。拒绝只能称条件不足，进展支持不等于可见显示。用户提及Tlrenhb参考仓后经固定提交只读评估，当前保留已实测Boot v3，不直接采用其v1、内存或分区参数。

用户随后要求“按你的判断继续，取得有效增量证据，我可以在场恢复，按需使用摄像头”。按固定小米52a2f18原生v1 get_status路径实施60f38e9 step17/18：major6硬件/INTF_STATUS bit0门控，计数配置只读并保持稳定，同一活动接口两窗各非回绕递增1..64才支持。最多26读/两次既有Stall，不写计数使能。旧f6c59ba拒绝结论和consumed账本保持，全部审计及逐笔文档推送后直接实测；若无有效进展，继续分离实际状态/计数/路由原因，不放宽成功判据或把目标当结果。原恢复与禁写/内存/verified边界不变。

双窗递增获互补支持后，用户“继续”：实施f0cef6f step19，严格沿历史首个合法描述，按本机FDT六CTL（0x2000..0x2a00）及固定小米非virtual SSPP位表检查CTL/LM staging和所选活动DSI双窗递增，最多241次既有映射内读及两次Stall。这是稳定配置关联，不称完整物理/可见路由；无像素/MMIO写入、新映射或授权扩张。按同源step18对照、step19正/互补逐笔文档提交推送与即时恢复门禁推进，旧实验资格沿历史源锁保存。

## 新摄像头与几何只读推进（2026-10-24）

用户更换摄像头后明确要求“之后需要你自己进行图像旋转”，随后“可以开始实机工作了”。摄像头仅主机采集，保留原图并自行顺时针90度旋转后判读；若以后相机方向改变则按实际画面调整，不能把旋转方向当设备显示方向证据。只读仍必要前后截图，实际输出/判读变化/恢复时录像。

012715b step20沿原R-004映射及首候选staging/所选DSI两窗条件，增加SSPP OUT_SIZE/OUT_XY及所选LM OUT_SIZE三个稳定配置字，只检验源/输出宽高相同、至少128x8、输出矩形完整位于LM配置范围。最多250读/两次既有Stall，禁写/无新映射/内存/verified/分区边界不变，R-005 consumed。同源step19对照与step20正/互补完整资格及逐笔文档提交推送后直接临时boot，不重复申请；复合拒绝不直接称裁剪，通过也不称scaler/decimator、遮挡、fetch或可见路由已证实。

## 保守单源/无dim混合只读推进（2026-10-24）

用户要求“继续推进主线”，沿已授权直接只读实测实施ff3db30 step21：严格保留step20首候选/首关联LM/几何/所选DSI双窗条件；四个staging字仅该非virtual源、编码1..12且无其他/未知/边框字段；11个dim bit16清零，BASE或精确常量FG255/BG0模式；新增LM模式及blend/alpha字每窗复查。最多289读/两次既有Stall，不写像素/MMIO、不新增映射/内存/verified/分区操作，R-005 consumed。通过仅支持保守配置，拒绝不称实际遮挡/透明；逐笔完整资格、文档提交推送和即时身份/备份/恢复后直接临时boot。相机保留原图、自行旋转判读，必要前后截图，真实输出/判读变化/恢复时录像。

## 更主动的六类取证推进（2026-10-24）

用户要求“继续 进度决策稍微大胆一点”。按有来源主判断优先取得能改变实现的证据，避免无定位能力的复合谓词。8fd3e62 step22保留原首候选/关联LM/几何/DSI双窗，<=289次既有映射内读，六类区分严格模式/border-only/其他staging/dim/alpha/继承失败，配置采样完成后以正反编码等待输出。每份最多额外20秒/总等待20.2秒、最多3次既有Stall，Core marker和75秒观察期限不变；正反差值、基线预测和合计20秒均符合限定容差且无按键恢复后才分类，否则未知。等待期间不再读MMIO，不把采样稳定扩张为整个编码时间稳定或可见输出。无像素/MMIO写入、新映射/内存/verified/分区操作，R-005 consumed。完整资格、全部当前文档推送及即时恢复门禁后同源step20/step22正反逐笔直接临时boot；摄像头保留原图、自行旋转判读。

## step22超时恢复后的隔离推进（2026-10-24）

step22正向75秒无自动返回，用户长按恢复Android且独立完成/root/原槽/解锁/原分区摘要通过；反向未执行，两份均冻结，不原样重试。按用户恢复后持续工作规则继续离线并实现c45e52a step23：从已验证step20仅增加本地staging解码，允许已知border bit24，原四字仍稳定复查；完全移除新增dim/alpha/LM模式读取及长编码等待。<=250读/两次既有100ms、原Core2/7秒。此为隔离新候选，不能称已解决step22根因。完成同源对照及正互补构建审计、所有当前文档推送与即时恢复核验后直接临时boot。禁写/内存/verified/R-005 consumed及相机规则不变。

## 接手后的通道校准与证据更正（2026-10-24）

用户要求“按照建议推进顺序和硬停要求进行推进，注意所有的文档落地”，并明确确认本轮“可以在场恢复”。先落实恢复核验、文档/源码与不可变产物资格，再按新计划逐笔常量0/3/0和校准通过后的最小只读样本推进；不从已消耗的R-005/R-007像素试验继承写入授权，R-008仍pending。

旧delay20的显示取数宏未进入C编译选项，不能把其时序当寄存器值；GOP查询detail16是精确marker在CoreStartImage返回后触发；像素路径先Sync/Read再Write，不能从超时直接认定写指令失败。旧因果解释由D-146取代，历史观测保留。

新value transport使用独立source/code/index/shift、每码3秒，常量路径无显示读取/像素/cache访问；通用reset gate只延时复位。主机默认离线检查、每次最多启动一笔，要求源码/全部适用文档提交推送、FD/raw/image/实际编译宏审计绑定。任何失败、模糊解码或中断冻结该计划，不追加设备启动；先恢复核验并当轮更新全部当前文档，然后自动继续独立离线分析。相机规则维持：必要前后截图，真实输出/判读显示/恢复动作时录像，原图保留并自行旋转。

## 当前隔离停点与文档更正（2026-10-24 23:04之后）

用户本轮要求查看最新情况并落实全部文档和提交；本轮只读核验及文档，不执行新候选。zero2超时后已独立核验恢复，旧0/3/0计划仍冻结，不统计性重试同一失败镜像。D-149取代D-148/b54bb2b过强解释：延时响应只是初步支持，公共路径安全、驱动返回挂点、fastboot残留均未定案；目录时间不当boot发出时间。firmware/三份未提交隔离代码不属于已资格74598df；先审查/提交/锁定/重构建和逐笔文档推送再谈实机。全部恢复与像素/内存/verified/分区边界维持。

## R-016：当前A单笔实机授权（2026-10-25）

用户本轮明确“批准上机”，对应D-166已构建A/detail15精确镜像29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4的一次临时boot。全部资格/当前文档提交推送及即时身份/备份/恢复和相机门禁通过后执行；不自动执行B、不原样重试、不扩大像素/内存/verified/分区操作。主机先观察fastboot断开再接受返回，记录精确UTC/monotonic时间；超时按既有规则停止追加、恢复、当轮更新文档，恢复核验后继续离线。

R-016执行账本（2026-10-25 02:11，D-168）：A已临时启动一次，回Android并独立核验通过，授权consumed；不重复该镜像、不自动扩展到B。时序支持启动边界但不唯一证明门命中；后续按STATUS和实测记录推进。

## 完整启动链与实际错误优先（2026-10-25最新澄清）

用户原文：“我本来的想法是一次性做到iPadOS 然后分析启动的报错 每次启动解决一些”。今后优先补齐完整输入，使每笔尽量沿完整链到达实际失败点，采集真实错误并每轮修复一批；减少孤立早停，单点探针仅为缺少直接错误时的必要隔离。不是密集绘制或增加录像频率的要求，也不是成功判据/内存/verified/分区/日志恢复门禁豁免。不要拿空ramdisk纯固件镜像当系统试启动；完整链能观测且可恢复后按有效授权推进。优先评估固定同SM8250、同donor的UniXNU-umi真实ADT/RAM载荷/PMGR/UFS实现，先核ABI与板差，不重复已有实现或复制其内存/GPT/显示/触控常量。当前D-170完整链主线取代默认A/B早停优先，B保留离线备用。

用户随后要求“尽量一次验证多个验证点”。同一候选优先顺序检查多个独立可判读节点，保留每项状态与未执行项；前置失败停止依赖读取，不能为了凑验证点越界继续或把整批构建通过当作每项实机通过。D-172的13项RAM运输报告为首个落实：map/FDT/initrd/prefix/BPB/FAT CRC/BlockIO/Connect/SFS及四个文件；可见文本/恢复尚未闭合时先离线推进，不复活已消耗的早停授权。

用户于本轮再次明确“继续 上机无需批准”：新候选在源码/产物资格、当前文档提交推送和即时身份/备份/采集/恢复条件满足后，直接执行可恢复临时boot，不再逐笔申请批准。此为新授权，不把旧R-016或失败镜像重试资格复活；不扩大为flash/erase/改槽、内存字段或verified变更。黑屏且无完整早期日志的单笔整链尝试按既有有界临时探针例外处理：相机与主机连续观察、固定观察期限、已示范的恢复路径；期限内无法判读或恢复失败立即停止追加并优先恢复，同轮更新文档。不能把主机观察期限说成固件自动返回保证。


## 真实GOP后端与双链路证据（2026-10-25）

用户要求继续接入真实GOP后端、闭合双链路，条件满足后直接上机并按结果推进，文档落地/提交推送，原始影音本地。软件/QEMU RAM通过不代替物理GOP；不得清ADDRESS/TOPOLOGY要求发布协议。新只读采样独立绑定源码/实际PE/编译宏/完整FAT/R-004映射和精确镜像，当前文档发布及即时身份/备份/采集/恢复后按既有授权单笔，不逐笔批准；异常/超时停止追加并先恢复。旧失败像素/value计划不复活；内存字段/verified/破坏性分区和媒体本地边界不变。

## 沟通、证据与逆向交付补充（2026-10-25用户授权摘取附件）

- 用简体中文自然、简短地给出判断。少用模板标题、套话和重复背景；不评价用户。必要进度更新只写新发现、实际变化与下一步待解决的问题。
- 讲解代码先说明目的，再按实际执行顺序解释条件、状态和后续影响。区分安排与执行、当前值与快照、单次启动与跨重启状态；图仅在确有帮助时使用。
- 逆向按文件类型/架构、字符串与导入、入口和调用路径、反汇编/动态验证、最小修复与回归推进。优先固定版本的真实上游实现，记录输入摘要、地址/偏移、依赖、许可和适用板差。
- 将已证事实、工作假设和推翻条件分开。实机观测、产物代码、配置、源码与注释各自只证明其能证明的范围；一次响应或返回时序不自动证明某条内部路径命中。
- 提出较强因果判断前检查对照是否同入口、同构造器、同输入、同返回处理。特别检查PASS和FAIL是否在不同位置继续执行；修正过强解释时同步改当前文档并保留原始试验记录。
- 交付可执行的完整实现，包含必要的边界、错误处理、超时和可中断性。输出留本仓out/；CLI及诊断参数显式绑定到输入/产物，不用伪代码或空成功冒充驱动。
- 不因附件中的通用角色、授权宣言或其他场景模板扩大本项目范围。现有设备恢复、内存/verified/分区、提交推送和原始影音本地规则继续适用。


## D-215：原生ramoops审计当前边界

用户支持继续推进路线；当前只完成未接线地址无关writer、只读收集器与主机审计。R-017拟新增console B0000000/2MiB映射及一次44字节留存探针仍pending，不把一般支持或旧R-002/R-008扩张成新地址批准。固件AGENTS的新内存base/size审查规则适用。实际内存表、board.toml/bringup-plan、Null后端和verified保持；明确批准精确A范围后，完成全FD/打包与发布和即时设备门禁，沿既有无需逐笔一般上机批准的授权直接执行。原始影音仅本地。


## R-017 A 本轮直接执行授权

用户在审查单给出精确A范围后明确“上机无需批准 直接进行 注意使用摄像头记录关键节点”。本轮按R-017 A最小console B0000000/2MiB映射、MMU后一次44字节标记和warm/cold回退单笔临时boot实施，不再索要批准。只在显式nonce探针构建启用，pmsg/分区/verified不动。资格、文档提交推送和即时身份/备份/恢复门禁维持；相机记录关键节点，原始影音仅本地。


R-017执行账本（D-217）：S-015已单次发出并超时，用户恢复Android及独立核验通过；writer单笔consumed，不重试原镜像。恢复后按既有规则继续离线map-only/cold隔离，后续新候选须完整资格、发布和即时设备/相机门禁；不扩大console范围或pmsg/分区/verified权限。


D-218：人工恢复独立核验后，沿用户本轮直接上机和隔离推进规则实施同已批准范围的map-only/cold新对照S-016。无console内容读取/写入或warm，原baseline gate保持，不复活R-017 writer单笔；精确新图资格/发布和即时门禁后单笔，相机超时后继续记录恢复，所有影音仅本地。


D-219执行账本：S-016同范围map-only/cold已自动回Android并独立核验，S-016/R-017-MAP单笔consumed。S-015 writer仍consumed，不复活；全部S-001..016不重试。下一步先隔离console最小只读可达性与原cold门，不据返回宣称物理访问/日志/verified通过；所有既有设备门禁和影音本地规则维持。


D-220：用户继续推进最小console头部只读隔离S-017；同B0000000/2MiB、stage10三读+0/4/8及cold，无console写或warm。完整资格/当前文档发布/即时恢复与相机门禁后直接单笔；不重试consumed图，不扩大旧writer范围，影音仅本地。
D-220执行账本：S-017头部三读/cold于20:48:03单次发出并自动回Android，独立完成/root/A槽/解锁/双分区备份摘要通过。S-017/R-017-READ consumed，S-001..017不重试；头部读数未输出，不称写入或留存成功，后续先隔离无console访问的warm路径。原始影音仅本地。


用户随后明确“继续推进 触发硬停再停”：在已批准console范围内继续按故障隔离推进，不因完成单笔就主动停；真实超时/恢复失败/既有门禁仍触发硬停并当轮落实交接。下一笔S-018仅同映射、无console内容访问的warm对照，不写RAM/pmsg/分区或verified，完整资格/发布/即时恢复及相机门禁后直接执行。


D-221执行账本：S-018无console访问warm对照超时触发硬停，用户恢复Android且独立完成/root/A槽/解锁/双分区设备及备份核验通过。R-017-WARM/S-018 consumed，所有S-001..018不重试。用户最新“触发硬停再停”优先于默认恢复后持续工作，本轮完成交接推送后停，不追加构建/上机；后续用户恢复推进再隔离cold写入或warm内部调用，原范围/verified/分区及影音本地边界保持。


D-222：D-221硬停后用户新请求仅参考enuma/elish同型公开仓，本轮授权范围为离线源码研究与交接，不是恢复上机实验。已固定9仓40文件、未新增设备动作或重复21:01:29恢复核验；S-001..018不重试。PON/SPMI/SCM/长按行为及early reader中的pmsg自测不能凭其他机型实现自动执行；后续具体范围按原规则审查，影音仅本地。


D-223：用户要求继续显示侧分析、尽快搞通UEFI；本轮完成离线源审和未接线NativeObserve核心/48项主机与AArch64验证，未新增设备动作。后续独立runtime前缀不能被当作放宽完整GOP准入；实际源/PE/宏/映射/完整载荷及发布/恢复/相机门禁维持。显示交付须相机确认固件自产图案和受控恢复；不复活consumed像素/旧图、不开新映射/verified，影音仅本地。


D-224，独立双路观测完整资格通过，准备S-019：用户本轮“继续推进 触发硬停再停”，恢复同R-004只读显示临时boot推进；独立26读/two100ms观察器不放宽GOP、不继承旧像素批准。完整资格/当前文档发布/即时恢复与相机门禁后直接执行，异常立即停止追加、当轮落实硬停及恢复交接。S-019/S-020尚未发出。先S-019 query1单笔；仅受控返回、独立恢复核验及当前文档再次推送后执行S-020 query2。原始影音仅本地。


D-225，S-019受控返回，准备互补S-020：用户本轮“继续推进 触发硬停再停”，恢复同R-004只读显示临时boot推进；独立26读/two100ms观察器不放宽GOP、不继承旧像素批准。完整资格/当前文档发布/即时恢复与相机门禁后直接执行，异常立即停止追加、当轮落实硬停及恢复交接。S-019 query1已单次发出并受控回Android、独立恢复通过；S-019 consumed。单笔时序不分类，当前文档推送与即时门禁后继续S-020 query2；S-020尚未发出。时序：{"issued_at": "2026-10-25 21:53:31", "issued_at_utc": "2026-10-25T13:53:31.737879+00:00", "boot_command_return_seconds": 2.625, "fastboot_disconnect_observed_seconds": 5.093, "fastboot_return_seconds": null, "adb_return_seconds": 25.422, "boot_complete_seconds": 39.531}。原始影音仅本地。


D-226，独立双路显示观测配对完成，按结果隔离：用户本轮“继续推进 触发硬停再停”，恢复同R-004只读显示临时boot推进；独立26读/two100ms观察器不放宽GOP、不继承旧像素批准。完整资格/当前文档发布/即时恢复与相机门禁后直接执行，异常立即停止追加、当轮落实硬停及恢复交接。S-019/S-020均consumed，均受控返回并独立恢复。配对结果：{"scope": "indirect same-source paired timing, not direct native register log", "conclusion": "ambiguous", "negative_minus_positive_seconds": {"adb_return_seconds": -4.281, "boot_complete_seconds": -1.359}, "predeclared_absolute_delta_window_seconds": [3, 7], "predicate": "collection success AND both active throughout AND both nonzero stable Timing AND both stable Enable AND both two-window Frame increments1..64", "exact_enable3_not_required": true, "complement_includes": ["metadata/PCD rejection", "read/wait/revision rejection", "one or both inactive", "Timing/Enable instability", "one or both nonmoving/wrapped/over64 frames"], "exact_values_observed": false, "gop_verified": false, "pixel_access": false, "limitation": "Android boot noise and inherited state changes across boots remain confounders; complement does not uniquely identify which mask failed"}。后续按实际结果选新候选，不重复本对镜像。原始影音仅本地。


D-227，内核启动时钟常量校准资格通过，准备S-021：用户继续至硬停；S-019/020仅配对未知、无超时，不能虚构已硬停。新常量2/7秒对照及只读boot-origin用于校准，0显示访问/新映射/写入；全部资格/当前文档发布与即时设备相机恢复后单笔。三样本boot-id/区间门禁和预定整个差区间[4,6]秒不满足即冻结新校准并停止追加，当轮落实恢复交接，不重试consumed图。原始影音仅本地。


D-228，S-021已受控返回，准备S-022七秒常量：用户继续至硬停；S-019/020仅配对未知、无超时，不能虚构已硬停。新常量2/7秒对照及只读boot-origin用于校准，0显示访问/新映射/写入；全部资格/当前文档发布与即时设备相机恢复后单笔。三样本boot-id/区间门禁和预定整个差区间[4,6]秒不满足即冻结新校准并停止追加，当轮落实恢复交接，不重试consumed图。原始影音仅本地。


D-229，启动时钟常量校准通过，继续显示隔离：用户继续至硬停；S-019/020仅配对未知、无超时，不能虚构已硬停。新常量2/7秒对照及只读boot-origin用于校准，0显示访问/新映射/写入；全部资格/当前文档发布与即时设备相机恢复后单笔。三样本boot-id/区间门禁和预定整个差区间[4,6]秒不满足即冻结新校准并停止追加，当轮落实恢复交接，不重试consumed图。原始影音仅本地。


D-230，S-023 独立显示掩码资格完成，准备单笔实测：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-231，S-023 独立显示掩码结果与交接：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-232，S-024 独立显示掩码资格完成，准备单笔实测：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


## D-233：预启动fastboot查询异常的恢复继续规则

用户明确“这种情况不需要硬停 只需要重新进入一次fastboot 进入规则 继续”。S-024首次仅进入fastboot、身份查询失败，镜像未发出且未consumed；已fastboot reboot并独立核验Android/原分区。此类预启动故障不作为整轮硬停，允许恢复核验后重新进入一次fastboot，保留完整身份/槽位/解锁/备份/相机门禁，通过才发原未执行图。不得因退出码0忽略FAILED正文，不把此规则扩展为重复已发出图、放宽准入或忽略真实超时/恢复失败。


D-234，S-024 独立显示掩码结果与交接：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-235，S-025 独立显示掩码资格完成，准备单笔实测：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-236，S-025 独立显示掩码结果与交接：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-237，S-026 独立显示掩码资格完成，准备单笔实测：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-238，S-026 独立显示掩码结果与交接：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-239，S-027 独立显示掩码资格完成，准备单笔实测：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-240，S-027 独立显示掩码结果与交接：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-241，S-028 独立显示掩码资格完成，准备单笔实测：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


D-242，S-028 独立显示掩码结果与交接：用户继续至硬停；新mask字段沿原R-004最多26读/two100ms、单独采集错误码；完整GUID返回处五码cold2/7/12/17/22秒，无fallback/写入。资格/实际代码/预定boot-origin窗口/全部当前文档推送与即时恢复相机门禁后单笔；新窗口模糊、采集时基或恢复失败、超时立即停止追加并本轮交接。旧图不重试，原始影音仅本地。


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


## 当前只读探针的摄像头偏好（2026-10-26最新用户规则）

用户明确“目前不需要摄像头，还没到点屏阶段，光看adb和fastboot状态”。当前禁绘制只读native探针使用--no-camera，保留完整镜像资格、即时身份/备份/恢复、ADB/fastboot状态与校准boot-origin分类，不因缺少画面硬停；USB恢复只证明恢复，不能单独当探针成功。实际点屏/画面变化判读或人工恢复需要时再启用相机；原始影音仍只留本地。此条取代前文当前纯探针每次必须相机的执行偏好，其他硬停与文档/提交推送边界不变。


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


## 当前点屏验收目标（2026-10-26用户授权补充）

先UEFI固件日志上屏，随后UniXNU菜单，用于继续固件开发；本阶段不以iPadOS图形界面为验收。按2026-10-26-uefi-console-menu-validation.md独立矩阵逐项记录依赖、已实现未实测、缺失、前置不足未执行。先尽量完成离线格式/范围/stride/覆盖、实际构建绑定、控制台连接、Print/DiagDraw/DEBUG路由及菜单入口审计。一次实机只合并原权限覆盖且结果可区分的低风险检查；五类时间码是首结果，不能声称同时取得多个独立结果。像素写、页表/缓存属性改变、路由切换仍按原门禁；consumed不重试，真正硬停当轮完整落地。纯只读查询继续无相机。


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


## D-285：新会话仅离线DXE日志实现

用户委派唯一接续写入会话，本轮先完成离线实现/验证，不自动继承新设备试验权限。128条Core状态RAM日志及回放接口默认关闭；未接屏幕/全局DEBUG/SEC/ConOut。后续新镜像/像素/寄存器/页表缓存/路由按交接门禁，精确方案具备后再核批准；S-001..047和R-018/R-019 consumed不重试。当前入口docs/HANDOFF.md及docs/operations/2026-10-26-dxe-status-journal.md；原始影音仅本地。

## D-286：用户新实机授权及直接推进

用户本轮明确继续并授权本项目目标内所需实机，随后“无需询问恢复问题 直接做”。不再因旧候选pending或重复询问恢复授权停住；按精确候选资格、scope/预算/摘要、当前文档源码提交推送以及即时enuma身份/备份/恢复/相机门直接执行。不得把授权当实际条件已具备。R-020为新独立缓存真实状态回放范围，不沿用S-001..047/R-018/R-019。硬停后不换包追加试验，按最新75秒/code4/恢复/观测时钟规则恢复和同轮交接。原始影音本地、不录音，无新内存字段/verified/破坏性分区授权扩张。

## D-287：S-048内容可读性观测门禁

S-048/R-020已consumed，自动Android及独立恢复通过，唯一时间码5；相机360帧完整但完整status/ordinal不可独立读清。按本轮用户委派的观测失败/歧义规则停止追加，不虚构时钟失败或恢复失败。当前无需恢复按键；本轮只完成既有媒体记录和交接，不换包重试或继续构建/上机。所有S-001..048不重试。后续先改善内容观测与字形的离线依据，新候选重新锁源/资格/发布/即时门，原始影音本地、verified/内存/分区边界不变。

## D-289：用户明确S048原图一次补拍例外

用户针对“是否覆盖S-001..048禁重试规则，原图仅补拍一次”的精确问题答复“明确授权原镜像仅补拍一次”。仅R-021/S-049可按原图c75b6c863d294d7b3e2772ddb7f46a239c7915685b9c7309f11310049945d8bf、原256x96/2s范围同软件观察复跑一次；S048/R020 consumed记录保持，不扩展其他旧图。独立执行ID和原子一次性claim，默认仍禁重试，不重包绕行。必须我先告知准备完成、用户明确拍摄已开始/就绪后才启动，手机拍屏是新观测安排而非已取得清晰值。其他发布/即时身份备份恢复/75秒/观测硬停/媒体本地规则保持。

## D-290：用户已断开主机相机，使用人手唯一画面通道

用户明确“主机摄像头清晰度不足已断开”，并由自己拍屏。本次R021原图一次补拍使用显式human-camera-only通道，保留主机USB/时钟/恢复门，不开启普通无观测像素模式。第一次因主机相机门前退出没有任何设备命令/claim，已通知暂停；准备发布后须重新取得当前拍摄开始确认，不能突然启动。未收到可读照片/视频之前不能判日志内容通过。

## D-291：S049同图例外已消耗，后续仅实质离线可读性改进

S049/R021已受控Android并独立核验，原S048标记保留。用户反馈虚焦/白字粘连及2秒对焦不足，内容验收失败，停止原图追加。新“重跑”请求不复活R021单次claim；先离线评估仅保持2→8s且面积/读写次数不变的新候选，完整资格后给出具体时长/镜像确认，再协调人手拍摄就绪。当前广泛授权不跨越观测硬停，原始媒体本地及全部既有边界保持。


## D-292：S049观测失败后的实际8秒改进及离线资格

2026-10-26T04:54:45.695706+00:00；前里程碑8aa23b5；固件8680ea79d6fd14d4526d314f430e9812955cb78a。用户2秒对焦不足是本次改变依据。见 [docs/operations/2026-10-26-r022-eight-second-log-observation.md](docs/operations/2026-10-26-r022-eight-second-log-observation.md)；新镜像f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b，R022 pending/计划S050未执行。仅增加6秒，不改面积和I/O；机器码两指令差异、Core相同、模型/Arm/全FD/FAT/Boot v3通过。旧补拍授权不复活，当前观测硬停必须按精确新范围确认后再协调拍摄；75秒/恢复/时钟门禁与所有verified限制保持。


## D-293：实机延后，增加主机格式反读与依赖证据

2026-10-26T05:49:29.611853+00:00；前设备里程碑fafe890，固件仍8680ea7。用户要求晚间才能实机、本轮仅离线；R022 pending不自动启动。新增96组C页面/2359296像素/64bit反读与严格转录测试、6模块链接/源码顺序审计通过，固件/归档/镜像未改。当前页只能含此前已完成point13，不能归为当前provider返回；GUID/sequence未显示。详见operations/2026-10-26-offline-log-readability-and-console-readiness.md；实际值和菜单/ConOut/GOP仍未实测。


## D-298：新路径完整开发构建与冻结 R-022 本地准备

用户最新要求继续至录像前、不自动提交推送。允许独立 out 快照/固定依赖/完整构建与 mock 验证；本轮完整 FD 和 stage10 开发 Boot v3 已生成，仅构建资格，不部署为菜单。R-022 保持原字节、pending/未 claim。新增 --local-preparation 只为精确 R-022 绑定本地 runner 和当前文档，落实不自动提交推送；它不授予硬件权限，不替代精确单次放行、当前拍摄、身份/备份/恢复/时钟门。其他候选的原发布门及 consumed 规则保持。历史备份路径只解析到新 enuma out，不改原证据；R-022 发图前原子 claim，崩溃不得自动复用。下一入口 docs/HANDOFF.md、docs/STATUS.md 与 docs/operations/2026-10-26-development-fd-and-r022-preparation.md。


## D-299：R-022单次放行与录像前预检

用户在已明确R-022单次8秒真实日志计划后表示“可以开始实机”，仅本图f684ef22/S-050放行一次。18:12只读enuma预检通过；待当前录像确认后才执行，未claim/未发图。新媒体仅存D:/Code/PortingiOS/enuma/Media-enuma/S-050-R022，旧媒体不移；不自动提交推送。全部单次/硬停/身份/备份门保持。


## D-300：S-050数值可读、圆角遮挡与停止追加

S-050/R-022已单次执行并consumed，Android62.594秒自动返回与独立恢复通过。用户照片ordinal31/status0/+可读，但圆角遮住左侧页面标识，完整页面未通过；停止追加实机，禁止复用原图。只继续离线布局/日志归因分析；原始媒体保留Media-enuma/S-050-R022且不上传，不自动提交推送。无恢复按键欠项，未批准新候选。


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

最新入口：[DisplayDxe 接续 prompt](docs/2026-10-27-displaydxe-handoff-prompt.md)。追踪可信性证据仍为 trust-check2（7 项测试、320 个模型快照、ASan/UBSan 和 AArch64 对象检查），没有新增原厂驱动执行或固件资格。代码提交不会把历史工作区快照构建变成新提交构建。全部 out、媒体、OEM 二进制、设备标识及备份不入库；本地证据需保留。

提交顺序：实际 firmware 子模块源码及迁移说明，随后设备仓代码/文档/脱敏报告及子模块指针；独立 uefi-enuma 仅提交 AGENTS/README 迁移说明，其 Mu_Basecore 及嵌套依赖既有改动不纳入本轮。提交号由 git log 和最终回复给出，不写自引用哈希。远端未发布。


## 2026-10-27：OEM运行版部署范围

用户“可以部署了”并选择“继续补齐 OEM 运行版后部署”。允许新 OEM control 首调用候选的一次临时 fastboot boot；R027仍冻结，旧stage10样本不上机。最新不推送约束保持，历史实测前推送要求在本次由本地源码/交接提交替代。只写独立enuma-oem-display工作区。

当前已编出运行FD，首调用取证失败不转发；本CPU中断屏蔽和异常早复位仅是有限防护，没有独立看门狗或全局窗口所有权证明。部署前最终软件资格、精确镜像单次绑定、即时设备/备份核验和当前录像/人工恢复准备必须完成。详见docs/operations/2026-10-27-oem-runtime-deployment.md。没有扩大为刷分区、改槽、内存/verified变更或MMU候选自动轮测。

## 2026-10-27：无实机后续系统开发
用户要求继续离线内核启动、用户态和iPadOS桌面开发，并参考已适配设备。允许隔离worktree代码/构建/测试与本地提交，不恢复设备执行；现有OEM候选保留等待，R027冻结，不推送。实际状态见STATUS/HANDOFF及kernel-userland-offline专项。参考设备的已报告阶段与本机证据严格分开，不将公开组件/桌面配置当成完整适配成功。


## 实机前先做代码归因（2026-10-27 用户持久规则）

用户明确要求：“充分分析实际代码，给出最大嫌疑后再继续实机验证。”

- 每次故障后的下一次实机验证前，结合本次精确镜像对应的实际源码、必要的编译后指令、现场证据与恢复记录，先分析执行路径、依赖、追踪器自身影响及失败/清理路径；不能仅凭现象连续试图。
- 先向用户给出当前最大嫌疑及按证据强弱排序的竞争解释，说明具体代码位置、证据、置信程度和能推翻判断的观测。区分“缺陷已复现”“路径可能到达”和“本次实机根因已证实”；证据不足以选出唯一根因时，明确最大可操作嫌疑及不确定性，不强编确定结论。
- 下一候选必须说明它能区分哪些解释、预期观察到什么、失败或没有输出时还能/不能推断什么。优先修复或隔离取证组件自身的已知缺陷，再用独立资格的新候选取证；不重复已消费镜像，不把最后可见事件或缺失返回直接认定为根因或死锁。
- 分析结论与验证范围落入 STATUS/HANDOFF 及对应 operations 记录后，才能进入下一次实机验证准备；离线分析、测试、构建可以继续。此规则不要求先证明唯一根因，也不替代当前单次授权、录像、身份、备份、恢复和硬停门禁，不妨碍已有授权下的紧急恢复。
- 共享或独立工作树须核对最新实际成果；本规则通过受控同步传递，不能擅自改写另一会话正在维护的工作树。


## 2026-10-27 registration-v5换会话：当前边界

用户在先前明确“允许推送”，取代此前离线阶段“不推送”限制；源码/脱敏文档可向既有GitHub分支正常发布，不强推、不改main。原始媒体/out/二进制/备份/设备标识仍不可上传。固件origin指向本地共享主线，不得推送origin，应显式使用GitHub URL。最新远端发布未确认，不把本地提交写成远端成功。

用户本轮仅要求全部文档、本地提交和新会话prompt。现行接续入口docs/2026-10-27-oem-registration-v5-handoff-prompt.md；唯一写入根D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display，其firmware为实际固件源码，共享UniXNU-enuma只读。registration-v5已离线编出、未claim/上机，旧v4两笔consumed且两组日志已确认；R027冻结。既有部署授权不替代新试验当前手机录像/人在场恢复、身份/备份及精确资格门禁。本轮不追加设备或重复构建。


## 补丁换行与构建前检查（2026-10-27 用户持久规则）

用户明确要求：反复发生的“补丁CRLF与目标文件LF不一致”必须记入规则。

- 新建或修改.patch前，先按字节检查补丁与目标文件的LF/CRLF/混合换行，确认目标是源码树、隔离staging还是冻结记录。
- 新建/修改.patch一律显式UTF-8、LF。Windows原生Python不得用默认newline的write_text/open文本写入.patch；使用write_bytes(text.replace('\r\n','\n').encode('utf-8'))，或open(...,encoding='utf-8',newline='\n')。优先使用WSL Python；PowerShell写入也必须明确编码/换行，写后按字节复核。
- 每次完整构建前，先运行scripts/check_changed_patch_eol.py；在隔离staging中按实际顺序执行git apply --check，再应用补丁，换行/上下文失败立即拒绝，不等完整编译后才发现。正式构建原有preflight不能跳过。
- 目标必须统一换行时，只规范当前新源码或一次性staging中的明确文件，并记录原因；禁止批量重写共享主线、原始归档、冻结R027/旧资格/镜像/历史证据或媒体。补丁LF与目标原有CRLF需在隔离副本显式处理，不修改原证据来迁就补丁。
- 保留失败输出，新构建另建out路径；修复后重新做适用的补丁/构建/来源绑定，不能把失败资格标通过。原本受控CRLF的非补丁文件不因本规则一刀切重写。

## 2026-10-28 far-chain-v7当前边界

用户要求重点让启动链走得更远；v7已完成离线镜像/资格，OEM期间RAM-only、真实返回后继续整轮DXE，分派结束一次汇总，仍在BDS前保留恢复出口。精确产物与后续卡点见STATUS/HANDOFF及operations/2026-10-27-oem-far-chain-v7.md。v7未claim/上机，旧v6就绪不沿用；共享主线只读、R027/旧镜像冻结。源码/脱敏文档沿既有显式GitHub URL/oem-progress-20261027发布授权，不推固件origin，不force，不上传out/媒体/二进制/备份/标识。
