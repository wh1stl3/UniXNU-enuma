# enuma Data store `>2GiB` 阈值与绕行事实

状态：**`self-checked`**（纯离线只读取证：源码、`out/` 既有产物、基线 `UniXNU` 只读树；未上机，未编译，未做独立复核）
整理日期：2026-11-17
范围：`out/owner-data-query-20261113-r3/source-ram/`（RamBlock 消费者）、`out/ufs-sm8250-policy-20261116-r1/source/` 与 `self-check/merged-source/`（ShengUfs 提供者）、基线 `UniXNU@693f5d9c`（只读）、`out/production-complete-20261114-r1/INSTALL-LAYOUT.json`（几何数字）
本文只列事实与未确定项，不含安全判定、方案选型或推荐。

---

## 0. 取证命令与退出码

全部为只读命令，工作目录 `D:/Code/PortingiOS`；无设备访问、无构建。

| # | 命令 | 退出码 | 用途 |
| --- | --- | --- | --- |
| C1 | `Get-FileHash UniXNU/drivers/RamBlock/NativeRamBlock.cpp, enuma/UniXNU-enuma/out/owner-data-query-20261113-r3/source-ram/NativeRamBlock.cpp -Algorithm SHA256` | 0 | 两者同为 `B8BE57091A0657C41FB12D22C70E4821096209E84533E1602E69E9FAADBD8D59`、24778 B，**行号可同时引用基线与 `out/` 副本** |
| C2 | 四则运算（`pwsh`，输入取自 C3 的 JSON） | 0 | §3 的 pages/bitmap/blocks/store_start/gap 复算 |
| C3 | `Get-Content out/production-complete-20261114-r1/INSTALL-LAYOUT.json` | 0 | 3 GiB Data、store 窗口、root 镜像、userdata 区间与几何（历史离线快照，非当前 GPT 读数） |
| C4 | `Select-String … -Pattern '0x80000000\|isBig\|direct = \|attachStore'` | 0 | §1、§2 代码点定位 |
| C5 | `Select-String patches/xnu/offline-owner-systemos-mount.patch` | 0 | XNU 侧调用方 `native_owner_data_prepare` 的尺寸判据（§1.1 第 5、6 行） |
| C6 | `Get-Item out/data-seed-transfer-20261113/received-43379610501/data.dbr` | 0 | packed seed 实体大小 1171584 B |
| C7 | `Get-Content UniXNU/scripts/seed-data-grow.py`、`UniXNU/drivers/DarwinBoot/Test/packed_ramdisk.py`、`UniXNU-enuma/scripts/ci/data_seed_macos.py` | 0 | §4.1 生成 ≤2 GiB seed 所需的输入与现有工具边界 |

---

## 1. 精确阈值与拒绝位置

### 1.1 阈值就是 `0x80000000` 字节 = 2,147,483,648 B（2 GiB）

同一个常量出现在 6 个代码点，**判定对象各不相同**：

| # | 位置 | 原文（逐字） | 判定对象 | 命中后果 |
| --- | --- | --- | --- | --- |
| 1 | `NativeRamBlock.cpp:57-59`（注释） | `// A disk above 2 GiB keeps only the nonzero pages of its seed (SeedDisk.h), in memory proportional to the content, and is served by the` / `// direct (store-backed) path alone: it needs the persistent store open read-write, or its requests fail.` | 设计说明 | 说明 2 GiB 以上只走 direct 路径 |
| 2 | `NativeRamBlock.cpp:211` | `if (!bytes \|\| bytes > 0x80000000 \|\| (physical & 4095) \|\| (!packedInput && (bytes & 4095)) \|\|` | `/chosen/memory-map` 里 `RAMDisk`/`PackedRAMDisk` 描述符的**长度字段**（packed seed blob 字节数，或 dense RAMDisk 字节数） | `start()` 返回 `false`：设备不注册、`/dev` 无节点 |
| 3 | `NativeRamBlock.cpp:219` | `if(logical>0x80000000ULL){` | packed seed 头里的**逻辑磁盘字节数** `size`（`ramPackedLayout` 输出） | 走 `isBig`/`SeedDisk` 路径（不是拒绝） |
| 4 | `SeedDisk.h:75` | `if (d.bytes <= 0x80000000ULL) {` | 同一逻辑磁盘字节数 | 决定 seed identity **哈希格式**（≤2 GiB 全字节哈希；>2 GiB 走 `SHNGSEED2`+size+非零页索引，`:83-93`） |
| 5 | `UniXNU/patches/xnu/offline-owner-systemos-mount.patch:214` | `+	if (!size \|\| size > UINT64_C(0x10000000000) \|\| (size & 4095)) goto done;` | typed provider（`native_ram_block_volume_seed`）回报的逻辑尺寸 | 上限 1 TiB；注释 `:213` 明说 `The typed provider's disk may be far larger than 2 GiB …` |
| 6 | 同上 `:218` | `+	    !size \|\| size > UINT64_C(0x80000000) \|\| (base & 4095) \|\| (size & 4095)) goto done;` | **dense `md` 路径**（`mdevgetrange`）的尺寸 | 仅在不走 typed provider 的 `#else` 分支生效 |

结论（事实层）：对**本板当前配置**（`CONFIG_XNU_NATIVE_RAM_BLOCK=y`、typed provider 可用），XNU 侧的 2 GiB 上限不生效（XNU 放行到 1 TiB），2 GiB 边界只出现在 RamBlock 内部（第 3、4 点）。第 2 点作用在 **blob 长度**上：本板 packed seed 实体 `data.dbr` = 1,171,584 B（C6），远低于 2 GiB；`ramPackedLayout`（`SparseDisk.h:14`）另有更严的 `n>0x10000000`（256 MiB）上限。

### 1.2 判定用的是什么

- 用的是**逻辑磁盘字节数**（seed 头的 `size`），不是块数、不是 LBA、不是物理地址。
- 边界是开区间上界：`logical == 0x80000000`（正好 2 GiB）仍走 `≤2 GiB` 分支；`0x80000001` 起走 `isBig`。
- `capacity`（512 B 块数）在 `NativeRamBlock.cpp:233` 由 `logical/512` 得到，与阈值判定无关；`reportMaxValidBlock` 返回 `capacity - 1`（`:176`）。
- 0x80000000 在这里**不是内存地址**：与 §3 的 DRAM 基址 `0x80000000` 是同一数值但无关。

### 1.3 ">2GiB 被拒"实际发生在写路径，不是尺寸检查

`isBig` 且 `direct == false` 时，`doAsyncReadWrite` 只放行读：

```c
269:  if(isBig && !direct) {
270:    // Before the store is attached (APFS probes the disk for its volume UUID long before the kernel asks for the Data volume, which is what
271:    // attaches the store) a disk this size is read from its seed alone; it has no volatile mode, so writes wait.
272:    if(buffer->getDirection()==kIODirectionIn) {
...
293:    IOLockUnlock(gate);return kIOReturnNotReady;
```

即：>2 GiB 的 Data 盘**读得到、写不了**（返回 `kIOReturnNotReady`），没有 RAM 易失写入回退。`scripts/build-enuma-owner-data.py:428` 把这一点记成字符串 `'NativeRamBlock >2GiB requires direct RW store; no volatile write fallback'`；`INSTALL-LAYOUT.json:52` 记为 `"blank_store_normal_boot": "refuses >2GiB Data without direct store, no volatile fallback"`。

补充：≤2 GiB 的盘可写（`ramSparseIO` 写入按页分配的 RAM，`SparseDisk.h:44-60`），但重启即丢——这是"有易失写、无持久"的分支。

---

## 2. `isBig` / `direct` / `SeedDisk` 的实际语义与调用路径

### 2.1 `SeedDisk`（`SeedDisk.h:10-22`）

```c
10: struct SeedDisk {
11:   uint64_t bytes = 0, count = 0, capacity = 0, resident = 0;
12:   uint64_t *index = nullptr;       // capacity entries, ascending, count used
13:   uint8_t **page = nullptr;
14:   const uint8_t *find(uint64_t i) const { … 二分查找 index … return lo < count && index[lo] == i ? page[lo] : nullptr; }
```

只保存 seed 的**非零页**：`count/resident` 随内容增长，与磁盘容量无关（`:3-5` 注释：`a disk of hundreds of GiB costs memory in proportion to its content (a packed seed holds a few thousand pages), not to its size`）。`big.bytes` 是逻辑容量，`big.capacity` 是 `seedCountNonzero()` 数出的非零页数（`NativeRamBlock.cpp:221-225`）。

### 2.2 `isBig`

- 置位点唯一：`NativeRamBlock.cpp:219-226`（`logical>0x80000000ULL` → `big.bytes=logical; big.capacity=nonzero; … isBig=true; sparse.bytes=logical;`）。
- 副作用：`memory=nullptr`（`:239`）——>2 GiB 时不再持有连续物理视图；`native_ram_block_sparse=1`（`:250`）；resident 统计取 `big.resident`（`:251`、`:336`）；`free()` 走 `:361-366`。
- `seedIdentity()`（`SeedDisk.h:72-95`）在 `isBig` 时按 `SHNGSEED2` + size + (index,page) 计算 `seedHash`（`NativeRamBlock.cpp:236-239`），与 ≤2 GiB 的全字节哈希（`:241-246`）**不是同一格式**。

### 2.3 `direct`

- 只有两处置真，都在 `attachStore()` 内：

```c
119:          direct = mode == 2;                 // Open::Fresh（请求了 sheng-data-reset，且是首次）
122:          direct = true;                      // mode == 2 且 Open::Resumed
```

- 语义（`:66-68` 注释）：`Direct mode (the store is open read-write): changed pages live in the store window only, never in RAM; reads of them go to the window. A failed store write stops all further writes (a page the system was told is written must be on the medium).`
- 失败即锁死写：`:310` `if(write && directFailed)actual=0;`，`:313-315` 置 `native_data_persist_state=5`。
- `direct` 为真后 I/O 走 `directDiskIO`（`DirectDisk.h:16-67`）：页位图命中读 store、否则读 seed；写入 `ov.writeRun()` 先落介质再置位。

### 2.4 `attachStore()` 的调用路径

```c
83:  void attachStore() {
84:    if (!gate) return;
86:    if (storeAttached) { IOLockUnlock(gate); return; }
88:    unsigned mode = &native_ufs_store_mode ? native_ufs_store_mode() : 0;
89:    if (mode && (sparse.pages || isBig) && &native_ufs_store_open && &native_ufs_store_read && &native_ufs_store_write &&
90:        &native_ufs_store_sync && &native_ufs_store_gpt_check) {
91:      uint64_t pages = (isBig ? big.bytes : sparse.bytes) / 4096, first = 0;
95:      if (!native_ufs_store_open(persist::windowBlocks(pages), &first, &why)) {
96:        native_data_persist_state = 4;
97:        IOLog("NativeRamBlock: persistent store refused: %s\n", why);
```

唯一调用点是 `selectVolumeSeed()` 的 provider 遍历内：

```c
410:    unsigned depth = 0;
411:    for (IOService *provider = media; provider && depth++ < 64; provider = provider->getProvider()) {
412:      NativeRamBlock *ram = OSDynamicCast(NativeRamBlock, provider);
413:      if (!ram) continue;
414:      ram->attachStore();
415:      if (!ram->seedInfo(&base,&bytes,hash)) continue;
```

`selectVolumeSeed` 由 `native_ram_block_volume_device()`（`:432-434`）与 `native_ram_block_volume_seed()`（`:456-461`）导出；XNU 侧调用者是 `native_owner_data_prepare()`：`UniXNU/patches/xnu/offline-owner-systemos-mount.patch:209-214` 以 `XNU_OWNER_DATA_VOLUME_UUID` 查卷，拿到 `device_path` 后 `mount(p, …)` 到 `/private/var`。所以 **`attachStore()` 在"内核按 UUID 找 Data 卷"这一刻触发**，早于 APFS 挂载；APFS 自己的探测读（`:270-271` 注释）发生在 store 挂上之前，只走 seed。

### 2.5 `direct == false` 的完整条件（静态穷举）

`mode = native_ufs_store_mode()`（`NativeUfs.cpp:1683-1692`，`sheng-data-persist` 缺省或非 0/1/2 时为 0）。`direct` 保持初值 `false`（`:68`）当且仅当命中其一：

| # | 条件 | 代码点 | 结果 |
| --- | --- | --- | --- |
| 1 | `mode == 0`（无 `sheng-data-persist` 或值非法） | `:89` 条件不成立 | 完全不进 store 分支，state 保持 0 |
| 2 | 六个 weak 符号有任一缺失 | `:89-90` | 同上（`&symbol` 为假） |
| 3 | `native_ufs_store_open()` 拒绝 | `:95-97` | state 4 |
| 4 | `overlay.open()` 返回 `Failed` | `:107-109` | state 4 |
| 5 | 返回 `Blank`（mode 1 只读，或 header 无效） | `:110-111` | state 1 |
| 6 | 返回 `Kept`（header 有效但不属于该 seed/尺寸，且未请求 reset） | `:112-116` | state 7 |
| 7 | `mode == 1`（只读窗口） | `:104` 传 `ro = (mode == 1)`，:117-149 走加载分支，永不到 `:119/:122` | state 6（Resumed）或 1 |

反过来说，`direct = true` 要求同时满足：`mode == 2`；`overlay.open` 得到 `Fresh` 或 `Resumed`。`Fresh` 需要 `sheng-data-reset=1|2`（`:82` `discardRequested()`、`PersistOverlay.h:89-90`、`:100`）。

### 2.6 提供者侧 `native_ufs_store_open()` 的拒绝分支（`NativeUfs.cpp:1700-1728`）

```c
1704:  if (!storeMode ()) reason = "off";
1705:  else if (!gStoreGeometry.valid || !gHost.ready) reason = "no root layout";
1706:  else if (gStoreRegionBlocks) reason = "already open";
1708:    uint64_t partition = gStoreGeometry.last - gStoreGeometry.first + 1;
1709:    uint64_t imageBlocks = (gStoreGeometry.imageBytes + 4095) / 4096;
1710:    const uint64_t reserve = reserveBlocks ();
1711:    if (!blocks || reserve >= partition || blocks > partition - reserve) reason = "size";
1712:    else if (partition - blocks - reserve < imageBlocks + 1024) reason = "overlaps the root image";
1716:      uint64_t first = gStoreGeometry.last + 1 - reserve - blocks;
1717:      if (storeMode () == 2 && !hostStoreOpen (first, blocks)) reason = "window refused";
```

- `blocks` 由消费者给：`persist::windowBlocks(pages) = 1 + ceil(pages/32768) + pages`（`PersistOverlay.h:41-43`），即**每逻辑页占一个 4 KiB 介质块**，窗口随 Data 容量线性增长。
- `reserve = reserveBlocks()`：`sheng-log-reserve` MiB（缺省 1024，上限 16384），换算 `mib * 256` 个 4096 B 块（`NativeUfs.cpp:1670-1680`）；注释 `:1667-1670` 说明该值决定 store 落位，**一个镜像一生只能用一个值**。
- `gStoreGeometry` 只在 `startRoot()` 通过 manifest 校验后填写（`:2609-2617`），而 root 发布要求 owner 验证（`:2658-2666`，未定义 `NATIVE_VERIFIED_BLOCK` 时 `return false; // Root publication requires owner verification in every build.`）。
- 提供者写窗口是**单窗口**：`RootCommands.h:287-295` `if (gStoreOpen || !blocks || …) return false;`，写前再校验 `hostInWindow()`（`:280-284`），窗口外写入返回 `kIOReturnBadArgument`（`:301`）。

### 2.7 静态观察（未验证可达性）

`attachStore()` 的 `else` 分支（`mode != 2` 且 `Open::Resumed`）把 store 里的页拷进 `sparse.pages`：

```c
125:          struct Loader {
128:              if (i >= self->sparse.bytes / 4096) return false;
129:              if (!self->sparse.pages[i]) {
```

`isBig` 时 `sparse.pages == nullptr`（只有 `sparse.bytes` 被赋值，`:226`）。因此组合"`isBig` + `mode == 1` + header 与本 seed 匹配（`Resumed`）"在第 129 行会解引用空指针。该组合是否可达取决于介质上是否已存在该 seed 的合法 `SHNGDATA` 头（本板尚未写入过，未验证）。

---

## 3. 本板实际数字与阈值的关系

全部取自 `out/production-complete-20261114-r1/INSTALL-LAYOUT.json`（标注 `current Android GPT-backed offline layout; not an installed disk`），并用 C2 复算一致。

| 项 | 值（字节 / 4 KiB 块） | JSON 键 | 与 2 GiB（2,147,483,648 B）关系 |
| --- | --- | --- | --- |
| Data 逻辑容量（seed 头的 `size`） | **3,221,225,472 B** = 正好 3 GiB / 786,432 页 | `Data.logical_bytes`、`Data.pages` | **超阈值 1,073,741,824 B（+262,144 页）** ⇒ 走 `isBig` |
| Data 位图块 | 24 块（`ceil(786432/32768)`） | `Data.bitmap_blocks` | — |
| store 窗口 | **786,457 块 = 3,221,327,872 B**（1+24+786432） | `current_enuma_geometry.store_blocks` / `store_bytes` | 窗口比逻辑盘多 102,400 B（头+位图）；**`3221327872` 是窗口字节数，不是 Data 逻辑容量** |
| packed seed 实体 | 1,171,584 B | C6 `data.dbr` | 远低于 blob 上限（0x80000000）与 `ramPackedLayout` 的 256 MiB 上限 |
| 生产 root 镜像 | **9,382,658,048 B** = 2,290,688 块 | `root_image.bytes` | 与阈值无关；用于 `imageBlocks` 与 4 MiB guard（1024 块） |
| `userdata` 区间 | `[2686976, 61880315)` = **59,193,339 块 = 242,455,916,544 B**（≈225.8 GiB） | `userdata_first`/`userdata_end_exclusive`/`capacity_bytes` | 分区容量远大于任何候选 Data 尺寸 |
| reserve（`sheng-log-reserve` 缺省） | 262,144 块 = 1,073,741,824 B（1024 MiB） | `reserve_blocks` | 恰好等于阈值本身，但作用于**介质预留**，与 Data 尺寸判定无关 |
| store 落位 | `store_start = 60,831,714`，`store_end_exclusive = 61,618,171` | 同名字段 | `= userdata_last+1-reserve-blocks`，与 `NativeUfs.cpp:1716` 一致 |
| root 镜像后的空隙 | 55,853,026 块 | `gap_after_root_guard_blocks` | `= store_start - userdata_first - imageBlocks - 1024` |
| 无镜像约束时的窗口上限 | 58,931,195 块 = 241,382,174,720 B | 复算 `partition - reserve` | 3 GiB 窗口远低于此 |
| 留出镜像+guard 后的窗口上限 | 56,639,483 块 = 231,995,322,368 B（≈216.1 GiB） | 复算 | 同上 |

即：**当前 3 GiB 方案几何上通过 `native_ufs_store_open()` 的全部尺寸判据**（`size`、`overlaps the root image`、`already open`、`window refused` 皆不触发），`>2GiB` 的后果只落在消费者"必须有 direct store 才能写"这一条上（§1.3）。

顺带的数量关系：2 GiB 盘的窗口为 `1+16+524288 = 524,305` 块 = 2,147,553,280 B；≤2 GiB 分支的页指针数组为 `pages*8`：2 GiB 时 4,194,304 B，3 GiB 时为 6,291,456 B（`isBig` 路径不分配后者，见 `:229`）。

---

## 4. 四种绕行方案：现有代码的支持情况与代价（只列事实，不选型）

### 4.1 把 Data seed 精简到 ≤ 2 GiB

**代码路径**：`logical <= 0x80000000` 时 `NativeRamBlock.cpp:227-231` 走 `RamSparseDisk`，写落在 `ramSparseIO()`（`SparseDisk.h:44-60`，按需 `IOMallocZero(4096)`）——**无需 store 即可写**，但重启全丢；seed identity 变为全字节哈希（`SeedDisk.h:75-82`）。

**需要的输入**：

- 一份 APFS Data 容器（CS APFS，`scripts/ci/data_seed_macos.py:189` `hdiutil create -size 1g … -fs Case-sensitive APFS -volname EnumaData`）→ 打包成 `DBRDISK1`（`packed_ramdisk.pack`，`MAX_INPUT = 256 MiB`、`MAX_LOGICAL = 1 TiB`）。
- macOS 工具链：`hdiutil` / `diskutil`（`packed_ramdisk` 的 `pack` 只做打包，容器生成/伸缩在 macOS 上）。
- 现有官方工具**不支持**该尺寸：`UniXNU/scripts/seed-data-grow.py` 是唯一尺寸选择工具，`if not 3 <= gib <= MAX_GIB: sys.exit(f'{gib} GiB is outside 3..{MAX_GIB}')`，且 `if target <= logical: sys.exit(… growing needs a larger size)` —— 只放大、最小 3 GiB。
- 因此 ≤2 GiB 只能取设备 CI 脚本产出的 **1 GiB 基础容器**（`-size 1g`），或另写新工具。

**会失去什么（事实层）**：

- Data 容器容量从 3 GiB 降到 ≤2 GiB（可选值目前是 1 GiB）；容器内超出新容量的内容不存在。
- seed identity 换格式（§2.2），介质上任何为 3 GiB seed 写入的 `SHNGDATA` 窗口都变成 `Kept`（`PersistOverlay.h:100`），旧 Data 不会自动接续。
- **仍然不解决持久化**：写可以进 RAM，但重启即失；要持久依旧需要 direct store（§4.3）。该方案只消除"无易失写回退"这一条拒绝。

**失效的现有产物**：

| 产物 | 原因 |
| --- | --- |
| `out/production-complete-20261114-r1/INSTALL-LAYOUT.json` 的 `Data.*` 与 `current_enuma_geometry.store_*`、`destructive_scope_if_later_authorized.Data_store_write_byte_range` | 尺寸/页数/窗口/LBA 全变 |
| `out/production-complete-20261114-r1/{payload.img,prelink.macho,native.macho,boot.img,candidate-manifest.json}` | packed seed 内嵌在 payload（`prelink + seed + trust ≤ 192 MiB` 预算），1,171,584 B 的旧 seed 换了字节与哈希 |
| `out/verify-data-seed-receipt-20261113/`（3 GiB seed 的接收/审计回执） | 回执绑定旧 seed 的字节与哈希 |
| `porting.toml` 中 `Historical3GiB store3221327872B` 一类表述与 README 进度文本 | 数字口径改变 |
| `scripts/build-enuma-owner-data.py` 的 `require(sha(record(SEED / 'data.dbr')) == data['encoded_sha256'], 'packed seed changed')` 与其 geometry 断言 | 输入变了，断言按新值重算 |

### 4.2 分卷写入（多块 store region）

**现有代码不支持**，证据：

| 证据 | 位置 | 含义 |
| --- | --- | --- |
| `else if (gStoreRegionBlocks) reason = "already open";` | `NativeUfs.cpp:1706` | 每次启动只允许开一个 store 窗口 |
| `static bool gStoreOpen = false, gLogOpen = false;` `static uint64_t gStoreFirst…gStoreBlocks…` | `RootCommands.h:267-268` | 提供者侧只有"store / log"两个窗口、各一组基址+长度 |
| `hostStoreOpen()` 内 `if (gStoreOpen \|\| …) return false;`；`hostInWindow()` 只匹配这两个窗口；`hostWrite4k()` 窗口外即 `kIOReturnBadArgument` | `RootCommands.h:287-289`、`:280-284`、`:299-303` | 第二个 store 区间的写入会被硬拒 |
| `persist::windowBlocks(pages) = 1 + bitmapBlocks(pages) + pages`；`pageBlock(pages,i) = 1 + bitmapBlocks(pages) + i` | `PersistOverlay.h:42-43` | 单一连续窗口内的偏移映射，没有"区间→基址"表 |
| 头块固定 block 0，含 `"SHNGDATA"`、version `1`、`page count`、seed SHA-256、generation、crc32 | `PersistOverlay.h:6-9`、`:45-56`；`checkHeader` 版本必须为 1（`:61`） | 分卷要么共用一份位图+相对页号的映射层，要么改格式版本 |
| `native_ufs_store_read/write(rel, blocks, …)` 的 `rel` 相对**唯一** `gStoreRegionFirst` | `NativeUfs.cpp:1730-1756` | 没有绝对 LBA 或区间号参数 |
| log 窗口占用 userdata 末端 32 MiB + 下方 256 MiB 导出区，且与 store 不得重叠 | `NativeUfs.cpp:1661-1666`、`RootCommands.h:273`、`:290` | 可用窗口只剩 store 那一段 |

**代价/影响（若实现）**：需要新的介质格式（版本号变化 ⇒ `checkHeader` 的 `version==1` 判据、`overlay.open` 的恢复路径都要改）、消费者侧"页号→(区间,页内偏移)"映射、提供者侧多窗口登记与 `hostInWindow` 扩展。

**失效产物**：任何已写入的 `SHNGDATA` v1 窗口（版本不符 ⇒ 走 `Kept`/`Blank`）；`INSTALL-LAYOUT.json` 的单一 `store_start/store_end_exclusive` 与 `Data_store_write_byte_range`（`[249166700544, 252388028416]`）；`candidate-manifest.json`/`audit.json` 中与该区间绑定的条目。

**与本板 3 GiB 的关系**：3 GiB 窗口（786,457 块）在现有几何下已通过全部尺寸判据（§3），分卷不改变其可行性；只有当 Data 容量逼近可用区间（约 216 GiB 上限）时才会触及 `size`/`overlaps the root image`。

### 4.3 直连 store（`sheng-data-persist=2` + 已发布 root）

**它是 `isBig` 唯一能写/能持久的路**，依据（逐条）：

1. `direct` 只在 `mode == 2` 得到 `Fresh` 或 `Resumed` 时置真（`NativeRamBlock.cpp:119`、`:122`）；`mode` 来自 `PE_parse_boot_argn("sheng-data-persist", …)`，值 `>2` 归零（`NativeUfs.cpp:1688`）。
2. `isBig && !direct` 的写分支直接 `return kIOReturnNotReady`（`:269-293`）。
3. `direct` 为真后写只能落在 store 窗口（`DirectDisk.h:47-65`），窗口必须先由 `native_ufs_store_open` 分配给 `hostStoreOpen`（`NativeUfs.cpp:1717`、`RootCommands.h:287-295`），后者要求 `gStoreGeometry.valid && gHost.ready`（`:1705`）。
4. `gStoreGeometry` 仅在 `startRoot()` 通过 manifest 校验后填写（`:2609-2617`），而 root 发布要求 owner 验证（`:2666`）。
5. 首次写入还要求 `Fresh`：正常启动不带 `sheng-data-reset` 时，空白窗口得到 `Kept`（`PersistOverlay.h:100`）→ `direct` 仍为假；`INSTALL-LAYOUT.json:48-52` 记 `"offline_recipe_only": "after separate identity/GPT and device-write authorization, one explicit initialization boot adds sheng-data-reset=1; never persist this in the normal entry"`。

**板级准入在两份快照里不同（都给了，不作解释）**：

| 快照 | 判据 |
| --- | --- |
| `out/owner-data-query-20261113-r3/source-ufs/UfsPlatformResources.h:110-114` | `bool supported = root.soc == Soc::Sm8550;` … `return {true, root.soc == Soc::Sm8250, supported, …}` — SM8250 下 `takeoverSupported == false`，`NativeUfs.cpp:2259-2261` 据此 `return false` |
| `out/ufs-sm8250-policy-20261116-r1/source/UfsPlatformResources.h:116-120` | `bool supported = root.soc == Soc::Sm8250 && root.enuma;` … `Policy::Sm8250Warm` — 精确 enuma（ADT `xiaomi,enuma` + `qcom,sm8250`/`-ac` + `0x01d84000/0x3000`）给出 `takeoverSupported == true` |

即：同一路径能否拿到 `gHost.ready`/`gStoreGeometry`，取决于烧进镜像的是哪一份 provider 源码；两份都在 `out/`，无默认构建同时启用两者的记录。

**代价/影响**：

- 需要一次带 `sheng-data-reset=1`（或 `2`，附带请求 Setup）的初始化启动，且不能写进常规启动参数（`INSTALL-LAYOUT.json:50`）。
- store 落位由 `sheng-log-reserve` 决定且终生固定（`NativeUfs.cpp:1667-1670`），改值会把旧窗口读成 blank。
- 写介质使 §3 的 `Data_store_write_byte_range` 成为真实写范围，属设备写入，须当轮授权。
- 依赖 owner 验证与 manifest（`:2658-2666`）；`NATIVE_VERIFIED_BLOCK` 未定义时 root 不发布，store 不可用。
- 不改动 seed/payload，故不使现有产物失效（换个启动参数即可）；但 3 GiB 的 `Data.logical_bytes`/窗口几何仍绑定当前 seed。

### 4.4 保持 ≤2 GiB 且完全不用 store（易失）

`RamSparseDisk` 路径可写 RAM（`SparseDisk.h:44-60`），`doAsyncReadWrite` 在 `overlay.active == false` 时只做 `ramSparseIO`（`NativeRamBlock.cpp:318-320`、`:321-333` 的写回分支被 `overlay.active` 关掉）。代价：断电即丢，与"持久根卷"里程碑定义不符（`docs/context-brief.md`「目标」）。不使任何产物失效，但没有 store 窗口、也没有 `SHNGDATA` 介面格式。

### 4.5 交叉表（事实汇总）

| 方案 | 现有代码支持? | 需要的新输入 | 3 GiB Data 可用? | 主要失效产物 |
| --- | --- | --- | --- | --- |
| 4.1 精简 seed ≤2 GiB | 支持（`≤2 GiB` 分支可写 RAM） | macOS + 新 seed（≤2 GiB；官方工具最小 3 GiB、只放大） | 否（容量下降） | INSTALL-LAYOUT 几何、payload/prelink/native/boot、seed 回执、`porting.toml`/README 数字 |
| 4.2 分卷 store | **不支持**（单窗口 + 单头 + 版本 1） | 新介质格式、区间映射、提供者多窗口 | 是（几何本就够） | 已写 `SHNGDATA` v1 窗口、写范围披露、manifest 中该区间条目 |
| 4.3 直连 store | 支持（需 `sheng-data-persist=2` + 发布 root + `Fresh`） | 板级准入源码（两份快照不一致）、owner 验证、初始化启动 | 是 | 无（运行参数级）；受 `sheng-log-reserve` 终生绑定 |
| 4.4 易失（≤2 GiB，无 store） | 支持 | 同 4.1 的 seed | 否 | 同 4.1（尺寸相关） |

---

## 5. 未确定项

1. **store 提供者在真实设备上的可用性**：`native_ufs_store_open` 要求 `gHost.ready && gStoreGeometry.valid`，其上游是 `startRoot()` 的 native UFS bring-up；本板是否有任何镜像真正跑到该点没有任何实机证据（现有实机记录停在 rootwait/控制台，未进入 store）。
2. **板级准入取哪份源码**：§4.3 两份 `UfsPlatformResources.h` 语义相反，`out/` 中无记录说明默认 recipe 用哪一份，也无记录说明 `Sm8250Warm` 策略在设备上被接受过。
3. **`hostStoreOpen` 的窗口被拒条件**：`RootCommands.h:287-295` 只看"未开过、非零、LBA 不溢出、不与 log 重叠"；`NativeUfs.cpp:1649-1650` 注释提到"at most a quarter of the partition"，但代码里没有四分之一判据（`scripts/build-enuma-owner-data.py` 的 `quarter_note` 也这么记）。注释与实现不一致，以哪一方为准未定。
4. **`isBig + mode==1 + Resumed` 的空指针组合（§2.7）**是否可达、是否已被测试覆盖：未找到对应测试；本板介质上尚无 `SHNGDATA` 头。
5. **≤2 GiB seed 的实际可用性**：现有工具只能产出 1 GiB 基础容器或 ≥3 GiB 放大结果；2 GiB 容器能否生成、iPadOS 17.7.11 的 Data 卷在 1–2 GiB 内能否挂载并完成首启，均无证据。
6. **`data.dbr` 的 3 GiB 容器是否与 `Data.logical_bytes = 3,221,225,472` 一致**：只比对了 `INSTALL-LAYOUT.json` 与 `build-enuma-owner-data.py` 的算术（一致）；未解析 `data.dbr` 头读出 `size` 字段本身。
7. **实际介质上的 `SHNGDATA` 头状态**（是否存在、gen、page count）：无设备读取，`native_data_persist_header` 无观测值。
8. **`sheng-log-reserve` 的最终取值**：默认 1024 MiB，但正式镜像是否改过、是否与 log 同用，未在 `board.toml`/recipe 中找到定值记录。
9. **分卷方案的介质格式改动**是否需要同步 XNU 侧（当前 XNU 只拿 `device_path` 与 seed 尺寸/哈希，理论上不需要），未验证。
10. **`gStoreGeometry.imageBytes` 的来源**（manifest 里的 root 镜像长度）：`RootLayout.h` 的解析未在本轮复核，只确认赋值点 `:2616`。

---

## 6. 代码点速查

| 文件（`out/owner-data-query-20261113-r3/source-ram/`，与基线 `UniXNU/drivers/RamBlock/` 同哈希） | 行 | 内容 |
| --- | --- | --- |
| `NativeRamBlock.cpp` | 57-59 | >2 GiB 只走 direct 的注释 |
| 同上 | 66-68 | `direct`/`directFailed` 语义 |
| 同上 | 83-155 | `attachStore()` 全流程 |
| 同上 | 119、122 | `direct` 置真两点 |
| 同上 | 157-163 | `available()` / `seedInfo()`（`base = 0`，`bytes = capacity*512`） |
| 同上 | 211 | blob 长度 ≤ 0x80000000 |
| 同上 | 219-226 | `logical > 0x80000000` → `isBig` |
| 同上 | 233 | `capacity = logical/512` |
| 同上 | 236-239 | `seedIdentity()`（`SHNGSEED2`） |
| 同上 | 258-349 | `doAsyncReadWrite`：269-293 只读、303-317 direct、321-333 写回 |
| 同上 | 376-434、456-461 | `selectVolumeSeed`（414 调 `attachStore`）与两个导出入口 |
| `SeedDisk.h` | 3-5、10-22 | 结构与非零页语义 |
| 同上 | 72-95 | identity：`<=0x80000000` 全字节 / `>0x80000000` `SHNGSEED2` |
| `SparseDisk.h` | 13-25 | `ramPackedLayout`（`n>0x10000000` 拒绝、`count>65536` 拒绝） |
| 同上 | 44-60 | `ramSparseIO`：≤2 GiB 的易失写 |
| `PersistOverlay.h` | 6-9 | 窗口介质布局（头/位图/页） |
| 同上 | 41-43 | `bitmapBlocks` / `windowBlocks` / `pageBlock` |
| 同上 | 58-65、82-109 | `checkHeader`（version 1）、`open`（Resumed/Fresh/Blank/Kept/Failed） |
| 同上 | 129-146 | `writeRun`：页先落盘、位图后写 |
| `DirectDisk.h` | 16-67 | direct I/O（页命中读 store，否则读 seed；写必落窗口） |

| 文件（`out/ufs-sm8250-policy-20261116-r1/`） | 行 | 内容 |
| --- | --- | --- |
| `source/NativeUfs.cpp` | 1646-1650 | store 窗口的用途与拒绝条件注释 |
| 同上 | 1661-1670 | log 32 MiB + 导出 256 MiB、`sheng-log-reserve` 默认 1024 MiB |
| 同上 | 1671-1692 | `reserveBlocks()`、`storeMode()` |
| 同上 | 1697-1728 | 六个 store 导出函数与几何判据 |
| 同上 | 1730-1761 | `read/write/sync`（`rel` 相对唯一窗口；写用 FUA） |
| 同上 | 1846-1857 | `native_ufs_store_gpt_check` |
| 同上 | 2609-2617 | `gStoreGeometry` 赋值 |
| 同上 | 2658-2666 | root 发布要求 owner 验证 |
| `self-check/merged-source/RootCommands.h` | 264-268 | 单 store / 单 log 状态 |
| 同上 | 270-278、286-296 | `hostLogOpen` / `hostStoreOpen`（拒绝重叠与二次打开） |
| 同上 | 280-284、299-303 | `hostInWindow` / `hostWrite4k`（窗口外拒绝） |
| `self-check/merged-source/UfsPlatformResources.h` | 116-120 | 精确 enuma → `Sm8250Warm` |

| 基线只读 | 行 | 内容 |
| --- | --- | --- |
| `UniXNU/patches/xnu/offline-owner-systemos-mount.patch` | 209-214 | typed provider 取卷 + 1 TiB 上限 |
| 同上 | 216-219 | dense `md` 路径 2 GiB 上限 |
| `UniXNU/scripts/seed-data-grow.py` | 12、92、97、116 | 只放大（`target <= logical` 即报错）、`3..1024` GiB、macOS `diskutil apfs resizeContainer` |
| `UniXNU/drivers/DarwinBoot/Test/packed_ramdisk.py` | 9-20 | `MAX_INPUT=256 MiB`、`MAX_LOGICAL=1 TiB`、`count<=65536` |
| `UniXNU-enuma/scripts/ci/data_seed_macos.py` | 189 | 基础容器 `-size 1g`、CS APFS |
