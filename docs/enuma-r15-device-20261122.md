# enuma r15 单次实机观察（2026-11-21）

`self-checked`：用户提供现场录像及一张关键帧照片，主控目视转录；无 `vision` 逐帧核读。本次只整理转述，未重新上机或核读。阶段不提升。

## 操作

- 2026-11-21 23:56:38 +08:00 一次 `fastboot -s <enuma> boot`，exit 0（`Sending 165968 KB OKAY 4.022s` / `Booting OKAY 0.259s`）；claim `.cache/enuma-srmap-r15-20261122.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-keystore-20261122-r15/boot.img`，169,951,232 B，SHA-256 `4224d84cef09f59f85f1cf795b1b112236445b19ec84a75bd18ca710fd5a2083`。

## 共享区探针

```text
enuma-sr: check ret=12 first=0
enuma-sr: check ret=12 first=0
enuma-sr: call=1 size=0xc45ad000 slide=1 kr=0
enuma-sr: check ret=0 first=1
```

按 [r15 探针定义](enuma-r15-shared-region-probe-host-20261122.md)，一次共享区映射 syscall 返回成功（`kr=0`），所 copyin 映射描述符 `sms_size` 合计约 3.29 GB，选中非零 slide；此大小不是缓存文件大小或实际成功映射量。随后一次查询返回成功且 `first=1`，说明该查询对应的共享区已有首映射。

前两次 `check ret=12 first=0` 在记录顺序上出现于映射调用之前，与 reviewer 对 `sr_first_mapping` 的解释一致：查询时对应区域尚无首个映射，不能将其直接当作故障。探针是全机记录，**不带 PID 或区域标识**；因此不能单凭这几行证明调用者是 dyld、各查询和映射属于同一进程或区域，或证明某个特定缓存的完整加载及后续使用。

## launchd boot task 序列

同帧可见：

```text
<exclaves-boot>            Doing boot task
<fsck>                     Skipping boot task
<mount-phase-1>            Skipping boot task
<data-protection>          Skipping boot task
<finish-obliteration>      Skipping boot task
<detect-installed-roots>   Skipping boot task
<commit-boot-mode>         Doing boot task → boot-mode committed: main
<restore-data-partition>   Doing boot task → optional boot task not present
<mount-phase-2>            Skipping boot task
<init-with-data-volume>    Doing boot task
<fixup-mobile-tap>         Doing boot task → /private/var/mobile/tmp already exists, skipping
```

另可见 `boot-mode set by sysctl: main`、`hello, launchd UUID: 4B525992-8C69-315E-A51A-CC9433E45B51`、`Darwin Bootstrapper Version 7.0.0`、完整 boot-args 列表。`data-protection` 跳过的原因及影响未知。

## 控制台吞吐

`enuma-con: lines=20 chars=1560 ns=226270677 ns_per_line=11313533 ns_per_char=145045`；短行组 `ns=50714114`。与 [r13](enuma-r13-device-20261122.md)、[r14](enuma-r14-device-20261122.md) 同类批次相比，三次均约 11.2–11.6 ms/行；这是内核 `printf` 批次执行经过时间，不是纯入队或像素可见延迟。

## 判读边界

- **已观察**：一次非空描述符共享区映射调用返回成功，size/slide 如上；有查询返回 `first=1`，前面的查询记录为 `first=0`；launchd boot task 序列中 `data-protection` 被跳过；控制台长行约 11.3 ms/行。
- **修正此前假设**：这次记录不支持「所有共享区始终为空」或「所有共享区映射均失败」。但全机无 PID/区域标识，不能仅据此排除某个特定进程或缓存的映射失败，也不能完全排除其对慢启动的影响。
- **UNKNOWN**：映射和查询的调用者与区域是否相同、具体缓存身份及后续使用；共享区建立之后的慢因；`data-protection` 跳过的原因与影响；`aksid 0` 与 data protection 是否同源；SpringBoard 是否停住及其直接依赖。

阶段不提升。
