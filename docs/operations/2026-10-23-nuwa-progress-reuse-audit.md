# nuwa进展对enuma的帮助

2026-10-23（Asia/Shanghai）。用户要求只读查看同级nuwa进展；未操作任何设备、启动CI、应用固件补丁或修改参考仓。固定设备仓UniXNU-nuwa@436c5570e6f05b66f318be7ea2d00f248575f3ca，固件源uefi-nuwa@1ccf760d667b9eec6dd3491c90cc04ebb7c58340。输入路径/SHA、干跑命令与实际enuma SEC结果见[机器报告](../../reports/enuma-nuwa-progress-audit.json)。nuwa另有会话推进；未提交记录只作为带哈希的时点快照，不能当上述commit内容。

## 当前进展及差异

| 项目 | nuwa | 对enuma的意义 |
| --- | --- | --- |
| 实机位置 | 已有可拍摄的DXE日志；R-010确认27次pool分配失败、末屏100KiB空闲/32KiB最大raw块、缺架构协议后断言，未到BDS/XNU | 缺协议或某PE不返回可能是资源耗尽的后果，不能只查驱动实现；不把该根因直接转移给enuma |
| 堆变更 | 已批准69MiB恢复同机原厂209.75MiB；新实际SEC的41条表仅Heap地址/长度不同，CI通过 | 借鉴“同机来源→实际FD→运行对照”方法，不借数值 |
| 最新运行状态 | STATUS仍停在09:08试前；新未提交postcondition记录09:14 Android完成1、三分区摘要不变 | 说明已有测试/恢复记录；未读到足够的新屏幕/分配结果，不能说扩堆修复成功 |
| enuma堆 | 本轮实际解析已测FD，SEC唯一DXE Heap为0x98900000/0x3300000，即51MiB；与本机XBL来源一致 | 小于nuwa旧堆只提高排查优先级，不等于耗尽；也没有nuwa那种本机原厂Heap差异证据 |
| 通用核心 | 两边Mu_Basecore都固定cfb93724a06ff86ff5ba971413368a7809ee42a5 | 分配器实现/锁语义/诊断位置可直接对照，强于跨SoC复制硬件驱动 |
| 日志出口 | nuwa当前使用既有FrameBufferSerialPortLib，用户照片确认了具体数字 | enuma覆盖为Null serial，GOP/几何未通，DFPS尾部不能借用；不能仅贴printf期待看到日志 |
| 平台/内核 | SM8550、iOS16/Darwin22 | SM8250、iPadOS17/Darwin23；不导入nuwa的地址、vendor驱动、donor/ADT、Darwin22 boot_args或loader补丁 |

51MiB是固件初始Heap描述，不是已测运行空闲量，更不是XNU owned memory。既有512MiB请求不会自动增加DXE堆；额外DRAM能否成为ConventionalMemory取决于实际资源发布/HOB/MMU与所有权，不能拿设备总RAM代替分配器视角。

## 已实际验证的可复用性

只读审查nuwa的0008分配诊断：首次CoreAllocatePoolPages搜索失败时采集请求type/pages/alignment/guard/caller及当前free/largest/ranges/special和各类型页数；最终架构服务断言前再快照。复用现有gMemoryMap，已持锁入口不重复取锁，外部调用通过Page.c内包装取锁/放锁；不在锁内调用GetMemoryMap/AllocatePool/AllocatePages。不改变原错误与断言。raw最大块不等于满足某个请求的可用块。

本轮仅把enuma固定且哈希匹配的Mu归档中两个目标原字节解出到本仓out/nuwa-progress-audit/mu-raw，用nuwa原patch执行git apply --check -p2，成功。未执行apply，未向固件源锁添加patch；未编译/运行enuma分配诊断。源文件同版不等于与现有扩展patch组合已经重放通过。行尾策略也不同：nuwa保留精确两目标CRLF，本仓管线规范化LF；真正接入时应重生成符合本仓基线的扩展patch，而非放宽空白检查。

另只读加载nuwa实际FD解析器，在内存中校验enuma已测point24/7秒FD的FV/FFS并取唯一SEC TE；读到51MiB Heap，与enuma-platform-config.json的本机XBL来源完全一致。只证明实际产物包含该描述，不证明运行页数、当前最大块或所有权。

Mu目标文件为BSD-2-Clause-Patent。nuwa设备仓本轮未检索到许可文件，新增patch不单列许可；未来直接移植应记录新增代码出处/许可并保留原版权，不能仅因共同Mu就推定所有新增片段的许可。本轮不复制源码或OEM字节入Git。

## 对主线的具体调整

1. 把“是否发生真实分配失败”提升为下一轮优先观测项，与Display构造器/服务调用排查配合。先保持51MiB、原表/512MiB/example/verified与OEM字节不变。
2. enuma没有nuwa的文字出口，R-002跨复位日志已失败并停止。可将真实首次失败/进入Display前的分配状态变成受控定时门，复用现有Timer/PSCI与2/7/2及完整恢复核验；具体门的锁/重入/无分配契约需先审计和主机验证。本文未实现或启动新门。
3. 若采到失败，区分总空闲、最大连续块、PoolType/bin、alignment/guard、SP排除及资源发布；调用者可能只是pool包装层，不能自动归因Display。若未观察失败，也不能据负向门排除所有内存错误。
4. Display库构造器/UEFI服务边界仍继续，但要核对真实调用归属，避免把嵌套镜像/事件回调当目标PE。已有canary前缀存在证据不被推翻。
5. 只有本机证据指向需要修改内存字段，才提出精确审阅项；本轮不申请或实施扩堆，不照搬209.75MiB，也不重启失败的RAM日志路线。

主要参考：[nuwa分配实测](D:/Code/PortingiOS/nuwa/UniXNU-nuwa/docs/operations/2026-10-23-dxe-allocation-build-trial.md)、[nuwa分配器审计](D:/Code/PortingiOS/nuwa/UniXNU-nuwa/docs/operations/2026-10-23-dxe-allocation-source-audit.md)、[nuwa实际SEC验收](D:/Code/PortingiOS/nuwa/UniXNU-nuwa/docs/operations/2026-10-23-factory-heap-build-trial.md)。这些是本机只读参考链接；机器报告固定具体哈希，后续工作树更新不改变本次审计结论范围。
