# STATUS

更新：2026-10-23（Asia/Shanghai）。当前唯一真相，历史见WORKLOG。

## 当前结论与停点

**新强停规则及允许有界黑屏/定时返回的澄清已写入AGENTS。主线实测推进到：正常ABI探针与受保护16字节回读均通过；固定marker同次启动匹配，经Bootloader进入不写marker的保留Android后不匹配。按R-002批准边界停止跨复位日志路线，不换地址、不扩大、不启用持久固件日志。**

最后设备为Android，sys.boot_completed=1、root、原boot/vendor_boot摘要正常；测试模块均卸载、临时KO上传已清理。无flash/erase/改槽，无board/bringup-plan/既有内存/512MiB/example/验证标记或固件gitlink/42项源锁变更。无待按键事项。

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
- 默认原生33OEM、已实施无UFS32OEM、拟议SimpleFb30OEM保持区分。固件仍b988fa418de55de2dcaa396d016e30231159d1fe，原25文件/六patch保持。
- 目标仍enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB、UniXNU5fdbd5d/21模块；历史通用内核成功不是本板最终内核。

## 下一步

R-002跨复位日志路线已停，后续候选见NEED-REVIEW/R-003。推荐在用户允许的可控返回探针范围细分真实Image EntryPoint/构造器/异常边界，并准备经核实的UART；不将失败改为新地址重试。另一条同次GOP/USB输出路线需要先有真实可用通道，不能假装已具备。

GOP/map/BDS闭合后再推进ADT/NVRAM、板级最终内核/prelink与最小XNU入口；不从此次Android marker回读推导UEFI/内核启动成功。

上次设备提交217dd29已推送；本里程碑以Git提交/发布记录为准。五件套已更新，参考仓及固件仓未改。
