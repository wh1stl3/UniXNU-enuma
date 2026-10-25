# 当前状态：D-219，S-016映射/cold对照自动返回；Android正常

2026-10-25T20:25:27+08:00。S-016于20:21:48单次临时boot，命令0/2.641秒、断开5.110秒、ADB20.063秒、完成35.406秒，无主机fastboot恢复reboot。独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与本地备份摘要全部通过，证据`out\device-tests\20261025T202334-recovery-reconciliation.json`。相机251/251帧解码；中间Android重启logo和最终桌面已目视，logo不是UEFI/GOP输出。当前无人工按键或审批待办。

S-016来源`a657b79018a47a0b4a6af4fe9c4b14a8f490cd12`，镜像`1fcb56736b7fbae40cf3250691c1e70b67866d375ff741bb43423f96471d1513`，FDb5c52587814fb17ad7bb80af9d576aa1831632e06af696914e2cacf2ca259325；实际Core/描述符/宏/完整FAT/Boot v3资格见reports/enuma-ramoops-map-control-qualification.json与code.json。只启用相同已批准B0000000/2MiB映射，CANARY0，原stage10/delay2/ResetCold gate逐字节保留；没有console头/payload访问或warm请求。R-017-MAP及S-016已consumed，不重复。

S-015于20:04:30单次发送后75秒无自动返回，用户恢复Android且20:07:27独立核验通过。原镜像2583de23dbf426692e4edc573faeadb0a383147f8fa82d3f01aff1fb73abbd1e及R-017 writer单笔consumed，不重试；原始失败记录保留。559/559帧录像终点仍黑屏，之后补拍桌面；恢复按键不在已确认连续录像范围。没有有效nonce读回，65字节cat缺文件诊断不是pstore日志；采集器已改shell -T/test -f，6项回归通过。详见reports/enuma-ramoops-S-015-result.json。

主判断：新增映射配合原early/cold路径能够受控返回，单独映射导致必现挂死不再是首要嫌疑。S-015差异仍包含console物理访问/写入与warm请求，不能单独认定哪一个失败；没有直接执行日志，启动间变化/引导器噪声仍可混淆，也不称映射或物理RAM访问已实机verified。较强可推翻条件：同源后续map-only再现早期挂死，或最小只读访问/写入+cold能够稳定受控返回，会改变当前嫌疑排序。

下一步先以同一cold gate隔离console最小头部只读访问，随后分别隔离写入和复位；不先启全局日志，不扩大到pmsg，不复活consumed writer/旧失败图。新最小访问探针尚未实现/构建/资格/上机。此前S-013/014只间接支持首样本Enable门禁Reason5，后续稳定性按该路径未执行；显示双路计数前缀仍未实现。真实GOP、CPU/SMMU/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合。

全部原始影音仅本地out/camera-capture，未录音/上传；本轮两笔均只临时boot，无flash/erase/改槽/分区/verified/pmsg/显示寄存器写入。全局SerialPort仍Null，默认profile不添加console映射。固件a657b79已推送；设备仓e2b6ea5资格在S-016执行前已推送，本里程碑提交结果与当前文档。S-001..016均consumed。
