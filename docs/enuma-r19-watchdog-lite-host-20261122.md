# enuma r19：watchdogd 与 lite（2026-11-22）

`self-checked`；仅主机候选 `out/ufs-sm8250-launchd-keystore-20261122-r19/`。
基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；iPadOS 17.7.11 / 21H461。

## 策略与来源

[`HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503`
的 `package/BootWatchdogPolicy.c`](https://github.com/HuajiFruit/UniXNU-sirius/blob/ac0c900485f3c0cd18de9707579a1cdcd3365503/package/BootWatchdogPolicy.c)
（文件 SPDX MIT，仅取固定提交的文本）。`package/BootWatchdogPolicy.c`
保留其两开关、21 个 job 和 VFS 写入机制，不带 Setup、其他 job 参数或 BootProgress。

- `sheng-disable-watchdogd=1` 写入 `com.apple.watchdogd = true`。
- `sheng-lite=1` 对下表 21 个 label 写入 `true`。不会关闭 `iconservices.iconservicesagent`。
- 两者均通过 `/private/var/db/com.apple.xpc.launchd/disabled.plist` 改写
  launchd 的禁用集合，并创建同目录空的 `disabled.migrated`。只有相应参数等于
  `1` 才加入键；均未启用时不写，不清除旧表。非零 `errno` 记录后继续启动，
  不新增 panic。日志 `enuma launch policy: watchdogd=1 lite=1 errno=0`
  只表示写入路径返回成功，不证明 launchd 消费了覆盖表。

| Lite job（每项均加 `com.apple.` 前缀） | | |
|---|---|---|
| `identityservicesd` | `locationd` | `CommCenter` |
| `bluetoothd` | `photoanalysisd` | `mediaanalysisd` |
| `mediastream.mstreamd` | `icloud.searchpartyd` | `findmy.findmybeaconingd` |
| `familycircled` | `financed` | `softwareupdateservicesd` |
| `ndoagent` | `biomesyncd` | `email.maild` |
| `amsengagementd` | `adid` | `eyereliefd` |
| `fairplayd.A2` | `passd` | `mobile.obliteration` |

## 接线与 VFS 上下文

唯一 XNU 源码差异在 r19 生成的 `bsd/kern/kern_exec.c:8291–8292`，
`load_init_program()` 的 `native_owner_data_prepare()` 成功分支，launchd exec
前。`bsd/kern/bsd_init.c:1257–1283` 的 `bsdinit_task()` 用 `current_proc()`
进入该函数；沿该路径无调用方持锁，已经执行可睡眠的 VM 分配、APFS mount
及 VFS lookup，后续还会 exec。在 `kern_exec.c:8017–8044`，Data mount
flags 为 0，`/private/var` 回查要求设备匹配、APFS 且非 `MNT_RDONLY`，在
返回前 `vnode_put`。因此策略运行于可睡眠的 PID 1 bootstrap 线程、可写 Data
挂载之下。目标路径的父目录与权限、实际 VFS 写入结果未在 enuma 实机验证。
用户 scratch 的文件名槽、`+0x200` 写入块和 `+0x800` stat 槽位于原有一页内，
不覆盖 `+0x400–0x600` 的 SystemOS exec 环境槽。写入会截断已有表；写失败可
留下部分表，仅限当前临时 Data 诊断候选，不用于持久 Data。

使用 r17 记录的 BSD 编译参数及链接链，归档 `libEnumaBootWatchdogPolicy.a`
按既有板级归档方式显式 `-force_load`，只替换 `kern_exec.o`、新增该归档。
`XNU_BOOT_PROGRESS=0` 不变；默认 board、series、ADT 注入链和内存窗口不改。

## 实验判读

**两个开关可独立验证。** 将同一 `scratch-data.img` 作为每个候选的全新初始
Data，分别只加 `sheng-lite=1` 或只加 `sheng-disable-watchdogd=1`，保留其余
r19 输入，以同一墙钟窗口比较每类 job 的 spawn/exit 和 SIGKILL。不要用已写
过覆盖表的 Data 做关态对照。

| 观察 | 判读 |
|---|---|
| SIGKILL 减少且 Lite 名单中的 job 不再启动 | 支持 Lite 生效；双开不能单独归因 SIGKILL 降幅。 |
| SIGKILL 减少、Lite 名单无可见变化，且确认 `watchdogd` 原来启动、本次未启动 | 支持 watchdogd 假设；用 watchdogd-only 对照确认。 |
| 确认 launchd 消费 override、`watchdogd` 未启动，SIGKILL 仍无变化 | 不支持 watchdogd 是主要来源，转查 jetsam / launchd；未确认 override 消费时不能排除。 |

仅禁止 launchd 启动 watchdogd，不关闭内核/硬件看门狗、不拦截 SIGKILL；
停 daemon 可掩盖它原本会报告的真故障，内核/硬件看门狗保护是否完整未验证。
未验证项还包括实机文件写入、override 加载、21 个 job 在 enuma 的实际覆盖、
SIGKILL 来源、SpringBoard、交互与持久化。无设备操作；待
`deep_reviewer` 审查启动链变更和独立 `verifier` 复跑，不提升阶段。

## 主机证据

| 文件 | r19 字节数 | SHA-256 |
|---|---:|---|
| `BootWatchdogPolicy.o` | 54,392 | `a72890e6a15ae5be7418e74203575021c555d01d0e8a3c2502d8ec4e9b7f0736` |
| `libEnumaBootWatchdogPolicy.a` | 54,600 | `997e24f94eaa916b189d35ec7ff276b0d90609565a9b03e5482c423c63b3168d` |
| `kern_exec.o` | 479,984 | `488126693b9310fb710eeb7879e6afba139636edbf77504ebb34721185d23288` |
| `native.macho` | 91,876,104 | `da3de61584eda12d3c52fc618c42d8950565c2d08720a17003f986fc994536b7` |
| `prelink.macho` / FAT `Payloads/kernel.macho` | 124,719,104 | `1a4f8c51fc486415b80ad9e88c15182f2844a01c531bf8f9948043c996ff4063` |
| `payload.img` | 167,772,160 | `22fbf3ece2d0ed5a9729edab54b66e51c8fa638572fafbeb63fd8448840516da` |
| `boot.img` | 169,951,232 | `f05eeac6ac64f4db7c38ad4cac6500a92b5f3a445889b25f89a140a03d8eceaa` |
| FAT `Payloads/kernel.macho.adt`（不变） | 14,048 | `099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059` |
| FAT `Payloads/scratch-data.img`（不变） | 1,142,976 | `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470` |
| FAT trustcache（不变） | 61,356 | `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7` |

归档只含 `BootWatchdogPolicy.o`，链接 map 中唯一拥有策略符号。两个最终
Mach-O 各有一个 `_sheng_boot_watchdog_policy`、一个来自 `_load_init_program`
的直接 BL（`0xfffffff00bd0e290` → `0xfffffff00bfe4034`）、两个各一处的解析串
及一处完整日志格式串；`llvm-nm -u` 均为空（含 weak）。r17 `proc_exit`
格式串仍各一处。相对 r17：`kern_exec.o` +176 B，native +17,368 B，
prelink +16,384 B；`__DATA` 虚拟/文件尺寸仍为 1,310,720/278,528 B。
1,005 个链接表条目和 1,022 个显式链接输入的哈希未变（范围重叠）。

FAT 回读的 `unixnu.toml` 只追加两个 token，kernel 等于 prelink，
initrd 仍指向 `Payloads/scratch-data.img`。boot header v1 的 ramdisk
内容等于完整 FAT payload；FAT 内容 125,921,822 → 125,938,245 B，
payload 与 boot 文件尺寸不变，boot 距分区上限仍有 31,375,360 B。
FD、DTB、trustcache、ADT、initrd 和临时配置 pin 不变；root-match
exit 0，仍匹配签名 OS 窗口 `04769D26-2CA0-4825-B443-E2E5F88300F2`。

`delta-vs-r17.json`、`candidate-manifest.json` 和 `self-check/build-final/logs/`
记录逐项证据。重核 28 个 r17 冻结项与显式链接输入未变；r17 boot 仍是
`4fed789b186b0ef478f1f040f5a2b95e3db37c6c7c8f1fed83339d6f3dcc9d2a`。
Windows OpenSSL 重算 r19 boot、payload、native、新归档和两个对象的哈希
与记录一致。UniXNU 本地 HEAD 与 origin HEAD 前后不变，未重新钉上游。

独立复跑（保留现有候选，用空 r19 输出，WSL root）：
`python3.11 -B scripts/build-enuma-r19-watchdog-lite.py kernel`，随后同脚本
`package`；本轮这两步均 exit 0。初次编译在生成副本 `kern_exec.c:184` 缺
同目录 `kern_exec_internal.h`，已按 r16 的隔离编译方式复制同目录输入，首次
失败输出另留 `…-r19-incomplete-headers/`。在 UniXNU 根运行
`python3.11 -B scripts/porting-record.py check --device <UniXNU-enuma> --base origin/feat/step10-ramblock-probe`，
exit 0（15 个 area）；`git diff --cached --check` exit 0。
