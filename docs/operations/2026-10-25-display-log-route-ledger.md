> D-214补充：随后发现本机原生ramoops后端与umi布局相合，已提升日志审查优先级；详见[公开路线排序](2026-10-25-public-route-priorities.md)。以下保留D-213对账，尚无另一条已资格的UEFI全文日志通道这一边界仍成立。

# D-213：点屏与日志替代路线的实测账本复核

用户询问除继承显示取证外能否点屏或输出日志，并要求先核对已经试过的路径。本次只读对账，不新增设备动作，不修改构建源锁、审批或分区。设备最后状态仍是D-212：S-013/S-014受控回Android，独立完成/root/A槽/解锁/设备与备份摘要通过，两图consumed。

| 路线 | 真正完成到哪一步 | 当前判断与有意义的后续 |
| --- | --- | --- |
| 原厂DisplayDxe/CPRDxe直接点屏 | R-014两笔均75秒无自动返回；有连续拍摄的一笔未见可判读固件画面。后续S-002只关闭显示线程仍超时；目标调用前边界有返回，而后续PE/返回边界未闭合 | 已试过，不把简单放回原厂驱动、再切线程当新方案。若回此支线，应定位构造器/真实UEFI服务依赖和失败点 |
| 发布两个未知GUID的stub | 只是旧提案，未成为有效修复；D-163确认实际FD中DisplayDxe在APRIORI第33项（零基32），绕过DEPEX排队，但不证明实际执行到达 | 原动机被推翻，不补未知ABI空接口来碰运气 |
| 直接像素白条 | R-005受控回Android但未确认白条；R-007超时、无白条，后已恢复 | 两项已执行消耗。D-146已撤回“必定挂在写指令”的归因，因为Sync/Read先于Write；不能原样重试或把旧失败当精确写故障 |
| KTZ8866独立背光 | 芯片/总线等Android只读事实及R-012批准已有；没有独立UEFI I2C通道资格或背光写入成功记录 | 是尚未真正闭合的支线。优先审原厂I2C PE接口ABI和有界只读应答，再按已有背光范围；缺头文件不等于必须重写整个GENI控制器。背光亮也不证明有效像素或日志可见 |
| 保留RAM，经bootloader回读 | R-002临时FDT保留及8页PageReserved、ABI/reader正常加载通过；经bootloader后`matches_seed_marker=false` | 这条具体路径已验证不能保持原标记，不原样重跑；不扩大成“所有保留日志都不可能”或唯一清零函数已定位 |
| 保留RAM加warm reset | R-008写保留区/warm范围已有批准，但完整warm保留、受保护Android接手和读回尚未验证；原boot_a写入方案R-013仍pending | 不是已经成功的现成通道，也不是旧cold路径的同一试验。需先解决读回所有权/启动链，不能仅切ResetWarm或暗中写分区；不承诺XBL保留DRAM |
| UART早期串口 | 10月23日只读发现过软件配置：调试UART节点disabled、未见活动ttyMSM控制台、当时实际固件绑定SerialPortNull；尚无实物测试点/电平/接线/早期输出验证 | 真正独立于显示的早期全文日志候选，但物理链和板级后端未建立；Android串口配置不是UEFI日志实测 |
| USB CDC日志/终端 | 已审上游主机工具及giulia设备后端前提，没有enuma早期UEFI设备端日志演示 | 可开发的独立路线，需真实设备端USB初始化/CDC后端及对应启动阶段；主机脚本不能自行产生板端日志，也不能覆盖其初始化之前的故障 |
| AdvancedLogger加QR | 已审固定上游导出器，未在enuma实机输出；需要日志生产者/协议、显示、菜单输入 | 点屏以后适合复用作批量日志导出；不能单独解决当前黑屏前阶段 |

## 证据与更正边界

- [UART只读发现](2026-10-23-uart-or-screen.md)、[机器报告](../../reports/enuma-uart-discovery.json)。软件引脚组不等于已确认物理焊盘，不据此给接线指令。
- 原厂路线见[边界方案及D-163更正](2026-10-25-display-entry-isolation-plan.md)、[关闭线程实测](2026-10-25-display-thread-off.md)、DECISIONS的D-160至D-168和NEED-REVIEW的R-014/R-015。D-160/D-161中缺GUID阻派发、PE未含GUID即不调用的解释已被后续更正，不能重新采用。
- 像素见[R-005结果](../../reports/enuma-r005-device.json)、WORKLOG的R-007执行和DECISIONS D-146。早期“预热已修复”“定位store”等硬件归因不能盖过后续控制流/构建宏审查。
- RAM见[实际读回](../../reports/enuma-log-seed-after-bootloader-01.json)：8页仍保护、ABI及reader加载/卸载返回0，但标记不匹配，`persistence_proven=false`。不能只读早期“模块尚未执行”的准备文档；它们是历史。
- [背光与warm方案](2026-10-25-backlight-and-batch-transport.md)保留硬件事实与审批记录，但其中“必须自写I2C”“打包模块即运行”“必须某一种分区方案”等说法不作已证事实。先查原始XBL内容及实际ABI/启动依赖。
- [上游路线复审](2026-10-25-latest-porting-route-review.md)已覆盖cas/umi/另一enuma、QR和主机终端。cas/umi的继承显示正是当前路线的重要来源，不把相同思路改名后当第二条独立路线。

本次重新校验固定框架16e592abee8a550dec8154ed1f38b5ebc4f16213的`docs/porting/log-capture.md`、`AdvancedLogDxe.c`文件摘要及`debug_terminal.py`的git blob；没有更新当前构建pin。上游明确将QR输出放在已有菜单/GOP/日志协议的阶段。官网umi显示其CPU framebuffer菜单/用户态已有记录，但它的手机面板、内存、分区和Recovery布局不能照搬enuma。

## 实际取舍

没有找到一条本机已经资格通过、现在可立即启用的另一条早期全文日志通道。当前继承显示路线已有新信息：计数使能门在完整管线/稳定性之前拒绝，应继续以独立原生活动/计数观察补证，不扩大为硬件不工作。

有独立增量价值的备选是原厂I2C ABI/背光通道资格，以及具备实物接入条件时的UART。前者只能解决背光这一个环节，后者可绕开显示输出依赖；USB/完整warm日志是更大的专项。原厂显示栈只作为有新故障隔离依据的支线，QR留待显示可用后接入。本问题仅完成对账，不自动改变主线、不复活已消耗镜像或增加设备动作。

机器对账：[enuma-display-log-route-ledger.json](../../reports/enuma-display-log-route-ledger.json)。原始影音始终只留本地。
