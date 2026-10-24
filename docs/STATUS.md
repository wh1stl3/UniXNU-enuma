# 当前状态：zero2 超时后已核验恢复，隔离方案已审并撤回，下一步建挂死率基线

2026-10-24 23:45之后，Asia/Shanghai。本轮只读核验、离线构建与文档对账；未启动新候选，未写设备分区。

## 当前设备与恢复

enuma已恢复Android，主机独立核验boot_completed=1、root、原A槽、解锁，以及boot_a/vendor_boot_a设备和本地备份摘要匹配。证据 reports/enuma-recovery-reconciliation.json，原始证据 out/device-tests/20261024T230449-recovery-reconciliation.json。恢复的具体人工动作/发生时刻未独立记录，不推断。失败试验result.json未改，current.local.json通过新恢复证据更新为recovered-android-boot-complete。

本轮接手时再次只读核验：`d0fd0840`=enuma、`boot_completed=1`、`_a`、`flash.locked=0`；同时在线 `fe5ed56e` 是 nuwa（只读参考，不是目标）。无需再次要求恢复按键；恢复不代表固件问题已解决。现有value transport计划仍冻结，不因恢复清空失败账本或原样重试失败镜像。

## 最近实测及硬停

| 试验 | 实际发出时间 | ADB返回时间 | 结果 |
| --- | --- | --- | --- |
| zero1，常量0 | 22:49:52 | 16.991秒 | 自动回Android，root/分区核验通过 |
| known3，常量3 | 22:50:59 | 25.503秒 | 自动回Android，root/分区核验通过 |
| zero2，常量0 | 22:52:12 | 75秒观察期无自动返回 | runner退出2，停止追加，计划冻结 |

时间来自各result.json的issued_at；目录时间22:49:38/22:50:44/22:51:58是准备时间，不当作boot发出时间。zero2观察期限结束约22:53:27；没有单独事件时间戳，不把估算当精确硬停时刻。

最后候选zero2与zero1镜像相同：SHA256 9b3c1df33c2fc5f0612cc0b669434607cf85547bed75c36c897603dee82a9ce1；FD bfb3d6a6018498ea1b94368b1d8a394983234b32d84368fdf0df49f41d1c1551。known3镜像357706af66517e7c1d7dac9629f55b1ee57e88b6701bfa4176315a3f4d3ace96；FD72d2b0a9384bdb7ba76b43b9c24bb69f42c8c65f1cf7eed27070df338300a3b2。两份已归档产物本轮复核完整（sha256 与资格记录一致）。构建固定固件74598df的等价源码；精确资格见reports/enuma-value-transport-qualification.json和out/value-transport/。失败账本reports/enuma-value-transport-device.json保留。

## 可支持的结论与未知项

前两笔差8.512秒，对预期9秒残差0.488秒，符合0.75秒容差：这是符合预期的延时响应证据，不能称完整通道已校准或可靠。第三笔零码未返回，完整0/3/0校准失败，禁止解码寄存器。未执行任何新寄存器模式、像素实验或XNU启动。

**本轮把这一条再推进一步**：常量helper在`Code==0`时直接`return EFI_SUCCESS`，不调Read、不调Wait、不写寄存器，且zero1/zero2是同镜像同码，故这段"什么都不做"的代码一次返回一次挂死。因此挂死**不必**与显示访问相关；剩余嫌疑至少还包括fastboot临时boot载体、XBL侧对临时镜像的处理、以及连接/供电时序差异，这些均与显示无关。75秒无返回仍未定位到某条指令；公共启动、驱动执行/返回、异常或复位出口都待隔离，三类嫌疑不构成互斥穷尽分类。

**方法论缺口**：R-006自算过15%单笔挂死率下"5笔全干净"先验仅44%，而"0读5笔干净 vs 2读首笔挂"由5+1笔构成；在挂死率未知时该对照不构成证据。unclocked access主判断（17:45）与23个step的证据降级都建立在该对照上，现保留为历史观测，不再作为当前判断依据。

旧delay20宏未进入编译参数，历史时序不能作为寄存器值；GOP_QUERY/detail16在CoreStartImage返回后匹配marker。像素函数先Sync/CPU Read再Write，像素超时不能认定store失败。旧硬件因果解释已由D-146/D-149/D-152取代，历史原始记录保留。

## 在途代码处置（本轮）

三份在途改动已按审查结论处置，不再是游离状态：

| 项 | 处置 |
| --- | --- |
| 驱动内复位隔离（`--value-reset in-driver`） | 提交为e5f1ab5后**经构建实测撤回**（d00c416）。WSL构建在`Resources/Scripts/build_enuma_firmware.py:258`断言失败：该处三条守卫刻意禁止ResetSystemLib进入SimpleFbDxe（INF须与源逐字节一致、AutoGen.c不得含ArmPsciResetSystemLibConstructor、库清单不得含pscireset/resetsystemlib），且enuma平台dsc无任何ResetSystemLib绑定。D-145曾因同一约束撤回，D-149要求审查，审查结论为维持守卫 |
| Windows alternates 换行 | 保留（96d354a）。`write_text`在Windows把`\n`写成`\r\n`，git读到`.../objects\r`导致update-ref全失败；改为`write_bytes`，WSL下等价 |
| 构建环境 | **Windows原生不可用**：另一处`symlink_to`需创建符号链接特权，普通权限报`WinError 1920`，未修。历史构建均在WSL内完成，故此前未暴露。本轮构建一律在`wsl.exe`+Python 3.10.12下进行 |

**构建不可复现**：同参数重建FD为02f8d31d，与已资格bfb3d6a6不同。故"资格"只能绑定到已归档镜像（`out/value-transport/zero/candidate.img`，sha256 9b3c1df3…），不能靠重建复得；本轮未把重建产物用于任何实测。

## 显示初始化规格（本轮新增，只读）

设备常态就是Android（Linux），`su -c dmesg` 即可取得规格，不需要先boot一台droidian/postmarketOS。已取得：面板`xiaomi 42 02 0a video mode dual dsi cphy panel`，`mi,panel-id=0x4b383100420200`（K81+42 02 0a，与仓内`Panel_K81_42_02_0a_dualdsi_cphy_lcd_vid.xml`完全对应）；时序`hactive=1600/vactive=2560`，60/120fps动态；面板命令量级`cmds(117)`/`cmds(115)`；电源`mdss_core_gdsc: supplied by pm8150a_s4_level`，DSI PHY无独立GDSC（dummy regulator）；时钟`disp_cc-kona af00000`、DSI PLL 0/1为7nm、`sde_rsc af20000`；地址dsi_phy `ae94400/ae96400`、dsi_ctrl `ae94000/ae96000`。未取到`/sys/kernel/debug/pm_genpd`与`/sys/kernel/debug/dri/0`（debugfs未暴露）。这些是自写显示序列的**规格输入**，不是设备执行授权。固件`Drivers/`仅5个模块、无任何显示组件，点亮屏幕必须自写MDP+DSI+panel序列，这一点不变。

## 下一步与继续条件

1. **先建挂死率基线（不改任何固件）**：用已资格zero镜像（`out/value-transport/zero/candidate.img`，sha256 9b3c1df3…）重复至8笔，只记录"返回/挂死"，不解码、不校准、不进寄存器模式。零读档若与历史"读档挂死"同量级，则以显示为因的整条归因链作废，按载体/XBL方向重开；若8笔全干净，只能把上界压到约25%，届时再议笔数。
2. 逐笔按既有门禁：身份、备份、恢复路径核对后临时boot；失败即停、不原样重试；每笔后核验Android完成/root/槽位/解锁与双分区摘要。
3. 驱动内复位的判断保持本轮审查结论，不重启；若确需改守卫，必须走NEED-REVIEW另立编号，不能顺带放宽。
4. 常量重复性通过后才考虑最小寄存器读；随后分离描述符、cache Sync、CPU Read和Write，并核对实际FDT、CPU映射与SMMU。
5. FAT publisher/完整ADT/donor预链接可离线准备；继续复用上游通用实现，再适配SM8250 UFS和用户态。

## 源码与发布边界

设备仓既有提交b54bb2b已推送；本轮设备仓文档提交号以Git后续记录为准。独立固件仓HEAD已到d00c416（e5f1ab5提交后撤回、96d354a保留），设备锁`config/uefi-source.lock.json`已按destination重算并重固定，firmware工作树干净。独立固件仓Mu_Basecore原有递归脏状态保留，不使用reset/clean覆盖。

## 审查与系统里程碑

R-005/R-007像素单次均consumed；R-008保留日志/warm reset pending，未启用。本轮不批准新像素/MMIO写、内存字段/映射、verified或破坏性分区操作，撤回动作也未放宽任何守卫。512MiB owned、51MiB heap、example=true、Boot v3不变。用户确认可在场恢复；每笔新设备动作前仍核对当时条件。

目标iPadOS17.7.11/21H461、iPad7,1/j120ap、XNU10063.141.1/4KiB，UniXNU固定5fdbd5d。已有源平台内核最终链接与donor闭包规划，未emit预链接镜像；64MiB配置FAT未接publisher，SM8550 NativeUfs参数未启用。无可见GOP/白条闭环、未进XNU或iPadOS。TWRP/UART未验证。
