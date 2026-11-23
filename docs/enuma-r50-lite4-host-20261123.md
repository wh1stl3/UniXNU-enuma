# r50 lite4 主机候选（2026-11-23）

状态：self-checked；未部署，未实机验证，启动链改动待 deep reviewer。
以 r49 为基线，仅重新编译 `BootWatchdogPolicy.c` 的 lite 字符串并替换
`libEnumaBootWatchdogPolicy.a`。保留 r49 参数、计数及周期重打；独立
`sheng-disable-watchdogd=1` 不变。

从实际 `prelink.macho` 执行 `strings` 读回（`native.macho` 相同）：
```
com.apple.identityservicesd,com.apple.locationd,com.apple.CommCenter,com.apple.bluetoothd
```
移除 `com.apple.` 前缀下的 photoanalysisd、mediaanalysisd、
mediastream.mstreamd、icloud.searchpartyd、findmy.findmybeaconingd、
familycircled、financed、softwareupdateservicesd、ndoagent、biomesyncd、
email.maild、amsengagementd、adid、eyereliefd、fairplayd.A2、passd、
mobile.obliteration。

## migration

`package/BootWatchdogPolicy.c:72-106` 在检查 marker 之前，以 `O_TRUNC`
重写 `disabled.plist`；成功后才在 `:131-142` 尝试创建
`disabled.migrated`，`EEXIST` 视为成功。因此既存 marker 不会跳过本代码
的 plist 重写，不改 marker，也不额外改 Data。写入失败可能留下截断文件，
这是原有行为；launchd 实际是否读取新内容尚未验证。

## 机械证据

WSL root `/home/wh1stl3/.local/bin/python3 scripts/build-enuma-r50-lite4.py --r50`
exit 0；构建前后 UniXNU HEAD 均 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`。
完整逐输入散列、命令与日志在 ignored
`out/ufs-sm8250-lite4-20261123-r50/{candidate-manifest.json,commands.json,logs/}`。

- `BootWatchdogPolicy.o` r19 原对象 SHA-256
  `a72890e6a15ae5be7418e74203575021c555d01d0e8a3c2502d8ec4e9b7f0736`，
  r50 `5ba0c9016bd5707c49c688fdac3750e5a6f179b39cb0ba50ba1f53d8791209d9`。
  策略 archive 原 `997e24f94eaa916b189d35ec7ff276b0d90609565a9b03e5482c423c63b3168d`，
  新 `0165cff70d4a3ef2190a143a439a5f0c90f10f1bb97bef16e8e3d856dae2ef94`。
- 1022 个输入逐项散列对照 r49 记录：仅 r49 本来替换过的 `kern_exec.o`
  路径不同；r50 沿用 r49 该对象。其余均相同，只有上述 archive 替换。
- 两张 Mach-O 各有一份完整四项字符串、一个 policy 格式串及一个 r49
  周期重打格式串；`_load_init_program` 各有一处调用 policy；两张均无
  undefined，包含 weak。只检查了旧长串片段不存在，不主张其他位置不含
  被移除服务的名称。
- ADT 逐字节相同，SHA-256
  `1fb896cf756f7cfbd93ac99ddb9ed6ac062ece28697a487708b6bbe3449a7457`；
  payload 文件成员仅 `Payloads/kernel.macho` 变化，配置成员相同，启动参数
  与 r49 相同。
- `boot.img` 169951232 B，SHA-256
  `f0d795af2317d6c1b80fc66de816473c2d58a799b4f3a348c3eea09803cfc959`；
  相对 r49 大小 delta 0；native 大小 delta -32 B，prelink、payload 大小
  delta 0。r49 boot 构建前后 SHA-256 均
  `1180a2c7b2c7f903cf412791a704a3051dbf6335f696f0183896a4c3b1f9d3f5`。

| 后续观察 | 可支持的判断 |
| --- | --- |
| SpringBoard 推进 | 与裁剪禁用列表有关联；单次观察不能确定具体服务因果。 |
| 没有变化 | 不证明策略已生效或无关；还需区分写入错误、launchd 消费及其他阻塞。 |

原先禁用的服务重新启动可能增加日志、负载，甚至重现早期 sig=9。
实际文件写入、launchd 消费、服务状态、图形输出、持久化均尚未验证；
不提升阶段、不授权设备操作。
