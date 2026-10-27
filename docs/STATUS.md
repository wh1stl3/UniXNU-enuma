# 当前：v6单次已消费，主入口E01确认，自行回Android（2026-10-27）

用户本次“上机”并重新确认“拍摄已就绪，在场可恢复”。准备提交f7dc965及固件d393211执行前远端精确核验通过；Git直连连接失败保留，改用Windows已启用系统代理的单命令http.proxy完成推送及核验，没有改全局Git/系统代理或共享主线。即时身份/原备份/恢复门禁通过后仅一次临时fastboot boot。

scope oem-main-entry-v6，trial cfee120a-a6a4-4b02-bcff-21b1aa82372f已claim/consumed，镜像c372c5e89a25aabe8d025469364c7d160be7c034481f5cec5e0283cc3338036d（out/oem-main-entry-20261027/qualification2/image.img，3153920字节）；原资格/FD/镜像不回写。fastboot调用0.401秒返回0；执行器观察断开后Android完成。用户明确没有操作、设备自行返回；23:06独立核验enuma、boot_completed=1、root、A槽、解锁及原boot_a/vendor_boot_a和本地备份摘要全部通过。无追加启动、分区写入、改槽或恢复欠项，没有设备硬停。

目录内一张原图已先独立判读保存（independent-read1.json），再严格解码和本次session绑定，用户确认五行逐字一致且现场只有这一页：

```text
E01C0000000000000006
Q000000000000000C
O0000000000003608
E
G91C9B0CA3369EA72
```

照片SHA256 7a8f944ea3b53063c339cc34b6cdbf67c7b1fb7a5c4a5005fe176c39106f4b8d。E01/C6/Qc/RVA3608支持原厂最后注册构造返回并进入主入口ChipInfo查询包装入口；本次没有注册区间/服务返回侧绘制，不能再说本次未到主入口。E01可见先于窗口恢复/读回及原始LocateProtocol调用，所以不证明查询执行/返回、GetChipFamily、SID或CoreStartImage返回。没有S02/S04是v6设计，不是缺失返回记录。

下一最大可操作区间为E01窗口收尾/包装器转发→ChipInfo原始查询→接口+48 GetChipFamily及条件协议方法/事件创建→SID入口和后续输出准入。唯一根因置信低，优先诊断取证收尾/出口，不能根据单页判ChipInfo/SID内部死锁。v6绕过旧v5 S02绘制并到达主入口，只支持本次路径到达；不反推v5收尾通过或把变化唯一归因为移除窗口。实际代码和后续方案依据见[main-entry-v6分析](operations/2026-10-27-oem-main-entry-v6.md)。

当前无人工媒体/字符串/恢复欠项；v6不重试，下一新软件须独立资格、当前发布及当次拍摄/即时身份备份恢复门禁，旧就绪不复用。共享主线只读、R027及旧候选冻结；内存base/size、verified、分区边界不变。生产GOP/ConOut/BDS/实体输入/XNU仍未验收。

结果reports/enuma-oem-main-entry-v6-trial-20261027.json；证据out/device-tests/oem-cfee120a-a6a4-4b02-bcff-21b1aa82372f及out/oem-main-entry-live-20261027（publication-verified、preflight、postcheck、human-return-confirmation、media-review）。runner的pending-user-confirmation和独立初读pending快照保留，通过新确认文件闭合，不覆盖历史证据。independent-read.json为首次写入异常留下的空文件，有效初读为independent-read1.json。

原始媒体只在D:/Code/PortingiOS/enuma/Media-enuma/OEM-main-entry-v6-20261027-cfee120a；原图/裁图/out/二进制/备份/设备标识不入Git或云端。本轮结果提交/发布以git log及result-publication.json为准。
