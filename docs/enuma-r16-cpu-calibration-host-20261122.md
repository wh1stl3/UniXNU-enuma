# enuma r16 — 单核 CPU / 内存标定（2026-11-22）

`self-checked`，仅主机候选：`out/ufs-sm8250-launchd-keystore-20261122-r16/`。r16 = r15 + CPU 标定；UniXNU 基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`，iPadOS 17.7.11 / 21H461。补丁不进默认 series。

## 测量设计

`bsd/kern/kern_exec.c:8333`，`load_init_program()` 在已有 SystemOS/Data 准备之后、exec 之前调用 `enuma_path_probe()`。已有的 `seq=0` 门控不动；`enuma_path_probe():8307` 在原控制台测量之后调用新 helper `enuma_cpu_probe():8251`，每次启动一次。r15 共享区探针不变。

```text
enuma-cpu: memcpy %u ns=%llu mbps=%llu
enuma-cpu: loop %u ns=%llu mops=%llu
```

- 复制：两个 64 字节对齐的 8 MiB 静态数组。计时外先填充两块内存，计时内只做一次 `memcpy`；编译器屏障保留数据访问。`mbps` 是复制的有效载荷 MB/s（十进制、向下取整；读写不双计），即 `8,388,608 × 1000 / ns`。预触后单次复制不是强制冷缓存或纯 DRAM 带宽，也不要求测量结束时数据已写回 DRAM。
- 整数：AArch64 `asm volatile` 执行 100,000,000 次串行依赖的 `add` + `ror`，另有 `subs` + `b.ne` 循环控制。`mops` 只计前两条、含循环控制的时间，即 `200,000,000 × 1000 / ns`。不经每轮内存读写，不可被优化成闭式；不是峰值多发射吞吐。
- 两次独立使用 `mach_absolute_time()`，之后用 `absolutetime_to_nanoseconds()` 换算；填充和两次 `printf` 均不在计时区。两行最多 66 / 68 字符（含 LF，不含控制台附加前缀）。`ns=0` 的显示速率为 0，样本无效。未关中断、未改调度；结果是当时环境下的有效吞吐。
- 省略可选 FP/除法测试，不引入内核 FP/SIMD 使用；也省略 CPU 频率：本候选没有已验证的实时核心频率字段，不用 ADT 标称值、不读 PMU 或私有寄存器，也不测同源计数器比值。

## 判读表

| 实机读数 | 判读 |
|---|---|
| `mbps ≥ 5000` 且 `mops ≥ 1000` | 达到现代 ARM64 单核粗参考量级：复制约 1.68 ms 以内、整数约 200 ms 以内。启动时 CPU 与这条内存复制路径未见整数量级降速；优先调查长等待，不能排除用户态后期降频或其他路径。 |
| `mbps ≤ 500`，`mops` 接近参考 | 复制 ≥16.78 ms，复制/内存路径比参考低至少一数量级；先查内核内存属性、缓存及复制实现，不据此认定 CPU 低频。 |
| `mops ≤ 100`，`mbps` 接近参考 | 整数 ≥2 s，CPU 有效整数执行显著偏慢；先区分频率、抢占和中断，不以吞吐换算实际 MHz。 |
| 两者均低至少一数量级 | CPU/内存子系统的有效执行异常；先用外部墙钟核对计时并排除明显调度干扰，再定位具体环节。 |
| 中间量级、缺行或 `ns=0` | 中间值没有单样本判因力；缺行或零时长不是吞吐证据。 |

参考量级是诊断门槛，不是 enuma 验收线。[AmpereOne 单线程 memcpy 实测](https://community.amperecomputing.com/t/memcpy-performance/3403) 报告 libc 约 9.62 GB/s（不同平台与缓存条件），仅支持现代 ARM64 的数 GB/s 量级；不把 LPDDR 理论带宽当作实测。[Qualcomm Snapdragon 870 产品简报](https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/prod_brief_qcom_sd870_5g.pdf) 给出 Kryo 585 最高 3.2 GHz；[Arm Cortex-A55 Software Optimization Guide v2，§4.3–4.4](https://wordpress-courses2425.wolfware.ncsu.edu/ece-785-sprg-2025/wp-content/uploads/sites/80/2020/03/arm_cortex_a55_software_optimization_guide_v2.pdf) 给出基础 ALU 和立即数移位的单周期延迟，支撑 GHz 级核心上约 1 Gops/s 的参考数量级。两者都不是这段循环的同板对照；循环开销、核心型号和实际频率不由参考值决定。

## 主机证据

完整证据在候选目录 `delta-vs-r15.json`、`candidate-manifest.json` 和 `self-check/build-final/logs/`。

| 文件 | r15：字节数 / SHA-256 | r16：字节数 / SHA-256 |
|---|---|---|
| `kern_exec.o`（唯一重编） | 479808 / `9c8a1211e2d9c3722f5512519d3dc942164ad56ff0dfe7f94bd811ca0bd6793c` | 482200 / `839e36aa038d6882922c823a6d7b423b592d827cd0b79e77edb74ff4c48a93fd` |
| `native.macho` | 91858672 / `e0691e2ff7d9b88aae3b3008d70c6f9e3eed04df2c951ad81b4f6692191db0fd` | 91875296 / `55c6bf61b10fd6a4921941364f88ca0b3a51b6c73a20ffbd9d4f8dc6274465f9` |
| `prelink.macho` | 124702720 / `22adea4d8528497e77898c14b124495302c56eb2f26600bbe992fb05ac405e8b` | 124719104 / `ca68f5abedeb22fb9b71bd096b501e3680b5614dbb103119ec0d87c60644eb34` |
| `payload.img` | 167772160 / `3554f8d049b83947de0350de84d816f2848ca1f8474f4dcb75412cf5f6e8688c` | 167772160 / `9794e97a2aff096c072ff8906573a3e04da708652ec39eebe132b34056b05524` |
| `boot.img` | 169951232 / `4224d84cef09f59f85f1cf795b1b112236445b19ec84a75bd18ca710fd5a2083` | 169951232 / `9e94a06c41e4d1556a2d0c569bfca983e5d3bba0515ee311f37e0800637796a9` |

- 源文件旧/新 SHA-256：`0bd9beaf03d2db942777d5eaa7326b22559a53eac40e655f3b5c10db192f592a` / `109089ddf65e0431a1d8ab38e291d145d3d355e19abc0f56a9152c1e3e592501`。沿用已有 Clang 命令，仅改输入源和输出对象。补丁 dry-run/实贴零 fuzz、零 offset。链接文件表只换 `kern_exec.o`；其余 1005 项、1022 个显式链接输入（含 `vm_unix.o`）与 9 个保存对象哈希不变，范围重叠；r15 的 27 个冻结条目（含 boot/payload/native/prelink、FAT 回读件、recipe 和对象）前后相同。
- 两个格式串各自均为 r15 对象/native/prelink 0 处、r16 各 1 处；两个最终 Mach-O 都有 1 个 `load_init_program` → CPU helper 调用点，helper 内 2 个 `printf`、4 个时间读取、2 个时间换算、1 个复制调用；循环机器码计数常量及回跳匹配 100,000,000 次。`llvm-nm -u` 无输出，r15 两个共享区格式串仍各 1 处。首轮静态审计的符号预期与实物不符：填充编到 `_secure_memset`，复制反汇编显示 `_memmove`；`llvm-nm` 证实 `_memcpy` / `_memmove` 同地址，审计据此修正后重跑；旧输出保留为 `…-r16-incomplete-audit/`，未用于打包。
- 两块数组合计 16,777,216 B，位于 `__DATA` 零填充范围；`__DATA` 虚拟尺寸 1,310,720 → 18,087,936 B，文件尺寸仍 278,528 B。native 文件 +16,624 B，prelink 和 FAT 内容各 +16,384 B，固定长度 payload/boot 不增。按 Mach-O 段计算，加载跨度 141,107,200 → 157,900,800 B（+16,793,600 B），增加的是启动窗口内使用量，不是文件中的 16 MiB。按固定基座 DarwinBoot `DarwinBoot.c:724–741` 的布局，r16 静态计算使用 159,137,792 B，距 ADT 512 MiB 窗口扣除 2 MiB 后的上限还余 375,635,968 B；不是实机内存分配结果。
- r15 recipe 只换 manifest 标签，沿用相同 wrapper 在 FAT 构建前注入 r6 ADT。FAT 回读的 kernel 等于 r16 prelink；ADT 14,048 B `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059`；initrd `Payloads/scratch-data.img` 1,142,976 B `c89592f808326f7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`；trustcache 61,356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`。后三者、FD、DTB、菜单、boot-args 都与 r15 相同，boot ramdisk 等于完整 payload；manifest 产物仅 kernel/payload/boot 内容发生变化。root-match 检查 exit 0：`/chosen/root-matching` 等于签名 OS 窗口 UUID `04769D26-2CA0-4825-B443-E2E5F88300F2`。

### 复跑

WSL root、设备仓工作目录，使用 `/home/wh1stl3/.local/bin/python3.11 -B scripts/build-enuma-r16-cpu-calibration.py kernel`，然后用同一脚本执行 `package`；本轮两者 exit 0，基座 HEAD 构建前后相同。独立 verifier 需保留现有候选，并以同一基线在干净的 r16 输出目录复跑两条命令和比较 `delta-vs-r15.json`。记录检查从 UniXNU 根运行 `python3.11 -B scripts/porting-record.py check --device <UniXNU-enuma> --base origin/feat/step10-ramblock-probe`，exit 0（15 个 area）。

尚未验证：实机镜像加载、两行输出、实际吞吐及其重复性、实时频率、后续用户态慢启动归因、GUI 或持久化；无设备操作、阶段不变、独立 verifier 未复跑。
