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

## 继续：两组完整FD已构建并抽取核对（2026-10-27）

本节取代前文“依赖未齐/未构建”的当前状态。所有依赖从本地固定来源建立独立副本，未修改原主线依赖、权限或staging；out/prepare_local_dependencies.py保存准备命令。UniXNU固定5fdbd5d08518bc2d5c196264c56a377dd80cf5ca，Mu_Basecore固定cfb93724a06ff86ff5ba971413368a7809ee42a5。嵌套依赖由每次构建dependency-bindings.json记录；压缩包逐一按firmware-build.lock.json核对。

两个build-1均在正式编译前失败：解包Mu目录没有.git，WSL Git向父目录发现Windows原生worktree gitfile并无法解析D:/路径。隔离firmware提交322f427仅给本次临时Mu目录执行git init，使补丁apply/reverse不再向上发现父仓。未修改Windows worktree的.git或原主线。失败目录及日志完整保留，使用全新build-2重跑成功。

两份3MiB FD：

| profile | 输出目录（本worktree out下） | FD SHA256 |
| --- | --- | --- |
| oem-control | oem-control-build-20261027-2 | 409edc8914a16fbafb80d497e3b48e2a87912aa38a285c3419bf24df6f593f84 |
| oem-mmu-only | oem-mmu-only-build-20261027-2 | f4ee1be1f10ec48561c1910152d9f2fe195bd9481c0f7e0f814f3c9476c39fd6 |

FD均位于各目录work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd。build-result.json complete=true，deployment_ready=false，hardware_execution=false。实际源码由source-manifest绑定；base_commit为构建时072251e，包含当时未提交、后来提交为322f427的三行Git上下文修复。不能将构建称为322f427干净提交构建。

新增audit_oem_development_fd.py从最终FD解码，每组核对32个OEM PE及DEPEX、39项APRIORI、两份K81 RAW，以及DxeCore/EnumaProbe与编译输出的字节一致性、实际stage10/SimpleFb0编译宏。拒绝UFSDxe、SimpleFb、GOP selftest混入及错误profile。旧通用audit/qualifier未放宽。审计输出oem-{control,mmu-only}-fd-audit-20261027-1。

compare_oem_development_fds.py确认原始源码和构建配置相同，实际抽取DisplayDxe只在0x1994..0x1997改变e1031f32→01008052；不是声称整个FD仅差四字节。两份Core整PE摘要因构建产物不同而不同，实际.text摘要均为c7d1d3344beed8154bacc330add107d347728c7484894ab2e11bd95d82f7b4e6。证据oem-fd-pair-comparison-20261027-1。

check_oem_stage10_code.py结合链接map与最终Core PE，核对0x3c90/94/98/9c依次调用MicroSecondDelay、ResetCold、CpuDeadLoop、CoreDispatcher，每组删除任一调用的4项负测通过。原DxeMain.obj为LTO中间文件，不能当普通机器对象反汇编；最终核对使用已链接PE。本检查只证明调用序列，不是完整控制流证明、设备复位保证或非返回OEM取证出口资格。

check_oem_fd_audit.py测试错误profile、部署声明、FD摘要、manifest摘要、stage13、FD损坏，以及外层仍有效时解码后DisplayDxe损坏拒绝。初版尝试搜索压缩FD内原始PE而失败，negative-1保留为测试脚本失败证据；修正版在解码边界注入，不伪称重新压缩后的物理FD损坏。最终结果使用negative-2。两次审计之间原产物保持不变。

复现工具均使用--build/--output，比较工具使用--control/--mmu/--output；输出必须为本worktree out下全新目录。源码与报告可提交，生成PE/FD及公开二进制不入库。

下一阶段继续Core精确句柄/变体绑定和调用前板级出口；本次未激活追踪、未包装Boot.img、未执行OEM，R027不改。elish原生K81资源线与nabu最小MMU假设线共用一个构建框架，仍分开实验身份。没有新增设备或录像待办，不推送。
