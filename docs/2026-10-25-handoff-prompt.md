# 当前状态：D-208，互补支持非Topology，Android已核验

S-011与S-012互补两笔均已执行并consumed。S-011(query1)于18:45:34发送4f413f286bba150e007e2333d9aa466fef98d046bc23ebb05256d01f213261a7，命令2.625秒/断开5.093秒/ADB26.484秒/完成40.547秒；S-012(query2)于18:47:15发送4454dfaa0b00d08d277e921641b51b250850906236770d6514f97cca51f54389，命令2.640秒/断开5.109秒/ADB20.062秒/完成33.781秒。两笔fastboot机型/槽位/解锁首轮精确通过，均无主机恢复reboot、受控回Android，随后各自独立完成/root/A槽/解锁与boot_a/vendor_boot_a设备及本地备份摘要核验通过。278/278与245/245帧解码，已目视核对恢复桌面；全部原始拍屏/视频只留本地out/camera-capture/20261025T184517-system-transport及184658-system-transport，无音频、未上传。

negative-minus-positive的ADB差-6.422秒、完成差-6.766秒，均在执行前固定的-7..-3窗口，支持首个有效状态非Topology13。不是直接状态日志，不能据此称拓扑合格或GOP通过；非Topology集合包含成功状态0和错误1..12，跨启动状态变化仍可混淆。因此D-204“拓扑模型首嫌”优先级下调，不能继续把两个独立SSPP/边框作为已定位故障，更不改相关准入来凑PASS。

进一步固定源码/历史审查：小米52a2f18 sde_hw_intf_v1_get_status仅以INTF_STATUS bit0读FRAME_COUNT，不要求Enable&3==3；历史step15该复合使能前置拒绝，而step18保留使能值稳定并观察至少一路双窗递增获得支持。当前Evidence.c又在首样本和稳定性中对两路强制Enable&3==3，是比原生状态路径和历史成功谓词更强的条件。此为已确认的软件/历史差异，不是本次计数使能数值或确切拒绝点；当前领先假设转为RefreshMode10类的接口/计数前置或稳定性，置信中等。元数据/PCD、revision/mode/格式/几何/地址等拒绝以及成功0仍未排除。

下一步先以新候选区分RefreshMode10及互补，必要时再分首次接口资格和后续等待/稳定性；取得分类后才依据原生status/实际递增评估精确谓词修正。不直接删除Enable门禁、放宽双链路或回旧失败图。若结果非RefreshMode10或直接counter资格已满足/采样成功，应推翻该首嫌排序。新RefreshMode候选尚未实现/构建/资格/执行；本轮新增软件、两份完整资格、互补实测与离线审查均完成，S-001..012不重试，当前无人工/审批待办。

机器证据：reports/enuma-video-topology-S-011-result.json、S-012-result.json、pair-result.json、enuma-video-topology-code.json、enuma-video-topology-pair-code.json，以及enuma-video-counter-gate-review.json。固件8710ebd已推送，实际两Core可执行段与已审查S-010相同，provider仅三条结果指令差异，完整输入保持；55生产选择器场景、330读失败与GOP/拓扑主机和AArch64对象检查、23固件回归与3配对解析回归通过。

真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零；无flash/erase/改槽、内存字段或verified变化。
