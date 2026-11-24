# enuma 启动策略会整体覆盖 disabled.plist（2026-11-25）

范围：当前 `package/BootWatchdogPolicy.c` 的 21 项版本、r64 生成源码及 r65/r66 已有主机记录。仅静态审查；未构建、未接触设备。

## 1. 触发、时序与覆盖方式

`package/BootWatchdogPolicy.c:54–60`：两个整数初值为 0，任一个解析为 **恰好 1** 才写；两者都不等于 1 就直接返回，不碰文件。`sheng-lite` 不是多档选择器。

```c
PE_parse_boot_argn("sheng-disable-watchdogd", &watchdog, sizeof(watchdog));
PE_parse_boot_argn("sheng-lite", &lite, sizeof(lite));
if (watchdog != 1 && lite != 1) {
    return 0;
}
```

调用点：`scripts/build-enuma-r19-watchdog-lite.py:81–86,92` 将 hook 插在 Data 检查之后；r64 生成的 `out/ufs-sm8250-ustack-20261124-r64/source/bsd/kern/kern_exec.c:8304,8318–8322,8353–8354` 在 `load_init_program()` 的 `XNU_OWNER_DATA_MOUNT` 分支中，先验证 scratch Data，成功后才调用策略，随后才走 `/sbin/launchd` exec 路径（另有候选路径选择）。Data 验证失败在策略之前 panic。r19 的同一调用点为生成的 `bsd/kern/kern_exec.c:8291–8292`，其 Data 检查详见 `enuma-r19-watchdog-lite-host-20261122.md:33–43`。

```c
int data_error = native_owner_data_prepare(p, (user_addr_t)scratch_addr);
if (data_error) panic("offline scratch Data mount failed: %d", data_error);
extern int sheng_boot_watchdog_policy(void *, uint64_t);
(void) sheng_boot_watchdog_policy(p, (uint64_t)scratch_addr);
/* ... */
error = load_init_program_at_path(p, (user_addr_t)scratch_addr, "/sbin/launchd", init_envp);
```

`package/BootWatchdogPolicy.c:62–77,89–110`：从空白 XML 字典构造新内容，对目标文件**原地截断后分段顺序写入**。没有读取旧字典、合并、`rename` 或 `O_APPEND`；截断成功即清掉全部原键，只有本轮生成的键会写回来。截断后出错可留下空/不完整文件，不会恢复旧表。`:127–148` 的 `disabled.migrated` 在 plist 写入和关闭之后处理；marker 已存在不跳过重写。

```c
strlcpy(policy, policy_head, sizeof(policy));
/* ... */
static const char path[] = "/private/var/db/com.apple.xpc.launchd/disabled.plist";
/* ... */
struct open_args op = {.path = scratch, .flags = O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW, .mode = 0644};
/* ... */
if ((error = write(p, &wr, &written))) {
    goto done;
}
```

## 2. 完整写入清单

`sheng-lite=1`（`package/BootWatchdogPolicy.c:19–24,28–45,66–72`），每项写 `<key>…</key><true/>`：

1. `com.apple.identityservicesd`
2. `com.apple.locationd`
3. `com.apple.CommCenter`
4. `com.apple.bluetoothd`
5. `com.apple.photoanalysisd`
6. `com.apple.mediaanalysisd`
7. `com.apple.mediastream.mstreamd`
8. `com.apple.icloud.searchpartyd`
9. `com.apple.findmy.findmybeaconingd`
10. `com.apple.familycircled`
11. `com.apple.financed`
12. `com.apple.softwareupdateservicesd`
13. `com.apple.ndoagent`
14. `com.apple.biomesyncd`
15. `com.apple.email.maild`
16. `com.apple.amsengagementd`
17. `com.apple.adid`
18. `com.apple.eyereliefd`
19. `com.apple.fairplayd.A2`
20. `com.apple.passd`
21. `com.apple.mobile.obliteration`

`sheng-disable-watchdogd=1`（`:17,63–65`）只写 `com.apple.watchdogd = true`。两个参数同为 1 时写并集（22 项，watchdogd 在前），没有互相覆盖或优先级。

## 3. 能否按参数只禁一个指定 label

**不能。** enuma 策略只解析上述两个参数（`package/BootWatchdogPolicy.c:54–72`）；没有 `disable-jobs=` 或 `sheng-disable-jobs=`，因而没有该类参数的语法或优先级。只开 watchdogd 开关能只写入一个键，但键固定是 `com.apple.watchdogd`，且仍覆盖整个文件。pipa/sirius 的可配置参数不是本板实现（`disable-list-revert-20261123.md:7`、`pipa-reference-20261123.md:154`）。

## 4. 失败可观测性

`package/BootWatchdogPolicy.c:76–150`：目录、打开、写入、元数据检查、关闭或 marker 操作的错误会走到同一条内核 `printf`，只报数字 errno，不报阶段；短写设 `EIO`。`errno=0` 表示写入/文件检查和 marker 处理走通，不证明 launchd 消费。marker 错误也可使 errno 非零，即使 plist 已完整写入。

```c
printf("enuma launch policy: watchdogd=%d lite=%d errno=%d\n", watchdog == 1, lite == 1, error);
```

内核控制台输出上屏时可看到这一行；查阅的设备记录未找到实机屏上命中。双参数未启用、或者构造 XML 时提前返回的错误（`:58–60,67–75`）不打印此行。调用点丢弃返回值，策略写失败本身不阻止 exec。

## 5. 对 seed 的影响

**是，当前参数下会覆盖。** r65/r66 的现有包记录均显示两个参数为 1（`enuma-r65-fp-host-20261124.md:93`、`enuma-r66-seedfix-host-20261124.md:31–35`）。一旦策略对 Data 里的 `disabled.plist` 成功打开并截断，seed 预置键就被清掉；即使同名键仍在，也是策略重新写的，不是从 seed 保留的。这改的是启动后挂载的 scratch Data 文件，不是主机上的 seed 镜像。两个开关都不为 1 时，此策略不覆盖；这不等于已证实 launchd 会读取 seed 表。

## 6. 与 backboardd 卡点的关系

**证据不足，只有弱间接关联。** 完成的重写与关闭都在 launchd exec 之前，不是 `__xpc_bootstrap_services` 当下正在进行的写入。若 launchd 消费此表，且该请求要加载的服务或其依赖命中禁用项，表内容可以改变后续服务可用性；没有证据表明它使本次 `0x320` 请求挂起。r65 FP 链定位到 PID domain uncork 注册的客户端调用，但没有实际请求内容、服务名或接收端响应（`fp-symbols-r65-20261124.md:64`）。donor 的 handler 静态记录显示可延后完成，未把它与此表的读取或某个禁用项相连（`launchd-21h461-routine-320.md:40–73`）。

## 7. iconservicesagent 是否在表内

**不在。** `com.apple.iconservices.iconservicesagent` 不在上述 21 项，也不是独立 watchdogd 条目（`package/BootWatchdogPolicy.c:17–24`）。

## 8. 加 seed 或参数是否有意义

当前双开关下，**只加进 seed 的 `disabled.plist` 无效**；填进 `sheng-disable-jobs=` 也无效，因为没有解析器。若要用这个内核策略单独禁用它，现有参数做不到；要改策略，或停用两个开关后另核 seed 表是否被 launchd 消费。本轮没有该 label 被目标 launchd 通过此表禁用的证据，也没有它参与 `0x320` 卡点的证据。

- enuma 是否整体覆盖 disabled.plist：**是**（任一开关为 1，且成功截断）。
- seed 级禁用配置是否有效：**无效**（当前双开关下的 `disabled.plist`）。
- `iconservicesagent` 是否在禁用清单：**不在**。
- 与 bb 卡点的相关性：**证据不足，弱间接关联**。
