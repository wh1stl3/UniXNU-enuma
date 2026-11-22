# enuma r29 backboardd newUserClient 扫描

隔离候选，复用 r28 构建与 ADT 输入；不接默认 recipe。仅记录 `is_io_service_open_extended` 内虚分派 `service->newUserClient` 的调用，不覆盖服务匹配、其他打开路径或用户态等待。返回值是该虚分派的返回值，不是整个 syscall 的最终返回值。

调用者 `current_proc()->p_comm` 精确等于 `backboardd` 才计数；不可取 comm 无法判定属于 backboardd，因此不记入表。类名来自分派前 `getMetaClass()->getClassName()`，不可取或空时为 `-`，截断为 24 字节。`bb_calls` 记录所有命中；CAS 分配前 12 个槽，满后只增 overflow，不覆盖。并发时顺序是 CAS 占槽顺序，不保证真实发生先后；返回后 release 发布，dump acquire 仅打印已完成槽，进行中槽暂时省略。计数和表不是事务快照，计数可能先于条目；调用从未返回也不会出现条目。计数持续递增，输出仅在 r28 计时框架前 20 次、每 30 秒发生。

```text
enuma-bb: begin calls=<n> overflow=<n>
enuma-bb: [0]=<class> type=<n> ret=<n>
enuma-bb: end
```

最多 14 行，不打印未完成及未用槽；原有 r28 framebuffer 输出保留。

| 观察 | 限定判读 |
|---|---|
| 前几项 HID 相关类 | 该路径已尝试打开这些 HID 类，不证明 HID 初始化完成或停在该处。 |
| 均为其他类 | 表内没有显示/HID 的打开，不证明尚未执行匹配或初始化；overflow 后无法排除后续打开。 |
| 最末项失败 | 该分派返回失败；不证明进程因此停住。 |
| calls 大于已打印项 | 可能因进行中、未返回或 overflow；不能仅凭行数判断阻塞位置。 |
| calls=0 | 仅表明该定时快照之前没有可识别的 backboardd 调用抵达本分派点。 |

未验证：运行时计时、并发交错、类名与进程身份、用户态行为及显示输出；新原子协议需 deep_reviewer 审查，最终构建待独立 verifier。

## 主机构建与机械证据（self-checked）

候选 `out/ufs-sm8250-launchd-bbscan-20261123-r29/`；WSL root 执行 `PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r29-bbscan.py --dtb /root/enuma-step10/inputs/enuma.dtb` exit 0。UniXNU 基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`；前后远端 HEAD `8542980d02b4d2cc5c32ee3542de1760b2562aac`。候选 `source/iokit/Kernel/IOUserClient.cpp:4430-4434` 分派前取得类名并占槽、分派后记录返回值。原有分派及返回值未改。

链接后、prelink 前执行 `llvm-nm -u native.macho` 输出为空；native 与 prelink 包括 weak 的 undefined 均为零。`logs/link.log` 尾部只有 unused `-mllvm` 及两个目录不存在的警告，无链接错误。两个 Mach-O 的三个 `enuma-bb` 格式串各一份；`llvm-objdump` 中 `_is_io_service_open_extended` 分别恰有一处调用 `_enuma_bb_record` 和 `_enuma_bb_record_done`。

| 项目 | r28 大小 / SHA-256 | r29 大小 / SHA-256 | 字节差 |
|---|---|---|---:|
| `kern_exec.o` | 498776 `8cbef9e8eb7f9c4cf9d559f3df1a07bb3fc9536086330a8e0b83196f54e373b8` | 504312 `826f9594590d64dafb478a2319deabec2fa085af3431a9e7b0ad2153e67f0d20` | +5536 |
| `IOUserClient.cpo` | 701704 `da268498fdd2d14b9b105525bcbf07de09be436a94288d11c32fecb780fbdf7a` | 702344 `ab54ffc5c236967d5b103e3f4345904c6dca8772b5cb8ffeab11310ee6596de0` | +640 |
| `native.macho` | 91890176 `81b5d8e9040b1af18def7e700b494d1f2ad12a36b582c39ae56a05322395d2b6` | 91890816 `197429cc5d50c9bd5df0cbc34e780f23d96982fd8085994c3e6a650437ff9135` | +640 |
| `prelink.macho` | 124735488 `e2df38bc6c7ce3ad838ea51fd63ea661399ae0e41dbfbfafc05370f936420a18` | 124735488 `0117c78c89decb9d4fde795431db5d59cb0d6fadcc0ce72f5fed18223667eba5` | 0 |
| `payload.img` | 167772160 `e5064107d4d129acde86a63e1ce98403eae827462af2415a0bef46e4b744fb05` | 167772160 `e678c4d48e11b98a867711dee52820d1b40f87949798371abfa4820b74a91f4e` | 0 |
| `boot.img` | 169951232 `44694629826b0b7e7a8dc5332b8891a013fed892a468f7c46e78012796f8ca0d` | 169951232 `2a74b3e1c76df21b7da561b4cf6d8a45b2b5311819f37ad7ea3ce4443dab920b` | 0 |

两份 filelist 均为 1006 项，仅以上两项路径与内容不同，其他 1004 项为相同路径且逐项哈希检查一致；显示归档直接复用 r28 的 `45ae470d98ee459c45b68b2e99904c490a9ecc37fdf34f9a481b86caf36c1478`。构建前后 r28 全 50 文件哈希不变。候选目录为重放会产生一个未链接的重编显示归档；实际链接输入为 r28 原归档。继承的 `candidate-manifest.json` 的 `unchanged_filelist_entries=1005` 和 `reused_link_inputs` 是相对 r23 的旧 recipe 描述，**不是 r29 相对 r28 的证据**，且后者列出被替换的旧 `IOUserClient.cpo`；以本节实际 filelist 比较为准。

ADT 14088 B `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5`；initrd 1142976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`；trustcache 61356 B `7416ca4f8377146626bb284e2133c76bee6cb4e3ee0af5d648b186235a7323a7`；`unixnu.toml` 804 B `272e2ed556a51d5706f60fcc5daa33c045fcd5d99f03d71cd1b88138d101afee`，均与 r28 相同。FAT 成员仅 kernel 变化；payload offset 2179072，boot args 相同。

首次构建因启动命令超时终止，留存 `...-r29-interrupted`；重试首版链接成功但显示归档重编后字节不同，留存 `...-r29-rebuilt-display`；最终改为复用 r28 归档并重建上述候选。记录检查使用 `/home/wh1stl3/.local/bin/python3 -B scripts/porting-record.py check --device ../enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`，15 areas，exit 0；系统 Python 因无 `tomllib` 不可用。
