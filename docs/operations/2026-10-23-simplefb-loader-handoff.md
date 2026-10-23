# SimpleFb真实配置重试、范围约束与DarwinBoot视频交接

2026-10-23（Asia/Shanghai）。承接00505f8继续离线主线；全程没有ADB/fastboot查询或设备启动。上次实机状态仍以12:11:03人工恢复核验为准，不能把它当成本轮连接检查。

## 两个复现与修复

6bc5b81的CreateFrameBufferConfig使用STATIC大小变量。真实Mu FrameBufferBltConfigure先判断调用者大小是否足够，足够后再拒绝NULL配置指针；失败清理不重置静态大小，因此后续NULL sizing query返回INVALID_PARAMETER，而非预期BUFFER_TOO_SMALL。原mock无条件返回BUFFER_TOO_SMALL，掩盖了这条重试路径。新实现将大小改为每次调用初始化为0的局部变量，仍由真实库决定所需大小，不硬编码大小。

GetFrameBufferInfos原先只检查区域非空，未比较Width×Height×bytes-per-pixel与描述符Length。新实现先检查乘法溢出、Span≤Length/UINTN和Address+Length不回绕，再交付地址，避免GOP宣称超出描述符。没有修改任何内存表、地址、大小或verified；该约束**不证明实际scanout或像素所有权**。Display Reserved仍包含DFPS，不能把整个描述符都当像素写入区。

两问题在6bc5b81分别触发断言退出，证据保留在[基线回归](../../reports/enuma-simplefb-handoff-regressions.json)。82ce8a5修复后，范围、真实配置/loader及组合三种host运行全部通过。重试缺陷不必然在首次入口发生，不能将它认定为首测黑屏根因。

## 复用与集成测试边界

脚本[check_simplefb_handoff.py](../../scripts/check_simplefb_handoff.py)先核对固定Mu cfb93724归档SHA，再原字节提取FrameBufferBltLib.c从文件头至VideoFill前的完整前缀：结构体、mask、ConfigurePixelFormat及Configure主体均保留，仅通过C宏给Configure改名以接入错误注入包装。没有将上游实现复制入Git，也没有自行重写配置算法。完整Blt绘制函数不在该host测试内。

真实SimpleFb整份补丁后C、上述真实Mu前缀和固定DarwinBoot BootVideo.h共同编译执行。UEFI服务/分配器和HighBitSet32是host适配，帧缓冲地址为合成夹具、不映射或写物理内存。覆盖分配/配置/安装失败后的重试清理、恰好容量/少一字节/地址回绕/尺寸溢出，以及视频元组、非BGRX拒绝和跨度不足拒绝。它不是构造器、UEFI ABI、缓存或设备证明。

夹具1600×2560×32产生rowbytes6400、span16384000；这只是紧密BGRX假设下的数值链路。实际enuma pitch/格式/偏移仍未知，不能把测试值写成硬件事实。16/24位路径即使GOP可描述，也不满足当前BootVideo只接受BGRX32的契约。

## 实际构建依赖

82ce8a5实际AArch64构建成功，FD 75c34141a785d4dc38f1475e6ce1a60b894f30db98c18b58926958c6e2bd203f；编译后的SimpleFb源SHA与host使用的完全相同。30 OEM PE/DEPEX逐字节、官方core patch还原、192字节BootShim/3MiB FD、v3打包回读均通过，镜像只在out归档。源码CI39912601757成功并回读PASS，仅验证源码契约。

本次实际AutoGen的构造器顺序为BaseDebugLibSerialPortConstructor、UefiBootServicesTableLibConstructor；as-built INF绑定BaseSerialPortLibNull。固定Mu Debug构造器仅调用SerialPortInitialize，Null实现返回成功；BootServices构造器缓存并断言句柄/SystemTable/BootServices指针。MemoryMapHelper从本机MemoryMapLib静态表按名称查找，不依赖另一个显示协议。这些是源码/链接事实，不代表实机执行完成；point20仍在整个PE入口调用前，不能把它直接当RegisterFrameBuffer主体入口。

50项Python、完整驱动ASan/UBSan、真实库/loader联测、组合patch重复重放、50项源锁通过。一次workspace检查与build的qualification并发，因两者临时apply/reverse同一out上游补丁而瞬时失败；构建完成后已串行重查通过。以后这两个命令必须串行，不将该瞬时状态误判为上游漂移。

## 到XNU还差什么

| 关口 | 本轮能证明的 | 实机通过条件 |
| --- | --- | --- |
| DXE与SimpleFb | 驱动可构建，配置/错误边界及视频接口host通过 | 先早期复位，再完整GUID调用前2/7/2；之后观察调用返回/状态与唯一GOP字段 |
| 显示与loader | BGRX32视频元组兼容已做合成联测 | 真实base/偏移/pitch/格式/有效像素子范围、可见输出及生命周期；保持metadata禁止猜测写屏 |
| 内存与固件退出 | 512MiB请求及既有合成AllocateWindow检查 | 实际GetMemoryMap、保留区、连续窗口与分配失败路径，随后EBS交接 |
| XNU入口 | 固定iPadOS/XNU来源、平台支持代码 | 实际入口和最早异常/串口等可观察证据，再验证中断/定时器/基础平台 |

不能据此承诺第几轮进入内核；当前最短动作链仍是实机DXE/GOP→UEFI内存与loader交接→XNU入口。进入XNU与进入iPadOS用户态是不同验收点。新固件继承GUID-only/正常分派完成兜底，但同步兜底不能救驱动卡死；失败立即恢复并停止追加候选。R-002跨复位日志保持停止。

当前完整机器证据：[离线构建及依赖](../../reports/enuma-simplefb-loader-bringup.json)、[真实库/loader测试](../../reports/enuma-simplefb-handoff-host.json)。不把静态检查或host执行升级成QEMU/实机成功。
