# 当前：OEM运行版已完成软件资格，待当前现场准备

2026-10-27。用户已授权“继续补齐 OEM 运行版后部署”。新候选是原始OEM control首调用取证版；R027/S055仍冻结未消费。只写独立worktrees/enuma-oem-display，原共享UniXNU-enuma及firmware不改，不推送。

已生成可临时启动的Boot v3：

- 镜像：out/oem-runtime-qualification-20261027-3/image.img，3153920字节。
- SHA256：17d0169e6bd1447b358d1e91c6af9a8bf6ed368c6c44fea591fa73b970b82f08。
- FD：out/oem-runtime-build-20261027-1/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd。
- FD SHA256：d08f338dc49f60eb08ecd25a14c66e0f6e8fe9e5724d19f04684ca2d1fd08345。

## 本次运行行为

Core精确匹配原厂DisplayDxe/FV/LoadedImage/重定位文本后，才绑定持久私有服务表。随机session与trial UUID对应一次首调用call0取证；320×160窗口位于(64,96)，停留8秒并恢复/读回。取证拒绝或恢复未确认时终止，不转发该原服务。事务屏蔽本CPU异步中断并直接计时，异常在格式化输出前尝试复位，返回则永久暂停。

运行版已移除stage10派发前停止；精确目标实际CoreStartImage返回触发2秒复位，正常派发完成fallback为7秒复位。没有异步看门狗，不能保证OEM卡住时自动恢复。本CPU屏蔽不证明AP/DMA排他；相机可读性、物理恢复和OEM实际返回仍未验证。

## 已通过的离线检查

完整FD核对32个OEM PE/DEPEX、39项APRIORI、两份K81 RAW以及实际Core/Probe/ArmCpuDxe产物。真实C编译参数、运行身份头和异常头绑定；Core派发/返回/取证失败/中断序列20项删除负测通过，Core和ArmCpuDxe异常终止序列核对通过。Boot v3打包、官方解包回读及源码/镜像绑定通过。

ASan/UBSan覆盖绑定失败和首调用取证失败不得转发；部署入口9项测试覆盖镜像/源码/范围/缺人工准备/重复领取拒绝、一次boot后恢复、boot失败不重试、错误Android身份不写入。机器码检查仅证明所检序列，不是完整控制流或实机保证。证据qualification-3、out/oem-runtime-binding-check-20261027-1及out/oem-deployment-review-20261027-1/runtime-tests.txt。

## 设备与继续条件

本轮12:15/12:16 +08只读核验enuma Android启动完成、A槽、解锁、root，boot_a/vendor_boot_a与本地备份摘要一致。尚未发出重启、boot或分区写入；当时状态不能替代启动前即时核验。

只差当前录像及人在场长按恢复确认。依据AGENTS设备门禁及拍摄规则，本次有实际像素输出，必须连续录像；原始影音仅本地。确认后即时重查设备和资格，单次ledger领取，唯一一次fastboot boot；75秒无可确认返回则停止追加并优先人工恢复，不自动试MMU候选。没有当前准备回复前不启动。

源码仅本地提交，构建基点b6fe1a2加哈希开发快照，后续提交不改称干净提交构建。qualification-1因构建收尾报告未落盘提前检查而失败；-2为初步资格，-3增加机器码和ArmCpuDxe审计后为当前资格，旧证据保留。共享主线与R027资格不合并、不重写。

详见[OEM运行与部署记录](operations/2026-10-27-oem-runtime-deployment.md)。生产GOP、ConOut、完整BDS、实体输入及XNU均未验收；未观察到返回不能判死锁。

2026-10-27 用户最新回复：现在不方便，保留候选等待。现场准备未满足，部署暂停；不发重启或boot，不消费单次ledger，不重新构建或更换候选。待用户恢复现场条件后即时复核资格、设备、备份及录像再执行。
