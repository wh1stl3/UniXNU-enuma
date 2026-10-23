# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 已确认与未确认

用户已选择R-003推荐A并要求继续主线。正在用真实Mu入口、共享Dispatcher上下文、完整文件GUID及可控定时返回细分Display启动边界。尚未进入XNU；无GOP、UEFI实时内存图、BDS或NT36523实机证明。

- a927ca1、无UFS、Display实际PE调用前point20的2/7/2样本：ADB16.977/22.272/16.367秒，差5.295/5.905秒，支持到达调用前。不是PE内包装器/构造器/主体执行证明。
- point21直接返回后、point22 Exit代码块后的2秒候选：ADB33.063/32.894秒，均未观察短门。不能把负向时序说成绝无返回。
- 903ffed独立全局默认DumpCpuContext门point23的2/7秒候选：ADB30.766/30.772秒，差0.006秒，未观察到门；不能排除其他handler/更早故障/其他复位来源，不能归因Display。
- 903ffed同版point20正对照：ADB15.951秒/Android30.408秒，恢复核对正常，支持该版本调用前门仍可达。
- d3a0972只读point24存在门2/7/2：ADB17.298/21.464/16.058秒，差4.166/5.406秒；支持调用前已有包装器匹配的canary GUID前缀。保留噪声，未读取canary值、未证明完整GUID或PE内部执行。point25缺失门仅主机检查，未实测。

上述所有候选均自动恢复Android，sys.boot_completed/root/原boot和vendor_boot摘要正常。没有flash/erase/改槽；有界定时返回不是驱动成功。

## 当前源码与验证

固件gitlink为d3a0972，源锁44项；此前903ffed加入独立异常门。本版新增只读point24/25，匹配锁定OEM包装器实际使用的canary配置表GUID前64位，不读取VendorTable、不写入canary或调用RNG/SMC。4096项只是诊断遍历上限，异常表结构不报告为缺失。原25迁移文件/六patch、内存字段/512MiB/example/verified保持；OEM PE/DEPEX不修改。

47组真实header/bridge ASan/UBSan、6组全局异常门和45项Python/重复patch通过。workspace固定来源、精确R-002配置与example guard通过。903ffed源码CI39834543624成功并回读PASS；d3a0972源码CI39882096705成功并回读PASS。源码CI不代替固件编译与硬件验证。

已构建/实测的各个候选均完成官方backend及core补丁还原、32原厂PE/DEPEX审计、192字节BootShim+3MiB FD、AOSP v3回读。d3a0972的point24两候选已完成完整构建/审计与2/7/2实测。默认完整33-OEM模式未在新source重建，不以无UFS32模式代替存储验证。

## R-002与显示路线限制

R-002精确范围0x9fff7000/0x8000：活动FDT/8页保护、normal ABI/reader运行和同次16字节marker匹配已实测；经Bootloader进入无writer保留Android后marker不同。按原批准已停止跨复位持久日志，不换址/扩大/借DFPS或SMEM。没有启用SEC/DXE持久日志。

SimpleFb仍为离线审计，优先复用Mu SimpleFb/FrameBufferBltLib及alioth/elish设计。enuma真实入口base/stride/像素格式/线性布局/跨度/生命周期缺失，未开启拟议30-OEM变体；显示区尾部日志落DFPS，保持Null serial。33个本机原厂PE均含同canary GUID，字节线索不等于运行表存在，更不能单独判定Display/RNG根因。

## 下一步与授权

配置表前缀存在已有对照支持，降低“缺表触发canary RNG初始化”的嫌疑；不能据此认定canary值正确或排除其他SMC。下一步优先细分库构造器/UEFI服务调用，使用真实Mu服务边界并核对调用归属，保持原厂PE字节；尚未实现该下一层门。无新固定内存/verified变更，也无待人工按键。详细契约及证据见[PE入口门记录](operations/2026-10-23-direct-pe-entry-gates.md)。

生成镜像无需确认；有身份、备份和返回证据的有界临时boot允许黑屏/定时复位。恢复失败、越权、内存字段或verified变更仍按AGENTS硬停。TWRP未测试。难题继续评估同SoC UniXNU/UEFI真实实现，不直接照搬板级参数。

目标保持enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块。旧通用内核CI不是本板最终内核。设备上一里程碑df705f6已推送；后续以Git/WORKLOG发布记录为准。
