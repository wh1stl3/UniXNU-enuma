# 当前：registration-v5 接续复核通过，发布连接失败（2026-10-27）

已完整读取新会话 prompt，按规则、当前状态、现成固件和资格顺序接手。设备仓起点9f98d3e，固件fd94b265d1b0112c4a60d36a058d7b91efbb250d；接手时两工作树干净。唯一写入根为本隔离工作树，共享UniXNU-enuma只读；R027及旧OEM候选冻结，v4两笔consumed不重试。

最大可操作嫌疑仍为call4成功返回后的guided-section注册区间：16字节复制→0x5cc4配置表安装→后续构造/主入口；区间置信中等，唯一故障指令置信低，旧S02窗口恢复是竞争解释。v5的E01/S02观察call5、RVA5cc8安装前/真实返回，E03/S04观察SID前/后，S05观察真实CoreStartImage返回；缺页不能直接判死锁。详见[代码归因与候选范围](operations/2026-10-27-oem-registration-v5.md)。

唯一当前候选仍为out/oem-registration-20261027/qualification3/image.img，3153920字节，SHA256 f9bd10078db5b049e7ad0cd050300c872cdcd1d0d975b6ed3065e4b03dac650d。FD SHA256 f83b1869f65377ec2b4af4bdc69f1f64f0fcf41a3a296c6ea795a76d3b7fe6d5；qualification.json SHA256 9b532a16587cec5ce2c96f7085ec5c73aeed2aaec0a06bf23bcb4b7e739e31ed。trial 4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e，session 15050556181532298825，selected_call=5、oem-control，账本不存在，未claim/上机。

本轮默认离线runner通过，2446项来源绑定和镜像匹配；独立核验FD/资格摘要及共享树R027冻结image/qualification摘要均通过。没有修改源码、重建或回写旧资格。构建仍是f82039e基线的工作树快照，不称提交后重编。既有31项Python、ASan/UBSan、真实Core配置表与机器码负测的历史结果保留，本轮未重复宣称重跑。

本轮对两个GitHub分支做有界ls-remote，分别连接重置/443连接失败；随后显式向https://github.com/wh1stl3/uefi-enuma.git的oem-progress-20261027非force补推失败。未向固件origin、本地主线或main推送；因固件发布未确认，未继续设备仓推送。远端状态仍未确认，下一步网络恢复后先固件、后设备仓发布并核验。

本轮没有ADB/fastboot命令或设备动作，当前设备在线/Android状态未知；最后设备事实仍为v4自行回Android且独立核验通过。当前手机拍摄及人在场可长按恢复均未确认，不能继承旧就绪状态。发布确认后，重新取得当次拍摄/在场条件，由单次runner即时核验enuma身份、原备份、槽位、解锁及恢复条件，再执行已有授权范围内一次临时boot。75秒无合格返回停止追加、优先恢复并同轮记录；不flash/erase/改槽，不改内存或verified。当前是准备条件未齐，未发生设备硬停。

证据：out/oem-registration-takeover-20261027/takeover-audit.json、remote-before.json、firmware-publication.json。旧证据与原媒体保持本地。接续入口仍为[registration-v5 prompt](2026-10-27-oem-registration-v5-handoff-prompt.md)，其中上一会话任务范围属于历史；本轮已继续完成接手复核及有界发布尝试。后续软件或执行器修改必须另建资格，不回写qualification3。
