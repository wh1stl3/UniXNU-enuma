# enuma r30 全局对照（2026-11-23）

`self-checked`，仅主机构建；未上机。r29 仅按 `comm` 统计，零值没有阳性对照，无法区分无命中与观测问题。本候选复用 r29，在 `is_io_service_open_extended` 的 `service->newUserClient` 原有前置 `enuma_bb_record` 调用内增加全局计数，不改变分派及返回值，保留 `enuma-bb:` 原记录。

`all` 覆盖到达该分派点的全部进程；`bb` 为 comm 精确匹配 `backboardd` 的调用数。八槽按 CAS 抢占顺序记录首次出现的不同 comm，不是频率排序；已有槽继续累加，无法入槽的调用累计 overflow。空进程名显示 `-`。名称取自现有 16 字节 comm 表示，长名称会截断；并发顺序不保证真实时间顺序。各字段独立原子操作，dump 不是事务快照；槽名可能先于其计数出现。复用原 30 秒、最多 20 次周期，每次输出最多十行：

```text
enuma-ctl: begin all=<n> bb=<n> overflow=<n>
enuma-ctl: [com] <comm>=<n>
enuma-ctl: end
```

对照是事后在同一 dump 内核对，不依赖跨次重现。请求的判读口径如下：

| 同一次 dump | 请求的判读 |
|---|---|
| comm 表出现 `MobileGestaltHelper` 或 `IOMFB_FDR_Loader` | 说明该钩子能记到已知的 framebuffer 打开事件（这两个名字是 r28 在同分派点观察到的调用者）。 |
| 出现上述任一、但 comm 表里没有 `backboardd`，且 `bb=0` | 在该窗口内 backboardd 未走该路径。 |
| 两者都不出现、`all=0` | 本次未记到任何已知事件，不能据此下结论（观测失败）。 |

实际表只记录调用者而不记录服务类或返回值，因此同名条目只能证明该调用者到达该分派点，不能独立证明它打开 framebuffer；长名称按截断形式核对。`bb=0` 仍受 comm 精确匹配和观测窗口限制；overflow 可隐藏其他名称。

## 构建证据

WSL root：`PATH=/home/wh1stl3/.local/bin:/opt/unixnu-linux/bin:/usr/bin:/bin /home/wh1stl3/.local/bin/python3 -B scripts/build-enuma-r30-control.py --dtb /root/enuma-step10/inputs/enuma.dtb`，exit 0；UniXNU 固定基座 `693f5d9cae8a408dd18b39f3f9fdc4228c934241`，构建后 origin HEAD `8542980d02b4d2cc5c32ee3542de1760b2562aac`。首次候选因接线脚本未插入控制代码而在格式串检查失败，保留为 `...-r30-interrupted`，不用于交付。

`logs/link.log` 末尾为一个 unused 参数及两个搜索目录不存在警告；prelink 前 `llvm-nm -u native.macho` 为空。native/prelink 的三条 `enuma-ctl:` 和三条 `enuma-bb:` 格式串各唯一，均无 undefined（包括 weak）；`_is_io_service_open_extended` 中 `_enuma_bb_record`、`_enuma_bb_record_done` 各一次。控制代码在 record 内，保留原分派调用及返回值。

| 产物 | r29 大小 / SHA-256 | r30 大小 / SHA-256 | 大小差 |
|---|---|---|---:|
| kern_exec.o | 504312 `826f9594590d64dafb478a2319deabec2fa085af3431a9e7b0ad2153e67f0d20` | 512448 `8c92e5d24beb93dd487871b414763be189978ab11e5082f50d4fb3d9cc77cbe9` | +8136 |
| IOUserClient.cpo | 702344 `ab54ffc5c236967d5b103e3f4345904c6dca8772b5cb8ffeab11310ee6596de0` | 702352 `150c50ac86e58303210f2e7e5bf26108afa9f406475085d9e0bc760356cb1b54` | +8 |
| native.macho | 91890816 `197429cc5d50c9bd5df0cbc34e780f23d96982fd8085994c3e6a650437ff9135` | 91891080 `b572b63afa24eab0b9ab82ba14d2bd9910ca9e9e1a1cc82d0109c5ad032ee3fc` | +264 |
| prelink.macho | 124735488 `0117c78c89decb9d4fde795431db5d59cb0d6fadcc0ce72f5fed18223667eba5` | 124735488 `db892d0a6fc832ab4df399926198902d7e924c11adb149c142c4dcf23fa9e292` | 0 |
| payload.img | 167772160 `e678c4d48e11b98a867711dee52820d1b40f87949798371abfa4820b74a91f4e` | 167772160 `5e1a5ec567ea42fdaea3df7229613d6e5bf28fb3a2bc81d4d846f2ec8ef2e63a` | 0 |
| boot.img | 169951232 `2a74b3e1c76df21b7da561b4cf6d8a45b2b5311819f37ad7ea3ce4443dab920b` | 169951232 `ac7ca17e9af1b133633d4c17ccea9e50b9713fadaf9d971adad4788140c63675` | 0 |

两份 filelist 均 1006 项，仅上述两个对象路径不同，其余 1004 项路径相同。ADT 两者均 14088 B `5f3ebeb6b29a9e47c7c314443dc3564db07caf830de5054e9bec0e5773f521d5`；initrd 复用 r29 的 1142976 B `c89592f808326f7c7c831e23238050efd2f92cdb73d24c78e62190053d8e0470`；unixnu.toml 均 804 B `272e2ed556a51d5706f60fcc5daa33c045fcd5d99f03d71cd1b88138d101afee`。构建后 r29 表中产物哈希与 r29 既有文档一致；未在构建前对 r29 全目录做快照，因此不声明全目录构建前后哈希不变。继承的 manifest 对文件列表的旧比较不是本次 delta。

运行时、并发交错、对照事件、设备显示及独立 verifier 均未验证；新原子协议须 deep_reviewer 审查。未操作设备或 claim。
