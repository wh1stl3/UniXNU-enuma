# 当前状态：D-221，S-018超时硬停；Android已恢复，本轮停止

2026-10-25T21:03:20+08:00。用户要求“继续推进 触发硬停再停”。S-018于2026-10-25 20:57:13单次临时boot，命令返回0/2.641秒、5.110秒观察到断开，75秒内未回Android/fastboot，触发停止追加镜像的硬停。runner未记录超时精确墙钟；按发出时间推算期限约20:58:28，不把推算当实际检测时刻。已停止所有后续boot/写入，仅处理恢复取证和交接。用户报告恢复Android，21:01:29独立完成/root/A槽/解锁及boot_a/vendor_boot_a设备与本地备份摘要均通过。当前Android正常，无人工按键或审批待办；按最新要求停在此处，不再构建/执行下一候选。

最后候选：固件`5cfcd4cc68c0c37ffb322322efc256760d9389e3`；镜像`6b145fd370bb67a5db16112764701d8a4234b27c0eabc5d9e043bb7d92d843a5`；FD`fb8a9ae93a279e6ad8f181c277eb620483d5cd5b8f1cd4c41bf4b7af19f9908f`。只在探针构建保留同已批准B0000000/2MiB映射，stage10延时2秒后ResetWarm，返回则deadloop；不读写console/pmsg、不使用nonce、不写分区/改槽/显示寄存器或verified。完整FAT/Boot v3、实际Core/参数/描述符与反汇编审计在执行前完成并以4ca93ca提交推送；资格reports/enuma-ramoops-warm-control-qualification.json、代码reports/enuma-ramoops-warm-control-code.json、归档out/ramoops-audit/S-018-qualified。默认profile仍无新增映射，SerialPort仍Null。

硬停规则来源：AGENTS的75秒有界临时探针/失败后停止追加并先恢复，以及用户本轮“触发硬停再停”。S-018/R-017-WARM已consumed，S-001..018及旧失败图不重试。a3870d3已先推送恢复待核验停点；本里程碑补齐实际恢复和最终交接。原始失败记录`out/device-tests/20261025T205659-system-transport/result.json`保持manual-recovery-needed，不改写为自动通过。独立恢复证据`out\device-tests\20261025T210129-recovery-reconciliation.json`；脱敏结果reports/enuma-ramoops-S-018-result.json。

相机关键节点：out/camera-capture/20261025T205656-system-transport，1090/1090帧解码通过；早段黑屏，frame-0468目视Android重启logo，说明录像延长覆盖到恢复启动。恢复后out/camera-capture/20261025T210129-system-transport补拍桌面已确认。没有明确核对按键动作，不猜测其时间。原始视频/图像只留本地out，无录音/上传；公开仅文字、状态和摘要。

主判断（中等置信）：S-016同映射/原cold与S-017头三读/cold均约20秒回ADB、35–36秒完成；S-018无console访问、仅改warm请求仍未受控返回，因此warm请求链是当前优先嫌疑。它包含PSCI_FEATURES、返回值分支、SYSTEM_RESET2或cold回退及其前置日志，实际执行到哪一步未知；不能声称一定执行reset2、DRAM保留、warm不被硬件支持或S-015必然同一根因。更早路径/跨启动变化仍可混淆，header写入仍未验证安全。

有效历史：S-015 writer+warm也超时并人工恢复，未取得有效nonce；65字节cat缺文件诊断不是console日志，collector已修复。S-016 map-only/cold自动返回，ADB20.063秒/完成35.406秒。S-017三次头部load/cold自动返回，ADB20.047秒/完成35.969秒，253帧及独立恢复通过；没有导出头数值，不称写权限/留存通过。真实GOP、13项RAM运输、XNU/iPadOS/PMGR/UFS仍未实机闭合。

继续条件与下一步：用户恢复推进后，先离线审查warm功能查询/SMC参数及回退路径，优先以已返回的cold门隔离一个新的最小写入候选；不是复活S-015/018或扩大console范围。候选尚未实现/构建/资格/上机。后续仍需新精确源码/实际PE/宏/描述符/完整载荷审计、全部当前文档提交推送及即时身份/备份/相机/恢复门禁；新内存范围/verified/破坏性分区仍按原专项规则。当前本轮工作已停。
