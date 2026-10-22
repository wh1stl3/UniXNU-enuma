# enuma 首次 Probe 临时启动与恢复

2026-10-22，Asia/Shanghai。用户明确“可以开始实机推送了”，在 A-002 既有授权范围执行一次临时启动。没有 flash、erase、改槽或写引导链。

## 结果

**fastboot 传输和 boot 命令被接受；用户报告黑屏，无 Probe/GOP/内存图证据。已恢复 Android，boot_completed=1、root 可用，活动槽 A 与 boot/vendor_boot 摘要均未改变。** 不把 Booting OKAY 当成 BootShim/SEC/DXE/UEFI 已执行的证据，也不能仅由黑屏确定是面板驱动失败或 CPU 卡死。

| 阶段 | 证据 |
| --- | --- |
| Android 前置 | 唯一在线 enuma；BL unlocked、root uid0、sys.boot_completed=1、槽 _a |
| 恢复备份 | 本轮重新读取 boot_a 192 MiB、vendor_boot_a 96 MiB；本地摘要与设备一致 |
| fastboot 前置 | product=enuma、current-slot=a、unlocked=yes、is-userspace=no |
| 正常往返 | 先从 Android reboot bootloader，再 fastboot reboot；确认回 Android、boot_completed=1 |
| 候选启动 | 20:16:21 发出 fastboot boot；Sending 3080 KB OKAY / Booting OKAY，退出码 0，总计约 0.342 s |
| 屏幕 | 用户报告“黑屏”；没有 ENUMA PROBE 01 或菜单读数 |
| USB | 20:16:39 目标 ADB/fastboot 均不可见；本固件没有可依赖的 ADB/fastboot 回传，不能据此判定执行阶段 |
| 恢复 | 用户长按电源并配合音量下返回 FASTBOOT；再次核对 enuma 和槽 A，正常 reboot |
| Android 回收 | 20:18:24 确认 boot_completed=1、root 可用，boot_a/vendor_boot_a 摘要未变；pstore 内容 0 bytes |

候选：out/boot-candidate/enuma-uefi-probe01-r2-boot-v3.img，3153920 bytes，SHA256 3db695db10c1114352994ab64e551abc74391c2e50bbabfd48be0b37acec790a。候选不含 XNU/完整 ADT/iPadOS payload。

恢复后 boot_a SHA256 8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959；vendor_boot_a SHA256 3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba。这里只是本次确实未改变的分区，不扩展为整机存储无任何写入的保证；Android 正常启动有自己的系统写入。

结构化脱敏证据：reports/enuma-probe01-device-test.json。完整命令日志、当前二进制备份和 Android dmesg/pstore 采集在本仓忽略的 out/device-tests/20261022T201404/，不提交原始日志或设备序列号。pstore 为空不证明没有异常；本候选不运行 Linux/XNU，也不能期待其自动留下 Linux 崩溃记录。

## 执行命令范围

每条设备命令均显式指定从唯一 enuma 身份解析出的目标，未对默认设备发命令：

```text
adb -s <enuma> shell getprop ...
adb -s <enuma> exec-out su -c 'cat /dev/block/bootdevice/by-name/boot_a'
adb -s <enuma> exec-out su -c 'cat /dev/block/bootdevice/by-name/vendor_boot_a'
adb -s <enuma> reboot bootloader
fastboot -s <enuma> getvar product/current-slot/unlocked/is-userspace
fastboot -s <enuma> reboot
adb -s <enuma> reboot bootloader
fastboot -s <enuma> getvar product
fastboot -s <enuma> boot out/boot-candidate/enuma-uefi-probe01-r2-boot-v3.img
# 用户按键返回 FASTBOOT 后
fastboot -s <enuma> getvar product/current-slot
fastboot -s <enuma> reboot
# Android 启动后检查 boot_completed、root、槽位及两分区摘要，读取 pstore
```

上面斜杠列出的是分别执行的 getvar 项，不是可以原样复制的单个参数。原始 stdout/stderr 留在本机证据目录。

## 下一步定位边界

先建立更早的可观察阶段，不原样重复当前候选。需要区分 ABL 实际跳转、BootShim 复制/缓存同步、SEC 入口、DXE 调度和 GOP/应用入口。当前原厂模块字节一致与完整构建都不能替代执行证据。

静态复查注意到：所复用 BootShim 的 ARM64 头将 FD_BASE 写入 text_offset，并将 FD_SIZE+shim 写入 image_size；其内部再复制 FD 并跳到 FD_BASE。固定 MiCode 52a2f180 的 Documentation/arm64/booting.txt 将 text_offset 定义为相对 2 MiB 对齐基址的偏移，并要求 EL1/EL2、MMU/cache 入口约定。需要核对本机 ABL 对这份 raw v3 临时镜像的实际加载/跳转处理；**这是待核对契约，不是已定位根因，不能凭文档对比直接改地址再试。**

512 MiB 分配、GetMemoryMap、GOP 格式和 EBS 显示保持仍未观察；XNU 基础与 NT36523 保持此前离线状态。未修改 board.toml 内存字段、未设置 *_verified=true。恢复闭环完成，当前无人工待办；下一次新实验仍先核对在旁按键条件。
