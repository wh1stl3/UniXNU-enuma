# 当前状态：D-186，完整输入 PE 直接返回候选已资格，待单笔实测

S-005入口前point20已自动返回并于15:40:47独立Android完成/root/A槽/解锁/原两分区及备份摘要通过，已consumed。S-004调用前自动返回、S-003调用后超时后人工恢复事实保持；不重复任何已执行镜像。当前无人工/审批待办，本轮15:47 Android和相机门禁复核通过，实测runner仍即时重验。

新point21镜像76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节，out/full-boot/transport/enuma-pe-return-full-input-v3.img；FD6d4aa5f5f050e88a0faff7608bf3a03b2009963a70ac9c776795534d3b5c40d3；归档out/full-boot/transport/pe-return-boundary-cb9e568。仍firmwarecb9e568/UniXNU5fdbd5d/完整96MiB FAT/display-thread0/精确DisplayDxe GUID-only/fallback0。尚未上机或consumed，无OEM修改、内存字段、verified或分区操作。

实际Core/map审核：0xc428间接PE调用直接返回后，0xc43c执行point21，之后才CoreExit。完整句柄/文件/GUID/point桥接、两次1秒专门化延时及ResetCold/死循环均审核；point21六项破坏负例拒绝、旧20/15/13回归通过，32OEM PE/DEPEX、SEC配置0、AOSP完整FAT往返和冻结清单绑定通过。机器证据enuma-full-input-pe-return-boundary/core/negative.json。静态资格不等于实机门命中。

重要判读：point21只覆盖入口直接return，驱动主动Exit会绕过本门。若返回，支持直接PE返回并提高CoreExit/LongJump/句柄连接阶段嫌疑；若超时，构造器/主函数未返回、直接Exit、异常及复位等仍竞争，不能证明显示内部挂死。自动返回/USB时序不是唯一门命中证明。仍无13项运输/GOP/XNU/iPadOS运行成功证据。

本轮构造器提供者核对：Mu Core在派发前安装标准gDS和HOB配置表，不把原厂查询误当已缺失。内核协议b5062be7-170b-4a32-be21-689262ff4399的查询失败时可走HOB8ec2bd8d-56d7-49ef-8796-631778f8ebf8回退；PlatformPei仅发现调度器地址后发布。当前map无FD Reserved/FD_Reserved，源码发现路径返回，故该来源存在具体缺口；其他OEM提供者未排除，构造器允许空回退，不认定根因或拷外机地址修复。enuma-display-constructor-providers.json记录来源摘要与限制。

发布本次代码和文档后，沿用户现有无需逐笔批准授权执行一笔S-006；run_system_transport_trial.py --qualification reports/enuma-full-input-pe-return-boundary.json --execute。先相机后即时设备身份/备份检查，75秒期限；超时立即停止追加、优先恢复、同轮文档，恢复核验后自动继续离线。所有旧镜像保持consumed，内存/verified/破坏性分区和R-002/R-015/像素旧边界保持。

## D-187：S-006超时恢复优先

2026-10-25（Asia/Shanghai）15:52:23发出S-006 point21完整输入候选76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节；执行前74ad907已推送，原源码cb9e568/UniXNU5fdbd5d/96MiB FAT不变。即时身份、Android/root/原槽/解锁及设备/备份摘要、相机守卫通过。fastboot命令返回0/2.625秒，5.110秒断开，随后75秒没有Android或fastboot返回。已停止追加并consumed，禁止原样重试。

当前为manual-recovery-needed，最后观测未枚举，Android恢复未确认。恢复录像已开启并请求用户沿此前长按方式恢复，非新启动审批；恢复后必须独立核验Android完成/root/A槽/解锁/原boot_a与vendor_boot_a及备份摘要，未通过前不发新候选。触发依据AGENTS异常停止追加/恢复优先和当轮交接规则。记录452/452主录像可解码，未得到可读阶段报告。

结合S-005入口前自动返回而S-006直接PE返回门不返回，主判断提升PE包装层/构造器/主函数调用区间嫌疑；但point21不覆盖主动Exit，异常/复位及观测原因未排除，不能称DisplayDxe内部挂死或门已到达。point13超时同样保留。下一步先离线审主动Exit/CoreExit与已存在point22路径，再选真实服务取证或Exit后边界，避免继续盲调显示配置。标准gDS/HOB来源已核；调度器HOB发现路径缺名称仅源码缺口，不直接归因，不添加外机地址或stub。

主证据reports/enuma-system-transport-S006-result.json及其evidence/camera_evidence路径；原trial result保留，current.local.json为实时恢复状态。S-001/002/003此前人工恢复、S-004/005自动恢复均核验通过且consumed。没有flash/erase/改槽、内存字段或verified变更，R-002/R-015/像素硬边界保持。恢复通过后自动继续离线分析/新软件，无需重复批准或结束推进；当前只差恢复状态和独立核验。

## D-188：S-006恢复与影音本地规则

S-006 point21于2026-10-25 15:52:23（Asia/Shanghai）发出，命令返回0/2.625秒，5.110秒断开，75秒无Android/fastboot返回。已consumed且停止追加。用户长按恢复后反馈Android，15:55:30独立enuma Android完成/root/A槽/解锁/boot_a与vendor_boot_a及本地备份摘要一致，恢复停点解除。452/452主录像、740/740恢复录像可解码；抽样黑屏无可读报告。当前Android，无人工或审批待办。

镜像76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节；执行前74ad907已推送。firmwarecb9e568/UniXNU5fdbd5d、同96MiB FAT/display-thread0/GUID-only/fallback0保持。原trial result不重写；公开结果reports/enuma-system-transport-S006-result.json，独立恢复out/device-tests/20261025T155530-recovery-reconciliation.json。所有已执行镜像不重试，旧恢复事实保留，无flash/erase/改槽、内存字段/verified变更。

按结果推进：S-005入口前能自动返回、S-006直接PE返回门无返回，继续将PE包装层/构造器/主函数调用区间列首要嫌疑，但直接Exit会绕过point21，异常/复位也未排除，不能写成显示内部挂死。已审CoreExit源码：有效当前映像Exit经LongJump回StartImage；现有point22在该汇合后、TPL检查/释放JumpBuffer/句柄连接前，可覆盖直接return经CoreExit及成功主动Exit。源码证据reports/enuma-pe-exit-source-review.json。正结果也不证明GOP成功；负结果不能区分PE卡住、无效Exit、ExitData分配失败、异常或reset失败。

恢复等待期已开始同源/完整载荷point22/fallback0离线构建，产物/实际Core资格尚未完成，本轮不追加设备启动。先审实际桥接和LongJump汇合点以及负例，再发布新候选。标准gDS/HOB在Mu派发前安装；调度器源码发现缺映射名称是具体来源缺口，但其他OEM提供者未排除、构造器允许空回退，不按猜测改地址或造stub。PMGR/UFS/root/Data/GOP/XNU/iPadOS仍未闭合。

用户本轮强调原始影音不要上传GitHub：已核对设备仓main、固件main/sheng的影音扩展名历史无媒体文件，两仓GitHub Release无附件；本地out/camera-capture被忽略，CI证据路径不包含它。本轮OpenCV只采画面无音频，不推断其他历史录像是否有音轨。规则已写AGENTS并增加影音扩展名忽略：原始视频/音频/现场图片仅本地，不force-add、不传Release或CI附件，只提交检查后的文字/JSON摘要。审计不覆盖无关第三方或手工其他渠道上传。

后续新启动仍沿现有无需逐笔批准授权，满足资格/当前文档提交推送/即时身份备份采集恢复门禁才执行。异常先停追加/恢复，当轮文档；恢复核验后自动离线分析。R-002/R-015/像素及内存/verified/分区硬边界不变。
