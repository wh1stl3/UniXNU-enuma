# 根卷读取适配与真实Data载荷：离线增量

按用户要求保留OEM候选等待，执行官网规则第2/8节。依据[UFS](https://unixnu.com/porting/ufs)、[平台与OS服务](https://unixnu.com/porting/platform)、[启动分层](https://unixnu.com/porting/bring-up)，2026-10-27核对。仅隔离worktree代码、主机文件与本地提交，无设备查询/启动/写入，无推送。

## 实现和实际边界

`EnumaRootRead.cpp/.h`接通固定NativeUfs的生产RootWindowRead与本仓EnumaUfsRead。输入是真实LUN几何及已验证窗口；将OS 512字节扇区请求转换为有界4KiB SCSI读，保持同一锁跨读取、校验和复制。强制完整性策略回调，失败返回真实已复制字节数，禁止越界及缺失回调。完成通知由IOKit调用方在返回、释放锁后执行。

生成Mach-O ARM64 `libEnumaRootRead.a`，包含SMMU、READ(10)和窗口桥接对象；入口`_enuma_root_read`，内部引用`_enuma_ufs_prepare_read`，SMMU仍需内核`_bzero/_memcpy`。这是可链接组件，不是已接入XNU的驱动；没有注册空IOService。真实transport须保证OCS/UPIU/SCSI、缓存同步、排他及失败DMA隔离，未知stream/PMGR依赖没有用默认值填充。

`enuma_data_seed.py`按固定NativeRamBlock格式校验DBRDISK1、范围、长度和输入SHA256。`prepare_enuma_userland_payload.py`新增显式seed/hash成对输入，接通scratch-data.img、initrd和PackedRAMDisk ADT；从实际FAT回读数据摘要，并再次检查输入未变。维持96MiB FAT及原512MiB内存请求，不扩大内存字段；打包格式接受不代表APFS或目标OS验收。

## 真实APFS seed

参考fajita固定`fb8c389bd9877d4db0ef6e09170b83752dec7259`的`make-data-seed-linux.py`，使用umi固定`3eb72578597d2ca16471b172d45eddc096a34a04`打包器。包装脚本逐文件与固定提交比对；apfsprogs固定`1bd1c1c2140d13d1b6d2e03379316572bee70aa3`，只在新out子目录构建。

从参考规格仅取目录、权限、大小写敏感及无role配置；不取SetupDone、ForceNoBuddy、身份记录或其他文件偏好。新UUID独立生成并留在产物报告，没有写入板级配置。512MiB是可丢弃测试文件系统逻辑容量，不是设备分区或RAM预留。54个目录、112条catalog记录、3个叶节点及10个对象校验和通过回读；apfsck无错误，打包后解包与raw逐字节相等。role策略仍须目标OS验证。

这修正了此前“Data构建需要Mac”的过宽限制：固定参考已提供可独立验证的Linux路线。本次确实生成了APFS文件系统；目标iPadOS挂载、目录需求、owner策略、用户态和桌面仍未运行。

## 产物与验证

所有输出位于`out/kernel-userland-20261027-2/`，旧目录不覆盖。

| 路径 | 结果 |
| --- | --- |
| bridge2/libEnumaRootRead.a | SHA256 `18f609c48d2d55474561f898fd9d6cacf440af6f2139aabb5f5de406c8cdccac` |
| data1/seed/data-linux.dbr | 86128字节、5个extent；SHA256 `8a4483bcc910875cbae2cc2ee1090abced93ea8297ef4c346a263ca42a9c5385` |
| data1/seed/data-linux.raw | 536870912字节；SHA256 `b2c589db422d7160a5b130c3d7cbc907b1c8705dd7009c4d6dd6ee28e2d91089` |
| payload-data/payload/payload.img | 100663296字节；SHA256 `4a9c77df42ef50664618d62be4564bc7056f5de5f4612a35adaecd00e3a69d49` |
| payload-no-data | 无Data回归通过，内核仍为原30组件`e879b2f0…`，未重新链接内核 |
| bridge2 | ASan/UBSan：8种扇区对齐、3处传输失败、65处完整性失败、短复制及边界/策略缺失；139组packed解析与生产C++解析器对照一致（11接受、128拒绝），另拒绝摘要错配 |
| handoff1 | 固定DarwinBoot真实AdtNode/Trust函数接受两份FAT回读输入；有Data时确认PackedRAMDisk零占位符，512MiB请求不变；全部截断及既有错误用例拒绝 |
| rejections1 | 5项CLI缺参、短输入、错误摘要/头部在构建FAT前拒绝 |
| storage-regression | 原SMMU/READ准备与固定生产RootLayout/RootPublication/RootWindowRead sanitizer、AArch64对象回归通过 |

bridge1首次Mach-O交叉编译因默认C++标准库搜索警告失败；无标准库依赖的组件添加`-nostdinc++`后bridge2通过，失败目录保留。139组格式夹具只用于主机测试，没有装入Data载荷。

## 重现与集成点

在本隔离树的WSL路径下执行以下脚本，全部指定新`--output`；具体执行命令及输入摘要见对应commands.json/invocation.json。

- `check_enuma_root_bridge.py --output <新目录>`：源码pin、sanitizer、ARM64 archive及packed差分。
- `prepare_enuma_data_seed.py --evidence-root /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma --output <新目录>`：构建目录型APFS及回读；UUID每次新建，以该次报告为准。
- `prepare_enuma_userland_payload.py --evidence-root <只读主线> --prelink <prelink1> --output <新目录> --data-seed <data-linux.dbr> --data-seed-sha256 <该次摘要>`。
- `check_enuma_data_handoff.py --with-data <载荷目录> --without-data <无Data目录> --output <新目录>`。
- `check_enuma_data_rejections.py --evidence-root <只读主线> --prelink <prelink1> --output <新目录>`。

下一步须把已实现的读组件接入真实IOKit storage对象、初始化调用者和XNU归档；核定UFS stream与PMGR ABI，明确Root/Owner/Data UUID与策略，再接RamBlock初始化。CPU framebuffer/IOSurface、NT36523 HID和launchd/backboardd/SpringBoard仍分别需要实现/运行证据。当前FAT虽有Data文件，内核尚没有相应完整服务闭包，不能作为桌面就绪镜像部署。

OEM镜像重新计算仍为`17d0169e6bd1447b358d1e91c6af9a8bf6ed368c6c44fea591fa73b970b82f08`，未boot、未消费ledger。R027冻结；共享主线git状态干净。来源、脚本、测试及产物绑定摘要汇总于`reports/enuma-root-data-offline.json`。
