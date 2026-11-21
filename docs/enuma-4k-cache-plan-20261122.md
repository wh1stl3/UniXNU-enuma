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

## 6. donor 缓存审计实测

`self-checked`，未访问设备或修改卷；未取得 donor 缓存的有效审计结果。活动 UniXNU 为 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。输入 `out/userdata-clean-20261112/OS.raw` 为 6,077,580,800 B，`044-76034-038.dmg` 为 3,303,014,400 B；文件存在不独立验证其 donor 身份。

两个脚本均无容器或路径参数。`audit-target-dyld-cache.py:14-35` 固定 dyld 源码 revision `a571176e8e00c47e95b95e3156820ebec0cbd5e6`、macOS `xcrun clang++` 和 `UniXNU/.cache/firmware/target-volumes/systemos-mount/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64*`，排除 `.symbols`；严格要求 magic `dyld_v1   arm64`，arm64e 会拒绝，扫描 mapping、slide 和原始 CodeDirectory，但不输出总文件大小或镜像数量。脚本会向 UniXNU 的 `build/target-userspace` 写辅助代码和结果。`audit-native-cache-slide.py:12-52,80-89,134-145` 需固定 XNU revision `d8b80295118ef25ac3a784134bcf95cd8e88109f`、本地 `.cache/xnu-work`、前一脚本 JSON、同一挂载、macOS arm64 编译运行环境，且硬编码恰好四个 v2 slide mapping 和 32 个样本；不同 donor 布局不能将其失败直接判为不兼容。它也写 UniXNU 构建目录。故不能直接把 IPSW、DMG 或 OS.raw 传给脚本，本轮也不能越过 UniXNU 只读约束去补齐其写入路径。

WSL 原样运行（两个均在创建输出前失败）：

```
python3 /mnt/d/Code/PortingiOS/UniXNU/scripts/audit-target-dyld-cache.py
# exit 1: line 15: git -C .../UniXNU/refer/dyld rev-parse HEAD 返回 128，目录不存在
python3 /mnt/d/Code/PortingiOS/UniXNU/scripts/audit-native-cache-slide.py
# exit 1: line 13: git -C .../UniXNU/refer/xnu rev-parse HEAD 返回 128，目录不存在
```

另确认固定 SystemOS 挂载路径和 `.cache/xnu-work` 均不存在。**架构、全部 mapping 的 address/size/fileOffset 及对齐、slide 版本和页粒度、镜像数量、缓存总大小与完整 subcache 集合均未判定**。先前 `docs/enuma-dyld-cache-layout-20261122.md` 的原始字节扫描发现 arm64 候选头和编号文件名，但未解析 APFS 活动 inode，不能作为实际 donor 活动缓存的字段或完整性证据。结论：**无法判定是否满足 4 KiB 内核消费条件**；缺经身份确认的完整活动缓存及可运行的隔离审计环境，签名/真实消费路径也未验证。

可选取出方式：在 macOS 将现有 SystemOS 镜像用 `hdiutil attach -readonly -nobrowse` 只读挂载，确认活动卷和来源后读取/复制完整缓存及 subcache 至本地 `out/`；官方 `scripts/build-boot-runtime.py:34-57` 已有只读 `hdiutil` 挂载模式，但不是 SystemOS 缓存提取 CLI，不能声称其直接提取。也可取得可信的已解出完整缓存及身份记录。随后在独立可写的官方仓副本中准备原脚本规定的固定路径、源码和 macOS 环境；先对完整文件集逐项核查，不能靠 glob、计数或脚本通过推定 subcache 完整。未找到官方现成的 DMG→缓存独立提取脚本；本轮未挂载、未提取、未转换。

## 7. 子模块检出后复审

`self-checked`：标题为计划步骤，实际**未能检出子模块**。UniXNU 基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241` 的 `.gitmodules` 没有 `refer/dyld` 或 `refer/xnu` 条目；`git ls-tree HEAD refer/dyld refer/xnu` 无输出，不存在这两个路径的 gitlink pin。WSL 在 UniXNU 目录执行 `git submodule update --init --depth 1 refer/dyld refer/xnu` 返回 1，首个错误 `error: pathspec 'refer/dyld' did not match any file(s) known to git`；`refer/xnu` 同样报 pathspec 错误。并非网络错误，未用 Windows git 重试，未初始化任何子模块。两个路径均不存在，实际 commit 无法读取、无法与不存在的 UniXNU 子模块 pin 比对；脚本自身要求的 dyld 和 XNU 源码 commit 分别为 `a571176e8e00c47e95b95e3156820ebec0cbd5e6` 和 `d8b80295118ef25ac3a784134bcf95cd8e88109f`，它们是脚本检查值而非 gitlink。

WSL 原样重跑 `python3 scripts/audit-target-dyld-cache.py` 和 `python3 scripts/audit-native-cache-slide.py` 均 exit 1，分别在第 15 行和第 13 行因上述源码目录不存在而失败，未读取 donor。故 arch、每个 mapping 的 address/size/fileOffset 和 4096 整除性、slide 版本/页粒度、镜像数量、缓存总大小及 subcache 集合仍未知；**无法判定 donor 能否以 4K 页消费**。脚本期望的是固定 SystemOS 挂载目录内的实际缓存文件，而非 OS.raw 或 DMG，取法与额外环境要求见上节。

拟用替代方式：另获明确授权后，在独立可写副本按脚本要求取得并核对两个源码 revision，准备只读挂载或经身份核实的完整缓存集合，再执行原脚本；先确认 macOS arm64 构建执行环境及 slide 脚本固定四个 mapping 的适用性。该替代不是子模块初始化，本轮未执行。
