# D-292：8秒真实状态缓存页离线资格完成，R-022待精确确认

更新时间 2026-10-26T04:54:45.695706+00:00。S049/R021原镜像补拍已消耗，停止原图追加。最后一次设备动作仍为S049（2026-10-26T04:28:25.785364Z），自动返回Android56.859秒；独立恢复后验 out/device-tests/20261026T123411-recovery-reconciliation.json 通过启动完成、root、A槽、解锁、设备分区与本地备份摘要。未执行新候选；当前不是新鲜设备预检。

用户实拍反馈虚焦/白字粘连，并明确“两秒确实断了 对焦时间不足”。没有收到可读原片，status/ordinal仍未知；S048图案可见、S049间接code5和恢复成功均不能代替内容可读。

实际改进只将缓存页保持2秒改8秒；字体、原点、256×96、3行16列、73728次读/49152次写/3DSB、660次MDP只读与四次100ms、EL1/Native6/全帧WT条件不变。没有新增地址/寄存器写入/页表或缓存操作/分区操作。128条DXE RAM日志和私有快照协议保持，显示最近真实point13返回的完整EFI_STATUS和ordinal；这是缓存回放，不是早期实时日志、全局DEBUG、ConOut/Print、正式GOP或UniXNU菜单。

固件 8680ea79d6fd14d4526d314f430e9812955cb78a；新Boot v3镜像 `f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b`；FD `7bee85343b6f8837c1081f5cb08db939facfc1ec084c6f498d918ded1e02f035`。本地归档 out/inherited-gop/qualified-dxe-log-8s-8680ea7。提供器相对R020只有0x191c/0x1924两条立即数变化（0x1e8480→0x7a1200）；Core机器码与PE摘要完全相同。实际入口栈98832字节，未更改原256KiB CPU栈。

离线通过：2秒/8秒各24通道排列及960故障边界、保存/恢复/读回与零I/O拒绝；真实EDK AArch64双版本栈98544字节；旧像素/文本回归；scope6项、补拍与人手采集12项、固件审计10项。完整FD/30个OEM PE与DEPEX、排除驱动、完整FAT、源码/实际CC宏/打包PE一致性、BootShim192字节+3MiB、Boot v3 103817216字节通过。源码锁/旧board表/R002边界检查通过。机器码审阅摘要 e23b12cdeeea632ceec769d97d22d1eecbc51f267f89f6bafab2d444a11f5f38。

新时钟窗在执行前固定：仅完整原点区间落入39.252..41.748秒的唯一code5可提供间接CPU事务/恢复支持；code1..4、重叠、时钟不确定或观察失败均停止追加，不事后放宽。失败窗可能重叠，不能唯一定位错误。75秒硬停不变；历史约57秒加6秒仅预测约63–64秒，不保证新候选自动返回，也不修改看门狗。

R022 pending，计划S050仅单次临时fastboot boot，不继承已耗尽R021，不重包旧镜像。先确认本新镜像2→8秒精确变化及观测硬停后的单次继续；随后提交推送批准记录，核对当前身份/备份/恢复/时钟并重新取得用户“正在拍摄/已就绪”确认。主机摄像头已断开，只允许显式human-primary-only路径；不能把授权当作拍摄已开始。

拍摄：提前对准左上角256×96区域并锁焦，适当压低曝光避免白字粘连，关闭录音，从启动前持续到Android返回。验收分别记录：原始片中C0d O八位ordinal（可有+）、S高32位八位和下一行低32位八位是否逐字可读；CPU时钟推断；保存/恢复读回推断；Android/root/槽位/摘要后验。未知值不猜测。若仍不清晰，停止追加并保留本地原片，不能靠重复次数算通过。

后续依赖：可读缓存页→对具体DXE返回值归因；更早阶段日志须另有输出链证据；菜单前文本/ConOut须实际执行；GOP必须满足完整准入，菜单还依赖BDS路径。requirements22/alpha/SMMU及任何verified结论不提升。所有原始影音仅本地out，不上传、不录音。nuwa与旧会话未操作。

证据：reports/enuma-log-hold8-code-review.json、enuma-log-replay-host.json、enuma-native-route-qualification.json、enuma-native-route-code.json、enuma-console-path-audit.json、enuma-fd-audit.json，以及S049历史结果。固件与设备仓完成本里程碑提交后正常推送；实际远端状态另行核对。
