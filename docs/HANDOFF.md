# 交接：D-168，A单笔已返回并完成恢复核验

2026-10-25 02:11–02:12（北京时间）完成R-016批准的A/detail15一次临时启动。16.187秒观察到ADB，31.312秒结束Android完成/root/分区检查；随后独立核验Android完成、root、A槽、解锁及boot_a/vendor_boot_a设备/备份摘要一致。没有新超时或人工恢复请求；R-016已消耗，本轮不追加B、不重复A。

## 实际结果与证据

- 镜像：29b84e1fac13caa3780f85ef1d1a21e90b6bf061553adfbd277b1c0c8fa72bd4；固件aa9ec66；实机前文档/工具b1cf33c已推送。Core point15/2秒目标门位于DisplayDxe CoreStartImage前，completion fallback7秒非watchdog。
- 发出时间2026-10-24T18:11:21.751570+00:00，boot命令0.390秒返回，0.953秒观察fastboot断开，直接于16.187秒观察ADB，没有观察到回fastboot或执行后续fastboot reboot。
- 单笔out\device-tests\20261025T021107-dxe-driver-return/result.json及reports/enuma-display-boundary-device.json；独立恢复核验out\device-tests\20261025T021235-recovery-reconciliation.json和reports/enuma-recovery-reconciliation.json。旧结果不覆盖。
- 录像415/415帧可解码，50对原图/旋转图，无相机错误。观察到Android桌面→小米/Android启动画面→Android桌面。画面不能算UEFI/原厂显示驱动成功，也不推断不可见按键。

专项实测记录：[A单笔结果](operations/2026-10-25-display-boundary-A-result.md)，机器汇总reports/enuma-display-boundary-A-result.json。

## 结论强度

本次可返回性和恢复核验通过。结合正确GUID、Core机器码位置及16.187秒返回时序，工作判断更支持到达DisplayDxe启动调用前；只有单笔，没有唯一门标记，不宣称已独立证明目标门命中。仍可能有完成兜底/其他复位及Android耗时差异，不能定位R-014旧超时在驱动内部。

未证明DisplayDxe PE入口、EFI_SUCCESS、SetMode、可见GOP、PE_Video、XNU入口或用户态。D-166 ABI/ABL-DTB名称缺口与D-164路线维持，见[交接契约](operations/2026-10-25-handoff-contract.md)和[原厂ABI](operations/2026-10-25-native-display-abi.md)。

## 下一步与边界

若继续，先离线构建并独立资格同源B/detail13；本轮不发B，R-016只批准且已消耗A一次。B用以观察CoreStartImage返回，后续状态/GOP各自验收。没有理由重试A、补未知协议stub、直接改线程/内存/DTB或复活旧像素批准。

R-015暂停；内存字段/映射、verified、像素/背光及破坏性分区仍按原门禁，不因本次返回扩张。任何后续实机仍需文档发布与即时身份/备份/恢复核验；超时停止追加并恢复。当前无人为待办。

本轮结果与当前文档正在提交发布，发布结果以Git/远端摘要为准；实机前门禁已由b1cf33c满足。本轮没有改固件源码/候选、分区或槽位。目标iPadOS17.7.11/21H461、XNU10063.141.1/4KiB、UniXNU5fdbd5d维持。

接手先读AGENTS、STATUS、DECISIONS D-168、NEED-REVIEW R-016及A结果，禁止按旧“尚未执行”记录再次启动A。
