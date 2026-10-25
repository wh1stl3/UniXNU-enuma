# enuma交接：D-178，两次整链已恢复，完整输入返回边界候选离线就绪

先读AGENTS/STATUS/D-178及operations/2026-10-25-full-input-return-boundary.md。用户要完整链/真实报错/同次多点，并已明确上机无需逐笔批准；实际两次整链都75秒无返回，均人工恢复并独立完成/root/A槽/解锁/原boot与vendor_boot摘要核验通过。S-001 d2ab5ef8…7e1db75和S-002 5e07e65e…77413327均consumed，禁止重试；最后核验14:31:50，无人工或批准待办。

关闭显示线程单一策略没有可观察改善；别从黑屏/时间/USB定位阶段。停止追加同类整链黑屏尝试，现准备必要返回边界定位，仍带相同96MiB FAT/display-thread0。源码firmwarecb9e568/UniXNU5fdbd5d，stage13/detail13/正确GUID-only/fallback0。镜像103817216字节，SHA256 d716e159d6852b398d1b8a999b17852c4affd8318123cbd61e8afe27047f8304，归档out/full-boot/transport/return-boundary-cb9e568。没有第三笔boot。

实际Core/map/GUID/调用顺序/SEC TE/原厂PE/AOSP资格完成。LTO延时专门化为两个1秒NanoSecondDelay，审核精确callee形状并有参数篡改拒绝；旧A/B及point/fallback/FAT负例回归通过。point13是任何CoreStartImage返回，不是成功或SetMode。受控返回仅支持门命中，未返回不证明目标曾到达。

下一步用run_system_transport_trial.py --qualification reports/enuma-full-input-return-boundary.json离线检查；未来具备已发布源/即时设备备份/相机恢复条件时可加--execute直接单笔，不需再批准。此为无直接错误时必要支线，不恢复无限早停。任何超时先停止追加/恢复/同轮文档，恢复后自动离线分析。board/plan内存字段/512MiB/verified/分区规则及旧R-016/B/R-002/R-015限制保持；不声称GOP/XNU/iPadOS运行通过。
