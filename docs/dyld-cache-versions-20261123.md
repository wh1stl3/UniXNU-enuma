# 21H461 本地 dyld 共享缓存清单

`self-checked`；只读本地镜像，无构建、无设备访问。**`.13` 存在，两个条目不是因目标文件不存在而失效的死条目。** r44 采样 `parsed=4 applied=1 bits=0x08`：按本地目标文件及原字节匹配定义，**3 条有效共享缓存条目中未报告命中 3 条**；四条全部 fixup 中则 4 条均有对应本地目标、3 条未报告命中。bit3 是普通的 `BTAudioHALPlugin`，不是共享缓存条目。此结论是 r47 判读基线，不是 r47 已运行的断言。计数为采样时状态，非事务快照，采样之后仍可能应用；运行时文件和页访问未回读。

## 方法与范围

使用 `sgan81/apfs-fuse@66b86bd525e8cb90f9012543be89b1f092b75cf3` 的本机编译版，依次以 `-o ro` 挂载 `out/userdata-clean-20261112/OS.raw` 和 `out/userdata-clean-20261112/044-76034-038.dmg`，在各挂载根执行 `find <mount> -name 'dyld_shared_cache*' -printf '%P %s\n'`；卸载。OS.raw 无匹配；后者 SystemOS donor 的完整结果如下。路径为该 APFS 挂载根内绝对路径，含 `root` 卷目录，不等同于设备运行时路径；仅覆盖这两个本地镜像。

| SystemOS 卷内完整路径 | 字节数 |
|---|---:|
| `/root/System/DriverKit/System/Library/dyld/dyld_shared_cache_arm64` | 14286848 |
| `/root/System/DriverKit/System/Library/dyld/dyld_shared_cache_arm64.symbols` | 2146304 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64` | 491520 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.01` | 114720768 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.02` | 49152 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.03` | 114229248 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.04` | 229376 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.05` | 115458048 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.06` | 327680 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.07` | 75857920 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.08` | 245760 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.09` | 112934912 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.10` | 245760 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.11` | 111951872 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.12` | 376832 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.13` | 113868800 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.14` | 376832 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.15` | 104628224 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.16` | 409600 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.17` | 115261440 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.18` | 393216 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.19` | 107970560 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.20` | 442368 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.21` | 113278976 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.22` | 294912 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.23` | 107675648 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.24` | 360448 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.25` | 112279552 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.26` | 442368 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.27` | 111132672 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.28` | 507904 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.29` | 113197056 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.30` | 327680 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.31` | 67960832 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.32` | 344064 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.33.dylddata` | 226721792 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.34.dyldlinkedit` | 27410432 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.35` | 115818496 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.36` | 524288 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.37` | 115818496 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.38` | 638976 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.39` | 106545152 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.40` | 606208 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.41` | 115965952 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.42` | 491520 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.43` | 115326976 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.44` | 606208 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.45` | 114573312 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.46` | 770048 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.47` | 115884032 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.48` | 786432 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.49` | 1458176 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.50` | 49152 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.51.dylddata` | 118456320 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.52.dyldlinkedit` | 404865024 |
| `/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.symbols` | 685817856 |

## ADT 条目和偏移

来源为 `UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241:profiles/os/ipados-17.7.11-21H461/profile.toml:40-41`。直接在上述 SystemOS `.13` 用 `od -An -tx1 -j 28335084 -N 4` 和 `-j 28334856 -N 4`：对应 `0x1b05bec` 和 `0x1b05b08`，均为 `44 00 80 52`，与两个 ADT 原字节 `44008052` 均一致。两条在本地 donor 上均有真实目标，不能判为死条目；不证明实际运行时已访问这些页。

bit0 的 AW `.15` 位于同一 SystemOS 路径，basename 与 AW fixup 期望一致；先前同一 donor 的只读检查在 `0x421e8bc` 读得 `28 ad 1b b0 00 85 44 f9`，与 ADT 原字节一致，见 `text-fixup-20261123.md:58-64`。映像内路径与匹配不证明设备运行时该卷已挂载、对应页已映射、签名通过或 fixup 已应用。bit3 的 OS 卷文件存在见 `sharedcache-fixup-gap-20261123.md:15-24`，采样时已报告应用。
