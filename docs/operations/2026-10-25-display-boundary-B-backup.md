# B/detail13离线备用（D-169）

状态：已构建/归档/审计，未实测；用户随后明确完整启动链优先（D-170），因此本候选不作为当前优先上机任务。R-016已消耗，不能用A批准自动执行B。

镜像SHA256 bf6e014dbda4fc64ea00762034b5107ffd617e5ae24752b708c143bfca03b2e3，FD 995a962df36d84c34b2ffa742a477baed69b8a6524302babdd58c525a30b53f2。固件仍aa9ec66，stage13/detail13、目标DisplayDxe完整GUID、delay2、fallback7、without-ufs、query0/step0/value-off。源输入、框架pin和配置与A一致，唯一定义差异是DETAIL_POINT 15→13。

从实际打包Core及其链接图确认：RVA0x1047c调用CoreStartImage，0x1048c调用point13门；门核对point13、GUID两半，再延时2秒、ResetCold和CpuDeadLoop。不是EFI_STATUS输出通道。

72个PE中70个逐字节相同；DxeCore是运行代码差异。PcdDxe另有8字节变化，全部位于文件偏移0x6148起16字节RSDS/PDB GUID字段内；仅屏蔽这一已识别字段后整个PE逐字节一致，代码、路径、age和其他数据相同。32个原厂PE/DEPEX保持不变，仅省略UFSDxe，192字节BootShim一致。不能把“运行代码只有Core改变”写成“所有PE只有Core改变”。

工具audit_display_boundary_core.py及check_display_boundary_core.py实查Core/map/归档摘要，四项负例通过：去掉真实StartImage调用、损坏GUID立即数、错point、PcdDxe代码篡改均拒绝。证据reports/enuma-display-boundary-B-code.json与enuma-display-boundary-B-qualification.json；完整产物在out/display-entry-boundary/return-aa9ec66。

只有完整启动链缺乏可定位报错且确需区分CoreStartImage是否返回时，再评估此备用。返回不等于SetMode/GOP成功；超时不等于已唯一定位驱动内部。没有新的实机动作、内存字段/映射、verified或分区变化。
