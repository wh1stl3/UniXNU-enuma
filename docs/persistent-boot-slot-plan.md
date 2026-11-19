# 持久启动槽位：离线事实与设备待测清单

范围：只回答「把载荷放进设备、断电重启仍进系统」这条路上**现在能离线确定什么**与**必须靠设备一条只读命令确认什么**。不含选型结论，不含设备操作。全部事实给到文件 + 行号；判不出的一律进 §6。

状态：`self-checked`（§1–§3 为既有材料交叉核对；§4.1 转录 2026-11-17 一轮设备**只读**采集，本文未发起任何设备操作；未构建、未写设备）。

---

## 0. 摘要（只有事实）

1. LUN0（`sda`）的 GPT 有 **34 项**在用（index 0..33），主备头与项数组 CRC 均已重算通过；**`boot`/`vendor_boot` 及 `xbl*`/`abl*`/`tz*`/`hyp*`/`modem*` 全都不在这张表里**。`super`(9,126,805,504 B) 与 `userdata`(242,455,916,544 B) 与 `vbmeta_system_a/_b` 在同一张表里。
2. `boot_a/boot_b` 在 **LUN4（`sde`）**，`vendor_boot_a/_b` 也在 LUN4；`xbl_a` 在 LUN1（`sdb`），`xbl_b` 在 LUN2（`sdc`）。分区名 → 设备节点映射有完整只读采集（123 条 by-name 链接 = 6 个整盘节点 + 117 个分区）。
3. 原厂槽位容量：`boot_a`/`boot_b` = **201,326,592 B**，`vendor_boot_a`/`vendor_boot_b` = **100,663,296 B**。当前 `boot.img` = **203,505,664 B**，比 `boot_a` 大 **2,179,072 B**，比 `vendor_boot` 大约 2 倍。
4. `fastboot boot` 只把镜像送进内存启动一次、不写槽（官方文档 + 本板多次实机记录）；`flash` 才是写入槽位。本板 `boot_a` 在 2026-10-21 被实际刷写过一次（Magisk），回读校验通过、Android 仍可启动。
5. 仓库自身已经把「槽位容量与持久载荷落点」标为未确认：`out/enuma-gop-production-20261114-r5/INSTALL-LAYOUT.json:136`。
6. **容量算术（只有数字，不含选型）**：`boot.img` 203,505,664 B 仍比 `boot_a` 的 201,326,592 B 大 **2,179,072 B**；但 `boot.img` 的 ramdisk 槽是 **192 MiB 圆形分配**（`payload.img` = 201,326,592 B），2026-11-17 采集方给出的载荷内容合计为 **124,596,682 B（约 118.8 MiB）**。算术：124,596,682 + 2,179,072 = 126,775,754 ≤ 201,326,592，即把 ramdisk 从 192 MiB 圆形分配收缩到实际内容量级后，`boot.img` 总体积落进 `boot_a` 的 201,326,592 B 在算术上可行（内容合计值的出处见 §4.1 注 1）。
7. **前提：Android `/data` 是 FBE 加密 f2fs**：`/proc/mounts` 为 `/dev/block/dm-40 /data f2fs`，`ro.crypto.state=encrypted`、`ro.crypto.type=file`；raw `userdata` 首块偏移 1024 既非 ext4 也非 f2fs 明文 magic（§4.1）。**写入自有根卷布局会覆盖 Android `/data`**，按 D2（`docs/decisions.md:18`）需用户确认数据可弃；该确认已于 2026-11-17 记录（`docs/decisions.md` D7），**不等于任何刷写授权**。

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

控制器 `1d84000.ufshc`、驱动 `ufshcd-qcom`、`proc_name=ufshcd`；六盘同型号 `KLUEG8UHDC-B0E1`（SAMSUNG，rev 0200）。记录另注明：**LUN1–5 未导出，其上是否有 GPT 及 CRC 状态未核**（`record.md:90`）——2026-11-17 已补 LUN4（`sde`，有完整 GPT，见 §4.1、§6-1），LUN1/LUN2/LUN3/LUN5 仍未核。

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
| 断电重启后 | 回原槽内容（D2：`docs/decisions.md:15`「设备自行重启会回 Android」；该句已按 2026-11-19 实测加注——warm/PSCI reset 回 fastboot，冷启动未测，见 `docs/enuma-fastboot-entry-and-pmgr-write.md`） | 走该槽内容 |

参考（**别板**，不可当本板结论）：alioth 记录 `fastboot boot` 不写槽、`flash` 落到 `boot_b`（`UniXNU/docs/zh/devices/alioth.md:666`）。

### 3.3 候选位置：只有容量与代价，不做选型

| 候选 | 容量 | 当前镜像是否装得下 | 写入代价 / 不可逆性 |
| --- | --- | --- | --- |
| `boot_a`（sde12） | 201,326,592 B | **否**（差 2,179,072 B） | 覆盖 Android 启动镜像；已有整分区 stock 备份 `759eaf09…`（外部备份）可回写恢复；A/B 另一槽保留 |
| `boot_b`（sde37） | 201,326,592 B | **否**（同上） | 同上；覆盖的是未激活槽，但 `boot_b` 的现有内容 `ac3bd652…` 也已有备份 |
| `vendor_boot_a`（sde25） | 100,663,296 B | **否**（约 2 倍差） | 覆盖原厂 vendor_boot（含 4 个 SoC 基座 DTB，`proprietary-files.txt:49`、`README.md:151`）；已有备份 `3da202d0…` |
| `vendor_boot_b`（sde49） | 100,663,296 B | **否** | 同上；备份 `6e733d43…` |
| `super`（sda29）内的逻辑分区 | 分区总量 9,126,805,504 B | 逻辑分区清单已知（§4.1）：7 个逻辑分区，**无 `boot`/`vendor_boot`** | 需改 `super` 的 dynamic partition 元数据（写操作），无备份；`ABL` 是否从 super 逻辑分区取启动镜像**无任何仓库证据** |
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
| 5 | adb+root | `adb -s <serial> shell "su -c 'dd if=/dev/block/by-name/vendor_boot_a bs=1 count=8 2>/dev/null'"` | 确认 vendor_boot 槽当前镜像格式 | 原始预期（历史，**2026-11-17 实测推翻**）：`ANDROID!` 或其它 → **实测 `VNDRBOOT`（header v3）** | 已实测**不是** `ANDROID!`：`VNDRBOOT` + header_version 3，按 boot header v3 解析（§4.1、§6-4）；写入前须按 v3 布局与已解出的窗口核算 |
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

执行情况（2026-11-17）：#1–#8 已在 adb 侧只读执行，结果见 §4.1；#9–#15 的 fastboot 侧 `getvar` **未执行**（当时设备在 adb 侧），故 §6 的 fastboot 相关项仍未关。

### 4.1 设备侧采集结果（2026-11-17）

一轮**只读**采集（`ls`/`cat`/`getprop`/`blockdev --getsize64`/`lpdump`/`dd if=…` 到 stdout），零写入、未 `reboot`、未 `flash`/`erase`/`format`/`dd of=`、未改任何分区或属性、未操作另一台 nuwa。原始材料：`enuma` 工作区根下的 **`.cache/android-slot-probe-20261117/`**（51 个文件 + `RECORD.md`，**不在本仓 `UniXNU-enuma/` 内**，路径相对本文件为 `../../.cache/android-slot-probe-20261117/`）。本节只转录结论并对可复核项抽查，不复述命令；命令、退出码、逐文件 SHA-256 见该目录 `RECORD.md`。下文 `@<file>` 指该目录下的文件名。

**A. 识别与环境**

| 项 | 实测值 | 文件 |
| --- | --- | --- |
| 型号（唯一命中） | `getprop ro.product.device` = `enuma`；`adb devices -l` → `product:enuma model:M2105K81C device:enuma` | `@00-product-device.txt`、`RECORD.md:3` |
| `ro.boot.hardware` | **`qcom`**（不是 `kona`）⇒ 本板机型识别只能靠 `ro.product.device` | `@00-boot-hardware.txt` |
| 活动槽 | `ro.boot.slot_suffix` = **`_a`**（两次，值一致）；`ro.boot.slot` **为空** | `@00-slot-suffix.txt`、`@09-slot-suffix.txt`、`@09-slot.txt` |
| shell / root | shell `uid=2000`；`su -c 'id'` → `uid=0(root) … context=u:r:magisk:s0` | `@00-id-uid.txt`、`@00-su-id.txt` |

**B. by-name 映射与槽容量**

| 项 | 实测值 | 文件 |
| --- | --- | --- |
| `ls -l /dev/block/by-name` | **123 条链接 = 6 个整盘节点 + 117 个分区**；分组 sda 34 / sdb 2 / sdc 2 / sdd 4 / sde 65 / sdf 10 | `@01-by-name.txt`、`@03-proc-partitions.txt` |
| 启动相关节点 | `boot_a→sde12`、`boot_b→sde37`、`vendor_boot_a→sde25`、`vendor_boot_b→sde49`、`vbmeta_a→sde17`、`vbmeta_b→sde42`、`dtbo_a→sde18`、`dtbo_b→sde43`、`vbmeta_system_a→sda30`、`vbmeta_system_b→sda31` | `@10-by-name-boot-vbmeta-dtbo.txt`（`@01-by-name.txt` 同值） |
| 槽容量 | `boot_a`/`boot_b` = **201,326,592 B**；`vendor_boot_a`/`vendor_boot_b` = **100,663,296 B**（与 §2.3 的 2026-10-21 记录**逐字节一致**） | `@02-boot_a-size.txt`、`@02-boot_b-size.txt`、`@02-vendor_boot_a-size.txt`、`@02-vendor_boot_b-size.txt` |
| `super` / `userdata` 容量 | 9,126,805,504 B / 242,455,916,544 B（与 §1.2 GPT 一致） | `@08-super-size.txt`、`@08-userdata-size.txt` |

**C. LUN4（`sde`）有完整 GPT**

| 项 | 实测值 | 文件 |
| --- | --- | --- |
| 头 | signature `EFI PART`；`header_size` 92；`current_lba` 1；`backup_lba` 557,055；`first_usable_lba` 6；`last_usable_lba` 557,050；`entries_lba` 2 | `@04-lun4-gpt-lba1-head.txt`、`@04-lun4-gpt-lba1-fullhead.txt`、`@04d-lun4-gpt-inspect.txt` |
| CRC | `header_crc32` = **0xFFE04383**、`entries_crc32` = **0x56C9EAFF**，**本地重算均相符** | `@04d-lun4-gpt-inspect.txt`（本地 `@gpt-inspect.ps1`） |
| 项数组 | 96 项槽 × 128 B = 12,288 B（LBA2–4）；**非空 66** = 65 个实分区 + Qualcomm 占位 `last_parti`（idx 65，LBA 525,470–557,050） | `@04b-lun4-gpt-entries-lba2-4.bin`、`@04d-lun4-gpt-inspect.txt` |
| 盘总 | 557,056 × 4096 = **2,281,701,376 B**；`/proc/partitions` 中 `sde` = 2,228,224 KiB（同值） | `@04d-lun4-gpt-inspect.txt`、`@03-proc-partitions.txt` |
| `boot_a` extent | LBA **145,030–194,181**（49,152 扇区 = 201,326,592 B） | `@04d-lun4-gpt-inspect.txt` |
| `boot_b` extent | LBA 393,654–442,805（同上容量） | 同上 |
| `vendor_boot_a` extent | LBA **224,054–248,629**（24,576 扇区 = 100,663,296 B） | 同上 |
| `vendor_boot_b` extent | LBA 460,390–484,965（同上容量） | 同上 |
| 与 by-name 对齐 | GPT idx N ↔ `sde(N+1)`，65 个实分区一一对应（含 idx 48 `vendor_boot_b`↔`sde49`、idx 49 `imagefv_b`↔`sde50`） | `@04d-lun4-gpt-inspect.txt`、`@01-by-name.txt` |

**D. 槽内当前内容**

| 项 | 实测值 | 文件 |
| --- | --- | --- |
| `boot_a` 头 8 B | `ANDROID!`（标准 boot 镜像头） | `@06-boot_a-head8.txt` |
| `vendor_boot_a` 头 | `VNDRBOOT`；`header_version` **3**、`header_size` **2112**、`page_size` 4096、`kernel_addr` **0x00008000**、`ramdisk_addr` **0x01000000**、`vendor_ramdisk_size` **2230**、`tags_addr` **0x00000100**、`name` 空、`dtb_addr` **0x01F00000**、`dtb_size` **1,613,832**、`cmdline` 347 B（**无设备标识**，仅两处 `0x` 常量） | `@14-vendor_boot_a-head2048.bin`、`@14b-vendor_boot_a-head4096.bin`、`@16-analysis.txt` |
| 按页推得镜像实占 | 4,096（头 1 页）+ 4,096（ramdisk 1 页）+ 395 × 4,096（`dtb_size` 1,613,832 B 向上取整）= **1,626,112 B**（远小于分区 100,663,296 B） | `@16-analysis.txt` |
| 与本地 stock 比对 | 设备前 4,096 B 与 `UniXNU-enuma/.cache/firmware/vendor_boot_a.img` 前 4,096 B **逐字节相同**（两侧 SHA-256 均 `6c8dd864…69f0`）；**只证首 4,096 B，不证整分区** | `@16-analysis.txt`、`@14b-vendor_boot_a-head4096.txt` |
| `boot_a` 前 8 MiB SHA-256 | `94a6e4723271dfd335ce1d3060f305ac16f36bfa2641074748001d7603a84d46` | `@15-boot_a-first8MiB-sha256.txt` |

**E. `super`（`super` 内无 boot/vendor_boot）**

| 项 | 实测值 | 文件 |
| --- | --- | --- |
| metadata | version **10.2**、size 2,244 B、max size 65,536 B、slot count **3**、header flags **`virtual_ab_device`** | `@07d-lpdump-full.txt`、`@07-lpdump-super.txt` |
| 逻辑分区 | **7 个**：`system_a`、`system_ext_a`、`product_a`、`vendor_a`、`odm_a`、`mi_ext_a`、`system_a-cow` | `@07d-lpdump-full.txt` |
| 组上限 | `qti_dynamic_partitions_a` = **9,122,611,200 B**；`default` = 0；`cow` = 0 | 同上 |
| block device 表 | `super` first sector 2,048、size 9,126,805,504 B | 同上 |
| 是否有 `boot`/`vendor_boot` 逻辑分区 | **无** | 同上 |

**F. AVB 与 `userdata`**

| 项 | 实测值 | 文件 |
| --- | --- | --- |
| AVB / 锁 | `ro.boot.verifiedbootstate` = **`orange`**、`ro.boot.flash.locked` = **`0`**（已解锁、校验放宽） | `@09-verifiedbootstate.txt`、`@09-flash-locked.txt` |
| `userdata` raw 首块 | offset 1024：`u16 LE` = 0xE90E（≠ ext4 `0xEF53`）、`u32 LE` = 0x47D7E90E（≠ f2fs `0xF2F52010`）⇒ 按该判据为「其它/未知」 | `@12-userdata-first64.txt`、`@12-userdata-first64-hex.txt`、`@13-userdata-first2048.bin`、`@16-analysis.txt` |
| 挂载态 | `/dev/block/dm-40 /data f2fs`（另多个 `/data/*` 挂载同源）；`ro.crypto.state` = **`encrypted`**、`ro.crypto.type` = **`file`**（FBE；dm 表未读，映射层级未证） | `@13b-userdata-mount.txt`、`@13c-crypto-state.txt`、`@13d-crypto-type.txt` |

**注 1**：§0 第 6 条用的载荷内容合计 **124,596,682 B** 由 2026-11-17 采集轮在汇报中给出；**上述采集目录与仓库内均无对应清单文件**。本文只按该值做算术，未自行重算，也未据此做任何选型判断。

**注 2**：`ro.boot.hardware` = `qcom` 不改变 `docs/context-brief.md`「设备访问」的识别规则（本板仍按 `ro.product.device` = `enuma` 唯一识别），但说明 `ro.boot.hardware` 在本板不含 SoC 名，不能用于机型判定。

**注 3**：本轮的 fastboot 侧 `getvar` 全部未执行（设备停在 adb 侧）；`RECORD.md:46-48` 明记该跳过，且本机 `fastboot devices` 当时只列出无名条目，未对其下发命令。

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
- `boot` 分区写入与 AVB：`vbmeta_a/_b` 各 131,072 B，`vbmeta_system_a/_b` 各 131,072 B（§1.2、§2.3）。2026-10-21 的 Magisk 记录里 `partition_written` 只标 `boot_a`，**未见 vbmeta 写入或校验位变化的记录**；`vbmeta_*` 分区内容仍未读（AVB/锁状态已实测 `orange` / `flash.locked=0`，见 §4.1 F、§6-7）。
- 生产包自身把「槽位容量与持久载荷落点」列为未确认，并列出 `before_any_install` 五项（重核身份与 GPT、UEFI/native LUN 映射、warm 能力准入、重算 LBA、显式授权），`out/enuma-gop-production-20261114-r5/INSTALL-LAYOUT.json:129-136`。
- 本文 §1 的 GPT 是 **Android/Linux 侧**读数；UEFI（ShengUfs）侧看到的 LUN 映射是否相同**未证明**（`record.md:92-94`、`INSTALL-LAYOUT.json:116` `"native_or_UEFI_mapping_proven": false`）。
- `userdata` 当前是 Android 的 **FBE 加密 f2fs**（`/dev/block/dm-40 /data f2fs`、`ro.crypto.state=encrypted`、`ro.crypto.type=file`，§4.1 F），raw 首块不是明文 ext4/f2fs magic ⇒ **写入自有根卷布局即覆盖 Android 全部 `/data` 用户数据**，无本地恢复副本。用户已于 2026-11-17 确认数据可弃（`docs/decisions.md` D7），该确认**只是 D2 的一个前置**，不是刷写授权。

---

## 6. 未确定项

状态标记：**[已关闭]** = 已被 2026-11-17 设备只读采集补齐；**[部分关闭]** = 部分已证、剩余已写明；**[仍开]** = 未采集。

1. **[部分关闭] LUN1–5 是否有 GPT，及其 CRC**：LUN4（`sde`）**已有完整 GPT**——主头 `header_crc32` 0xFFE04383、项数组 `entries_crc32` 0x56C9EAFF 均本地重算相符，96 项槽 / 非空 66（65 分区 + `last_parti`），`boot_a`（LBA 145,030–194,181）与 `vendor_boot_a`（224,054–248,629）extent 与 `blockdev` 容量吻合（§4.1 C）。**剩余**：LUN1（`sdb`）、LUN2（`sdc`）、LUN3（`sdd`）、LUN5（`sdf`）仍只知 by-name 与 `/proc/partitions` 边界，GPT 与 CRC 未读（`record.md:90` 的范围据此收窄）。
2. **[仍开] UEFI/native 视角的 LUN 与分区映射**：本轮全部读数来自 Android/Linux 侧；`INSTALL-LAYOUT.json:116` 仍为 `native_or_UEFI_mapping_proven = false`，未经 ShengUfs 读取证明。
3. **[已关闭] `super` 内的逻辑分区清单、剩余可分配空间、metadata 版本**：`lpdump` 只读全量（185 行）给出 metadata version **10.2**、metadata size 2,244 B / max 65,536 B、slot count **3**、header flags **`virtual_ab_device`**；逻辑分区 **7 个**（`system_a`、`system_ext_a`、`product_a`、`vendor_a`、`odm_a`、`mi_ext_a`、`system_a-cow`），**无 `boot`/`vendor_boot`**；组上限 `qti_dynamic_partitions_a` = **9,122,611,200 B**，`default`/`cow` = 0；block device 表 `super` first sector 2,048、size 9,126,805,504 B（§4.1 E）。原「从未采集」作废。
4. **[已关闭] `vendor_boot_a` 的 header 字段值**：`VNDRBOOT` / `header_version` **3** / `header_size` **2112** / `page_size` 4096 / `kernel_addr` **0x00008000** / `ramdisk_addr` **0x01000000** / `vendor_ramdisk_size` **2230** / `tags_addr` **0x00000100** / `name` 空 / `dtb_addr` **0x01F00000** / `dtb_size` **1,613,832** / `cmdline` 347 B；镜像按页实占 **1,626,112 B**（§4.1 D）。⇒ 「加载地址与窗口未定」不再成立：ramdisk 与 dtb 的地址与页边界已实测。
5. **[仍开] ABL 是否接受「boot 镜像带 192 MiB ramdisk」的常态启动**：`fastboot boot` 路径已多次接受同类镜像，但写入槽后冷启动未测；本轮无任何 fastboot 侧动作。
6. **[部分关闭] 当前 `boot_a` 内容身份与活动槽**：活动槽已实测 **`_a`**（`@00-slot-suffix.txt`、`@09-slot-suffix.txt`）；`boot_a` 头 8 B = `ANDROID!`，前 8 MiB SHA-256 = `94a6e472…a84d46`。**但**既有记录 `8f40f0c9…`/`759eaf09…` 是**整分区 201,326,592 B** 的哈希，范围不同**不可直接比对**，本机也无 `boot_a.img` 整分区副本 ⇒ 是否仍是 2026-10-21 的镜像**未定**；已确定的是「标准 boot 头 + 前 8 MiB 指纹」，只能作为后续比对的锚点（`@15-boot_a-first8MiB-sha256.txt`、`@16-analysis.txt`）。
7. **[已关闭] 当前 `vbmeta` / AVB 状态**：`ro.boot.verifiedbootstate` = **`orange`**、`ro.boot.flash.locked` = **`0`**（已解锁、校验放宽；`@09-verifiedbootstate.txt`、`@09-flash-locked.txt`）。**仍注**：`vbmeta_a/_b` 的实际内容与校验位未读，刷写后是否需要同步 vbmeta 仍归 §6-9。
8. **[仍开] `fastboot flash boot` 在本板落 `_a` 还是 `_b`**：fastboot 侧 `getvar`/flash 本轮均未执行；alioth 记落 `boot_b`，本板无证据。
9. **[仍开] `boot_a` 分区的 AVB footer 结构**：头/尾是否带 AVB footer、刷写后是否需同步 vbmeta 未核（官方文档提到 `vendor_boot` 末尾 64 B AVB footer 会被重指向 vbmeta，`guide/boot.md:112-113`；本板未验）。本轮只读了头 8 B 与前 8 MiB。
10. **[已关闭] 槽位容量是否随固件变化（`boot_a`/`boot_b`/`vendor_boot_a`/`vendor_boot_b`）**：2026-11-17 复测 `boot_a`/`boot_b` = 201,326,592 B、`vendor_boot_a`/`vendor_boot_b` = 100,663,296 B，与 2026-10-21 记录**逐字节一致**；LUN4 盘总 557,056 × 4096 = 2,281,701,376 B 与 `/proc/partitions` 一致，且 GPT extent 与 `blockdev` 吻合（§4.1 B、C）。⇒ §4 第 2 条已完成一次。**注**：LUN5（`sdf`）的 10 个分区容量本轮未单独读取，不在本项范围内。
11. **[仍开] `super`/`rescue` 等非槽位分区是否可被 ABL 或 UniXNU 当作启动源**：仍无任何仓库证据；本轮只证 `super` 内**没有** `boot`/`vendor_boot` 逻辑分区。
12. **[仍开] 断电重启后「仍进 UniXNU」的完整链条**：槽内容 + 根卷 UUID 命中 + 载荷自举，三者仍无任何一次实机组合验证；本轮为纯只读采集，不产生运行时证据。

---

## 附录：本文引用的证据文件

| 文件 | 用途 |
| --- | --- |
| `enuma/.cache/android-slot-probe-20261117/`（51 个文件 + `RECORD.md`，相对本文件 `../../.cache/android-slot-probe-20261117/`，**不在本仓内**） | §4.1 全部设备侧只读采集：识别、by-name、`blockdev` 容量、LUN4 GPT 头/项数组与 CRC、`vendor_boot_a` 头、`lpdump`、AVB、`userdata` 首块与挂载态；`RECORD.md` 含命令/退出码/逐文件 SHA-256 |
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
| `docs/decisions.md` D7（2026-11-17） | 用户确认 enuma Android `/data` 数据可弃（D2 前置之一，非刷写授权） |

状态：`self-checked`（§1–§3 数值与上表文件逐一对照；§4.1 数值取自 2026-11-17 只读采集，本文件作者对 by-name 计数、槽容量、GPT extent、`lpdump` 组上限等项做了抽查复核；§0 第 6 条的内容合计值无仓库内文件，见 §4.1 注 1。本轮未构建、未写设备、无 fastboot 动作）。
