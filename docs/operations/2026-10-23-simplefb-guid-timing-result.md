# SimpleFb完整GUID调用前2/7/2实测

2026-10-23 Asia/Shanghai。用户授权继续实机、自行录像分析，出现看不清的日志时再由手机复现录制。复用固件82ce8a5与已归档晚间候选，不改参数、内存、verified或OEM。

## 已完成三笔及单独的启动前拦截

| 发出时间 +08 | 候选 | ADB返回秒 | Android完成秒 | 恢复核验 |
| --- | --- | --- | --- | --- |
| 18:27:42 | SimpleFb完整GUID point20/2秒 | 16.065 | 31.618 | 完成1/root/原boot与vendor_boot摘要通过 |
| 18:31:06 | 同GUID point20/7秒 | 21.482 | 34.527 | 同上 |
| 18:32:22 | 原2秒同一镜像复测 | 16.069 | 32.175 | 同上 |

7秒减前/后2秒的ADB差为5.417/5.413秒，两个2秒样本仅差0.004秒。用户明确确认三次均未按键。每笔Android和fastboot的身份/槽/root/解锁/备份/原摘要先复核，完整恢复后再执行下一笔，均为fastboot boot，无flash/erase/改槽。

2秒镜像SHA6baf95968292746998d260810596d090b42ed28e991d3157866e93330a093bc4，7秒fea7478b6fe5556c26b3ca592a2c434fb0c881f4f15441685c5de19bc4de977b；完整GUID dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92，GUID-only/ordinal1占位，正常Dispatcher完成固定7秒兜底保持。

18:28一笔7秒准备曾在启动前被拦截：产品/current-slot/unlocked连续五组返回unknown command或Variable Not found，工具returncode仍0，精确输出检查正确拒绝。截图可见FASTBOOT，后来is-userspace=no；未知其原因，不能称错误模式或设备更换。该笔没有issued_at、没有发送boot，更不是7秒候选执行失败。主机普通fastboot reboot恢复Android/root/解锁/槽/原摘要通过后，新会话重新完整通过三字段才允许18:31那笔；未改校验器、未接受缺失字段、未仅凭屏幕FASTBOOT放行。主机无遗留fastboot进程，版本37.0.1；尚不能归因主机工具/USB/安装ABL。

## 能证明什么

相比固定7秒完成兜底，两份2秒候选和7秒候选的可重复约5秒延时响应支持目标point20执行，即SimpleFb的PE入口包装器调用前已到达；这是时序推断，不是直接SEC/DXE日志或主体执行跟踪。point20仍在PE EntryPoint之前，包括构造器尚未执行，不代表RegisterFrameBuffer、GOP安装或返回成功。

实际Android启动完成时间有用户态噪声，故主要比较ADB首次返回，保留全部原始计时。不能用同一7秒时长的单次复位区分目标/完成兜底，也不能用无失败门证明零故障。原233a9d8未知ordinal32的历史无返回不改写；本组已经避免ordinal与GUID误耦合。

## 录像与可读性

四段1920×1080 MJPG（含启动前拦截）全部可解码、帧数匹配单调时钟记录，SHA/计数见[公开报告](../../reports/enuma-evening-simplefb-first-pass.json)。原始视频、逐秒帧、runner和私有目标文件仅out，不入Git。

录像目录依次out/camera-capture/20261023T182720-simplefb-pre-2s、20261023T182825-simplefb-pre-7s（拦截）、20261023T183045-simplefb-pre-7s、20261023T183201-simplefb-pre-2s；对应实际runner为182728、183052、183208，拦截为182832。抽查2秒23秒小米标志/50秒Android锁屏，7秒25秒黑屏/35秒小米/52秒锁屏；未观察需辨认的UEFI诊断文字。不是逐帧OCR，不宣称完全排除短暂文字。菜单/屏幕后端本来未启用，当前无手机补录必要。

下一步复用既有point21观察PE EntryPoint返回；保留禁绘制与Probe早退，不直接放行菜单。同步完成兜底不能救SimpleFb内部挂死，试验需录像/恢复条件，任次无返回停止追加并先恢复。后续构建和运行结果另记，不将本组调用前证据外推。
