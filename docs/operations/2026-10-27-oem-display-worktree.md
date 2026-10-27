# 原厂显示实验隔离工作区

用户批准按一个新增worktree、两个profile推进。桌面create_worktree工具因聊天根目录不是Git仓库返回Not a git repository；使用原生git worktree add --detach建立D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display，基点97ef242。这里是本任务后续写入位置。D:/Code/PortingiOS/enuma/UniXNU-enuma保留给原主线/另一对话，只读引用其已固定来源。未新建第二worktree。

firmware在本worktree内从原固件本地对象初始化为11c6cf1，是独立检出；没有修改原工作区固件。没有递归初始化或更新嵌套构建依赖。新worktree是Git原生创建，未附加为桌面managed artifact；后续工具须显式指定本工作目录。当前detached提交可由原仓git worktree list追踪，勿清理。

## 已落地

scripts/stage_oem_display_profiles.py要求显式--prepare-pair，产生oem-control、oem-mmu-only两个vendor树。源为原工作区out/firmware-vendor，只读快照复制；对源前后摘要复核，输出全新目录且不能与来源重叠。遇到来源变化不出通过记录。两个树都是普通副本，不建软链接/硬链接，不共用可写staging。

每份102文件。仅Binaries/enuma/DisplayDxe/DisplayDxe.efi不同，分别绑定原始6c6351c3...和补丁ed37a4e...摘要；其余模块、INF/include和K81 RAW逐文件相同。profiles.json包含完整source_files、变体摘要、patch和panel契约；enabled=false、firmware_packaged=false、hardware_executed=false。verify重新读取实际文件，按原始PE重算最小补丁，拒绝额外或遗漏文件、非预期改动以及错误资格字段。

实物目录：本worktree out/oem-profile-pair-20261027-c999。检查脚本check_oem_display_profiles.py使用独立临时副本验证控制PE破坏、实验非补丁位破坏、面板改动、额外模块、错误enabled、变体身份错配、已存在输出及跨out输出，结束再复核原pair。最终证据out/oem-profile-check2-20261027-c999/result.json。早期check目录是开发检查，不取代最终源码绑定。

## 尚未完成的接线

当前两profile是已验证暂存契约，尚未连接构建器。firmware/Resources/Scripts/build_enuma_firmware.py目前将ENUMA_VENDOR固定到设备根out/firmware-vendor；不能通过环境变量假装切换已生效。后续须在独立固件检出增加默认关闭的profile选择、验证manifest、使用指定的只读vendor快照，再核对构建命令/实际FV解包身份。设备锁及脚本摘要更新必须在固件提交后进行，不能绕过clean-checkout校验或调用restore_mu_baseline修改共享主线。

之后才接同句柄CoreStartImage/SystemTable及持久追踪上下文、MMU-only变体身份、板级出口/终止恢复。未完成这些便不产生可执行资格。当前没有固件构建、OEM运行、GOP/ConOut成功声明或设备操作。R027镜像、原vendor均不修改，不推送。
