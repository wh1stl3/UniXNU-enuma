# 官网具体适配方法：enuma 执行规则

2026-10-27依用户“具体方法也落位规则”建立；同日在线核对下列官方章节。本文件由AGENTS强制引用。每轮涉及某个子系统时，执行对应条目并阅读链接原文及其源码引用；本文是项目执行清单，不是官网全文或已完成证明。官网与固定源码不一致时，记录版本差异再选实现，不自动升级依赖。

## 适配顺序与共用交付要求

依据[官方适配顺序](https://unixnu.com/porting/drivers)：平台/内存 → 存储/root/Data → 显示/亮度 → 触摸/按键 → GPU/Metal → Wi-Fi → DSP/音频/电源 → OS服务/打包。这是依赖与验收顺序；不阻止无实机时独立实现后续代码，但未满足前置依赖不得宣称运行通过。

- 每项先明确寄存器/IRQ/时钟/复位归属、传输及超时、CPU与DMA地址/缓存、OS接口和构建入口。
- 接通provider匹配及probe/start，或明确板级初始化调用者；核对类注册时机、依赖就绪条件和服务发布。
- 私有ABI按所选kernelcache核对布局、虚表、方法参数和符号，保留生成头及编译依据。
- 源码进入归档，归档进入最终链接，启动参数进入真实调用分支；检查归档对象、启动符号和预链接报告，再重建payload/boot。
- 初始化失败、停止、复位均先停止新请求，取消或排空异步工作，再释放IRQ、计时器、映射和DMA资源。验证完整请求、完成、OS可见结果、释放与重复运行。

## 1. 平台、CPU、中断和内存

来源：[Platform and memory](https://unixnu.com/porting/platform)。

1. 从本机资料记录MPIDR、BSP、PSCI、GIC窗口/stride、timer频率/IRQ；区分SoC定义与板级启用。DTS编译后反编译检查reg/ranges/phandle/中断父节点，核对ADT消费者字段宽度与字节序。
2. 先验证BSP及timer，再验证副核入口与IPI；未确认GIC/PSCI前不扩大启用CPU集合。性能簇划分依据目标拓扑。
3. 对账UEFI内存图、保留区、framebuffer、固件和载荷分配。逐设备写清PA/IOVA、地址宽度、SMMU context/stream归属及缓存操作。
4. 宿主检查布局、边界和无效输入；运行验收分别记录设备节点、timer、副核、IPI、DMA。任一项缺失只标该项未验证。

enuma落点：已有ADT/4K离线检查不能替代上述运行证据；内存字段变更仍遵守原有授权边界。

## 2. UFS、根卷与持久Data

来源：[UFS storage](https://unixnu.com/porting/ufs)。

1. 建立controller/PHY、时钟/电源/复位、SMMU、DMA、LUN/块大小/容量清单；先读取接管状态，决定保留固件初始化或完整冷启动，记录唯一队列与映射所有者。
2. 顺序实施：资源就绪 → DMA可达 → 队列接管 → 有界命令 → 容量及已知块回读 → 根卷发布。命令分别检查超时、OCS、协议响应及SCSI状态。
3. 区分磁盘容量、GPT范围、根卷窗口，按实际块大小换算LBA；时钟门控状态不能单凭CLK_OFF判定。
4. 只读、挂根、Data写入及重启持久化分别验收。失败记录请求阶段/状态，不在DMA未停止时回收队列或映射。

enuma落点：EnumaUfsSmmu/EnumaUfsRead宿主测试之后还须接真实控制器、IOKit与电源接口。stream归属未证实前不启用参考机ID；合成GPT不是本机容量证据。持久写入须在已有设备授权范围内另行实施。

## 3. 显示、刷新与亮度

来源：[Display and brightness](https://unixnu.com/porting/display)。

1. 对账GOP地址/长度/尺寸/stride/格式和内存保留；确认交接期间活动buffer不被重新分配，再接XNU framebuffer与所选IOSurface ABI。
2. 先做CPU已知帧，验证几何/缓存，再实现swap。每次校验buffer范围，序列号与完成事件匹配，surface保活至完成；错误和超时也必须结束请求。
3. 请求刷新率与计数器实测刷新率分开记录。改scanout前读取现有管线并设计可恢复路径。
4. 亮度按本机I2C/DSI/PWM、供电、地址与编码实现；一次传输完成或取消后再启动下一次。验证最小/中间/最大、渐变和OS控制链。

enuma落点：R027、待部署OEM候选冻结；SimpleFb/private GOP只作临时适配。nabu/elish/enuma即使面板相同，也须分别核对供电、桥接、固件及调用路径。

## 4. 触摸与按键

来源：[Touch and buttons](https://unixnu.com/porting/input)。

1. 先确认芯片/固件、总线、矩阵、方向、reset/IRQ及显示几何。协议、控制器transport、板级资源与HID分别实现。
2. 采用适配后的Novatek接口时，按identify → firmware parse → download → frame read检查返回；xfer保持一次完整传输的片选，下载失败保留CRC与回读诊断。
3. 发布原子一致的接触帧；验证坐标变换、稳定ID、多点、边缘和抬起。HID描述符、范围、contact上限匹配传感器及目标ABI。
4. 按键单独核对GPIO/PMIC归属、极性、确认中断方式，验证按下/释放、长按、组合键和有界中断活动。

enuma落点：先证实本机协议兼容性，不因同厂商或同面板直接套用参考触摸固件、矩阵或sheng-*参数。

## 5. GPU与Metal

来源：[GPU and Metal](https://unixnu.com/porting/gpu)。

1. 确认GPU代际、固件、GMU/电源、包格式与OS ABI。其他代际必须有匹配backend和编译器支持，不能仅选择Adreno740前端。
2. 依次验证电源/固件响应、受控映射、ring进度、fence与已知图像；请求结构及输入输出长度绑定实际dispatcher。
3. 超时记录request/handle/fence，停队列并确认DMA停止后释放BO；覆盖客户端退出、映射生命期及失败。优化映射前证明缓存及不重叠条件。
4. Metal插件、编译器、Data seed、trust与user-client按目标OS整合并重打payload；分别验证设备发现、连接、pipeline、渲染与呈现，区分冷编译与缓存时延。

enuma落点：SM8250不能继承SM8550/A740完成状态；预链接包含IOGPUFamily不证明Metal可用。

## 6. Wi-Fi

来源：[Wi-Fi adaptation](https://unixnu.com/porting/network)。

1. 确认实际radio/硬件版本/固件与board-data再选驱动。适用PCIe路径时按电源时钟 → link → endpoint ID/BAR → DMA → MSI推进。
2. 补齐时间、日志、内存、DMA映射/方向同步、固件读取及板级接口。先安装events，再start/step；固件内存保持消费期有效。
3. 异步接收先复制到OS拥有的buffer；停止时拒绝新请求、停worker/component，再释放BAR/MSI/DMA。
4. 固件启动、扫描、认证、关联、地址配置、收发、重连与持续流量逐项留证。卡住时记录worker阶段、统计、MSI和固件日志。

enuma落点：未核对芯片与transport前，不默认采用sheng的WCN7850/Ath12k链路或其DMA/固件存储回调。

## 7. DSP、音频、电池与电源

来源：[DSP, audio and power](https://unixnu.com/porting/power)。

1. 按目标固件确认DSP认证/内存/mailbox及协议。先建立ready/crash路径；接收回调仅入有界队列。断线取消请求和远端handle，重连后重建订阅。
2. 音频先完成一条实际route：协议响应匹配 → graph配置 → DMA period → 完成/位置 → OS服务。失败释放已创建对象；停流后再unmap。验证已知PCM、反复启停、饥饿、超时和DSP重启，再验证应用。
3. 电池只发布有效快照，明确单位及电流符号；协议丢失标记过期，覆盖超时与重连，核对原系统读数。测量发布不改变充电控制归属。
4. 频率/电源按目标domain、LUT、OPP和热约束实现请求与回读；依赖DMA/IRQ停止后释放vote，休眠恢复验证映射、时钟和中断恢复。

enuma落点：不复制SM8550的AudioReach拓扑、时钟ID、地址限制或调速策略；先确认SM8250实际接口。

## 8. OS服务、打包与用户态

来源：[平台中的OS基础设施](https://unixnu.com/porting/platform)、[构建](https://unixnu.com/building)、[启动分层](https://unixnu.com/porting/bring-up)。

核对RamBlock格式/回调、VerifiedRoot镜像与owner策略、SoftwareAES接口、AppleKeyStoreState事件及目标XNU ABI；匹配XnuPrelink、DarwinBoot与ADT/sidecar输入。地址、卷几何、UUID及OS版本分别绑定实际配置。

本项目执行要求：每次产物记录输入commit/hash、参数和输出hash。依次取得载荷读取、DarwinBoot交接、XNU入口、驱动发布、root/Data、launchd、图形服务、SpringBoard证据；阶段失败保留最后可确认日志，不用文件存在、符号链接成功或进程占位替代运行成功。Data seed和图形插件改动必须进入最终包。

当前离线产物只支持格式、组件与读回结论；后续优先补真实UFS/电源/OS集成和Data依赖，无实机时继续独立实现与负测。

## 每项工作必须留下的记录

使用已有操作文档、报告及适配记录承载，不要求每轮新建重复清单：

| 字段 | 必须记录 |
| --- | --- |
| 依据 | 对应本文件章节、官网URL/核对日期、参考仓commit/文件、本机差异 |
| 实现 | 本轮能力、前置依赖、硬件常量来源、ABI、初始化调用者、归档/链接入口 |
| 生命周期 | 所有者、缓存同步、超时、取消、清理顺序、取证出口 |
| 验证 | 实际命令、输入/产物摘要、正常与失败用例结果；宿主/QEMU/设备分列 |
| 结论 | 已实现、已集成、已运行分别陈述；未完成依赖和下一步 |

缺项标明未知并推进不依赖它的工作；不能补写成功。具体协议负测跟随实现，不要求为纯文档变更制造测试。

本规则只在当前隔离worktree落位；共享主线由后续明确整合操作同步。R027、OEM候选、无实机、不推送及既有授权边界继续有效，不新增逐步审批。
