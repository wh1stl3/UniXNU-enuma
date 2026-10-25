# 交接：D-178，两次整链超时均已恢复，返回边界新候选离线就绪

S-001/S-002均已单笔超时并消耗，不重试。S-001于14:12:13发出，2.625秒命令返回/5.110秒断开、75秒无返回，14:15:38人工恢复后独立核验通过。S-002于14:29:26发出，2.657秒命令返回/5.125秒断开、75秒无返回，14:31:50人工恢复后独立enuma/完成/root/A槽/解锁/boot_a与vendor_boot_a设备备份SHA256一致。主录像450/451帧和恢复录像739/741帧均可解码；无可判读13项报告。

只关闭显示线程没有带来可观察改善，降低该单一策略优先级，不能据此确认配置查询已执行或定位根因。两次失败和恢复均已落实并推送，停止追加同类整链黑屏尝试，改为缺少直接错误时的必要边界定位。本轮没有第三笔启动。

已实际构建新的完整输入返回边界镜像：d716e159d6852b398d1b8a999b17852c4affd8318123cbd61e8afe27047f8304，103817216字节，out/full-boot/transport/enuma-display-return-full-input-v3.img；FD50bba978359f56b9d1c55bcb83fc5d545879127f4feaf82da2d15e734a2bc815，归档return-boundary-cb9e568。仍同firmwarecb9e568/UniXNU5fdbd5d、96MiB真实FAT和display-thread0，只启用正确DisplayDxe GUID的CoreStartImage返回后point13门，completion fallback关闭。point13是任何返回，不是成功状态或SetMode结果。

完整构建、32保留OEM PE/DEPEX、实际Core/map/GUID/调用顺序、SEC TE值0与AOSP真实FAT往返通过。无fallback时编译器把2秒延时专门化为两次1秒NanoSecondDelay；审核器逐条核固定callee形状，不跳过常量检查。错point/GUID/StartImage调用/纳秒参数、fallback或错误FAT负例拒绝，旧A/B审核回归通过。机器证据enuma-full-input-return-boundary/core/negative.json。

下一步入口：run_system_transport_trial.py --qualification reports/enuma-full-input-return-boundary.json 默认离线，仅加--execute才会先相机/已发布源/即时身份备份守卫后发一笔，仍沿用户无需逐笔批准授权。当前未执行新门；若未来有受控返回只支持门命中，不以耗时唯一证明；无返回不能证明目标已到达或DisplayDxe挂死。本定位是恢复完整链实修的必要支线，非默认无限早停路线。

详见operations/2026-10-25-full-input-return-boundary.md；两次真实结果分别enuma-system-transport-result.json和enuma-system-transport-S002-result.json，current.local.json已恢复完成。当前无人工/批准待办，无未恢复硬停；不复活两份失败镜像。board/plan内存字段/512MiB/verified/分区规则不变，无flash/erase/改槽。root/PMGR/UFS/Data/实际GOP/XNU仍未闭合。执行前32a3c63与最新恢复f98a37f已推送，本轮离线候选发布以Git/远端核验为准。

接手不再询问两次恢复或逐笔批准，均已明确；禁止重试已消耗镜像。新返回门只有离线资格，查账本和当前状态后再决定下一笔，不能把它记成已执行。
