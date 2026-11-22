# enuma r43：扩展 IOKit 计数，改用 exec 后单次采样

`self-checked`，仅主机；候选 `out/ufs-sm8250-matchcnt2-20261123-r43/`。
基线为 r42（`03b1e5d`），官方基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。

## 与 r42 的差异

r42 的 `M/N/O` 扩为 `M/N/O/P/I`。以下为候选
`source/iokit/Kernel/IOUserClient.cpp` 行号，五类各一处，M 的单个和多个
查询各有独立汇合点，因此实际共六处：

| 项 | 函数和计数行 |
| --- | --- |
| M | `internal_io_service_get_matching_services:2709`、`internal_io_service_get_matching_service:2793` |
| N | `internal_io_service_add_notification:2881` |
| O | `is_io_service_open_extended:4382`，保留原 `entry/entry_bb` |
| **P** | **`internal_io_service_match_property_table:2627`**，`bin` 和 copyout 成功的 `ool` 在此汇合，先计数再走既有 `CHECK` 和 `passiveMatch` |
| **I** | **`internal_io_service_add_interest_notification:3157`**，32/64 位 wrapper 完成 ref 校验后在此汇合，先计数再走既有 `CHECK` 和 `registerInterest` |

每处一次 `proc_selfpid()`；保留 4 个固定 PID（34、5、56、66）、28
个不回收的开放寻址槽及 `other`。固定 PID 最多四次比较加一次 relaxed
原子递增，其他槽常见一次加载，首次登记使用 CAS，最坏探测 28 槽。
计数路径不分配、不加锁、不睡眠、不打印。不改返回值、匹配/open 行为、
`kern_exec`/`bsd_init` 启动顺序、UFS、`enuma-sg:` 或 `enuma-tb:`。

## 采样

r42 依赖最后一个周期槽，r43 不再依赖它。原成功 exec 路径
`source/bsd/kern/kern_exec.c:2123–2130` 仍调用 `enuma_fb_arm`；
`source/bsd/kern/EnumaBbScan.inc:179–185` 只在观察到
`pid=34, comm=backboardd` 并首次原子置位时，给**同一回调函数**
单独排一个 `THREAD_CALL_OPTIONS_ONCE` 任务。其截止时间在 exec 钩点
之后计算，是当前 `mach_absolute_time()` 加 30 内核秒；任务用非空
`param0` 区分，`param1` 为自身句柄。回调的 `:130–135` 分支打印并释放
自己的句柄，不重排；原周期任务的排程、计数和释放不变。单次分配及排队
在 exec 插桩，不在 IOKit 热路径；即使原周期回调已结束，也不妨碍排队。

构建树 XNU `osfmk/kern/clock.c:1642` 基于 `mach_absolute_time()` 计算
截止时间；`thread_call.c:1217,1298,2019` 传递该绝对截止时间并在尚未
到达 soft deadline 时不执行；`:1098` 的 `thread_call_free` 支持活动
调用结束后释放。因此打印蕴含已观察到目标 exec 且已过至少 30 内核秒。
调度可以晚于截止时间；没有目标 exec、到期前复位或回调未获调度，不应把
无报告解释为零。计数自启动累计，**不是**仅统计 exec 后的 30 秒。

真实格式串如下；`t` 是 `mach_absolute_time()` 换算的整内核秒，不是
墙钟，不能与录像秒相减。

```c
"enuma-mt: t=%u all=%x/%x/%x/%x/%x\n"
"enuma-mt: other=%x/%x/%x/%x/%x\n"
"enuma-mt: bb(34)=%x/%x/%x/%x/%x\n"
"enuma-mt: sb(5)=%x/%x/%x/%x/%x\n"
"enuma-mt: A%.68s\n"
"enuma-mt: B%s\n"
```

顺序均为 `M/N/O/P/I`。将可选的 A、B 行去掉标签后拼接，按 45 字符
切分：5 位 PID 加五个 8 位计数，全部为十六进制、无截断。除 34、5
外（含 56、66），按五项之和降序、PID 升序取前三。最多 6 行，最长
79 字符（不含换行）；分开打印 `all` 和 `other` 以容纳 32 位满值。

## 判读

| 同轮 `bb(34)` | 结论 |
| --- | --- |
| `M>0, O=0` | 排除 B：走了查找，未到受测 open。不证明未匹配到服务。 |
| `N>0`、`P>0` 或 `I>0`，`M=O=0` | 排除 B：进入对应的通知或已有服务属性匹配入口；不证明操作成功。 |
| `O>0` | 排除 B，进入受测 open，不证明打开成功。 |
| 五项全零，且同轮身份、时序及阳性对照成立 | 只支持未观察到这五类入口；不代表没进入整个 IOKit。MIG/参数早拒及其他族仍不在覆盖内。 |
| 无报告、身份或时序不成立、全局 M 或 O 为零 | 不作零值判读；仅有其他 PID 增长不能证明 bb 归属错误。若单独解读全零 P/I，也记录各自全局是否有正例。 |

r30 历史 `open=70` 是分派层阳性对照，不替代 r43 同轮全局 `M>0`
和 `O>0`。快照非事务、计数 32 位回绕，PID 重用会合并；固定槽的
数字不用于推断其他 PID 的进程身份。

## 机械证据

在设备仓以 WSL root 执行：

```sh
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  python3 -B scripts/build-enuma-r42-matchcnt.py --r43
```

构建 exit 0。只替换两编译单元，其余 1004 个 filelist 条目、15 个直链
归档及 prelink donor 哈希不变；r42 的 10 个冻结文件与两个对象前后
不变。native 和 prelink 都通过 `llvm-nm -u` 和原始 nlist 检查（含
weak）。两张图的六个 `enuma-mt:` 格式串各唯一、六个计数点各一个
机器调用、报告调用一处；都保留旧调度路径，且各有一处新的
`thread_call_enter1_delayed` 调用。逐输入哈希与反汇编在候选
`candidate-manifest.json` 和 `logs/calls-*.macho.log`。

FAT 仅替换 `Payloads/kernel.macho`，读回等于 prelink；
ADT 文件及 FAT 内 ADT 均逐字节等于 r40/r42。两份 boot 的 ramdisk
均等于各自 FAT；ramdisk 之前只改变镜像 ID。

| 文件 | r42 SHA-256 | r43 SHA-256 | r43 字节 / Δ |
| --- | --- | --- | ---: |
| `IOUserClient.cpo` | `39bf62e32faf0ed39b3db7befd5c5ea239a11741c02c15ec92299944e5133e2b` | `fcf2bb99e696d5dd67933df358650040e32e6762715383b6e0198d64129f8d28` | 703736 / +240 |
| `kern_exec.o` | `557f747dee0203c9c41f2fdaa3a82e25ca77d4984c8d69f4f2e75a9176ce1c7e` | `eb14289d16b757952a85817c2ccb1d3d79991f0d7eeb3d51cfd2f0224dbfe839` | 538280 / +2880 |
| `native.macho` | `b96a6be6e7e8fb645d121bed7d6d123f85a56250c56fde62f591e4081b5804d8` | `98525b03552e0c48bfdca7f3ec70a85030f35596c283255ddcf229b99ce74668` | 91909664 / −64 |
| `prelink.macho` | `6d2e4a7330cbfae3372218dfbfcee6a352e6794b6ed356aaeca638cf7600c830` | `cb28043902ba95dde91d29a081fa0a9de12c73f7cd296b2eee0fd9e29cefeef9` | 124751872 / 0 |
| `kernel.macho.adt` | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | 同 r42 | 14128 / 0 |
| `payload.img` | `d570555445392f2612828f2640fba73a1dee04461b9ef502a6ca5835d93b0c2d` | `c1a1f7eea0ab774bf4d6a6aa827a4ba90777c90832a04ca677398fe42c612b67` | 167772160 / 0 |
| `boot.img` | `95a0cb167c5af84bfc0bf000fb376adb282baaee5ec608d3d1b7695ae768b070` | `0cde0acb9ac5d310bb9cdc8631e844979c26394bec09e1d9382f2852b17e4660` | 169951232 / 0 |

主机 UBSan smoke 用真实片段验证 28 个相撞 PID、满表聚合、五项
32 位满值、top 并列排序和无损解码，6 行且最长 79 字符。
未上机；目标机时基、回调实际到期、归属及同轮阳性对照未验证。
未独立 verifier 或 deep review，不提升阶段。
