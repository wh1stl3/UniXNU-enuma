D-323：本轮仅文档与本地提交；无录像、按键或恢复待办，实机暂停不变。接续见 docs/2026-10-27-displaydxe-handoff-prompt.md。

# 当前：用户暂停实机，没有录像/按键待办

仅继续离线工作。D321取代此前R027录像催办；R027未消费、未启动。以下为历史待办，不可据此执行。

# 当前待办：R027/S055连接与本次录像

新候选离线已完成，尚未发送。镜像0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a。01:48之前绑定enuma未以已授权ADB在线；请连接并进入Android、允许此电脑USB调试。需要明确本次R027一次临时boot和当前录像就绪后才执行；仅“晚上可用/随时录像”不是即时确认。无需提前按恢复键。录像覆盖整屏及后续恢复，媒体目录Media-enuma/S-055-R027。独立判读先由助手保存并公布，再由用户核对。R026/S054已确认并消费，以下旧待办均属历史，不得重复执行。

# R025 / S053：请准备本次录像；尚未发送镜像

最终build3/qualification2及真实菜单QEMU验证已完成。新镜像17a18ace93a002ac394ef4727148e893d7defe420496b4d3e8df7dde115be0cd，实验为(64,96)起800×600实际UniXNU菜单窗口、8秒倒计时，保存/恢复/读回。需要本次明确单次放行和当前录像已就绪，旧消费不复用。

请保持enuma连接电脑并停留Android，录像覆盖整块平板及后续恢复。无需现在按恢复键；按主机通知操作即可。媒体存放D:/Code/PortingiOS/enuma/Media-enuma/S-053-R025。仍采用助手先独立读媒体保存并公布、用户确认/纠正的核对流程。


## D-312：R025本次单次批准和录像确认

用户明确“批准 录像已经就绪”。仅R025/S053镜像17a18ace93a002ac394ef4727148e893d7defe420496b4d3e8df7dde115be0cd、(64,96)800×600真实菜单窗口一次临时boot获批准，当前录像就绪。此前D311待确认已关闭；尚未发图，即时身份/备份/恢复门由runner核对。无自动重试、分区刷写或提交推送；75秒无返回停止追加并恢复。执行授权记录out/r025-live-20261027/authorization.json。


# D-313：S053菜单窗口已实测并恢复Android，画面待用户核对

2026-10-27 00:09:34，R025精确镜像17a18ace93a002ac394ef4727148e893d7defe420496b4d3e8df7dde115be0cd仅执行一次临时fastboot boot，授权已consumed。发送返回0，ADB49.812秒，Android完成64.406秒；00:11:06开始的独立复核确认enuma/root/A槽/解锁、boot_a/vendor_boot_a和本地备份一致。用户也报告回到Android。无分区刷写、追加启动、提交推送。

助手已独立查看本地视频16/21/23秒帧并保存判读：UniXNU标题、版本0.1.0、enuma - bounded GOP experiment、Return to Android和GOP window test两项清晰可见；倒计时8/3/1秒，蓝色高亮由第一项变为第二项。文字避开圆角，底部No input device提示在the后截断。此为助手画面观察，等待用户核对后关闭视觉验收，不能提前写人工核对通过。

这是实际Ui/Menu经临时PixelBltOnly GOP的800×600内缩窗口显示证据；全UniXNURun/BDS/配置发现、实体输入、正式生产GOP、QR日志仍未验收。返回码未知，不套旧R024 code5时序，不从Android恢复推断窗口逐字恢复通过。requirements22保持；旧R022/R023/R024冻结产物未改。

证据：reports/enuma-menu-window-S-053-result.json；out/r025-live-20261027/authorization.json、postcheck.json、independent-visual-read.json；原媒体在D:/Code/PortingiOS/enuma/Media-enuma/S-053-R025，仅本地保留。最终镜像仍为out/menu-window-20261026/qualification2，execution-review.json和preparation2保存发图前绑定；它们是历史资格，发图后文档变化不追写旧资格。

下一步：向用户展示已保存判读并核对；然后离线接通完整菜单启动链、持久GOP生命周期及输入依赖。R025不得重试；新镜像另行资格和实机范围评估，不把本次批准扩张到下一次。


D-314：用户“对的”确认S053菜单文字/高亮/倒计时独立判读。原始证据保留，增量确认reports/enuma-menu-window-S-053-confirmed.json。R025 consumed，Android独立核验已通过；无待恢复或待人工转录事项。继续完整应用入口离线工作，不启动设备。


D-315：完整UniXNU独立应用入口离线通过，新增EnumaMenuApplication.h子系统表/GOP绑定与清理，真实磁盘TOML/UniXNURun/exit动作在application和firmware两入口通过，9种失败场景/22条命令通过。当前尚未接入板级profile、未生成新板级镜像；ConnectAll前置及GOP生命周期仍须处理。详见docs/operations/2026-10-27-full-menu-application-entry.md和reports/enuma-menu-application-development.json。S053已人工确认，R025 consumed，无设备动作、提交推送，冻结资格文件哈希一致。


# D-316：完整UniXNU应用固件已编译，离线资格通过

用户“继续推进直至编出固件”的本轮目标已完成。新full-menu完整FD及Boot v3启动镜像已生成，未上机、未提交推送。R025/S053保持consumed；S053菜单独立判读已由用户确认，设备最后经独立核验恢复Android/root/A槽/解锁且原分区摘要一致。本轮没有设备命令。

## 当前产物

- 镜像：out/full-menu-20261027/qualification1/image.img（103817216字节）。SHA256 d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce。
- FD：out/full-menu-20261027/qualification1/SILICIUM_UEFI.fd（3MiB）。SHA256 9d513b79c98662977d77acdc5c4984bf131bc10f4fe2b0c89e21e688e5c56ca8。
- build2于2026-10-27 00:58:56编译完成，完整编译2分11秒；独立工作区快照，不是干净提交构建。
- 软件资格：out/full-menu-20261027/qualification1/qualification.json，通过，execution_ready=false。新候选范围标识R026，尚未请求/登记单次实机批准。

## 本版实际运行路径

保留原DXE stage13诊断入口，从固件卷加载真实UniXNU EFI，给子应用绑定私有GOP系统表和仅含exit动作的只读内存配置卷，实际运行完整UniXNURun/配置解析/菜单/动作返回。application host避免配置加载前无条件ConnectAll。GOP覆盖整个子应用执行期，退出后先关闭子应用与配置卷，再撤销GOP并释放内存；故障停止present、恢复窗口、卸载失败保留引用存储。

仍是(64,96)800×600/8秒有界窗口，scale1修复底部文字截断；物理读写/屏障/MDP预算不增加，requirements22/verified/内存参数不改。不是正常BDS链完成、实体按键或生产GOP准入；尚无XNU启动或QR日志。菜单返回后沿现有Core诊断复位，自动复位不作为未来菜单的额外前置要求。

## 已完成验证

本次实际UniXNU PE经qemu3端到端23条命令通过，完整真实配置/菜单/exit、模拟像素恢复、读1687441/写1207441/屏障30，CRC69F91C2A。包含只读卷读/写拒绝/EOF/seek/句柄/分配失败及9种子镜像生命周期场景；host1另46组/24通道事务故障检查通过，策略及旧R025回归23项通过。FD内30个OEM PE/DEPEX一致、宏与配置实际字节正确、完整96MiB FAT和Boot v3反解一致。

build1因本轮DSC CRLF导致旧LF补丁不匹配失败，修复为LF后独立build2成功，失败证据保留。新旧资格文件哈希复核一致；没有覆盖旧镜像/资格或媒体。

## 下一步与边界

本轮停在用户要求的编译完成点。实机之前还需针对新的完整应用路径做编译后指令/嵌套分派复核、新单次执行器和来源/文档绑定，再确认此镜像单次批准与当前录像/即时设备门禁。不得沿用R025或把本软件资格当作实机通过。不需现在按恢复键或开始录像。

详细实现、失败过程和复现入口：docs/operations/2026-10-27-full-menu-firmware.md。总报告：reports/enuma-full-menu-development.json。历史完整应用单独VM验证D315和S053确认报告保持原字节。


# D-317：R026准备完成，本次录像已开始，S054待发图

R026镜像d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce，资格10d3564a3cd5d4fce35b7b597098a0de31a546d9186d5cbe74da7d9a60d77221，冻结qualification1不改。584字节物理回调与R025一致，Core.text/.data一致，子应用加载/系统表/卸载/只读拒写/首错与清理门逐条核对，删除关键指令3种变异拒绝。嵌套应用不能冒充调度驱动的ASan/UBSan检查通过；应用类型跳过Core自动连接，application host无隐式ConnectAll。60项执行器/策略/旧准备器回归通过。

01:12:03独立只读核验enuma Android完成/root/A槽/解锁及设备与本地备份摘要通过。用户明确要求机器码复核、失败路径、单次绑定与构建同轮完成，只差录像时停；以后遵守此工作方式。用户随后“我开始录像了”，绑定当前R026一次临时启动与当前拍摄，授权记录out/r026-live-20261027/authorization.json。尚未claim或发图，将再做即时门禁，不自动重试。

范围：真实FV UniXNU EFI→只读exit配置→完整UniXNURun→800×600内缩/scale1/8秒→应用退出、窗口恢复与原诊断终止。正常BDS、实体按键、生产GOP、XNU/QR未验收，requirements22保持。旧R025/S053 consumed，画面已确认且Android已恢复。

执行绑定out/full-menu-20261027/execution-review.json；preparation1仅为空目录（首次只读验证因Windows无法读取WSL链接而退出，未发图），有效准备将写preparation2。入口scripts/run_full_menu_trial.py默认离线，显式--execute --human-camera-ready和独立UUID才启动。75秒无返回停止追加并恢复，不套旧日志code5时序。媒体D:/Code/PortingiOS/enuma/Media-enuma/S-054-R026仅本地；助手先独立保存判读再给用户核对。无提交推送、分区刷写、改槽或nuwa操作。


# D-318：S054完整应用菜单已拍到，Android恢复通过，画面待用户核对

R026/S054已单次消费。2026-10-27 01:25:32发送镜像d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce，fastboot返回0/2.641秒，ADB49.797秒，Android完成66.000秒。01:28:03独立检查enuma/root/A槽/解锁、boot_a/vendor_boot_a及本地备份摘要通过。无分区刷写、追加启动、提交推送或nuwa操作。

实际落地媒体为单张照片（不是完整视频）。助手已独立查看并保存判读：UniXNU标志/标题，版本0.1.0，config路径\EFI\UniXNU\unixnu.toml，第一项Return to firmware蓝色高亮，Booting Return to firmware in 1 s，完整No input device提示，drivers 0 loaded / 0 failed、kits 0、acpi 0。无圆角遮挡，底部提示未出现上一版截断。当前等待用户核对，不预写人工验收通过；单张照片不证明8秒持续或完整倒计时过程。

结合精确已绑定镜像，此画面对应独立UniXNU应用的真实配置/菜单路径。底部drivers计数是UniXNU配置注入驱动统计，不是全部UEFI DXE驱动数量。当前仍为DXE早期显式应用加载+有界GOP/内存配置，非正常完整BDS；实体输入、生产GOP、XNU/QR未验收。返回码未知，不套旧R024 code5窗口，不以Android返回推断窗口每字恢复通过。

用户问为何比nuwa快：当前enuma省略正常BDS/全控制器连接，未启用OEM DisplayDxe/UFSDxe，使用继承显示和私有内存配置，工作量明显不同；这是对enuma当前路径的解释，不是nuwa耗时分布已核验，也不称enuma完整固件性能领先。

用户持久要求：构建、机器码复核、失败路径和单次绑定同轮完成，只差当前录像时才停，不再把离线步骤拆成多轮停点。当前单次已结束，先完成媒体人工核对，后续新软件离线继续；不得重复R026。

证据：reports/enuma-full-menu-S-054-result.json；out/r026-live-20261027/authorization.json、postcheck.json、independent-visual-read.json。原媒体D:/Code/PortingiOS/enuma/Media-enuma/S-054-R026，仅本地。冻结qualification1、execution-review和preparation2保存当时绑定，不回写旧资格。剩余工作是正常入口/持续显示与输入依赖，下一次候选仍独立资格及单次/录像门禁。

## 2026-10-27：OEM入口与返回RVA离线增量

已核对Core真实EntryPoint传入Image->Info.SystemTable及同句柄LoadedImage来源；新增精确OEM PE返回RVA校验工具，6项失败/指令测试通过，原追踪5条资格命令独立重跑通过。证据out/oem-rva-20261027-session-c999；详见docs/operations/2026-10-27-oem-rva-and-entry-binding.md。未接Core/profile、未运行OEM或新建固件候选；现有同步像素窗口不能保证OEM非返回时的恢复/所有权，取证出口仍阻塞。实机暂停、R027冻结未消费，无人工录像待办；本轮新增代码/测试/文档准备本地提交，不推送。共享工作区其余文件保持。
