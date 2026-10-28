# v14：并行核对参数来源与运行时地址翻译

2026-10-28。用户要求“下一步把两条线一起核对 出新包”。本轮只做离线源码/二进制分析、验证及新包制作，没有设备动作。共享主线只读、R027 冻结。

## 已知故障与两条线的结果

v12/v13 均在原厂 DisplayDxe RVA 0x2b140 执行 `stur w8,[x9,#-172]`，ESR=0x96000047、FAR=0x0aeb0004；v13 新增静态 VBIF 描述符未消除实测 L3 translation fault。不能把描述符存在当运行期映射生效，也没有证据把前置参数排除。

参数线：精确原厂 PE 摘要 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425。基址来源可追到 helper 0x1bd58 的 EFI_HWIO_PROTOCOL.MapRegion("MDSS")，GUID 9e61de7c-9927-4f28-9f3d-320705d81801，方法位于协议 +8；经 0x16a84 调用、结构传递及 0x156e0 setter 写到全局 RVA 0x467d0。公开 Qualcomm 接口镜像 [EFIHWIO.h 固定提交](https://github.com/Rivko/android-firmware-qti-sdm670/blob/20bb8ae36c93fc16bbadda0e0a83f930c0c8a271/boot_images/QcomPkg/Include/Protocol/EFIHWIO.h) 的 GUID、结构偏移与参数形状相符。这是不同 SoC 的公开代码镜像，仅用于接口比对，不能代替本机运行值。

直接调用者 0x263b8 从 ID=0 开始、flags=1，并按硬件信息 +72 的 count 循环。helper 0x2b398 使用实例偏移表 RVA 0x4b3b8；无效 ID 返回零偏移。故障地址为 `base + instance_offset + 0xb0004`。当前 FAR 只约束前两项之和为 0x0ae00000，不能分别证明基址、实例偏移或 ID 正确。X0 在故障前已恢复为实例 ID；它不是该 helper 的返回偏移。静态直接调用者也不是本轮实际调用栈证明。本轮未发现可确认的直接 ABI 错位，不修改原厂参数或 PE。

映射线：把本次 build2 的实际 ArmMmuLibCore.c 建表部分及 MemoryMapLib.c 放入宿主重放，保留描述符原顺序和实际属性；仅替换分配器、寄存器、cache/TLB 操作。全部活动描述符处理后 VBIF 三页仍为 identity mapping 且 AF 有效，DSI0/1、DISP_CC 也有效。省略 VBIF 的反例按预期失败；27 个分配失败点均返回资源不足且释放页表。ASan/UBSan 通过。这个结果降低“这组分段描述符必然互相覆盖”的嫌疑，不验证硬件 MMU、活动 TTBR、后续修改或 TLB。

## 新包行为

scope `oem-exception-context-v14`。保留 v13 的地址范围、原厂 PE、真实 CoreStartImage 返回、完整 DXE 分派及门控原厂 GOP 路径。新增逻辑只在既有未处理异常出口执行。

先锁递归保护，保存原始 EFI 异常上下文，再在首次像素/owner 访问前保存 X0/X8/X9/X10/X20/X21、CurrentEL、TTBR0/1、TCR、SCTLR。只有 EL1、SCTLR.M=1 且 TCR.HA/HD 均为零，才对 FAR 执行 AT S1E1R/W，读取两次 PAR 并恢复原 PAR；否则 ProbeValid=0。不读目标 MMIO，不软件遍历页表指针，不调用 Boot Services、GOP 或格式化输出。没有增加 ramoops 留存。

| 页 | 头部 C / O / S / C 三数值行（E13 为特殊格式） |
|---|---|
| E11 | Type / PC / ESR / FAR |
| E12 | Owner 与 GuidValid / Base / RVA / Size |
| E13 | LR / GUID 前半 / GUID 后半 / SPSR |
| E14 | X0 / X8 / X9 / X10 |
| E15 | TTBR0 / TTBR1 / TCR / SCTLR |
| E16 | CurrentEL 原值 OR (ProbeValid<<8) / PAR-read / PAR-write / X20 |

每页末行仍是本轮 session。六页各四秒，总显示停留 24 秒；像素事务由三次增到六次，不声称总扰动完全不变。每页独立验证现场、保存并恢复原像素；任一页失败就停止后续页面。递归异常立即 cold reset，仍可能无页。75 秒是主机观察期限，不是独立固件 watchdog 或保证返回。

## 验证与构建记录

v14 已完成 build2/qualification2：同时核对原厂参数来源和实际 MMU 建表代码，新增故障寄存器与异常后地址翻译取证。73 项 Python、8 组宿主检查、354 处链接指令删除、36 项映射变异、28 处参数指令删除和 27 个页表分配失败点检查通过。2501 项来源绑定；软件就绪，trial 未消费，尚未上机。

- 镜像：`out/oem-context-20261028/qualification2/image.img`，3153920 字节。
- SHA256：`2e3e6814fac86e6a7da35887f03c50abf0e6986bdf7d8d4a22949621a2961a4c`。
- 资格 SHA256：`946ba1408495899bea81980fc896df487d2b81d7569d552607545496433ec067`。
- FD SHA256：`c749df261bc12c9aba52fefb33688e68f91e0befce4da513e8708e120dfbb720`。
- trial：`4dd84d0a-d44f-4230-9747-5baae31b61be`；session：`0xffffaabcc96a520b`；未 claim/未发送。
- 固件提交：`07c9bf6c6c2bf924d9fb5c38d3231d024266adbb`。使用逐文件绑定工作树快照构建；提交发生在构建后，不称提交后重编。

宿主异常流程同时覆盖旧三页与新六页、各页失败短路、递归/空上下文，以及后三页全部字段逐值输出；像素事务覆盖失败恢复，ARM64 严格编译通过。最终 ArmCpuDxe 机器码核对保存上下文的真实偏移、六次输出顺序、EL1/M/HA-HD 拒绝门、AT 两种操作、PAR 恢复、session 和四秒 hold；逐处删除被拒绝。最终 FD 内原厂 PE、72 个镜像清单、SEC TE 与四条显示映射核对通过。

build1 在补齐 DSC 编译开关传递期间触发源码变化拒绝，已保留且不准入。build2 使用新快照成功。qualification1 通过后补强页面字段测试，最终采用 qualification2 重新绑定；两份镜像字节相同，仅最终资格可用。所有失败和中间目录保留。24 份旧候选/R027 镜像和资格摘要保持。

补丁写入显式 UTF-8 LF，变更补丁检查和隔离 apply --check 通过。既有 PixelTransaction.h 原本全文件 122 行 CRLF，本轮保持原格式，仅改一行条件；不对历史源码做整文件换行转换。

## 上机后的判据

1. 同 PC 时先检查 X9-0xac 是否等于 FAR、X10+X20 是否等于 X9，以及 X0 的实例 ID、W8 的实际写值；这些是故障现场值，不冒充函数入口参数。
2. ProbeValid=1 且 PAR 报翻译失败：证实采样时仍有翻译问题。结合 TTBR/TCR 再决定是追建立/切换、后续修改还是补早期对照；本包没有早期 TTBR 对照和叶项快照，不能直接判定“被谁改坏”。
3. ProbeValid=1 且翻译通过：检查异常前后时点、TLB/翻译制度等差异；不能据此推翻已采集的原始 ESR。
4. ProbeValid=0 或只有前几页：明确记录拒绝/证据不足，不把零 PAR 当成功。无页不能默认 OEM 内部故障。
5. 若 PC/FAR 已变化，重新按精确镜像/RVA 分流。Android 返回不证明 OEM 返回、全 DXE 或正式 GOP 成功。

本包目标是用同一次现场把两条嫌疑分开，尚不是已证修复，也不保证让启动链越过 VBIF。下一步只有取得现场后才选择针对性改动；不扩大 MDSS 窗口、不跳过原厂调用、不合成成功。

用户当轮“可以上机”已定义为正在录像且在场可恢复，届时不重复询问这两项；仍核对新资格、未消费账本、设备身份/分区备份/恢复条件，仅一次临时 boot。本轮未继承任何旧现场状态。原视频只落 Media-enuma，清晰内容独立判读，仅真实歧义再问。

源码和文档最后统一发布；发布状态与本地资格分开记录。公开资料的背景及限制见 [v13 页表研究](2026-10-28-oem-v13-page-table-public-research.md)。
