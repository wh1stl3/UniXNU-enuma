# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相；历史见WORKLOG。

## 当前状态

**只读GOP查询变体首笔未自动返回，已硬停追加候选；人工恢复Android后核验通过。**
2026-10-23 19:45:38临时fastboot boot被接受，75秒内未检出ADB/fastboot。
用户反馈恢复Android，主机于2026-10-23 19:48:15确认enuma、启动完成、root、解锁、原槽及原boot/vendor_boot摘要。
本轮仅一笔实机启动，无flash/erase/改槽；互补候选已构建但未启动。不能称GOP审计通过或失败，更不能称菜单/XNU通过。

见[本轮审计与硬停](operations/2026-10-23-readonly-gop-query.md)、[结构报告](../reports/enuma-gop-query-device.json)。
相机抽查20/40/80秒为黑屏，无可读UEFI文字；原录像仅out，不能由抽查排除所有瞬时输出。
依用户新偏好，尚无渲染/屏幕日志的探针不持续录像，采用必要截图及主机日志；需要判读画面或恢复动作时再录像。
电源键在画面右上角，可用明确可见动作作证，遮挡/窗口外不能推断；已有证据不重复问按键。

## 已完成与限制

- 固件250849f固定提交，53项输入锁；新增默认关闭的GOP只读审计。复用SimpleFb实际提供者，安装后枚举唯一句柄、HandleProtocol匹配实例、校验Mode/跨度及QueryMode字段一致性，释放临时分配。禁Blt/SetMode/物理帧缓冲访问，Probe早退保持。
- 查询选择器1/2在通过/错误时复用两秒门，Core状态门禁用以免误判，未命中走原七秒正常Dispatcher完成兜底。安装后不返回新错误，避免驱动卸载造成悬空协议函数。同步兜底不能恢复卡死，本次已实际未返回。
- 36组真实Mu头元数据/参数ASan/UBSan、AArch64对象、六组实际补丁谓词、六组CLI拒绝及155组入口/桥接/Core门回归通过。两份候选实际AArch64全链接、core还原、30OEM/FD/192B BootShim/v3打包通过，源输入一致；workspace串行通过。这些不是硬件执行证明。
- 首次019191f构建在INF解析error4000失败，未实测；250849f改为普通库依赖后重建通过。失败证据保留。
- 上一轮82ce8a5的17/16/17三笔时序支持最终StartImage非错误，用户确认无按键。更早point20/21也有互补时序支持；不能转移到新250849f变体。旧233a9d8人工恢复失败历史仍保留。

## 下一步

先离线拆分新增依赖/构造器、审计调用前可达性、枚举/HandleProtocol/QueryMode/FreePool与复位路径。
自动返回失败尚未定位，不再直接重试完整查询或已生成的互补镜像。优先把复位判断留在已验证的Core路径、减少提供者新增依赖，再评估最小单阶段候选；不是先放开绘制。
新的实机试验须重新满足当时身份/备份/可控返回条件；无返回继续停追加并恢复。GOP数值快照、真实scanout/像素所有权、BDS及菜单仍缺。

## 系统与内核现状

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d。
macOS CI39927966148/head250cdf9已真实链接crypto plain/namespace、pthread、ArmDTPlatform、ArmCpu服务与源内核；21417672B内核SHAb940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d，本地NativePrelink解析通过。仅源平台链接，未预链接donor或启动，正式board归档/opt-in/ADT接回仍待做。

64MiB配置专用FAT已生成并双份一致，仅ENUMA FAT DISCOVERY 01/reset，无kernel/EFI/ADT/Data；未接publisher或打包启动。历史Android initrd非512对齐，不能冒充临时候选实际FAT范围。
OS/SystemOS只读根卷与Data分开；NativeUfs含SM8550参数且当前禁用，根卷PMGR依赖/GPT/UUID/Data仍未落实；未生成大系统卷或写userdata。
见[系统预研](operations/2026-10-23-system-kernel-userland-roadmap.md)、[平台链接与FAT](operations/2026-10-23-discovery-volume-platform-link.md)。

51MiB DXE heap、已批准512MiB owned、board example与所有verified不变。
R-002跨Bootloader持久日志失败边界保持，不换地址/扩区/借DFPS或SMEM；UART接点与TWRP未验证。NT36523未实测。
EnumaScreen文本后端仅host/AArch64对象通过，尚无INF/FDF/调用者集成，不在当前镜像中。

两仓源码可写，nuwa及其他参考只读；原始设备数据/视频/镜像仅out。固件250849f已推送，设备本轮提交发布状态以Git/WORKLOG为准。
