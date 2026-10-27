# 当前：v8已单次消费，自行回Android，用户未见日志页（2026-10-28）

用户明确“v8上机，正在拍摄，我在场可以恢复”。准备提交6c3d8de、固件49affe7发布及远端精确核验后，执行器再次通过即时enuma/Android/root/A槽/解锁与原双分区/备份门禁，仅一次临时fastboot boot。trial a35583f7-e92d-4999-96d2-116793825026已claim/consumed，不重试；镜像197e44f8379189e56d1efd3518ef3f9eb8ecf88c59e019bb8f2f272553655b29，qualification1 b42faaa664c7613f147cf16dabec5b914550c64a013661b358039c992a66e8ff原字节保持。

执行器观察Android完成并复核分区。用户确认“设备自行返回 从fastboot到Mi标之间都没有”；独立00:51只读核验enuma、boot_completed=1、root、A槽、解锁及设备/本地boot_a/vendor_boot_a原摘要全部通过。无追加启动/分区操作/恢复欠项，没有设备硬停。当前媒体目录D:/Code/PortingiOS/enuma/Media-enuma/OEM-far-event-v8-20261028-a35583f7为空，尚未独立逐帧判读；“无页”依据用户现场陈述，不生成预期S05、不冒充独立视频结论。

v8修复了宿主已复现的RestoreTPL后环尾竞态，且实际链接/资格绑定通过，但本次仍未观察到汇总页。因此不能继续把该竞态当作无页的充分/唯一解释，也不能认定修复未执行；本机实际Core/DXE/GOP阶段仍未知。v7/v8相同外部现象不足以证明内部路径相同，Android返回只证明恢复。

下一最大可操作方向转向末端可观测性与提前复位的分离（诊断优先级中等，唯一根因置信低）：EnumaOemFarDispatchComplete在Owner或真实Core返回位不满足时直接不绘制，completion仍沿7秒恢复；OemProgressEmit拒绝非TPL_APPLICATION；OemBoardSink还要求原继承路由、1600×2560几何、Splash范围、CPU策略和窗口恢复准入，任何拒绝都可能在显示前ResetCold。OEM/后续DXE异常入口同样直接ResetCold，仍是竞争解释。优先设计独立于晚期继承显示准入的阶段/拒绝出口，保留远端路径；不再仅凭无页细化ChipInfo，不能通过放宽像素边界、伪造EFI_SUCCESS或删除全部恢复出口来制造进度。新方案须实际代码/失败路径/机器码/完整构建及新单次资格，本图不重试。

证据：reports/enuma-oem-far-event-v8-trial-20261028.json，out/device-tests/oem-a35583f7-e92d-4999-96d2-116793825026，out/oem-far-event-live-20261028（authorization、publication-verified、preflight、postcheck、human-return-confirmation）。原runner pending快照保留，由新人工确认独立闭合。生产GOP/ConOut/BDS/实体输入/XNU未验收，R027/v6/v7/v8镜像资格冻结，共享主线只读；无内存base/size、verified、flash/erase/改槽变化。媒体/out/二进制/备份/设备标识不入Git或云端。当前无恢复/字符串核对欠项，结果发布以git log及result-publication.json为准。
