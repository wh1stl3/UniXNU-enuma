# Bootprogress r5 boot_b flash — 2026-11-26

- 操作前审查留痕：reviewer `ses_dec5e6b22ffedlH8anudUa8k0G` **PASS WITH CONDITIONS**；本新版未经 `deep_reviewer`。
- 授权范围：确认唯一 enuma、校验槽位、解锁状态、分区容量及指定镜像后，最多一次 `flash boot_b`；仅明确成功后最多一次 `reboot`。无切槽、临时 boot、continue 或重试。
- 初次只读预检：fastboot 两台、唯一 enuma（另一台 nuwa）；current-slot=b、unlocked=yes、boot_b=201326592 B；镜像 169951232 B，SHA-256 `52c7232d4f74c67fc5ac3f102f47589c41482911bab0e6d4b51e871dd44f2e36`。
- 新门禁 `.cache/bootprogress-r5-flash-20261126.claimed`，采用原子创建；不访问旧门禁。
- 刷写前再次确认唯一 enuma、全部设备条件和镜像哈希。新门禁于 2026-11-26 00:58:36.161 +08:00 原子创建，已消耗，禁止访问、删除或重放。
- 00:58:36.161–00:58:40.764 +08:00，执行一次 `fastboot -s SERIAL flash boot_b out/bootprogress-upstream-20261126-r5/boot.img`，exit 0：`Sending 'boot_b' (165968 KB) OKAY [ 4.106s ]`、`Writing 'boot_b' OKAY [ 0.378s ]`，总计 4.569 s。
- 00:58:40.766–00:58:40.797 +08:00，执行一次同设备 `fastboot -s SERIAL reboot`，exit 0，`Rebooting OKAY`。
- 未切槽、临时 boot、continue 或重试；重启后未发送设备命令。未观察启动画面，未进行设备端回读；启动和运行状态未知，阶段不提升。结果为 `self-checked`，未经独立 verifier 复核。
