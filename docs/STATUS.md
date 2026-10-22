# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前边界

**旧诊断第24项返回后单点ADB16.954秒，第32项32.917秒；新版d6900d2第28项31.877秒，均已恢复Android/root/分区摘要。长复位不认定命中返回门。正在用同一新版测第26项，尚不跨版本认定精确故障模块。**

最强延时边界仍为第8项：2/7/2秒ADB20.142/21.233/15.917秒，首对差1.091秒不认定，原2秒镜像复测后与7秒差5.316秒支持返回后门。第16/24项为短门单点，第32/28项为长复位单点；返回状态/GUID和完整调度仍未采集。没有GOP/UEFI map、菜单、DarwinBoot/XNU或触控运行证明。

本轮至此九次候选临时启动均自动恢复Android、root、boot_a/vendor_boot_a摘要；另一次第16项推送前身份校验中止，正常恢复核对后才重试。当前最后为新版第28项恢复后的Android。没有flash/erase/改槽，暂无人工待办。

## 新固件诊断

- 固件仓已推送 **d6900d29700a901e876702cfebea62570a1e9958**。原25迁移文件/六patch逐字节保留；新增补丁/头及helper以extensions.json单独锁定，设备源锁38项。
- 复用原计数、Mu计时和PSCI复位：stage13下detail point13返回任意状态、14加载返回、15入口前、16/17入口错误/非错误返回、18/19加载错误/非错误返回。可额外按完整GUID两半匹配。stage0仍不复位，stage12原门保留。
- 新DSC选项补丁只作用于out暂存原DSC；新增core补丁由官方backend应用/恢复。两类补丁真实基线重复应用回归通过。默认13新增插桩的第28项已启动，但长复位不能当作诊断门命中。
- 真实header的20组ASan/UBSan用例覆盖序号、状态类、GUID两半/NULL、stage0/12及无效点；40项Python通过，包括UUID端序、扩展篡改预写拒绝、重叠patch幂等。来源/旧board表/defconfig/example检查通过；ADT只刷新board摘要，DarwinBoot契约在WSL通过（Windows无clang，未把环境失败记作通过）。
- 新源CI run39807061433通过，日志PASS已回读并记录摘要；只检查公开源码。macOS通用4KiB XNU run39790786938历史成功不变，本轮未重跑，不是本板最终内核。

## 固定输入与产物

目标enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB。UniXNU仍5fdbd5d及21模块。512MiB请求、example=true、物理内存字段和所有 *_verified 标记不变。

最新完成第28项快照out/entry-probe/official-queue28-stage13-delay2/：FD15442416f8647a566e6bdc2f673d1bbabfcaf0d2bfaa11c27af3c83b2d59798c，镜像4f06b9fb5d19b142f423b54f286643edbb0e1e122b2642e35fed01975c66134f。102私有输入预检、81文件/33OEM PE-DEPEX字节、v3回读及Mu core补丁恢复通过。私有输入、标识、备份和镜像不入Git。

原3376c44第24/32项与新d6900d2第28项的FD和镜像分别保存在各快照及entry-device-tests，不混用运行证明。GetVar精确解析、五组完整校验及私有日志保留，第16项前的异常原因仍未知，未放宽身份或备份条件。

## 后续

1. 完成新版第26项，按同版相邻边界定位；必要时用GUID限定、加载返回/入口前及状态门，关键边界做2/7对照。
2. 取得真实GOP、UEFI map、BDS/Probe与菜单协议闭包；内存或验证标记的变化仍需审查。
3. 补齐ADT/NVRAM、板级archives/最终内核/donor prelink，做最小XNU入口，再推进基础平台与NT36523 IRQ/HID。A650后置，不继承SM8550参数。

按用户要求持续到需人工节点再停，无待批准或按键事项。设备上次b9e0a59与固件d6900d2已推送，本次设备接入状态见Git。

详见[DXE实测](operations/2026-10-22-dispatch-checkpoints.md)、固件docs/dispatch-details.md及enuma-dispatch-details-host报告。
