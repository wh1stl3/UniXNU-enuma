# enuma 持久 Data store 几何可行性

状态：self-checked，离线源码和既有记录分析；无设备访问、卷修改或构建。以下窗口是指定输入下的条件推算，不是写入授权或当前候选实测值。

## 1. 几何来源与公式

当前 `package/EnumaRamBlockStore.cpp:5-13` 的强符号 `native_ufs_store_mode() { return 0; }`，open/read/write/sync 都失败。仅加 mode 2 参数不会启用它；必须核实最终候选实际六符号归属。以下是历史快照 `out/ufs-sm8250-policy-20261116-r1/source/NativeUfs.cpp`，并非断言当前候选使用它。

该快照 `:2600-2617` 在 `findRootLayout` 成功且 manifest 状态为 0 后：

```cpp
gStoreGeometry = { true, layout->userdataFirst, layout->userdataLast, layout->imageBytes, layout->gptEntriesLba,
                   layout->gptHeaderCrc, layout->gptEntriesCrc, layout->gptEntryCount };
```

同快照 `self-check/merged-source/RootLayout.h:13-16,59-102,135-148,159-171,208`：先读主 GPT 并检查 header/entry CRC，读取 userdata GPT 项首末 LBA；`imageBytes` 来自 userdata 首块 manifest，而非分区大小。LBA 为 LUN 0 的 4096 B 块，last 包含在内。`NativeUfs.cpp:1667-1679,1704-1717`：

```cpp
cached = static_cast<int64_t> (mib) * 256; // 4096-byte blocks
uint64_t partition = gStoreGeometry.last - gStoreGeometry.first + 1;
uint64_t imageBlocks = (gStoreGeometry.imageBytes + 4095) / 4096;
if (!blocks || reserve >= partition || blocks > partition - reserve) reason = "size";
else if (partition - blocks - reserve < imageBlocks + 1024) reason = "overlaps the root image";
uint64_t first = gStoreGeometry.last + 1 - reserve - blocks;
```

reserve 默认 1024 MiB、参数可改；消费者按 seed 页数请求 `1 + ceil(pages/32768) + pages` 块（`docs/data-store-2gib-analysis.md:110-115,146-164`）。开窗还要求 `gHost.ready`、有效布局、未重复打开，mode 2 另需 `hostStoreOpen` 成功；该文 `:164` 描述写窗口边界。不得把注释中的四分之一限制当作上述实际 `native_ufs_store_open` 已检查的条件。

## 2. 实机证据

* `docs/ufs-sm8250-policy-r2-device-observation.md`：11-17 r2 probe 显示 ready 及 `userdata first=290000 last=3b037fa`，对应 4 KiB LBA 2686976、61880314；探针不调用 `startRoot`（`:220`）。该轮主控与 vision 核读一致。
* `docs/ufs-sm8250-startroot-mode0-observation.md`：11-18 r1 显示 warm bring-up ready 与同样首末值，但 manifest 拒绝，未到几何赋值。
* `docs/ufs-root-mount-20261118-observation.md:135-148,159-166,280-283`：11-18 r2 mode 0 显示 ready、发布 SystemOS 和 OS，越过 manifest 闸；结合所运行 provider 的控制流，几何赋值可静态推断，**不是字段打印或直接回读**。观察为主控单次转录，缺影像独立核读。具体候选源码及实际链接的差异仍须确认。
* **无 `gStoreGeometry` 字段值或 mode 2 store 窗口起止值的实机打印证据**；亦无持久 store 写入及重启存活证据。

## 3. 既有 userdata 几何

`.cache/android-sysfs-20261112-113131/batch.log:3-26` 为历史只读采集：sda34 start 21495808、size 473546712，均为 Linux 512 B sector；sda logical/physical block 均 4096 B。换算 userdata 4 KiB LBA `[2686976, 61880315)`，长度 59193339 块、242455916544 B；disk 61880320 块。11-17 native 主 GPT 对应首末与之吻合；这是历史交叉证据，不是当前 GPT 或备份 GPT 校验。`docs/ufs-warm-capacity-r2-diagnostic.md` 另有 11-16 设备 4096 B 逻辑块容量观察。

## 4. 条件写入区间及风险

以历史 11-19 临时 seed 为例：`docs/data-seed-20261119-generation.md` 记录逻辑大小 2146996224 B = 524169 页；假设同一 seed、上述历史 provider、历史分区边界和默认 reserve 1024 MiB：

* bitmap `ceil(524169/32768)=16` 块，窗口 `1+16+524169=524186` 块。
* reserve `1024*256=262144` 块；窗口结束（不含）`61880315-262144=61618171`，开始 `61618171-524186=61093985`。
* 条件写入包络：绝对 4 KiB LBA **[61093985, 61618171)**，字节 **[250240962560, 252388028416)**，总 2147065856 B；尾部再留 1073741824 B 到 userdata 结束。store 不一定实际写满整个包络。
* 算术上窗口完全在历史 userdata 内，避开该次 9382658048 B root image 前缀（`docs/ufs-root-mount-20261118-observation.md:62-68`），也与历史磁盘末尾及分区外区域不重叠；**不证明当前 GPT/备份 GPT 位置、完整性或其它分区现状**。seed、reserve、分区或 provider 变化均改变计算。
* mode 0 scratch Data 为 RAM overlay，重启丢失（`docs/ufs-launchd-data-20261119-observation.md:92`）；mode 2 初始化元数据和后续数据写持久介质，会覆盖对应尾部原有内容，reset 还会丢弃旧 overlay（`docs/swap-and-persistent-data-20261123.md:22-23`）。历史 userdata 前缀刷写不证明尾部为空。

## 5. 判断与证据缺口

持久 Data 对目标有价值，但现在不能把上述几何当作安全写入候选。必须取得：最终候选的六符号实际归属、具体 seed 身份/大小和 reserve；同次只读读取 LUN 容量与当前主/备 GPT（含 CRC、分区边界和身份），在不打开写窗口下核对 manifest imageBytes、计算并打印 store 起止/长度及 root 非重叠；验证 owner-authenticated placement binding 与现有写窗口约束，不能把几何正确当作 DMA/持续所有权或写能力通过。任何真实设备操作及写入仍须对应当轮授权；mode 1/2 未放行。
