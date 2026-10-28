# gop-mode-v10：真实DXE完成后推进原厂GOP模式

按当前分析优先级先核对本机Clock/HAL IOMMU ABI及代码，再补齐下一段原厂GOP模式调用。原厂PE、Clock/HAL提供者及SM8250三路时钟原始方法不修改、不伪造返回，不把公开旧版平台实现直接套成enuma缺陷。

## 本机提供者核对

ClockDxe SHA834428700f5e034e52285e1d516b98e86e71ce4b6d7211a9b40fa87d92137cab；接口表RVA1e150，版本10009，与固定EFIClock.h匹配，GetClockID14dc、EnableClock1524。它们经全局319f0的DAL上下文，再调用内部虚表+72/+80；初始化是否成功及真实方法返回仍未知。

HALIOMMU SHA36a5adbe91a796940f4c09eb53ae4ffb1632ef20d8c3085f7cceb2a706c1e306；接口9098版本1，GetAPI14cc把函数表90b0写到x0输出指针，不带This，与原厂DisplayDxe的1bd04调用一致。表+0/+16/+64对应16b4/1920/2f10，仍需对后端资源/执行进一步取证。此本机入口1504发布协议后调用15a0，后者只是返回0；公开旧样例dummy初始化失败分支不能作为本机已存在缺陷。实际provider disassembly/指令在out/oem-gop-mode-20261028。

HAL原厂DEPEX含常见Arch集合，但原始XBL本就把HAL放在Variable/Watchdog等之前；不能仅凭通用DEPEX擅自重排全部Mu架构服务。Metronome的既有提前补丁仍保留。当前证据不足以修补Clock/HAL，因此继续其真实路径，并在运行条件满足时推进更后的GOP阶段。

## 新执行路径

保持OEM期间RAM-only、精确私有表同步和通知竞态修复。CoreDispatcher返回后，仅当目标Owner存在、匹配Core返回位存在且真实Status严格为EFI_SUCCESS，才运行OemGopAdvance。错误/缺失/其他镜像返回不得进入GOP。

不ConnectAll、不进入BDS，不直接读写MDP/像素，不调用Blt或显示电源循环，不改内存字段、verified或分区。新helper通过原BootServices枚举最多8个GOP handle，只接受恰好一个QueryMode/SetMode/Blt函数均位于本次已认证原厂DisplayDxe text范围的实例。64KiB静态内存图缓冲与受控数据类型/溢出检查用于对象解引用前的RAM跨度校验，不在栈上放大数组。

QueryMode(0)最多一次；成功返回的信息必须为1600×2560、stride1600..4096和支持的32位像素格式。真实分配信息回收后才最多调用一次真实SetMode(0)，严格要求EFI_SUCCESS，随后重新获取内存图/接口，核对当前Mode0、Info、stride、帧大小以及既有Display Reserved范围9c000000..9e400000。helper不解引用framebuffer。已验证的正常分配按原FreePool清理；无法验证的异常返回指针不free，保持有限分配至诊断复位。无重试，无合成EFI_SUCCESS。方法内部是否阻塞无独立看门狗保证。

## 取证与资格

新增code6等待27秒，只表示本次真实Core返回后，原厂GOP API/结构检查通过。code5仍为Core成功，但未获得通过检查的原厂GOP模式；code1..4沿原定义。两份新对照强制2/27秒，仍经过相同真实路径；对照时长不证明GOP成功。不能沿用v9低/高对照或旧拍摄，三个新trial独立且各一次。

主机执行器保持75秒恢复观察上限；27秒终止等待计入预算，不能据此保证原厂方法或Android在75秒内返回。超时停止追加并优先恢复，不自动延长或重试。时间码仅间接推断，未知复位/前缀抖动可别名，不能证明scanout/物理画面、ConOut/BDS/输入/XNU。

修正校准计划有效期：不得用创建计划的时间把旧控制观察再续期一小时；到期取两份控制观察各自一小时上限与计划创建一小时的最早者。v10六类和旧v9五类窗口严格分开，错族/过期/错误来源先于claim/设备命令拒绝。

helper的ASan/UBSan、严格ARM64编译与真实Core绑定失败门检查通过；55项Python包含新增六码/错族/到期边缘/目标缺计划先于设备拒绝。完整build1与最终链接/打包资格完成后追加。v9及R027等历史字节冻结，本轮不上机。

## 最终构建与资格

三份build1完整FD和qualification1通过，每份2475来源绑定，同一logic指纹。55 Python，gop1/clock2/progress1/path1/race1和各binding3，最终链接224/174/182逐条删除负测通过。固件2c18bc6，edc579d工作快照，不称提交后重编；全部未消费，校准未完成，无设备命令。

### target — oem-gop-mode-v10

- 镜像：`out/oem-gop-mode-20261028/target/qualification1/image.img`，3153920字节。
- image SHA256：`41585b244499f4405bb0050e31106480e0c039234d931ce4be83c79cab6e17c8`
- qualification1 SHA256：`a34b0fdb1d2c11ba7584c8bad7a9d306d9d61a3dc4977648d3b153c502332909`
- FD SHA256：`ddce655ea409c59b33ceb577cd8e59d71587b784bc694fd003d581cb82afb5e9`
- trial：`bff01371-9799-4d1f-8f58-c5e0143f794b`；session：`10001734413525956626`；未claim。

### low — oem-gop-mode-low-v10

- 镜像：`out/oem-gop-mode-20261028/low/qualification1/image.img`，3153920字节。
- image SHA256：`c9cb7c200ea35894e1002075102a432ac8d867c40d89291ef5da5771791ef586`
- qualification1 SHA256：`61710da895a2eb9774a2193f3fdccdef058d6ce34556086abc95975743b55a03`
- FD SHA256：`6e30c8eca82c6057cbfc7502988988bd55bfcd1baa2b6ae5f0066e3d85e12713`
- trial：`2f8dcedf-588e-4e05-809a-f653c1efc25f`；session：`3837297856041383997`；未claim。

### high — oem-gop-mode-high-v10

- 镜像：`out/oem-gop-mode-20261028/high/qualification1/image.img`，3153920字节。
- image SHA256：`d581d070a30a942fb0bb6662404e875c472ad1d36ccd366b124d45237080960e`
- qualification1 SHA256：`bb6d3f5386163875e1b583b3fbaf3078a82107492bc3f2d2fb1299e003e9a01e`
- FD SHA256：`92579193b3f4535a68829b012b25c72ec0d250ac1ba814fcd73e682a0bc7a34a`
- trial：`c6f3f7dc-52ed-4e9a-8dd2-721a87075cae`；session：`10631535210084727465`；未claim。
