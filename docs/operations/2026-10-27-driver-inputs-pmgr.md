# XNU编译输入留存与PMGR实际重定位契约

2026-10-27，继f0ab484继续依赖顺序。依据[官网驱动集成](https://unixnu.com/porting/drivers)的匹配生成头/编译记录、私有ABI和初始化要求。仅隔离树修改、本地验证与提交；不上机、不推送、不启动远端CI。

## 确认的输入缺口与代码修复

现有平台内核来自macOS run 39927966148：Xcode16.4、iPhoneOS SDK18.5、XNU10063.141.1（d8b80295118ef25ac3a784134bcf95cd8e88109f）。result.json保留了IOPlatformExpert.cpo.json和prng_random.o.json的摘要，却未保存两份文件或对应生成头。本地设备out和旧公共工具树中未发现可直接复用的一套输入；不会用猜测的类定义或其他候选的记录代替。

新增`scripts/ci/driver_inputs.py`，并接入`platform_archives.py`的真实平台链接完成路径：

- 保留原始structured compile records、编译源文件、显式include目录中的源/生成头，生成逐文件摘要manifest。
- 最终平台重编可能改变flags，因此保存最终记录摘要，旧archive阶段摘要独立保留；manifest绑定同次内核摘要并复查一致。
- SDK/toolchain仍是外部输入；不复制SDK内容、不执行导出的命令。此包不声称无SDK即可编译。
- 拒绝越界路径、逃逸文件/目录链接、未分类外部include、缺失文件、response/module间接输入和覆盖旧输出。不能完整表达的依赖明确失败，不静默丢弃。
- 输出位于原有CI evidence/driver-inputs，现有artifact规则会随下一次实际构建保存；本轮未运行或发布该流程，因此目前没有真实新增生成头包。

14项宿主测试通过，包含正常捕获、SDK排除、记录变更、外部路径、符号链接、缺失强制头、间接输入、路径归一化和覆盖拒绝。夹具不是XNU真实构建证明。日志：out/kernel-userland-20261027-4/driver-input-tests-final.log。

## 当前enuma内核的PMGR静态契约

`check_enuma_pmgr_contract.py`复用umi固定3eb72578597d2ca16471b172d45eddc096a34a04的审计脚本，验证其Git字节及固定NativePrelink解析器后，在新out生成适配脚本。保留原脚本所有指令、导入和donor段摘要检查；以当前PMGR text段和参考constructor位置求地址差，原donor检查部分不改。

真实候选e879b2f0…的slide为-0xe00000；参考契约对应-0x1000000，地址差为+0x200000。实际AMFI/ApplePMGR代码摘要、服务匹配导入、nub+0x88 provider间接调用及320/321槽吻合。原AppleT8011PMGR读取常量/写立即返回只是该donor的静态行为，不代表Snapdragon电源能力，也没有安装替代nub或绕过安全流程。

最终pmgr4通过；读取/写入指令篡改分别由代码摘要检查拒绝，导入指针篡改由PMGR imports检查拒绝。负测还检查确切拒绝原因，没有把Python异常当通过。

pmgr1曾错误假设参考slide为-32MiB，地址范围检查拒绝；改成实际段锚定后pmgr2正测通过，但负测报告路径与输入manifest同名造成测试器误判。pmgr3修复命名；pmgr4增加确切拒绝原因检查。全部旧目录保留，真实候选/原始镜像未修改。

## 下一依赖和不可混淆的结论

static PMGR contract通过不等于私有ABI已资格：尚缺匹配编译对象的布局/虚表检查及真实运行期元数据。固定storage绑定器明确要求live_native_4k、190槽及抽象析构陷阱证据；本轮没有伪造这些字段或放宽条件。

下一步需要在匹配macOS/Xcode环境实际完成平台构建并取得新增输入包，再接storage/PMGR编译和运行期ABI验证，随后接IOKit provider、初始化调用者及XNU归档。当前Windows/WSL仍可做源码和宿主工作，但不能把导出工具单测称为已经取得生成头或服务已编译。

本轮未新增内核/FAT、未注册服务、未挂载Data或进入用户态。前轮根读/RAM后端、APFS seed及Data载荷保留；OEM候选和R027保持等待/冻结。汇总：reports/enuma-driver-inputs-pmgr.json。
