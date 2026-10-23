# step2 返回、step3 超时与恢复

2026-10-23 Asia/Shanghai。用户要求继续直到进入XNU，沿现有可恢复临时boot授权逐层推进；未到XNU，step3触发无返回停点后已停止追加。

## 设备事实

step2（HandleProtocol）21:20:06临时启动，ADB16.923秒、启动完成与原摘要核验31.178秒，用户确认全程未按键。step3（Mode/Info/跨度）21:24:57临时启动，75秒内未见目标ADB/fastboot，runner记录manual-recovery-needed并退出。21:25:52截图为黑屏；不能据此判定具体执行点。

step3后没有启动step4或任何互补候选。用户按恢复提示回到Android，21:27:29主机核对enuma、sys.boot_completed=1、root、原槽_a、解锁、boot_a/vendor_boot_a原摘要通过。无flash/erase/改槽。

两次启动前由run_enuma_entry_probe.py重新核对唯一目标/备份/原摘要/完成/root/槽/解锁，fastboot三字段无重试通过。依用户偏好不持续拍摄无显示探针；必要前后截图为21:18:24、21:21:07、21:25:52，恢复期间21:26:31起录像120秒，601帧完整解码。原件和标识只存out，用户已明确的无按键/人工恢复事实不重复询问。

## 构建与离线证据

固定固件e286834、54输入锁，复用out/mainline/gop_core_variant.py按step2/3顺序完整构建：stage13/detail16/delay2、selector1、SimpleFb完整GUID、正常完成兜底、禁绘制/Probe早退。每份30 OEM/FD/192B BootShim/v3回读通过，分别归档生成的AutoGen/静态库清单。out/mainline/qualify_gop_candidate.py对比step0源输入、仅step/query可差异的宏、源锁、提供者无Reset库、FD和镜像嵌入字节/摘要通过。

结构化实测、摘要、归档路径见reports/enuma-gop-step23-device.json。step4未构建/启动，旧250849f未重试。build报告现在对应step3，不能当正常启动配置。

已归档实际step3链接DLL/map与入口反汇编。_ModuleEntryPoint位于RVA0x1050；新增Mode指针读从0x1388，Mode字段0x1398，Info指针0x13ac，Info字段0x13c0，跨度运算0x13f8；统一句柄释放0x15a8、warning1/5编码0x15c0。静态指令没有在该审计段解引用FrameBufferBase，也没有调用QueryMode。不能将这些位置当实际异常PC，不能排除代码布局变化、安装前路径、清理或Core路径；无ESR/FAR/PC日志。

下一步先离线拆成Mode指针及所属分配证据、Mode头/Info指针、Info字段、跨度运算、清理/Core返回等边界，不直接重试step3或跳QueryMode。继续实机前须完成新的故障隔离方案和现场恢复门禁。同步兜底不能救卡死，真实scanout、屏幕/XNU仍未验证。未改内存、example或verified。

## XNU输入离线进展

scripts/audit_enuma_donor.py使用固定UniXNU IM4P解析器、本地只读LZFSE工具和固定NativePrelink解析器。原容器SHA256与manifest SHA384匹配，解压得到46,415,872字节普通ARM64 MH_EXECUTE，SHA256 f18b4df865405f2a287b84977d7aca745e056d656d9fc9df1662970ce2969de7，完全匹配固定sheng同donor的独立pin。解码器源码版本本轮未独立确认，但二进制哈希已锁且输出受上述固定pin约束。

237个donor模块；以已审计platform-kernel为源，AMFI、APFS及参考roots三组闭包/指针绑定计划通过。参考-0x1000000只用于离线比较，没有采用为enuma放置方案或修改board。未emit预链接镜像，AMFI initializer/ABI、完整ADT、载荷运输、实际内存/EBS/入口仍未闭合。报告enuma-donor-decompression.json与enuma-donor-closure-audit.json；可重放命令为Windows Python -X utf8 -B scripts/audit_enuma_donor.py。
