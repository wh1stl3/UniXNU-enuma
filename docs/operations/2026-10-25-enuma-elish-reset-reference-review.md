# D-222：enuma / elish 同型仓复位与日志路线复审

2026-10-25，用户要求参考同机型及Wi-Fi版elish。范围仅公开源码研究和文档，无新设备命令、构建、映射、写入或启动。S-018硬停与已核验Android恢复保持。

结论：没有找到这些enuma/elish仓库已闭合本机PSCI warm留存的证据。真正值得转向的是它们引用的**板级PMIC PON/SPMI/PS_HOLD复位，配合提前读取pstore的临时Linux**。这不同于本仓S-018的通用PSCI_FEATURES→SYSTEM_RESET2路径；不能继续将函数名ResetWarm当作保留RAM的资格。

## 固定来源及证据等级

| 来源 | 固定提交 | 本轮核对结论 |
| --- | --- | --- |
| Tlrenhb/uefi-enuma | 70ba7ba3367d1083822fbe3cb86177ec3d7224c2 | 有pipa来源的RamoopsLogLib及PMIC复位实现，但代码显式TODO(enuma)，需核PON/arbiter与返回fastboot；不是本机已验证闭环 |
| Tlrenhb/UniXNU-enuma | 606a99279bb8fc59207fe653585004bc0efb6cd0 | 固件迭代脚本仍有reader移植TODO，不能用脚本存在当读回成功 |
| hpadmx/UniXNU-elish | a357eae98a0da0796c8efec8519825367da1e3e7 | README明确缺UEFI侧与固定构建树，不能直接生成可烧写产物；未发现专用复位留存闭环 |
| edk2-porting/edk2-msm | e1952621f419f8db60ed28271264e1b5184c571d | elish实际DSC继承SM8250/common，提供FramebufferSerialPort或GENI UART，复位绑定ArmSmcPsciResetSystemLib |
| tianocore/edk2，按上项gitlink | e7aac7fc137e247edad22f7ee53b9a1fba227397 | 实际ResetWarm仍查询FEATURES并reset2/cold回退；没有elish板级PON替代，不构成该问题修复证据 |
| torvalds/linux v6.12 | adc218676eef25575469234709c2d87185ca223a | elish公共DTS有B0000000/4MiB ramoops，但record4096、console2MiB、ECC16，与本机原厂ECC0/record0/pmsg2MiB不等价 |
| xVanTuring/uefi-pipa | 1f6a1520f84c699a6f748e7b0b0ee72b79c7997b | PON复位类型、bootloader原因、SPMI权限、SCM与PS_HOLD组合，源码报告PMIC warm及reader留存；仅作对方报告，未独立复验 |
| xVanTuring/UniXNU-pipa | c28476ea5d3c66fb634152ea7cd0f5ddc7a63233 | 有独立init、RAM中FAT与只读USB导出、reader打包/主机读取脚本；绕开Android用户态消费者 |
| reAAAq/UniXNU-umi | 3eb72578597d2ca16471b172d45eddc096a34a04 | 之前只深入审了writer；这次补核其板级UmiResetSystemLib和UmiSpmiLib。源码记录PSCI SYSTEM_RESET挂死，转用PON/SCM/PS_HOLD；不是enuma实测 |

所有40份文件的URL、SHA256、Git blob及提交见`config/enuma-elish-reset-sources.lock.json`。运行`python -B scripts/audit_enuma_peer_reset_routes.py`验证9仓40文件的SHA256/Git blob及9组源码事实，报告`reports/enuma-elish-reset-route-review.json`。Windows同名大小写文件会覆盖，缓存因此按Git blob隔离，避免把PROVENANCE.md与provenance.md混为同一份。未执行第三方脚本、导入实现或变更任何现有依赖pin。

## 同机型实际做了什么

[enuma RamoopsLogLib](https://github.com/Tlrenhb/uefi-enuma/blob/70ba7ba3367d1083822fbe3cb86177ec3d7224c2/Platforms/Xiaomi/enumaPkg/Library/RamoopsLogLib/RamoopsLogLib.c)包含DBGC环及PrepareWarmFastboot。它通过SPMI识别arbiter/APID/EE所有权和PON类型，设置bootloader原因与PS_HOLD warm类型，还会改电源键/组合键的S2复位类型，再执行SCM和PS_HOLD。这是板级控制路径，并非PSCI reset2。

然而文件开头明确其为pipa复制且需enuma核验；[DSC](https://github.com/Tlrenhb/uefi-enuma/blob/70ba7ba3367d1083822fbe3cb86177ec3d7224c2/Platforms/Xiaomi/enumaPkg/enuma.dsc)对SerialPort/UmiResetSystemLib等仍标TODO。所审MemoryMapLib表也没有B0000000 console记录，不能推断日志写入在其MMU阶段已有资格。[设备脚本](https://github.com/Tlrenhb/UniXNU-enuma/blob/606a99279bb8fc59207fe653585004bc0efb6cd0/scripts/build-enuma-uefi.sh)仍要求移植reader。这些是具体可审的实现来源，尚非“同机型已解决”的运行证据。

## elish两条线不要混为一谈

[hpadmx README](https://github.com/hpadmx/UniXNU-elish/blob/a357eae98a0da0796c8efec8519825367da1e3e7/README.md)描述的是UniXNU准备状态。其旧文档对pipa“尚未上机”的说法不能用来否定当前pipa新增的日志测试报告；必须按各自固定快照与具体证据区分，不能将旧准备资料当最新硬件结论。

[edk2-msm elish DSC](https://github.com/edk2-porting/edk2-msm/blob/e1952621f419f8db60ed28271264e1b5184c571d/Platform/Xiaomi/sm8250/elish.dsc)继承SM8250配置。[common DSC](https://github.com/edk2-porting/edk2-msm/blob/e1952621f419f8db60ed28271264e1b5184c571d/Silicon/Qualcomm/QcomPkg/QcomCommonDsc.inc)默认可走FramebufferSerialPort，USE_UART时走GENI UART。FramebufferSerialPort直接使用PCD地址/几何绘字并有清屏行为；不是USB早期日志，也不能绕过本机R-005/R-007失败和扫描地址/格式未闭合的事实。UART还需确认本机引脚、时钟和物理接线。

该common绑定的[精确EDK复位源](https://github.com/tianocore/edk2/blob/e7aac7fc137e247edad22f7ee53b9a1fba227397/ArmPkg/Library/ArmSmcPsciResetSystemLib/ArmSmcPsciResetSystemLib.c)也有PSCI功能查询和reset2/cold回退，使用ArmSmc接口而非本仓ArmMonitor接口；不能据库名不同就认为能解决S-018，不能默认其warm在elish实际通过。

[elish Linux DTS](https://github.com/torvalds/linux/blob/adc218676eef25575469234709c2d87185ca223a/arch/arm64/boot/dts/qcom/sm8250-xiaomi-elish-common.dtsi)的ECC16/record4096配置不能给本机ECC0 writer套用。按ramoops先分配dump再console的算法推算，该DTS还可能使console偏移与本机console-at-base不同；这是布局推导，不是本机现场值。因此只借鉴“标准pstore读取端”和保留声明，实际格式/区域始终以当前enuma原厂参数为准。

## 完整可借鉴链：PMIC warm＋早期reader

[umi板级复位](https://github.com/reAAAq/UniXNU-umi/blob/3eb72578597d2ca16471b172d45eddc096a34a04/overlay/Platforms/Xiaomi/umiPkg/Library/UmiResetSystemLib/UmiResetSystem.c)在改PON前读取身份/状态与SCM能力，写后读回，处理SCM_INTERRUPTED和失败回滚；ResetWarm选择BoardReset(1)，并非SYSTEM_RESET2。对方代码中PSCI挂死的记录与本机“cold返回/warm未返回”方向相符，但umi连SYSTEM_RESET曾失败而本机cold已返回，不能把两机根因等同。优先复用其核验、超时和回滚方法，不复制地址/PMIC类型/SCM参数或更改本机长按恢复行为。

[pipa reader init](https://github.com/xVanTuring/UniXNU-pipa/blob/c28476ea5d3c66fb634152ea7cd0f5ddc7a63233/package/linux-log/init.c)的设计是早启动复制pstore到RAM内LOG.BIN，再以只读USB mass-storage导出；不等Android init/ADB，减少被清理的窗口。实际固定提交链接以源锁为准。[打包器](https://github.com/xVanTuring/UniXNU-pipa/blob/c28476ea5d3c66fb634152ea7cd0f5ddc7a63233/package/linux-log/build-log-reader.py)使用自己的stock kernel和vendor_boot DTB，按需要加入force-warm-reboot；当前实现生成v2并自行构造ramdisk和DTB，主机reader还使用macOS卷路径。这些都是移植条件，不能直接运行它控制enuma或替换本仓Boot v3。init还写pmsg/kmsg测试标记，不属于本仓现有“不碰pmsg”范围；移植首版应移除该自测试写入。

## 结合本机结果的下一步排序

1. **先审enuma原生复位链**：以本机保存的DT/固定小米msm-poweroff/qpnp-pon/scm为准，核PON代际/SID/外设、SPMI版本/EE/APID所有权、PS_HOLD/IMEM、SCM能力和长按恢复设置。先完成离线匹配，后续必要的读命令也要明确SPMI“读”会写命令MMIO，不能冒充纯物理只读。
2. **写入可达性与留存分开**：以已经返回的cold门审一个新的最小writer隔离候选；cold写入成功也不证明日志能跨复位保留。S-015/018全部consumed，不原样重试；本轮没有实现新候选。
3. **优先准备enuma早期reader**：复用本机stock kernel/准确ramoops布局，在独立临时启动中于Android用户态之前读取并只读导出RAM镜像。单独闭合本机Boot/FDT/USB/恢复边界，移除pmsg测试写入，不需要通过刷boot_a来获得读取端。是否跨fastboot保留仍须验证。
4. **再评估板级warm留存**：只有前置身份/SCM/映射与reader都闭合后，才提出可审的最小PON/SCM/PS_HOLD实施范围。原R-017仅console标记/映射及临时boot不自动授权新增PMIC控制或改长按行为；本轮研究不请求实施批准，也不执行该路径。

这次公开仓复审将“继续调通用PSCI warm”降为次要路线；主判断改为先审查原生板级复位与早期读取器的完整链。可推翻条件包括：本机证明只修复通用SMC传参就能稳定留存，或原生PON/SCM条件与参考机不相容。暂不声称任何路线已在enuma通日志、点屏或启动XNU。
