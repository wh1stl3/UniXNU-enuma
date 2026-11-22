# enuma r40 存储几何实机观察（2026-11-22）

`self-checked`：记录主控提供的操作和屏幕转录；本次未重新访问设备或核读。阶段不提升。

## 操作与审查

- 2026-11-22 22:04:59 +08:00 刷入 `boot_b`：`Sending 'boot_b' OKAY [4.010s]` / `Writing 'boot_b' OKAY [0.379s]`，exit 0；随后 `reboot` exit 0。claim `.cache/enuma-r40-storegeom-20261123.claimed` 已消耗，禁止访问、删除、重放。
- 刷写前完成设备消歧，另一台识别为 nuwa；序列号按项目规则不入库。
- 镜像 `out/ufs-sm8250-storegeom-20261123-r40/boot.img`，169,951,232 B，SHA-256 `f2937ed83a7c66a6481bd8d7f6eb5daa34c77d0d747c481198b4f27717c3bbcf`。
- 主控提供刷写前 `deep_reviewer` **PASS WITH CONDITIONS**：零新增 UFS I/O、字段已赋值、不改 `startRoot` 行为、只读诊断。这是 deep 审查，非「方案 B、未经 deep_reviewer」；本次未独立复核审查。

## 九行结果

```text
enuma-sg: begin
enuma-sg: ud first=2686976 last=61880314
enuma-sg: crc hdr=bc24942b entries=33a4f637
enuma-sg: manifest status=0 magic=474e4853/544f4f52
enuma-sg: seed=524169 reserve=262144 blocks
enuma-sg: win start=61093985 len=524186
enuma-sg: chk in_ud=1 below_first=0 hits_root=0
enuma-sg: no-new-ufs-io
enuma-sg: end
```

## 判读与边界

- **已观察**：既有启动路径读入并解析的主 GPT 快照报告 `userdata` 4 KiB LBA `[2686976, 61880314]`（两端含）；manifest `status=0`、magic `SHNG`/`ROOT`，即现有解析器认可 `SHNGROOT`。两 CRC 为该主 GPT 快照字段，不是本轮备份 GPT 对照。探针只输出已赋值字段，不新增 UFS I/O；不是重新读盘。
- seed 524169 块、reserve 262144 块；候选窗口为 `[61093985, 61618171)`。根据输出端点的算术比较，窗口落在 `userdata` 的 `[2686976, 61880315)` 内；`below_first=0`、`hits_root=0` 表示未越过起点、未命中已记录 manifest 根前缀。历史 Android sysfs 也是 `[2686976, 61880315)`（右端不含），几何一致。
- `in_ud=1` **仅表示相交**，本身不证明完全包含；上述包含性来自端点算术。该输出不证明所有 store 几何检查或根后 1024 块间隙、owner 绑定，不是写入许可。备份 GPT 与 LUN 容量本轮未读；不能据此证明持久写入或持久 Data。
- 同轮主控另报告 Data `disk1s1`、UUID `62F1BC9E-…` 有 `mount-complete`；swap 仍有 `Failed to open swap file 30` → `vm_swap_create_file failed`。本记录未独立核读或验证后续 I/O。

阶段不提升。探针字段和公式见 [r40 主机记录](enuma-r40-storegeom-host-20261123.md)。
