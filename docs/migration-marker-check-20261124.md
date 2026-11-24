# Migration marker check — 2026-11-24

`self-checked`，仅离线只读分析；未构建、未访问设备。nabu 与 enuma 是不同设备，不能直接套用其运行结论。

## 1. nabu 做了什么

公开仓 [Lux12138/unixnu-nabu](https://github.com/Lux12138/unixnu-nabu/tree/156163f72d19d61173d4b3c8f59715cb07724d60)，固定 commit `156163f72d19d61173d4b3c8f59715cb07724d60`：

* [README.md:41-46](https://github.com/Lux12138/unixnu-nabu/blob/156163f72d19d61173d4b3c8f59715cb07724d60/README.md#L41-L46)：“`sheng-mig=1` 把 264 B 强制迁移态写进了 `com.apple.migration` 的 CFPreferences 域，覆盖了 365 B 官方完成态，导致 `lastBuildVersionPref=(null)`，每轮强制重跑数据迁移”；“保留官方完成态，把强制态写去无害路径 `com.apple.migratiox.plist`。”
* [board-report-l730.md:3](https://github.com/Lux12138/unixnu-nabu/blob/156163f72d19d61173d4b3c8f59715cb07724d60/board-run/reports/board-report-l730.md#L3)：“`setup_skip[4]` 的 365 B 官方完成态 `LastSystemVersion=21H461 / DMUserDataDisposition` 与 readback 仍写旧 `com.apple.migration.plist`”。同文 :25 列出 `LastSystemVersion / DMUserDataDisposition / SyntheticDidUpgrade / buildVersion`。该文件位于 `/var/mobile/Library/Preferences/`；不是 `com.apple.DataMigration.plist`，后者是相邻不同的链（同文 :13）。
* [board-report-l729.md:7](https://github.com/Lux12138/unixnu-nabu/blob/156163f72d19d61173d4b3c8f59715cb07724d60/board-run/reports/board-report-l729.md#L7) 原文：“`System build version changed from (null) to 21H461. Migration necessary.`” :11 记录 l727 中 `LaunchServicesMigrator`、`MSUDataMigrator` 成功，`SystemAppMigrator` 启动但完成通知及 UI 交还标志全 0；这是日志而非重启计数器。
* [board-run/rounds/l730.json:31](https://github.com/Lux12138/unixnu-nabu/blob/156163f72d19d61173d4b3c8f59715cb07724d60/board-run/rounds/l730.json#L31) 记录 seq0/seq1 解码 os_log：`System build version unchanged from 21H461. Migration not necessary.` 分别 5 / 11 条，`finishedStartup:YES` 和 `Dismissing overlay` 各 2 条；为 nabu 作者的观察，未独立复核原始日志。

## 2. enuma seed

只读检查 `out/data-seed-macos-20261119/data.dbr`：SHA-256 `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`，与 `data-seed-20261119-generation.md:52` 一致。方法：对 DBRDISK1 打包文件全文件运行 `strings -a`，不是 APFS 目录树解析。字符串命中可证明字节存在，不能证明当前活动目录项、完整路径或文件内容；未命中也不能证明不存在。未核当前载荷与此文件字节一致。

| 项 | 结论 |
|---|---|
| `com.apple.migration.plist` | 字符串有；`LastSystemVersion`、`21H461` 字符串也有，但未关联到活动文件。生成记录 :44 显示 `--build 21H461 --skip-setup`；固定官方工具 `UniXNU/scripts/make-data-seed.py:76-87` 写 mobile 域 `LastSystemVersion` 和 `DMUserDataDisposition`（内含 `SyntheticDidUpgrade=False`、`buildVersion`）。生成流程证据较强，不是 APFS readback。 |
| `.AppleSetupDone` | 未确认：字符串未命中，不足以证无。 |
| `disabled.plist`、`disabled.migrated` | seed 未确认：字符串未命中，不足以证无。另 `docs/launchd-disable-list-20261123.md:69` 记载条件启动策略在挂载后重写/创建它们，不是迁移完成态的证据。 |
| `MobileIdentityData` | 未确认：字符串未命中，不足以证无。 |
| mobile Preferences 前 20 项 | 未能按目录枚举。全镜像字符串包含 `com.apple.migration.plist`、`com.apple.purplebuddy.plist`、`com.apple.purplebuddy.notbackedup.plist`、`com.apple.springboard.plist`、`com.apple.managedconfiguration.notbackedup.plist`、`backboardd.plist`、`.GlobalPreferences.plist` 等；不能将全镜像字符串列表冒充该目录清单。 |

`data-seed-20261119-generation.md:106-117` 记载 seed 每次从 initrd 装载、写入易失；并指出模板 uid/gid 由 VM 用户产生，消费权限尚未验证。

## 3. enuma 历史记录命中

用 `grep -RinE 'migration|migrat|data-migration|DataMigrator|finishedStartup|Skipping boot task' docs --include='*.md'`；以下是设备日志原文命中（排除引用外机、服务名清单、host 分析及本文）：

```text
docs/enuma-r15-device-20261122.md:29:<fsck>                     Skipping boot task
docs/enuma-r15-device-20261122.md:30:<mount-phase-1>            Skipping boot task
docs/enuma-r15-device-20261122.md:31:<data-protection>          Skipping boot task
docs/enuma-r15-device-20261122.md:32:<finish-obliteration>      Skipping boot task
docs/enuma-r15-device-20261122.md:33:<detect-installed-roots>   Skipping boot task
docs/enuma-r15-device-20261122.md:36:<mount-phase-2>            Skipping boot task
```

这些是其他 boot task，不是 migration 被跳过的直接记录；所检索的 enuma 设备记录未见 `Migration necessary` 或 `finishedStartup` 运行时行。其他命中如 `docs/mach-service-dependency-inventory-20261123.md:1011` 是服务名清单，不是日志；`docs/public-repo-similar-blockers-20261124.md:13` 是 nabu 引用。

## 4. 判断与下一步

每次重新载入同一 scratch seed 成立，但“每次都被当作首次启动/反复执行迁移”**证据不足（弱可能）**：seed 生成方案本就写了与 nabu 同名的完成态，缺活动 APFS 文件内容、属主/权限、实际载荷身份及设备 datamigrator/CFPreferences 日志。RAM 写入消失只能证明状态不持久，不能证明原 seed 缺完成态或系统每次重跑。

不能据此推荐补 `.AppleSetupDone` 或 launchd `disabled.migrated`。最小下一步是只读 APFS 目录与 plist、核实际 initrd 同源，以及确认启动后是否覆盖 `com.apple.migration.plist`、是否出现 `Migration necessary`。如证实完成态确实缺失且是阻塞，候选最小更改是在实际 seed 的 mobile `com.apple.migration.plist` 中恢复该 build 的 `LastSystemVersion` 和对应 `DMUserDataDisposition`，并核消费权限；具体内容和是否足够仍需验证。改 seed 持续用于此 initrd 方案需重新打包载荷；运行时改写是另一机制，不必然修改 seed，但本次无授权实施。
