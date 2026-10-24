# 交接：zero2 超时已恢复，隔离方案已审并撤回，下一步建挂死率基线

2026-10-24 23:45之后，Asia/Shanghai。本轮只读核验、离线构建与文档对账；未启动新候选，未写设备分区。

## 当前设备与恢复

enuma已恢复Android，主机独立核验boot_completed=1、root、原A槽、解锁，以及boot_a/vendor_boot_a设备和本地备份摘要匹配。证据 reports/enuma-recovery-reconciliation.json，原始证据 out/device-tests/20261024T230449-recovery-reconciliation.json。恢复的具体人工动作/发生时刻未独立记录，不推断。失败试验result.json未改，current.local.json更新为recovered-android-boot-complete。

本轮接手再次只读核验：`d0fd0840`=enuma、`boot_completed=1`、`_a`、`flash.locked=0`；同时在线 `fe5ed56e` 是 nuwa（只读参考，不是目标）。无需再次要求恢复按键；恢复不代表固件问题已解决。value transport计划仍冻结，不清空失败账本、不原样重试失败镜像。

## 最近实测及硬停

| 试验 | 实际发出时间 | ADB返回时间 | 结果 |
| --- | --- | --- | --- |
| zero1，常量0 | 22:49:52 | 16.991秒 | 自动回Android，root/分区核验通过 |
| known3，常量3 | 22:50:59 | 25.503秒 | 自动回Android，root/分区核验通过 |
| zero2，常量0 | 22:52:12 | 75秒观察期无自动返回 | runner退出2，停止追加，计划冻结 |

zero2镜像与zero1相同：SHA256 `9b3c1df33c2fc5f0612cc0b669434607cf85547bed75c36c897603dee82a9ce1`，FD `bfb3d6a6…`。known3镜像 `357706af…`，FD `72d2b0a9…`。两份已归档产物本轮复核完整。失败账本reports/enuma-value-transport-device.json保留。

## 可支持的结论与未知项

前两笔差8.512秒、残差0.488秒，在0.75秒容差内：这是符合预期的延时响应证据，不能称通道已校准或可靠。第三笔零码未返回，0/3/0校准失败，禁止解码寄存器。

**本轮推进**：常量helper在`Code==0`时直接`return EFI_SUCCESS`，不调Read、不调Wait、不写寄存器；zero1/zero2同镜像同码。故"什么都不做"的代码一次返回一次挂死，挂死**不必**与显示访问相关；剩余嫌疑还包括fastboot临时boot载体、XBL对临时镜像的处理、连接/供电时序差异。75秒无返回仍未定位到某条指令。

**方法论缺口**：R-006自算15%挂死率下"5笔全干净"先验仅44%，"0读5笔干净 vs 2读首笔挂"由5+1笔构成，基线未知时不构成证据。unclocked access主判断与23个step的证据降级均建立在该对照上，保留为历史观测。

旧delay20宏未进入编译参数；GOP_QUERY/detail16在CoreStartImage返回后匹配marker；像素函数先Sync/CPU Read再Write。旧硬件因果解释已由D-146/D-149/D-152取代。

## 在途代码处置

三份在途改动已处置完毕，firmware/工作树干净：

- 驱动内复位隔离（`--value-reset in-driver`）：提交e5f1ab5后**经构建实测撤回**（d00c416）。WSL构建在`build_enuma_firmware.py:258`断言失败，该处三条守卫刻意禁止ResetSystemLib进入SimpleFbDxe，且enuma平台dsc无该库绑定。审查结论维持守卫。
- Windows alternates换行修复：保留（96d354a），WSL下等价。
- Windows原生构建仍不可用（`symlink_to`需特权，`WinError 1920`未修）；**构建一律在`wsl.exe`+Python 3.10.12下进行**。
- **构建不可复现**：同参数重建FD `02f8d31d` ≠ 已资格 `bfb3d6a6`。资格只能绑定已归档镜像，不能靠重建取得。

## 下一步与继续条件

1. **先建挂死率基线，不改任何固件**：用已资格zero镜像（`out/value-transport/zero/candidate.img`，`9b3c1df3…`）重复至8笔，只记"返回/挂死"，不解码不校准。零读档若与历史读档挂死同量级，则以显示为因的归因链作废、按载体/XBL重开；若8笔全干净，只能把上界压到约25%。
2. 逐笔门禁：身份、备份、恢复路径核对后临时boot；失败即停不原样重试；每笔后核验Android完成/root/槽位/解锁与双分区摘要。
3. 驱动内复位不重启；若确需改守卫，必须另立NEED-REVIEW编号。
4. 常量重复性通过后才考虑最小寄存器读；随后分离描述符、cache Sync、CPU Read和Write，核对实际FDT、CPU映射与SMMU。
5. FAT publisher/完整ADT/donor预链接可离线准备；复用上游通用实现，再适配SM8250 UFS和用户态。

## 源码与边界

独立固件仓HEAD `d00c416`，设备锁`config/uefi-source.lock.json`已重固定，firmware工作树干净；Mu_Basecore原有递归脏状态保留，不用reset/clean覆盖。设备仓既有提交b54bb2b已推送。UniXNU固定5fdbd5d。

R-005/R-007像素单次均consumed；R-008保留日志/warm reset pending未启用。不批准新像素/MMIO写、内存字段/映射、verified或破坏性分区操作；撤回动作未放宽任何守卫。512MiB owned、51MiB heap、example=true、Boot v3不变。用户确认可在场恢复，每笔仍核对当时条件。

目标iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB。无可见GOP/白条闭环、未进XNU或iPadOS。TWRP/UART未验证。

接手顺序AGENTS、STATUS、DECISIONS、NEED-REVIEW；专项记录operations/2026-10-24-takeover-calibration.md。不得从历史D-148或旧提交正文提取更强的"机制成立/挂点已定位"结论，当前以D-152/D-153为准。
