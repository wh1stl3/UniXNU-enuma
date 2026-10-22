# 主分支迁移后的 DXE 定位

2026-10-22 Asia/Shanghai。沿 A-002 临时启动授权推进，不 flash/erase/改槽。所有启动后已回 Android，root、boot_a/vendor_boot_a 摘要不变。

## 实测与解释

| 候选 | 复位门 | ADB恢复/秒 | Android完成/秒 | 解释 |
| --- | --- | ---: | ---: | --- |
| 新底座stage10 | CoreDispatcher前2秒 | 16.952 | 31.357 | 升级基线回归通过 |
| stage11 delay2 | CoreDispatcher后2秒 | 30.826 | 44.497 | 仅观察到自动重启 |
| stage11 delay7 | CoreDispatcher后7秒 | 30.831 | 46.601 | 没有预期5秒差值，不能记为命中stage11 |
| stage12 ordinal1 | 首个实际队列项加载前2秒 | 15.870 | 31.623 | 与早期复位门一致，支持进入首项加载前检查点；尚无此门独立2/7对照 |

关键结果是**不把自动重启当调度完成**。stage11的ADB差仅0.005秒，Android完成时间还含用户态启动抖动；现有数据不支持已走到CoreDispatcher返回。可能为调度内停滞后的其他复位、入口异常或其他原因，尚未识别复位来源及具体模块。当前把重点放在队列项加载、驱动入口及后续调度，不能说已证实DisplayDxe是根因。

最后实测镜像 `out/boot-candidate/enuma-dxe-queue1-stage12-boot-v3.img`，SHA256 `d974069340e6fc69d5e8eb898bd3cdab4eff202a226fb449cbdfdc0dfd40850e`；FD `33d8dcc5d62ab61064dbb760672d989155f3968467c42b538250eedbeb641af9`。当前构建报告正对应此FD，不继承旧镜像的运行证明。

stage11 delay2 FD a5379465565fbb205424df285cd5a96b195480f8a1228474174eff6910cd7e89；delay7 FD dc8dbc436ca1e5824ec1709f0b53e9e086ebde25caae2623a8cdd075faa7267b。快照在 out/entry-probe/dxe-return-stage11-delay{2,7}/，当前stage12快照在 out/entry-probe/dxe-queue1-stage12/。各自保留构建日志、审计和FD。

## 实现与复用

原四个固件patch文件内容保留。新增 dxe-dispatch-return.patch 在CoreDispatcher之后挂stage11；新增 dxe-driver-checkpoints.patch 在真实Mu Dispatcher队列取项后、LoadImage之前挂stage12，并在真实CoreStartImage返回后挂stage13。

EnumaDispatchCheckpoint.h 仅在stage12/13统计实际队列序号，`--dispatch-ordinal 1..128`选择对象；不凭APRIORI顺序猜测GUID。加载失败会跳过StartImage后的门，FV项也不会走StartImage分支，因此stage13未命中不等于驱动入口必然卡住。下一步先用ordinal1的stage13分开首项LoadImage/StartImage，再按实测序号推进，必要时增加GUID关联证据。

复位仍复用Mu TimerLib和Arm PSCI ResetCold，`--stop-delay 2/7`作对照；不写NVRAM、日志分区或猜测MMIO。stage0保持无诊断复位。板内存字段、owned-memory与验证标记不变。

构建器针对重叠patch改为先逆序撤销完整系列，再顺序应用；初始化独立staging根，避免Git跳过嵌套路径。真实Mu archive中的DxeMain/Dispatcher文件已通过重复应用回归，31项Python通过；实际共享header的ASan/UBSan覆盖stage0、3..13、7秒选择和队列计数/前后门。

完整UEFI、81文件/33OEM PE-DEPEX字节、boot v3、当前source-overlay检查通过。不是GOP/菜单/完整XNU或触控运行证明。

## 一次推送前中止

第一次stage12尝试在fastboot身份校验中止：先product=enuma，随后current-slot查询失败，再查询三个身份变量均返回Variable Not found。没有发boot命令。仅对已由ADB确定的同一目标正常reboot，确认Android完成/root/分区摘要后才重试。原因未确认。获取完整身份字段的五次有界重试已加入工具，每次仍须所有字段精确匹配；本次成功重试不需要额外轮询。

证据：reports/enuma-entry-device-tests.json、enuma-fastboot-query-abort.json、enuma-stage-gates.json、enuma-dispatch-gates.json、enuma-firmware-build.json、enuma-fd-audit.json。设备标识与原始备份仅留out/。
