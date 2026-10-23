# 实际字段只读描述候选

代码7dc3bf1，固件主分支文档2b3849a，设备全套文档7c6e1c6。旧ab0cb79固定几何step11正/互补均无按键恢复，时序支持假设拒绝。新step12只解码实际SRC_SIZE、XY、YSTRIDE0低半字和格式/压缩，最多48读；按宽度/stride、对齐、裁剪后完整跨度检查较小splash保留区。跳过不满足条件的候选，取首个自洽有界描述，不证明其他候选、唯一/活动、颜色顺序或物理/IOVA一致。

本次两个候选均全链接、源锁/AutoGen/库依赖/FD/原OEM/Boot v3/资格与同源bundle通过。step10 image93a787117d8b72bf24c9397141b13b95332e694f2ef8c055b9a3eca29abc6b21，FDde159ec291cdfb30cabc083757eb4e755c059fc5eb37d756d32212ba3b4b29d4；step12 image3770151e19731745d253cff397f16cb16da752f389dcf321ba8fe3e0e92f09b7，FD602449c0598f1513dd12f546590653eced359fa5094b755f293d1e848b9ca982。尚未上机，不把主机10000样本/ASan/UBSan/AArch64通过当实机通过。证据reports/enuma-descriptor-bundle.json、enuma-scanout-descriptor-host.json；原始构建/镜像在out/entry-probe/descriptor-{control,pointer}-...。

当前选择：先完成全套文档提交推送，再完整设备门禁测试同源step10，确认Android完成/root/原摘要及无按键后才继续step12。候选B为仅离线等待实际数值/异常PC，现无可用UART/持久日志，不能取得新的入口观测；按既有只读临时启动授权选择A。新源没有地图/像素/寄存器写入、RAM/verified/分区变化。真正超时立即停止追加、优先恢复并同轮落实交接；受控拒绝不硬停。


2026-10-24 00:24:06 · 7dc3bf1 step10，ADB15.877秒/完成30.799秒，用户确认无按键，Android/root/原槽/解锁及boot/vendor_boot原摘要通过。image93a787117d8b72bf24c9397141b13b95332e694f2ef8c055b9a3eca29abc6b21，FDde159ec291cdfb30cabc083757eb4e755c059fc5eb37d756d32212ba3b4b29d4。
同源格式对照已完成。下一步先提交推送当前文档，再以完整新设备门禁运行step12。step12已离线资格通过、尚未实测。


2026-10-24 00:27:02 · 7dc3bf1 step12，ADB16.927秒/完成30.978秒，用户确认无按键，Android/root/原槽/解锁及boot/vendor_boot原摘要通过。image3770151e19731745d253cff397f16cb16da752f389dcf321ba8fe3e0e92f09b7，FD602449c0598f1513dd12f546590653eced359fa5094b755f293d1e848b9ca982。
step12已受控返回；只能结合时序评估描述谓词，不认证活动/唯一性或物理-IOVA一致。尚未写屏，不扩大R-004。
