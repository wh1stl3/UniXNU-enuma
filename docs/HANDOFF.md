# 当前进度：DSI时序使能只读探针已实现并完成构建审计

2026-10-24 Asia/Shanghai。用户明确要求实现DSI时序使能只读探针，完成构建审计并落实全部文档后直接实机验证；用户可在场恢复，按需摄像。无逐笔重新审批要求；即时身份/备份/恢复、每笔前当前文档提交推送和超时停止追加规则保持。

## 当前软件与范围

固件338db59/设备gitlink及62项源锁固定。step14严格按固定Qualcomm SDE及保存enuma DT，只读取0xae6b800与0xae6c000各一次，即两个DSI INTF_TIMING_ENGINE_EN；至少一个非零返回成功，两者零返回EFI_UNSUPPORTED。只分类时序配置使能，不是活动scanout、SSPP路由、计数增量、面板/背光、物理/IOVA或可见输出证明。无需新映射、heap、库/构造器、timer、显示或计数写入、像素访问。

8项DSI主机用例在O1/Oz+ASan/UBSan通过，含null/两者零/单边及双边非零/非bit0值/最大值、精确顺序和两读上限；真实AArch64对象两次加载、无存储/调用/外部依赖。84项旧scanout回归、GOP provider补丁组合/真实Mu warning传输、像素错误旗标及7项审批门禁通过。三份完整固件链接/补丁回退、30个原OEM PE/DEPEX、AutoGen/库无新增reset/PSCI构造器、实际step14 FD中的两个目标加载且无目标存储、192字节BootShim/3MiB FD/Boot v3和同源bundle通过。只有step/query宏不同，所有像素旗标为0。均为离线资格，未测阶段不能记为硬件通过。

| 候选 | step/query | Boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- | --- |
| dsi-control | 12/1 | `9671a05975cebf613fa352e422fbb9f94b103cf296b2b98513713943425a0e5b` | `2917d0f0c4cdad9ec77cc79e60338bae3b40eecdc4bc3030942a3f760c3dfd3a` |
| dsi-enabled | 14/1 | `11311dfc2cd87b7b3a667af3f9a82a3644cc8a830b01e2c3f2f69daacb2dbcd3` | `d1f66fa1579073227ab487de48ff718569ade91a275729f9c4d4d2f31c25c2f8` |
| dsi-disabled | 14/2 | `25662b789fdbd1b6f82ddcad8b6e9f077d26bfad40b8b866519fae7d0053b466` | `93ad4f44d6ad80ada7e9dc49625b4133d93204115072e61eb68fa44b5b66d17c` |

query1在非错误标记后由Core延时2秒返回，query2在错误标记后返回；未命中目标时可能走7秒同步完成兜底，兜底不是watchdog。按同源step12→step14/query1→step14/query2逐笔恢复后推进。单笔短时序不能独立证明目标命中或数值状态。

## 最新设备结果

dsi-control（step12/query1）：2026-10-24 01:59:48，recovered-android-boot-complete；ADB15.906秒/Android完成29.797秒；用户无按键确认True，恢复原摘要True，独立后置槽/解锁/root检查True。

互补结果尚未齐备，配置使能状态未判定。

## 下一步、恢复和限制

同源step12已返回；先落实用户无按键证据、Android完成/root/槽/解锁/原摘要，提交推送全部当前文档，再临时boot step14/query1。

只读探针按用户偏好留必要的前后截图、主机日志/时序；出现实际屏幕输出、需判读变化或恢复时连续录像。相机反光不算设备输出。用户已确认可在场恢复；Android/fastboot沿既有恢复证据，TWRP/UART未验证。无返回立即停追加，优先恢复并当轮对齐STATUS/HANDOFF/审核/人工/WORKLOG/DECISIONS；恢复核验后继续离线分析及新软件，不原样重试失败镜像。

R-005已消耗（consumed），旧c73eb6e像素对照与实验仅历史证据，审批账本不变；config/pixel-preview-probes.json通过source-history/uefi-c73eb6e.lock.json重放历史离线资格，不继承为新源码实测或重新授权。没有像素或显示/计数寄存器写入，不flash/erase/改槽；51MiB heap、512MiB owned、example=true及全部verified不变。尚未进入XNU或确认可见写屏。

当前证据：reports/enuma-dsi-timing-host.json、enuma-dsi-timing-bundle.json、enuma-dsi-timing-device.json（若已执行）、enuma-dsi-timing-preflight.json（若已核验）；原始日志、镜像、标识、备份、相机画面仅out。顶层build/FD/payload报告对应最后构建的step14/query2，每份独立快照在out/entry-probe。复现check_dsi_timing.py、check_dsi_timing_bundle.py、audit_enuma_fd.py；实现/来源见firmware/docs/dsi-timing.md和operations/2026-10-24-display-activity-plan.md。

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。

接手顺序AGENTS/STATUS/DECISIONS/NEED-REVIEW；源码338db59，按config/dsi-timing-probes.json及各份qualification/bundle核验。发布状态以本轮Git提交及远端核验为准，不预写成功。
