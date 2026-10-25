# D-215 接手入口

先读AGENTS、STATUS/HANDOFF、NEED-REVIEW的R-017和operations/2026-10-25-ramoops-compatibility-audit.md。原生ramoops路线已有未接线核心/收集器和51,210+5项主机测试，AArch64对象通过；尚无新FD/硬件资格。固件pin 91a8a7c56d327e30262765548e2cd98bd5107037，最近实测b93b3bb。

当前停点仅R-017精确新内存范围审查。A只console B0000000/2MiB、一次44字节nonce、MMU后Core有界入口、warm请求/cold回退及一笔新资格临时boot；pmsg/分区/verified不动。未经明确批准不得更改实际映射或接物理writer。当前Null后端和原内存表保持；不可从用户一般支持或R-002/R-008推断新地址授权。

批准后继续绑定最小探针、完整构建/实际PE/宏/映射/镜像审计、逐笔文档发布和即时恢复门禁，再按已授权直接上机。用只读收集器在out保留原始日志，缺nonce不能唯一归因；成功后才另行评估批量日志。不要先启全局SerialPort或触及pmsg。

最终只读Android完成/root/A槽/解锁/原分区及备份通过，见reports/enuma-recovery-reconciliation.json。本轮无boot，无人工按键待办。S-001..014及失败图不重试；S-013/014仅间接支持Reason5，后续稳定性按该路径未执行。GOP/XNU/iPadOS未实机闭合。所有原始影音仅本地out、无录音/上传。
