# OEM 非返回前的单次取证出口：离线实现与边界

2026-10-27。设备仓接手80bfadd、实际firmware 7a5c920，开始时两者干净；过程中只出现本轮文件。没有第二写入者、设备查询/启动、远端推送或nuwa操作。固件实现本地提交11c6cf1；设备仓本轮提交号以git log为准。

## 已实现的因果顺序

EnumaOemServiceTrace.h新增默认NULL的BeforeForward观察器。每次三服务包装器先在原高TPL临界区记入真实入口，恢复调用者TPL，执行可选观察器，然后调用原服务。观察器不替换服务返回值或输出参数；未安装观察器时保持旧无输出路径。未加入任何Core/profile/FV，不是新板级候选。

EnumaOemPrecallCapture.h在任何目标调用前一次性绑定同一trace context、非零session和预选call ID。只在所选调用且原TPL_APPLICATION时将完整环形快照复制到持久上下文，输出begin、最多129行原快照、end及FNV1a64完整性值。共最多131次sink调用，无分配、无自动重试，不依赖原服务返回。会话/调用身份由外部运行绑定校验；FNV仅检测意外损坏，不是身份认证或抗篡改签名。

状态区分armed/emitting/exported、sink失败、重入、TPL拒绝、记录丢失、计数耗尽、停止和中断。输出中重入包装服务会锁存失败，内层原服务仍按原接口转发，不让重入产生一个貌似完整的新快照。停止或失败后不再输出，已冻结的快照不被后续环形覆盖改写；原RAM日志可以继续记录。不存在运行中reset/rearm API；上下文和快照必须持久。非局部退出留下emitting，恢复管理方调用Stop将其标为interrupted，不能将遗留记录当新运行。

exported仅表示sink按契约接受了这次输出；不等于持久存储、显示可见或相机已经采集。完整文本接收端必须取得完整footer、身份和校验值才解码。预转发快照中的enter是包装器入场，**不证明原服务本体已经执行**；输出或转发过渡本身也可能失败。仅凭没有return，仍不能建立死锁。

## 非返回与进程外证据测试

check_oem_precall_capture.py运行真实C包装器与宿主原服务替身：sink逐行写独立文件并fflush/fsync；完成footer后才转发原服务。原服务先写另一个“已进入”见证文件，再停在不返回的pause循环。父进程见到完整快照及独立入场见证，确认子进程仍存活后仅终止该测试子进程；再次读取外部快照并解码。

final1验证外部文件仍完整，selected call0只有真实入口。749种截断、逐字节改字、重复帧和身份错配均拒绝。没有模拟OEM PE执行；这是宿主进程终止后的文件可取证测试，不是设备复位/掉电后的持久性证明。decoder输出仍是deadlock_established=false及forwarded_call_execution_proven=false；额外宿主见证仅属于本测试。

ASan/UBSan还验证：原错误状态/输出保持、嵌套调用、每一行部分输出失败、sink重入、显式停止、sink非局部退出、原服务非局部退出、TPL拒绝、序号/调用计数耗尽、selected丢失、环形覆盖、重复arm拒绝和恢复后无自动重试。只有一次选定调用的导出，不宣称连续追踪全部不返回点。

## 有界像素后端

EnumaOemCapturePixel.h复用现有Frame约束、地址算法和字形，独立实现一次(64,96)/320×160/8秒窗口。Saved[51200]、页面和运行状态均位于持久上下文，避免把约200KiB保存区压到OEM调用栈。最大153600读、102400写、3次屏障、1次hold、1次重验；未增加地址范围、内存配置或verified标志。这里的预算一致仅是软件约束，不继承旧实机资格。

在转发OEM前完成保存→路由/所有权重验→页面写入/反读→hold→完整恢复/反读。五行呈现：E+服务号+C+完整call ID、Q+sequence及覆盖标志、O+返回RVA、协议GUID两半；无GUID时第四行C表示请求大小。没有给entry编造status。未知RVA直接拒绝输出。该页面是选定事件的摘要，**不是完整文本快照**；session、精确PE身份和请求参数完整关联仍依赖未来外部单次manifest及拍摄绑定。

PixelSink仅在最终marker调用像素事务；前面的文本不物理绘制。此适配器的exported表示CPU窗口事务完成，不表示完整文本流已导出，也不表示人眼可见。测试使用RAM像素回调，不接OEM GOP/ConOut，也未安装板级MMIO/计时/验证回调。

返回1为无写拒绝，2/3为图案或hold失败但恢复成功，4为恢复未确认，5为CPU事务/恢复完成。首次写前置Active=true及Result=4，异常/非局部退出不会误报恢复成功；Attempted锁存禁止重复窗口。所有常规写后失败尝试完整恢复和反读，恢复失败仍为4。PixelSink要求非返回Stop回调；result4先标interrupted再终止，不转发OEM、不造EFI_STATUS。若Stop错误返回，进入无服务调用/无写入的本地停循环。此防线不是已验证的板级恢复路径，必须由未来独立恢复策略解决。

集成宿主测试证明：窗口恢复后原服务才被调用；原服务longjmp不影响已完成恢复。恢复屏障失败时Stop先执行、原服务调用数为0；窗口写入异常留下Active/result4且未调用原服务。这个异常路径不保证已经写过的像素可恢复，必须终止整次试验，不允许从测试longjmp推导实机异常恢复成功。

像素故障覆盖保存/图案/恢复阶段边界与中点、写前拒绝/写后报错、3处屏障、hold、重验、未知RVA、CPU策略拒绝、重复调用、异常以及24种通道排列。未做穷尽所有物理字地址故障注入，未验证多核/中断期间窗口所有权。

## 机器码、证据与保留

final1/result.json通过8条编译/执行/反汇编命令（两个host sanitizer程序、两个AArch64对象）。额外检查三包装器先EnumaServiceBegin再原服务间接调用，Begin内RestoreTPL先于observer；两个对象共6项删除关键指令/引用的负测均拒绝。PixelRun自身AArch64栈帧112字节；这不是整个调用链或固件总栈验收。反汇编及输入SHA256在同目录。

原追踪回归trace-regression/result.json的5条命令通过，含7项Python测试/320个模型快照及真实C往返。旧trust-check2不改；本轮对trace header的修改由新证据覆盖，不冒充旧源摘要。check1..4是本轮开发中间结果，最终以final1为准。

preservation.json确认R027 image.img与qualification.json未变化，2434项execution-review源码绑定未变化。原有PixelTransaction及日志页面未改。R027未执行/未消费、旧preparation过期；不申请录像，不复用R022—R026。

复现：在D:/Code/PortingiOS/enuma/UniXNU-enuma对应WSL路径运行`python3 -B scripts/check_oem_precall_capture.py --output out/<全新目录>`；旧追踪检查仍用`python3 -B scripts/check_oem_service_trace.py --output out/<另一个全新目录>`。

## 剩余卡点与下一步

不返回后的“必须返回包装器才能输出”依赖已由预转发导出消除，且宿主外部接收端可保留证据。板级可靠出口尚未闭合：须接精确加载句柄/PE/FV来源，证明预选call的身份；接单CPU下的当前CPU策略和路由重验、独占窗口、原始有界物理回调及不依赖OEM的终止恢复策略；加入独立默认关闭profile并做完整构建/打包/机器码与失败绑定。不能拿函数指针接口当作板级工作已完成。

若OEM在首次被包装服务前、或未覆盖的协议方法/MMIO/SMC/锁中不返回，这个选定入口不能直接定位那个区间；还需按真实新观测选取下一次call，不能自动扫描、多次点屏或重复实机。8秒预调用延迟会扰动时序，也必须写进候选解释。下一实机仍需用户明确恢复、精确单次放行及当前拍摄条件。当前只保留离线实现和验证，没有原厂运行、正式GOP/ConOut/BDS或硬件成功结论。
