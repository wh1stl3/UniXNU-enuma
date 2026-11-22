# enuma r29 backboardd 分派观察（2026-11-22）

`self-checked`：依据主控转述操作和用户口述记录，未重新访问设备、镜像或 claim；无录像、无 vision 核读。阶段不提升。

2026-11-22 17:54:55 +08:00，r29 刷入 `boot_b`：`Sending 'boot_b' OKAY [4.106s]`、`Writing 'boot_b' OKAY [0.368s]`，exit 0；随后 `reboot` exit 0。claim `.cache/enuma-r29-bbscan-20261123.claimed` 已消耗，禁止访问、删除、重放。

镜像 `out/ufs-sm8250-launchd-bbscan-20261123-r29/boot.img`，169,951,232 B，SHA-256 `2a74b3e1c76df21b7da561b4cf6d8a45b2b5311819f37ad7ea3ce4443dab920b`。

主控提供刷写前 `deep_reviewer` 判定 **PASS**：类名取值安全、槽与返回值配对正确、语义限定足够、判据明确。

用户口述 `enuma-bb:` 块中 `calls=0`、`overflow=0`，无任何类名记录。在已观察窗口内，backboardd 未通过该 `newUserClient` 分派打开任何 IOKit 服务。结合 [r28](enuma-r28-device-20261123.md) 中板级 framebuffer 仅由 `MobileGestaltHelper`、`IOMFB_FDR_Loader` 打开，所观察的显示链未被 backboardd 使用。

`calls=0` 不能排除 `comm` 未命中、backboardd 走其他打开路径或观察窗口之后才发生；不能据此断言 backboardd 从未做任何 IOKit 操作，也不证明 SpringBoard 阻塞原因。
