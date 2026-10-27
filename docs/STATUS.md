# 当前：离线推进内核、根卷与用户态组件；OEM部署继续等待

2026-10-27。按用户最新要求，在无实机情况下继续开发后续内核启动、用户态与iPadOS桌面链路，参考固定umi/sheng/fajita源码。仅独立worktrees/enuma-oem-display可写；原共享主线和firmware不改，不上机、不推送，R027冻结。

## 本轮实际产物

- 新实验性内核：out/kernel-userland-20261027-1/prelink1/userland-components.experimental.macho，54259712字节，SHA256 e879b2f03f995107ad5b10ea21f48430894cbbf31ead1b62143256e07a7f9e59。真实NativePrelink输出，新增图形/HID roots，30个可执行原始组件；普通ARM64/4KiB/入口检查通过。
- 新96MiB FAT：out/kernel-userland-20261027-1/payload2/payload/payload.img，SHA256 31a7defb9dbc63305b222fbfa236b7350f03e09fc4b0cefb1ca423e1d384fbb8。原有payload builder/完整ADT/原始trust bundle，真实FAT回读一致；未包含Data/root卷。
- 新根卷组件文件：out/kernel-userland-20261027-1/root1/root-components.img，9382658048字节，SHA256 fd43ee7035ce185ce4215ac93fdc006fd784a54b3b7442e21457c226cbe03093。固定UDIF/LZFSE展开OS/SystemOS，输入pin、展开摘要、文件回读均通过；生产RootLayout接受实际manifest。测试GPT是上游宿主夹具，不是本机容量证明。

这些是离线输入，不是已资格上机的完整系统。没有XNU/launchd/backboardd/SpringBoard实机结果，没有声称进入桌面或图形加速可用。

## 新代码与验证

EnumaUfsSmmu组件移植umi双stream接管思路，加入显式stream/已分配DMA范围、完整路由表重查、写入拒绝/读回失败、单次消费与失败不放行DMA；重复拒绝也清除放行标志。EnumaUfsRead提供实际容量解析和受窗口/缓冲约束的READ(10)，无磁盘写接口。这两个模块尚未接IOKit、真实MMIO或XNU归档，调用方仍须实现队列停止和排他。

最终storage3：ASan/UBSan逐点覆盖22次计划读、51次应用读、7次写拒绝等失败路径；两个AArch64对象及固定上游RootLayout/RootPublication/RootWindowRead测试通过，含2048项manifest变异。storage1失败保留；storage2修复Linux测试字面量类型；storage3额外覆盖重复拒绝清DMA标志。上游源码未修改。

## 来源差异与下一步

umi同SM8250，维护者报告Hello/Setup Assistant，不是完成主屏。enuma历史FDT没有UFS iommus属性，0xe0/0x4e0仅是umi测试夹具，尚未作为enuma默认值；不借用其容量或4.75GiB窗口。sheng用于服务依赖参考，不移植SM8550硬件参数；fajita仅报告内核挂根等待，用于Linux镜像/验证方法参考。正式框架pin保持5fdbd5d，另固定16e592a的UDIF读工具，不整体升级底座。

继续方向：实际stream归属/IOKit UFS适配、同donor PMGR ABI与服务、根卷策略及UUID、匹配版本的可丢弃APFS Data seed、framebuffer/IOSurface和NT36523 HID，随后分别验收launchd、backboardd、SpringBoard。现有公开umi配方仍要求本地ABI/seed输入，不能用空服务或跳过Setup配置冒充用户态完成。内存和verified规则不变。

## 保留的设备候选

OEM qualification-3/image.img仍为17d0169e6bd1447b358d1e91c6af9a8bf6ed368c6c44fea591fa73b970b82f08，用户“现在不方便，保留候选等待”，未boot、未消费单次ledger。本轮无设备查询或写入；最后设备只读状态仍是此前12:15/12:16的Android完成/A槽/root/备份一致，不是当前在线断言。部署须用户恢复现场准备后即时核验，不把本次离线开发当作恢复上机授权。

详见[内核及用户态离线记录](operations/2026-10-27-kernel-userland-offline.md)和[OEM部署边界](operations/2026-10-27-oem-runtime-deployment.md)。所有大文件仅本地out，代码和脱敏记录仅本地提交。

后续执行规则：用户指定以UniXNU官网为开发指南，见[官网开发指南](operations/official-development-guide.md)及AGENTS开头。按官方流程核对版本/依赖/分层验收；当前离线、冻结、不推送边界保持。

2026-10-27规则补充：官网具体方法已由AGENTS绑定，见[执行规则](operations/official-adaptation-rules.md)。本轮仅文档，硬件与构建进度不变。
