# enuma r14 单次实机观察（2026-11-21）

`self-checked`：单张实机照片，主控目视转录，无录像、无 `vision` 核读；本次只整理转述，未重新上机或核读。阶段不提升。

## 操作

- 2026-11-21 23:10:35 +08:00 一次 `fastboot -s <enuma> boot`，exit 0（`Sending 165968 KB OKAY 4.011s` / `Booting OKAY 0.259s`）；claim `.cache/enuma-arm64cache-r14-20261122.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-keystore-20261122-r14/boot.img`，169,951,232 B，SHA-256 `6022cca4d56b988132a6c96222a7b8537d9d9639359eca0d2b733881c9f2fa4a`。

## 探针实测

主控转录的 14 条 `enuma-vn:`（省略号表示打印标签缩写或照片裁切）：

```text
enuma-vn: 0 DIR /System/Library/LaunchDaemons
enuma-vn: 0 REG /System/Library/LaunchDaemons/com.apple.CommCenter.plist
enuma-vn: 0 REG /System/Library/LaunchDaemons/com.apple.SpringBoard.plist
enuma-vn: 0 REG /usr/libexec/xpcproxy
enuma-vn: 0 DIR /System/Library/CoreServices/SpringBoard.app
enuma-vn: 0 REG .../CoreServices/SpringBoard.app/SpringBoard
enuma-vn: 2 -   /usr/libexec/CommCenter
enuma-vn: 2 -   /System/Cryptexes/OS
enuma-vn: 2 -   /System/Cryptexes/OS/System/Library
enuma-vn: 2 -   /System/Cryptexes/OS/System/Library/dyld
enuma-vn: 2 -   .../Cryptexes/OS/.../dyld/dyld_shared_cache_arm64
enuma-vn: 0 REG .../Caches/com.apple.dyld/dyld_shared_cache_arm64
enuma-vn: 0 REG .../Caches/com.apple.dyld/dyld_shared_cache_arm64.symbols
enuma-vn: 2 -   .../Cryptexes/OS/.../dyld/dyld_shared_cache_arm64e
```

第 12、13 条照片左侧裁切，完整路径依 [r14 主机探针清单](enuma-r14-arm64-cache-probe-host-20261122.md) 为 `/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64` 与同路径 `.symbols`；这是结合标签和清单的路径归属，不是照片显示了完整路径。

## 判读

- **已观察**：探针执行时、其 pre-exec 凭据和视图下，传统 Caches 路径的 `dyld_shared_cache_arm64` 与 `.symbols` 可解析为 `0 REG`。因此该视图中的这两个路径并非不可达；不证明 dyld 后续选择、打开、读取或映射成功。
- **已观察**：`/System/Cryptexes/OS` 及后续所列路径返回 ENOENT；可能是该路径或祖先缺失，并不证明整个 SystemOS 卷不存在。主控另报告挂载日志 `disk1s1 mounting volume …SystemCryptex`；仅 `mounting` 行不能单独证明挂载完成或实际挂载点。卷已挂载但不在该路径视图是候选解释，挂载点与机制均未确证。
- **已观察**：本次长行批次 `ns=224721979 ns_per_line=11236098 ns_per_char=144052`，短行组 `ns=50333697`；长行约 11.24 ms/行，与 [r13](enuma-r13-device-20261122.md) 的约 11.64 ms/行接近。计量仍是该批内核 `printf` 执行耗时，不是纯入队或字形可见延迟。
- **待查假设**：缓存路径可解析与 dyld 可打开缓存相容，但尚无打开或映射返回码。用户提出共享区未建立可能与内核 16K 元数据和 4K 页组装缺失有关：`osfmk/vm/vm_dyld_pager.c` 的 `fixup_page()` 按 `PAGE_SIZE` 索引，所查范围未见对应四片组装实现；这既不证明运行时走到 fixup，也不证明缓存布局或失败因果。不得据此判为更可能的根因。
- **UNKNOWN**：`/System/Cryptexes/OS` 为何不可见、SystemOS 实际挂载点及完成状态；dyld 实际是否打开缓存、映射返回码、共享区失败具体条件。

阶段不提升。
