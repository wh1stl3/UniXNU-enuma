# 独立 uefi-enuma 与官方固件配置

2026-10-22 Asia/Shanghai。按用户明确要求建立 [wh1stl3/uefi-enuma](https://github.com/wh1stl3/uefi-enuma)，迁移固件增量并接入官方配置。本轮没有USB、启动、刷写或改槽操作。

## 仓库分工和固定来源

- UniXNU-enuma保留board.toml、内核/ADT/驱动、构建编排、boot v3打包和五件套。
- firmware/改为Git子模块，URL指向wh1stl3/uefi-enuma；当前固定 **3376c4411e08442f45f4120ed6d96f2e302c51e8**，并由config/uefi-source.lock.json记录33项输入摘要。Gitlink、锁、实际HEAD与文件逐项核对。
- uefi-enuma是UniXNU/uefi-sheng的派生仓，以329b473df1e53a3bfa64b2b39b79670c4c02279b为基线。迁移自设备提交1ab7ee8，25个原文件逐字节核对，映射见Resources/Enuma/migration.json。六个补丁、两份诊断头、板级DSC/FDF、内存/配置表和打包配置保持原字节。旧LICENSE改名LICENSE.enuma，旧README保存在docs/enuma-overlay.md，根LICENSE保留上游许可。
- 保留Mu_Basecore、Common/Mu、Common/Mu_OEM_Sample三个固定gitlink；移除继承的Binaries/外板ACPI/未用OpenSSL入口和外板构建工作流。新工作流仅手动检查源码契约，不能产生OEM固件。
- 本地独立维护树D:/Code/uefi-enuma与设备firmware子模块为两个checkout；修改应先提交/推送固件仓，再更新设备gitlink与锁，禁止复制回重复的板级源码。

厂商102个输入只有路径/摘要写入Resources/Enuma/vendor.json；33个PE/DEPEX、原始cfg/XML、备份及标识留在设备out/。不自动下载或公开厂商内容。

## 官方配置与实际执行路径

board.toml只新增[firmware]与[firmware.defines]，指定config、dsc、fd、packages、preflight及四个Mu core补丁。所有旧表与1ab7ee8完全一致，example=true、512MiB请求及内存/验证标记未改。

scripts/build_enuma_firmware.py现在负责核对固定源、暂存源码/依赖、组装最小固件构建树和设置环境，实际编译调用固定UniXNU的 **unixnu.firmware.build**。没有另写一套EDK编译命令。配置来自board.toml，诊断选项仅临时覆盖该次构建的defines；默认stage0不插入复位。

官方preflight经scripts/enuma_firmware_preflight.py调用固件仓Resources/Scripts/enuma_preflight.py：先限制写入设备out/，核对来源、102厂商文件、三依赖提交、DarwinBoot接口和Mu原始基线，再复制需要的私有输入/生成Probe include/应用UEFI自身补丁。官方backend负责Mu core补丁的顺序应用和finally逆序恢复；构建后再次核对DxeMain/Dispatcher基线。

[firmware].submodules=[]是因为包装器已校验并物化依赖路径，不代表不需要Mu依赖；它避免backend对暂存根发起子模块写入。新检出可使用固件子模块自身的三个固定依赖；本地回归复用了只读--reference，不写共享参考仓。

官方顶层CLI的example保护仍生效，实际执行build firmware已确认在构建前拒绝。此阶段使用明确限定“只构建固件”的包装器，沿用已批准的镜像生成范围，不放行完整XNU/prelink或整机build。

## 复现

```sh
# 在设备仓内，用WSL初始化所需固定依赖；厂商输入须另行本地提取。
git submodule update --init --recursive -- firmware
python3 -B scripts/check_firmware_source.py
python3 -B scripts/check_workspace.py
python3 -B scripts/build_enuma_firmware.py --unixnu /path/to/pinned/UniXNU --stop-stage 12 --dispatch-ordinal 1
```

Python需tomllib（3.11+，或既有firmware-tools venv的tomli兼容），固件编译需clang/lld/llvm工具、make和BaseTools依赖。包装器默认--reference为firmware；已有固定依赖checkout可显式--reference。输出全在设备out/firmware-build；原UEFI归档锁仅保留历史基线来源，本轮UEFI源码实际来自固定gitlink，Mu core仍用固定归档暂存。

打包仍使用prepare_enuma_boot_payload.py及package_enuma_boot.py，raw BootShim+FD、Android boot v3、空ramdisk、保留原厂vendor_boot。不能换成通用gzip/v0路径。

## 验证与边界

- 最新33项Python通过，含真实重叠patch重复应用、禁止把源树当暂存和缺少OEM输入时停止。
- 固件仓首轮源码Actions run39796073610通过（a1215b7）；最新固定3376c44的run39796926508随后完成并通过，已回读日志及源码契约PASS行。本地最新源码契约也通过。
- 官方backend实际完成完整UEFI构建。当前FD **bc3e16ffd0ab46ceff6bee689c2ba18c496e31e43be553163755fd0922c1f917**，81文件/33原厂PE-DEPEX字节审计通过；Mu core补丁已恢复。
- 新v3候选 out/boot-candidate/enuma-official-backend-stage12-boot-v3.img，3153920 bytes，SHA **25d6947b0eeb2112baeab69d301d97984747b17082d279808e72bcd3d09525d7**，回读通过，**未启动**。快照out/uefi-migration/official-backend-stage12/。
- 最新实机仍为迁移前stage12首项加载前镜像d9740693…，GOP、BDS、菜单、完整内存图和XNU仍未观察。新构建不能继承旧实机结论。

预检曾发现配置需在预检前暂存，以及旧Mu原文件摘要为CRLF而工作副本规范化为LF。已保留原始摘要并从锁定Mu归档推导独立LF摘要，未放宽内容校验或内存规则。官方backend恢复后再次核对这些LF基线。

证据：reports/enuma-firmware-source-migration.json、enuma-firmware-preflight.json、enuma-official-firmware-integration.json、enuma-firmware-build.json、enuma-fd-audit.json、enuma-uefi-source-actions.json。
