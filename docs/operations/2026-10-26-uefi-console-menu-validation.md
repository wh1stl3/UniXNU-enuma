# UEFI 固件日志上屏 → UniXNU 菜单：独立验收矩阵

目标是固件开发用的 UEFI 日志和随后菜单，不以 iPadOS 图形界面作为本阶段验收。2026-10-26 当前纯只读探针不采摄像头，实际像素/可见输出验证再采集；原始影音只留本地。源码、生成库清单的哈希证据见 `reports/enuma-console-path-audit.json`，只读审计脚本 `scripts/audit_enuma_console_path.py`；不是运行证明。

| 可验项 | 依赖 | 当前独立结果 | 验收条件 / 未执行原因 |
|---|---|---|---|
| 两源 staging 与全屏坐标 | 安全路由采集、原始稳定、双路两窗推进 | S-039 间接码5支持精确逻辑坐标模型；三样本原始字保留 | 不等于物理 CTL→PP/DSC→DSI 关联；后者未闭合 |
| 格式和颜色通道 | 仅236ff/237ff，至少一个开启alpha，其他编码不变 | S-039 支持逻辑8888 RGB描述；未输出原始寄存器数值 | alpha语义仍未验证；不能直接套用RGBX绘制策略 |
| 候选地址、步长、范围、覆盖 | Native6完整decode | S-039同次通过4字节对齐、pitch>=1600*4、stride上位约束、bytes=pitch*2560、共同base/stride/unpack、Splash包含、完整几何覆盖 | 只支持解码模型，不能称实际CPU/SMMU地址等价，也不知道具体base/stride数值 |
| CPU stage1每页映射 | 上述同次完整成功/requirements22 | S-040已实现，56000故障注入和18432最大查询主机路径通过，S-040首页属性非bb提前返回；S-041排除精确44/ff/Device；S-042整段每页R/W恒等非fault、内外WT通过，具体提示字节未知 | 每覆盖4KiB页依次R/W AT成功、输出恒等、内外策略NormalWT（分配/Transient提示不同可有不同字节）；仍不证明EL1最终stage2或SMMU |
| CPU真实数据访问与缓存一致性 | 安全映射、恢复、明确像素实验范围 | S-043单字、S-044读前DSB、S-045原点128x8共1024字读取均完成；运行于EL1，最终stage2/SMMU和写入/存储后屏障仍未验证 | 独立区分Sync、只读、保存、写、恢复；不能把AT通过直接升级为可写 |
| alpha/混合语义 | 实际操作字、源alpha、常量alpha及dim | S-034严格操作字门拒绝；Native6有意保留BLEND，且alpha_semantics_unproven=true | 从固定小米实现解释有效混合方式，并验证安全不透明写入；不能直接清requirements |
| 正式GOP发布 | 上述义务及下游闭合 | InheritedGopLib后端已实现并有host/Mu Blt测试；当前诊断无GOP发布，生产接入未完成 | 合格Frame、持续Validate、GOP+匹配DisplayDevicePath在同一handle；拒绝requirements!=0；四种Blt和SetMode单独验证 |
| GraphicsConsole/ConSplitter | 合格GOP及device path、BDS连接 | 两驱动已打包；BdsEntry顺序是BeforeConsole→默认控制台连接→AfterConsole | 静态/链接已核对，当前Core终端早于BDS所以未执行；连接可能调用SetMode/清屏，是像素状态变更，不能夹带到只读试验 |
| UefiLib Print | ConOut已连接且可见 | EnumaProbe的Line调用Print；实现已打包，当前未执行 | 单独一行Print可见且正确换行；“GOP存在”不足以证明ConOut可用 |
| DiagDraw | GOP + DarwinBootVideoFromGop + 安全像素/缓存语义 | 生成DarwinProbe.inc有直接Fb[]写；不是Print或GOP Blt | 当前raw0xff000000/0xffffffff假定alpha位置，不能适配所有unpack；与Print同一个Line会相互遮蔽，应先隔离并补mask/opaque适配，再按像素门禁执行 |
| 全局DEBUG日志 | DebugLib/SerialPortLib有效接收端 | 实际EnumaProbe库清单为BaseDebugLibSerialPort + BaseSerialPortLibNull；板级明确Null覆盖 | 缺失安全屏幕日志接收/重放；仅接GOP或ConOut不会自动修复DEBUG；审计逐模块库清单，不只看DSC默认值 |
| UniXNU菜单入口 | payload检查通过、UniXNURun、显示/输入 | EnumaProbe→UniXNURun已接入；Main连接控制器、加载配置、注入驱动、初始化UI再跑Menu；Ui有GOP Blt和ConOut回退 | 源码/构建已有，当前诊断提前返回因此未执行；先验收菜单画面，再验收音量键选择/取消，不能因编译成功称菜单上机成功 |
| 早期日志 | GOP之前的独立记录通道 | SEC/早期DXE没有已验证的屏幕日志/重放 | 建议有界RAM环形记录、GOP合格后重放；尚未实现。不能为了早期日志恢复猜格式的FrameBufferSerialPortLib或修改映射 |

## 构建与观察的边界

每笔独立冻结源码提交、实际编译宏、provider/Core PE、FD/R-004记录、完整FAT和Boot v3；当前时间码是五类首结果，无法同时提供多个子项的独立结果。S-040只在Native6全部前置满足后检查CPU转换，code1统一表示前置/上下文拒绝，code2..5才属于转换阶段；若code1，应进一步隔离，不把其余检查写成已执行。

S-040历史纯查询配置计划最多18432个AT，没有像素加载/存储、MMIO store、缓存维护或页表setter。只允许EL1/EL2、MMU开启、<=48bit PA；拒绝VHE及硬件AF/dirty更新，逐次保存/恢复DAIF和PAR。仍保留requirements22、alpha和SMMU义务。依据固定Mu `AArch64Mmu.h` 的MAIR write-through0xbb，以及Arm [AT/PAR架构说明](https://documentation-service.arm.com/static/6166bfbaac265639eac59049)和[TCR HA/HD字段](https://documentation-service.arm.com/static/624ff3decaabfd7b3c13e9c7)；架构格式事实不是本机访问结论。

对现有权限内可独立验证的离线项尽量一次完成；同一实机窗口仅合并结果可区分、低风险、原授权覆盖的检查。像素写、页表/缓存属性修改、显示路由切换仍走原门禁。已consumed镜像不重试；时基无效/模糊或75秒无识别恢复立即硬停并当轮更新所有交接。


D-278补充：R-018新候选完成离线构建/实际代码审查，尚未上机，待精确范围批准。它在同次EL1/全页NormalWT/Frame和两次Native6门下尝试128x8保存、500ms对比色、全部恢复读回；最多3072load/2048store/3DSB。此为独立像素事务，不是上表只读查询的隐含扩张。当前14项native、12项历史pixel、10项FD策略测试通过；精确镜像和候选比较见2026-10-26-r018-bounded-pixel-transaction.md。只读前置不采相机；实际像素可见性再采，仅本地保存原始影音。


D-280实机更新：S-046在R-018单图批准下完成128x8保存/重验证/对比色/恢复读回，预声明时间码5；相机frame103..105可见左上白条，102前/106后消失，350帧全解码，独立Android/root/A槽/解锁/两分区及备份核验通过。此为首个最小区域可见输出证据，非文字/完整GOP/全屏/菜单验收，不清requirements22与通用alpha/SMMU义务。R-018 consumed，不重试；原始影音仅本地。后续转安全不透明绘制/文字与控制台离线实现。


D-281离线进展：独立R-019候选提供mask-aware固定UEFI字形4倍放大/128x32/500ms保存恢复，源码、主机故障注入、实际PE字形/边界/栈/恢复、FD/FAT/Boot v3已审查，未执行，pending新镜像/高度范围批准。它不调用旧DiagDraw、不发布GOP、不接全局DEBUG或ConOut；因此原始绘制/FrameBufferBlt alpha适配、日志接收与控制台连接项仍未完成，不能因本候选编译成功更新硬件验收。


D-283实机进展：S-047 R-019一次试验code5与精确恢复完成，352帧全解码，frame104/105可辨认固定UEFI，103前/106后消失；Android55.625秒且独立身份/设备与备份摘要通过。固定字形在左上小区域可见，不是全局DEBUG或Print、全屏GOP、菜单验收，不清22。R-019 consumed，不重试，原始影音仅本地。下一步优先记录并显示已有真实CPU/固件状态，避免再只验静态字符串。


D-284用户主线纠偏与安全交接：固定UEFI字样已正常显示，不再追加字母/图案/重复点屏验证；接续应直接推进UEFI固件开发、真实日志记录/屏幕输出和启动阶段诊断。S-047并未验收全局DEBUG/Print/GOP/菜单，不通过清22或标verified跳过生产接入条件。本会话只做安全收尾，没有日志新实现或R-020候选，等待管理方在旧会话结束后创建唯一接续会话。


D-285接续：新增默认关闭的DXE状态RAM日志与未接屏幕的单行回放接口，主机/AArch64及完整FD宏/staging检查通过。它不接全局DEBUG/SEC、ConOut或菜单；原矩阵中未执行的硬件项维持。独立新矩阵、失败记录、证据和下一步精确条件见2026-10-26-dxe-status-journal.md，不能用新源码覆盖历史FD审计结论。

D-286：新R-020精确候选已完成私有Core真实返回快照与256x96/2s有界缓存回放离线资格，准备S-048；用户新实机授权有效，发布/即时门后直接单笔。尚无新硬件结果，正式DEBUG/SEC/ConOut/GOP/菜单仍独立未验；详见2026-10-26-r020-cached-dxe-log-replay.md。
