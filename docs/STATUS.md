# STATUS

更新：2026-10-22（Asia/Shanghai）。当前唯一真相；历史见 WORKLOG。

## 当前结论

**已接入UniXNU主分支固定版本5fdbd5d及21个固定模块，保留enuma原四个固件patch、板级驱动和boot v3；macOS真实通用4 KiB XNU最终链接与审计通过。主线已回到实机DXE定位，仍无GOP通过证据。**

设备仓仍为独立overlay，整树留在忽略的out/sources/UniXNU；原共享参考源码与nuwa不作编辑。目标仍为enuma/SM8250、iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4 KiB。board.toml未变、example=true、已批准512 MiB请求，未改内存大小/基址或 *_verified 标记。

## 上游与构建

- 75bc13dd → 5fdbd5d（本轮查询的main，领先101提交）。21模块SHA、源接口、GENI独立来源和补丁摘要均已锁定。DarwinBoot新增AddonOffset契约已迁移，不自动开启新驱动。
- 新增编译期legacy display保护：关闭功能不再引用该符号，开启时保留真实驱动；没有添加空stub。完整内层XNU patch可应用到固定Apple原文件，主机对象0/1符号对照通过。
- macOS **run39790786938成功**（设备提交d3ce3c4）：固定21模块及本地patch、Xcode16.4/SDK18.5、arm64编译、通用最终链接、Mach-O/初始TCR审计均通过。21,041,528-byte产物SHA256 **de5ccd244f0b4fd6c0ebe5f6173aa6f7be993e31aa45db583150cd65c2f4c0fd**，TG0/TG1均4096。artifact已回读并重算hash。它关闭板级功能，不是可启动enuma内核或donor prelink。
- 历史run39784240390是旧legacy符号链接失败；迁移首次run39789234153在头文件匿名API403失败、未编译。已用固定Apple Git树提供同格式元数据，复用原恢复器与blob校验，26文件主机核对通过；随后上述新版CI成功。
- 31项Windows Python、共享诊断头ASan/UBSan（stage0/3..13、延时和队列序号）通过。GENI/NT36523/UFS主机回归及四个AArch64对象在新底座通过。完整UEFI、81文件/33OEM字节审计、v3回读及当前overlay检查通过。

## 最新实机

- 新底座stage10调度前2秒门：ADB16.952秒，Android完成31.357秒，基线回归正常。
- 调度后stage11的2/7秒候选：ADB分别30.826/30.831秒，只有0.005秒差，**不支持已命中调度后门**。自动重启来源未知，不把它记成CoreDispatcher完成或GOP成功。
- 新增实际队列加载前stage12、StartImage返回后stage13及1..128队列序号选择。首项加载前stage12实测：ADB15.870秒，Android完成31.623秒，root/分区摘要不变，支持到达首项加载前；该门尚无独立2/7对照。
- 首次stage12因fastboot身份查询异常在推送前中止；没有发boot命令。正常reboot核对Android/root/摘要后才成功重试。原因未确认，工具保留全部身份匹配并加入有界重试。
- 最新镜像 out/boot-candidate/enuma-dxe-queue1-stage12-boot-v3.img，3153920 bytes，SHA **d974069340e6fc69d5e8eb898bd3cdab4eff202a226fb449cbdfdc0dfd40850e**；FD **33d8dcc5d62ab61064dbb760672d989155f3968467c42b538250eedbeb641af9**。当前构建/审计报告与之对应。已回Android；未flash/erase/改槽。

按官网仍属阶段1 UEFI。阶段编号是内部复位点；没有GOP base/stride/format、UEFI内存图、菜单/FAT负载卷、DarwinBoot/XNU或触控实机运行证据。Android1600×2560及35MiB cont_splash不是GOP或黑屏根因证明。

## 下一步

1. 用stage13/ordinal1分开首项加载和入口返回，再按实际队列序号/必要GUID门缩小调度内故障；不要盲重试原黑屏镜像。新候选始终核对目标、备份与恢复路径，结束回Android。
2. 优先取得实际GOP、UEFI map、BDS/Probe与菜单协议闭包；新内存字段、预算或验证标记仍需审查。
3. 再补完整ADT/NVRAM/种子/占位符，推进真实板级archives、最终enuma内核和donor prelink、基础平台与NT36523 IRQ/HID。SM8550 PHY/电源/A740不得继承，A650后置。

公开origin https://github.com/wh1stl3/UniXNU-enuma.git；迁移83f4608与获取修复d3ce3c4已推送，本固件里程碑提交号见Git。无新增硬停或待按键事项。

详细证据：[主分支接入](operations/2026-10-22-upstream-integration.md)、[DXE定位](operations/2026-10-22-dispatch-checkpoints.md)、reports/enuma-macos-upstream-success.json、enuma-entry-device-tests.json。历史官网144页核对与入口探针记录保留，各自版本范围不转移。
