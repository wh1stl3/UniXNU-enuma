# S-010：实机结果与后续判断

2026-10-25T18:29:27+08:00。S-010已于18:26:07（UTC10:26:07.186360）执行一次临时boot，镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386，固件1a4b20487aa6ac0fbb2973bf508aea1851b61192，FD490fe01ebda7bf8091b3944a54135fb439f73c8c0f05d8ac609e7cdd19b9ba9e。全部执行前文档7d1312b已推送；即时Android/备份/相机门禁及fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过。上次GetVar异常没有重现，根因仍未知，不删除D-202原始中止记录，不放宽身份检查。

命令2.641秒返回，5.110秒观察断开，ADB25.469秒出现、39.438秒完成Android。runner未发恢复reboot；随后独立核验完成/root/A槽/解锁和boot_a/vendor_boot_a设备及本地备份摘要全部通过。270/270拍屏帧解码通过，已目视核对试前桌面、中途小米/Android启动标志及试后桌面；无UEFI/GOP文本证据。原始影音仅out/camera-capture/20261025T182550-system-transport，未录音，不上传Git/Release/CI。

本笔有受控返回，不能记为75秒无报告超时。相对S-009，ADB晚4.313秒、完成晚4.219秒，支持FAIL5/7秒终止的谓词拒绝判断，中等置信；不是直接状态日志，也不是PASS/GOP成功或精确寄存器定位。两个候选Core与采集范围不同、Android时序含噪声，不能仅凭差值确证7秒或S-008根因。S-010已consumed，S-001..010及旧失败图不重试。

按结果推进：主判断转向保守准入模型与实际继承布局不匹配，优先细分首次拒绝阶段/状态，不再默认把本笔当MMIO挂死或盲改缓存。源码要求单CTL/双LM/两个独立SSPP、无border/额外staging、严格dim/blend及RGBX；历史step21保守混合拒绝提供同方向旁证，但不是本笔快照。单源跨LM、border/合法混合、格式/几何/地址边界列为候选；描述表/PCD门禁、双接口前置/稳定性仍不能排除。只有直接取得阶段/状态或同入口对照后才能排序到具体寄存器，不放宽安全准入换通过。

新候选尚未实现/资格/执行。下一步保持同完整输入、完整GUID双结果终止及FALLBACK0，先设计可判读的首拒绝证据（同时区分未到达与已拒绝），主机故障注入和实际Core/provider审查后再构建；不恢复旧长时间编码或失败像素/value计划。若新证据显示采样/解码已全部通过或故障在入口前，则推翻当前拒绝模型主假设。真实GOP/CPU-SMMU/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合；ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更，当前无人工或审批待办。

证据：reports/enuma-inherited-video-S010-result.json；原trial out/device-tests/20261025T182553-system-transport/result.json；独立恢复out\device-tests\20261025T182657-recovery-reconciliation.json。身份解析3项、恢复核验2项、恢复硬门1项回归通过；不可变归档各文件摘要再次匹配。当前源码固件未改动，设备文档/脱敏证据单独提交推送。

## 具体拒绝面（源码审查，不是硬件观测）

- diagnostics/EnumaInheritedVideoAudit.c：Display MDP/Reserved描述、1600x2560 PCD，可在MMIO之前FAIL。
- Evidence.c：revision、两路timing/counter-enable/active、两窗计数稳定性及等待失败。
- VideoCapture.c与Topology.c：单CTL active精确6；每LM单源、两独立SSPP且无border/未知staging；dim、blend、LM mode bit30、局部几何严格拒绝。
- Decode.c：RGBX/source-alpha关闭、非secure/非UBWC/无缩放、全屏覆盖与splash范围/共基址一致性。

这些分支最终都被入口折叠为FAIL5，现有返回不能选定其中一个；330为上限，不是本笔已完成读数。

## 执行前计划（历史）

# S-010：对称terminal video-only单笔验证

2026-10-25T18:25+08:00。用户明确要求重启fastboot后执行S-010并按结果推进。Android完成/root/A槽/解锁、boot_a/vendor_boot_a设备与本地备份摘要再次独立通过（out/device-tests/20261025T182509-recovery-reconciliation.json）；1920x1080相机通过，不采音频。不可变镜像24aed9e0c8c98d3af74f1baa1698b1930da8a6d6bfd2cd462623ba4dae9e2386及1a4b204资格再次通过，尚未消耗。

文档提交推送后由既有runner定向重启选定enuma到bootloader，仍要求product=enuma/current-slot=a/unlocked=yes全部精确通过；再次异常则不发送，保留日志并恢复排查，不用Android结果代替fastboot门禁。通过后仅一笔S-010临时boot，连续本地拍屏及主机时序，75秒观察，无已识别返回立即consumed并停止追加，先恢复核验。2/7秒仅支持terminal分类，不唯一证明内部路径；未发布真实GOP。原始影音仅本地out，不上传Git/Release/CI。无flash/erase/改槽、内存字段或verified变更。此前D-202未发送的原始记录保留。
