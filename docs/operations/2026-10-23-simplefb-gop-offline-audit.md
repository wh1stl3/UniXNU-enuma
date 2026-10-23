# SimpleFb GOP 诊断变体：alioth / elish 离线审计

日期：2026-10-23（Asia/Shanghai）。范围：用户明确要求对照 alioth/elish，优先复用现有实现，记录差异与实机条件，暂不操作实机。

## 结论

推荐以**现有 Mu SimpleFbDxe + FrameBufferBltLib**为主体设计独立诊断变体，不重写 DSI/GPU/面板初始化；前提是 ABL 已留下可持续工作的线性扫描输出。当前只完成离线审计，**不能直接改一个开关就启动**，也没有证据证明 enuma 符合该前提。

本轮未修改固件/驱动、board、内存表或任何验证标记，未构建镜像、运行 CI、调用 ADB/fastboot 或加载模块。最后实机状态仍引用 R-002 的历史记录，本轮没有重新查询设备。默认原生 33 OEM 路线保持；本文件不是启用变体或新增显示内存地址的批准。

新增静态证据：[机器可读审计](../../reports/enuma-simplefb-reuse-audit.json)，含 22 个源码文件的仓库、提交、Git blob、SHA256、行号锚点，以及本机既有报告/FDT摘要。下文 A/M/N/E/S 编号对应报告 source id；源码正文和外仓缓存不复制进 Git。

## 固定来源与复用优先级

| 来源 | 固定版本 | 本次用途与许可 |
| --- | --- | --- |
| 本仓 firmware / wh1stl3/uefi-enuma | b988fa418de55de2dcaa396d016e30231159d1fe；继承 UniXNU/uefi-sheng 329b473d | 首选。直接复用已有 SimpleFb.c/INF、MemoryMapHelperLib、FrameBufferBltLib 及 enuma 保屏补丁。根 LICENSE 为 BSD 两条款；DSC/部分组件明确 BSD-2-Clause-Patent，逐文件保留原版权/许可；SimpleFb C/INF 未单列 SPDX，不自行重标许可 |
| UniXNU/uefi-sheng | 0eb4514db0744b8136a3897ab1af93b713c2c27b | 比对 alioth 的选择方式及 ShengGopLogDxe 的验证方法。A1/A2/M1/M6 与本固件对应文件的 Git blob 相同；不是本轮合并上游或更改 gitlink |
| edk2-porting/edk2-msm | e1952621f419f8db60ed28271264e1b5184c571d | elish/SM8250 的第二实现对照。复用设计和验证思路，优先不移植另一套 PCD/内存库。根 LICENSE 为 BSD 两条款，相关 DSC 为 BSD-2-Clause-Patent；不由这些许可证推断闭源二进制可再分发 |
| 固定 DarwinBoot | 本仓 UniXNU 5fdbd5d 下的已锁定子模块文件 | 复用现有 BootVideo.h 和 EnumaProbe；视频信息可被 loader 接受需要单独验收。具体文件 SHA 在审计报告 |

主源码链接：[Mu SimpleFb](https://github.com/wh1stl3/uefi-enuma/blob/b988fa418de55de2dcaa396d016e30231159d1fe/Silicon/Silicium/SiliciumPkg/Drivers/SimpleFbDxe/SimpleFb.c)、[alioth APRIORI](https://github.com/wh1stl3/uefi-enuma/blob/b988fa418de55de2dcaa396d016e30231159d1fe/Platforms/Xiaomi/aliothPkg/Include/APRIORI.inc)、[elish DSC](https://github.com/edk2-porting/edk2-msm/blob/e1952621f419f8db60ed28271264e1b5184c571d/Platform/Xiaomi/sm8250/elish.dsc)。原厂 PE/DEPEX、K81 XML、内核头、设备标识仍只留 out/。

## 三条路线的具体差异

| 项目 | alioth / Mu | elish / edk2-msm | enuma 当前证据与处理 |
| --- | --- | --- | --- |
| 选择与打包 | A1:26 默认 USE_CUSTOM_DISPLAY_DRIVER=0；A2:54–65 在原生 Display 与 SimpleFb 间选择，并把 CPR 放在原生分支 | E1 引入 SM8250 公共 DSC；E3:133 将 SimpleFb 加入 FV，共用组件表也包含它 | N1:20 原生开关为 1；独立生成的 Vendor DSC/FDF/APRIORI 仍无条件列 Display/CPR。只改开关只会启用 SimpleFb 的编译，不会将其加入本板FV或移除原生打包/调度，仍可能卡住原生驱动；随后只补SimpleFb入卷又会形成双提供者风险 |
| 显示参数 | A1 明确 1080×2400、ColorDepth=32 | E1:20–21 为1600×2560，E2:43 PCD 地址为0x9c000000；E5 固定32位、BGRX、stride=宽 | N2:12–13 只有1600×2560；未给 ColorDepth，M3:26 默认0。不能把另板32位或相同地址当成 enuma 扫描输出事实；未改动的实现可能返回 EFI_UNSUPPORTED |
| 地址取得 | M1:97–98 用 MemoryMapHelperLib 查询 Display Reserved 名称 | E5:167 起取不同命名空间的 PcdMipiFrameBufferAddress | 本机 OEM 的 Display Reserved 起点相同，但它是所有者保留范围，不是已观测到的扫描输出指针。不能复制 elish 内存图或改用其 PCD 体系 |
| stride/格式 | M1:169/177 按宽×高×色深计算大小，PixelsPerScanLine=Width；32位选BGRX | E5 同样假定紧密32位BGRX，并有显式缓存清理 | 实际 base/stride/通道顺序/线性或压缩/缓冲偏移均未知；面板链路24bpp不能推导内存色深。若 stride 不等于 width，需适配真实 pitch，不能让 GOP 虚报 |
| 底层初始化 | SimpleFb 暴露既有缓冲区，不建立 DSI/PHY/电源时序 | 同样是既有 framebuffer 的 GOP 包装 | enuma 是双 DSI、每链800、总1600×2560；分辨率一致不等于面板/格式/生命周期一致。ABL 若已关屏或采用不可直接写的压缩布局，此路线不能恢复画面 |
| 依赖顺序 | alioth 保留 UFS，早排真实 Metronome，源码 SimpleFb 的 DEPEX=TRUE | E4 同样早排 Metronome，并沿自己的 SM8250 vendor 集合加载 UFS | 本板已知 UFS 返回前有停点。GOP 诊断必须明确隔离 UFS，且不能把换了队列的旧 ordinal 当同一驱动；用完整 GUID/实际调度计数重新定位 |
| 调试输出 | DEBUG 默认 framebuffer serial；可通过真实GOP更新几何 | 另有 framebuffer/GENI serial 实现 | N2:6 已覆盖为 Null SerialPortLib，应保留。不得借此次 SimpleFb 顺手启用盲写屏幕日志或照抄 UART 地址 |

## 本机显示所有权：哪些知道，哪些不知道

既有输入为 enuma XBL SHA256 7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057、Android FDT SHA256 643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62。它们是原厂/Android证据，不是自制UEFI实时内存图。

- OEM Display Reserved 为 `[0x9c000000,0x9e400000)`，36 MiB，Reserv / WRITE_THROUGH_XN。
- Android FDT 将其分为 cont_splash `[0x9c000000,0x9e300000)` 35 MiB，以及 DFPS `[0x9e300000,0x9e400000)` 1 MiB；后者不属于可任意写像素或日志的空间。
- 已知 DRM 模式为1600×2560、120/60/30Hz；双链路配置与24bpp描述的是面板传输。旧采集没有 fb0/通用DRM state，保存 FDT 没有 simple-framebuffer 节点，chosen 也没有可直接取用的 framebuffer 几何属性。
- 仅作边界演算：假设1600×2560紧密32位，则最小stride=6400字节、单帧16,384,000字节（0xfa0000）。这不是对真实base、stride、32位或线性布局的确认，也不能因为“放得下”就填入配置。
- 未知：ABL临时boot时是否保留scanout；真实base及偏移；stride/像素顺序；是否UBWC/tiled/多平面；时钟/电源/MDP SMMU域能否持续；进入DXE及ExitBootServices后的生命周期。

保留现有 N4 的 SEC 不清空显示区、N5 的不 detach 六个 MDP SIDs，以及原内存属性；这些是避免主动破坏的措施，不证明面板仍开着或域/时钟有效。原存储、显示、SMEM等所有权不能互相挪用。

## 可复用部分与必须加的适配

**直接复用核心，不另起显示栈：** M1/M2 的单模式 GOP 与 Blt 包装、现有 FrameBufferBltLib、Mu UEFI boot services/设备路径、N3 EnumaProbe 的实际 GOP 查询及 DarwinBootVideoFromGop 检查。SimpleFb GUID为 dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92（比较时规范化小写）。它的 DEPEX=TRUE，复用这些通用库无需引入外板二进制或空协议。

**不能原样启用：**

1. M1:93–102 的区域描述符未初始化，也忽略两次查找状态；M5 在未找到时不写输出。板级适配需清零、检查返回值/长度，第二个别名仅在首次未找到时查询；未知地址立即拒绝，禁止退回 elish 常量。
2. M1:169/177 没有真实 stride 输入，大小乘法先按32位参数运算，也不检查输出跨度是否在允许的像素子范围。需已证实的base/pitch/format、有检查的64位计算、对齐/溢出/边界校验，隔离 DFPS，不清空整个 Display Reserved。真实格式不是线性时拒绝此变体。
3. M1:17–49 未校验 QueryMode/SetMode 的单模式范围；SetMode 对任意编号返回成功。需只允许已存在的mode0，对非法查询/不支持模式按 GOP 契约报错；SetMode 成功不能描述成进行了面板初始化。
4. M1:238–254 cleanup 会在 Mode 可能为空时先解引用 Mode->Info。需空指针保护、失败分配释放及重入状态处理。
5. M1:293–299 GOP安装失败时先 ASSERT，后面仍无条件返回 EFI_SUCCESS；ASSERT不终止/被禁用时会掩盖错误，DEBUG也可能先陷入assert。需传播真实失败状态，失败不宣称GOP已建立。
6. 明确缓存/一致性方案。E5 的显式 clean 提供参考，不能无条件把整个36MiB显示区刷写/清空；只处理已验证的像素跨度。Blt可见与直接线性写可见要分别验证。

上述均为**未来最小适配要求**，本轮没有写patch或修改任何驱动，不能将静态发现当修复已完成。应沿既有extensions/暂存patch机制实现并锁定相关输入，保留原25迁移文件/六patch的字节。边界、无效模式、查找/分配/安装失败、stride与缓存跨度应在未来实现时做有意义的主机检查，再做固件构建/FD审计。

## 现成 framebuffer 日志为什么暂不复用

M6:166 的cursor放在区域末尾8字节；M7:17 的handoff offset为0x40，M6:287及S1把handoff放在显示区尾部。按本机范围计算，分别为 **0x9e3ffff8 / 0x9e3fffc0，均落入DFPS**。这不是R-002批准的0x9fff7000/0x8000日志范围。

此外，handoff头说明依赖SEC清空来避免旧Magic，而 enuma 专门保留显示区；直接启用可能读取旧记录、回退到未验证几何并写入已有所有者的区域。因此保留Null SerialPortLib，不导入显示区尾部handoff/cursor写入，不把保屏补丁撤掉来“修”日志。

S1的可复用部分仅是验证顺序：等待真实GOP、查询base/pitch/format、分别做GOP Blt和线性小标记。需剥离其尾部存储假设，用受控的DXE内存变量管理临时状态，不占新固定地址。只有GOP以后，才能讨论安全的屏幕文字日志；早于GOP的黑屏仍由R-002日志路线定位。

## 推荐的未来诊断组合（仅设计，未实现）

| 模式 | OEM集合 | 图形提供者 | 用途 |
| --- | --- | --- | --- |
| 默认 native | 33个，保持当前默认 | 原厂enuma DisplayDxe/CPRDxe | 主线路线，不能被本审计改写 |
| 现有 no-UFS | 32个，仅缺UFSDxe | 原厂DisplayDxe/CPRDxe | 已有入口边界证据的独立基线 |
| 拟议 SimpleFb + no-UFS | 精确缺CPRDxe、DisplayDxe、UFSDxe，其余30个PE/DEPEX不变 | 唯一的Mu SimpleFbDxe | 隔离已知UFS/原厂显示入口，检查Bootloader既有scanout能否被包装 |

CPR与Display同选是参考alioth的诊断选择，不表示已证明其他enuma驱动不依赖CPR；需在接入时核对剩余协议及队列。CPR/UFS缺席的诊断成功不能算原厂显示或存储已修复。

接入须一次闭合：

- 显式、默认关闭的诊断选择；同时在**Components、FV打包、APRIORI**移除同一组原生驱动并加入SimpleFb。只保留唯一GOP提供者，检查SimpleFb GUID在卷中且APRIORI无悬空/重复引用，不靠未知环境下改一个宏。
- 保留其他原厂驱动、K81原始资源和已固定加载契约；不修改OEM PE/DEPEX，不用空协议补位，不复制elish ACPI/DTB/内存表/厂商二进制。队列变化后按SimpleFb完整GUID重新定位，不再沿用Display ordinal32。
- 现有 scripts/firmware_audit_policy.py 只允许精确UFSDxe缺项，scripts/audit_enuma_fd.py:59–61要求原厂Display并拒绝SimpleFb。这是正确的默认保护，**不能删除或全局放宽**。未来须为明确SimpleFb模式建立精确缺三项、完成FD摘要匹配、唯一提供者及其余30项逐字节核对的独立分支；默认33/现有32模式规则保持。
- 如参数需要新增/修改board或bringup-plan内存地址/大小，先按AGENTS列出真实值和依据供审查；不因为本报告引用了OEM范围而视为已获新地址配置批准。本轮没有这些变更或新的待批项，R-001/R-002范围保持。

## 实机验证前置条件与逐层验收

以下是**未来操作的条件**；用户当前要求暂不操作实机，本轮没有执行其中任何设备步骤。

| 门禁 | 需要的证据 | 失败时如何解释/处理 |
| --- | --- | --- |
| G0：原始输入 | 从enuma明确身份及当前匹配固件取得scanout地址、stride、格式、线性布局/有效跨度与ABL保屏依据；Android DRM、面板XML、保留区地址不能单独代替入口时事实 | 没有可说明来源的几何就不启用写屏；保持Null serial，先推进R-002日志。不能用试写未知区域来发现格式 |
| G1：离线变体 | 上述必要适配完成，错误/边界检查、真实固件链接与补丁恢复、精确30项/唯一SimpleFb/APRIORI/加载v3审计通过；原生默认规则回归 | 本轮仅源码/证据静态审计，不是这些检查或构建通过；没有硬件ready镜像 |
| G2：恢复保障 | 用户明确恢复设备测试后，核对恰好选中enuma、原备份/分区摘要/槽位/解锁、可恢复fastboot路径；必要的按键配合准备好 | 不能在nuwa或身份查询不完整时发boot；本轮没有任何ADB/fastboot查询 |
| G3：真实入口与协议 | 只做有界临时boot；记录版本/GUID、调用与返回状态、查询GOP全部字段；只接受唯一提供者，QueryMode成功、无效mode正确拒绝 | 调度到前门/返回非错误不是主体/出图证明；若没到SimpleFb，先定位更早的剩余驱动；不继续堆开关 |
| G4：实际可见输出 | 在已验证像素子范围做小块Blt，再做独立线性图案；记录base、stride、格式、cache处理和照片/构建标签，确认双链路接缝/边缘无错位、通道正确 | GOP元数据有值但黑屏不能算通过，也不能据此立即更换base/扩大写范围；可能ABL关屏、压缩/偏移/缓存或电源域不成立，保留证据 |
| G5：loader视频契约 | N3复用的DarwinBootVideoFromGop返回成功，Video rowbytes/范围与实际画面一致 | 当前BootVideo.h:21只接受PixelBlueGreenRedReserved8BitPerColor。RGBX、PixelBitMask、BltOnly即使可显示也不满足当前loader；不能虚报BGRX来绕过 |
| G6：生命周期 | DXE运行一段时间、BDS/菜单可见与复位恢复Android/root/原分区摘要正常 | 先结束本层测试。现有EnumaProbe明确不调用EBS、不分配512MiB；ExitBootServices后保持、owned窗口和XNU入口另立后续验收，不从照片推导 |

若G0仅缺不能离线取得的实际scanout信息，应整理所缺字段及最小只读/有界观测方案；不猜MMIO寄存器或借其他区域。不因这条GOP诊断路线去改变R-002的跨复位日志存活条件；两条证据链独立。

## 本轮校验与交接

静态核对了22个源码的固定Git blob及SHA256，复核既有33项OEM清单、保存FDT/Display保留区及DFPS尾部地址演算；A1/A2/M1/M6与选定上游一致。没有运行驱动单测、QEMU、固件/镜像构建或CI，不把历史45项Python/21组FDT sanitizer当作SimpleFb通过。文档/JSON/来源锚点和Git差异检查属于本轮文档审计。

可复核入口：阅读 reports/enuma-simplefb-reuse-audit.json 的sources逐项按Git提交/路径取文件、核对sha256与blob；保存的FDT仅在out/device/live-fdt.bin，用scripts/audit_inputs.py的parse_fdt读取。工作区保持原board、gitlink及42项固件源锁；没有修改任何参考仓。

下一步（仍离线）：先把G0所缺参数与可获取来源逐项闭合，再实现受控暂存变体/严格FD审计与错误路径检查；在几何未闭合前不生成“硬件可用”候选。是否恢复实机由用户后续指令决定。

## 后续执行索引

2026-10-23后续用户要求借鉴其他设备。独立metadata诊断已实现并完成一次AArch64构建，但首测未自动返回，等待实体恢复；详见[当前执行交接](2026-10-23-simplefb-metadata-variant.md)。本审计的六项真实scanout条件仍未闭合，不能将metadata假设或构建当成它们已通过。新Blt/Probe守卫与未编译/未恢复边界以当前STATUS为准，本文件保留原离线时点记录。
