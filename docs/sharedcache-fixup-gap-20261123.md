# r44 共享缓存 text-fixup 缺口

`self-checked`，只读源码和本地镜像；无设备操作或构建。**共享缓存的标准映射链允许目标页进入同一签名验证 hook，但不保证该页被访问或走 slow；不能由 r44 总计数定位静默门禁。** 三个目标在本地 donor 的可执行文件映射内，原字节均匹配。r44 的 `parsed=4 applied=1`、`bits=0x08` 表明采样时前三个位未报告成功，第四位已成功；报告非事务快照，且采样后可能仍发生应用（见 `enuma-r44-matchcnt2fx-host-20261123.md:30-55`）。

## 机制、位置和时序

以下 `ubc_subr.c` 是 r44 构建目录 `out/ufs-sm8250-matchcnt2fx-20261123-r44/source/bsd/kern/ubc_subr.c`；共同补丁为只读基座 `UniXNU/patches/xnu/native-text-fixup.patch`。r44 `vm_fault.o` 沿用基线对象（`enuma-r44-matchcnt2fx-host-20261123.md:66-67`）；下述 `vm_fault.c` 为该基线构建树 `.cache/xnu-work/osfmk/vm/vm_fault.c` 当前副本，SHA-256 `2a888ce0625bfef2e42e0bea1234bcd3883e55ac4807849e4aa56eee64f7438d`，源码与已链接对象的逐字节对应尚未重新验证；补丁 `:192-201` 有相同调用逻辑。

* 解析：`ubc_subr.c:6172-6182,6205-6207`：`SecureDTGetProperty(chosen, "text-fixups", ...)`，成功解析增加 count，`cs_text_fixup_parsed = cs_text_fixup_count; STARTUP(EARLY_BOOT, ... cs_text_fixup_init)`。这是启动早期读 ADT 表，不是打开目标文件，也不是一次性扫描；早于用户态根路径加载。不能从解析时间推断后续页访问时 Data 是否已挂载。
* 目标定位：`vm_fault.c:7773-7795`：`vnode = vnode_pager_lookup_vnode(pager); mo_offset = page->vmp_offset + object->paging_offset; cs_validate_page(vnode, pager, mo_offset, ...)`。`ubc_subr.c:6217-6227`：先检查 `f->offset` 是否在当前页，再检查 `vp == NULLVP || vp->v_name == NULL || strcmp(vp->v_name, f->name) != 0`，最后 `memcmp(at, f->original, f->length)`。**没有主动遍历 vnode、namecache、目录或 mount 列表**；访问某个对象的目标页并走到该调用时才比较当前 vnode basename，不区分卷或完整路径；三个失败分支均静默。
* 签名：`vm_fault.c:7803-7808`：`if (validated == VMP_CS_ALL_TRUE && tainted == VMP_CS_ALL_FALSE && cs_text_fixup_page(...) != 0) cache_sync_page(...)`。`ubc_subr.c:5985-6001` 的 `found_hash == FALSE` 令 `validated = FALSE`；`:6043-6056` 哈希不符置 `CS_VALIDATE_TAINTED`。因此无可用签名哈希或校验污染可使修补被跳过；不等于本次缓存页实际发生了这些情况。`vm_fault.c:7822-7829` 还先调用 `vm_page_validate_cs_fast`，fast 返回真时不进入带 hook 的 slow；目标页是否走了该路径未知。`vm_dyld_pager.c:945-952` 对 signed backing 页调用 `vm_page_validate_cs_mapped(...)` 并传递签名状态，说明不能简单断言 dyld pager 一律绕过 hook；缓存映射具体路径和 fast/slow 结果仍未观测。
* 类型：`ubc_subr.c:6214-6239` 无 Mach-O、可执行文件或共享缓存排除判断；入口所在 slow 路径 `vm_fault.c:7773-7776` 断言 `object->code_signed`、非 internal 且 pager 就绪。签名验证路径而非文件扩展名决定能否到达；共享缓存不因名称被硬编码排除。
* 时序：页匹配发生在后续实际页验证，不在 EARLY_BOOT 主动查找；对该次页操作而言文件及相应卷必须已可访问，但目标页不一定已访问。共享缓存建立、Data 挂载相对于 r44 采样的具体顺序未由此证明。r14 独立记录主缓存及 `.symbols` 在传统路径可解析（`enuma-r14-device-20261122.md:25-35`），并不证明 `.13`/`.15` 已打开或目标偏移已 fault。

## 本地路径与四条结果

本轮用本机 `sgan81/apfs-fuse@66b86bd525e8cb90f9012543be89b1f092b75cf3` 以 `-o ro` 挂载 `out/userdata-clean-20261112/OS.raw` 并 `find`，找到 OS 卷内 `root/System/Library/Audio/Plug-Ins/HAL/BTAudioHALPlugin.driver/BTAudioHALPlugin`，随后卸载。此前 `text-fixup-20261123.md:58-64` 只读挂载 SystemOS donor `044-76034-038.dmg`，找到卷内 `root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.15`，在 `0x421e8bc` 读到 `28ad1bb0008544f9`。这些是不同本地卷，不是设备回读；SystemOS 缓存的运行时路径和挂载机制不能仅靠卷内路径推定。不同卷本身不会被 basename 比较排除；可见性、映射及页访问差异是待验证的可能条件，不是已证原因。

| 位 | 目标 | 采样结果与原因边界 |
|---|---|---|
| 0 | `.15+0x421e8bc` | 未报告写入；本地 SystemOS 同名、原字节匹配降低离线条目错误可能，但不证明设备运行页相同。目标页未到 slow hook、签名不合格、vnode 名不同或运行字节不同均未排除。 |
| 1 | `.13+0x1b05bec` | 未报告写入；本地 donor 原字节 `44008052` 和条目一致，实际页是否访问及各门禁仍需运行时证据。 |
| 2 | `.13+0x1b05b08` | 未报告写入；本地 donor 原字节 `44008052` 和条目一致，同属 `.13` 可执行映射，与 bit 1 处于同一 4K 页 `0x1b05000`。 |
| 3 | `BTAudioHALPlugin+0x38bec` | 已观察至少一次写入；该次页已通过 hook 的签名、偏移、名称与字节判断，但不证明替换指令已执行。 |

## sheng 对照和最小候选

sheng **未见记录**：`text-fixup-20261123.md:39-50` 已检查现有历史转录，未见 AW 的 `text-fixup: ... applied` 或实际 parsed/applied 数字；不能据此说 sheng 全中或同样失败，也不能证明记录穷尽。

1. 首选先做仅诊断的逐目标页计数：分别记录目标 basename/偏移页是否到达验证、fast/slow、validated/tainted、vnode 匹配和原字节比较；须保证计数与采样语义并审查并发。代价是少量隔离插桩；风险是页故障热路径与日志时序扰动。确认本机失败分支需要另获授权后一次新上机，离线源码不足以决定。
2. 只有若证实目标页因 fast 路径绕过 hook，才考虑在已验证页合适位置补同等受控应用；需保持签名、原字节、页生命周期及指令缓存一致性，不放宽校验。代价为改 VM 启动链/并发敏感路径，须 `deep_reviewer` 审查及独立构建验证，运行效果需要另获授权上机；当前未证实该路径是根因，不实施。

## 2026-11-23 补充：函数与完整调用链

1. **计数不在同一个函数**。r44 `ubc_subr.c:6166-6206` 是 `static void cs_text_fixup_init(void)`：`:6205` 的 `cs_text_fixup_parsed = cs_text_fixup_count;` 保存解析后的有效条数，`:6207` 用 `STARTUP(EARLY_BOOT, STARTUP_RANK_MIDDLE, cs_text_fixup_init)` 注册。`:6097-6098` 是两个全局变量定义，不在函数内。`ubc_subr.c:6213-6240` 是 `uint32_t cs_text_fixup_page(...)`；函数头 `:6209-6211` 原文为 “Applies the fixups that fall in this validated page of vp. kva is a writable kernel address of the page. Returns the number of fixups written, so the caller makes the instruction cache coherent.” `:6229-6233` 为 `memcpy(at, f->replacement, f->length); written++; ... os_atomic_inc(&cs_text_fixup_applied, relaxed); ... os_atomic_or(&enuma_fx_bits, ...)`，`:6239` 返回 `written`。

2. **直接调用者只有一个**：在基线构建树 `bsd/`、`osfmk/` 搜索 `cs_text_fixup_page(`，只得到其定义、`osfmk/vm/vm_protos.h:542` 声明和 `osfmk/vm/vm_fault.c:7805-7807` 调用：`validated == VMP_CS_ALL_TRUE && tainted == VMP_CS_ALL_FALSE && cs_text_fixup_page(vnode, mo_offset, ...) != 0` 后 `cache_sync_page(...)`。调用者 `vm_page_validate_cs_mapped_slow` 为页签名验证完成后，不是 exec 或 mmap syscall 直接调用。其两个直接上游为 `vm_fault.c:7822-7829` 的 `vm_page_validate_cs_mapped`（fast 返回 false 才 slow），以及 `:7834-7882` 的 `vm_page_map_and_validate_cs`（直接 slow）；后者由 `vm_page_validate_cs` 在 `:7912-7915` fast 不通过时调用，也由 `revalidate_text_page` 在 `:8425-8484` 致命进程错误文本页重验时调用。`vm_page_validate_cs_mapped` 还由 `vm_dyld_pager.c:945-946`、`vm_shared_region_pager.c:654-655`、`vm_apple_protect.c:504-505` 对有签名的来源页调用。共享缓存和普通文件可由各自的页访问触发，不能把建立映射等同于每页已经校验。

3. **共享缓存并非在源码中被一概排除**。`osfmk/vm/vm_shared_region.c:55-64` 注释称 exec 先 `vm_shared_region_enter()`，随后 dyld 调用 `shared_region_check_np()` 和 `shared_region_map_and_slide_2_np()` 填充对应 cache。`bsd/kern/syscalls.master:848` 定义后者 syscall 536；`bsd/vm/vm_unix.c:2962,3078` 调用 `_shared_region_map_and_slide(...)`，`:2449-2478` 获取传入 fd 对应 regular vnode、执行 `mac_file_check_mmap`，`:2813-2822` setup 后调用 `vm_shared_region_map_file(...)`。`vm_shared_region.c:1698-1705,1752-1757,1823-1833` 对 file-backed 项使用文件 pager 和 `sms_file_offset` 调用 `vm_map_enter_mem_object`；按 `:1760-1764` 带 `VM_PROT_SLIDE` 的项另交 sliding pager，`vm_shared_region_pager.c:651-655` 同样对已签名源页调用 `vm_page_validate_cs_mapped`。`vm_dyld_pager.c:943-952` 的 `if (src_page_object->code_signed) vm_page_validate_cs_mapped(src_page, PAGE_SIZE, 0, ...)` 明确对该 pager 的 signed 源页使用同套验证，并复制验证状态。普通 file-backed text 页也能经 VM 页校验路径进入相同 slow hook；以上静态可达不是 r44 已执行该 syscall 或目标页命中的证明，也不能把 dyld pager 与所有 cache mapping 等同。

4. **为何不能指定本次失败门禁**：`vm_fault.c:7719-7723,7728-7738,7742-7747` 中已验证、tainted、可选 validation bitmap 命中或 object 终止等均可让 fast 返回 TRUE 而绕过 slow；`:7805` 又要求整页验证成功且不 tainted；`ubc_subr.c:6219-6227` 依次检查目标文件偏移是否在本页、basename 和原字节，任一 `continue`。表项遍历没有“只处理首个页”的条件。r44 未记录哪条条件触发，也未证明目标页在采样前发生 fault、运行时文件与 donor 相同或选用 shared-region 路径；不能将结果归因于特定条件，亦不能据此断言接错位置。

### 新增直接镜像检查

以同一 `sgan81/apfs-fuse@66b86bd525e8cb90f9012543be89b1f092b75cf3` 对 SystemOS donor `044-76034-038.dmg` 使用 `-o ro` 挂载，用 `od` 读取两个实际 inode 的 cache header 和目标字节后卸载。`mappingOffset=0x200, mappingCount=1`；按 `enuma-cache-pagesize-20261122.md:9-13` 的 dyld mapping 格式，`.13` 的唯一 mapping 为 `(address=0x1a67c8000, size=0x6c60000, fileOffset=0, maxProt=5, initProt=5)`，`.15` 为 `(address=0x1ad480000, size=0x6394000, fileOffset=0, maxProt=5, initProt=5)`；三偏移均落在对应映射的文件区间，权限 5 为读/执行。`od -j 28335084 -N 4` 和 `-j 28334856 -N 4` 分别在 `.13` 读得 `44 00 80 52`，与 `UniXNU/profiles/os/ipados-17.7.11-21H461/profile.toml:41` 两条 `44008052` 一致。`.15` 的匹配记录见上。映射表只证明 donor 静态范围，不证明运行时已映射或访问这些页。

### sheng 对照：逐 hunk

参考 `UniXNU/UniXNU-sheng@da9fab96aea0b5dcdb3bef730b10397276514dac` 的树：`patches/` 只有 `.gitkeep`，不是含独立 native-text-fixup 的设备补丁；其 parent `8a2dd99a9af7540cc13b06a586f6133d1aba5866` 到该提交的 diff 仅 `board.toml:190-192` 增 `text-fixup0=dyld_shared_cache_arm64.15,421e8bc,28ad1bb0008544f9,c0035fd6008544f9` 和 `package/BootLog.c:25-26,478-483` 增 parsed/applied 输出。历史 sheng 实际构建所用 UniXNU commit 未钉住，因此无法断言该次最终链接二进制的实现。

可取得的同作者上游共同补丁早期版本 `UniXNU@1bcc447ccf4a05c720f5d96c59278749710c27d0:patches/xnu/native-text-fixup.patch`，时间比上述 sheng commit 早 22 秒；与 enuma 基座 `UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241` 的同路径做 `git diff 1bcc447 693f5d9 -- patches/xnu/native-text-fixup.patch`。这是可复现的上游版本对照，不是历史构建 pin 证据：

| 补丁 hunk | 上游早期版本 / sheng 相关 | enuma 基座及 r44 | 影响 |
|---|---|---|---|
| `ubc_subr.c` 声明/解析 hunk | 原版 8 条 boot-arg，`CS_TEXT_FIXUP_MAX 8` | 最多 32 条，先读 `/chosen/text-fixups` 再读 8 boot-arg；r44 额外引入 bitmap 报告 | 输入来源和上限不同；r44 `parsed=4` 已确认四条解析，不能证明后续页命中。 |
| 同一 hunk 的 page matcher | 页范围、`v_name`、`memcmp`，成功后 `memcpy` 和 applied 计数 | 匹配与写入逻辑相同，r44 在成功后增加 bit | 无额外 cache 特判或改变门禁；bitmap 是观测差异。 |
| `vm_fault.c` include hunk | arm64 include `arm/caches_internal.h` | 相同 | 无额外 cache 路径。 |
| `vm_fault.c` slow validation hunk | `validated == VMP_CS_ALL_TRUE && tainted == VMP_CS_ALL_FALSE` 后调用 `cs_text_fixup_page`，然后同步 cache | 相同 | hook 位置和签名门禁相同；无共享缓存专用补丁。 |
| `vm_protos.h` 声明 hunk | 声明 `cs_text_fixup_page` | 相同 | 无行为差异。 |

`UniXNU@477e530a8689af4a09eacb4eb9bdb878c737d8b6` 另改 `native-4k-signature-hash-cache.patch`：大于 32 MiB 的签名输入用 `IO_NOCACHE` 分块读取并生成 4K 验证 hash；这不是 `cs_text_fixup_page` 的 cache 专用 hook，也不证明 r44 某目标页的 fast/slow 状态。后续 sheng `c8f92b208068eeaa4cd2b0f592671f04ee70076e:patches/xnu/series` 只列 audio、CPU idle、AMP 三个板级补丁，不含 text-fixup 专项；不能据此证明它的共同补丁闭包或历史机器行为。现有 sheng parsed/applied 仍无运行输出。

## 2026-11-23 补充：tainted 假设与修复比较

**判定：证据不足。** 静态代码证明被 taint 的 slow 校验结果会跳过 fixup；没有 r44 的目标页 `validated`、`tainted`、`cs_blob`、fast/slow 或页访问记录，不能把 SystemOS 的 `system-volume-auth-blob` ENOENT、`Need authenticator (81)`、`failed to find named root snapshot` 推导为这几个页的 hash mismatch 或 taint。卷/快照认证、CodeDirectory 签名信任与页内容哈希是不同层；没有观察到它们在本次目标页上的因果链。r44 `bits=0x08` 仅说明第四条采样前至少一次被写入，不证明它的完整信任链，也不证明缓存签名状态。

以下 `ubc_subr.c` 行号指 r44 局部构建源码；`vm_fault.c` / `kern_codesigning.c` 指上文所列的基线构建树当前副本，复用对象与该副本的精确对应仍以此前限制为准。`commands.json:370` 显示 r44 重编 `ubc_subr.o` 带 `XNU_NATIVE_CS_HASH_CACHE=1`，不是仅凭补丁文件存在推定启用。

### taint 的赋值链与条件

* slow 局部变量：`vm_fault.c:7787-7805` 的 `validated = 0; tainted = 0; nx = 0; cs_validate_page(..., &validated, &tainted, &nx); page->vmp_cs_tainted |= tainted;`。slow 自己不直接构造非零局部 taint，而是接收 `cs_validate_page` 的结果；hook 判断的是**这次局部变量**，不是只看原先的 `page->vmp_cs_tainted`。
* 签名 hash 不等：r44 `ubc_subr.c:6043-6056`：`if (bcmp(expected_hash, actual_hash, hashtype->cs_size) != 0) ... *tainted |= CS_VALIDATE_TAINTED;`，`:6065` 即便不等仍 `validated = TRUE`。`:6374-6379,6386-6397,6405-6413` 的 `cs_validate_page` 把 `CS_VALIDATE_TAINTED` 转换为 `*tainted_p = VMP_CS_ALL_TRUE` 或按 4K chunk OR 相应 bit，故传回 slow 后被 taint 门禁挡住。
* 4K 派生 hash 元数据不合格：`ubc_subr.c:5952-5962` 在 4K kernel / 16K 签名 hash 分支检查对齐、codeLimit、缓存指针及索引/长度，失败时 `*bytes_processed = PAGE_SIZE; *tainted = CS_VALIDATE_TAINTED; return FALSE;`；这同时导致 validated 不满足和 taint，不等同于已证明签名 hash 不匹配。
* 先前写映射：`vm_fault.c:7702-7710` 的 `page->vmp_wpmapped && !VMP_CS_TAINTED(...)` 执行 `VMP_CS_SET_VALIDATED(..., TRUE); VMP_CS_SET_TAINTED(..., TRUE);`。随后 `:7721-7723` 检查已验证或已 taint 就 `return TRUE`，该次走 fast 而根本不调用 slow/hook。这是页状态 taint，不是 slow 局部 taint 的赋值。
* 缺 blob / 无覆盖 hash：`ubc_subr.c:6331-6339` 取 blob（可选 supplemental），`:5920-5933` 无覆盖或 blob 数据释放则跳过，`:5985-6001` 无 hash 时 `validated = FALSE; *tainted = 0;`；`:6362-6384` 默认未验证、无 taint，零处理字节则跳过该 chunk。缺 blob **不是自动置 tainted**，但可因 `validated` 不全跳过 hook；签名未装载/页无签名也可能使对象在更早路径不具备 `code_signed`。`:6008-6013,6395-6396` 末段不完整置 `CS_VALIDATE_NX`，由 `nx_p` 接收，**不是 tainted**。
* 非 Apple 信任 / cryptex 未认证：这些可以影响签名 blob 准入、卷挂载、映射或执行，但上述 `cs_validate_hash` 的 taint 赋值没有检查“Apple/非 Apple”或 `system-volume-auth-blob` 的条件。`bsd/vm/vm_unix.c:2474-2479` 有 `mac_file_check_mmap`，`:2484-2498` 的 trust-cache/ownership 分支明确受 `XNU_TARGET_OS_OSX && __arm64__` 条件约束，不能当成此 iPadOS 路径的实测行为。缺少具体失败与签名记录，因此这些条件不能直接判为 r44 页 taint。

### 补丁、配置与 fast/slow

* `UniXNU/patches/xnu/native-4k-signature-hash-cache.patch:71-75,97-104,107-113,250-251` 在 blob 发布前准备 hash，对原始 16K 块验证后生成 4K 摘要；准备失败可拒绝 blob，运行时缓存元数据失败显式置 tainted。对应 r44 `ubc_subr.c:4877-4882,5848-5868,5952-5966`。该补丁改变签名数据和拒绝路径，**不是把所有页标成已验证**；上述检查均不能证明某目标页实际失败。
* `native-text-fixup.patch:192-201` 的签名后 hook 已链接；本身不把页预先置 validated。静态搜索 UniXNU `patches/xnu/*.patch` 与 enuma `patches/` 的 `vm_page_validate_cs`、`vmp_cs_validated`、`CS_CONFIG_INTEGRITY_SKIP`、`cs_validate_page`、`cs_native4k_prepare`、`cs_enforcement`、`cs_observe`，直接涉及的主要是上述两条；搜索范围不是最终复用对象的完整补丁闭包证明。
* 上游已有 DEVELOPMENT/DEBUG 特例 `ubc_subr.c:6343-6359`：`if (cs_config & CS_CONFIG_INTEGRITY_SKIP) { *validated_p = VMP_CS_ALL_TRUE; *tainted_p = VMP_CS_ALL_FALSE; ... return; }`，会在 slow **跳过计算 hash 但让本次 hook 门禁通过**，并不直接令当前调用改走 fast；以后的页状态可影响 fast。基线 `kern_codesigning.c:252-256,292-295` 通过 `cs_integrity_skip` 参数设置该 flag。r44 候选 `device/board.toml` 的 kernel_args 含 `amfi_get_out_of_my_way=1`、不含 `cs_integrity_skip`；前者在 `kern_codesigning.c:283-289` 对应 `CS_CONFIG_GET_OUT_OF_MY_WAY`，与后者的 `CS_CONFIG_INTEGRITY_SKIP` 是不同标志。此处仅核对冻结配置和源码，不证明实际运行配置或原版 AMFI 消费行为。
* `zzyc-owner-skip-launch-constraints.patch:23-27` 有 `sheng-no-lc` 门控的 launch-constraints 返回 0，与页 hash 不同；本轮未证实它进入 r44 实际对象，候选参数也未列 `sheng-no-lc`。不能由该补丁或 `amfi_get_out_of_my_way` 推断目标页 `tainted=0`。
* shared-region 标准源码链见上文：`vm_shared_region_pager.c:651-655` 对 signed 来源页调用 `vm_page_validate_cs_mapped`，其 `vm_fault.c:7822-7829` **先 fast 后可选 slow**；未访问、已验证、已 tainted、可选 bitmap 命中或 pager 终止均可不进 slow。`.13` 两目标属于同一个 4K 页，若只访问其中任一处且该页进入成功 matcher，理论上循环会尝试同页两条，但实际页访问和运行字节均未证实。

### 假设若成立：三个候选

| 方案 | 改动量及签名影响 | 安全模型 | 离线验证 |
|---|---|---|---|
| A：放宽 tainted 门禁 | 表面上改一处条件，但已 tainted 页的目标字节即使匹配也不能证明整页可信；不必改变 hash 计算，但在失败结果上写页，可能仍被执行策略拒绝或污染其他使用者 | 明确破坏“只修改验证通过页”的边界；不推荐 | 合成页和门禁状态可测；无法离线证明设备 taint 成因或安全后果 |
| B：共享区映射/页路径单独处理 | 多于单行：须选择真实文件源页、偏移、生命周期、签名状态和 I-cache 同步；映射时没有保证物理页已 fault。严格保留签名门禁本身不放宽 hash，但**不能修复真正 tainted 的页** | 若绕过 taint 仍与 A 一样削弱；若保持门禁则不降低该边界 | 可用源码路径和模拟页测试，无法离线证明实际映射/访问成功 |
| C：早期直接改文件 | 修改镜像/文件及后续签名或信任链，涉及只读卷、持久性、签名和缓存一致性；不调用现有页校验不是保持原签名 | 原签名会因修改失效；若靠关闭校验或额外信任绕过，会削弱模型 | 副本字节、签名失效及镜像结构可离线检查；设备效果不可离线证明 |

**建议：不实施 A/B/C 的绕过。** 若必须选探索方向，选 **B 的受限诊断/已验证页版本**，先证实 fast 绕过或页到达后保留签名门禁；若真正是 tainted，应先定位并修复合法信任/签名或数据完整性前置，再考虑 B，不能声称 B 单独治好 taint。涉及 VM fault/共享区生命周期和并发的实现须明确 brief、`deep_reviewer` 与独立 verifier；本轮无代码变更。
