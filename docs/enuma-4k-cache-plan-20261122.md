# enuma donor dyld cache 4K 离线调查

`self-checked`：只读源码和现存文件名/记录；未读设备、未修改卷、未构建、未执行审计脚本。UniXNU 基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；远端 HEAD 查询为 `8542980d02b4d2cc5c32ee3542de1760b2562aac`，未更新基座。donor 为用户指定的 iPad7,1 / A10X / iPadOS 17.7.11 (21H461) / arm64；内核维持 4K。

## 1. 官方资料

- `UniXNU/docs/zh/xnu/four-k-page-tables.md:80`：「4 KiB 用户态需要 4 KiB `mmap` 对齐、4 KiB commpage shift 和 4 KiB dyld shared cache 布局。」
- `UniXNU/scripts/audit-target-dyld-cache.py:2-5`：「Inspect original dyld cache mappings and verify complete signature blocks.」「No file, CodeDirectory, cache layout or page table is converted by this audit.」第 34–60 行检查原文件 mapping 对齐和 slide 页粒度，第 61–98 行检查原签名；路径固定于官方目标挂载，不等于已检查本 donor。
- `UniXNU/scripts/audit-native-cache-slide.py:2,28-31,80-89,134-145`：「Execute unchanged Darwin 23 rebasing logic on real target 4K data pages, on the host.」「Target ordinary ARM64 data mapping is not native-4K v2 metadata」。脚本设计为在四个目标映射采样 32 个 4K 页；本次未运行，目标身份不能推定为本 donor。
- `UniXNU/docs/zh/devices/qemu.md:14-19`：「DarwinBoot 交接、4 GiB 窗口、内核入口、MMU 和 4 KiB 页表 | 工作」「SystemOS union 和 dyld shared cache | 工作」。第 3 行明确为独立社区移植；不能将该记录转化为本 donor 的直接证据。

按 `4k`、`4K`、`4096`、`dyld_shared_cache`、`cache layout`、`page size`、`relayout`、`rebase` 检索 `docs/zh`、`scripts`、`kits`：找到原始缓存审计、页表和签名支持，未找到 dyld 缓存 16K→4K 转换或生成工具/流程。不能说官方只有要求而无任何实现：它有原缓存兼容性审计及运行路径，但没有找到转换器。16K 对齐同时是 4K 对齐；硬件页、mapping 对齐、slide 粒度与签名哈希页是不同概念，不能从 16K 签名推断必须转换。

## 2. donor 现有输入

Windows 对设备仓 `out/`、`.cache/` 递归按 `dyld_shared_cache*` 搜索独立普通文件，未找到；没有检查容器内部完整内容。`docs/enuma-cryptex-view-check-20261122.md:31-42` 记载主控转述的四个同名 SystemOS 目录记录，OID 路径、活动树和身份均未确认；不能据此认定有两份不同页布局。`out/enuma-gop-production-20261114-r5/package.json:361-363` 列 `.13`、`.15`，只是包配置引用，不能判为独立的另一种页布局。相同文件名可出现于不同目录/快照，但是否为不同内容、是否分别为 4K 和 16K，缺缓存头、mapping、slide 与身份证据，未知。

`four-k-page-tables.md:3,60-67` 给出 Apple ARM64 多数 SoC 使用 16K 和 Apple profile 策略，不能单凭该概括证明该 iPad7,1 的运行时 granule；A10X 原生 iPadOS 页大小暂不能以当前证据定论，须取得该型号、该版本的运行时或构建配置直接证据。A10X 硬件支持的 granule 与该 iPadOS 实际选用页大小亦不可混同。签名 16K 不证明运行时页或 slide 粒度。

## 3. 如果实际证明需要转换

- 机械但须全量验证：各 mapping 的 `address`、`size`、`fileOffset` 的 4K 对齐和非重叠、文件偏移及引用、权限和 `mappingCount`；仅当拆分/合并 mapping 时调整数量，不能无条件把数量乘四。`audit-target-dyld-cache.py:45-54` 给出实际读取字段。
- 硬骨头：真正为 16K 的 slide metadata 要按版本和 4K 页拆分链、重算每页 starts/extras、delta、边界和大小/偏移，保留所有 fixup，不能只改 `page_size`。v2 具体检查可参考 `audit-native-cache-slide.py:80-114`；其他版本不得套用 v2。
- 若移动虚拟地址或重排文件，要处理跨映射引用、内嵌 Mach-O、subcache 关联、offset、UUID、优化表和预构建 loader 等版本相关元数据；地址和内容保持不变的直接映射不必机械重写这些项。有效性取决于实际格式和 dyld/XNU 消费者。
- 重新生成后的文件完整性及授权是独立硬骨头；只重算偏移或哈希不自动获得受信签名。

## 4. 签名

`four-k-page-tables.md:84-103`：「原始 CodeDirectory 使用 16 KiB 哈希页，4 KiB 内核校验 4 KiB 页」；其先用原 CodeDirectory 校验整个 16K 块，再派生 4K 摘要；原始块哈希失败不产生表。转换若改变原签名覆盖的字节而保留原 CodeDirectory，会在原块校验失败，不能靠派生表绕过；即使新建 CodeDirectory，信任链、cdhash、trust cache 和镜像认证仍须另行证明。没有找到官方说明说转换后可复用原签名，官方脚本反而明确不转换。原字节不变而直接使用 4K 对齐映射则没有这一转换所致冲突；实际运行仍须验证。

## 5. 公开项目

未找到能证实完成同类 16K→4K dyld 缓存转换的第三方项目。相关但不等价：[keith/dyld-shared-cache-extractor](https://github.com/keith/dyld-shared-cache-extractor) 提取库供逆向，不是转换器；[blacktop/ipsw](https://blacktop.github.io/ipsw/docs/guides/dyld) 解析/提取，不证明输出可启动缓存；[xVanTuring/UniXNU-qemu](https://github.com/xVanTuring/UniXNU-qemu) 的 4K 运行记录见上述官方文档，但不证明转换或 donor 相同。未下载这些项目。

结论：先只读解析本 donor 的现有缓存头、所有 mapping、slide 版本/页粒度及签名，并确认路径与身份；若原缓存已满足 4K，避免转换。当前不证明共享区失败原因。
