# 当前状态：D-215，原生ramoops核心与审计完成；R-017映射待审

2026-10-25T19:45:02+08:00。用户支持继续后，已实现未接线的原生console环形写入核心及只读pstore收集器。51,210个独立队列oracle/边界用例、ASan/UBSan和实际EDK头文件AArch64对象编译通过；5个收集器主机测试通过。未完成新FD/打包/实机资格，不能称日志已经打通。

核心来源为固定umi 3eb7257，保留BSD许可；MiCode 52a2f18仅作格式参考，未导入GPL内核代码。12字节DBGC头与本机ECC0、console2MiB布局相合。当前UEFI页表缺少B0000000区域，不能直接启用后端。Normal Non-cacheable不等于XN，ResetWarm可能回退cold，跨复位保留及Android早期清理仍未验证。

**本轮停点是新增内存范围审查，不是设备故障。R-017 pending。** 固件AGENTS明确新memory size/base仍走companion review。最小A方案：仅新增0xB0000000/0x200000普通不可缓存保留映射，MMU完成后的有界Core入口仅追加一次44字节随机nonce标记，短延时后warm请求/不支持时cold回退，一笔新资格镜像临时boot；pmsg不映射/不写，不写分区/改槽/verified，不启全局SerialPort。B方案保留现表继续独立计数隔离。需明确A精确范围后才接线与完整构建审计；全部资格、文档发布和即时恢复门禁满足后沿已授权流程直接上机，不重复申请一般上机许可。

当前内存表、board.toml/bringup-plan及Null后端均保持。固件源码pin 91a8a7c56d327e30262765548e2cd98bd5107037 已推送，是未接线核心的新源码里程碑；最近已实测源码仍为b93b3bb。无新boot、物理RAM访问、模块加载或分区写入。最终只读核验Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备和本地备份摘要均通过，证据 `out/device-tests/20261025T194122-recovery-reconciliation.json`、`reports/enuma-recovery-reconciliation.json`。

S-013/S-014的历史互补时序支持首样本Enable门禁Reason5（间接证据、中等置信），后续完整采样/稳定性按该路径未执行；S-001..014及旧失败镜像consumed，不重试。显示独立原生双路计数前缀尚未实现，完整GOP资格不放宽。真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合。

详见 `docs/operations/2026-10-25-ramoops-compatibility-audit.md`、`reports/enuma-ramoops-compatibility-audit.json`、`reports/enuma-ramoops-buffer-tests.json`、`reports/enuma-ramoops-kernel-sources.json`。原始影音仅本地out，未录音/未上传；本轮未产生新影音。无人工恢复按键待办，审批见NEED-REVIEW的R-017，不把旧R-002/R-008扩张到新区域。
