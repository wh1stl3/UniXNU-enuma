# UniXNU-enuma

**2026-11-14 暂停交接**：当前候选、授权边界、生产包和 GOP 暂停状态见 [session handoff](docs/SESSION-HANDOFF-20261114.md)；下方较早计划按历史快照阅读。

**GOP 生产整包 r5 主机侧封存完成（2026-11-16，self-checked，未部署未实机验证）**：`out/enuma-gop-production-20261114-r5/` 已封存。`seal.py` exit 0：`sourcepin.json` 4187 B `e804b868b5348f1054ae32ba7a13c476b709f4ed40dbba85893f7f56acaa4c26`、`device-enuma-gop-legacy.patch` 50828 B `26f02f65676c60ea6e98b13a9f0034e9600fbbbbe6f945f65017b2b1c0792a53`（941 行 / 7 hunk，独立临时目录 `git apply --check`+`apply` 均 exit 0，7/7 逐字节一致）及 `patch-replay/` 9 文件。`audit.py` 与 `audit.py --verify` 均 exit 0 并重建 manifest：`candidate-manifest.json` 449545 B `27c7b92cc2291b5ce6ca3c05d9683d93f423d367170ec3787e3e63b708fa3859`（`files`=429）、`verify-audit.json` 28759 B `535d582b5a5af8b66a2492de9dff43ab3ee84bfe18355873e6b2b58a414be7b1`。五件目标产物字节与 SHA-256 未变：`display/libEnumaGopLegacy.a` 598792 B `c88510ae599cd678d2b0f83a98034d61a5e5e167e05295cb9c58085672cbb1b5`、`native.macho` 91823176 B `5ba046a084adad242d7972c5d782d075b452b292b0520e932995ce871b840574`、`prelink.macho` 124665856 B `4d7eb65c6c57d23ee31caafa7750983c7c28f26f089667a089184c3c70bbdeb8`、`payload.img` 201326592 B `44022ef27b3bffd8e48bc9efb35c295433681e0110f7d6be993e9f149b3e5c97`、`boot.img` 203505664 B `fd97c13571b1001f1c6910c2df509da23af82504cddaf94cf659f35bf1bb5600`（哈希取自该 manifest 自身）。复现条件：`wsl -u root`（`build.json` 输入位于 `/root/enuma-step10/...`）且 `https_proxy=http://172.17.144.1:7890`（`audit.py` L324 `git ls-remote` 需出网）。封存前旧 manifest/audit 保留在 `out/enuma-gop-r5-preseal-manifest-20261116/`（`.bak`，未删除）。`upstream_at_final_audit=4a654d1f31662f18ab94391a4f0297b17b9bb2fe`，基座 pin 仍 `693f5d9c…`，未 uprev。状态 `self-checked`、`release_allowed=false`、`hardware_tested=false`、`deployment=false`；本轮未叫独立 verifier，无设备/claim/签名/刷写授权，未部署、未实机验证。细节见该目录 `HANDOFF.md`「2026-11-16 更新」块与 `DELIVERY.md`。

**UFS warm 路线决策（2026-11-14，用户明确决定）**：主控提供本轮六读 Observed 已验证的结果；这是有限观察，不证明 DMA 安全、持续所有权或 root，也不将 FAULT 或观察当作 fence。用户接受的具体残余工程风险是：vendor 异常返回后旧 DMA backing 已释放或复用，但 DMA 退役未完整证明；按官方 ShengUfs warm 路线继续，不再以此交接问题作为当前主机实现前置阻塞。若后续 UFS 接入出现异常、数据损坏或超时等具体故障，回到此交接问题分析。保留正常完成检查、DBR/fatal 门禁、失败保留/不重试、本地双 SID 模板和已有先停后分配；不回退为 `adoptAndRead` 借旧 16KiB。此决策不是 DMA 安全证明或执行准入，不改变默认 NoAccessPolicy/NoContract，不放宽 boot 或任何设备写入的当轮授权，正式阶段不提升。最终目标仍是真实 UFS 持久 iPadOS 交互并断电重启后仍可操作。早期交接分析见 [检查点](docs/ufs-handoff-design.md)，其历史前置建议由本决策限定。

**上游受控 UFS Provider 隔离非执行实现 r3（落实 H1/H2/H3/M4，2026-11-14，self-checked，待普通复审/deep专项/独立verifier）**：保留冻结 `out/ufs-upstream-provider-nonexec-20261114/`（`r2` 及独立机械验证 `independent-*-20261114b/` 原字节未改），在新隔离目录 `out/ufs-upstream-provider-nonexec-20261114-r3/` 落实 reviewer `ses_e29e5eb51ffewFikIZr3AVNTgt` 四项 CHANGES REQUIRED：①H1 在不改标准 `PciIo->Map`/`UfsHc->Map` 签名下新增 `EDKII_UFS_DMA_MAP_OWNERSHIP_PROTOCOL` 贯通 `NonDiscoverablePciDeviceDxe`→`UfsPciHcDxe`→`UfsPassThruDxe`，`SetAttribute+Unmap` 双失败时单调锁存残留所有权，上层零 `FreeBuffer` 保留全部 68 页 CommonBuffer、`MapInfo` 与 `Private`，永久 `Poisoned` 且不可重试/拆卸；②H2 采用 `RaiseTPL(TPL_HIGH_LEVEL)` 短临界区 + 64 位 `GateWord` 非阻塞 CAS 统一全部提交、查询、`Stop` 与 `PrepareHandoff`（覆盖 BSP Boot Services 回调抢占域与同缓存一致性域，无自旋死锁），`BUSY` 在预检 MMIO 读前原子置位并持有至响应校验与 `CopyMem` copy-out 完成之后；③H3 明确 `EfiBootServicesData` 不等于跨 EBS/DarwinBoot/XNU 保留、`PciIoFlush` 不作 DMA drain，`PrepareHandoff` 置 `ArenaPinnedInBootServices=1`、**`ArenaRetainedAcrossBoot=0`**、`ListRegistersStoppedObserved=1`、`LifecycleState=Closed` 并返回 `EFI_NOT_READY` 拒绝伪造跨启动保留认证；④M4 将 NOP/Query/SCSI 全部结构与长度/残余校验前置到 copy-out 与退休之前，畸形一律 `UfsProviderFailStop`（零输出、禁止下一请求）。`self-check-r3/result.json` 131 条命令（双补丁重放、66 个真实上游函数 ASan/LSan/UBSan 进程、13 个 AARCH64 `CLANGPDB` 对象、目标 host-hook 编译拒绝、`lld-link` 与反汇编）及 `integrity-r3` 正/负篡改检查均 exit 0 self-checked；`sourcepin-r3.json` `35071d8192b83f79d900b9661ed58b50645d8b61c33156a26f386ec2a83003f6`、`increment-from-r2-to-r3.patch` `6dbd2b797de00b9eb335d563dba2c81f391927f7d401aca2e6d8933f4de69e36`、`increment-upstream-to-r3.patch` `fc4064c0bfde46207e17af2bd35d280de3b6bb41f06e54fb0980d27f591170da`；本地检查 `.dll` 不作跨环境字节复现或部署 pin。非完整固件或硬件准入，无设备/claim/boot/签名/刷写。

**上游受控 UFS Provider 隔离非执行实现与早期边界审查修订（2026-11-14，r2 历史快照）**：落实普通 reviewer `ses_e2a313baaffej0Hvh3BpF7hkIS` 对 `out/ufs-early-takeover-boundary-20261114/{DESIGN,SOURCES}.md` 的 CHANGES REQUIRED 修订及 `out/boot-entry-contract-20261114/FINDINGS.md` 边界核对（保留审查变更记录，早期写入事实不等于旧DMA重叠，R含适用实际入口的可信平台交付约定，移除vendor `UFSDxe` 后其错误路径不自动归XBL，执行入口交付缺口与候选自身映射/生命周期缺口分列，原件许可逐一核实，不采纳shim承担交付或header字段无关的未验证推断）。新隔离 `out/ufs-upstream-provider-nonexec-20261114/` 基于 `mu_basecore@cfb93724a06ff86ff5ba971413368a7809ee42a5` 与 `edk2-platforms` `QcomUfsHcDxe@eedc0612ddb2bcecef5053ab31672fe058c2f21d`（均为 `BSD-2-Clause-Patent`，保留 `MU_CHANGE`）完成：修 `NonCoherentPciIoMap` 中 `IoMmuSetAttribute` 首错被 `IoMmuUnmap` 覆盖并在 `Unmap` 失败时保留 bounce 页；272KiB 专属完整 CommonBuffer arena（TMRL/TRL/CmdDesc/256KiB 自有数据 bounce，零调用方直映）在首次基址写前登记固定；真实 NOP/Query（单次无重试）/SCSI 三路径统一 slot0 串行门禁、重复提交拒绝、门铃前/后 cache 同步与 `Flush`、有效 OCS/UPIU 校验及不确定结果 `UfsProviderFailStop` 保留（AARCH64 目标 `wfe` 死循环无 `ret`，测试注入终止钩子）；4 个正常入口恒返 `EFI_ACCESS_DENIED`、缺真实 `IoMmu` 返回 `EFI_NOT_READY`（不用 identity/bypass 假值），112B 纯数据 `UfsPassThruPrepareHandoff` 明确保留范围且固定前任/SMMU/执行准入标志为 0。114 条命令（51 个真实上游函数 ASan/LSan/UBSan 故障进程、13 个 AARCH64 `CLANGPDB` 对象编译、目标 host-hook 编译拒绝、`lld-link` 检查件 `LOCAL_ONLY_UNLOADABLE_UfsProviderLinkCheck.dll` 61440B `7ca6dc84e047921241baf35089de09f6724a1689c6f67977623907eb7b1afd27` 及反汇编）、`sourcepin-r2.json` `314d509d2c49e5ccfec382b56df38ddba1b197df4e55cb787f1dbcf1436a3287`、`increment-r2.patch` `4914e8d58aecc7018af214d5db164812600abe4c0ad3b562f67bf75b8bae9075` 及只读 runner 正/负篡改检查均 self-checked。非完整固件或硬件准入；旧冻结 native/失败 provider/默认配方不改，无设备/claim/boot/签名/刷写，NoAccessPolicy/NoContract 与正式阶段不变。

**目标接线编译/链接检查（2026-11-13，self-checked，待最终审验）**：新隔离 `out/ufs-native-warm-target-wiring-20261113-r1/` 从主控报告已独立PASS的r1提取同一warm执行函数，绑定真实板级资源/mapPhys/IOBuffer/cache/RootQueue/RootCommands；正常target入口在所有warm/backend宏组合下仍先拒绝，无issuer/bootarg或旧SMMU配置fallback。保留双候选完整表/动态context/三宽度Observed算法，不采用配置型plan或借FW页；公开同donor官方profile/真实XNU10063头与同SoC alioth对照、许可差异见SOURCES。51共用函数ASan/UBSan、4target宏格正常拒绝、fixture真实编译拒绝及独立ARM64调用者+Apple ld -r均self-checked；MH_OBJECT保留88节点真实调用/重定位与未解析XNU导入，仅本地不可部署链接检查，非完整kernel链接或运行成功。显式新patch/pin及真实argv/exit/反汇编在CHECKPOINT/self-check-r1；只读runner normal与副本tamper检查通过。r1/基座/默认recipe/失败provider归档不改，无设备/claim/DMA执行/boot包；新增硬件读取/旧页/producer/持续owner准入未成立，NoAccessPolicy/NoContract及owner/root NO-GO、正式阶段不变。

**Native warm-adopt 主机隔离增量（2026-11-13，修后 self-checked，待最终 review/verifier）**：交付 `out/ufs-native-warm-adopt-host-20261113-r1/`，产品源码默认 off、target 在新增 HC/context 读取和分配前拒绝；真实 hostBringUp/RootQueue/RootCommands 验证双候选精确唯一/可见共享/context与地址范围、TR/TM stop 后才分配、首错 poison/保留，成功亦不开放 root/Data。旧 runner 确覆写 patch/pin，但外部前后哈希与 handoff 相同，不能称冻结完整性通过；修后读取固定 pin、生成 patch 仅 OUT 并比对/重放交付，normal 及独立 source/patch/pin tamper 检查、46host+RootCommands ASan/UBSan、target0/1及fixture真实编译拒绝均 self-checked。仅移除测试恒零计数，旧 pin/patch 原字节保留，新测试 pin/patch 显式另存；精确哈希、修复diff、argv/exit与复跑见 CHECKPOINT/runner-fix。provider 保持封存失败，非验证成果；无设备/claim/部署/boot包，NoAccessPolicy/NoContract、持续owner/root NO-GO及正式阶段不变。

**VisibleRoutes 末屏有效槽重印（2026-11-13，self-checked，待普通review/独立verifier）**：主控转述cp26r视频首帧PAGE02/slot06、PAGE01未录到；末屏95/95 COMPLETE、valid5、hits e0=1/4e0=1，后续rootwait panic非MMIO。不补造缺失raw、不提升owner/root或正式阶段；cp26r及旧claims不可访问/删除/重放。新 `out/smmu-visible-routes-tail-20261113/` 仅改采样后的输出和两测试shim：原两短行slot打印提为局部复用，summary附近集中重印全部cached有效槽，≤5项末屏≤17行；>5全部缓存分页后末屏留候选命中槽，并明示valid/hits/shown/hit_overflow/valid_paged，绝不按本次5项硬截其它有效数据。capture/issuer/claim/177调度、DMA/root不改，复用既有IOSleep，无新框架或MMIO计时器。192实际executor ASan/UBSan覆盖95读5有效首槽+候选、87全有效/overflow82、partial/字段逐字保留，2target/patch及采样指令/import不变self-checked。新完整 `out/smmu-visible-routes-tail-candidate-20261113/` 已真实重编native91753368B `7a84f672ede58e332b7cead13d97a89c802710a918bcb1551319fc6d55b8996f`、prelink124596224B `f6c05f9e84280f516b4015075ac25783ac71828b31f451e1797f228248469924`、payload201326592B `c6b3e235c02605c9a4899c5b176b512beeb3c00cb12ed8e49cc45539612a2321`、boot203505664B `418550031c61ad2cc8de950a3927f4982a93e7f4e15532171c2cd005540b9292`；实际最终机器码/复用打印helper/API归属、zeroUndefined含weak、新live成员、FD/payload/kernel/ADT/trust/entry提取及预算self-checked。固定FD仍e524988b…、诊断trust6440/无initrd，非OS/root包。精确hunk/末屏行数/快速增量验收及完整fresh命令在新CHECKPOINT/OUTPUT-REVIEW；旧包冻结不改。用户重新部署授权由主控在新审验后执行一次临时boot非刷写，本agent不执行设备/claim/签名；并行ownership deep不受此输出任务阻挡，默认NoAccessPolicy/NoContract、持续owner/root NO-GO不变。

**VisibleRoutes 分页输出修复（2026-11-13，self-checked，待新review/verifier）**：主控最终 reviewer `ses_e2b3cca93ffe6FBNUrXUVmafxn` Medium 指出旧候选刷屏且汇总不留末尾；旧 `out/smmu-visible-routes-candidate-20261113/` 冻结，**不得部署**。新 `out/smmu-visible-routes-paged-20261113/` 仅改采样后缓存输出及实际executor测试：全部87slot raw/read-valid、TYPE/CB/ref/候选匹配保留，15小页、每页现有IOSleep(1500)、短行≤80字节；不逐行刷177地址，完整缓存保留并以确定性前缀/计数/last/last_ok报告精确失败位置；末尾数值capture/decode/result、三ID、两候选计数及TERMINAL。186实际executor ASan/UBSan、macro0/1受影响TU、patch复现均self-checked；capture机器指令、issuer/claim/177读范围不改，IOSleep import原已存在、实际链接仍IOLib.cpo，无新计时器/线程/锁框架。新 `out/smmu-visible-routes-paged-candidate-20261113/` 完整新native91753368B `bb848fc26b480d7964ef952473b5c288b50ccff7cc2f33abdb1ad3e3dfd09dc8`、prelink124596224B `893930fdb585fc8fdb13ba30ae7cd6c96a3cf9620a017552efd99f704a22706e`、payload201326592B `8b5e50d55107aecde03111c7895ec6f15c92cd82423bc7cacf72e6d49dffa474`、boot203505664B `978957c738b5b164bb75e5e62d9b9529baab62f1da60fea3dfb626550754058f`，实际最终指令、API归属、zeroUndefined含weak、live新成员、包提取/预算self-checked。固定FD仍e524988b…、诊断trust6440B/无initrd，非OS/root包；完整manifest、精确输出hunk/API证据与fresh命令见两新目录CHECKPOINT/OUTPUT-REVIEW。实际时长/屏幕可读性未上机观察；新候选待普通reviewer及独立verifier，之后才另申请新boot授权。本轮无设备/claim/私钥/签名/部署，cp25r不访问/重放，默认NoAccessPolicy/NoContract、持续owner/root NO-GO和阶段不变。以下未分页候选状态为历史快照。

**VisibleRoutes 组件独立 PASS、完整候选主机 self-checked（2026-11-13，未部署）**：主控提供 reviewer `ses_e2b6243b4ffe5DfWMSmjRCT0Xx` PASS 无修复、独立 verifier `ses_e2b61f668ffejCmnvrHYe0u8UE` 392host+5真实executor/2target/patch复现/指令 PASS，证据 `.cache/verify-visible-routes-20261113/`。来源为官方 `UniXNU@693f5d9c` ArmSmmu4K MIT 纯表达式（完整通知保留）及现有本地 capture/geometry/许可；T970 只比较、未采用。新 `out/smmu-visible-routes-candidate-20261113/` 逐字节复制最终 sourcepin、零新增源码 hunk（既有4行hookguard不重复），真实重编archive→native91753072B SHA256 `c1c4b71922a08cdee4dc79701d0c8e1346b443013659e536e61e7346e3851ef8` →prelink124596224B `36826e6af0029110926e697bedaf9e1b4fc6b67ed29bf7e1aac57a3318a71437` →payload201326592B `0c578b2427dba57423a64f2b1943e5c6a163f2cfb63f7102312a37d2e3a17bf7` →boot203505664B `c7676db63a3825da07669bc09cc7ec0d643145ca39b8f54dfc590393fa395be6`。仅新VisibleRoutes宏/session，旧ThreeId宏0不竞争入口；精确三ID后全部87SMR缓存，再有效S2CR一次，90+valid≤177，无0/400/CB/HC/GCC读、MMIO写、二遍采样或native/DMA续行。最终机器码、zeroUndefined含weak、新live成员归属、实际ADT/personality/entry/包提取与95%预算均self-checked。固定FD `e524988b8a05f15847ffc991170de8a5e0ead607400421e0835084497a71bf1e` 由boot内实际字节绑定，不用bootarg自证；诊断trust6440B、无initrd，**非OS/root包**。完整输入链/manifest/精确fresh复跑命令见该目录 `CHECKPOINT.md`；最终候选尚待独立review/verifier，新boot未授权。未访问设备/claim/密钥，未部署或签名；默认NoAccessPolicy/NoContract、持续owner/接管NO-GO及原阶段不变，cp25r已消耗不重放。

**三ID cp25r 单次CPU读取完成（2026-11-13，主控照片转录）**：最终候选 reviewer `ses_e2baa23dfffeGBj7P0vMI2rflD` 和 verifier `ses_e2ba83bdbffeA5rJxXt9wkwLur` 主机 PASS，证据 `out/smmu-three-id-independent-r2-20261113/`。用户本轮授权一次boot及录像；确认 enuma 后 adb reboot bootloader exit 0。首次脚本 preboot STOP，scout `ses_e2b8bcdc2ffeihW1cy8eSlUyPG` 确认 cp25r marker 不存在且未发boot；确认 fastboot product enuma 后运行 `run-threeid-r2-once.ps1 -AuthorizeDeviceThisRound -AuthorizationRound cp25r`，fastboot boot exit 0，实际仅发一次。原r2 boot SHA256 `45d51344bd366a4da9266dc0935168daf4dbf09fdeced1e4cb7c18b54cabdfb8`。主控直接读照片：`UFSOBS COMPLETE completed_count=3 raw[0]=0x4c017e57 raw[1]=0x6000004a raw[2]=0x00005111 decode_status=0`；下一行 `TERMINAL no retry/no native UFS/no DMA`。reviewer `ses_e2b89a494ffelUohSePbmF0CAK` 基于文字转录核对固定源码：Observed=0，87 slots、15bit SID、74 CB、0 stage2-only、4K寄存器页、CB base 0x15080000 至末端 0x150ca000、IAS/OAS/UBS 36，与profile一致。三ID CPU读取完成且decoder接受；照片未落文件。cp25r 已消耗，禁止访问/删除/重放；不证明持续owner、DMA或root通过，不提升阶段。持续访问/接管 NO-GO，默认 NoAccessPolicy/NoContract 不变。以下候选执行前叙述为历史快照。

**三ID完整主机候选历史快照（2026-11-13，self-checked，当时未部署）**：`out/smmu-three-id-candidate-guard-r2-20261113/` 含 native91751904B、prelink124596224B、payload201326592B、boot.img203505664B 与完整 `candidate-manifest.json`。来源源码独立审验、构建和预算细节见该目录 CHECKPOINT.md；无 initrd，root mount 前终止，不是用户态/root包。manifest SHA256 `8826a1d6394da4a62f69742bd3ee86c03b07f9470a051f4eb0410c9b4c049e0a`。

**三ID诊断源码限定GO待验，持续访问/接管未放行（2026-11-13，self-checked）**：主控提供 deep `ses_e2bdebf21ffeykL6DfJ2etefx1` 基于固定FD SEC证据的限定批准。仅新 ignored `.cache/smmu-three-id-20261113/source/` 实现一次IdsOnly snapshot；全部准入/map后一次ATTEMPT，15000020/24/28各32bit一次，load间只有内存breadcrumb/barrier，统一缓存输出completed_count/raw[3]/decode_status后WFE。默认issuer仍NoAccessPolicy，隔离宏才可签发精确enuma/SM8250-AC/profile、独立session/version、空SID/bank、全局一次性claim及静态不可变context；NoContract、正常root/Data写不变。实际入口/reader 87 ASan/UBSan用例、default/closed-candidate/diag三target格、实际三load反汇编与独立patch apply-check完成；普通review和verifier未复跑。增量 `patches/isolated/enuma-smmu-three-id-20261113.patch` 不接series；完整sourcepin/命令exit/候选清单草案见该目录 `CHECKPOINT.md`。未创建boot/claim、未上机；最终FD/载荷身份由外部candidate清单核验，下一设备动作须新授权。下列历史GR0 NO-GO不再一概覆盖本次源码切片，持续访问/接管仍NO-GO，不提升实机阶段。

**正常 consumer 隔离最终链接闭合（2026-11-13，独立验证 PASS；主控提供）**：verifier `ses_e2cd80d67ffe8F1QBORKcy7oji` 在 `out/verify-guard-r4-independent-20261113/` 完成 runner22命令、auditor、record/diff PASS；native变化仅LINKEDIT/path，机器字节及policy相同，prelink124575744B。正常consumer、零undefined（含weak）、六符号归属及最终完整policy/anchor字节绑定已验证；实现与原始命令见 `out/production-final-link-guard-20261113-r4/CHECKPOINT.md`。deep `ses_e2cd7b836ffe1ljM0BWe8Fa716` **PASS WITH CONDITIONS、无必修项**：当前固定VA加载下，运行副本copy→降低max/current只读→vr_open→publish与常驻生命周期静态成立；早期DATA_CONST可写，契约依赖运行副本，不声明非零KASLR/teardown已验证。默认recipe/series未接入，SM8250入口仍拒绝，不提升实机阶段；GR0 NO-GO、NoAccessPolicy/NoContract不变。

**Data seed 已具备（2026-11-13，独立验证 PASS）**：verifier `ses_e2c56245dffevCY9czlwOUMlHo` 对本地 seed/receipt 40 checks及只读API PASS，证据 `out/verify-data-seed-receipt-20261113/`。seed 为首安装3GiB逻辑 `3221225472B`、packed `1171584B`，SHA-256 `ea4921098ea2393d8b2fa77ec59e78e0284c843cb88a90e3fca8e7532dbe478e`；位置 `out/data-seed-transfer-20261113/received-43379610501/data.dbr`，同目录manifest/receipt保留，不公开新UUID。run43379610501在dc3587648a6d8e7f69e0a94fdce0eb7910015572成功，receipt关联，artifact数量0且原ID404。独立核验未重解密：GCM认证来自原receiver成功；具体Mac权限/verifyVolume来自原job构建结果，独立API仅证step success。不是r3的215GiB计划或持久store通过。

**剩余输入与整合**：隔离链接已完成，下一实际工作是 **production OS trust身份/实际输入、配置集成及完整payload预算**，不再索要macOS/seed、不以历史restore替代production trust。参考192MiB减prelink124575744B、seed1171584B、诊断ADT14012B、restore trust6440B后，raw余量75558812B、95%guard余量65492482B；这是restore trust参考预算，非完整生产总量。默认生产整合与Data/store配置、GR0/持久UFS仍独立阻塞；r3不改。owner私钥备份未确认，不自动备份；不生成部署包。

**Owner policy 离线签名（2026-11-13，独立验证 PASS；主控提供）**：长期 owner key 在 ignored `out/owner-keys/`，Windows ACL 仅当前账户和 SYSTEM，但不隔离 WSL root；用户备份尚未确认，不自动备份，原密钥生成命令及不覆盖保护的执行日志未留存。公钥 DER SHA-256 `b9650685b499b374b61d74336b07de22e1f0687377de695c9c90387caaf50560`，395B anchor SHA-256 `44a5f2f40f4102fd20c2d8f855a662e87acb5c760f2f12d79e6e21e746375f3d`。真实 generation 1 OS/SystemOS policy 与 key 未改：reviewer `ses_e2d0af0b5ffeclYk6VsN2KkJBt` 两 finding CLOSED、新报告与 provider 输入绑定 PASS；verifier `ses_e2d049d1bffePOAga5URcXZozf` fixture、C/OpenSSL 全表和 1483785/806400 全块、真实 provider 独立重编及 partial link、ACL/ignore 和正确 base record/diff 检查 PASS。新证据 `out/verify-fresh-20261113/{os,systemos}/result.json`、`out/provider-rebuild-20261113/result.json`；partial 对象 SHA-256 `b9d7bf5854849201910c28ae3bcd99d090bba77377e1e7356afec7d32fc37be1`。全块实际使用 shebang Python 3.10，fixture/record 使用 3.11；旧无绑定报告保留未替换。provider 自身 `signature_checked=false` 仅其工具范围标记，外部验签已按 hash 绑定。正确 record base 为 `origin/feat/step10-ramblock-probe`，先前错误 base 导致的 cellular 报错不是当前阻塞。后续隔离最终链接已验证、本地3GiB seed已具备；默认生产整合、完整预算及Data配置、当前GPT和持久UFS所有权仍缺，不是整体production ready；GR0 NO-GO / NoAccessPolicy / NoContract不变。

**Production 离线规划快照（2026-11-13，静态与机械验证完成；主控提供）**：`out/production-recipe-r3/` 的固定配方由 reviewer `ses_e2d5bad70ffeCIX5urEcqUYob2` 两 finding CLOSED、静态 PASS，verifier `ses_e2d471ec8ffewoO68938dtarf0` 七测试、预期 check exit 2、独立生成 330 文件一致、诊断配置前后 hash 不变及 diff/porting-record 检查 PASS；材料见 ignored `out/verify-r3-20261113/`。r3 额外的 `generator-revision.json` 为手工记录，非生成器产物；生成器 SHA-256 `58e81fc19fb35181fdbe69d2ef0c50dce18a2c1073548d203cd95f115bdeb4fb`，测试 SHA-256 `e895ea044459b7df86ed7dced04b02b0ffffec6037d1f419a8ebfd67b83a40a1`（verifier expected 栏多写的 `a` 为转录错误）。这仅验证固定快照，不认证输入就绪性；该快照未链接或打包，GR0/MMIO NO-GO保持。owner输入、隔离最终链接及本地seed后续结果见上；下一工作是production OS trust身份、配置集成与完整预算，不再扩展固定blocked框架或索要已有seed。

**隔离观察入口（2026-11-12，self-checked）**：ignored `.cache/ufs-observation-stage-20261112/` 的 local-module 将 probe/start 接到独立观察 issuer 和分级采样；生产 issuer 固定 `NoAccessPolicy`，在映射/MMIO 前拒绝，DMA 仍 `NoContract`。host 负例、独立 patch 应用及 default/观察 target archive self-checked；NS CPU 访问依据和独立 bank policy 未有，限定复核、独立 verifier 与设备授权待完成。命令、哈希和范围见该目录 `CHECKPOINT.md`；24r 未读取 SMMU，DAL 属性不是寄存器快照。

**Android 被动 sysfs 采集（2026-11-12，self-checked）**：唯一 enuma 的现有 root 读取显示 `1d84000.ufshc`/`ufshcd-qcom` → `host0`/Linux SCSI `0:0:0:0` → `sda` → `sda34` userdata；`sda` 非永久身份。`/sys/class/block/sda/device` canonical 指向该 SCSI 设备，`/sys/class/block/sda34` canonical 位于该设备的 `block/sda/sda34`。Linux LUN 0 按 [Xiaomi 固定源码普通 LUN 转换](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/blob/52a2f180865f8368828985d6384130acd093fa93/drivers/scsi/ufs/ufshcd.h) 推得 UPIU LUN 0；参考源码未与当前 Android 内核精确对应，不推翻已有内核二进制绑定与分析。sysfs 512B sector start 21495808、size 473546712；换算 4096B 块 disk 61880320、userdata [2686976,61880315)，容量 242455916544B，与历史几何一致；9382658048B 镜像仅容量上可容纳。未读当前 GPT 或验证其 CRC；UEFI/native 身份、SID/CB、持续映射和所有权仍 UNKNOWN，无写入授权。原始/派生记录 `.cache/android-sysfs-20261112-113131/` ignored。

**OS/SystemOS 主机准备（独立 verifier PASS）**：verifier `ses_e324d9012ffegEvKQS6ClPF2l3` 核验 DMG 完整 hash、manifest 和 APFS UUID；verifier `ses_e3248e668ffesoy4RUd4iZFKvA` 核验 9382658048B SHNGROOT v1 中间镜像的流式 SHA-256、header checksums、两窗口原始内容 hash、对齐/边界及 zero padding。镜像由非原 IPSW 本地虚拟 ZIP 构建，不含 policy/Data，不可发布或刷写；摘要和限制见本地 ignored `out/userdata-prepare-20261112-b/README.md`，旧并发失败见 `out/userdata-cdn-20261112/REPORT.md`。board 当前 UUID 属于 restore；不提升阶段。

**当前路线（2026-11-12，静态与机械已验证）**：临时 ShengUfs 默认关闭的 `Hci30Legacy` 精确 0x300 选择及 OCS 低四位离线适配完成，reviewer `ses_e32026e5fffeiZbbCNp7CjWNNd` 静态 PASS、verifier `ses_e31f9ebfdffeUJH1044vdqoHrc` 机械 PASS；本增量无新增高风险跨模块变化，不需 deep。材料见 ignored `.cache/hci30-layout-ocs-20261112/`。不证明本板兼容或 DMA 准入；生产 NoContract、无 issuer、未部署。同次有效映射、producer 排除、队列控制、DMA 退役与 backing 持续机制仍缺；旧 reuse gate A/D5 不变，UFS 持久目标未达成。

历史离线 UFS 采集检查点：见 [采集设计](docs/ufs-handoff-capture.md)；纯主机合成判读器 self-checked，实际捕获挂点和完整输出通道未闭合，已停止扩展，不具备上机准备状态。

**2026-11-12 当前检查点**：24r 已单次实机执行并以 VER300 INCOMPLETE 终止，claim 已消耗；Android 身份和 root 的后续实查见上方。历史「未上机」文字均为执行前快照。旧 reuse gate A 仍仅 HCI21（0x210），UFS userdata 持久根及设备内载荷是终态主链；RamBlock 仅临时取证，不能满足断电重启后可交互的目标。保留现有版本诊断候选及验证状态，不重放 claim、不追加仅终止的探针，后续方向由主控整合。等级不提升。

**Restore 内容只读抽查（self-checked，非完整文件系统遍历）**：既有 `/home/wh1stl3/scratch-apfs/inspect_apfs.py` 校验 packed 与 raw 字节一致及 APFS checkpoint/superblock 校验和：单个 `ramdisk` 卷，role `0x0`，容器 45056×4096 = 184549376 bytes；free 未测。原始 APFS 中完整 binary plist 的 `com.apple.restored_external` 指向 `/usr/local/bin/restored_external`，RunAtLoad true，stdout/stderr `/dev/console`，未见 stdin 配置；这不是输入或持续交互证据。原始字符串亦出现 `mount_tmpfs`、`/System/Library/dyld/`；不是完整服务、shell 或依赖清单。23r 用户日志曾见 `mount_tmpfs /mnt5`；具体写需求未知。板级 DTS `chosen` 为空、共享 QUP 节点 disabled；官方 `VirtioMmioConsole` 为 QEMU 用，未证明 enuma 有 UART/USB/键盘输入。须另行建立真实双向通道，不能将屏幕日志或固件按键当 XNU 输入。没有构建新候选或进行设备操作。

## 历史检查点（以下当时状态与计划不代表当前下一步）

以下 24r/23r 执行前候选、native/prelink 和授权表述均为当时快照；实际执行与当前路线以上方进度块为准，已消耗 claim 不重放。后续单次观察不自动提升正式阶段验收。

**24r observation-only实现完成 + deep静态审查（2026-11-11，self-checked，仅主机；无设备授权）**：默认0 `NATIVE_UFS_OBSERVATION_ONLY` 变体已实现（为1须 diagnostic 与 external-provider 均1，非法值/组合 `#error`；入口仅 `native-ufs-observe-reuse=1` 且 root/probe 缺席），o=1 的 `-Werror` unused 阻塞按既有条件编译块处理。官方矩阵 NEW exit0：4 默认格、4 显式 o=0 格、o=1 合法格（archive `82811fc3…`、215 undefined、旧7缺符号零引用）、3 组合拒绝、2 非法值拒绝；组件guard 54/624、host 633/639。交付 ignored `.cache/ufs-observation-only-20261111/`（source-snapshot、`increment.patch` `51c851e1…05321a`、evidence.json、SHA256SUMS）；patch 在 fix2 干净基线 apply 后逐字节重现。**实现只在临时 ShengUfs 工作树与本地 `.cache` 证据中，未进入本仓源码，也未提交/推送远端。** 全部 self-checked，未独立验证；无24r设备授权。deep `ses_e35de8053ffel32m1bGoaREoKE` 判 **CHANGES REQUIRED 仅证据/措辞，源码 completion 正确、无须改源码**：①identity/`explain_default` 只在 external=0 两格（`scripts/build-enuma-ufs-store-matrix.py:114-126`），external=1 与 observation 格仅符号集合（`scripts/build-enuma-ufs-observation-matrix.py:68-73`），不得称四格函数体等价；②o=1 准入后 `ufsReuseDiagnostic`（`NativeUfs.cpp:194-225`）noreturn，异常/摘要失败/正常摘要均经 `ufsReuseFinish`（`:188-192`）IOLog+永久 `wfe` 驻留，不 panic/reboot/正常继续，`:1848-1849` 不可达；诊断仍有 GCC/HC/SMMU `mapPhys` 与 OSSharedPtr 映射分配（`:207/213/218`），写路径是编译期不可达而非“无写代码”，单CPU驻留不阻止其他CPU/固件/DMA，watchdog 仍可能复位（`:185-187`）；③host 测试未启用 o=1，不构成动态覆盖。evidence.json 已按此收窄并重算 SHA256SUMS，源/patch 快照 hash 未变（NativeUfs `3fe914…`、RootCommands `96fe71…`、RootQueue `84d904…`、patch `51c851…`）。无 native/prelink/link-map/payload/boot、无 personality/PMGR-observer 重绑定、无24r候选/入口；不升级等级、不称上机通过。下一步独立 verifier 在 NEW ext4 输出复跑观察矩阵（不得 `--archives-from`）、组件 guard、patch apply 重现及 record/diff。下方为历史检查点。

**24r此前检查点（2026-11-11，self-checked，真实链接阻塞；已由上方 observation-only 结论取代）**：已由成功23r记录定位resolved config，官方defconfig/status/archive-plan闭包完成；仅UFS编译开关变化，Virtio和owner-root仍关闭，storage补官方依赖记录后record check0。实际双宏=1 ShengUfs及PMGR archive已构建，最终native链接首缺`_boot_progress_poll`及6个正常VerifiedRoot路径符号，停止不凑stub/策略/启Virtio。11个真实输入archive强符号无重复、六store唯一EnumaRamBlockStore.o；1010对象+11archive未提供缺失符号，23r原hash不变。完整输入及限定dry-run恢复链接argv、供deep裁定的诊断专用fail-closed裁剪问题见[24r记录](docs/ufs-24r-diagnostic.md)。无新native/prelink/map/payload/boot/入口，不可上机；等待主控/deep明确方案，不升等级。下方是历史检查点。

**24r部分主机准备（历史，2026-11-11，self-checked，未上机）**：设备侧仅启ufs/不启PHY的ADT等价门禁通过，原GIC物理地址/长度与CPU/中断属性保持；真实BCM2837预处理排除pe_fiq的另一GIC路径，ArmCpu从ranges+reg映射intc。ShengUfs组件/双开关wrapper及唯一观察参数已写但未构建；首次隔离准备因runner假定的已解析`.config`路径不存在，在kernel/prelink调用前停止。无24r候选/包装/单次入口，不可上机；当前board/defconfig为未完成集成，不是放行配置。首阻塞、证据与预先判读见[24r记录](docs/ufs-24r-diagnostic.md)。不改基座/pin/共享仓，不触旧claim/23r/22r，等级不升；下一步先只读确定真实配置路径，最终审查/验证及当轮设备授权仍须完成。下方是此前检查点。

**历史：方案D fix2 archive/host范围完成，self-checked，当时待独立verifier+deep增量审。** 经主控窄许可，同一默认0开关`NATIVE_UFS_EXTERNAL_STORE_PROVIDER`条件编译六个store导出及其专用helper/state，保留RamBlock空后端和共享log/geometry，无target禁警告或transport函数体修改。最终源码四archive实际重编通过（不复用archive）；默认仍87个globals/六store，external为81个/零store，与RamBlock合并的全强符号扫描无重复。真实空后端+RamBlock guard矩阵每诊断设置64组合，633/639原诊断用例同时重跑通过；guard54/624复用未变证据。默认对象差异已精确定位为45处panic源行号MOV和DWARF路径/坐标，不误称仅ar mtime；新实测hash与完整patch `91500f6c…4cdee4d`、旧失败历史见[实现记录](docs/ufs-reuse-diagnostic-implementation.md)。未改RamBlock/archive、活动board/defconfig/DTS、基座/pin；无24r链接/候选/入口或设备操作。候选阶段最终native/prelink/map唯一性仍须另验。

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

## 历史快照：固件输入取证与第 6 步候选

以下候选矩阵和阶段 3 输入表是当时快照，不是当前配置或下一步；当前状态见顶部进度块、`board.toml` 和 `porting.toml`。

`scripts/enuma_firmware_inputs.py` 已从备份（`decisions.md` D6）单文件取用并校验：

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

## 历史快照：阶段 3 就绪度分析（kernel/package/payload）

第 7 步 bring-up 阶段 3 首次需要的输入（逐项，缺一不可）：

| 位置 | 内容 | 现状 |
| --- | --- | --- |
| OS profile 补丁 | `ipados-17.7.11-21H461` 的 `patches/xnu/series` 补丁与 TODO（`early_security_init`、`text_fixups`、`product-id`、`artwork-device-subtype`）清点 | 待读 `UniXNU/docs/zh/building` 与 `concepts/payload` 后清点 |
| `[payload] dram_size` | 实机 `/memory` 或 SMEM 取证（RamManagerDxe 映射 `0x80000000-0x280000000` = 8 GiB；已写入 `0x200000000`，2026-11-09 阶段 3 上机通过 ABL 启动，但该单段 span 非连续可分配内存证明） | 已写入，阶段 3 上机通过 |
| `[payload] kernel_args` | `native-ufs-root=1`（路线 B，见 `../../docs/decisions.md` §4） | 未加 |
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
python3 scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe
```

## 文档

- 固件日志抓取（ramoops）：[`docs/firmware-log-capture.md`](docs/firmware-log-capture.md)
- 移植流程：<https://unixnu.com/zh/porting/steps>
- SoC 支持：<https://unixnu.com/zh/porting/soc-support>
- 设备仓规范：<https://unixnu.com/zh/porting/device-repository>
- 设备树：<https://unixnu.com/zh/porting/device-tree>
- 启动验证：<https://unixnu.com/zh/porting/bring-up>

## 约定

治理规则见 `../../docs/context-brief.md`。Apple 派生产物只留本地 `out/`，不上传 GitHub；ECID 等设备种子只经命令行或 Git 忽略的配置传入。`scripts/` 下的历史审计工具产生于 format 1 布局，其中部分引用已不存在的 `firmware/`、`diagnostics/` 目录，接入前先核对。
