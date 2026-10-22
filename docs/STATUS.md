# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见 WORKLOG。

## 当前工作与边界

**离线主线续进完成：16字节marker只读模块已实际编译并通过实际源码的主机保护检查；SimpleFb保存输入门禁明确缺六项入口scanout证据。保持用户“暂不操作实机”限制，停在需要新实机观测的节点。无ADB/fastboot、模块加载、物理日志读写或新boot/UEFI镜像。**

用户新增的同SoC参考仓评估规则已写入AGENTS.md，作为后续会话可读的项目持久规则。详见 [本轮交接](operations/2026-10-23-log-reader-offline-followup.md)。

- marker KO离线构建4088字节，SHA256 6644cf40bd4ee85ce6ec8a0a57eeef08aa0a6a2e79b61b75e1230f6b469bd6f2；vermagic、832字节结构、3个所需CRC与已有实际头/原厂KO输入匹配。未insmod，不能称运行ABI通过。
- 新C主机检查直接包含实际reader源码，以mock页状态验证8处任一未保留时均在映射前拒绝，全部保留才读精确16字节且源不变；ASan/UBSan通过。45项Python回归通过，不是实机证明。
- audit_saved_scanout.py预期exit2，报告入口base/stride/格式/线性布局/有效像素跨度/自制UEFI存活均未知。旧Android日志cont_splash提示仅支持原厂Android交接，不证明新UEFI几何；未生成SimpleFb候选、未提前放宽FD策略。
- 本轮未改固件仓/gitlink、board/bringup-plan/内存/验证标记或42项源锁。没有新待批项或待按键事项；后续加载/回读须重新核对活动FDT/8页和正常ABI探针，R-002失败即停限制保持。

推荐复用本固件已有Mu SimpleFbDxe/FrameBufferBltLib；先闭合参数，再接最小适配与独立诊断，不能凭同SoC参数盲写。此前审计见 [SimpleFb离线审计](operations/2026-10-23-simplefb-gop-offline-audit.md)。

## SimpleFb 审计结论

- 核对22个源码文件的提交/Git blob/SHA256及保存的本机输入。固件仍 b988fa418de55de2dcaa396d016e30231159d1fe；alioth默认开关、APRIORI、SimpleFb和framebuffer serial四文件与选定uefi-sheng 0eb4514相同，没有合并上游。
- alioth用SimpleFb代替原厂Display并条件排除CPR；elish/SM8250显式打包SimpleFb，分辨率1600×2560。本板不能只改USE_CUSTOM_DISPLAY_DRIVER：独立Vendor清单仍打包/调度Display/CPR，SimpleFb需同时接入Components/FV/APRIORI。
- enuma有1600×2560模式和原厂Display Reserved事实，但实际入口scanout base/stride/格式/线性布局/存活均未知。面板链路24bpp不能作为framebuffer格式；本板未给SimpleFb的ColorDepth，DEC默认0，并非已知32位。
- 现有Mu SimpleFb假定stride=width，且区域查找、模式范围、分配清理和GOP安装失败传播需要保护。仅协议注册成功不证明出图；当前DarwinBoot视频契约只接受BGRX32，需第三层独立验收。
- 现成framebuffer日志的handoff/cursor按本机区域会落入DFPS（0x9e3fffc0/0x9e3ffff8），不能照搬。保留Null SerialPortLib、SEC不清屏和Kona不detach MDP的现有补丁；不启用显示尾部元数据写入。
- 推荐未来显式SimpleFb+no-UFS诊断：只缺CPRDxe、DisplayDxe、UFSDxe，其余30 OEM PE/DEPEX不变，唯一SimpleFb。该组合尚未实现或证明运行时闭包。当前33/32模式审计仍禁止SimpleFb，未来需单独的严格分支，不能删除默认保护。

SimpleFb部分仍仅静态审计，未运行其驱动测试、固件构建或QEMU；不把本轮reader检查或历史FDT测试当SimpleFb通过。原25迁移文件/六patch、42项固件源锁、board/内存/512MiB/example/验证标记均未改。对其他板的同地址/同分辨率仅作对照，不视为实机参数确认。

## 最后一次实机证据（本轮未重查）

R-002已批准，临时Android日志候选保留于01:04:27的第二次启动通过：FDT唯一0x9fff7000/0x8000，8页全部reserved，节点/属性值与原样本相同。ADB16.079秒、启动完成31.722秒，root与boot/vendor_boot原摘要正常。镜像e0bd9b25d6e472a52735893dac970bb6f475e6c5394e6d878c615e54d6fc0e42。首版未保留的失败样本也保留。

该结论只适用于当次诊断Android；普通重启可能恢复普通RAM，未来必须重新核对活动FDT/页状态。不能声称本轮重新验证了设备或当前页保护。未加载模块、未读写物理日志/标记、未验证跨复位存活；ABI探针仅离线构建，正常内核加载仍未验收。R-002资料见 [实测交接](operations/2026-10-23-log-reservation-validation.md)。

## 主线位置与固定目标

完整GUID与延时对照支持到达UFSDxe及无UFS时DisplayDxe的CoreStartImage调用前，返回后门未观察到。UFS前门差5.357秒，Display四样本重复差5.277秒；Metronome提前未解决UFS。尚不能区分公共包装器/构造器/主体或复位来源。

没有GOP/UEFI map、菜单、DarwinBoot/XNU或NT36523运行证明。默认33 OEM、已实施无UFS32 OEM和拟议SimpleFb30 OEM证据必须分开。目标仍enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB，UniXNU5fdbd5d/21模块。历史通用4KiB内核成功不是本板最终内核。

## 下一步

1. 仍离线：整理实际scanout各缺失字段与可观测来源；在参数及所有权闭合后，按审计文档接最小SimpleFb暂存适配、精确30项FD策略与错误/范围检查。几何未知时不盲写或宣称硬件ready。
2. 恢复实机须用户后续指令；按文档G0–G6依次核对身份/恢复保障、唯一GOP、真实可见输出、loader视频契约和恢复。当前无待按键或在场操作，不自动续测。
3. R-002日志链保持独立：活动FDT/8页保护→正常ABI探针加载/卸载→最小标记与只读回读/跨复位存活→有界SEC/DXE日志。候选清空、ABI或临时契约不满足即停，不换址或刷分区。
4. GOP/内存图/BDS闭合后，再推进ADT/NVRAM、板级最终内核/prelink及最小XNU入口。EBS后显示、512MiB连续分配与触控均未由本审计验证。

设备上个里程碑 ac627bb 已推送；本轮提交与发布状态以Git记录为准，固件仓/gitlink未改。
