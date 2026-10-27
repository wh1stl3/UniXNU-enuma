# D-297：WT／不透明GOP实现，部署前保留真实准入缺口

2026-10-26，Asia/Shanghai。用户要求“打通实机阻塞、推进进度，在实际部署镜像前停”。本轮完成软件适配与独立EFI运行，未发送镜像、未进入fastboot、未调用设备工具；未自动提交推送、改权限、清理/重置或操作nuwa。R-022镜像/归档/资格保持冻结。

## 主判断与代码

原通用Mu后端要求UNCACHED、source alpha disabled；既有enuma间接实测支持的是局部NormalWT、不透明mask写入。直接用Mu Blt写reserved=0的像素，不能假设等同于前述不透明试验。本轮增加独立WT／不透明路径，原`EnumaGopCreate`的Mu路径保留；没有改映射/MAIR/页表、没有用缓存维护强行兼容WB。

- `InheritedGopAccess.h`／`OpaqueBlt.h`：新`EnumaGopCreateWtOpaque`与版本/大小/policy3的Read32/Write32/Synchronize接口；四类GOP Blt按RGB mask打包，每次像素写入都带完整ReservedMask。不透明黑色SetMode写ReservedMask，不是全0。VideoToBltBuffer按标准BGR像素返回，Reserved为0；VideoToVideo处理横纵重叠。Delta/范围/指针加法溢出和帧缓冲作为外部BltBuffer的别名拒绝。
- 同一个backend对象在读、写、同步或Validate异常时锁存首个故障。尝试后的stores仍执行末次同步，随后所有Query/Blt/SetMode均拒绝；不让忽略Blt返回值的UI继续写。GetAccessState保留callback尝试次数和首故障，计数不宣称物理屏幕完成。Blt是标准非事务操作，失败可能部分写入；**没有自动保存/恢复整屏**，不可沿用R-022恢复语义。
- `InheritedGopWtArm.h`：实际AArch64 volatile 32位访问和`dsb sy`，访问限定于调用方提供的window，无硬编码新物理地址、无新MMIO映射。window/Policy=3是机制参数，不能代替同启动WT/identity/ownership证明。
- `InheritedGopPublishWtOpaque`接入D-296相同的成对发布/撤销生命周期。新旧创建入口都继续拒绝requirements22，要求Frame.Requirements=0、有效Validate和既有范围/掩码/路由约束。此轮没有为真实Frame清除任何位，没有把诊断provider接成正式GOP。
- `InheritedScanoutLib/OpaqueBlend.h`：基于固定MiCode52a2f18寄存器事实的纯保存字分析器。支持FG/BG常量、明确不透明前景像素前提及简单反相，计算有效FG/BG系数；仅255/0标记数学上的full-source。背景像素alpha、缺少不透明前提、modulation、transparency、dim和未知位拒绝；输出未知时不改调用方结果。它不检查其他stage/dim/LM processing，不证明unpack、路由或屏幕，也不清BLEND位。

固定事实源`out/display-native-sources/sde_hw_mdss.h`及`sde_hw_lm.c`已与历史`reports/enuma-scanout-blend-sources.json`摘要重新匹配；没有导入GPL实现，旧报告不改。

## 验证结果

`out/wt-opaque-dev-20261026/run2/result.json`：10项命令通过。旧Mu后端回归、WT新路径ASan/UBSan、24通道排列、四种Blt、重叠复制、stride/前后哨兵/溢出/opaque clear、读/写/两次同步/Validate故障锁停及requirements22拒绝通过。131072组混合常量及pixel-alpha前提/未知flag拒绝通过。真实backend/publication及volatile/DSB访问头AArch64对象编译通过，反汇编核对DSB。

`out/wt-opaque-dev-20261026/menu-run2/result.json`：21项命令通过。使用本轮WT新路径、**实际ARM volatile/DSB回调**，在分配的VM RAM上发布GOP→真实AAVMF GraphicsConsole→归因ConOut→固定实际UniXNU Ui/Menu。横800×600、竖768×1024的无输入默认超时、脚本选择/取消/确认、文本回退、哨兵、断开及撤销均通过。VM RAM测试**未证明CPU实际属性为WT**，只是WT机制路径的软件验证。

| 项目 | 横屏 | 竖屏 |
|---|---|---|
| VM帧CRC | 0F9904BF | 20F229FE |
| callback读尝试 | 1 | 1 |
| callback写尝试（hex） | 1CC8F3 | 30B170 |
| 同步尝试（hex） | 7C | 9C |
| 首故障 | EFI_SUCCESS，未锁停 | EFI_SUCCESS，未锁停 |

读1来自测试末尾显式VideoToBltBuffer，不将它冒充菜单必然进行了屏幕读回。导出FAT帧CRC与VM一致；PNG的RGB字节与D-296旧Mu菜单完全相同，但原始reserved字节及CRC不同，验证没有靠换颜色掩盖alpha适配。所有原图/原始帧只在本地out。

初次menu-run1在横屏结束的测试断言失败：测试错误要求菜单绘制必然产生Read32；绘制路径可只写。没有将它记通过。随后明确执行一次VideoToBltBuffer验证读路径，再读取计数/故障状态，menu-run2两布局通过。旧失败结果保留；这不是硬件硬停或恢复事件。

可重现命令（输出目录必须新建）：

```powershell
wsl --exec python3 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_wt_opaque_gop.py --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/wt-opaque-next/host
wsl --exec python3 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_unixnu_menu_qemu.py --wt-opaque --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/wt-opaque-next/menu
```

## 部署前状态：未形成可部署的enuma菜单镜像

具体边界记录`out/wt-opaque-dev-20261026/deployment-boundary.json`，deployment_ready=false、enuma_boot_image=null。本轮只生成QEMU独立EFI/FAT测试盘，没有生成或资格一个新的enuma Boot v3菜单镜像，不能将测试EFI直接发给设备。

已解决的是**WT访问机制、不透明像素、IO故障冻结及混合系数解码的软件缺口**。以下仍须真实同启动证据；离线不能假装闭合：

1. 当前选中LM的实际operation/alpha、其他dim与processing以及source unpack。写FF只满足像素不透明的一个前提，逆alpha/调制/遮挡仍可能使输出不可见。
2. 完整Frame的CPU/display地址等价和SMMU关系。历史小区域可见与AT WT不能升级为全帧、所有源同址及最终stage2证明。
3. CTL/PP/DSC/DSI下游关联。稳定shadow结构和双DSI计数推进不是整条可见路由证明。
4. 新开发源的完整构建/源锁/metadata/PE/FD/实际宏/完整载荷资格。当前仍脏且禁止自动提交推送，未刷新旧锁、未调用会修改原staging的适配器；新的独立测试manifest不能冒充完整设备资格。

因此在实际部署前停止，保留新API和证据供下一候选使用，而不是将22强制归零。没有改变board.toml/bringup-plan的内存base/size或任何verified，没有寄存器、页表/cache属性、路由或分区写入授权扩张。若后续形成可检验实机候选，继续按用户要求尽量合并可独立判读的准入/日志/控制台/菜单/返回结果，前置失败的后项标未执行。

R-022仍为固件8680ea7／镜像f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b／FD7bee85343b6f8837c1081f5cb08db939facfc1ec084c6f498d918ded1e02f035，256×96/8秒预算不变，pending、S-050未执行。S-001..049及R-020/R-021消费事实不变；无当前恢复按键待办，不拿历史Android后验当新鲜状态。原始实机影音仍仅本地，不上传、不录音。

收尾`out/wt-opaque-dev-20261026/preservation-final.json`确认467份受保护文件不变、所有最终测试输入绑定匹配。导出横/竖帧分别480000/786432个可见像素的reserved字节全为255，非opaque像素0，RGB与旧Mu一致。32份原迁移脏文件逐字节不变；AGENTS.md检测到本轮之外的一条新增说明（未改固件/设备门禁），已保留并单独记录前后摘要，未回退。旧源码锁精确漂移5项，未刷新。没有遗留检查/设备进程，当前无enuma Boot镜像、deployment_ready=false。
