# enuma r24：去显示参数的对照候选

主机 `self-checked`，未上机；以 r23 为基线，仅删显示相关启动参数，
调查显示适配器是否参与 SpringBoard exec 后状态和用户域 bootstrap。
不是独立 verifier 复跑或设备运行结果。

## 参数逐项对照

从 r23 最终 FAT payload 的 `EFI/UniXNU/unixnu.toml` 读回完整原文：

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1
```

按原顺序：留 `-v`、`serial=3`、`rd=md0-ramblock`、`pmgr=2`、
`native-ufs-root=1`、`sheng-pmgr=2`；删 `offline-mobile-graphics-load=1`、
`offline-legacy-register=1`、`offline-legacy-phase=4`、`offline-legacy-gop=1`、
`offline-legacy-pm=1`、`offline-legacy-validate=1`、`offline-legacy-transfer=1`、
`offline-legacy-cpu-present=1`、`sheng-vsync=60`；留 `sheng-aks=1`、
`amfi_get_out_of_my_way=1`、`sheng-disable-watchdogd=1`、`sheng-lite=1`、
`sheng-touch-hid=1`。九个指定删除项各出现一次；没有额外 token。

包内 r24 读回：

```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1 sheng-touch-hid=1
```

## 文本控制台判断

预计仍可输出，但 r24 本身未实测。[r4 实机记录](ufs-launchd-data-20261119-observation.md)
的参数不含这九项，记录了屏上持续数分钟的 launchd 用户态文本；该屏幕记录是主控转录，
不是 r24 的实机验证。r23 保存的 `source/bsd/kern/bsd_init.c:542-555` 中缺
`offline-mobile-graphics-load` 时直接返回，不加载 IOMobileGraphicsFamily 或从此入口注册
legacy 显示。r23 保留 `-v serial=3`。此前 GOP 观察的控制台释放关联 swap，
见 [GOP 记录](enuma-gop-r5-device-observation.md)。这些证据支持保留文本路径，
但 r4 的内核和 r24 不同，不能保证本次屏上输出；若无文本则无法观察实验结果。

## 机械证据

复用 r23 所有内核输入，不重编。以下哈希在打包前后核对 r23 未变；
native/prelink 同时复制至 r24 并校验一致。对象使用 r23 原文件，并未复制到 r24。

| 文件 | SHA-256 |
|---|---|
| native.macho | `306b71f131c9814ea97e5daac7055546f1fc03327d8647ad8bb7426d8fe1f1a9` |
| prelink.macho | `edbb9422c9ae53f486aa540482aaa5f9b0b2489cc7428abfbbcfc76543ca1062` |
| objects/EnumaHidStandin.o | `6476eee54d2852d47a62f412992c161302153f1675b34af4a93dce281f903d27` |
| objects/NativeHidInput.o | `a03a15cfe506f3e83ff50e98991a79a9ba754e64aed299b2c92d81edd606d348` |
| objects/NativeHidInput.late.o | `537f032122d77c4411d0a325128f207a0dea5de86037a0825007336abbd689fe` |
| objects/hid-original-bindings.o | `d6290d09b1830369a8b4f637ef73357a8c1272a8d7136a15fdc2c7f4a2be7d6b` |
| objects/kern_exec.o | `304bc5c75a2045082b537db57e5b154631e8ea4a7a9610fd65827da4b70f3ff2` |
| objects/libShengHidInputStandin.a | `61e12135a41a2752233d7ad701fedfb499bb838e813a2d7481091d30991a2e3d` |

输出目录 `out/ufs-sm8250-launchd-hid-20261122-r24/`：

| 产物 | bytes | SHA-256 |
|---|---:|---|
| payload.img | 167772160 | `09cde35935d862faf771d3ee09233e8ca7dd98ac1209aa7b6247e36437c976af` |
| boot.img | 169951232 | `058090e9a3c63335b3ebc59f05d1b6c2a8ba0e7365219e6dd2ad69ee0c315d7d` |
| 包内 ADT | 14088 | `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5` |

包内 ADT 与 r23 逐字节相等，读回 memory-size `0xaa000000`（2720 MiB）、
sleep-disabled `1`；r23 主机记录已记录与 r22 相同。包内 kernel 同 prelink，
trustcache `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`、
scratch Data `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`
均不变。FAT 目录树不变，逐项读回的五个文件仅 `unixnu.toml` 改变，
其唯一文本变化为上述 args；FAT 元数据和 boot header ID 是派生变化。
boot payload offset 2179072，boot 中 payload 哈希与单独 payload 一致；
此前缀除 header ID 字节 576–595 外相同。
r23 `payload.img` `72723451bd753ab40ad4ab999b68046addf7fbc8b495ff8be9da22ca2b8f3dba`、
`boot.img` `f82391886dea2a47915a51c6455b51924285dc3ff8e447adc768ea1775e0da1b`
前后未变；其余 r23 文件未作全目录哈希。

主机打包命令 exit 0（WSL Ubuntu-22.04 root，设备仓根目录）：

```sh
PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin \
  /home/wh1stl3/.local/bin/python3 -B out/ufs-sm8250-launchd-hid-20261122-r24/build.py
```

该脚本面向空输出目录，不覆盖已有目录复跑；独立核验应在新输出目录复制脚本后执行。
在 `UniXNU/` 目录运行 `python3 scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`
exit 0，检查 15 区；独立 verifier 应复跑。

## 实验判读及未验证项

| 观察 | 判读 |
|---|---|
| SpringBoard 仍 exec、同样未观察到 bootstrap 退出 | 本次不支持显示参数为该现象的必要原因；单次观察不能排除显示参与。 |
| 行为明显不同 | 与显示参与相容；先排除观察时间和其他运行时变动，不能直接证明因果。 |
| SpringBoard 不再 exec | 重新评估启动前置与采样，不能判定卡住原因。 |
| 无屏幕文本 | 不能观察，实验无判读结果。 |

未验证设备文本、SpringBoard 存续/卡住、bootstrap 完成、backboardd、图形、
持久性或可交互性。未操作设备、未创建 claim；设备动作须另获授权。
