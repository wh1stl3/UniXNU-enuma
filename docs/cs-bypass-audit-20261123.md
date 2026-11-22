# r44/r47 code-sign validation bypass audit

状态：self-checked，纯离线源码审计；没有构建或设备访问。结论：**尚无一处已证明的我方改动能解释三条共享缓存 fixup 未命中而普通文件命中；需实测路径**。不能仅由未命中推出目标页一定进入过 slow 或一定未进入：目标页可能未访问、fast 返回、slow 门禁失败，或 matcher 未匹配。r44 报告只是采样时刻；r47 尚未上机。

## 范围和证据

设备 `patches/xnu/series` 仅列 `enuma-pid1-observer.patch`、`enuma-pmgr-publisher.patch`；检查设备 `patches/xnu/`、`scripts/`、SM8250 common patches 和基座 `UniXNU/patches/xnu/`，包括脚本生成的隔离增量。基座 HEAD `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；不把 `xnu-12377` 的补丁当作 xnu-10063 本次输入。r44/r47 实际编译源在各自 `out/ufs-sm8250-{matchcnt2fx-20261123-r44,fxdiag-20261123-r47}/source/`，下文 `r47/source` 指后者。`scripts/build-enuma-r42-matchcnt.py:37,153-170,202-219` 表明 r47 沿 r46 来源复制并重编相关源；`commands.json` 保留各次编译命令。未逐个反汇编其余所有链接对象，因此不把搜索结果升级为完整二进制证明。

## 可疑项及排除项

1. **`native-text-fixup.patch`（确定的设计限制，而非证明已发生的绕过；最相关）**：基座 `patches/xnu/native-text-fixup.patch:192-203` 只在 slow 验证通过后调用 matcher；r47 `source/osfmk/vm/vm_fault.c:7791-7814` 为 `validated == VMP_CS_ALL_TRUE && tainted == VMP_CS_ALL_FALSE`，且 fast 返回不会调用 matcher。该补丁使原生 fast 返回、未请求验证及失败门禁均表现为 fixup 未命中，但**尚无证据证明三个目标页走了哪条路径**。这是能产生不对称现象的候选机制，不是已证实因果。
2. **`native-4k-user-abi.patch`（弱间接候选）**：基座补丁 `:66-82` 将非 Apple 4K 平台共享区 submap 从 16K 改为 `vm_map_set_page_shift(sub_map, FOURK_PAGE_SHIFT)`。它确实改变共享区映射粒度，但未直接修改签名验证或 fast 条件；是否间接影响目标页访问未确定，不能认定其让页绕过 slow。
3. **`native-4k-signature-hash-cache.patch`（未发现直接绕过）**：r44 和 r47 `commands.json` 均给 ubc 编译参数 `-D XNU_NATIVE_CS_HASH_CACHE=1`。基座补丁 `:64-75` / r47 `source/bsd/kern/ubc_subr.c:4877-4882` 在 blob 发布前调用 `cs_native4k_prepare(vp, &tmp_blob)`；`:5818-5831` 通过 `vn_rdwr` 读取，超过 32 MiB 的 codeLimit 用 `IO_NOCACHE`，其他为缓存读取。`:5839-5879` 先核对 16K 原签名 hash，再计算 4K digest 并只读保护后将 `blob->csb_native4k_hashes` 指向摘要。该函数没有直接设置 `vmp_cs_validated`、validation bitmap、`validated` 或 `tainted`；缓存读取可能影响驻页，但不能据此断言页已验签或 fast 命中。`:5952-5966` 在实际 hash 验证时选择 4K digest，失败时置 tainted 并返回 FALSE，不是跳过验证。slow 的初值在 `vm_fault.c:7792-7794` 均为 0；`cs_validate_page` 正常初值在 `ubc_subr.c:6370-6372` 均为 ALL_FALSE。

## Bitmap、放宽和共享区

* **bitmap 编译启用**：r44 `commands.json:168-169,574-575` 和 r47 `:168-169,626-627` 的编译参数均为 `-D CHECK_CS_VALIDATION_BITMAP`。`r47/source/osfmk/vm/vm_fault.c:7727-7739` 命中 bitmap 时直接设置 page validated/untainted 并返回；`:7818-7824` slow 验证成功才设置 bitmap。`ubc_subr.c:6515-6526,6536-6551,6566-6592` 限定 rootfs、未尝试升级可写、bitmap 已分配且对应位已设置。**编译开启不证明目标 vnode 有 bitmap 或命中**；此前成功 slow 如果在 fixup 初始化之后且是同一 vnode/offset，按现有 hook 应已尝试 matcher。不能以 bitmap 命中本身解释首次未命中。没找到我方补丁新增 bitmap 的启用项；记录的编译参数已足以证明实际编译启用。
* `ubc_subr.c:6351-6367` 的原有 DEVELOPMENT/DEBUG `CS_CONFIG_INTEGRITY_SKIP` 将 validated 设 ALL_TRUE、tainted/NX 设 ALL_FALSE 并跳过 hash，但依然返回 slow 的 fixup 门禁，**本身不绕过 matcher**；`:6276-6290` 为 range 验证对应分支。搜索设备、common、基座 xnu 补丁及设备脚本未找到新增 `cs_integrity_skip` 或 `CS_CONFIG_INTEGRITY_SKIP`；运行时 config 未取证。
* r47 打包 `device/board.toml:72` 含 `amfi_get_out_of_my_way=1`；实际保存的 `kern_exec.c:1757-1767` 消费的是 `AMFI_bootarg_disable_mach_hardening`，且受 OSX 与 DEVELOPMENT/DEBUG 条件约束，不是 slow 验证早退。缺 AMFI 全部内核侧实现和运行时配置证据，不能排除其他消费路径；不能把该 boot-arg 等同 integrity skip。
* 扫描上述 xnu-10063 补丁和设备脚本，未发现修改 `shared_region_map_and_slide_2_np`、`vm_shared_region_pager.c` 或 `vm_dyld_pager.c` 的补丁；共享区文件改动见上面的 `native-4k-user-abi.patch`，设备 `enuma-r15-shared-region-probe.patch` 为 syscall 诊断而非验证绕过。`xnu-12377/native-4k-shared-region-slide.patch` 属另一版本，不能计入本次。搜索未发现补丁改 `vm_page_validate_cs_fast` 返回条件或新增无条件 validated/tainted 清零；实际 r47 fast 分支仍在 `vm_fault.c:7699-7747`。

## 下一步

先核对目标 vnode/offset 的访问和验证路径：区分未请求、已有页 validated/tainted、bitmap 命中、slow 的 validated/tainted 门禁和 matcher 拒绝。r47 的 `sv/fx/taint/novalid` 为系统聚合，不能单独归因具体缓存页，且 boot-arg 默认未开；如果证实特定 bypass，先定位首次验证与 fixup 时序再设计修复；如果未证实 bypass，则继续查目标映射、访问时机和 matcher 的 vnode/offset。设备操作另需授权；本次无代码修改。
