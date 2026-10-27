# 2026-10-27 编译输入导入与 CI 推进

用户已允许推送。仅推送独立 CI 分支所需构建代码，不变更共享主线；R027/OEM候选继续冻结，暂不上机。

新增 scripts/import_enuma_driver_inputs.py：检查同次成功构建报告、manifest、最终编译记录、内核及文件摘要；拒绝路径越界、符号链接、未列出文件和夸大资格。生成仅数据的可重定位命令模板，不执行编译、不声明私有ABI通过。SDK仍须由匹配macOS环境提供。

28项合成宿主测试通过（14导出、14导入），证据 out/kernel-userland-20261027-5/input-tests-final.log。真实XNU输入包尚未取得；下一步独立CI分支 preflight -> platform，按同次构建身份下载验收。macos-15固定Xcode16.4/iPhoneOS18.5，版本不符即失败。