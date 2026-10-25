# 当前状态：D-241，S-028 独立显示掩码资格完成，准备单笔实测

2026-10-25T23:27:01+08:00。用户“继续推进 触发硬停再停”，无需逐笔批准。本候选尚未发出，源/资格/文档发布及即时身份、备份、恢复与摄像门禁后直接单笔临时boot。

已完成的mask观测均consumed，不重试：[{"trial": "S-023", "field": 1, "result": {"conclusion": "mask-inferred", "mask": 3, "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}, "automatic_android_return": true}, {"trial": "S-024", "field": 4, "result": {"conclusion": "mask-inferred", "mask": 3, "warning_code": 4, "stop_additional_trials": false, "direct_register_log": false}, "automatic_android_return": true}, {"trial": "S-025", "field": 5, "result": {"conclusion": "mask-inferred", "mask": 0, "warning_code": 1, "stop_additional_trials": false, "direct_register_log": false}, "automatic_android_return": true}, {"trial": "S-026", "field": 6, "result": {"conclusion": "mask-inferred", "mask": 1, "warning_code": 2, "stop_additional_trials": false, "direct_register_log": false}, "automatic_android_return": true}, {"trial": "S-027", "field": 2, "result": {"conclusion": "mask-inferred", "mask": 1, "warning_code": 2, "stop_additional_trials": false, "direct_register_log": false}, "automatic_android_return": true}]。跨启动的不同字段不能拼成一次同时成立的完整GOP证据。

D-233用户新规则保持：镜像发出前的fastboot查询异常不作整轮硬停；恢复核验后允许重新进入一次fastboot，仍须完整product/slot/unlocked检查。S-024首次仅查询异常、未发图，fastboot reboot后独立恢复；重新进入检查通过后才发图。原首次拦截事实保留reports/enuma-native-mask-S-024-preflight-attempt1.json，不能称那次运行固件或固件超时。

固件5712c00bbd48947b8e5b1db2c610c04890511e21，字段7（1活动全程/2非零时序稳定/3计数使能稳定/4双窗递增/5使能低两位为3/6同次活动、非零时序稳定、使能稳定、递增四项求交/7三次Timing全零且同次活动、使能稳定、帧推进）。用户要求适合时一次尽量多推进，故S-026优先合并字段6，旧2bb165f字段2仅离线归档未发出。字段6合并掩码3表示两路在同次三个样本同时满足四项；字段7专门区分Timing全零却仍满足其他运行前置的接口，不能由零值推断master/slave角色，不将跨boot证据拼接。同独立采集器，原R-004 MDP映射内最多26次读/两次100ms；先读STATUS bit0才读FRAME，不要求Enable==3。无像素/MMIO写、新映射、board/verified/分区操作，不发布GOP，不继承consumed像素批准。采集或元数据失败单独code5，不混入mask0。

实际warning1..4分别代表mask0..3；warning5采集失败。在完整GUID dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92的CoreStartImage返回点13/detail16，只有状态1..5进入cold终止，对应2/7/12/17/22秒，随后deadloop，无dispatcher fallback。与旧Core不同处已重新审计，不能声称整个Core与S-010字节相等。真实头文件504入口/状态/GUID、53单字段、521合并和525零Timing合并/错误选择器用例ASan/UBSan通过，旧默认返回路径回归通过。实际PE、源码、宏、FD表、96MiB完整FAT与Boot v3已冻结审查。

图1e47f6856beaa95e74869060b9b28c067ca9ed20a8c3bad247996b973b283e31，FDa3767884c3efac6621073069dc1c47275278a6596ded2f7f648998cf1041b28c；本地不可变归档out/inherited-gop/qualified-native-mask-5712c00-field7。资格reports/enuma-native-mask-qualification.json；实际代码reports/enuma-native-mask-code.json；主机reports/enuma-native-mask-host.json。现场原始视频和旋转图只留out、不上传、不录音。

S-021/S-022常量2/7秒boot-origin差区间[4.957,5.096]落入预定[4,6]，仅证明本轮时基能分辨常量差。新候选预先固定判读：{"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}。三次uptime/boot-id样本必须新boot、相交、宽<=0.25秒；整个原点区间完整落入唯一窗口才间接推断code。容差不得观察后调整，旧S-019/S-020仍ambiguous，所有S-001..022 consumed且不重试。时间推断不等于直接寄存器日志，也不是点屏/GOP成功。

75秒无识别恢复、恢复核验失败、相机/时基失效或新编码模糊，立即停止追加，当轮落实恢复与硬停交接。22秒终止上限低于主机观察期限并不保证返回。最近独立恢复证据out\device-tests\20261025T232006-recovery-reconciliation.json：Android完成/root/A槽/解锁/boot_a及vendor_boot_a设备和备份摘要一致。新实测后仍须再次核验及相机桌面确认。

主判断：现有复合谓词隐藏的是具体接口条件，先分离活动与递增，随后据实际掩码决定管线/使能/采集失败路线；不能由计数门拒绝直接判断面板关断。公开小米固定52a2f18原生v1读STATUS再读FRAME支持本观察方式，但不证明本机接管时状态。固件自产图案、GOP、CPU/SMMU扫描源关系、背光I2C与XNU/iPadOS仍未闭合。
