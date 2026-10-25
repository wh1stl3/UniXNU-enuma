# 当前状态：D-220，S-017头部只读隔离：自动返回Android并独立核验

2026-10-25T20:49:39+08:00。用户继续推进，沿已明确的直接上机授权实施新S-017：相同B0000000/2MiB映射，在MMU后的stage10仅作三个volatile UINT32读取（+0/+4/+8），原2秒延时/ResetCold；不依赖读数、不写console、不读payload、不请求warm，不触及pmsg/分区/verified。默认profile仍无新增映射，全局SerialPort仍Null。完整FAT/Boot v3/实际FD、Core、参数及描述符资格已完成，实际代码审查见reports/enuma-ramoops-header-read-code.json。

固件`89e6491626ed0edbc48dc7fb41a6902e8ce7eb4c`，镜像`0586196e4666f9e119cca0afd984901b635084237a30a29e82d9450e2a3ca43a`，FD`26e03f46313af2bf0a588eb1d8833ccb7859d4aca1f9b04cf40a20461e997440`；归档`out/ramoops-audit/S-017-qualified`。资格见reports/enuma-ramoops-header-read-qualification.json；三次读取实际机器码核对、无console store/warm/writer，10项保护门禁和8组无效CLI组合测试通过。执行前源码/全部当前文档已提交推送、即时身份/备份/恢复/相机门禁通过后发出一次；本笔自动返回，无须人工恢复。原始影音只留本地out，无录音/上传。

历史：S-015 writer/warm单笔75秒无自动返回，用户恢复且独立核验通过；无有效nonce，65字节cat缺文件诊断不算日志。S-016仅映射+原cold自动回Android，ADB20.063秒/完成35.406秒，独立完成/root/A槽/解锁/双分区备份摘要通过，相机251帧已目视logo和桌面。两笔及其专项账本consumed，不重试；详见reports/enuma-ramoops-S-015-result.json、S-016-result.json。

判断：单独映射不再首嫌，S-015物理访问/写入与warm差异仍未分离。S-017自动返回只能支持此最小读取路径与cold返回的可控性，不能输出实际头数值、证明写权限/持久化/全局日志或GOP成功；超时同样不能唯一定位某条load，先恢复再分析。下一步按本笔结果隔离warm或写入，不能复活consumed writer或扩大范围。S-001..016已consumed，真实GOP/XNU/iPadOS仍未实机闭合。

本笔实际结果：20:48:03发出一次，命令2.625秒/返回0，断开5.094秒，ADB20.047秒、完成35.969秒，无主机fastboot恢复reboot；独立完成/root/A槽/解锁与设备双分区及备份摘要全部通过。录像253/253帧解码并目视最终Android桌面。结果reports/enuma-ramoops-S-017-result.json；S-017/R-017-READ已consumed，S-001..017均不重试。

当前主判断收敛：最小头部三读本身不再首嫌，S-015的写入/头更新与warm请求仍未分离。下一步优先同映射无console访问的warm对照，先隔离复位路径，再考虑新的写入候选。该下一候选尚未实现/构建/资格/上机；不会重复S-015或从读回归成功推断写入/持久化成功。当前最新独立恢复证据`out\device-tests\20261025T204851-recovery-reconciliation.json`。资格a0c7afb已在本笔执行前推送；结果与所有当前文档随本里程碑提交推送。
