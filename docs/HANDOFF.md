# 当前状态：D-214，发现原生ramoops日志候选；Android正常

2026-10-25T19:28:32+08:00。D-214公开实现复审新增：选定enuma当前pstore后端为ramoops，0xB0000000/4MiB、console/pmsg各2MiB、ECC0，1024页元数据均报告Reserved；这与umi RamoopsSerialPortLib布局相合。此前FDT无节点不能排除厂商硬编码后端。日志优先审原生ramoops兼容/映射/缓存/保留链，显示继续cas式继承和独立原生活动/计数观察，I2C背光为独立支线。当前没有UEFI写入/跨复位读回资格，不更改内存表或写RAM。详见operations/2026-10-25-public-route-priorities.md及reports/enuma-ramoops-route-discovery.json。

2026-10-25T19:19:31+08:00。D-213替代路线对账：已核原厂显示栈/线程关闭、R-005/R-007像素及R-002跨bootloader标记的已执行结果，区分UART只读发现、独立背光未资格、warm/USB/QR未实机闭合。缺头文件不等于必须自写I2C，缺DEPEX GUID不解释APRIORI驱动黑屏。无新设备动作，D-212计数隔离结论与下一步独立原生计数观察不变；详情operations/2026-10-25-display-log-route-ledger.md和reports/enuma-display-log-route-ledger.json。

2026-10-25T19:12:38+08:00。S-013/S-014互补时序支持首样本Enable门禁Reason5，后续稳定性按该路径未执行；两笔Android/root/A槽/解锁/原分区与备份独立核验通过，均consumed。下一步独立验证原生双路计数推进，不放宽GOP准入。

S-013 target1/query1于19:07:50发送1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，命令2.640秒/断开5.109秒/ADB20.078秒/完成34.343秒；S-014 target1/query2于19:09:35发送54f466c1fa0e617af343c237ac65b132d17b68640196f877c474453a86cff523，命令2.641秒/断开5.125秒/ADB26.516秒/完成41.063秒。两笔fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过，无主机恢复reboot，随后分别独立核验Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与本地备份摘要全部通过。248/248与279/279拍屏帧解码，已目视核对恢复桌面；原始影音仅out/camera-capture/20261025T190733-system-transport及190918-system-transport，无音频、未上传。

negative-minus-positive：ADB+6.438秒、完成+6.720秒，均在执行前固定的+3..+7秒窗口。支持Reason5首样本CounterEnable条件先拒绝（中等置信），不是直接原因/寄存器数值日志，也不称GOP/显示成功。跨启动继承变化和Android噪声仍可混淆；S-010/S-011/S-012的历史结果不改写。

源码路径含义：Reason5只在N=0且Timing非零、Enable&3!=3时赋值，随后立即返回；按该分类成立的前提，采样回调最多9读、零等待，完整CTL/SSPP/LM采集、Decode及后续稳定性均未到达。不能称稳定性失败、Frame不递增、某接口不活动或某个bit为零；拒绝接口与实际Enable值未知，Enable检查之后的Active条件也可能尚未执行。实际执行读数仍未知，9为条件路径上限，不当作数字转储。

当前主判断从泛化RefreshMode/稳定性收敛到过强的首样本Enable资格门：它阻断了对实际帧进展的观察。固定小米52a2f18 v1 get_status读取活动接口FrameCount不要求Enable&3==3；旧step15使能复合条件拒绝与step18原生至少一路双窗递增支持只作为同方向历史旁证，不能当本次两路数值。不能直接删条件换PASS，也不修改CounterEnable或时钟。

下一步：实现独立诊断前缀，沿原映射仅观察两路原生活动状态、Timing与Enable稳定值、两窗各1..64非回绕Frame增量；不把Enable是否精确3作为其提前返回条件，不访问尚未证明安全的后续管线银行、不发布GOP。该前缀是新的独立观测，不等于放宽完整EnumaSampleVideo准入；成功后才评估有依据的原生资格修正，失败再细分活动性/稳定性/计数进展。新前缀尚未实现/构建/资格/上机，完整采样所有原条件保持。若新证据显示原因非5、两路不活动/不稳定或CounterEnable实际已满足，应修正当前判断。

新增Detailed接口保留旧入口语义：固定8710ebd oracle覆盖330失败位置和成功的完整回调/等待顺序、返回状态、Out字节；首/后续计数、初始接口、等待、配置变动及Frame停滞原因用例通过，164选择器场景、24固件和4配对解析回归及AArch64对象通过。实际两FD/PE/宏/R-004/完整FAT/BootShim不可变资格通过，实际Core可执行段与已审查S-010相同，provider仅三条映射指令差异已人工审查并摘要绑定，现场运行前提交均已推送（d6c9dfa资格、f399374首笔结果）。

证据reports/enuma-video-counter-S-013-result.json、S-014-result.json、pair-result.json、path-interpretation.json，enuma-video-reason-code.json及pair-code.json；源码b93b3bb已推送。S-001..014及旧失败图不重试，当前无人工/审批待办。

固件固定b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107。真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。
