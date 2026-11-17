# 载荷收缩：算术、影响面与将来执行入口

范围：只做算术与影响面分析。**不构建、不打包、不改 `out/` 下任何文件、不碰设备、不改 `UniXNU` 基线、不改 `board.toml`/`dts/`/`configs/`/`porting.toml`**。不给「该选哪档」的建议。

状态：`self-checked`（§1 组成表来自对 `out/ufs-sm8250-policy-20261116-r1/boot.img` 的只读解析与官方 `bootimg.py`/`payload.py` 源码；§2 为纯算术；§3 的 137 B 未定，缺口已写明；本轮未构建、未打包、未写设备）。

---

## 1. `boot.img` 精确组成与「ramdisk 段最大可取值」

### 1.1 实测头字段（只读解析 `out/ufs-sm8250-policy-20261116-r1/boot.img`）

| 偏移 | 字段 | 值 | 说明 |
| --- | --- | --- | --- |
| 0 | magic | `ANDROID!` | |
| 8 | kernel_size | **2,171,783** | gzip(shim+FD) + 追加 DTB |
| 12 | kernel_addr | `0x8000` | = `boot.json:5` `kernel_address` |
| 16 | ramdisk_size | **201,326,592** | = payload.img 全字节 = `payload.json:12` `payload_bytes` |
| 20 | ramdisk_addr | `0x1000000` | 官方默认（`bootimg.py:19` 未覆盖） |
| 24 | second_size | **0** | 官方 v1 路径无 second 段 |
| 32 | tags_addr | `0x1e00000` | = `boot.json:6` |
| 36 | page_size | **4096** | = `bootimg.py:19` `pagesize` |
| 40 | header_version | **1** | = `boot.json:4` |
| 44 | os_version | 0 | |
| 64 | cmdline[512] | 空 | cmdline 走 payload 内 `unixnu.toml`，不进头 |
| 1632 | recovery_dtbo_size（v1） | **0** | ⇒ 无 recovery_dtbo 段 |
| 1636 | recovery_dtbo_offset（v1） | 0 | 同上 |
| 1644 | header_size（v1） | **1648** | 与 AOSP `boot_img_hdr_v1` 大小一致 |

镜像**无尾部 AVB/vbmeta footer**：按官方布局算出的总长与落盘文件长度逐字节相等（§1.2 第 5 行、§1.3）。

### 1.2 逐段字节数与来源

| # | 组成 | 字节数 | 来源 / 断言 | 备注 |
| --- | --- | --- | --- | --- |
| 1 | header 1 页 | **4,096** | 头 `page_size`=4096；`bootimg.py:142,150-151` `start = page` | |
| 2 | kernel 段（页对齐） | **2,174,976** = 531 页 | `kernel_size` 2,171,783 → `ceil(2171783/4096)`=531（`bootimg.py:151`） | 段内尾垫 **3,193** |
| 2a | └ gzip(BootShim 192 B + FD 3,145,728 B) | 1,194,260 | `boot.json:11` `shim_bytes`=192；`boot.json:9` `fd_sha256`；`run_self_check.py:611-616`（解压后 `len(combined)-len(fd) == 192`） | `gzip.compress(..., mtime=0)`，`bootimg.py:104` |
| 2b | └ 追加 DTB（原始字节） | **977,523** | `boot.json:10` `dtb_sha256`；`run_self_check.py:617` `decomp.unused_data == DTB` | 与 `docs/persistent-boot-slot-plan.md:13` 记的 977,523 一致 |
| 3 | ramdisk 段 | **201,326,592** | 头 `ramdisk_size`；`payload.json:12` `payload_bytes`；`run_self_check.py:610` 逐字节相等 | 已是页倍数，尾垫 0 |
| 4 | second 段 | 0 | 头 `second_size`=0 | 不存在 |
| 5 | 尾部 footer/填充 | **0** | 文件长 203,505,664 == 4,096+2,174,976+201,326,592 | 无 AVB footer |
| — | **合计** | **203,505,664** | = `boot.json:8` `image_bytes`；`candidate-manifest.json:39` | |

### 1.3 只随 `size_mib` 变化的量与不变量

固定开销（与 payload 大小无关）：

```
fixed = 页(4096) + kernel 段(531 页 = 2,174,976) = 2,179,072 B (0x214000)
```

**ramdisk 段最大可取值**（使 `boot.img ≤ boot_a` = 201,326,592）：

```
max_ramdisk = 201,326,592 − 2,179,072 = 199,147,520 B = 0xBDEC000 = 189.921875 MiB
```

`payload.img` 的大小恒为 `size_mib × 1,048,576`（`payload.py:81-82` `mformat -T size_mib*2048` 个 512 B 扇区，`payload.py:246`），必为 4096 的整数倍，所以 ramdisk 段**不发生额外页垫**，`boot.img = 2,179,072 + size_mib × 1,048,576`。按整数 MiB 取值，**上限档是 189 MiB**。

前提（必须复算、不能假定）：`fixed` 的 531 页来自 `kernel_size` 2,171,783 落在 (2,170,880, 2,175,976] 这个 5,096 B 窗口内。FD 与 shim 不变时 gzip 长度应不变，但重打包后必须**重读头的 `kernel_size`**，不能沿用 2,171,783。

---

## 2. 候选尺寸（逐档算术）

内容量取 `payload_content_bytes` = **124,596,545**（= `candidate-manifest.json:74`）；95% 门限按官方 `payload.py:248` `content > size*1024*1024*0.95` 即 `content ≤ trunc(size_mib × 1,048,576 × 0.95)`。括号内若改用文档记的 124,596,682，结论不变（见 §3）。

| size_mib | payload.img 字节 | boot.img 字节 | 相对 `boot_a`(201,326,592) 余量 | 内容使用率 | 95% 门限余量 | 同时满足「≤95%」与「装得进槽」 |
| --- | --- | --- | --- | --- | --- | --- |
| 125 | 131,072,000 | 133,251,072 | +68,075,520 | 95.06% | **−78,145**（越界） | **否**（只差 95% 门限） |
| **126** | **132,120,576** (0x7E00000) | **134,299,648** | **+67,026,944** | **94.31%** | **+918,002** | **是**（最小档） |
| 128 | 134,217,728 | 136,396,800 | +64,929,792 | 92.83% | +2,910,296 | 是 |
| 152 | 159,383,552 | 161,562,624 | +39,763,968 | 78.17% | +26,817,829 | 是 |
| 160 | 167,772,160 | 169,951,232 | +31,375,360 | 74.27% | +34,787,007 | 是 |
| 176 | 184,549,376 | 186,728,448 | +14,598,144 | 67.51% | +50,725,362 | 是 |
| 189 | 198,180,864 | 200,359,936 | +966,656 | 62.87% | +63,675,275 | 是（容量上限档） |
| 190 | 199,229,440 | 201,408,512 | **−81,920** | 62.54% | +64,671,423 | **否**（超 `boot_a` 81,920 B） |
| 192（现状） | 201,326,592 | 203,505,664 | **−2,179,072** | 61.89% | +66,663,717 | **否** |

交叉核对：192 MiB 行的 95% 门限余量 **66,663,717** 与 `candidate-manifest.json:75` `payload_guard95_remaining_bytes` 逐字节相同，说明上表公式与已封存 manifest 的计算一致。

边界算术：

- 满足 95% 门限的最小尺寸 = 124,596,545 / 0.95 = 131,154,258 B = 125.078 MiB ⇒ 整数档 **126 MiB**（125 MiB 差 78,145 B）。
- 满足槽容量的最大整数档 = 189 MiB（199,147,520 / 1,048,576 = 189.92）。
- 两头同时成立的可选整数档位：**126 ≤ size_mib ≤ 189**。
- 126 MiB 档位内：卷内剩余 132,120,576 − 124,596,545 = **7,524,031 B**；其中 95% 门限只吃掉 918,002 B，剩下 6,606,029 B 才是「FAT 元数据（引导扇区/保留扇区、两份 FAT、目录项）+ 余量」可用的空间。FAT 元数据开销**不被 95% 门限建模**，必须由打包时的 `mformat`/`mcopy` 实跑与 `mdir` 余量读数确认（见 §6.3 判据 1），本文件不估算其具体值。

---

## 3. `124,596,682` 与 `124,596,545` 的 137 B 差异

### 3.1 可复现的一侧（124,596,545）

`run_self_check.py:601` 定义 `content_bytes = sum(len(v) for v in blobs.values())`，其中 `blobs` 是 `run_self_check.py:566-576` 从 `payload.img` 中 `mtype` 取出的 4 个 FAT 成员。逐项（`out/ufs-sm8250-policy-20261116-r1/self-check/extracted/` 实测目录尺寸）：

| FAT 成员 | 字节 |
| --- | --- |
| `EFI/UniXNU/Payloads/kernel.macho`（= `prelink.macho`，`81cfca98…`） | 124,575,744 |
| `EFI/UniXNU/Payloads/kernel.macho.adt`（`47a07f11…`） | 13,916 |
| `EFI/UniXNU/Payloads/kernel.macho.trustcache`（`750b5d8a…`，脚本 `:501` 断言 6,440） | 6,440 |
| `EFI/UniXNU/unixnu.toml` | 445 |
| **合计** | **124,596,545** |

⇒ 这一侧是**纯文件内容之和**，不含 FAT 引导扇区/保留扇区、FAT 表、目录项、簇尾松弛、页对齐。与 `candidate-manifest.json:74` 和官方 `payload.py:247`（`content = sum(p.stat().st_size for p in stage.rglob('*') if p.is_file())`，同样只数文件）同一定义。

### 3.2 未定的一侧（124,596,682）

- 出处只在文档：`docs/persistent-boot-slot-plan.md:16,324`（明记「采集目录与仓库内均无对应清单文件」）、`README.md:9`、`docs/SESSION-HANDOFF-20261117.md:29,38`。
- 2026-11-17 的采集目录 `.cache/android-slot-probe-20261117/`（51 文件 + `RECORD.md`）**没有任何载荷清单**：`grep` 该目录与整仓脚本均无 `124596682` 的计算代码或数据文件。
- 把 `out/` 下 24 个已解包的 payload 副本按「macho + adt + trustcache + unixnu.toml(+gpuaddon/vroot/scratch-data)」重算，**没有任何一个等于 124,596,682**；最接近的就是 124,596,545（差 +137）。
- 137 不是 512 的整数倍，因此**不可能**是 FAT 扇区/对齐填充或簇尾松弛（那必然是 512 或簇大小的整数倍）；也不能由现有任一 `kernel.macho`（124,575,744 / 124,592,128 / 124,596,224 / 124,604,416 / 124,633,088 / 124,665,856）配现有 adt/trustcache/toml 组合成；若装成 `macho + 20,938`，需要一个 137 B 的额外成员或一个 582 B 的 `unixnu.toml`，两者在仓库中都不存在。

**结论**：`124,596,545` 可由已封存产物完全复现，应作为唯一有效的「载荷内容量」；`124,596,682` **不可复现，按未溯源值处理**。要关闭这一项，只缺一样东西：2026-11-17 采集轮那份清单（不存在），或者对同一 `payload.img` 重跑一次 `mdir -i payload.img -/ ::` + `mtype | wc -c` 并把输出存盘（本轮按硬边界未做）。

**影响**：两个值相差 137 B，都落在同一个最小档（126 MiB，门限余量 918,002 / 917,865 B）与同一个容量上限档（189 MiB），不改变本文任何算术结论。

---

## 4. 改变 / 不变清单

### 4.1 会变（缩 `size_mib` 后必然变化）

| 对象 | 变化点 |
| --- | --- |
| `payload.img` | 字节数 = `size_mib × 1,048,576`；`sha256` 全变（FAT32 引导扇区的总扇区数、FAT 表尺寸、簇链随卷大小变） |
| `boot.img` | 头 offset 16 `ramdisk_size`；总长 = 2,179,072 + payload；`sha256` 全变 |
| `payload.json` | `payload_bytes`、`payload_sha256`（其余 `kernel_sha256`/`payload_kernel_sha256`/`adt_sha256`/`trust_cache_sha256`/`kernel_args`/`data_ramdisk_sha256`/`skip_setup`/`panic_screen` 不变） |
| `boot.json` | `ramdisk_bytes`、`image_bytes`、`image_sha256`（`kernel_sha256`、`header_version`、`kernel_address`、`tags_address`、`fd_sha256`、`dtb_sha256`、`shim_bytes` 不变） |
| `candidate-manifest.json` | `artifacts.payload.img.{sha256,bytes}`、`artifacts.boot.img.{sha256,bytes}`、`package_audit.payload_bytes`、`package_audit.boot_bytes`、`package_audit.payload_guard95_remaining_bytes`（= `trunc(size*0.95) − content`，`run_self_check.py:643`）、`checkpoint.{sha256,bytes}`（指向新 `CHECKPOINT.md`） |
| `CHECKPOINT.md` / 交付说明 | 体积与哈希相关段落、`audit`/`verify` 清单项数 |
| 设备侧可见后果 | 固件记录的 initrd 块设备大小随 `payload.img` 走：历史实机日志 `UNIXNURAMDISK: initrd block device 0xA3FFF000 size 0xC000000`（= 201,326,592，`porting.toml` stage3 记录）；126 MiB 时该值应为 `0x7E00000`（132,120,576） |

### 4.2 不变

- 代码与输入：`self-check/native.macho`（91,733,104，`fd5d3b67…`）、`self-check/prelink.macho`（124,575,744，`81cfca98…`）、`self-check/libShengUfs.a`（474,584，`0bd6f531…`）、`sm8250-policy.patch`（64,465，`de1b57ff…`）、`sourcepin.json`（23,645，`06375cf3…`）——见 `candidate-manifest.json:20-32`。
- 打包输入：FD（3,145,728，`e524988b…`）、DTB（977,523，`42d36a00…`）⇒ gzip(shim+FD) 1,194,260 与 kernel 段 531 页（**须按 §1.3 的前提复读核实**）。
- payload 成员字节：ADT 13,916、trustcache 6,440、`unixnu.toml` 445（含 boot args 原文）、`prelink.macho` 124,575,744。
- 头语义：`header_version` 1、`page_size` 4096、`kernel_addr` 0x8000、`tags_addr` 0x1e00000、`second_size` 0、`shim_bytes` 192。
- `host_tests`、`disassembly_audit`、`root_uuid_dependency`、`boot_args`、`status`/`validation`/`release_allowed` 等 manifest 块——与体积无关。
- 审查侧的**源码零 hunk**：缩载荷不产生任何源码/补丁/链接变化，本仓 tracked 默认 recipe 不变。

---

## 5. 对审查范围的影响（必读）

1. **已审候选的镜像哈希全部失效。** 现在被引用的 `payload.img` `517bda75…`（`candidate-manifest.json:34`）、`boot.img` `6f3e0e92…`（`:38`）、r5 封存包 `fd97c135…`/203,505,664（`AGENTS.md` 与 `README.md` 的多条记录）在缩载后都不再属于任何产物。缩载必须**另建目录重新封存、重新确认审查范围**，不能把新镜像挂到旧封存结论上。
2. **审查范围可以收紧但不能省。** 源码、补丁、`native/prelink/libShengUfs`、ADT/trustcache 都不变，所以普通 reviewer 的范围可缩到「打包参数、头字段、段内容、95% 门限、manifest 绑定」；但最终构建/测试仍须由独立 `verifier` 复跑（§6 判据），本文件不构成任何通过结论。
3. **`fastboot boot` 不校验槽容量，所以缩载只在准备刷写时才必要。** 本板 2026-11-09 起多次以 **203,505,664 B** 镜像 `fastboot boot` 成功（stage3/4/5 与 2026-11-16 GOP r5 均记 203,505,664 B，r5 那次 23:35:20 exit 0、无刷写/无重试；`docs/persistent-boot-slot-plan.md:16,189,208-213` 同结论），该路径与 `boot_a` 的 201,326,592 无关（受下载缓冲/`max-download-size` 约束）。受槽容量约束的只有 `fastboot flash boot_a|boot_b`。⇒ 现有 `fastboot boot` 诊断路线**不需要**为容量缩载；缩载的触发条件是「把载荷写进 `boot` 槽」。

---

## 6. 将来真正缩载时的执行入口与判据

### 6.1 目录与改动点

- 新目录（**不覆盖** `out/ufs-sm8250-policy-20261116-r1/`）：`out/<新候选名>/`，自检脚本从其 `self-check/` 复制过来即可（`run_self_check.py:26` `DELIVERY = SCRIPT_DIR.parent`，复制到新目录后所有相对路径仍落在新目录，`--seal-delivery` 也只写新目录）。
- 唯一参数改动点：**打包树内那份 `board.toml` 副本**的 `[payload] size_mib`（`out/ufs-sm8250-policy-20261116-r1/self-check/packaging/device/board.toml:67` 现为 192；工作树 `board.toml:67` 同为 192——按硬边界本轮两份都不改）。`run_self_check.py:488-497` 已经是「复制 device 目录再就地改副本」的写法，缩载沿用同一位置追加一次替换即可。
- 脚本内必须同步的硬编码：`run_self_check.py:600` `budget_bytes = 192 * 1024 * 1024`，以及 `:602` `assert payload_work_copy.stat().st_size == budget_bytes`。不改这两行，任何非 192 MiB 的档位都会在自检中直接失败。
- 不涉及的：`payload.py`/`bootimg.py`（官方 API，只吃 `size_mib` 与 `--ramdisk`）、`board.toml` 的其余字段、`dts/`、`configs/`、`porting.toml`。

### 6.2 命令（示意，需 WSL 侧解释器与环境，与既有记录一致）

```bash
# 0) 复制自检脚本到新目录（不触碰 r1）
cp -r out/ufs-sm8250-policy-20261116-r1/self-check <新目录>/self-check

# 1) 改两处：<新目录>/self-check/run_self_check.py:600 的 budget_bytes；
#    以及脚本运行时生成的 packaging/device/board.toml 的 [payload] size_mib
#    （在 run_self_check.py 的 board_txt 替换段追加一行 size_mib 替换，不改工作树 board.toml）

# 2) 跑（--seal-delivery 才会写 candidate-manifest.json）
wsl -u root -e /home/wh1stl3/.local/bin/python3 -B \
  <新目录>/self-check/run_self_check.py \
  --work-dir /tmp/<新目录名>-work --seal-delivery
```

### 6.3 验收判据（全部必须成立）

1. `payload.img` 字节数 == `size_mib × 1,048,576`，且 `mdir -i payload.img -/ ::` 报告的剩余空间 > 0（FAT 元数据装得下；95% 门限不覆盖这一项）。
2. `content`（4 个成员和）≤ `trunc(size_mib × 1,048,576 × 0.95)`（官方 `payload.py:248` 的同一条规则）。
3. `boot.img` 字节数 == `2,179,072 + payload 字节数`，且 ≤ 201,326,592。
4. 头字段：`ANDROID!`、`header_version == 1`、`page_size == 4096`、`kernel_size` 与重算的 gzip+DTB 一致（现状 2,171,783）、`ramdisk_size == payload 字节数`、`second_size == 0`、`recovery_dtbo_size == 0`、`header_size == 1648`。
5. `boot.img[ram_at : ram_at+rs]` 与 `payload.img` **逐字节相同**（`run_self_check.py:610` 已有该断言）。
6. kernel 段 gzip 解压后 == 192 B shim + FD，且 `unused_data` == DTB（`run_self_check.py:611-617`）。
7. 记录新旧哈希对照：新的 `payload.img`/`boot.img` 哈希；§4.2 列出的所有「不变」项哈希必须与本文表格逐字符相同。
8. `candidate-manifest.json` 的 `payload_guard95_remaining_bytes` == `trunc(size*0.95) − content`，并与上表对应档位一致。
9. 封存后新 manifest/CHECKPOINT 的哈希另存；旧 `out/ufs-sm8250-policy-20261116-r1/` 原样保留。

### 6.4 未包含（本轮不做，也不推定）

- FAT 元数据的具体字节数（由 mtools 在给定 `-T` 扇区数时的簇大小决定，未在本轮取证；由判据 1 的实跑读数关闭）。
- 缩载后 ABL 冷启动是否接受该镜像（`docs/persistent-boot-slot-plan.md:373` 第 5 项仍开），与容量无关。
- 任何档位选择结论：本文只给算术与影响面。

---

状态：`self-checked`（只读解析一个 `boot.img` 头 + 官方 `bootimg.py`/`payload.py` 源码 + 已封存 manifest/`extracted/` 尺寸；未构建、未打包、未改 `out/`、未写设备、未提交）。

---

## 7. 已落地的参数改动（2026-11-18）

### 7.1 真源与改动点

| 文件:行 | 改前 | 改后 | 说明 |
| --- | --- | --- | --- |
| `board.toml:71` `[payload] size_mib` | `192` | `160` | **唯一生效的真源**：官方 `unixnu build payload` 读 `board.toml [payload] size_mib`（`UniXNU/scripts/unixnu/payload.py:246`，缺省也是 192），95% 门限由它推导（`payload.py:248`），无独立常量 |
| `board.toml:152` `[package] boot_partition_bytes` | 不存在 | `201326592` | 官方可选字段，`unixnu release` 的 `verify` 用它拒绝更大的 `boot.img`（`UniXNU/scripts/unixnu/pipeline.py:61-64`，文档 `docs/zh/porting/packaging.md:81`） |
| `board.toml:67-70` 注释 | — | 新增 | 记录算术、生效时机（下次构建）与「已封存 192 MiB 产物不变」 |

选 **160 MiB** 的理由：`boot.img = 2,179,072 + 167,772,160 = 169,951,232 B`，比 `boot_a/boot_b` 的 201,326,592 B 少 **31,375,360 B**；内容 124,617,025 B 占 74.28%，95% 门限余 34,766,527 B，FAT 卷实剩 42,473,472 B。即同时留出 ADT/trust cache 继续长大与 FAT 元数据的余量，而不是贴着 126 MiB 最小档。

### 7.2 不动的定义点（刻意保留）

- `out/*/self-check/run_self_check.py` 内的 `budget_bytes = 192 * 1024 * 1024`（r1、r2 等）只属于各自封存候选，不是构建真源，未改。
- `scripts/check-enuma-pid1-package.py:72`、`scripts/build-enuma-owner-data.py:414`、`scripts/audit-enuma-production-final-link.py:182` 的 192 MiB 是**候选级预算模型**（作用于各自 `out/` 目录），不是打包输入；改它们只会把旧产物的预算读数改错，保持原值。
- `scripts/prepare_full_payload.py:81`、`scripts/prepare_enuma_userland_payload.py:38` 各自把 `size_mib` 覆写为 96，与本板默认载荷无关。

### 7.3 断言

`boot.img ≤ boot_a 容量` 现在由官方 `verify` 检查（`[package] boot_partition_bytes`），错误信息形如 `boot.img is N bytes; the boot partition holds 201326592`。**未覆盖**的是单独的 `unixnu bootimg` 命令（`bootimg.py` 不看槽容量，它只按 `--ramdisk` 打包）；候选自检脚本自己断言，理由上一轮已确认：`fastboot boot` 不受槽容量约束，只有 `fastboot flash boot` 才需要。该命令在只读基线里，未改。

### 7.4 实测（新候选 `out/ufs-sm8250-policy-20261118-r3/`，2026-11-18）

输入沿用 r2：`prelink.macho` `340997d8…aae75a`（124,596,224 B）、`native.macho` `62a2c185…dbb2fc`、`libShengUfs.a` `372b2d59…058ef`；FD `e524988b…71bf1e`、DTB `42d36a00…82f698`、基线 `693f5d9c`、boot-args `-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-probe=10`。

| 项 | 实测 |
| --- | --- |
| `payload.img` | 167,772,160 B，`0e422cc5…49b158` |
| `boot.img` | 169,951,232 B，`d51a9ac8…ac7623`；相对 `boot_a` 余 31,375,360 B |
| 头字段 | `ANDROID!`、v1、page 4,096、header 1,648、`kernel_size` 2,171,783（531 页）、`ramdisk_size` 167,772,160、`second_size` 0 |
| ramdisk 段 | 与 `payload.img` 逐字节相同 |
| kernel 段 | gzip 解压 = 192 B shim + FD，`unused_data` = DTB |
| 载荷内容 | 124,617,025 B（74.28%），95% 余 34,766,527 B，FAT 实剩 42,473,472 B |
| ADT | 与 r2 除 `/chosen:random-seed` 外逐属性相同；`devicetree.generate()` 每次写 256 B 随机种子，故 ADT/`payload.img`/`boot.img` 哈希每次构建都变 |

命令：`unixnu build payload`（exit 0）、`unixnu bootimg`（exit 0），完整 argv、日志哈希见该目录 `candidate-manifest.json` 与 `CHECKPOINT.md`。

**生效范围**：`board.toml` 改动只影响下一次构建。最后一次 192 MiB 构建是 r2（`payload.img` 201,326,592 B、`boot.img` 203,505,664 B）；r1/r2/r5 的产物字节与哈希在 r3 构建前后逐字节未变。r3 未封存（无 `seal.py`）、未部署、未上机。
