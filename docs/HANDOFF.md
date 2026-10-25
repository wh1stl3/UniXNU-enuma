# 当前状态：D-210，计数首拒绝互补产物已审查，准备S-013

2026-10-25T19:07:27+08:00。首样本计数门禁互补候选已完成实际产物审查，当前文档推送后先S-013一笔；S-014待前笔受控返回、独立恢复及文档再次推送。当前Android核验通过，无新boot、无人工/审批待办。

S-013 target1/query1镜像1090b697ce5e6703fa5098735a2a8c9fb65f9df87514b718b0d9f0ce0ad50048，FD54f057e2306d27d7e77f658472fc89a3de63339886afbfd4b1601f839a7b3d6a；S-014 target1/query2镜像54f466c1fa0e617af343c237ac65b132d17b68640196f877c474453a86cff523，FD835147420761982c133e90f5d943f047c78e6de18fe414edf6f8e630ba1da139。均103817216字节、完整96MiB FAT，归档out/inherited-gop/qualified-counter-b93b3bb-q1/q2。实际Core可执行段均与已审查S-010完全一致；两provider全指令比较仅0x112c、0x1188两处元数据拒绝返回常量5/1和0x2874一处csinc条件eq/ne不同；该三条完整差异已逐条审查并绑定SHA40e0c19e8f6a9e2bd1a5ab417f6d2eda64bc46ddf4a9b969a9409144df673552。Core/其余模块、构造器、库、BootShim、完整FAT不变，非provider差异只精确CodeView GUID，实际PE/源码/两级编译宏/FD中R-004记录和不可变资格通过。

Reason5只表示首样本Timing已非零后Enable&3!=3首先拒绝；仍不能给出接口编号、缺失哪一bit或该接口Active值（原条件优先级保持，Enable失败后Active检查不再执行）。此时最多首样本9读，无等待、无管线/Decode、无后续稳定性。stability target2覆盖后续资格和稳定性原因6/9/10/11/13，尚未执行。所有原始判据、读/等待顺序和失败Out保持旧8710ebd，callback oracle覆盖330失败位置及成功/多类原因；164选择器、24固件回归和4配对解析回归通过。

预先固定配对negative-minus-positive：ADB出现和完成两项均+3..+7秒仅支持Reason5，均-7..-3秒仅支持其他原因（含成功Complete），否则ambiguous。两次跨重启状态可能变化，时序不当作直接原因日志。若首门禁匹配，后续稳定性记未执行，不把它写失败；若不匹配，继续选初始Timing/Active或后续稳定性，不能为PASS盲删准入。任何身份、采集、恢复异常或75秒无已识别返回立即consumed、停追加并先恢复。S-001..012及旧失败图不重试。

即时独立Android完成/root/A槽/解锁/设备与备份摘要及1920x1080相机再次通过，现场恢复路径沿已示范受控/长按恢复，不声称75秒是固件自动返回保证。两笔分别完整文档提交推送和门禁后临时fastboot boot，无分区操作。证据reports/enuma-video-reason-code.json、enuma-video-reason-pair-code.json及counter正反资格。

固件固定b93b3bb9c0e8f32baa81c1b2b3d0eb22aedaf107。真实GOP、CPU/SMMU地址/下游拓扑、13项RAM运输、XNU/iPadOS/PMGR/UFS/root/Data仍未实机闭合，ADDRESS/TOPOLOGY不清零。无flash/erase/改槽、内存字段或verified变更；原始影音仅本地out，不录音、不上传Git/Release/CI。
