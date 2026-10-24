# 交接：D-170，完整启动链优先，B保留备用

用户已澄清期望：“一次性做到iPadOS 然后分析启动的报错 每次启动解决一些”。今后优先准备完整链输入，让每笔尽量推进到实际失败点并修复一批；不再把连续单点早停作为默认主线。必要定位探针仍可保留，日志/恢复及内存/verified/分区边界不变。

## 本轮真实进展

- B/detail13已离线构建、归档和Core调用顺序审计，未上机，降为备用。镜像bf6e014dbda4fc64ea00762034b5107ffd617e5ae24752b708c143bfca03b2e3；A/B源pin与配置除point15→13外一致，32个OEM PE/DEPEX不变。72个PE中70个完全相同，PcdDxe仅8字节PDB GUID差异，运行代码差异仅Core。四项破坏输入负例拒绝通过。
- 已用固定上游发出器实际生成系统预链接实验文件：54231040字节，SHA256 be83a7ec0c11132c13b9581d8784a1775584bb97ff5c66484bcbb2e7bef0879e；29个原始Apple组件，原始可执行字节保持不变，输出ARM64/4KiB/入口/平台导出复查通过。不是完整可boot镜像，不声明runtime/loadable或指令数据流资格。
- 已固定同SM8250、同donor的UniXNU-umi 3eb7257及其测试firmware 48bc412，核到真实ADT/RAM载荷/PMGR/UFS/CPU显示源码。维护者报告Hello；本仓尚未复现。其框架7b52与本仓5fdb不同，私有ABI/seed记录不在公共仓，不能直接运行builder或搬参数。

## 当前主线与真实缺口

先迁移/适配umi的完整ADT组织和RAM载荷边界机制，复用上游FAT builder，闭合本机boot v3实际initrd/FDT与SFS发现及错误输出；同时核对其PMGR/UFS接口，为原生root和后续用户态准备。我们的board仍example=true，仅512MiB入口预算；只有硬件ADT片段，缺完整ADT/FAT系统包、真实载荷运输、root/Data/UUID及可用错误通道。不能拿空ramdisk诊断镜像当iPadOS试启动。

专项：[完整链路线与复用清单](operations/2026-10-25-full-boot-mainline.md)；[B备用](operations/2026-10-25-display-boundary-B-backup.md)。机器证据enuma-system-prelink.json、enuma-system-prelink-format.json、enuma-system-roadmap-audit.json、enuma-umi-system-reuse.json、enuma-display-boundary-B-code.json；原始产物仅out/，参考源码固定在system-reuse-sources.lock.json。

## 实机与授权

本轮没有新增设备动作。前轮A/detail15于02:11启动，16.187秒观察ADB、31.312秒结束Android/root/摘要检查，独立A槽/解锁/备份核验通过；该状态是当时记录，未刷新为当前实时事实。R-016 consumed，不重复A、不从中自动扩张B。A支持但不唯一证明入口前门命中，不证明DisplayDxe/GOP/XNU或iPadOS运行。

没有修改board内存数值、物理地址、verified或分区；实验prelink的虚拟slide由输入重叠检查导出，不是新物理内存配置。umi的12GiB/0x130000000窗口、GPT、1080x2340显示和FTS触控不可继承；R-002失败跨复位日志限制和R-015暂停保持。

当前工具/证据/新方向文档正在提交推送；最新既有提交ada2f3b包含A实测记录。没有新硬停、人工按键待办或新的破坏性操作审批请求。目标iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB维持。

接手先读AGENTS、STATUS、D-169/D-170和完整链专项。不要回到默认A/B逐笔早停；B只在完整链缺少可定位错误时作为备用，不能跳过完整输入建设。
