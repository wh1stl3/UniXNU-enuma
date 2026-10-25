# 当前状态：D-188，S-006已恢复核验，point22离线构建中

S-006 point21于2026-10-25 15:52:23（Asia/Shanghai）发出，命令返回0/2.625秒，5.110秒断开，75秒无Android/fastboot返回。已consumed且停止追加。用户长按恢复后反馈Android，15:55:30独立enuma Android完成/root/A槽/解锁/boot_a与vendor_boot_a及本地备份摘要一致，恢复停点解除。452/452主录像、740/740恢复录像可解码；抽样黑屏无可读报告。当前Android，无人工或审批待办。

镜像76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节；执行前74ad907已推送。firmwarecb9e568/UniXNU5fdbd5d、同96MiB FAT/display-thread0/GUID-only/fallback0保持。原trial result不重写；公开结果reports/enuma-system-transport-S006-result.json，独立恢复out/device-tests/20261025T155530-recovery-reconciliation.json。所有已执行镜像不重试，旧恢复事实保留，无flash/erase/改槽、内存字段/verified变更。

按结果推进：S-005入口前能自动返回、S-006直接PE返回门无返回，继续将PE包装层/构造器/主函数调用区间列首要嫌疑，但直接Exit会绕过point21，异常/复位也未排除，不能写成显示内部挂死。已审CoreExit源码：有效当前映像Exit经LongJump回StartImage；现有point22在该汇合后、TPL检查/释放JumpBuffer/句柄连接前，可覆盖直接return经CoreExit及成功主动Exit。源码证据reports/enuma-pe-exit-source-review.json。正结果也不证明GOP成功；负结果不能区分PE卡住、无效Exit、ExitData分配失败、异常或reset失败。

恢复等待期已开始同源/完整载荷point22/fallback0离线构建，产物/实际Core资格尚未完成，本轮不追加设备启动。先审实际桥接和LongJump汇合点以及负例，再发布新候选。标准gDS/HOB在Mu派发前安装；调度器源码发现缺映射名称是具体来源缺口，但其他OEM提供者未排除、构造器允许空回退，不按猜测改地址或造stub。PMGR/UFS/root/Data/GOP/XNU/iPadOS仍未闭合。

用户本轮强调原始影音不要上传GitHub：已核对设备仓main、固件main/sheng的影音扩展名历史无媒体文件，两仓GitHub Release无附件；本地out/camera-capture被忽略，CI证据路径不包含它。本轮OpenCV只采画面无音频，不推断其他历史录像是否有音轨。规则已写AGENTS并增加影音扩展名忽略：原始视频/音频/现场图片仅本地，不force-add、不传Release或CI附件，只提交检查后的文字/JSON摘要。审计不覆盖无关第三方或手工其他渠道上传。

后续新启动仍沿现有无需逐笔批准授权，满足资格/当前文档提交推送/即时身份备份采集恢复门禁才执行。异常先停追加/恢复，当轮文档；恢复核验后自动离线分析。R-002/R-015/像素及内存/verified/分区硬边界不变。
