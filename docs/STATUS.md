# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相；历史见WORKLOG。

接手入口：[HANDOFF](HANDOFF.md)。实现里程碑595d6a6已推送；本次仅补交接并重算两镜像摘要，均匹配既有报告，未操作实机。

## 当前状态

**GOP查询与复位已离线拆分：复位回到既有Core门，step0/1两候选完成全链接和打包审计，均未启动。上次无返回根因仍未确定。**
本轮按用户要求只离线工作，未调用ADB/fastboot、未重新查询设备、未录像或启动镜像。
最后实机仍为250849f于19:45:38启动后75秒无自动返回，用户人工恢复，19:48:15主机确认Android完成/root/解锁/原槽/原boot与vendor_boot摘要通过。不能把历史状态视为下一次的新门禁证据。

见[拆分说明与验证顺序](operations/2026-10-23-gop-core-return-split.md)、[候选审计](../reports/enuma-gop-core-split.json)。旧完整查询/互补镜像不重试。没有数值GOP快照、真实scanout、像素/菜单或XNU通过证据。

## 本轮实现和证据

- 固件e286834/54项输入锁，SimpleFb INF恢复原文件，移除新增Timer/Reset依赖及本地复位调用。实际构建的AutoGen和静态库清单确认无新增PSCI构造器/复位库；Core原StageCheckpoint头保持相同摘要。
- 私有非错误warning 1/5传回阶段通过/错误标记。固定Mu实际入口/返回段主机验证标记保留、warning驱动不卸载，CoreExit复制状态已有源码核对。安装前错误保持原路径，不冒充标记。
- Core仅在最终point13/detail16、完整SimpleFb GUID和精确标记匹配时复用两秒门；普通成功/其他warning/错误/其他hook不匹配，原七秒正常完成兜底保持。同步兜底仍不能救卡死。
- 五层累计：0安装后直接返回；1枚举+释放；2加HandleProtocol；3加Mode/跨度；4加QueryMode/比对/释放。各层都保持禁绘制/Probe早退，不改物理保留区。step1/2尚不能区分服务与释放卡点。
- 137组真实Mu头/ASan/UBSan阶段/参数检查、四份step1–4的AArch64对象、30组实际补丁标记、六组真实Mu状态传输和七组CLI拒绝通过；Core完整177组回归通过。
- step0与step1两份候选实际AArch64全链接、core还原、30OEM/FD/192B BootShim/v3通过。只改ENUMA_DIAG_GOP_STEP；源输入一致，镜像嵌入FD与各摘要核对通过。step2/3/4尚未单独全链接打包，不称实机通过。
- 复核已锁elish/SM8250 SimpleFb E5缓存摘要，借鉴提供者/诊断分离，不移植其清屏、cache或PCD地址。它不能解释本次超时根因。

## 下一步

继续保持离线，实机须有新的执行指令并重新评估当时恢复条件。下一轮只先验证step0，证明新标记回Core及既有复位通道能受控返回；再考虑step1枚举+释放。不直接跳到完整QueryMode。
若step0无返回，立即停追加并恢复，范围仍包括更早路径/状态传输/Core返回，不归咎GOP调用；若step0正常而step1不返回，再围绕枚举/释放缩小。
长返回不单独证明阶段错误，可再评估同step选择器2，但不能用旧250849f互补镜像替代。生成镜像无需确认，新增内存/verified/破坏性分区仍按原规则。

无屏幕日志时不持续录像，采用必要截图及主机日志/摘要/时序；实际显示变化或按键判读时录像。电源键在右上角，已有明确画面/用户反馈不重复询问，遮挡/窗口外不推断。当前无人工按键待办。

## 系统与内核现状

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d。
macOS CI39927966148/head250cdf9已真实链接crypto plain/namespace、pthread、ArmDTPlatform、ArmCpu服务与源内核；21417672B内核SHAb940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d，本地NativePrelink解析通过。仅源平台链接，未预链接donor或启动，正式board归档/opt-in/ADT接回仍待做。

64MiB配置专用FAT已生成并双份一致，仅ENUMA FAT DISCOVERY 01/reset，无kernel/EFI/ADT/Data；未接publisher或打包启动。历史Android initrd非512对齐，不能冒充临时候选实际FAT范围。
OS/SystemOS只读根卷与Data分开；NativeUfs含SM8550参数且当前禁用，根卷PMGR依赖/GPT/UUID/Data仍未落实；未生成大系统卷或写userdata。
见[系统预研](operations/2026-10-23-system-kernel-userland-roadmap.md)、[平台链接与FAT](operations/2026-10-23-discovery-volume-platform-link.md)。

51MiB DXE heap、已批准512MiB owned、board example与所有verified不变。
R-002跨Bootloader持久日志失败边界保持，不换地址/扩区/借DFPS或SMEM；UART接点与TWRP未验证。NT36523未实测。
EnumaScreen文本后端仅host/AArch64对象通过，尚无INF/FDF/调用者集成，不在当前镜像中。

两仓源码可写，nuwa及其他参考只读；原始设备数据/视频/镜像仅out。固件e286834已推送，设备实现595d6a6已推送；后续文档提交发布状态以Git/WORKLOG为准。
