# 当前进度：超时恢复后隔离唯一staging条件

2026-10-24 Asia/Shanghai。用户要求更大胆推进，仍以证据决定实现，沿人工恢复后继续离线修复及直接只读实测授权。

## 上次硬停与当前恢复

8fd3e62 step22正向2026-10-24 16:03:42临时启动，image429c3c14ec2ee527a554012140049baad1f1ac67fb84bd925c849ce7df64d97e，75秒无ADB/fastboot自动返回；约16:04:58触发硬停，16:05:02确认并停止追加，反向未执行。用户长按恢复Android，16:06:02独立sys.boot_completed=1/root/原槽/解锁/匹配备份及boot、vendor_boot原摘要通过。当前恢复阻塞解除，Android完成；不将该笔写为自动/无按键成功，六类结果unknown。失败正向及未执行反向均冻结不原样重试，历史源锁uefi-8fd3e62.lock.json保留，证据enuma-scanout-blend-reason-device/preflight及operations。0efa313已提交推送恢复交接。

## 主判断

中等置信先查观察器/ABL遗留配置不匹配，DSI整体停摆和Boot格式低优先级。step22超时的新增长等待/继续blend采样是隔离点，尚无根因定论；先用不新增寄存器地址的唯一staging条件区分额外源，再考虑dim/alpha。

## 新隔离候选及审计

固件 c45e52a24f7c094e5949cc0ed6f7e017e4233b78，69项源锁/gitlink固定。step23从原step20完整算法出发，仅将已读四个staging字复制到局部变量、局部屏蔽已知CTL_MIXER_BORDER_OUT bit24后调用源编码解码：要求只含首候选非virtual源、stage编码1..12。保持第一个描述和第一个关联CTL/LM，不换候选；原完整四字仍每窗复查，border变化也拒绝。旧step19/20/21/22头文件字节保持。

隔离依据：step20先前多次及8fd3e62同源实机通过；新step23不新增任何MMIO地址，不读取LM_OP_MODE/dim/alpha，不调用长编码Stall；最大250读/两次既有Stall(100000)，保留原major/minor6.0、几何、所选活动DSI两窗各非回绕1..64递增及描述/配置稳定，Core仍原2/7秒正互补。这同时移除step22新增长等待与完整blend访问，不能称已确定超时根因。固定小米52a2f18在没有BASE源时可设border，故border本身不等于另一SSPP；源/FDT契约沿enuma-scanout-blend-sources.json。通过只降低额外源字段解释，不证明无dim/alpha、实际物理LM/pingpong/DSC、fetch/IOVA/cache/面板可见。拒绝不等于高层遮挡，需继续解码额外/未知/virtual字段和层次。

69项O1/Oz+ASan/UBSan及精确250读、禁止fixture读取blend地址/长等待、AArch64仅gBS通过；真实Mu GOP补丁/marker、5项像素/恢复守卫、源锁/workspace通过。三份完整链接/回退、30OEM PE/DEPEX、AutoGen/库、实际FD受限指令指纹、Boot v3及同源宏差异bundle通过。PE指纹不是完整动态MMIO/store/CFG证明；锁定源码和故障注入另审边界。三份仅step/query宏差异，pixel flag0。

| 候选 | step/query | Boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- | --- |
| stage23-control | 20/1 | `459961e1675150602631647e6db7760a929bed19f922111dd3bccc606d9f0416` | `7e2ec318f63505bbddaa19c663acd8ae6e2ab50f260338f6667853d384279bf3` |
| stage23-sole | 23/1 | `4a88e6e6ca8d0f5fbe16ea2de4e48dfc49a3b20bb3a95974eafdbe865878e4ff` | `73a37c143caca27f06d2f4ba48eaa2cc7a1096fd0e7281450cef39245e78b6c3` |
| stage23-unproven | 23/2 | `c8984dd00ed4f877eb29e5435a2872ebb6a47672f2e8405ca36aac85fc60203b` | `a3ae18bc5d3ce45d0d520b71c152cc2acf64108480d3e94a627485e64b6f6b84` |

## 最新实测

c45e52a尚未新实测。最近设备为step22超时后人工恢复Android，独立完成/root/原槽/解锁/原分区摘要通过；见enuma-scanout-blend-reason-device.json。

本轮互补未齐，唯一staging条件未知。

## 下一步与边界

全部当前文档提交推送后，以即时身份/备份/恢复核验临时启动stage23-control；独立恢复及无按键确认后继续。

用户可在场恢复，主机摄像头原图保留、自行旋转判读，必要前后截图，真实输出/判读变化/恢复时录像。即时身份/Android/root/原槽/解锁/备份与原分区摘要保持；Android/fastboot已核对，TWRP/UART未验证。超时立即停止追加、优先恢复并当轮落实交接；恢复后继续离线新软件，不重试失败镜像。R-005 consumed，无像素/MMIO/分区写入、新映射/内存基址/大小/verified变更；51MiB heap、512MiB owned、example=true和Boot v3保持。原始日志/图像/标识/备份/镜像仅out。仍无可见日志/菜单，文本后端未集成，未进入XNU。

证据firmware/docs/scanout-sole-stage.md、config/scanout-sole-stage-probes.json、reports/enuma-scanout-sole-stage-{host,bundle,device,preflight}.json（device仅实测产生时存在）、operations/2026-10-24-scanout-sole-stage.md及display-fault-hypotheses.md。每笔前全部当前文档提交推送、即时核验后才启动。

## 对照超时恢复更新（取代以上待实测状态）

# 当前进度：同源step20对照超时已恢复，转启动状态隔离

2026-10-24 Asia/Shanghai。用户要求更大胆推进；新证据已推翻“仅step22长等待/新增blend逻辑导致超时”的单一解释，当前不追加显示探针。

## 两次硬停与已核验恢复

8fd3e62 step22正向16:03:42启动，75秒无自动ADB/fastboot返回，立即停追加；用户长按恢复，16:06:02 Android完成/root/原槽/解锁/匹配备份及原boot/vendor_boot摘要独立通过，0efa313推送。反向未执行、冻结，六类未知。

恢复后按持续工作规则完成隔离新软件c45e52a：step23从step20仅加局部staging解码，允许border，不新增MMIO地址、不读dim/alpha/LM模式、不长等待；最大250读/两次100ms。69项sanitizer用例/AArch64及完整三份构建/实际FD/OEM/依赖/Boot v3审计通过，86adc68文档推送后2026-10-24 16:20:56启动同源step20对照（尚未执行step23）。Boot v3 SHA-256 `459961e1675150602631647e6db7760a929bed19f922111dd3bccc606d9f0416`，FD `7e2ec318f63505bbddaa19c663acd8ae6e2ab50f260338f6667853d384279bf3`。约16:22:12观察期限内仍无返回，16:22:16确认manual-recovery-needed，再次停止追加；stage23正/互补均未执行、冻结。

用户再次长按恢复并明确确认Android；2026-10-24T16:23:08.877428+08:00独立enuma、sys.boot_completed=1、root、原槽、解锁、匹配备份及原分区摘要通过。当前实际Android完成、恢复阻塞解除；不能称两笔自动返回或无按键成功。硬停来源AGENTS失联/无法受控返回规则，每次均优先恢复，当前交接本轮落实。无分区写入，原始日志/备份/标识/相机只存out，摄像头自行旋转判读。

## 已完成离线分析与更新主判断

成功reason22-control与失败stage23-control宏完全一致，均79模块；77个PE/DEPEX完全相同，仅PcdDxe和SimpleFbDxe二进制差异。SimpleFb的.text、.data、.pdata、.reloc逐节SHA完全相同，仅.rdata不同。详见reports/enuma-step20-control-comparison.json。因此新显示算法代码差异的解释进一步下降；.rdata差异是否纯元数据及PcdDxe差异仍需解析，不能现在称完全相同固件。前次step22超时不应唯一归因长等待，结论已修正。

中等置信首查：恢复后启动链/ABL遗留状态差异、跨构建PCD/元数据/打包状态及早期执行位置。现无早期日志或返回marker，不能证明执行到了SimpleFb/MMIO，面板/DSI/staging/alpha皆不能据超时定责。Boot v3格式此前同源基线多次正常，整体切换v1仍低优先级。

## 下一步（离线继续）

冻结step22失败正向及未执行反向、stage23失败对照及未执行正互补，不重试。继续解析两个差异PE的节/PCD有效数据，核对BootShim/打包字节；据此准备具有更早停止点、无显示MMIO/等待的新启动定位软件，先资格和全文档推送，再即时身份/恢复门禁后才可实测。用户人工恢复后继续离线规则有效；本次不以恢复后盲加显示探针作为推进。当前无新增批准项或人工待办，未宣称新自动返回资格。

R-005 consumed，禁像素/MMIO/分区写、新映射/内存大小/基址/verified变更；51MiB heap、512MiB owned、example=true/Boot v3保持。TWRP/UART未验证。尚无可见日志/菜单，文本后端未集成，未进入XNU。

证据enuma-scanout-sole-stage-device/preflight、enuma-step20-control-comparison及operations/2026-10-24-scanout-sole-stage.md；新源码c45e52a资格沿bundle/host，超时不能冒充运行通过。当前文档推送状态以实际Git远端核验为准。
