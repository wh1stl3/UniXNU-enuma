# enuma r14 — arm64 dyld cache 路径探针（2026-11-22）

`self-checked`：r13 临时源上的补丁 dry-run 与实贴成功，零 fuzz、零 offset。r14 编译、链接、预链接、打包与 root-match 检查完成；仅主机候选，未上机。

## 路径与判读

完整路径传给 `vnode_lookup`；只缩短打印标签。`0` 仅表示在该 pre-exec 视图可解析到 vnode，目录要看到 `DIR`，缓存文件要看到 `REG`。**ENOENT 只说明该路径或祖先不存在，不能单独区分路径猜错与视图未挂载。** 目录可见也不证明是独立挂载点，文件可见也不证明 dyld 选择或可映射该缓存。

| 路径 | `0` 且类型符合 | `ENOENT` |
|---|---|---|
| `/System/Cryptexes/OS` | `DIR`：cryptex OS 命名空间入口可见 | 入口或上级缺失 |
| `/System/Cryptexes/OS/System/Library` | `DIR`：cryptex OS 的 Library 可见 | 若上条成功，缩小到其下的 `System` 或 `Library` |
| `/System/Cryptexes/OS/System/Library/dyld` | `DIR`：cryptex dyld 目录可见 | 若上条成功，`dyld` 子路径缺失 |
| `/System/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64` | `REG`：cryptex 路径下的 arm64 缓存可见 | 若父目录成功，该文件名不可见 |
| `/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64` | `REG`：传统 Caches 路径下的 arm64 缓存可见 | 缓存文件或其上级缺失；不能否定其他路径 |
| `/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.symbols` | `REG`：传统路径的符号伴随文件可见；不代表主缓存可见 | 伴随文件或其上级缺失；不能否定主缓存 |
| `/System/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e` | `REG`：对照路径意外可见；不说明 donor ABI 改变 | 若父目录成功，符合 arm64 donor 没有该文件的预期 |
| `/System/Library/LaunchDaemons` | `DIR`：系统 LaunchDaemons 目录可见 | 该目录或上级缺失 |
| `/System/Library/LaunchDaemons/com.apple.CommCenter.plist` | `REG`：CommCenter 作业描述可见 | 若 LaunchDaemons 成功，该 plist 名不可见 |
| `/System/Library/LaunchDaemons/com.apple.SpringBoard.plist` | `REG`：SpringBoard 作业描述可见 | 若 LaunchDaemons 成功，该 plist 名不可见 |
| `/usr/libexec/xpcproxy` | `REG`：xpcproxy 可见；不证明能 exec | xpcproxy 或上级缺失 |
| `/System/Library/CoreServices/SpringBoard.app` | `DIR`：SpringBoard bundle 路径可见 | bundle 或上级缺失 |
| `/System/Library/CoreServices/SpringBoard.app/SpringBoard` | `REG`：SpringBoard 可执行文件路径可见 | 若 bundle 成功，该可执行文件名不可见 |
| `/usr/libexec/CommCenter` | `REG`：CommCenter 可执行文件路径可见 | CommCenter 或上级缺失 |

保留 7 条非缓存路径，缓存组为 2 条旧路径（cryptex `dyld` 目录及 `arm64e` 文件）加 5 条新路径，共 14 条。删除 `/System/Library/dyld`、`/System/Library/Caches/com.apple.dyld`、`/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64e`：前两项由更具体的目录或文件探针替代，最后一项与保留的 cryptex arm64e 对照重复，以减少刷屏。

`enuma-vn: <errno> <type> <path>` 格式不变。cryptex 文件标签用 `.../Cryptexes/OS/.../dyld/` 加完整文件名；传统路径文件用 `.../Caches/com.apple.dyld/` 加完整文件名（含 `.symbols`）；SpringBoard 可执行文件沿用 `.../CoreServices/SpringBoard.app/SpringBoard`。其他标签为完整路径。

## 主机检查与未验证项

此前源码差异断言保留空行而误报；现在分别断言新增 5 条、删除 3 条的路径集合，且公共路径标签与探针行之外的源码不变。

- r13 `kern_exec.o` 477720 B `9d1941370d5cc240d771276f0a410b71f9ca8884e6db1eec8f7c6d76fb6afb9a`；r14 479808 B `9c8a1211e2d9c3722f5512519d3dc942164ad56ff0dfe7f94bd811ca0bd6793c`。其余保存对象及 1022 个显式链接输入哈希相同。
- r14 native `b52fff2481d99f253a3d76877dab801e881a305ddb12b5dc50e70fa77dfd1995`；prelink `3bcff23a352a44316f72e9d7e5445c384b3cd01286546aaf1597b4ac553f1fca`。对象、native、prelink 各有唯一 `enuma-vn:` 格式串；机器码探针 printf 调用点 r13 12、r14 14；两个链接产物无 undefined。
- 第二次断言问题：`package()` 中 recipe 哈希常量误多一个 `e`，导致打包前失败；常量已更正为实际 SHA-256 `c2f37534b4d3695dfd7aa324af83bc09bb9ebaedacf991fd978809edff7b7d39`。只重跑 `package`，未重建内核。
- r14 payload 167772160 B `bd25d7d8df3b3743e498b9aedbbf5bcf542d6a83d4ac8adeb79387e73a314762`；boot 169951232 B `6022cca4d56b988132a6c96222a7b8537d9d9639359eca0d2b733881c9f2fa4a`。
- 生成 FAT 前注入 r6 ADT，读回 14048 B `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059`，与 r13 相同；initrd 1142976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`，trustcache 61356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` 也与 r13 相同。FAT 读回 kernel 等于 r14 prelink，boot ramdisk 等于整个 payload；root-match 输出 OK。
- r13 三件产物打包前后哈希未变：prelink `5f7df3bdf7111c44536e3d2eb3d89401541adfd4fb5b90bce992a7c6060dfd5a`、payload `ee2d0aabf66ba1e8a769df03953da7bfad929fa88f39e49cde4f9cfabc4d4e66`、boot `0fc6fd9536be414e420d4dedae48494e6ad10c257b7e824a4b7bcfb0a25e5ae4`。r14 相对 r13 的 manifest 产物只有内核、payload、boot 内容变化；相应长度、ADT、initrd、菜单、boot 参数、FD、DTB 不变。详见本地产物 `delta-vs-r13.json`。
- WSL root：`/home/wh1stl3/.local/bin/python3.11 -B scripts/build-enuma-r14-arm64-cache-probe.py kernel`；修正常量后仅运行同脚本 `package`。实机路径可见性、缓存能否被 dyld 使用、GUI 与持久性尚未验证；无独立 verifier 结果。
