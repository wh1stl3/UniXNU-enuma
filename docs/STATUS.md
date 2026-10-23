# 当前进度：R-005已批准，同源候选完整资格通过

2026-10-24 Asia/Shanghai。用户在本轮明确“批准R005”，并确认可以在场恢复、在合适时使用摄像头。批准仅对应c73eb6e下述最终step13一次临时启动；精确摘要已绑定审批账本，不扩张为重试失败镜像、寄存器写入、分区操作、新内存字段或verified变更。

## 设备与实测

step12：2026-10-24 01:20:42，阶段recovered-android-boot-complete，ADB15.875秒/完成32.281秒，用户无按键确认True，原摘要核验True。

本轮只读预检见reports/enuma-r005-preflight.json：enuma、Android完成/root/原槽/解锁、boot/vendor_boot与备份摘要通过。此预检不替代每笔runner即时核验。Android/fastboot沿既有恢复证据，TWRP/UART仍未验证。

## 当前c73eb6e候选

| 候选 | Android boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- |
| step12 | `d656b861d4054c7165bfbfc370818776266cea5930942b803434e883ccf7b0d5` | `5ad3039820ef8e1c99c88ee68c147b75f15927e85ce1ba42d3f6542f79489250` |
| step13 | `c81def7defd58f55beb7b3c22161b3314fb20b49d98057279074d0ea385df534` | `5eba112a1091151cffb1d4ba496cd21d6ea34bfe785f78a625bc324ef21a0394` |

62项源锁、完整官方backend链接和补丁回退、30个原OEM PE/DEPEX、AutoGen/静态库无新增reset/PSCI构造器、3MiB FD、192字节BootShim/Boot v3、实际FD内像素缓存指令及成对bundle均通过。两份仅step/显式像素旗标不同；默认及step0..12不写像素。33假显存场景O1/Oz+ASan/UBSan和AArch64对象通过，6审批/4FD策略/7v3/1恢复/3身份测试通过。这些是离线资格，不能当硬件通过。公开顶层build/FD/payload报告现对应最新step13，step12独立快照在out/entry-probe，公开成对摘要在reports/enuma-pixel-preview-bundle.json。固件主分支文档71cd5cb已提交推送，记录本轮批准；设备gitlink保留c73eb6e以固定实测源码，子模块旧pending文字是历史快照，当前批准以本仓用户记录及账本为准。

R-005仅128x8白条500000us：保存4096字节、二次描述核对、绘制、恢复、读回；最多2048像素读/2048存储、96寄存器只读、24行缓存同步。只写八行各128个32位字，各行gap不写；无新映射/heap/构造器/模式切换/显示寄存器存储。选中描述仍可能不活动或为IOVA；无可见白条不能单独证明地址错误。

## 下一步和限制

同源step12已由用户确认全程无按键返回，Android完成/root/原槽/原摘要通过。先提交推送本笔实测及全部当前文档，然后连续录像并经完整即时门禁执行已批准step13一次。

摄像头DSHOW 1920x1080已实际取帧并核对画面；旧cp313 NumPy与当前Python3.12不兼容，已在out/camera-tools-py312隔离安装。只读对照使用前后截图；像素实验必须启动前连续录像，保存实际帧时序、镜像摘要和恢复检查。所有视频/原始日志/备份/设备标识留out，不公开。同步Core复位不是watchdog；异常可能阻止恢复，超时立即停追加、优先现场恢复并当轮更新交接，恢复核验后自动继续离线分析与新软件。

尚未确认写屏或进入XNU；51MiB DXE heap、512MiB owned、example=true和全部verified不变，不flash/erase/改槽。原838b38f step3失败根因未知，image a8061b8510935bbe8991ec0d8723a1bcc3b1a9460422ecc9ac30ffe13813016a禁重试。参考仓只读。旧4db/d8离线镜像仅历史证据，不能替代当前同源对照。

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。
