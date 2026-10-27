# OEM Core追踪与板级适配器固件

继续沿一个隔离worktree、两个OEM profile推进。本轮只写入D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display；原主线及R027不改，不查询/操作设备、不推送。

## 新接线

开发builder新增显式`--oem-trace-build`，只允许oem-control/oem-mmu-only，仍强制stage10。未指定时不应用新的Core patch，旧profile默认路径保持。新代码在同一次完整FD链接中包含Core绑定、三服务包装、调用前快照及板级像素适配器；并不因为链接成功而获得执行资格。

Dispatcher保存本次调度的ImageHandle、完整File GUID和FvHandle；Image.c在真正调用EntryPoint之前将同一私有Image的LoadedImage地址和EntryPoint传入桥接。嵌套其他句柄透明跳过；目标句柄必须与LoadedImage协议返回的指针相同，DeviceHandle必须是该次FV，路径必须为精确DisplayDxe FV文件节点及结束节点，FV2协议必须存在。选择尝试一次锁存，不自动重试。绑定失败沿CoreExit报告实际StartImage失败；若CoreExit意外返回则在CpuPause循环终止，不能当OEM入口已运行或OEM返回状态；成功才把私有SystemTable传给原入口。

原始PE文件SHA256在构建输入和最终FV抽取阶段验证。运行态已重定位的.text采用独立完整性指纹：生成器从精确PE提取756个DIR64位置，加载态先减去重定位差量，再对249856字节.text计算FNV64。核对映像大小315392和入口RVA0x1000。两个变体有不同指纹，宿主交叉输入会拒绝。此指纹只用于诊断身份/误配检测，不称密码学认证，也不校验可写.data的运行态内容。

上下文、快照、320×160保存区均为Core静态存储；不把对象放到OEM入口栈上，不因驱动返回就释放。SystemTable/BootServices复制与CRC保持原实现，只替换LocateProtocol/HandleProtocol/AllocatePool。其他服务透明保留；三服务之外的协议方法、MMIO、SMC、锁和首次服务前故障仍未覆盖。

## 板级适配器与边界

OemBoardSink在完整快照footer时才尝试像素事务。它直接使用原BootServices的Stall，避免经包装服务递归；先核对MemoryMapHelper返回的既有Display MDP和Display Reserved契约，再采样原生路由、整帧CPU属性及CurrentEL。写入前再次采样路由/比较证据并复核CPU策略。只接受已有EL1、identity/WT和1600×2560契约；requirements22不清，未改映射、内存大小或verified。

本编译单元局部选择诊断日志几何320×160、(64,96)、8秒及whole-policy检查；没有改变全局旧profile宏。最多660次MDP读/4次100ms等待，像素最多153600读、102400写、3次屏障和一次8秒hold。事务在转发OEM之前恢复并反读；恢复未确认调用ResetCold，若返回则进入CpuPause永久循环，不编造OEM EFI_STATUS。

这仅是板级函数已经接入并可编译，不是已验证独占窗口、异常恢复、真实可见或相机留证。8秒显示的是选定事件五行摘要，不是完整RAM快照。若MMIO异常或中断/SMP改变窗口所有权，当前软件接口不能保证恢复；这些仍需独立资格，不能据本轮移除stage10。ResetCold也不是已验证的新恢复路径。

当前选择session=1、call=0仅用于编译接线；不是实机trial nonce或采集到的OEM调用序号。builder报告明确trial_nonce=false、board_runtime_qualified=false、deployment_ready=false。两profile在派发前停止，所以不会到达OEM或物理回调。

## 验证与复现

`scripts/check_oem_core_binding.py --pair out/oem-profile-pair-20261027-c999 --output out/<新目录>`：真实两PE重定位、.text/重定位字节损坏、入口/大小、嵌套句柄、LoadedImage指针、FV路径/句柄、单次锁存、CRC失败与私有表/捕获arm，以及交叉变体拒绝。ASan/UBSan通过；同轮编译实际板级适配器AArch64对象并核对内存区查询、复位、屏障和CPU系统寄存器代码存在。最终组件证据out/oem-core-binding-20261027-5。

原调用前出口回归out/oem-trace-link-precall-regression-20261027-1通过，含749种文本损坏拒绝、独立进程非返回后的外部文件保留、像素事务失败路径和6项AArch64删除检查。这些不被重命名为新板级实测。构建入口原8项检查在out/oem-trace-link-profile-regression-20261027-2通过。

完整构建命令沿原开发builder增加`--oem-trace-build`，每次使用全新output；失败目录保留。新生成EnumaOemBuildIdentity.h位于本次Core暂存树，其摘要和PE身份由oem-trace-identity.json/build-result.json绑定。源码仍使用独立source-manifest；旧发布锁和vendor原始锁不改。

最终检查使用`audit_oem_trace_fd.py`，它先执行原OEM FD身份审计，再从实际抽出的PE重新生成指纹并比对暂存头，核对已链接Core中的包装器、观察器、板级sink和终止函数。另用check_oem_stage10_code.py验证实际派发前停止调用序列。它们不是全路径控制流证明。

## 继续条件

新固件编出后仍留在离线阶段。接下来解决运行态单次参数/精确选点、窗口所有权和异常终止策略、实际取证与恢复边界，再形成可执行候选。R027不合并本次代码、不复用旧单次授权；未观察到return仍不能断言死锁。

## 本轮最终结果

隔离固件提交b6fe1a2。两组trace-build-2完整FD及source/patch回退复核通过；trace-build-1因新增补丁未暂存而在编译前失败，保留目录，builder显式复制后重跑成功。构建基点为322f427加当时工作树快照，最终提交不追写旧manifest。

| profile | FD SHA256 |
| --- | --- |
| oem-control | e856368faa31690518cea62f6212d536dd13c82941910f9cf6825c9450ad1786 |
| oem-mmu-only | 984aa8cf15f6358ce5eb5c6743a67a94a050f1dd0cfc7c3b4df9361ac5e37ef6 |

FD路径分别是本worktree out/oem-{control,mmu-only}-trace-build-20261027-2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd。最终审计在out/oem-{control,mmu-only}-trace-fd-audit-20261027-1；每组32 OEM PE/DEPEX、39 APRIORI、K81 RAW、生成身份和已链接代码检查通过。

Core桥接函数经LTO内联进CoreStartImage，不能因为map里没有独立函数名就称未接线。实际失败路径0xc93c调用CoreExit、0xc940调用CpuPause、0xc944回跳，check_oem_entry_failure_code.py每组3项删除拒绝通过。对照版实际OEM间接入口位于CoreStartImage内0xc4b8，源码point20/21保持前后归因；本轮未宣称完整控制流证明。stage10延时/复位/死循环/dispatcher调用位于0x3c94/98/9c/3ca0，每组4项删除拒绝通过。两变体的Core.text包含不同指纹常量，不能套用上一版Core.text相同结论。

总报告reports/enuma-oem-core-trace-development.json。固件/设备仓只本地提交，所有生成二进制和影音不入库。尚无Boot.img、设备查询/启动或部署资格；普通sink拒绝仍遵守原服务转发语义，仅恢复未确认进入终止路径，不能把编译成功解释为可靠外部取证已验收。
