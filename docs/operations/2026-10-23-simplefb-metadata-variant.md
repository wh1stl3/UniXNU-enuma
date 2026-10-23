# 借鉴alioth/elish的SimpleFb诊断：已构建，首测需人工恢复

2026-10-23（Asia/Shanghai）。承接用户“从其他设备仓库借鉴一些解决方案过来”。设备仓上一里程碑e4a40fb已推送。**最新设备恢复未确认：233a9d8首个SimpleFb入口前候选未在75秒内回ADB/fastboot，再次只读检查仍无目标端点；用户暂时无法按键，已停止后续设备试验。** 不能声称GOP安装、显示、UEFI map、BDS或XNU成功。

## 实际采用的方案

- alioth / Mu：复用原生Display与Mu SimpleFb二选一的打包/分派设计，诊断时移除CPR。来源固定uefi-sheng329b473d及本仓现有alioth代码；其分派/依赖与文件SHA已有enuma-simplefb-reuse-audit.json记录。UFS额外隔离是enuma此前实际停点要求，不谎称alioth也删除UFS。
- elish / edk2-msm e1952621：借鉴沿用bootloader既有scanout、以SimpleFb包装GOP的路线及参数有效性检查。没有复制其固定帧缓冲PCD地址、二进制或板级内存表。
- 通用实现：继续使用真实Mu SimpleFb和FrameBufferBltLib。基址来自enuma自己的MemoryMapHelper/Display Reserved描述，不新增固定地址。颜色32位、紧密stride是诊断元数据假设，不是enuma实际扫描输出事实；像素布局/偏移/生命周期仍未知。
- 结合先前nuwa借鉴：全局pool后备页搜索门已落地并实测；成功门有5.370秒延时响应，失败门未观察。没有把nuwa堆耗尽结论或209.75MiB数值照搬到enuma。

默认仍原生33-OEM；既有无UFS为32-OEM；新显式SimpleFb诊断严格排除CPRDxe/DisplayDxe/UFSDxe，保留其余30个enuma PE/DEPEX逐字节，并在原Display的静态APRIORI位置换入SimpleFb。SimpleFb已在FV/DSC/APRIORI三处接通，不是只改一个开关。FD审计必须匹配实际完成FD/hash、确切三个排除项和唯一预期SimpleFb提供者，否则拒绝。普通模式仍拒绝未获资格的SimpleFb打包。

## 已补的通用错误路径

区域描述符清零、检查查询状态，只有第一个名称确实Not Found才查下划线别名；拒绝空指针、零地址/长度、未知色深。QueryMode/SetMode检查模式和启动状态，复制完整像素mask；分配、Blt配置、协议安装失败传播真实状态并清理，防止Mode为空时解引用、重复释放和重入泄漏；跨度改为检查过的64位运算。

233a9d8的诊断Blt直接EFI_UNSUPPORTED，不调用FrameBufferBlt写像素。**这不是整份固件不可能写像素的证明**：首测后离线发现，若预期核心门未命中而继续到BDS，原EnumaProbe仍有DiagDraw直接写帧缓冲路径，绕过GOP Blt。7479da1已添加EnumaProbe诊断入口提前返回守卫，原native行为不变。该守卫只是限制已知上层路径，不代表所有潜在GOP客户端已穷尽审计。

剩余物理显示条件仍要满足：真实scanout base/偏移、pitch/格式/线性布局、像素子范围（隔离DFPS）、缓存一致性及生命周期。没有开启像素绘制或把假设写成verified=true。不能直接把metadata模式当可用生产GOP。

## 构建与代码检查

- source233a9d8：实际AArch64官方backend成功，core patch还原通过；FD 465c5564003fcb78895861a43a3038644a35b82adfabf4485e466902b8fa690d，79个FFS；30 OEM PE/DEPEX逐字节、SimpleFb静态位置33、BootShim及AOSP v3回读通过。实际编译SimpleFb.c与host补丁后源码相同，clang命令确有ENUMA_DIAG_SIMPLEFB=1。源码CI39888162938成功并回读PASS。
- source7479da1：补EnumaProbe直写入口守卫、LF暂存和哈希；当前gitlink/49项源锁，源码CI39889743071成功回读。**未再次构建AArch64固件或设备启动，不继承233a9d8实测。**
- 整份实际补丁后SimpleFb C在UEFI mock适配器下ASan/UBSan通过，覆盖查找、mask/模式、三个分配失败点、配置/安装失败、溢出、清理及诊断Blt不调用像素库。实际Probe入口守卫前缀在宏0/1下编译执行检查通过；条件选择/现有UFS/DSC/contract组合patch重复重放一致。仅host行为，不是UEFI ABI或硬件证明。
- 48项Python检查通过，含新增“上一探针manual-recovery-needed时，在任何设备工具调用前拒绝新试验”回归。工作区静态检查确认49来源、旧内存/512MiB/example/verified保持。

机器证据：[实际构建/恢复状态](../../reports/enuma-simplefb-bringup.json)、[整驱动host检查](../../reports/enuma-simplefb-contract-host.json)、[所有设备尝试](../../reports/enuma-entry-device-tests.json)、[源码CI](../../reports/enuma-uefi-source-actions.json)。原始源码/日志/FD/镜像只在本仓out，不复制进Git。

## 首测和停点

233a9d8候选于10:16:30临时fastboot boot接受，镜像92b11e7d35351abc6415e0fd2bfe580f52830261014c9c30bfa8656d37de06b4。选择SimpleFb完整GUID dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92、detail20 PE调用前、2秒、ordinal32。静态APRIORI位33沿用旧Display映射，但**实际Dispatcher计数未在新布局校准**；静态位置检查不能替代实际序号，AND筛选可能漏门只是待查候选原因之一。

75秒内未观察到目标ADB/fastboot，runner记录manual-recovery-needed并停止；后续两次只读端点检查同样未检出。用户明确“暂时无法按键”。不能从无端点判断是某处异常、黑屏死机还是UEFI仍在运行；也不知道是否进入了SimpleFb/EnumaProbe。未flash/erase/改槽；试前摘要核对正常，但本次**试后Android/root/分区摘要尚未核验**，不称“原分区已验证不变”。

已停止所有追加镜像/设备写入，只完成离线代码守卫、host/static、源CI和交接。私有自动编排现对SimpleFb仅构建归档，不自动启动；公共探针也拒绝上一轮未恢复状态。没有静默重试、换驱动二进制、改内存或重启R-002日志。

## 恢复后再做的工作

先由用户长按电源约15–20秒、重启时按音量下回FASTBOOT；若直接回Android也可。主机随后只沿现有授权恢复，核对enuma身份、槽位、Android完成1/root和原boot/vendor_boot摘要后，才可把手工恢复状态清除。TWRP仍未测试。

当前不能继续实机。恢复后先审计实际分派计数或设计单独GUID-only选择，不能再次把静态APRIORI位置当真机序号；补齐成功/失败/加载错误/意外BDS路径均可观察且有界的返回契约，再谈任何候选。7479da1的上层绘制守卫不能单独修复未知复位问题。地址/大小/verified若有新需求仍按AGENTS审阅。当前没有新内存批准请求，主要依赖是实体恢复与观测条件。

## 后续恢复与离线推进（2026-10-23）

上述“当前不能继续实机/暂无法按键”是首测停点时的历史事实。用户已人工按键恢复，12:11:03主机确认Android/root/原摘要；新指令转为离线，无新启动。7479da1已实际构建未实测；后续6bc5b81引入GUID-only与正常分派结束兜底，不能覆盖卡死，也不能追溯保护233。当前唯一状态见[STATUS](../STATUS.md)，方案见[新审计](2026-10-23-guid-only-dispatch-offline.md)。
