# 受控GOP Blt屏幕诊断后端

2026-10-23 Asia/Shanghai。继续屏幕路线的离线实现。本轮没有ADB/fastboot查询、启动、写入或新固件构建，晚间82ce8a5三候选和源锁保持不变。

## 实际完成的代码

[EnumaScreen](../../diagnostics/screen/EnumaScreen.c)及[接口/约束](../../diagnostics/screen/README.md)实现文本、64位十六进制状态/地址和十二行快照页。阶段、EFI状态、GOP尺寸/stride/format/base/span、GetMap状态和最大空闲段由调用者提供；后端不读取设备或创建这些观测值，也不证明其来源。阶段值不自动等同现有Dispatcher detail编号。

复用固定DarwinBoot d099354d的AOSP BSD字模与两个6行打包半区的解码方式，保留字模版权/许可于out暂存。没有复用其直接FrameBufferBase写入路径。字模依赖继续由config/porting-sources.lock.json约束，不复制上游整树。

每行只发一次EfiBltBufferToVideo，通过标准Blt像素缓冲抽象物理格式，不解引用帧缓冲基址、不手算物理stride、不写缓存/MMIO。独立测试使用PixelBltOnly且基址/跨度为零，确保没有偷偷依赖线性显存；这不放宽DarwinBoot仍要求BGRX32的契约。

初始化要求显式矩形在当前模式范围内，最大40列/12行，单元12×28像素。调用者提供的行scratch最大53760字节，不占固件大栈、不用新固定地址、显示区尾部或R-002 RAM。scratch须与context/GOP/输入文本分离，caller保证生命周期，仅application TPL、EBS之前单上下文使用。

写入开关必须显式传入，future caller默认false。true只代表caller依据已核对的提供者/实际scanout/像素范围允许调用，不是自动硬件验证。模式、Info/Blt指针或尺寸/格式变化后关闭；Blt错误锁存并停止后续输出。Busy拒绝回调重入，不是跨CPU锁。Blt本身挂死无法由此模块恢复，不称有界返回或看门狗。

## 验证结果及预览

[checker](../../scripts/check_screen_diagnostics.py)先核对固定Mu归档和字模SHA，提取真实UEFI头进行host ASan/UBSan与AArch64 COFF编译，不用mock UEFI结构类型。服务仅Blt回调为host替身。

[测试](../../tests/enuma_screen.c)覆盖默认禁写、无物理帧缓冲的BltOnly、scratch/坐标/行号/输入长度/格式边界、固定A字模像素、未知字符替代、EFI错误最高位的十六进制图形对照、边缘矩形、回调重入、模式/协议变化锁存、Blt失败锁存、页面第三次调用失败立即停、完整十二行页。全部通过。[机器报告](../../reports/enuma-screen-diagnostics-host.json)区分主机与目标对象证据。

合成预览在本仓out/screen-diagnostics/host-preview.png，明确标有HOST PREVIEW / SYNTHETIC。所有显示值都是夹具数据，不是设备截图或真实GOP/UEFI内存图。目标COFF机器类型AArch64；当前优化对象仅有memset外部依赖，完整固件链接/编译器运行时解析尚未验证。不能把目标对象编译当完整固件或实机成功。

## 尚未接入与下一步

目前没有调用者、固件INF/FDF集成或设备写屏开关；SimpleFb metadata拒绝Blt和EnumaProbe早退均保持，不能为展示本后端就绕过守卫。今晚仍先用冻结的三候选验证最早复位与完整GUID调用前路径。

实际接入前需唯一GOP/提供者选择与QueryMode字段核验、实际scanout六项和受控像素矩形证据；随后安排小标记，验证调用与可见输出后才打印整页。caller适配必须替换旧Line/DiagDraw直写路径，分配/释放scratch并验证生命周期、链接运行时依赖、显式默认关闭的选择及错误回退。诊断绘制和分配会影响内存图，EBS必须由loader重新GetMemoryMap，不复用屏幕页显示的Key。

此后端只能在GOP可调用后提供信息，不解决GOP之前的SEC/DXE黑屏，故可控复位仍是前期辅助。新地址/大小/verified若有真实需求再按AGENTS处理。本轮无此变更；R-002跨复位日志不重启。
