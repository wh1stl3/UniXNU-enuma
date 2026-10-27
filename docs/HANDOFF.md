# 当前：registration-v5 新固件与离线资格完成（2026-10-27）

本轮离线，未查询/操作设备。v4两组完整字符串已确认，仅观察到call4成功返回；用户确认设备无按键自行回Android，恢复独立核验通过。v4原始trial及手机retry均consumed，R027和旧候选冻结，共享主线只读。

最大可操作嫌疑为call4之后的guided-section注册区间：16字节复制→0x5cc4 InstallConfigurationTable→后续构造/主入口；对该区间置信中等，对唯一故障指令置信低，S02窗口清理仍为竞争解释。具体指令、边界、推翻条件及新候选观测解释见[registration-v5分析](operations/2026-10-27-oem-registration-v5.md)。缺少SID/返回画面不证明最后可见位置死锁。

新镜像out/oem-registration-20261027/qualification2/image.img，3153920字节，SHA256 `f9bd10078db5b049e7ad0cd050300c872cdcd1d0d975b6ed3065e4b03dac650d`。完整FD：out/oem-registration-20261027/build1/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd，SHA256 `f83b1869f65377ec2b4af4bdc69f1f64f0fcf41a3a296c6ea795a76d3b7fe6d5`。

新scope oem-registration-v5，trial 4549e5e6-22a7-4e4d-bd8a-4ee65d8e621e，尚未claim或上机。只在此scope包装原厂返回地址0x5cc8的InstallConfigurationTable，其他配置表调用原样转发、不占追踪序号。call0..4不画窗；E01/S02=call5配置安装前/真实返回，E03/S04=SID前/后，S05=真实CoreStartImage返回。原厂DisplayDxe不改，私有SystemTable同步修复保留；ROI(64,96)320×160/每窗8秒/最多五窗40秒保持。

完整FD、原厂模块审计、Boot v3打包/解包回读通过。31项WSL Python、check3 ASan/UBSan与真实Core扩容/通知及两处删除负测、binding1精确PE重定位/错PE拒绝和AArch64板级对象通过；最终机器码32处原运行路径+52处同步/选择/注册删除负测及一处GUID变异均拒绝。qualification1保留其旧分支布局检查失败，qualification2按实际新增指令审查后通过，未为满足检查重写FD。

执行器已修复只等fastboot：观察断开后也接受绑定enuma Android完成，并完整核验root/槽/解锁/双分区摘要；直接返回、错误身份、fastboot残留模拟验证均只boot一次且无分区操作。ADB终点不推断用户是否按键，人工恢复事实继续按现场反馈记录。

固件提交fd94b26；构建是以f82039e为基线的工作树快照，保留manifest，不称提交后重编。脱敏报告reports/enuma-oem-registration-candidate.json。尚未确认本轮远端发布；最后设备状态沿上一笔Android恢复核验，本轮没有重新观测。下一实测须完成当前文档发布及即时身份/备份、当次手机拍摄与人工恢复条件；本轮任务到编出新固件，不追加实机。原始媒体仅本地，无新内存base/size、verified或分区范围变更。
