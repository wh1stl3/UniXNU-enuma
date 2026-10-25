> D-177实际结果：S-002也已超时，14:31:50人工恢复后独立核验通过，镜像consumed。下文执行前计划为历史；单一关闭线程未带来可观察改善，转离线边界定位。

# D-176：实际显示线程配置ABI与S-002新候选

S-001超时并人工恢复后，14:15:38独立Android/root/A槽/解锁/原分区摘要核验通过；不重复S-001。遵循用户恢复后自动继续离线分析/新软件规则，产生这一份有来源、单变量的新候选。

## 主判断与可推翻条件

优先排除原厂显示入口依赖的线程环境（中等置信），而不是把黑屏认作FAT/prelink错误。固定同SM8250 umi测试固件[48bc412配置](https://github.com/reAAAq/uefi-umi/blob/48bc41218c480519bfd299c22205f44e418df9d0/Platforms/Xiaomi/umiPkg/Library/ConfigurationMapLib/ConfigurationMapLib.c)明确关闭EnableDisplayThread；本机实际DisplayDxe确实消费此值。只将本机此项1→0，保留其他CPU、多线程、日志、存储和全部内存数值；不引入shim成功stub。

如果0策略下仍超时无文字，不能据此认定线程路径仍在运行；应降低该单一配置为根因的判断，转向Display入口前其他调用/Console连接/新运输入口等有区分力的证据。尤其旧代码在Kernel接口缺失时本来也可能清零并返回，因此本候选可能没有行为差异。设置0不等于同步完成面板或GOP初始化。

## 实际消费者到提供者

audit_display_thread_policy.py绑定原始XBL/DisplayDxe PE及固定umi Git blob，记录：

- DisplayDxe 0x1be4调用0x3874查询EnableDisplayThread（真实字符串0x2da98）。
- 0x3874 helper经0x38a4读取表slot0x18，0x38bc跳转；此slot与实际EFIUefiConfig.h中GetCfgInfoVal一致。
- 配置表通过0x22cb0读取bedaeabc-5e70-4d66-9733-213d072b9d04 shim HOB；0x22cc8取HOB payload+0x18的loader地址。与本仓PlatformPei发布的GUID和ShimLoader ConfigLib结构对应。
- ConfigLib把GetCfgInfoVal映射到真实LocateConfigurationEntry32，读取本机GetConfigurationMap，非造成功值。
- 0x1bfc在读到0时跳0x1c60返回路径，避开0x1c38/0x1c5c的ThreadCreate/Resume路径；没有声称后续SetMode已初始化。

check_display_config_contract.py在ASan/UBSan主机上组合生产配置表、生产helper和实际ABI头，核offsetof=0x18、读取0、case-insensitive查询、NULL/unknown拒绝，以及其他线程/CPU策略保持。它是接口主机执行，不是OEM PE实机执行。

## 新候选与离线资格

- firmware cb9e56866aeff2985a06b4b39cb8ec2390b2985a，已推送；语义差异报告只含EnableDisplayThread=[1,0]。
- FD 43f18cd3e9355ea802822831060f2437d7d694750a1a6f897e5c4299cb357808。
- boot-v3 out/full-boot/transport/enuma-display-thread-off-v3.img，103817216字节，SHA256 **5e07e65e75bc02ac515b30eec4c6306cb89d9593c91d56c31b85002e77413327**。
- 独立资格归档out/full-boot/transport/qualified-cb9e568；FAT仍49b4d622…6818773，报告/运输代码、真实系统输入保持，无人为早停。
- 完整构建、32个OEM PE/DEPEX、实际编译宏/PE常量/写保护代码和AOSP往返通过。audit_display_config_te.py直接从实际FD提取SEC TE，核64字节Name字段后的uint64值确为0；变回旧1负例拒绝，并拒绝旧source pin的构建报告。

构建包含make clock-skew警告，不能只凭build完成认定修改生效；本轮以实际FD中配置表值0、完整源pin、PE和文件摘要核对排除该项使用旧产物。没有因此放宽资格或重复执行旧镜像。

机器报告enuma-display-thread-policy.json、enuma-display-config-contract.json、enuma-display-policy-delta.json、enuma-display-config-te.json及最新enuma-ram-payload-qualification.json。board/plan内存字段未改，512MiB/verified/破坏性分区门禁保持。

## S-002执行前计划

用户已授权上机无需逐笔批准。全部当前文档和新工具提交推送后，用原相机wrapper执行新SHA的一笔临时boot；即时Android/root/槽/解锁/备份守卫、相机先开、75秒观察与既有恢复路径维持。S-001已独立恢复且consumed，不把它重新发出。

本笔仍尝试完整输入及13项同次观察；若超时/无实际文字/恢复失败，停止追加并先恢复/记录，不能放宽为成功。当前S-002未执行，实际结果将在同轮追加；不要求重新批准，不保证自动返回，不宣称线程政策已实机修复显示。

## S-002实际结果（D-177）

14:29:26.342062发出，命令2.657秒返回0、5.125秒观察断开；命令后75秒无Android/fastboot返回。451/451帧可解码，未见可判读13项报告。已停止追加并请求既有恢复，录像预先开启；14:31:50独立Android/root/槽/解锁/原两分区摘要通过。原始失败result.json及consumed账本保留。线程0单一解法未带来可观察改善，不能因此认定查询已执行或根因被排除；下一步只准备有区分力的边界软件，不再盲调配置。
