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

最后实测镜像 `out/boot-candidate/enuma-dxe-queue1-stage12-boot-v3.img`，SHA256 `d974069340e6fc69d5e8eb898bd3cdab4eff202a226fb449cbdfdc0dfd40850e`；FD `33d8dcc5d62ab61064dbb760672d989155f3968467c42b538250eedbeb641af9`。该次构建快照对应此FD，不继承旧镜像的运行证明；当前构建见下方续测与STATUS。

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

## 官方backend续测：首项入口调用返回

2026-10-22，固件固定3376c44，使用现有诊断而不修改源码。各次执行同一工具，均先核对唯一Android enuma、解锁/root、槽位、备份及真实boot/vendor_boot摘要，再临时fastboot boot，恢复后重新核对。

| 变体 | 发出时间 | ADB恢复/秒 | Android完成/秒 |
| --- | --- | ---: | ---: |
| 官方stage12 ordinal1 delay2基线 | 22:54:44 | 16.986 | 30.151 |
| 官方stage13 ordinal1 delay2 | 22:59:07 | 15.903 | 33.378 |
| 官方stage13 ordinal1 delay7 | 23:03:12 | 22.308 | 37.808 |
| 同一stage13 delay2镜像复测 | 23:04:24 | 16.939 | 31.606 |

初次2/7差6.405秒，故复测同一份2秒镜像。7秒与复测2秒ADB差5.369秒，接近设定5秒；2秒自身波动1.036秒。计时来自主机monotonic至ADB枚举，含USB与Android延迟，不是芯片级时间测量。保留所有样本，不替换较慢/较快样本。结合代码中唯一复位门位置，数据支持实际队列ordinal1的CoreStartImage已返回；门在错误状态返回后也会执行，**未采集EFI_STATUS，不认定该驱动初始化成功或协议已安装**。没有实测GUID，也不把APRIORI顺序当运行证据。stage11的反例结论保留，整个调度仍未观测到完成。

每次均自动恢复Android，root与boot_a/vendor_boot_a摘要不变，无手工恢复、flash/erase或改槽；物理内存字段与验证标记未变。

候选与FD摘要：

- stage12基线镜像25d6947b0eeb2112baeab69d301d97984747b17082d279808e72bcd3d09525d7，FDbc3e16ffd0ab46ceff6bee689c2ba18c496e31e43be553163755fd0922c1f917。
- stage13 delay2镜像d815d4d450c69679514b6cffb4cbf3749d0e222921723a1267aba4359ec5787c，FDabc2c264b7f93d09121b198d5d582ca72b0d2697d8a6809ce577cacdc24453cb。
- stage13 delay7镜像a8cc8f442f39bf8b8ebe64a61253f4fadc42ad8d75918bdd5ee61af1cac1ec48，FD1a6b17b0e3eb6bd34ef9d5128d31ee37c80aad3931e2bb7738f402395e2ee59b。

两个stage13快照在out/entry-probe/official-queue1-stage13-delay{2,7}/，含FD、build/preflight/audit/payload报告及日志。当前reports/enuma-firmware-build.json对应7秒构建；最后设备复测使用2秒镜像，不混为同一变体。完整FD均33OEM字节不变、v3回读通过，Mu补丁已恢复。来源/board/defconfig/example保护复查通过；固件源码未改，未重复源码CI、macOS内核CI或33项代码单测。

复现命令（本地工具和备份不发布）：

```powershell
wsl -d Ubuntu-22.04 -- /mnt/d/Code/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/UniXNU-enuma/scripts/build_enuma_firmware.py --reference /mnt/d/Code/PortingiOS/common/sources/mu-nuwa-firmware --unixnu /mnt/d/Code/UniXNU-enuma/out/sources/UniXNU --stop-stage 13 --dispatch-ordinal 1 --stop-delay 7
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -B scripts/run_enuma_entry_probe.py --image out/boot-candidate/enuma-official-queue1-stage13-delay7-boot-v3.img --label dxe-driver-return
```

构建后须先audit_enuma_fd、prepare_enuma_boot_payload、package_enuma_boot完成一致性审计和独立v3回读，才可运行临时启动工具；输出不得覆盖已有候选。下一步从ordinal2及后续实际队列边界继续，必要时增加GUID/LoadImage状态诊断。没有GOP/UEFI map/XNU或触控运行证明。

## 扩大至第8项返回后

2026-10-22续测，官方backend、固件3376c44不变。第2项delay2 ADB15.938秒/Android32.704秒；第4项delay2 ADB16.944秒/Android31.829秒，先作为单点初步边界。第8项delay2 ADB20.142秒/Android33.399秒；delay7 ADB21.233秒/Android34.952秒，首轮差1.091秒不能作命中证明，因此复测完全相同2秒镜像：ADB15.917秒/Android29.285秒，7秒与复测2秒差5.316秒支持第8项CoreStartImage返回后门命中。所有样本保留，恢复时序包含USB与Android波动；未采集EFI_STATUS/GUID，不认定初始化成功或完整调度完成。

五次都自动恢复Android/root/boot与vendor_boot摘要，无flash/erase/改槽。每份固件均33OEM PE-DEPEX字节审计与v3回读通过。快照out/entry-probe/official-queue{2,4,8}-stage13-delay{2,7}/，精确镜像/FD摘要见entry-device-tests各variant。当前编译第16项；后续按真实边界推进，而非猜测第9项就是故障模块。

## 第16项与第二次推送前查询异常

第16项stage13/delay2完整FD ebdb9017106c9f76790f4ac6a45bc9fe9176609493dce29d714478637444d2f0，镜像647503568b075796af2a0944e0b4d25d195023707cec80887512048282481a59。首次完整身份查询五次均缺字段，未发boot，仅正常重启回Android并核对root/槽/boot与vendor_boot摘要。公开报告分别保留中止与启动记录。重试23:29:16发出，ADB16.953秒、Android30.316秒，全部恢复核对通过；单点尚无独立延时对照，不能推断EFI_SUCCESS/GUID。

GetVar解析现要求恰好一个完整值，拒绝错误变量、enuma后缀、重复/冲突、FAILED和非零返回；每轮完整查询的输出保存在当前私有attempt目录fastboot-identity.local.json，失败phase显式区分boot前/后。首次异常未有完整原始查询日志，不能追认其错误文字；根因仍未知。36项Python通过，包括三组解析回归，重试当场三字段首轮通过。第32项继续构建。

## 第24/32项及细分诊断接入

原3376c44：第32项23:33:05发出，ADB32.917秒/Android46.204秒；回查第24项23:37:31发出，ADB16.954秒/Android32.252秒。前者仅长复位，不认定返回门，后者仅短门单点。所有恢复核对通过。

新固件d6900d2以extensions.json独立锁新增detail header和两补丁，原25迁移文件/六patch保持。stage13可选point13任意入口返回、14加载返回、15入口前、16/17入口错误/非错误返回、18/19加载错误/非错误返回；可用完整GUID两半限定。LoadImage门对已加载项/FV项会绕过；非错误返回不证明协议闭包。真实头20组ASan/UBSan、40项Python、四core重叠patch与DSC幂等/来源/旧board表/example/WSL DarwinBoot契约通过。源CI39807061433通过并回读日志。

新版本默认point13第28项23:44:13发出，ADB31.877秒/Android45.206秒，自动恢复root/分区摘要，长复位不当作返回证明。FD15442416f8647a566e6bdc2f673d1bbabfcaf0d2bfaa11c27af3c83b2d59798c，镜像4f06b9fb5d19b142f423b54f286643edbb0e1e122b2642e35fed01975c66134f；33OEM/v3/补丁恢复通过。新版第26项构建中，先取同版较前门再细分，避免跨布局直接锁模块。具体CLI见build_enuma_firmware.py --help，GUID参数由UUID.bytes_le生成两半，不用文本顺序猜测。
