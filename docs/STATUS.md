# 当前状态：先审显示交接契约，原厂DisplayDxe有界验证

## D-164：公开资料复审后的当前顺序（2026-10-25）

当前主线改为先离线审计ABL→BootShim→UEFI的continuous-splash交接契约；原厂DisplayDxe保留为有界支线。先输出实际FDT/显示生命周期证据与原厂PE真实调用/ABI清单，再按缺口选择候选，detail15/detail13不再自动排在离线审计之前。详见[公开资料路线复审](operations/2026-10-25-public-source-route-review.md)。

新静态发现：enuma配置EnableMultiThreading/EnableDisplayThread=1，但当前GetXblHobAddresses只识别FD Reserved/FD_Reserved，板级内存表无此名称；以该表调用此路径不会恢复scheduler/DTB扩展HOB地址。这不证明实机挂点或DisplayDxe必然使用该ABI；需绑定实际PE/SEC证据。不得直接改名、加内存区、关线程或补stub来冒充修复。

同SoC edk2-msm有继承帧缓冲实现，MiCode/LineageOS提供SMMU/split-DSI和KTZ8866依据；这些实现不证明本机scanout有效。暂不重写完整显示栈；若证实仅背光等窄缺口，再复用真实协议实现。D-163四项更正继续有效。此轮仅研究和文档，未构建/访问设备/实测，未提交推送，未扩大授权。

2026-10-25 01:38文档复核。本轮仅修改文档与方案，未构建、未启动、未写设备。当前结论以D-163为准，D-162中过强解释已取代；原始观测保留。

## 最近实测与恢复

R-014镜像922972e61b0e4e3d7b7c931b53b76531a2db2a08504c6794263e5ff3f5ab1a75，FD dbca3fcb2f470807f1fdac8b17e47c6eb604f3be49b1563c42df5bfc020615e0。两笔均75秒未自动返回，第二笔60帧间隔采样未见固件画面；不能定位到DisplayDxe或宣布稳定挂死。目录/拍摄相对时间不能冒充精确boot时间。

最新已有恢复证据reports/enuma-recovery-reconciliation.json、out/device-tests/20261025T012053-recovery-reconciliation.json：Android完成/root/A槽/解锁及双分区设备/备份摘要通过。本轮未重新访问设备，不推断当前实时状态或恢复按键细节。旧失败记录不改，实机前重做即时核验。

## 四项核心更正

1. 实际FD内DisplayDxe在APRIORI第33项（零基索引32），是排入队列资格，不是实际进入或返回证据；不是“必定已dispatch”。
2. R-014目标门指向未打包的SimpleFbDxe，但completion fallback=1。CoreDispatcher返回后仍应等待7秒再尝试ResetCold，故75秒无返回不是配错GUID的必然结果。更早阻塞、异常、复位或观测问题仍待区分。
3. 未知两个GUID完整字节未命中，不能证明没有提供者、代码不调用或初始化语义无关。缺GUID不是已证明的DEPEX调度阻塞；R-015不按原动机执行。
4. detail13只表明CoreStartImage任意返回，不能输出具体状态；detail15成功、detail13无响应也不能直接判驱动内部挂死。

## 原厂支线候选（离线审计后再决定，未构建、未实测）

专项方案：[DisplayDxe执行边界定位](operations/2026-10-25-display-entry-isolation-plan.md)。目标GUID4138022f-06c7-4f79-9c94-7e33b511a4e7；候选A detail15启动调用前，候选B detail13启动调用返回后。保持原厂PE和派发顺序，without-ufs、SIMPLEFB=0、query0、step0、value-source off。先A，依据有效阶段与返回证据再决定B；不硬编码Android返回秒数，不以一次超时定位因果。

如B返回，后续用query0的detail16/17区分错误/非错误并另验GOP；如需细分PE包装器/构造函数/返回机制，再审detail20/21/22。没有新像素、背光、未知协议或寄存器写方案。暂不自写I2C/背光，取得真实接口缺口后再评估，不以原厂PE存在当作全栈可运行证明。

## 来源和设备门禁

gitlink/锁/firmware检出aa9ec66已对齐；独立参考检出和Mu递归脏状态不清理。本文修改未提交，设备仓不是干净已发布状态。下一次实机前先完成来源/实际宏/FD/打包资格、适用文档提交推送与即时身份/备份/现场恢复门禁。不能用旧R-014资格报告替代新候选。

R-015暂不执行；其余批准按NEED-REVIEW原记录核对，本文不新批或扩张R-008/R-012/R-013/R-014。原厂DisplayDxe可能写硬件，新边界候选不是整镜像只读。超时停止追加、先恢复核验、当轮更新全部当前文档；不原样重试失败镜像。

## 系统里程碑

目标iPadOS17.7.11/21H461、iPad7,1/j120ap，XNU10063.141.1/4KiB；固定UniXNU5fdbd5d。现有原厂模块/面板资源支持复用方向，DSI计数支持采样期接口活动；未确认端到端显示、GOP可见输出、PE_Video交接或XNU实机入口。原平台内核链接/闭包规划、FAT准备不能当整机启动。
