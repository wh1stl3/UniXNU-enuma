# enuma r44：在 r43 单次报告中重打 text-fixup 计数

`self-checked`，仅主机。候选 `out/ufs-sm8250-matchcnt2fx-20261123-r44/`；
基线 r43 `a01dbc3`。不改 fixup 解析、匹配、写页、失败分支及早期日志
阈值，不改 ADT、r43 的五类计数、`enuma-sg:`/`enuma-tb:` 或采样时机。

## 数据与位序

- r43 `ubc_subr.c:6097–6098` 已有 `cs_text_fixup_parsed` 和
  `cs_text_fixup_applied`；`:6204` 在早期解析完成后保存有效条数，
  `:6230` 原子递增 applied。r44 生成源码对应 `:6097–6098,6205,6231`。
  Applied 是执行条目写页的次数，不是唯一条目数、唯一页数或缓存文件数。
- `package/EnumaFixupReport.inc:3` 新增一字节位图。生成的
  `source/bsd/kern/ubc_subr.c:6229–6236` 在原有成功 `memcpy` 和原有
  applied 递增之后，以 release 原子 OR 设置 bit `i`（仅 `i<8`）。
  失败或跳过不置位，重复应用同一条不改变其位；原已打印次数判断仍
  使用同一次递增返回值。两张 Mach-O 均可见 `ldxrb/stlxrb` 和读取侧 `ldarb`。
- 机制本身允许 32 个有效条目且会压缩无效条目。r44 只为此冻结候选
  解释位序：主机构建解析 `/chosen/text-fixups` 原始 NUL 分隔属性，
  核对四条的顺序并确认 ADT/载荷 boot-args 无 `text-fixup0..7` 覆盖。
  样本 `parsed!=4` 时打印 `bits=n/a`，不拿压缩后的索引解释原始位序。

| ADT 条目（从 1 开始） | 位 | basename + 文件偏移 |
| ---: | ---: | --- |
| **1** | **bit 0 / `0x01`** | **AW：`dyld_shared_cache_arm64.15+0x421e8bc`** |
| 2 | bit 1 / `0x02` | `dyld_shared_cache_arm64.13+0x1b05bec` |
| 3 | bit 2 / `0x04` | `dyld_shared_cache_arm64.13+0x1b05b08` |
| 4 | bit 3 / `0x08` | `BTAudioHALPlugin+0x38bec` |

## 采样与判读

`source/bsd/kern/EnumaBbScan.inc:135` 在 r43 原单次分支中，紧接
`enuma_matchcnt_dump()`、释放回调前调用 `enuma_fixup_report()`。
仍由首次观察到 `pid=34 comm=backboardd` 成功 exec 后安排的 30 内核秒
截止任务触发，不加 timer、报告次数或等待。以下三条格式实际每次
只打印两行；原 `enuma-mt:` 最多 6 行，合计最多 **8 行**。

```c
"enuma-fx: parsed=%u applied=%u\n"
"enuma-fx: bits=0x%02x\n"
"enuma-fx: bits=n/a\n"
```

无 `cache=`：现有机制不保留最近命中的 basename；配置表中的名字
不是独立运行时记录。读取端先 acquire 读取位图，再读 applied，二者
不是事务快照；采样可落在其他 CPU 已计数、尚未置位的窗口。

| 同次读数 | 判读 |
| --- | --- |
| `parsed=0 applied=0 bits=n/a` | 没有报告到有效解析条目或页写；不能从零值判断为何没有条目。 |
| `parsed!=4`（非零） | 部分或非预期解析，`applied` 仍只代表总页写；不判 AW。 |
| `parsed=4 applied=0 bits=0x00` | 四条有效，采样未观察到任何应用。 |
| `parsed=4 applied>0`、`bits & 1 == 0` | 有页写，但采样未观察到 AW；可能是其他条目，或撞上计数先于置位的窗口。 |
| `parsed=4 applied>0`、`bits & 1 != 0` | AW 条目至少写过一次；不证明用户态执行了替换后指令或死锁解除。 |
| 无报告，或出现 `parsed=0, applied>0`、`applied=0` 却已有命中位 | 不下运行时结论；后两种不符合该候选正常计数关系。 |

## 机械证据

在设备仓，用 WSL root 和 Python 3.11：

```sh
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r42-matchcnt.py --r44
```

构建 exit 0。只换 `ubc_subr.o`、`kern_exec.o`；其余 1004 个 filelist
条目（含 `IOUserClient.cpo`）、15 个直链归档和 prelink donor 的哈希
未变，r43 冻结文件与原对象哈希未变。两张 Mach-O 中三条 `enuma-fx:`
和六条 `enuma-mt:` 格式串各唯一，报告调用在同一个单次分支各一处，
紧随原报告且在释放前；两张图 `llvm-nm -u` 和原始 nlist 均无
undefined（含 weak）。逐项输入哈希及调用点见 `candidate-manifest.json`
和 `logs/calls-*.macho.log`。FAT 唯一变化成员为内核，ADT 文件及 FAT
内 ADT 与 r43 逐字节相同；两份 boot 的 ramdisk 分别等于各自 FAT，
其前缀仅镜像 ID 改变。

| 文件 | r43 SHA-256 | r44 SHA-256 | r44 字节 / Δ |
| --- | --- | --- | ---: |
| `ubc_subr.o` | `3b3256855e3992e4e5c68098ec90f7740e3834c0e3b13dcd86fa9869cea3faa7` | `1b510846e44bf7136011c52b23801fe77f6b1302f1affacded28de3c2ca3f930` | 277288 / +1664 |
| `kern_exec.o` | `eb14289d16b757952a85817c2ccb1d3d79991f0d7eeb3d51cfd2f0224dbfe839` | `92298b1105b52e3c463a7f5cef885d5ebee33134c2cbc9666e6ea9acfff86c0a` | 538416 / +136 |
| `native.macho` | `98525b03552e0c48bfdca7f3ec70a85030f35596c283255ddcf229b99ce74668` | `00ecb1a2ff72fed7b8a25d7739d185bfbf366b81b99a686f449dd88097c097da` | 91909760 / +96 |
| `prelink.macho` | `cb28043902ba95dde91d29a081fa0a9de12c73f7cd296b2eee0fd9e29cefeef9` | `98f16cda0a77fdec183f4f5c3618e6e4f7c00c8ca2af73a8768d158d720737a9` | 124751872 / 0 |
| `kernel.macho.adt` | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | 同 r43 | 14128 / 0 |
| `payload.img` | `c1a1f7eea0ab774bf4d6a6aa827a4ba90777c90832a04ca677398fe42c612b67` | `caab11ce6726170ed35106124175db4ab743d13ab94111f41fdd816e4e7a8f6b` | 167772160 / 0 |
| `boot.img` | `0cde0acb9ac5d310bb9cdc8631e844979c26394bec09e1d9382f2852b17e4660` | `b997b33af1d85f67da89cf5b3817f53ef5545a41605b856882288bb322601b4e` | 169951232 / 0 |

主机 UBSan smoke 用真实报告片段测试了 `n/a`、零应用、其他条目命中及
AW 命中，四组均只输出两行。未上机；实际 parsed/applied、AW 命中
与报告是否可达尚未验证。无独立 verifier 或 deep review，不提升阶段。
