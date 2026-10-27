# D-311 / R025：真实菜单引擎的有界 GOP 窗口候选

用户要求推进到实机验证。新候选在已有 Native6/EL1/整帧 stage1 identity-WT 前置下，使用 (64,96) 起的 800×600 像素窗口，运行固定 UniXNU 的真实 Ui/Menu，scale=2、两个 action 类型项目、8秒倒计时与高亮轮换，然后恢复并读回原窗口。它不是预先生成的菜单位图；也不是整个 UniXNURun、配置发现、BDS 启动链、实体按键或 XNU 验收。

## 实现边界

- `MenuWindow.h` 复用既有 Frame 合法性判定，requirements22 原样保留；没有修改生产 GOP 的拒绝条件。独立实验接口保存480000字，再次完成原有 Native6 相同性检查后才允许绘制。
- `EnumaBoundedMenu.c` 使用真实 FrameBufferBltLib 渲染 RAM surface，提供临时 PixelBltOnly GOP。800×600 模式不向菜单暴露物理帧缓冲地址；仅允许规定窗口中的转换/写入/读回。全局协议仅在本次函数期间发布，没有DevicePath，不连接GraphicsConsole；原gST恢复后撤销协议。撤销失败保留所有被引用存储。
- UI/Menu 复用当前固定 UniXNU 5fdbd5d。本候选没有调用 UniXNURun 或 BootEntry；菜单选项只供绘制/倒计时，返回默认索引后直接恢复窗口，由既有 Core 终止机制返回，不执行项目。ConOut/ConIn 在局部系统表中为空；不声称实体按键通过。
- 新 ARM 回调只在原 Display Reserved 范围内访问该窗口。每个 present 写入完整不透明 reserved mask，执行 DSB 并逐字读回。首错锁停后续 present；无论部分写入在哪一字失败，仍尝试完整窗口恢复和读回。无MMIO、缓存属性、页表、分区或verified写入。

## 新范围与旧资格的关系

窗口480000像素，旧R024为51200像素；不是旧预算的复跑。最大present写5760000字，恢复480000字，总写6240000字；最大物理读6720000字，present调用8192，DSB8194。MDP仍最多660读/4次100ms等待，整帧translation最多18432次。8秒是实际菜单倒计时，不是对整段运行时间的保证；初始化、绘制、恢复另有耗时。恢复结果4或75秒无可控返回时停止追加并优先人工恢复。可用已验证的人工按键返回路径，不以必须新增自动复位功能为前提。

新scope由scripts/menu_window_scope.py唯一描述，R025/S053的一次性claim独立于全部旧授权；不能使用R022/R023/R024旧镜像或claim。run_menu_window_trial.py默认为离线，--execute还需要本次精确镜像批准、执行UUID、当前录像就绪、源码/文档绑定和即时身份/备份/恢复门。复用原guarded runner，仅选择此前已绑定enuma，不查询其他设备。保留主机boot-clock供记录，不套用旧日志页面的code5时序窗来宣称恢复事务完成。

## 离线结果与构建

host2：ASan/UBSan下46组检查通过，含24种通道排列、保存/验证失败、部分写入/读回失败、恢复失败、边界/预算/DSB故障。qemu1因测试fixture遗漏标准GUID定义链接失败，保留；qemu2真实运行通过；qemu3改为PixelBltOnly与更短菜单标签后通过19命令。实际菜单timeout8000ms、无输入，返回默认索引0；完整模拟物理内存恢复，frame CRC BF9C5462。最终QEMU统计读2270360、写1790360、barriers52，均小于新硬上限。底部上游长提示在scale2窗口内有裁剪，不将其写成完整可读验收。

完整build1因旧PixelArmProbe在新路径未使用而-Werror失败，未生成合格FD。只修复互斥编译include，旧函数实现不改；用实际build1响应参数对新provider独立ARM编译通过。build2为独立新目录，最终资格以其build-result.json及qualification.json为准。全部输出在out/menu-window-20261026，不覆盖旧资格或镜像。

当前尚未发图、尚无实机菜单结果。编译/机器码/全FD/完整FAT/Boot v3资格、执行review和本地准备闭合后，才进入本次录像与单次实测。拍摄需覆盖整个平板屏幕，重点观察左上内缩窗口：UniXNU、两个项目、高亮变化与倒计时。验收仍按助手先独立读媒体落盘→公布→用户确认/纠正。若黑屏或窗口无内容，记录实际观测，不能当作进入菜单。

R025准备补充：23:47绑定设备未以授权ADB状态在线，未发图；用户确认连接并进入Android后，23:48:33独立只读预检通过enuma/Android完成/root/A槽/解锁及boot_a/vendor_boot_a与本地备份一致，current.local.json未改。证据out/menu-window-20261026/read-only-preflight2.json。build2/qualification1已通过；最终复核将退出禁止写入提前至卸载协议前，qemu4通过，新build3构建中，最终镜像及资格不能沿用build2。尚未claim/boot；当前录像确认仍未取得。

D311最终资格：build3、qualification2通过；镜像 17a18ace93a002ac394ef4727148e893d7defe420496b4d3e8df7dde115be0cd，FD 275ce57a02b7c33393eeb5d63a9c9817ec527951a3dd4f2982e311a997caf46e。最终qemu4、compiled-code-review3通过；临时GOP在卸载前先禁止写入。资格1与旧code-review结果保留。物理回调584字节相同，Core.text/.data相同；新的菜单时序不套旧日志code5窗。23:48:33独立只读设备核验通过，尚未claim/boot，当前R025单次与录像确认pending。旧冻结绑定复核通过，无提交推送。原EnumaInheritedVideoAudit顶部NO GOP注释仅适用于默认/旧profile；ENUMA_BOUNDED_MENU=1通过新helper临时发布并撤销GOP，当前实现和范围以本记录为准。

