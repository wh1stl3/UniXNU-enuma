# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前结论

**已支持到达首个实际调度项的 CoreStartImage 返回后检查点。stage13/ordinal1 的 2/7/2 秒实测 ADB 恢复为15.903/22.308/16.939秒；7秒与复测2秒差5.369秒，符合设定5秒差值。返回状态和模块GUID未采集，不能说驱动初始化成功或整个DXE调度完成。**

新官方backend的stage12加载前基线也已临时启动，ADB16.986秒、Android完成30.151秒。四次测试全部自动恢复Android，启动完成、root与boot_a/vendor_boot_a摘要逐次核对不变；没有flash/erase/改槽。当前设备最后运行的是同一份stage13/ordinal1/2秒镜像复测后恢复的Android。

目标仍为enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB。512MiB请求、example=true、物理内存字段和所有 *_verified 标记不变。仍处官网阶段1 UEFI；没有GOP、UEFI map、菜单/FAT卷、DarwinBoot/XNU或NT36523运行证明。

## 构建与来源

- 双仓保持：设备firmware固定公开uefi-enuma **3376c4411e08442f45f4120ed6d96f2e302c51e8**，25原文件/六patch保持；33项摘要及gitlink互锁。UniXNU固定5fdbd5d及21模块。
- 继续复用真实unixnu.firmware.build、Mu加载/计时/PSCI复位；只通过临时defines选择诊断门。本轮无固件源码改动、无需新增固件提交或源码CI。
- 两个stage13完整固件均完成102输入预检、Mu core补丁恢复、81文件/33OEM PE-DEPEX字节审计及boot v3回读。当前构建报告是7秒变体，FD **1a6b17b0e3eb6bd34ef9d5128d31ee37c80aad3931e2bb7738f402395e2ee59b**，镜像 **a8cc8f442f39bf8b8ebe64a61253f4fadc42ad8d75918bdd5ee61af1cac1ec48**。
- 2秒FD **abc2c264b7f93d09121b198d5d582ca72b0d2697d8a6809ce577cacdc24453cb**，镜像 **d815d4d450c69679514b6cffb4cbf3749d0e222921723a1267aba4359ec5787c**，两次启动复用完全相同镜像。快照out/entry-probe/official-queue1-stage13-delay{2,7}/；新旧FD证据不混用。
- 本轮来源锁、全部旧board表不变、donor身份、defconfig与example保护检查通过。此前33项Python和共享门sanitizer通过，本轮无代码变化未重复整套测试。
- 固件源码Actions run39796926508通过；macOS通用4KiB XNU最终链接/审计run39790786938通过，产物de5ccd24…，仍不是enuma最终内核或donor prelink。本轮未重跑这两项CI。

## 未闭合边界与下一步

stage11调度后门的2/7秒差仍仅0.005秒，不能认定CoreDispatcher返回。新实测支持越过首项StartImage，但不识别首项GUID、不采集其EFI_STATUS、不证明协议安装成功，也不能认定第二项就是故障模块。计时含USB/Android延迟，2秒镜像两次ADB出现相差1.036秒；全部样本保留。

1. 依次用stage12/13的ordinal2及后续实际队列边界定位首次未返回项，必要时增加GUID/加载状态诊断；保留延时对照。
2. 获取GOP、真实UEFI map、BDS/Probe与菜单协议闭包，再审查新内存值或验证标记。
3. 补齐ADT/NVRAM、真实板级archives/最终内核/donor prelink，推进基础平台与NT36523 IRQ/HID。A650后置，不继承SM8550参数。

远端：https://github.com/wh1stl3/UniXNU-enuma 与 https://github.com/wh1stl3/uefi-enuma。此前设备7d6e23e与固件3376c44已推送，本轮实测里程碑发布状态见Git。无新增待批准硬停或待按键事项。

详情：[DXE实测](operations/2026-10-22-dispatch-checkpoints.md)、[双仓接入](operations/2026-10-22-uefi-repository.md)。
