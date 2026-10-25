# D-193：S-007后复审最新官网与其他设备，主线转向可见GOP

复审日期：2026-10-25，Asia/Shanghai。遵照用户“下一步决策之前看官网最新移植界面、其他设备及仓库”的要求，本轮S-007后没有追加启动、没有更新构建源码pin。所有引用的最新版本另放out/sources/*-review，未替换现有构建树；锁与文件SHA见config/upstream-route-review-20261025.lock.json。

## 本机实测与恢复

S-007 point22在16:03:54发出，2.640秒命令返回，5.109秒USB断开，75秒无Android/fastboot返回，453/453主录像可解码。镜像dedd87a68a005817d8ee2d95c60d7949b244bdc31c974e1bd4c760d817c25361已consumed，不重试。用户报告Android恢复，16:06:22独立完成/root/A槽/解锁/原boot_a、vendor_boot_a及备份摘要一致；恢复录像739/739帧可解码。原始影音仅本地，当前无人工或审批待办。

入口前S-005自动返回，而直接返回S-006和退出汇合S-007均超时，支持优先怀疑PE包装层/构造器/主函数调用区间，但不是门命中或驱动挂死证明；异常/无效Exit/复位仍竞争。原OEM路线连续早停已难获得可读错误，下一步不再默认继续更深的同类早停。

## 最新官网及框架

已实际打开[Port a device](https://unixnu.com/porting/)、[Firmware integration](https://unixnu.com/porting/uefi-firmware)、[Migration](https://unixnu.com/porting/migration)、[Log capture](https://unixnu.com/porting/log-capture)和[Devices](https://unixnu.com/devices/)，并读最新源文件。搜索摘要仍可能给旧页面，判读以打开的页面和固定源码为准。

- UniXNU最新审查pin：16e592abee8a550dec8154ed1f38b5ebc4f16213。新版使用schema2、SoC源、OS profile、components.toml、统一DTS/ADT及porting.toml；共享组件按硬件范围命名，ShengUfs和Adreno740不是SM8250通用驱动。
- 本仓构建pin仍5fdbd5d08518bc2d5c196264c56a377dd80cf5ca。GitHub compare显示diverged（最新端ahead250/旧端behind137），不是原pin上的小幅快进。API文件列表达300上限，不能当完整差异清单；未作全量迁移审计，也不直接换底座或rename全部组件。
- 官网要求共享UniXNURamDiskDxe、DiskIo和FAT。实际新驱动将整个FDT initrd作为块设备，并要求长度是512倍数；enuma已审的vendor前缀2230+100663296字节FAT余182字节，若实际FDT按该拼接范围传入会被拒绝。运行时FDT仍未观察，不能据静态预测声称运输成功/失败。保留本机精确前缀、原有映射边界和CRC诊断；未来复用共享驱动要做受审薄适配，不能为了“用上游”删除这些检查或同时发布两个相同卷。
- AdvancedLogDxe/QR是共享现成实现，应复用，不重写QR栈。但它消费AdvancedLogger协议并通过可用UniXNU Tools菜单输出，日志生产者、GOP和输入需先建立，不能解决当前菜单前无画面。接收应在本地解码，原始相机画面不上传；不复活R-002跨复位RAM日志。
- debug_terminal是主机工具，现有后端依赖giulia设备端CDC协议。仅安装主机脚本/改USB ID不会给enuma增加早期USB日志，不把它当即插即用修复。

## 同板/同SoC与其他设备核对

| 来源及固定提交 | 实际有用证据 | 对enuma的判断 |
| --- | --- | --- |
| [umi](https://unixnu.com/devices/umi)，UniXNU-umi 3eb72578597d2ca16471b172d45eddc096a34a04；uefi-umi HEAD727f6c2，已实测固件仍48bc412 | 同SM8250、同iPad7,1/21H461，维护者attempt80记录Setup Assistant/触控、UFS/root/Data；本次HEAD与原审查相同 | 继续作为OS/ADT/PMGR/UFS首要真实实现参考；保留板差，不复用手机内存/GPT/触控常量。HEAD不是实测固件pin |
| [cas](https://unixnu.com/devices/cas)，设备HEAD6cb54b05，固件HEADa491522d；实测346a404f/893f5025，框架67e8ef0 | 同SM8250；维护者记录三笔UEFI菜单、RAM FAT、CasSmoke执行返回和Android恢复。casPkg当前对实测固件提交无差异；本轮实际运行纯DisplayDecode/DisplayBlt主机测试16项通过，未访问MMIO | 新的优先显示实现来源。它绕过OEM DisplayDxe，解码继承SDE管线，支持分块覆盖/像素布局/自动或手动刷新。主机通过和cas实测均不等于enuma通过 |
| [elish](https://unixnu.com/devices/elish)，a357eae98a0da0796c8efec8519825367da1e3e7 | 官网/源码仍为板描述、分阶段配置和TODO，缺本机固件与完整构建树；源码有Wi-Fi/5G文字混用 | 不是可用enuma固件基线；Windows检出PROVENANCE大小写冲突，审查用git blob，不拿检出状态当代码改动 |
| [另一enuma](https://unixnu.com/devices/enuma)，Tlrenhb设备606a9927/固件70ba7ba3 | 最新源码仍pre-dump骨架，固件留# error，采用其他SM8250 v1参数 | 不是另一份enuma实机成功；不以其v1布局替代本机已审ABL v3。官网wh1stl3段落来自我们旧记录，是同源转述而非独立佐证 |
| [sheng](https://unixnu.com/devices/sheng)，框架相关设备0e1f6e52、固件20ac23d5 | 完整schema2样例；最新DXE清单明确可选OEM显示与继承SimpleFb路径，集成共享RAM和日志 | 复用通用接口/组织方式，SM8550 UFS/GPU/显示寄存器及内存不能直接移植 |
| [fajita](https://unixnu.com/devices/fajita)，fb8c389bd9877d4db0ef6e09170b83752dec7259 | SDM845已到XNU root等待，无存储驱动；记录ABL大ramdisk限制和特殊槽/分区操作 | 参考阶段定位方法，不照搬flash/改槽。官网与当前README对FAT承载分区有不同表述，更说明必须按具体源和设备核验 |

## 调整后的推进顺序

1. **首选：离线评估继承扫描输出的真实GOP。** 复用cas的纯快照解码/Blt算法及边界检查方法，适配为enuma显式几何/本机splash边界输入；对照本机FDT和固定小米/Lineage SDE定义，审CTL/SSPP、双DSI、多源矩形、stride/format、secure/UBWC/压缩及刷新模式。先用已保存事实和合成负例，缺少本机运行时快照写未验证，不把cas快照当本机。此步骤不访问设备或改变内存字段。
2. **再做可审查的最小GOP候选。** 保留完整系统FAT，避开未闭合OEM DisplayDxe依赖，仅在本机范围/格式/路由谓词全满足时发布GOP并记录真实失败。不是放宽原来保守谓词，也不是原样重试旧SimpleFb。要能解释与旧step20/21及R-005失败路径的区别，失败就返回明确原因。
3. **新增写入先单独审。** cas有0x9f940000状态区、0x9c000000 splash、1080x2340面板和8MiB FD等专用值；全部不可复制。CasGop SetMode会清屏，DisplayHardware会写像素及CTL_START，定时器还会刷新。当前不移植这些副作用或假定获得新像素/MMIO授权。若本机命令模式必须kick，先做具体源码/固定地址/谓词/保存恢复/观察及最小写入范围的可审查实现，再按AGENTS决定是否需精确批准；此轮未请求批准、不改内存。
4. **可见菜单后复用AdvancedLogger+QR取得批量真实错误**，同步核13项RAM运输/文件，再到DarwinBoot/XNU。不是为了显示单点永远停住。日志文本经脱敏后提交，原始影音本地。
5. **OEM真实服务取证作为备用**：若继承路线确不适用或无法形成可恢复可观测候选，再对原厂构造器的具体真实服务做目标活动映像门控取证；不默认继续point23/24等旧早停序列。
6. **schema2迁移独立进行**：先记录当前源/组件/板级契约并做离线解析迁移，保持数值和来源；待确定新通用组件收益再迁移构建链。此次不改board.toml/example、内存、verified、源锁或分区。

主判断（中等置信）：现在最有价值的工作是恢复可见错误通道，cas提供了比继续猜OEM构造器更具体、同SoC且有记录的替代实现。它不证明OEM根因，也不保证enuma能用。若本机快照显示不支持的压缩/secure/不连续布局或无可恢复刷新条件，则推翻首选并回备用方案，绝不放宽格式/范围判据。

## 本轮落地与未执行

新增固定来源锁、audit_latest_porting_review.py、enuma-latest-porting-review.json，核8个仓库/40个文件，cas平台目录对实测提交相同，16项主机测试通过。仅做源码/主机复审，S-007之后无新boot，无新固件功能实现、像素/MMIO写入、内存/verified变化或flash/erase/改槽。构建仍锁firmwarecb9e568/UniXNU5fdbd5d；所有已执行镜像consumed。原始影音从未进入本轮Git提交/Release/CI。
