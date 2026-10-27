# 主线离线续进：最小日志回读与 SimpleFb 观测停点

2026-10-23（Asia/Shanghai）。用户要求沿主线和强停规则继续，并新增持久规则：难题应评估同SoC设备的UniXNU/UEFI仓库作为候选方案来源。该规则已写入项目AGENTS.md，固件仓遵循设备仓规则；不是声称已设置应用全局记忆。

本轮继续可独立完成的离线工作。前一轮明确“暂不操作实机”仍保持，因此未调用ADB/fastboot、推送或加载模块。未修改board/bringup-plan/固件源码/源锁/内存字段/验证标记；未生成新的boot或UEFI镜像。

## 日志主线已完成

沿用R-002和原实际内核头/原厂KO来源，执行既有build_log_reader.py --read-marker，首次完成16字节只读模式的实际AArch64 KO构建。不是空实现；它复用实际内核PageReserved/pfn_to_page、__va和printk，不包含物理写入、可变地址参数或强制加载代码。

- 输出仅在out/log-readback/module-marker/，KO 4088字节，SHA256 6644cf40bd4ee85ce6ec8a0a57eeef08aa0a6a2e79b61b75e1230f6b469bd6f2。
- vermagic=4.19.157-perf-gf8cf95f4dc15 SMP preempt mod_unload modversions aarch64，实际头编译struct module为832字节，与已有两份原厂模块一致。
- 所需CRC均来自原厂__versions：module_layout=0xaad0c453、printk=0x7c32d0f0、memstart_addr=0x9688de8b。默认无物理访问ABI探针保持独立；正常运行时加载仍必须由内核判断，禁止force-load。
- 反汇编静态核对：检查8页标志后才进入16次单字节读取；该init函数中看到的store为本地栈拷贝，cleanup为ret。仅针对这个对象的人工静态结论，不是内核加载/内存所有权/存活证明。
- 新增tests/log_reader_guard.c包含实际diagnostics/enuma_log_reader.c，仅mock内核API；分别模拟8个未保留位置，检查拒绝发生在__va/printk前；全保留时源是精确16字节ASan分配，校验输出一致和源不变。scripts/check_log_reader_guard.py在WSL以ASan/UBSan执行通过。
- 这套mock不模拟真实页表、FDT、缓存、__va可访问性或Linux ABI，不替代实机门禁。报告明确hardware_loaded=false、physical_memory_accessed=false。已有45项Python回归通过，与新C检查分开计数。

公开报告为reports/enuma-log-reader-marker-build.json和enuma-log-reader-host.json；KO、头文件及反汇编原件不提交。尚未实现标记writer、跨复位读取链或实际SEC/DXE日志，更没有写入/读取目标物理区。

复现（只构建/主机检查，不触发设备动作）：

```text
wsl -d Ubuntu-22.04 -- /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/build_log_reader.py --read-marker
wsl -d Ubuntu-22.04 -- /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_log_reader_guard.py
python -B -m unittest discover -s tests
```

## SimpleFb参数来源继续核对

仍参考已锁定alioth/elish的实现与差异，具体见2026-10-23-simplefb-gop-offline-audit.md。这次增加scripts/audit_saved_scanout.py，以保存输入复算缺口，**预期返回2**表示不满足启用写屏条件，不是程序崩溃或新的地址授权。

新发现与来源边界：

- 旧Android dmesg的两份保存样本各有`cont_splash enabled in 1 of 1 display(s)`。这支持当次原厂Android存在连续开机画面交接；未报告base/stride/格式，不能外推自制UEFI入口持续扫描或EBS后保持。
- 保存FDT没有simple-framebuffer节点，Android模式与OEM区域仍是已知来源，无法补全入口几何。
- 初次collection.json的framebuffer记录为空且exit1，但当前framebuffer.stdout被后来仅打印FILE标签的采样替换。工具保留原记录，注明不匹配、不继承旧exit code；不能拿标签本身当fb0参数。drm-state仍为空且与原记录匹配。
- 旧panel XML的InterfaceColorFormat/DSIColorFormat属于面板/接口设置，不转换成已验证的内存像素布局。不能用alioth的32位或elish的同起始地址填补这些缺口。

当前缺六项：入口scanout base、stride bytes、像素格式、线性非压缩布局、有效像素跨度、自制UEFI期间scanout存活。报告为reports/enuma-scanout-evidence-gap.json，simplefb_write_eligible=false。没有构建SimpleFb变体或新增固定几何配置；不提前放宽FD审计。

## 当前停点与恢复工作后的最小方案

这里是**暂不操作实机这一用户约束下的实测依赖停点**，不是新内存审查项或自动批准失败。没有新硬停地址提案、没有待按键事项。后续必须先恢复设备工作的授权范围，才做以下动作；本轮不执行：

1. 日志链优先：重新核对enuma身份、root、当前内核、备份/原分区摘要和活动FDT的唯一保留tuple及8页flags；旧R-002报告不能代替当前状态。若普通重启失去保留，用已经审计的临时保留镜像及既有身份/恢复流程重新建立，不绕过门禁。
2. 先正常加载/卸载无物理访问ABI探针，采集内核真实错误与返回；失败即按R-002停，不强载。随后才能在相同保护条件下讨论marker reader加载。PageReserved只是必要条件，FDT所有权/地址可访问性仍需主机门禁。
3. 在writer实现前审查最小标记/复位/回读链，不能经过未保留的Linux启动。仅在批准的32KiB范围内设计writer，reader只读16字节。若Bootloader清空候选、ABI或临时契约不满足，按R-002停，列方案，不换地址/扩大/刷分区。
4. SimpleFb观测先只读：在当前ROM支持的DRM状态/调试节点里取得有效scanout字段，或从可信Bootloader handoff/有界早期日志取得入口事实；Android状态仍须和实际ABL/UEFI入口区分。没有字段时记录缺口，不挂载未知接口、不猜MDP寄存器、不通过试写扫描地址。
5. 有真实几何后才接入Mu核心最小保护patch、精确30-OEM诊断模式及对应严格FD审计；默认33/既有32模式不改。另按G0–G6验证GOP注册、可见图案、DarwinBoot接受、恢复。需要修改board/bringup-plan内存地址/大小或verified=true时列出具体审查项再停。

同SoC参考仓可为步骤2–5提供实现及依赖线索；每次固定提交，区分协议/库复用与板级参数移植，记录适用性和否决理由。没有将别机成功当enuma已成功。
