# 2026-11-23 磁盘清理核查（self-checked）

状态：self-checked，未运行独立 verifier；无删除、无复制、无设备操作。递归扫描超过 300 秒被停止，签名材料及逐项占用未完成，不能据此签发安全删除白名单。

## 清单与存在性

清单声明批 1 为 186 目录、79.334694 GiB；批 2 为 2 文件、14.398469 GiB；批 3 为 71 目录、4.270204 GiB；合计 98.003367 GiB 均为历史文件长度，不是当前实际占用或可释放量。逐项按清单原文路径检查：批 1 186/186 存在、批 2 2/2 存在、批 3 71/71 存在。第 273 行末尾 U+F00D 是目录名组成部分，按原文存在，不作规范化。

Step 0A 要求备份 trustcache、module、密钥及证书扩展名和不大于 1 MiB 的 BEGIN 文件（排除 libspdm/unit_test/sample_key/），逐个 SHA-256 校验；0B 备份顶层 Markdown，超过 200 MB 时可仅保留列名命中指定关键词的文件并记录。两项目标目录均不存在，未执行备份；失败目录不得整删。批 2 只指两个文件，不删父目录或相邻 DMG；清单的排除项、暂缓项与 worktree 不纳入。

## 目录引用（保守子串匹配）

以下列出 README.md、porting.toml 及 docs 全部可读取 UTF-8 文件中出现目录名的文件和行；匹配为子串，因此名字是其他目录名前缀时可能误报，须逐行复核。将全部命中暂列不可清，且不代表其他目录可安全删除。

| 目录 | 命中位置 |
|---|---|
| `ufs-sm8250-rx-20261123-r51` | `docs/enuma-r51-rx-host-20261123.md:8` |
| `ufs-sm8250-lite4-20261123-r50` | `docs/enuma-r50-lite4-host-20261123.md:31` |
| `ufs-sm8250-bp2-20261123-r49` | `docs/enuma-r49-bp2-host-20261123.md:6` |
| `ufs-sm8250-fxdiag-20261123-r47` | `docs/enuma-r47-fxdiag-host-20261123.md:9` |
| `ufs-sm8250-bp-20261123-r46` | `docs/enuma-r46-bp-host-20261123.md:59` |
| `ufs-sm8250-ps-20261123-r45` | `docs/enuma-r45-ps-host-20261123.md:3`, `docs/enuma-r45-ps-host-20261123.md:87`, `docs/offline-codesign-and-plists-20261123.md:28` |
| `ufs-sm8250-matchcnt2fx-20261123-r44` | `docs/enuma-r44-device-20261123.md:7`, `docs/enuma-r44-matchcnt2fx-host-20261123.md:3`, `docs/sharedcache-fixup-gap-20261123.md:7` |
| `ufs-sm8250-matchcnt2-20261123-r43` | `docs/enuma-r43-matchcnt2-host-20261123.md:3` |
| `ufs-sm8250-matchcnt-20261123-r42` | `docs/enuma-r42-matchcnt-host-20261123.md:3`, `docs/enuma-r42-matchcnt-host-20261123.md:79` |
| `ufs-sm8250-storegeom-20261123-r40` | `docs/enuma-r40-device-20261123.md:9`, `docs/enuma-r40-storegeom-host-20261123.md:3`, `docs/hid-stack-backboardd-20261123.md:8`, `docs/hid-stack-backboardd-20261123.md:11`, `docs/pipa-reference-20261123.md:57`, `docs/pipa-reference-20261123.md:154`, `docs/pipa-reference-20261123.md:162`, `docs/repo-diff-adt-bootargs-20261123.md:7`, `docs/sheng-donor-branches-20261123.md:119` |
| `ufs-sm8250-launchd-aksid-20261123-r39` | `docs/apple-arm-io-device-20261123.md:16`, `docs/enuma-r39-aksid-host-20261123.md:26` |
| `ufs-sm8250-launchd-match-20261123-r36` | `docs/enuma-r36-match-host-20261123.md:53` |
| `ufs-sm8250-launchd-match-20261123-r36-compile-failed` | `docs/enuma-r36-match-host-20261123.md:53` |
| `ufs-sm8250-launchd-scale-20261123-r35` | `docs/enuma-r35-scale-host-20261123.md:26`, `docs/enuma-r35-scale-host-20261123.md:43` |
| `ufs-sm8250-launchd-ipc-20261123-r34` | `docs/display-config-diff-20261123.md:9`, `docs/display-config-diff-20261123.md:41`, `docs/pipa-reference-20261123.md:162` |
| `ufs-sm8250-launchd-attempt-20261123-r32` | `docs/hid-stack-backboardd-20261123.md:29` |
| `ufs-sm8250-launchd-attempt-20261123-r32-intermediate` | `docs/hid-stack-backboardd-20261123.md:29` |
| `ufs-sm8250-launchd-control-20261123-r30` | `docs/enuma-r30-device-20261123.md:8` |
| `ufs-sm8250-launchd-bbscan-20261123-r29` | `docs/enuma-r29-bbscan-host-20261123.md:27`, `docs/enuma-r29-device-20261123.md:7`, `docs/SESSION-HANDOFF-20261123.md:5` |
| `ufs-sm8250-launchd-fbcount-20261123-r28` | `docs/enuma-r28-device-20261123.md:8`, `docs/enuma-r28-fbchain-host-20261123.md:3`, `docs/SESSION-HANDOFF-20261123.md:17` |
| `ufs-sm8250-launchd-fbcount-20261123-r27` | `docs/enuma-r27-fbcount-host-20261123.md:3`, `docs/enuma-r27-fbcount-host-20261123.md:31` |
| `ufs-sm8250-launchd-fbcount-20261122-r26` | `docs/enuma-r26-device-20261123.md:8`, `docs/enuma-r26-fbcount-host-20261122.md:3`, `docs/SESSION-HANDOFF-20261123.md:16` |
| `ufs-sm8250-launchd-census-20261122-r25` | `docs/enuma-r25-census-host-20261122.md:3` |
| `ufs-sm8250-launchd-hid-20261122-r24` | `docs/enuma-r24-census-20261122.md:8`, `docs/enuma-r24-nodisplay-host-20261122.md:55`, `docs/enuma-r24-nodisplay-host-20261122.md:79`, `docs/SESSION-HANDOFF-20261123.md:15` |
| `r23-upstream` | `porting.toml:228`, `docs/enuma-r23-hid-standin-host-20261122.md:80` |
| `ufs-sm8250-launchd-hid-20261122-r23` | `docs/enuma-r23-hid-device-20261122.md:8`, `docs/enuma-r23-hid-standin-host-20261122.md:34`, `docs/enuma-r23-hid-standin-host-20261122.md:81`, `docs/hid-standin-equivalence-20261123.md:8`, `docs/SESSION-HANDOFF-20261123.md:14` |
| `ufs-sm8250-launchd-keystore-20261122-r22` | `docs/enuma-r22-device-20261122.md:8`, `docs/enuma-r22-memory-window-host-20261122.md:3`, `docs/enuma-r22-memory-window-host-20261122.md:87` |
| `ufs-sm8250-launchd-keystore-20261122-r21` | `docs/enuma-r21-exec-exit-pair-host-20261122.md:4` |
| `ufs-sm8250-launchd-keystore-20261122-r20` | `docs/enuma-r20-amfi-host-20261122.md:5`, `docs/enuma-r20-amfi-host-20261122.md:81` |
| `ufs-sm8250-launchd-keystore-20261122-r19` | `docs/enuma-r19-watchdog-lite-host-20261122.md:3`, `docs/enuma-r20-amfi-host-20261122.md:81` |
| `ufs-sm8250-launchd-keystore-20261122-r17` | `docs/enuma-lite-watchdog-args-check-20261122.md:36`, `docs/enuma-lite-watchdog-args-check-20261122.md:61`, `docs/enuma-r17-exit-probe-host-20261122.md:3`, `docs/enuma-trustcache-coverage-20261122.md:7` |
| `ufs-sm8250-launchd-keystore-20261122-r16` | `docs/enuma-r16-cpu-calibration-host-20261122.md:3` |
| `ufs-sm8250-launchd-keystore-20261122-r15` | `docs/enuma-r15-device-20261122.md:8`, `docs/enuma-r15-shared-region-probe-host-20261122.md:29` |
| `ufs-sm8250-launchd-keystore-20261122-r14` | `docs/enuma-cache-pagesize-20261122.md:17`, `docs/enuma-r14-device-20261122.md:8`, `docs/official-4k-patch-audit-20261122.md:17` |
| `ufs-sm8250-launchd-keystore-20261122-r13` | `docs/enuma-4k-cache-split-check-20261122.md:7`, `docs/enuma-cryptex-view-check-20261122.md:9`, `docs/enuma-r13-console-throughput-host-20261122.md:4`, `docs/enuma-r13-device-20261122.md:8` |
| `ufs-sm8250-launchd-keystore-20261121-r11` | `docs/enuma-r11-keystore-host-20261121.md:4`, `docs/pipa-cs-dyld-diff-20261123.md:23`, `docs/repo-diff-patches-20261123.md:179` |
| `ufs-sm8250-launchd-display-20261121-r10` | `docs/enuma-cryptex-view-check-20261122.md:19` |
| `ufs-sm8250-launchd-display-20261121-r9` | `docs/enuma-r9-device-20261121.md:8` |
| `ufs-sm8250-launchd-display-20261120-r8` | `porting.toml:354`, `docs/enuma-r8-device-20261121.md:8`, `docs/enuma-timebase-r8-20261120.md:94` |
| `ufs-sm8250-launchd-display-20261119-r6` | `docs/ufs-launchd-display-r6-build.md:4` |
| `enuma-gop-production-20261114-r5` | `README.md:61`, `README.md:65`, `porting.toml:209`, `docs/enuma-4k-cache-plan-20261122.md:16`, `docs/enuma-gop-r5-device-observation.md:24`, `docs/enuma-gop-r5-device-observation.md:38`, `docs/enuma-gop-r5-device-observation.md:39`, `docs/enuma-gop-r5-device-observation.md:80`, `docs/enuma-gop-r5-device-observation.md:83`, `docs/enuma-gop-r5-device-observation.md:205`, `docs/enuma-r26-fbcount-host-20261122.md:25`, `docs/fb-wc-cached-check-20261122.md:7`, `docs/persistent-boot-slot-plan.md:15`, `docs/persistent-boot-slot-plan.md:31`, `docs/persistent-boot-slot-plan.md:200`, `docs/persistent-boot-slot-plan.md:359`, `docs/persistent-boot-slot-plan.md:393`, `docs/persistent-boot-slot-plan.md:394`, `docs/pipa-reference-20261123.md:163`, `docs/root-uuid-alignment.md:91`, `docs/root-uuid-alignment.md:156`, `docs/SESSION-HANDOFF-20261114.md:25`, `docs/SESSION-HANDOFF-20261117.md:15`, `docs/unit-scale-investigation-20261123.md:24` |
| `enuma-gop-r5-preseal-manifest-20261116` | `README.md:65`, `porting.toml:209`, `docs/SESSION-HANDOFF-20261117.md:15` |
| `production-final-link-20261113-r4` | `porting.toml:158` |
| `production-final-link-guard-20261113-r4` | `README.md:89`, `porting.toml:344`, `docs/root-uuid-alignment.md:127` |
| `verify-guard-r4-independent-20261113` | `README.md:89`, `porting.toml:157` |
| `owner-data-query-20261113-r3` | `README.md:65`, `porting.toml:154`, `porting.toml:209`, `docs/data-store-2gib-analysis.md:5`, `docs/data-store-2gib-analysis.md:16`, `docs/data-store-2gib-analysis.md:267`, `docs/data-store-2gib-analysis.md:312`, `docs/enuma-lite-watchdog-args-check-20261122.md:27`, `docs/SESSION-HANDOFF-20261117.md:15` |
| `production-recipe-r3` | `README.md:97`, `porting.toml:412`, `porting.toml:416` |
| `ufs-sm8250-launchd-cache-20261119-r3` | `porting.toml:193`, `docs/enuma-fastboot-entry-and-pmgr-write.md:73`, `docs/launchd-vmm-present-20261119-observation.md:6`, `docs/launchd-vmm-present-20261119-observation.md:32`, `docs/launchd-vmm-present-20261119-observation.md:63`, `docs/launchd-vmm-present-20261119-observation.md:72` |
| `ufs-sm8250-policy-20261118-r3` | `README.md:45`, `porting.toml:317`, `docs/payload-shrink-plan.md:225` |
| `ufs-upstream-provider-nonexec-20261114-r3` | `README.md:69`, `porting.toml:143` |
| `verify-r3-20261113` | `README.md:97`, `porting.toml:416` |
| `enuma-gop-legacy-20261114-r2` | `docs/apple-arm-io-device-20261123.md:50`, `docs/enuma-gop-r5-device-observation.md:75`, `docs/pipa-reference-20261123.md:44`, `docs/pipa-reference-20261123.md:115`, `docs/pipa-reference-20261123.md:164`, `docs/porting-provenance-20261123.md:34`, `docs/repo-diff-implementation-20261123.md:4`, `docs/repo-diff-implementation-20261123.md:135`, `docs/sirius-display-chain-port-eval-20261123.md:7`, `docs/unit-scale-investigation-20261123.md:24` |
| `smmu-4k-live-pool-hard-r2-20261114` | `porting.toml:110` |
| `smmu-route-contexts-candidate-20261114-r2` | `porting.toml:141` |
| `smmu-three-id-candidate-guard-r2-20261113` | `README.md:85`, `porting.toml:152` |
| `smmu-three-id-independent-r2-20261113` | `README.md:83`, `porting.toml:151` |
| `ufs-native-warm-capacity-20261114-r2` | `README.md:63`, `porting.toml:191`, `docs/SESSION-HANDOFF-20261114.md:14`, `docs/ufs-warm-capacity-r2-diagnostic.md:22`, `docs/ufs-warm-capacity-r2-diagnostic.md:40`, `docs/ufs-warm-capacity-r2-diagnostic.md:41`, `docs/ufs-warm-capacity-r2-diagnostic.md:166` |
| `ufs-sm8250-policy-20261117-r2` | `README.md:47`, `porting.toml:192`, `docs/SESSION-HANDOFF-20261117.md:25`, `docs/ufs-sm8250-policy-r2-device-observation.md:22`, `docs/ufs-sm8250-policy-r2-device-observation.md:45`, `docs/ufs-sm8250-policy-r2-device-observation.md:87`, `docs/ufs-sm8250-policy-r2-device-observation.md:237` |
| `ufs-sm8250-startroot-mode0-20261118-r2` | `README.md:41`, `porting.toml:122`, `porting.toml:193`, `docs/root-uuid-alignment.md:195`, `docs/root-uuid-alignment.md:217`, `docs/SESSION-HANDOFF-20261119.md:17`, `docs/ufs-root-mount-20261118-observation.md:7`, `docs/ufs-root-mount-20261118-observation.md:28`, `docs/ufs-root-mount-20261118-observation.md:116`, `docs/ufs-root-mount-20261118-observation.md:354` |
| `gop-cpu-consumer-20261114-r1` | `docs/repo-diff-implementation-20261123.md:64` |
| `production-complete-20261114-r1` | `docs/data-store-2gib-analysis.md:5`, `docs/data-store-2gib-analysis.md:18`, `docs/data-store-2gib-analysis.md:182`, `docs/data-store-2gib-analysis.md:227`, `docs/data-store-2gib-analysis.md:228`, `docs/SESSION-HANDOFF-20261114.md:21` |
| `smmu-route-contexts-20261114-r1` | `porting.toml:142` |
| `smmu-route-contexts-rebuild-runner-20261114-r1` | `porting.toml:140` |
| `ufs-allocation-facts-20261114-r1` | `porting.toml:107`, `porting.toml:122`, `porting.toml:126` |
| `ufs-allocation-full-nonexec-20261114-r1` | `porting.toml:106` |
| `ufs-iommu-identity-20261114-r1` | `porting.toml:109` |
| `ufs-iommu-live-20261114-r1` | `porting.toml:108` |
| `ufs-native-warm-adopt-host-20261113-r1` | `README.md:75`, `porting.toml:146` |
| `ufs-native-warm-target-wiring-20261113-r1` | `README.md:73`, `porting.toml:145` |
| `ufs-prepublish-rollback-20261114-r1` | `porting.toml:105` |
| `ufs-sm8250-launchd-data-20261119-r1` | `README.md:33`, `porting.toml:138`, `porting.toml:194`, `porting.toml:354`, `docs/data-seed-20261119-generation.md:84`, `docs/r4-screen-timestamps-offline-20261120.md:7`, `docs/SESSION-HANDOFF-20261120.md:14`, `docs/ufs-launchd-data-20261119-observation.md:6`, `docs/ufs-launchd-data-20261119-observation.md:26`, `docs/ufs-launchd-data-20261119-observation.md:45` |
| `ufs-sm8250-launchd-display-20261119-r1` | `README.md:35`, `docs/SESSION-HANDOFF-20261120.md:17`, `docs/SESSION-HANDOFF-20261120.md:61` |
| `ufs-sm8250-policy-20261116-r1` | `docs/data-store-2gib-analysis.md:5`, `docs/data-store-2gib-analysis.md:268`, `docs/data-store-2gib-analysis.md:335`, `docs/payload-shrink-plan.md:5`, `docs/payload-shrink-plan.md:11`, `docs/payload-shrink-plan.md:96`, `docs/payload-shrink-plan.md:158`, `docs/payload-shrink-plan.md:159`, `docs/payload-shrink-plan.md:167`, `docs/payload-shrink-plan.md:189`, `docs/SESSION-HANDOFF-20261117.md:17`, `docs/store-geometry-feasibility-20261123.md:7`, `docs/swap-and-persistent-data-20261123.md:27`, `docs/ufs-reserved-memory-audit.md:5`, `docs/ufs-reserved-memory-audit.md:58`, `docs/ufs-reserved-memory-audit.md:59`, `docs/ufs-reserved-memory-audit.md:351`, `docs/ufs-reserved-memory-audit.md:357`, `docs/ufs-reserved-memory-audit.md:394`, `docs/ufs-reserved-memory-audit.md:437` |
| `ufs-sm8250-startroot-mode0-20261118-r1` | `README.md:43`, `porting.toml:122`, `porting.toml:192`, `porting.toml:344`, `docs/enuma-r40-storegeom-host-20261123.md:16`, `docs/root-uuid-alignment.md:79`, `docs/root-uuid-alignment.md:104`, `docs/SESSION-HANDOFF-20261118.md:14`, `docs/ufs-sm8250-startroot-mode0-observation.md:5`, `docs/ufs-sm8250-startroot-mode0-observation.md:22`, `docs/ufs-sm8250-startroot-mode0-observation.md:46`, `docs/ufs-sm8250-startroot-mode0-observation.md:212` |
| `smmu-visible-routes-tail-candidate-20261113` | `README.md:77` |
| `smmu-visible-routes-candidate-20261113` | `README.md:79`, `README.md:81`, `porting.toml:150` |
| `smmu-visible-routes-paged-candidate-20261113` | `README.md:79`, `porting.toml:148` |
| `owner-data-config-20261113-final` | `porting.toml:155` |
| `production-final-link-guard-20261113` | `README.md:89`, `porting.toml:344`, `docs/root-uuid-alignment.md:127` |
| `provider-rebuild-20261113` | `README.md:95`, `porting.toml:159` |
| `ufs-upstream-provider-nonexec-20261114` | `README.md:69`, `README.md:71`, `porting.toml:143`, `porting.toml:144` |
| `smmu-visible-routes-paged-20261113` | `README.md:79`, `porting.toml:148` |
| `smmu-4k-table-pool-hard-20261114` | `porting.toml:111` |
| `smmu-visible-routes-tail-20261113` | `README.md:77`, `porting.toml:147` |
| `owner-data-query-20261113` | `README.md:65`, `porting.toml:154`, `porting.toml:209`, `docs/data-store-2gib-analysis.md:5`, `docs/data-store-2gib-analysis.md:16`, `docs/data-store-2gib-analysis.md:267`, `docs/data-store-2gib-analysis.md:312`, `docs/enuma-lite-watchdog-args-check-20261122.md:27`, `docs/SESSION-HANDOFF-20261117.md:15` |
| `production-recipe` | `README.md:97`, `porting.toml:405`, `porting.toml:408`, `porting.toml:412`, `porting.toml:416`, `docs/enuma-cryptex-view-check-20261122.md:24`, `docs/root-uuid-alignment.md:88`, `docs/root-uuid-alignment.md:184`, `docs/SESSION-HANDOFF-20261118.md:21`, `docs/ufs-root-mount-20261118-observation.md:214`, `docs/ufs-sm8250-startroot-mode0-observation.md:162` |
| `fdr-loader-investigation-20261123` | `docs/missing-bootargs-and-fdrloader-20261123.md:15`, `docs/missing-bootargs-and-fdrloader-20261123.md:17` |
| `bb-offline-20261123` | `docs/backboardd-offline-20261123.md:10`, `docs/backboardd-offline-20261123.md:11`, `docs/backboardd-offline-20261123.md:12`, `docs/backboardd-offline-20261123.md:14`, `docs/backboardd-offline-20261123.md:16`, `docs/backboardd-offline-20261123.md:18`, `docs/backboardd-offline-20261123.md:128`, `docs/backboardd-offline-20261123.md:129`, `docs/backboardd-offline-20261123.md:131`, `docs/backboardd-offline-20261123.md:132`, `docs/backboardd-offline-20261123.md:152`, `docs/backboardd-offline-20261123.md:216`, `docs/bb-entry-disassembly-20261123.md:3`, `docs/bb-entry-disassembly-20261123.md:10`, `docs/bb-entry-disassembly-20261123.md:11`, `docs/bb-entry-disassembly-20261123.md:12`, `docs/bb-entry-disassembly-20261123.md:13`, `docs/bb-entry-disassembly-20261123.md:14` |
| `owner-data-config-20261113` | `porting.toml:155` |
| `verified-root-provider-test3-20261113` | `porting.toml:160` |
| `verify-fresh-20261113` | `README.md:95`, `porting.toml:17`, `porting.toml:122`, `porting.toml:159`, `docs/root-uuid-alignment.md:54`, `docs/root-uuid-alignment.md:86`, `docs/root-uuid-alignment.md:96`, `docs/root-uuid-alignment.md:122`, `docs/root-uuid-alignment.md:145`, `docs/root-uuid-alignment.md:148`, `docs/ufs-root-mount-20261118-observation.md:214` |
| `verify-data-seed-receipt-20261113` | `README.md:91`, `porting.toml:156`, `docs/data-store-2gib-analysis.md:229` |
| `ufs-early-takeover-boundary-20261114` | `README.md:71`, `porting.toml:144` |
| `boot-entry-contract-20261114` | `README.md:71` |

## 其他判断

- `enuma-gop-production-20261114-r5` 和 `enuma-gop-r5-preseal-manifest-20261116` 有封存记录：`docs/SESSION-HANDOFF-20261117.md:15`；清除会丢失包或原始 manifest 证据，不可仅凭可重建代替。
- `.o`、Mach-O、prelink、boot.img 在固定源码、工具链、输入和构建选项齐全时可重建；位级复现未证。示例 `out/enuma-gop-production-20261114-r5/build.py`；该封存路线记录依赖 WSL root 和宿主代理，不需要设备。其他轮次不得假设相同命令或输入仍存在。
- `UniXNU/scripts/porting-record.py:118-125` 检查 evidence 的 `reference` 文件存在，`:137-140` 对 Markdown 变更不要求 area 归属；删除仅出现在自由文本的 out 引用可能不导致该检查失败，但仍会破坏记录指针。未逐条证明所列 out 路径是否是结构化 reference，不能推断删后必然成功。
- 基线记录检查使用 WSL `/home/wh1stl3/.local/bin/python3 scripts/porting-record.py check --device /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma --base origin/feat/step10-ramblock-probe`，exit 0；未模拟删除。
- 原清单配套 `disk-cleanup-final.ps1` 的批 1 由当前目录动态枚举，且具有删除分支，不可作为本次受限白名单脚本直接运行。

## 未完成

实际占用、内容级签名扫描、顶层 Markdown 全量保护覆盖核验、精确引用复核、逐目录分类、可执行复制命令及删除脚本均未完成。禁止执行删除；需完成扫描并对签名材料和审计文档备份逐个核验后重新评估。


## WizTree 快照精算与受限脚本（2026-11-23）

CSV `WizTree_20261123205743.csv`，946632 行，快照时间 20:57:45；以路径末尾分隔符区分目录行，逐文件的 `大小` 累加，不用目录聚合行。Windows 路径忽略大小写、统一分隔符，目录按分隔符边界匹配；CSV 是快照，不代表当前文件或实际分配空间。总计 **105230314325 B / 98.003367 GiB**，与旧值一致。3 项无文件行，不能仅据此断定目录不存在；此前逐项存在性检查结果见上。

分类优先级 C > A > B > D；C 包括文件自身受保护情形及 CSV 中含指定镜像的目录；A 按 failed/incomplete/interrupted/attempt/selfcheck 名称，B 限定 `ufs-sm8250-*-r数字` 精确轮次，其余 D。分类只依名字与 CSV 路径，不证明可安全删除。

| 类别 | 项数 | GiB |
|---|---:|---:|
| A | 77 | 6.162616 |
| B | 50 | 50.812737 |
| C | 4 | 15.381465 |
| D | 128 | 25.646550 |

结构化 `area[].evidence[].reference` 以 `out/` 开头且落入清单项的条目 **0**；`UniXNU/scripts/porting-record.py:118-125` 对每个非 HTTPS reference 要求真实文件，缺失即失败；本清单中因此会失效的结构化条目为 0，故无需为该检查改条目。自由文本中存在 out 路径（按边界匹配命中 43 项），删除仍使文本指针失效，本结论不代表文本引用安全。

脚本 `scripts/prepare-cleanup-enuma-out.ps1` 仅 A 类 77 目录，快照 6.162616 GiB；未将 B 判作纯构建产物（仅凭名称无法证明），排除全部 C 与 porting.toml 文本命中。默认 dry-run；`--apply` 时每项目录需用户交互确认 Step 0 已完成、验哈希及链接已检查。**只能由用户手动执行；agent 不执行删除。** 快照后目录内容或引用可能变化；执行前须重新核对。脚本文件名使用现有 `scripts/prepare-*` 路径归属，避免改写并发工作的 porting.toml。

### 大小前 30（GiB，文件长度）

| 路径（相对 out） | 类 | GiB |
|---|---|---:|
| `userdata-prepare-20261112-b\run-1\userdata\userdata-root.img` | C | 8.738281 |
| `userdata-clean-20261112\OS.raw` | C | 5.660188 |
| `ufs-sm8250-launchd-display-20261121-r9` | B | 2.877095 |
| `ufs-sm8250-launchd-display-20261121-r10` | B | 2.670901 |
| `ufs-sm8250-launchd-keystore-20261121-r11` | B | 2.160754 |
| `ufs-sm8250-launchd-display-20261120-r7` | B | 2.143664 |
| `ufs-allocation-full-nonexec-20261114-r1` | D | 1.990049 |
| `ufs-allocation-full-independent-build-20261114-r1` | D | 1.865767 |
| `ufs-prepublish-rollback-20261114-r1` | D | 1.664005 |
| `ufs-sm8250-launchd-display-20261120-r8` | B | 1.552936 |
| `ufs-sm8250-policy-20261117-r2` | B | 1.523449 |
| `ufs-sm8250-policy-20261116-r1` | B | 1.522475 |
| `ufs-sm8250-startroot-mode0-20261118-r1` | B | 1.499132 |
| `ufs-sm8250-launchd-keystore-20261122-r13` | B | 1.468347 |
| `ufs-sm8250-launchd-keystore-20261122-r19` | B | 1.467403 |
| `ufs-sm8250-launchd-keystore-20261122-r20` | B | 1.467385 |
| `ufs-sm8250-launchd-keystore-20261122-r16` | B | 1.466549 |
| `ufs-sm8250-launchd-keystore-20261122-r21` | B | 1.462523 |
| `ufs-sm8250-launchd-keystore-20261122-r17` | B | 1.461531 |
| `ufs-sm8250-launchd-keystore-20261122-r14` | B | 1.460615 |
| `ufs-sm8250-launchd-data-20261119-r1` | B | 1.459852 |
| `ufs-sm8250-launchd-keystore-20261122-r15` | B | 1.455661 |
| `ufs-sm8250-launchd-cache-20261119-r1` | B | 1.365737 |
| `ufs-sm8250-launchd-display-20261119-r6` | B | 1.233766 |
| `ufs-sm8250-launchd-display-20261119-r1` | B | 1.227922 |
| `ufs-sm8250-launchd-cache-20261119-r2` | B | 1.221872 |
| `smmu-route-contexts-candidate-20261114-r2` | D | 1.110151 |
| `ufs-sm8250-launchd-cache-20261119-r3` | B | 1.105821 |
| `ufs-full-fv-nonexec-20261114-r3` | D | 1.026518 |
| `ufs-sm8250-startroot-mode0-20261118-r2` | B | 1.020677 |

### 全清单逐项结果（字节）

| 路径（相对 out） | 类 | 字节 |
|---|---|---:|
| `ufs-sm8250-fbfill2-20261123-r53` | B | 580648433 |
| `ufs-sm8250-fbfill2-20261123-r53-selfcheck` | A | 580657322 |
| `ufs-sm8250-fbfill-20261123-r52` | B | 580644597 |
| `ufs-sm8250-fbfill-20261123-r52-failed1` | A | 879155 |
| `ufs-sm8250-fbfill-20261123-r52-failed2` | A | 1882681 |
| `ufs-sm8250-fbfill-20261123-r52-failed3` | A | 242470388 |
| `ufs-sm8250-rx-20261123-r51` | B | 580356222 |
| `ufs-sm8250-lite4-20261123-r50` | B | 578717886 |
| `ufs-sm8250-bp2-20261123-r49` | B | 579889239 |
| `ufs-sm8250-fxdiagbp-20261123-r48` | B | 554418847 |
| `ufs-sm8250-fxdiag-20261123-r47` | B | 586559444 |
| `ufs-sm8250-fxdiag-20261123-r47-incomplete1` | A | 551816 |
| `ufs-sm8250-fxdiag-20261123-r47-incomplete2` | A | 1267456 |
| `ufs-sm8250-bp-20261123-r46` | B | 585822874 |
| `ufs-sm8250-bp-20261123-r46-initial` | D | 585822866 |
| `ufs-sm8250-ps-20261123-r45` | B | 585802792 |
| `ufs-sm8250-ps-20261123-r45-audit-attempt1` | A | 245244272 |
| `ufs-sm8250-matchcnt2fx-20261123-r44` | B | 585955610 |
| `ufs-sm8250-matchcnt2-20261123-r43` | B | 586319860 |
| `ufs-sm8250-matchcnt-20261123-r42` | B | 586667686 |
| `ufs-sm8250-matchcnt-20261123-r42-audit-attempt1` | A | 245515413 |
| `ufs-sm8250-storegeom-20261123-r40` | B | 579918503 |
| `ufs-sm8250-storegeom-20261123-r40-audit-attempt1` | A | 242114905 |
| `ufs-sm8250-launchd-aksid-20261123-r39` | B | 578689861 |
| `ufs-sm8250-launchd-aksid-20261123-r39-compile-failed` | A | 136795 |
| `ufs-sm8250-launchd-aksid-20261123-r39-selfcheck2` | A | 578689951 |
| `ufs-sm8250-launchd-match-20261123-r36` | B | 585855920 |
| `ufs-sm8250-launchd-match-20261123-r36-compile-failed` | A | 2227880 |
| `ufs-sm8250-launchd-scale-20261123-r35` | B | 338011479 |
| `ufs-sm8250-launchd-scale-20261123-r35-incomplete` | A | 337746782 |
| `ufs-sm8250-launchd-ipc-20261123-r34` | B | 585840759 |
| `ufs-sm8250-launchd-ipc-20261123-r34-failed-compile` | A | 1682800 |
| `ufs-sm8250-launchd-ipc-20261123-r34-failed-compile2` | A | 1677022 |
| `ufs-sm8250-launchd-ipc-20261123-r34-failed-json` | A | 1352462 |
| `ufs-sm8250-launchd-attempt-20261123-r32` | A | 585421185 |
| `ufs-sm8250-launchd-attempt-20261123-r32-intermediate` | A | 585412630 |
| `ufs-sm8250-launchd-control-20261123-r30` | B | 585405854 |
| `ufs-sm8250-launchd-control-20261123-r30-interrupted` | A | 247344394 |
| `ufs-sm8250-launchd-bbscan-20261123-r29` | B | 585391005 |
| `ufs-sm8250-launchd-bbscan-20261123-r29-interrupted` | A | 2592107 |
| `ufs-sm8250-launchd-bbscan-20261123-r29-rebuilt-display` | D | 585391002 |
| `ufs-sm8250-launchd-fbcount-20261123-r28` | B | 584075393 |
| `ufs-sm8250-launchd-fbcount-20261123-r28-before-open-table` | D | 584066046 |
| `ufs-sm8250-launchd-fbcount-20261123-r28-format-check-failed` | A | 246027710 |
| `ufs-sm8250-launchd-fbcount-20261123-r27` | B | 581004686 |
| `ufs-sm8250-launchd-fbcount-20261123-r27-audit-map-failed` | A | 242956922 |
| `ufs-sm8250-launchd-fbcount-20261123-r27-audit-stab-failed` | A | 242629267 |
| `ufs-sm8250-launchd-fbcount-20261123-r27-dtb-cr-argv-failed` | A | 410752557 |
| `ufs-sm8250-launchd-fbcount-20261123-r27-patch-context-failed` | A | 504043 |
| `ufs-sm8250-launchd-fbcount-20261123-r27-patch-context2-failed` | A | 504043 |
| `ufs-sm8250-launchd-fbcount-20261122-r26` | B | 581847138 |
| `ufs-sm8250-launchd-fbcount-20261122-r26-ar-check-failed` | A | 2439789 |
| `ufs-sm8250-launchd-fbcount-20261122-r26-ar-padding-failed` | A | 2439789 |
| `ufs-sm8250-launchd-fbcount-20261122-r26-compile-cwd-failed` | A | 1258816 |
| `ufs-sm8250-launchd-fbcount-20261122-r26-late-link-failed` | A | 3475067 |
| `ufs-sm8250-launchd-fbcount-20261122-r26-patch-dry-run-failed` | A | 413034 |
| `r25-failed-patch-context` | A | 446387 |
| `r25-failed-patch-offset` | A | 446338 |
| `r25-failed-private-callout` | A | 750863 |
| `ufs-sm8250-launchd-census-20261122-r25` | B | 580104426 |
| `ufs-sm8250-launchd-hid-20261122-r24` | B | 554360297 |
| `r23-failed-audit1` | A | 248188003 |
| `r23-failed-compile1` | A | 105462 |
| `r23-upstream` | D | 1208279 |
| `ufs-sm8250-launchd-hid-20261122-r23` | B | 586068446 |
| `ufs-sm8250-launchd-keystore-20261122-r22` | B | 338015010 |
| `ufs-sm8250-launchd-keystore-20261122-r22-memory-only` | D | 338014918 |
| `ufs-sm8250-launchd-keystore-20261122-r21` | B | 1570372646 |
| `ufs-sm8250-launchd-keystore-20261122-r20` | B | 1575592653 |
| `ufs-sm8250-launchd-keystore-20261122-r19` | B | 1575612504 |
| `ufs-sm8250-launchd-keystore-20261122-r19-incomplete-headers` | A | 501923 |
| `ufs-sm8250-launchd-keystore-20261122-r17` | B | 1569306951 |
| `ufs-sm8250-launchd-keystore-20261122-r17-incomplete-sidecar` | A | 469773082 |
| `ufs-sm8250-launchd-keystore-20261122-r16` | B | 1574695161 |
| `ufs-sm8250-launchd-keystore-20261122-r16-incomplete-audit` | A | 251742564 |
| `ufs-sm8250-launchd-keystore-20261122-r15` | B | 1563004431 |
| `ufs-sm8250-launchd-keystore-20261122-r15-incomplete-width` | A | 246077858 |
| `ufs-sm8250-launchd-keystore-20261122-r14` | B | 1568323343 |
| `ufs-sm8250-launchd-keystore-20261122-r14-incomplete-prev` | A | 6092830 |
| `ufs-sm8250-launchd-keystore-20261122-r13` | B | 1576625404 |
| `ufs-sm8250-launchd-keystore-20261122-r13-audit-first` | D | 252303961 |
| `ufs-sm8250-launchd-keystore-20261122-r13-failed-first` | A | 501554 |
| `ufs-sm8250-launchd-keystore-20261121-r11` | B | 2320091474 |
| `ufs-sm8250-launchd-display-20261121-r10` | B | 2867858443 |
| `ufs-sm8250-launchd-display-20261121-r9` | B | 3089257695 |
| `ufs-sm8250-launchd-display-20261120-r8` | B | 1667452576 |
| `ufs-sm8250-launchd-display-20261120-r7` | B | 2301741908 |
| `ufs-sm8250-launchd-display-20261119-r6` | B | 1324746491 |
| `enuma-gop-production-20261114-r5` | C | 1055007182 |
| `enuma-gop-r5-preseal-manifest-20261116` | C | 475971 |
| `ufs-upstream-provider-nonexec-20261114-r5` | D | 19479476 |
| `enuma-gop-production-20261114-r4` | D | 322004532 |
| `production-final-link-20261113-r4` | D | 75785120 |
| `production-final-link-guard-20261113-r4` | D | 318519040 |
| `ufs-upstream-provider-nonexec-20261114-r4` | D | 27762578 |
| `verify-guard-r4-independent-20261113` | D | 318512090 |
| `verify-r4-independent-20261114b` | D | 8773032 |
| `enuma-gop-production-20261114-r3` | D | 77676176 |
| `owner-data-query-20261113-r3` | D | 478234435 |
| `production-final-link-20261113-r3` | D | 254772 |
| `production-final-link-guard-20261113-r3` | D | 318488509 |
| `production-recipe-r3` | D | 1922550 |
| `smmu-prepare-final-r3-20261114` | D | 10116 |
| `smmu-prepare-final-r3-check-20261114` | D | 15625998 |
| `smmu-prepare-final-r3-independent-20261114` | D | 15626772 |
| `smmu-prepare-r3-oracle-probe-20261114` | D | 349001 |
| `ufs-full-fv-nonexec-20261114-r3` | D | 1102214960 |
| `ufs-full-fv-nonexec-20261114-r3-verifier` | D | 1021092495 |
| `ufs-sm8250-launchd-cache-20261119-r3` | B | 1187366414 |
| `ufs-sm8250-policy-20261118-r3` | B | 970759816 |
| `ufs-upstream-provider-nonexec-20261114-r3` | D | 31506808 |
| `verify-r3-20261113` | D | 1922092 |
| `enuma-gop-legacy-20261114-r2` | D | 14974030 |
| `enuma-gop-production-20261114-r2` | D | 322063745 |
| `owner-data-config-20261113-r2` | D | 150756649 |
| `owner-data-query-20261113-r2` | D | 237793131 |
| `production-final-link-20261113-r2` | D | 1724 |
| `production-final-link-guard-20261113-r2` | D | 318502591 |
| `production-recipe-r2` | D | 1921620 |
| `smmu-4k-live-pool-hard-r2-20261114` | D | 2809232 |
| `smmu-4k-live-pool-hard-r2-verifier-20261114` | D | 2383824 |
| `smmu-prepare-final-r2-20261114` | D | 8283 |
| `smmu-prepare-final-r2-check-20261114` | D | 15270471 |
| `smmu-prepare-final-r2-independent-verify-20261114` | D | 1038428 |
| `smmu-prepare-final-r2-independent-verify2-20261114` | D | 14924160 |
| `smmu-route-contexts-candidate-20261114-r2` | D | 1192015407 |
| `smmu-route-contexts-candidate-20261114-r2-verifier-20261114` | D | 136069176 |
| `smmu-route-contexts-candidate-20261114-r2-verifier-20261114-protocol` | D | 1231 |
| `smmu-route-contexts-candidate-r2-readonly-selfcheck-20261114` | A | 136069320 |
| `smmu-route-contexts-r2-independent-rebuild-20261114a` | D | 1047443900 |
| `smmu-three-id-candidate-guard-r2-20261113` | D | 1047050581 |
| `smmu-three-id-independent-r2-20261113` | D | 1047030961 |
| `ufs-allocation-facts-20261114-r2` | D | 13174 |
| `ufs-allocation-facts-r2-independent-verifier-20261114a` | D | 1441244 |
| `ufs-allocation-facts-r2-selfcheck-20261114` | A | 0 |
| `ufs-allocation-facts-r2-selfcheck02-20261114` | A | 26868 |
| `ufs-allocation-facts-r2-selfcheck03-20261114` | A | 2173 |
| `ufs-allocation-facts-r2-selfcheck04-20261114` | A | 1437471 |
| `ufs-allocation-facts-r2-selfcheck05-20261114` | A | 1437471 |
| `ufs-allocation-facts-r2-selfcheck06-20261114` | A | 2173 |
| `ufs-allocation-facts-r2-selfcheck07-20261114` | A | 1441236 |
| `ufs-full-fv-nonexec-20261114-r2` | D | 999494839 |
| `ufs-iommu-live-20261114-r2` | D | 34097 |
| `ufs-iommu-live-r2-selfcheck-20261114` | A | 5944868 |
| `ufs-iommu-live-r2-selfcheck02-20261114` | A | 5948897 |
| `ufs-iommu-live-r2-selfcheck03-20261114` | A | 5954121 |
| `ufs-iommu-live-r2-verifier-20261114` | D | 5953914 |
| `ufs-issuer-lifecycle-20261114-r2` | D | 7859 |
| `ufs-native-warm-capacity-20261114-r2` | D | 980960106 |
| `ufs-prepublish-rollback-artifact-selfcheck-20261114-r2` | A | 187 |
| `ufs-sm8250-launchd-cache-20261119-r2` | B | 1311975409 |
| `ufs-sm8250-policy-20261117-r2` | B | 1635790934 |
| `ufs-sm8250-startroot-mode0-20261118-r2` | B | 1095943875 |
| `gop-cpu-consumer-20261114-r1` | D | 93978 |
| `production-complete-20261114-r1` | D | 1050097986 |
| `smmu-route-contexts-20261114-r1` | D | 52551788 |
| `smmu-route-contexts-rebuild-runner-20261114-r1` | D | 42041 |
| `smmu-route-contexts-rebuild-stage-selfcheck-20261114-r1` | A | 555722 |
| `smmu-route-contexts-rebuild-stage-selfcheck-20261114-r1-empty` | A | 0 |
| `ufs-allocation-facts-20261114-r1` | D | 1084127 |
| `ufs-allocation-facts-final-selfcheck-20261114-r1` | A | 16223883 |
| `ufs-allocation-facts-independent-20261114-r1` | D | 16200171 |
| `ufs-allocation-full-independent-build-20261114-r1` | D | 2003352321 |
| `ufs-allocation-full-independent-verify-20261114-r1` | D | 0 |
| `ufs-allocation-full-independent-verify-20261114-r1b` | D | 130960732 |
| `ufs-allocation-full-nonexec-20261114-r1` | D | 2136799314 |
| `ufs-controlled-provider-lifecycle-20261113-r1` | D | 552112 |
| `ufs-full-fv-nonexec-20261114-r1` | D | 808478827 |
| `ufs-iommu-identity-20261114-r1` | D | 566437 |
| `ufs-iommu-identity-postcheck-20261114-r1` | D | 36 |
| `ufs-iommu-identity-selfcheck-20261114-r1` | A | 5047704 |
| `ufs-iommu-live-20261114-r1` | D | 917358 |
| `ufs-iommu-live-final-selfcheck-20261114-r1` | A | 17278850 |
| `ufs-iommu-live-postcheck-20261114-r1` | D | 4427 |
| `ufs-iommu-live-verify-20261114-r1` | D | 17322240 |
| `ufs-issuer-lifecycle-20261114-r1` | D | 7227 |
| `ufs-native-warm-adopt-host-20261113-r1` | D | 35044330 |
| `ufs-native-warm-capacity-20261114-r1` | D | 977833404 |
| `ufs-native-warm-target-wiring-20261113-r1` | D | 28316539 |
| `ufs-prepublish-rollback-20261114-r1` | D | 1786711552 |
| `ufs-prepublish-rollback-artifact-selfcheck-20261114-r1` | A | 187 |
| `ufs-sm8250-launchd-cache-20261119-r1` | B | 1466449050 |
| `ufs-sm8250-launchd-data-20261119-r1` | B | 1567504085 |
| `ufs-sm8250-launchd-display-20261119-r1` | B | 1318471323 |
| `ufs-sm8250-policy-20261116-r1` | B | 1634745337 |
| `ufs-sm8250-startroot-mode0-20261118-r1` | B | 1609680220 |
| `userdata-clean-20261112\OS.raw` | C | 6077580800 |
| `userdata-prepare-20261112-b\run-1\userdata\userdata-root.img` | C | 9382658048 |
| `smmu-visible-routes-tail-candidate-20261113` | D | 1047747044 |
| `smmu-visible-routes-candidate-20261113` | D | 1047648029 |
| `smmu-visible-routes-paged-candidate-20261113` | D | 1047630412 |
| `verify-owner-data-query-20261113-fresh` | D | 478320694 |
| `owner-data-config-20261113-final` | D | 238006223 |
| `production-final-link-guard-20261113` | D | 176907406 |
| `provider-rebuild-20261113` | D | 147148763 |
| `smmu-three-id-candidate-guard-20261113` | D | 75855186 |
| `smmu-visible-routes-20261113` | D | 57205642 |
| `ufs-upstream-provider-nonexec-20261114` | D | 29212129 |
| `ufs-iommu-live-selfcheck10-20261114` | A | 16442115 |
| `ufs-allocation-facts-selfcheck-20261114-07` | A | 15920593 |
| `ufs-allocation-facts-selfcheck-20261114-05` | A | 15853182 |
| `smmu-prepare-final-check-20261114` | D | 15268819 |
| `smmu-visible-routes-paged-20261113` | D | 14402721 |
| `ufs-iommu-live-selfcheck08-20261114` | A | 14107682 |
| `ufs-iommu-live-selfcheck07-20261114` | A | 11717561 |
| `verify-prepublish-independent-20261114` | D | 10490469 |
| `smmu-prepare-range-verify5-20261114` | D | 10029075 |
| `ufs-iommu-live-selfcheck05-20261114` | A | 8493842 |
| `smmu-4k-table-pool-hard-20261114` | D | 8456897 |
| `smmu-visible-routes-tail-20261113` | D | 7550715 |
| `smmu-visible-routes-tail-independent-increment-20261113` | D | 7072049 |
| `ufs-allocation-facts-selfcheck-20261114-04` | A | 6725787 |
| `ufs-allocation-facts-selfcheck-20261114-03` | A | 6203758 |
| `ufs-iommu-live-selfcheck09-20261114` | A | 6117537 |
| `ufs-iommu-live-selfcheck03-20261114` | A | 5973152 |
| `ufs-iommu-live-selfcheck06-20261114` | A | 5939623 |
| `ufs-iommu-live-selfcheck04-20261114` | A | 5922641 |
| `ufs-iommu-live-selfcheck02-20261114` | A | 5826532 |
| `ufs-iommu-live-selfcheck01-20261114` | A | 5823762 |
| `smmu-prepare-range-verify4-20261114` | D | 3896526 |
| `smmu-prepare-range-verify3-20261114` | D | 3896219 |
| `ufs-allocation-facts-selfcheck-20261114-01` | A | 3159608 |
| `smmu-4k-live-pool-hard-20261114` | D | 2784048 |
| `smmu-three-id-candidate-20261113` | D | 2529767 |
| `owner-data-query-20261113` | D | 2370077 |
| `recipe-gen-verify-20261113` | D | 1915793 |
| `production-recipe` | D | 1907746 |
| `smmu-prepare-range-20261114` | D | 1862935 |
| `smmu-4k-table-pool-verifier-20261114a` | D | 1685241 |
| `smmu-4k-bind-debug-20261114` | D | 1627165 |
| `fdr-loader-investigation-20261123` | D | 1456398 |
| `ufs-allocation-facts-selfcheck-20261114-06` | A | 1285126 |
| `ufs-allocation-facts-selfcheck-20261114-02` | A | 1279655 |
| `bb-offline-20261123` | D | 1240967 |
| `verified-root-partial-link-20261113` | D | 403828 |
| `smmu-prepare-oracle-seed1-20261114` | D | 344898 |
| `owner-data-config-20261113` | D | 340521 |
| `userdata-host-20261112` | D | 206790 |
| `verify-owner-query-host-20261113-fresh` | D | 192242 |
| `owner-query-host-check-20261113` | D | 192140 |
| `verified-root-provider-test4-20261113` | D | 96196 |
| `verified-root-provider-test3-20261113` | D | 96103 |
| `verify-fresh-20261113` | D | 53793 |
| `verify-data-seed-receipt-20261113` | D | 41988 |
| `smmu-prepare-range-verify2-20261114` | D | 34563 |
| `ufs-controlled-provider-design-20261113` | D | 32744 |
| `verified-root-provider-test2-20261113` | D | 32711 |
| `userdata-verification-20261112` | D | 17280 |
| `ufs-early-takeover-boundary-20261114` | D | 16947 |
| `smmu-prepare-range-verify-20261114` | D | 16542 |
| `verified-root-provider-test-20261113` | D | 15886 |
| `smmu-4k-bind-20261114` | D | 12580 |
| `boot-entry-contract-20261114` | D | 6929 |
| `smmu-prepare-disasm-20261114` | D | 6355 |
| `smmu-prepare-disasm-check2-20261114` | D | 5288 |
| `smmu-prepare-final-20261114` | D | 4990 |
| `smmu-prepare-disasm-check-20261114` | D | 4652 |
| `verify-data-seed-ci-20261113` | D | 3054 |
| `verify-artifacts-independent-20261114` | D | 187 |


## `.cache` 二级目录分类（CSV 快照，self-checked）

二级目录 95 项、文件长度 4.682329 GiB；顶层文件另 0.000408 GiB，全部 4.682737 GiB。只统计设备仓 `.cache`，不涉及 nuwa。CSV 是快照；引用仅搜索 Git 跟踪的 docs、scripts 和 porting.toml，未证明无其他依赖。

已引用或已知为输入者保留；其余没有验证完整输入与重建命令，标不确定。`.cache` 可清 **0 项 / 0 GiB**，因此脚本不加入猜测性的目录；无前三项。截图帧虽常可由原视频重建，本次未验证原视频与重建参数；引用的 OCR 也保留。

- `firmware`：`scripts/enuma_firmware_preflight.py:15` 为 DTB 输入，`docs/ufs-reserved-memory-audit.md:47-55` 记录厂商镜像和实机 FDT；是否存在可再次取得的完整备份未核实，保留，不断言不可获取。
- `xnu-work`：`scripts/build-enuma-owner-data.py:269`、`scripts/build-enuma-production-final-link.py:84` 将 **构建树** `tree/.cache/xnu-work` 用作输入；不能将该路径误认成设备仓 `.cache/xnu-work`。后者 CSV 未列为二级目录；等价构建源码树不得清。
- `local-dup`：CSV 有 3 个文件；对照 `origin/feat/step10-ramblock-probe` 本地远端跟踪引用 d63e13674b49dd3a7d938fe4c93930387879ca94，两个 Git blob 相同，但 `scripts/build-enuma-r42-matchcnt.py` 本地 `7108ca76a21e5f3490e3001967d7f553e1dd6af6` ≠ 远端 `8301ace2f34c62a9cd6644054a1668cc1c8522a3`；因此并非全部为远端副本，保留。CSV 后变更未核实。

### 二级目录逐项（按大小降序；前 20 即 top 20）

| 目录 | GiB | 判定依据 |
|---|---:|---|
| `.cache/media` | 2.728411 | 需保留：引用 `docs/pmgr-23r-diagnostic.md`, `docs/ramblock-host-build.md`, `docs/runtime-summary-gate.md` |
| `.cache/ufs-boot-analysis-20261111` | 0.537955 | 需保留：引用 `docs/SESSION-HANDOFF-20261123.md`, `docs/ufs-gate-a-offline-20261121.md` |
| `.cache/firmware` | 0.294025 | 需保留：构建输入及设备证据 |
| `.cache/frames-r45-ocr` | 0.256914 | 需保留：引用 `docs/offline-codesign-and-plists-20261123.md` |
| `.cache/frames-r45` | 0.254886 | 不确定：帧名称；原视频与再生参数未核 |
| `.cache/live-capture` | 0.191912 | 需保留：引用 `docs/persistent-boot-slot-plan.md`, `docs/touch-evidence-inventory-20261122.md`, `docs/ufs-hci30-compat.md` |
| `.cache/ufs-observation-stage-20261112` | 0.070377 | 不确定：用途及重建输入未核 |
| `.cache/ufs-reuse-diagnostic-fix2` | 0.066213 | 需保留：引用 `docs/ufs-reuse-diagnostic-implementation.md`, `porting.toml` |
| `.cache/ufs-integration-20261112-proposal` | 0.034477 | 需保留：引用 `porting.toml` |
| `.cache/venv-uefi` | 0.024041 | 不确定：用途及重建输入未核 |
| `.cache/tools` | 0.023818 | 需保留：引用 `scripts/enuma_live_collect.py` |
| `.cache/smmu-three-id-20261113` | 0.022264 | 需保留：引用 `porting.toml` |
| `.cache/ufs-observation-output-20261112` | 0.019792 | 需保留：引用 `docs/root-uuid-alignment.md`, `scripts/build-enuma-production-final-link.py` |
| `.cache/native-read-adapter-20261112` | 0.015029 | 需保留：引用 `porting.toml`, `scripts/build-enuma-production-final-link.py` |
| `.cache/ufs-observation-binding-20261112` | 0.014256 | 不确定：用途及重建输入未核 |
| `.cache/verify-visible-routes-20261113` | 0.012381 | 需保留：引用 `porting.toml` |
| `.cache/extract-root` | 0.010109 | 需保留：引用 `scripts/enuma_vendor_import.py` |
| `.cache/native-read-review-fixes-20261112` | 0.009582 | 需保留：引用 `porting.toml` |
| `.cache/native-read-packets-20261112` | 0.007781 | 不确定：用途及重建输入未核 |
| `.cache/ufs-observation-entry-tests-20261112` | 0.005962 | 不确定：用途及重建输入未核 |
| `.cache/smmu-three-id-verify-root-20261113` | 0.005329 | 不确定：用途及重建输入未核 |
| `.cache/ufs-reuse-replay-24r-20261111` | 0.004949 | 需保留：引用 `docs/ufs-24r-diagnostic.md` |
| `.cache/smmu-three-id-verify-20261113` | 0.004505 | 不确定：用途及重建输入未核 |
| `.cache/ufs-external-equivalence-20261111` | 0.003996 | 不确定：用途及重建输入未核 |
| `.cache/ufs-final-checks-20261111` | 0.003959 | 不确定：用途及重建输入未核 |
| `.cache/pmgr-contract` | 0.003788 | 需保留：引用 `docs/pmgr-23r-package.md`, `docs/pmgr-host-gate.md`, `porting.toml` |
| `.cache/verifier-24r-independent-20261111` | 0.003656 | 不确定：用途及重建输入未核 |
| `.cache/ufs-reuse-diagnostic-fix1` | 0.003319 | 需保留：引用 `docs/ufs-reuse-diagnostic-implementation.md`, `porting.toml` |
| `.cache/ufs-reuse-diagnostic` | 0.003127 | 需保留：引用 `porting.toml` |
| `.cache/ref-binaries` | 0.003098 | 不确定：参考仓身份/修改与可重建性未核 |
| `.cache/smmu-spec-20261113` | 0.002951 | 不确定：用途及重建输入未核 |
| `.cache/ufs-adt-equivalence-24r-20261111` | 0.002770 | 需保留：引用 `docs/ufs-24r-diagnostic.md`, `scripts/audit-enuma-production-final-link.py` |
| `.cache/ref-sirius` | 0.002733 | 需保留：引用 `docs/repo-diff-implementation-20261123.md`, `docs/sirius-display-chain-port-eval-20261123.md` |
| `.cache/vision-video-20261113` | 0.002653 | 不确定：用途及重建输入未核 |
| `.cache/native-read-entry-slice-final3-20261112` | 0.002085 | 不确定：用途及重建输入未核 |
| `.cache/native-read-entry-slice-final-20261112` | 0.002079 | 不确定：用途及重建输入未核 |
| `.cache/native-read-entry-slice-20261112` | 0.002071 | 不确定：用途及重建输入未核 |
| `.cache/ufs-version-integration-20261112` | 0.001960 | 不确定：用途及重建输入未核 |
| `.cache/device-evidence` | 0.001934 | 需保留：引用 `docs/touch-evidence-inventory-20261122.md`, `docs/ufs-gate-a-offline-20261121.md`, `docs/ufs-hci30-compat.md` |
| `.cache/ref-orangepi5` | 0.001929 | 需保留：引用 `docs/repo-diff-implementation-20261123.md` |
| `.cache/ufs-boot-offline-20261111` | 0.001687 | 需保留：引用 `docs/ufs-gate-a-offline-20261121.md` |
| `.cache/ufs-boot-verifier-20261111-01` | 0.001646 | 不确定：用途及重建输入未核 |
| `.cache/ufs-exit-audit` | 0.001628 | 需保留：引用 `docs/ufs-hci30-compat.md`, `docs/ufs-resource-evidence.md`, `porting.toml` |
| `.cache/smmu-offline-20261112` | 0.001489 | 不确定：用途及重建输入未核 |
| `.cache/ufs-identity-core` | 0.001478 | 需保留：引用 `docs/ufs-resource-evidence.md`, `porting.toml` |
| `.cache/native-read-contract-20261112` | 0.001375 | 需保留：引用 `docs/ufs-native-readcheck.md`, `porting.toml` |
| `.cache/native-read-review-20261112` | 0.001355 | 需保留：引用 `docs/ufs-native-readcheck.md`, `porting.toml` |
| `.cache/imagefv-analysis` | 0.001215 | 不确定：用途及重建输入未核 |
| `.cache/ref-pipa` | 0.001180 | 需保留：引用 `docs/launchd-disable-list-20261123.md` |
| `.cache/ufs-component-guard` | 0.000822 | 需保留：引用 `docs/ufs-resource-evidence.md`, `porting.toml` |
| `.cache/sec-fd-evidence-20261113` | 0.000628 | 不确定：用途及重建输入未核 |
| `.cache/ufs-hci30-compat-20261111` | 0.000531 | 需保留：引用 `docs/ufs-gate-a-offline-20261121.md`, `docs/ufs-hci30-compat.md` |
| `.cache/pid1-stage` | 0.000473 | 不确定：用途及重建输入未核 |
| `.cache/ufs-micode-source-20261111` | 0.000440 | 不确定：用途及重建输入未核 |
| `.cache/hci30-layout-ocs-20261112` | 0.000364 | 需保留：引用 `porting.toml` |
| `.cache/ufs-protocol-index` | 0.000337 | 需保留：引用 `docs/ufs-handoff-design.md` |
| `.cache/ufs-hci-retirement-20261113` | 0.000316 | 不确定：用途及重建输入未核 |
| `.cache/ufs-version-test-snapshot-20261112-b` | 0.000298 | 不确定：用途及重建输入未核 |
| `.cache/adreno-source-20261114` | 0.000296 | 不确定：用途及重建输入未核 |
| `.cache/hci-layout-review-20261112` | 0.000266 | 不确定：用途及重建输入未核 |
| `.cache/ufs-version-entry-final-20261111` | 0.000222 | 不确定：用途及重建输入未核 |
| `.cache/ufs-observation-only-20261111` | 0.000173 | 需保留：引用 `docs/ufs-24r-diagnostic.md`, `porting.toml` |
| `.cache/ufs-handoff-boundary` | 0.000164 | 需保留：引用 `docs/ufs-handoff-capture.md`, `docs/ufs-handoff-design.md` |
| `.cache/ufs-public-matrix-20261114` | 0.000148 | 不确定：用途及重建输入未核 |
| `.cache/ufs-version-entry-20261111` | 0.000129 | 不确定：用途及重建输入未核 |
| `.cache/__pycache__` | 0.000077 | 不确定：用途及重建输入未核 |
| `.cache/patchsets` | 0.000070 | 需保留：引用 `docs/repo-diff-patches-20261123.md` |
| `.cache/android-ufs-identity-gpt-20261114-201917` | 0.000062 | 需保留：引用 `docs/SESSION-HANDOFF-20261114.md`, `docs/persistent-boot-slot-plan.md` |
| `.cache/stray-20261122` | 0.000058 | 不确定：用途及重建输入未核 |
| `.cache/cp22r-isolated-b3a3bf690069426bb960ac77c006a5d7` | 0.000056 | 不确定：用途及重建输入未核 |
| `.cache/ufs-kallsyms-candidate-20261111` | 0.000050 | 不确定：用途及重建输入未核 |
| `.cache/local-dup` | 0.000036 | 需保留：远端 blob 不全相同 |
| `.cache/verifier-ufs-version-final-20261112` | 0.000026 | 不确定：用途及重建输入未核 |
| `.cache/verify-production-os-trust-20261113` | 0.000018 | 不确定：用途及重建输入未核 |
| `.cache/pmgr-reference` | 0.000017 | 不确定：用途及重建输入未核 |
| `.cache/ufs-version-discrimination-20261111` | 0.000016 | 不确定：用途及重建输入未核 |
| `.cache/ufs-property-closure` | 0.000015 | 需保留：引用 `docs/ufs-resource-evidence.md`, `porting.toml`, `scripts/check-enuma-ufs-property-closure.py` |
| `.cache/ufs-version-model-20261111` | 0.000014 | 不确定：用途及重建输入未核 |
| `.cache/ufs-stock-package-20261111` | 0.000011 | 不确定：用途及重建输入未核 |
| `.cache/ufs-evidence` | 0.000010 | 需保留：引用 `docs/ufs-hci30-compat.md`, `docs/ufs-resource-evidence.md`, `porting.toml` |
| `.cache/android-sysfs-20261112-113131` | 0.000009 | 需保留：引用 `docs/persistent-boot-slot-plan.md`, `docs/store-geometry-feasibility-20261123.md`, `porting.toml` |
| `.cache/ufs-submit-audit-20261114` | 0.000008 | 不确定：用途及重建输入未核 |
| `.cache/cp22r-isolated-0bf4d8a7edb94f87b7be3c87418c68b4` | 0.000006 | 不确定：用途及重建输入未核 |
| `.cache/cp22r-isolated-d3f729022ec14c218da3c26ee5cfc115` | 0.000006 | 不确定：用途及重建输入未核 |
| `.cache/cp22r-isolated-eb32211ab71442208193bec1915e5388` | 0.000006 | 不确定：用途及重建输入未核 |
| `.cache/stage-a-connection-20261113` | 0.000005 | 不确定：用途及重建输入未核 |
| `.cache/ufs-identity-snapshot` | 0.000005 | 需保留：引用 `docs/ufs-resource-evidence.md`, `porting.toml`, `scripts/parse-enuma-ufs-identity.py` |
| `.cache/ufs-userdata-twrp-write-20261118` | 0.000004 | 需保留：引用 `docs/SESSION-HANDOFF-20261119.md`, `docs/ufs-root-mount-20261118-observation.md`, `porting.toml` |
| `.cache/ufs-handoff-design` | 0.000004 | 需保留：引用 `docs/ufs-handoff-design.md` |
| `.cache/ufs-24r-device-evidence-20261111` | 0.000002 | 不确定：用途及重建输入未核 |
| `.cache/ufs-obs-iterate` | 0.000002 | 不确定：用途及重建输入未核 |
| `.cache/rom-version-passive-20261111` | 0.000002 | 不确定：用途及重建输入未核 |
| `.cache/ufs-android-passive-20261111` | 0.000001 | 不确定：用途及重建输入未核 |
| `.cache/stage3` | 0.000000 | 不确定：用途及重建输入未核 |
| `.cache/upstream` | 0.000000 | 不确定：用途及重建输入未核 |

以上结果取代本文开头及「未完成」中关于逐项大小/分类未完成的旧时点表述；备份、链接复核、独立审验及删除仍未完成。

## B 类中间物估算（self-checked）

WizTree 同一快照的 50 项文件长度总计 54,559,760,410 B（50.812737 GiB）；50 项均有顶层 `boot.img` 文件行。按白名单逐文件分类、排除保留名称与 `.git`，候选上界 **22,573,286,814 B（21.023012 GiB）**，其余 **31,986,473,596 B（29.789725 GiB）**；后者包括 boot.img、文档及其他未命中白名单的文件，不只是 boot.img 和文档。两者之和精确等于 50.812737 GiB。A 快照 6.162616 GiB 加此候选上界为 **27.185628 GiB**（分别四舍五入）。CSV 不含文件头信息、当前文件状态及可靠的链接安全判定，此值不是可执行释放量。

按候选文件长度降序，最大的五项（均为 124,755,968 B，即 0.116188 GiB；路径相对 `out/`）：

1. `ufs-sm8250-rx-20261123-r51/prelink.macho`
2. `ufs-sm8250-ps-20261123-r45/prelink.macho`
3. `ufs-sm8250-lite4-20261123-r50/prelink.macho`
4. `ufs-sm8250-fxdiagbp-20261123-r48/prelink.macho`
5. `ufs-sm8250-fxdiag-20261123-r47/prelink.macho`

脚本 `--prune-b` 只枚举 B 内白名单文件，保留命名受保护文件及 `-----BEGIN` 开头文件；保留空目录以避免间接删除保护内容。缺失顶层 `boot.img` 或发现任意 reparse point 时整项跳过。当前 dry-run 跳过 24 个含 reparse point 的 B 目录，实际列出 **4.885808 GiB**，与 A 快照合计 **11.048424 GiB**；这是当前文件长度而非 CSV 上界，仍需人工核对。`--apply` 只供用户手动执行并逐项确认；本次未删除。文件内容和目录可在扫描后变化，执行前仍须停止构建并人工复核。独立 verifier 尚未复跑。

## WSL 手动清理替代方案（2026-11-24，self-checked）

本节取代上述 PowerShell 删除建议：PowerShell 脚本已废弃删除逻辑，仅可 dry-run 统计。WSL 脚本只由用户手动执行；agent 未执行删除。默认 dry-run，`--apply` 先列总项数和逻辑字节，且要求 `CLEANUP_CONFIRM=YES`。待删路径自身是链接则跳过，24 项全排除；B 类新增发现链接也跳过整个根，保留 boot.img、镜像、文档、签名材料及 BEGIN 文件。Linux `rm -rf` 不跟随目录树内符号链接；应用时须停止构建避免扫描与执行间路径变化。A 为整目录删除，故其内容保护依赖事先备份；自由文本引用仍会失效。B 清理后逐根检查 boot.img 和空目录。

用户先完成 Step 0A/0B 备份及逐个 SHA-256 核验、人工复核目标与引用，停止构建；预览 `bash scripts/cleanup-enuma-out.sh`，再由用户自行决定是否执行 `CLEANUP_CONFIRM=YES bash scripts/cleanup-enuma-out.sh --apply`。脚本不操作 .cache。未实际执行删除，未运行独立 verifier。

CSV 文件行快照沿用上节：A 全部 6.162616 GiB；排除下列 24 项后 B 总量 13.612576 GiB，B-prune 不超过整个剩余 B，故 A+B-prune 文件逻辑大小保守估计 **0–19.775192 GiB**。零下界体现快照过时、保护项与执行时跳过；这是宽泛上界而不是已验证的实际回收。此前 11.048424 GiB 是旧 live dry-run 估算，不是 CSV 精算且不能保证当前可释放量。CSV 不反映稀疏文件、硬链接、压缩和实际分配；实际磁盘可释放空间无法由此给出可靠区间。24 项合计是整目录逻辑大小，不是放弃的 B-prune 空间。

### 排除的 24 项（CSV 文件逻辑字节）

| out 下目录 | 字节 |
|---|---:|
| ufs-sm8250-launchd-keystore-20261122-r21 | 1570372646 |
| ufs-sm8250-launchd-keystore-20261122-r20 | 1575592653 |
| ufs-sm8250-launchd-keystore-20261122-r19 | 1575612504 |
| ufs-sm8250-launchd-keystore-20261122-r17 | 1569306951 |
| ufs-sm8250-launchd-keystore-20261122-r16 | 1574695161 |
| ufs-sm8250-launchd-keystore-20261122-r15 | 1563004431 |
| ufs-sm8250-launchd-keystore-20261122-r14 | 1568323343 |
| ufs-sm8250-launchd-keystore-20261122-r13 | 1576625404 |
| ufs-sm8250-launchd-keystore-20261121-r11 | 2320091474 |
| ufs-sm8250-launchd-display-20261121-r10 | 2867858443 |
| ufs-sm8250-launchd-display-20261121-r9 | 3089257695 |
| ufs-sm8250-launchd-display-20261120-r8 | 1667452576 |
| ufs-sm8250-launchd-display-20261120-r7 | 2301741908 |
| ufs-sm8250-launchd-display-20261119-r6 | 1324746491 |
| ufs-sm8250-launchd-cache-20261119-r3 | 1187366414 |
| ufs-sm8250-policy-20261118-r3 | 970759816 |
| ufs-sm8250-launchd-cache-20261119-r2 | 1311975409 |
| ufs-sm8250-policy-20261117-r2 | 1635790934 |
| ufs-sm8250-startroot-mode0-20261118-r2 | 1095943875 |
| ufs-sm8250-launchd-cache-20261119-r1 | 1466449050 |
| ufs-sm8250-launchd-data-20261119-r1 | 1567504085 |
| ufs-sm8250-launchd-display-20261119-r1 | 1318471323 |
| ufs-sm8250-policy-20261116-r1 | 1634745337 |
| ufs-sm8250-startroot-mode0-20261118-r1 | 1609680220 |
| 合计 | 39943368143 |

合计 **37.200160 GiB**（39943368143 B）。

## 链接目录保留判定（2026-11-24，self-checked）

上表 24 个目录逐一只读检查，**每项顶层 `boot.img` 均为现存普通文件、非符号链接**；本项检查未核对内容哈希，也未确认其它位置是否有相同备份。列表即上表全部 24 项。若按整目录删除，则 24 项都须先证明备份相同，否则先复制并校验；实际需要复制的数量未定。

判定继续按 B 类削中间物，而非整目录删除：`boot.img`、其他镜像、审计文档、manifest、签名材料和其他保留文件不能因发现符号链接而丢弃。用户提出的第二阶段 `rm -rf <dir>` 会删除这些保留项；仅备份 `boot.img` 不能满足保留规则，因此不能将两者视为同一个方案。现有脚本仍排除这 24 项，**没有实现 `--safe-remove-linked`**；也未执行删除、复制、或目标存在性核查。

CSV 中 A 和全部 B 的整目录逻辑长度上限为 **56.975353 GiB**（6.162616 + 50.812737，四舍五入），这不是 B 削中间物的预计释放量。按既有 B 白名单，A + 全部 B 候选文件长度上限为 **27.185628 GiB**；旧排除方案 **19.775192 GiB** 是 A + 剩余 B 整目录的宽泛上限，两者口径不同，不能直接计算实际增益。快照时间、链接、稀疏与保留文件均影响实际回收。
