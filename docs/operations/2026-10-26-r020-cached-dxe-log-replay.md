# R-020：真实DXE返回状态缓存回放（S-048）

2026-10-26T03:33:49.136994+00:00。用户本轮明确“让他继续推进 授权所有实机操作 注意硬停规则”，后补充“无需询问恢复问题 直接做”。本记录将该新授权绑定到本项目最小新候选，不恢复任何旧consumed许可；不重复申请已授予的实机权限，不把授权当任何实际门禁已通过。

A推荐并实施：Core在首个dispatch detail仅一次安装私有v1只读Snapshot协议，日志仍128条RAM；provider在同源Native6/全帧NormalWT/EL1通过后取真实快照，选最新point13(CoreStartImage返回)而非入口前SUCCESS，绘制完整EFI_STATUS及ordinal。三行固定格式但内容来自运行记录：C0d O<8hex ordinal>[有丢弃则+], S<高32位>, 空格<低32位>；C表示缓存回放，0d是十六进制point13，非直播DEBUG。

精确图c75b6c863d294d7b3e2772ddb7f46a239c7915685b9c7309f11310049945d8bf，固件962f8208a9d2eca3bc626db67090e28519e088e6，FD 57d94260b69ee1a19df285902ab539591fb3e1787e0b374e5194ac05393be884；归档out/inherited-gop/qualified-dxe-log-r020-962f820。CPU原点256x96、3x5 hex字形4倍、最多24576字保存/同源原始配置复核/绘制及逐字验证/一次2秒保持/完整恢复及读回。最多73728像素load、49152 store、3DSB；两Native6观测最多660 MDP只读、四100ms；最多18432原有全帧AT查询；无缓存行操作/MMIO写/页表改写/新映射/分区写/正式GOP。堆栈Arm单独实编译98544字节，低于128KiB，原CPU主栈256KiB不改。requirements22/alpha/最终stage2/SMMU及全部verified保持。

候选B：只导出RAM快照，不写屏幕，低风险但无法完成实机日志上屏；C：直接放行BDS/GraphicsConsole/ConOut，有SetMode/全屏清除及未闭合GOP问题，不推荐。A为当前最低依赖的真实状态输出，代价是区域由旧128x32扩大且不能称完整日志控制台。

离线：1万日志事件、快照/回放、协议安装一次/失败、五个固定EDK Arm对象；24像素通道排列、960行/阶段失败边界、无有效页面零像素访问、保存/重验证/完整恢复和失败优先级通过；旧白条/文字回归通过。5项scope/时间窗、10项FD策略、11项保护批准测试通过。完整FD、实际cc_resp、Core/provider协议头一致、完整FAT、Boot v3和实际PE/栈/恢复反汇编审查绑定；见本候选qualification及code报告。编译通过不等于实机通过。

返回码1=前置/协议/快照/无point13/保存/复核拒绝且无store；2=图案/读回拒绝但原区恢复；3=保持拒绝但恢复；4=恢复未建立硬停；5=CPU事务及恢复完成，视觉须相机单独判读。预声明sampler/hold总包络0..2.4s；固定S021/022基线、±1s、整区间包含和boot-id三样本/.25s限制，不能据观察再调窗口。具体计划已冻结于qualification。真实文字必须镜头独立可见/内容可辨，码5不能代替视觉或表明ConOut/GOP/菜单通过。

新鲜已完成预检out\device-tests\20261026T111629-recovery-reconciliation.json：Android完成/root/A槽/解锁及两分区设备/备份摘要一致。相机1920x1080，原点/屏幕已自行旋转查看；当前有影像清晰度限制，若字不能辨即记未验证。启动前仍由runner重做即时目标/备份/product/slot/unlocked门，并先完整提交推送全部当前文档和两仓源码；相机连续记录关键节点，原始AVI/帧只留本地，不录音/外传。

仅一次临时fastboot boot，无flash/erase/改槽。75秒无受控恢复、恢复未建立code4、观测/时钟失效或歧义、摘要或身份异常立即停追加，优先沿原已验证冷返Android/fastboot恢复，不换包重试；相机继续记录恢复。若需人工，按实际状态报告，不重复询问恢复授权。硬停当轮对齐STATUS/HANDOFF/WORKLOG/DECISIONS/NEED-REVIEW/PENDING-HUMAN及适用NEED-HUMAN并提交推送。S-001..047/R-018/R-019全部consumed。
