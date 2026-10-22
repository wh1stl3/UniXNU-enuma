# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前边界

**第8个实际队列项的CoreStartImage返回后门已有2/7/2秒对照支持；第16项单点测试亦在16.953秒恢复ADB。正在构建第32项探针，继续扩大/回查边界，尚未观察整个CoreDispatcher完成、GOP或UEFI map。**

第8项ADB20.142/21.233/15.917秒：初对照差1.091秒不认定，原2秒镜像复测与7秒差5.316秒支持门命中。保留全部样本，不采集到EFI_STATUS/GUID就不认定初始化成功。第2/4项单点ADB15.938/16.944秒，第16项16.953秒，后者尚无独立延时对照。stage11整个调度后2/7秒差0.005秒的反例仍有效。

本轮至此六次候选临时启动全部自动恢复Android/root/boot_a与vendor_boot_a摘要，另有一次推送前身份查询中止，不计作启动；中止后正常重启并核对恢复，再重试同一第16项镜像。当前最后为第16项2秒探针恢复后的Android，启动完成、root与分区摘要不变。没有flash/erase/改槽。

## 本次工具修复

fastboot GetVar再次连续未返回完整product/current-slot/unlocked，五次完整组校验中止，未发boot。原因未知，未降低准入条件。解析改为要求恰好一个完整字段值，拒绝前缀匹配、重复/冲突值、FAILED及非零状态；每次完整查询日志只存out/，失败阶段显式记录。重试时首轮三字段通过，候选正常启动并恢复。

36项Python通过，包含三组实际身份解析回归。固件仍复用相同3376c44，无新增固件源码；各构建102输入预检、33OEM PE-DEPEX字节审计、boot v3回读与Mu core补丁恢复通过。

## 固定来源与限制

- 目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB。512MiB请求、example=true、物理内存字段及所有 *_verified 标记不变。
- 固件gitlink固定3376c4411e08442f45f4120ed6d96f2e302c51e8；UniXNU固定5fdbd5d及21模块。25原文件/六patch保留，来源锁不变。
- 最新完成的第16项构建快照out/entry-probe/official-queue16-stage13-delay2/，FD ebdb9017106c9f76790f4ac6a45bc9fe9176609493dce29d714478637444d2f0，候选647503568b075796af2a0944e0b4d25d195023707cec80887512048282481a59。首次仅身份查询中止，第二次才启动；不将两者混算。
- 第8项对照快照out/entry-probe/official-queue8-stage13-delay{2,7}/，样本/FD/镜像摘要在entry-device-tests。所有产物、备份、设备标识留out/。
- 固件源码Actions run39796926508通过；macOS通用4KiB XNU最终链接/审计run39790786938通过，仍不是enuma最终内核或donor prelink。本轮未重跑CI。

## 后续

1. 完成第32项测试；按真实队列扩大/回查，必要时补GUID和LoadImage状态诊断，关键边界用延时对照。
2. 获得GOP、真实UEFI map、BDS/Probe与菜单闭包。内存字段与验证标记的变更仍单独审查。
3. 补齐ADT/NVRAM、真实板级archives/最终内核/donor prelink后验证最小XNU入口，再推进基础平台与NT36523 IRQ/HID。A650后置，不继承SM8550参数。

按用户要求持续到需人工节点再停。目前无待批准项或待按键事项。设备上次里程碑e79a675与固件3376c44已推送，本次发布状态见Git。

详见[DXE实测](operations/2026-10-22-dispatch-checkpoints.md)、reports/enuma-fastboot-query-abort.json与enuma-fastboot-identity-tests.json。
