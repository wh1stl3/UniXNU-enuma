# 最新接手入口

2026-10-23 21:12后：用户已授权并完成step0/step1实机，两次无按键自行回Android，root/原分区摘要通过。以[STATUS](STATUS.md)和[本轮实测](operations/2026-10-23-gop-split-device.md)为准；下方为此前离线交接记录，其“均未启动/保持离线/下一轮先step0”已被本轮结果取代。固件版本及候选摘要不变，旧超时根因仍未定。下一步离线准备step2，不自动追加设备测试。

---

# 交接入口：GOP 查询与 Core 返回诊断

日期：2026-10-23（Asia/Shanghai）。本次仅整理交接并复核本地产物，没有查询设备或启动镜像。

## 接手时先读

依次阅读 AGENTS.md、[STATUS](STATUS.md)、[DECISIONS](DECISIONS.md) D-055/D-056、[NEED-REVIEW](NEED-REVIEW.md)，然后阅读[完整拆分说明](operations/2026-10-23-gop-core-return-split.md)。本文件是接手索引，当前事实以 STATUS 为准。

设备仓 D:/Code/UniXNU-enuma，main，远端 wh1stl3/UniXNU-enuma；实现里程碑 595d6a6 已推送。固件仓 D:/Code/uefi-enuma，main，远端 wh1stl3/uefi-enuma；固定 e2868342daee0c196942f1a5569526d3ecb80850 已推送，设备仓 firmware gitlink 和54项输入锁与之匹配。此次只补文档，不改固件。

## 实机停点与证据边界

最后一次实机：旧固件250849f，19:45:38临时boot被接受，75秒内未自动返回，已停止追加。用户人工恢复，19:48:15主机核验Android启动完成、root、解锁、原槽及boot/vendor_boot摘要通过。新一轮必须重新核验，不能沿用这个历史状态。

失败原因仍未知，不能认定GOP查询或PSCI已被定位。旧完整查询及旧互补镜像不再试。证据为 reports/enuma-gop-query-device.json；私有现场在 out/device-tests/20261023T194524-dxe-driver-return/，恢复指针 out/device-tests/current.local.json。原始备份在 out/device-tests/20261022T201404/，不要提交设备标识、备份或视频。

新实现移除SimpleFb本地复位依赖，恢复INF基线；安装后以非错误warning 1/5传递私有阶段标记，复用既有Core门。通过主机检查不等于新标记路径已在设备运行。两秒目标门和七秒完成兜底均为同步执行，无法救服务卡死。

## 已备好的两份镜像

以下相对路径均从 D:/Code/UniXNU-enuma 起算；此次交接已重算镜像SHA-256，与报告一致，均未启动。

- step0：`out/boot-candidate/gop-core-control-queue1-stage13-delay2-point16-guiddcfd1e6d-simplefb-metadata-boot-v3.img`
  SHA-256：`b0a144978775dcfb4bd96cd2010fdd70d9c9674b8577eed5ce162cdf7639c054`。

- step1：`out/boot-candidate/gop-core-enumerate-queue1-stage13-delay2-point16-guiddcfd1e6d-simplefb-metadata-boot-v3.img`
  SHA-256：`596967b636a728c469fc0f991a22c11d5697e8c37eafc7aa9f661170630c7944`。

共同配置：core-warning-v2、selector1、stage13/detail16/delay2、完整SimpleFb GUID过滤、完成兜底；只差ENUMA_DIAG_GOP_STEP。仍禁绘制、Probe早退。

step0仅安装后返回；step1增加枚举/校验/释放。step2句柄、step3元数据、step4 QueryMode仅有源码/主机/目标对象覆盖，尚未分别完整链接打包。

构建报告及AutoGen/静态库清单在 out/entry-probe/<variant>/。公开清单 config/gop-split-probes.json、报告 reports/enuma-gop-core-split.json。已有137阶段/参数、30标记、6实际Mu传输、7 CLI、177 Core回归和四份AArch64对象检查通过；两镜像完整链接/FD/BootShim/v3、四项bundle负向检查及串行workspace通过。本次文档整理未重跑这些构建测试。

## 下一轮执行顺序

1. 当前保持离线；收到继续实机指令后重新核对enuma身份、解锁、槽、Android完成/root、原分区摘要、匹配备份和现场恢复条件。
2. 先重新运行 scripts/check_gop_split_bundle.py 核对本地产物，再只测step0。不要把两个候选排成无条件连续执行。
3. step0无返回立即停止追加并恢复；这不能归咎GOP查询，因为它尚未调用查询。step0受控返回成立后才考虑step1。
4. step1无返回再拆枚举与释放。长返回不能单独定性为错误，必要时另构建同step的selector2对照，禁止混入旧250849f候选。
5. 每笔记录镜像摘要、命令结果、返回时序、真实恢复终点；回Android后核验启动完成/root/原摘要。无屏幕文字不持续录像；实际显示或恢复按键需要判读时录像，电源键在右上角。已有明确证据不重复问按键。

执行器 scripts/run_enuma_entry_probe.py 虽有身份/备份/恢复检查，但不会消费 current.local.json 的 next_probe_blocked_pending_fault_isolation 标志，也不自动封禁所有旧失败镜像；接手者必须先按上述顺序审查。旧 out/camera-capture/run_gop_query.py 绑定旧固件和旧候选，不改pin绕过拒绝，不用于新测试。

## 后续主线与保留约束

先恢复受控Core返回，再逐层查询GOP；实际几何/像素范围闭合后才接入EnumaScreen与菜单。EnumaScreen尚无INF/FDF/调用者集成，当前镜像不会输出其页面。尚未进入XNU。

iPadOS17.7.11/21H461、iPad7,1/j120ap、4KiB目标不变。平台源内核已在macOS CI39927966148链接，未donor预链接或启动；FAT配置卷仅离线生成，未接运输/发布。系统卷/内核后续见STATUS及系统预研文档，不以它们绕开当前UEFI阻塞。

512MiB owned与51MiB DXE heap不变；R-002跨启动日志失败后不换地址/扩区/借DFPS或SMEM。内存基址/大小、任何verified=true、破坏性分区操作仍须编号方案。只做可恢复临时boot，不擅自flash/erase/改槽；TWRP与UART接点均未验证。

遇难题继续评估同SoC真实UniXNU/UEFI实现；本轮elish来源只借鉴提供者与诊断分离，不照搬物理清屏/cache/PCD。nuwa及其他参考目录只读。构建与workspace qualification串行，及时归档共享构建目录中的AutoGen/库清单，避免下一次覆盖。所有产物留out，不入Git。
