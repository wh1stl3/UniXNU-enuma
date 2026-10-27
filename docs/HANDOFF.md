# 当前：main-entry-v6 本次拍摄/恢复就绪，单次启动准备（2026-10-27）

此前离线完成新镜像；本次用户要求上机，已完成只读即时前检，尚未启动。v5两页与现场仅两组已确认，真实InstallConfigurationTable返回EFI_SUCCESS；用户无操作自行回Android且恢复独立核验通过。v5 consumed不重试；R027和旧产物冻结，共享主线只读。

新候选scope oem-main-entry-v6，镜像out/oem-main-entry-20261027/qualification2/image.img，3153920字节；SHA256 c372c5e89a25aabe8d025469364c7d160be7c034481f5cec5e0283cc3338036d。完整FD SHA256 37126098fc7804af36cfcafe908f17454fbc9757ded55986462461f13caf4fcc，位于out/oem-main-entry-20261027/build2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd。qualification.json SHA256 7d3575843a9904d4f8b63891aa9143f785cbe934949e1fa868918775daf2e486。trial cfee120a-a6a4-4b02-bcff-21b1aa82372f，session 10505121988310854258，尚未claim/上机。Boot v3指Android镜像头格式；新诊断固件版本是v6，不是v3。

最大可操作嫌疑仍为S02返回窗口收尾/包装器退出及后续出口拒绝（诊断优先级置信中等、唯一根因低）。精确原厂后段新增定位：0x1760进入0x35c8，0x3604查询ChipInfo、返回RVA3608；查询成功后0x3618调用接口+48 GetChipFamily；其后有条件协议方法及CreateEvent/Ex，SID在更后。它们都可能在SID前阻断，未将任何一处认定实机根因。解决方向与推翻条件见[main-entry-v6分析](operations/2026-10-27-oem-main-entry-v6.md)。

v6取消注册区间两窗与所有服务返回侧绘制，不更改原厂PE、服务指针/状态或GetChipFamily方法。只绘制E01（ChipInfo查询前，实际call>=6、精确RVA3608/GUID）、E03（SID查询前，主查询真实返回已记录）及S05（真实CoreStartImage返回和状态）。selected_call=6为最小序号，实际选择依精确RVA/GUID，不假定固定序号。板级拒绝其他phase/超过三窗；ROI(64,96)320×160，每窗8秒，最多Hold24秒，较v5预算少16秒，不称实测启动提速。无页/缺页仍可能是出口问题；E01不证明原始查询执行，E03不证明SID原始服务完成。

完整FD、原厂模块/RAW/编译产物审计及Boot header v3打包/解包回读通过；42项Python（含模拟传输）、check2 ASan/UBSan与真实Core配置表删除负测、path2精确PE和AArch64 ChipInfo ABI、binding3重定位/错PE拒绝及AArch64板级通过。最终机器码32处运行路径+77处主入口/转发/同步删除及2处GUID变异均拒绝。默认离线runner及2452项来源绑定通过。binding2旧夹具的固定序号停止假设失败已保留，修正测试语义后binding3通过，未为测试伪造运行逻辑。

固件提交d393211，已向显式GitHub URL/oem-progress-20261027正常推送；设备仓源码/文档发布以out/oem-main-entry-20261027/publication.json及git远端为准，不推固件本地origin/main。构建为fd94b26基线的工作树快照，保留manifest，不称提交后重编。qualification1保留旧绑定；最终qualification2绑定新的当前重定位/板级证据，FD/image字节相同。build1为改进选择方式在完整编译前中止，build2完整通过，历史输出不删除。

启动链按真实OEM返回→生产GOP模式/几何/显示所有权→ConOut/正常BDS/配置发现和输入→DarwinBoot/EBS→XNU推进。当前仍是目标OEM驱动后的诊断终止镜像，未验收生产GOP/ConOut/BDS/实体输入或XNU；临时菜单不替代OEM成功。官网显示/日志章节本轮在线重读成功，未升级固定依赖或复制其他设备参数。

用户最新要求“上机”，并明确本次“拍摄已就绪，在场可恢复”。本次条件独立记录，不复用v5。22:58只读即时前检通过：enuma、Android完成、root、A槽、解锁、原boot_a/vendor_boot_a与本地备份摘要一致。新v6仍未claim/发图；本准备提交发布及远端核验后，由原单次runner再次即时核验并执行一次临时boot。

仅main-entry-v6镜像c372c5e89a25aabe8d025469364c7d160be7c034481f5cec5e0283cc3338036d、trial cfee120a-a6a4-4b02-bcff-21b1aa82372f；E01主入口ChipInfo查询前、E03首次SID前、S05真实Core返回，最多三窗24秒Hold。75秒无合格返回停止追加、优先恢复并同轮记录；不flash/erase/改槽，R027及旧v5不执行。当前观察不能预写OEM/GOP/BDS成功。

本次媒体目录已提前创建D:/Code/PortingiOS/enuma/Media-enuma/OEM-main-entry-v6-20261027-cfee120a；原始媒体只留本地，助手先独立判读落盘、展示完整字符串再请用户核对。准备与前检证据out/oem-main-entry-live-20261027/authorization.json、preflight.json。发布前不发图，无自动重试。

总报告reports/enuma-oem-main-entry-v6-candidate.json；证据out/oem-main-entry-20261027。R027/v5冻结image/qualification摘要复核一致，旧原图和out二进制仅本地保留。
