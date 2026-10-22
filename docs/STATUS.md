# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前结论与停点

**完整GUID与延时对照支持到达UFSDxe、UFS隔离模式下DisplayDxe的CoreStartImage调用前；两者的返回后门均未观察到命中。正在等待R-002的新日志内存配置审查，不再启动新测试。设备已恢复Android，root和boot/vendor_boot摘要不变，无待按键事项。**

- 原d6900d2实际队列27，UFSDxe GUID0d35cd8e-97ea-4f9a-96af-0f0d89f76567，入口前7/2秒ADB22.311/16.954秒，差5.357秒。加载成功、到达入口调用前获得支持；不能确认已跳入驱动主体或具体故障。
- 281179c提前真实Mu Metronome后UFS变成28，返回后门仍30.841秒，未解决UFS边界。
- b988fa4显式排除UFS后，整个调度后门仍31.879秒。实际队列32、完整DisplayDxe GUID4138022f-06c7-4f79-9c94-7e33b511a4e7，入口前7/2/2/7秒ADB22.299/15.913/15.970/21.247秒；全部样本保留，重复对照差5.277秒支持该门。返回后门30.846秒，不当作返回证明。
- 尚无GOP/UEFI map、菜单、DarwinBoot/XNU或NT36523运行证明。公共CoreStartImage包装器、库构造器、驱动主体和复位来源仍不能互相替代归因。

本轮从第2项起累计20次实际临时启动全部恢复Android/root/分区摘要，另一次第16项推送前GetVar中止，正常恢复后才重试。最后测试为相同Display入口前7秒镜像复测（00:42:07），ADB21.247秒、Android36.259秒。没有flash/erase/改槽。

## R-002：实际日志内存保护缺口

OEM Log Buffer为0x9fff7000/0x8000（32KiB），只是本机OEM来源事实，未以运行中GetMap确认。当前Android FDT的/memory覆盖该区，无reserved-memory或头部reserve条目保护；/proc/iomem归入System RAM，实际4KiB内核的8页KPF_RESERVED全部false，已有普通LRU/映射/buddy页。因此不能直接写作持久日志。

推荐有界软件路线：申请独立诊断配置，只允许同一32KiB范围、临时Android FDT保留、匹配内核ABI的只读回读及最小标记存活试验，成功后再接日志。Bootloader可能清空，失败不得自行换地址或扩大。备选是核对UART接点/电平后人工连接。精确提案及范围见NEED-REVIEW/R-002和docs/proposals/R-002-board-config.patch，未应用。

Android未启用DEVMEM/PROC_KCORE；MODULES/MODVERSIONS/IKHEADERS可用、MODULE_SIG未启用，已只读取回匹配头文件。没有构建/加载回读模块、物理内存内容读取、RAM标记或FDT保留变更。AGENTS的新增内存大小/基址字段审查规则要求先确认；A-002镜像授权保留，512MiB不变。

## 已实现与验证

- 固件仓公开main/设备gitlink固定 **b988fa418de55de2dcaa396d016e30231159d1fe**，源锁42项。原25迁移文件与六patch保留，通过独立extensions增加detail、Metronome和UFS选择补丁，仅写out暂存。
- 默认ENUMA_DIAG_DISABLE_UFS=0保留33OEM。--diagnostic-without-ufs明确从Components/FDF/APRIORI三处排除UFSDxe，无空协议。报告必须有唯一缺项及匹配完成FD，审计检查文件和APRIORI GUID均不存在，其余32PE/DEPEX逐字节不变且无悬空引用。
- 42项Python、真实detail头20组ASan/UBSan、各补丁重复应用、来源/旧board表/defconfig/example检查通过；普通33模块FD、伪造缺项报告的实际负向审计通过。b988本轮实际构建的是32模块隔离变体，默认完整33模式未在此提交重建；281179c完整模式已构建审计。
- 当前完成构建为Display入口前2秒：FD5212eb5f11e6de0a0d45475db7325103bae16bf0bdaa352d808ce274d173f725。最后设备复测使用另一份已有7秒镜像54bb808e3147892d2f40c159f6dbe51b43774d345fe44721bd65629b4e23c4eb，不混用两份证据。各快照含FD/构建/预检/审计/payload/日志。
- 281179c/run39810564733及b988fa4/run39811887053源码CI通过且日志回读PASS。仍未重跑macOS内核CI；历史通用4KiB XNU run39790786938成功不是本板最终内核。

目标仍enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB，UniXNU5fdbd5d及21模块。example=true、owned_memory_size=0x20000000、既有内存字段和所有 *_verified 标记不变。

## 下一步

1. 等待R-002选择；批准后仅在限定范围实现临时保留和只读回读，先验证存活，再接入真实日志。未批准不改实际内存配置。
2. 据实际入口/异常/协议日志修复UFS与Display公共或厂商路径；保持GOP隔离与完整存储证据分开。
3. 取得GOP/UEFI map/BDS闭包后，补齐ADT/NVRAM、板级archives/最终内核/donor prelink，验证最小XNU入口，再推进NT36523。GPU后置。

固件281179c/b988fa4已推送；设备上次8dc4347已推送，本里程碑状态见Git。详见[入口边界](operations/2026-10-23-ufs-entry-boundary.md)、[R-002方案](operations/2026-10-23-early-log-review.md)。
