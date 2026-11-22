# iPadOS 17 GPU 与显示实现清点（2026-11-23）

状态：self-checked，静态调查；没有构建或设备操作。A = GPU/Metal 合成及 GPU presenter；B = 显示控制器扫描；C = CPU framebuffer 拷贝。扫描输出与合成是不同环节，可同时存在。

## 线别边界

- **iPadOS 17**：`UniXNU/UniXNU-sheng` 历史 `0c2046b84dbee545e7e3923eb74d7bb1ce020978` 的 README 报告原版 iPadOS Home Screen、Settings 和 Adreno 740 合成；同提交 board 指定 iPad7,1 / 17.7.11 / 21H461 与 OS UUID 04769D26-2CA0-4825-B443-E2E5F88300F2。运行记录与镜像哈希不在该 README，donor 关联是同提交配置，不是独立核实。原文、历史及界限见 [sheng donor 调查](sheng-donor-branches-20261123.md) §关键证据及 §da9fab9。历史 `da9fab96aea0b5dcdb3bef730b10397276514dac` 的同 donor 配置有 `sheng-fb-gpu=1`；README 汇总不能证明该次 logo 停滞运行到桌面。
- 同仓 `c8f92b208068eeaa4cd2b0f592671f04ee70076e` 是多 OS 单分支，不是仅 macOS：`board.toml:173-185` iPadOS 17 override 选择 Adreno740、AdrenoMetal、GopFramebuffer，参数改名 `fb-gpu=1`；`:188-189` 有相同 UUID。`:218-243` 为 macOS 27.3，排除其实测与说明作为 iPadOS 17 证据。历史删去 `sheng-` 前缀记录见上述 donor 调查 §前后显示相关提交。
- pipa、sirius 与 orangepi5 的 board 配置明确 21H461。pipa 作者汇报同代无插件 CPU UI 与 Metal UI；不能把它当 enuma 实测。独立组件仓代码不是单一 OS 的运行记录；下文只作接口证据。

## 1. sheng 的 GPU 合成是什么

历史 iPadOS 17 配置 `da9fab9:board.toml` 的 `sheng-fb-gpu=1` 不是仅名字；历史同接口可在 sirius 固定版本 `ac0c900485f3c0cd18de9707579a1cdcd3365503:drivers/GopFramebuffer/NativeGOPPresenter.cpp:94` 看到 `PE_parse_boot_argn("sheng-fb-gpu",&v,sizeof v);gpuMode=(v==1)`，`:109` GPU 模式拒绝 CPU copy，`NativeGOPWire.h:9` 描述向特权客户端提供完成帧。它是同接口的旁证，**不是 da9fab9 当次链接对象的 pin**。

现行独立 [GopFramebuffer](https://github.com/UniXNU/GopFramebuffer) `b0d812d578efa2acb005b66f73168891719af09a`，`NativeGOPPresenter.cpp:107` 解析 `fb-gpu`，`:122` GPU 模式拒绝 CPU copy，`:145-151` 入队提供帧；`NativeLegacyDisplay.cpp:697` 调用 `native_legacy_gpu_offer(...)`。 [AdrenoMetal](https://github.com/UniXNU/AdrenoMetal) `cc0a4e8e57d20f4a4698753c2530875f2b10c0ca` 的 `GpuScanoutClient.h:2-3` 描述 GPU 将 compositor surface 复制到 scanout 并完成 swap，`NativeAdrenoMetalPlugin.mm:2-7` 描述 IOAcceleratorES/Metal 插件发现和 render server GPU UI；[Adreno740](https://github.com/UniXNU/Adreno740) `be70fb13ed19d5fdf139d27977da6f54078cf50a` 的 `NativeAdrenoAccelerator.cpp:2-3` 指向 IOAcceleratorES 和 MetalPluginName。

**判定 A**：历史同 donor README 明确报告 Adreno 740 合成，配置打开 GPU handoff；GPU presenter 是 GPU 拷贝，不是仅 DPU 扫描，也不是 CPU 拷贝。现行代码展示对应机制，但没有核对历史运行镜像内每个组件精确版本，不能把当前代码逐字视为历史运行证据。独立的 DPU 扫描 B 可与 A 共存。`fb-gpu` 本身仅控制 presenter handoff，并不单独证明 Metal 合成已经启动。

## 2. 仓库清点

调查方法：GitHub 组织 API 列出仓名，浅克隆目标仓并搜索 GPU、显示关键词；本地 common 使用 Git tracked 内容。组织列表中设备仓为 UniXNU-sheng，common 为 UniXNU-sm8550-common；组织组件另有 Adreno740、AdrenoMetal、GopFramebuffer。下表“无”仅指本次检查范围，非全网断言。

| 仓及检出版本 | GPU/显示实现 | 类别 | SoC / GPU |
|---|---|---|---|
| [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) `c8f92b2`、历史 `0c2046b` | 有，17 profile 选 GPU 与 framebuffer；历史作者报告 GPU UI | A；另有 C 接口 | SM8550 / A740 |
| [UniXNU-sm8550-common](https://github.com/UniXNU/UniXNU-sm8550-common) `2dc650ca76ae38715cd0712e60a44b14fe251745` | 有，`soc.toml:11` 选择 GPU 组件，`kits/Sm8550Platform/` GMU 等板族支持 | A 的平台部分 | SM8550 / A740 |
| [Adreno740](https://github.com/UniXNU/Adreno740) `be70fb1` + [AdrenoMetal](https://github.com/UniXNU/AdrenoMetal) `cc0a4e8` | 有，内核服务及用户态 Metal 插件 | A | SM8550 / A740；不是 A650 现成驱动 |
| [GopFramebuffer](https://github.com/UniXNU/GopFramebuffer) `b0d812d` | 有 presenter、CPU copy、另有 DPU scanout 接口 | A 的 presenter / B / C | 组件通用接口，DPU backend 有平台依赖 |
| [FFT-infra/UniXNU-sm8250-common](https://github.com/FFT-infra/UniXNU-sm8250-common) 本地 `166235ec2480ff0992627b7aafa15c65ce6b4efa` | 有 `kits/Sm8250Platform/A650Gmu*` GMU、电源/时钟，`dts/sm8250.dtsi:69-72` A650 节点；`configs/sm8250.config:3` native Adreno 默认关闭 | A 的部分，非完整 A | SM8250 / A650 |
| UniXNU-enuma 当前及历史 | 有 legacy framebuffer 候选，`docs/enuma-gop-r5-device-observation.md`；此处未穷尽全部 ignored `out/` 快照 | C 候选，实际 swap 尚无证明 | SM8250-AC / A650 |
| [xVanTuring/UniXNU-pipa](https://github.com/xVanTuring/UniXNU-pipa) `cdb3d62771e31d48d832853ee0c90964346d78da` | 有，`README.md:66,81-86` 报告 A650、Metal 和无插件 CPU UI；`drivers/Adreno650` 子模块指 `xVanTuring/Adreno650` commit `01db67e0620fe0e70ab8cbce533cbdb1369f5922`，未检出其源码 | A / C，作者报告 | SM8250 / A650 |
| [HuajiFruit/UniXNU-sirius](https://github.com/HuajiFruit/UniXNU-sirius) `ac0c900` | 有 GOP presenter；`porting.toml:419,427` 记录 A616 资源和 Adreno6xx 方向，不等于已运行 GPU | C / A 候选 | SDM710 / A616 |
| [Ken-u/UniXNU-orangepi5](https://github.com/Ken-u/UniXNU-orangepi5) `729ba25f4d67225ff3853ba1e435b95af97e59e3` | README:25 当前 console defconfig 无显示、无 GPU；引用其他 EVB10 仓可复用代码，未检查其实现 | 当前配置无 A/B/C | RK3588S / Mali，型号未在本次源码核实 |
| [RigoLigoRLC/unixnu-adreno6xx](https://github.com/RigoLigoRLC/unixnu-adreno6xx) `86e0f1bd9afb3471b82ceac11fc062426af674a2` | sirius 提及的 A6xx 驱动来源；本次未核实该默认分支 A650 支持及 OS 集成 | A 候选 | A6xx；具体型号未核 |

外网查询中一次 `git ls-remote --heads` 遭 Windows schannel TLS 握手失败，未重试；此前克隆和组织 API 成功。额外 common 仓全网枚举不完整。仓内 `out/` 快照很多，本次未穷尽，不能推出不存在其他实现。

## 3. 适配距离与桌面

同 SoC 的 pipa 有最接近的完整 A650 驱动、Metal 和 presenter 组合；common 的 A650 GMU kit 已在本地，但它只是一部分，**同 SoC 不等于 enuma 直接可用或已验证**。板级固件、供电、时钟、内存/SMMU、显示和参数仍须本板证据；不跨用设备资产。A740 方案则除用户态 Metal/presenter 适配外，还涉及 A650 的内核硬件后端和平台资源；不能以重命名完成。

pipa 的同代 README:66 称去掉插件 publish 文件时 UI 使用 CPU 渲染，并报告已到桌面；这是同代同 SoC 的作者报告，显示 GPU 加速**不是原理上的必需条件**，不证明 enuma 当前 CPU 路径能到桌面。sheng 的 A 路径只证明其报告使用 GPU，不证明 GPU 是唯一可行路径。

**iPadOS 17 线到桌面是否需要 GPU：不需要作为普遍前提；pipa 同代 README 报告 CPU UI，但 enuma 尚未验证。**
