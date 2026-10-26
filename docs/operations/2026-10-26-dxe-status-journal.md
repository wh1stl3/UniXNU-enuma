# DXE真实状态记录到屏幕回放：D-285离线里程碑

主判断：现有阻塞首先是日志接收与控制台执行链未接通，而非再验证字形。S-047已证明仅该小区域固定字形及恢复；平台SerialPortLib仍Null，Core在BDS前返回，EnumaProbe.Line把Print与直接DiagDraw混在同一次调用。已有静态/实际链接路线审计见2026-10-26-uefi-console-menu-validation.md及reports/enuma-console-path-audit.json（历史FD绑定，不冒称本轮新FD审计）。此判断会被“当前实际FD存在非Null DEBUG后端且已运行ConOut”的真实代码/运行证据推翻；现在没有该证据。

本轮选择先实现真实DXE结构化状态而非替换整个SerialPortLib：不必在未知早期构造器阶段分配或跨模块共享RAM，不调用潜在递归DEBUG/Print，不绕过GOP。代价是仅有Core内部记录和未接屏幕的回放接口，尚无可现场读取的错误输出；这不是完整上屏交付。SEC、所有模块DEBUG及BDS日志另需正式共享协议或DebugLib设计，不把单模块静态BSS误称全局日志。

## 执行顺序与接口

1. --boot-journal进入board defines，再经dispatch-detail-options.patch传入真实CFLAGS；默认0。本轮首次完整构建发现只有EDK -D而无C -D，不计日志资格；修复后增加构建后断言。第二次编译完成但断言误读仅含间接引用的Makefile，报告complete=false；再次修正到实际OUTPUT/cc_resp.txt的独立token、staging头字节、Core PE摘要后最终通过。Makefile与响应文件分别留摘要。
2. 既有dispatcher/image bridge调用点14/15/20/21/22/13进入检查点，先写volatile Core BSS（保留LTO后的真实store；不表示原子/持久），然后原有GUID/marker/终端筛选照常。point15/20的SUCCESS仅说明“到达调用前”，不是被调模块成功；只有相应返回记录才是实收状态。与当前scheduled handle不匹配的嵌套Image调用仍被旧bridge排除。日志无时间戳，顺序号不等于时钟。ordinal是既有计数器快照，只在旧stage12/13计数配置下递增，其他配置可能保持0；不为日志改动旧计数/停止规则。
3. 最新128条；每覆盖一条计Dropped，序号耗尽拒绝。不读像素/MMIO，不分配/改页表/缓存/路由，不引入新的物理保留区，不触发复位。仅DXE单生产者，不宣称AP/异常并发安全。
4. Core-local EnumaDxeBootLogSnapshot复制到独立调用方内存；producer静止。它不是可供EnumaProbe LocateProtocol的接口。未调用snapshot不会产生可读屏幕内容。
5. ReplayNext只消费不变快照，先输出Dropped，然后每次最多一行；sink拒绝不推进游标，调用方每行之间可取消。所有值固定宽度十六进制，g=为16个EFI_GUID内存LE字节，不是规范UUID字符串；无GUID为'-'。尚未绑定屏幕、ConOut、文件或SerialPort sink。

| 可验项 | 依赖 | 本轮独立结果 | 验收条件/剩余限制 |
|---|---|---|---|
| 有界记录/覆盖/字段保真 | 主机独立算术模型 | 10000事件、每次检查全部保留记录，通过 | 不代表硬件路径已执行 |
| 快照和单步文本回放 | 调用方独立快照、sink | 失败重试、空日志、终点、GUID/错误status、输入拒绝/饱和通过 | 无屏幕接收端；单调用方同步 |
| 实际检查点接线 | 生产头，平台依赖桩 | on/off筛选一致；过滤前记录七节点通过 | 非完整DXE执行仿真；未收返回不补造 |
| AArch64 ABI/头文件 | 固定Mu_Basecore MdePkg头 | 三个freestanding对象通过 | 不等于QEMU或实机通过 |
| 完整FD/宏/staging | 已提交固定源码、干净pin、EDK构建 | 通过；FD f0c0608f597192c0589db8eb62fffd2c9532233c7a2f71874050e16da16ffc03 | 无Boot v3/FAT重新打包、无运行日志 |
| 真实状态小区域回放 | 快照消费者、字形/通道/保存恢复预算 | 未实现屏幕sink | 离线故障注入、精确范围审查及新批准后才试验 |
| 全局DEBUG/SEC | 有生命周期和共享语义的后端 | 未接入，SerialPortLib保持Null | 逐模块实际链接+启动时序检查；缓存回放必须标明阶段 |
| BDS/ConOut/Print | 正式GOP/DevicePath/Console连接 | 未执行，早停保留 | Print独立于DiagDraw，不能因GOP存在即判通过 |
| 稳定正式GOP | requirements、持续Validate/alpha/路由 | 未改变22/alpha/SMMU | 四类Blt/SetMode独立验收，连接可能清全屏 |
| UniXNU菜单 | payload合格、UI初始化、显示和输入 | 无新实机结论 | 菜单出现、选择/取消分别验收 |

## 离线证据与构建范围

固件b2ce0befab9d7938a52b5c381bc4a9e5d93b29c0；reports/enuma-boot-journal-tests.json包含命令和输入摘要，reports/enuma-boot-journal-build.json冻结当前FD/Core/实际宏，reports/enuma-boot-journal-artifact-audit.json另核实际C响应文件、LTO后存储符号及FD内Core PE逐字节相等。主机ASan PIE程序有间歇SIGSEGV，未证明根因；非PIE仍启用ASan/UBSan，三程序各10次通过。volatile修改后的负向别名测试曾因丢弃限定符编译拒绝，明确转换该故意非法输入后通过；生产代码没有丢弃volatile。相关主机诊断只留out/boot-journal-tests/；不将该现象推断成设备故障。

完整构建是新离线配置：--boot-journal --diagnostic-simplefb --stop-stage 13 --detail-point 13 --dispatch-guid dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92 --dispatch-guid-only。GOP_QUERY=0、RAM_PAYLOAD=0、CPU_TEXT/PATTERN=0；因此它仅是编译/接线验证，绝非可直接上机的完整链候选或菜单资格。未改依赖版本，不重建/执行历史S-047资格。

## 后续精确试验设计和批准条件

候选A推荐：在既有Core终端同次采集真实状态，生成快照，以原128x32上限、mask-aware不透明像素展示最多四行选定状态，完整保存/前置与后置复核/有界保持/恢复读回；有丢弃时单独显示标志，不把缓存回放标成当时直播。先把字符数、字体、保存区、load/store/屏障/MDP读次数和持续时间实数化，并完成所有失败点测试；现在尚无该sink/精确预算/新镜像摘要，故不是R-020已资格候选，也尚无请求执行的批准项。

候选B：仅建立Core日志共享读取协议和主机/QEMU导出，不写屏幕；风险低但不能完成实机日志上屏，且本机无已验证主机取数通道。候选C：直接解除早停、连接GOP/GraphicsConsole后Print/菜单；涉及SetMode/清全屏和未闭合GOP要求，不推荐作为下一笔。

A完成后需新像素/新镜像范围的明确批准；S-001..047/R-018/R-019均consumed，不沿用。本轮只授权离线，无设备动作。还需当前文档提交推送、精确源码/PE/宏/FD/完整FAT/Boot v3绑定、新鲜选定enuma身份/匹配备份/可恢复路径、相机关键节点连续记录（原始仅本地、无音频）、固定75秒观察和时钟判据。无法恢复、时钟/观察失效或75秒无受控返回即停止追加，恢复优先并当轮更新交接。未取得新鲜设备状态，不把历史Android恢复当此次预检。
