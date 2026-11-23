# launchd 禁用列表核查（2026-11-23）

状态：self-checked；只读源码与既有观察，不构建、不访问设备。比较范围为 lite 的 21 个 job；watchdogd 是另一个独立开关。

## 生成机制与完整清单

`package/BootWatchdogPolicy.c:19-24` 将逗号分隔 label 固定编译进 `lite_jobs`；`:56-71` 只有 `sheng-lite=1` 才遍历，`:28-45` 对每一个切片生成 `<key>完整label</key><true/>`。代码摘录：

```c
static const char lite_jobs[] =
    "com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.bluetoothd,"
    "com.apple.photoanalysisd,com.apple.mediaanalysisd,com.apple.mediastream.mstreamd,com.apple.icloud.searchpartyd,"
    "com.apple.findmy.findmybeaconingd,com.apple.familycircled,com.apple.financed,com.apple.softwareupdateservicesd,"
    "com.apple.ndoagent,com.apple.biomesyncd,com.apple.email.maild,com.apple.amsengagementd,com.apple.adid,com.apple.eyereliefd,"
    "com.apple.fairplayd.A2,com.apple.passd,com.apple.mobile.obliteration";
/* lite == 1: for (const char *job = lite_jobs; *job;) append_job(&job); */
/* append_job: <key> + label + </key><true/> */
```

每一项生成方式相同，都是上述静态字符串切分并生成 XML true；不是运行时发现进程。风险列是相对 SpringBoard、backboardd、FrontBoard、RunningBoard、HID、图形/显示、keybag/securityd、distnoted 的筛查；“未查证”不表示已经发现关联。

| 完整 label | 位置 | 风险筛查 |
|---|---|---|
| com.apple.identityservicesd | :20 | 相关：pipa 描述其参与 SpringBoard 同步 XPC 等待环，为间接关系，非 enuma 实证 |
| com.apple.locationd | :20 | 相关：pipa 描述其参与同一等待环，为间接关系，非 enuma 实证 |
| com.apple.CommCenter | :20 | 未查证 |
| com.apple.bluetoothd | :20 | 未查证，包括蓝牙 HID 的间接影响 |
| com.apple.photoanalysisd | :21 | 未查证 |
| com.apple.mediaanalysisd | :21 | 未查证 |
| com.apple.mediastream.mstreamd | :21 | 未查证 |
| com.apple.icloud.searchpartyd | :21 | 未查证 |
| com.apple.findmy.findmybeaconingd | :22 | 未查证 |
| com.apple.familycircled | :22 | 未查证 |
| com.apple.financed | :22 | 未查证 |
| com.apple.softwareupdateservicesd | :22 | 未查证 |
| com.apple.ndoagent | :23 | 未查证 |
| com.apple.biomesyncd | :23 | 未查证 |
| com.apple.email.maild | :23 | 未查证 |
| com.apple.amsengagementd | :23 | 未查证 |
| com.apple.adid | :23 | 未查证 |
| com.apple.eyereliefd | :23 | 未查证，包括视觉/显示相关性 |
| com.apple.fairplayd.A2 | :24 | 未查证，包括安全服务间接依赖 |
| com.apple.passd | :24 | 未查证，包括 keybag/securityd 间接依赖 |
| com.apple.mobile.obliteration | :24 | 未查证，包括 keybag/securityd 间接依赖 |

没有直接按名称禁用 SpringBoard、backboardd、FrontBoard、RunningBoard、HID、keybagd、securityd 或 distnoted；这不排除间接依赖。pipa 的原始注释见 `.cache/ref-pipa/package/BootWatchdogPolicy.c:17-21` 与 `board.toml:193-198`，参考仓 `xVanTuring/UniXNU-pipa@cdb3d62771e31d48d832853ee0c90964346d78da`；详见 `pipa-reference-20261123.md:143-154`。

## 同 donor sheng 对照

比较 `UniXNU/UniXNU-sheng@da9fab96aea0b5dcdb3bef730b10397276514dac` 的 `board.toml`，该提交配置 iPad7,1 / 21H461，并写：

```toml
"sheng-disable-watchdogd=1",
"sheng-disable-jobs=com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.bluetoothd",
```

来源：[固定提交 board.toml](https://github.com/UniXNU/UniXNU-sheng/blob/da9fab96aea0b5dcdb3bef730b10397276514dac/board.toml)，本仓 `docs/sheng-donor-branches-20261123.md:117-130,340`。比较的是该提交配置的 jobs，不泛化到 sheng 所有分支或其 Data 既存状态。

* 双方均有：com.apple.identityservicesd、com.apple.locationd、com.apple.CommCenter、com.apple.bluetoothd。
* 我方有、sheng 无（17）：com.apple.photoanalysisd、com.apple.mediaanalysisd、com.apple.mediastream.mstreamd、com.apple.icloud.searchpartyd、com.apple.findmy.findmybeaconingd、com.apple.familycircled、com.apple.financed、com.apple.softwareupdateservicesd、com.apple.ndoagent、com.apple.biomesyncd、com.apple.email.maild、com.apple.amsengagementd、com.apple.adid、com.apple.eyereliefd、com.apple.fairplayd.A2、com.apple.passd、com.apple.mobile.obliteration。
* sheng 有、我方无：无。两者还均单独配置 watchdogd，非 lite 的第 22 项。

## pipa 六项

`board.toml:197` 的六项逐一核对：identityservicesd、locationd、CommCenter、bluetoothd（完整前缀均为 `com.apple.`）包含；`com.apple.PerfPowerServices`、`com.apple.iomfb_fdr_loader` 不在 lite_jobs。交集 4/6。pipa 另配 watchdogd；它不属于六项。

## 声明与实际生效

源码 `:76-77,89-110,135-145` 截断重写 Data 上的 `disabled.plist`，写入各 key=true，并创建 `disabled.migrated`；原有 plist 内容不是合并保留。执行发生在 Data mount 后、PID 1 exec 前（`enuma-r19-watchdog-lite-host-20261122.md`），只是在启动前写 launchd 的禁用声明：该代码不杀进程、不拦截后续 spawn，也不证明 launchd 已消费或强制执行；具体运行时语义需独立验证。错误打印 errno 而非新加 panic；单看配置不证明文件成功写入。

目前未找到设备上直接读取完整 disabled.plist、launchd 消费该文件、或对指定 job 禁用/启用做正反对照的证据，因此未证明实际禁用生效。`enuma-r30-device-20261123.md:25-32` 的 `PerfPowerService=1` 是截断的进程 comm 计数，不是 launchd label 或 disabled 状态；且 `com.apple.PerfPowerServices` 本不在 lite 列表。用户提及 r44 同样形式的日志也不能证明 21 项生效。r23 的 pending spawn 是 user/501 域记录，不等同于证明 system 域此表被消费。
