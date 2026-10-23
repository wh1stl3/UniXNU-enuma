# STATUS

更新：2026-10-23 21:12后（Asia/Shanghai）。当前唯一真相；历史见WORKLOG。

## 当前状态

**新GOP拆分step0/step1均临时启动后自行回Android，用户确认两次全程未按键；恢复核验通过。本轮止于step1，尚未进入XNU。**

用户本轮明确撤销暂时离线限制，授权重新核验后先step0、受控返回后step1，并确认可在场恢复。step0于21:10:18启动，ADB16.906秒、完成与摘要核验30.438秒；step1于21:11:37启动，ADB15.844秒、完成与摘要核验30.547秒。两次root/原boot_a与vendor_boot_a摘要通过，启动前唯一enuma/解锁/原槽/备份和fastboot身份均通过，最后再次核对身份/完成/槽/解锁。

短时序与无按键恢复支持新Core返回路径及step1枚举/释放整体返回；没有同版本延时对照或数值EFI日志，不能唯一确认目标门命中或每项校验成功。旧250849f的75秒超时及人工恢复事实保留，根因未确定；旧完整查询/互补镜像不重试。

证据：[本轮实测](operations/2026-10-23-gop-split-device.md)、[脱敏报告](../reports/enuma-gop-split-device.json)。无数值GOP快照、真实scanout、像素/菜单或XNU通过证据。

## 已有实现与验证

固件e286834/54输入锁，core-warning-v2，将非错误warning1/5从SimpleFb传回既有Core门；提供者无新增本地Timer/Reset依赖，七秒正常完成兜底仍同步，不能救卡死。五层累计为安装后控制、枚举/释放、HandleProtocol、Mode、QueryMode。保持禁绘制/Probe早退。

既有137阶段/参数、30实际标记、6Mu传输、7CLI、177Core检查及四份AArch64对象通过。本轮只重跑bundle审计，不重跑或冒充新构建：step0/1源锁、FD、BootShim/v3嵌入FD和摘要全部通过。step2/3/4尚未单独全链接打包/实测。

## 下一步与约束

本次授权两笔完成，不自动追加step2。下一步离线准备step2完整链接/打包/审计；需要强化门命中结论时先做同版本延时对照或同step selector2，不用旧候选。继续实机前重新核对现场与恢复条件，任何无返回停追加并恢复。

无绘制不持续录像，本次前后截图配合主机日志和用户无按键确认；当前无人工待办。未flash/erase/改槽，未改内存/example/verified。UART接点与TWRP未验证。

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
