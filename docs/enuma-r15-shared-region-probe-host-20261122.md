# enuma r15 — dyld 共享区 syscall 探针（2026-11-22）

`self-checked`，仅主机候选。r15 在 r14 上只重编 `bsd/vm/vm_unix.c`，不进默认 XNU patch series，不改变 syscall 返回、锁、共享区状态或映射策略。基座 UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241`，iPadOS 17.7.11 / 21H461，XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f`。

## 观测点

- **map（syscall 536）**：r14 `bsd/vm/vm_unix.c:2962` 的 `shared_region_map_and_slide_2_np`，在 r15 `:3120`（原 `:3082` return 的前一条插入）记录。r14 `:2822` 是内部 `_shared_region_map_and_slide` 中 `vm_shared_region_map_file` 的调用点。VM 在 `osfmk/vm/vm_shared_region.c:2091–2095` 清除映射进行状态并解锁；原 `:2822` 并非锁内，但它漏掉 syscall 参数、分配、copyin 和映射前 setup 退出。改选 syscall 的统一出口，在内部清理及两个 `kfree_data` 之后输出一行，覆盖所有**返回的**调用。
- **check（syscall 294）**：r15 `bsd/vm/vm_unix.c:2157` 保存原有 `vm_shared_region_start_address` 的结果，`:2214` 在 `vm_shared_region_deallocate` 后记录。VM 在 `osfmk/vm/vm_shared_region.c:1012–1041` 等待正在进行的映射，并在既有锁下用 `sr_first_mapping != (mach_vm_offset_t)-1` 得到快照；其 `kr == KERN_SUCCESS` 等价于该条件。探针不读共享区字段、不再取锁，也不在锁内打印。两个控制命令（空地址表示移除、`DYLD_VM_END_MWL` 表示禁用后续 linking）不是首映射查询，不计入 check。

```text
enuma-sr: call=%u size=0x%llx slide=%u kr=%d
enuma-sr: check ret=%d first=%u
```

`call` 是从 1 开始的全机完成序号（32 位，无符号回绕）。`size` 是所有已 copyin 映射描述符的 `sms_size` 字节和，不是 cache 文件大小或实际成功映射量；溢出饱和为 `UINT64_MAX`，未收到完整描述符时为 0。`slide=1` 表示内核选中的 slide 非零；提前退出未选中时为 0。不输出地址、路径或密钥。`check` 首次查询打印，随后仅在全机 `(ret, first)` 对变化时打印；按探针原子更新去重，不绑定 PID/region，多并发打印顺序不保证。两处均用独立的 relaxed 原子状态，不参与原逻辑。

## 判读

| 观测 | 可判读 |
|---|---|
| 完整采集内 0 条 `call` | syscall 536 未被观察到**返回**；不能排除尚未返回、走其他路径或采集遗漏。 |
| 有 `call`，`kr=0` | 至少一次该 syscall 返回成功。`size=0` 时可为空操作；仍应看 `check first=1`，不能只凭 `kr=0` 断言新建缓存映射。 |
| 有 `call`，`kr!=0` | 是 syscall 实际返回给 BSD 分发层的整数，不是内部 VM 原始 `kern_return_t`。常见 `22/EINVAL` 为参数/setup 拒绝，或底层映射失败被折叠为 EINVAL；`14/EFAULT` 可是 copyin 或底层 `KERN_INVALID_ADDRESS`；`1/EPERM` 可是 setup 拒绝或底层 `KERN_PROTECTION_FAILURE`；`12/ENOMEM` 可是 setup 内存不足或底层 `KERN_NO_SPACE`。入口的少数分支直接返回 `5/KERN_FAILURE`（如计数越限）或 `6/KERN_RESOURCE_SHORTAGE`（分配失败）；数字与 BSD errno 可重叠，不能仅凭数字定位分支。 |
| `check ret=12 first=0`，随后 `check ... first=1` | 前次查到空区；后来有查询的区已有首映射。翻转只在后续 check 看到快照时打印；不是映射建立时刻。全机行不能证明两次查询为同一进程/区域。 |
| `check first=1` 且 `ret!=0` | 首映射存在；随后的 auth remap 或 copyout 失败仍可导致 `ret!=0`。`ret=22 first=0` 表示查询时任务没有共享区。 |

## 主机证据

候选：`out/ufs-sm8250-launchd-keystore-20261122-r15/`。机械检查明细：`delta-vs-r14.json` 和 `self-check/build-final/logs/`。

| 文件 | r14：字节数 / SHA-256 | r15：字节数 / SHA-256 |
|---|---|---|
| `vm_unix.o`（唯一重编） | 382944 / `bc72d157493aebed0f5422109c6b5bce104327a7050da4bd10837238e94e2417` | 385928 / `4b28590024c860c50b67eadf160ed0c3998dce7353f4ee93546f2f346baa0869` |
| `native.macho` | 91858224 / `b52fff2481d99f253a3d76877dab801e881a305ddb12b5dc50e70fa77dfd1995` | 91858672 / `e0691e2ff7d9b88aae3b3008d70c6f9e3eed04df2c951ad81b4f6692191db0fd` |
| `prelink.macho` | 124702720 / `3bcff23a352a44316f72e9d7e5445c384b3cd01286546aaf1597b4ac553f1fca` | 124702720 / `22adea4d8528497e77898c14b124495302c56eb2f26600bbe992fb05ac405e8b` |
| `payload.img` | 167772160 / `bd25d7d8df3b3743e498b9aedbbf5bcf542d6a83d4ac8adeb79387e73a314762` | 167772160 / `3554f8d049b83947de0350de84d816f2848ca1f8474f4dcb75412cf5f6e8688c` |
| `boot.img` | 169951232 / `6022cca4d56b988132a6c96222a7b8537d9d9639359eca0d2b733881c9f2fa4a` | 169951232 / `4224d84cef09f59f85f1cf795b1b112236445b19ec84a75bd18ca710fd5a2083` |

- `vm_unix.c` 旧/新 SHA-256：`81cdb09c3f45b429f14dd93b4e624c4f7ff65b2dbfcd15cf7ead8b1d0a10e482` / `9cf08d356413fd09d0d5c35dab2d5c4b9c93a357f7c1129bd7a7e2a2eed4a39f`。复用既有 `vm_unix.o.json` 的 Clang argv，只替换输入源和输出对象路径。补丁 dry-run/实贴零 fuzz、零 offset。
- r15 与 r14 比对：文件表仅替换 `vm_unix.o`；其余 1005 文件表项、1022 个显式链接输入及 9 个保存对象的哈希不变（范围重叠）。r14 原有冻结记录、对象、native/prelink/boot/payload 及 FAT 读回件打包前后不变。
- 两格式串在 r14 对象/native/prelink 均各 0，在 r15 均各 1。r15 native 和 prelink 各有 1 个 map→`enuma_sr_call` 及 1 个 check→`enuma_sr_check` 静态调用点，各 helper 到 `printf` 各 1；`llvm-nm -u` 两链接产物均无输出。`call` 最长 73 字符（含换行）。首次自检在脚本 `audit()` 的行长断言失败：64 位十进制 `call` 超限；改为 32 位并把断言前置，保留初版目录 `…-r15-incomplete-width/`，成品不使用其中任何产物。
- 沿用 r14 recipe，只改 manifest 标签，沿用其在 FAT 生成前注入 r6 ADT 的方式。FAT 内 `kernel.macho` 等于 r15 prelink、ADT 14048 B `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059`、initrd `Payloads/scratch-data.img` 1142976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`、trustcache 61356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`。后三件与 r14 相同；boot ramdisk 等于整个 payload。FD、DTB、菜单、boot-args、包体长度均不变；manifest 产物仅 kernel、payload、boot 内容变化。root-match 回读确认 `/chosen/root-matching` 等于签名 OS UUID `04769D26-2CA0-4825-B443-E2E5F88300F2`。
- WSL root `/home/wh1stl3/.local/bin/python3.11 -B scripts/build-enuma-r15-shared-region-probe.py kernel`、同脚本 `package` 均 exit 0。独立 verifier 复跑同两条命令须用另外的干净候选目录（脚本按所在设备仓 `out/` 解析，不覆盖已有 r15）；同时复核完整 `delta-vs-r14.json`。
- `scripts/porting-record.py check --device <UniXNU-enuma> --base origin/feat/step10-ramblock-probe`（UniXNU 根目录，WSL Python 3.11）：exit 0，15 areas。

尚未验证：实机日志是否完整可见、调用者与具体 cache 文件身份、实际映射结果与 4K 假设、SpringBoard/GUI、用户态稳定性、持久性。`map_with_linking_np` 和用户态 fallback 不在本探针内；无设备操作、无阶段提升、无独立 verifier。
