# enuma r22：扩大 XNU 持有内存窗口并设 sleep-disabled（2026-11-22）

`self-checked`，仅主机候选：`out/ufs-sm8250-launchd-keystore-20261122-r22/`。
未执行设备操作，未提升 bring-up 阶段。

## 依据与前置核查

- r21 刷入 boot 后首启（派单转录）：0–150 秒只见 `st=0/sig=0` 或 `sig=1`；
  securityd、akd、keybagd、backboardd、runningboardd、tccd 均见成功 exec。
  约 180 秒起成批 `st=9 sig=9`，包括 nfcd、tccd、homed、backupd、
  corespeechd、mobiletimerd、routined、securityd，且反复起落。录像未见
  watchdogd、jetsam/memorystatus 杀进程日志或 `comm=SpringBoard`，无图形。
  `sig=9` 不标识发送者；扩窗用于测试内存压力假说。
- 同 donor 的 [sirius](../../../UniXNU/docs/zh/devices/sirius-huajifruit.md#memory)
  （UniXNU `693f5d9c`，第 231–233 行）已到 SpringBoard，并用了 `0xaa000000`；
  这是诊断取值依据，不是 enuma 的分配证据。
- 加入 bring-up 默认值 `/defaults/sleep-disabled = 1`，参考官方
  `docs/zh/devices/evb10.md:52`、`sirius-dddqmmx.md:510`、`orangepi5.md:41`
  （均为 UniXNU `693f5d9c`）。这是第二项行为变量，主机回读不证明
  enuma 实际不再停驻，也不证明 suspend/resume 已实现。
- **物理几何允许，实际分配未验证。** `porting.toml:60` 的 live FDT 给出约
  7.9 GiB，其中 `[0xc0000000,0x180000000)` 是 3072 MiB。若能沿用旧观测基址
  `0xc007c000`，2720 MiB 到 `0x16a07c000`，仍在同一物理段内，尾余约
  351.5 MiB，与已知固定保留范围无交集。DarwinBoot `AllocateWindow`
  (`DarwinBoot.c:519–529`) 只从当次 `EfiConventionalMemory` 连续区间取满足
  2 MiB congruence 的地址，再 `AllocatePages(AllocateAddress)`。缺 r21 同路径
  分配时的 EFI map；加载输入和固件分配造成的碎片可导致 `NO WINDOW`，不会
  回退到 512 MiB。窗口也可能移到别处或跨过 UFS 的单 DRAM bank 边界而被拒绝。
- **UFS DMA 未验证。** `docs/ufs-reserved-memory-audit.md:383` 的 32 位门禁
  针对 DMA buffer，不是整个 XNU 窗口；带所有权检查的 warm 路径核对
  `CAP` bit 24（非 `HCS`）和 SMMU 宽度，且整个 DMA 缓冲必须在可用窗口内。
  若窗口仍从 `0xc007c000` 起，虽跨 4 GiB，仍留有低地址可用空间；
  现有分配未保证挑选低于 4 GiB 的页。若窗口全部移到 4 GiB 以上，
  需要 32 位访问时就无合规落点，UFS 根发布会受阻。旧 DMA `0xc8a10000`
  不是 r22 的证据；地址宽度、实际分配及旧队列/保留区相交情况均未验证。
- **RamBlock 无已知新增冲突。** r21 的 FAT 根匹配是 UFS OS window；同一
  1,142,976 B packed scratch Data 仍随 payload 传入。DarwinBoot
  `Boot` (`DarwinBoot.c:722–735,754–759`) 先分配窗口再在窗口内排布并复制
  packed Data，扩容不增加该前缀的大小。旧 ABL payload 放置在
  `0xa0000000–0xb0000000` Kernel reservation，不与上述兼容窗口示例相交；
  r22 实际落点、UFS 和 Data 挂载均未验证。

## ADT 与机械证据

**本轮有意打破 ADT 固定，记录新旧 ADT 哈希。** 从冻结的 r21 board 副本、
`hardware.dtb` 和本地身份配置，用官方 `unixnu.devicetree.generate` 重生
ADT，绕过 r7 的 r6 ADT 注入。`devicetree.py:319–323` 生成窗口属性，
`:378–380` 生成 `/defaults`，`:275,280–287` 把 `[adt.defaults.u32]` 编为
LE32 属性。全树属性路径和原始值比较，仅窗口大小、`sleep-disabled` 和
生成器的 256 B `random-seed` 有变化。最终 FAT 经 `mtype` 回读并断言：
`/chosen/darwinboot-memory-size` = LE64 `0xaa000000`（2,852,126,720 B），
`/defaults/sleep-disabled` = LE32 `1`；r6 / r21 分别为 `0x20000000` 和缺失。

| 产物 | 字节 | SHA-256 |
|---|---:|---|
| r6 / r21 FAT ADT | 14,048 | `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059` |
| r22 FAT ADT | 14,088 | `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5` |
| r22 payload | 167,772,160 | `f984a976c52a00cb2ad2cfe266739767095cdbff1d7c1c2c0ced597939742eb4` |
| r22 boot | 169,951,232 | `646e7d8dd2d1d3e4ae25d02c9b34cced7e1a1e7f20f34506cc9437b34fb360e7` |
| r21 payload（未变） | 167,772,160 | `546ba82a1e7ae2b1427f76c86d91ec84df109345bf7019c41166364d7fcf03de` |
| r21 boot（未变） | 169,951,232 | `cb02ded1039189582dfb1458a218068c93cdcee152151b4708353d0c2320c23f` |
| r21 native（复用，无重链） | 91,875,952 | `b505a024c6f8d226826ad56a6c6c0cec8884dc352c8b3f99dfd4e336adc6c28f` |
| r21 prelink = r22 FAT kernel | 124,719,104 | `5c24e268ad59309c08629e6b3a5a770386b364ae072e61052fa7581c02f887bd` |

- 对 r21 的 1006 个 `link.filelist` 条目和 14 个诊断对象目录文件去重后，
  1018 项逐一复算 SHA-256，构建前后全同。完整逐项清单
  `r21-link-inputs.sha256`：`63cf4b39b0492d6fcdf0db3554575c807a51ff9545433ae7d988041f86b85cee`。
  `kern_exec.o`：`67f3b058209da04d6125a72d6f5b56cb7712ca45d07490`。
  `kern_exit.o`：`2481cac19e4b7919e3099db51059f8d0fca40bdcb16c3bbe417e04e333eea64d`。
- `mcopy` 只替换 r21 FAT 副本中的 ADT。全卷文件列表相同；kernel、
  trustcache、scratch Data、`unixnu.toml`（含 boot-args）回读逐字节相等。
  `cmp -l`：payload 共 2,728 个不同字节，扇区差异限于 FAT32 FSInfo
  (1)、两份 FAT (507/512/1145/1150)、ADT 目录项 (1320)、新 ADT 数据
  (247304–247305、247309、247321–247331)；`mshowfat` 的 ADT 链由
  60904–60910 改为 61501–61507。官方 `bootimg.build` 打包并验证：boot
  除偏移 `2179072` 后的载荷 delta 和 Android header v1 ID（SHA-1）外全同。
  固件、shim、Android DTB、boot header 其余字段、槽预算未变。
- 打包 exit 0；Windows Git OpenSSL 复算上表 SHA-256 全同。入口与 base pin
  如下；复跑选择新 `--out`，ADT 随机种子不同，验证结构和不变量，不要求
  新镜像哈希与表逐字相同。

```sh
# WSL Ubuntu-22.04 root，设备仓目录；保持 UniXNU 693f5d9c 只读。
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r22-memory-window.py \
  --dtb /root/enuma-step10/inputs/enuma.dtb
# verifier 复跑时追加 --out out/ufs-sm8250-launchd-keystore-20261122-r22-verify
```

## 上机后判读（本轮未执行）

先确认实际 hand-off `owned=0xaa000000`、UFS DMA `check=PASS` 和同一根卷、
Data 路径正常，再比较 r21 / r22 相同墙钟区间内同批进程的 `sig=9` 密度。

| 观察 | 判读 |
|---|---|
| `sig=9` 密度明显下降 | 支持内存压力假说，不证明由 jetsam 发信号。 |
| 密度无变化 | 不支持该假说，但不排除内存压力。 |
| `NO WINDOW`、UFS DMA/根发布失败或不足以比较 | 本轮不能判读内存压力。 |

由于同时加入 `sleep-disabled`，下降不能单独归因于窗口扩大；区分两项
需要单变量对照。先前仅扩大窗口的主机镜像保留于同路径后缀 `-memory-only`，
不是此次 r22 交付。

可分配窗口和实际落点、DMA/SMMU 宽度通过、Data/根挂载、服务稳定性、
SpringBoard、图形和持久化均未验证；设备侧前交 `deep_reviewer`。
