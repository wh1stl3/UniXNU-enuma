# 当前：registration-v5 已单次消费，自行回 Android，媒体待判读（2026-10-27）

按用户“随时准备拍照 可以开始了”的本次条件执行，未复用旧录像状态。固件fd94b26及设备仓准备提交c878c8d已正常发布至各自GitHub的oem-progress-20261027，执行前ls-remote核验精确提交匹配；未向固件本地origin或main推送。即时enuma/Android完成/root/A槽/解锁、原boot_a/vendor_boot_a及本地备份摘要通过后，仅一次临时fastboot boot。

registration-v5 trial 4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e已claim/consumed；镜像out/oem-registration-20261027/qualification3/image.img，3153920字节，SHA256 f9bd10078db5b049e7ad0cd050300c872cdcd1d0d975b6ed3065e4b03dac650d。fastboot boot返回0，传输调用0.394秒；观察到fastboot断开后绑定enuma Android完成。用户明确“没有操作，设备自行返回”。22:05独立核验enuma、boot_completed=1、root、A槽、解锁及原双分区/本地备份摘要全部通过。没有追加启动、flash/erase/改槽。无需恢复按键；当前没有设备硬停。

本次现场日志内容尚未获得媒体，不能断言配置表安装、SID或CoreStartImage返回。最大可操作嫌疑仍是旧v4 call4成功返回后的guided-section注册区间，S02窗口恢复仍是竞争解释；本次Android返回只确认可控终点，不替代驱动/显示结论。v5页面含义、失败解释及代码依据见[分析](operations/2026-10-27-oem-registration-v5.md)。

原始媒体唯一当前收集目录：D:/Code/PortingiOS/enuma/Media-enuma/OEM-registration-v5-20261027-4549e5e6。先前误建的out/device-tests/.../media为空且不使用；用户已明确纠正至Media-enuma。本轮先独立查看原图/视频、保存完整五行和摘要，再展示供用户核对，不能按预期补猜。媒体/out/备份/标识及二进制不上Git或云端。

本次结果reports/enuma-oem-registration-v5-trial-20261027.json；证据out/device-tests/oem-4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e和out/oem-registration-live-20261027（authorization、publication、preflight、postcheck、human-return-confirmation）。原始runner状态保留pending-user-confirmation快照，独立human-return-confirmation关闭按键事实待办，不回写历史字节。

共享主线只读，R027及旧候选冻结；本次v5不重试。现成FD/qualification摘要保持，2446项源绑定已核验，无源码修改或重新构建；仍是f82039e基线工作树快照。下一步先判读本次媒体并结合精确PE和代码归因，再决定独立新软件；新输入必须新资格，不复用本次账本。生产GOP、ConOut、BDS、实体输入和XNU仍未验收。
