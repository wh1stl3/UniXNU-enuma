# 在 macOS 15 VM 里生成 Data seed 的命令单

状态：`self-checked`。已实际执行：`--gib` 下限拒绝（WSL `python3.11` 跑真脚本）、6.2/6.4 校验逻辑（合成 DBRDISK1 稀疏镜像，`packed_ramdisk.pack` → 头字段 → NXSB/APSB 扫描 → UUID 对账全通）。未执行：任何 `hdiutil`/`diskutil` 步骤（无 macOS）；**第 5 节（3 GiB → 2,147,000,000 B 缩容）整节未执行，属未验证**。逐行粘贴即可执行；每条命令后给出预期输出与判定。**所有命令在同一个 shell 里按序执行**（`$SHARE`、`$MP`、`$SRC` 等依赖前序赋值）。

前置事实全部来自本仓/基座源码：

| 事实 | 来源 |
| --- | --- |
| `hdiutil create -size 32m -fs APFS` 建 32 MiB，再 `diskutil apfs resizeContainer <container> 0` 扩到目标 | `UniXNU/scripts/make-data-seed.py:51-52`、`UniXNU/scripts/seed-data-grow.py:99-116` |
| `make-data-seed.py:19` 把 `ROOT/drivers/DarwinBoot/Test` 插入 `sys.path`，`:97` 用 `sys.executable` 调 `ROOT/scripts/seed-data-grow.py` | 同上 |
| OS 窗口是压缩 UDIF（尾部 `koly`），解出的 raw 6,077,580,800 B、SHA-256 `e5634d04…a4f2`，APFS 容器起点 17408（NXSB 在 0x4420） | `UniXNU-enuma/out/userdata-clean-20261112/{REPORT.md:14,apfs-check.py:28-52,apfs-report.json:11-13}` |

## 0. 与任务书的三处偏差（先看，再粘贴）

| 任务书 | 实际 | 处置 |
| --- | --- | --- |
| `--gib 1` | 官方工具硬拒（**已实测复现**）：`make-data-seed.py:45-46` 与 `seed-data-grow.py:92-93` 都要求 `3 <= gib <= 1024`，`--gib 1` 输出 `make-data-seed.py: error: --gib must be in 3..1024` 并以 exit 2 退出（直接调 `seed-data-grow.py` 则是 `1 GiB is outside 3..1024`，exit 1） | 本文一律用 `--gib 3`（工具下限，已实测能通过全部参数校验并走到 `hdiutil`）；要 ≤2 GiB 看第 5 节（先建 3 GiB 再缩）。1 GiB 只有 CI 门版本 `enuma/data-seed-ci-20261113/scripts/ci/data_seed_macos.py:189,236` 产出，那不是本任务指定的官方工具 |
| 「`stat -f%z` 校验 raw 大小」 | 官方工具输出的是 **DBRDISK1 打包格式**（只存非零页），`stat` 得到的是几 MB 的打包大小，不是逻辑容量 | 第 6 步用 DBRDISK1 头 `logical` 字段判容量，`stat` 只作对照说明 |
| `hdiutil attach -imagekey diskimage-class=CRawDiskImage -offset 17408 <dmg>` | `044-76040-038.dmg` 是压缩 UDIF，`-offset` 只对 raw 字节流生效，直接套在压缩镜像上会失败；且 `-offset` 本身在部分 macOS 版本不存在 | 第 3 步先 `hdiutil convert -format UDTO` 解出 raw，再按 3.5 默认整盘挂载（不用 `-offset`；挂不出卷才按 3.5 的回退切片） |

目标产物：`~/seed/data.dbr`，最终拷到 `enuma/UniXNU-enuma/out/data-seed-macos/`（`/out/` 已在 `.gitignore` 中）。本文不涉及设备、不刷写、不签名、不部署。

---

## 1. 前置检查

### 1.1 磁盘空间 ≥ 20 GB

```bash
df -h "$HOME"
```

判定：`Avail` ≥ 20Gi。峰值占用 ≈ 12 GB（DMG 副本 5.2 GB + 解出的 raw 6.1 GB）；`seed.raw` 走稀疏，实际占地小。

### 1.2 必须是 macOS 15.x

```bash
sw_vers
```

判定：`ProductVersion` 以 `15.` 开头。此版本的 APFS 格式化器是 `newfs_apfs` 2332.140.13.704.3；换 macOS 版本则生成的 APFS 元数据与卷 UUID 都不同，本轮已确认的 15.x 记录不再适用。

### 1.3 python3

```bash
python3 --version
```

判定：≥ 3.9（系统自带 3.9.6 即可）。三个脚本只 import 标准库（见第 2 步清单），不需要 pip。

### 1.4 工具存在

```bash
command -v hdiutil diskutil shasum awk
```

判定：四条路径全部打印（`/usr/bin/hdiutil`、`/usr/sbin/diskutil`、`/usr/bin/shasum`、`/usr/bin/awk`），无「not found」。`python3` 已在 1.3 确认。

### 1.5 共享目录可见

```bash
SHARE="/Volumes/VMware Shared Folders/PortingiOS"   # 改成你自己的挂载点
ls "$SHARE"
```

判定：列出 `UniXNU`、`enuma` 等顶层项。路径含空格，后续所有引用带引号。

### 1.6 建目录

```bash
mkdir -p "$HOME/unixnu/scripts" "$HOME/unixnu/drivers/DarwinBoot/Test" "$HOME/unixnu/build" "$HOME/seed"
```

判定：`ls -d "$HOME"/unixnu/*` 列出三项。`unixnu/build` 是 `seed-data-grow.py:99` 的临时目录父级，**脚本自己不会建它，缺了就 `FileNotFoundError`**。

---

## 2. 把最小输入拷进 VM

需要的文件只有三个（`make-data-seed.py` 全部 import 已在宿主侧核实：`argparse json os pathlib plistlib shutil stat subprocess sys tempfile` 为标准库，唯一外部模块是 `packed_ramdisk`，它自身只 `import argparse hashlib pathlib struct`）。目录结构必须复刻成 `scripts/` + `drivers/DarwinBoot/Test/`，因为 `ROOT = Path(__file__).resolve().parents[1]`。

```
~/unixnu/
  scripts/make-data-seed.py            <- UniXNU/scripts/make-data-seed.py
  scripts/seed-data-grow.py            <- UniXNU/scripts/seed-data-grow.py
  drivers/DarwinBoot/Test/packed_ramdisk.py  <- UniXNU/drivers/DarwinBoot/Test/packed_ramdisk.py
  build/                               <- 空目录
```

### 2.1 复制

```bash
SRC="$SHARE/UniXNU"
cp "$SRC/scripts/make-data-seed.py" "$SRC/scripts/seed-data-grow.py" "$HOME/unixnu/scripts/"
cp "$SRC/drivers/DarwinBoot/Test/packed_ramdisk.py" "$HOME/unixnu/drivers/DarwinBoot/Test/"
```

判定：无 `No such file`。

### 2.2 校验（哈希 pin）

```bash
shasum -a 256 "$HOME/unixnu/scripts/make-data-seed.py" \
              "$HOME/unixnu/scripts/seed-data-grow.py" \
              "$HOME/unixnu/drivers/DarwinBoot/Test/packed_ramdisk.py"
```

判定（逐字符）：

| 文件 | SHA-256 |
| --- | --- |
| `make-data-seed.py` | `a10a818ae19e2853b8a2e04ac56f9af2ea555c47ef6abaf85e0ee4da2865df0b` |
| `seed-data-grow.py` | `507bce30053936608ebf4d5b7de75397d7e544934a9949a071a244cc0a3c810c` |
| `packed_ramdisk.py` | `2291ff803553ee6e5431a4ce3770a36dab0a09f0d1fe036d3e1264ee5dd2a3b3` |

任一不符：停，不要继续（基座 pin 变了，后面所有预期值失效）。

### 2.3 导入自检

```bash
cd "$HOME/unixnu" && python3 -c "import sys; sys.path.insert(0,'drivers/DarwinBoot/Test'); import packed_ramdisk as p; print(p.PAGE, p.MAX_INPUT, p.MAX_LOGICAL)"
```

判定：`4096 268435456 1099511627776`。

---

## 3. 挂载 OS 窗口

### 3.1 源镜像 pin

```bash
DMG="$SHARE/enuma/UniXNU-enuma/out/userdata-clean-20261112/044-76040-038.dmg"
ls -l "$DMG"
```

判定：`5157406069` 字节。文件大小不符即停止（不做任何后续）。

### 3.2 拷到本机（不要直接从共享盘 hdiutil）

```bash
cp "$DMG" "$HOME/seed/044-76040-038.dmg"
shasum -a 256 "$HOME/seed/044-76040-038.dmg"
```

判定：`3f99b859c9728379110b66657c7b15285bcb1925ad8b5726542e2cdcf8b1028d`（约 30–60 s）。不符：停。

### 3.3 解压成 raw

```bash
hdiutil convert "$HOME/seed/044-76040-038.dmg" -format UDTO -o "$HOME/seed/os-window"
```

判定：产出 `~/seed/os-window.cdr`，无 `error`。约 1–3 min。

### 3.4 校验 raw

```bash
stat -f%z "$HOME/seed/os-window.cdr"
shasum -a 256 "$HOME/seed/os-window.cdr"
```

判定：`6077580800`；SHA-256 `e5634d04a8ac35f024845f583394e0a35deb26a04cb0c00286a8674e25a9a4f2`。
尺寸相同但哈希不同：停并回报 —— `hdiutil convert` 只做无损解压，哈希不一致说明源 DMG 不是 pin 的那一份。

### 3.5 挂载（默认挂整盘，自动发现挂载点）

```bash
BEFORE=$(ls /Volumes)
hdiutil attach -readonly -nobrowse -owners off "$HOME/seed/os-window.cdr"
```

判定：打印一行 `/dev/disk<N> … Apple_APFS` 与一个 `/Volumes/…` 挂载点，无 `hdiutil: attach failed`。

挂载点不写死：整盘交给 `hdiutil` 后由它读 GPT 自行命名。用前后 `/Volumes` 的差集发现它，要求**恰好一个**新增项，把它设为 `OSX_MOUNT`；3.6 节起所有路径都用 `$OSX_MOUNT`：

```bash
AFTER=$(ls /Volumes)
comm -13 <(printf '%s\n' "$BEFORE" | sort) <(printf '%s\n' "$AFTER" | sort)   # 必须恰好一行
OSX_MOUNT="/Volumes/<那一行>"
```

校验（两条都成立才算挂好）：`test -d "$OSX_MOUNT/private/var"` 与 `test -e "$OSX_MOUNT/sbin/launchd"`。
`-owners off` 让所有权映射到当前用户，否则 `700` 的 root 目录会让后面的 `os.walk` 静默漏拷贝。

> **`-offset` 在部分 macOS 版本不可用**（实测报 `hdiutil: attach: unknown option "-offset"`），本流程不再尝试它。只有整盘挂不出可用卷（`/Volumes` 没有新增项，或上面两条校验不成立）时才切片：

```bash
dd if="$HOME/seed/os-window.cdr" of="$HOME/seed/container.raw" bs=512 skip=34
hdiutil attach -imagekey diskimage-class=CRawDiskImage -readonly -nobrowse \
  -owners off -mountpoint /Volumes/OSX "$HOME/seed/container.raw"
```

> 34×512 = 17408 是 GPT 首分区起点，跳过它使块 0 直接是 NXSB（文件内 0x4420）；`-imagekey diskimage-class=CRawDiskImage` 保留：`.raw` 后缀没有可嗅探的 UDIF 尾部，与本单其它 `.raw` 挂载一致地显式指定镜像类。这条路把 `OSX_MOUNT` 定为 `/Volumes/OSX`。两个校验点，任一不成立即停：① `stat -f%z "$HOME/seed/container.raw"` = `6077580800 − 17408 = 6077563392`；② 块 0 偏移 32 的 4 字节魔数为 `NXSB`（`python3 -c "import sys;d=open(sys.argv[1],'rb').read(36);print(d[32:36]);sys.exit(d[32:36]!=b'NXSB')" "$HOME/seed/container.raw"`）。`data-seed-vm-run.sh` 的 §3/11 就是这两条路径（先整盘，判据不成立才切片），并把实际方式记进摘要块 `ATTACH_MODE=whole|dd`；切片分支尚未在 VM 上实测，额外占 ~6 GB，§1.1 的 20 GiB 下限未计入这部分。

### 3.6 确认是 IPSW OS 卷

```bash
ls -l "$OSX_MOUNT/sbin/launchd"
test -d "$OSX_MOUNT/private/var" && echo "var=dir"
```

判定：`launchd` 存在且 `var=dir`。这正好是 `make-data-seed.py:41` 的两条前置判断；任一不成立，第 4 步会以 `not an IPSW OS volume` 退出。

---

## 4. 生成 seed

### 4.1 生成

```bash
cd "$HOME/unixnu"
python3 scripts/make-data-seed.py "$OSX_MOUNT" "$HOME/seed/data.dbr" --gib 3 --build 21H461 --skip-setup
echo "exit=$?"
```

流程：`hdiutil create -size 32m -fs APFS -type UDTO` 建 32 MiB（约 2 s）→ 挂载并把 OS 卷 `private/var` 拷进去（该模板实测 166 目录 / 39 文件 / 1 符号链接，秒级）→ 按 `--skip-setup` 写 purplebuddy / springboard / migration 等偏好 → 打包成 `base.dbr` → `seed-data-grow.py --gib 3` 建 3 GiB 稀疏 raw、`diskutil apfs resizeContainer <container> 0` 撑满、再打包成 `data.dbr`。总耗时约 1–2 min。

预期 stdout 是**两段** JSON（`seed-data-grow.py:128` 的报告先出，`make-data-seed.py:99` 的一行后出）：

```text
{
  "base": "/Users/<you>/seed/new-data-XXXXXXXX/base.dbr",
  "gib": 3,
  "container_bytes": 3221225472,
  "bytes": 3221225472,
  "sha256": "<64 hex，seed identity>",
  "encoded_bytes": 几 MB 到几十 MB,
  "encoded_sha256": "<64 hex>"
}
{"output": "/Users/<you>/seed/data.dbr", "first_install": true, "preserve_for_future_builds": true}
```

判定：
1. `exit=0`；
2. `gib == 3`，`bytes == 3221225472`；
3. `bytes - container_bytes <= 67108864`（64 MiB，`seed-data-grow.py:124` 自己的判据）；
4. `encoded_bytes` 远小于 `bytes`（打包只留非零页）；若 ≥ 64 MiB，说明 raw 没有保持稀疏。

`sha256` 是 seed identity（>2 GiB 时走 `packed_ramdisk.seed_identity`，`packed_ramdisk.py:56-66`），下游若要绑定 store，绑的是它，不是文件哈希。

### 4.2 卸载 OS 窗口

```bash
hdiutil detach "$OSX_MOUNT"
hdiutil info | grep -c "os-window.cdr" || true
```

判定：`detach` 成功（`"disk<N>" unmounted` / `ejected`）；计数为 `0`。

---

## 5. 从 3 GiB 缩到 2,147,000,000 B（≤2 GiB 的可写分支）

本节状态：**未执行，属未验证**（无 macOS）。`diskutil` 是否允许把这个容器缩到 2,147,000,000 B（`2147m`）、最终 `block_count`、`encoded_bytes` 都没有实测值；下面写的「预期」是按 `diskutil` 手册与本仓既有判据推出来的，不是观测结果。

### 5.1 为什么需要这一节

| 事实 | 来源 |
| --- | --- |
| 官方尺寸工具只接受 **3..1024** GiB，且只放大（`target <= logical` 直接报错） | `UniXNU/scripts/make-data-seed.py:45-46`、`UniXNU/scripts/seed-data-grow.py:92-98` |
| packed seed 的逻辑尺寸 **> 2 GiB（严格大于 `0x80000000`）** 时置 `isBig`，只保留非零页，且只由直接（store 支撑）路径服务 | `UniXNU/drivers/RamBlock/NativeRamBlock.cpp:57-60`、`:219-226` |
| `isBig && !direct` 时读仍可用，**写直接返回 `kIOReturnNotReady`**（没有易失写回退） | 同上 `:269-293` |
| `direct` 只在 `sheng-data-persist=2` 且 store 打开成功（`Fresh`/`Resumed`）时置真 | 同上 `:119`、`:122`；`direct == false` 的完整条件见 `data-store-2gib-analysis.md` §2.5 |
| mode 0（`sheng-data-persist` 缺省）时 `attachStore()` 整个分支不成立，`direct` 保持 `false` | 同上 `:88-90` |
| **≤2 GiB** 走 `RamSparseDisk`：按需分配 4 KiB 页，**无需 store 也能写**（易失） | 同上 `:227-231`、`:319`；`UniXNU/drivers/RamBlock/SparseDisk.h:44-60` |
| 阈值是开区间上界：正好 2 GiB 仍走 ≤2 GiB 分支，`0x80000001` 起走 `isBig` | `NativeRamBlock.cpp:219`；`SeedDisk.h:75` |

结论：mode 0 下要让 Data 卷**能写**，seed 逻辑尺寸必须 ≤2 GiB。官方工具只给 ≥3 GiB，所以只能「先建 3 GiB，再用 `diskutil` 把 APFS 容器缩小」。

**这条路线会改变的东西**（下游必须按 5.10 改）：

1. `seed identity` 换格式：>2 GiB 是 `SHNGSEED2`+尺寸+非零页索引，≤2 GiB 是**整盘 SHA-256**（`NativeRamBlock.cpp:236-246`、`SeedDisk.h:69-95`、`packed_ramdisk.py:38-53`）。所以这是**另一次安装**，不是同一份 seed 换大小。
2. 卷/容器 UUID 不变（缩容是改容器的自描述，不重建卷；`seed-data-grow.py:12-13` 对 grow 也是这个前提）。
3. store 窗口按页数线性缩小（`PersistOverlay.h:41-43` 的 `1 + bitmap + pages`），旧的 3 GiB 绑定全部失效。

### 5.2 先拿到 3 GiB 的 raw

`seed-data-grow.py:99` 把 3 GiB 的 raw 建在 `tempfile.TemporaryDirectory(prefix='data-grow-', dir=ROOT/build)` 里，**脚本一退出就删**。所以 raw 只能从第 4 节的 `data.dbr` 还原；DBRDISK1 只丢全零页，还原逐字节等价（`packed_ramdisk.py:14-35`、`:102-151`）。这一步与 6.3 相同，只是输出名不同。

```bash
python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.expanduser('~/unixnu/drivers/DarwinBoot/Test'))
import packed_ramdisk as pr
src = os.path.expanduser('~/seed/data.dbr')       # 第 4 节的 3 GiB 产物
dst = os.path.expanduser('~/seed/data-3g.raw')
logical, extents = pr.regions(open(src, 'rb').read())
if os.path.exists(dst): os.unlink(dst)
with open(dst, 'wb') as f:
    f.truncate(logical)
    for off, data in extents:
        f.seek(off); f.write(data)
print('raw_bytes', os.path.getsize(dst), 'logical', logical, 'extents', len(extents))
PY
stat -f%z "$HOME/seed/data-3g.raw"
```

判定：`raw_bytes 3221225472 logical 3221225472`，`stat` 同为 `3221225472`。此步**不要动** `~/seed/data.dbr`，它是 5.9 的输入。

### 5.3 记下缩容前的卷 UUID

缩容前后要证明「UUID 没变」，所以先取一次。用 6.5 同一套只读挂载，只把文件换成 `data-3g.raw`：

```bash
MP="$HOME/seed/mnt-3g"; mkdir -p "$MP"
hdiutil attach -imagekey diskimage-class=CRawDiskImage -readonly -owners off -nobrowse -mountpoint "$MP" "$HOME/seed/data-3g.raw"
diskutil info -plist "$MP" | python3 -c "import plistlib,sys; d=plistlib.loads(sys.stdin.buffer.read()); print('UUID_BEFORE', d['VolumeUUID'], 'NAME', d['VolumeName'])"
hdiutil detach "$MP"
```

判定：打印 `UUID_BEFORE <8-4-4-4-12>`、`NAME Data`。把 `UUID_BEFORE` 记下来，5.10 用它和缩容后的 `VOLUME_UUID` 逐字符对账。

### 5.4 挂 raw、取 container、看 limits

```bash
DISK=$(hdiutil attach -imagekey diskimage-class=CRawDiskImage -nomount -nobrowse \
  "$HOME/seed/data-3g.raw" | grep -o '/dev/disk[0-9]*' | head -1)
STORE=$(basename "$DISK")
CONTAINER=$(python3 - "$STORE" <<'PY'
import plistlib, subprocess, sys
store = sys.argv[1]
listing = plistlib.loads(subprocess.check_output(['diskutil', 'apfs', 'list', '-plist']))
refs = [e['ContainerReference'] for e in listing['Containers']
        if any(s['DeviceIdentifier'] == store for s in e.get('PhysicalStores', []))]
print(refs[0] if len(refs) == 1 else '')
PY
)
echo "DISK=$DISK STORE=$STORE CONTAINER=$CONTAINER"
test -n "$CONTAINER"
diskutil apfs resizeContainer "$CONTAINER" limits
```

取 `<container>` 用的就是 `seed-data-grow.py:106-116` 的同一取法：`hdiutil attach -nomount` 拿物理设备，再在 `diskutil apfs list -plist` 里按 `PhysicalStores[].DeviceIdentifier` 匹配，取 `ContainerReference`。**不要自己按 `diskN` 拼 `diskNs1`**——手册明确说卷设备名不可由容器引用推导。

判定：`DISK` 形如 `/dev/disk9`，`CONTAINER=disk9`，`test -n` 通过。`limits` 只打印约束、不动数据（手册原文：*Specifying limits instead of a size causes no action to be taken, but instead prints a range of valid values, taking into account various constraints*）；它的 `exit` 状态未验证，**以打印出来的范围为准**。若范围下限高于 2,147,000,000 B，见 5.11。

### 5.5 缩容

```bash
diskutil apfs resizeContainer "$CONTAINER" 2147m
echo "exit=$?"
```

`2147m` = 2,147,000,000 B，距硬上限 2,147,483,648 B（`0x80000000`）只剩 483,648 B。手册 SIZES 节：输入尺寸是十进制数（可带小数）加后缀，大小写不敏感、`B` 可省；`K/M/G/T` 是 10 的幂，`Ki/Mi/Gi` 是 2 的幂。所以 `2.147g` 与 `2147m` 同值；**不要用二进制后缀**：`2.147Gi` ≈ 2,305,323,696 B、`2147Mi` = 2,251,292,672 B，都已越过 2 GiB 上限。

> 来源：`diskutil(8)` 的 `APFS resizeContainer` 条与 SIZES 节（macOS 15.x），本文转引自 ss64.com/mac/diskutil.html 转载的同一份 man page 文本，**未在 macOS 上 `man diskutil` 复核**。手册对该 verb 的限定：*The operation is live, non-destructive, and does not mount or unmount any APFS Volumes*；*Shrinks are constrained by the amount of data usage by all APFS Volumes ... file content, quotas and/or reserves, snapshots, metadata overhead*；*Ownership of the affected disks is required, and all APFS Volumes on the Container must be unlocked*。

判定：`exit=0`，整段输出原样留存（含它报的目标大小/结果）。失败处理见 5.11——**不要**为了绕过失败去手改 `block_count` 或补零。

### 5.6 卸载

```bash
hdiutil detach "$DISK"
```

判定：`disk<N>` unmounted / ejected。后面全部在文件上做，不再需要挂载。

### 5.7 校验 NXSB 自描述与 Fletcher64

```bash
python3 - <<'PY'
import os, struct, uuid
p = os.path.expanduser('~/seed/data-3g.raw')
TARGET = 2147 * 1000 * 1000             # 5.5 请求的 2147m，十进制
LIMIT  = 2 * 1024**3                    # NativeRamBlock 的 isBig 阈值（严格大于才触发）

def valid(b):                           # 与 out/userdata-clean-20261112/apfs-check.py:18-25 同算法
    a = c = 0
    for w in struct.unpack('<' + 'I' * ((len(b) - 8) // 4), b[8:]):
        a = (a + w) % 0xffffffff
        c = (c + a) % 0xffffffff
    lo = 0xffffffff - (a + c) % 0xffffffff
    hi = 0xffffffff - (a + lo) % 0xffffffff
    return struct.unpack_from('<Q', b, 0)[0] == hi << 32 | lo

h = open(p, 'rb').read(4096)
bs     = struct.unpack_from('<I', h, 36)[0]      # nx_block_size
blocks = struct.unpack_from('<Q', h, 40)[0]      # nx_block_count
chosen = blocks * bs
print('magic', h[32:36], 'cksum_ok', valid(h), 'block_size', bs, 'block_count', blocks)
print('container_bytes', chosen, 'container_uuid', str(uuid.UUID(bytes=h[72:88])).upper())
assert h[32:36] == b'NXSB' and valid(h), 'NXSB missing or checksum broken'
assert bs == 4096, 'block size is not 4096'
assert abs(chosen - TARGET) <= 64 * 1024**2, 'container size did not follow the requested shrink'
assert chosen < LIMIT, 'still at or above the 2 GiB isBig threshold'
print('OK blocks=%d bytes=%d' % (blocks, chosen))
PY
```

判定：

1. `magic b'NXSB' cksum_ok True block_size 4096`；
2. `block_count × 4096` 落在 2,147,000,000 ± 64 MiB 内，且 **< 2,147,483,648**（上侧容差实际只剩 483,648 B 余量）；
3. 末行 `OK blocks=<N> bytes=<chosen>`。

预期 `block_count` 是 **524,169**（= 2,146,996,224 B）或 **524,170**（= 2,147,000,320 B）——请求值 2,147,000,000 不是 4096 的整数倍（商 524,169.92…），转换时有取整，方向未验证。**以打印值为准**，不要为了凑 2,147,000,000 去改字节。若打印值 ≥ 2,147,483,648（取整越过了上限），按 5.11 停，不要手改 `block_count`。

若 `block_count × 4096` 仍是 3,221,225,472（块 0 的 NXSB 没反映缩容），不要假设「重启后就同步」：按不可判定处理，见 5.11。`container_uuid` 是**容器** UUID（NXSB 偏移 72），不是 5.3 的卷 UUID，记录它与 `block_count` 即可。

### 5.8 截断到 block_count × 4096

```bash
python3 - <<'PY'
import os, struct
p = os.path.expanduser('~/seed/data-3g.raw')
chosen = struct.unpack_from('<Q', open(p, 'rb').read(4096), 40)[0] * 4096
before = os.path.getsize(p)
assert before >= chosen, 'file shorter than the container it holds'
with open(p, 'r+b') as f: f.truncate(chosen)
print('raw_bytes %d -> %d' % (before, os.path.getsize(p)))
PY
stat -f%z "$HOME/seed/data-3g.raw"
```

判定：`->` 之后的值与 `stat` 都等于 5.7 的 `container_bytes`。截掉的是容器自述之外的部分：容器只覆盖 `block_count` 块，缩容已保证被引用的块都在这个范围内。

### 5.9 打包成 data.dbr

```bash
mv "$HOME/seed/data.dbr" "$HOME/seed/data-3g.dbr"      # 3 GiB 原件留档，不要删
cd "$HOME/unixnu"
python3 drivers/DarwinBoot/Test/packed_ramdisk.py "$HOME/seed/data-3g.raw" "$HOME/seed/data.dbr"
stat -f%z "$HOME/seed/data.dbr"
```

`packed_ramdisk.py:142` 用 `'xb'` 打开输出，目标已存在会直接失败，所以先 `mv`。

判定（JSON 是 `packed_ramdisk.py:154-160` 打印的）：

1. `bytes` 等于 5.8 的 `container_bytes`，且 **< 2,147,483,648**（目标 2,147,000,000，余量 483,648 B）；
2. `encoded_bytes` 等于 `stat` 的值，且 ≤ 64 MiB（与第 4 节判据 4 同口径；硬上限 256 MiB，见 `SparseDisk.h:14` 的 `n>0x10000000` 与 `NativeRamBlock.cpp:211`）；
3. `sha256` 是**整盘** SHA-256（≤2 GiB 不走 `SHNGSEED2`），与 `data-3g.dbr` 的 `sha256` 不同格式、不同值——这是新 seed。

### 5.10 与第 6 节衔接

1. **6.2** 的 `assert logical == 3 * 1024**3` 换成 `assert logical == <5.8 的 container_bytes>`；
2. **6.3** 判定行里的 `3221225472` 换成同一个值（脚本本身不用改）；
3. **6.4 / 6.5** 照跑：6.4 打印的 `VOLUME_UUID` 必须与 5.3 的 `UUID_BEFORE` **逐字符相同**，6.5 的 `VolumeName` 仍是 `Data`；
4. **5.9** 打印的 `sha256`（seed identity）与 3 GiB 那份不是一回事（格式也不同），下游绑定 store 时用新的这一个；
5. 本轮记录除第 7 节要求外，再额外记：5.7 的 `block_count`、`container_bytes`、`container_uuid`，以及 5.3 的 `UUID_BEFORE`。

### 5.11 停止判据

| 现象 | 处置 |
| --- | --- |
| `limits` 下限高于 2,147,000,000 B，或 `limits` 报错 | 停：这个容器缩不到 2,147,000,000 B。原样记下输出，回第 0 节另找来路（CI 版 1 GiB）或另定尺寸 |
| `resizeContainer` 报空间不足（如 `not enough free space`）或任何拒绝缩小 | 停：把原错误逐字记进本轮记录。**不要**手改 `block_count`、不要 `dd` 补零、不要改用别的尺寸硬凑 |
| 报 `Ownership of the affected disks is required` / 权限错误 | 停：手册要求磁盘所有权。是否用 `sudo` 重试由主控决定，本节不预设 |
| 5.7 的 `block_count × 4096` 未变（仍 3,221,225,472）或校验和 `cksum_ok False` | 停：按不可判定处理并记录，不要靠改字节推进 |
| 5.9 的 `encoded_bytes` 接近或超过 256 MiB | 失败：超过打包格式硬上限（`SparseDisk.h:14`），回 5.2 重做，不要删数据凑数 |

---

## 6. 校验

### 6.1 打包大小 ≠ 逻辑大小

```bash
stat -f%z "$HOME/seed/data.dbr"
```

判定：这个值是 `encoded_bytes`（几 MB 级），**不要**拿它和 3 GiB 比。逻辑容量看 6.2。

### 6.2 DBRDISK1 头字段

```bash
python3 - <<'PY'
import os, struct
p = os.path.expanduser('~/seed/data.dbr')
magic, ver, page, logical, count = struct.unpack('<8sIIQQ', open(p, 'rb').read(32))
print('magic', magic, 'version', ver, 'page', page, 'logical', logical, 'extents', count)
print('packed_bytes', os.path.getsize(p))
assert magic == b'DBRDISK1' and ver == 1 and page == 4096, 'header mismatch'
assert logical == 3 * 1024**3, 'logical size is not 3 GiB'
assert os.path.getsize(p) <= 256 * 1024**2, 'packed size over the format bound'
print('OK logical =', logical)
PY
```

判定：`magic b'DBRDISK1' version 1 page 4096 logical 3221225472`，末行 `OK logical = 3221225472`。

### 6.3 还原 raw（稀疏）

```bash
python3 - <<'PY'
import os, sys
sys.path.insert(0, os.path.expanduser('~/unixnu/drivers/DarwinBoot/Test'))
import packed_ramdisk as pr
src = os.path.expanduser('~/seed/data.dbr'); dst = os.path.expanduser('~/seed/seed.raw')
logical, extents = pr.regions(open(src, 'rb').read())
if os.path.exists(dst): os.unlink(dst)
with open(dst, 'wb') as f:
    f.truncate(logical)
    for off, data in extents:
        f.seek(off); f.write(data)
print('raw_bytes', os.path.getsize(dst), 'logical', logical, 'extents', len(extents))
PY
```

判定：`raw_bytes` 与 `logical` 同为 `3221225472`。

### 6.4 魔数 + APSB 页 + 页内 16 字节 UUID

```bash
python3 - <<'PY'
import os, struct, uuid, sys
sys.path.insert(0, os.path.expanduser('~/unixnu/drivers/DarwinBoot/Test'))
import packed_ramdisk as pr

def valid(b):                      # obj_phys 的 fletcher64，与 out/userdata-clean-20261112/apfs-check.py:18-25 同算法
    a = c = 0
    for w in struct.unpack('<' + 'I' * ((len(b) - 8) // 4), b[8:]):
        a = (a + w) % 0xffffffff
        c = (c + a) % 0xffffffff
    lo = 0xffffffff - (a + c) % 0xffffffff
    hi = 0xffffffff - (a + lo) % 0xffffffff
    return struct.unpack_from('<Q', b, 0)[0] == hi << 32 | lo

logical, extents = pr.regions(open(os.path.expanduser('~/seed/data.dbr'), 'rb').read())
hdr, apsb = None, {}
for off, data in extents:
    for at in range(0, len(data), 4096):
        page = bytes(data[at:at + 4096])
        if len(page) < 4096: continue
        index = (off + at) // 4096
        if index == 0: hdr = page
        if page[32:36] == b'APSB' and valid(page):
            apsb[index] = str(uuid.UUID(bytes=page[240:256])).upper()
assert hdr is not None, 'block 0 is not present in the packed extents'
print('NXSB', hdr[32:36], 'cksum_ok', valid(hdr), 'block_size', struct.unpack_from('<I', hdr, 36)[0])
print('APSB pages', len(apsb), sorted(apsb))
assert hdr[32:36] == b'NXSB' and valid(hdr), 'NXSB missing or bad checksum'
assert apsb, 'no checksum-valid APSB page'
assert len(set(apsb.values())) == 1, 'APSB pages disagree'
print('VOLUME_UUID', next(iter(apsb.values())))
PY
```

判定：`NXSB b'NXSB' cksum_ok True block_size 4096`；`APSB pages` ≥ 1 且所有页 UUID 相同；末行打印的 `VOLUME_UUID` 留给 6.5 对账。

### 6.5 UUID ↔ 字节绑定（FS 视图对账）

```bash
MP="$HOME/seed/mnt-seed"; mkdir -p "$MP"
hdiutil attach -imagekey diskimage-class=CRawDiskImage -readonly -owners off -nobrowse -mountpoint "$MP" "$HOME/seed/seed.raw"
diskutil info -plist "$MP" | python3 -c "import plistlib,sys; d=plistlib.loads(sys.stdin.buffer.read()); print('VolumeUUID', d['VolumeUUID']); print('VolumeName', d['VolumeName'])"
ls -ln "$MP" | head -5
hdiutil detach "$MP"
```

判定：
1. `VolumeUUID` 与 6.4 的 `VOLUME_UUID` **逐字符相同** —— 这就是「UUID 与磁盘字节绑定」的证据：该 16 字节位于校验和有效的 APSB 页 `[240:256]`，且 `diskutil` 从同一份字节里读出同一个值；
2. `VolumeName` 为 `Data`（`make-data-seed.py:52` 的 `-volname Data`）；
3. `ls -ln` 的 uid/gid 见第 9 节，不在这里修正。

---

## 7. 回传

### 7.1 拷回共享目录

```bash
OUT="$SHARE/enuma/UniXNU-enuma/out/data-seed-macos"
mkdir -p "$OUT"
cp "$HOME/seed/data.dbr" "$OUT/"
shasum -a 256 "$OUT/data.dbr"
```

判定：打印 64 位十六进制，记作 `<MAC_SHA256>`。

### 7.2 Windows 侧核对

```powershell
Get-FileHash -Algorithm SHA256 "D:\Code\PortingiOS\enuma\UniXNU-enuma\out\data-seed-macos\data.dbr" | Format-List
```

判定：`Hash` 必须等于 `<MAC_SHA256>`（占位，按 7.1 实际输出填）。不等即传输损坏，重拷，不要重跑第 4 步。

### 7.3 记录

把 7.1 的哈希、`encoded_bytes`、`sha256`（seed identity）、`VOLUME_UUID` 与 6.4 的 APSB paddr 一起记进本轮 `porting.toml`/README。`data.dbr` 本身不要 `git add`。

---

## 8. 失败排查（一行处置）

| 现象 | 处置 |
| --- | --- |
| `hdiutil: create failed - Resource busy` | 该 raw 已被别的挂载占用：`hdiutil info \| grep -i os-window`，对列出的 `/dev/disk<N>` 执行 `hdiutil detach /dev/disk<N> -force`，再重跑 |
| `hdiutil attach` 报 `-mountpoint` 不可用 / 路径已存在 | 只有 dd 回退那条命令带 `-mountpoint`：`ls /Volumes/OSX` 必须为空；仍失败则改用 `MP=$HOME/seed/mnt-os`，把 `-mountpoint` 换成它，并让 `OSX_MOUNT` 指向它（第 4 步路径随之改变） |
| `diskutil apfs resizeContainer` 失败 | 先 `diskutil apfs list` 确认容器存在且无快照；最常见原因是 raw 没被 `truncate` 到目标大小（`seed-data-grow.py:101-105`），核对 6.3 的 `stat -f%z ~/seed/seed.raw` |
| 第 4 步 `refuse to overwrite an existing installation seed` | `mv "$HOME/seed/data.dbr" "$HOME/seed/data.prev.dbr"`，不要删（旧的可能是已绑定下游的唯一一份） |
| 第 4 步 `not an IPSW OS volume` | 回 3.6 检查 `sbin/launchd` 与 `private/var`；多半是 3.5 挂错了卷（差集不止一项）或漏了 `-owners off` |
| `ls -ln` 显示 `99 99` | 当前挂载用了 `-owners on`，而 seed 里存的 uid 在 VM 里不存在。用 `-owners off` 重挂查看，**不要** `chown`/`chmod -R`（会改角色语义，见第 9 节） |
| 6.5 只读挂载报卷不一致 / dirty | `seed-data-grow.py:118` 是 `hdiutil detach -force`，容器可能留在 dirty 状态。去掉 `-readonly` 重挂即可（`seed.raw` 是临时还原物，允许被改写）；不要试图修 `data.dbr`，那要回第 4 步重做 |
| 空间不足 / `No space left on device` | 删 `~/seed/044-76040-038.dmg` 与 `~/seed/os-window.cdr`（第 3 步已完成即可），保留 `data.dbr` 与 `seed.raw` |
| `--gib must be in 3..1024` | 工具下限是 3 GiB，见第 0 节；不要改成 1 GiB 硬跑。要 ≤2 GiB 的 seed 走第 5 节（3 GiB 建完再缩） |

---

## 9. 注意事项

1. **所有权会丢**。`make-data-seed.py:71` 用 `shutil.copy2`（保 mode/mtime，不保 uid/gid），磁盘上存的是 VM 当前用户的 uid。设备侧 `mobile` = 501、`root` = 0 的归属必须在镜像/运行时环节处理，不在本命令单范围内。
2. **seed UUID 每次不同，变了必须全链重绑**。`newfs_apfs` 每次生成新卷 UUID，`seed_identity`（`packed_ramdisk.py:56`）与 store 窗口都随之改变；不是「换一份文件」而是「换一次安装」。`make-data-seed.py:4-5` 明确要求同一份 seed 后续复用。
3. **role = 0 与真实 iOS Data 卷的 `0x40` 不同**。`hdiutil -fs APFS` 建出的是普通 APFS 卷，没有 Data 卷的 `APFS_VOL_ROLE_DATA`(0x40) 标记；驱动侧若按 role 分辨，需要额外处置，不要在 macOS 上手工改。
4. **`-fs APFS` 是大小写不敏感**。不加 `-s`，不要用 `Case-sensitive APFS`；CI 门版本用的是 case-sensitive（`data_seed_macos.py:189`），与官方工具不是一回事。
5. **APFS 格式化器版本即 macOS 版本**。本文的预期字节/耗时对应 `newfs_apfs` 2332.140.13.704.3（macOS 15.x）；换版本请重开一节记录。
6. **Apple 派生产物不入库**。`data.dbr`、`seed.raw`、`os-window.cdr` 只放本机 `out/`（`UniXNU-enuma/.gitignore` 已忽略 `/out/`），禁止上传 GitHub / CI artifact / Release。
7. **不要重跑第 4 步覆盖**。脚本会拒绝；若确有需要，先 `mv` 留档，因为旧的 seed 可能已与下游 policy/store 绑定。
8. 本文不含任何设备标识；6.4/6.5 打印的 UUID 是你本机这一次生成的，记录时按需截断。
