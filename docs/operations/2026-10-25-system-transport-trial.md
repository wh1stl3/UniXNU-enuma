# D-173：报告刷新修复及S-001单笔整链试启动

用户本轮明确“继续 上机无需批准”，继续沿此前在场恢复/完整链/同次多点偏好执行。无需再申请这笔可恢复临时boot；内存字段/verified/破坏性分区及失败后停止追加、恢复优先规则不变。

## 新候选与修复

firmware 945942685770eb7200ac2a6551cd3ee5aa554b61已提交推送。旧698b7c1应用在报告缺失/版本异常/文件失败时提前返回，绕过Map释放和最终帧缓冲cache flush；这可能使真实错误文本无法呈现。现统一走PayloadFinish，先清理/刷新；13行改到0..12以容纳横竖两种几何，保留2秒供相机判读，再继续UniXNURun或返回真实错误。不是定时复位，也不把2秒当阶段编码。

check_payload_report_flow.py提取生产BDS尾部在ASan/UBSan主机适配器中注入missing/version/file/missing-stage四种失败与成功：失败均清理、flush、展示后返回，成功继续原链；13项完整输出。实际staging只有既有preflight插入的SimpleFb safety return比源多，实际编译宏SIMPLEFB=0；被测payload尾部逐字相等。证据enuma-payload-report-flow.json与enuma-system-trial-preflight.json，不声称实际GOP flush/显示已成功。

- FD SHA256 cb24c8f14dd19fba1e759301efbb8003d433cccd243f5a0fb087e6641a27dc09。
- 镜像out/full-boot/transport/enuma-system-transport-visible-v3.img，103817216字节，SHA256 **d2ab5ef8c44a9160e79150a34651e3fa616852ca3205beefa99ab60df7e1db75**。
- 独立资格归档out/full-boot/transport/qualified-9459426；原698b7c1镜像保持历史归档，没有启动或重试它。
- 完整构建、32保留OEM PE/DEPEX、实际编译宏/常量/写保护代码、BootShim和AOSP真实96MiB FAT往返均通过。

## 观察、恢复与执行门禁

本轮先重新核验唯一Android enuma、boot_completed=1、root、A槽、解锁和boot_a/vendor_boot_a设备/备份摘要一致；摄像头起初未枚举，尚未发任何reboot/boot。用户回复“已连接，请重新检测”后，2026-10-25 14:06:59相机成功采集1920x1080帧，Windows标识OsmoAction5pro；原图及90度顺时针图显示目标Android画面。初始采集阻断已解除，不是批准等待；当前不保留为未解决硬停。

run_system_transport_trial.py默认离线校验，只有--execute才进行设备动作。执行前要求设备/固件两仓clean且HEAD已在origin/main、资格/候选摘要一致、未消耗该镜像。先开启相机/录像，失败不启动设备runner；复用run_enuma_entry_probe.py核对即时设备、备份、fastboot product/slot/unlocked后，仅一笔fastboot boot。保留原图并自行旋转；录像每帧有主机相对时间，解码复查。不得把旧Android截图当作UEFI输出。

整链镜像没有人为早停或自动返回保证。沿已有黑屏有界临时试验例外执行：主机在boot命令返回后观察最多75秒，整段相机runner上限240秒；先观察fastboot断开再接受返回。若正常回fastboot则核身份并正常reboot Android；回Android必须再次核完成/root/槽/原分区摘要。否则标manual-recovery-needed，停止追加候选，按已示范的长按电源路径恢复，核验后自动继续离线分析。人工按键若不在画面内则不推断，依明确用户反馈/独立恢复状态确认。

相机在执行中丢失会停止runner并转恢复核验；主机期限不是硬件watchdog，不声称保证自动返回。若缺少实际文本，13项均保持未知/未观察，不用耗时、黑屏、USB或发送成功解码阶段。此笔目的是让完整输入沿实际链尽量前进，不预设会到Hello；根卷/PMGR/UFS/Data等未闭合限制保持。

## S-001账本（执行前）

当前新候选已资格，授权来自用户本轮原话，不需再次确认；计划一笔，不flash/erase/改槽/写分区。当前尚未执行，待全部当前文档和host runner提交推送后发出。原始实测输出留out/device-tests与out/camera-capture，镜像若已发出则写独立consumed记录，不能原样重试。结果/恢复与后续分析须同轮追加并重写STATUS/HANDOFF。
