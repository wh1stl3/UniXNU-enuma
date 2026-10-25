# enuma交接：D-173，S-001完整输入单笔试启动

目标enuma/SM8250运行iPadOS17.7.11。用户要求完整链、实际报错、同次多点，本轮明确“上机无需批准”。先读AGENTS/STATUS/D-173和operations/2026-10-25-system-transport-trial.md，再核S-001是否已执行，禁止重复消耗镜像。

新firmware9459426已推送，修复报告失败路径缺flush；13项同屏、2秒拍屏后继续，无定时复位。完整构建/ASan故障注入/实际PE和AOSP真实96MiB FAT往返资格通过。镜像103817216字节，SHA256 d2ab5ef8c44a9160e79150a34651e3fa616852ca3205beefa99ab60df7e1db75，归档out/full-boot/transport/qualified-9459426。报告只能读实际文本，不按时间/USB认阶段。

当前执行前：Android/root/A槽/解锁/boot与vendor_boot备份摘要复核通过；OsmoAction5pro已恢复并采集。run_system_transport_trial.py默认离线，--execute要求两仓clean且已推送、资格/候选绑定，先相机后复用原guarded runner即时核验并一笔临时boot。75秒命令后观察，240秒总相机上限；超时停止追加，先既有长按恢复与独立核验，再自动离线分析。并无自动返回保证。当前文档发布后执行；以STATUS/当前状态文件及consumed记录查真实进展。

不再申请逐笔上机批准；内存字段/verified/破坏性分区和恢复门禁保持。UniXNU5fdbd5d、board example=true、512MiB请求未变，无flash/erase/改槽。R-016已消耗，旧B备用/R-002失败/R-015暂停不复活。root/PMGR/UFS/Data/种子及实际GOP/XNU/Hello仍未闭合，不重复已有prelink/ADT/FAT建设。参考仓只读，二进制仅out/。任何失败须当轮更新全部交接和恢复记录。
