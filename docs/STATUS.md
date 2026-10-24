# 当前进度：读显示窗口被定位为 unclocked access，旧结论整体降级

2026-10-24 Asia/Shanghai。设备已正常回到 Android（enuma `d0fd0840`，`boot_completed=1`、root、`_a`、unlocked、`boot_a`/`vendor_boot_a` 摘要与备份一致）。本轮未 boot 任何探针镜像。

## 核心结论

**固件在读 MDP/DSI 寄存器之前，没有任何人把显示域打开。** 现场观察 + 三条公开来源逐环吻合：

1. **现场（已证实）**：`adb reboot bootloader` 进 fastboot、不加载任何镜像，屏幕显示橙色 **FASTBOOT** 字样 → 停在 fastboot 时显示管线是活的（`out/camera-capture/20261024T174400/`）。
2. **来源一**：Qualcomm 官方的 bus-hang 演示模块，"unclocked access" 读一个 MDP 寄存器就会挂总线并复位开发板——不是返回错误码。
3. **来源二**：BSP 实战记录——XBL 的 Display 驱动在 **EnterFastbootExit 时关闭 Display 并释放 framebuffer**，不恢复到待 boot 状态；根因是 ABL 与 XBL 对"fastboot 退出后显示资源如何移交"的生命周期没有对齐。
4. **来源三**：SM8250 的显示时钟控制器由 **MMCX 电源域**供电，Linux 通过 runtime PM + GDSC 显式上电，`disp_cc_mdss_ahb_clk` 是寄存器能否访问的开关。

加上一个我们自己的事实：simplefb 变体**恰好把 OEM `DisplayDxe` 排除了**（镜内最后一个可能初始化显示的驱动不在）。

于是链条是：停在 fastboot 显示正常 → `fastboot boot` 退出时 XBL 关显示 → 控制权交给固件 → 固件直接读寄存器 → unclocked access → 总线挂死。表现就是黑屏、无 ADB、无 fastboot、只能长按。

细节与引用见 `operations/2026-10-24-display-window-root-cause.md`、`reports/enuma-display-power-sources.json`。

## 它解释了哪些旧现象

读两次就挂（与读深度无关）；断电冷启动无效（teardown 每次 fastboot 退出都发生，断电在它之前）；历史 S-001/250849f/S-002/S-003 反复出现却查不到代码缺陷（根本不是代码 bug）。

## 它还不能解释

15:06–16:02 有 **7 笔**碰窗口的实机全部干净返回。按机制链它们本该也挂。可能是 teardown 有延迟（时序竞争），也可能是某些路径没走 EnterFastbootExit。**保留为未知**，不编理由。

## 对既有结论的影响（重要）

过去 23 个 step 的 scanout 判断——描述符、几何、路由、blend、sole staging——都依赖"读回值是设备真实状态"。现在这个前提不成立：那些读可能本身就是非法访问。**它们的证据等级从"实测"降为"未知"**，包括 16:38 那次唯一的"成功"。要恢复证据地位，必须在上电正确之后重做。

## 下一步（按成本）

| 选项 | 内容 | 代价 |
| --- | --- | --- |
| **A（推荐先做）** | 把同样两次读放到 **stage 4**（SEC `PlatformInitialize` 之后，最早可插入点）。stage 4 成功而 stage 10/13 失败 → teardown 随时间发生被证实；stage 4 也挂 → 域在跳转瞬间已关 | 零写入，1 笔实机 |
| **D（优先级高于 B）** | 不排除 OEM `DisplayDxe`（连同 `CPRDxe` 一起放回），让厂商驱动自己完成上电并建立 GOP，探针在其后读 | 不需自写寄存器序列；代价是 DisplayDxe 会绘制并可能污染待观察屏幕，且 enuma 原厂 GOP 成功率未实测 |
| **B** | 在固件里按 Linux 顺序显式上电 MMCX/GDSC/AHB/MDP 时钟后再读 | 需写 dispcc/GDSC/RPMh 寄存器，属新写操作，**必须先走 NEED-REVIEW 拿范围**；RPMh 在 UEFI 无现成驱动，写错时序会把 GDSC 卡死 |
| **C** | 放弃在 UEFI 读 MDP，转 UART 或屏上文本 | 无写操作，但拿不到 scanout；屏上文本仍依赖 GOP，需先核实 GOP 是否也需要显示域 |

在 A 出结果之前，不再追加任何读取型显示探针。

## 边界

R-005 consumed，禁像素/MMIO 写、新映射、内存大小/基址、verified、分区写；51MiB heap、512MiB owned、example=true/Boot v3 保持。TWRP/UART 未验证，尚无可见日志/菜单，文本后端未集成，未进入 XNU。enuma 与 nuwa 同时在线，一律按 `ro.product.device` / fastboot `product` 选定 enuma。冻结镜像（step22 正向、stage23-control 及未执行正互补）不重试。

## 系统与内核现状

目标 enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9 已真实链接源平台内核，21417672 字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是 enuma 运行证据，未预链接 donor 或启动。donor 46415872 字节/237 模块和静态闭包计划通过，未 emit 预链接镜像。64MiB 配置 FAT 已生成但未接 publisher/打包启动；NativeUfs 为 SM8550 参数当前禁用；EnumaScreen 仅 host/AArch64 对象。
