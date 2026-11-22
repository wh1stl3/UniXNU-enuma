# 五仓 XNU 补丁文件名机械差分（2026-11-23）

状态：self-checked，仅文件名集合；未构建、未操作设备。

## 输入与方法

- enuma：递归扫描设备仓所有路径（包括 `.cache`、`out` 等），42 个不同 basename；外仓缓存和历史产物混入，不能视作 enuma 实际应用集。
- nuwa：`git worktree list --porcelain` 的 11 个工作树逐一递归扫描，38 个 basename；集合包含历史 worktree 与其缓存，不代表某个构建。
- sheng：`UniXNU/UniXNU-sheng@c8f92b208068eeaa4cd2b0f592671f04ee70076e` Git tree，25 个 basename。
- sirius：`HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503` 本地缓存，16 个 basename。
- OPi5：`Ken-u/UniXNU-orangepi5@729ba25f4d67225ff3853ba1e435b95af97e59e3` 本地缓存，7 个 basename。
- 路径按 `find <repo> -name '*.patch' -path '*xnu*'` 过滤并取 basename，sheng 用 `git ls-tree`；集合差由 `comm` 计算并以 Python set 核对。缓存结果位于 `.cache/patchsets/`。同名不代表内容相同；仅某仓有不代表其他仓构建缺少相应行为。
- 非共有项主题仅从文件名机械提取，未读补丁内容，作用标为“未读”。五个独有集合不包含在 2–4 仓出现的项目。

## 六组完整清单

### 仅 enuma：19 项

- `enuma-pid1-observer.patch` — 主题（仅文件名）：`enuma-pid1-observer`；作用未读。
- `enuma-pmgr-publisher.patch` — 主题（仅文件名）：`enuma-pmgr-publisher`；作用未读。
- `enuma-r10-vnode-space-probe.patch` — 主题（仅文件名）：`enuma-r10-vnode-space-probe`；作用未读。
- `enuma-r11-board-classes.patch` — 主题（仅文件名）：`enuma-r11-board-classes`；作用未读。
- `enuma-r11-keystore-probe.patch` — 主题（仅文件名）：`enuma-r11-keystore-probe`；作用未读。
- `enuma-r13-console-throughput.patch` — 主题（仅文件名）：`enuma-r13-console-throughput`；作用未读。
- `enuma-r14-arm64-cache-probe.patch` — 主题（仅文件名）：`enuma-r14-arm64-cache-probe`；作用未读。
- `enuma-r15-shared-region-probe.patch` — 主题（仅文件名）：`enuma-r15-shared-region-probe`；作用未读。
- `enuma-r16-cpu-calibration.patch` — 主题（仅文件名）：`enuma-r16-cpu-calibration`；作用未读。
- `enuma-r17-exit-probe.patch` — 主题（仅文件名）：`enuma-r17-exit-probe`；作用未读。
- `enuma-r25-census.patch` — 主题（仅文件名）：`enuma-r25-census`；作用未读。
- `enuma-r26-fbcount.patch` — 主题（仅文件名）：`enuma-r26-fbcount`；作用未读。
- `enuma-r27-fbcount.patch` — 主题（仅文件名）：`enuma-r27-fbcount`；作用未读。
- `enuma-r9-vnode-space-probe.patch` — 主题（仅文件名）：`enuma-r9-vnode-space-probe`；作用未读。
- `enuma-timebase-probe.patch` — 主题（仅文件名）：`enuma-timebase-probe`；作用未读。
- `llvm-xnu-builtin-type.patch` — 主题（仅文件名）：`llvm-xnu-builtin-type`；作用未读。
- `native-smp-secondary.patch` — 主题（仅文件名）：`native-smp-secondary`；作用未读。
- `native-smp-type-clusters.patch` — 主题（仅文件名）：`native-smp-type-clusters`；作用未读。
- `xnu.patch` — 主题（仅文件名）：`xnu`；作用未读。

### 仅 sheng：25 项

- `sheng-appsync-runtime.patch` — 主题（仅文件名）：`sheng-appsync-runtime`；作用未读。
- `sheng-appsync-user-trust.patch` — 主题（仅文件名）：`sheng-appsync-user-trust`；作用未读。
- `sheng-bluetooth-exit-diagnostic.patch` — 主题（仅文件名）：`sheng-bluetooth-exit-diagnostic`；作用未读。
- `sheng-bluetooth-runtime.patch` — 主题（仅文件名）：`sheng-bluetooth-runtime`；作用未读。
- `sheng-bootstrap-checkpoints.patch` — 主题（仅文件名）：`sheng-bootstrap-checkpoints`；作用未读。
- `sheng-cache-input-diagnostic.patch` — 主题（仅文件名）：`sheng-cache-input-diagnostic`；作用未读。
- `sheng-headless-startup-checkpoints.patch` — 主题（仅文件名）：`sheng-headless-startup-checkpoints`；作用未读。
- `sheng-main-thread-profile.patch` — 主题（仅文件名）：`sheng-main-thread-profile`；作用未读。
- `sheng-platform-sleep.patch` — 主题（仅文件名）：`sheng-platform-sleep`；作用未读。
- `sheng-process-exit-log.patch` — 主题（仅文件名）：`sheng-process-exit-log`；作用未读。
- `sheng-startup-failure-log.patch` — 主题（仅文件名）：`sheng-startup-failure-log`；作用未读。
- `sheng-wifi-association-event.patch` — 主题（仅文件名）：`sheng-wifi-association-event`；作用未读。
- `sheng-wifi-launchd-cache.patch` — 主题（仅文件名）：`sheng-wifi-launchd-cache`；作用未读。
- `source-storage-runtime.patch` — 主题（仅文件名）：`source-storage-runtime`；作用未读。
- `vmwait-dyld-pager-source-release.patch` — 主题（仅文件名）：`vmwait-dyld-pager-source-release`；作用未读。
- `zzyd-sheng-audio-addon-mount.patch` — 主题（仅文件名）：`zzyd-sheng-audio-addon-mount`；作用未读。
- `zzye-sheng-cpu-idle.patch` — 主题（仅文件名）：`zzye-sheng-cpu-idle`；作用未读。
- `zzyf-sheng-amp.patch` — 主题（仅文件名）：`zzyf-sheng-amp`；作用未读。
- `zzzz-sheng-ipados27-bringup.patch` — 主题（仅文件名）：`zzzz-sheng-ipados27-bringup`；作用未读。
- `zzzzzz-sheng-bsd-checkpoints.patch` — 主题（仅文件名）：`zzzzzz-sheng-bsd-checkpoints`；作用未读。
- `zzzzzz-sheng-latency-trace.patch` — 主题（仅文件名）：`zzzzzz-sheng-latency-trace`；作用未读。
- `zzzzzzzz-sheng-exit-latency.patch` — 主题（仅文件名）：`zzzzzzzz-sheng-exit-latency`；作用未读。
- `zzzzzzzzz-sheng-unnest-trace.patch` — 主题（仅文件名）：`zzzzzzzzz-sheng-unnest-trace`；作用未读。
- `zzzzzzzzzz-sheng-sigp-reinit-assert.patch` — 主题（仅文件名）：`zzzzzzzzzz-sheng-sigp-reinit-assert`；作用未读。
- `zzzzzzzzzzz-sheng-edge-matrix.patch` — 主题（仅文件名）：`zzzzzzzzzzz-sheng-edge-matrix`；作用未读。

### 仅 nuwa：38 项

- `8796-apple-only-cpu-tunables.patch` — 主题（仅文件名）：`8796-apple-only-cpu-tunables`；作用未读。
- `8796-clang-var-init-flag.patch` — 主题（仅文件名）：`8796-clang-var-init-flag`；作用未读。
- `8796-compile-records.patch` — 主题（仅文件名）：`8796-compile-records`；作用未读。
- `8796-indirection.patch` — 主题（仅文件名）：`8796-indirection`；作用未读。
- `8796-iorpc-kernel-content.patch` — 主题（仅文件名）：`8796-iorpc-kernel-content`；作用未读。
- `8796-kperf-kpc-link-guards.patch` — 主题（仅文件名）：`8796-kperf-kpc-link-guards`；作用未读。
- `8796-kperf-kpc-off.patch` — 主题（仅文件名）：`8796-kperf-kpc-off`；作用未读。
- `8796-non-apple-iommu-bootstrap.patch` — 主题（仅文件名）：`8796-non-apple-iommu-bootstrap`；作用未读。
- `8796-nuwa-boot-progress.patch` — 主题（仅文件名）：`8796-nuwa-boot-progress`；作用未读。
- `8796-nuwa-boot-time.patch` — 主题（仅文件名）：`8796-nuwa-boot-time`；作用未读。
- `8796-nuwa-cache-location-skip.patch` — 主题（仅文件名）：`8796-nuwa-cache-location-skip`；作用未读。
- `8796-nuwa-cs-observe.patch` — 主题（仅文件名）：`8796-nuwa-cs-observe`；作用未读。
- `8796-nuwa-exec-policy-skip.patch` — 主题（仅文件名）：`8796-nuwa-exec-policy-skip`；作用未读。
- `8796-nuwa-lookup-trace.patch` — 主题（仅文件名）：`8796-nuwa-lookup-trace`；作用未读。
- `8796-nuwa-observe-log.patch` — 主题（仅文件名）：`8796-nuwa-observe-log`；作用未读。
- `8796-nuwa-observe-markers.patch` — 主题（仅文件名）：`8796-nuwa-observe-markers`；作用未读。
- `8796-nuwa-panic-fallback.patch` — 主题（仅文件名）：`8796-nuwa-panic-fallback`；作用未读。
- `8796-nuwa-pmgr-root-publication.patch` — 主题（仅文件名）：`8796-nuwa-pmgr-root-publication`；作用未读。
- `8796-nuwa-r13-data-mount.patch` — 主题（仅文件名）：`8796-nuwa-r13-data-mount`；作用未读。
- `8796-nuwa-r13-ram-block-init.patch` — 主题（仅文件名）：`8796-nuwa-r13-ram-block-init`；作用未读。
- `8796-nuwa-r13-ram-block-persona.patch` — 主题（仅文件名）：`8796-nuwa-r13-ram-block-persona`；作用未读。
- `8796-nuwa-r14-data-mount.patch` — 主题（仅文件名）：`8796-nuwa-r14-data-mount`；作用未读。
- `8796-nuwa-r22-dyld-flags-readback.patch` — 主题（仅文件名）：`8796-nuwa-r22-dyld-flags-readback`；作用未读。
- `8796-nuwa-r24-reboot-observe.patch` — 主题（仅文件名）：`8796-nuwa-r24-reboot-observe`；作用未读。
- `8796-nuwa-reboot-observe.patch` — 主题（仅文件名）：`8796-nuwa-reboot-observe`；作用未读。
- `8796-nuwa-root-auth-skip.patch` — 主题（仅文件名）：`8796-nuwa-root-auth-skip`；作用未读。
- `8796-nuwa-root-cdir-ref.patch` — 主题（仅文件名）：`8796-nuwa-root-cdir-ref`；作用未读。
- `8796-nuwa-systemos-mount.patch` — 主题（仅文件名）：`8796-nuwa-systemos-mount`；作用未读。
- `8796-nuwa-trust-cache-init.patch` — 主题（仅文件名）：`8796-nuwa-trust-cache-init`；作用未读。
- `8796-nuwa-ufs-handoff-observe.patch` — 主题（仅文件名）：`8796-nuwa-ufs-handoff-observe`；作用未读。
- `8796-offline-legacy-display-early.patch` — 主题（仅文件名）：`8796-offline-legacy-display-early`；作用未读。
- `8796-offline-legacy-display-late.patch` — 主题（仅文件名）：`8796-offline-legacy-display-late`；作用未读。
- `8796-source-machine-layer.patch` — 主题（仅文件名）：`8796-source-machine-layer`；作用未读。
- `8796-sparse-prelink-index.patch` — 主题（仅文件名）：`8796-sparse-prelink-index`；作用未读。
- `8796-uio-stackbuf.patch` — 主题（仅文件名）：`8796-uio-stackbuf`；作用未读。
- `8796-unifdef-headers.patch` — 主题（仅文件名）：`8796-unifdef-headers`；作用未读。
- `8796-vfs-getvfs-with-vfsops.patch` — 主题（仅文件名）：`8796-vfs-getvfs-with-vfsops`；作用未读。
- `8796-zzx-pmap-sync-64bit-pa.patch` — 主题（仅文件名）：`8796-zzx-pmap-sync-64bit-pa`；作用未读。

### 仅 sirius：0 项

空。

### 仅 OPi5：0 项

空。

### 五仓共有：0 项

空。

四个非 enuma 独有组之和 63 项；其组之间定义上不重叠。四仓并集减 enuma 共 63 个不同文件名，包含跨 2–4 仓共有而不在独有组的项。

## enuma 脚本引用与 r40 构建边界

`grep -rnoE` 在 `scripts/` 找到 39 个不同 `.patch` basename；`.cache/patchsets/enuma-applied.txt` 是按题述命名保存的**全脚本引用候选，不是实际应用证明**。其中含 UEFI、测试 mock、审计引用与其他构建，不可全数归入 r40。完整引用路径和行号：

- `scripts/audit-enuma-24r-rebinding.py:503:patches/xnu/enuma-pid1-observer.patch`
- `scripts/audit-enuma-pid1.py:149:patches/xnu/enuma-pid1-observer.patch`
- `scripts/audit_console_readiness.py:16:firmware/patches/dxe-dispatch-details.patch`
- `scripts/audit_display_handoff.py:168:firmware/patches/kona-preserve-display.patch`
- `scripts/audit_display_handoff.py:169:firmware/patches/sec-preserve-display.patch`
- `scripts/audit_oem_apriori.py:60:firmware/patches/apriori-metronome.patch`
- `scripts/build-enuma-owner-data.py:276:offline-owner-boot-manifest.patch`
- `scripts/build-enuma-owner-data.py:276:offline-owner-root-binding-audit.patch`
- `scripts/build-enuma-owner-data.py:282:zzyb-native-cryptex-os-view.patch`
- `scripts/build-enuma-owner-data.py:283:zzy-native-gpu-addon-mount.patch`
- `scripts/build-enuma-owner-data.py:283:zzy-staged-system-apps.patch`
- `scripts/build-enuma-owner-data.py:284:offline-owner-z-air-init.patch`
- `scripts/build-enuma-owner-data.py:287:patches/xnu/offline-owner-systemos-mount.patch`
- `scripts/build-enuma-production-final-link.py:113:patches/isolated/sheng-ufs-boot-progress-guard.patch`
- `scripts/build-enuma-production-final-link.py:83:patches/xnu/zzz-boot-progress.patch`
- `scripts/build-enuma-r13-console-throughput.py:99:patches/xnu/enuma-r13-console-throughput.patch`
- `scripts/build-enuma-r14-arm64-cache-probe.py:126:patches/xnu/enuma-r14-arm64-cache-probe.patch`
- `scripts/build-enuma-r15-shared-region-probe.py:122:patches/xnu/enuma-r15-shared-region-probe.patch`
- `scripts/build-enuma-r16-cpu-calibration.py:176:patches/xnu/enuma-r16-cpu-calibration.patch`
- `scripts/build-enuma-r17-exit-probe.py:145:patches/xnu/enuma-r17-exit-probe.patch`
- `scripts/build-enuma-r25-census.py:188:patches/xnu/enuma-r25-census.patch`
- `scripts/build-enuma-r26-fbcount.py:114:patches/xnu/enuma-r26-fbcount.patch`
- `scripts/build-enuma-r27-fbcount.py:117:patches/xnu/enuma-r27-fbcount.patch`
- `scripts/check-enuma-pid1.py:18:patches/xnu/enuma-pid1-observer.patch`
- `scripts/check-enuma-smmu-route-contexts.py:10:minimal.patch`
- `scripts/check_firmware_overlay.py:111:firmware/patches/kona-preserve-display.patch`
- `scripts/check_firmware_overlay.py:140:firmware/patches/sec-preserve-display.patch`
- `scripts/check_firmware_source.py:40:patches/dxe-dispatch-return.patch`
- `scripts/check_firmware_source.py:40:patches/dxe-stage-checkpoints.patch`
- `scripts/check_firmware_source.py:41:patches/dxe-dispatch-details.patch`
- `scripts/check_firmware_source.py:41:patches/dxe-driver-checkpoints.patch`
- `scripts/check_firmware_source.py:42:patches/dispatcher-display-read.patch`
- `scripts/check_firmware_source.py:43:Resources/MuPatches/Gic-Spurious.patch`
- `scripts/check_gop_audit.py:51:simplefb-contract.patch`
- `scripts/check_gop_audit.py:51:simplefb-gop-query.patch`
- `scripts/check_oem_progress.py:32:firmware/patches/oem-system-table-sync.patch`
- `scripts/check_oem_progress.py:52:firmware/patches/oem-system-table-sync.patch`
- `scripts/check_optional_display.py:17:patches/xnu/offline-component-load-probes.patch`
- `scripts/check_simplefb_contract.py:10:patches/simplefb-contract.patch`
- `scripts/check_simplefb_contract.py:34:diagnostic-ufs-selection.patch`
- `scripts/check_simplefb_contract.py:34:dispatch-detail-options.patch`
- `scripts/check_simplefb_contract.py:34:simplefb-contract.patch`
- `scripts/check_simplefb_contract.py:34:simplefb-diagnostic-selection.patch`
- `scripts/check_simplefb_contract.py:37:patches/simplefb-diagnostic-selection.patch`
- `scripts/check_simplefb_handoff.py:33:patches/simplefb-contract.patch`
- `scripts/ci/native_final_link.py:131:patches/xnu/native-aes-personality.patch`
- `scripts/ci/native_final_link.py:140:patches/kernel/enuma-storage-late-init.patch`
- `scripts/ci/native_final_link.py:143:patches/xnu/zzx-enuma-storage-late-init.patch`
- `scripts/qualify_oem_runtime.py:92:source/patches/oem-system-table-sync.patch`
- `scripts/tests/test_enuma_owner_policy.py:87:mock.patch`
- `scripts/tests/test_enuma_owner_policy.py:88:mock.patch`
- `scripts/tests/test_enuma_owner_policy.py:90:mock.patch`

r40 `scripts/build-enuma-r40-storegeom.py:23-30,38-49,82-88,112-135` 从 r39 继承产物、读取 r11 已生成的 `source/bsd/kern/bsd_init.c` 和 UFS 已生成源码，插入片段并重编对象；并非 r40 在该脚本中重新 apply 全部 series。`git -C out/ufs-sm8250-launchd-keystore-20261121-r11/self-check/build-final/source rev-parse --show-toplevel` 返回设备仓根，说明该源码副本不是独立 Git 树，不能用其 `git log` 获得 XNU 变更。r40 完整实际补丁闭包不可得：复用对象和先前构建链的应用记录未在本轮机械引用扫描中闭合。

## 基线与证据边界

| 仓 / profile | 用户态 | XNU、页大小、架构 |
|---|---|---|
| enuma | iPadOS 17.7.11 / 21H461 | 本次机械扫描未核对 |
| sheng 像素参照 | macOS 27.3；未找到 iPadOS 17 像素证据 | 本次机械扫描未核对 |
| nuwa | iOS 16 | 本次机械扫描未核对各 worktree 产物 |
| sirius、Orange Pi 5 | 本次机械扫描未核对实际 profile | 本次机械扫描未核对 |

sheng 不是同版本参照：不能把 macOS 27.3 像素观察归给 iPadOS 17。
