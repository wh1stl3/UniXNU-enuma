# enuma r9 单次实机观察（2026-11-21）

`self-checked`：记录主控提供的操作与 `vision` 逐行核读，未重复上机、录像核读或构建。阶段不提升。

## 操作

- 2026-11-21 20:40:24 +08:00 一次 `fastboot -s <enuma> boot`，exit 0（`Sending 165968 KB OKAY 3.964s` / `Booting OKAY 0.259s`）。claim `.cache/enuma-timebase-r9-20261121.claimed` 已消耗，禁止访问、删除、重放。
- 镜像 `out/ufs-sm8250-launchd-display-20261121-r9/boot.img`，169,951,232 B，SHA-256 `fd5da6e4084d9b85e9f3921b15f1d4b9c8ce0e6dbb6c89681dfa603d14563669`。
- 录像 1300.598 s；前 90 s 以 4 fps 抽帧读探针，全片按 1 fps 抽帧；影像不入库。

## 探针实测

`vision` 逐行核读如下，全部探针行位于 `load_init_program: attempting to load … launchd` 之前：

```text
enuma-tb: enter seq=0 cntvct=32377400697 abstime_ns=1686322952500 cal=1686.322952
enuma-tb: exit seq=0 cntvct=32473440840 abstime_ns=1691325043802 cal=1691.325043
enuma-vn: 0 DIR /System/Library/LaunchDaemons
enuma-vn: 0 REG /System/Library/LaunchDaemons/com.apple.CommCenter.plist
enuma-vn: 0 REG /System/Library/LaunchDaemons/com.apple.SpringBoard.plist
enuma-vn: 0 REG /usr/libexec/xpcproxy
enuma-vn: 2 - /System/Library/dyld
enuma-vn: 0 DIR /System/Library/Caches/com.apple.dyld
enuma-fs: / 3225600 113900
enuma-fs: /private/var 2096676 2087620
enuma-fs: maxvnodes 66560
```

未出现 `var-critical`。Δcntvct = 96,040,143，除以 19,200,000 约 5.00209 s；Δabstime 约 5.002091 s。第三次独立启动仍为约 5.002 s 板内差值；不证明对独立真实时间的准确性。前两次见 [r8 观察](enuma-r8-device-20261121.md)。

## 判读与边界

- `/private/var` 在 exec 前快照的总量为 2,096,676 KiB（约 2047.5 MiB），可用 2,087,620 KiB（约 2039 MiB），总量减可用约 8.8 MiB；该时点不是空间耗尽。与 evb10 所述 256 MiB 卷 ENOSPC 情形不同；比较卷容量应使用 `total_kib`。这不排除后续或其他文件系统的空间问题。总量减可用不直接证明运行时写入量；剩余空间充足与 SpringBoard 未真正运行的假设相容，但不能证明该假设。
- CommCenter plist 在 exec 前视图解析为 `0 REG`，排除该次探针视图中该路径缺失；不能据此排除 launchd 后续视图或访问权限问题，也不能确定 `Failed to bootstrap path` 原因。候选包括所引用可执行体不可用、服务域或沙箱拒绝，均未证实。
- `/System/Library/dyld` 返回 ENOENT，与 iOS 17 将 dyld 共享缓存放在 cryptex 路径 `/System/Cryptexes/OS/System/Library/dyld` 一致；本轮未探该路径，不能断言缓存缺失。
- `/` 的 `statfs` 为总量 3,225,600 KiB（约 3.08 GiB）、可用 113,900 KiB（约 111 MiB），与 SystemOS 只读叠加侧相符，不作为可写空间判据。
- `vfs_context_current()` 是 PID 1 exec 前凭据，不可据此推断 launchd 后续打开或读取权限。路径解析为 REG 不证明文件内容、可执行体可运行或服务成功启动。

## 下一步候选（未实施）

补探 `SpringBoard.app` 主可执行体、CommCenter 可执行体、`/System/Cryptexes/OS/System/Library/dyld` 及其目录项，以区分可执行体缺失与其他候选；仅凭 exec 前查找仍不能证明或排除后续域或沙箱拒绝。
