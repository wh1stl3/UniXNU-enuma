# r44 共享缓存 text-fixup 缺口

`self-checked`，只读源码和本地镜像；无设备操作或构建。**失败点只能定位到采样前未完成目标页替换，不能定位到某一个静默分支。** r44 的 `parsed=4 applied=1`、`bits=0x08` 表明采样时前三个位未报告成功，第四位已成功；报告非事务快照，且采样后可能仍发生应用（见 `enuma-r44-matchcnt2fx-host-20261123.md:30-55`）。缺少逐条目标页到达、签名和名称计数，不能断言共享缓存未加载、签名失败或路径不可见。

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
| 1 | `.13+0x1b05bec` | 未报告写入；未核查该文件及原字节，实际页是否访问和各静默门禁均未知。 |
| 2 | `.13+0x1b05b08` | 未报告写入；同上，不能将 bit 0 的离线字节证据推广到本条。 |
| 3 | `BTAudioHALPlugin+0x38bec` | 已观察至少一次写入；该次页已通过 hook 的签名、偏移、名称与字节判断，但不证明替换指令已执行。 |

## sheng 对照和最小候选

sheng **未见记录**：`text-fixup-20261123.md:39-50` 已检查现有历史转录，未见 AW 的 `text-fixup: ... applied` 或实际 parsed/applied 数字；不能据此说 sheng 全中或同样失败，也不能证明记录穷尽。

1. 首选先做仅诊断的逐目标页计数：分别记录目标 basename/偏移页是否到达验证、fast/slow、validated/tainted、vnode 匹配和原字节比较；须保证计数与采样语义并审查并发。代价是少量隔离插桩；风险是页故障热路径与日志时序扰动。确认本机失败分支需要另获授权后一次新上机，离线源码不足以决定。
2. 只有若证实目标页因 fast 路径绕过 hook，才考虑在已验证页合适位置补同等受控应用；需保持签名、原字节、页生命周期及指令缓存一致性，不放宽校验。代价为改 VM 启动链/并发敏感路径，须 `deep_reviewer` 审查及独立构建验证，运行效果需要另获授权上机；当前未证实该路径是根因，不实施。
