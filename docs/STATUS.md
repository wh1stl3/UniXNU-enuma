# 当前状态：已恢复，先校准诊断再定位显示访问

2026-10-24 Asia/Shanghai。离线实现已完成，待检查与构建；未启动新候选。

## 设备与证据

只读恢复核验已独立通过：enuma、Android boot_completed=1、root、原A槽、解锁；boot_a/vendor_boot_a 的设备和本地备份摘要均匹配原账本。证据 reports/enuma-recovery-reconciliation.json 与其 out/device-tests 回链。原21:06失败试验 result.json 保留，current.local.json 通过新核验更新为 recovered-android-boot-complete。此恢复事实不代表显示修复。

## 有效结论

- 还没有可见 GOP/白条闭环，未进入 XNU 或 iPadOS 用户态。
- 旧 delay20 的显示取数宏未进入 DxeCore 编译选项，默认值为0；头文件还有未启用分支的 STAT 拼写错误。相关历史时序不得再解释成寄存器值。旧驱动内 vprobe1..7 每次也只取 bit4..7，且主机基线遗漏额外2秒。
- detail16 在 GOP_QUERY 模式由精确返回 marker 在 CoreStartImage 返回后触发；不是 PE 入口前。不能沿用旧“上下文窗口已经定案”的解释。
- 像素路径先执行 cache Sync(dc civac)和 CPU Read，再 Write；像素实验不返回不能定位为写指令挂死。数值范围检查不证明 CPU/SMMU 地址等价，也不能证明未上电或缺映射。
- SimpleFb预读与部分成功有关联，未证明安全或一次性缺页机制。同一旧通道有失败记录，既往自动返回只保留为返回事实。

## 本轮实测（2026-10-24 22:49，新 value transport 通道）

| 笔 | 常量码 | 返回时间 | 结果 |
| --- | --- | --- | --- |
| zero1 | 0 | 16.991 秒 | 成功 |
| known3 | 3 | 25.503 秒 | 成功 |
| zero2 | 0 | — | **挂死** |

码 3 比码 0 多 8.512 秒，对 3 码×3 秒 = 9 秒的残差 0.49 秒，在 0.75 秒容差内——**"把值编码进复位延时再由主机反解"这条机制本身成立**，且全程不读显示 MMIO、不做像素或 cache 访问。但**同一候选（同一镜像、同一常量码）两次运行一次成功一次挂死**，零码重复性不成立，因此按既定判据**不得解码、不进入寄存器模式**。

这条负面结果同时确认了方法论：上一棒"单笔 22.365 秒即读出寄存器值 6"的误判，根源正是只跑一笔就解读数据而缺少重复性验证。

## 待隔离的三条路径

现有证据已经把范围切到三段，三者互斥且都能用同一套常量档通道观测（不需要读显示）：

1. **公共启动路径** — stage 10/11/12 的检查点，历史上全部成功，视为安全。
2. **驱动返回路径** — detail 16 的精确返回 marker 门，发生在 `CoreStartImage` 返回之后。**zero2 挂死正落在这里**：常量档的 value probe 只在驱动内 stall，真正的复位由驱动返回后的 marker 门完成。
3. **驱动内部路径** — LoadImage 与 StartImage 执行期间。**这一段至今没有任何独立观测点**，是当前最大的盲区。

隔离方法：让同一份常量档候选把复位点分别放在三段（驱动内自己复位 / 驱动返回后 marker 门 / 更早的公共检查点），比较三者的成功率。驱动内自己复位需要给 SimpleFbDxe 的 INF 补上复位库依赖，并同步修正固件仓的补丁登记与源锁。

## 新隔离候选与次序

新 value transport 使用独立 source/index/shift/code，不复用 step1..7；常量0无额外等待、常量3额外9秒，两者均不读显示MMIO、不做像素/cache访问。先按0/3/0同源校准，漂移>0.75秒或码点残差>0.75秒即拒绝解码；寄存器每码3秒、位移0..28独立选择。构建不等于实机通过。

主机工具默认离线校验，--execute每次只启动一笔；源码/文档干净且已推送，所有不可变FD/raw/image/构建/审计摘要绑定后才可运行；失败、模糊或中断冻结整个计划。下层恢复门禁保留。

1. **隔离驱动返回路径**：同一常量档候选重复多次，量化 zero 档的失败率；若"首次成功后必挂"，指向 fastboot/bootloader 状态残留而非固件逻辑。
2. **隔离驱动内部路径**：给 SimpleFbDxe 补复位库依赖，让 value probe 在驱动内自行复位，绕开驱动返回路径；驱动内能稳定完成即把挂死定位到返回路径，反之定位到驱动内部。
3. **公共启动路径复核**：用更早的 stage 检查点跑同一常量档，确认启动前段稳定。
4. 重复性成立后再做最小显示寄存器读取；若仍失败则停止追加并离线隔离。
5. 之后分离描述符/Sync/CPU Read/Write，检查实际FDT、页表/GCD与SMMU。新像素写仍需具体单次审查。
6. 复用现有FAT publisher、DarwinBoot、NativePrelink/ADT，再推进SM8250 UFS与用户态；不重写上游通用实现。

## 来源与边界

独立固件仓已从c45e52a快进到b63c9bd基线；后续新固件以config/uefi-source.lock.json为准。原Mu_Basecore递归脏状态保留，不使用reset/clean覆盖。UniXNU固定5fdbd5d；远端新HEAD仅作差异待审，不直接切换。

R-005 consumed；R-007像素单次已消耗，旧同号MMIO提案仅历史记录；R-008 retained-log/warm-reset pending，不启用。新内存字段、映射、verified和破坏性分区仍遵守AGENTS；本阶段不写像素/MMIO/分区、不启用保留日志，512MiB owned/51MiB heap/example=true/Boot v3不变。冻结的旧镜像不重试。

目标 iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB。已有源平台内核最终链接、donor闭包规划；未emit预链接镜像。64MiB配置FAT未接publisher，NativeUfs的SM8550参数未启用，EnumaScreen仅主机/对象检查。TWRP/UART未验证；相机用于有显示输出/恢复动作，保留原图并按实际方向旋转。
