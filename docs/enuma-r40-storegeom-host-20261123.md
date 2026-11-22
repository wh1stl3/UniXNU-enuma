# enuma r40：启动路径存储几何快照

`self-checked`，仅主机。候选：`out/ufs-sm8250-storegeom-20261123-r40/`。
**本候选不写任何存储**，不追加 UFS 命令，不打开 store、不改 GPT、
返回值、隔离处理或 boot args。默认 recipe/series 未接入。

## 数据流和输出

- r39 `libShengUfs.a` 原始输入为 ShengUfs `38c19c2b` 的 enuma
  startroot WIP r11 本地源码（BSD-2-Clause-Patent，归档
  `d2a75264…`）。`RootLayout.h:59–105,130–158,206–218` 原本通过
  `hostRead4k()` 读取并校验 LUN 0 主 GPT 头和分区表，解析 `userdata`
  与首块 manifest。r40 输出目录 `source/NativeUfs.cpp:2907` 只在既有
  `findRootLayout()` 成功后复制返回的字段；没有改解析器或错误分支。
- r39 `libRamBlock.a` 保持不变。原配源
  `out/ufs-sm8250-startroot-mode0-20261118-r1/self-check/ram-merged/NativeRamBlock.cpp:214–260`
  在导入 seed 后发布 `native_ram_block_bytes`（逻辑字节数）和
  `native_ram_block_ready`。探针只读这两个既有字段；未就绪不猜值。
  `PersistOverlay.h`（同目录，BSD-2-Clause-Patent）提供既有
  `persist::windowBlocks()`，与 `NativeRamBlock.cpp:97–101` 的消费者一致。
- `source/NativeUfs.cpp:1712–1723` 共用原 reserve 的 boot-arg 解析；
  探针不碰正常路径的 reserve 缓存。`sheng-log-reserve` 缺省或
  超过 16384 MiB 时为 1024 MiB。`source/bsd_init.c:1265–1275,1317–1319`
  由 `bsdinit_task()` 内既有 timebase 探针的 `seq == 0` 路径调用，
  在 `load_init_program(p)` 之前。未另设触发计数。

```text
enuma-sg: begin
enuma-sg: ud first=<u32> last=<u32>
enuma-sg: crc hdr=<hex32> entries=<hex32>
enuma-sg: manifest status=<u32> magic=<hex32>/<hex32>
enuma-sg: seed=<u64> reserve=<u64> blocks
enuma-sg: win start=<s64> len=<u64>
enuma-sg: chk in_ud=<0|1> below_first=<0|1> hits_root=<0|1>
enuma-sg: no-new-ufs-io
enuma-sg: end
```

未捕获布局时用一行 `ud n/a; crc: n/a; manifest n/a; win n/a`。
有布局而 seed 未就绪或 manifest 无效时，窗口三行改为 `win n/a`
并给原因。现有启动失败若在到达探针前终止，则没有 `enuma-sg` 输出。

所有 LBA、seed、reserve 和窗口长度以 4096 B 块计。令 `P` 为 seed
逻辑字节数 / 4096，`R` 为实际 reserve MiB × 256，窗口长度
`N = 1 + ceil(P/32768) + P`（header、bitmap、Data）。窗为
`[last + 1 - R - N, last + 1 - R)`；`userdata` 为 `[first, last+1)`；
根前缀为 `[first, first + manifest.imageBytes/4096)`，仅使用
现有解析器已认可的对齐字节数。负起点按有符号数打印。

| 输出 | 判读 |
| --- | --- |
| `ud` 与两 CRC | 既有解析器接受的主 GPT 快照；非备份对照或重新读取。 |
| `status=0 magic=474e4853/544f4f52` | 现有解析器认可 `SHNGROOT`；不等于 store 几何获 owner 绑定。 |
| `in_ud=1 below_first=0 hits_root=0` | 窗口落在 `userdata` 内且与 manifest 根前缀不相交；不替代正式 store 须保留的 1024 块根后间隙、其他 gate 或持久写授权。 |
| `in_ud=1 below_first=1` | 与分区相交但越界；`in_ud` 是重叠，不是完全包含。 |
| `hits_root=1`、`in_ud=0`、或 `win n/a` | 不据此放行；分别为根重叠、完全不相交、或缺可信输入。 |

不读容量/备份 GPT：两者不在 r39 正常根路径的内存快照里。额外请求
若超时会经 `RootCommands.h:89–94` 隔离正常根卷共用的 host。
后续宜在不挂接活动根卷、另获设备授权的独立只读诊断中取得 READ
CAPACITY、备份头和表 CRC，并与主 GPT 交叉核对。不使用历史 LUN
大小或主 GPT 的备份指针冒充实测容量。

## 机械证据

WSL root，从设备仓运行：

```sh
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  python3 -B scripts/build-enuma-r40-storegeom.py
```

最终构建 exit 0；先 native link，再 prelink，均无 undefined（包括弱符号）。
首次链接本身成功，机器检查误用了 `_bsd_utaskbootstrap` 而停止，最终对
实际调用者 `_bsdinit_task` 检查通过。两张图各有 11 个格式串，每个恰好
一次，且各有唯一 `bl _enuma_storegeom_report`（`0xfffffff00bce1540`），
位于既有零序号分支内、在 `bl _load_init_program`（`0xfffffff00bce15c8`）之前。
报告函数只有 `_printf` 和 `_PE_parse_boot_argn` 外部调用，无间接分支调用。
真实 formatter 用 7 个合成输入做 UBSan 检查（正常、不就绪、无快照、
无效 manifest、根重叠、部分越界和负起点），exit 0、均 ≤10 行且每行 <80。

| 文件 | r39 SHA-256 | r40 SHA-256 | r40 字节 / 差值 |
| --- | --- | --- | ---: |
| `NativeUfs.o` | `19e6b7ccb2e1704e84afef771a9f1acba60a28a5761a672d4f867d10e9f4c28c` | `496b5c9364962ffe6baa3fc97bc855ccb90379687b6282a07b78d5213f4eb0ce` | 523392 / +6288 |
| `bsd_init.o` | `cd54914a7be410887172aedde462d9648f6c7eaebf84fd9c67aca5b8ecfce656` | `87793d86b586003a4765533717380ce72895457a020da7095a1c98a9e2289632` | 180040 / +24 |
| `libShengUfs.a` | `d2a75264af6dcec1f10fbf04aeab3b1633cbf5007d8ffd6bebc623216919ebf0` | `15d94bec1ab23732812d36740ad86d4327187571e51759eb69e5eb3a41d48be1` | 526528 / +6320 |
| `native.macho` | `217b433536c136c1e50a73bf3dd7b1e4baa940a975feefe945c017b533811223` | `ee6c4682914be771999b5d592d98774631a369d4e3ba7ba4ab1904466b811e5e` | 91909192 / +984 |
| `prelink.macho` | `8ca90d32e533e2135d013578560adfc56589e0c911382b7ff9f3ee405ae11ba0` | `b33bab4c434bcc9b94c77a9bff566eef90f3d5da9c2f950b6c1bf622e1282e58` | 124751872 / 0 |
| `kernel.macho.adt` | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | 同 r39 | 14128 / 0 |
| `payload.img` | `aa434989b592137543701de2f38d360388983304fcbadbcb467c7ac45eb83af4` | `33295a6895bd4bc9e24964abe372631179df8bad41b0f37d6b049bd7bbea2dc6` | 167772160 / 0 |
| `boot.img` | `65d896e954e871651cf48bf00614154911e440de477e8f9f0ebb7162a03b83f6` | `f2937ed83a7c66a6481bd8d7f6eb5daa34c77d0d747c481198b4f27717c3bbcf` | 169951232 / 0 |

1005 个其他 filelist 输入、14 个其他直链归档、r39 九件顶层输入和
上游 HEAD（`693f5d9cae8a408dd18b39f3f9fdc4228c934241`）前后不变。
`NativeUfs.o` 是 ShengUfs 归档的唯一成员；FAT 唯一变化的文件为
`Payloads/kernel.macho`，其内容等于新 prelink；ADT 逐字节等于 r39。
两份 boot 的 ramdisk 均与各自 FAT 相等；带填充的 Android kernel、
尾部和除镜像 ID 外的头部逐字节相同。完整证据见输出目录中的
`candidate-manifest.json`、`commands.json` 和 `logs/`。

在 `UniXNU` 工作目录运行
`python3 -B scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`：
15 个 area，exit 0。

未上机，无设备、claim、独立 verifier 或 deep review。本板是否能走到
该打印点、实际字段值、LUN 容量、备份 GPT、介质所有权、持久 Data 与
写入安全均未验证；阶段和既有写入门禁不变。
