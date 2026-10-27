# OEM 首次调用运行版与部署边界

用户在“可以部署了”后选择“继续补齐 OEM 运行版后部署”。本次选择原始 OEM 对照：先验证追踪/取证路径，不同时引入 nabu 参考的 MMU 参数变化。elish 的原生双 DSI/K81 初始化契约保持。R027/S055 冻结且未消费；旧 stage10 对照/MMU 固件仅是离线证据，不能作为本次运行镜像。

独立工作区为 D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display。原共享 UniXNU-enuma 及其 firmware 不改；无推送，无 flash/erase/改槽/内存基址/verified 变化。用户当前不推送约束优先于历史实测前推送惯例，源码和交接仅本地提交。

## 运行契约

生成的身份头绑定原厂 PE、归一化文本指纹、随机 session 和 trial UUID。只有 OEM control 可以启用 --oem-run-config；默认构建仍在 stage10 停止。运行版 stage13/detail13 精确 GUID 选择实际 CoreStartImage 返回，保留派发完成后的复位 fallback；没有异步看门狗。

首个包装服务 call=0 在转发前输出一次取证窗口，320×160、位置(64,96)、停留8秒；必须通过原有映射/路由/CPU WT 条件并完成保存、写入、恢复和读回。该次取证拒绝或恢复未确认时终止，不调用原服务。后续调用不重复绘制。屏幕记录是调用前摘要，不能据此声称原服务已经进入或完成。

运行版检查 BSP affinity，并在事务期间屏蔽本 CPU 异步中断，用直接计时避开 Boot Services Stall。此举没有证明 AP 或外部 DMA 排他性。异常处理在格式化日志前尝试冷复位，复位返回则永久暂停；不能保证物理复位一定成功，也不能保证异常时帧缓冲已恢复。

## 部署入口

scripts/qualify_oem_runtime.py 核对最终 FD、真实 Core、OEM PE、运行身份、异常头和 Boot v3 解包回读。scripts/oem_runtime_candidate.py 绑定镜像/源码/范围与单次 ledger；scripts/run_oem_runtime_trial.py 默认仅离线核验，显式执行要求当前录像和人工恢复准备。独立 ledger 在首次设备变更前排他创建，不因失败或运输超时重新激活。

入口只选择原先绑定的 enuma，复核本地备份、设备分区、Android/root/槽/解锁。只发一次 fastboot boot；观察实际 USB 离开后再返回，核对 fastboot 身份才普通重启 Android，并重新核对原分区。75秒无返回停止追加并记人工恢复待办。Android恢复最多等待120秒；无自动第二镜像或 boot 重试。

2026-10-27 12:15/12:16 +08 已做本轮只读身份和恢复核验，证据 out/oem-deployment-review-20261027-1/{device-precheck,recovery-precheck}.json。实际启动前必须即时重查。当前没有发出设备写入/重启/boot，尚无 OEM 实机执行结果。

## 验证与限制

out/oem-runtime-binding-check-20261027-1/result.json：ASan/UBSan 身份/交叉变体/首次取证失败不得转发检查通过；运行版板级 AArch64 对象通过。tests/test_oem_runtime_candidate.py 的6项测试覆盖正常单次领取和镜像/源码/范围/缺当前准备/重复领取拒绝。

构建 out/oem-runtime-build-20261027-1 基于本地固件 b6fe1a2 加哈希绑定开发快照；后续本地提交不把它改称干净提交构建。旧组件749种损坏及恢复失败证据继续独立保留，不冒充本次实机结果。最终镜像摘要和机器码检查以新 qualification.json 为准。

当前必须区分：软件审计通过、CPU事务完成、相机拍到可读记录、OEM返回、生产GOP/BDS/输入成功。没有 return 记录不能直接判死锁；没有可读画面不能把定时返回当具体执行日志。相机原始影音仅本地，助手先独立判读再请用户核对。
