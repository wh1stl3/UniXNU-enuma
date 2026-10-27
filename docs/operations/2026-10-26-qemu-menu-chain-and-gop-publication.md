# D-296：GOP发布生命周期、BDS借用接口与实际UniXNU菜单软件链

2026-10-26，Asia/Shanghai。用户要求继续进入菜单的离线工作，补充“可检查实机结果时尽可能一次性多推进”。本轮将可区分的检查合并到同一QEMU候选，未将此原则解释为R-022单次放行/拍摄就绪或取消暂不上机。没有enuma/nuwa设备命令、摄像头、提交推送、权限变更、重置清理或第二写入者。

## 实际代码增量

1. `firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedGopLib/InheritedGopPublish.{h,c}`：以既有`EnumaGopCreate`为唯一准入，GOP及BDS使用的DisplayDevicePath在同一个新handle上成对发布。路径字节与固定`Configuration/BootDevices.h`逐字节比对通过；发布不连接控制器、不切模式、不写像素、不创建全局ConsoleOutHandle别名。requirements22仍拒绝，不清位。原后端仍要求合格的identity-mapped UNCACHED RGBX及source alpha disabled，不能把已测WT局部事务升级为这一契约。
2. 生命周期明确：三处分配失败和安装错误清理；重复owner拒绝；非错误warning保留owner交给调用者；撤销失败保留GOP/path/handle及调用方frame/context，成功才释放。调用方须先断开消费者，失败不能释放背后的帧内存。INF增加实际发布源及协议依赖，没有把诊断provider改成自动发布GOP。
3. `firmware/Silicon/Silicium/SiliciumPkg/Library/BootManagerLib/ConsoleGop.h`及真实`BootManager.c::PostGopSetup`：从ConsoleOutHandle查询，必要时LocateProtocol回退，只借用完整已有GOP，不再把同一指针额外InstallProtocolInterface到全局控制台handle。输出先清空，空协议/不完整mode/callback/警告/错误不会遗留旧指针；无需创建第二个所有者。真实BootManager.c已用固定包头编译AArch64对象，但未在QEMU执行整个enuma PlatformBootManager回调。
4. `firmware/diagnostics/EnumaMenuConsole.h`新增连接GraphicsConsole前的独立预检：固定Mu实现要求80×25个8×19字形，即至少640×475像素；检查GOP mode、Info大小和回调，不调用SetMode/Blt、不代表物理GOP准入。600像素宽和474像素高拒绝，640×475接受；文本回调保护及D-295日志接口保留。

## 运行的链及结果

最终`out/menu-chain-dev-20261026/run8/result.json` passed=true，21项命令；另`journal-regression/result.json` 17项命令通过。两个输出目录均是本轮新建，未刷新reports/或R-022。

QEMU EFI由本轮实际`InheritedGop`、新发布源、固定Mu FrameBufferBlt源码及固定UniXNU的Ui/Menu/Font/Logo源码重新编译链接；支持库及constructor/entry对象从已有构建缓存只读复用，每件SHA256记录。不是完整设备FD构建，也不使用设备适配器的脏树/源码锁绕过开关。单独EFI、64MiB临时FAT盘和AAVMF变量盘只在本轮out/，不会写设备分区或旧staging。

UniXNU固定提交`5fdbd5d08518bc2d5c196264c56a377dd80cf5ca`与device sources.lock一致；Ui/Menu/Font/Logo/Internal/LogoShape逐字节对比该提交。QEMU 6.2.0；AAVMF CODE/VARS模板及支持库哈希在result.json。没有改写上游源码。

实际顺序：分配RAM帧缓冲→requirements22拒绝对照→纯RAM合格fixture发布GOP+路径→真实UEFI协议查询→ConnectController绑定**AAVMF真实GraphicsConsole**→新归因日志经真实OutputString→固定UniXNUUiInit/MenuRun→超时默认项→脚本输入选择→确认取消/确认→文本回退→检查前后及逐行padding哨兵→断开消费者/撤销GOP/释放内存。横竖各完成一次；不执行任何BootEntry或载荷。

| 独立检查 | 本轮实际结果 | 不能升级的结论 |
|---|---|---|
| requirements22门 | 主机和QEMU均拒绝，没有改位绕行；仅合成RAM fixture明确为0 | 不是enuma同次准入成功 |
| 发布/撤销 | 同handle双协议，完整路径身份；分配/安装/撤销失败及warning所有权主机回归通过 | 不是物理显示provider已启用 |
| BDS GOP借用 | 空/失败/警告/null/malformed回退及输出清空通过；真实BDS源AArch64编译通过；QEMU执行实际helper | 没有运行enuma的BeforeConsole/AfterConsole全部逻辑 |
| GraphicsConsole | 真实AAVMF驱动经ConnectController在新GOP handle上产生SimpleTextOut，预检通过 | 不是设备BDS已连接控制台 |
| 归因日志 | 合成的两个v1事件经真实formatter/OutputString成功；不调用DEBUG | 不是实际DXE日志或全局DEBUG接通 |
| 菜单图形 | 实际Ui/Menu源码在800×600横屏及768×1024竖屏运行、截图已目视检查 | 不是enuma面板、全屏stride或alpha验证 |
| 默认/输入 | 无输入fallback 1秒选择默认0；脚本Down+Enter选择1 | 不是音量/电源键硬件已用；timer运行在VM |
| 确认与文本 | Esc取消、Enter确认以及真实GraphicsConsole文本回退的数字键选择均完成 | 不是系统启动或系统返回验收 |
| 哨兵/清理 | 前后32字节、每行32字节padding保持；断开/撤销/释放完成，QEMU正常退出 | 不是Android恢复/设备超时规则已验 |

QEMU fixture只替换输入设备和日志接收端：合成SimpleTextIn+设备路径、真实UEFI event/timer服务；测试UniXNULog转到AAVMF原串口ConOut，菜单使用独立RAM GOP。配置是两条手工构造的测试条目，未运行ConfigLoad、驱动注入、UniXNURun/Main或内核启动。图上明确标QEMU RAM ONLY，不能作为实机照片。无全局系统表更改：仅应用内gST指针暂时指向本地副本，之后还原；没有写BDS变量/启动项。

## 帧证据与失败过程

- 最终VM内CRC：800×600为`E598E719`，768×1024为`985CBF3E`。通过独立FAT盘导出后逐字节CRC及行padding复核，使用标准库生成PNG；已检查菜单文字、条目、高亮和倒计时。原始bgra、PNG、serial、EFI/map及FAT盘均在run8/。这是实际渲染读回，不是手工绘制的菜单示意图。
- run1编译拒绝：主机variadic测试误用EDK的MS VA_START，而宿主回调为System V；改用宿主stdarg；发布源EndDevicePath长度改为sizeof明确类型。
- run2：横屏完整链通过，600×800竖屏ConnectController同步异常，55秒VM期限停止。固定Mu GraphicsConsole源码存在MaxColumns>=80/MaxRows>=25断言；600/8=75不满足，是首要解释，不把PC地址直接当根因定位完成。新增独立尺寸拒绝检查并改用768×1024，随后两布局完整运行，支持该判断；未移除断言、清准入位或扩大设备权限。
- run3两布局VM执行PASS，但主机缺PIL，导出后处理失败，整轮result保持false；改用标准库PNG输出。
- run4两布局VM PASS，但目录式QEMU vvfat导出出现边界簇零字节/CRC不符，未接受图像或把整轮标通过。改用独立真实FAT文件并显式Flush，run5完整通过。
- 后续加入BDS源码/借用helper时，run6因不支持的warning选项、run7因保存staging的Common/Mu旧绝对symlink导致缺头而编译失败。只解析旧响应文件的include引用，按迁移关系用`firmware/Common/Mu`真实固定新路径，不执行保存的命令、不修复旧symlink。run8加入这些检查后21项全通过。旧结果/文件未覆盖。

主机发布/借用测试均ASan/UBSan；新最小尺寸测试没有调用实际连接/绘制函数。D-295日志、三分支Probe对象、旧journal10000事件及8秒事务回归全部在独立journal-regression/通过。

重现命令（必须选不存在的输出目录）：

```powershell
wsl --exec python3 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_unixnu_menu_qemu.py --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/menu-chain-next/run1
wsl --exec python3 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/test_journal_console.py --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/menu-chain-next/journal-regression
```

## 实机候选边界与下一步

本轮降低了菜单软件链能否工作的不确定性；没有闭合enuma的blend/address/topology（22=2|4|16）、CPU/SMMU地址关系或正式GOP后端要求的uncached/source-alpha-disabled条件。局部WT写字和恢复不能自动覆盖这些条件，不能直接将R-022改成“不早停菜单”。诊断provider仍不发布GOP，BDS前停止规则保持。正式接入还需合格的same-boot Frame/Validate实现及新完整源锁、metadata、FD/PE/宏/载荷资格；当前禁止自动提交推送，旧锁不刷新。

用户“尽可能一次多推进”按此落实：未来候选可按依赖顺序记录provider准入/发布、GOP查询、控制台连接、归因日志、菜单到达、输入和返回等**独立结果**；前置失败的后续项标未执行。不得用五类首结果时间码声称取得所有子项，不在一个试验中夹带未批准的全屏清屏/SetMode、路由/cache/映射变更或已消耗镜像重跑。当前仅QEMU完成该组合，未安排设备启动。

R-022冻结镜像`f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b`及归档/报告/审批保留；pending、S-050未执行，原S-001..049/R-020/R-021 consumed不复用。R-022仍需精确单次放行及当前拍摄就绪、发布门和新鲜身份/备份/恢复/时钟。晚间可用不自动启动，没有当前恢复按键待办；没有新硬件硬停。原始实机影音仅本地、不录音/不上传；nuwa不动，内存/verified/破坏性分区门禁保持。

收尾`out/menu-chain-dev-20261026/preservation-final.json`确认467份冻结/报告/配置摘要不变、33份原迁移脏文件不变、WORKLOG/DECISIONS原字节前缀保留，run8及journal-regression全部输入绑定与最终源一致。Mu_Basecore与Common/Mu提交分别cfb93724/b8d46c71，与固定依赖一致。最终输出EFI/map/serial/原始帧/PNG摘要另存于该报告；没有遗留测试/设备进程。旧锁精确漂移仍是Probe.c、Probe.inf、preflight.py、InheritedGopLib.inf四项，新增及共享BootManager改动未冒充旧资格。
