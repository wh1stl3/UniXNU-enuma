# enuma：可应用的显示实验补丁与接管方案

2026-10-27。用户要求将elish/nabu分析推进到本机可用patch或方案。本轮交付精确PE离线补丁生成器、实际生成的实验PE、K81逐控制器契约及实施/验收方案。尚无实机修复成功结论。用户报告ADB恢复，本轮未查询；无设备动作、部署、推送。R027冻结。

## A：nabu启发的最小enuma实验补丁

本机原始DisplayDxe为315392字节，SHA256 6c6351c3c770d4f698e5e22097021fe8d20d35a8d4181df05676a48c4347f425。仅修改RVA/文件偏移0x1994四字节：e1031f32 → 01008052，即MDPInit的w1参数2→0。新PE SHA256为ed37a4e137cca2fcf4d5fa5718e18a319c2aa1b7a1cfab480693325bfbe2b5e3。

保留0x1998→0x167d8调用和错误检查、全部构造器，以及MDPSetupPipe、MDPPanelInit。它只跳过MMU/SID bit1控制区，不保证其他初始化不改硬件。原始PE checksum为0、无证书目录，本补丁不改任何头部。不是签名固件替换机制。

工作假设：前级已建立合用的显示MMU/SID配置，在二次加载中再次通过原厂协议配置可能出问题。若故障实际发生在构造期或更早的MDP初始化，补丁不会解决。若继承状态不可用，跳过SID设置也可能导致显示访问失败。它是单变量归因实验，不是已证实修复。

脚本scripts/prepare_enuma_mmu_experiment.py先校验整个PE摘要/大小、执行节映射、原指令、bit1分支、三个保留调用目标、checksum/证书目录。默认只出manifest；--emit-pe才生成PE。输出必须是本仓out下全新目录，拒绝重用及错PE。只产生副本，不修改out/firmware-vendor或任何生产目录。

已生成：out/enuma-display-application-20261027-c999/mmu-only/DisplayDxe.mmu-flag-only.efi；同目录manifest.json。只有PE，没有可启动镜像。

复现（WSL，在设备仓对应目录，输出需全新）：

```sh
python3 -B scripts/prepare_enuma_mmu_experiment.py \
  --pe out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi \
  --output out/enuma-mmu-new-run --emit-pe
python3 -B scripts/check_enuma_mmu_experiment.py \
  --pe out/firmware-vendor/Binaries/enuma/DisplayDxe/DisplayDxe.efi \
  --output out/enuma-mmu-new-check
```

检查脚本还消费此前phase2/semantic-comparison.json作为面板参考计数；完整本地证据位于out/public-display-references-20261027-c999。无需下载/执行外部程序。

## B：elish同屏路线在enuma上的实施方案

本机K81 42 02 0a原始XML摘要62aa7bd9b434c7622da7b3bb1709c69c1962a9a3ea026c2fea25602b557f480f。已核对的公开elish/CSOT资料支持复用本机现成命令和面板资源，无依据修改这些数据。scripts/plan_enuma_panel_handoff.py验证精确资源，生成逐事件和逐控制器契约，保留100ms/16ms等待及FD02、FD01的分链退出休眠。输出out/enuma-display-application-20261027-c999/elish-panel-contract.json，两链各188条命令。

具体执行分为两个互斥模式，必须在新profile中显式选择：

1. **继承画面接管**：沿已有SimpleFb有界适配实现，输入必须来自本机已核验的实际扫描源、pitch、格式、地址范围及所有权；不得仅凭面板1600×2560推导framebuffer。复用现有路由/CPU属性/边界检查，满足后发布临时GOP并测试消费者。这条方案不发送K81 reset/init命令、不重建DSI，也不承诺前级退出后硬件一直可用。R027只是冻结的相关历史候选，不拿来改造或执行；需要时另建候选和资格。
2. **正规显示初始化**：保留本机OEM DisplayDxe和K81资源，由原厂实现处理DPU/双DSI/CPHY/供电/背光；上述契约用于检查资源选择、命令顺序和控制器含义。不能把Linux DRM面板回调直接接到UEFI，它依赖Linux DSI host、regulator、GPIO等实现。本轮没有实现独立UEFI DSI主机驱动，也不把JSON契约称为驱动。若走完全开源重初始化，所缺的是这些控制器/PHY/供电后端与交接，而非重新猜面板命令。

对于当前目标，推荐正规初始化继续采用本机资源，先用A的独立实验验证MMU/SID交接嫌疑。若只需要已继承画面上的菜单，则采用模式1，明确其临时适配性质。不要同时重置面板又假设旧扫描状态保持有效。

## 新实验接入与最小判别

以下是待实施的profile接线要求，不是已经存在的构建开关，也不是本轮实机放行：

- 新默认关闭profile将原始和MMU-only作为互斥变体。隔离vendor staging，只替换目标GUID 4138022f-06c7-4f79-9c94-7e33b511a4e7对应的DisplayDxe副本；其他模块、K81 RAW、内存表、调度配置保持同源。实际FV重新抽取PE并核对变体摘要，不能只检查暂存文件名。
- 在目标CoreStartImage对同一个句柄/LoadedImage/FileGUID绑定实际入口SystemTable、持久追踪上下文与变体身份。现有EnumaOemTraceTarget只做GUID/LoadedImage一致性等检查，没有运行时PE摘要认证；现有离线RVA mapper只认原始摘要，会拒绝新PE。本轮没有放宽它。新profile必须提供受控变体身份与映像范围绑定，不得给任意PE加通用跳过认证选项。
- 先让板级出口取得可信的构造期/入口证据，再决定是否在原始变体观测MMU/SID LocateProtocol：GUID 54b6d3b4-5d33-4f91-8600-6c41d5deb19a、调用0x1bcdc、返回RVA0x1bce0。缺这一事件不证明没有执行；选定call的预转发页面也不证明原服务进入。
- 原始变体若LocateProtocol已返回，之后仍可能停在0x1bd04/18/2c/4c协议方法；这四处不受当前三项Boot Services包装器覆盖。不能把原始输出最后一条LocateProtocol当根因。必要时另做精确协议方法观测。
- MMU-only变体在到达对应路径时应跳过SID块；它仍可能因构造器、供电、锁或其他硬件调用失败。观察实际CoreStartImage返回及状态，成功返回后再独立核对GOP注册、模式、像素路由/可见性，最后才是ConOut/菜单；这些不能互相替代。
- 板级预调用出口尚需物理回调、独占窗口、当前路由/CPU重验、恢复失败终止及独立恢复策略。宿主验证不能替代该缺口。未完成前不生成可执行试验资格，不因ADB在线就临时boot。

判别表：构造链未完成→优先修实际依赖，A无预期收益；SID协议阶段有明确异常→A可区分重复初始化；A返回而原始未返回→提升SID交接嫌疑但仍需排除时序/观测扰动；A返回但无GOP/无画面→驱动返回与显示建立分开排查；A也未返回→不得扩大为连续自动试补丁或断言SID无关。

## 已完成验证与保留

check2/result.json的16项检查通过：全文件仅四字节改变，错PE/截断/重复补丁拒绝，独立指令和分支保护，输出范围及覆盖拒绝，离线mapper拒绝新身份，AArch64反汇编保留调用/错误检查，面板分链与等待保留以及错XML拒绝。此为静态/宿主检查，没有运行OEM、没有固件构建或实机通过。

无需以完整nabu跳过管线/面板初始化作为第一补丁；本轮只交付能保留真实初始化和返回判据的最小变体。两条线已形成能用于enuma的具体实验patch和实施方案，但板级接线/资格及实际效果仍待完成。不得把本文件或输出manifest解释为设备启动授权。
