# 当前状态：D-172，boot v3运输已实现并离线资格，13项同次报告

用户要求推进boot v3 payload运输，并补充“尽量一次验证多个验证点”。本轮新增可选只读RAM BlockIO、同次13项报告，完成完整UEFI构建、实际FD/PE资格和包含真实96MiB FAT的boot v3打包。没有实机动作，不宣称运行时运输或SFS通过。

## 已交付

firmware固定698b7c17dbbd80993070a45e2aa5ae15d330b63b并已推送。实际FD SHA256 5a031cd8b39c84a23a3ffd847400adbe5c85944f5fde59e307f7c4c9c1e13f68；新镜像out/full-boot/transport/enuma-system-transport-v3.img，103817216字节，SHA256 194fa0f2bf51236ba7d1ed2f741ea1597104c8278197a0485b039b8e100f8b9e。资格归档out/full-boot/transport/qualified-698b7c1，含实际PE/map/编译命令、FD/raw/image和清单，拒绝覆盖。

复用固定umi的真实只读BlockIO/FDT模式，使用enuma已有Kernel映射/保留区，不新增物理映射；源锁保留版权/许可。运行时必须检查x0 HOB、FDT完整范围、initrd精确长度与不重叠、vendor前缀、BPB和完整FAT CRC，再发布只读块设备。CRC是传输损坏检查，不是认证。

本机实际ABL PE指令已核：v3先复制vendor、按原始size推进目的地址，再复制generic，没有页补齐。源/字节/负例证据enuma-abl-v3-concat.json；实际临时入口FDT仍未观察，不能省略运行时检查。vendor前缀长度由锁定备份生成而非手填猜值，FAT起点非sector对齐由byte CopyMem处理。

同一候选记录MAP/FDT/INITRD/PREFIX/BPB/FAT CRC/BLOCKIO/CONNECT/SFS/KERNEL/ADT/TRUST/CONFIG共13项。前置失败停止依赖读取，未执行保留NOT_READY；SFS/文件在BDS检查，payload模式移除旧60秒暂停。实际编译宏、PE数组、write-protected返回机器码及FD内字节均核对；ASan/UBSan首尾非对齐读取、越界/溢出/重叠/错误介质/损坏/写保护检查通过。32个保留OEM PE/DEPEX未变，仅省略UFSDxe。AOSP打包/解包回读真实ramdisk一致。

## 当前缺口和下一步

13项报告只在同次Boot Services生命周期内，Print/DiagDraw的enuma可见文本尚未实证，完整UEFI→XNU错误通道仍缺。下一步优先闭合可观察/可恢复条件，再用同一候选一笔读取多个结果；本轮未安排新boot。不要把构建成功、报告协议存在或时序当作每项实机成功。

D-171的完整结构ADT/96MiB FAT保持，D-170实验prelink保持runtime/loadable限制；root UUID、平台种子、PMGR/UFS/root/Data仍缺，没有进入XNU/Hello/桌面。运输候选不是完整可运行iPadOS镜像。

专项operations/2026-10-25-boot-v3-payload-transport.md，机器报告enuma-ram-payload-host/contract/qualification、enuma-abl-v3-concat、enuma-firmware-build、enuma-fd-audit与源迁移报告。UniXNU仍5fdbd5d。firmware/子模块为权威；standalone D:/Code/uefi-enuma旧检出和原有Mu脏状态未动，不要混用。

## 实机与边界

本轮无设备动作、新硬停或人工待办；设备实时状态未知。最后实机是02:11 A/detail15的Android/root/A槽/解锁/分区摘要恢复核验，当时通过，不升级为当前状态。R-016 consumed，不重试A；B离线备用、R-015暂停、R-002失败跨复位日志不复活。可恢复临时启动及实机前文档/身份/备份/观察门禁保持。

board仍example=true，未修改board/bringup-plan内存字段，R-001入口请求仍512MiB；未新增verified、像素或分区操作。固件01ffaec/336760b/698b7c1记录实现、换行和补丁上下文修复；设备仓上轮adfb63f已推送，本轮发布以同轮Git记录和远端核验为准。
