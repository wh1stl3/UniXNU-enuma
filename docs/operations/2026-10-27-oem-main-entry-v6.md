# OEM main-entry-v6：减少取证干扰，推进真实主入口

本轮用户要求继续直到编出镜像、按实际代码分析卡点和解决方法，并快速推进启动链。本轮离线，不继承拍摄就绪，不追加实机。唯一写入工作树enuma-oem-display，实际固件firmware；共享主线只读、R027及v5等历史产物冻结，v5已consumed。

## 已确认事实与主判断

v5两张原图独立初读及完整字符串经用户确认，现场仅两页：call5/RVA5cc8、Qa→Qb、InstallConfigurationTable真实返回EFI_SUCCESS。设备无按键自行回Android且独立身份/root/槽/解锁/原分区核验通过。返回页绘制先于Hold后的恢复和读回，不能证明包装器已返回原厂0x5cc8；原厂代码、返回窗口收尾与下一出口拒绝必须区分。

首要诊断优先级仍为返回侧取证事务收尾/后续出口拒绝（置信中等，唯一根因低）；本轮消除注册两窗和服务返回侧绘制，既减少共同干扰又让真实OEM继续执行。没有已复现的新硬件缺陷，不修改原厂PE或伪造成功去强行越过初始化。

## 精确执行链与下一个具体卡点

精确PE SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425。已将指令和ABI检查落实scripts/check_oem_main_path.py：

- 0x1470→0x6ffc→0x7014尾跳0x5b64；0x5cc4调用配置表安装，0x5cc8置x0=0，0x5ccc..5cdc退栈返回0x1474。
- 返回入口框架后才进入0x1508→0x16e8主路径，四段内存清理之后0x1760调用0x35c8。
- 0x3604 BLR x8，经BootServices+320查询GUID b0760469-970c-487a-a4b5-28db7b45cef1，返回地址0x3608。固定QcomPkg.dec对应该GUID的ChipInfo协议；不是本轮SID观察GUID。
- 查询返回0才在0x3618调用接口+48；固定EFIChipInfo.h的GetChipFamily偏移由AArch64真实头文件_Static_assert证实为48，签名是This和输出family。协议方法没有经过现有BootServices包装，因此是SID之前具体竞争卡点，尚未证明运行到此。
- family==93才走另一协议查询/方法循环，随后回主入口；0x17e0调用BootServices+80 CreateEvent，0x1810/1838/1860调用+368 CreateEventEx。不能把缺SID页简化为SID内部死锁，也不能说CreateEvent在ChipInfo之前。

解决方向按证据推进：先用无注册窗/无返回窗候选排除取证器干扰；若E01后没有SID页，再分离ChipInfo原始查询返回、GetChipFamily/条件协议方法、事件创建及出口准入。ABI头文件一致只是布局证据，不保证运行时实例/方法/枚举或供电就绪；不能硬编码family或替换成功返回。若OEM改变显示管线后旧出口拒绝，应改取证/生产GOP接管，不能把拒绝当原厂失败。

## v6实现、区分力与边界

新scope oem-main-entry-v6，selected_call=6表示最小候选序号；真正选择条件是LocateProtocol、精确RVA3608、ChipInfo GUID，允许框架中先出现其他包装调用，不靠假定唯一call6定位。错误目标GUID/顺序拒绝，其他调用正常记录和原样转发。保留配置表同步和真实注册包装，但call0..5不绘制。

仅三类页面：E01为主入口ChipInfo查询前（实际call>=6，RVA3608）；E03为首次SID LocateProtocol前，并要求主查询真实返回已记录；S05为真实CoreStartImage返回和真实status。主查询/SID的返回在RAM追踪中保存，不绘制S02/S04。不制造服务状态或更改协议方法，不增加地址/MMIO/内存base/size/verified范围。板级另行拒绝其他phase及超过三次窗口；ROI(64,96)320×160、每窗8秒，最多24秒Hold，75秒观察门保持。

有E01证明本次经过未绘制的注册路径、最后构造返回并进入真实主路径；有E03进一步证明ChipInfo查询已返回并走至SID包装入口，但不证明SID原始服务执行或GetChipFamily成功；S05才给出真实驱动返回。单独E01仍不能区分该窗收尾、ChipInfo内部/方法和下个出口拒绝，全无页也不能定位。无独立看门狗或持久崩溃日志。

## 启动链推进顺序

本轮通过减少16秒最坏Hold、删除服务返回侧UI等待，推进真实OEM至主入口/SID/返回，保留目标驱动后诊断终止。下一依赖按真实OEM返回→生产GOP的Mode/Framebuffer/几何及显示所有权→ConOut与正常BDS/配置发现和输入→DarwinBoot/EBS→XNU验收。不能用临时SimpleFb菜单覆盖OEM失败，也不将本轮诊断包称完整正常BDS/XNU启动镜像。没有正常生产显示时不为追求启动速度扩大控制器连接、修改内存或升级verified。

本轮在线重读官网显示与日志章节成功（2026-10-27）：https://unixnu.com/porting/display、https://unixnu.com/porting/log-capture。按其先建立固件scanout、保存最后可确认日志和分层验收执行；现固定版本未因此升级AdvancedLogger/QR或复制sheng地址/刷新参数。

## 产物与验证

新输出根out/oem-main-entry-20261027。check2含v6及原有state machine/pixel/precall/trace/真实Core表扩容和删除负测，ASan/UBSan通过；path2精确PE指令及真实AArch64 GetChipFamily ABI通过。build1在完整编译前主动中止，以改为精确RVA/GUID而非固定call序号；原输出保留，build2使用新快照。其余最终构建、机器码负测、打包和精确源绑定完成后追加，不提前写通过。


## 2026-10-27 main-entry-v6离线编译与启动链定位

按用户要求编出新镜像c372c5e89a25aabe8d025469364c7d160be7c034481f5cec5e0283cc3338036d（3153920字节），FD 37126098fc7804af36cfcafe908f17454fbc9757ded55986462461f13caf4fcc，最终qualification2 7d3575843a9904d4f8b63891aa9143f785cbe934949e1fa868918775daf2e486。固件d393211，fd94b26基线工作树快照；trial cfee120a-a6a4-4b02-bcff-21b1aa82372f未claim/上机。取消注册窗与服务返回绘制，主入口ChipInfo精确RVA3608/GUID、SID入口及真实Core返回最多三窗24秒Hold；不伪造返回或跳过原厂初始化。32+77删除/2 GUID变异负测、42 Python、ASan/UBSan真实Core负测、ARM64 ABI/绑定、完整FD及Boot header v3回读通过，2452项默认离线绑定通过。固件已正常推送指定GitHub分支，设备仓发布见publication.json。

实际代码定位至ChipInfo GetChipFamily(+48)、条件协议方法及事件注册等SID前竞争位置，优先隔离返回窗收尾/出口；不称唯一根因。缩短诊断Hold是实际代码改动，不当作实测OEM/BDS/XNU成功。共享主线只读、R027及v5冻结摘要不变，本轮无设备命令。详情docs/operations/2026-10-27-oem-main-entry-v6.md、reports/enuma-oem-main-entry-v6-candidate.json、out/oem-main-entry-20261027。当前无人工/恢复欠项，未来新试验重做现场条件。

复现：WSL /usr/bin/python3 -B scripts/run_oem_runtime_trial.py --qualification out/oem-main-entry-20261027/qualification2 为默认离线入口，不带execute或human-ready。构建入口及完整argv在build2日志；资格使用check2/result.json、path2/result.json、binding3/result.json。原注册/返回窗只在旧scope保留，本v6不绘制S02/S04。


## 2026-10-27 22:58 v6本次单次启动准备

用户最新要求“上机”，并明确本次“拍摄已就绪，在场可恢复”。本次条件独立记录，不复用v5。22:58只读即时前检通过：enuma、Android完成、root、A槽、解锁、原boot_a/vendor_boot_a与本地备份摘要一致。新v6仍未claim/发图；本准备提交发布及远端核验后，由原单次runner再次即时核验并执行一次临时boot。

仅main-entry-v6镜像c372c5e89a25aabe8d025469364c7d160be7c034481f5cec5e0283cc3338036d、trial cfee120a-a6a4-4b02-bcff-21b1aa82372f；E01主入口ChipInfo查询前、E03首次SID前、S05真实Core返回，最多三窗24秒Hold。75秒无合格返回停止追加、优先恢复并同轮记录；不flash/erase/改槽，R027及旧v5不执行。当前观察不能预写OEM/GOP/BDS成功。

本次媒体目录已提前创建D:/Code/PortingiOS/enuma/Media-enuma/OEM-main-entry-v6-20261027-cfee120a；原始媒体只留本地，助手先独立判读落盘、展示完整字符串再请用户核对。准备与前检证据out/oem-main-entry-live-20261027/authorization.json、preflight.json。发布前不发图，无自动重试。


## 2026-10-27 23:08 v6主入口E01确认，自行回Android

准备f7dc965/固件d393211发布及远端精确核验后，trial cfee120a-a6a4-4b02-bcff-21b1aa82372f仅boot一次并consumed，fastboot调用0.401秒返回0，观察到Android完成。用户确认没有操作、自行返回；23:06独立enuma/完成/root/A槽/解锁及原双分区/本地备份摘要通过，无追加启动/分区操作或硬停。

一张本地照片先独立保存完整五行和摘要，再解码及人工核对；用户确认一致且现场只有一页。E01/C6/Qc/RVA3608/session91c9b0ca3369ea72，支持原厂注册后已到主入口ChipInfo查询包装入口；不证明E01窗口恢复或原始查询执行/返回，更未证明GetChipFamily/SID/Core返回。没有S02/S04是本版设计，不可作为缺失返回。下一定位优先E01收尾/转发、ChipInfo查询与+48方法、条件协议/事件至SID及出口；唯一根因未知，不凭最后可见页判死锁。结果reports/enuma-oem-main-entry-v6-trial-20261027.json，out/oem-main-entry-live-20261027保存确认/恢复/发布证据；原图SHA256 7a8f944ea3b53063c339cc34b6cdbf67c7b1fb7a5c4a5005fe176c39106f4b8d仅本地Media-enuma本次目录。R027/旧候选冻结，v6不重试，无人工欠项。

直连GitHub失败后通过系统已有代理的单命令Git参数完成推送，不修改全局配置。有效独立初读为media-review/independent-read1.json，首次写入异常空文件保留；原runner/独立初读pending状态不回写，由新human确认闭合。
