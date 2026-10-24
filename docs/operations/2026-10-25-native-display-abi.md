# 原厂DisplayDxe ABI离线审计（D-166）

输入严格绑定R-014镜像922972e61b0e4e3d7b7c931b53b76531a2db2a08504c6794263e5ff3f5ab1a75和原厂XBL 7ac67cbf4c7870a972cb4ffd9cc09d5db1c96b7f4a5abc7a80c0da9cabc65057。审计从两者独立解码FV取出DisplayDxe，PE逐字节相同：315392字节，SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425；ARM64，ImageBase=0，PE入口RVA=0x1000。以下地址均为此PE的RVA，不是实机加载地址。

可复现工具scripts/audit_display_handoff.py；机器证据reports/enuma-display-handoff-audit.json。使用Capstone 5.0.9、pefile 2024.8.26、uefi_firmware 1.16，隔离安装在out/reverse-tools。没有依赖字符串搜索来认定调用发生。

Windows复现：`python -B scripts/audit_display_handoff.py --tool-path out/reverse-tools`；负例：`python -B scripts/check_display_handoff_audit.py --tool-path out/reverse-tools`。后者从不可变R-014镜像提取原PE，确认将真实BL改NOP、截断FV或FDT都会被拒绝；无需也不会启动设备。

## 已证实的真实调用关系

| 范围/地址 | 二进制行为 | 解释及限制 |
| --- | --- | --- |
| 0x1bd8–0x1bfc | 将0x2da98的EnableDisplayThread传给0x3874，检查返回状态和配置值 | 真实配置读取，不证明实机已执行到该点 |
| 0x1c00–0x1c18 | DispInit名称和输出锁句柄传给0x6008；精确比较EFI_UNSUPPORTED | 有明确无运行时降级分支 |
| 0x6008–0x60c0 | 从全局Kernel指针取Lock表（+0x58），检查版本0x10005；调用InitLock，旧版本有兼容路径 | 与EFIKernelInterface.h的Lock布局相符；不使用stub |
| 0x1c1c–0x1c3c | 名称Disp、线程入口0x1f38、参数NULL、优先级25、栈0x3000传给0x5f78 | 线程真实创建；硬件运行结果未验证 |
| 0x5f78–0x5f94 | Kernel->Thread（+0x18）->首函数，Kernel为空则返回NULL | 对应ThreadCreate；空指针有显式处理 |
| 0x1c50–0x1c5c | 调0x5fe8后调0x5f98 | 后者取Thread表+8，对应ThreadResume；前者取+0x58，未仅凭偏移给它强行命名 |
| 0x1f38–0x1f5c | 将全局GOP对象（0x3e398）与ModeNumber=0传给0x2014 | 线程入口会调用模式设置函数 |
| 0x2014及0x2110–0x214c | 模式校验及配置路径；线程标志非0时经0x60c4获取锁并更新状态 | SetMode不是纯元数据函数，可能清缓冲/操作硬件，不能作为只读探针调用 |

## Kernel Protocol及HOB回退

0x612c是初始化封装：0x6158构造Kernel Protocol GUID B5062BE7-170B-4A32-BE21-689262FF4399，0x6164从Boot Services表取+0x140，0x6168间接调用LocateProtocol，输出到全局0x44430。失败或输出NULL则0x61ac调用HOB回退。

回退0x61f4–0x6214以0x3e418的GUID 8ec2bd8d-56d7-49ef-8796-631778f8ebf8查找HOB，非空时读+0x18，即GUID HOB头后的UINT64地址。该GUID与当前源码gEfiSchedulerInterfaceHobGuid一致。0x1400处构造函数链确实调用0x612c。LocateProtocol/HOB两条路都需要检查，不能只看FD名称缺口就宣告全局Kernel必定为NULL。

同次旁证：已有EnvDxe PE也引用相同Kernel/HOB GUID，并有类似LocateProtocol/HOB消费路径。这不是协议安装提供者证明；EnvDxe存在不能自动补齐调度器。

## 一个改变判读的重要分支

若Kernel为空，0x6008在0x60b0返回EFI_UNSUPPORTED；0x1c18跳0x1bec，把线程标志清0且将返回状态置0，然后走公共返回。线程创建返回NULL也走相同降级。因此：

- 即使CoreStartImage返回EFI_SUCCESS，也可能未创建显示线程，且没有通过该线程调用SetMode。
- 无Kernel这一条件本身不要求驱动在此处无限挂死；不能用它单独解释R-014的75秒无返回。
- 关闭EnableDisplayThread不会自动触发这段入口的同步SetMode；不能仅改0就称适配完成。外部显式调用SetMode可能走其他真实路径，必须另审其参数、锁及硬件写入范围。

0x1b70可见协议安装调用早于0x1bd8读取线程配置，进一步说明“GOP安装”和“显示模式初始化”是不同验收点。模式设置前仍可能在更早硬件初始化、构造函数、其他驱动或异常/复位路径出问题，本审计不是完整调用图或挂点定位。

## 下一步分流

先以正确GUID的A/detail15候选定位是否到达DisplayDxe启动边界，不执行它的PE入口。A若取得有效命中，后续优先核查运行时Kernel Protocol与scheduler HOB的实际存在和兼容性；再决定B/detail13与独立GOP/模式审计。不能将静态地址当动态指针，不能调用未知表来探测ABI。

实际协议/HOB/线程运行、精确EFI_STATUS、GOP模式及可见显示仍未验证。所有硬件门禁维持，R-015不复活。
