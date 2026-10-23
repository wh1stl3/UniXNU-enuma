# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前必须先处理的停点

**enuma恢复未确认，实机工作已硬停。** source233a9d8的首个SimpleFb入口前2秒候选10:16:30被fastboot接受，但75秒未回目标ADB/fastboot；后续只读检查仍无端点。用户暂时无法按键。当前不能声称Android/root恢复或试后分区摘要正常，更不能声称SimpleFb/GOP/XNU成功。

没有flash/erase/改槽。最后一次已完整恢复的是09:58:57的7276dcd pool成功门7秒；它只是历史状态，不能当当前状态。具体步骤见[PENDING-HUMAN](PENDING-HUMAN.md)。按照AGENTS的实际恢复失败停点，不追加任何设备试验。

## 已从其他设备落地的部分

1. nuwa同Mu的真实pool搜索诊断：7276dcd成功门2/7 ADB16.108/21.478秒，差5.370；失败门31.129/32.248秒，未观察预期5秒响应。四次均恢复，不能据此断言零失败或堆不足，没有扩堆依据。
2. alioth/elish式独立SimpleFb：显式交换Display提供者，诊断仅排除CPR/Display/UFS，严格保留30本机OEM PE/DEPEX，默认原生33及无UFS32模式分别保留。真实Mu SimpleFb/FrameBufferBltLib已接通，不拷贝他板地址/二进制。
3. 补SimpleFb查找/模式/mask/分配/配置/安装错误传播、清理和64位溢出检查。诊断Blt禁用写像素；32位紧密布局仅元数据假设，实际scanout六项条件仍缺。

233a9d8实际AArch64固件、30OEM/FD/BootShim/v3审计与源码CI通过。首测只证明命令接受，未观察预期入口门。所用ordinal32来自旧布局，当前实际Dispatcher计数未校准；静态APRIORI位33不能替代它。更早停点/漏门/UEFI仍运行等均未排除。

## 当前源码与离线守卫

固件gitlink7479da1，49项源锁。发现EnumaProbe可绕过Blt直接DiagDraw后，已补诊断入口提前返回；新版本仅host/static/源码CI通过，未重建AArch64固件或启动。实际首测仍是233a9d8，不能把新守卫追溯到旧镜像，也不能宣称旧镜像绝无像素写入。

公共runner现在在上一轮manual-recovery-needed时拒绝新试验；私有SimpleFb编排只构建归档，不自动启动。48项Python、整份SimpleFb的host ASan/UBSan、Probe守卫宏0/1编译检查、选择/contract组合patch重复重放、49项workspace检查通过。源码CI39888162938（233）/39889743071（747）均回读PASS；源码CI不是固件/硬件证明。

详见[SimpleFb借鉴及首测交接](operations/2026-10-23-simplefb-metadata-variant.md)、[pool门](operations/2026-10-23-pool-search-gates.md)、[nuwa对照](operations/2026-10-23-nuwa-progress-reuse-audit.md)。

## 保持的边界与既有证据

51MiB DXE Heap与512MiB owned请求、原内存表/example/verified均未改。R-002精确范围保护/ABI/同次marker曾通过，但跨Bootloader不保留，持久日志路线仍停，不换址/扩大/借DFPS或SMEM。Native Display此前只有调用前及canary前缀存在门支持，直接返回/Exit后/默认异常门未观察；这些旧source结论不转移为新SimpleFb运行证据。

目标保持enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块。未进入XNU，未验证GOP可见、实时UEFI内存图、BDS或NT36523。默认完整33模式未在新source重建。

## 下一步

先等实体按键回FASTBOOT或Android，沿既有授权恢复并核对身份/完成1/root/原分区摘要。恢复前不再设备试验。随后只离线审计实际分派序号或GUID-only选择，建立包括加载错误、驱动失败和意外BDS落入在内的可观察有界返回，再准备后续实测；不直接重复本候选。生成镜像无需一般确认，但当前恢复失败的硬停有效。TWRP未测试，无新内存/verified审批请求。

设备上一里程碑e4a40fb已推送；本轮以Git/WORKLOG发布记录为准，参考仓保持只读。
