# 当前进度：固定几何假设已拒绝，新描述解码器离线构建中

2026-10-24，Asia/Shanghai。设备最后核验为Android启动完成，root/原槽/解锁与boot/vendor_boot原分区摘要通过；用户确认最近全部测试均无按键。当前无待恢复设备、无人工按键待办，未新增实机启动。

## 已取得的实机证据

| 固件/步骤 | ADB返回 | 结论与限制 |
| --- | --- | --- |
| f15d520 step0 | 15.856秒 | 安装后Core返回，无GOP/MDP额外访问 |
| f15d520 step9/10 | 16.964/16.947秒 | 时序支持splash地址存在及线性未压缩4字节格式谓词 |
| ab0cb79 step10 | 16.919秒 | 同源格式对照，无按键返回 |
| ab0cb79 step11 selector1 | 21.196秒 | 长返回，不是几何通过 |
| ab0cb79 step11 selector2 | 15.866秒 | 与上一笔结合，支持固定几何/stride/跨度假设被拒绝；具体字段未知 |

最近一笔2026-10-24 00:08:19，完成核验30.310秒。image a1d729570ea8e7e210bfcab9bbb13f20b8268e313754d76279bb98ab56954ce7，FD d93a1cec8c27ef1ee6653a87b250b8a89292f15ea79103c79f3d38546d1f064f。证据reports/enuma-geometry-device.json、operations/2026-10-23-geometry-layer.md。有界受控拒绝不是硬停。

## 当前源码、构建与未执行项

固件代码7dc3bf1已推送，设备工作树gitlink/60项源锁已更新；设备最新已推送085deac记录ab0cb79三笔实测。新设备集成及文档同步尚待提交。7dc3bf1的step10同源对照已全链接/打包及候选审计，image93a787117d8b72bf24c9397141b13b95332e694f2ef8c055b9a3eca29abc6b21；step12正在完整构建，两者均未上机；两者仍须实际链接、AutoGen/静态库、FD、Boot v3及同源配置检查，不能把主机测试写成实机通过。

step12只读实际SRC_SIZE、XY裁剪、YSTRIDE0低16位、格式/压缩字段，寻找第一个在较小splash区间内自洽的描述，最多48次寄存器读。它不要求源矩形等于面板输出，不认证其他候选、唯一性、活动性、颜色顺序或物理地址与IOVA一致。固定SDE源码610..634行证明YSTRIDE0包含两个16位stride字段；这只是解码依据，不是本机数值。

新增解码器边界/格式拒绝、裁剪/padding、packed stride和10000样本，在O1/Oz+ASan/UBSan通过，AArch64对象无外部依赖。既有84 scanout用例和GOP240/7对象/48标记/真实Mu传递6用例/7 CLI拒绝通过。证据reports/enuma-scanout-descriptor-host.json、enuma-scanout-host.json、enuma-gop-audit-host.json。

下一动作先完成离线候选及审计并同步所有当前文档，再核对身份/匹配备份/Android完成/root/原槽/解锁/原摘要及fastboot身份。未完成前不追加设备启动。无新批准申请；R-004只允许0x0ae00000/0x85000映射与有界只读，不包含像素/显示寄存器写入。

## 历史硬停与恢复

838b38f step3于2026-10-23 23:16:54临时启动后75秒无返回，已当轮停止追加并落实交接；用户人工恢复后23:20:44核验Android/root/原槽/解锁/原摘要通过。旧失败image a8061b8510935bbe8991ec0d8723a1bcc3b1a9460422ecc9ac30ffe13813016a不原样重试，根因/故障PC未知。新step0及只读路径返回不证明step3修复。

SEC source epoch固定后的双构建SEC载荷一致，其他可执行叶模块只差Pcd RSDS八字节；整FD不一致，不宣称完全可复现或已定位故障。硬停证据见operations/2026-10-23-linear-control-timeout.md，离线隔离见operations/2026-10-23-sec-epoch-isolation.md。

用户最新要求：下一次硬停前落实所有文档；现在完成当前状态同步，下一笔实测前必须提交推送。真正超时仍立即停止追加、优先恢复，并在同轮补齐实际停点/模式/摘要/恢复结果/继续条件。人工恢复后持续离线分析和新软件，不原样重试。历史操作记录与WORKLOG保留时序，STATUS/HANDOFF仅保留当前有效状态。

## 边界与剩余主线

尚未写屏或进入XNU。保持51MiB DXE heap、512MiB owned、example=true及所有verified不变，不flash/erase/改槽、不新增保留区。TWRP/UART未验证，Android与匹配备份为已核对恢复路径。参考仓只读，产物/设备标识仅out/。

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。


固件文档主分支2b3849a已推送，修正README/构建归属和历史说明；设备代码有意固定7dc3bf1以完成同源重建，子模块中的README/AGENTS属于该提交历史快照，当前工作规则与状态以本仓及固件主分支文档为准。
