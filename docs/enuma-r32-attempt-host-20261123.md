# enuma r32 pre-dispatch attempts（2026-11-23）

`self-checked`，仅主机构建；未上机。并发原子协议待 deep_reviewer；独立 verifier 未复跑。

## 位置与判读

隔离构建副本 `source/iokit/Kernel/IOUserClient.cpp`：函数入口 `:4376` 计 entry/entry_bb；task 拒绝 `:4386,4391` 计 early；MAC 拒绝 `:4397` 计 mac；properties 拒绝 `:4403` 计 early。MAC 调用位于 `:4396`，r30 `enuma-ctl` 的分派计数在其后 `service->newUserClient` 前。所有检查和返回值不变。入口在 CHECK 类型转换之前，不安全解引用原始服务取类名，因此使用入口进程 comm 前六个不同截断名，满表不记录额外名称；并发抢槽顺序不保证时间顺序。保留 r29 `enuma-bb` 和 r30 `enuma-ctl`。

30 秒一次、最多 20 次；每次最多 8 行：
```
enuma-att: begin entry=<n> entry_bb=<n> mac_rej=<n> mac_rej_bb=<n> early_rej=<n> early_rej_bb=<n>
enuma-att: [com] <comm>=<n>
enuma-att: end
```
计数器独立 relaxed 原子，dump 非事务快照；comm 按既有 16 字节表示截断，精确 `backboardd` 匹配。尝试不等于成功。

| 观察 | 判读 |
|---|---|
| entry_bb=0 | 窗口内未观察到 backboardd 进入该内核函数；不证明用户态未发请求，之前 IPC/参数阶段仍可失败。 |
| entry_bb>0 且 mac_rej_bb>0 | 有尝试到达并被 MAC 拒绝，与 vphone-cli `9becab4` 所述情形同型；不证明其他尝试也被拒绝。 |
| entry_bb>0 且 early_rej_bb>0 | 有尝试被 task/properties 校验拒绝。 |
| entry_bb>0 且两个 reject 均为 0 | 没有观察到上述拒绝；检查后仍可能阻塞或未到分派，须与 enuma-ctl 对照。CHECK 失败、窗口、非事务采样也限制判断。 |

## 构建证据

WSL root，`PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r32-attempt.py --dtb /root/enuma-step10/inputs/enuma.dtb` exit 0。固定基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`，构建后上游 HEAD `8542980d02b4d2cc5c32ee3542de1760b2562aac`。中间版本已保留为 `r32-intermediate`，不交付。

link 先于 prelink；`link-undefined.log` 空，native/prelink 的 `llvm-nm -u` 空，包含 weak 的符号检查也为零。`link.log` 末三行为一个 unused 参数及两个目录不存在警告。native 和 prelink 的三个 `enuma-att:` 格式各唯一，保留三条 `enuma-ctl:` 与三条 `enuma-bb:` 格式。native 反汇编 `is_io_service_open_extended` 中有四条 `_enuma_att_record` 调用；源码五处，优化后不应把机器调用数量当源码分支数。

| 产物 | r30 SHA-256 | r32 SHA-256 | 大小差 |
|---|---|---|---:|
| kern_exec.o | 8c92e5d24beb93dd487871b414763be189978ab11e5082f50d4fb3d9cc77cbe9 | b34d3a4d9d4e512c6274f8a15ac01c3f6716ce87bfec452c2be7e121246d5fe4 | +7720 |
| IOUserClient.cpo | 150c50ac86e58303210f2e7e5bf26108afa9f406475085d9e0bc760356cb1b54 | a916b55a8c43ea076d447e27330013277a9b9d3b2abca51c44265338dce7431b | +424 |
| native.macho | b572b63afa24eab0b9ab82ba14d2bd9910ca9e9e1a1cc82d0109c5ad032ee3fc | a95b41811931830683da764d88b6e50106f940b970495bea19f5c1de987357fa | +512 |
| prelink.macho | db892d0a6fc832ab4df399926198902d7e924c11adb149c142c4dcf23fa9e292 | 9c3413aad135e2e43b07855f45d021cecd3bf38b96c77c4990e321be020ff18e | 0 |
| payload.img | 5e1a5ec567ea42fdaea3df7229613d6e5bf28fb3a2bc81d4d846f2ec8ef2e63a | 877ee476c72af5e497d34f5a9ababd0f72b3736a01eef70e1457d3d3909cfe14 | 0 |
| boot.img | ac7ca17e9af1b133633d4c17ccea9e50b9713fadaf9d971adad4788140c63675 | 9fe165606f0300dd83e53e6377a58ff9a3791f08845701d95ff6fa1e9dd40011 | 0 |

boot 169951232 B。两个 filelist 仅上述两个对象路径不同，其余 1004 项路径相同；不声称对全部输入逐项重新哈希。r30 六项哈希与其既有记录一致，但构建前未做 r30 全目录快照，不能声称全目录前后不变。设备运行、拒绝路径、屏上输出、时钟间隔、原子并发及 independent verifier 均未验证。
