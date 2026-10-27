# 当前：v4 手机重试已消费，自动回 Android；两张日志独立解码（2026-10-27）

用户明确授权同图重试一次并确认手机录像和人工恢复就绪。准备提交8533f8b已推送后，仅执行retry 7e4ec36d-755e-440a-8f47-3c98ae38dbdc一次临时boot，镜像SHA256 233088a740b8241c4ac38ab5e67aadfef5d1ade9f5802ce670c2662df73529d7。旧trial及ledger保留，新retry已consumed，不追加启动。无flash/erase/改槽。

用户确认没有操作，自行返回Android；独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a原摘要通过。旧runner只等fastboot导致误报manual-recovery-needed，原状态保留，当前已纠正；不能据此报告设备挂住或人工恢复。

手机s1/s2已独立保存完整五行及SHA256，严格v4解码/session匹配通过：E01/C4/Q8/RVA3abc，S02/C4/Q9/RVA3abc/status0。完整字符串在本地phone-independent-read.json，现场一致性确认待用户回复。照片只证明call4进入且成功返回，不证明SID或CoreStartImage返回、GOP/ConOut/BDS。

结合既有精确PE路径，观测支持本次运行到达guided-section注册附近的第五次包装服务，前置HOB/cache路径不再是本次未达call4的解释；不能据此反推v3窗口清理通过。下一步重点检查call4返回后的AllocateCopyPool复制、guided-section配置表安装/同步、后续构造器至SID，以及S02窗口恢复；两张照片缺少后续阶段不能独立证明其未执行，更不能宣称确定死锁。

证据out/device-tests/oem-retry-7e4ec36d-755e-440a-8f47-3c98ae38dbdc；原始照片仅本地D:/Code/PortingiOS/enuma/Media-enuma/OEM-v4-phone-retry-20261027-7e4ec36d。R027及原候选冻结，共享主线只读。无恢复按键待办；待现场字符串核对，之后继续离线归因。报告reports/enuma-oem-v4-phone-retry-20261027.json。
用户随后确认两组完整字符串一致、现场仅此两组。独立初读保留pending快照，另存phone-human-confirmation.json闭合确认；不再待人工核对。下一步离线分析call4返回至SID的实际路径与S02窗口清理。
