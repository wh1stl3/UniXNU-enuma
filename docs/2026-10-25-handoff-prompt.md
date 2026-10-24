# enuma交接提示词：完整链优先（D-170）

目标是enuma/SM8250运行iPadOS17.7.11/21H461。用户最新澄清：希望一笔尽量完整启动到iPadOS，分析实际启动报错，每轮修复一批，减少孤立早停。先读AGENTS、STATUS、DECISIONS D-169/D-170与docs/operations/2026-10-25-full-boot-mainline.md。

本轮已实际生成54,231,040字节实验系统预链接（29个Apple组件、原始可执行字节不变、ARM64/4K复查），但完整ADT/FAT/initrd运输/root/Data/错误输出尚未闭合；它不是可直接boot镜像。prepare_system_prelink.py复用固定发出器，不要再重复已有平台内核CI或另写FAT builder。

优先评估同SM8250、同donor的reAAAq/UniXNU-umi 3eb7257，测试firmware 48bc412；文件hash与许可在config/system-reuse-sources.lock.json。实际有ADT/RAM载荷/PMGR/UFS/CPU显示实现，维护者报告Hello；默认board不是Hello配方。它使用旧7b52框架，本仓5fdb模块接口不同，且需要本地ABI/seed/固件输入记录；不得直接执行会改参考树的builder。先迁移完整ADT与v3载荷/报错通道，核对PMGR/UFS接口。不要复制其DRAM、owned窗口、GPT、显示几何、触控和私有Recovery保留区。

B/detail13镜像bf6e014d…a03b2e3已离线资格，保留备用、未实测；A仅前轮一笔返回Android，R-016已消耗，禁止重试。R-015 stub不执行，旧像素批准不复活。完整链启动优先不意味着忽略日志/恢复、内存/verified/破坏性分区门禁。

当前firmware仍aa9ec66，UniXNU仍5fdbd5d；所有原始二进制/源克隆/图像在out/，nuwa和PortingiOS参考只读。没有本轮新设备动作或硬停。详见当前状态及机器证据，不把历史观察升级为实时状态或系统成功。
