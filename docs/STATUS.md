# 当前停点：失败对照已人工恢复，继续离线隔离与新软件

2026-10-23，Asia/Shanghai。838b38f的linear-control step3在23:16:54临时启动后75秒未返回，已当轮停止追加启动并落实全部交接文档。用户随后确认回Android，主机于2026-10-23 23:20:44核验enuma/boot_completed/root/原槽/解锁/原分区摘要全部通过。当前设备已恢复Android，不再等待人工按键。

失败候选SHA a8061b8510935bbe8991ec0d8723a1bcc3b1a9460422ecc9ac30ffe13813016a，不能原样重试；step10镜像已完成离线构建/审计但没有实测，不得绕过对照停点启动它。R-004映射不变，未发生像素/寄存器写入或分区操作。

离线进度：与17aa47a成功对照解包比较，DxeCore/OEM叶载荷一致，SimpleFb和Pcd差异仅RSDS调试标识八字节；SEC存在编译时间字符串及引用布局变化，压缩级联改变整包。故障PC/根因未知，不声称新增格式代码导致失败，亦不声称SEC布局就是根因。64主机用例/对象和两份838b38f完整构建/bundle四负例/workspace均通过，证明离线构建而非实机通过。

接下来按用户要求持续离线：稳定SEC编译时间造成的构建布局变化，重放相同输入检查产物一致性，再准备新的安装后返回基线（step0）而非重复失败step3。该软件尚在准备，不声称修复或新镜像通过。新的设备动作仍须身份/备份/恢复和故障隔离门禁，超时停追加并优先恢复，真实硬停当轮写交接。

源码与发布：固件838b38f已推送，设备源锁/gitlink在工作树与之匹配；设备已推送最新文档3161bf4，本组实现/恢复记录待本次提交发布。参考仓只读，内存/verified/分区边界不变。无待批准项、无按键待办。证据reports/enuma-linear-control-timeout.json、enuma-linear-control-offline-diff.json、operations/2026-10-23-linear-control-timeout.md；恢复录像out/camera-capture/20261023T231903，601帧完整解码。

## 系统与内核现状

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d。
macOS CI39927966148/head250cdf9已真实链接crypto plain/namespace、pthread、ArmDTPlatform、ArmCpu服务与源内核；21417672B内核SHAb940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d，本地NativePrelink解析通过。仅源平台链接，未预链接donor或启动，正式board归档/opt-in/ADT接回仍待做。

64MiB配置专用FAT已生成并双份一致，仅ENUMA FAT DISCOVERY 01/reset，无kernel/EFI/ADT/Data；未接publisher或打包启动。历史Android initrd非512对齐，不能冒充临时候选实际FAT范围。
OS/SystemOS只读根卷与Data分开；NativeUfs含SM8550参数且当前禁用，根卷PMGR依赖/GPT/UUID/Data仍未落实；未生成大系统卷或写userdata。
见[系统预研](operations/2026-10-23-system-kernel-userland-roadmap.md)、[平台链接与FAT](operations/2026-10-23-discovery-volume-platform-link.md)。

51MiB DXE heap、已批准512MiB owned、board example与所有verified不变。
R-002跨Bootloader持久日志失败边界保持，不换地址/扩区/借DFPS或SMEM；UART接点与TWRP未验证。NT36523未实测。
EnumaScreen文本后端仅host/AArch64对象通过，尚无INF/FDF/调用者集成，不在当前镜像中。

本轮新增donor离线审计：46,415,872字节普通ARM64 Mach-O，摘要与固定同donor pin一致，237模块及三组闭包/绑定计划通过；仅比较参考slide，未采用为板级配置、未emit预链接镜像。scripts/audit_enuma_donor.py可重放；完整ADT/载荷/内存/EBS/入口仍待闭合。
