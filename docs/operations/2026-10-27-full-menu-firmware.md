# D-316：完整UniXNU应用固件候选（离线）

用户要求“继续推进直至编出固件”。本次只编译和离线验证；不发图、不复用R025授权、不提交推送。新实验编号R026仅用于区别资格范围，尚未批准或建立实机执行器。

## 实际实现

full-menu profile保持原stage13、SimpleFb GUID返回点、660次MDP读/4次100ms及800×600内缩(64,96)窗口读写预算。新增ENUMA_FULL_MENU=1与ENUMA_BOUNDED_MENU=1，从FV2读取固定UniXNU应用GUID 9b665204-a133-47a2-9396-9e2b370a4e25 的PE32，拒绝认证失败/无内容/超过8MiB。所有来源准备在保存/显示事务之前完成。

EnumaFullMenu.h把固定只读配置作为独立内存卷安装，不访问或修改分区；仅支持实际配置文件路径，所有写/创建/SetInfo拒绝，最多8个文件句柄。子应用的DeviceHandle指定该卷，因此真实UniXNUConfigLoad优先从它读到8秒倒计时、scale1、一个exit动作；无驱动/内核/切片/ACPI项。代码检查读取字节数、句柄归还及子应用退出状态，不把未读取配置的返回当成功。

EnumaMenuApplicationStartSource调用真实LoadImage/StartImage，并通过LoadedImage.SystemTable提供私有GOP控制台。以application host运行，避免firmware host在读配置前无条件ConnectAll；这不是enuma正常BDS已完成的声明。GOP在应用整个执行期间有效，应用卸载和配置卷撤销完成后才撤销GOP/释放存储；异常时停止后续present，尝试完整像素恢复，无法卸载的对象保持存储而非制造悬空指针。

应用完成后仍沿原Core诊断终止/复位路径；这只是本候选行为，并不重新把自动复位设为未来菜单前置条件。实体按键、正常BDS、正式生产GOP准入、XNU、QR/AdvancedLogger均不在本次验收范围。requirements22/verified/内存参数不变。

## 离线验证及构建过程

out/full-menu-20261027/qemu2：23命令通过，包括9种子应用生命周期失败场景、只读配置卷的模式/路径/元数据/部分读/EOF/seek/句柄预算/分配失败、RAM GOP回归与实际完整应用。物理访问和FV内容由VM fixture提供，加载器/只读卷/有界提供器均使用实际源码。真实应用读取配置、显示800×600 scale1菜单、8秒倒计时、执行exit后退出；模拟像素完整恢复，reads1687441/writes1207441/barriers30，均在不变预算内。菜单CRC69F91C2A；已查看完整图形和底部提示。host1的46组/24通道及故障恢复通过。policy-tests.json的23个策略/旧R025回归测试通过。

build1在预处理simplefb-diagnostic-selection.patch阶段失败：本轮DSC编辑产生CRLF，与旧LF补丁不匹配；未进入固件编译。将本轮编辑的DSC及dispatch选项补丁恢复LF后，在新目录build2从独立快照重新构建，build1保留。最终产物和离线资格以完成后报告为准，当前不提前写编译成功。

最终还需以本次新编译UniXNU PE重新跑QEMU、验证生成编译宏与FD原生PE/DEPEX、配置实字节及AOSP boot打包反解。固件构建和软件资格不等于实机授权；新候选执行前仍需机器码复核、独立单次执行绑定与当时录像/设备门禁。


## 最终结果（2026-10-27）

build2于00:58:56完成，实际编译2分11秒。完整FD 3145728字节，SHA256 9d513b79c98662977d77acdc5c4984bf131bc10f4fe2b0c89e21e688e5c56ca8。qualification1通过；Boot v3镜像103817216字节，SHA256 d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce。源码工作区快照manifest 841a74ab2753c3ffbd9fa39a4720e5bef6b1500e865ab613522635481cfd284f，不冒充干净提交构建。

使用本次实际UniXNU PE的qemu3共23命令通过，菜单CRC69F91C2A；46组/24通道事务测试和23个策略回归通过。FD审计30个OEM PE/DEPEX原字节一致，实际FULL_MENU/BOUNDED_MENU等宏及私有配置完整字节检查通过；保持原完整96MiB FAT，AOSP Boot v3反解与原始kernel/ramdisk逐字一致。新qualification全部文件、旧R022/R023/R024/R025资格绑定复核一致。CRLF文件使用明确cr-at-eol检查通过，不改Git配置。

当前目标“编出固件”已完成。未实测、未登记可执行批准；现有runner也不接受未知R026。进入实机前尚需编译后物理回调/嵌套StartImage分派复核、新R026单次执行绑定以及本镜像明确批准和当时录像/设备门禁。此处不是恢复硬停，无待人工恢复事项。

证据：reports/enuma-full-menu-development.json；out/full-menu-20261027/qualification1、build2、qemu3、host1、policy-tests.json、preservation.json。


# D-317：R026准备完成，本次录像已开始，S054待发图

R026镜像d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce，资格10d3564a3cd5d4fce35b7b597098a0de31a546d9186d5cbe74da7d9a60d77221，冻结qualification1不改。584字节物理回调与R025一致，Core.text/.data一致，子应用加载/系统表/卸载/只读拒写/首错与清理门逐条核对，删除关键指令3种变异拒绝。嵌套应用不能冒充调度驱动的ASan/UBSan检查通过；应用类型跳过Core自动连接，application host无隐式ConnectAll。60项执行器/策略/旧准备器回归通过。

01:12:03独立只读核验enuma Android完成/root/A槽/解锁及设备与本地备份摘要通过。用户明确要求机器码复核、失败路径、单次绑定与构建同轮完成，只差录像时停；以后遵守此工作方式。用户随后“我开始录像了”，绑定当前R026一次临时启动与当前拍摄，授权记录out/r026-live-20261027/authorization.json。尚未claim或发图，将再做即时门禁，不自动重试。

范围：真实FV UniXNU EFI→只读exit配置→完整UniXNURun→800×600内缩/scale1/8秒→应用退出、窗口恢复与原诊断终止。正常BDS、实体按键、生产GOP、XNU/QR未验收，requirements22保持。旧R025/S053 consumed，画面已确认且Android已恢复。

执行绑定out/full-menu-20261027/execution-review.json；preparation1仅为空目录（首次只读验证因Windows无法读取WSL链接而退出，未发图），有效准备将写preparation2。入口scripts/run_full_menu_trial.py默认离线，显式--execute --human-camera-ready和独立UUID才启动。75秒无返回停止追加并恢复，不套旧日志code5时序。媒体D:/Code/PortingiOS/enuma/Media-enuma/S-054-R026仅本地；助手先独立保存判读再给用户核对。无提交推送、分区刷写、改槽或nuwa操作。


# D-318：S054完整应用菜单已拍到，Android恢复通过，画面待用户核对

R026/S054已单次消费。2026-10-27 01:25:32发送镜像d6d3d61a65d36d0194c5af6656c2e58220c64175548e155d8742f104cadcebce，fastboot返回0/2.641秒，ADB49.797秒，Android完成66.000秒。01:28:03独立检查enuma/root/A槽/解锁、boot_a/vendor_boot_a及本地备份摘要通过。无分区刷写、追加启动、提交推送或nuwa操作。

实际落地媒体为单张照片（不是完整视频）。助手已独立查看并保存判读：UniXNU标志/标题，版本0.1.0，config路径\EFI\UniXNU\unixnu.toml，第一项Return to firmware蓝色高亮，Booting Return to firmware in 1 s，完整No input device提示，drivers 0 loaded / 0 failed、kits 0、acpi 0。无圆角遮挡，底部提示未出现上一版截断。当前等待用户核对，不预写人工验收通过；单张照片不证明8秒持续或完整倒计时过程。

结合精确已绑定镜像，此画面对应独立UniXNU应用的真实配置/菜单路径。底部drivers计数是UniXNU配置注入驱动统计，不是全部UEFI DXE驱动数量。当前仍为DXE早期显式应用加载+有界GOP/内存配置，非正常完整BDS；实体输入、生产GOP、XNU/QR未验收。返回码未知，不套旧R024 code5窗口，不以Android返回推断窗口每字恢复通过。

用户问为何比nuwa快：当前enuma省略正常BDS/全控制器连接，未启用OEM DisplayDxe/UFSDxe，使用继承显示和私有内存配置，工作量明显不同；这是对enuma当前路径的解释，不是nuwa耗时分布已核验，也不称enuma完整固件性能领先。

用户持久要求：构建、机器码复核、失败路径和单次绑定同轮完成，只差当前录像时才停，不再把离线步骤拆成多轮停点。当前单次已结束，先完成媒体人工核对，后续新软件离线继续；不得重复R026。

证据：reports/enuma-full-menu-S-054-result.json；out/r026-live-20261027/authorization.json、postcheck.json、independent-visual-read.json。原媒体D:/Code/PortingiOS/enuma/Media-enuma/S-054-R026，仅本地。冻结qualification1、execution-review和preparation2保存当时绑定，不回写旧资格。剩余工作是正常入口/持续显示与输入依赖，下一次候选仍独立资格及单次/录像门禁。
