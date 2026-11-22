# enuma r42：按 PID 统计 IOKit 请求

`self-checked`，仅主机。候选 `out/ufs-sm8250-matchcnt-20261123-r42/`。
基线 r40，官方构建基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。
只加计数和报告；无新 UFS I/O、返回值/打开行为、panic、启动等待或生产配置改动。

## 钩点与成本

| 生成源码（候选 `source/` 下） | 分类 |
| --- | --- |
| `iokit/Kernel/IOUserClient.cpp:2708` `internal_io_service_get_matching_services` | M：多服务查询 |
| `iokit/Kernel/IOUserClient.cpp:2792` `internal_io_service_get_matching_service` | M：单服务查询 |
| `iokit/Kernel/IOUserClient.cpp:2880` `internal_io_service_add_notification` | N：匹配通知 |
| `iokit/Kernel/IOUserClient.cpp:4380` `is_io_service_open_extended` | O：open 入口；原 `entry/entry_bb` 计数未动 |

计数在内部汇合入口，覆盖 `bin` 和已成功 copyout 的 `ool`，通知含
`bin/ool` 的 32/64 位变体；不重复统计 wrapper。当前源码无独立
`_priv` 实现，旧 `Unsupported` 桩及未汇合的早期拒绝不计入。
四个固定 PID 槽为 34、5、56、66，其余 PID 使用 28 个不回收的开放
寻址槽，满表或无正 PID 进入 `other`。一次 PID 读取；固定 PID 最多
四次比较加一次 relaxed 原子增量；散列表命中通常为一次槽读取再增量，
首次占空槽 CAS、最坏 28 次探测。没有锁、分配、睡眠、打印或全局热计数。
目标编译以静态断言约束字宽原子无锁。报告按槽采样，再求和和
选前六；各项非事务快照、计数按 32 位回绕，PID 若复用会合并。

## 采样时机与格式

`bsd/kern/kern_exec.c:2123–2130` 的成功 exec 路径先保留原
`enuma-exec` 行，再调 `enuma_fb_arm`。`bsd/kern/EnumaBbScan.inc:175–176`
只为本轮 `pid=34, comm=backboardd` 置标记。原回调每 30 内核秒调度、
最多 20 次；只在最后一次（launchd arm 后名义约 600 内核秒）
`EnumaBbScan.inc:164–169` 调报告。报告 acquire 读取 exec 标记，再用
一次性原子置位，标记缺失则不打印。没有改周期、次数或回调注册。
因此可见报告的采样晚于本轮目标 exec 观测，不拿 r23 视频的 79.824 秒
去换算 r42 内核时钟。若最终槽未到或该 PID/comm 未命中，没有采样，
不得把没有输出读作三项零。

历史 [r24 更正](enuma-r24-census-20261122.md) 记录了 r23
的 79.824 秒 exec；[r30 实机](enuma-r30-device-20261123.md) 同回调曾捕获
两个 opener 和 `all=70, bb=0`，不证明当时已晚于 bb exec；
[r34 主机](enuma-r34-ipc-host-20261123.md) 不是实机时序证据。

```c
"enuma-mt: t=%u %x/%x/%x %x/%x/%x\n"
"enuma-mt: %s(%u)=%x/%x/%x\n"
"enuma-mt: %x:%08x%08x%08x %x:%08x%08x%08x\n"
"enuma-mt: %x:%08x%08x%08x\n"
```

`t` 为 `mach_absolute_time()` 换算成的内核整秒，非录像秒。首行两组
分别是 `all`、`other`；组内顺序 `M/N/O`、十六进制。固定行
`bb(34)`、`sb(5)`、`fb(56)`、`fb(66)` 的 PID 为十进制。
末尾只列其余有计数的前六，按 `M+N+O` 降序、同分 PID 升序；
PID 为十六进制，冒号后是三个相邻的八位十六进制值。最多 8 行，
最长 77 字符（不含换行）。只限制新增 `enuma-mt:`；原有输出不变。

| 同轮读数 | 判读 |
| --- | --- |
| `M34>0, O34=0` | 排除 B：已查询，但未到受测 open。不能证明没匹配到服务，复数查询成功可返回空迭代器，也可能有匹配但不 open。 |
| `M34=0, N34>0, O34=0` | 进入通知路径；不是 A/B 二分中的任一原义。 |
| `O34>0` | 已进受测 open；不属于 `entry_bb=0`，不证明 open 成功。 |
| 三项全零且身份、时序、阳性对照均成立 | 仅支持观察窗内未到三个受测类别，不代表整个 IOKit 未进入，也不排除 IPC/校验在入口前失败。 |
| 全局 M 为零，或全局 M 增长但 bb 归属、时序或入口覆盖未证 | 测量无效；其他 PID 增长本身不证明 bb 归属错误。 |

历史阳性对照 `open=70` 对应 r30 `enuma-ctl: all=70`（分派计数）。
r42 仍须同轮全局 `O>0`、`M>0`；历史 70 不能代替同轮对照，
也不要求新入口计数等于 70。56/66 是历史对照 PID，核对同轮身份，
例如 r30 的 FDR loader 已是 57。

## 主机机械证据

在设备仓以 WSL root 运行：

```sh
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  python3 -B scripts/build-enuma-r42-matchcnt.py
```

最终构建 exit 0；可用 `--out out/ufs-sm8250-matchcnt-20261123-r42-verify`
独立复跑。只替换两对象；其他 1004 个 filelist 条目、15 个直链归档
及 prelink donor 的输入哈希未变，r40 的 10 件冻结文件前后未变。
两个 Mach-O 的 `llvm-nm -u` 与原始 nlist 检查均无 undefined（含
weak）。四个格式串各出现一次；各有一个由 `enuma_fb_dump` 到
`enuma_matchcnt_dump` 的调用及四个计数钩子的实际调用点。报告有八处
机器 `printf`：首行一处、固定四处、三个 top 行位置各一处；
每个 top 行位置的两种格式共用其调用。完整反汇编与逐输入哈希见
`logs/calls-*.macho.log`、`candidate-manifest.json`。FAT 唯一变化成员
为 `Payloads/kernel.macho`，读回等于 prelink；ADT 文件及 FAT 内 ADT
逐字节同 r40。两份 boot 的 ramdisk 都等于各自 FAT，ramdisk 前缀只改
镜像 ID（带填充的 Android kernel 不变）。

真实计数/格式化片段的主机 UBSan smoke exit 0：六线程共 60,000 次
增量竞争三个相撞 PID，填满 28 槽后验证聚合；exec 前不打印，
exec 后调用两次只打印一组 8 行，每行 <80 字符。

| 文件 | r40 SHA-256 | r42 SHA-256 | r42 字节 / Δ |
| --- | --- | --- | ---: |
| `IOUserClient.cpo` | `455ebd7abc178922efeb1faed7020b828fa56a300cef023c3639de58dd397568` | `39bf62e32faf0ed39b3db7befd5c5ea239a11741c02c15ec92299944e5133e2b` | 703496 / +728 |
| `kern_exec.o` | `ca1370c29397c93f86ad1399a62dbe1020d419b7a3b485b429896ca0fd61c79d` | `557f747dee0203c9c41f2fdaa3a82e25ca77d4984c8d69f4f2e75a9176ce1c7e` | 535400 / +12992 |
| `native.macho` | `ee6c4682914be771999b5d592d98774631a369d4e3ba7ba4ab1904466b811e5e` | `b96a6be6e7e8fb645d121bed7d6d123f85a56250c56fde62f591e4081b5804d8` | 91909728 / +536 |
| `prelink.macho` | `b33bab4c434bcc9b94c77a9bff566eef90f3d5da9c2f950b6c1bf622e1282e58` | `6d2e4a7330cbfae3372218dfbfcee6a352e6794b6ed356aaeca638cf7600c830` | 124751872 / 0 |
| `kernel.macho.adt` | `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457` | 同 r40 | 14128 / 0 |
| `payload.img` | `33295a6895bd4bc9e24964abe372631179df8bad41b0f37d6b049bd7bbea2dc6` | `d570555445392f2612828f2640fba73a1dee04461b9ef502a6ca5835d93b0c2d` | 167772160 / 0 |
| `boot.img` | `f2937ed83a7c66a6481bd8d7f6eb5daa34c77d0d747c481198b4f27717c3bbcf` | `95a0cb167c5af84bfc0bf000fb376adb282baaee5ec608d3d1b7695ae768b070` | 169951232 / 0 |

未上机、未验证最后一槽可达、内核时钟与实际经过时间的对应、PID
分配与实际匹配结果；未独立 verifier 或 deep review，不提升阶段。
