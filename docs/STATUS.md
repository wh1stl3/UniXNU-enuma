# 当前进度：原生DSI活动状态与双窗递增探针完成构建审计

2026-10-24 Asia/Shanghai。用户明确“按你的判断继续，取得有效增量证据，我可以在场恢复，按需使用摄像头”。沿已有临时boot、全套文档逐笔提交推送、即时身份/备份/恢复门禁执行，无新增逐笔审批。目标是取得可解释的UEFI阶段递增证据，不能用Android计数或静态通过替代。

## 当前实现和资格

固件60f38e9eee70151c09d4fe30bc992ee6835f9b79，设备gitlink和64项源锁固定。保持R-004既有MDP映射，版本读取0xae00000；DSI基址0xae6b800/0xae6c000，原生INTF_STATUS在+0x26c。

step17仅在版本major6后检查两接口STATUS bit0，最多3读。step18依照固定小米52a2f18的v1 get_status读取路径：实际活动位作为采样门，记录timing/enable稳定性，不再要求旧Linux完整配置值低两位=3。新契约不改变旧step15/16语义和拒绝结论，不写计数使能。无活动接口不采样/等待，版本不支持不访问接口。

step18最多26读及两次既有gBS->Stall(100000)。同一原始活动接口须在两个窗口内各非回绕递增1..64；所有采样接口不允许递减或超64，活动bit0保持、timing/enable原字和最终版本一致。等待错误/警告、状态或配置变化、零进展、回绕/复位拒绝。非原子读不能排除瞬变或巧合复位；支持只说明活动接口计数推进，不证明SSPP/LM路由、像素、面板/背光、物理IOVA或精确频率/实测100ms。

27项fake MMIO/wait用例O1/Oz+ASan/UBSan、真实AArch64仅gBS、GOP补丁组合/真实Mu传输、源锁与workspace门禁通过。三份完整链接/补丁回退、30OEM PE/DEPEX、AutoGen/库依赖、实际FD目标加载/无识别到目标存储、BootShim/FD/Boot v3和同源宏差异bundle通过。机器代码审计仅覆盖可识别的入口CFG常量/表访问，不是完整间接访问/所有控制流证明；读数上界和分支契约由固定源码及测试约束。所有资格为离线，实测只见下列结果。

| 候选 | step/query | Boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- | --- |
| native-active | 17/1 | `9068815fc7d5eb5862686aae1500404bf0c5e7f0a8ef9221ba66a1c190bf1fc4` | `7175c9cf7dd346c4e97df6f296da59921929a2e8b237dcd6cbeddb503a2a297e` |
| native-progress | 18/1 | `f1fb4d377744ba7aa69162aa7998a18e51c12cb0575d961208219843b58203a3` | `0692327ba65fa877eadd434e35f809854a1dc4bb639ebee962fcc30515eb5de3` |
| native-no-progress | 18/2 | `cc3a698fcbaa53a6249cd04a7b1150a357743f44beb39768325c58ec30f4d8d1` | `58d378d37093545ca68e518c2b62271d53307ac8758f7bd854253fdb2a4118da` |

query1为非错误标记门、query2为错误标记门，Core命中延时2秒；未命中可走7秒同步派发完成兜底，非watchdog。原生状态候选在前，双窗正/互补在后；单笔短返回不能独立证明寄存器数值或活动。双窗成功的互补时序可支持“同一接口每窗差值在1..64”的谓词，仍不是数值快照日志。

## 实际设备与结果

native-active step17/query1：2026-10-24 03:04:04，recovered-android-boot-complete；ADB16.063秒/Android完成29.266秒；用户无按键True，原摘要True，独立恢复核验True。

native-progress step18/query1：2026-10-24 03:05:34，recovered-android-boot-complete；ADB16.969秒/Android完成32.266秒；用户无按键True，原摘要True，独立恢复核验True。

双窗互补尚未齐备，未取得有效增量证据。

## 下一步和边界

先提交推送所有当前文档，再以即时身份/备份/恢复门禁临时启动 native-no-progress，逐笔独立恢复与无按键确认后再推进。

只读留必要前后相机截图及主机时序/日志；实际输出、变化判读或恢复时再录像。白点是用户键盘反光，不算输出。用户已确认可在场恢复，Android/fastboot恢复已核对，TWRP/UART未验证；超时停追加先恢复并当轮落实交接，恢复核验后继续离线修复，不原样重试失败镜像。

R-005 consumed，不重放像素；无像素/MMIO/分区写入、新映射、内存/基址/verified变更，保留51MiB heap/512MiB owned/example=true/Boot v3。旧f6c59ba计数资格用source-history/uefi-f6c59ba.lock.json冻结，旧338db59时序和c73eb6e像素同样沿历史源锁保存。顶层构建/FD报告对应最后候选，各份独立快照在out/entry-probe，镜像/日志/相机/标识/备份仅out。

故障主判断仍优先活动SSPP/LM/CTL路由与持续显示交接，Boot头低优先级，见operations/2026-10-24-display-fault-hypotheses.md。后续应把有意义递增绑定到实际输出链路，不能仅因计数推进宣称可见写屏。文本后端尚未集成，当前诊断固件在Core门主动返回，DXE/BDS/UniXNU菜单未放行，尚未进入XNU。

证据：firmware/docs/dsi-native-progress.md、config/dsi-native-probes.json、reports/enuma-dsi-native-{host,bundle,device,preflight}.json（设备/预检仅实际产生时存在）、enuma-native-display-diagnosis-sources.json。来源为已锁小米内核52a2f18的INTF_STATUS/v1 get_status、catalog major5/6功能选择及KMS core_rev读取；源码未导入。

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。
