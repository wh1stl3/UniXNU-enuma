# UEFI → 原生 UFS：执行边界与 backing 类别检查点

状态：**self-checked 静态证据，未实现、未运行设备、未独立验证**。deep 对上一版设计判定 CHANGES REQUIRED；本版撤销必须在 EBS 前实现全局 Stop 的要求。输入固定 FD `e524988b…a71bf1e`、UFSDxe `ffeaed46…a88b8dc9`；原始指令/PE 偏移见 ignored `.cache/ufs-handoff-boundary/execution-backing.json`、`identity-and-events.json` 和 `.cache/ufs-protocol-index/callchain.json`。本检查点不改变 gate A。

## 表 1：成功 EBS 后相关执行可达性

| 入口 / 执行域 | 已见静态链 | 成功 EBS 后结论及边界 |
|---|---|---|
| BSP 正常控制流 | 固定 Core `DxeMain.c:778–846` 在 EBS 通知后关 CPU interrupt、清 system-table BS、清零 gBS；DarwinBoot `812–825` 成功立即调用 DarwinEnter，`Entry.S:10–52` 屏蔽异常、维护缓存、关 MMU 后 `br x1`。 | **条件性支持**：所审成功返回的 BSP 控制流不再调 UFSDxe；这不是其他 CPU/硬件域全局证明。失败/重试不属于此结论。 |
| UEFI 事件/队列 | `1a640` timer callback `4008` 可经 `4210→3ec0` 提交；`5de8/60c0` 是 EBS 回调，后者调用 `603c` StatusCode Locate。Core 在 map 成功后通知 EBS，通知期间仍可能执行其他已挂起 callback；`CoreRestoreTpl` 可派发 pending。 | EBS **期间** callback 提交不自动否定交接。关键是成功返回以后该 BSP 的正常事件派发是否终止，以及 native 首次操作时请求仍 pending 要拒绝。硬件 timer 停止不等于通知期间已排空。 |
| 已安装 protocol | `2aa4` 安装 BlockIo（Read `15f4`/Write `16ac`→`3700`）；`2c6c` 还安装 GUID `ef6fd01d-8861-4132-834e-decc0ff1aafa` 接口，其方法合约未知。`8b1c` Locate 的 `9a10db8c…` 不是 BlockIo。 | 成功后已审 DarwinEnter 路径不再调用 protocol；并未穷举已获缓存接口的其他执行域，也不能把未知私有方法称 Stop。 |
| runtime / VA event | INF 标记 `DXE_RUNTIME_DRIVER`；`5e88/6120` 注册 virtual-address-change 回调 `5df8/60a0`，分别走 `5e24` 转换相关指针；`5eec/6184` 为 EBS 回调。 | runtime 类型本身不证明有能提交的 runtime service；VA callback 的调用取决于后续 SetVirtualAddressMap；所审 DarwinEnter 无此调用，**未证明整个内核或外部固件永不调用**。 |
| AP / 其他控制域 | 本 PE 未含本地 EDK2 MP Services GUID `3fdda605-a76e-4f46-ad29-12f4531b3d08` 原始字节；现有事件索引及调用证据没有识别出本模块 AP 启动调用。 | GUID 不存在并非动态生成、间接派发、其他 AP/安全域或控制器自主 DMA 不存在的证明。**该边界尚未闭合**，需有限平台所有权证据而不是泛化搜索整个固件。 |

结论：成功 EBS→DarwinEnter 的 **BSP 局部执行边界有静态支持，系统级无新 producer 尚未证明**；selectedVolume 不明不妨碍这一控制流结论。不能把 `ExitBootServices` 中发生的 I/O、成功后仍在飞 DMA、AP 或外部执行域混为同一问题。

## 表 2：backing 来源与失效（按类别）

| 类别 | 固定 PE 中的实际来源 / 路径 | 生命周期与窗口排除结论 |
|---|---|---|
| 请求列表和 task 区 | `e0ec` 请求 `0x1400` 字节→`13efc→7fec` 传 memory type 4（本地 UEFI 头的 EfiBootServicesData）→`7fbc→7f6c→7c9c`；`7c9c` 可复用匹配 type 的内部块，也可在 `7dbc/7ddc` 调 gBS AllocatePages(+`0x28`)；`e0fc–e11c` 按 0x400 对齐，`context+10/+18` 与 `+20/+28` 分别写相同两个相隔 `0x1000` 的指针，再写寄存器 `+4050/54`、`+4070/74`。 | 新分配分支的 type 是已知，不等于所有复用块目前仍 allocated。`e194` 初始化错误返回本局部未见配对释放，但不证明其他调用者不会释放；是否存活到 DMA 结束、重用/全局 teardown 和具体 PA/IOVA 仍未闭合。 |
| command/response、PRDT | `e28c:e2bc/e2d8` 取 `context+20/+10`，写请求对象 `+8/+10/+18`；`e314–e328` 分别加 `0x100` 再写请求 `+20/+28`。`d940:da94–dafc` 按请求长度构建 PRDT，`dbb0` 进行门铃式写入。 | 指针算术和提交已证；各地址是 CPU VA、PA 还是 IOVA 不能仅凭相等赋值决定。共享上述 backing 的分配/映射和错误生命周期，完整保护未知。 |
| 数据 / caller buffer | BlockIo `15f4/16ac` 将 caller Buffer 传 `3700→2298/2408`；分块分别到 `91b8→9798` / `91f4→9a2c`，`9858/9aec` 将 caller 指针写命令对象，`c0c0–c0d0` 到请求 `+78`，`dabc–dae4` 写 PRDT。 | 所审路径**直接传播 caller buffer**，没有证据将其全部替换为持久 bounce；调用者可能是文件系统、loader 或其他 driver，实际内存类型、所有权和正常完成后释放未知。超时未确认停止时绝不能假设 caller 不会释放/复用。 |
| 映射/缓存及 bounce | 分配成功后 `7df8` 调 `[global 1a958]+38`、`7e2c` 调同表 `+40`，状态/失败分支 `7eb8–7ee0` 可调 gBS FreePages(+30)；`db40/db58/db9c` 和 `dd6c/dd88` 调 cache helper `13bf0`。 | 表通过 `67d0–67ec→6484` 按 GUID 获取；`+38/+40` 的具体契约、映射结果/解除、cache 能见性及是否还有其他 bounce **UNKNOWN**。`7eb8–7ee0` 是分配/配置错误路径，不能泛化为正常 teardown。 |
| timeout / task / unmap | `dbec` 负返回到 `c1f8–c20c` 调 `dda8`；`dda8–ddbc` 向 base+`405c` 写掩码补码后直接返回，所审窗口无确认读回。task 的初始地址由 `context+18/+28` 设置。 | 该写不证明取消完成、DMA 排空、页可释放；task 命令的 producer/清理和成功/错误后 mapping unmap 未闭合。停止点：`7df8/7e2c` 函数表 target、task 实际缓冲调用者、timeout 后 caller 释放及 teardown。 |

**完整类别保护尚未成立。** 尤其 caller data 与映射/timeout 生命周期无足够证据。DarwinBoot `419–440,516–529` 只从 ConventionalMemory 分配 EfiLoaderCode 窗口，XNU `arm_vm_init:1837–1854,1964–1970` 管理该窗口：如果所有仍活跃类别确实已分配、非 Conventional 且与窗口不交，则可条件性排除，无须默认新增范围 ABI；目前不能把 type 4 的一条分支推成全部类别。`mapperNone` 也不构成单独的安全分配域。

## A：优先成功 EBS 执行边界 + native 局部接管

设计候选，**不是已证明可部署**：成功 EBS 后依赖已核定 BSP 控制流边界，并以有限平台证据排除 AP/其他域继续提交；native 在任何会复用旧 backing 的分配/清零前满足类别保护。之后对硬件执行局部、fail-closed 的采纳，不要求 EBS 期间队列从未提交或预先新增全局 Stop。必须分别满足：

1. **无新 producer**：成功 EBS 后所涉执行域不再提交；不能从一次空 doorbell 推断，也不能把 timer cancel 当全部域同步屏障。若特定 producer 可在 EBS 后存活，才设计最小受审控制接口或替换该 producer。
2. **当前无 pending**：固定 ShengUfs `e2b32cc` `RootQueue.h:18–31` 检查 TR doorbell `0x58`、TM doorbell `0x78` 为零并拒绝错误状态；任何 pending/错误或证据不全时拒绝接管，不抢清并继续。
3. **TR stop/readback**：同文件 `33–39` 禁 interrupt、写 TR run/stop `0x60=0` 并回读；它**不停止 TM**，空 TM 不等于 TM 引擎已停止；不得据此盲写 `0x80` 或声称 TM 已停。TM 后续状态/使用要求须基于现有平台契约和实际下一步，缺证则拒绝。
4. **映射变更前**：要求无新 producer、无 pending、相关 backing/映射仍存活，且所要修改的 SMMU 映射及其它使用者具备独占/兼容证据。TR stop 不自动证明 TM、外部设备或互连缓存已排空。

固定 `NativeUfs.cpp hostBringUp` 在 `hostStopQueue` **之前**分配并清零自己的新 DMA；这不自动证明重叠或危险：若窗口及所有仍活跃旧 backing 的排除前提已在该首次 allocator 前成立则可能安全，否则必须先解决保护。成功/失败路径均不得把未知旧对象视为新驱动私有内存；timeout 不自动证明 DMA 停止。

## B 与下一具体分支

只有类别级保护不能从实际分配/有效期契约建立、且确有旧页可被窗口或更早 allocator 复用时，才考虑最早保留/范围传递；覆盖 descriptor、command/response、data/bounce、task、映射/页表等全部仍活跃类别。B 涉 ABI/pmap/DMA，非现成实现；不能只传 UTRD。

**推荐下一分支：针对 allocator 类别设计最小采集，而非继续泛化 Stop 逆向。** 在另行授权的 UEFI 合法上下文，使用预分配记录缓冲并避免 UFS 日志，采集 `e0f0` 分配/内部复用的 EFI type、PA/长度及 `1a958+38/+40` 输出与有效期；关联最后读请求 caller data/bounce 的来源、EFI type、完成或 timeout 后释放时点；记录 TM backing、窗口及逐段不交。成功 EBS 后以 native 可安全读取的既有状态判定 TR/TM 和 stop readback；未知/失败即拒绝。采集计划不是可执行设备入口，不证明外部域独占。若采集证实某 producer 能跨 EBS 提交，转**局部控制接口**；若证实可复用重叠，转**最早保留**；都排除后才评估局部接管。

候选改动仅是未来审查范围：设备 UEFI 的选件/受控 provider（确有存活 producer 时）、DarwinBoot 的必要检查或失败路径、ShengUfs `NativeUfs.cpp`/`RootQueue.h` 的局部接管与必要拒绝；当前不改固件/XNU/DMA/ABI。旧 `.cache/ufs-handoff-design/model.py` 模拟的是更强的 pre-EBS gate **假设模型**，不证明、也不是新方案必需条件。DMA、映射、跨模块并发/ABI 改动需另行明确 brief 和专项审查。
