# bootprogress 折行版 r3 刷写记录

- 授权范围：指定 r3 镜像仅一次显式刷写 `boot_b`，不重启。
- 最终审查：reviewer `ses_dec48af8effe85M2w5V8uyAIkP` PASS；本包未经 deep_reviewer。审查结论由主控提供。
- 指定镜像：`out/bootprogress-wrap-20261126-r3/boot.img`，169951232 B，SHA-256 `eab38cf6070d2a43e38db48a962506663d8326c198bdce26080d0b0feae05a27`。
- 结果：预检中止，未进入刷写。镜像大小与 SHA-256 核对一致；PowerShell 脚本误用大小写不敏感的自动变量 `$Matches` 保存设备列表，正则匹配后该变量变成哈希表，追加时报 `InvalidOperation`。为防后续误操作，终止预检进程；未创建本轮 claim，未执行 `flash`、重启或其他启动动作。门禁未完成，未重试。`self-checked`

## 修正预检后的一次刷写

- 主控确认原授权仍有效；修正宿主脚本变量名后，合成枚举的唯一、多台、不匹配三分支通过，镜像大小和 SHA-256 与上述指定值一致。
- fastboot 型号核对唯一 enuma，当前槽 `b`、`unlocked: yes`、`boot_b` 201326592 B 门禁均通过；随后以 `CreateNew` 原子创建 `.cache/bootprogress-wrap-r3-flash-20261126.claimed`，该 claim 已消耗，不得访问、删除或重放。
- 2026-11-26 01:27:20.1786767–01:27:24.8034546 +08:00，一次显式 `fastboot -s <serial> flash boot_b`，退出码 0；`Sending 'boot_b' (165968 KB) OKAY [4.134s]`，`Writing 'boot_b' OKAY [0.373s]`，总计 4.593 s。
- 刷后未发送设备命令；无重启、切槽、continue 或临时 boot，无回读或启动验证，阶段不提升。`self-checked`

## 后续重启与观察

- 主控提供：2026-11-26 08:40:38 发生后续重启；这是上述刷写之后的独立动作，不改变刷写当时未重启的记录。具体命令及返回值未在本记录中核实。
- 本地 `media/bootprogress3.jpg` 单帧 SHA-256 `17603cfa07adc2a173fcb768c6f8974580db4670ed285eb6010ef3ecfd99d783`，照片不入库。画面顶栏为 `LIVE: DEADLINE EXCEEDED - OS and diagnostic recording continue`，蓝色背景延伸到可见区域右侧；仅凭一帧不能证明全程显示效果或持续推进。
- 可辨字段：`time=1163s idle=790s IRQ=n/a monitor=1159 lost=n/a root=0 procs=n/a free=88649`；`UFS requests=224085 verified4K=990523 failures=0 integrity=0 published=2`；阶段 `Starting userspace`，历史列出 0s `Kernel startup`、1s `BSD initialization`、5s `Starting userspace`。这些均为页面单次异步采样，不证明持续运行或根卷挂载。
- 内核日志标题为 `snapshot boundary; ring overwrite unknown`；本帧可见 `enuma-fb` open/refresh/kick/scanout/swap 为 0、`enuma-bb` calls=0 overflow=0，以及 `enuma-ipc` send=34904 recv=24738、bb send=25 recv=25、sb send=113 recv=83。这是屏上文本而非独立 IPC 采集；不能由此补足本轮不可用的 IPC/显示采集。本帧未展示可核实的长行续行效果，不能以单帧证明折行功能完整或日志无截断。
- 显示 stage/PM/guard、swap/copy/retirement、handoff、client/frame history 字段均显示 unavailable；进程快照、exit records 和 UI trace 亦不可用。`Starting userspace` 是 `load_init_program` 之前的打点，不能据此声称 PID 1 已启动。页面 deadline 不是操作系统卡死的证据；单帧不能证明时间推进、持续稳定或完整日志，不与其他轮次合并作证，阶段不提升。`self-checked`
