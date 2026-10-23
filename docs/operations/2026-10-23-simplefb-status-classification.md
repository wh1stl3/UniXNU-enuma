# SimpleFb最终StartImage状态分类

2026-10-23 Asia/Shanghai。用户要求继续推进，沿既有临时boot/外置录像授权。复用固件82ce8a5既有point17（非错误）/point16（错误）最终StartImage返回门；未修改固件源码、表、OEM、内存或verified。

## 方法与构建

两份同源候选均stage13、完整GUID dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92、GUID-only/ordinal1占位、命中延时2秒，未命中保留正常Dispatcher返回后固定7秒兜底。metadata Blt拒绝和Probe早退不变。17/16条件为 !EFI_ERROR(Status) / EFI_ERROR(Status)，取自CoreStartImage返回到Dispatcher后的真实Status，而非point21的PE入口直接返回值。

条件互补不等于能从单次时长断定数值。17包括EFI warning，不能将命中等同Status=EFI_SUCCESS(0)；16的长返回只作未观察命中/完成兜底的时序推断。完成兜底仍不是异步看门狗。

复用既有构建包装器，独立归档两个variant：evening-simplefb-status-guid-only-queue1-stage13-delay2-point{17,16}-guiddcfd1e6d-simplefb-metadata。实际AArch64/core patch还原/30OEM/3MiB FD/192B BootShim/v3及官方unpack回读通过，源输入、FD、raw和镜像摘要交叉检查通过。完整实际诊断头/桥接147组host sanitizer与非法组合/完成门重跑通过；开始首笔前也核对未变源码与旧通过报告的hash一致。测试没有更改源码，最后workspace qualification串行通过。

| 候选 | boot v3 SHA256 |
| --- | --- |
| 非错误17 | e82e997ee7b734713830386f2ca36988744f2d4b12c60ace071b692caae7708b |
| 错误16 | b04cecf6d8b15e40548d3276a89a56b153fbc611f4a0a04ad5287cfb5a1db6ff |

完整FD/源锁与录像摘要见[结构报告](../../reports/enuma-simplefb-status-classification.json)，原件仅out。

## 实际结果

| 发出时间 +08 | 门 | ADB返回秒 | Android完成秒 |
| --- | --- | --- | --- |
| 18:52:06 | 17非错误/2秒 | 16.057 | 30.215 |
| 18:57:15 | 16错误/2秒 | 22.524 | 35.034 |
| 18:58:31 | 同一17镜像复测 | 16.082 | 30.519 |

每笔完整唯一enuma/Android完成/root/槽/解锁/备份/原分区摘要检查后，重启fastboot并完整检查身份再临时boot；各笔最终回Android完成/root，boot_a/vendor_boot_a与原备份摘要一致，无flash/erase/改槽。本组没有身份查询拦截，前组曾发生的异常不删除。

两次17短返回差0.025秒；16比前后17长6.467/6.442秒。结合point20/21先前两组响应，本组支持目标SimpleFb最终StartImage返回非错误，16未观察到2秒命中、表现与完成兜底一致。不是精确5秒差，USB/原厂启动/轮询噪声仍在；没有读取数值EFI状态、不能确定warning为零。人工按键确认以结构报告字段和后续补充为准，不从相机未见手推断没有按键。

## 对GOP的意义与下一步

实际AutoGen中ProcessModuleEntryPointList返回RegisterFrameBuffer结果；固定SimpleFb正常路径依次获取描述符/几何、分配、模式/Blt配置、InstallMultipleProtocolInterfaces，在安装非错误后返回EFI_SUCCESS，失败则清理并返回错误。故本组对“该正常安装路径完成”有源码结合时序的支持，排查重心可从稳定卡在SimpleFb内部，转到实际GOP元数据、消费者与显示路径。

但这不是运行时GOP句柄快照：未枚举提供者/句柄，没有HandleProtocol、QueryMode实测结果，没有验证唯一协议、真实scanout、像素格式/stride/base/span或受控Blt。不得把报告写为GOP/屏幕已验证，metadata本身也不能证明对应活动面板。EnumaScreen尚未全固件集成，Probe guard不能直接撤。

下一层应做显式默认关闭的只读GOP观察：枚举/选择本次实际协议、确认provider归属与句柄，读取当前Mode并调用QueryMode交叉比较，检查返回指针/长度/状态/几何/溢出/清理。先通过host实际UEFI接口、目标编译/全链接和现有恢复条件，再运行候选；不做Blt、不直接访问物理FB、不扩内存、不借DFPS或R-002。取得实际范围后再决定受控小矩形文字输出，而非直接进菜单。

## 录像与当前设备

三录像均1920×1080，全部解码帧数匹配单调时间戳。私有目录out/camera-capture/20261023T185145-simplefb-status17-2s、20261023T185654-simplefb-status16-2s、20261023T185810-simplefb-status17-2s，runner分别185152、185701、185817。抽查17的48秒为Android锁屏、16的25秒为黑屏、末17的48秒为锁屏，未见UEFI文字需手机补录；不是逐帧OCR，不排除未抽查时刻内容。原录像不入Git，帧抖动以时间戳而非固定5fps播放时长分析。

摄像头已经释放，设备为最后一次恢复核验后的Android。当前无恢复按键或手机补录待办；新测试仍逐笔检查在场/恢复条件，实际无返回即停追加先恢复。
