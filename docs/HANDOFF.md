# 当前：v7已单次消费，自行回Android，用户未见日志页（2026-10-28）

用户“v7开始 正在拍摄”后，准备提交8f31a71/固件1f05eef均远端精确核验，即时enuma身份、原备份与恢复门禁通过，仅一次临时fastboot boot。trial 61c29945-1399-49eb-8133-d11d465bb6c4已claim/consumed，不重试；镜像SHA256 c02ab64cb7afa292f53823a38ea4ddcc98f3f9b0cee42fa4c32d706bbba47d5d，qualification2原字节保持。

执行器观察到Android完成并核对原分区；用户确认“设备自行返回 从fastboot到Mi标之间都没有”，记录为自动返回、用户没有观察到日志页。00:16独立只读复核enuma、boot_completed=1、root、A槽、解锁、设备与本地boot_a/vendor_boot_a原摘要均通过。没有追加启动、分区写入、改槽或恢复欠项，没有设备硬停。

当前媒体目录D:/Code/PortingiOS/enuma/Media-enuma/OEM-far-chain-v7-20261028-61c29945为空，尚未独立逐帧核验。本次“无页”依据用户现场陈述，不能冒充助手视频判读，也不生成/解码预期S05。Android恢复仅证明恢复终点，不证明OEM/Core返回、完整DXE分派、GOP或BDS成功。

实际代码的第一排查方向是无页的提前复位/末端拒绝链（诊断优先级中等，唯一根因置信低）：异常入口直接ResetCold；追踪校验/同步失败会终止；若走到DXE末端，Owner/Core返回门不满足则不绘制而走7秒恢复，TPL、路由/CPU策略或窗口准入拒绝也可在显示前复位。其次仍有OEM协议方法/直接访问及后续DXE异常。v7删除了v6 E01窗口，所以这笔不能再归因为该窗口收尾本身，但不排除其他追踪负担或出口问题。没有汇总页无法判ChipInfo/SID死锁，也不能宣称实际走得更远。

下一步只做离线代码归因：优先区分真实Core返回门/后续分派与末端取证出口，并审查是否可在不增加早期UI停顿的前提下提供独立失败归因；需要原视频时先独立落盘逐帧检查，再展示可读全文供人工核对。新软件须新的完整资格和单次门禁，不复活v7，不以未校准USB时长推断执行阶段。BDS/生产GOP/ConOut/实体输入/XNU均未验收。

证据：reports/enuma-oem-far-chain-v7-trial-20261028.json；out/device-tests/oem-61c29945-1399-49eb-8133-d11d465bb6c4；out/oem-far-chain-live-20261028的authorization、publication-verified、preflight、postcheck、human-return-confirmation。runner原pending状态不覆盖，由新人工确认独立闭合。共享主线只读，R027和旧镜像/资格冻结；内存base/size、verified、分区与媒体本地边界保持。当前没有恢复或字符串核对欠项；源码/文档本轮结果发布以git log及result-publication.json为准。
