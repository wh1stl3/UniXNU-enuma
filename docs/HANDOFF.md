> 2026-10-28 v10本次实机准备：用户明确“可以部署实机了”，并确认“正在拍摄，在场可恢复”。本轮独立记录现场条件，按low2→恢复/人工确认→high27→恢复/人工确认→精确校准→target顺序，各一次临时boot，不自动轮测。候选尚未claim；即时身份/原备份/恢复与当前文档发布门禁通过后先发low。75秒未回合格终点停止追加、优先恢复。不flash/erase/改槽，不改内存或verified；R027冻结、共享主线只读。证据out/oem-gop-mode-live-20261028；v10原有离线资格和镜像字节保持。

# 当前：gop-mode-v10三份镜像与软件资格完成，未上机（2026-10-28）

2026-10-28当前：gop-mode-v10目标及2/27秒对照已完成完整build1、qualification1和离线来源核验，三trial未消费。本机Clock/HAL ABI核对后未发现可确认的接口错配，保留原始方法，新增真实Core成功及整轮DXE后原厂GOP QueryMode/SetMode/读回检查。55项Python、sanitizer/ARM及224/174/182处链接删除负测通过。v9仅离线对照、不安排上机；旧源码准入已过期但镜像/资格字节冻结。没有本轮设备动作，不沿用旧拍摄/校准。

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

## 当前分析、行为及证据

优先级按用户要求固定为三路显示时钟→HAL IOMMU→生产GOP模式/控制台。精确本机Clock接口1e150/版本10009、GetClockID14dc、EnableClock1524与固定头一致，三路名称存在；后端依赖319f0的DAL上下文。HAL接口9098/版本1、GetAPI14cc写出函数表90b0，与DisplayDxe真实参数一致；create16b4、attach1920、configure-bypass2f10。该本机HAL入口发布后调用的15a0只是返回0，不能借公开旧平台dummy失败路径认定本机同错。原始XBL也把HAL放在Variable/Watchdog等之前，通用Arch DEPEX不构成盲目重排依据。实际方法运行状态仍未知，无新实机根因结论。

v10原厂PE、Clock/HAL提供者、私有SystemTable同步与RAM事件临界区保持。整轮CoreDispatcher返回且匹配目标Core严格EFI_SUCCESS后才进入新helper；失败状态、缺Owner/返回位、其他镜像不能启用它。枚举最多8个GOP handle，唯一候选的QueryMode/SetMode/Blt函数须位于本次已认证原厂DisplayDxe text，解引用前校验原Core内存图与RAM跨度/算术。QueryMode(0)最多一次，核对1600×2560/stride/像素格式；正常信息分配回收后最多一次真实SetMode(0)，再读回Mode0、Info及framebuffer尺寸/既有Display Reserved边界。未绘制，不Blt、不ConnectAll、不进BDS、不直接访问MDP/像素或循环显示电源，不伪造EFI_SUCCESS。

新增code6等待27秒，仅对应真实Core成功后的原厂GOP API/结构检查通过；code5为真实Core成功但GOP模式未通过完整检查，code1/2/3/4保持异常/诊断终点/缺匹配返回/Core非零。新low/high强制2/27秒且保留真实GOP路径，不能从对照时长推断成功。无独立看门狗，方法内部可阻塞；75秒主机恢复观察限不变，27秒等待计入预算，不能保证自动返回。时间码仍是间接推断，不能证明物理scanout/画面、ConOut/BDS/输入/XNU。

GOP helper ASan/UBSan与严格ARM64通过，覆盖唯一原厂候选、错误/警告、坏指针/内存类型、大小/stride/格式/帧边界、清理失败和禁止重试/禁止Blt。真实Core绑定验证错误状态/错handle/缺Owner不能进入GOP。55项Python含六码/错族/缺计划先于设备拒绝及校准到期边缘；计划到期不再由创建时间给旧观察续期，取两个控制观察的一小时上限与计划创建上限的最早者。最终PE224/174/182逐条指令删除均拒绝，覆盖Core身份/真实状态门、同步与事件、GOP原厂代码归属/实际QueryMode/SetMode/最终边界以及CPU时钟出口，仅为选定序列而非全程序证明。

三份FD/原厂模块/panel RAW/真实compiler flags、Boot v3封包解包和每份2475绑定通过，同一源码logic指纹，全部未claim。固件2c18bc6；构建基于edc579d工作树快照，不能称提交后重编。有效组件证据gop1/clock2/progress1/path1/race1和各binding3；初次宿主夹具缺ZeroMem实现的链接错误已补齐夹具，不放宽真实编译条件。v9三图/旧资格及R027/v6/v7/v8冻结摘要复核通过。最后设备证据仍是v8在00:51自动回Android及独立恢复/原分区核验；本轮零设备命令，当前在线状态未刷新，无恢复欠项。

## 下一步

本轮不再安排v9上机，仅保留未消费离线对照；源码升级后其旧准入不再适用于当前树。新v10按当次现场条件依次low→独立恢复/人工确认自动返回→high→同样确认→生成精确目标校准计划→target，各一次临时boot，无自动轮测。目标execute缺少/错族/错图/错源/过期校准时在claim和任何设备命令前拒绝。每次重新核对enuma、原备份/双分区、恢复路径及当次拍摄和人在场可恢复；不继承v8/v9就绪。

控制报告须automatic_android_return=true、independent_recovery_passed=true和本次clock_observation；新boot_id、原点区间<=0.25秒、扣除2/27秒后基线包络<=1秒，用固定±1秒窗口，不能用Android总就绪耗时解码。两份观察的一小时有效期不能靠晚建计划延长。目标完成后同样独立恢复并确认按键事实，再作间接分类；歧义、漂移、人工恢复不给正向类别。75秒未回合格终点停止追加并优先恢复，不自动重试；恢复后继续离线分析。

若仍提前终止，按本机三路时钟DAL后端与HAL domain方法链取证；若真实Core/DXE及GOP模式的合格间接码支持推进，再独立验收物理画面、ConOut/受控控制器连接和BDS。不能硬编码family、跳过提供者或复制外机SMMU stream IDs。共享UniXNU-enuma只读、R027冻结；不改内存base/size/verified，不flash/erase/改槽。原始媒体/out/二进制/备份/标识不入Git或云端。

默认离线入口，无设备命令：

```
wsl --cd /mnt/d/Code/PortingiOS/enuma/worktrees/enuma-oem-display /usr/bin/python3 -B scripts/run_oem_runtime_trial.py --qualification out/oem-gop-mode-20261028/target/qualification1
```

详见operations/2026-10-28-oem-gop-mode-v10.md、reports/enuma-oem-gop-mode-v10-candidates-20261028.json、reports/enuma-oem-clock-hal-static-20261028.json及out/oem-gop-mode-20261028。固件→设备仓按显式GitHub URL/oem-progress-20261027发布，不推firmware的本地origin，不force。实际发布以git log及本输出publication.json为准。
