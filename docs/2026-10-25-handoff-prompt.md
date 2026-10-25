# 当前状态：D-218，S-015已恢复；S-016映射对照完成资格待执行

2026-10-25T20:21:00+08:00。S-015于20:04:30单次发出后75秒无自动返回，用户恢复Android，20:07:27起独立完成/root/A槽/解锁及boot_a/vendor_boot_a设备与本地备份摘要全部通过。当前最新只读恢复证据`out\device-tests\20261025T201930-recovery-reconciliation.json`，Android正常。原失败记录保留；R-017 writer单笔和S-015均consumed，不重试。没有有效nonce读回，65字节缺文件cat错误不算pstore日志；收集器已改shell -T/existence guard，6项回归通过。

恢复后按用户直接上机及故障隔离规则完成新S-016：只保留相同已批准B0000000/2MiB映射，不读取/写入console头或payload，不请求warm；原迁移stage10/delay2/ResetCold header逐字节不变。writer开关0、map1、nonce全0，实际Core无writer表/标记或ResetWarm符号。映射描述符实际字段及有界cold调用在CoreDispatcher之前已审查。默认生产profile仍无新增映射，Null后端不变。

固件`a657b79018a47a0b4a6af4fe9c4b14a8f490cd12`已推送；新镜像`1fcb56736b7fbae40cf3250691c1e70b67866d375ff741bb43423f96471d1513`，FD`b5c52587814fb17ad7bb80af9d576aa1831632e06af696914e2cacf2ca259325`，103817216字节，完整FAT/Boot v3回环及不可变归档`out/ramoops-audit/S-016-qualified`通过。资格/实际代码见reports/enuma-ramoops-map-control-qualification.json及enuma-ramoops-map-control-code.json。R-017-MAP只绑定此无内容访问的新对照，不继承或重新批准writer；无新base/size、pmsg/分区/verified/显示寄存器范围扩张。

当前S-016尚未发出。源码/实际PE/宏/描述符/完整载荷审计及保护门禁回归通过；当前文档提交推送后，沿即时身份/备份/恢复/相机门禁直接单笔临时boot。相机覆盖关键节点；若超时继续拍摄至独立恢复或235秒相机界限，主机75秒无返回仍立即停止追加。原始影音仅本地out，不录音/上传。

解释边界：自动回归只能支持map-only/early/cold路径可控，不能称console物理访问或日志成功，也不能唯一证明门命中；若成立，S-015怀疑重点转到writer物理访问与warm路径的差异。若再次超时，先恢复再分析新增映射/更早启动差异，不追加其他writer。S-001..015及旧失败图不重试；真实GOP/XNU/iPadOS仍未实机闭合。当前无人工按键/审批待办。
