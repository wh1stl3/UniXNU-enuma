# UFS入口边界与GOP隔离

2026-10-23 Asia/Shanghai。A-002/A-004范围内的临时启动，未flash/erase/改槽，所有已完成测试均自动回Android/root/分区摘要不变。没有改变内存字段或验证标记。

## 实机边界

| 变体 | 本地发出时间 | ADB/秒 | Android/秒 | 说明 |
| --- | --- | ---: | ---: | --- |
| official-queue26-stage13-delay2 | 2026-10-22 23:48:52 | 16.965 | 31.118 | d6900d2，第26项短门 |
| official-queue27-stage13-delay2 | 2026-10-22 23:53:14 | 31.886 | 45.947 | d6900d2，第27项返回后长复位，不认定返回 |
| official-queue27-stage13-delay7-point15-guid0d35cd8e | 2026-10-22 23:57:35 | 22.311 | 34.432 | d6900d2，完整UFS GUID入口前7秒 |
| official-queue27-stage13-delay2-point15-guid0d35cd8e | 2026-10-23 00:01:58 | 16.954 | 31.505 | 同一控制点2秒，形成5.357秒对照 |
| metronome-queue28-stage13-delay2-guid0d35cd8e | 2026-10-23 00:06:53 | 30.841 | 45.518 | 281179c，真实Metronome提前，UFS返回后仍长复位 |
| isolate-queue1-stage11-delay2-no-ufs | 2026-10-23 00:15:25 | 31.879 | 45.744 | b988fa4，明确排除UFSDxe，整个调度后仍长复位 |
| isolate-queue32-stage13-delay7-point15-guid4138022f-no-ufs | 2026-10-23 00:22:00 | 22.299 | 36.573 | b988fa4，排除UFS，完整Display GUID入口前7秒；尚无该点独立2秒对照 |

UFS文件GUID为0d35cd8e-97ea-4f9a-96af-0f0d89f76567，原实际队列27，入口前7/2秒ADB22.311/16.954秒，差5.357秒，支持加载成功且到达CoreStartImage前。返回后门未观察到命中；不能区分驱动构造器/主体、具体内部故障或复位来源，不把长复位叫作驱动返回成功。

Metronome插入后UFS序号28。原厂84项APRIORI确有Metronome早于UFS，Mu CoreStall在缺该协议时返回NOT_AVAILABLE_YET；已有真实Mu模块提前后，UFS返回后仍30.841秒，因此这个服务顺序修正未解决UFS边界，不认定其为根因。原APRIORI/旧25文件/六patch都以暂存扩展形式保留，所有原INF相对顺序不变。

## 显式隔离配置

默认board中ENUMA_DIAG_DISABLE_UFS=0，保持全部33OEM模块。包装器--diagnostic-without-ufs只在当前诊断变体设置1，从Components/FDF/APRIORI三处排除UFSDxe，不提供空协议或替代驱动。构建报告必须声明唯一缺项，审计要求匹配的完成FD摘要，实际UFS文件及APRIORI GUID必须均不存在，其他32OEM PE/DEPEX逐字节匹配。普通33模块FD与伪造缺项声明的负向实测也通过；42项Python覆盖防止扩大遗漏或错配摘要。

隔离模式整个调度后门仍31.879秒，说明还有后续未闭合路径。DisplayDxe GUID4138022f-06c7-4f79-9c94-7e33b511a4e7，实际队列32，入口前7秒探针ADB22.299秒、Android36.573秒，支持走到显示入口前，但尚无独立2/7对照。正在测试同GUID的入口返回后门。此模式不是存储或完整平台通过，也未证明GOP协议存在。

两个隔离FD均80文件/32原厂模块字节匹配、APRIORI无悬空引用、boot v3回读与core补丁恢复通过。源锁42项固定b988fa4，默认完整模式未被改成缺UFS。

## 日志与复位原因

第26项短门和第27项长复位后的Android属性都为bootloader，PMIC SID0记录Hard Reset/cold与PS_HOLD，次级PMIC为SOFT，不能据此区分复位来源或归因看门狗。完整内核消息只在out/，公开报告保留摘要及比较。

只读检查确认/dev/mem、/dev/kmem、/proc/kcore不可用，CONFIG_DEVMEM/PROC_KCORE未启用，live FDT无ramoops节点。CONFIG_MODULES/MODVERSIONS/IKHEADERS开启，MODULE_SIG关闭；已只读取回实际内核头文件，尚未构建/加载回读模块或写RAM标记，不把可行性当日志回读成功。内核头/配置/设备标识不发布。二进制读取使用adb exec-out，首次shell传输的gzip损坏不当作源配置问题。

## 复现与证据

```powershell
# 所有实际构建仍经官方backend；先预检、审计、独立v3回读，后临时启动。
wsl -d Ubuntu-22.04 -- /mnt/d/Code/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/UniXNU-enuma/scripts/audit_oem_apriori.py
# 当前GOP隔离模式，不代表完整固件：
wsl -d Ubuntu-22.04 -- /mnt/d/Code/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/UniXNU-enuma/scripts/build_enuma_firmware.py --reference /mnt/d/Code/PortingiOS/common/sources/mu-nuwa-firmware --unixnu /mnt/d/Code/UniXNU-enuma/out/sources/UniXNU --stop-stage 13 --dispatch-ordinal 32 --dispatch-guid 4138022f-06c7-4f79-9c94-7e33b511a4e7 --diagnostic-without-ufs
```

精确FD/镜像/源提交见entry-device-tests各variant；快照out/entry-probe/<variant>/包含FD、构建/预检/审计/payload和日志。来源CI281179c/run39810564733及b988fa4/run39811887053均回读PASS，未跑新的macOS内核CI。静态原厂顺序与三份固定Mu服务源码摘要见enuma-oem-apriori-gap-audit，缺项审计负向证据见enuma-firmware-omission-policy-check。

## Display复测与当前审批边界

相同GUID返回后2秒探针00:29:23发出，ADB30.846秒/Android44.289秒，未观察到返回门。入口前2秒00:35:05发出，ADB15.913秒/Android30.600秒；重复相同2秒镜像00:40:22发出，ADB15.970秒/Android29.173秒；重复相同7秒镜像00:42:07发出，ADB21.247秒/Android36.259秒。初始差6.386秒没有当精确5秒；保留全部7/2/2/7样本，重复对照差5.277秒支持完整Display GUID入口调用前门。它仍不能证明已执行到厂商主体或GOP存在。

全部恢复核对通过。当前构建报告为前门2秒FD5212eb5f11e6de0a0d45475db7325103bae16bf0bdaa352d808ce274d173f725，最后设备复测使用已有7秒镜像54bb808e3147892d2f40c159f6dbe51b43774d345fe44721bd65629b4e23c4eb，分别保留，不把两份报告混算。

匹配实际内核页定义与4KiB配置读取8页标志，现有Log Buffer并非Linux保留页；FDT和iomem复算也一致。没有向这些页面写标记或读其内容。下一步软件日志需新增保留内存配置，按AGENTS列R-002等待选择；精确范围和外接UART备选见早期日志方案。当前无待按键事项，设备正常Android。
