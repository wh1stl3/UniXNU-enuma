# sheng-lite 禁用列表恢复（2026-11-23）

状态：self-checked；未构建、未访问设备。恢复 sirius 的 21 项：sirius 的 Setup 触摸记录对应源码版本配置了同一列表，见 `docs/lite-list-sirius-origin-20261123.md`；这不证明各项在 sirius 逐一生效，也不证明 enuma 的运行结果。

相对 r50（`98afba2`），保留原前四项并恢复后 17 项，顺序不变；生成逻辑、`disabled.plist`、`disabled.migrated` 和 watchdogd 代码不变。恢复后的 `lite_jobs` 声明与 `git show 98afba2^:package/BootWatchdogPolicy.c` 的对应声明逐字节一致；不声称整个文件一致。

sirius `HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503` 的 `package/BootWatchdogPolicy.c` 另有 `sheng-disable-jobs` 参数解析、Setup 完成标志重置和 `sirius-skip-setup` 偏好写入，我们未实现，本次不实现。
