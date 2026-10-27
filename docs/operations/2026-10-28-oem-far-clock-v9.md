# far-clock-v9：保留远端DXE路径，移除末端显示依赖

v7/v8均已consumed，用户报告FASTBOOT到Mi标未见日志且自行回Android；独立恢复和原分区/备份核验通过，无独立视频判读。v8修复已复现的追踪通知竞态，但没有消除报告的无页现象，不把该缺陷继续当唯一根因。

## 选择与实际代码

当前最大可操作方向是分离晚期显示出口拒绝与提前终止，优先级中等，唯一根因置信低。旧OemProgressPresent在真实Core与整轮DXE后仍要求TPL_APPLICATION、继承1600×2560路由、原Splash、CPU策略及完整窗口恢复；异常和多种拒绝均可无页直接ResetCold。下一版不再将这条显示出口当唯一取证通道。

新scope target=oem-far-clock-v9，另有low/high校准scope。保留精确OEM PE、私有表同步、v8临界区RAM事件、真实Core状态锁存和后续DXE分派；实际CoreDispatcher返回之后按RAM状态选有界延时并复位。本scope不链接旧OemBoardSink/像素/MMIO采样，不查询GOP或解引用Mode，不绘制，不在OEM中途等待。仍不进BDS、不合成EFI_SUCCESS，不改内存、verified、分区或R027。

EnumaOemExitClock只使用既有MicroSecondDelay、ResetCold、CpuPause。目标五类：1受控异常入口（2秒），2诊断terminal（7秒），3本次DXE已返回但没有匹配的目标Core返回（12秒），4分派返回且目标Core状态非零，包括warning（17秒），5分派返回且目标Core EFI_SUCCESS（22秒）。相应等待只发生在终止点，不在OEM前段阻塞；不是异步看门狗，挂起/未包装复位仍可能没有合格码。

低/高对照使用相同源码和OEM输入，但把出口等待固定为2/22秒，不能从对照码推断Core成功。它们有独立trial/session/image/qualification，不能用旧S-021/S-022或v7/v8返回时长当本轮校准。

## 时间通道的限制与执行门

Android总就绪时间不能直接解码。执行器在启动前后只读取得各三组Linux uptime/boot_id样本，以host monotonic请求区间减去量化uptime求启动原点交集，要求新boot_id及<=0.25秒不确定度。原样本与标识仅留本地out。

低/高对照各须人工确认无操作自动返回、独立恢复核验通过；控制报告源码指纹必须与精确目标相同，两个独立trial与image不同于target。扣除2/22秒后的基线包络差<=1秒，使用固定±1秒窗，不根据target结果调窗；校准计划绑定精确target image并只有效一小时。target --execute在缺少、过期或不匹配计划时，于claim及任何设备命令之前拒绝。校准对照也各仅一次临时boot，无自动轮测。

即使唯一包含于时间窗，也只能称间接时间码推断。不同路径的执行前缀耗时、未包装的OEM复位和跨次抖动仍能别名，不能宣称唯一异常位置、逐条日志或生产GOP成功。非唯一/宽区间/漂移/人工恢复均不给正向分类。低/高对照不是独立成功证据；真实GOP/ConOut/BDS/XNU仍待分层验收。

## 离线验证

实际helper覆盖5类、无匹配返回、EFI warning/error、非法code、ResetCold返回后的停循环；force0/1/5均经ASan/UBSan及ARM64编译。精确PE重定位/错PE/真实Core绑定与ARM64时钟对象通过。原进度、真实配置表同步和v8通知竞态回归保留。Python新增校准来源/漂移/过期/目标/区间拒绝及target缺计划不得claim/触碰设备，52项通过。首次binding缺MdeModulePkg头路径及旧模拟q缺scope失败保留，修正测试夹具/编译包含后另建通过结果，不放宽产品门禁。

三份最终完整FD来自各自隔离build4，补丁显式LF且staging git apply --check通过。build1暴露异常TU中未使用helper的-Werror；改inline后build2因旧UI函数未隔离被定向中止，保留中止证据；build3暴露宿主夹具预先包含旧捕获头而掩盖真实Core缺类型。修复为clock完全隔离旧捕获上下文/回调，并增加不预包含该头、无unused抑制的独立实际Core绑定ARM64编译；通过后才构建build4。所有失败/中止输出保留，没有reset/clean或放宽-Werror。

最终链接检查绑定实际CoreDispatcher返回后的时钟出口、真实CoreStartImage x0保存/身份门/拒绝分支、配置表发布及同步顺序、事件记录在RestoreTPL前完成并传递原事件指针、Recorded回调真实地址以及CPU默认异常出口。编译器把CPU的2秒等待专门化为两次1秒NanoSecondDelay，把22秒等待专门化为22轮1秒循环；按实际指令核对，不能假定调用者仍传literal参数。目标/low/high分别拒绝99/82/90处逐条指令删除；仅为选定序列审查，不是完整控制流证明。

新的FD审计还逐项比较当前firmware与构建source-manifest.original_files，阻止打包时用新源码给旧编译快照背书。资格保留构建前快照基点49affe7，不称提交后重编。软件资格不等于已完成实机校准，本轮不上机、不继承v8拍摄就绪。

## 最终镜像与资格

三份均3153920字节，qualification1通过，每份2470来源绑定、同一logic指纹，未claim/上机。固件提交edc579d，构建原始基点49affe7工作树快照；当前文档不构成本次现场就绪或真实时间校准。

### target — oem-far-clock-v9

- 镜像：`out/oem-far-clock-20261028/target/qualification1/image.img`，3153920字节。
- image SHA256：`3691d5989d9f50ead22f995b240644e58b579693d7f3db4f6b9d4329215f8e96`
- qualification1 SHA256：`dfea3b0f95e34702129485b6ba95fbd9599c2226101410dab6e67a7769a46858`
- FD SHA256：`577dde36ceba29e78393ef6d1a1d34a457686592f72d4d19c4ef0ba64146018b`
- trial：`96b78e34-892b-4ac1-b84d-8d3cc74a1f82`；session：`10889924087055404375`；未claim。

### low — oem-far-clock-low-v9

- 镜像：`out/oem-far-clock-20261028/low/qualification1/image.img`，3153920字节。
- image SHA256：`422139ef5b0d26bd4887c21b67e004331d3ca220c74077799cb3c77c848f6ab4`
- qualification1 SHA256：`cf07716a197bc08d70dad9c5144cc5424b971686f82e8baf6c4ef13dcb56ea44`
- FD SHA256：`76b1659f70e1cb13f0806bc6b27ed0afc1411b768df85b76a8cf21258fc5bcb7`
- trial：`d07aaceb-e633-42c3-9746-7c2304740a8b`；session：`72241299989157236`；未claim。

### high — oem-far-clock-high-v9

- 镜像：`out/oem-far-clock-20261028/high/qualification1/image.img`，3153920字节。
- image SHA256：`b8980a2d309b42b8b9207ac63fe8e0ab7ba68d545bfa97777071ed721277ce97`
- qualification1 SHA256：`3a8d1876bf807e1d4ca8845006e86809b5daf40c42ee7a380af4b65a18cc52c4`
- FD SHA256：`38e3113afdf34d8cc86cb3113c274039371a0d93c9966d8ca6692c6195e23889`
- trial：`0e8e88d1-faea-4829-8b8c-93ebbece2544`；session：`360695613987928583`；未claim。

最终结果与下一步以STATUS/HANDOFF为准。
