# 当前进度：读显示窗口被定位为 unclocked access，旧结论整体降级

2026-10-24 Asia/Shanghai。设备已正常回到 Android（enuma `d0fd0840`，`boot_completed=1`、root、`_a`、unlocked、`boot_a`/`vendor_boot_a` 摘要与备份一致）。本轮未 boot 任何探针镜像。

## 核心结论（2026-10-24 21:00 实测定案）

**一、读显示窗口本身曾经不合法，但已找到稳定规避。**

三点包围把挂死锁定在 `[LoadImage + StartImage]` 区间：stage 10（派发前）成功、stage 11（`CoreDispatcher` 返回后）成功、stage 12（第一个驱动 LoadImage 前）成功、stage 13（SimpleFb StartImage 后）挂死。地址、读法（`*(volatile UINT32*)`）、映射属性（R-004 是 UNCACHEABLE+NS_DEVICE 且读路径实际未使用它）、调度前状态四项逐一排除。

在 SimpleFb 的 step 分支**之前**补一次同地址的预热读之后：early14 四笔全成功（17.016/17.033/15.956/15.949），step20 的 250 次完整 scanout 读取三笔全成功（17.004/17.056/18.110）——这两者历史上都会挂死。**自 23 个 step 以来，第一次能稳定执行完整读取。**

**二、已经能把显示窗口的实际数值传出固件。**

新建"延时编码"通道：stage 13 先预热 `0x0ae6b800`，再读目标寄存器的 4 个 bit，按每 bit 一档、每档一秒编码进复位延时；主机侧量返回时间即可反解。首笔返回 22.365 秒，较 16 秒基线多 6.06 秒，对应 `0x0ae00000`（MDP version）的低 4 位 = 6。**这是自 23 个 step 以来第一次拿到显示窗口的实际数值**，而且 1 秒档位在主机侧分辨得出来。

**三、读与写是两种失败模式，写仍未解决。**

R-007 像素白条实验已执行（用户批准）：gop_step=13 + 像素预览 + 预热读，**挂死，且 220 帧密集摄像全程无白条**（帧 0–26 为 Android 桌面 mean 121.8；帧 27 骤降至 33.1；帧 31 起稳定黑屏 mean 64.0、白像素 2.4% 为反光）。读路径已被预热修复，写路径仍挂。写有严格边界检查（只允许写 `0x9c000000..0x9e300000` 的 DRAM），所以不是写错到 MMIO；step20 同样调用描述符查找且成功，故挂死落在真正的写动作上，嫌疑转向那些 framebuffer 页未映射/不在 GCD（UEFI 的 page fault handler 对这种地址会 fatal）。

**四、读 display 寄存器是否安全，取决于在驱动的哪个位置读，与地址本身无关。**

| 读的位置 | 读 `0x0ae00000` | 读 `0x0ae05014` |
| --- | --- | --- |
| stage 检查点（PE 入口**之前**） | 成功 | 挂死 |
| SimpleFb 内、协议安装**之前** | 挂死 | 挂死 |
| SimpleFb 内、协议安装**之后** | 成功 | 成功 |

`CreateFrameBufferConfig` 与协议安装之间存在一个让显示窗口不可读的窗口期。取数与探针必须放在协议安装之后（early14 与 step20 验证过的位置）。这也解释了为何"预热读"能救：它把危险窗口之后的读变成了安全窗口之后的读。

## 下一步


1. **取数（已备好，待设备恢复）**：取数分支已按上面的安全窗口定稿（`gop_step` 1..7 各读一个地址的 bit 4–7，用 `gBS->Stall` 把值编码进延时，由既有 PASS 门复位）。七档镜像中 **step 1、2 已构建完成，step 3–7 在收尾时随任务终止而未完成**，均未实测。恢复设备后跑 `scripts/run_value_probes.py 1 2 3 4 5 6 7` 即可一次拿到七个寄存器的实际值。
2. **写路径**：按取数结果决定是补 framebuffer 映射，还是改为写向已确认安全的地址。
3. **更宽的通道（R-008，待批准）**：用 R-002 保留区 `0x9fff7000` 的 16 字节配合 warm reset 一次带出 128 位，见 NEED-REVIEW。

## 边界

## 边界

R-005 consumed，禁像素/MMIO 写、新映射、内存大小/基址、verified、分区写；51MiB heap、512MiB owned、example=true/Boot v3 保持。TWRP/UART 未验证，尚无可见日志/菜单，文本后端未集成，未进入 XNU。enuma 与 nuwa 同时在线，一律按 `ro.product.device` / fastboot `product` 选定 enuma。冻结镜像（step22 正向、stage23-control 及未执行正互补）不重试。

## 系统与内核现状

目标 enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9 已真实链接源平台内核，21417672 字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是 enuma 运行证据，未预链接 donor 或启动。donor 46415872 字节/237 模块和静态闭包计划通过，未 emit 预链接镜像。64MiB 配置 FAT 已生成但未接 publisher/打包启动；NativeUfs 为 SM8550 参数当前禁用；EnumaScreen 仅 host/AArch64 对象。
