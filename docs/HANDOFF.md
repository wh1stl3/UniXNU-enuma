2026-10-27：用户明确允许progress-v2上机，并确认当前在场、连续录像及人工长按恢复准备完成。仅新镜像adbb2c41216bc0c934af4046fe8c0127ce40a6c22c12bfc3f2c7880eee80679f一次临时fastboot boot；前检由绑定runner即时执行，不flash/erase/改槽，75秒无返回停止追加。R027及旧OEM冻结。

# 最新交接：OEM progress-v2候选已就绪，等待实机条件

新镜像out/oem-progress-20261027/qualification1/image.img，SHA256 adbb2c41216bc0c934af4046fe8c0127ce40a6c22c12bfc3f2c7880eee80679f。固件3adfb77本地提交，完整FD/32项机器码删除负测/Boot v3/宿主与29项Python测试通过。软件资格不代表实机成功；本轮不部署，ledger未消费。旧OEM和R027冻结、摘要不变，旧源码资格不与新版混用。运行边界及五阶段解读见operations/2026-10-27-oem-progress-candidate.md。主线下一实机优先可靠取证→OEM返回与GOP，再独立进入引导交接；本镜像尚不测GOP/XNU。

以下内核输入及集成交接仍有效：

# 交接：从已验收真实输入继续 storage/PMGR 服务集成

2026-10-27。用户允许推送，暂不上机；R027冻结，OEM候选17d0169e6bd1继续等待。共享D:/Code/PortingiOS/enuma/UniXNU-enuma只读。

1. 主开发树D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display保留完整离线历史。最小CI树D:/Code/PortingiOS/enuma/worktrees/enuma-xnu-input-ci，分支ci/enuma-driver-inputs-20261027已推送，最新文档e81f73c；远端main未变。
2. 最终平台运行40478893674成功，代码cdfb7ae；原始包在CI树out/ci-runs/40478893674/enuma-macos-platform-40478893674，验收副本在同级imported。2259文件/2记录绑定通过，manifest和内核摘要见reports/enuma-driver-input-ci.json。不要重用上传缺失的40477385983，也不要覆盖旧失败证据。
3. 已取得真实IOPMGR/IOService及生成头/命令；下一步仍须IOKit/storage接口和同donor私有ABI。IOKitUser下同名头不能替代。随后接入现有RootRead/RamDisk的provider、start/stop、注册及归档链接，验证失败生命周期。
4. 新平台内核be17abfc…未做donor预链接或设备启动，旧e879b2f0实验内核及静态PMGR结果不自动转移。没有用户态或桌面运行证据。
5. 32项宿主测试通过，最终真实包导入通过；详细失败/修复链见operations/2026-10-27-driver-input-import-ci.md及CI分支同名文档。按官网具体规则继续；内存/verified/分区门禁不变。