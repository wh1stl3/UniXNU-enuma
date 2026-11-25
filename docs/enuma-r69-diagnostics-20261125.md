# enuma r69 diagnostics — 2026-11-25

状态：self-checked，未上机。除本次打包和镜像哈希检查外，构建与诊断细节为上游交接记录，本次未重新测量。

## 1. 构建链结论

- 官方 `./unixnu build kernel` 可用；交接记录中 r68 出包 169,951,232 B，三个 identical 字段均为 true。
- 官方链不编译设备仓 `package/*.c`，也不注入钩子。
- 钩子靠 `scripts/inject-hooks-and-rebuild.py --apply` 覆盖 `xnu-work` 注入。

## 2. 注入清单

- XNU 树有 7 个修改过的源文件：`bsd_init.c`、`kern_exec.c`、`kern_exit.c`、`ubc_subr.c`、`vm_unix.c`、`OSKext.cpp`、`vm_fault.c`，另有 14 个 `Enuma*.inc`。
- 注入源共 35 文件：19 新增、16 覆盖，其中 9 个 SHA 相同而跳过。
- `NativeUfs.cpp` 已回退：候选版第 44 行引用 feed 中不存在的 `RootWarmInput.h`，导致 fatal error；clang 随后在错误恢复路径触发 `RecordLayoutBuilder.cpp:3439` assertion 崩溃。

## 3. 修掉的 bug

- `EnumaIpc.inc` include 顺序错误：`EnumaBootProgress2.inc` 第 8 行使用 `enuma_ipc_s`，而 `EnumaIpc.inc` 第 46 行才定义，差 38 行。
- 方案 A：调整 `EnumaBbScan.inc` include 顺序，把 `EnumaIpc.inc` 移到 `EnumaBootProgress2.inc` 之前。
- 两处同步：`xnu-work` 与注入源 `out/ufs-sm8250-ustack-20261124-r64/source/`，交接记录称 `diff` 为 IDENTICAL；未动 `package/`。
- 这解释了 r67 当初一直编不出来。

## 4. 验证方法学

- 不能用 `nm` 判断钩子是否编入：官方链 strip 符号，交接记录中 r69 的 `nm | grep -cE "sheng_|enuma_"` 为 0。
- 判据是 `strings | grep 'enuma-'` 输出前缀：交接记录中 r69 为 62 行，r68 为 0 行。
- 辅助判据：`__text` 段 r69 为 `0x7b3124`（8,073,508 B），r68 为 `0x7af5cc`（8,058,828 B），增加 14,680 B。

## 5. 诊断能力清单

12 个输出前缀：`enuma-exec:`、`enuma-fb:`、`enuma-bb:`、`enuma-mt:`、`enuma-ps:`、`enuma-ex:`、`enuma-ipc2:`、`enuma-ctl:`、`enuma-att:`、`enuma-ipc:`、`enuma-exit:`、`enuma-fx:`。

触发链（行号为交接记录）：

1. `kern_exec.c:2131`：每次 exec 调用 `enuma_fb_arm(p->p_comm, proc_getpid(p))`。
2. `EnumaBbScan.inc:185-193`：`name=="backboardd" && pid==34` 首次命中后延迟 30s 调度 `enuma_fb_dump`。
3. `EnumaBbScan.inc:141`：`enuma_fb_dump` 的 `match_snapshot != NULL` 分支调用 `enuma_bp_start()`。
4. `EnumaBootProgress2.inc:47-54`：`enuma_bp_start` 要求 boot-arg `enuma-bp=1`，调用 `enuma_bp_print(0)` 并通过 thread_call 每 60s 重印。
5. `EnumaBootProgress2.inc:7-30`：`enuma_bp_print(idx)` 在 `i>=1 && i<=2` 时额外打印 `enuma-ipc2` 行。

## 6. 未包含的内容

- watchdog（`sheng_boot_watchdog_policy`）和 HID standin（`enuma_hid_standin_start`）未编入：二者在 `kern_exec.c` 的 `#if defined(XNU_OWNER_DATA_MOUNT) && XNU_OWNER_DATA_MOUNT` 块内。
- `XNU_OWNER_DATA_MOUNT=1` 需要完整门禁链：`XNU_OWNER_ROOT_AUDIT=1` → `ROOT_TRUST=1` → `CACHE_MOUNT=1` → `CACHE_STARTUP=1` → `BOOT_MANIFEST=1` → `DATA_MOUNT=1`，外加 `XNU_SOURCE_STORAGE=1`、`XNU_OWNER_ROOT_VOLUME_UUID`、`XNU_OWNER_DATA_VOLUME_UUID`；见 `build-xnu-4k-baseline.sh:283-428`。
- 对排查 bb 卡点不是必需，本次不开。

## 7. 构建性能

- 交接记录：`/mnt/d` 是 9p 挂载，编译时 `wchan = p9_client_rpc`，进程绝大多数时间在等磁盘协议往返，不是编译。
- r68 全量耗时 2 小时 23 分；`kernel.log` 为 190 MB，`warning: multiple candidates for header` 出现 44,110 次。
- `unixnu build kernel` 每次重跑组件归档（如 corecrypto 529 文件），不是 make 增量。
- 改进方向：把 `--out` 移到 WSL ext4（`/root` 或 `~/build`）；20–40 分钟是预计值，尚未验证。

## 8. 镜像数据

- `out/ufs-sm8250-full-20261125-r69/boot.img`：169,951,232 B；SHA-256 `4de6df419f1d1ab8277c2cfeb9655e47a77bc45db1570325c54c84577f72208f`；相对 r68 大小 delta 0 B。
- `boot_args_identical=true`、`r66_non_kernel_payload_members_identical=true`、`r66_firmware_dtb_identical=true`；字段虽沿用 r66 名称，本次脚本实际比较 r68。
- payload 内 `kernel.macho` SHA-256：`6a194336d589304356df151ffbae41f256e0d5bb676325ca5fb8c6ea1789c3db`。
- 本次打包 exit 0；以上镜像数据 self-checked，尚未经独立 verifier 复核。

## 9. 上机判读表

| 现象 | 判读 |
|---|---|
| `enuma bp r49 i=0` 出现 | backboardd 已 exec 且 framebuffer 匹配成功 |
| `i=1`/`i=2` 的 `enuma-ipc2` 行 | launchd 的总计数增长只说明对应计数有活动，不识别对端或 routine |
| 注意 | send/recv 非配对，差值不能证明未回复数量或积压；不能据此证明 launchd 收到或未回复 routine 800 |
| `enuma-bb:` / `enuma-att:` 行 | 附属诊断（bb 记录 / 分发尝试） |

## 10. 局限

- 未上机，全部为离线结论。
- `enuma_fb_dump` 需 `match_snapshot != NULL`；若 framebuffer 未匹配，`enuma_bp_start` 不会被调用，屏上不会出现 `enuma bp`。
- 未包含 watchdog / HID standin。
- `package/` 下的 `.inc` 未与构建树同步（历史旧版，绝不强行同步）。
