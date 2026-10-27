# enuma 离线适配基线

2026-10-22，Asia/Shanghai。当前是板级输入、构建接口和复用边界的静态检查；尚未完成 XNU 编译、QEMU 或实机启动。

## 固定输入与复现

设备仓首提交 `ee52c26`。固定来源与文件哈希见 `config/sources.lock.json`；完整输入审计见 `reports/input-audit.json`。

| 输入 | 固定提交 | 用途与许可边界 |
| --- | --- | --- |
| UniXNU | 75bc13dd34dc4e403826793739e316a264ce00dd | 构建、DarwinBoot、通用驱动；BSD-2-Clause-Patent |
| UniXNU-sheng | a599a1a8a92093b5077543e071b72130769eb325 | donor/ADT 契约参考；BSD-2-Clause-Patent，不继承板值 |
| xnu-ios17-full | d8b80295118ef25ac3a784134bcf95cd8e88109f | feeds 对应 10063.141.1；Apple 源码许可按文件审查 |
| MiCode kernel_devicetree | 43b11af42a275b9415634f4d196579938820896d | enuma 厂商 DT 候选；本地根目录无 LICENSE，暂仅引用事实 |
| MiCode Xiaomi_Kernel_OpenSource | 52a2f180865f8368828985d6384130acd093fa93 | NT36523/Linux 时序参考；COPYING 和文件声明，不直接混入 BSD 驱动 |
| uefi-sheng | 329b473df1e53a3bfa64b2b39b79670c4c02279b | Kona/接线参考；上游根 LICENSE 为 BSD-2-Clause，组件按文件许可证。初次本地未见 LICENSE 是 sparse checkout 未展开，已核对修正 |
| Mu-Silicium | 42fe563791e51bf5500c2e470ed294ca0c94b97c | KonaPkg/alioth 候选；BSD-2-Clause，GPL 子目录另审 |

参考仓全部只读。没有复制整棵源码、生成镜像或修改 nuwa。远端只做读取，没有创建或推送 enuma 仓库。

Windows 使用 Python 3.11+（本轮为 `C:/Program Files/WorkBuddy/resources/vendor/python/python.exe`，系统 python 可能是 WindowsApps 占位符）：

```powershell
python -B scripts/audit_inputs.py
python -B scripts/plan_adt.py
python -B scripts/check_workspace.py
python -B -m unittest discover -s tests -v
python -B scripts/audit_reuse.py
```

`audit_inputs.py` 顺序读约 8.5 GB 系统 DMG；`check_workspace.py` 只复核来源固定点与已有摘要报告，不代替完整重算。

```powershell
wsl -d Ubuntu-22.04 -- python3 -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_reused_ufs.py --source /mnt/d/Code/PortingiOSLegacy/common/sources/UniXNU
```

## iPadOS donor

缓存 BuildManifest 唯一匹配 j120ap / ApChipID 0x8011 / ApBoardID 12 / Erase 身份（索引 0），对应 iPad7,1、17.7.11、21H461。Erase 仅为离线身份选择，没有执行恢复或擦除。

六个组件全量 SHA384 与 manifest 相等：KernelCache、DeviceTree、StaticTrustCache、Cryptex1,SystemTrustCache、OS、Cryptex1,SystemOS。两个 DMG 的 SHA256 同时与参考 board 相等。Apple 签名未校验，内容摘要不能独立证明缓存来源。

IPSW kernelcache 容器 SHA256 为 `13b97fa2c5ce97f04408dcc28c41fb6b0d60b9440065197879acf44b2572bf7b`。这不是 sheng prelink 的解压 Mach-O 哈希；本轮没有解压/预链接，roots、slide、入口地址未写入 board。

## 历史 FDT 与硬件差异

旧仓 `enuma/backups/android-root/20261021T124813939334Z/android-root-fdt.stdout`，941691 字节，SHA256 `643aa3ec450139d38f8cde9a94bca6d9e8e75e752cb7aa992685d34267434c62`。独立 dtc 反编译返回 0，但有原树 reg_format 等告警，不是无警告验证。解析得到 4613 节点，输出排除 chosen bootargs、serial 和唯一标识；DTB 原件不提交。

`plan_adt.py` 检查 `/soc` 的 cell 格式和 ranges 后才将 GIC reg 解释为物理地址，不对任意总线猜测转换。输出仅 JSON 计划，不产生 ADT 二进制。

| 项目 | enuma 历史事实 | 适配影响 |
| --- | --- | --- |
| CPU | affinity 0,0x100,…,0x700；PSCI smc | 可准备八核拓扑；不继承 cortex-a715 compatible |
| timer | 19.2 MHz | FDT 事实；EL1 timer/XNU 执行未验证 |
| GIC | D=0x17a00000，R=0x17a60000，stride=0x20000 | sheng 是 0x17100000 / 0x17180000 / 0x40000，三者均不可照抄 |
| UFS | HC=0x1d84000；PHY=0x1d87000，QMP v4 | HC 同地址不代表 PHY/GCC/ICE/SMMU 兼容 |
| GPU | qcom,chipid=0x06050002 | 不继承 A740 SQE/GMU/PM4；暂不启用 NativeAdreno |
| touch | SPI@0x990000，IRQ GPIO 39，`novatek_nt36523_k81_fw01.bin` | 与源码候选 `novatek_nt36523_fw01.bin` 不同，精确固件/绑定待核对 |

`/memory` 是 Android 树中的银行，不是 UEFI 可分配内存映射；没有求和后写进 board。窗口、内存基址、装载地址和 userdata LBA 保持未配置。

## 驱动复用与固件接线

- **Kona UEFI**：固定上游树有 KonaPkg 与 aliothPkg，未发现 enuma/elish 包。alioth 是同系列 SoC 参考，内存/面板/固件二进制不得照搬。uefi-enuma 需明确 vendor blobs 来源、内存表和恢复路径。
- **接线**：参考 sheng DSC 第107–115行的 UniXNU、UniXNUDxe、DarwinBoot、UniXNULib；FDF 第95–103行及 Include/DXE.inc 第49行确认实际装入。只加 DSC 而未进入固件卷不算完成。
- **UFS**：`NativeUfs/GccUfs.h` 第2–24行明确为 SM8550 GCC 常量；NativeUfs.cpp 引用 SmmuTakeover。复用协议与边界检查，另做 SM8250 时钟/PHY/ICE/stream-id 接口。初始配置关闭 NativeUfs。
- **touch**：固定 MiCode NT36523 文件有 SPI、IRQ、input_report 等 Linux 依赖；XNU 仍需 SPI、电源、事件上报和坐标映射。没有用空函数冒充驱动。
- **显示**：先核对 GOP 延续与 framebuffer，分辨率不等于 stride；sheng 的 artwork、面板与按钮策略须逐项调整。
- **ADT**：固定 sheng 源码的 ipad_identity 同时控制产品和安全属性；继承说明已按 D-004 修正。

复用文件 URL、提交、哈希和相关行见 `reports/reuse-source-audit.json`；这是来源审查，不是已移植驱动清单。

## 验证与剩余门槛

- 9 项 Python 测试通过：合法/逐字节截断 FDT，非法 token/offset，donor 版本/产品/板 ID/身份歧义/组件损坏/参考哈希不匹配。
- 真实 UniXNU defconfig 接口成功读取 enuma，example guard 拒绝本板。直接调用 guard，未调用 build/bootimg，避免上游路径变动误产出镜像。
- WSL clang14 的四组上游 helper 测试通过 ASan/UBSan：TransferPoll、RootDiagnostics、RootPublication、SmmuTakeover。纯内存 fake port，未映射 MMIO。首次 PIE 版某次运行失败且输出为空，直接重跑 RootPublication 成功；根因未确认。最终采用 non-PIE sanitizer 配置，见 `reports/ufs-host-check.json`。
- 完整 XNU 编译/链接、donor prelink、QEMU、UEFI 和 enuma 启动均未进行；board 保留 example=true。
- ADB 只读身份发现仅有 nuwa；用户选择「稍后接入，先继续离线适配」，本轮不再访问设备。

## 下一工作包

1. 离线准备 uefi-enuma Kona 包差异及 UniXNU/DarwinBoot DSC/FDF 接入；厂商输入须为 enuma。
2. 独立复现 10063.141.1 通用平台链接，不混入 nuwa 的 8796 补丁队列。
3. enuma 接入后只读比对 ROM、驱动绑定、FDT、内存、GPT；历史输入不代表当前状态。
4. 有可审查内存/装载方案后再提最小批准范围。修改 board 内存或生成诊断/固件镜像前遵守硬停；现在证据不足以要求批准具体窗口或镜像。
