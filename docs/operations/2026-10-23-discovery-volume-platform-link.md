# FAT发现测试卷与源内核平台链接

日期：2026-10-23。用户批准按系统预研推荐继续。范围：离线FAT产物、归档配方和macOS平台链接任务；没有设备查询、启动或分区写入。

## FAT产物

复用UniXNU5fdbd5d的scripts/unixnu/payload.py/write_volume，先校验函数文件及util、Config.c、Menu.c与固定Git blob完全一致。输入config/discovery-volume.toml仅含唯一标题“ENUMA FAT DISCOVERY 01”、关闭kit自动加载、一个reset动作，10秒timeout/fallback_timeout。没有XNU、EFI、DTB/ADT、Data或可执行文件，不依赖尚未完成的板级内核。

脚本scripts/prepare_enuma_discovery_volume.py输出out/payload-discovery/enuma-fat-discovery-01.img：64MiB FAT32、512字节扇区、ENUMAPROBE标签。SHA256为567431ade5af6d74cd963ded01d74d568babcd0995cfb5a92036e0b76fde9fb7；以[产物报告](../../reports/enuma-discovery-volume.json)为准。64MiB仅是本地文件容量，不是新的board物理内存配置或已证明的启动RAM开销。

两次官方函数输出的尾部空闲簇出现不同非零字节，即使固定输入mtime和SOURCE_DATE_EPOCH仍不同，故没有沿用“原函数自然确定性”的假设。脚本检查FAT32几何和两份FAT一致后，仅清空FAT条目标为free的簇及完整簇后padding，保留全部已分配簇和元数据；实际两次各清理一个非零空闲簇。最终两镜像逐字节相同；mdir递归只见目标配置，mcopy提取逐字节回读相同。三组测试覆盖已分配数据保留、FAT分歧与畸形/截断拒绝且不改输入。

```sh
wsl -d Ubuntu-22.04 -- /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/prepare_enuma_discovery_volume.py --unixnu /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/sources/UniXNU
```

这仍不是可启动候选：未打包boot v3、未新增固件initrd publisher、未证明实际initrd范围或SFS发现。10秒菜单倒计时遇输入会取消，不是独立复位保护或挂死看门狗，不满足单独实机安全门禁。现有三份晚间镜像不包含它。

## 固件发现契约与接入前条件

enuma现有Include/UniXNU.dsc.inc已有UniXNULib/FdtLib及Probe、UniXNU、UniXNUDxe、DarwinBoot绑定，但未发现本板BootMemoryDxe发布路径。固定sheng329b473的实现把x0 FDT从gSiliciumEntryArgHobGuid取出，读取chosen/initrd start/end，要求正长度/512对齐，然后发布只读BlockIo；原入口还调用AddMemory，不能整份移植。

后续若裁剪复用，仅发布逻辑也要补严格HOB长度/FDT可读边界、运行内存图覆盖/内存类型与所有权、禁止覆盖固件或其他保留区、BlockIo读取边界、重复发布/失败清理等审查。更不能把DT指针或字段存在直接视为可解引用物理范围。本轮没有引入该驱动、添加内存或猜测vendor/cpio前缀偏移。

先在屏幕诊断可用后采集当前候选的实际x0/FDT/chosen与UEFI map，再选运输路径。Android历史chosen仅为对照。若整段是组合initrd，须取得准确受保留的FAT范围和适当发布契约；单纯长度凑整或扫描任意物理内存不作为方案。

### 既有Android范围的本机离线核对

新增scripts/audit_enuma_initrd_transport.py，只读取2026-10-22已备份的boot_a/vendor_boot_a和15:18 UART发现保存的Android FDT；先重算两分区备份SHA与既有FDT SHA。没有ADB调用，也未把原始FDT或启动镜像提交Git。根model为Qualcomm Technologies, Inc. xiaomi enuma，compatible仍是qcom,kona-mtp/qcom,kona/qcom,mtp；不是假定有xiaomi,enuma兼容串。

| 输入 | 结果 |
| --- | --- |
| 原厂boot | v3，kernel54839312B，generic ramdisk50122422B |
| 原厂vendor_boot | v3，page4096，vendor ramdisk2230B，DTB1613832B |
| 历史Android chosen | initrd长度50124652B，等于generic+vendor声明长度之和，mod512=364 |

这份Android范围不满足固定sheng发布器的整扇区长度前置条件；不能因此宣称临时UEFI候选一定走同一组合分支或肯定发布失败。当前候选真实chosen、FAT偏移、可读/保留范围均未取得；报告明确标为unknown/false。下一步需要候选观测，不截掉2230字节、不取整向外读、不据此填板级地址。[脱敏报告](../../reports/enuma-initrd-transport.json)。

```powershell
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -X utf8 -B scripts/audit_enuma_initrd_transport.py --backup out/device-tests/20261022T201404 --fdt out/uart/20261023T151810/live-fdt.bin
```

## 真实归档和平台链接CI

新增config/kernel-archives.lock.json：固定6份配方/许可文件的Git版本及SHA；scripts/ci/platform_archives.py负责校验和顺序执行。ArmDTPlatform/ArmCpu复用sheng a599a1a8的通用scripts/build-arm-driver.py，原文件加下述精确兼容补丁只暂存到本仓out/ci/macos/UniXNU/scripts/enuma-build-arm-driver.py，ROOT指向可写构建树；不复制sheng board、参数、其他专有驱动或上游源码进Git。

执行顺序：

1. 真实通用bootstrap产生Kernel.framework头、link.filelist及IOPlatformExpert/prng_random编译记录，先审计通用内核。
2. 从feeds固定提交获取corecrypto-2023/libpthread，运行corecrypto plain、corecrypto --namespace、pthread、ArmDTPlatform、ArmCpu五步，四个最终归档必须实际存在并记录摘要。
3. 根据enuma_defconfig启用既有四服务及timer/PAN等选项，再运行真实XNU构建；不启用UFS/PMGR/显示/boot-progress，不用空服务。
4. 完整链接成功后运行官方内核审计，检查_armdt_platform_configured/_armcpu_registered/_source_pthread_status真实定义，保留platform-kernel.macho、编译日志、原始工具链/归档/内核摘要与结果。

corecrypto源为ONLYA/corecrypto-2023第三方快照，固定builder明确“未对Apple原始档案认证”；构建通过也不能称已验证密码自检/服务初始化。Arm平台对象以实际XNU的C++编译记录为ABI输入；macOS编译记录不可从旧宿主原样跨路径复制。

macos-xnu.yml增加独立platform手动模式；preflight/bootstrap原语义保持。board.example、归档opt-in、board archives/prelink/ADT字段不变：先用限定CI验证配方与真实链接，再评估把成功配置接回正式设备构建。源码与测试本地检查通过不代表macOS已通过；实际run/status/日志另记后续结果。

即使platform模式成功，输出也缺Apple donor组件预链接和完整ADT，不是iPadOS可启动内核，不打包boot。下一步为编译失败的具体依赖修复或成功后的donor预链接审计；内存字段、verified和破坏性写入门禁不变。

## 本地验证与执行边界

53项Python测试通过；六份归档配方Git blob/SHA通过；FAT双构建/文件清单/回读通过。固件82ce8a5与晚间三候选不改，R-002仍停。无设备操作，无新增人工待办。macOS运行事实见随后补充或STATUS，不用计划冒充结果。

首轮实际CI39926725474/head a801314：通用bootstrap通过，corecrypto plain/namespace和pthread三步通过，第4步ArmDTPlatform因Apple Clang不支持-Wno-unnecessary-virtual-specifier、配方-Werror而失败。原始日志/结果下载到out/ci-runs/39926725474，脱敏结构报告见reports/enuma-platform-kernel-first-failure.json。

新增patches/kernel/0001-apple-clang-driver-warning.patch仅移除该不支持开关，保留-Werror与其余warnings；lock固定补丁及完整输出SHA，隔离副本严格git apply通过，参考源码未改。不使用-Wno-unknown-warning-option整体屏蔽未知参数。修复后CI需重跑，不能以本地补丁通过代替macOS构建。新增audit_enuma_platform_kernel.py供成功产物按run/head/配方/feature/摘要及锁定NativePrelink解析器独立核验普通ARM64/入口/TCR/平台符号；未取得成功产物前不运行成功审计或造报告。

## 第二轮实际结果（取代上文待重跑状态）

[CI39927966148](https://github.com/wh1stl3/UniXNU-enuma/actions/runs/39927966148)，head250cdf9261e6c43e14f9364a393320a809e234a2，2026-10-23 09:03:35 UTC job完成，结论success。五个归档步骤、四最终归档与源平台内核实际链接通过；ArmDTPlatform/ArmCpu的-Werror与对象ARM64/iOS17审计通过。kernel为21417672B，SHAb940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d，原件/全部日志仅out/ci-runs/39927966148。

下载后独立解析：普通ARM64、MH_EXECUTE、入口0xfffffff0073f9488位于__TEXT_EXEC且有文件字节支撑，双页粒度4K/TCR0x22a51a251a、iOS17.0 deployment；23367导出符号中含_armdt_platform_configured/_armcpu_registered/_source_pthread_status。四服务、timer/PAN/DT panic区域开关匹配既有defconfig；UFS/PMGR/Adreno等保持关闭。run/head/源版本/精确recipe patch与归档清单一致。[公开复核报告](../../reports/enuma-platform-kernel-ci.json)。

```powershell
& 'C:/Program Files/WorkBuddy/resources/vendor/python/python.exe' -X utf8 -B scripts/audit_enuma_platform_kernel.py --evidence out/ci-runs/39927966148/enuma-macos-platform-39927966148 --run 39927966148 --head 250cdf9261e6c43e14f9364a393320a809e234a2
```

四归档哈希来自CI实算报告，未下载归档到本地重算，报告明确区分；本地独立核对的是下载kernel的摘要/格式/符号。内核构建日志仍有缺失搜索目录及dsymutil忽略--minimize等warning，没有声称零warning。源kernel POST字段生成不代表运行初始化/密码自检通过。首轮失败产物被成功审计器拒绝，未产出成功记录。

本里程碑解决“仅有设备功能全关的通用内核”这一缺口，但输出尚无donor预链接、完整ADT/根卷/实机执行。正式board的archives/opt-in与包装器闭环仍待后续接入，不能拿platform CI绕过example保护。下一轮离线优先donor解压/roots/AMFI/slide审计，再结合晚间UEFI证据推进loader；本轮没有生成XNU启动镜像或操作设备。
