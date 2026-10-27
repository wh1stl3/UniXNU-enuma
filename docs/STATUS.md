# 当前：真实 macOS XNU 编译输入已取得并通过本地验收

2026-10-27。用户已允许推送；本轮只推送独立 ci/enuma-driver-inputs-20261027，远端main仍89b609e。原共享UniXNU-enuma不修改；R027冻结、OEM候选继续等待，暂不上机。

## 当前成果

- CI代码cdfb7ae；预检40475516645、最终平台构建40478893674成功。Xcode16.4、iPhoneOS18.5及固定源码。分支最新文档提交e81f73c。
- 下载后本地导入通过：2259个文件、2份真实编译记录、内核及manifest摘要绑定。32项合成宿主测试通过；两份实际命令重定位通过。模板仅数据，未执行新驱动编译。
- 新平台内核SHA256 be17abfc29241d95e40d2b7e568e84d84ab0922a03e0cf734d1757cbbec51ba7。未将它替换进旧预链接、payload或OEM候选。
- 首次导出失败、一次主动取消及一次上传过滤不完整包全部留存；修复缺席搜索目录记录、sanitizer输入及隐藏目录上传。最终成功以下载后验收为准。

证据在D:/Code/PortingiOS/enuma/worktrees/enuma-xnu-input-ci/out/ci-runs/40478893674，导入结果imported/result.json。摘要见reports/enuma-driver-input-ci.json及operations/2026-10-27-driver-input-import-ci.md。

## 已有离线实现保持

RootWindowRead/EnumaUfsRead桥接与ARM64 archive、真实512MiB逻辑APFS Data seed、96MiB FAT及DarwinBoot解析、EnumaRamDisk易失Data后端和生命周期负测均保留。详见operations/2026-10-27-root-data-offline.md、operations/2026-10-27-volatile-data-backend.md。它们尚未成为真实IOKit服务或接入新XNU。

旧30组件实验内核e879b2f0…及PMGR静态契约/三项篡改拒绝证据保持；静态资格不迁移到新平台内核，不替代live_native_4k。原OS/SystemOS根卷文件、Data/FAT及所有旧实验产物不变。

## 下一依赖

已经取得IOPMGR.h、IOService.h、meta_features及真实编译记录。IOBlockStorageDevice同名头位于IOKitUser，并非NativeUfs/NativeRamBlock要求的IOKit/storage接口。下一步：匹配storage接口及私有ABI、PMGR布局/元数据、真实IOKit provider/start/stop和初始化归档链接。然后继续UFS stream归属、DMA/队列排他及Root/Owner/Data策略。

无新MMIO、IOKit注册、APFS挂载、launchd/backboardd/SpringBoard运行结论。遵守官网规则及固定参考源码，不能借用其他机型地址或verified状态。

## 冻结候选与工作区

OEM out/oem-runtime-qualification-20261027-3/image.img复核SHA256仍17d0169e6bd1447b358d1e91c6af9a8bf6ed368c6c44fea591fa73b970b82f08，未boot、未消费ledger。设备当前状态未重新探测。

主开发树D:/Code/PortingiOS/enuma/worktrees/enuma-oem-display；最小CI树D:/Code/PortingiOS/enuma/worktrees/enuma-xnu-input-ci。主开发树同步构建修复并本地提交；只CI分支推送，未合并main或触碰共享工作区。