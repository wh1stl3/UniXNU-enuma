# pipa 与 enuma 的 cs / dyld 差异：闭包未闭合

状态：self-checked，静态分析；没有构建或访问设备。

## 实际闭包的阻塞

pipa 来源 `https://github.com/xVanTuring/UniXNU-pipa`，commit `cdb3d62771e31d48d832853ee0c90964346d78da`。其 `README.md:64-68` 报告同 donor 的 CPU 渲染 UI，但没有绑定该次实机的构建日志、UniXNU 主仓 commit 或完整补丁清单。`unixnu.lock:21-22` 只固定 Apple XNU 源 `d8b80295118ef25ac3a784134bcf95cd8e88109f`，不是 UniXNU 构建工具与补丁版本。

`scripts/kernel-round.sh:19-20,59-66` 使用旁边的 UniXNU checkout 调用 `unixnu build kernel`；`board.toml:39-70` 未声明 `patch_series`，`board.toml:123` 是固件补丁而非 XNU 补丁。仓内 `package/xnu-patches/native-smp-type-clusters.patch` 存在、`board.toml:284` 提到它，但本仓没有证明它在该次构建中被应用的脚本或记录。不能据文件存在或注释认定实际应用。

对照用本地 UniXNU `693f5d9cae8a408dd18b39f3f9fdc4228c934241` 的 `scripts/unixnu/kernel.py:170-187` 和 `scripts/build-xnu-4k-baseline.sh:37-56`：schema 2 用所选 series；旧模式 glob 主仓 `patches/xnu/*.patch` 和 `kits/XnuPrelink/patches/*.patch`。但 pipa 的历史主仓 revision、schema、源码副本状态和构建记录缺失，不能用当前 glob 推算其历史实际补丁数或相关项数。`README.md:91` 也显示该构建树存在仓外输入。配置使用不等于已验证的编译和链接。

## 主题对照

三态按证据使用：pipa 有 = 本仓明确配置或源码；enuma 有 = 对应源码/配置可见；enuma 无 = 有范围充分的反证。以下均不声称 pipa 历史 XNU 补丁实际闭包已确认。

| 项 | pipa | enuma | 作用和边界 |
|---|---|---|---|
| 4K 签名 hash cache | 有配置：`configs/pipa_defconfig:16-17` | 有：本轮题设已确认启用 `native-4k-signature-hash-cache.patch` | 本地基座该补丁 `patches/xnu/native-4k-signature-hash-cache.patch:31-32,84-107` 在 blob 可见前准备 hash；pipa 构建实际采用的补丁版本尚未知。 |
| 4K shared region ABI | 未知 | 有本地候选：`UniXNU/patches/xnu/native-4k-user-abi.patch:66-82` | 非 Apple 4K 下 shared-region submap 页移位改为 4K；不能单凭本地基座推定 pipa 实机采用，也未核实 r40 链接对象的该分支。 |
| text fixup | 未知 | 有：`scripts/build-enuma-r42-matchcnt.py:89-100,149-160` 处理 r44 ADT 与替换对象 | 本地基座 `UniXNU/patches/xnu/native-text-fixup.patch:192` 把 fixup 放入 slow 校验路径；pipa 仓未找到同名配置，不能证明其 XNU 没有。 |
| owner cache carrier | 未知 | 本地有候选，不等于启用：`UniXNU/patches/xnu/offline-owner-cache-carrier.patch:7-10,69-105` | 条件启用时允许满足严格设备及目录约束的跨卷 shared cache 通过映射检查；不是绕过页校验的证据，也未证实 pipa 或 enuma r40/r44 启用。 |
| IOKit 早期 graphics 加载 | 有配置：`board.toml:199-205` | 有源码：`out/ufs-sm8250-launchd-keystore-20261121-r11/self-check/build-final/source/bsd/kern/bsd_init.c:546` | `offline-mobile-graphics-load` 控制早期加载；两者实际启用、链接及运行顺序不能仅凭此项等同。 |
| launchd job 裁剪 | 有配置和实现：`board.toml:193-198`、`package/BootWatchdogPolicy.c:43-49,60-75` | 未知 | pipa 策略在 Data 的 launchd `disabled.plist` 写入所列 job 和 watchdogd；属于辅助实现与启动参数，非已证实的独立 XNU 补丁。enuma 跟随路径和最终链接尚未逐项闭合。 |

## 开关与因果

pipa `board.toml:177-268` 的默认 kernel_args 不含 `cs_integrity_skip`、`amfi_get_out_of_my_way` 或 `-nocs`；enuma 跟踪版 `board.toml:75` 同样不含。pipa `kernel-round.sh:9-10,27-32,64-65` 允许单次追加参数，因此默认值不能证明历史实机实际参数；enuma r40/r44 实际打包 boot args 未在此项核验。

**结论：没有已证实的 pipa 实际补丁可以解释共享缓存页不进 slow 校验或 fixup 不命中。** 这不等于证明 pipa 没有此类补丁：历史构建闭包缺失。r44 的 `parsed=4 applied=1 bits=0x08` 只证明观察窗口内三个目标未应用、普通文件正控已应用；不能据此断言共享缓存页未进入 slow、taint 是原因，或 SystemOS 认证失败就是原因。需先获得 pipa CPU UI 那次的 UniXNU commit、`xnu-patches.list` 或构建日志及最终对象/构建配置，再完成逐补丁差分。
