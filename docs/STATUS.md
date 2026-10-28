# 当前：v10三图均已单次消费，用户确认全部未按键、自行回Android且没有新画面，独立恢复/原分区及备份核验通过。低/高校准基线6.164..6.362秒，目标原点8.127..8.261秒，间接推断code1异常出口；不是直接异常日志，未取得Core/GOP成功证据。本组三图不重试。（2026-10-28）

2026-10-28T11:45:27.566337+08:00。用户本轮已确认正在拍摄、在场可恢复；本次现场条件独立记录，不沿用旧就绪。

## 候选与证据

- low：trial `2f8dcedf-588e-4e05-809a-f653c1efc25f`；image SHA256 `c9cb7c200ea35894e1002075102a432ac8d867c40d89291ef5da5771791ef586`；已claim/消费。
- high：trial `c6f3f7dc-52ed-4e9a-8dd2-721a87075cae`；image SHA256 `d581d070a30a942fb0bb6662404e875c472ad1d36ccd366b124d45237080960e`；已claim/消费。
- target：trial `bff01371-9799-4d1f-8f58-c5e0143f794b`；image SHA256 `41585b244499f4405bb0050e31106480e0c039234d931ce4be83c79cab6e17c8`；已claim/消费。

完整构建与软件资格：operations/2026-10-28-oem-gop-mode-v10.md；reports/enuma-oem-gop-mode-v10-candidates-20261028.json。每份完整FD、Boot v3和2475绑定通过；固件2c18bc6，构建为edc579d工作树快照，不能称提交后重编。

本轮结果：reports/enuma-oem-gop-mode-v10-live-20261028.json；本地out/oem-gop-mode-live-20261028及out/device-tests/oem-<trial>保留原始状态/传输/时钟，人工与独立恢复另存，不改写runner历史。媒体位于D:/Code/PortingiOS/enuma/Media-enuma/OEM-gop-mode-v10-<kind>-20261028-<trial前8位>/original。

## 执行与验收边界

本次code1间接结果使异常现场取证成为下一优先项；先取得异常类型/ELR/ESR/FAR及镜像归属，再判断Clock/DAL、HAL或其它路径，未确认唯一根因。v10只有目标Core严格EFI_SUCCESS且整轮CoreDispatcher完成后才调用原厂GOP QueryMode(0)、最多一次SetMode(0)并读回，核对原厂函数归属、几何和内存边界；不Blt/像素绘制、不ConnectAll、不进BDS。成功间接码也不能证明物理scanout或画面。

顺序low→独立恢复/人工确认→high→独立恢复/人工确认→精确校准→target，各一次。校准要求新boot_id、原点区间<=0.25秒、扣除2/27秒后基线包络<=1秒，固定±1秒窗；计划不得给旧观察续期。歧义/漂移/人工恢复不作正向分类。75秒未回合格终点停止追加并优先恢复，无独立看门狗保证。v9仅离线，R027及旧产物冻结，共享主线只读；不改内存/verified、不flash/erase/改槽。源码/脱敏文档发布至显式GitHub URL/oem-progress-20261027，不推firmware本地origin，原始媒体/out/二进制/备份/标识不上传。

用户本轮明确文档可最后统一发布，不因网络问题阻塞。860e31b发布遇连接重置，46f8515已确认远端；最终结果以本地新提交及随后发布记录为准。其余运行门禁保持。

## 本次代码归因与下一步

目标8.127..8.261秒整体位于预定code1窗口7.164..9.362秒；2/27秒对照差异符合25秒，降低固定早复位完全遮蔽终止等待的解释优先级。实际EnumaOemExceptionStop.h在未处理异常checkpoint调用EnumaOemClockExit(1)，出口等待2秒并ResetCold；补丁把checkpoint放在AArch64异常状态输出函数开头、递归检查及文本打印之前。因此优先取得异常类型、ELR/ESR/FAR、目标镜像归属及最近服务阶段，不能继续只凭无页认定Clock/HAL死锁。

当前异常hook不传入现场上下文、直接等待复位，现有报告不能恢复异常PC；异常可能出现在OEM、其它DXE、追踪器或GOP helper，尚不能认定未进入后段。下一候选应在不依赖常规屏幕打印/分配的条件下保留或有界输出异常现场，再归到实际本机指令；需独立实现/失败验证/完整构建和新单次资格，本轮没有生成或执行新候选。未直接采到异常，仍保留未插桩复位、前缀时延变化与时间码别名竞争解释。
