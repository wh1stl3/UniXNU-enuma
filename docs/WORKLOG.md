# WORKLOG（只追加）

- 2026-10-22 Asia/Shanghai · 建立独立仓库纪律，用户选择 iPadOS 17.7.11 · 提交号见下一里程碑记录 · AGENTS.md、docs/DECISIONS.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑提交 ee52c26；六组件摘要、FDT/ADT 计划、Kona/NT36523 来源、9 项测试和四组 UFS 主机检查完成；修正 ipad_identity · 本里程碑提交号由 Git 日志定位 · reports/、docs/operations/2026-10-22-offline-bringup.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 b34ecba；离线接入既有 Kona/UniXNU 固件源码，新增 GENI FIFO 适配和 Kona UFS 只读时钟支持；主机 sanitizer、AArch64 对象及固件图/补丁检查通过；提出 R-001，内存字段未修改 · 本里程碑提交号由后续记录/Git 日志定位 · reports/enuma-driver-check.json、reports/firmware-overlay-check.json、docs/operations/2026-10-22-kona-platform.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 3249989；用户批准 R-001，512 MiB 请求已写入，更新精确配置保护并通过 source pins/上游 defconfig/example 检查；未生成镜像或访问设备 · 本次提交号见后续记录/Git · board.toml、reports/workspace-check.json、docs/NEED-REVIEW.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 982dcc0；将已批准预算接入 ADT JSON 计划，复用真实 DarwinBoot 解析/窗口选择函数完成主机 sanitizer 检查；最初测试夹具低估对齐余量，修正预期并新增拒绝用例后通过，未改上游 · 本次提交号见后续记录/Git · reports/darwin-adt-contract.json、docs/operations/2026-10-22-owned-memory.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑5a86159；用户放开镜像生成和可恢复推送/启动，已只读采集当前enuma并从本机XBL补齐平台表、原厂驱动及K81资源；v3打包往返测试和完整EDK构建完成，复核并修正GIC补丁根目录后重建；未启动候选 · 本次提交号见后续记录/Git · reports/enuma-platform-observations.json、enuma-firmware-build.json、enuma-fd-audit.json、enuma-boot-candidate.json、docs/operations/2026-10-22-native-platform-firmware.md。

- 2026-10-22 Asia/Shanghai · 上一里程碑 5d84d7b；用户暂时不能配合按键，保持设备状态。新增复用 DarwinBoot 的 EnumaProbe 01，完整 UEFI/81 文件/33 OEM 字节审计及 boot v3 往返通过；生成 enuma 硬件 ADT 片段与 NT36523 解码核心，27 项 Python/主机 sanitizer/4 个 AArch64 对象通过。未实机启动、未改内存字段及验证标记 · 本里程碑提交号由后续记录/Git 日志定位 · docs/operations/2026-10-22-probe-platform-touch.md、reports/。
