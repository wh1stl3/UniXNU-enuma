# 当前进度：同源格式对照已受控返回，实际描述探针待实测

2026-10-24，Asia/Shanghai。当前设备Android启动完成，无人工按键/恢复待办。

2026-10-24 00:24:06 · 7dc3bf1 step10，ADB15.877秒/完成30.799秒，用户确认无按键，Android/root/原槽/解锁及boot/vendor_boot原摘要通过。image93a787117d8b72bf24c9397141b13b95332e694f2ef8c055b9a3eca29abc6b21，FDde159ec291cdfb30cabc083757eb4e755c059fc5eb37d756d32212ba3b4b29d4。

同源格式对照已完成。下一步先提交推送当前文档，再以完整新设备门禁运行step12。step12已离线资格通过、尚未实测。

## 源码与资格

代码7dc3bf19c2997d7203e305697564e7a2586b57cd，60项源锁及gitlink固定；固件入口文档2b3849a已推送，代码为同源镜像重建有意保留7dc3bf1。全套文档门禁7c6e1c6/b10b1f2/bc3e29f已推送；本笔结果和当前文档同步发布，精确提交见Git历史。

两份候选已完整构建、AutoGen/静态库、原OEM、FD、Boot v3、候选资格与同源bundle通过。step10 image93a787117d8b72bf24c9397141b13b95332e694f2ef8c055b9a3eca29abc6b21；step12 image3770151e19731745d253cff397f16cb16da752f389dcf321ba8fe3e0e92f09b7、FD602449c0598f1513dd12f546590653eced359fa5094b755f293d1e848b9ca982。

step12只读实际源矩形、XY裁剪、stride低半字及格式/压缩，最多48读，检查对齐、行宽与裁剪后完整跨度在较小splash区间内。可跳过无效描述选择首个自洽候选，不认证其他候选、唯一性、活动性、颜色顺序或物理/IOVA一致。固定SDE源码610..634行解释两个stride半字，不是本机数值证明。10000样本/O1/Oz/ASan/UBSan/AArch64对象无外部依赖通过；既有84 scanout及GOP240/7对象/48标记/真实Mu6用例/7 CLI拒绝通过。

## 历史结果与限制

f15d520 step0/9/10无按键返回（15.856/16.964/16.947秒）。ab0cb79格式对照16.919秒，固定几何step11 selector1 21.196秒/selector2 15.866秒均无按键返回；互补时序支持固定几何/stride/跨度假设拒绝，具体字段未知，不把它当通过或硬停。实测里程碑367134b/a50d0fb/085deac已推送。

旧838b38f step3于2026-10-23 23:16:54启动后75秒无返回，已当轮停追加和落实交接，23:20:44人工恢复及Android/root/原槽/解锁/原摘要通过。失败image a8061b8510935bbe8991ec0d8723a1bcc3b1a9460422ecc9ac30ffe13813016a不原样重试，根因/故障PC未知。固定SEC source epoch后双构建SEC载荷一致，Pcd仅八字节RSDS差异，整FD不一致；不称完全可复现或已修复。新scanout路径不调用GOP Mode审计。

## 执行边界与交接

尚未写屏或进入XNU。R-004仅0x0ae00000/0x85000映射和有界只读，不含像素/显示寄存器写入。51MiB DXE heap、512MiB owned、example=true与全部verified不变，不flash/erase/改槽、不新增保留区；UART/TWRP未验证。参考树只读，镜像/备份/原始日志/私有标识仅out/。

下一实机前先落实并提交推送全套当前文档，再核验唯一enuma/匹配备份/Android完成/root/槽/解锁/原摘要及fastboot身份。真正超时立即停止追加、优先恢复，并同轮补齐模式/候选摘要/恢复结果/继续条件，恢复后刷新；人工恢复后继续离线出新软件。受控谓词拒绝不硬停。当前无新增批准/现场待办。

证据reports/enuma-descriptor-device.json、enuma-descriptor-bundle.json、enuma-scanout-descriptor-host.json；operations/2026-10-24-bounded-descriptor.md、2026-10-23-geometry-layer.md、2026-10-23-linear-control-timeout.md。最新恢复原始目录见out/device-tests/current.local.json，公开文档不含设备标识。

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。
