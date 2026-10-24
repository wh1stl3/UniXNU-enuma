# 当前状态：zero2超时后已核验恢复，校准计划冻结

2026-10-24 23:04之后，Asia/Shanghai。本轮只读核验与文档对账；未构建或启动新候选，未写设备分区。

## 当前设备与恢复

enuma已恢复Android，主机独立核验boot_completed=1、root、原A槽、解锁，以及boot_a/vendor_boot_a设备和本地备份摘要匹配。证据 reports/enuma-recovery-reconciliation.json，原始证据 out/device-tests/20261024T230449-recovery-reconciliation.json。恢复的具体人工动作/发生时刻未独立记录，不推断。失败试验result.json未改，current.local.json通过新恢复证据更新为recovered-android-boot-complete。

因此无需再次要求恢复按键；恢复不代表固件问题已解决。现有value transport计划仍冻结，不因恢复清空失败账本或原样重试失败镜像。

## 最近实测及硬停

| 试验 | 实际发出时间 | ADB返回时间 | 结果 |
| --- | --- | --- | --- |
| zero1，常量0 | 22:49:52 | 16.991秒 | 自动回Android，root/分区核验通过 |
| known3，常量3 | 22:50:59 | 25.503秒 | 自动回Android，root/分区核验通过 |
| zero2，常量0 | 22:52:12 | 75秒观察期无自动返回 | runner退出2，停止追加，计划冻结 |

时间来自各result.json的issued_at；目录时间22:49:38/22:50:44/22:51:58是准备时间，不当作boot发出时间。zero2观察期限结束约22:53:27；没有单独事件时间戳，不把估算当精确硬停时刻。规则来源AGENTS“硬停当轮必须落实交接”及“接手后的通道校准与证据更正”。既往未及时对齐的当前文档，本轮补齐。

最后候选zero2与zero1镜像相同：SHA256 9b3c1df33c2fc5f0612cc0b669434607cf85547bed75c36c897603dee82a9ce1；FD bfb3d6a6018498ea1b94368b1d8a394983234b32d84368fdf0df49f41d1c1551。known3镜像357706af66517e7c1d7dac9629f55b1ee57e88b6701bfa4176315a3f4d3ace96；FD72d2b0a9384bdb7ba76b43b9c24bb69f42c8c65f1cf7eed27070df338300a3b2。构建固定固件74598dfa2b223716450de044caf937c4a30e51f5；精确资格见reports/enuma-value-transport-qualification.json和out/value-transport/。失败账本reports/enuma-value-transport-device.json保留。

## 可支持的结论与未知项

前两笔差8.512秒，对预期9秒残差0.488秒，符合0.75秒容差：这是符合预期的延时响应证据，不能称完整通道已校准或可靠。第三笔零码未返回，完整0/3/0校准失败，禁止解码寄存器。未执行任何新寄存器模式、像素实验或XNU启动。

常量helper没有显示MMIO/像素/cache访问，说明显示读取不是发生超时的必要条件；不证明整份固件没有其他设备访问。75秒无返回没有定位到某条指令，公共启动、驱动执行/返回、异常或复位出口均待隔离。历史stage成功不等于持续安全，三类嫌疑不构成互斥穷尽分类。一次成功一次失败也不能判定“首次成功后必挂”或bootloader残留。

旧delay20宏未进入编译参数，历史时序不能作为寄存器值；GOP_QUERY/detail16在CoreStartImage返回后匹配marker。像素函数先Sync/CPU Read再Write，像素超时不能认定store失败。旧硬件因果解释已由D-146/D-149取代，历史原始记录保留。

## 源码与发布边界

设备仓最新既有提交b54bb2b已推送；本轮文档提交号以Git后续记录为准。设备仓gitlink及锁、独立固件仓HEAD仍为74598df。firmware/有三份未提交在途改动：Resources/Scripts/build_enuma_firmware.py、patches/dispatch-detail-options.patch、patches/simplefb-gop-query.patch。本轮不改写、不提交这些代码，不声称它们已构建/审计/发布；设备源码校验必须拒绝此脏状态。独立固件仓Mu_Basecore原有递归脏状态也保留。新实机前必须先明确代码所有权、审查、锁定干净来源并完整重新资格，不能沿用旧候选报告。

## 下一步与继续条件

1. 保留冻结计划及原失败镜像，不以统计失败率为由原样重试。先离线审查在途隔离方案，设计有区分力的新检查点/异常或复位证据。
2. 驱动内复位只能作为待审候选：新增库依赖/constructor会改变上下文，应先审副作用和编译/FD，不把内外两版本差异直接当唯一因果。更早检查点也需同源资格与自己的复位可靠性证据。
3. 每个新候选完成主机/实际编译宏/FD/打包审计、精确摘要绑定，当前文档提交推送，确认现场恢复及即时身份/备份条件后，才能执行单笔。超时停止追加，恢复后继续离线分析。
4. 常量重复校准通过后才考虑最小寄存器读；随后分离描述符、cache Sync、CPU Read和Write，并核对实际FDT、CPU映射与SMMU。
5. FAT publisher/完整ADT/donor预链接可离线准备；继续复用上游通用实现，再适配SM8250 UFS和用户态。

## 审查与系统里程碑

R-005/R-007像素单次均consumed；R-008保留日志/warm reset pending，未启用。本轮不批准新像素/MMIO写、内存字段/映射、verified或破坏性分区操作。512MiB owned、51MiB heap、example=true、Boot v3不变。用户此前确认本轮可在场恢复，具体新设备动作前仍核对当时条件。

目标iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB，UniXNU固定5fdbd5d。已有源平台内核最终链接与donor闭包规划，未emit预链接镜像；64MiB配置FAT未接publisher，SM8550 NativeUfs参数未启用。无可见GOP/白条闭环、未进XNU或iPadOS。TWRP/UART未验证。
