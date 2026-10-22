# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见 WORKLOG。

## 当前结论与停点

**R-002 已批准；临时 Android FDT 的 32 KiB 日志候选保留已实机通过。按用户“做完这笔实机验证就停下，写好文档”要求，本轮已停止，不再启动镜像或加载模块。设备在 Android，启动完成、root、boot/vendor_boot 原摘要正常，无待按键事项。**

这次证明的是当前诊断 Android 启动保护了 `[0x9fff7000, 0x9ffff000)`，不是持久日志可用。未加载内核模块、未读取物理日志内容、未写标记、未验证跨复位存活，也未设置任何 `*_verified=true`。

## R-002 本轮结果

- board 新增独立 diagnostics.persistent_log，默认 enabled=false，physical_base=0x9fff7000、size=0x8000。来源是本机 OEM Log Buffer，不是运行中 UEFI GetMap。严格检查只允许这组字段；既有内存表、512 MiB owned 请求、example=true、验证标记保持不变。
- 复用原厂 ARM64 Image 与 v3 boot/ramdisk、固定 AOSP 解包器；只改 Image 第一条分支及 image_size，并追加入口封装/临时栈；原厂 vendor_boot 保留。入口在原 FDT 缓冲区内加入唯一保留项，不增大 FDT，不改属性值或随机种子。输入不满足空间/结构要求则不修改，继续原厂入口，主机侧门禁会拒绝后续回读。
- 第一次 01:00:21 临时启动恢复 Android，但 FDT 与原样本一致，8 页仍非 reserved；作为失败样本保留。不能据此认定入口未执行或 Bootloader 清空日志。旧实现依赖运行中 FDT 的 NOP；该 NOP 位于 chosen，固定 MiCode 源码会在读取 rng-seed 后生成 NOP，这是入口前/运行后布局差异的合理解释，未直接观测入口前 FDT。
- 第二次 01:04:27，采用 NOP 不足时复用相同名称后缀的修复，镜像 SHA256 e0bd9b25d6e472a52735893dac970bb6f475e6c5394e6d878c615e54d6fc0e42。ADB 16.079 秒、启动完成 31.722 秒；实际 FDT 唯一 reserve tuple 为 0x9fff7000/0x8000，8 页标志全部 0x100000000（KPF_RESERVED）。与原 Android FDT 比较，所有节点/属性值相同。恢复核对正常，无 flash/erase/改槽。
- 实际内核头、原厂 rdbg/wifi 模块核对后，离线 ABI 探针编译成功：实际 release/vermagic 一致、struct module 832 字节、module_layout/printk CRC 精确匹配。**未 insmod，因此仍不是运行时 ABI 通过。** 16 字节只读 marker 模式仅有源码，未构建/执行。
- 45 项 Python、实际 C 的 21 组 ASan/UBSan、原 board/固件来源/defconfig/example 检查通过；临时镜像经固定 AOSP 解包逐字节回读。真实 marker、固件日志、异常采集未启用。

**临时保留只在本次诊断 Android 启动有效；普通 Android 重启后可能恢复普通 RAM，未来模块加载/回读前必须重新采集活动 FDT 与 8 页状态，不能沿用旧报告。**

## 主线与固定来源

- 完整 GUID 与延时对照支持到达 UFSDxe 和 UFS 隔离模式下 DisplayDxe 的 CoreStartImage 调用前；返回后门均未观察到。公共包装器、库构造器、驱动主体和复位来源尚不能区分归因。
- UFS 前门 7/2 秒差 5.357 秒；提前真实 Metronome 未解决 UFS。隔离 Display 前门四样本 7/2/2/7，重复差 5.277 秒，返回后仍长复位。不代表驱动主体/GOP/完整调度成功。
- 尚无 GOP/UEFI map、菜单、DarwinBoot/XNU 或 NT36523 运行证明。
- 固件仓/gitlink 仍 b988fa418de55de2dcaa396d016e30231159d1fe，42 项源锁、原 25 迁移文件/六 patch 不变。默认保留 33 OEM；显式无 UFS 变体保留其余 32 OEM 字节，不能代替完整存储验证。本轮未改固件仓或重建 UEFI，也未运行 macOS CI。
- 目标 enuma/SM8250，iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB，UniXNU5fdbd5d/21 模块不变。历史 macOS 通用 4KiB 内核成功不是本板最终内核。

## 恢复工作后的顺序（本轮不执行）

1. 重新核对 enuma 身份、恢复备份、活动 FDT、8 页保护与完整内核 ABI，正常加载/卸载无物理访问的 ABI 探针；不得强载。
2. 构建并审计 16 字节只读回读模块，设计不会经过未保留 Linux 启动的最小标记/复位/回读链，先证明存活。若 ABI/临时启动契约不满足或候选被 Bootloader 清空，按 R-002 停下，不换地址或刷分区。
3. 存活与回读都成功后才接同范围有界 SEC/DXE 日志，定位 UFS/Display，再验证 GOP/map/BDS，最后推进 ADT/NVRAM、板级最终内核/prelink 和最小 XNU 入口。

本里程碑记录见 Git；上次设备提交 73f34e5 已推送。本轮证据与可复现命令见 [R-002 实测交接](operations/2026-10-23-log-reservation-validation.md)；总报告为 reports/enuma-log-reservation-device.json。
