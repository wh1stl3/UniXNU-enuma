# R-002 临时 Android 日志区保留实测

状态：2026-10-23，保留阶段完成；用户要求本轮实测收尾后停下。未加载模块、未读写物理日志或标记，未验证持久性。

## 授权与边界

用户明确“批准 R-002 软件日志路线（推荐）”。应用的 board 字段与原提案语义一致：enabled=false、source_region="Log Buffer"、physical_base="0x9fff7000"、size="0x8000"。不改原 DRAM/FD/栈/heap/MemoryMapLib、512 MiB、example 或任何验证标记；A-002 下只做临时 fastboot boot。未 flash/erase/改槽，未写 stock vendor_boot。提案文件保留为历史审查材料，不要再次应用。

原 Android 对这 8 页无保留，原审计仍有效。用户批准配置不意味着地址运行时已验证或日志可用。

## 实现与复用

- 原厂备份 boot_a SHA256 8f40f0c93cbc8b183f6296b427522e1155eb9ba1ff32065f09f6bc98cf972959，vendor_boot_a 为 3da202d0c9a5b618b61cd1923e87810536c5f70c9da7875de80075290641daba。私有备份仍在 out/device-tests/20261022T201404/。
- 原 kernel 为 54,839,312 字节 raw ARM64 Image，原 image_size=66,211,840；原第一条分支目标为 Image+0x2b80000。入口封装放在原 image_size 之后，只修改原第一条 B 与 Image size，不平移原内核。原头的 OS version、command line、ramdisk 保留，v3 解包回读比对通过。镜像约 116 MiB，小于备份分区大小。
- diagnostics/android_fdt_entry.S 保留 x0..x3、恢复 SP，再跳原入口。diagnostics/fdt_reserve.c 严格验证结构、大小和空 reserve map；先只读规划，确保空间后才改 FDT。只增加候选 32 KiB 的一个 reserve tuple，名称后缀复用只改变 nameoff 编码，不改变名称或属性值。重入/已有 reserve owner/空间不足均拒绝修改。写后按 CTR_EL0 的实际缓存行清理到 PoC。
- 没有分配新的外部 FDT 缓冲区，没有新增物理地址；入口代码与临时栈作为 Image 附加字节，进入原内核后不再依赖它们。对其他/更大布局不泛化成功。
- 复用固定 AOSP unpack_bootimg、已有 enuma 身份/备份/恢复检查器。capture_log_reservation.py 只读 FDT、kpageflags、iomem、dmesg，不读取日志物理内容。

## 两次实机样本

| 项目 | 第一次 | 第二次 |
| --- | --- | --- |
| 发 boot 时间 | 01:00:21 | 01:04:27 |
| 镜像 SHA256 | 5c219c89f635f44732e085ba0a94f6d17d3c7ba990f472c0e3310bc58e625d20 | e0bd9b25d6e472a52735893dac970bb6f475e6c5394e6d878c615e54d6fc0e42 |
| ADB / 完成（秒） | 15.003 / 27.448 | 16.079 / 31.722 |
| 活动 FDT reserve map | 空 | 唯一 0x9fff7000 / 0x8000 |
| 8 页 KPF_RESERVED | 全 false | 全 true，标志均 0x100000000 |
| Android/root/分区摘要 | 正常、原摘要 | 正常、原摘要 |

第一次仅靠 NOP 腾空间，保护未生效。运行后 FDT 的全部 524 字节 NOP 在 /chosen、kaslr-seed 之后；固定 MiCode 驱动源码 drivers/of/fdt.c:1173–1178 在读取 rng-seed 后将它改为 NOP。这支持“运行后 NOP 不一定在入口前存在”的解释，但没有直接观测入口前 FDT，不断言首次封装的具体分支或 Bootloader 清空行为。

第二版增加同表相同名称后缀复用，原样本前四处 etm7/etm6/etm5/etm4 共可省 20 字节；保留完整 rng-seed。加入合成 512-byte seed、无 NOP 的输入回归。第二次活动 FDT SHA256 为 6e88ca4a3bfaf8823da9bcf44defdd5ad7a3f8eec671223675076fd5457a0d09；与原 FDT 解析比较，节点及属性值差异为零。

## 离线模块工作与限制

实际 /sys/kernel/kheaders.tar.xz SHA256 e2482393e1d7ae0d2ec9c8155f940ae70317c907f54ef4f04f186f3c3db63c5c。存在仅大小写不同的 Linux 头文件；普通 Windows 目录会冲突，失败的 out/log-readback/kheaders/ 不可用于构建。最终在 out/log-readback/kheaders-exact/ 启用 NTFS case-sensitive 属性后提取，构建器逐一比对所有常规文件与原 archive。5 个链接条目不提取，其中有原构建主机绝对路径，不能跟随。

从当前设备只读取回 rdbg.ko / qca_cld3_qca6390.ko 提取 __versions 与 .modinfo，不发布二进制。两者 module_layout CRC=0xaad0c453，printk=0x7c32d0f0；vermagic 为 4.19.157-perf-gf8cf95f4dc15 SMP preempt mod_unload modversions aarch64，struct module=832 字节。

复用固定 MiCode 52a2f180 的 scripts/module-common.lds、arch/arm64/kernel/module.lds；它们是链接参考来源，不冒充实际运行内核的完整构建源码。来源 URL/SHA 在总报告中。无物理访问 ABI 探针 3808 字节，SHA256 43b6bbd06fa16af578501db60ed917c5c205243aa6f8429763ca79671e4e2313，离线字段核对通过，但未 insmod、未推入设备、未作运行时 ABI 判定。

16 字节 marker reader 源码默认不启用，显式构建时还会检查 8 页 PageReserved；此模式未构建/执行。后续正常加载仍须由内核校验所有 CRC/布局，禁止 force-load。尚无最小 marker writer、跨复位链或 SEC/DXE 实际日志。

## 已执行命令与验收

以下仅记录，不表示本轮要继续执行。路径为 WSL；Windows 静态检查 Python 使用 WorkBuddy bundled Python。

```text
python -B -m unittest discover -s tests
python -B scripts/check_workspace.py
python -B scripts/audit_log_reservation.py
wsl -d Ubuntu-22.04 -- /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/check_log_fdt.py
wsl -d Ubuntu-22.04 -- /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/build_log_reservation_boot.py --approved-r002 --stock-boot /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/device-tests/20261022T201404/boot_a.bin --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/boot-candidate/r002-android-reservation-02.img
python -B scripts/run_enuma_entry_probe.py --image D:/Code/PortingiOS/enuma/UniXNU-enuma/out/boot-candidate/r002-android-reservation-02.img --label android-log-reservation
python -B scripts/capture_log_reservation.py --name reservation-device-02
wsl -d Ubuntu-22.04 -- /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/firmware-tools/bin/python -B /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/build_log_reader.py
```

45 项 Python、21 组实际 C ASan/UBSan（含拒绝时零修改、重复拒绝、全部节点/属性值相等）、来源/board/defconfig/example 检查、AOSP v3 回读通过。ABI 探针编译通过。没有重新构建 UEFI、重跑 macOS CI 或设置 verified 标记。不要覆盖已有候选或报告，复测选新名字。

## 停止状态与恢复顺序

按用户要求停止；无人工按键/在场待办、无新审批项。当前是已经完成启动的临时保留 Android，最后一次身份/root/boot 与 vendor_boot 摘要复核正常。保护不会自动延续到普通 Android 重启，不能用本次报告授权之后的物理读回。

恢复工作时，先重新检查活动 FDT 和 8 页状态，再正常加载/卸载 ABI 探针；随后才审计 marker reader/writer 及跨复位链。链中不能让未保留的 Linux 启动覆盖候选区。只有最小标记存活和只读回读都通过，才启用同范围的有界固件日志。候选清空、ABI 或临时契约不满足按 R-002 停，不自行换址、扩大、借显示/SMEM 或改为刷分区。

公开证据：reports/enuma-log-reservation-device.json 汇总全部样本与离线 ABI；*-01.json 保留失败；*-02.json 为实际保留通过；enuma-log-fdt-host.json 为主机检查。原始 FDT、页标志、dmesg、头文件、KO、镜像、设备标识与备份只在 out/。
