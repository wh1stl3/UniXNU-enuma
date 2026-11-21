# enuma r20 AMFI 主机候选（2026-11-22）

`self-checked`，未上机。r20 只在 r19 的 `sheng-aks=1` 后插入
`amfi_get_out_of_my_way=1`，不编译、不重新链接，复用 r19 的内核。
输出目录 `out/ufs-sm8250-launchd-keystore-20261122-r20/`。
打包前既有 wrapper 将 r6 ADT 注入官方 payload 构造；FAT 回读与 r6 字节相同。

## 参数与判读

XNU `bsd/kern/kern_codesigning.c:207–244,265–290` 在 DEVELOPMENT/DEBUG
配置解析此参数，设置 `CS_CONFIG_ALLOW_ANY_SIGNATURE` 和
`CS_CONFIG_GET_OUT_OF_MY_WAY`；r19 为 DEVELOPMENT 内核。
放宽签名可掩盖真正的签名故障，启动推进不能作为 trust cache 验证通过。

| 观察 | 判读 |
|---|---|
| 对比 r19，同一观测条件下 SIGKILL 减少 | 支持 AMFI 假设，不证明根因。 |
| 无变化 | 不支持该假设，但不排除 AMFI；未证参数实际生效时尤其如此。 |

相对 r17，r19 已同时打开 `sheng-disable-watchdogd=1` 和 `sheng-lite=1`；
r20 是三变量叠加。r19 对 r20 只隔离 AMFI 一项；若要拆开三项，在相同
内核和其他输入下分别关闭全部三个、仅启用各单项并逐项比较。每次必须从
同一个全新 scratch Data seed 开始，避免 r19 的 launchd 禁用表残留。
不凭本次候选推断任何运行时效果。

## boot-args 逐 token 对照

r19:
```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 sheng-disable-watchdogd=1 sheng-lite=1
```
r20:
```text
-v serial=3 rd=md0-ramblock pmgr=2 native-ufs-root=1 sheng-pmgr=2 offline-mobile-graphics-load=1 offline-legacy-register=1 offline-legacy-phase=4 offline-legacy-gop=1 offline-legacy-pm=1 offline-legacy-validate=1 offline-legacy-transfer=1 offline-legacy-cpu-present=1 sheng-vsync=60 sheng-aks=1 amfi_get_out_of_my_way=1 sheng-disable-watchdogd=1 sheng-lite=1
```
逐 token 断言：仅插入 `amfi_get_out_of_my_way=1`，余项和顺序不变。

## 内核输入哈希

下表各文件的 r19 与 r20 SHA-256 均一致；对象目录所有 14 个文件均列出。

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| native.macho | 91876104 | da3de61584eda12d3c52fc618c42d8950565c2d08720a17003f986fc994536b7 |
| prelink.macho | 124719104 | 1a4f8c51fc486415b80ad9e88c15182f2844a01c531bf8f9948043c996ff4063 |
| BootWatchdogPolicy.o | 54392 | a72890e6a15ae5be7418e74203575021c555d01d0e8a3c2502d8ec4e9b7f0736 |
| bsd_init.o | 180016 | cd54914a7be410887172aedde462d9648f6c7eaebf84fd9c67aca5b8ecfce656 |
| EnumaKeyStoreProbe.o | 141344 | e7d5910b79926faeab1da4fed6c6a4e2b39aef6ffd57e930c20f98ea0a12018e |
| EnumaUfsOwnerQuery.o | 157664 | 768ba0c391e8276fcf6a565a70eeb0b0c996d3f8561408f18105ee05c10a64ae |
| IOKitBSDInit.cpo | 325944 | 09d4a807c6a51ac44182a38588604a1b7ae410b50908e3de2057f0163f031d4b |
| IOUserClient.cpo | 701704 | da268498fdd2d14b9b105525bcbf07de09be436a94288d11c32fecb780fbdf7a |
| kern_exec.o | 479984 | 488126693b9310fb710eeb7879e6afba139636edbf77504ebb34721185d23288 |
| kern_exec.o.i | 841182 | ac8671b085711dd6e1de57830d4bdea4325e5e54b535f837774bf97fb0a1cf43 |
| kern_exit.o | 232552 | 1f2ab38169cd095e84da9a903dd844cba86f92fa12cd49036ffd4a28c6722761 |
| libEnumaBootWatchdogPolicy.a | 54600 | 997e24f94eaa916b189d35ec7ff276b0d90609565a9b03e5482c423c63b3168d |
| NativeKeyStoreEvents.late.o | 276350 | 0387cee85f7b738092d38ccb6ab03e9b33356f78b1fdf8efb5d916cff2a29867 |
| NativeKeyStoreEvents.o | 276472 | 964f793c0075574b2aeb97bd14f2a06838b4be920e9e86e014139a825694c03f |
| OSKext.cpo | 1179088 | e739162099834ec736410cf615d270923f598d463808aa9397f1ae8a34d80d7e |
| vm_unix.o | 385928 | 4b28590024c860c50b67eadf160ed0c3998dce7353f4ee93546f2f346baa0869 |

## 打包与 delta

| 文件 | 字节数 | SHA-256 |
|---|---:|---|
| r19 payload.img | 167772160 | 22fbf3ece2d0ed5a9729edab54b66e51c8fa638572fafbeb63fd8448840516da |
| r20 payload.img | 167772160 | b98dc66e0c40539c3e8caea9acdba747cdf9e4ac17b40d07767dd9fba609e3ab |
| r19 boot.img | 169951232 | f05eeac6ac64f4db7c38ad4cac6500a92b5f3a445889b25f89a140a03d8eceaa |
| r20 boot.img | 169951232 | 579da83aee339da92b8071a87044d207155c2b33012618aadf27f323e7f1c0ed |
| r6 / r19 / r20 FAT ADT | 14048 | 099dda97e8c01592cf9542b806b868ce098415ef9bab8ed7a01c8d03edd95059 |

六项打包产物 manifest 比较：仅 `self-check/unixnu.toml`、`payload.img`、
`boot.img` 不同；FAT kernel、ADT、scratch Data 不变。对 r19 的六项
manifest 产物重新计算文件长度与哈希，均与原 manifest 相同；对象目录及
native/prelink 比较如上。r20 recipe 的 `EXPECTED_ARGS` 是复制 r19 后唯一
改动；现有 recipe 的历史 status 和相对 r4 的 added_tokens 元数据未更新，
应以本记录及 FAT 实际回读为准。
payload 的五个 stage 文件逐项哈希比较只有 `EFI/UniXNU/unixnu.toml` 不同；
Windows Git 自带 OpenSSL 重算 r20 boot 和 payload 的 SHA-256 与上表一致。

本地基座 HEAD `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；打包命令
`/home/wh1stl3/.local/bin/python3.11 -B out/ufs-sm8250-launchd-keystore-20261122-r20/run_packaging.py --seed-feeds-from out/ufs-sm8250-launchd-keystore-20261122-r19/self-check-package/packaging/out/feeds`
（WSL root，仓库根目录）exit 0。独立 verifier 尚未复跑；设备操作未授权且未执行。
在 UniXNU 根运行 `python3.11 -B scripts/porting-record.py check --device
/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`，
exit 0（15 areas）。
