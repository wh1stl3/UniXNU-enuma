# OEM early-v3 新候选已编出（2026-10-27）

已完成配置表生命周期修复、完整FD构建及qualification3离线资格。固件提交7c97dc6；构建为以3adfb77为基线的工作树快照，精确输入由source-manifest绑定，不称干净提交构建。报告见reports/enuma-oem-early-candidate.json，细节见operations/2026-10-27-oem-early-v3.md。

启动镜像：out/oem-early-20261027/qualification3/image.img；SHA256 `3d263b531074c483fb96c60954ac52d139c7342b8e7bf561d31ea64f25af1628`。FD SHA256 `361c67d72b5f34ed6b4e2d7364b8fc55ab155404e5d752d4b6344160d828a5bd`。修复在旧配置表释放及通知前同步私有SystemTable指针/数量/CRC；新窗口观察call1和首次Kernel协议查询，S05仍仅代表真实CoreStartImage返回。最多五个8秒窗口，范围不扩大。

32项Python测试、真实Core ASan/UBSan回归与两处同步删除负测通过；实际PE新增23处指令删除和一次GUID变异均被拒绝，原运行时检查及Boot v3封装回读通过。软件资格不证明实机根因已解决，也不代表GOP/BDS/XNU/桌面验收。

本轮未连接、查询或启动设备；最后独立核验状态为progress-v2人工恢复后的Android完成。旧progress-v2仍consumed，不重试；R027及旧OEM冻结，原始媒体只在本地。下一步如进入实测，重新核对当前身份/备份/录像/人工恢复及新候选单次门禁。本轮无人工待办。共享主线未改，未合并main；本地设备仓提交4ca8be4、固件7c97dc6；两仓向oem-progress-20261027推送均因github.com:443连接失败，未确认发布成功。暂不部署，待网络恢复后补推并重新核对资格。

以下为此前状态与其他依赖记录，新OEM当前状态以上文为准。

# OEM progress-v2 实测结果（2026-10-27）

一次临时启动已消费，75秒观察内未见合格fastboot返回，已停止追加启动。用户人工恢复Android后，独立核验enuma、boot_completed=1、root、A槽、解锁及boot_a/vendor_boot_a摘要均通过。当前设备恢复完成；不能原样重试本镜像。

候选SHA256：adbb2c41216bc0c934af4046fe8c0127ce40a6c22c12bfc3f2c7880eee80679f。源码设备仓61eacd1、固件3adfb77；首次连接失败的前检未启动，重新连接后仅一次实际boot。单次ledger保留consumed，R027及旧OEM候选冻结。

两张本地照片独立判读：E01/C0/Q0与S02/C0/Q1，均为返回RVA 0x3abc、session 0x1c2e8da897800e00；S02状态0（EFI_SUCCESS）。精确原厂PE在0x3ab8执行BLR x8，前序从表偏移0x40取函数，对应AllocatePool。0x3a8c前序不是调用，与照片B字形也不符。无符号，不能断言上层调用函数名称或分配用途。

主判断：首个AllocatePool已经成功返回，优先缩小S02取证清理至后续OEM执行之间的区间。S02可见发生在等待/恢复完成之前，因此清理/复位失败仍是第一组待排除项；其次是后续服务或未包装协议/MMIO执行，另有后段显示出口因路由变化被拒绝的可能。两张静态照片不能证明E03/S04/S05从未发生，不能判定SID死锁或完整驱动返回，更未验证GOP/BDS/XNU。此排序是下一步诊断优先级，不是故障概率结论。

下一软件方案：以独立有界探针观察后续选定服务调用入口/返回，并区分取证清理与OEM继续执行；不先套用MMU补丁。新镜像须重新构建/失败路径/机器码/单次绑定审核，不沿用本次ledger或在场状态。原始媒体仅本地，文字判读待用户核对。

证据：reports/enuma-oem-progress-trial-20261027.json；out/oem-progress-20261027/media-review/（转录、解码、精确PE RVA映射）；out/device-tests/oem-b78f01e4-35ff-4113-890d-251a1d51d106/（transport、超时快照、恢复核验）。媒体位于D:/Code/PortingiOS/enuma/Media-enuma/OEM-progress-v2-20261027-b78f01e4。只收到stage1.jpg和stage2.jpg，未收到连续录像。

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

2026-10-27代码归因更新：用户已确认E01/S02判读。宿主ASan/UBSan复现私有SystemTable配置表指针/数量陈旧缺陷；这是当前最强代码缺陷证据，尚未证实为本次根因。已核对首分配后的构造链与实际Core返回/清理指令，下一验证先隔离追踪器并覆盖call1/2及Kernel协议，暂不跳到SID/MMU补丁。详见operations/2026-10-27-oem-post-s02-analysis.md。新候选未生成，本轮无追加实机；7d74ce9文字取证已推送oem-progress-20261027。
