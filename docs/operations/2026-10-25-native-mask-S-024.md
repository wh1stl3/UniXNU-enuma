# D-233：S-024首次进入fastboot查询异常，已恢复，按用户新规则重新进入一次

2026-10-25T22:49:37+08:00。S-024字段4镜像尚未发出、未consumed。22:44:23首轮fastboot身份门禁拦截：最初product=enuma，current-slot返回unknown command、unlocked返回Variable Not found；随后整组查询仍失败，尽管工具退出码为0，严格正文检查正确拒绝，没有fastboot boot。相机确认FASTBOOT。

已对原选定目标执行fastboot reboot（OKAY），独立恢复核验out\device-tests\20261025T224737-recovery-reconciliation.json通过：Android完成/root/A槽/解锁、boot_a及vendor_boot_a设备与备份摘要相等；相机frame0431确认Android桌面。视频1009帧/解码1009帧仅本地。相机runner_exit=1保留首次门禁失败事实，不能改写成固件启动成功。

用户新指令：“这种情况不需要硬停 只需要重新进入一次fastboot 进入规则 继续”。因此这次预启动查询故障不是本轮停止点；当前文档推送后从已验证Android重新进入一次fastboot，继续原product/slot/unlocked完整检查，通过才执行原S-024精确镜像。不是重试已启动/consumed固件，也不放宽查询接受条件。若再次无法满足身份/恢复门禁仍不发图，按实际情况处理；真正固件75秒超时/恢复失败、观测模糊等原规则保持。

固件2bb165fa0dd882da1f79b9919435f00f3a4e36d8；S-024图a50f11765285ca1b9a7cd1ac6d41b1648767cc0c2170036a41ee8141e0e84dc4，FDe98eb9bad37f8ad59db3cb33c5d9c4276811bb7f7f17e9c2d58c5104bfbb218f，归档out/inherited-gop/qualified-native-mask-2bb165f-field4。构建/实际PE/宏/FD/完整FAT/Boot v3均已审，字段4相对S-023只有RVA14d4的结果LDR偏移改变，Core PE相同。原R-004最多26读/two100ms、无像素或MMIO写、无新地址/verified/分区变化，固定五码cold2/7/12/17/22秒及boot-origin窗口不变。

有效增量仍是S-023活动掩码3间接支持，两路在三个样本均活动，启动原点27.450..27.523秒、自动Android49.250秒，恢复核验已发布909ad77。S-024帧递增尚未观测，完整GOP/点屏仍未成功。S-019/020保持ambiguous，S-021/022仅时基校准，S-001..023已consumed。后续根据S-024实际结果继续隔离Enable/Timing/布局，跨boot不拼接同时成立证据。

资格reports/enuma-native-mask-qualification.json、代码reports/enuma-native-mask-code.json、此次门禁reports/enuma-native-mask-S-024-preflight-attempt1.json。全部原始影音仅本地out，不录音/上传。无人工待办或新增范围审批。
