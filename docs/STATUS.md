# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前结论与进行中工作

**用户已选择R-003推荐方案。已接入真正Image->EntryPoint前后/Exit返回门；无UFS的Display完整GUID实际PE调用前point20完成2/7/2实测，支持到达该调用前。直接C返回后point21未观察到短延时返回（ADB33.063秒/Android45.293秒），已恢复；point22正在构建，继续检查Exit路径。尚不能确认PE内部构造器/主体执行或返回，也没有GOP/XNU证明。**

point20三次ADB16.977/22.272/16.367秒，差5.295/5.905秒，全部样本保留；均自动Android/root/原boot和vendor_boot摘要正常。无flash/erase/改槽，无board/bringup-plan/内存/512MiB/example/验证标记变化。R-002跨复位日志仍停止，不再写RAM标记。

新固件gitlink a927ca1（入口功能0924fbd + Image.c LF基线修复），43项源锁；原25迁移文件/六patch及其余32OEM PE/DEPEX保持字节。35组实际头/bridge ASan/UBSan、45项Python/补丁重复重放通过；两源CI回读成功。官方backend真实构建/32OEM/BootShim/v3审计及补丁还原已通过两份point20候选。此提交默认完整33模式未重建，不以无UFS测试代替完整存储。

详见 [真实PE细分门](operations/2026-10-23-direct-pe-entry-gates.md)。最终结论待point22后门实测，点20只能证明到达PE调用前；原厂入口RVA0x1000仍含系统表/配置表包装。

## 当前授权

- 生成镜像无需硬停；已授权范围内继续主线设备工作，取代前几轮暂不操作实机的当前限制。
- 过程日志与至少一条Android/fastboot/TWRP可控恢复路径应先核对。用户随后明确黑屏和定时复位可以：有身份/备份/可控返回证据的有界临时探针，不因缺完整早期日志单独停；不能把返回当驱动成功。
- 无法恢复、超出授权、内存字段/verified变更仍按AGENTS停。TWRP未测试，不声称已验证。R-002存活失败即停、不换址边界未被取消。
- 遇难题评估同SoC UniXNU/UEFI参考仓的持久规则保持。

## R-002本轮实测

1. 新预检确认唯一enuma/实际内核/Android/root/槽位/备份摘要，活动FDT唯一保留0x9fff7000/0x8000、8页全reserved，随后每次回读前重新核对。
2. normal insmod/rmmod ABI探针通过：实际模块出现/消失，先启动的dmesg流收到新ABI_OK记录。16字节reader也正常加载、记录、卸载，运行时ABI不再只是离线推断；不代表持久性。
3. 新增显式--seed-marker封装，只在FDT保留成功后写入[0x9fff7000,0x9fff7010)固定16字节；同次Android回读完全匹配。seed镜像SHA256 3b1a685ef8b45a72587b28e58dda3801b685e79d0c91981a9adcfc3116c7f764，01:56:59启动，ADB16.061秒/完成30.625秒。
4. 随后经Bootloader临时启动原有不写marker镜像e0bd9b25d6e472a52735893dac970bb6f475e6c5394e6d878c615e54d6fc0e42，01:58:14，ADB16.044秒/完成29.605秒；保护与正常ABI/reader仍通过，但marker不同。没有经过未保留普通Linux，没有在回读镜像重新种marker。
5. 结论仅为当前完整路径不保持marker，不能单独归因某个Bootloader清零点。已停止该跨复位日志路线；未写SEC/DXE日志、没有改地址或扩大。

实际writer host ASan/UBSan（guard/null/16-byte边界与canary/重复）、21组实际FDT sanitizer及45项Python通过；seed镜像固定AOSP回读通过。scripts/run_log_reader.py复用实际模块、FDT/页保护与日志流门禁，未来存活调用加--require-seed，不匹配exit2。原始marker内容只在out私有日志，公开固定测试marker及结果。

详见 [本轮实测交接](operations/2026-10-23-runtime-abi-marker-survival.md) 和 reports/enuma-marker-survival-device.json。

## GOP与XNU主线

- UFS及无UFS时DisplayDxe仍只有CoreStartImage前门支持证据，后门未观察。包装器/库构造器/主体/异常与具体改写阶段未知，没有GOP/map/BDS/DarwinBoot/XNU/NT36523运行证明。
- SimpleFb离线审计已完成，优先复用Mu核心，真实入口base/stride/格式/线性布局/跨度/存活仍缺。当前只读DRM state两个路径正文为不存在（虽然su返回0），panel enabled不等于入口几何。没有启用SimpleFb或DFPS尾部日志。
- 默认原生33OEM、已实施无UFS32OEM、拟议SimpleFb30OEM保持区分。固件现为a927ca1，原25文件/六patch保持。
- 目标仍enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块；历史通用内核成功不是本板最终内核。

## 下一步

R-002跨复位日志路线已停；用户已选择NEED-REVIEW/R-003推荐A，正在细分真实Image EntryPoint/构造器/异常边界，不再等重复批准。不将失败改为新地址重试。另一条同次GOP/USB输出路线需要先有真实可用通道，不能假装已具备。

GOP/map/BDS闭合后再推进ADT/NVRAM、板级最终内核/prelink与最小XNU入口；不从此次Android marker回读推导UEFI/内核启动成功。

上次设备提交f97a91c已推送；本里程碑以Git提交/发布记录为准。五件套已更新，参考仓及固件仓未改。
