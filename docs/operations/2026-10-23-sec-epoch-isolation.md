2026-10-23 23:40 Asia/Shanghai · 新候选故障隔离审查

失败838b38f step3已于23:20:44人工恢复并完整核验，原镜像禁止重试。f15d520只在staging固定SEC横幅的source epoch，原内存/映射/verified不变。两次相同输入全构建的SEC TE SHA807c543145290eb7ff4c9fa7d30c58746e92fc8216fb5e33c6d2d7360cc843a2完全一致；其他可执行叶模块仅Pcd的RSDS后8字节不同，整FD并不相同。这排除一个已观察到的布局变量，不证明修复根因。

新试验仅epoch-control-b step0安装后Core返回，不执行GOP枚举/Mode/Info/span或MDP读写；比失败step3减少运行路径，不跳过对照测step10。image603a799ba2ce0e82651e23ef6f9e99351a63153e3ee388ea6fc815ae4d506cda，FD5eaf4ae0444b8657157164adf09b72cf02545cb5e3cef0f9b58db0e8894197b2，来源f15d520。两个构建均全链接/打包/候选审计通过，workspace及历史bundle五个负例通过。仍可能再次卡死，定时复位不是可抢占watchdog。

选择A：新源码step0最小路径，先重新确认设备/备份/root/槽/摘要/fastboot身份，使用已有现场恢复条件及前后截图；75秒不返回立即停止追加、请求恢复并当轮落实交接。选择B：只继续离线等待异常PC，当前无可用UART或持久日志，不能获得运行证据。根据用户持续推进和恢复后出新软件授权执行A，范围不新增内存/verified/分区审批；完整step3和step10保持未获新基线前禁止追加。

证据reports/enuma-sec-epoch-rebuild.json，两份out/entry-probe/epoch-control-{a,b}-.../candidate-qualification.json。历史bundle使用各自固定Git对象源锁；真实构建/启动仍受当前源锁和全部设备门禁约束。
