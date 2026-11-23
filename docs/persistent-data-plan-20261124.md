# enuma 持久 Data store 路线与 nuwa 对照

状态：self-checked，离线分析；本轮无构建、设备操作或写入。引用的设备读数为原记录所述，不是本轮独立复核。这里只推荐一条可行路线；不存在已放行的持久 store 候选。

## A. 最小路线：认证现有 overlay + 消除挂载期重复 GPT 读

1. **保持同一 seed、启用真实 provider。** `package/EnumaRamBlockStore.cpp:5-13` 是全部失败的 RAM-only 强符号 stub，不能靠参数变成持久 provider；核对目标最终链接的六个 `native_ufs_store_*` 实际归属，选择现有本板 warm provider 而非该 stub。r40 审计源 `out/ufs-sm8250-storegeom-20261123-r40-audit-attempt1/source/NativeUfs.cpp:1726-1735,1742-1759` 使用 `sheng-data-persist=2`，`1708-1723` 的 `sheng-log-reserve=1024` 固定 1024 MiB。实际构建定义和链接仍需确认；不能假设切换参数已接线。
2. **加 owner placement 认证，不是把 false 硬改成 true。** 同源 `NativeUfs.cpp:2958-2974` 在已认证 root window UUID 后初始化 `{true,true,false,...}`；只有本板 owner 信任锚验证了包含下述完整写入范围及身份的签名声明，且与本次已验证的 root/GPT 快照、实际 seed 和计算出的窗口逐项一致，才可将 pending `storeBound` 设为 true；认证缺失、变化或失效一律 false。保留 `:1746-1790` 的大小、root 间隔、窗口与 epoch 检查以及 `:1809-1841` 写入和 sync 的再次检查。此处是方案，不是已存在的签名格式或 API；revocation、并发和写入生命周期需 deep_reviewer 审查。
3. **处理共享 host 重读风险。** 目标 RamBlock 的 `attachStore` 必须先查最终源码和符号：nuwa 的参考实现 `nuwa/UniXNU-nuwa/package/nuwa-ramblock/NativeRamBlock.cpp:85-105` 在 Data 挂载前调用 GPT check，再 open；enuma 历史调用路径见 `docs/data-store-2gib-analysis.md:102-128`。r40 审计源 `NativeUfs.cpp:1930-1945` 重读 GPT header 和 entries 并比较 CRC；最终链接和 RamBlock 调用仍需核实。优先方案是在同一启动中 root 验证时取得并固定已认证 GPT/manifest 快照，attach 时复用它、不要额外发 GPT 读；须证明快照与写窗口 epoch/介质身份一致，且无外部写者/重分区能使其过期，否则拒绝开启。**缓存本身不能保证安全，也不是允许跳过 GPT 校验**；若不能证明这些条件，保持 mode 0。参考 `docs/nuwa-persistent-store-20261123.md:20`，超时或 fatal 可令共享 host `poisoned=true, ready=false`，后续 root 读失败；store 读写本身超时也有同类风险，去掉一次 GPT 重读不能解决整个 host 故障隔离问题。不得声称失败后 RAM fallback 就能恢复根卷；需 deep 审核 timeout、DMA ownership 和 root/store 故障语义。
4. **门禁与写盘。** r40 单次打印的 primary GPT 快照为 userdata 闭区间 `[2686976,61880314]`；seed 524169 页，bitmap 16 页，加 header 共 524186 块，reserve 262144 块，因此候选写入包络为 **LUN 0、4 KiB LBA `[61093985,61618171)`，即 61093985–61618170（含）**，共 2147065856 字节。`docs/enuma-r40-device-20261123.md` 记录 root 非重叠算术检查，不是当前备份 GPT、LUN 容量或写许可证明。按该快照包络在 userdata 内，且不碰 root 前缀、其他分区或 GPT；实际首次写前必须在同一可信介质身份上核实容量、主/备 GPT 及 CRC、分区边界、root manifest imageBytes、所有窗口非重叠和签名绑定；若任何值不符则停止，不沿用此区间。store 元数据、bitmap 和数据可能写及整个包络；不能假设尾部为空。禁用额外 log 写入；seed/reserve 改变则重新计算和签名。
5. **初始化与授权。** 首次全新安装按最终 RamBlock 语义决定是否一次性使用 `sheng-data-reset=1` 初始化；它会丢弃旧 overlay，正常重启不得带 reset（参考 `NativeRamBlock.cpp:88-91,113-132`）。确认 Data UUID、seed hash 和逻辑大小与签名声明一致，后续始终复用相同 seed。任何 mode 2 初始化或后续设备写入须用户当轮明确授权 userdata 写入及确切范围；新候选 boot、持久 boot 槽写入也分别按既有规则授权。现有授权不等于本次写入授权。
6. **验收。** 主机上验证最终链接、owner 签名正反例、窗口越界、seed/geometry 不匹配和撤销均 fail-closed，审查通过后才申请实机。实机首次确认正确窗口、Data 真正挂载且 store Fresh/direct；在 Data 创建带随机内容的文件并 sync，正常关机断电后从设备内载荷重启，不带 reset，以同一 seed 验证 store Resumed/direct、同一 Data UUID 和文件内容/哈希一致；再确认 root 仍可读。仅有成功 open、mount、RAM 写或单次启动不算持久成功；完整交互里程碑另需 GUI 可操作。尚未验证。

### 最小 owner 认证定义

由设备 owner 用已有 owner 私钥签署**版本化、域隔离**的 placement 声明，运行时以配置的 owner 公钥/信任锚验证。声明至少明确本设备/安装身份、LUN 和分区身份及边界、root manifest/owner policy 身份及 imageBytes、块大小、store 起始和长度、reserve、seed 身份哈希与逻辑大小（必要时 Data UUID）；核对它们与同一次已验证快照及实际请求完全一致，并验证 root guard、容量、其他分区/窗口不重叠。签名密钥必须是被现有信任链接受的 owner，而非从无认证 GPT、seed hash 或命令行自取授权；具体编码、绑定点与撤销方案尚待设计和 deep 审查。已有 OS/SystemOS 签名本身不授权 store。

## B. nuwa：未做到持久

`docs/nuwa-persistent-store-20261123.md:7-12` 汇总主控转述：实机 `DS=4`、persistent store open 失败，已检查的链接内核中 mode 2 到无条件拒绝 stub；这份转述未附原始反汇编。对于该次已报告的 RAM overlay，它不持久；不能推广到全部 seed 大小：大于 2 GiB 的历史 RamBlock 在未进入 direct 时写返回 not-ready，见 `docs/data-store-2gib-analysis.md:28-65`。没有跨重启保留实测，nuwa **未做到**持久 Data。

历史 r35 参数 `native-ufs-root=1 native-ufs-lun=0 sheng-data-persist=2 sheng-data-reset=1 sheng-log-reserve=1024`；8 GiB 是**逻辑** seed 大小，reserve 1024 MiB，历史离线布局为 userdata `[3110976,61850619)`、store `[59491258,61588475)` 4 KiB LBA，共 2097217 块（参考 `docs/nuwa-persistent-store-20261123.md:12`）。这些不是当前已认证几何，不能用于 enuma；reset 每次使用都会丢弃旧 overlay。

nuwa `worktree-display-dsp/docs/nuwa-systemgroup-fix-result-20261122.md:5-13,15-27` 的新 dbr 仅改 seed 内容，记录同一 kernel hash；754 秒 mobileactivationd 未见此前崩溃，但无跨重启 store 写读验证，文档也明确 persistence unproven。它没有改变 `DS=4`/store 未证持久的结论；不把旧一次 DS 数值断言为新启动重新测得。

## C. 结论

最小路线是本板现有真实 UFS overlay 加 owner 签名 placement/seed 绑定、经审查的安全 GPT 快照复用和一次授权初始化，再做断电重启内容比对；owner placement 是现有 enuma 安全门禁，必须先解决。sirius 的 unverified 开关和 sheng 的几何门控不是 enuma owner 授权的替代。无新设备操作或验收阶段提升。
