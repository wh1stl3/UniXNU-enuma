# 2026-10-27 编译输入导入与 CI 推进

用户已允许推送。仅推送独立 CI 分支所需构建代码，不变更共享主线；R027/OEM候选继续冻结，暂不上机。

新增 scripts/import_enuma_driver_inputs.py：检查同次成功构建报告、manifest、最终编译记录、内核及文件摘要；拒绝路径越界、符号链接、未列出文件和夸大资格。生成仅数据的可重定位命令模板，不执行编译、不声明私有ABI通过。SDK仍须由匹配macOS环境提供。

28项合成宿主测试通过（14导出、14导入），证据 out/kernel-userland-20261027-5/input-tests-final.log。真实XNU输入包尚未取得；下一步独立CI分支 preflight -> platform，按同次构建身份下载验收。macos-15固定Xcode16.4/iPhoneOS18.5，版本不符即失败。
## 发布与运行记录

用户授权推送后，从远端main 89b609e建立最小分支 ci/enuma-driver-inputs-20261027，提交de17286，仅6个构建/测试/说明文件；未推送OEM实验历史、未修改远端main。预检40475516645已成功，实际runner 20260907.0337.1、arm64、macOS15.7.9、Xcode16.4(16F6)、SDK18.5。平台运行40475779089正在执行，尚无编译成功结论。

CI检出目录 D:/Code/PortingiOS/enuma/worktrees/enuma-xnu-input-ci；原离线开发树仍为enuma-oem-display，2f7532a本地保存导入与授权记录。原共享UniXNU-enuma保持只读。真实运行结果后续追加，不以预检代替平台链接。

首次平台40475779089链接完成，导出遇到编译器允许缺席的EXPORT_HDRS/libsa搜索目录而失败；保留失败证据。CI修复5549be7已推送，30项宿主测试通过，只记录缺席搜索目录，不放宽强制include或外部路径。第二次平台40477102284运行中。

基于真实编译记录追加sanitizer ignorelist文件采集和路径重定位；32项测试通过。真实IOPlatformExpert参数重定位检查通过，无runner源绝对路径残留。CI e8a023d已推送；40477102284主动取消，40477385983运行中。

最终CI cdfb7ae / 40478893674成功，2259文件、2记录下载后本地导入通过。内核be17abfc29241d95e40d2b7e568e84d84ab0922a03e0cf734d1757cbbec51ba7。报告reports/enuma-driver-input-ci.json；CI分支e81f73c含最终记录。前次40477385983虽CI成功，但upload-artifact过滤.cache导致1072文件缺失，本地拒绝；cdfb7ae仅限证据目录开启隐藏文件上传，最终包验证通过。IOPMGR/IOService生成头已取得；storage头及私有ABI仍需继续，未运行新驱动/用户态。
