# 共享缓存 fixup 目标离线定位

状态：self-checked；仅本地 donor 静态分析，无构建、设备访问或运行时验证。

## 输入与方法

本地 `out/userdata-clean-20261112/044-76034-038.dmg` 以 `sgan81/apfs-fuse@66b86bd525e8cb90f9012543be89b1f092b75cf3` 的本机编译版 `-o ro` 挂载，读取 `root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64.{13,15}`，完成后 `fusermount -u` exit 0。文件分别为 113,868,800、104,628,224 字节。非设备回读。

Python 只读 mmap 全文件按 ASCII 字节序列搜索；偏移均为各自文件起始偏移，命中包括其他更长字符串的子串。手写 little-endian cache header 读取：offset 16 为 `mappingOffset`、`mappingCount` 两个 uint32；mapping 记录按 `<QQQII` 解为 VM address、size、fileOffset、maxProt、initProt。再遍历 `MH_MAGIC_64`、检查 ARM64 Mach-O header，并解析 `LC_SEGMENT_64` 和其 section，以 `VM = mapping.address + fileOffset - mapping.fileOffset` 与段的 VM 范围匹配；`LC_ID_DYLIB` 给出 image 名。对照 section 文件范围确认 `__text`。这不是完整符号表或调用链解析。ARM64 指令用 GNU aarch64-linux-gnu-objdump 2.38，`-D -b binary -m aarch64`，ADRP 另用目标 VM 作为 `--adjust-vma`。

## 类名搜索

`.15` 全文件逐字节查找：

| ASCII 子串 | 次数 | 文件偏移 |
|---|---:|---|
| `AWClientPreferences` | 1 | `0x42306de` |
| `AWAttentionAwarenessConfiguration` | 5 | `0x42308fd`, `0x4230bd4`, `0x4235fcb`, `0x42361bf`, `0x4236446` |
| `SASMyriadController` | 0 | 无 |

字符串命中证明该字节序列存在，不单独证明运行时类已注册；第三个名称在 `.15` 未命中不证明整个系统不存在该类。

## `.15+0x421e8bc`

原始 4 字节 `28 ad 1b b0` 是 `adrp x8, 0x1e8c43000`，PC 为未滑动 cache VM `0x1b169e8bc`；计算一个 PC 相对的 4K 页地址置入 x8，尚未读取该地址。配置替换 `c0 03 5f d6` 为 `ret`，跳转到 x30；若该处确为函数入口则立即返回，不设置返回值。后一条 `00 85 44 f9` 未改。sheng 注释将此点称为 `+[AWAttentionAwarenessConfiguration initialize]`，本次未独立解析函数符号，不能将此归属视为已证；亦未证明实际执行或修复生效。

前 64 字节、目标 4 字节、后 64 字节（行首为文件偏移）：

```text
421e87c  00 d0 40 39 c0 03 5f d6 02 d0 00 39 c0 03 5f d6
421e88c  00 d4 40 39 c0 03 5f d6 02 d4 00 39 c0 03 5f d6
421e89c  00 d8 40 39 c0 03 5f d6 02 d8 00 39 c0 03 5f d6
421e8ac  00 dc 40 39 c0 03 5f d6 02 dc 00 39 c0 03 5f d6
421e8bc  28 ad 1b b0 00 85 44 f9 9f 67 00 14 20 00 80 52
421e8cc  c0 03 5f d6 f4 4f be a9 fd 7b 01 a9 fd 43 00 91
421e8dc  28 ad 1b b0 00 81 44 f9 1f 6f 00 94 b6 af 86 94
421e8ec  f3 03 00 aa 94 70 00 94 f4 03 00 aa dc af 86 94
421e8fc  e0 03 14 aa
```

Cache mapping 唯一项：VM `0x1ad480000`、size `0x6394000`、file offset `0`、max/init protection `5/5`（R-X）。目标属于 `AttentionAwareness.framework/AttentionAwareness` 的 `__TEXT`，VM `[0x1b1674000,0x1b16bb000)`、文件 `[0x41f4000,0x423b000)`；细分 `__TEXT,__text` 起始文件 `0x41f52c4`、size `0x2fc8c`。未定位最近符号；最近的可识别构建标识字符串为 `@(#)PROGRAM:AttentionAwareness  PROJECT:AttentionAwareness-158.140.2`，其所在 ASCII 序列从 `0x422759e` 开始，距目标起点 `0x8ce2`（36,066）字节；不将随机指令字节碰巧形成的短 ASCII 算作可识别字符串。`AWClientPreferences` 字符串距目标 `0x11e22` 字节。

## `.13` 两条

配置来源：`UniXNU@693f5d9cae8a408dd18b39f3f9fdc4228c934241:profiles/os/ipados-17.7.11-21H461/profile.toml:41`。

| 文件偏移 | 原始 | 原指令 | 替换 | 替换指令 |
|---|---|---|---|---|
| `0x1b05bec` | `44 00 80 52` | `mov w4, #2` | `24 00 80 52` | `mov w4, #1` |
| `0x1b05b08` | `44 00 80 52` | `mov w4, #2` | `24 00 80 52` | `mov w4, #1` |

两处在同一 4K 文件页 `0x1b05000`，相距 `0xe4` 字节；各自仅将写入 w4 的常量从 2 改为 1，具体参数含义和调用对象未解析。Cache mapping 唯一项 VM `0x1a67c8000`、size `0x6c60000`、file offset 0、max/init 5/5。两者在 `PosterBoardServices.framework/PosterBoardServices` 的 `__TEXT`：VM `[0x1a82c1000,0x1a8325000)`、文件 `[0x1af9000,0x1b5d000)`，具体均在 `__TEXT,__text`（文件起点 `0x1afb0fc`、size `0x462f0`）。

按文件偏移最近的可识别长字符串线索为 Mach-O 依赖路径 `/System/Library/PrivateFrameworks/SoftLinking.framework/SoftLinking`，起点 `0x1afa4e8`，分别距两补丁起点 `0xb704` 和 `0xb620` 字节；这是依赖路径，不是目标函数名或调用关系。同页出现的短可打印字节无法辨认为有效字符串。

## 关联判断

**无法判定三处是否修复同一次死锁，证据弱。** 两条 `.13` 同 image、同页、同指令替换，相互关联的静态线索强，但未解析它们的函数和调用链。`.15` 在 AttentionAwareness，sheng 注释将其归为 AW 初始化死锁绕行；`.13` 在 PosterBoardServices，现有数据不能建立其与 AW 初始化或该死锁的因果关系，也不能证明独立。共处同一 profile 或文件邻近均不足以证明同一问题；缺实际符号、跨 image 调用链和线程等待栈。
