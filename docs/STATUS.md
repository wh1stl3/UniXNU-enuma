# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前状态

**按用户要求离线准备，留到晚上集中实测。** 本轮没有设备查询、启动、推送或自动设备任务。最近实机证据仍是12:11:03人工恢复后Android完成1/root/槽_a/BL解锁/原boot与vendor_boot摘要正常；不是当前连接证明。首测233a9d8未自动返回的历史失败保留。

## 本轮完成

已备齐同一82ce8a5源的三镜像：早期加载前2秒、完整SimpleFb GUID调用前2秒和7秒。计划执行早期对照→目标2/7/2，末次复用同一2秒镜像。新早期/7秒实际AArch64构建、官方core patch还原、30原厂PE/DEPEX、FD/192字节BootShim/v3通过；三份源输入、诊断宏、FD/raw/镜像摘要交叉检查通过。全部只在out归档，未实测。

新增离线检查器和config/evening-probes.json，无USB调用。完整步骤/摘要/停点见[晚间计划](operations/2026-10-23-evening-validation-plan.md)、[候选报告](../reports/enuma-evening-probe-bundle.json)。正常分派完成兜底只在Dispatcher返回后固定7秒复位，不是看门狗；目标7秒与兜底7秒单次不可区分。

已用固定NativePrelink解析器复核保存的macOS通用内核：普通ARM64、可执行段内入口、4K TCR及历史产物摘要一致，六种篡改被拒绝。该bootstrap全部设备功能关闭，缺所查平台/CPU/pthread状态符号，不能作为enuma启动候选。当前还缺板级归档构建声明/opt-in、donor预链接和完整ADT工具；不仅是等待GOP。见[内核审计](../reports/enuma-kernel-baseline-audit.json)。没有预链接、选择物理地址或新建板级内核。

## 保持的实现与边界

固件82ce8a5/50源锁不变：完整GUID-only/实际句柄/detail/status守卫，SimpleFb配置重试和描述符范围修复，metadata Blt禁止绘制，Probe早退。上一轮真实Mu配置前缀/完整SimpleFb/BootVideo联测及AArch64通过；不证明实际scanout或首次黑屏根因。默认原生33、无UFS32和独立SimpleFb30模式保持；本轮不改固件源码。

51MiB DXE Heap、512MiB owned、内存/example/verified不变；无扩堆证据。R-002跨Bootloader不保留，持久日志路线仍停，不换地址/扩大/借DFPS或SMEM。TWRP/UART未验证。build与workspace qualification须串行。

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块。尚未验证SimpleFb入口/返回、GOP可见、实际scanout六项、实时UEFI map/窗口/EBS、BDS、XNU或NT36523。

## 晚上下一步

重新核对设备身份/备份/原摘要和按键恢复条件后，按上述四次顺序逐次执行并核验Android/root/分区摘要。任何一次无返回即停追加、先恢复。目标门命中只支持PE调用前，不能当主体/协议/内核成功；通过后再准备返回与GOP字段观测。没有新的内存/verified/破坏性操作审批项。

设备上一里程碑6b8545b、固件82ce8a5已推送；本轮设备发布见Git/WORKLOG。参考仓只读，镜像不入Git。
