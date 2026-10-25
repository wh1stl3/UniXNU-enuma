# UEFI 固件日志上屏 → UniXNU 菜单：独立验收矩阵

目标是固件开发用的 UEFI 日志和随后菜单，不以 iPadOS 图形界面作为本阶段验收。2026-10-26 当前纯只读探针不采摄像头，实际像素/可见输出验证再采集；原始影音只留本地。源码、生成库清单的哈希证据见 `reports/enuma-console-path-audit.json`，只读审计脚本 `scripts/audit_enuma_console_path.py`；不是运行证明。

| 可验项 | 依赖 | 当前独立结果 | 验收条件 / 未执行原因 |
|---|---|---|---|
| 两源 staging 与全屏坐标 | 安全路由采集、原始稳定、双路两窗推进 | S-039 间接码5支持精确逻辑坐标模型；三样本原始字保留 | 不等于物理 CTL→PP/DSC→DSI 关联；后者未闭合 |
| 格式和颜色通道 | 仅236ff/237ff，至少一个开启alpha，其他编码不变 | S-039 支持逻辑8888 RGB描述；未输出原始寄存器数值 | alpha语义仍未验证；不能直接套用RGBX绘制策略 |
| 候选地址、步长、范围、覆盖 | Native6完整decode | S-039同次通过4字节对齐、pitch>=1600*4、stride上位约束、bytes=pitch*2560、共同base/stride/unpack、Splash包含、完整几何覆盖 | 只支持解码模型，不能称实际CPU/SMMU地址等价，也不知道具体base/stride数值 |
| CPU stage1每页映射 | 上述同次完整成功/requirements22 | S-040已实现，56000故障注入和18432最大查询主机路径通过，S-040已有效实测：首个页读AT恒等/非fault，属性非0xbb提前返回；写权限及其余页未执行 | 每覆盖4KiB页依次R/W AT成功、输出恒等、属性0xbb；仍不证明数据访问、EL1最终stage2或SMMU |
| CPU真实数据访问与缓存一致性 | 安全映射、恢复、明确像素实验范围 | 当前未执行；历史像素超时不能定位为store故障，Sync/Read先于Write | 独立区分Sync、只读、保存、写、恢复；不能把AT通过直接升级为可写 |
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

计划最多18432个AT，没有像素加载/存储、MMIO store、缓存维护或页表setter。只允许EL1/EL2、MMU开启、<=48bit PA；拒绝VHE及硬件AF/dirty更新，逐次保存/恢复DAIF和PAR。仍保留requirements22、alpha和SMMU义务。依据固定Mu `AArch64Mmu.h` 的MAIR write-through0xbb，以及Arm [AT/PAR架构说明](https://documentation-service.arm.com/static/6166bfbaac265639eac59049)和[TCR HA/HD字段](https://documentation-service.arm.com/static/624ff3decaabfd7b3c13e9c7)；架构格式事实不是本机访问结论。

对现有权限内可独立验证的离线项尽量一次完成；同一实机窗口仅合并结果可区分、低风险、原授权覆盖的检查。像素写、页表/缓存属性修改、显示路由切换仍走原门禁。已consumed镜像不重试；时基无效/模糊或75秒无识别恢复立即硬停并当轮更新所有交接。
