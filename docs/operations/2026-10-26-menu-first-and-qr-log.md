# D-308：菜单优先与 QR Log 适用性

用户最新目标是最快进入真实 UniXNU 菜单。连续文本日志、全局 DEBUG 和 QR 导出不再是菜单验收的前置任务。既有 S052/R024 结果与消费记录保持，未批准新实机试验；本轮不提交推送。

## 已落到代码的路径缩短

`firmware/Platforms/Xiaomi/enumaPkg/Include/UniXNU.dsc.inc` 新增默认关闭的 `ENUMA_DIRECT_MENU`。值为 1 时，UniXNUDxe 的应用 PCD 指向真实 UniXNU GUID `9B665204-A133-47A2-9396-9E2B370A4E25`；默认仍指向 EnumaProbe。真实应用识别 `unixnu:firmware` 启动标记并调用 UniXNURun，无需先成功回放 EnumaProbe 的日志。

独立开发构建支持 `--profile stage10 --direct-menu`，明确拒绝与 attributed-log/diagnostic-log 混用。保留 stage10 诊断早停和 GOP 准入，不生成一个假称可实机进菜单的包。构建证据目录 `out/menu-priority-20261026/build1`，最终结果以该目录报告为准。

`tests/uefi_menu_chain.c` 在两种几何下将 ConOut 设为 NULL，实际固定版本 Ui/Menu 仍完成绘制、默认倒计时、选择、取消和确认，再恢复 ConOut 单独测文本回退。`scripts/check_unixnu_menu_qemu.py` 要求两种几何都出现新增成功标记。`out/menu-priority-20261026/qemu1/result.json`：21 条命令通过，包含主机内存检查、ARM 编译链接、QEMU 执行、帧 CRC 与越界保护。已查看竖屏图。

此证据是分配的 VM RAM 与模拟输入上的真实 Ui/Menu；不是整个 UniXNURun 的配置发现链，不是 enuma 的物理 WT 映射、按键或屏幕验收。测试前面的 GraphicsConsole 和日志回放仍作为独立回归保留；菜单自身在 ConOut=NULL 期间运行。

## QR Log 结论

当前构建固定 `5fdbd5d08518bc2d5c196264c56a377dd80cf5ca` 没有 AdvancedLogDxe。已在本地审阅的新上游固定版本 `16e592abee8a550dec8154ed1f38b5ebc4f16213` 确认存在 `AdvancedLogDxe`、UniXNUMenuPlugin 协议与 `docs/porting/log-capture.md`；不是对网络最新 HEAD 的声明。

它是 Tools → Advanced Logger 插件，读取 Advanced Logger 内存日志并用 GOP 画 OneSend QR 帧。INF 的 DEPEX 是 `gAdvancedLoggerProtocolGuid`，依赖 AdvLoggerPkg、MsGraphicsPkg、AdvancedLoggerAccessLib、QrEncoderLib；还须 DSC/FDF 纳入模块并有 Tools 菜单。当前 128 条 DXE 状态环不是 Advanced Logger 协议，不能仅加一个 INF 就导出这些记录。

决策：本轮不升级整个 UniXNU、不把 QR 接入作为菜单阻塞项。菜单可用后再独立升级/回移插件与协议，并确定日志生产者。QR 不能解决菜单出现前的显示故障。

## 真实剩余路径

1. 将已经可见的有界像素事务扩展为可持续、可停止的实际显示提供器：解决物理范围/映射、opaque blend 与持续路由校验，以及失败后停止写入/恢复；不能直接将 requirements22 清零。
2. 接入实际 GOP 发布与 BDS 直达应用，使用只含返回/复位的菜单配置，单独核对配置发现和实体按键。真实 UniXNURun 会关闭 BDS watchdog，不能把旧诊断自动复位当作菜单的返回保障。
3. 新镜像完整资格和可控返回方案完成后，再申请该镜像单次实机与当前录像。成功标准是实际 UniXNU 菜单与操作，不是固定菜单位图或 QEMU 截图。

最短依赖链为实际可用 GOP → 真实 UniXNU 图形菜单 → 实体输入/返回。ConOut、完整文本日志、QR 导出可并行或后置。没有新的设备命令、内存字段或 verified 变更。

D308最终离线结果：build1完整FD c72d4e3ef72b386fccd0353d5eb59aee2c9f3552d5a7e5a28319ff29817270ae；direct-entry.json核对实际生成PCD与PE均为真实UniXNU应用。qualification3通过FD/OEM PE与DEPEX、模块/库检查和Boot v3打包反解，镜像SHA256 0808ef8b0dcb36329c927f0d5096f484a4eeac7bc9c8c45e124eff117b0292dc。qualification1/2旧审计假设失败保留，分别修复固定Probe目标和旧ConOut函数名假设；原R024实际资格元数据回归与错误direct-menu选择拒绝通过。全部仅离线，stage10早停/空ramdisk，不可直接上机进菜单。完整证据reports/enuma-menu-priority-development.json。


## D-309：纠正自动返回前置要求

用户指出nuwa菜单可手动回fastboot或Android。重新核对本仓AGENTS的设备门禁与既有人工恢复规则：要求有可用恢复路径，不要求菜单固件必须自动返回。D308及对话中“必须单独实现菜单阶段自动/受控返回”作为新增软件前置的解释撤回；它是本轮过度收紧，不是原规则。菜单可沿本机已有证据支持的人工按键恢复路径，在人在场、当前条件核对及精确新候选资格满足时验证。UniXNURun关闭BDS watchdog这一源码事实仍成立，旧探针自动复位和75秒观察窗不能冒充菜单自动返回保证。无需为此另实现自动复位功能。当前实际GOP/配置发现/实体输入仍待接通，新镜像资格与单次范围/录像条件不跳过，R024消费记录不复活；未做任何新设备动作或提交推送。nuwa本次未核验，不将其行为当enuma恢复证据。

历史D308构建和报告保持原字节；其中remaining内的自动/独立返回任务由本条纠正，后续以STATUS/HANDOFF为准。
