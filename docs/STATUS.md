# 当前状态：D-220，S-017头部只读隔离：完整资格完成，尚未发出

2026-10-25T20:47:04+08:00。用户继续推进，沿已明确的直接上机授权实施新S-017：相同B0000000/2MiB映射，在MMU后的stage10仅作三个volatile UINT32读取（+0/+4/+8），原2秒延时/ResetCold；不依赖读数、不写console、不读payload、不请求warm，不触及pmsg/分区/verified。默认profile仍无新增映射，全局SerialPort仍Null。完整FAT/Boot v3/实际FD、Core、参数及描述符资格已完成，实际代码审查见reports/enuma-ramoops-header-read-code.json。

固件`89e6491626ed0edbc48dc7fb41a6902e8ce7eb4c`，镜像`0586196e4666f9e119cca0afd984901b635084237a30a29e82d9450e2a3ca43a`，FD`26e03f46313af2bf0a588eb1d8833ccb7859d4aca1f9b04cf40a20461e997440`；归档`out/ramoops-audit/S-017-qualified`。资格见reports/enuma-ramoops-header-read-qualification.json；三次读取实际机器码核对、无console store/warm/writer，10项保护门禁和8组无效CLI组合测试通过。源码/全部当前文档提交推送与即时身份/备份/恢复/相机门禁后直接单笔，不重复申请批准；75秒无返回立即停止追加并优先恢复，相机继续记录关键节点，影音只留本地out、无录音/上传。

历史：S-015 writer/warm单笔75秒无自动返回，用户恢复且独立核验通过；无有效nonce，65字节cat缺文件诊断不算日志。S-016仅映射+原cold自动回Android，ADB20.063秒/完成35.406秒，独立完成/root/A槽/解锁/双分区备份摘要通过，相机251帧已目视logo和桌面。两笔及其专项账本consumed，不重试；详见reports/enuma-ramoops-S-015-result.json、S-016-result.json。

判断：单独映射不再首嫌，S-015物理访问/写入与warm差异仍未分离。S-017自动返回只能支持此最小读取路径与cold返回的可控性，不能输出实际头数值、证明写权限/持久化/全局日志或GOP成功；超时同样不能唯一定位某条load，先恢复再分析。下一步按本笔结果隔离warm或写入，不能复活consumed writer或扩大范围。S-001..016已consumed，真实GOP/XNU/iPadOS仍未实机闭合。
