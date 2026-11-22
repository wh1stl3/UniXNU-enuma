# enuma r28 framebuffer 链计数（self-checked）

隔离候选 `out/ufs-sm8250-launchd-fbcount-20261123-r28/`；r26 recipe 重放，未接入默认 series。基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；UniXNU upstream HEAD 开工前查询为 `279ed14ec316d3a62c869e08f3932c08f7372b1d`，未改变基座。

## 入口与限定

行号相对于候选 `source/display/NativeLegacyDisplay.cpp`。计数均为入口/调用尝试，不证明成功或实际显示：

| 字段 | 行号 | 语义 |
|---|---:|---|
| start | 481 | `startDisplay` 调父类 `start` 前 |
| open | 840 | `newUserClient` 进入，不证明打开成功 |
| refresh | 534 | `getRefreshAttributes` 进入，是刷新属性查询，不是显示模式设置 |
| kick | 551 | `kickSwapQueue` 进入；vsync 注册及内部重试也可触发，不等于提交 |
| scanout | 588, 622, 650, 668 | 四处调用 `native_legacy_prepare_scanout` 前，累计调用次数 |
| swap | 767 | `validateSwap` 进入，含拒绝的请求 |

四个 scanout 点都位于 `kickOnce` 的已验证待处理 swap 传输路径，但分别用于空白填充、普通表面 GPU offer 前、half 格式 CPU 转换前及普通 CPU 拷贝前；并非四种互斥请求，单次请求可经过多点，不能当作帧数。mode 和 owner **不可观测**：该子类源码无模式设置/查询或 owner 绑定入口，父类二进制内部行为未插桩；`getRefreshAttributes` 不等价于 mode，`getDisplayDimensions` 是父类接口及子类内部调用。

每个计数有独立 64 位原子计数和独立 128 位原子 comm；名字取当前上下文 `p_comm`，空或内核上下文为 `-`，最多 16 字节。不同线程竞争时计数和名字并非事务快照，异步上下文也不必是原始提交者。定时复用 r26 `THREAD_CALL_OPTIONS_ONCE`：launchd 成功 exec 后 30 秒首次、最多 20 次，停止后不再计数。

另有八槽 open 表：进入时原子保留不重复的槽并记录当前 comm、PID、type；父类 `newUserClient` 调用返回后、override 返回之前写入 `ret` 并 release 发布，dump acquire 后才读取。返回码不是在 override 实际返回之后记录。未用或已占但尚未完成的槽都显示 `-`；表满后不覆盖，后续 open 仍计数但不再记录逐次详情。最终回调后不再接受新记录。它记录最先获得槽的八个调用，未承诺并发调用的绝对时间顺序；PID 0/名字不可取用 `-`。

```text
enuma-fb: begin
enuma-fb: start=1 comm=-
enuma-fb: open=2 comm=IOMFB_FDR_Loader
enuma-fb: refresh=0 comm=-
enuma-fb: kick=0 comm=-
enuma-fb: scanout=0 comm=-
enuma-fb: swap=0 comm=-
enuma-fb: open[0]=IOMFB_FDR_Loader pid=100 type=0 ret=0
enuma-fb: open[1]=backboardd pid=101 type=0 ret=0
enuma-fb: open[2]=-
enuma-fb: open[3]=-
enuma-fb: open[4]=-
enuma-fb: open[5]=-
enuma-fb: open[6]=-
enuma-fb: open[7]=-
enuma-fb: end
```

示例仅示格式，并非 r28 运行结果。共十六行，`uint64_t` 最大 20 位、comm 最多 16 字节，每行均小于 80 字符；背景日志可穿插。

| 观察 | 限定判读 |
|---|---|
| open>0，refresh=0 | 打开入口曾被调用、刷新属性入口未被调用；不能推出模式设置前阻塞 |
| refresh>0，swap=0 | 刷新属性被查询过、swap 校验未到达；不证明同一调用者或调用顺序 |
| kick>0，swap=0 | 队列 kick 被调用，不证明提交，因为 vsync 可触发 |
| swap>0，scanout=0 | 校验有入口但准备 scanout 未调用；不证明校验成功 |
| scanout>0 | 至少一次准备调用发生，不证明其成功或显示完成 |

## 链接与机械证据

WSL root 执行 `PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r28-fbchain.py --dtb /root/enuma-step10/inputs/enuma.dtb`，exit 0。链接后、prelink 前 `llvm-nm -u native.macho` 输出为空；native 与 prelink 含 weak 的 undefined 均为零。`llvm-nm native.macho` 显示 `fffffff00bfe1554 S __GLOBAL__sub_I_NativeLegacyDisplay.cpp`。`logs/link.log` 末尾：clang unused `-mllvm -disable-atexit-based-global-dtor-lowering` 警告，以及 `-L.../usr/local/lib/kernel/platform` 和 `-F/System/Library/Frameworks/` 目录不存在两条 warning；无链接错误。

native 的机器指令分支调用点数：start/open/refresh/kick/swap 各 1，scanout 4，open 完成记录 1。native 与 prelink 中十个输出格式串各一份；构建检查输出与最终反汇编为 self-checked。

| 项目 | r26 SHA-256 | r28 SHA-256 | r28 bytes / 相对 r26 字节 delta |
|---|---|---|---:|
| kern_exec.o | b78ba80cbacf7cb2b723ff7c8389528dd9f26ed490de6f7b45d651da2dafc801 | 8cbef9e8eb7f9c4cf9d559f3df1a07bb3fc9536086330a8e0b83196f54e373b8 | 498776 / +10008 |
| NativeLegacyDisplay.late.o | 1dc8ebfc30afc18c8ec80acc81dac7b0cdac78257225967221f5ffcbe25980c1 | a3e9453cb0d4d3b95040d30db6e79de96b32f59c01333c4cda4d67d2b6a60023 | 349222 / +700 |
| libEnumaGopLegacy.a | 73c5a2bf86b82a449bf79fed5623501580514b799c435ee86012498ee80875c1 | 45ae470d98ee459c45b68b2e99904c490a9ecc37fdf34f9a481b86caf36c1478 | 599840 / +696 |
| native.macho | 9738e8b30d3b9ab4456b76e6c84be5316b1690775fb85868d02459a3287b86e9 | 81b5d8e9040b1af18def7e700b494d1f2ad12a36b582c39ae56a05322395d2b6 | 91890176 / +800 |
| prelink.macho | 3552500b69a268357f083ce93871b0a761c4491cf6c0c83eb611ac8e03711884 | e2df38bc6c7ce3ad838ea51fd63ea661399ae0e41dbfbfafc05370f936420a18 | 124735488 / +4096 |
| payload.img | 91675ca1757ca762a3f8fb92785a2523ef593c027678b2083ce883e849a0fb77 | e5064107d4d129acde86a63e1ce98403eae827462af2415a0bef46e4b744fb05 | 167772160 / 0 |
| boot.img | a60d634bb92e9be03af29df71d09634a543f924c9b27281a299d33a2b139bd92 | 44694629826b0b7e7a8dc5332b8891a013fed892a468f7c46e78012796f8ca0d | 169951232 / 0 |

1,006 filelist 项中仅 `kern_exec.o` 路径及内容不同，其他 1,005 项字节相同；显示归档另两成员 `EnumaLegacyDisplay.o` 和 `original-bindings.o` 相同，SHA-256 分别 `612b2f98bfd89669066b365391159c6bcba89372f4f0208e5321259b34847101`、`3650732909f83fc31951f9dfea24eae435e89004d7a5c391ee2888f11fad5773`。构建前后 r26 全部 61 个文件哈希不变；清单还记录相同外部链接输入。清单的 `old` 比较目标是 r23，上表才是 r26 delta。

ADT 14088 B `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5`；initrd 1142976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`；trustcache 61356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`；`unixnu.toml` 804 B `272e2ed556a51d5706f60fcc5daa33c045fcd5d99f03d71cd1b88138d101afee`，均与 r26 一致。FAT 仅 kernel 成员变化；payload offset 2179072，注入的 ADT 与 boot-args 不变。详细清单为 `candidate-manifest.json`。

记录检查：在 `UniXNU` 执行 `python3 -B scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`，15 areas，exit 0（self-checked）。

第一次逐次表构建链接成功，但格式检查把 NUL 写成字面 `\\0`，导致断言失败；修复检查后重建成功，失败目录保留。未实机验证定时、调用顺序、caller、呈现或显示；未由独立 verifier 复跑最终构建，并发发布协议待 deep_reviewer。
