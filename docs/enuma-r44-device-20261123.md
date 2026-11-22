# enuma r44 单次设备观察

状态：`self-checked`；主控转录，无 `vision` 独立核读。阶段不提升。

## 操作与审查

2026-11-22 23:18:51 +08:00（锚点 23:18:47）刷入 `boot_b`，前置消歧为现场唯一 fastboot 设备且产品为 `enuma`、槽位 `b`。镜像 `out/ufs-sm8250-matchcnt2fx-20261123-r44/boot.img`，169,951,232 B，SHA-256 `b997b33af1d85f67da89cf5b3817f53ef5545a41605b856882288bb322601b4e`。

`Sending 'boot_b' (165968 KB) OKAY [4.036s]`，`Writing 'boot_b' OKAY [0.415s]`，exit 0；随后 `reboot` exit 0。claim `.cache/enuma-r44-matchcnt2fx-20261123.claimed` 于 23:18:08 创建，已消耗，禁止访问、删除、重放。

主控报告写前 `reviewer` **PASS WITH CONDITIONS**：置位在页写成功后、不改修补决策；AW 为 bit 0；输出不超过 8 行；`parsed!=4` 时输出 `bits=n/a`。

## 实机输出

```text
enuma-ipc: begin send=15405 recv=11071
enuma-ipc: bb send=25 recv=25
enuma-ipc: sb send=101 recv=71
enuma-ipc: end
enuma-exec: pid=34 comm=backboardd        （在该行之前，未在此片段内）
enuma-mt: t=119 all=00/1f/2b/0/16
enuma-mt: other=c/4/4/0/1
enuma-mt: bb(34)=0/0/0/0/0
enuma-mt: sb(5)=0/0/0/0/0
enuma-fx: parsed=4 applied=1
enuma-fx: bits=0x08
```

## 判读与边界

五项顺序 `M/N/O/P/I`，`all` 为全局累计。全局 `N=0x1f`（31）、`O=0x2b`（43）、`I=0x16`（22）非零，阳性对照成立，钩子有效。backboardd(34) 与 SpringBoard(5) 五项全零，支持截至 `t=119`（backboardd exec 后至少 30 内核秒）未进入这五类受测入口，偏向 B（未走到 IOKit）；但不证明未进入整个 IOKit，interest notification 之外的匹配方式、其他进程代查等间接路径未覆盖。

`parsed=4` 表示四条 ADT 条目全部解析；`applied=1` 与 `bits=0x08` 表示只有第 4 条 `BTAudioHALPlugin+0x38bec` 成功，前三条未命中：bit 0 为 AW `dyld_shared_cache_arm64.15+0x421e8bc`，bit 1/2 为 `dyld_shared_cache_arm64.13` 两处。强证据表明本次 text-fixup 对三条 dyld 共享缓存条目无效，唯一命中普通文件；**AW 死锁修复在本次采样前从未生效**。`bits` 仅证明页内替换完成，不等于改后指令被执行；`applied` 与 `bits` 不是同一瞬间快照，采样后行为未知。

离线独立核对见 [text-fixup 记录](text-fixup-20261123.md)：本地 SystemOS 镜像中的缓存 basename 为 `dyld_shared_cache_arm64.15`，偏移 `0x421e8bc` 的原字节 `28ad1bb0008544f9` 与 ADT 条目完全吻合，因此该离线文件的原字节不构成不匹配；设备实际运行文件未回读，不能排除运行时不同文件的字节不匹配。

下一步查共享缓存条目未命中的原因：文件查找、映射时机、签名页校验、路径及 cryptex 位置等；现有证据不能确定原因，也不能证明 enuma 存在 AW 死锁。新设备操作须另获授权。
