# R-006 候选 A：无显示 MMIO 的早期停止点

2026-10-24 Asia/Shanghai。用户批准 R-006 候选 A。本文件记录候选设计、与历史镜像的真实差异、判别逻辑和执行计划。

## 为什么停在第 10 阶段

`patches/dxe-stage-checkpoints.patch` 把 `EnumaStageCheckpoint` 插在两个位置：`DxeMain.c` 入口（stage 9）与 `CoreDispatcher ()` 调用之前（stage 10）。其余 4–8 在 SEC，11 在 `CoreDispatcher ()` 返回之后，12/13 在 Dispatcher 的驱动装载与 `CoreStartImage` 返回处。

选 stage 10 的理由是它**恰好站在所有 DXE 驱动被派发之前**：此时 SimpleFbDxe 虽已打进 FV，但一行代码都没执行过，`0x0ae00000..0x0ae84207` 一次都没被读。于是这一笔只检验一件事——`MicroSecondDelay(2s)` + `ResetCold()` 这条路走不走得通。

## 与失败镜像的真实差异

必须说清楚，这份候选**不是** step20 的同源对照。构建参数上：

| 项 | step20 / stage23-control | 本候选 |
| --- | --- | --- |
| `--stop-stage` | 13 | **10** |
| `--stop-delay` | 2 | 2 |
| `--dispatch-ordinal` | 1 | 1 |
| `--detail-point` | 16 | 13 |
| `--dispatch-guid` / `--dispatch-guid-only` | 有 | **无** |
| `--dispatch-completion-fallback` | 有 | **无** |
| `--diagnostic-gop-query` / `--gop-step` | 1 / 20 | **0 / 0** |
| `--diagnostic-simplefb` | 有 | 有 |

中间四项不是选择，是脚本的硬约束：`build_enuma_firmware.py` 对 `--stop-stage != 13` 直接拒绝 `--detail-point != 13`、`--dispatch-guid`、`--dispatch-guid-only`、`--dispatch-completion-fallback` 和 `--diagnostic-gop-query`。这些代码路径全部位于 stage 13 之后才可能到达的位置（`CoreStartImage` 返回、GOP 查询结果编码），stage 10 之前永不执行，因此它们不构成运行期变量。SimpleFbDxe 仍然打包（保持 FOD 集合与失败笔一致），只是不会被执行。

## 判别逻辑

重复最多 5 笔，每笔前置同一套核验：

| 观测 | 结论 | 下一步 |
| --- | --- | --- |
| 5 笔全部自动返回 | 复位出口在"未触碰显示 MMIO"时稳定 | 超时归到派发之后，转查 MDP 上电/时钟门控与 R-004 映射时序 |
| 任一笔挂死 | 无显示 MMIO、无等待仍挂死，复位出口自身失效 | 换出口：warm reset、BootShim 兜底，或干脆不主动复位让正常启动继续 |
| 不足 5 笔完成 | 不成立结论 | 记录实际完成笔数与停止原因 |

第 2 种情况是本轮最想要的结果：它一次性把"显示探针"从嫌疑名单里摘出去，也解释了历史上 S-001 / 250849f / S-002 / S-003 反复出现却查不到的同一个现象。

## 构建与打包命令

固件源码不变（stage 10 已在既有补丁里），固定提交仍是 `c45e52a`。在 WSL 中执行：

```bash
cd /mnt/d/Code/UniXNU-enuma
python3 scripts/build_enuma_firmware.py \
  --device-root /mnt/d/Code/UniXNU-enuma \
  --unixnu /mnt/d/Code/UniXNU-enuma/out/sources/UniXNU \
  --stop-stage 10 --stop-delay 2 \
  --dispatch-ordinal 1 --detail-point 13 \
  --diagnostic-simplefb --jobs 8
```

打包沿用 `scripts/package_enuma_boot.py`，`--kernel` 取本次 BootShim+FD，`--ramdisk` 用空文件，输出到 `out/boot-candidate/`，文件名按 `config/exit-early-probes.json` 的 variant。

## 阻塞

本轮宿主把 `wsl.exe` 列入安全策略的程序黑名单，本会话无法调用，Windows 侧也没有 clang，因此构建与 `check_scanout_*` 一类主机/AArch64 资格脚本都无法执行。需要解除该黑名单，或在 WSL 终端代跑上述命令后由本会话继续打包、审计与实测。

## 边界

不改固件源码、不改内存字段/verified/新映射，不做像素或 MMIO 写、不写分区。冻结镜像（step22 正向、stage23-control 及未执行正互补）不重试。R-005 仍 consumed。
