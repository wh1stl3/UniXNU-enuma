# 持久启动槽位：离线事实与设备待测清单

范围：只回答「把载荷放进设备、断电重启仍进系统」这条路上**现在能离线确定什么**与**必须靠设备一条只读命令确认什么**。不含选型结论，不含设备操作。全部事实给到文件 + 行号；判不出的一律进 §6。

状态：`self-checked`（本文只做既有材料的交叉核对，未上机、未构建、未写设备）。

---

## 0. 摘要（只有事实）

1. LUN0（`sda`）的 GPT 有 **34 项**在用（index 0..33），主备头与项数组 CRC 均已重算通过；**`boot`/`vendor_boot` 及 `xbl*`/`abl*`/`tz*`/`hyp*`/`modem*` 全都不在这张表里**。`super`(9,126,805,504 B) 与 `userdata`(242,455,916,544 B) 与 `vbmeta_system_a/_b` 在同一张表里。
2. `boot_a/boot_b` 在 **LUN4（`sde`）**，`vendor_boot_a/_b` 也在 LUN4；`xbl_a` 在 LUN1（`sdb`），`xbl_b` 在 LUN2（`sdc`）。分区名 → 设备节点映射有完整只读采集（123 条 by-name 链接 = 6 个整盘节点 + 117 个分区）。
3. 原厂槽位容量：`boot_a`/`boot_b` = **201,326,592 B**，`vendor_boot_a`/`vendor_boot_b` = **100,663,296 B**。当前 `boot.img` = **203,505,664 B**，比 `boot_a` 大 **2,179,072 B**，比 `vendor_boot` 大约 2 倍。
4. `fastboot boot` 只把镜像送进内存启动一次、不写槽（官方文档 + 本板多次实机记录）；`flash` 才是写入槽位。本板 `boot_a` 在 2026-10-21 被实际刷写过一次（Magisk），回读校验通过、Android 仍可启动。
5. 仓库自身已经把「槽位容量与持久载荷落点」标为未确认：`out/enuma-gop-production-20261114-r5/INSTALL-LAYOUT.json:136`。

---

## 1. 已知事实：LUN0 GPT 里没有 boot / vendor_boot

### 1.1 证据来源

| 证据 | 路径 | 关键行 |
| --- | --- | --- |
| 采集记录（含命令、CRC、几何） | `UniXNU-enuma/.cache/android-ufs-identity-gpt-20261114-201917/record.md` | LUN 表 36-45；GPT 导出 56-80；34 项 80；期望值 82-90 |
| 主 GPT 头 + 项数组的逐项解析 | 同上 `inspect-primary.txt` | 头 4-27；34 条 entry 28-299 |
| 备 GPT 头 | 同上 `inspect-backup.txt` | 头字段与 CRC |
| 原始字节（本地，不入库） | `gpt-primary-lba0-1.bin` 8192 B `84a6a7b8…e159b`；`gpt-primary-entries-lba2-3.bin` 8192 B `4eb14543…af89f`；备头 4096 B `7b2c4198…89403`；备项数组 8192 B（与主项数组同哈希） | `record.md:60-65` |
| 生产侧引用同一份证据 | `out/enuma-gop-production-20261114-r5/INSTALL-LAYOUT.json` | 54-101（证据文件与主备头字段）、102-116（`"used_partitions": 34` 与 userdata 边界） |

几何：LBA = 4096 B；盘块数 61,880,320 = 253,461,790,720 B；`first_usable` 6，`last_usable` 61,880,314；项数组 LBA2–3（64×128 B）；备份头 LBA 61,880,319，备份项数组 LBA 61,880,315–16。主头 CRC `0xd10f49a7`、项数组 CRC `0xae19c5c4` 均计算相符（`inspect-primary.txt:7-27`）。

### 1.2 LUN0 全部 34 个分区（`inspect-primary.txt:28-299`）

| # | name | start LBA | end LBA | bytes(4K) | 备注 |
| --- | --- | --- | --- | --- | --- |
| 0 | switch | 6 | 7 | 8,192 | |
| 1 | ssd | 8 | 15 | 32,768 | |
| 2 | dbg | 16 | 23 | 32,768 | |
| 3 | bk01 | 24 | 31 | 32,768 | |
| 4 | bk02 | 32 | 63 | 131,072 | |
| 5 | bk03 | 64 | 127 | 262,144 | |
| 6 | bk04 | 128 | 255 | 524,288 | |
| 7 | keystore | 256 | 383 | 524,288 | |
| 8 | frp | 384 | 511 | 524,288 | |
| 9 | countrycode | 512 | 1023 | 2,097,152 | |
| 10 | misc | 1024 | 2047 | 4,194,304 | |
| 11 | bk06 | 2048 | 4095 | 8,388,608 | |
| 12 | logfs | 4096 | 6143 | 8,388,608 | |
| 13 | ffu | 6144 | 8191 | 8,388,608 | |
| 14 | oops | 8192 | 12287 | 16,777,216 | |
| 15 | devinfo | 12288 | 16383 | 16,777,216 | attrs `0x1000…` |
| 16 | oem_misc1 | 16384 | 16639 | 1,048,576 | |
| 17 | metadata | 16640 | 20735 | 16,777,216 | |
| 18 | bk08 | 20736 | 24575 | 15,728,640 | |
| 19 | splash | 24576 | 32767 | 33,554,432 | |
| 20 | bk09 | 32768 | 40959 | 33,554,432 | |
| 21 | persist | 40960 | 57343 | 67,108,864 | **红线** |
| 22 | persistbak | 57344 | 73727 | 67,108,864 | **红线（persist 备份）** |
| 23 | mtdblk | 73728 | 81919 | 33,554,432 | |
| 24 | logdump | 81920 | 98303 | 67,108,864 | |
| 25 | minidump | 98304 | 122879 | 100,663,296 | |
| 26 | rawdump | 122880 | 155647 | 134,217,728 | |
| 27 | cust | 155648 | 417791 | 1,073,741,824 | |
| 28 | super | 417792 | 2646015 | 9,126,805,504 | attrs `0x1000…` |
| 29 | vbmeta_system_a | 2646016 | 2646047 | 131,072 | attrs `0x1004…` |
| 30 | vbmeta_system_b | 2646048 | 2646079 | 131,072 | attrs `0x1000…` |
| 31 | bk010 | 2646080 | 2654207 | 33,292,288 | attrs `0x1000…` |
| 32 | rescue | 2654208 | 2686975 | 134,217,728 | |
| 33 | userdata | 2686976 | 61880314 | 242,455,916,544 | 根卷目标 |

**结论（事实）**：`boot`、`boot_a`、`boot_b`、`vendor_boot`、`vendor_boot_a`、`vendor_boot_b`、`xbl*`、`abl*`、`tz*`、`hyp*`、`modem*` 均不在这 34 项里。任务描述中的「33 个非空项」应为 **34**（`record.md:80`、`INSTALL-LAYOUT.json:102` 一致写 34）。

---

## 2. 多 LUN 架构事实

### 2.1 六个 LUN（Android/Linux 视角）

`.cache/android-ufs-identity-gpt-20261114-201917/record.md:36-45`：

| 磁盘 | SCSI 路径 | LUN | 512B sectors | 4096B blocks | bytes |
| --- | --- | --- | --- | --- | --- |
| sda | `1d84000.ufshc/host0/target0:0:0/0:0:0:0` | 0 | 495,042,560 | 61,880,320 | 253,461,790,720 |
| sdb | `…/0:0:0:1` | 1 | 32,768 | 4,096 | 16,777,216 |
| sdc | `…/0:0:0:2` | 2 | 32,768 | 4,096 | 16,777,216 |
| sdd | `…/0:0:0:3` | 3 | 65,536 | 8,192 | 33,554,432 |
| sde | `…/0:0:0:4` | 4 | 4,456,448 | 557,056 | 2,281,701,376 |
| sdf | `…/0:0:0:5` | 5 | 131,072 | 16,384 | 67,108,864 |

控制器 `1d84000.ufshc`、驱动 `ufshcd-qcom`、`proc_name=ufshcd`；六盘同型号 `KLUEG8UHDC-B0E1`（SAMSUNG，rev 0200）。记录另注明：**LUN1–5 未导出，其上是否有 GPT 及 CRC 状态未核**（`record.md:90`）。

### 2.2 分区名 → 设备节点（全量 117 个分区，只读采集）

来源：`UniXNU-enuma/.cache/live-capture/20261107T141941555586Z/by_name_links.txt`（8854 B，`ls -l /dev/block/by-name` 原样输出，123 条链接 = 6 个整盘节点 + 117 个分区；同内容另存于外部备份 `PortingBackup-20261106/legacy-enuma-backups/android-root/20261021T124813939334Z/block-links.stdout`）。各 LUN 分区数：sda 34、sdb 2、sdc 2、sdd 4、sde 65、sdf 10，合计 117。

**LUN1 `sdb`（16 MiB）**

| 分区 | 节点 | 行号 |
| --- | --- | --- |
| xbl_a | sdb1 | 121 |
| xbl_config_a | sdb2 | 123 |

**LUN2 `sdc`（16 MiB）**

| 分区 | 节点 | 行号 |
| --- | --- | --- |
| xbl_b | sdc1 | 122 |
| xbl_config_b | sdc2 | 124 |

**LUN3 `sdd`（32 MiB）**

| 分区 | 节点 | 行号 |
| --- | --- | --- |
| ALIGN_TO_128K_1 | sdd1 | 2 |
| cdt | sdd2 | 27 |
| ddr | sdd3 | 35 |
| mdmddr | sdd4 | 66 |

**LUN4 `sde`（2,281,701,376 B，65 个分区）**

| 分区 | 节点 | 分区 | 节点 | 分区 | 节点 |
| --- | --- | --- | --- | --- | --- |
| aop_a | sde1 | aop_b | sde26 | bk42 | sde51 |
| bk41_a | sde2 | bk41_b | sde27 | bk43 | sde52 |
| tz_a | sde3 | tz_b | sde28 | bk44 | sde53 |
| hyp_a | sde4 | hyp_b | sde29 | dip | sde54 |
| modem_a | sde5 | modem_b | sde30 | apdp | sde55 |
| bluetooth_a | sde6 | bluetooth_b | sde31 | gsort | sde56 |
| mdtpsecapp_a | sde7 | mdtpsecapp_b | sde32 | msadp | sde57 |
| mdtp_a | sde8 | mdtp_b | sde33 | spunvm | sde58 |
| abl_a | sde9 | abl_b | sde34 | limits | sde59 |
| dsp_a | sde10 | dsp_b | sde35 | limits-cdsp | sde60 |
| keymaster_a | sde11 | keymaster_b | sde36 | storsec | sde61 |
| **boot_a** | **sde12** | **boot_b** | **sde37** | uefivarstore | sde62 |
| cmnlib_a | sde13 | cmnlib_b | sde38 | secdata | sde63 |
| cmnlib64_a | sde14 | cmnlib64_b | sde39 | vm-keystore | sde64 |
| devcfg_a | sde15 | devcfg_b | sde40 | vm-data | sde65 |
| qupfw_a | sde16 | qupfw_b | sde41 | | |
| vbmeta_a | sde17 | vbmeta_b | sde42 | | |
| dtbo_a | sde18 | dtbo_b | sde43 | | |
| uefisecapp_a | sde19 | uefisecapp_b | sde44 | | |
| multiimgoem_a | sde20 | multiimgoem_b | sde45 | | |
| multiimgqti_a | sde21 | multiimgqti_b | sde46 | | |
| vm-linux_a | sde22 | vm-linux_b | sde47 | | |
| featenabler_a | sde23 | featenabler_b | sde48 | | |
| imagefv_a | sde24 | imagefv_b | sde50 | | |
| **vendor_boot_a** | **sde25** | **vendor_boot_b** | **sde49** | | |

行号：`boot_a` 25、`boot_b` 26、`vendor_boot_a` 115、`vendor_boot_b` 116、`abl_a` 4、`abl_b` 5、`tz_a` 105、`hyp_a` 51、`modem_a` 74、`vbmeta_a` 111、`dtbo_a` 42、`uefivarstore` 109、`secdata` 98。

**LUN5 `sdf`（64 MiB）**

| 分区 | 节点 | 行号 |
| --- | --- | --- |
| ALIGN_TO_128K_2 | sdf1 | 3 |
| modemst1 | sdf2 | 76 |
| modemst2 | sdf3 | 77 |
| fsg | sdf4 | 49 |
| fsc | sdf5 | 48 |
| bk51 | sdf6 | 22 |
| mdm1m9kefs3 | sdf7 | 64 |
| mdm1m9kefs1 | sdf8 | 62 |
| mdm1m9kefs2 | sdf9 | 63 |
| mdm1m9kefsc | sdf10 | 65 |

LUN0 的 34 条在 §1.2；by-name 里 `super`→`sda29`（103）、`userdata`→`sda34`（110）、`vbmeta_system_a/_b`→`sda30/sda31`（113/114）、`persist`→`sda22`（86）、`rescue`→`sda33`（91）、`misc`→`sda11`（73）。

### 2.3 槽位容量的独立取证

外部备份 `PortingBackup-20261106/legacy-enuma-backups/android-root/20261021T124813939334Z/`（只读快照，2026-10-21）：

| 量 | 值 | 文件 |
| --- | --- | --- |
| `blockdev --getsize64 /dev/block/by-name/boot_a` | 201,326,592 | `boot_a-size.stdout` |
| boot_b | 201,326,592 | `boot_b-size.stdout` |
| vendor_boot_a | 100,663,296 | `vendor_boot_a-size.stdout` |
| vendor_boot_b | 100,663,296 | `vendor_boot_b-size.stdout` |
| vbmeta_a / vbmeta_b | 131,072 | `vbmeta_a-size.stdout`、`vbmeta_b-size.stdout` |
| 整分区 `dd` 副本 `boot_a.img` | 201,326,592 B，`759eaf09…a0ecb`，`remote_hash_verified: true` | `report.json` → `original`、`backups[]` |
| 整分区副本 `vendor_boot_a.img` | 100,663,296 B，`3da202d0…1daba` | `report.json` → `backups[]`；入库引用见 `proprietary-files.txt:49` |
| 当时的活动槽 | `_a` | `slot.stdout`、`flash-slot.stdout` |
| 当时的 patch 目标 | `boot_a` | `report.json` → `patch_target` |

另一处独立佐证：`.cache/firmware/vendor_boot_a.img` 实际落盘 **100,663,296 B**（与 `vendor_boot_a-size.stdout` 一致）。

**推论（算术，不是新证据）**：`boot_a` 分区 201,326,592 B < 当前 `boot.img` 203,505,664 B → 当前镜像**按字节数放不进 `boot` 槽**；`vendor_boot` 槽 100,663,296 B，只有当前 `boot.img` 的 49%。

---

## 3. 当前载荷形态与候选位置

### 3.1 两个产物是什么

| 产物 | 大小 | 是什么 | 证据 |
| --- | --- | --- | --- |
| `enumaPkg`（UEFI 固件 FD） | 3,145,728 B（`0x9FC00000`/`0x300000`） | Mu-Silicium 固件卷：SEC→DXE→BDS 与 UniXNU/DarwinBoot 模块；**不含内核**，当前也不含板级 DTB（`uefi-enuma/Platforms/Xiaomi/enumaPkg/enuma.fdf:105-110` 的 `DtPlatformDxe`/`FdtBlob` 整段为注释） | `AGENTS.md:15`；`README.md:117`；`enuma.fdf:105-110` |
| `boot.img` | 203,505,664 B | AOSP boot header **v1**，`ANDROID!`；kernel 槽 = 192 B BootShim + gzip(FD) + 追加设备树 `Image.gz-dtb`；ramdisk 槽 = 192 MiB FAT 负载（`payload.img`，含 `UniXNU.efi`、`kernel.macho`、ADT、trustcache、Data 种子） | `out/enuma-gop-production-20261114-r5/boot.json:2-12`；`docs/ufs-reserved-memory-audit.md:65` 引 `UniXNU/scripts/unixnu/bootimg.py` `combined = shim + firmware`；`docs/ramblock-host-build.md:185-186`；官方 `UniXNU/docs/zh/guide/boot.md:43-51` |
| `payload.img` | 201,326,592 B | 上述 ramdisk，SHA `44022ef2…e5c97` | `payload.json:11-12`；`boot.json:3` |

`boot.json` 另有：`kernel_address 0x8000`、`tags_address 0x1e00000`、`fd_sha256 e524988b…`、`dtb_sha256 42d36a00…`、`hardware_tested: false`。

### 3.2 `fastboot boot` 与 `fastboot flash` 的区别

| | `fastboot boot <img>` | `fastboot flash <partition> <img>` |
| --- | --- | --- |
| 作用 | 镜像经 USB 进内存，ABL 直接跳转；**不写槽** | 写入指定分区，掉电后仍在 |
| 官方表述 | 「传输镜像并启动一次」（`UniXNU/docs/zh/guide/boot.md:38-41`） | 「刷写会覆盖该分区」（同文件 `:22-28` 用于 userdata） |
| 本板实机 | 2026-11-09 起多次成功，最近两次 2026-11-16（`fastboot boot` exit 0，无刷写） | 2026-10-21 对 `boot_a` 执行 1 次（`flash_attempts: 1`），回读 `8f40f0c9…` 校验通过，Android 带 root 启动成功 |
| 依赖 | bootloader 解锁且接受自定义镜像（官方要求，`guide/requirements.md:114`） | 同上 + 分区容量与 AVB/vbmeta 接受镜像 |
| 断电重启后 | 回原槽内容（D2：`docs/decisions.md:15`「设备自行重启会回 Android」） | 走该槽内容 |

参考（**别板**，不可当本板结论）：alioth 记录 `fastboot boot` 不写槽、`flash` 落到 `boot_b`（`UniXNU/docs/zh/devices/alioth.md:666`）。

### 3.3 候选位置：只有容量与代价，不做选型

| 候选 | 容量 | 当前镜像是否装得下 | 写入代价 / 不可逆性 |
| --- | --- | --- | --- |
| `boot_a`（sde12） | 201,326,592 B | **否**（差 2,179,072 B） | 覆盖 Android 启动镜像；已有整分区 stock 备份 `759eaf09…`（外部备份）可回写恢复；A/B 另一槽保留 |
| `boot_b`（sde37） | 201,326,592 B | **否**（同上） | 同上；覆盖的是未激活槽，但 `boot_b` 的现有内容 `ac3bd652…` 也已有备份 |
| `vendor_boot_a`（sde25） | 100,663,296 B | **否**（约 2 倍差） | 覆盖原厂 vendor_boot（含 4 个 SoC 基座 DTB，`proprietary-files.txt:49`、`README.md:151`）；已有备份 `3da202d0…` |
| `vendor_boot_b`（sde49） | 100,663,296 B | **否** | 同上；备份 `6e733d43…` |
| `super`（sda29）内的逻辑分区 | 分区总量 9,126,805,504 B | 逻辑分区清单与空闲空间**未读取** | 需改 `super` 的 dynamic partition 元数据（写操作），无备份；`ABL` 是否从 super 逻辑分区取启动镜像**无任何仓库证据** |
| `misc`（sda11，4 MiB） | 4,194,304 B | 不是载荷位 | 只承载 bootloader 命令（recovery 等），非镜像容器 |
| `rescue` / `cust` / `ffu` / `oops` / `splash` / `bk08`-`bk09`-`bk010` / `rawdump` 等 | 8 MiB–1 GiB | 体积上部分够 | **无证据**表明 ABL 或 UniXNU 会从这些 GPT 分区取启动载荷；写这些分区同样属设备写入 |
| `uefivarstore`（sde62） | 未单独取证（LUN4 内） | 不是载荷位 | UEFI 变量存储，非镜像容器 |

补充（官方文档给出的通用约束，非本板实测）：payload 进 `vendor_boot` 时受三条上限约束——header 窗口（ramdisk `0x01000000`、dtb `0x01f00000`，只剩 15 MiB）、分区容量、FAT 可挂载性（`mformat -T 8192 -h 64 -s 32`）；文档同时说明该路线针对「`boot` 无 ramdisk 的 GKI 设备」（`UniXNU/docs/zh/guide/boot.md:100-118`）。本板 4.19 内核、`vendor_boot` 自带 ramdisk（`README.md:151`），是否属于该情形**未判定**。

---

## 4. 最小设备侧探测清单（全只读）

前提：按型号唯一识别 enuma（`fastboot getvar product` / `getprop ro.product.device` 均为 `enuma`），所有命令带 `-s <serial>`。Android 侧命令按当前 Android 13 + Magisk root 侧环境写（root 仅在读块设备/GPT 时需要）；fastboot 侧全部是 `getvar`，不写 flash。

| # | 侧 | 命令 | 目的 | 预期输出 | 判定标准 |
| --- | --- | --- | --- | --- | --- |
| 1 | adb | `adb -s <serial> shell "ls -l /dev/block/by-name"` | 复核 by-name 映射是否仍与 §2.2 一致 | 123 条链接（117 个分区），`boot_a -> /dev/block/sde12`、`vendor_boot_a -> /dev/block/sde25` | 与 `by_name_links.txt` 逐条一致→映射未变；出现新名字或节点变化→§2.2 作废，重取 |
| 2 | adb+root | `adb -s <serial> shell 'for p in boot_a boot_b vendor_boot_a vendor_boot_b; do printf "%s " $p; su -c "blockdev --getsize64 /dev/block/by-name/$p"; done'` | 确认四个槽容量未变 | `boot_a 201326592` / `boot_b 201326592` / `vendor_boot_a 100663296` / `vendor_boot_b 100663296` | 任一 ≤ 203,505,664 即「当前 boot.img 装不进该槽」；与 §2.3 一致→旧容量可用 |
| 3 | adb+root | `adb -s <serial> shell "su -c 'cat /proc/partitions'"` | 一次拿到六个 LUN 的边界与 LUN4 分区数 | `sda..sdf` 六个主项 + `sde1..sde65` 等子项（该文件以 1 KiB 为单位，故 `sda` 的 size 列应为 247521280） | `sda` = 247521280（1 KiB 单位 = 253,461,790,720 B）；LUN4 子项 65 个且含 `sde12`/`sde25` |
| 4 | adb+root | `adb -s <serial> shell "su -c 'dd if=/dev/block/sde bs=4096 skip=1 count=1 2>/dev/null \| head -c 8 \| od -An -c'"` | 判断 LUN4 是否为 GPT（而非仅 QCOM ptable） | `E   F   I       P   A   R   T` | 出现 `EFI PART` → LUN4 有 GPT 头，可导出项数组核对；否则只能靠 by-name 与 ptable |
| 5 | adb+root | `adb -s <serial> shell "su -c 'dd if=/dev/block/by-name/vendor_boot_a bs=1 count=8 2>/dev/null'"` | 确认 vendor_boot 槽当前镜像格式 | `ANDROID!` 或其它 | `ANDROID!` → 原厂 vendor_boot 是标准 boot 格式（可解析 v3 header 字段）；其它→该槽非标准容器，需先取证再谈写入 |
| 6 | adb+root | `adb -s <serial> shell "su -c 'lpdump /dev/block/by-name/super 2>/dev/null \| head -60'"` | 只读列出 `super` 内逻辑分区与空闲 | `Metadata version`、`Partition:` 列表、`Free space` | 列表里**没有** `boot`/`vendor_boot` → super 不是槽位；有 → §3.3 该行需重写。命令不存在则记「未确认」 |
| 7 | adb | `adb -s <serial> shell "getprop ro.boot.slot_suffix; getprop ro.boot.slot"` | 当前活动槽 | `_a`（2026-10-21 时）或 `_b` | 决定「刷哪一槽不会立刻切断 Android 启动」的事实前提，仅记录 |
| 8 | adb | `adb -s <serial> shell "getprop ro.boot.verifiedbootstate; getprop ro.boot.flash.locked"` | AVB / 锁状态 | `orange`/`green`、`0`/`1` | `orange`+`0` → 解锁且校验已放宽；`green` → 刷写路径需另证 |
| 9 | fastboot | `fastboot -s <serial> getvar product` | 机型唯一识别（前置门禁） | `product: enuma` | 非 `enuma` 立即停 |
| 10 | fastboot | `fastboot -s <serial> getvar current-slot` | fastboot 侧活动槽 | `current-slot: a` | 与 #7 一致→可信；不一致→记冲突，不继续 |
| 11 | fastboot | `fastboot -s <serial> getvar partition-size:boot_a` | ABL 视角的槽容量 | `partition-size:boot_a: 0x0C000000`（=201,326,592） | 与 §4 第 2 条一致→容量事实固化；不同→以 ABL 值为准并记账 |
| 12 | fastboot | `fastboot -s <serial> getvar partition-size:vendor_boot_a` | 同上 | `0x06000000`（=100,663,296） | 同上 |
| 13 | fastboot | `fastboot -s <serial> getvar has-slot:boot` | 是否 A/B | `has-slot:boot: yes` | `yes` → 双槽回退可用；`no` → 单槽，覆盖即无回退 |
| 14 | fastboot | `fastboot -s <serial> getvar max-download-size` | 单次下载上限 | 十六进制字节数 | ≥ 203,505,664 → `fastboot boot` 现有镜像路径无障碍（本板上机已多次成功，此项只作固化） |
| 15 | fastboot | `fastboot -s <serial> getvar all` | 一次拿全部只读变量（含 `unlocked`、`slot-count`、各 `partition-size`） | 变量列表 | 只作留档；输出含序列号——**不入库** |

约束：任何一条返回异常/不支持即记为「未确认」，不重试、不改命令为写操作；全程不得出现 `flash`、`erase`、`format`、`oem`、`set_active`。

---

## 5. 风险与红线

### 5.1 红线分区（不得写）

`xbl*`（sdb1/sdc1 及各 `xbl_config_*`）、`abl*`（sde9/sde34）、`tz*`（sde3/sde28）、`hyp*`（sde4/sde29）、`modem*`（sde5/sde30，另含 sdf2–sdf10 的 modemst/fsg/fsc/mdm1m9kefs*）、`persist`（sda22）/`persistbak`（sda23）、RPMB。

依据：`docs/context-brief.md:26`、`docs/decisions.md:17`（写入分级：`xbl/abl/tz/hyp/modem/persist/RPMB` → 红线）。

`devinfo`(sda16)、`secdata`(sde63)、`storsec`(sde61)、`keystore`(sda8)、`frp`(sda9)、`cdt`(sdd2)、`ddr`(sdd3)、`mdmddr`(sdd4) 未在红线清单内，但属设备身份/校准数据；本文件不对其写入作任何推定。

### 5.2 D2 对刷写时机的前置要求

| 位置 | 原文要点 |
| --- | --- |
| `docs/decisions.md:13` | 终态把 `userdata` 刷成 UniXNU 根卷；bring-up 用 `fastboot boot` |
| `:15` | 继续 `fastboot boot`，不刷 `boot` 分区；设备自行重启回 Android |
| `:16` | 「只刷 `userdata` 不够」——启动载荷必须进设备（刷 `boot`/`vendor_boot` 槽或等价持久启动方案）；**`boot`/`vendor_boot` 刷写不在红线内，但仍是设备写入，须用户当轮授权**；并且「在 bring-up 前五阶段有日志证据、根卷持久化验证通过后再做」 |
| `:17` | 写入分级：主机刷写与自研代码写 userdata → 当轮授权；厂商固件启动的附带写入允许 |
| `:18` | 刷 `userdata` 时机：前五阶段全部有真实日志证据 + 用户确认 Android 数据可弃 |
| `:20` | 验收六项含「写入跨重启保留」「重启不再进 Android」 |

另：`docs/context-brief.md:11`（持久化需载荷进设备，属设备写入，须当轮授权）、`:7-9`（持久根卷必须在真实 UFS `userdata`）；`enuma/AGENTS.md:50`（长期授权只覆盖 `adb reboot bootloader`，不含 boot/刷写）。

### 5.3 其它记录在案的风险事实

- 官方已记录一类已知缺陷：`fastboot boot` 送进内存的镜像与「掉电后从活动槽读」不是同一条路径，某些镜像 `fastboot boot` 失败而掉电冷启动成功，且**「板子是否运行 boot 镜像而非槽镜像」在 alioth 上未证实**（`UniXNU/docs/zh/devices/alioth.md:686,725`）。本板无同类观测记录。
- `boot` 分区写入与 AVB：`vbmeta_a/_b` 各 131,072 B，`vbmeta_system_a/_b` 各 131,072 B（§1.2、§2.3）。2026-10-21 的 Magisk 记录里 `partition_written` 只标 `boot_a`，**未见 vbmeta 写入或校验位变化的记录**；本板当前 vbmeta 内容与校验状态未读。
- 生产包自身把「槽位容量与持久载荷落点」列为未确认，并列出 `before_any_install` 五项（重核身份与 GPT、UEFI/native LUN 映射、warm 能力准入、重算 LBA、显式授权），`out/enuma-gop-production-20261114-r5/INSTALL-LAYOUT.json:129-136`。
- 本文 §1 的 GPT 是 **Android/Linux 侧**读数；UEFI（ShengUfs）侧看到的 LUN 映射是否相同**未证明**（`record.md:92-94`、`INSTALL-LAYOUT.json:116` `"native_or_UEFI_mapping_proven": false`）。

---

## 6. 未确定项

1. **LUN1–5 是否有 GPT，及其 CRC**：整套六个 LUN 只导出了 LUN0 的 GPT 头与项数组；LUN4 上 `boot_a`/`vendor_boot_a` 的边界只能从 by-name 与分区容量反推，无项数组证据（`record.md:90`）。
2. **UEFI/native 视角的 LUN 与分区映射**：未经 ShengUfs 读取证明，`INSTALL-LAYOUT.json:116` 明写 `native_or_UEFI_mapping_proven = false`。
3. **`super` 内的逻辑分区清单、`super` 剩余可分配空间、`super` 的 metadata 版本**：从未采集（无 `lpdump` 输出）。
4. **`vendor_boot_a` 的 header 字段值（header 版本、`vendor_ramdisk_addr`、`dtb_addr`、`ramdisk_size`）**：仓库只记录了文件内的偏移（page 4096、ramdisk 2230、dtb 1,613,832 @ 8192；`README.md:151`），没有解出加载地址与窗口，因此「本板 vendor_boot 可用窗口有多大」未定。
5. **ABL 是否接受「boot 镜像带 192 MiB ramdisk」的常态启动**：`fastboot boot` 路径已多次接受同一类镜像，但那是内存启动路径；写入 `boot_a` 后冷启动是否同样接受，未测。
6. **当前 `boot_a` 内容与活动槽**：2026-10-21 时 `boot_a` 回读 `8f40f0c9…`（Magisk 补丁后）、活动槽 `_a`；此后是否被改动、当前槽位，均未知。
7. **当前 `vbmeta` / AVB 状态**（校验是否已 disabled、`flash.locked`、`verifiedbootstate`）：从未 `getvar` 或 `getprop` 采集。
8. **`fastboot flash boot` 在本板落 `_a` 还是 `_b`**：alioth 记为落 `boot_b`，本板无证据。
9. **`boot_a` 分区的 AVB footer 结构**：`boot_a` 头部/尾部是否有 AVB footer、刷写后是否需要同步 vbmeta，未核（`vendor_boot` 侧官方文档提到末尾 64 字节 AVB footer 会被重指向 vbmeta，`guide/boot.md:112-113`；本板未验）。
10. **LUN4/LUN5 上分区容量是否与当前镜像一致地随固件版本变化**：现有容量取自 2026-10-21 的单次采集，之后的固件/OTA 状态未知（§4 第 2 条就是在补这一条）。
11. **`super`/`rescue` 等非槽位分区是否可被 ABL 或 UniXNU 当作启动源**：无任何仓库证据，既不能断言可以，也不能断言不可以。
12. **断电重启后「仍进 UniXNU」的完整链条**：槽内容 + 根卷 UUID 命中 + 载荷自举，三者都还没有任何一次实机组合验证（README 与各诊断文档一致声明不证明持久根卷）。

---

## 附录：本文引用的证据文件

| 文件 | 用途 |
| --- | --- |
| `.cache/android-ufs-identity-gpt-20261114-201917/{record.md,inspect-primary.txt,inspect-backup.txt,gpt-*.bin,gpt-inspect.ps1}` | LUN0 几何、GPT 头/项数组与 CRC、34 项分区 |
| `.cache/live-capture/20261107T141941555586Z/by_name_links.txt` | 123 条 by-name 链接（117 个分区 + 6 个整盘）→ `/dev/block/sdXN` 映射 |
| `.cache/android-sysfs-20261112-113131/derived.json` | userdata 几何与 LUN0 上游约束 |
| `PortingBackup-20261106/legacy-enuma-backups/android-root/20261021T124813939334Z/` | `boot_a/b`、`vendor_boot_a/b`、`vbmeta_a/b` 分区容量与整分区副本哈希；活动槽；2026-10-21 单次 `boot_a` 刷写记录 |
| `out/enuma-gop-production-20261114-r5/{boot.json,payload.json,package.py,INSTALL-LAYOUT.json}` | 当前 `boot.img` 结构与大小、生产包几何与未确认项 |
| `out/enuma-gop-production-20261114-r5/INSTALL-LAYOUT.json:136` | 「boot/vendor_boot 槽容量与持久载荷落点未确认」 |
| `docs/ramblock-host-build.md:171,185-186`、`docs/ufs-reserved-memory-audit.md:65` | `boot.img` 203,505,664 B、header v1、kernel 槽 = shim+gzip(FD)+DTB |
| `proprietary-files.txt:17-23,49` | `xbl_a`/`abl_a`/`dtbo_a`/`imagefv_a`/`vendor_boot_a` 的实机只读取回与哈希 |
| `UniXNU/docs/zh/guide/boot.md:38-51,100-118`、`guide/requirements.md:114`、`devices/alioth.md:666,686,725` | 官方对 `fastboot boot`、boot 镜像构成、payload 进 vendor_boot 三上限、内存启动与槽启动差异的表述（`UniXNU/` 只读） |
| `docs/decisions.md:13-20`、`docs/context-brief.md:7-11,26`、`enuma/AGENTS.md:50` | D2 刷写时机与授权、红线、验收定义 |

状态：`self-checked`（文档内全部数值已与上表文件逐一对照；未上机、未构建、未写设备、未提交）。
