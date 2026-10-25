# 当前状态：D-278，R-018像素候选离线资格完成，未上机

2026-10-26T04:30:24+08:00。当前验收目标为UEFI固件日志上屏，随后UniXNU菜单。S-045已完成并consumed；新R-018像素事务只完成离线构建/资格/审查，**pending批准，不是硬件硬停，也没有执行S-046**。详见[R-018范围与选项](operations/2026-10-26-r018-bounded-pixel-transaction.md)。

## 已获证据

S-039稳定逻辑8888描述保留BLEND|ADDRESS|TOPOLOGY=22；S-042覆盖范围每页stage1读写转换恒等NormalWT；S-043一个实际字读取、S-044一个读前DSB、S-045原点128x8全部1024字读取及一个DSB在EL1完成。上述结论由预先声明的校准时间码间接支持，不能称原始数值日志、最终stage2、SMMU、写入、alpha/混合或可见显示通过。

S-045镜像315f5daa39f5b8a7b1e65edd030243eb179ea88a78713b27c39f3b08a8760f1e，origin27.462..27.522秒，Android49.172秒。首次发图前身份查询拒绝，恢复核验后按D-233仅重入一次，完整身份门通过才首次发图；现已consumed，历史preissue未发图状态不代表当前未消耗。证据reports/enuma-native-route-S-045-result.json。S-001..045全部consumed，不重试。

## 当前候选

固件 `c9530a746dbf6efbd7b1d55c020ce63477b8c198`；镜像 `743335d25d8cbd4b590acc462081fd992e5d4b32c0bcb234386033d13af08b56`；归档 `out/inherited-gop/qualified-native-cpu-pattern-c9530a7`。R-018最多128x8保存/复核/不透明对比色500ms/完整恢复读回，3072像素读、2048像素写、3DSB、660MDP只读及四次100ms采样等待。仅EL1、同次完整Native6和整段恒等NormalWT与精确Frame门通过才尝试store；保留22与所有未证明义务。

主机失败注入、实际Arm回调编译、14项native、12项历史pixel及10项FD策略测试、真实PE/Core手工审查、FD/完整FAT/Boot v3及控制台绑定完成。报告reports/enuma-pixel-transaction-host.json、enuma-native-route-qualification.json、enuma-native-route-code.json、enuma-console-path-audit.json。所有结果为离线资格，零本候选设备操作。reports/enuma-r018-preexecution-gate.json确认pending在设备动作前拒绝执行。

## 观察、恢复与下一步

按用户最新偏好，**点屏之前的只读探针不使用摄像头**；用选定enuma的ADB/fastboot状态、新boot-id/三次uptime区间和独立恢复摘要判定分类/恢复。它们不证明实际显示；只有图案、背光或画面验收才启用摄像头。原始影音仅本地out，禁止上传/录音。

最近独立恢复out/device-tests/20261026T040135-recovery-reconciliation.json：Android完成、root/A槽/解锁，boot_a/vendor_boot_a及本地备份摘要一致；本轮离线工作没有改变设备，当前在线状态须下次设备动作前重新查询，不把历史核验当即时状态。

当前需R-018精确镜像的一次最小像素事务批准；R-005已consumed不可复用。批准之后先落实全部当前文档/提交推送、重新核验身份/备份/恢复和摄像头，再单次临时boot；未批准时不执行像素写。code4恢复未建立、75秒无识别恢复、恢复失败、所需观测/时基失败或码歧义时停止追加并当轮落地。发图前身份查询异常沿D-233可控恢复后仅重入一次，不能忽略FAILED或重复已发图。

控制台/菜单源码已存在并打包，但本诊断早于BDS返回，均未实测。全局DEBUG当前空SerialPort；还需安全GOP发布、mask/alpha绘制适配及屏幕日志接收/重放，见[验收矩阵](operations/2026-10-26-uefi-console-menu-validation.md)。本阶段尚未点屏，不以iPadOS图形作验收。更早记录保留WORKLOG/DECISIONS/operations，不叠为当前状态。
