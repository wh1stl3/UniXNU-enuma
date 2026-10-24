# 读显示窗口为什么挂：机制链与对既有结论的影响

2026-10-24。本篇把现场观察与三条公开来源接成一条机制链，并说明它如何改变对过去 23 个 step 的评估。文中的"已证实"只用于有实测或公开代码支撑的环节，其余标为推断。

## 现场观察（已证实）

恢复正常 Android 后，用 `adb reboot bootloader` 进入 fastboot（**不加载任何探针镜像**），摄像头拍到的屏幕上有清晰的橙色 **FASTBOOT** 字样（`out/camera-capture/20261024T174400/`）。

也就是说：**停在 fastboot 时，显示管线是活的**——XBL 已经初始化 MDSS/DSI 并显示了界面。

而同一台设备、同一天，`fastboot boot` 我们的固件之后，读 `0x0ae6b800` 两个寄存器就挂死。两者只差一个动作：**退出 fastboot、把控制权交给我们的镜像**。

## 三条公开来源

**一｜Qualcomm 自己的 bus-hang 示例。** Qualcomm 工程师为演示寄存器访问追踪写过一个 debugfs 模块，做的唯一一件事是：**不开时钟**直接读一个 MDP 寄存器。官方描述是 "This does an unclocked access and will reset db410c"——不是返回错误码，而是总线挂死、板子复位。

**二｜XBL 在退出 fastboot 时关掉显示。** 一份 BSP 实战记录追到的结论是：XBL 的 Display 驱动"在 EnterFastbootExit 时把 Display 关闭并释放了 framebuffer，但没有重新初始化到待 boot 状态"，并把根因归为 ABL 与 XBL 对"fastboot 退出后显示资源如何移交"的生命周期没有对齐。修复方式是在 XBL 里补一次重新安装 GOP。

**三｜SM8250 的显示时钟属于 MMCX 电源域。** 上游内核补丁写明 "On SM8250 both the display and video clock controllers are powered up by the MMCX power domain"。Linux 的做法是：runtime PM 投票 MMCX → 使能 GDSC → 使能 `disp_cc_mdss_ahb_clk`/MDP 时钟 → 才访问寄存器。`disp_cc_mdss_ahb_clk` 的 halt 状态就是寄存器能不能通的开关。

## 机制链（推断，但与三条来源逐环吻合）

1. 停在 fastboot 时显示域是开的（已证实，现场照片）。
2. `fastboot boot` 退出 fastboot，XBL 按 EnterFastbootExit 的路径**把显示关掉并释放 framebuffer**（来源二）。
3. 控制权交给我们的镜像。它是 simplefb 变体，**恰好把 OEM `DisplayDxe` 排除了**（`diagnostic_omitted_oem_modules: CPRDxe, DisplayDxe, UFSDxe`）——镜内最后一个可能初始化显示的驱动不在。
4. 探针直接 `Read(0x0ae6b800)`。此时 MMCX/dispcc/AHB 时钟都没人开，固件也没有任何上电动作（来源三描述的资源全部为关）。
5. 这次读是 **unclocked access**（来源一），结果是总线挂死，而不是返回全 F 或错误码。表现就是黑屏、无 ADB、无 fastboot 枚举、只能长按。

## 它解释了哪些旧现象

- **读两次就挂**：与读多少无关，第一次触碰就够。
- **排除 DisplayDxe 有影响**：simplefb 变体让镜内没有任何显示初始化者。
- **完全断电冷启动无效**：teardown 发生在每一次 fastboot 退出之后，断电在它之前，清不到它。
- **历史 S-001 / 250849f / S-002 / S-003 反复出现且查不到代码缺陷**：它们都不是代码 bug，而是同一个非法访问。

## 它还不能解释什么

15:06–16:02 有 **7 笔**碰窗口的实机全部干净返回（geometry×2、route×2、blend×3、reason22-control）。按上面的机制链，它们本该也挂。

可能的解释有两个方向，但目前都没有证据：
- teardown 有延迟或条件，那些笔的读赶在关闭生效之前（时序竞争）；
- 某些 bootloader 路径没有走 EnterFastbootExit，因此跳转时显示仍然开着。

**这一点必须保留为未知**，不能为了故事完整而编一个理由。它同时说明：不解决上电问题，"读窗口"的结果就一直在赌时序。

## 对过去 23 个 step 的影响

过去所有 scanout 判断——描述符存在性、几何、路由、blend、sole staging——都建立在"读 MDP 寄存器返回的是设备真实状态"这一前提上。现在这个前提不再成立：**那些读可能根本就是非法访问**，读回值可能是总线错误响应、残留值或未定义。

这不等于结论一定错，而是说它们的**可信度从"实测"降级为"未知"**，必须在上电正确之后重做，才能重新获得证据地位。16:03 之后唯一那次"成功"（16:38 geometry20-control）同样按此降级。

## 下一步（按成本排序）

**A｜最早点对照（零写入，1 笔，可立即执行）**
把同样的两次读放到 **stage 4**（SEC 里 `PlatformInitialize` 之后，全流程最早的可插入点）。如果 stage 4 成功、stage 10/13 失败，就能把"teardown 是随时间发生的"从猜测变成有界事实；如果 stage 4 也挂，说明域在跳转瞬间就已关，时序窗口不存在。

**B｜在固件里显式上电 MDSS（需要新授权）**
按 Linux 的顺序打开 MMCX 投票、GDSC、AHB/MDP 时钟后再读。这是唯一能真正修好读取的办法，但涉及写 dispcc/GDSC/RPMh 寄存器，属于新的写操作，必须先走 NEED-REVIEW 拿到明确范围。

**C｜放弃在 UEFI 读 MDP（不需要写操作）**
转向 UART 或屏上文本这类真正的日志通道。代价是拿不到 scanout 现场，但不再有非法访问。注意屏上文本仍依赖 GOP，而 GOP 的建立可能同样需要显示域，需要先核实。

## 边界

本轮只做了 Android 侧只读核验与一次 fastboot 界面观察，未 boot 任何探针镜像，无像素/MMIO 写、无分区写、无新映射。设备已正常回到 Android。
