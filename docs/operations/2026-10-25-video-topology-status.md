

## D-205，互补首拒绝分类源码/主机通过，完整构建进行中

2026-10-25T18:39:28+08:00。用户要求继续推进。S-010已consumed，最后独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要通过，原结果D-204保留。当前固件8710ebd93da7b19bb7ffd0e388f6925399231153新增互补首状态查询，未改采样/拓扑/格式/地址准入、Core双结果终止和完整FAT，不发布GOP、不访问像素、不新增硬件读写。新入口把首个有效status==Topology13映射query1的marker1（2秒），其余有效状态marker5（7秒）；query2精确反转。描述表/PCD拒绝作为Arguments11。无效状态、成功但错误Requirements不发已识别marker；诊断match不能称完整采样/GOP成功。

55个生产选择器用例、原GOP/拓扑/330读失败及等待失败主机回归通过，23个固件相关Python回归及3个双时序解析回归通过。源码已提交推送；实际两FD/PE/编译宏、归档和完整打包资格另核。只允许固件-owned构建和设备-owned打包/恢复，原内存/verified/分区边界不变。

预先固定两笔计划：S-011=query1，受控回Android且独立恢复通过后，文档再次推送才S-012=query2。任一身份/采集/恢复异常、超时或单笔明显不受控则停止后续；失败图不重试。两笔均完整同源同输入，同Core及构造器，唯运行代码差异限provider选择结果。配对比较negative-minus-positive的ADB出现和Android完成两指标：均在+3..+7秒只支持Topology状态；均在-7..-3秒只支持非Topology；任何其他组合记ambiguous并冻结该对。该容差是预先采用的判读窗口，不是硬件标定精度；跨启动状态变化和Android噪声仍可混淆，不声称直接读到状态。75秒无已识别返回仍立即consumed并先恢复。保留必要的完整输入和现场恢复条件，原始影音仅本地out且不采音频。

当前没有S-011/S-012设备动作，两候选完整产物资格尚未完成；当前无人工或新增审批待办。新资格完成并落实全部文档推送、即时身份/备份/相机/恢复后才逐笔执行。


## D-206，互补分类实际产物资格通过，先单笔S-011

2026-10-25T18:44:56+08:00。用户要求继续推进。S-010已consumed，其试后独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要通过，原结果D-204保留。当前固件8710ebd93da7b19bb7ffd0e388f6925399231153新增互补首状态查询，未改采样/拓扑/格式/地址准入、Core双结果终止和完整FAT，不发布GOP、不访问像素、不新增硬件读写。新入口把首个有效status==Topology13映射query1的marker1（2秒），其余有效状态marker5（7秒）；query2精确反转。描述表/PCD拒绝作为Arguments11。无效状态、成功但错误Requirements不发已识别marker；诊断match不能称完整采样/GOP成功。

55个生产选择器用例、原GOP/拓扑/330读失败及等待失败主机回归通过，23个固件相关Python回归及3个双时序解析回归通过。源码已提交推送；实际两FD/PE/编译宏、归档和完整打包资格另核。只允许固件-owned构建和设备-owned打包/恢复，原内存/verified/分区边界不变。

预先固定两笔计划：S-011=query1，受控回Android且独立恢复通过后，文档再次推送才S-012=query2。任一身份/采集/恢复异常、超时或单笔明显不受控则停止后续；失败图不重试。两笔均完整同源同输入，同Core及构造器，唯运行代码差异限provider选择结果。配对比较negative-minus-positive的ADB出现和Android完成两指标：均在+3..+7秒只支持Topology状态；均在-7..-3秒只支持非Topology；任何其他组合记ambiguous并冻结该对。该容差是预先采用的判读窗口，不是硬件标定精度；跨启动状态变化和Android噪声仍可混淆，不声称直接读到状态。75秒无已识别返回仍立即consumed并先恢复。保留必要的完整输入和现场恢复条件，原始影音仅本地out且不采音频。

两份完整不可变资格已完成，无新boot。S-011(query1)镜像4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7，FDfa02b3a0ed300f4876c2f2b7a691efb1dbe2abbab17279e8c4f4b317245451d4；S-012(query2)镜像4454dfaa0b00d08d277e921641b51b250850906236770d6514f97cca51f54389，FDd82cf752f0d6e7d6831a49878b05cb100c2dbbca76a0d75c30986013d22dd57c。每份103817216字节、完整96MiB FAT。归档out/inherited-gop/qualified-topology-8710ebd-q1和q2。实际Core可执行段均等于已审查S-010；实际两provider只有两处前置拒绝返回常量与一处status13选择条件三条指令不同，其他实际PE只允许已精确核对的CodeView GUID变化。Core/provider实际宏均TERMINAL1/FALLBACK0，TOPOLOGY_QUERY分别1/2，R-004记录/实际PE/入口与所有采集源码/BootShim/完整FAT摘要通过。

Android/root/A槽/解锁/设备和备份摘要及1920x1080相机再次通过。源码8710ebd已推送。当前文档与资格提交推送后，S-011一笔；S-012仍待S-011有界返回、独立恢复核验及结果文档推送，不批量连发。预先窗口见上文，不更改观测判据。实际代码证据reports/enuma-video-topology-code.json与enuma-video-topology-pair-code.json；正反资格分别enuma-video-topology-positive-qualification.json和negative-qualification.json。当前无人工/审批待办。


## D-207，S-011受控返回并独立恢复，准备互补S-012

2026-10-25T18:46:54+08:00。用户要求继续推进。S-010已consumed，其试后独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要通过，原结果D-204保留。当前固件8710ebd93da7b19bb7ffd0e388f6925399231153新增互补首状态查询，未改采样/拓扑/格式/地址准入、Core双结果终止和完整FAT，不发布GOP、不访问像素、不新增硬件读写。新入口把首个有效status==Topology13映射query1的marker1（2秒），其余有效状态marker5（7秒）；query2精确反转。描述表/PCD拒绝作为Arguments11。无效状态、成功但错误Requirements不发已识别marker；诊断match不能称完整采样/GOP成功。

55个生产选择器用例、原GOP/拓扑/330读失败及等待失败主机回归通过，23个固件相关Python回归及3个双时序解析回归通过。源码已提交推送；实际两FD/PE/编译宏、归档和完整打包资格另核。只允许固件-owned构建和设备-owned打包/恢复，原内存/verified/分区边界不变。

预先固定两笔计划：S-011=query1，受控回Android且独立恢复通过后，文档再次推送才S-012=query2。任一身份/采集/恢复异常、超时或单笔明显不受控则停止后续；失败图不重试。两笔均完整同源同输入，同Core及构造器，唯运行代码差异限provider选择结果。配对比较negative-minus-positive的ADB出现和Android完成两指标：均在+3..+7秒只支持Topology状态；均在-7..-3秒只支持非Topology；任何其他组合记ambiguous并冻结该对。该容差是预先采用的判读窗口，不是硬件标定精度；跨启动状态变化和Android噪声仍可混淆，不声称直接读到状态。75秒无已识别返回仍立即consumed并先恢复。保留必要的完整输入和现场恢复条件，原始影音仅本地out且不采音频。

S-011(query1)于18:45:34发出，镜像4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7已consumed。命令2.625秒、断开5.093秒，ADB26.484秒/完成40.547秒受控回Android，无主机恢复reboot。独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要全部通过，278/278帧解码，原始影音仅本地无音频。证据reports/enuma-video-topology-S-011-result.json，原trial out/device-tests/20261025T184520-system-transport/result.json。

单笔时序接近长返回，仅初步支持首次状态非Topology，不据此确证。按预先计划，当前文档提交推送后执行S-012(query2)一次，仍保持即时Android/备份/fastboot/相机/恢复门禁及75秒期限，完成互补核对后才分类。S-011与S-010及旧图不重试；当前无人工/审批待办。


## D-208，互补支持非Topology，Android核验通过，转查计数前置

2026-10-25T18:50:24+08:00。用户要求继续推进。S-010已consumed，其试后独立Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与备份摘要通过，原结果D-204保留。当前固件8710ebd93da7b19bb7ffd0e388f6925399231153新增互补首状态查询，未改采样/拓扑/格式/地址准入、Core双结果终止和完整FAT，不发布GOP、不访问像素、不新增硬件读写。新入口把首个有效status==Topology13映射query1的marker1（2秒），其余有效状态marker5（7秒）；query2精确反转。描述表/PCD拒绝作为Arguments11。无效状态、成功但错误Requirements不发已识别marker；诊断match不能称完整采样/GOP成功。

55个生产选择器用例、原GOP/拓扑/330读失败及等待失败主机回归通过，23个固件相关Python回归及3个双时序解析回归通过。源码已提交推送；实际两FD/PE/编译宏、归档和完整打包资格另核。只允许固件-owned构建和设备-owned打包/恢复，原内存/verified/分区边界不变。

预先固定两笔计划：S-011=query1，受控回Android且独立恢复通过后，文档再次推送才S-012=query2。任一身份/采集/恢复异常、超时或单笔明显不受控则停止后续；失败图不重试。两笔均完整同源同输入，同Core及构造器，唯运行代码差异限provider选择结果。配对比较negative-minus-positive的ADB出现和Android完成两指标：均在+3..+7秒只支持Topology状态；均在-7..-3秒只支持非Topology；任何其他组合记ambiguous并冻结该对。该容差是预先采用的判读窗口，不是硬件标定精度；跨启动状态变化和Android噪声仍可混淆，不声称直接读到状态。75秒无已识别返回仍立即consumed并先恢复。保留必要的完整输入和现场恢复条件，原始影音仅本地out且不采音频。

S-011与S-012互补两笔均已执行并consumed。S-011(query1)于18:45:34发送4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7，命令2.625秒/断开5.093秒/ADB26.484秒/完成40.547秒；S-012(query2)于18:47:15发送4454dfaa0b00d08d277e921641b51b250850906236770d6514f97cca51f54389，命令2.640秒/断开5.109秒/ADB20.062秒/完成33.781秒。两笔fastboot机型/槽位/解锁首轮精确通过，均无主机恢复reboot、受控回Android，随后各自独立完成/root/A槽/解锁与boot_a/vendor_boot_a设备及本地备份摘要核验通过。278/278与245/245帧解码，已目视核对恢复桌面；全部原始拍屏/视频只留本地out/camera-capture/20261025T184517-system-transport及184658-system-transport，无音频、未上传。

negative-minus-positive的ADB差-6.422秒、完成差-6.766秒，均在执行前固定的-7..-3窗口，支持首个有效状态非Topology13。不是直接状态日志，不能据此称拓扑合格或GOP通过；非Topology集合包含成功状态0和错误1..12，跨启动状态变化仍可混淆。因此D-204“拓扑模型首嫌”优先级下调，不能继续把两个独立SSPP/边框作为已定位故障，更不改相关准入来凑PASS。

进一步固定源码/历史审查：小米52a2f18 sde_hw_intf_v1_get_status仅以INTF_STATUS bit0读FRAME_COUNT，不要求Enable&3==3；历史step15该复合使能前置拒绝，而step18保留使能值稳定并观察至少一路双窗递增获得支持。当前Evidence.c又在首样本和稳定性中对两路强制Enable&3==3，是比原生状态路径和历史成功谓词更强的条件。此为已确认的软件/历史差异，不是本次计数使能数值或确切拒绝点；当前领先假设转为RefreshMode10类的接口/计数前置或稳定性，置信中等。元数据/PCD、revision/mode/格式/几何/地址等拒绝以及成功0仍未排除。

下一步先以新候选区分RefreshMode10及互补，必要时再分首次接口资格和后续等待/稳定性；取得分类后才依据原生status/实际递增评估精确谓词修正。不直接删除Enable门禁、放宽双链路或回旧失败图。若结果非RefreshMode10或直接counter资格已满足/采样成功，应推翻该首嫌排序。新RefreshMode候选尚未实现/构建/资格/执行；本轮新增软件、两份完整资格、互补实测与离线审查均完成，S-001..012不重试，当前无人工/审批待办。

机器证据：reports/enuma-video-topology-S-011-result.json、S-012-result.json、pair-result.json、enuma-video-topology-code.json、enuma-video-topology-pair-code.json，以及enuma-video-counter-gate-review.json。固件8710ebd已推送，实际两Core可执行段与已审查S-010相同，provider仅三条结果指令差异，完整输入保持；55生产选择器场景、330读失败与GOP/拓扑主机和AArch64对象检查、23固件回归与3配对解析回归通过。
