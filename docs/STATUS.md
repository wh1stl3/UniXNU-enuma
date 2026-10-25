# 当前状态：D-217，S-015超时后Android已独立恢复；继续离线隔离

2026-10-25T20:11:30+08:00。S-015于2026-10-25 20:04:30发出一次，fastboot返回0/2.641秒，5.110秒观察到断开，75秒未自动返回Android/fastboot，立即停止追加。用户报告已恢复Android，20:07:27独立核验完成/root/A槽/解锁及boot_a/vendor_boot_a设备和本地备份摘要均通过。当前Android正常，无人工恢复/审批待办；按持久规则继续离线分析和新软件，不把人工恢复当整轮结束。

最后镜像`2583de23dbf426692e4edc573faeadb0a383147f8fa82d3f01aff1fb73abbd1e`，固件`10a546ee9a6b352ec4e2bcf2b9510dad5fc48fb6`，FD9773cea18ea6a35694eb8ee5409d073fc92918543338c9e7d46e8db2fb8766e7。R-017 A一次writer试验及S-015均consumed，不原样重试。详细结果reports/enuma-ramoops-S-015-result.json，原始超时记录out/device-tests/20261025T200416-system-transport/result.json保留；最新独立恢复证据`out\device-tests\20261025T200727-recovery-reconciliation.json`。

没有本次nonce的有效pstore数据。旧收集器把exec-out返回0时stdout内65字节“cat文件不存在”诊断误存为快照；那不是console日志，原证据保留，不算读回。Android恢复后后端仍ramoops、console2MiB、pstore目录为空。已定位主机采集缺陷，改用shell -T保留远端状态并先test -f，补回归。不能用缺nonce唯一归因于映射、写入或warm复位。

相机启动/超时过程559/559帧解码通过，最后一帧仍黑屏镜面；恢复后补拍已目视Android桌面。用户恢复按键不在已确认的录像范围，不猜测按键时间。原始视频/图像/错误快照均仅本地out，无录音/上传。

主判断：S-015同时新增映射、物理写入和warm请求，没有内部到达证据，须先减变量。按信息价值和安全性准备独立map-only对照：仅相同已批准B0000000/2MiB映射，恢复原字节不变stage10/delay2/ResetCold，不访问console内容，不启用writer/warm。先排除新增映射和早期启动路径，再决定是否继续writer/reset隔离。该新候选尚未实现/构建/资格/执行；必须新源码/全FD/实际代码/镜像审计、所有当前文档提交推送和即时身份/备份/相机/恢复门禁后才能执行。无flash/erase/改槽/verified/pmsg/显示寄存器写入；S-001..015和旧失败图不重试。真实GOP/XNU/iPadOS仍未实机闭合。
