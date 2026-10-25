# 当前状态：D-222，完成enuma/elish公开仓离线研究；设备硬停后状态保持

2026-10-25T21:17:35+08:00。D-221硬停后，用户新要求“参考一下同机型的其他人的仓库和WIFI版型号elish的仓库 看看他们怎么解决这个问题”。本轮仅按该请求查公开源码、固定版本/摘要、做对照和文档；没有新设备命令、读取物理RAM、加载模块、构建候选、映射/写入或上机。最后已知设备状态仍为21:01:29独立核验通过的Android完成/root/A槽/解锁及设备/本地备份双分区摘要一致；未为研究重复该恢复核验。

新结论：未发现受审enuma/elish仓库已解决本机PSCI warm留存的实机证据。同型Tlrenhb/uefi-enuma内有pipa复制的RamoopsLogLib，具体路线为SPMI/PON warm配置、重启原因、SCM/PS_HOLD，而非通用PSCI reset2；文件明确TODO(enuma)，DSC对板级reset/serial仍待移植，设备reader脚本仍TODO。hpadmx/UniXNU-elish处于准备阶段；edk2-msm elish可走FramebufferSerialPort或GENI UART，但common仍绑定通用PSCI reset2/cold回退，并非已核实的warm留存修复。

最值得借鉴的是完整板级复位＋早期reader链：umi的UmiResetSystemLib源码记录PSCI复位曾挂死，改为核验PON/SPMI/SCM后PS_HOLD复位；pipa提供独立临时Linux，在Android用户态之前复制pstore并以只读USB磁盘导出。对方报告不是enuma通过。pipa默认还会改电源键复位类型、reader写pmsg测试标记并使用其自身DT/boot格式；这些均不能直接移植或视作现有授权。elish Linux的record4096/ECC16配置也不等于本机record0/ECC0/console与pmsg对半布局。

建议后续排序：先离线核对enuma原生PON代际、SPMI版本/EE/APID、PS_HOLD/IMEM和SCM约定，再以已返回cold门隔离新的最小writer，同时准备去掉pmsg测试写入的enuma早期reader；最后才评估板级warm留存。新PMIC控制、长按行为或范围扩大须按现有规则形成具体实施审查；本轮只研究，不提出未构建方案的执行批准，不开始硬件实验。仍无ramoops留存/GOP/XNU/iPadOS实机闭合。

研究固定9仓40文件，SHA256及Git blob双校验和9组源码事实检查通过。源锁config/enuma-elish-reset-sources.lock.json；复现scripts/audit_enuma_peer_reset_routes.py；报告reports/enuma-elish-reset-route-review.json；详细来源与边界docs/operations/2026-10-25-enuma-elish-reset-reference-review.md。没有更改固件pin、board.toml/bringup-plan或verified；固件仍5cfcd4cc68c0c37ffb322322efc256760d9389e3，默认映射和Null后端保持。

最后实机：S-018于20:57:13单次发出6b145fd370bb67a5db16112764701d8a4234b27c0eabc5d9e043bb7d92d843a5，命令0/2.641秒、断开5.110秒、75秒无返回触发硬停；用户恢复，独立证据out/device-tests/20261025T210129-recovery-reconciliation.json，原失败记录保持。录像1090/1090帧、末段Android重启logo及补拍桌面已目视，按键动作未明确核对。结果reports/enuma-ramoops-S-018-result.json。S-016映射/cold、S-017三读/cold均自动返回，使warm链成为首嫌，但FEATURES/reset2/回退执行点未定位，writer安全未证明。S-001..018及旧失败图consumed，不重试。

当前无人工恢复按键或执行审批待办；硬件实验仍停在D-221后的边界。本轮研究与文档提交推送后完成答复。所有原始影音仅本地out，无录音/上传；本轮无新增影音。82430d4是前一恢复交接已推送里程碑，本轮新增仅离线研究。
