# enuma r13 单次实机观察（2026-11-21）

`self-checked`：用户单张实机照片、主控目视转录；无录像、无 `vision` 核读。本文整理主控提供的结果，未重新上机或核读照片；阶段不提升。

## 操作

- 2026-11-21 22:42:14 +08:00 一次 `fastboot -s <enuma> boot`，exit 0（`Sending 165968 KB OKAY 3.967s` / `Booting OKAY 0.259s`）；claim `.cache/enuma-console-r13-20261122.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-keystore-20261122-r13/boot.img`，169,951,232 B，SHA-256 `0fc6fd9536be414e420d4dedae48494e6ad10c257b7e824a4b7bcfb0a25e5ae4`。

## 控制台吞吐

```text
enuma-con: lines=20 chars=1560 ns=232736302 ns_per_line=11636815 ns_per_char=149189
enuma-con: lines=5 chars=90 ns=52344375
```

长行组约 11.64 ms/行、0.149 ms/字符；短行组约 10.47 ms/行，落在 10–100 ms/行区间。20 行合计约 0.23 s，该批次单独不足以解释 40 s 级服务间隔；若按长行组均速线性外推，2000 行约 23 s，但实际行数与条件尚未建立。每字符 0.149 ms 与 framebuffer 按 uncached/device 内存写入的假设相容，**不证明映射属性**。

这是启动线程执行一批内核 `printf` 的经过时间，不是纯入队时间，也不是字形可见时间；存在自污染，无统一校正系数。多个批次及其他执行开销的实际贡献未知。

## 新增关键错误

照片底部由主控目视转录：

```text
load_init_program: attempting to load /usr/appleinternal/sbin/launchd.development
load_init_program: attempting to load /sbin/launchd
shared_region: 0x312bc5f65d61ce15 [1(launchd)] check_np(0x16f14ebb0) vm_shared_region_start_address() failed
shared_region: 0x312bc5f65d61ce15 [1(launchd)] check_np(0x16f14e150) vm_shared_region_start_address() failed
```

launchd 的两次 `check_np` 报告 `vm_shared_region_start_address()` 失败，提示当时共享区未建立；与各进程自行映射库、部分服务 bootstrap 失败的假设一致，但不证明这些后果或已确认根因，具体机制仍 UNKNOWN。

## 其他观察

- 先尝试 `launchd.development`，随后尝试 `/sbin/launchd`；与前者缺失后回落、AppleInternal 路径缺失相容，单凭两行不独立证明失败原因。
- launchd 行时间戳 `1970-01-01 00:04:09.201400` 与日历未设置、显示近似开机时长相容；此前 `cal` 值同理，绝对时钟来源未在本次独立确认。
- 主控提供的本轮探针统计为 4 条 `enuma-aks`（`reg 0` / `pub 1` / `match 1 AppleKeyStore` / `aksid 0`）、12 条 `enuma-vn`、3 条 `enuma-fs`，与 r11 一致；照片只可见部分，不能以单张照片独立核实完整计数及不可见内容。

## 判读边界

- **已观察**：所转录长行组约 11.6 ms/行；launchd 上报 `vm_shared_region_start_address()` 失败。`enuma-aks` 四项与 r11 相同是主控提供的统计，受单张照片可见范围限制。
- **待证假设**：无共享区与无可用 dyld 缓存可能导致进程冷启动缓慢、部分服务 bootstrap 失败；缓存是否实际不可用、关联与因果均未证实。
- **UNKNOWN**：`vm_shared_region_start_address` 失败的具体条件；dyld 缓存实际架构（既有卷内调查只见 `arm64`、未见 `arm64e`）；framebuffer 是否 uncached；后续用户态稳定性和 GUI。

阶段不提升。
