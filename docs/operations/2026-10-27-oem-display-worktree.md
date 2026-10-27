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

## 继续：开发构建入口已接线

固件本地提交072251e在本worktree的独立firmware检出。审查发现已有build_enuma_development.py支持导出当前源码并生成完整摘要manifest，因此不必改旧发布锁8680ea79。8680ea79到11c6cf1有46个文件差异（含菜单、像素事务、追踪和开发构建工具）；不能仅改锁的commit字段视为旧资格延续。本轮保持config/uefi-source.lock.json及原始vendor.json不变，沿既有开发快照机制隔离变化。

开发builder新增--profile oem-control/oem-mmu-only以及必须显式提供的--oem-profile-pair。旧默认仍stage10；旧profile禁止pair，OEM禁止direct-menu。新helper enuma_oem_profile.py独立以固件vendor.json的102文件摘要核对control，并严格重建四字节MMU补丁验证另一变体，不依赖pair manifest自报合法。之后复制到本次构建out/oem-vendor，readback确认，只有导出source/Resources/Enuma/vendor.json产生带development_derivative的摘要衍生；原始锁保存为vendor.json.historical。衍生和所有源码由原source-manifest机制绑定。

OEM两个profile都强制stage10、SimpleFb=0、GOP_SELFTEST=0、菜单关闭、UFS关闭。保留DisplayDxe和CPRDxe，但停在DXE派发前，仅用于编译/打包检查，没有调用前追踪激活。preflight实际收到独占vendor目录，构建报告记录变体身份及仅UFSDxe被省略。不能沿用旧qualify_development_fd.py的SimpleFb模块预期给OEM profile出资格，后续须做对应实际FV抽取与模块检查。

调用入口（尚未完成全FD构建）：

```sh
python3 -B firmware/Resources/Scripts/build_enuma_development.py \
  --device-root . --output out/oem-control-build-new \
  --dependency-root out/development-dependencies \
  --profile oem-control --oem-profile-pair out/oem-profile-pair-20261027-c999
```

另一变体单独使用全新output及--profile oem-mmu-only。上述dependency-root是待准备位置，不能把例子当作已存在依赖。当前隔离树out/sources/UniXNU、out/firmware-build的固定archives及三项固件嵌套gitlinks尚未准备，因此未运行完整FD编译；也未回退到共享缓存进行可写构建。

scripts/check_oem_build_profiles.py直接执行helper与builder参数入口：两变体精确复制/快照锁衍生、stage10宏、缺pair/旧profile带pair/菜单混用、control损坏/MMU非补丁位损坏/面板损坏等8项检查通过；原锁复核未变。证据out/oem-build-profile-check-20261027-c999/result.json，摘要绑定三份实际源码，full_fd_built=false。没有把缺失依赖当作需要用户审批；后续继续准备隔离的固定依赖并构建、抽取核对，再接Core与板级出口。
