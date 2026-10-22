# uefi-enuma source overlay

本目录是未来独立 uefi-enuma 仓的设备增量源码，基于 UniXNU/uefi-sheng `329b473df1e53a3bfa64b2b39b79670c4c02279b` 中已有的 Kona 实现。其 Mu_Basecore `cfb93724a06ff86ff5ba971413368a7809ee42a5` 与 UniXNU feeds 一致。Kona/alioth 参考文件与较新的 Mu-Silicium `42fe563791e51bf5500c2e470ed294ca0c94b97c` 内容相同，无需为此升级底座。不包含整棵上游树，也不是已构建固件。

`enuma.dsc` 复用 KonaPkg，UniXNU.dsc.inc 绑定真实 UniXNU/UniXNUDxe/DarwinBoot 模块，UniXNU.fdf.inc 将三者放入 FvMain。不能只添加 DSC 声明而漏掉 FDF。

必须提供三项经过审查的输入才允许完整 EDK II 构建：

- `ENUMA_PLATFORM_CONFIG`：实际 enuma MemoryMapLib、ConfigurationMapLib、DDR/栈/GOP；不提供 alioth 的默认内存值。
- `ENUMA_VENDOR_APRIORI` 与 `ENUMA_VENDOR_DXE`：enuma 厂商驱动及依赖顺序；未找到官方 Device-Binaries enuma 包，禁止改用 alioth 包充数。
- Resource config 的 FD 基址/尺寸及 boot header，需对应本板装载方案；尚未新增包含这些值的配置文件。

`patches/kona-preserve-display.patch` 是针对固定上游的最小修改：ENUMA_PRESERVE_DISPLAY=1 时跳过 Kona PlatformSec 的显示 SMMU detach，保留原 watchdog 处理。原实现会写显示 stream 映射；尚无 enuma GOP/地址空间交接证据，因此不能原样执行。此开关不证明 scan-out 可跨 ExitBootServices 保持。

运行 `scripts/check_firmware_overlay.py` 做源码级检查；不会运行 EDK II、生成镜像或改变参考树。`--require-image-ready` 在缺少前置输入时必须失败。

先用 `scripts/fetch_porting_references.py --fetch` 获取缺少的固定文件；默认不联网，只核验缓存。来源和许可证见 `config/porting-sources.lock.json` 与 `THIRD-PARTY.md`。本地参考树是 sparse checkout，根 LICENSE 未展开不等于上游没有许可证。

固件构建还要求独立可写 Mu/EDK2 工作树；UniXNU firmware.py 会初始化子模块、临时 apply 补丁，不能把只读资料库直接传给它。
