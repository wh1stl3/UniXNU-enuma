# 当前状态：D-249，S-032 原生显示管线合并审计资格完成，准备实测

2026-10-26T00:20:20+08:00。用户要求“继续推进 触发硬停再停，尽量一次推进最多的验证点和实测点”。本候选尚未发出。全部当前文档提交推送、即时身份/原槽/解锁/备份/恢复和相机门禁通过后直接单次临时boot。

## 已证实与主判断

S-023活动mask3、S-024双窗帧推进mask3、S-025 ExactEnable3 mask0；S-026同次活动/非零Timing稳定/Enable稳定/帧推进mask1，S-027非零Timing稳定mask1。S-028同次三次Timing零且活动/Enable稳定/帧推进mask2。因此第二路Timing零不等于接口停止；旧非零Timing/Enable低两位3门可能过严。所有S-001..028 consumed，不重试；S-024首次仅预启动查询失败未发图。

S-029完整native审计有效返回Topology类别：boot-origin22.241..22.328秒，Android44.719秒。S-030细分返回source-staging-topology-rejected：22.257..22.322秒，Android45.750秒。S-031返回border-only-normalized-two-source-route：17.246..17.316秒，Android40.812秒。三笔独立摘要和相机桌面通过，均consumed不重试。已定位到当次border位与严格staging门的差异，不能称全三样本稳定性通过。

当前native_border_view=True。独立native border路径在解析副本仅清bit24，原始字保留并逐样本比较；其余严格源/混合器/布局条件不变。原严格和原native采样API不变，staging模式仍只分类。独立border路径全部64组合保留原始快照、330读失败、border中途变化/未知位/混合器/等待/帧稳定性拒绝通过。

新独立native sampler采用固定小米52a2f18 v1 STATUS bit0门控FRAME，允许Timing零和Enable低位非3，但保留完整Timing/Enable字相等、双路三样本活动、两个100ms窗口各非回绕递增1..64。复用现有六CTL、所选两源SSPP、两LM混合配置和布局解码，首次拒绝立即返回；不强行读取未满足路由前置的管线。旧严格GOP路径与固定基线逐回调一致，不因本审计自动放宽GOP。

## 当前候选与验证

固件c45191c00100634ba6cfa09ee06986edaafe8d53已推送。原R-004 MDP0xae00000/0x85000，最多330次读取、两次100ms，最高偏移0x6c26c；Splash0x9c000000/0x2400000不变。无像素/MMIO写、新映射、board/verified或分区操作，不发布GOP，不继承consumed像素批准。成功候选仍保留ADDRESS|TOPOLOGY要求。

选择器native_route_detail=True、native_route_staging=False；五码分类{"1": "non-topology-or-contract-rejected", "2": "ctl-selection-topology-rejected", "3": "source-staging-topology-rejected", "4": "mixer-or-layout-topology-rejected", "5": "stable-candidate-address-and-downstream-unproven"}。码义以本候选归档为准：staging模式code2仅支持局部清除已知border后恰好两条不同单源路由、无其他未知字段，code3源数量/编码、code4其他字段、code5混合器数量/重复源，code1其他结果。staging模式code5不是成功；不继续后级采样，不修改原快照。完整SimpleFb GUID dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92返回点13/detail16接受warning1..5，cold延时2/7/12/17/22秒后deadloop，无dispatcher fallback。

ASan/UBSan原严格路径固定基线330失败位置/负例回归、新native330读失败和两等待失败、活动门控/配置/帧稳定性通过；对fafb8a3 native基线逐330边界比较调用顺序/状态/输出一致，三个拓扑位置fixture通过；staging64个border组合/768单比特扰动/快照不变及负例、12480staging结果映射通过；真实头文件7200普通和10080细分类映射、504入口/GUID/状态案例通过。主机测试只证明模型与边界，不替代实机。实际构建源码/宏、PE、FD R-004表、完整96MiB FAT与Boot v3已冻结审查。

镜像SHA256 4bc3fb98f20d1ea7780556652203be17dd02b5c27b5e1e08b029bf1fb3283243；FD 92c4cf55b3f19818f8056e3cedbceb3f09f2a57cb922c086799088c4c252f5f3；归档out/inherited-gop/qualified-native-border-c45191c。资格reports/enuma-native-route-qualification.json、代码审计reports/enuma-native-route-code.json；详细审查docs/operations/2026-10-25-native-route-code-audit.md。

固定S-021/S-022校准计划{"baseline_envelope_seconds": [10.25199999997858, 10.347999999998137], "tolerance_seconds": 1, "sampler_seconds": [0, 0.2], "code_windows_after_issue": [[11.25199999997858, 13.547999999998137], [16.25199999997858, 18.547999999998137], [21.25199999997858, 23.547999999998137], [26.25199999997858, 28.547999999998137], [31.25199999997858, 33.54799999999814]], "source_trials": ["S-021", "S-022"], "full_interval_containment": true, "uncertainty_limit_seconds": 0.25, "limitation": "Indirect timing inference; boot overhead can change. No exact register or unique execution-path proof."}。整个boot-origin区间须唯一窗口包含，三样本新boot-id且交集宽<=0.25秒；不按观测调整容差。时间码仍是间接分类，不是直接寄存器值、物理路由或可见显示证明。

## 恢复、硬停与下一步

最近独立恢复out\device-tests\20261026T001127-recovery-reconciliation.json：Android完成/root/A槽/解锁、boot_a和vendor_boot_a与本地备份摘要一致。每笔之后重新核验并查看相机旋转图。原始视频/图像仅本地out，不上传、不录音。

D-233：镜像发出前fastboot查询异常不作整轮硬停；恢复核验后允许重新进入一次fastboot，完整product/slot/unlocked门禁仍须通过。不重复已发图，不忽略FAILED正文。真实75秒无识别恢复、恢复失败、相机/时基失败或新时间码模糊，停止追加并当轮落实交接；有效负分类继续分析。

按本轮类别推进运行稳定性、CTL/LM拓扑或源布局定位；稳定候选仍需CPU/SMMU扫描地址关系和下游路由证据，之后才谈受控图案与正式GOP接管。固件自产图案、背光I2C、GOP和XNU/iPadOS仍未闭合，不能声称点屏。
