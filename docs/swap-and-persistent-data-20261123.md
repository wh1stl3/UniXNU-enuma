# r39 swap 与持久 Data：只读调查

状态：self-checked 静态调查；r39 日志为主控转录。本轮无设备访问、卷修改或构建。nuwa 数值仅作对照，不能跨板复制。

## 1. swap

Apple 开源 [xnu-10063.121.3](https://github.com/apple-oss-distributions/xnu/tree/xnu-10063.121.3)（非 r39 最终二进制源码映射证明）：

* `osfmk/vm/vm_compressor_backing_store.h:42-61`：非 macOS 默认 `/private/var/vm/swapfile` 加序号，单文件最大 128 MiB、最小 64 MiB；`vm_compressor_backing_store.c:1529-1555` 从最大值预分配，失败则减半。目录必须存在且挂载可写、有空间；`bsd/vm/vm_compressor_backing_file.c:58-80` 用 kernel VFS context、`O_CREAT|O_TRUNC|FREAD|FWRITE`、0600 创建，并拒绝 NOSWAP 挂载。
* 同文件 `:64-67` 直接打印 `vnode_open` 错误；`bsd/sys/errno.h:122` 的 30 是 `EROFS`（只读文件系统），不是内部状态码。它指向此次打开路径所经文件系统只读，不证明 Data 本身只读或确定具体挂载点；缺 r39 实际前缀、路径解析及挂载表。`No _nvramController` 和 snapshot authenticator 81 无证据与此因果关联。
* `vm_compressor_backing_store.c:802-812` 的 20 是调用前 `clock_get_system_nanotime` 取到的系统时钟秒值，不是等待了 20 秒；代码还用上次失败时间和 15 秒阈值控制重试（`:162-180`），不能将显示数值当实测墙钟。
* 本条日志按证据排序：① 路径所在挂载只读（EROFS）；② 其他原因须另一条错误或现场证据：目录不存在通常 ENOENT，权限通常 EACCES，空间不足通常 ENOSPC；不能仅凭 30 排其相对概率。dynamic_pager 未就绪不能解释此处内核 `vnode_open` 返回 EROFS。
* `bsd/kern/kern_sysctl.c:3978-3979,4516`：`vm.swap_enabled` 只读、`vm.swapfileprefix` 可写；初始前缀如上，`vm_swap_enabled` 初值 0，初始化完成置 1 并打印 ON（`vm_compressor_backing_store.c:462,519-520`）。ON 不证明文件创建成功。非 macOS 一般最大 5 文件；app swap 配置按容量及编译目标约束，可为 4 GiB 或 16–64 GiB，开发版还可覆盖文件数（`:140-155,421-459`）。这是配置上限，不是预留空间或实际可用空间。
* enuma seed 逻辑 2,146,996,224 B，不是可用空间数（`docs/data-seed-20261119-generation.md`）。多个 128 MiB 文件可能耗尽容量，但此次失败发生于打开、返回 EROFS，不能归因 ENOSPC。

## 2. nuwa 参考：配方和写入边界

* 实际 r35 参数包括 `native-ufs-root=1 native-ufs-lun=0 ... sheng-data-persist=2 sheng-data-reset=1 sheng-log-reserve=1024`（`nuwa/UniXNU-nuwa/docs/nuwa-r35-display-20261120-observation.md:37`）；不是说 reset 应一直保留。
* macOS 15 VM 官方脚本制作 8 GiB 逻辑 APFS packed seed：r16–r33 是 `data-8g-fixed.dbr`，r34 是添加 keybag 的 `data-8g-keybag.dbr`，卷 UUID 编入内核；文件分别 1,609,888 和 1,896,608 B（`nuwa/UniXNU-nuwa/docs/nuwa-userspace-20261119-observation.md:126-144`）。r34 后确切 seed 和注入方式本次未核实，不能把推测写成 initrd 配方。
* 离线布局快照 `nuwa/UniXNU-nuwa/out/nuwa-data-seed-macos-20261116-r2/layout.json:65-90,109-120`：4 KiB LBA，userdata `[3110976,61850619)`，reserve 262144 块（1024 MiB）；8 GiB seed 2,097,152 页、位图 64 块，store 2,097,217 块，LUN LBA `[59491258,61588475)`。这是历史计划，不是当前 GPT/seed 的认证。
* 窗口公式 `1 + ceil(pages/32768) + pages` 块，首 LBA `userdata_last + 1 - reserve - blocks`；须与 root image 及其 1024 块 guard 不重叠，不能超过分区（enuma 对应源码摘录 `docs/data-store-2gib-analysis.md:150-164`；nuwa 计划的源码版本和公式见上述 layout `:11-19,65-74`）。更改 seed 大小或 log reserve 改变布局；必须保持 seed 身份及 reserve 一致。
* `nuwa/package/nuwa-ramblock/NativeRamBlock.cpp:66-89,95-113,128-150,351-354`：大于 2 GiB 的 seed 需要 mode 2 直连打开的 store；未改变页读 seed，改变页读 store，写通过 store。reset=1/2 丢弃旧 overlay、请求新建；正常重启不得保留 reset，否则丢掉旧 Data。reset=2 的 Setup 行为在 nuwa fork 未移植（`nuwa/package/nuwa-watchdog/SOURCE.md:28-29`）。
* 读取 seed、GPT、已有 store 是读；初始化 reset 写 store 元数据，正常持久 Data 运行写 store 数据及元数据。r35 参数不能单独证明跨重启持久通过；nuwa 卷挂载与 overlay 写观察见上述 userspace 文档 `:139-141`。

## 3. enuma 能否复用

* 当前 `package/EnumaRamBlockStore.cpp:1-13` 是 RAM-only 强符号：mode 恒 0、open/read/write/sync 均失败；只加参数不能启用它。历史带 UFS 的不同构建源 `out/ufs-sm8250-policy-20261116-r1/source/NativeUfs.cpp` 的解析、窗口和门禁见 `docs/data-store-2gib-analysis.md:150-164,253-270`；不能假定它就是 r39 的提供者。最终六符号归属须针对实际候选确认。
* enuma 需自己的 SM8250 warm provider、owner/manifest 和认证绑定，不能照抄 nuwa 板值或 seed。配置层面需真实 store provider 取代 RAM stub、匹配的本板 seed/UUID 和 root 布局、mode 2、稳定 reserve，空白 store 才一次 reset；是否还需代码改动以及实际候选是否已满足，以最终链接和 owner placement 证据为准。现有记录明确 mode 1/2 未放行，历史几何通过不等于持久化通过。
* enuma 历史 3 GiB 示例 store 为 786457 个 4 KiB 块，LUN `[60831714,61618171)`，字节 `[249166700544,252388028416)`，按当时 userdata 和 1024 MiB reserve 计算（`docs/data-store-2gib-analysis.md:180-194,249`）。此范围只适用于该 3 GiB seed；r39 约 2 GB seed 窗口不同，当前 GPT、非重叠与 owner placement 均需重新确认，不能拿此数字授权写入。
* 初始化和运行期 store 写属于对 UFS `userdata` 尾部的设备写入，可能覆盖该范围仍存的 Android 数据；写 root image 前缀、写 boot/vendor_boot 槽、临时 boot 各需对应当轮明确授权。曾同意 Android 数据可弃不等于本轮写授权（`../AGENTS.md`）。启动链/DMA/并发变更另需明确 brief 和 deep review。
