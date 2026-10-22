# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相；历史见 WORKLOG。

## 当前结论

**首轮离线适配已落地；尚未构建或启动 enuma 的 XNU/UEFI。** 独立设备仓沿用 nuwa 的提交、五件套与四类硬停规则。用户已确认 iPadOS 17.7.11；目标为 iPad7,1 / j120ap / 21H461、XNU 10063.141.1、4 KiB。

## 已完成

- board.toml、候选 enuma_defconfig、固定源码锁建立；真实 UniXNU defconfig 接口通过，example=true 保护仍有效。
- 六组件全量摘要与 BuildManifest 相等，两个 DMG 同时匹配 sheng 哈希；Apple 签名和 prelink 未验证。
- 历史 FDT 4613 节点解析、dtc 反编译与 GIC/PSCI/timer/八核 ADT 输入计划完成；内存/基址未写入 board。
- 固定 Kona/alioth、MiCode NT36523 真实来源，记录许可、哈希和差异。
- 9 项输入审计测试通过；四组 UFS 通用逻辑在 WSL non-PIE ASan/UBSan 下通过，仅主机侧验证。

复现命令、失败记录与证据见 [离线报告](operations/2026-10-22-offline-bringup.md) 和 reports/。

## 下一步

1. 离线准备 uefi-enuma Kona 适配及 UniXNU/DarwinBoot 固件卷接入，核对 enuma 厂商输入。
2. 独立复现 10063.141.1 通用内核构建/平台链接，不能用 nuwa 的 8796 队列。
3. 用户稍后接入 enuma 后只读核对 ROM、FDT、内存、驱动绑定、GPT；本轮按用户选择继续离线。
4. 有具体内存/镜像方案后再审查；当前缺 UEFI 内存图、GOP 交接和 SM8250 UFS/电源/SMMU 证据。

## 边界与已知坑

- enuma 历史 GIC stride=0x20000，不能照抄 sheng 的 0x40000；UFS HC 同地址不代表 PHY/GCC 兼容。
- 历史 touch 固件名含 _k81_，不同于 MiCode 候选；实际绑定待确认。
- ipad_identity 在固定 sheng 源码中同时控制产品和安全属性，D-004 已修正继承说明。
- XNU 完整构建、UEFI、prelink、QEMU、实机及 iPadOS GUI 均未验收；未生成新诊断/固件镜像，未设置任何 *_verified=true。
- 参考仓只读。远端仅查询；本仓当前仅本地 main 提交，未建立/推送远端。
