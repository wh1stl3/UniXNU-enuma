## D-323：文档归档与本地提交授权（2026-10-27）

用户明确要求落地全部文档和提交，并提供分析 DisplayDxe 的接续 prompt。本轮允许本地提交，取代此前“不自动提交”的限制；不含远端推送、实机执行或旧授权复用。实机继续暂停，R027 paused-by-user/未消费，旧 preparation 已过期。

最新入口：[DisplayDxe 接续 prompt](2026-10-27-displaydxe-handoff-prompt.md)。追踪可信性证据仍为 trust-check2（7 项测试、320 个模型快照、ASan/UBSan 和 AArch64 对象检查），没有新增原厂驱动执行或固件资格。代码提交不会把历史工作区快照构建变成新提交构建。全部 out、媒体、OEM 二进制、设备标识及备份不入库；本地证据需保留。

提交顺序：实际 firmware 子模块源码及迁移说明，随后设备仓代码/文档/脱敏报告及子模块指针；独立 uefi-enuma 仅提交 AGENTS/README 迁移说明，其 Mu_Basecore 及嵌套依赖既有改动不纳入本轮。提交号由 git log 和最终回复给出，不写自引用哈希。远端未发布。

# D-322：实机暂停；OEM追踪可信性增强验证通过

用户最新指令：“暂时不能实机 继续离线推进”。停止录像催办与设备操作，当前仅离线工作。本轮没有ADB/fastboot、设备重启、推送、分区操作、提交推送或nuwa操作。最后实际设备检查仍是D320的01:48未以已授权ADB在线，当前模式未知，不能当作本轮检查结果。

已实现独立开发组件：EnumaOemServiceTrace.h使用目标私有Boot Services表，原样转发LocateProtocol、HandleProtocol、AllocatePool；调用前/后分开记入128条RAM环形日志，保留实际成功/警告/错误返回、调用ID、协议GUID、请求大小与目标映像内返回地址RVA。入口记录不伪装返回值；内层返回不能关闭外层未返回记录；覆盖丢失明确计数。记录更新以原RaiseTPL/RestoreTPL串行化，实际服务调用前已恢复TPL；记录器不分配内存、不输出、不直接访问设备。

EnumaOemTraceTarget.h只为完整匹配DisplayDxe GUID 4138022f-06c7-4f79-9c94-7e33b511a4e7、BootServicesCode和有效映像范围的LoadedImage替换私有SystemTable，CRC失败不替换，原全局SystemTable/BootServices保持原字节。上下文必须持久保存，不能因为StartImage返回就释放。助手已针对本机原始PE摘要6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425复核引用；GUID门控不是任意PE字节的认证，未来Core接线还须绑定同一调度句柄与精确镜像。

EnumaOemServiceTraceView.h提供无控制台依赖的只读快照文本回放；scripts/decode_oem_service_trace.py严格解码、关联调用、保留未返回及丢失入场记录，不猜缺字或补成功。可读输出是测试夹具结果，未称真实OEM运行日志。

验证：新增out/oem-service-trace-20261027/trust-check2/result.json通过5条命令；7项Python测试包含320个嵌套/覆盖快照的独立模型对照，新增透明失败转发与部分写出拒绝测试。原check3作为历史保留。最新验证包括：宿主ASan/UBSan测试、真实C格式化到Python解码往返、7项Python用例、AArch64对象编译及实际服务偏移/LR采集指令检查。覆盖真实转发参数/输出/失败/警告、嵌套调用与在途快照、环形覆盖/计数耗尽、CRC失败、错误GUID/代码类型拒绝和后续回调生命周期。早期host-test的断言误把最后一个内层返回当成外层返回，已修正测试判据，失败输出不作通过证据。最新完整命令及源码摘要在trust-check2报告；check3仅为历史。

边界：该组件尚未加入任何固件profile、Core入口或FV，不改变R027运行代码。没有执行原厂DisplayDxe，不能称它的卡点已定位或正式GOP已修复。只覆盖上述3项Boot Services；协议方法、MMIO、SMC、锁等不在覆盖范围。RAM记录不能保证在卡死/复位后可取出，尚需有界、可观测的输出/取证路径；在此之前不生成原厂实测候选。多核调用也未验收。

冻结基线：R027/S055镜像out/deferred-menu-20261027/qualification1/image.img，SHA256 0db64285d13c0e2f60e68403b0b5498433b0b0c0143f6ce336c1885dad4afb5a，未实测/未消费。它只是继承前级显示的有界SimpleFb适配路径，不是原厂显示初始化成功。R022—R027资格/产物摘要及R027的2434个执行源码绑定均校验未变，见out/oem-service-trace-20261027/preservation.json。旧preparation1绑定的是旧文档，现已过期；不回写它，未来恢复实机时须新建准备并重新取得当前单次放行/录像，不复用旧消费。

S054完整UniXNU应用照片的人工确认保持有效，证据reports/enuma-full-menu-S-054-confirmed.json；全DXE/BDS、实体输入、生产GOP、XNU/QR仍未验收。下一步继续离线设计原厂调用追踪的可靠取证出口和精确Core接线；不增加只有黑屏/时间差的早停实验，不把暂时适配成功当原厂驱动成功。

当前新增结论：解码明确deadlock_established=false；没有返回记录只代表该快照未观察到，不能判死锁。详细证据docs/operations/2026-10-27-oem-trace-trust-validation.md及reports/enuma-oem-trace-trust-validation.json。

提交前检查：trust-check2 全部输入摘要与当前工作树一致；暂存限定文本源码/配置/文档/报告，无产物或影音。git diff --cached --check 发现既有 CRLF/行尾空白及 EOF 空行，报告保存在 out/handoff-20261027-d323；未为格式清理改写已绑定源码，不能称 whitespace 检查通过。未重新编译或新增硬件资格。
