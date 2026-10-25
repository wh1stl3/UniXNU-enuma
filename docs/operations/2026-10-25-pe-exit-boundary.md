# 当前状态：D-189，S-006已恢复，Exit汇合边界候选离线就绪

2026-10-25（Asia/Shanghai）S-006 point21于15:52:23发出；命令返回0/2.625秒、5.110秒断开，75秒无自动返回，已consumed，不重试。用户长按恢复Android，15:55:30独立核验enuma/Android完成/root/A槽/解锁/boot_a与vendor_boot_a及本地备份摘要一致。452/452主录像、740/740恢复录像可解码；抽样黑屏无可读阶段报告。当前Android恢复完成，无人工或审批待办。

S-006镜像76d4b09fcbe1c8e1f02b3114d13dba0c786d365da97bd92595cfe005f3736b09，103817216字节；执行前74ad907已推送，失败停点6b061e2和恢复/影音规则a787f0e也已推送。公开结果reports/enuma-system-transport-S006-result.json保留原phase和timeout事实，并追加独立恢复；原trial result不改写。当前状态见current.local.json/本页，不能把原失败phase当仍未恢复。

主判断（中等置信）：S-005入口前能自动返回，S-006入口直接返回门不返回，PE包装层/构造器/主函数调用区间仍列首要嫌疑。但主动Exit绕过point21，异常/复位等尚未排除，不能证明显示驱动挂死。CoreExit有效当前映像经LongJump回StartImage；已存在point22在该汇合后、TPL清理/释放JumpBuffer/控制器连接前，优先用它排除主动Exit解释。正结果支持到达退出后上下文，不证明GOP或状态成功；负结果仍不能区分PE未返回、无效Exit、ExitData分配失败、异常或复位失败。

已完成同源完整输入point22离线软件：dedd87a68a005817d8ee2d95c60d7949b244bdc31c974e1bd4c760d817c25361，103817216字节；out/full-boot/transport/enuma-pe-exit-full-input-v3.img；FDcc7a39d8b2f181eae341203130566fdbc6cb8778ecc3e3fbe31beeb09f330fdb；冻结归档out/full-boot/transport/pe-exit-boundary-cb9e568。firmware仍cb9e568/UniXNU5fdbd5d、相同96MiB FAT/display-thread0/GUID-only/fallback0。此新镜像尚未consumed或上机，本轮只有S-006一笔，未追加S-007。

实际Core/map审核：SetJump调用0xc3fc，非零分支到point22参数准备；CoreExit转移0xc450；检查点0xc460在TPL检查前。同一scheduled handle/file非空及匹配、精确point/GUID、专门化两次1秒延时/ResetCold/deadloop均按具体编译形态审计。删除SetJump、CoreExit、非零分支、句柄门、GUID/point或延时参数等八负例拒绝，旧21/20/15/13负例回归通过。32OEM PE/DEPEX、SEC配置0、AOSP完整FAT回读及冻结清单绑定通过。机器证据enuma-full-input-pe-exit-boundary/core/negative.json；这些是静态资格，不是point22实机通过。

构造器来源审计继续保留：Mu派发前安装gDS/HOB标准配置表；内核协议失败可走调度器HOB回退。当前map无FD Reserved/FD_Reserved使源码发现路径不能从此来源发布调度器HOB，但其他OEM提供者未排除，构造器可容许空回退，不能拿该缺口直接当黑屏根因或复制外机地址修复。未造stub、未改原厂PE、未补canary值。

用户明确原始影音不要上传GitHub：设备仓main及固件main/sheng可见历史中未发现影音扩展名文件，两仓GitHub Release无附件；本地out/camera-capture被忽略，CI上传目录不含它。本轮OpenCV不采音频，不推断其他历史录像音轨；审计不覆盖无关第三方或其他手工渠道。AGENTS已禁止把原始视频/音频/现场图片force-add或传Git/Release/CI，影音扩展名也加入忽略，仅提交检查后的文字/JSON摘要。原始录像始终本地，未随本轮提交上传。

下一步：新point22候选按现有无需逐笔批准授权、完整源码/产物/文档发布及即时身份备份采集恢复守卫后可单笔验证；入口run_system_transport_trial.py --qualification reports/enuma-full-input-pe-exit-boundary.json默认离线，加--execute才操作设备。本轮没有执行。若它也无返回，不继续无限早停，优先在目标活动映像范围内评估真实UEFI服务调用/返回与原厂构造链ABI取证，或复用已证实同SoC实现的具体缺口适配；不再盲调显示开关。若返回则聚焦后置TPL/清理/控制器连接。

所有已执行镜像consumed；S-001/002/003/006已人工恢复核验，S-004/005自动恢复核验。没有flash/erase/改槽、board/plan内存字段或verified变化，R-002/R-015/像素及其他硬边界保持。仍无13项RAM运输、GOP、XNU或iPadOS运行通过证据，PMGR/UFS/root/Data契约未闭合。

## D-190执行前（2026-10-25 16:03，Asia/Shanghai）

用户明确要求执行point22。16:03:16即时enuma Android完成/root/A槽/解锁/原boot_a与vendor_boot_a及本地备份摘要一致；冻结point22完整载荷dedd87a6…17c25361离线复核通过，相机1920x1080画面可用，尚未发出。本次文档发布后S-007仅一笔临时boot，75秒观察，禁fallback；异常先停止追加并恢复。原始影音只留本地，不上传Git/Release/CI。无内存/verified/分区变更，无人工/审批待办。

## D-191：S-007超时恢复优先

2026-10-25（Asia/Shanghai）16:03:54发出S-007，镜像dedd87a68a005817d8ee2d95c60d7949b244bdc31c974e1bd4c760d817c25361，103817216字节；执行前2036dfc已推送，16:03:16 Android/root/原槽/解锁/设备和备份摘要及相机通过。fastboot命令返回0/2.640秒、5.109秒断开，随后75秒没有Android/fastboot返回。镜像consumed，停止追加且不原样重试。453/453主录像帧可解码，无可读阶段报告。

当前manual-recovery-needed，最后观测未枚举，Android恢复未确认。已开启仅本地恢复录像并请求用户沿此前长按恢复反馈，非新启动审批。恢复后独立核验Android完成/root/A槽/解锁/原boot_a和vendor_boot_a及备份摘要；通过前不发任何新boot。依据AGENTS异常停止追加/恢复优先和当轮交接规则。

主判断：S-005入口前返回，S-006直接PE返回及本次S-007退出汇合门均无返回，继续提高PE包装层/构造器/主函数未完成的优先级，降低“主动Exit成功汇合，仅TPL清理/连接停住”的解释；但未证明门已到达，错误Exit/异常/复位路径仍未排除，不能称DisplayDxe已执行或内部挂死。下一步不再追加同类早停，转原厂构造链及目标活动映像范围的真实UEFI服务调用/返回取证，先离线设计来源/边界/脱敏采集和恢复，选择能定位具体服务的方案。

源码firmwarecb9e568/UniXNU5fdbd5d/完整96MiB FAT/display-thread0/GUID-only/fallback0不变；无flash/erase/改槽、内存字段或verified变化。原trial result保留，公开结果reports/enuma-system-transport-S007-result.json含本地证据路径。原始影音只留本地，不传Git/Release/CI。旧实验均consumed，恢复核验后自动继续离线分析和新软件；R-002/R-015/像素硬边界保持。没有13项运输/GOP/XNU/iPadOS成功证据。

## D-192当前：S-007已恢复，下一步决策先复审官网与其他设备

用户确认Android恢复，16:06:22独立完成/root/A槽/解锁/原分区及备份摘要核验通过，恢复停点解除，无人工/审批待办。S-007 consumed，不重试。用户最新要求：下一步决策之前先查看UniXNU官网最新移植界面、其他设备和仓库；现暂停新设备动作与新取证实现，先核官网及最新固定提交、与本仓pin的变化和板级适用性，再给方案。旧D-191恢复未确认仅历史，当前Android。原始影音始终本地。
