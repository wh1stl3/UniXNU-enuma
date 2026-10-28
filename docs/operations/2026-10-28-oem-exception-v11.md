# enuma exception-v11：异常现场与镜像归属

本轮用户要求继续分析异常出口，定位 PC/ESR/FAR 和所属镜像，完成验证并编出下一版；文档最后统一发布。工作仅在 `D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display` 及其 firmware，未操作设备。共享主线只读，R027、v6–v10 旧镜像/资格保持原字节；旧源码准入失效不改写旧资格。

## 现有证据与可操作卡点

v10 的低/高对照基线 6.164331503..6.361941059 秒，目标原点 8.126917412..8.260633677 秒落在 code1 窗口；用户确认三个回合均未按键、自行返回 Android、没有新画面。此为间接异常出口嫌疑，尚无直接异常日志，仍有未插桩复位、前缀时延变化及时间码别名解释。

固定 Mu 的 `CommonCExceptionHandler` 在没有注册的处理器时进入 `DumpCpuContext`。原 v10 hook 在常规状态打印之前直接等待/复位，没有接收保存的上下文，因此从旧证据无法恢复 PC/ESR/FAR，也不能断言属于 DisplayDxe 或 Clock/HAL。v11 针对这个观测缺口；没有根据时长猜测修补 OEM 指令、跳过真实调用或合成 EFI_SUCCESS。

## 实现及边界

- 新独立 scope `oem-exception-v11`，一个新 session/trial。保留 v10 OEM 运行期间 RAM-only、真实 Core 返回、整轮 DXE，以及真实成功后原厂 GOP QueryMode/SetMode 的门控路径。
- 异常 hook 接收真实 `EFI_SYSTEM_CONTEXT_AARCH64`，先设置重入锁、屏蔽 DAIF，再复制 Type/ELR/ESR/FAR/LR/SPSR。使用保存现场中的 ELR 作为 PC；不以异常处理器当前寄存器替代原故障现场。
- 先尝试原始现场页，再查 UEFI Debug Image Info Table，最后显示归属和附加上下文。表更新中、非法地址、无匹配、多重匹配、超限均不得输出猜测归属。
- 所有元数据读取先检查既有 EL1 恒等映射和 normal-memory 属性，仅允许原固件 RAM 窗口；最多 64 个配置表、128 个镜像、8 个路径节点/256 字节。读取前后核对调试表头，不调用分配、协议定位、格式化或 Boot Services。表外或范围外地址拒绝，不能据此认定镜像不存在。
- 异常输出复用既有继承路由、整帧 CPU 映射属性校验和 ROI 保存/绘制/读回/恢复/读回。每页重新确认路径；ROI `(64,96) 320×160`，每页 8 秒、最多三页。任一页失败终止后续页；递归异常直接复位，不能保证恢复像素。没有新增映射、修改内存容量或重新初始化显示控制器。
- 仍是 75 秒宿主恢复观察上限，无独立 watchdog 或持久异常存储。v11 不属于时长分类 scope；不安排新的低/高时长对照，也不将返回秒数解释为 PC/GOP 成功。

## 三页读法

每页五行，均带同一个完整 session；十六进制字段均为 16 位。`E11/E12/E13` 是页标识，不是驱动状态码。

| 页 | 第一行 C 后 | O 行 / G0 行 | S 行 / G1 行 | C 行 / S 行 | 末行 |
|---|---|---|---|---|---|
| E11 | exception type | PC/ELR | ESR | FAR 原值 | session |
| E12 | owner flags | image base | PC RVA | image size | session |
| E13 | LR | GUID 前半 | GUID 后半 | SPSR | session |

owner flags 低 8 位：0 unavailable、1 unique、2 no match、3 ambiguous、4 updating、5 invalid、6 limit；bit8 为 GUID 有效。GUID 以标准规范文本拼接两半，不能用内存字节顺序直接拼。

`scripts/decode_oem_exception.py` 接收人工核对后的 `{"pages":[[五行],...]}`、本次 qualification.json；拒绝跨 session、截断、乱序及 PC/base/RVA/size 不一致。保留 FAR 原值并按 ESR EC/FnV 标注 abort 适用性；不能把所有异常的 FAR 当成有效故障地址。完整 GUID 和 ImageSize 可与本次实际 FD 镜像清单匹配，得到模块名、固定 PE 摘要和 PC 所在节；这不是运行时镜像内存完整性校验。

## 验证与构建记录

最终产物和机器码检查结果在本轮完成后汇总于 `reports/enuma-oem-exception-v11-20261028.json`。本地原始输出根 `out/oem-exception-20261028/`，不上传镜像或 OEM 二进制。

已保留失败输出：check1–3 为头文件/依赖接入修正，check5 为宿主 include 路径；build1 在新补丁复制前缺少 staging patches 目录，build2 被严格宏重复定义检查拒绝。均修正来源后使用新目录，未把失败记录改为通过。Python 初轮未区分 v11 与纯时长 scope 的测试断言已修正并新增三页预算负测；Windows 原生全套测试的 WSL 路径夹具不适用，正式回归在 WSL 执行并保留两者日志。

## 上机后的判读与后续修复顺序

1. 若取得 E11：先校验 session 和完整字段，按 ESR 分类同步异常/指令或数据 abort 等；先检查 PC 附近真实指令，再解释 FAR，不能先认定空指针。
2. 若 E12/E13 提供唯一归属：与新 FD 清单核对 GUID/大小，计算 RVA 并定位实际模块指令。OEM Clock/HAL/DisplayDxe 按真实故障调用及寄存器语义分析；若落在本地 Core/诊断组件，优先修复本地缺陷。
3. 若有 E11 但归属未知：保留原始 PC/ESR/FAR；检查调试表忙、地址策略拒绝及表是否覆盖该镜像，不放宽到任意物理读。当前页未包含全部通用寄存器，必要时下一独立候选按已定位指令补充操作数现场。
4. 若仍无页：不能否定异常，也不能认为 GOP 成功；候选解释仍包括异常发生在此处理器之外、路由/CPU 属性拒绝、取证路径递归故障或未插桩复位。禁止重复消费同一 trial，先结合媒体和独立恢复证据分流。

任何下一次实机须重新确认当轮拍摄/人在场恢复、精确资格与单次账本、即时身份和原分区/备份；不沿用 v10 就绪，不 flash/erase/改槽。网络发布按用户要求统一放在离线工作完成之后，不作为本地编译的阻塞条件。

## 参考

- 本机固定源码：`Mu_Basecore/UefiCpuPkg/Library/CpuExceptionHandlerLib/AArch64/CpuExceptionHandlerLib.c`、`MdeModulePkg/Core/Dxe/Misc/DebugImageInfo.c`、`MdePkg/Include/Protocol/DebugSupport.h`。
- [UEFI Debug Image Info Table](https://uefi.org/specs/UEFI/2.10_A/18_Protocols_Debugger_Support.html)：表更新状态和加载镜像信息结构。
- [Arm ESR_EL1](https://support.arm.com/documentation/111107/2026-09/AArch64-Registers/ESR-EL1--Exception-Syndrome-Register--EL1-)：异常类与 FnV 解释。文档不替代本机执行证据。

## 最终离线交付

- 完整 build3 成功，qualification2 通过，Boot v3 打包/解包逐字节一致；镜像 3153920 字节，SHA256 `73d1327f75f9123cd13898c24cd005c5db91e8e244132dfcba1364bde1ebaaa4`。
- 镜像：`out/oem-exception-20261028/qualification2/image.img`；资格 SHA256 `dc6d274ccbaf798cbdd182a2a28df772700ff52f1cc2a9549a56d981ca861e19`。trial `3ffbbf8d-21f5-4a1f-ae58-a84e56596c0f`，session `0x75ffd74f0d039ec6`，未消费、未执行。
- 固件提交 `0718922a03e0854005887c99c1a7fb3b9257e375`。build3 基于 2c18bc6 的工作树快照，之后提交相同固件来源；不是提交后重编。2489 项当前来源绑定、72 个实际 FD 镜像及最终离线准入通过。
- 61 项 WSL Python 测试；check7 覆盖真实 snapshot/owner/flow/prepared-only pixel 的 ASan/UBSan 和严格 ARM64；277 处链接指令删除负测通过，含真实上下文偏移、重入锁、DAIF、顺序/失败分支、session 常量及映射查询/恢复。删除负测只证明所选检查有效，不是全程序或硬件证明。
- qualification1 保留失败：LTO 改变 EnumaStartingImage 相对寻址位移；改为解析 ADRP/ADD/LDUR 并核对真实符号目标，拒绝错误目标；未修改固件或放宽真实身份门控，qualification2 重验通过。
- 20 份历史镜像/资格摘要通过；没有设备命令。本次实际故障 PC/ESR/FAR 与归属仍待新实机页，不能把 ArmCpuDxe 的处理器 RVA `0x6718` 当成故障 PC。
- docs/STATUS、HANDOFF、原交接入口和本操作记录已统一更新。发布结果在本地 publication.json 及最终答复记录；上传范围仅源码与脱敏文档。
