# 2026-10-27 编译输入导入与 CI 推进

用户已允许推送。仅推送独立 CI 分支所需构建代码，不变更共享主线；R027/OEM候选继续冻结，暂不上机。

新增 scripts/import_enuma_driver_inputs.py：检查同次成功构建报告、manifest、最终编译记录、内核及文件摘要；拒绝路径越界、符号链接、未列出文件和夸大资格。生成仅数据的可重定位命令模板，不执行编译、不声明私有ABI通过。SDK仍须由匹配macOS环境提供。

28项合成宿主测试通过（14导出、14导入），证据 out/kernel-userland-20261027-5/input-tests-final.log。真实XNU输入包尚未取得；下一步独立CI分支 preflight -> platform，按同次构建身份下载验收。macos-15固定Xcode16.4/iPhoneOS18.5，版本不符即失败。
首次平台运行40475779089在成功链接后导出失败：编译记录含不存在的EXPORT_HDRS/libsa搜索路径。修正为仅对源码范围内缺席的搜索目录记录absent_include_paths，不创建假头；强制include缺失仍拒绝。30项合成测试通过，待重新构建。

下载首次真实编译记录后发现-fsanitize-ignorelist也是必要文件输入，新增采集及路径重定位、缺失拒绝测试，合计32项通过。取消运行中的40477102284，改用同时含搜索目录缺席与sanitizer输入修复的新提交构建；取消不记构建失败或通过。

运行40477385983构建及导出成功，2259文件，内核59294b35a21566151f48b9fb7527769ed4e0a89497f2be5bd64af4c4fc3f1ee9；下载后验收拒绝：upload-artifact默认省略tree/.cache。仅对out/ci/macos/evidence启用include-hidden-files，保留实际源相对路径，不放宽摘要验收。该运行不能称可用输入包。

## 最终结果

平台40478893674成功，源码cdfb7ae；下载包本地导入通过：2259文件、2份真实编译记录、同次内核和manifest摘要绑定。内核be17abfc29241d95e40d2b7e568e84d84ab0922a03e0cf734d1757cbbec51ba7；manifest 0e590eb6835999a681f6ff98847cc10fb4b5ea67c187fa019a2b420ae1728929。报告reports/enuma-driver-input-ci.json；原始及导入证据位于本CI worktree out/ci-runs/40478893674。32项宿主测试通过。

IOPMGR.h、IOService.h及生成meta_features已取得；同名IOBlockStorageDevice.h在IOKitUser，不是NativeUfs/NativeRamBlock所需IOKit/storage接口。下一步为匹配storage接口/私有ABI、真实IOKit provider及初始化链接。没有执行新驱动编译命令、挂载Data、启动用户态或桌面。R027冻结，OEM候选17d0169e6bd1不变，未上机。
