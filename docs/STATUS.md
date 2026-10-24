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

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。
