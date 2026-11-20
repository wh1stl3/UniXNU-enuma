# Enuma r8 timebase diagnostic

Status: host-only self-checked; no device run or independent verification.

The parent reports that deep review rejected r7 because its DEVELOPMENT kernel
did not enable kprintf spam: its `kprintf` path sends output to os_log, whose
fallback does not set TOCONS. r8 substitutes `printf` at the existing three
probe source sites; atomic sequence gating, sampling, the single 5000 ms
sleep and position before `load_init_program` remain unchanged.

The r4 screen transcript in `docs/ufs-launchd-data-20261119-observation.md`
reports the kernel `decmpfs.c:1894` cluster-copy error. XNU
`bsd/kern/decmpfs.c:98-112,1894` expands its `ErrorLogWithPath` into
`printf`. The same transcript's `Early boot complete` is launchd output, not
evidence of a kernel printf call.

In the XNU source, `osfmk/kern/printf.c:873-888,895-905` sends `printf`
through `vprintf_internal`, `__doprnt` and `console_printbuf_putc`.
`osfmk/console/serial_general.c:144-155,159-186` flushes a newline to
`console_write`; `serial_console.c:524-550,554-590` writes directly or
through a console ring and attempts a drain. The latter can be disabled or
otherwise refused and is not a proof that every line reaches the panel.
`serial_console.c:252-263,278-288` dispatches `_cnputs` through `_cnputc`
to the selected `cons_ops` implementation (`:122-128`).

## Host build and packaging

Build exit 0 and packaging exit 0. The first isolated build was interrupted
by the invoking tool's one-second timeout (exit 143); the completed build
used a separate fresh `self-check/attempt2` directory. No interrupted outputs
were reused. The copied r7 recipe was adapted only to select that directory.
The r7 wrapper injects the complete r6 ADT before the official payload is
assembled; no post-packaging mcopy. Reusing the random-seed is diagnostic
only, not a production entropy strategy.

| Item | SHA-256 |
| --- | --- |
| r8 bsd_init.o | `f6e6f5ad7fa0c141ef4cd87ddb73ca0a2c7999ad6ae999cb499b4800dfe3b3ac` |
| r7 bsd_init.o | `2aa4d4caa3c0cbebc96a3bc1cb1c4fd2713016924be2ee3ae4fcc8f8c6bccea2` |
| r6 bsd_init.o | `6c54e226afccc480e1101335edee289c9bcdf46d6200342561f7d689f81b8c1c` |
| r8 native.macho | `ffea81061ec17ab23b6c06657d5fffb075cce7d5253529b301a2bbf8ffb6f25d` |
| r8 prelink.macho | `ff502bebd813e333f0f082adf0cf5424f9ed16017671f01fa937e050e754cc6b` |
| r8 payload.img, 167772160 B | `32acf717f122db943122d66e8067c027368ff4295597432d3c76a9da2c0c896a` |
| r8 boot.img, 169951232 B | `0797330553b8cd1e5c2833dadb70a29ae816a490ae63c172b6fd8cde00339779` |
| readback ADT, 14048 B | `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059` |

The payload and boot measured hashes match the candidate manifest; the
readback ADT is byte-identical to r6. The 15-token boot arguments, mode 0,
seed initrd, trust cache and payload size match r6. The four other recompiled
objects (`IOKitBSDInit.cpo`, `kern_exec.o`, `IOUserClient.cpo`,
`EnumaUfsOwnerQuery.o`) are byte-identical to r6 and r7.

The build's native-image reachability audit records two calls to
`_native_legacy_display_probe` and two to `_native_legacy_display_late_probe`.
`llvm-objdump --disassemble-symbols=_bsdinit_task` shows two `_printf`
instructions (exit and skip share one) and one `_IOSleep`. Enter, exit and
skip strings each occur once in prelink. Both linked images have zero strong
and weak undefined symbols.

R6 boot, payload and manifest were rehashed and match the three previously
recorded pins. R7 boot and payload match its recorded hashes. The build and
packaging used r6/r7 as inputs and wrote into r8 only; no whole-directory
before snapshot was available, so whole-directory byte identity is not
independently established. The official base HEAD remains
`693f5d9cae8a408dd18b39f3f9fdc4228c934241`.

No device run, display output, timebase behaviour or successful delay is
established. The independent verifier rerun remains pending.

## 上机前审查留痕

主控提供的审查结论：审查人 `deep_reviewer`，**PASS WITH CONDITIONS**；
对象是 `boot.img` SHA-256
`0797330553b8cd1e5c2833dadb70a29ae816a490ae63c172b6fd8cde00339779`。
条件：仅限该哈希的一次临时诊断；缺行不归因于 `IOSleep`；
屏到屏间隔不等于纯睡眠时长。审查不代替当轮设备操作授权。

审查确认 `_bsdinit_task` 的调用地址：`0xfffffff00bce1568`、
`0xfffffff00bce1570`、`0xfffffff00bce15ac`；三种格式串均以 `\n`
结尾，且短于缓冲上限；不需要 `-enable_kprintf_spam`。r8 ADT 下
串口路径不注册 UART，因此本候选的实际观测端只有屏幕。
`candidate-manifest.json:2` 的 status 仍为 `Legacy-display r6`，
是生成物残留，不手改生成物；候选身份以 boot 的完整哈希为准。

## r8 单次临时诊断 runbook

以下命令在 Windows PowerShell、设备仓根目录执行；仅在用户当轮
明确授权一次临时 `fastboot boot` 后执行。不得使用已有或已消耗的
claim；不得重试、刷写或 erase。任何检查失败立即停止，不发 boot。

1. 确认候选身份。执行以下命令，哈希必须与审查对象逐字符一致：

   ```powershell
   $image = 'out/ufs-sm8250-launchd-display-20261120-r8/boot.img'
   (Get-FileHash -Algorithm SHA256 -LiteralPath $image).Hash.ToLowerInvariant()
   # 0797330553b8cd1e5c2833dadb70a29ae816a490ae63c172b6fd8cde00339779
   ```

2. 执行 `fastboot devices`，再对清单中每台逐一执行
   `fastboot -s <serial> getvar product`；仅当 product 为 `enuma`
   的设备恰好一台时继续，设 `$serial` 为该设备的 serial。
   零台或多台 `enuma` 均停止；禁止凭连接顺序选择。此后所有
   fastboot 设备命令都使用这个 `$serial`，不要在记录中写入序列号。
3. 捕获优先使用串口；但此 r8 ADT 不注册 UART，故本候选按无串口
   执行：在 boot 前开始整屏录像，确保每行可辨、覆盖
   `enuma-tb:` 以及后续 launchd 行；记录录像和真实时间起点。
   视频、照片及帧不入 Git，只记录结论与哈希。
4. 确认录像已开始、目标唯一、镜像哈希正确且已获当轮授权后，
   **紧接 boot 前**以排他新建方式创建一次性 claim；创建失败立即停止。
   成功创建即视为已消耗，即使后续命令失败也禁止访问、删除或重放：

   ```powershell
   $claim = '.cache/ufs-timebase-r8-20261120-device-attempt.claimed'
   $f = [System.IO.File]::Open($claim, [System.IO.FileMode]::CreateNew,
       [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
   $f.Dispose()
   ```

5. 仅执行以下一次 boot，记录执行的真实时间及退出码，不因失败、
   无输出或缺行重试；禁止 `flash`、`erase` 和其他设备写入：

   ```powershell
   fastboot -s $serial boot $image
   $LASTEXITCODE
   ```

### 判读表

| 观察 | 能得出 | 不能得出 |
| --- | --- | --- |
| enter 和 exit 均出现 | 一组采样行被观察到；可对照外部真实时间及计数器差值 | 屏到屏间隔是纯睡眠时长，或系统时钟已正确 |
| 只有 enter | 未观察到完整采样对 | 缺 exit 必然由 `IOSleep` 阻塞造成；输出丢失、异常或后续失败均未排除 |
| 间隔异常短 | 显示间隔异常；结合计数器及外部计时缩小范围 | 单凭屏上间隔确定睡眠或时基的根因 |
| 连 enter 都没有 | 未观察到 enter | 探针一定未执行，或缺行由 `IOSleep` 造成 |

两行之间约 5 秒且计数器差约 96000000，只与假定的 19.2 MHz
和五秒真实时间一致，不证明时钟正确；`skip` 不构成第二次配对测量。
将实际观察、真实时间、命令退出码、候选哈希、claim 已消耗状态和
上述证据边界写回 `docs/`；只用于一次临时诊断，**不代表阶段提升**。
