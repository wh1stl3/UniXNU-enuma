# BootShim / SEC / DXE 黑屏定位

2026-10-22，用户授权继续操作实机。只临时 fastboot boot；未 flash/erase/改槽，未修改 board.toml / bringup-plan 内存字段或验证标记。每次先核对 enuma、解锁、root、槽 A、原始备份与设备分区摘要，结束检查 Android sys.boot_completed=1、root 和摘要。

## 入口契约

原 Probe 01 r2 是 raw ARM64 BootShim（192 bytes）+ 3 MiB FD，Android boot v3、空 ramdisk，保留原厂 vendor_boot。实际头部 text_offset=0x9fc00000、image_size=3145920。BootShim 原样保留 x0，把 FD 复制到 0x9fc00000，清理数据缓存、失效指令缓存并执行屏障，再跳入 FD；SEC 汇编选择 SP、设置栈并保存 x0 后进入 C。

text_offset 不宜按通用 Linux 文档直接修改。固定的公开 Qualcomm BootLinux.c 对照实现不引用该字段，raw 数据复制到 KernelLoadAddr，并用 ImageSize 检查空间；它有 v3/vendor_boot 支持。但该源码不是小米 enuma 的实际 ABL，不能宣称已反编译或完整核对厂商二进制。对照来源/提交/哈希见 config/entry-contract-sources.lock.json 与 reports/enuma-entry-contract.json。

真正入口证据改用定时复位。BootShim 探针读取架构计数器，延迟 2 或 7 秒，经 PSCI SYSTEM_RESET（0x84000009 / SMC）复位；如果调用返回就原地停住。SEC / DXE 则复用固定 Mu TimerLib、ArmPsciResetSystemLib 的 MicroSecondDelay / ResetCold，选择单个编译期检查点。没有猜测 framebuffer、串口或持久化 MMIO 标记，也不向分区写入日志。

## 实机观察

完整镜像摘要、命令回执和恢复状态见 reports/enuma-entry-device-tests.json；二进制只在 out/。

| 检查点 | 启动时间 | ADB 返回 / Android 完成 | 结论 |
| --- | --- | --- | --- |
| BootShim 入口，延迟 2 秒 | 20:39:14 | 15.918 / 30.103 秒 | 自动回 Android；用户明确没有按键 |
| BootShim 入口，延迟 7 秒 | 20:42:04 | 21.340 / 37.149 秒 | ADB 返回比 2 秒版晚 5.422 秒，支持定时门真实执行 |
| BootShim 复制与缓存维护后，延迟 2 秒 | 20:43:30 | 15.968 / 29.641 秒 | 到达跳入 FD 前的门；不是对全部内存内容的采样 |
| stage 3，SEC C 入口 | 20:46:49 | 16.991 / 29.875 秒 | SEC 汇编与栈交接可推进到 C |
| stage 9，DXE Core C 入口 | 20:53:55 | 15.924 / 30.194 秒 | 该诊断构建已通过 SEC 并进入 DxeMain |
| stage 10，CoreDispatcher 前 | 20:57:59 | 15.875 / 32.018 秒 | DXE 初始化已推进到调度前；尚未执行该次调度 |

每次 boot 命令成功，boot_reason=bootloader，Android 完成后 root 可用，boot_a / vendor_boot_a 摘要与原始备份一致。所有报告只保留脱敏证据，序列号留在忽略的 *.local.json。

stage 3 固件 SHA256 b0e15d90d5b97952bf4750eb4d40f690120305de7e49909fbc3193fca68096c3；stage 9 固件 db77509cf59b99862829b057a93c042c24edad12ef16e162346e816b87882d1c。各自完整构建报告、FD 审计及 raw payload 保存在 out/entry-probe/sec-entry-stage3 和 dxe-entry-stage9。

stage 10 固件 SHA256 da56498bcb5f8ce804bc9d1719d9be8cf2c4d7ed35113ec18bce70d654aeaabe，镜像 SHA256 fe97cac064925e430e4b2d4c8f058aa1cf8a0a05fb051e1c7c1b484b1eadc43b；报告/raw 保存在 out/entry-probe/dxe-dispatch-stage10。该镜像必定在调度前复位，不能当作正常 UEFI 候选使用。

提交前把补丁中标准的单空格空白上下文行规范为空行，git apply --reverse --check 仍确认与已应用源码相同，随后完成一次重建与 OEM 审计。新 FD SHA256 d6bf6bb203cd71da4b049db7f8a259c9d702be05180060e3b259c2c2d6c05d8c，尚未启动。重建未得到相同二进制摘要，原因未归因；标准构建/FD 审计报告记录此次新构建，历史实测报告保留原始输入哈希，boot-payload 报告和已测镜像/raw 仍对应原实测版，不能混用。没有因重复构建而重复设备测试。

后续解码比较见 reports/enuma-fd-rebuild-comparison.json：81 个固件文件中只有 SEC 的 TE、PcdDxe 的 PE 及外层压缩容器 section 发生变化。SEC 源 Sec.c:58 使用 __TIME__/__DATE__，观察到 20:56:24 与 21:02:55 两个时间字符串及常量池布局差异；PcdDxe 仅 RSDS 标识的 8 字节不同，其他 PE 字节一致。此处定位了具体可变元数据，尚未做 SEC 的完整语义等价证明，也不改变旧实测与新构建分别记录的原则。

这些变体有诊断插桩及链接变化，不能据此倒推最初黑屏镜像停在完全相同的位置。已证明当前路径可以越过 BootShim/SEC，下一步优先区分 DXE 初始化、驱动调度、显示依赖和 BDS/Probe 启动，而非盲改 BootShim 地址。

## 可复用诊断和检查

scripts/prepare_entry_probe.py 核对固定上游 BootShim/编译函数哈希，严格匹配单个插桩位置，保持原复制逻辑和 ARM64 头字段，拒绝覆盖已有变体。scripts/build_enuma_firmware.py --stop-stage 支持 0 或 3..10，0 为正常执行；SEC/DXE 补丁只施加于本仓 out/ 中的隔离源码。

stage 4/5/6/7/8 分别位于 PlatformInitialize、InitializeMemory、PlatformPeim、库构造、FV 解压返回后；stage 9 在 DxeMain C 入口；stage 10 在 CoreDispatcher 前。不能把相邻检查点之间所有资源都标为 verified。

BootShim 2/7 秒和复制后门在 QEMU virt 的 EL2/SMC PSCI 环境执行通过；它不模拟 Qualcomm。最初 QEMU 的 CPU 型号、ROM 和默认 HVC PSCI 配置不匹配已修正，不能把这些主机配置失败当作手机故障。stage 3 的 SEC 门也有 QEMU 执行记录；完整 Kona DXE 不以 QEMU virt 为验证平台。

30 项 Python 测试在 Windows Python 通过；共享 C 检查点头部在主机 ASan/UBSan 下验证 0 不复位、3..10 仅选定位置复位、非法值拒绝。曾误在系统 WSL Python 3.10 跑整套 Python 测试，因 tomllib 和 Windows 固定源路径失败；改用本仓已采用的 Windows Python 后全部通过，未将此误记为驱动问题。完整固件构建、33 个 OEM PE/DEPEX 原字节审计和 boot v3 往返另行通过。

## 后续边界

仍未知：实际 EL/MMU 寄存器值、GOP 参数、UEFI 可用连续窗口、512 MiB 分配、EBS、XNU 入口及 NT36523 IRQ/HID。当前诊断镜像到门即复位，不是可日用固件，不运行 iPadOS payload。后续 macOS 构建与远端缺项见 2026-10-22-build-environments.md。
