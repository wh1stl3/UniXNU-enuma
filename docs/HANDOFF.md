# 交接：校准诊断通道与显示访问隔离

2026-10-24 Asia/Shanghai。离线实现已完成，待检查与构建；未启动新候选。

## 设备与证据

只读恢复核验已独立通过：enuma、Android boot_completed=1、root、原A槽、解锁；boot_a/vendor_boot_a 的设备和本地备份摘要均匹配原账本。证据 reports/enuma-recovery-reconciliation.json 与其 out/device-tests 回链。原21:06失败试验 result.json 保留，current.local.json 通过新核验更新为 recovered-android-boot-complete。此恢复事实不代表显示修复。

## 有效结论

- 还没有可见 GOP/白条闭环，未进入 XNU 或 iPadOS 用户态。
- 旧 delay20 的显示取数宏未进入 DxeCore 编译选项，默认值为0；头文件还有未启用分支的 STAT 拼写错误。相关历史时序不得再解释成寄存器值。旧驱动内 vprobe1..7 每次也只取 bit4..7，且主机基线遗漏额外2秒。
- detail16 在 GOP_QUERY 模式由精确返回 marker 在 CoreStartImage 返回后触发；不是 PE 入口前。不能沿用旧“上下文窗口已经定案”的解释。
- 像素路径先执行 cache Sync(dc civac)和 CPU Read，再 Write；像素实验不返回不能定位为写指令挂死。数值范围检查不证明 CPU/SMMU 地址等价，也不能证明未上电或缺映射。
- SimpleFb预读与部分成功有关联，未证明安全或一次性缺页机制。同一旧通道有失败记录，既往自动返回只保留为返回事实。

## 新隔离候选与次序

新 value transport 使用独立 source/index/shift/code，不复用 step1..7；常量0无额外等待、常量3额外9秒，两者均不读显示MMIO、不做像素/cache访问。先按0/3/0同源校准，漂移>0.75秒或码点残差>0.75秒即拒绝解码；寄存器每码3秒、位移0..28独立选择。构建不等于实机通过。

主机工具默认离线校验，--execute每次只启动一笔；源码/文档干净且已推送，所有不可变FD/raw/image/构建/审计摘要绑定后才可运行；失败、模糊或中断冻结整个计划。下层恢复门禁保留。

1. 完成主机/实际AArch64及FD审计、保存每份候选资格。
2. 文档和来源锁提交推送、即时身份/备份/恢复核验后只测常量对照。首次无按键返回与已知延时响应后才能校准；回Android不能直接证明命中PASS门，需要已知码对照。
3. 校准通过后再做最小显示寄存器读取；若失败停止追加，恢复并离线隔离。
4. 之后分离描述符/Sync/CPU Read/Write，检查实际FDT、页表/GCD与SMMU。新像素写仍需具体单次审查。
5. 复用现有FAT publisher、DarwinBoot、NativePrelink/ADT，再推进SM8250 UFS与用户态；不重写上游通用实现。

## 来源与边界

独立固件仓已从c45e52a快进到b63c9bd基线；后续新固件以config/uefi-source.lock.json为准。原Mu_Basecore递归脏状态保留，不使用reset/clean覆盖。UniXNU固定5fdbd5d；远端新HEAD仅作差异待审，不直接切换。

R-005 consumed；R-007像素单次已消耗，旧同号MMIO提案仅历史记录；R-008 retained-log/warm-reset pending，不启用。新内存字段、映射、verified和破坏性分区仍遵守AGENTS；本阶段不写像素/MMIO/分区、不启用保留日志，512MiB owned/51MiB heap/example=true/Boot v3不变。冻结的旧镜像不重试。

目标 iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB。已有源平台内核最终链接、donor闭包规划；未emit预链接镜像。64MiB配置FAT未接publisher，NativeUfs的SM8550参数未启用，EnumaScreen仅主机/对象检查。TWRP/UART未验证；相机用于有显示输出/恢复动作，保留原图并按实际方向旋转。

接手顺序 AGENTS、STATUS、DECISIONS、NEED-REVIEW；操作细节见 operations/2026-10-24-takeover-calibration.md。不要按旧README或旧HANDOFF重跑失败镜像。当前候选摘要/执行结果以 reports/enuma-value-transport-qualification.json、reports/enuma-value-transport-device.json（若已生成）及 out/value-transport/ 为准。没有对应结果就写未执行。
