# enuma root-match UUID 对齐 — 2026-11-18

主机侧记录与实现；未构建、未打包、未上机。状态：新断言 `self-checked`（只跑了
`py_compile` 与合成 board 的正/负/跳过三例），实机与真实构建均未验证。

## 0. 结论

`/chosen/root-matching` 的值必须等于**本次构建里承载根的那个 media 的 UUID**，不是"某个固定对的
UUID"。enuma 有两条根路径，各有自己的值：

| 根路径 | 触发条件（`board.toml`） | root-match 应取 | media 的实际 UUID 来源 |
| --- | --- | --- | --- |
| restore ramdisk（内存根） | 默认 recipe：`rd=md0-ramblock`、`[payload.adt] packed_data_ramdisk = true`、无 `native-ufs-root=1` | `9071148B-B025-402D-AD7A-48464D8B5FFF`（`board.toml:104`） | restore ramdisk 的 APFS 卷 UUID |
| native UFS 的 OS window | `kernel_args` 含 `native-ufs-root=1` | OS 窗口签名 UUID = 官方 profile `[root] os_volume_uuid`（`04769D26-…`） | OS VROOT01 policy 里的 `volume_uuid` |

因此**不把 tracked `board.toml` 改成 047**：tracked 默认 recipe 的根是 restore ramdisk，改 047 会让
当前唯一在实机上走到 launchd 的内存根等不到 media。替代做法是把"按路径取值"这件事在打包/审计处
断言（§4），并让 `board.toml` 只留指针、不再复制一份 047（避免两处真源）。

也不采用 nuwa 的"打包脚本注入 root-matching"：enuma 的 ADT 由官方
`unixnu.payload.build` → `devicetree.generate` 生成，设备仓没有 ADT 打包器；要注入就得另造一个
ADT 后处理器并自己维护 encode/decode 与 digest 链，与"官方优先"冲突（对照见 §5）。

## 1. 两个 UUID 的来历

### 1.1 `root_match_volume_uuid` → `/chosen/root-matching`

1. `board.toml:86` `[payload.adt]`，值在 `board.toml:104`。
2. `UniXNU/scripts/unixnu/payload.py:155` 取 `adt = spec.get('adt', {})`；官方 format 2 走
   `:191-196`，把整个 `ctx.board` 交给 `devicetree.generate(...)`。
3. `UniXNU/scripts/unixnu/devicetree.py:300-301`（`options = payload.get('adt', {})`）→
   `:324-327`：`str(uuid.UUID(...)).upper()` 后拼成
   `<dict><key>IOProviderClass</key><string>IOMedia</string><key>IOPropertyMatch</key>
   <dict><key>UUID</key><string>…</string></dict></dict>` 写进 `/chosen/root-matching`。
   这是**逐字复制**：该选项唯一决定 ADT 里的等待值。
4. 运行时：XNU 的 `IOFindBSDRoot` 用这个 dict 匹配 IOMedia；屏上 `Waiting on <dict …>` 就是它
   （`docs/ufs-sm8250-startroot-mode0-observation.md:73`、`docs/enuma-gop-r5-device-observation.md:70`）。
5. 另有 format 1 的历史路径 `payload.py:198-202`（把 `root_match_volume_uuid` 交给设备仓 tool），
   对应 `scripts/make_enuma_adt.py:88,102` → 外部 `umi_adt.build_tree(..., root_match_volume_uuid=…)`。
   enuma 已是 format 2，官方流程不经过这条；`make_enuma_adt.py` 只是离线/历史工具，**不是当前 ADT 的
   生成器**。

### 1.2 OS window 的签名 UUID

1. 官方 profile `UniXNU/profiles/os/ipados-17.7.11-21H461/profile.toml:110-112`：
   `[root] os_volume_uuid`，注释写明 "The OS disk image: the APFS volume UUID the root policy signs."
2. 与真实 APFS 卷一致（macOS 侧取证）：`data-seed-ci-20261113/scripts/data-seed/build.py:296-300`
   挂载 OS 盘后要求 `info['VolumeUUID'].upper() == '04769D26-…'`，否则 `OS volume UUID differs`。
3. 签名：`scripts/enuma-owner-policy.py:51` 收 `--uuid` → `:94-96` 写进 VROOT01 头 offset 40..56；
   产物 `out/owner-sign-20261113/os/manifest.bin`，报告 `out/verify-fresh-20261113/os/result.json:18,27`
   （`policy_path` / `volume_uuid`）。
4. 进内核：`scripts/build-enuma-production-final-link.py` 归档并 `-force_load` 该 provider；
   `scripts/audit-enuma-production-final-link.py` 的 `audit_image()`（`:77` 起）从最终 MachO 的
   `_verified_root_policies` 重新取 `blob[40:56]`（`:108`）并要求等于报告 UUID（`:111`）。
5. 运行时：`NativeUfsBlock::signedVolumeUuid()`（`.cache/ufs-observation-output-20261112/source/NativeUfs.cpp:1877-1897`，
   读 `vr_open` 验证后的 `verified.volume_uuid`）→ `startRoot` 的 `validate()` 把每个窗口的 UUID 存进
   `gPendingUuid`（同文件 `:2436-2448`）→ 发布顺序 OS 最后（`:2016-2018`）→ `wait()` 轮询
   `mediaWithUuidExists(uuid)`（`:2102-2118`）。`authenticatesVolume()`（`:1843-1864`）另做一次
   字符串比对。
6. 结论：**根 media 的 UUID 就是签名 manifest 里的 `volume_uuid`**。ADT root-match 与它不一致时，
   即使 manifest 闸和窗口发布全部成功，`IOFindBSDRoot` 也等不到东西。

## 2. 两个 UUID 的出现位置

`9071148B-B025-402D-AD7A-48464D8B5FFF`（restore ramdisk APFS 卷 UUID）

| 位置 | 角色 |
| --- | --- |
| `board.toml:104` | tracked 默认 recipe 的 root-match 取值 |
| `scripts/check-enuma-pid1-package.py:15,50` | 22r 打包检查里硬编码，断言 ADT `root_matching` 等于它 |
| `docs/ramblock-host-build.md:64-66` | 来历：fuxi-oddlylabs 记录 + 字节序列出现在 raw APFS 镜像；无 APFS 遍历 |
| `docs/pmgr-23r-package.md:119`、`docs/runtime-summary-gate.md:218`、`docs/ufs-reserved-memory-audit.md:81` | 历史包/ADT 记录 |
| `docs/ufs-sm8250-startroot-mode0-observation.md:73,124,159` | 2026-11-18 mode 0 末屏 rootwait |
| `porting.toml:17`（findings）、`porting.toml:250`（22r evidence） | 设备记录 |
| `out/ufs-sm8250-startroot-mode0-20261118-r1/boot.img` | 冻结包 ADT 里的实际值（屏上可见） |

`04769D26-2CA0-4825-B443-E2E5F88300F2`（OS window 签名 UUID）

| 位置 | 角色 |
| --- | --- |
| `UniXNU/profiles/os/ipados-17.7.11-21H461/profile.toml:110-112` | 真源（官方只读 profile） |
| `out/verify-fresh-20261113/os/result.json:18,27` | 实际签名 policy 与其 UUID（`vr_open` 全块验证退出 0） |
| `scripts/build-enuma-owner-data.py:175,181` | 从 profile 读、并断言等于上面报告 |
| `scripts/enuma-production-recipe.py:17,104,167` | 固定离线快照的 `OS_UUID` 常量与两处检查 |
| `scripts/tests/test_enuma_owner_policy.py:37,76` | 签名器测试 |
| `data-seed-ci-20261113/scripts/data-seed/build.py:299` | macOS 挂载 OS 盘后核对 APFS `VolumeUUID` |
| `out/enuma-gop-production-20261114-r5/device/board.toml:70` | 冻结生产包（`native-ufs-root=1`）用的 root-match |
| `docs/enuma-gop-r5-device-observation.md:70,84` | 该包的实机 rootwait |
| `docs/ufs-sm8250-startroot-mode0-observation.md:161` | 纠正记录：OS window UUID |

`8846FE78-2910-4297-AF97-D59BB6F8FC16` 是同一链条上的 SystemOS 窗口 UUID
（`out/verify-fresh-20261113/systemos/result.json:27`），不是根，不参与 root-match。

## 3. 判定

- tracked 默认 recipe（`rd=md0-ramblock`、`packed_data_ramdisk = true`、无 `native-ufs-root=1`）：
  **907 正确**，且是唯一有实机证据的取值（阶段 6 内存根到 launchd，`board.toml:94-102` 注释与
  `docs/ramblock-host-build.md` 记录）。
- owner/Data 生产构建与任何 `native-ufs-root=1` 构建：**必须 047**（= 签名 OS 窗口 UUID）。
- 反例（本轮要拦的形状）：`out/ufs-sm8250-startroot-mode0-20261118-r1` 同时带 `rd=md0-ramblock` 与
  `native-ufs-root=1` 且无 initrd（`docs/ufs-sm8250-startroot-mode0-observation.md:33-35`）——能成为根的
  只有 UFS OS window，ADT 却声明 907，于是屏上 `Waiting on … 907…`；即使 manifest 闸通过，也不会匹配。
- 未判定项：907 与 restore ramdisk APFS 卷的对应只有"字节序列出现 + 阶段 6 实机"两条证据，没有 APFS
  遍历；enuma 本地 userdata 镜像里的 OS window 字节也没有做过 APFS 级重读（只有 CI 侧对 OS 盘的挂载
  断言）。这两点不影响上面的规则，但都属于取证强度而非"已证明"。

## 4. 打包期断言

不新增配置、不复制 UUID。两个既有脚本各加一处，条件是"该构建是否真以 native UFS 为根"。

**A. `scripts/build-enuma-owner-data.py`**（owner/Data 生产构建，写出构建副本后立刻检查）

- `:211-213`：`root_match_volume_uuid` 的替换改成 `re.subn` 并 `require(replaces == 1)`（原来是
  `re.sub`，替换不生效也不报错）。
- `:222-227`：读回刚写出的 `out/<build>/device/board.toml`，要求
  `native-ufs-root=1` 在 `kernel_args` 里，且 `payload.adt.root_match_volume_uuid == root_uuid`。
  `root_uuid` 来自 profile `[root] os_volume_uuid`，并在 `:179-181` 已被要求等于
  `out/verify-fresh-20261113/os/result.json` 的 `volume_uuid`，即**实际签名 policy 的 UUID**。

**B. `scripts/audit-enuma-production-final-link.py`**（最终链接审计，`check_root_match()` `:30-52`，
在 `:171` 调用，结果写进 `audit.json` 的 `root_match` 键）

- 取生效 board：优先 `<build>/device/board.toml`，否则 tracked `board.toml`；
- 仅当该 board 的 `kernel_args` 含 `native-ufs-root=1` 时才比对，要求声明值与
  `reports[0]['volume_uuid']`（OS 窗口）逐字符相等；不等则构建失败并打印两个值与 board 路径；
- 该 `volume_uuid` 又被 `audit_image()` 用最终 MachO 字节复核（`:108-111`），所以比对对象是**镜像里
  实际签名 manifest 的 UUID**，不是脚本常量，也不是 profile 抄本；
- restore 路径（无 `native-ufs-root=1`）不比对，故默认 recipe 不会误报。

**当前比较对象与升级点**：现在比的是"ADT 声明值 = 最终镜像里的 OS VROOT01 policy UUID"。
若将来引入多 generation 或多 OS 窗口（不同 size 的候选 policy 并存，`configureVerification()` 按
`imageBytes` 选 policy，`NativeUfs.cpp:1784-1810`），`reports[0]` 要改成按窗口 size/offset 选报告，
否则可能拿错窗口的 UUID。

**残留覆盖缺口（重要）**：enuma 的候选打包（如 `out/enuma-gop-production-20261114-r5/package.py:96-125`）
直接调官方 `unixnu.payload.build`，不经过 A 或 B。若某候选既不跑 owner-data 构建也不跑 B 的审计，
断言不会触发——mode0 r1 就是这种情形。因此 B 应作为每个候选的必跑步骤（含 ADT 提取后的复核）。

**自检**（本轮实际执行的只有这些）：

```sh
cd /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma
/home/wh1stl3/.local/bin/python3.11 -m py_compile scripts/build-enuma-owner-data.py scripts/audit-enuma-production-final-link.py
```

合成 board 的四例（临时目录，未触及仓库）：`907` + `native-ufs-root=1` → 拒绝；`047` +
`native-ufs-root=1` → 通过；restore 路径（无 `native-ufs-root=1`）→ 跳过；native 路径缺该字段 → 拒绝。
另验证：对真实 `board.toml` 去掉注释行后 `re.subn` 命中恰好 1 次。

## 5. 参考 nuwa 最终方案（哪些照搬、哪些不能）

nuwa（`D:/Code/PortingiOS/nuwa/UniXNU-nuwa`）2026-11-15 到 launchd 的做法：

| 事项 | nuwa | enuma | 采用 |
| --- | --- | --- | --- |
| 注入点 | 设备仓自有 packer：`scripts/build-ufs-apfs-root-chmh.py:42-45` 定义 `UUID`/`MATCH`，`:49-54` 的 `derived()` 在官方 ADT 后追加 `/chosen/root-matching`，`:63` 断言回读等于 `MATCH` | 无自有 ADT packer；官方 `devicetree.py:324-327` 从 `board.toml` 生成 | **不照搬注入**，沿用官方生成器；"注入点"就是 `board.toml` |
| `board.toml` 是否留空 | 留空：`board.toml:170-174` 注释掉 `root_match_volume_uuid`，`:76` `os_volume_uuid = ""`（stage 1–5 不需要 root-matching） | 默认 recipe 需要它（restore ramdisk 是当前唯一实机可用的根） | **不照搬留空**，改按路径取值 + 断言 |
| 一致性手段 | 同一 UUID 常量分别硬编码在签名脚本与打包脚本，打包期断言 ADT 值等于该常量；无"ADT 值 vs 签名 manifest 内 UUID"的自动交叉断言（`docs/` 未记录） | 断言对象是最终镜像里的签名 policy UUID | **照搬断言位置思路，加强比对对象**（不吃常量这份第二真源） |
| 运行时比对 | 官方 caller 比真实 C verifier 的 `vr_view.volume_uuid`，`vr_open` 不接收外部期望值（`docs/root-external-policies-20261113.md:102-104`） | 同一机制：`NativeUfsBlock::authenticatesVolume`（`NativeUfs.cpp:1843-1864`）、`signedVolumeUuid`（`:1877-1897`） | 机制相同，无需改动 |
| 身份取证 | OS `DADD93F8-…`（APSB role 1，非容器 `0E25F331-…`）、SystemOS `96096B28-…`（role 0），来自 APSB/checkpoint 级检查（`docs/root-signing-20261113.md:6-8`、`docs/root-external-policies-20261113.md:34-36`） | OS `04769D26-…`、SystemOS `8846FE78-…` 来自 profile + 签名报告，APFS 侧只有 CI `hdiutil attach` 断言（`data-seed-ci-20261113/scripts/data-seed/build.py:296-300`） | 真源相同，**取证强度不同**（enuma 无 APSB/role 级证据） |
| 布局差异 | OS window 5635081728 B、SystemOS 2743074816 B 且 SystemOS 是裸 APFS container（`docs/root-external-policies-20261113.md:13-17`） | OS @1 MiB / 6077580800 B，SystemOS @6079643648 / 3303014400 B（`scripts/enuma-production-recipe.py:20-21`） | 断言按 `reports[0]` 取 OS，不写死 offset/size，故不受布局差异影响 |

冲突点：nuwa 的 "打包脚本注入 + board.toml 留空" 依赖设备仓自己的 packer（它还顺带维护 CHMH
digest 链）。enuma 的候选打包只有官方 payload API，强行照搬会引入第二套 ADT 生成路径，且要同步
digest/encode 语义——收益（同样的一致性）已经在 §4 的断言里拿到，因此不做。

## 6. 未启用 / 未验证

- A、B 两处断言**没有在真实构建里执行过**（本轮不构建、不打包）；只有 `py_compile` 与合成 board 的
  三/四例逻辑自检。
- 没有读取任何 ADT 字节来核对：断言的是"声明值 = 签名 UUID"，其"= ADT 里的值"这一步建立在
  `devicetree.py:324-327` 逐字复制的静态阅读上（未执行 payload 构建）。若要字节级闭环，可复用
  `scripts/check-enuma-pid1-package.py:26-51` 的 `/chosen/root-matching` 解析方式，但那份是 22r 专用
  硬编码，本轮未改造成通用检查。
- §3 两个"未判定项"（907 无 APFS 遍历、enuma 本地 OS window 无 APFS 级重读）未解除。
- `out/` 冻结包未改动：mode0 r1 的 ADT 仍是 907、r5 仍是 047；两者都不受影响，历史记录保持原状。
- `porting.toml` findings 已在同一提交补齐（`configuration` / `firmware` / `storage` / `diagnostics` 各一条，
  写清规则、两处断言的位置与比较对象、以及 mode 0 r1 会被 B 拒绝这一事实）。
- 默认 NoAccessPolicy / NoContract、bring-up 阶段、任何实机结论均不变。

## 7. 复跑

```sh
# 语法与逻辑（无需 root、无构建）
cd /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma
/home/wh1stl3/.local/bin/python3.11 -m py_compile scripts/build-enuma-owner-data.py scripts/audit-enuma-production-final-link.py

# 真实构建后（需要既有 r4/verify-fresh 输入，成本高；由 verifier 决定是否跑）
python3 scripts/build-enuma-production-final-link.py --output out/<new-dir>
python3 scripts/audit-enuma-production-final-link.py --build-json out/<new-dir>/result.json --output out/<new-dir>/audit.json
# 期望：audit.json 的 root_match.asserted 为 true，且 declared == signed_os_volume_uuid
```
