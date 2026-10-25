# 当前状态：D-186，完整输入 PE 直接返回候选已资格，待单笔实测

S-005入口前point20已自动返回并于15:40:47独立Android完成/root/A槽/解锁/原两分区及备份摘要通过，已consumed。S-004调用前自动返回、S-003调用后超时后人工恢复事实保持；不重复任何已执行镜像。当前无人工/审批待办，本轮15:47 Android和相机门禁复核通过，实测runner仍即时重验。

新point21镜像76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节，out/full-boot/transport/enuma-pe-return-full-input-v3.img；FD6d4aa5f5f050e88a0faff7608bf3a03b2009963a70ac9c776795534d3b5c40d3；归档out/full-boot/transport/pe-return-boundary-cb9e568。仍firmwarecb9e568/UniXNU5fdbd5d/完整96MiB FAT/display-thread0/精确DisplayDxe GUID-only/fallback0。尚未上机或consumed，无OEM修改、内存字段、verified或分区操作。

实际Core/map审核：0xc428间接PE调用直接返回后，0xc43c执行point21，之后才CoreExit。完整句柄/文件/GUID/point桥接、两次1秒专门化延时及ResetCold/死循环均审核；point21六项破坏负例拒绝、旧20/15/13回归通过，32OEM PE/DEPEX、SEC配置0、AOSP完整FAT往返和冻结清单绑定通过。机器证据enuma-full-input-pe-return-boundary/core/negative.json。静态资格不等于实机门命中。

重要判读：point21只覆盖入口直接return，驱动主动Exit会绕过本门。若返回，支持直接PE返回并提高CoreExit/LongJump/句柄连接阶段嫌疑；若超时，构造器/主函数未返回、直接Exit、异常及复位等仍竞争，不能证明显示内部挂死。自动返回/USB时序不是唯一门命中证明。仍无13项运输/GOP/XNU/iPadOS运行成功证据。

本轮构造器提供者核对：Mu Core在派发前安装标准gDS和HOB配置表，不把原厂查询误当已缺失。内核协议b5062be7-170b-4a32-be21-689262ff4399的查询失败时可走HOB8ec2bd8d-56d7-49ef-8796-631778f8ebf8回退；PlatformPei仅发现调度器地址后发布。当前map无FD Reserved/FD_Reserved，源码发现路径返回，故该来源存在具体缺口；其他OEM提供者未排除，构造器允许空回退，不认定根因或拷外机地址修复。enuma-display-constructor-providers.json记录来源摘要与限制。

发布本次代码和文档后，沿用户现有无需逐笔批准授权执行一笔S-006；run_system_transport_trial.py --qualification reports/enuma-full-input-pe-return-boundary.json --execute。先相机后即时设备身份/备份检查，75秒期限；超时立即停止追加、优先恢复、同轮文档，恢复核验后自动继续离线。所有旧镜像保持consumed，内存/verified/破坏性分区和R-002/R-015/像素旧边界保持。
