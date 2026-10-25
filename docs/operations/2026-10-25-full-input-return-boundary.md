# D-178：完整载荷的精确返回边界候选（离线，未上机）

S-001/S-002均无可判读报告且人工恢复核验通过后，停止重复整链黑屏尝试及盲调配置。当前没有第三笔设备启动；继续按用户恢复后自动分析/新软件规则，完成这一份必要定位候选。它是缺乏直接错误时的隔离工具，不把单点早停恢复为默认系统路线。

## 目的与解释边界

沿现有固定Core门，仅在DisplayDxe完整GUID 4138022f-06c7-4f79-9c94-7e33b511a4e7的CoreStartImage返回后，使用已存在2秒延时/ResetCold路径。**关闭completion fallback**，不允许派发完成后的7秒回退混淆目标门。point13表示任何CoreStartImage返回，不代表EFI_SUCCESS、PE入口执行、GOP模式或SetMode成功。

若观察到符合新门的受控返回，只能结合实际资格和其他复位来源评估为门命中的支持；不能单靠耗时唯一认定。如果无返回，仍可能尚未到目标、LoadImage提前失败、StartImage内部未返回或复位路径失败，不能写成“已证明DisplayDxe挂死”。旧R-016/空ramdisk A的观察不能直接覆盖当前完整载荷交接。

候选保留相同96MiB真实FAT及当前display-thread=0策略，RAM运输/13项报告仍编入，未换成空ramdisk。若目标门命中会在BDS/SFS检查前复位，因此这笔本来就不能验证全部13项；其用途是为下一处实修取得边界证据。

## 实际产物

- 固件源码仍cb9e56866aeff2985a06b4b39cb8ec2390b2985a，UniXNU仍5fdbd5d；无新固件源码/内存字段或verified变化。
- boot-v3：out/full-boot/transport/enuma-display-return-full-input-v3.img，103817216字节，SHA256 **d716e159d6852b398d1b8a999b17852c4affd8318123cbd61e8afe27047f8304**。
- FD：50bba978359f56b9d1c55bcb83fc5d545879127f4feaf82da2d15e734a2bc815。
- 资格归档：out/full-boot/transport/return-boundary-cb9e568，含实际Core PE/map/编译命令、FD/raw/image、打包和清单；拒绝覆盖。
- FAT仍49b4d6229e88180c338eb41a347f8ecf9572ba60c7efc476ccf4573936818773，100663296字节，经过AOSP打包/解包和严格整镜像回读检查。

相对S-002改变的是诊断编译配置：stage0→13、启用完整GUID/GUID-only及其两半值、detail13，fallback保持0；不是“只改point”。32个保留OEM PE/DEPEX仍逐字节一致，仅省略UFSDxe。源代码仍同一pin，不宣称其他所有编译PE只有Core发生差异。

## 实际Core审核与编译专门化

初次资格因找不到2,000,000微秒立即数拒绝，没有跳过检查。实际Core/map显示LTO在删除fallback后把唯一MicroSecondDelay调用专门化：该callee只有固定栈帧、两次以1,000,000,000纳秒为参数调用NanoSecondDelay（一次BL、末尾一次tail-B）。GUID半值比较仍精确，点13调用紧跟CoreStartImage返回。

审核器保留原显式微秒参数模式，新增只接受这个具体callee形状的模式：固定FP/LR栈保存恢复、精确两个1秒参数、精确NanoSecondDelay目标、第二次为最终tail-B、无其他分支或未知内存操作。没有把“找不到常量”视为通过。报告保留每条指令、RVA、map/PE摘要和delay_contract。

负例包括删StartImage调用、改GUID立即数、错point、改专门化纳秒参数；另有配置point/fallback/FAT混入拒绝，所有拒绝均未生成错误归档。旧A/B的原有GUID/调用点/PcdDxe debug-normalization负例也回归通过。这仍是静态/主机资格，不是实机计时校准或执行成功。

机器报告：enuma-full-input-return-boundary.json、enuma-full-input-return-core.json、enuma-full-input-return-negative.json。实际SEC TE值0也已复查；源/内存/原厂PE边界维持。

## 下一步入口与当前状态

相机wrapper增加显式资格参数；默认仍指向完整链报告，不能意外复用已消耗的S-002。新边界报告必须精确point13/正确GUID/完整FAT/fallback=false才可进入执行守卫。默认调用只离线核验，不触相机或设备：

```text
python scripts/run_system_transport_trial.py --qualification reports/enuma-full-input-return-boundary.json
```

未来在新文档已推送、即时设备/备份/相机/恢复门禁满足后，可沿用户现有授权加--execute执行一笔，无需再批准；仍会先相机再设备、消费镜像并禁止原样重试。当前**未调用--execute，没有第三笔boot**。不能把本轮离线资格写成实机返回门已命中。

最新实际设备结果仍是S-002人工恢复后14:31:50独立Android完成/root/A槽/解锁/原两分区摘要一致。S-001/S-002均consumed且失败记录保留；没有当前人工按键/审批待办。其他R-001/R-002/R-015及内存/verified/分区规则保持。

## D-179执行前状态（2026-10-25 15:21，Asia/Shanghai）

用户继续授权；15:21:02只读核验enuma Android完成/root/A槽/解锁、boot_a与vendor_boot_a及本地备份摘要一致，相机1920x1080画面已人工判读为Android桌面，原图及90度旋转保留。d716e159…47f8304不可变完整输入候选离线复核通过，尚未发出。本轮在文档提交推送后直接执行一次point13精确DisplayDxe返回门，fallback关闭；相机先于设备，75秒观察期限，异常先恢复且不原样重试。无新增内存/verified/分区操作。当前无人工或审批待办，运行中状态以out/device-tests/current.local.json为准。

