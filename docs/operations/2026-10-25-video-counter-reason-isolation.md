

## D-209，首计数门禁与后续稳定性分类源码通过，完整构建中

2026-10-25T18:59:20+08:00。首返回原因记录及计数/稳定性互补选择器主机通过，完整构建中，无S-013/S-014。设备最后S-012独立Android/root/A槽/解锁/原分区与备份核验通过；S-001..012均consumed。

用户明确要求隔离计数使能和稳定性，完成审计后直接上机。新Detailed采样只记录首个返回原因；保留旧版完整谓词、短路优先级、原330读/两次100ms/最大0x6c26c、失败Out不变，不在拒绝后继续。原因枚举区分首样本Timing/Active、首样本Enable、后续Enable/接口变化、等待失败、配置变化、接口稳定性、Frame不推进和其他流水线/参数失败。counter-enable target1只匹配首样本Enable&3!=3（reason5）；stability target2匹配后续资格/配置/接口/帧失败reason6/9/10/11/13。首样本计数门禁先失败时，后续稳定性未执行，不把未执行写失败。

实际生产选择器164场景通过；固定旧8710ebd源码作为oracle，对330读失败位置及成功路径逐一比较完整回调/等待顺序、返回值和Out字节一致；新增首/后续计数、Timing/Active、等待、配置变动和计数停滞原因用例通过，原GOP/拓扑及AArch64对象保持。24固件Python回归、4配对解析回归通过。固件源码已提交推送，新完整FD/PE/编译宏/打包/归档资格正在完成；当前无新boot。

预先计划：S-013 target1/query1，受控回Android并独立核验、当前文档再次提交推送后才S-014 target1/query2。不沿用旧已消耗镜像。两笔同源/同完整FAT/同Core终止点，query1匹配原因2秒、其他有效原因7秒，query2精确反转；不增加旧长延时编码。配对negative-minus-positive的ADB出现和Android完成两指标均+3..+7秒仅支持选中原因，均-7..-3秒仅支持其他原因；其余ambiguous。分类不等于直接状态数值，未匹配集合含成功完成，跨重启继承变化和Android噪声仍是限制。75秒无已识别返回立即consumed、停追加并先恢复。若target1不支持，再按实际结果选首次接口或后续稳定性，不能盲删Enable门禁或放宽显示准入。

执行前必须通过所有源码/实际产物资格、当前文档提交推送及即时唯一enuma身份/备份/fastboot精确机型槽位解锁/相机/恢复门禁。历史S-011/S-012支持非Topology（包含成功0），仍不能定位本次确切拒绝点。

固件固定b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107。真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。


## D-210，计数首拒绝互补产物已审查，准备S-013

2026-10-25T19:07:27+08:00。首样本计数门禁互补候选已完成实际产物审查，当前文档推送后先S-013一笔；S-014待前笔受控返回、独立恢复及文档再次推送。当前Android核验通过，无新boot、无人工/审批待办。

S-013 target1/query1镜像1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，FD54f057e2306d27d7e77f658472fc89a3de63339886afbfd4b1601f839a7b3d6a；S-014 target1/query2镜像54f466c1fa0e617af343c237ac65b132d17b68640196f877c474453a86cff523，FD835147420761982c133e90f5d943f047c78e6de18fe414edf6f8e630ba1da139。均103817216字节、完整96MiB FAT，归档out/inherited-gop/qualified-counter-b93b3bb-q1/q2。实际Core可执行段均与已审查S-010完全一致；两provider全指令比较仅0x112c、0x1188两处元数据拒绝返回常量5/1和0x2874一处csinc条件eq/ne不同；该三条完整差异已逐条审查并绑定SHA40e0c19e8f6a9e2bd1a5ab417f6d2eda64bc46ddf4a9b969a9409144df673552。Core/其余模块、构造器、库、BootShim、完整FAT不变，非provider差异只精确CodeView GUID，实际PE/源码/两级编译宏/FD中R-004记录和不可变资格通过。

Reason5只表示首样本Timing已非零后Enable&3!=3首先拒绝；仍不能给出接口编号、缺失哪一bit或该接口Active值（原条件优先级保持，Enable失败后Active检查不再执行）。此时最多首样本9读，无等待、无管线/Decode、无后续稳定性。stability target2覆盖后续资格和稳定性原因6/9/10/11/13，尚未执行。所有原始判据、读/等待顺序和失败Out保持旧8710ebd，callback oracle覆盖330失败位置及成功/多类原因；164选择器、24固件回归和4配对解析回归通过。

预先固定配对negative-minus-positive：ADB出现和完成两项均+3..+7秒仅支持Reason5，均-7..-3秒仅支持其他原因（含成功Complete），否则ambiguous。两次跨重启状态可能变化，时序不当作直接原因日志。若首门禁匹配，后续稳定性记未执行，不把它写失败；若不匹配，继续选初始Timing/Active或后续稳定性，不能为PASS盲删准入。任何身份、采集、恢复异常或75秒无已识别返回立即consumed、停追加并先恢复。S-001..012及旧失败图不重试。

即时独立Android完成/root/A槽/解锁/设备与备份摘要及1920x1080相机再次通过，现场恢复路径沿已示范受控/长按恢复，不声称75秒是固件自动返回保证。两笔分别完整文档提交推送和门禁后临时fastboot boot，无分区操作。证据reports/enuma-video-reason-code.json、enuma-video-reason-pair-code.json及counter正反资格。

固件固定b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107。真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。


## D-211，S-013受控返回已核验，准备互补S-014

2026-10-25T19:09:12+08:00。S-013已受控回Android并独立核验完成/root/A槽/解锁/原分区与备份摘要通过，已consumed；当前文档推送后按原计划执行互补S-014一笔。

S-013 target1/query1于19:07:50发送1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，命令2.640秒/断开5.109秒/ADB20.078秒/完成34.343秒，无主机恢复reboot。248/248帧解码，已目视确认恢复桌面；原始影音只本地out/camera-capture/20261025T190733-system-transport，无音频。证据reports/enuma-video-counter-S-013-result.json，原始trial out/device-tests/20261025T190736-system-transport/result.json，独立恢复out\device-tests\20261025T190837-recovery-reconciliation.json。

短返回初步支持首样本Enable门禁Reason5，尚未完成互补，不能确证原因或位值；后续稳定性仍未获证据。当前未执行S-014，文档提交推送后沿原固定资格执行target1/query2。保持source b93b3bb、实际Core/provider审查、完整FAT和既有精确身份/备份/采集/恢复门禁；75秒无已识别返回停止追加并先恢复，所有已执行镜像不重试。

配对预先窗口不变：negative-minus-positive的ADB出现和完成均+3..+7秒才支持选中Reason5，均-7..-3秒支持其他有效原因（含成功Complete），其他记ambiguous。此为间接分类；先拒绝条件后的项记未执行。当前无人工或新增审批待办。

固件固定b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107。真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。


## D-212，互补支持首计数门禁拒绝，后续稳定性未到达，Android已核验

2026-10-25T19:12:38+08:00。S-013/S-014互补时序支持首样本Enable门禁Reason5，后续稳定性按该路径未执行；两笔Android/root/A槽/解锁/原分区与备份独立核验通过，均consumed。下一步独立验证原生双路计数推进，不放宽GOP准入。

S-013 target1/query1于19:07:50发送1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，命令2.640秒/断开5.109秒/ADB20.078秒/完成34.343秒；S-014 target1/query2于19:09:35发送54f466c1fa0e617af343c237ac65b132d17b68640196f877c474453a86cff523，命令2.641秒/断开5.125秒/ADB26.516秒/完成41.063秒。两笔fastboot product=enuma/current-slot=a/unlocked=yes首轮精确通过，无主机恢复reboot，随后分别独立核验Android完成/root/A槽/解锁及boot_a/vendor_boot_a设备与本地备份摘要全部通过。248/248与279/279拍屏帧解码，已目视核对恢复桌面；原始影音仅out/camera-capture/20261025T190733-system-transport及190918-system-transport，无音频、未上传。

negative-minus-positive：ADB+6.438秒、完成+6.720秒，均在执行前固定的+3..+7秒窗口。支持Reason5首样本CounterEnable条件先拒绝（中等置信），不是直接原因/寄存器数值日志，也不称GOP/显示成功。跨启动继承变化和Android噪声仍可混淆；S-010/S-011/S-012的历史结果不改写。

源码路径含义：Reason5只在N=0且Timing非零、Enable&3!=3时赋值，随后立即返回；按该分类成立的前提，采样回调最多9读、零等待，完整CTL/SSPP/LM采集、Decode及后续稳定性均未到达。不能称稳定性失败、Frame不递增、某接口不活动或某个bit为零；拒绝接口与实际Enable值未知，Enable检查之后的Active条件也可能尚未执行。实际执行读数仍未知，9为条件路径上限，不当作数字转储。

当前主判断从泛化RefreshMode/稳定性收敛到过强的首样本Enable资格门：它阻断了对实际帧进展的观察。固定小米52a2f18 v1 get_status读取活动接口FrameCount不要求Enable&3==3；旧step15使能复合条件拒绝与step18原生至少一路双窗递增支持只作为同方向历史旁证，不能当本次两路数值。不能直接删条件换PASS，也不修改CounterEnable或时钟。

下一步：实现独立诊断前缀，沿原映射仅观察两路原生活动状态、Timing与Enable稳定值、两窗各1..64非回绕Frame增量；不把Enable是否精确3作为其提前返回条件，不访问尚未证明安全的后续管线银行、不发布GOP。该前缀是新的独立观测，不等于放宽完整EnumaSampleVideo准入；成功后才评估有依据的原生资格修正，失败再细分活动性/稳定性/计数进展。新前缀尚未实现/构建/资格/上机，完整采样所有原条件保持。若新证据显示原因非5、两路不活动/不稳定或CounterEnable实际已满足，应修正当前判断。

新增Detailed接口保留旧入口语义：固定8710ebd oracle覆盖330失败位置和成功的完整回调/等待顺序、返回状态、Out字节；首/后续计数、初始接口、等待、配置变动及Frame停滞原因用例通过，164选择器场景、24固件和4配对解析回归及AArch64对象通过。实际两FD/PE/宏/R-004/完整FAT/BootShim不可变资格通过，实际Core可执行段与已审查S-010相同，provider仅三条映射指令差异已人工审查并摘要绑定，现场运行前提交均已推送（d6c9dfa资格、f399374首笔结果）。

证据reports/enuma-video-counter-S-013-result.json、S-014-result.json、pair-result.json、path-interpretation.json，enuma-video-reason-code.json及pair-code.json；源码b93b3bb已推送。S-001..014及旧失败图不重试，当前无人工/审批待办。

固件固定b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107。真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。
