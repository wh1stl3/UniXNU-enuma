# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前状态

**已生成FAT配置发现测试卷，并接入待运行的源内核平台链接CI；实机主线仍为屏幕诊断，镜像实测留到晚上。** 本轮没有设备查询/启动/写入。最近15:18 UART只读核对为enuma/root/Android完成1/槽_a；原boot/vendor_boot摘要核验仍为12:11恢复记录，不是本轮重查。首测233a9d8未自动返回的历史失败保留。

## 当前路线与已完成工作

新增64MiB配置专用FAT32（唯一标签/仅reset，无kernel/EFI），官方write_volume加经过FAT双表校验的空闲簇清理后，两次产物逐字节一致、mdir与mcopy回读通过；未打包boot或接入固件publisher，菜单倒计时不是复位保障。新增固定sheng通用builder配方与macOS platform模式，顺序构建真实crypto/pthread/ArmDTPlatform/ArmCpu归档后按既有defconfig链接，尚待实际CI结果。53项Python和六份配方检查通过。见[本轮实现](operations/2026-10-23-discovery-volume-platform-link.md)。

新增[系统卷/内核/用户态路线](operations/2026-10-23-system-kernel-userland-roadmap.md)及离线审计器，12份固定源码逐字节Git blob比对通过。区分FAT载荷、OS/SystemOS只读窗口和Data；确认本机载荷发现尚未闭合、缺GPT/UUID/完整ADT/prelink，NativeUfs含SM8550参数且当前禁用，原生root载荷检查要求尚未接入的PMGR契约。固定userdata dry-run不做展开后容量比较，不能当容量通过。优先复用通用工具/布局/校验算法，同SM8250固件只作依赖参考，不复制外板参数。未下载大DMG/构建系统卷/写分区，未触发新内存或破坏性操作审批；详见[审计报告](../reports/enuma-system-roadmap-audit.json)。

新增独立EnumaScreen受控GOP Blt后端，复用锁定DarwinBoot字模，可显示阶段、完整64位EFI状态、GOP字段与内存摘要快照。每行一次Blt、显式写门禁、caller持有有界scratch、模式/错误锁存及重入拒绝；不解引用物理帧缓冲。真实Mu头的host ASan/UBSan与AArch64 COFF编译通过，合成预览已检查。**尚未集成固件、未完成全链接、未上屏**；对象有memset依赖，需接入时验证。今晚三候选和82ce8a5源锁不变，bundle复查通过。见[后端与接入条件](operations/2026-10-23-bounded-screen-renderer.md)。

UART已取得软件线索：命令行请求ttyMSM0/115200n8、serial0=988000、GPIO117/118；但console节点disabled、无活动ttyMSM控制台，绑定998000是另一设备。实物测试点/TX-RX/电平与外部采集、UEFI输出均未验证，现有USB/ADB不是UART传输。因此按用户选择走屏幕诊断，先建立真实GOP/几何再受控显示阶段/错误码，不撤metadata绘制守卫。见[只读核对与路线](operations/2026-10-23-uart-or-screen.md)。

已备齐同一82ce8a5源的三镜像：早期加载前2秒、完整SimpleFb GUID调用前2秒和7秒。计划执行早期对照→目标2/7/2，末次复用同一2秒镜像。新早期/7秒实际AArch64构建、官方core patch还原、30原厂PE/DEPEX、FD/192字节BootShim/v3通过；三份源输入、诊断宏、FD/raw/镜像摘要交叉检查通过。全部只在out归档，未实测。

新增离线检查器和config/evening-probes.json，无USB调用。完整步骤/摘要/停点见[晚间计划](operations/2026-10-23-evening-validation-plan.md)、[候选报告](../reports/enuma-evening-probe-bundle.json)。正常分派完成兜底只在Dispatcher返回后固定7秒复位，不是看门狗；目标7秒与兜底7秒单次不可区分。

已用固定NativePrelink解析器复核保存的macOS通用内核：普通ARM64、可执行段内入口、4K TCR及历史产物摘要一致，六种篡改被拒绝。该bootstrap全部设备功能关闭，缺所查平台/CPU/pthread状态符号，不能作为enuma启动候选。当前还缺板级归档构建声明/opt-in、donor预链接和完整ADT工具；不仅是等待GOP。见[内核审计](../reports/enuma-kernel-baseline-audit.json)。没有预链接、选择物理地址或新建板级内核。

## 保持的实现与边界

固件82ce8a5/50源锁不变：完整GUID-only/实际句柄/detail/status守卫，SimpleFb配置重试和描述符范围修复，metadata Blt禁止绘制，Probe早退。上一轮真实Mu配置前缀/完整SimpleFb/BootVideo联测及AArch64通过；不证明实际scanout或首次黑屏根因。默认原生33、无UFS32和独立SimpleFb30模式保持；本轮不改固件源码。

51MiB DXE Heap、512MiB owned、内存/example/verified不变；无扩堆证据。R-002跨Bootloader不保留，持久日志路线仍停，不换地址/扩大/借DFPS或SMEM。TWRP/UART未验证。build与workspace qualification须串行。

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块。尚未验证SimpleFb入口/返回、GOP可见、实际scanout六项、实时UEFI map/窗口/EBS、BDS、XNU或NT36523。

## 晚上下一步

重新核对设备身份/备份/原摘要和按键恢复条件后，按上述四次顺序逐次执行并核验Android/root/分区摘要。任何一次无返回即停追加、先恢复。目标门命中只支持PE调用前，不能当主体/协议/内核成功；通过后再准备返回与GOP字段观测。没有新的内存/verified/破坏性操作审批项。

设备上一里程碑9c85a6b、固件82ce8a5已推送；本轮设备发布见Git/WORKLOG。参考仓只读，镜像不入Git。
