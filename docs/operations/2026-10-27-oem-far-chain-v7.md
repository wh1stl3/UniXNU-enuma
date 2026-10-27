# OEM far-chain-v7：把观察终点后移到 DXE 分派完成

用户澄清“不是更细，而是更远”。本轮据此扩大一次运行的后段覆盖，不再继续加密ChipInfo附近的停顿点。本轮仅离线实现、构建和资格；不复用v6拍摄/在场状态，不追加上机。v6已consumed且E01/C6/Qc/RVA3608确认，Android自行返回与独立恢复核验通过。

## 实际推进

v7在整个原厂DisplayDxe调用期间只记录有界RAM追踪与粗粒度里程碑，不绘制、不等待；真实CoreStartImage返回后只保存原始状态，不在该回调画页。新scope专用编译宏ENUMA_OEM_FAR_CHAIN=1使目标point13仍记录真实日志但不进入旧2秒复位。于是CoreDispatcher可以继续处理后续驱动。

DxeMain的真实CoreDispatcher调用返回后，EnumaDispatchCompletionCheckpoint首先调用Core内EnumaOemFarDispatchComplete，再沿既有7秒ResetCold/CpuDeadLoop出口停止；本版仍不进入BDS。不能把这称为全部DEPEX满足或全部DXE驱动成功，只证明这次分派调用返回。旧scope宏为0，旧逻辑/冻结产物不回写。

末端只查询当前GOP协议是否成功取得、Mode指针是否非空，以及原SystemTable.ConOut是否非空；不SetMode、不Blt、不ConnectAll、不使用新地址或启动项。存在性不证明OEM所有权、画面/几何/缓存完整性、ConOut可显示、正常BDS或实体输入。

## 一张集中汇总页

仅在真实目标Core返回已保存且分派已完成时输出一次，最多8秒。ROI仍(64,96)320×160，旧MDP/CPU/窗口恢复准入保持。前段没有E01/E03或服务返回窗；全无页不等于未到远端，可能原厂/后续驱动未返回，也可能末端显示出口拒绝或复位路径提前结束。无独立异步看门狗或持久日志。

五行格式为S05C[16位flags]、Q[next trace sequence]、O[last traced OEM caller RVA]、S[真实目标CoreStartImage状态]、G[session]。C是新scope的里程碑位图，不是call号；只在严格v7解码器解释，不能用v6标签解码。所有位是已观察事实的累计锁存，不表示其他未包装代码经过或最近一次调用成功。

| 位 | 含义 |
| --- | --- |
| 0x1 | 追踪已为精确目标挂接 |
| 0x2 / 0x2000 | 精确注册服务已返回 / 曾返回EFI_SUCCESS |
| 0x4 / 0x8 / 0x1000 | 主入口ChipInfo查询进入 / 返回 / 曾成功 |
| 0x10 / 0x20 / 0x800 | SID查询进入 / 返回 / 曾成功 |
| 0x40 | 真实目标CoreStartImage已返回，S行是其状态 |
| 0x80 | 本次CoreDispatcher已经返回 |
| 0x100 / 0x200 | GOP协议存在 / Mode指针非空（仅存在性） |
| 0x400 | ConOut指针非空（仅存在性） |

解码强制armed/Core-return/DXE-complete三位，拒绝未知位、子里程碑没有父里程碑、错误session、旧scope页面及截断；未出现的阶段不会补写。

## 因果区分与下一启动链

若取得汇总页，可一次看到主入口、SID、真实驱动状态以及后续DXE/GOP/ConOut存在性，覆盖范围超过旧单服务前页。若看到Core成功但无GOP，下一步转向显示协议发布/依赖；有GOP但无ConOut，推进控制台连接和BDS前置；Core错误时按真实错误和已到阶段修复，不伪造成功。若无页，必须保留前段/后续非返回与出口拒绝的竞争解释；此候选换取更远覆盖，牺牲中途可见页，不是提高缺页的定位确定性。

BDS仍是明确的下一边界，未执行其Entry，不称BDS/XNU成功。后续按生产GOP模式/几何及显示所有权→ConOut/配置发现和输入→BDS/DarwinBoot/EBS→XNU推进；不通过跳过原厂初始化或临时菜单填成功。

## 验证与构建记录

新输出out/oem-far-chain-20261027。新RAM-only/末端导出、真实失败状态、缺失阶段不补写、末端sink/TPL失败、目标point13不再复位且completion按导出→7秒→复位有序执行、页面字段检查均进入宿主验证；绑定与AArch64板级编译通过。44项Python含模拟传输通过，无设备命令。build1因修改DSC补丁引入CRLF而目标DSC为LF，预检拒绝；补丁转回LF后另建build2，失败输出保留。check1..4中保留缺头/夹具签名/字串大小写检查失败，最终check5为修正后的真实头文件/实际格式检查；没有以修改固件功能来满足这些失败。最终完整FD、机器码删除/变异负测、打包/解包和来源绑定完成后追加，不提前称硬件通过。

## 2026-10-28 最终离线资格与可上机镜像

镜像qualification2/image.img为3153920字节，SHA256 c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d；FD e16748c382248cdfddd4514ea6e274032ec3c987fc96bcd11ad01a3117610a2f；qualification2/qualification.json a1cdb2c1fbb1e4c7aacd0f6862db68c45275297f643e0241d092c7a622612823。路径均在out/oem-far-chain-20261027。trial 61c29945-1399-49eb-8133-d11d465bb6c4，session 9369882057737620086，尚未claim/上机。固件1f05eef62b62fc6f57b805e1cb346e3643457db7，build2是d393211基线工作树快照，与source-manifest精确绑定，不称提交后重编。

check5 ASan/UBSan与实际页面/point13/completion门、binding1重定位/错PE及ARM64板级、path1精确PE/ChipInfo ABI、44 Python通过。最终机器码30+108删除/3 GUID变异全部拒绝；默认离线2456项绑定、完整FD OEM审计及Boot v3封包/解包回读通过。qualification1因旧scope源码地址/布局断言与v7链接布局不同而拒绝，修正只作用于已反汇编复核的v7：真实返回句柄偏移24，SystemTable全局加载偏移2584；没有修改已编固件以迎合验证器。qualification1保留，最终机器码审查见machine-code-review.json。

编译后CoreDispatcher调用RVA3bb0；3c38调用OemProgressFarFinish，随后3c44 MicroSecondDelay(7000000)、3c48 ResetCold、3c4c CpuDeadLoop。目标point13在真实日志追加之后返回，删除负测绑定实际存储/RET；OEM Observe/Returned均无提前绘制。EnumaOemFarDispatchComplete由编译器内联进DxeMain，不以“缺少独立函数符号”误判未接线。

### 更远的下一卡点与实际解决方向

1. 当前最优先隔离v6 E01窗口收尾/转发的执行干扰；v7消除全部OEM侧UI和等待。若成功出现汇总，支持本次已跨过该区间，但不能反推v6根因唯一是UI；若无页，不能判ChipInfo死锁。
2. 原厂真实查询返回后，在RVA3618调用ChipInfo接口+48 GetChipFamily，随后有条件协议方法及17e0/1810/1838/1860事件注册。它们是未包装的竞争卡点，不能由v6 E01排除。v7先让其原样执行到真实Core返回；若Core失败且无GOP，按真实返回码/已到阶段审查发布和DEPEX，不合成EFI_SUCCESS或跳过OEM初始化。
3. 新版取消point13的提前复位，因此后续DXE现在可以继续；其他驱动不返回或依赖不满足仍可能阻止末端输出/所需协议就绪。CoreDispatcher返回只代表本次分派结束，并非全部DEPEX已满足。下一步按未分派目录和缺失架构协议补真实provider/初始化次序，不把目录里存在PE当驱动运行。
4. 板级Include/DXE.inc确实列出ConPlatformDxe、ConSplitterDxe、GraphicsConsoleDxe和BdsDxe，但编入不代表连接成功或可显示。v7存在性位之后应核对真实GOP Mode/framebuffer几何/所有权、输出句柄及控制台连接；ConOut非空可能只是分流器，不能直接跳为控制台验收。
5. 固定Core DxeMain在CoreDispatcher之后先检查CoreAllEfiServicesAvailable，再调用gBds->Entry(gBds)。v7故意在此之前保留恢复出口。下一BDS候选应绑定缺失架构协议处理、PlatformBootManager的连接/启动项发现和配置/存储来源，并提供新的可控出口；不是仅删复位。DarwinBoot/EBS/XNU仍随后分层验收。

本轮无设备命令，R027/v6冻结摘要不变。现行STATUS/HANDOFF/PENDING-HUMAN已对齐；当前拍摄/在场状态未确认，软件资格不替代即时设备门禁。补丁LF规则及scripts/check_changed_patch_eol.py已落位。

## v7本次拍摄与单次准备

2026-10-28 00:09 v7本次单次准备：用户明确“v7开始 正在拍摄”，按已说明的本次现场/在场恢复条件和既有恢复安排，仅新v7一次临时boot。即时只读前检enuma/Android完成/root/A槽/解锁及原双分区/备份摘要通过。未claim/发送；准备文档发布及远端核对后由runner重复即时门禁。精确镜像c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d，trial 61c29945-1399-49eb-8133-d11d465bb6c4。75秒无合格返回先恢复，不自动重试，不flash/erase/改槽；R027冻结，共享主线只读。证据out/oem-far-chain-live-20261028；媒体Media-enuma/OEM-far-chain-v7-20261028-61c29945本地保留。以下旧就绪状态不复用，实际执行/恢复随后更新。
