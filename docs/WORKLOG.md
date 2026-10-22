# WORKLOG（只追加）

- 2026-10-22 Asia/Shanghai · 建立独立仓库纪律，用户选择 iPadOS 17.7.11 · 提交号见下一里程碑记录 · AGENTS.md、docs/DECISIONS.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑提交 ee52c26；六组件摘要、FDT/ADT 计划、Kona/NT36523 来源、9 项测试和四组 UFS 主机检查完成；修正 ipad_identity · 本里程碑提交号由 Git 日志定位 · reports/、docs/operations/2026-10-22-offline-bringup.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 b34ecba；离线接入既有 Kona/UniXNU 固件源码，新增 GENI FIFO 适配和 Kona UFS 只读时钟支持；主机 sanitizer、AArch64 对象及固件图/补丁检查通过；提出 R-001，内存字段未修改 · 本里程碑提交号由后续记录/Git 日志定位 · reports/enuma-driver-check.json、reports/firmware-overlay-check.json、docs/operations/2026-10-22-kona-platform.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 3249989；用户批准 R-001，512 MiB 请求已写入，更新精确配置保护并通过 source pins/上游 defconfig/example 检查；未生成镜像或访问设备 · 本次提交号见后续记录/Git · board.toml、reports/workspace-check.json、docs/NEED-REVIEW.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑 982dcc0；将已批准预算接入 ADT JSON 计划，复用真实 DarwinBoot 解析/窗口选择函数完成主机 sanitizer 检查；最初测试夹具低估对齐余量，修正预期并新增拒绝用例后通过，未改上游 · 本次提交号见后续记录/Git · reports/darwin-adt-contract.json、docs/operations/2026-10-22-owned-memory.md。
- 2026-10-22 Asia/Shanghai · 上一里程碑5a86159；用户放开镜像生成和可恢复推送/启动，已只读采集当前enuma并从本机XBL补齐平台表、原厂驱动及K81资源；v3打包往返测试和完整EDK构建完成，复核并修正GIC补丁根目录后重建；未启动候选 · 本次提交号见后续记录/Git · reports/enuma-platform-observations.json、enuma-firmware-build.json、enuma-fd-audit.json、enuma-boot-candidate.json、docs/operations/2026-10-22-native-platform-firmware.md。

- 2026-10-22 Asia/Shanghai · 上一里程碑 5d84d7b；用户暂时不能配合按键，保持设备状态。新增复用 DarwinBoot 的 EnumaProbe 01，完整 UEFI/81 文件/33 OEM 字节审计及 boot v3 往返通过；生成 enuma 硬件 ADT 片段与 NT36523 解码核心，27 项 Python/主机 sanitizer/4 个 AArch64 对象通过。未实机启动、未改内存字段及验证标记 · 本里程碑提交号由后续记录/Git 日志定位 · docs/operations/2026-10-22-probe-platform-touch.md、reports/。

- 2026-10-22 Asia/Shanghai · 上一里程碑 940ef77；首次 Probe 01 r2 临时启动发送/boot 命令被接受，但用户报告黑屏；按键回 fastboot 后正常重启，20:18:24 确认 Android boot_completed=1/root、槽 A 与 boot/vendor_boot 摘要不变，pstore 空。无刷写或改槽，不宣称 UEFI/GOP 通过 · 本次提交号由后续记录/Git 日志定位 · reports/enuma-probe01-device-test.json、docs/operations/2026-10-22-first-device-probe.md。

- 2026-10-22 Asia/Shanghai · 上一里程碑 aaff143；核对 BootShim ARM64 头、复制与入口契约，加入复用 Mu 的 SEC/DXE 定时复位门；六次临时启动均回 Android，已走到 CoreDispatcher 前，2/7 秒入口对照差 5.422 秒。30 项 Windows Python、共享门主机 sanitizer、QEMU 入口和完整固件/OEM 字节审计通过；WSL 整套 Python 的环境/路径错误单独记录。未改内存字段或验证标记，未刷写/改槽；核对远端和 macOS 依赖但未创建/推送/触发 CI · 本里程碑提交号由后续记录/Git 日志定位 · reports/enuma-entry-device-tests.json、docs/operations/2026-10-22-entry-checkpoints.md、2026-10-22-build-environments.md。

- 2026-10-22 Asia/Shanghai · 上一里程碑 8aa2d95；用户批准公开建仓，已创建 wh1stl3/UniXNU-enuma 并推送 main。准备手动 macOS preflight/通用 4K bootstrap，固定 Xcode/SDK/来源提交，保存独立证据；修正与未启用 UFS 冲突的 BOOT_PROGRESS 候选开关。完整 enuma 归档/预链接尚未完成 · 本次提交号见后续 Git；远端执行结果随后记录 · .github/workflows/macos-xnu.yml、scripts/ci/macos_xnu.py。

- 2026-10-22 Asia/Shanghai · 上一里程碑 2312231 已推送；macOS preflight run 39784132935 成功，回读 artifact 核对 Xcode 16.4/SDK18.5/arm64 编译；通用 4K bootstrap run 39784240390 已启动，记录时仍运行，不宣称内核通过。另解码比较两次 stage10 FD，定位 SEC 时间字符串及 PcdDxe RSDS 标识差异，保留原实测摘要边界 · 本次提交号见后续 Git · reports/enuma-macos-preflight.json、enuma-macos-bootstrap-run.json、enuma-fd-rebuild-comparison.json。

- 2026-10-22 Asia/Shanghai · 上一里程碑 93acb9e；按用户要求遍历官网144页/3836站内链接并对照144源路由，中文72页逐页审阅，记录1处锚点问题。查明文档源码较固定构建领先89提交/完整509项树差异/新增21模块gitlink，保留原pin。用缓存FDT核对35MiB splash，只列为待核查线索。回读bootstrap CI失败的最终链接证据，修正先前运行中状态。形成分阶段路线/复用矩阵/源码与示例差异清单，未操作设备或改内存/镜像/验证标记 · 本里程碑提交号见后续 Git · docs/operations/2026-10-22-official-docs-route-review.md、2026-10-22-official-site-inventory.md、reports/enuma-official-docs-audit.json。
