# GOP 查询与 Core 复位路径离线拆分

## 结论与定位边界

需要先恢复可靠的诊断返回基线，否则完整查询再次无返回仍无法定位。
不要求先证明全部根因才继续离线工作。本轮依用户要求只做源码拆分、主机测试、
完整固件构建与打包审计，不调用ADB/fastboot，不重新查询或启动设备。

250849f的19:45:38临时启动在75秒内未自动返回，人工恢复Android后19:48:15
核验完成/root/原摘要通过。此历史结论不变；不能从本次静态修订倒推它必然卡在
GOP服务或本地PSCI，完整查询和互补旧镜像都不重试。

新固件固定e2868342daee0c196942f1a5569526d3ecb80850，移除SimpleFb新增的
BaseLib/TimerLib/ResetSystemLib直接依赖，INF恢复原文件。查询函数不调用复位，
复用原DxeCore最终StartImage返回门、完整GUID过滤、Timer/PSCI和正常完成七秒兜底。
StageCheckpoint头本身未改；Core只扩展对阶段标记的精确匹配。

## 分阶段契约

| step | 新增执行内容 | 返回前临时资源处理 | 能证明的上限 |
| --- | --- | --- | --- |
| 0 | 安装GOP后直接返回标记，不调用审计函数 | 无新增查询分配 | 安装后能通过新标记通道回Core |
| 1 | LocateHandleBuffer，唯一句柄且匹配实际ImageHandle | FreePool句柄列表 | 枚举/列表校验/释放整体已返回 |
| 2 | 在1后HandleProtocol，匹配实际SimpleFb实例 | 同上 | 实际协议实例检查已返回 |
| 3 | 在2后检查Mode/Info/单模式/BGRX/非零几何/stride/跨度 | 同上 | 元数据内部一致性 |
| 4 | 在3后QueryMode、比较所有定义字段 | FreePool查询信息和句柄列表 | 当前模式与QueryMode一致 |

各阶段累计执行，任一错误走统一清理并编码为失败标记。FreePool错误也归失败。
step1/2暂不能区分服务调用本身与列表释放的卡点；若它们成为故障边界再拆。
Mode几何来自当前PCD构造，不是实际scanout采集。全程没有Blt、SetMode、
帧缓冲物理地址解引用、MMIO写入或新物理保留区。

## 返回值通道及安全性

`EnumaGopResult.h`将阶段通过/错误编码成非错误EFI_STATUS 1/5（标准warning值，
这里只作私有诊断标记，不代表glyph或stale-data问题）。安装之前的错误仍走原清理、
原错误返回，不转为标记。安装成功后的审计错误不返回EFI_ERROR，避免卸载已发布函数的驱动。

固定Mu真实实现已核对：

- UefiDriverEntryPoint/DriverEntryPoint.c的_ModuleEntryPoint原样返回模块状态，
  只有EFI_ERROR才调析构；实际AutoGen单入口直接返回RegisterFrameBuffer结果。
- Image.c的CoreExit为已启动的当前映像复制`Image->Status = Status`，本路径无ExitData。
- CoreStartImage尾部先保存Status，只有EFI_ERROR或application才卸载；warning驱动保留。
- Dispatcher已有point13在CoreStartImage之后读取该Status，原point16位置用于匹配标记。

Core仅在启用查询配置、Point13/detail16、完整SimpleFb GUID匹配且Status等于
选择器1/2对应的通过/错误标记时调用已有两秒门。普通EFI_SUCCESS、其他warning、
错误、加载前/直接PE返回等位置不能冒充匹配。禁绘制/Probe早退和原七秒完成兜底保持。
兜底不是异步看门狗；任何阶段服务卡死仍可能需要人工恢复。

## 复用评估

继续复用现有alioth/Mu SimpleFb主体、已修契约和本仓实测过的Core门，不换整套驱动。
重新核对缓存elish/SM8250 SimpleFb（edk2-porting/edk2-msm
e1952621f419f8db60ed28271264e1b5184c571d，原审计E5），文件SHA与已锁报告一致。
其提供者安装协议后返回，不在提供者中加入诊断复位，可借鉴职责分离；
它还清空物理帧缓冲并clean cache，且使用另一套PCD，不能照搬这些操作来修enuma。
该来源没有可直接解释本次无返回的运行证据。旧审计来源和许可见
[SimpleFb同SoC审计](2026-10-23-simplefb-gop-offline-audit.md)。

## 验证与产物

137组真实Mu头/ASan/UBSan阶段和参数用例，覆盖各阶段不调用后续服务、故障清理、
跨度溢出及QueryMode字段差异；AArch64对象只导入GOP GUID。
组合实际SimpleFb补丁提取安装后代码，30组step/selector/状态验证标记，不调用本地复位。
从SHA固定Mu归档提取真实_ModuleEntryPoint和CoreStartImage返回段，六组warning/error/
application用例验证标记保留与卸载条件；另有七组不安全CLI配置拒绝。
Core矩阵保留原用例并增加1/5标记、错误GUID、NULL、非目标hook、其他warning检查。
结果见[查询主机报告](../../reports/enuma-gop-audit-host.json)、
[Core主机报告](../../reports/enuma-dispatch-details-host.json)。这些均不是实机证明。

构建默认关闭新增step。两个最小候选仅ENUMA_DIAG_GOP_STEP不同：0安装后对照、
1枚举+释放；其余stage13/detail16/delay2/selector1/完整GUID/兜底/OEM集合相同。
完整构建额外检查AutoGen无新增PSCI构造器、SimpleFb静态库清单无reset库、INF与基线相同。
`scripts/check_gop_split_bundle.py`再核对固定输入、FD与镜像SHA、v3镜像实际嵌入的FD、
两配置唯一差异和同SoC参考缓存摘要；不调用设备。配置见`config/gop-split-probes.json`。
实际构建结果见本文末尾完成记录和候选审计；未记载的步骤仍未验证。

可复现的固件命令：

```text
scripts/build_enuma_firmware.py --reference /mnt/d/Code/PortingiOS/common/sources/mu-nuwa-firmware --unixnu /mnt/d/Code/UniXNU-enuma/out/sources/UniXNU --stop-stage 13 --stop-delay 2 --dispatch-ordinal 1 --detail-point 16 --dispatch-guid dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92 --dispatch-guid-only --dispatch-completion-fallback --diagnostic-simplefb --diagnostic-gop-query 1 --diagnostic-gop-step 0 --jobs 8
```

step1只改`--diagnostic-gop-step 1`。构建与workspace qualification必须串行。
CLI未指定step时默认为最小step0，不再隐式执行完整查询；新固件及报告标明core-warning-v2，
不与250849f旧语义/旧候选混用。step2/3/4有主机及对象覆盖，尚未单独全链接打包。

## 下一轮实机条件

当前保持离线。未来收到实机执行指令后重新核对身份/原备份/摘要/解锁/槽位和恢复条件，
只先测试step0；没有受控返回就停追加并恢复，不用step1“试试看”。
step0返回证据成立后再考虑step1，依用户偏好无屏幕日志时不用持续录像，保留主机日志、
摘要、时序和必要截图；实际画面或按键需要判读时录像。
短返回结合对照支持选中阶段通过；长返回不能单独证明阶段错误，也可能是未命中标记/完成兜底。
若需要分类再独立构建同step的selector2，不复用旧失败镜像。不称数值GOP快照、像素/菜单或XNU通过。

51MiB DXE heap、512MiB owned、R-002地址范围、example与所有verified不变；无新审批项。

## 本轮完成记录

Core实际177组全部通过（口头193曾计数错误，已更正）；137/30/6/7主机与四份目标对象检查通过。
两候选全链接/30OEM/FD/BootShim/v3通过，已保存各自AutoGen/静态库清单并匹配构建报告摘要。
归档文件为各候选目录下的SimpleFb.AutoGen.c和SimpleFb.static_library_files.lst，来自完整构建模块的DEBUG/AutoGen.c及OUTPUT/static_library_files.lst；保存前核对构建报告中的摘要。
候选审计复核源/唯一宏差异、归档FD、镜像中实际嵌入FD及v3头/摘要通过；串行workspace通过。
`tests/test_gop_split_bundle.py`四组负向检查通过：错误固件版本、旧状态传输方式、额外宏差异、内存中篡改镜像均被拒绝；未改动原产物，未调用设备。
未做实机操作，原超时根因未定。详细摘要和路径以reports/enuma-gop-core-split.json为准。
