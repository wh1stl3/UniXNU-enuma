# 实机显示映射与scanout前置核对

仅通过已选定enuma的root Android读取设备树/DRM，不访问像素或MMIO、不修改设备。audit_live_framebuffer.py可重放，报告enuma-live-framebuffer.json。

实机cont_splash base0x9c000000、长度0x2300000；UEFI Display Reserved长0x2400000，两者交集只能取较小范围。DRM确认1600x2560的30/60/120Hz模式。fbdev不存在，debugfs未挂载且目录不存在，未修改挂载。诊断PCD32bpp不构成真实scanout格式证据，面板DSI24bpp也不能直接替代内存像素格式。

固定Qualcomm SDE参考d066b4b959a95fd4686754ee82a7c6d21466b27c，源码SHA和来源见reports/enuma-scanout-source-audit.json。实机DT确认MDP base0xae00000/length0x84208、八个SSPP偏移与历史enuma DT相符。相对寄存器0x14/0x24/0x30/0x34/0x38分别支持核对源地址、pitch、格式、解包和操作模式。尚未读取硬件寄存器，不称运行配置已验证。

下一软件：在既有映射内只读管线描述，拒绝未知/压缩/多平面/越界配置；只有与splash保留区及预期线性布局一致时才考虑保存、短显、恢复的小亮条。缓存同步与原内容恢复必须完整，不能直接打开整屏FrameBufferSerialPortLib。没有修改board/bringup内存或verified，没有新审批项。
