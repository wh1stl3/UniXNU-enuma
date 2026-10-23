# 晚间实测准备与内核基线审计

2026-10-23（Asia/Shanghai）。用户要求“继续推进主线 留着晚上一起实测”。本轮只生成、归档与审核镜像、核验保存的内核产物；没有设备查询、推送或启动，也没有创建自动执行设备的任务。

## 三镜像、四次计划尝试

三份都固定uefi-enuma82ce8a5和同一套源输入，包括SimpleFb配置重试/描述符范围修复、Blt禁止像素和Probe早退守卫。共用30个原厂PE/DEPEX，精确缺CPR/Display/UFS。新构建早期2秒与目标7秒，复用已归档同版目标2秒；不混用旧7479da1早期对照。

| 候选 | 镜像SHA256 | FD SHA256 |
| --- | --- | --- |
| early-control-2s | 297110a4b97fb05a146b128050837445d719806e21f2e4ddb0cd63c388601996 | d0901dc384146c98acf034b9cbd0d5840c668ad304d382d24111f334a5bd3c6c |
| simplefb-pre-2s | 6baf95968292746998d260810596d090b42ed28e991d3157866e93330a093bc4 | 75c34141a785d4dc38f1475e6ce1a60b894f30db98c18b58926958c6e2bd203f |
| simplefb-pre-7s | fea7478b6fe5556c26b3ca592a2c434fb0c881f4f15441685c5de19bc4de977b | 15579755a85b09a491ed6fba7291ff687b49e1ce4d0c793a34202ffd4107bae9 |

镜像和完整日志仅在本仓out。命名/顺序在[计划配置](../../config/evening-probes.json)，交叉审计在[检查器](../../scripts/check_evening_probe_bundle.py)及[报告](../../reports/enuma-evening-probe-bundle.json)。检查器核对源锁、构建宏、官方patch还原、归档FD/OEM报告、BootShim、v3布局、raw/镜像摘要，绝不调用USB工具。

顺序：early-control-2s → simplefb-pre-2s → simplefb-pre-7s → simplefb-pre-2s。最后一次必须复用第一次目标2秒的完全相同镜像，不临时重建。每次独立核验返回状态后才判断能否执行下一次，不做盲目连跑。

早期对照为stage12/ordinal1，在首个scheduled DXE驱动加载前复位。目标为stage13/detail20，匹配完整SimpleFb GUID，不依赖未知序号；2/7秒是命中门后的延时，不是保证整次尝试只需2/7秒。正常Dispatcher完成兜底固定7秒，早期对照关闭该兜底。

## 晚上执行条件与停点

开始时重新核对唯一enuma、BL解锁、槽位、Android完成1/root及boot/vendor_boot原摘要、备份/镜像摘要，并确认人员能配合恢复按键。12:11人工恢复只作为历史证据，不代替晚间连接检查。沿既有授权优先临时fastboot boot，不flash/erase/改槽，不试TWRP。

每次保存源/FD/镜像摘要、发送日志、命中/返回的可采信信号、ADB/Android时序和试后root/分区摘要。若任何一次未返回或身份/摘要异常，立刻停止追加候选并沿既有恢复路径处理，需按键时记录人工节点。

目标7秒与正常完成兜底7秒单次不可区分；2/7/2的目标相关时序响应才支持调用前检查点。固定7秒不能声称命中，单次复位不能声称驱动返回/GOP成功。同步兜底不能救更早驱动或分派卡死，也不能排除漏门后意外继续执行。metadata/Probe守卫限制已知绘制路径，不是全固件无帧缓冲写入的证明。本批不以执行SimpleFb主体、出图、EBS或XNU为目标；调用前链路验证后再决定返回/协议层探针。

## XNU基线到底具备什么

保存的macOS bootstrap产物SHA为de5ccd244f0b4fd6c0ebe5f6173aa6f7be993e31aa45db583150cd65c2f4c0fd，来自39790786938。本轮复用固定NativePrelink2b6ffb5的macho/exports/backed_offset解析器，按Git对象核对解析器及构建/配置依赖，而非重新写一套Mach-O解析器。确认普通ARM64 MH_EXECUTE、iOS17.0部署、唯一ARM64线程入口、入口在文件有字节支持的可执行段、两级4K TCR；与历史CI报告一致。ARM64e/错误入口/线程状态/部署/16K TG0/截断六种篡改均拒绝。没有执行内核或生成预链接。

当前enuma_defconfig请求corecrypto14、pthread、ArmDTPlatform、ArmCpu；该bootstrap实际把四项都置0，符号表也未见选定的平台/CPU/pthread状态符号。不能拿它直接启动enuma。它能证明工具链和普通4K内核构建基础，不能证明板级组件或完整链接。

当前真实构建缺口还包括：未声明kernel.archives、未启用归档构建、无kernel.prelink、无payload.adt.tool。固定上游链接脚本需要corecrypto命名空间归档、pthread归档、ArmDTPlatform和ArmCpu归档；路径在[内核报告](../../reports/enuma-kernel-baseline-audit.json)。后续要审查可执行归档配方、编译记录/SDK/接口及donor依赖，再构建板级内核；不复制示例slide、外板地址或用空service补位。

因此到XNU不只剩实机GOP：还须闭合板级归档与donor预链接、完整enuma ADT，之后验证真实UEFI map/512MiB窗口与EBS交接。现有平台支持C核心不等于IOKit服务已注册。本轮不修改board/内存/verified，保留example=true与R-002停止边界。

## 重跑离线检查

在本仓运行Python `-B scripts/audit_enuma_kernel_baseline.py` 与 `-B scripts/check_evening_probe_bundle.py`。前者只读已保存的通用内核；后者只读已归档镜像。缺文件、旧源或摘要不匹配即失败，不会重新生成、下载或启动设备。固件build与check_workspace的qualification会修改同一out上游补丁状态，仍须串行。
