# 当前进度：读显示窗口被定位为 unclocked access，旧结论整体降级

2026-10-24 Asia/Shanghai。设备已正常回到 Android（enuma `d0fd0840`，`boot_completed=1`、root、`_a`、unlocked、`boot_a`/`vendor_boot_a` 摘要与备份一致）。本轮未 boot 任何探针镜像。

## 核心结论（2026-10-24 19:27 实测定案）

**显示域交给我们时是开的，是我们自己的派发过程把它关掉的。**

A/B 两笔对照闭合，方法是把两次只读放进 `EnumaStageCheckpoint` 的运行期分支（该分支已被 delay 对照证明确实执行并遵守配置的延时）：

| 笔 | 同位置的读 | 结果 |
| --- | --- | --- |
| A（19:20:36） | `0x0ae6b800`、`0x0ae6c000` | 正常返回 16.975 秒，分区摘要未变 |
| B（19:26:55） | `0xdeadbeef`（未映射） | **挂死**，75 秒无返回 |

B 挂死证明读确实执行；因此 A 的正常返回证明**显示窗口在 stage 10 仍然可访问**。

这**推翻了**此前"XBL 在 EnterFastbootExit 关闭显示、域在我们接手时已关"的解释。unclocked access 致总线挂死的机制不变（Qualcomm 官方 bus-hang 示例：不开时钟读 MDP 即挂并复位），但时钟被关掉的原因现在在**本固件内部**。

## 这带来什么

- **不需要补 OEM protocol 提供者**（候选 D1 的前提消失）。
- **不需要自写 MMCX / RPMh 上电序列**（域本来就是开的，候选 B 的难度大幅下降）。
- 方向变成二选一：**在派发前把需要的寄存器读完**，或**定位派发过程中关掉时钟的那个驱动**。
- 23 个 step 在派发后读取，证据等级维持"未知"，但成因已从"神秘"变成"已知"：它们读到的是时钟正在被移除时的窗口。
- 历史上的间歇性成功与"读恰好落在 teardown 之前"一致。

细节与引用见 `reports/enuma-display-window-access.json`、`docs/operations/2026-10-24-display-window-root-cause.md`。

## 下一步

**二分定位关闭者**：同样的两读放到 **stage 11**（`CoreDispatcher` 返回后）。

- stage 10 成功 + stage 11 挂死 → teardown 发生在派发期间，继续用 stage 12 细分
- stage 11 也成功 → teardown 更晚，问题落在派发之后的路径

随后按定位结果二选一：把完整 scanout 读取整体前移到 stage 10，或针对关闭者做处理。

## 边界

R-005 consumed，禁像素/MMIO 写、新映射、内存大小/基址、verified、分区写；51MiB heap、512MiB owned、example=true/Boot v3 保持。TWRP/UART 未验证，尚无可见日志/菜单，文本后端未集成，未进入 XNU。enuma 与 nuwa 同时在线，一律按 `ro.product.device` / fastboot `product` 选定 enuma。冻结镜像（step22 正向、stage23-control 及未执行正互补）不重试。

## 系统与内核现状

目标 enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9 已真实链接源平台内核，21417672 字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是 enuma 运行证据，未预链接 donor 或启动。donor 46415872 字节/237 模块和静态闭包计划通过，未 emit 预链接镜像。64MiB 配置 FAT 已生成但未接 publisher/打包启动；NativeUfs 为 SM8550 参数当前禁用；EnumaScreen 仅 host/AArch64 对象。
