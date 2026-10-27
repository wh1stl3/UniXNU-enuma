# D-298：完整开发固件构建通过，补齐迁移后的 R-022 准备入口

2026-10-26，Asia/Shanghai。用户要求继续至需要开始录像，同时保留不自动提交推送、冻结 R-022、不得复用已消费试验及实机部署前停点。本轮零 ADB/fastboot/相机操作，无提交推送、权限更改、重置清理或 nuwa 操作。

## 完整开发构建

新增固件仓 `Resources/Scripts/build_enuma_development.py`，显式导出当前工作树到设备仓全新 `out/` 子目录，保存原始源码 SHA256 清单和单独标记的开发 metadata 派生件。原 `Resources/Enuma` metadata、设备源锁、R-022 资格和旧 staging 不改。新目录的 Git metadata 只为固定上游构建器提供历史时间戳，不能代表开发快照；实际输入身份是 `source-manifest.json`。

继续调用固定 UniXNU 官方 `unixnu.firmware.build` 和现有 enuma preflight/patch 系列。preflight 增加可选的新报告路径，开发报告只进新 `out/`。上游补丁检查改在临时副本重建，原 UniXNU 源码不反向应用/重施补丁。没有调用会先恢复旧 staging 的设备兼容入口。

`run1` 失败于 BaseTools 缺失 Brotli 源码，未产生 FD，失败报告与日志保留。实际固件仓 Mu 的这些嵌套子模块是空目录。新增 `stage_enuma_development_dependencies.py`，仅在新 `out/development-fd-20261026/dependencies` 获取 Mu 固定 gitlink 的 Brotli、libfdt、MIPI Sys-T、libspdm，检查精确 commit 和干净检出后导出；无更新原子模块。`run2` 重新从固定归档构建 BaseTools 和整机 FD，通过，所有 Core 临时补丁已回退。

| 产物 | SHA256 |
| --- | --- |
| 完整 3 MiB FD | `e8251bf1dcae6fefda4e995e6b9765260f4f8d5fdd8cdb929dedbf112d57357e` |
| 开发 Boot v3，3153920 字节 | `6bc685ae06d030a2df4f71c7effcf5834bd5b48b24d27da79cd640f1fde13e19` |
| 开发源 manifest | `d59e5b457037261670ec38f6f82578d8c42607367f4920843a0184eea1207fe0` |

路径：`out/development-fd-20261026/run2/work/uefi/Build/enumaPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd`；`out/development-fd-20261026/qualification1/enuma-development-stage10.img`。

新增 `scripts/qualify_development_fd.py`：实际 FD 解析为 80 个 FFS 文件；OEM PE/DEPEX 保持身份，诊断排除 CPR/Display/UFS；DxeCore、EnumaProbe、BdsDxe、GraphicsConsole、UniXNU、自测应用的实际 PE/编译响应绑定，Core journal=1/stage10 宏成立。生成 Probe 不再含 DiagDraw/Fb[]/raw framebuffer cache 写回，归因/控制台头进入完整构建；新 WT 创建、发布、故障状态符号存在于实际 InheritedGopLib 库。192 字节 BootShim 与 3 MiB FD 拼装，固定 AOSP Boot v3 打包和独立解包逐字节一致。

**这是整机开发构建与链接资格，不是实机菜单候选。** stage10 在 BDS 前停止，晚期 Probe 回放默认关闭，自测应用不自动启动，ramdisk 为空，未接通真实 WT GOP 发布路径。新 API 在库内存在不等于所有未引用函数进入最终 PE，更不等于物理运行。D-296/297 的真实菜单软件行为继续由独立 QEMU 证据支持；本轮不重报为设备成功。

重现命令（所有输出目录须不存在）：

```powershell
wsl --exec env PYTHONDONTWRITEBYTECODE=1 python3 firmware/Resources/Scripts/build_enuma_development.py --device-root /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/development-fd-next --dependency-root /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/development-fd-20261026/dependencies --jobs 6
wsl --exec /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/firmware-tools/bin/python -B scripts/qualify_development_fd.py --build out/development-fd-next --output out/development-fd-next-qualification
```

## 实测前软件阻塞的修复

历史 current.local.json 仍含 `D:/Code/UniXNU-enuma/out/device-tests/...`。新增 `enuma_paths.evidence_path`，只接受明确 enuma 根下的 out 路径或本仓相对 out 路径，解析到新根，拒绝 nuwa、近似前缀、上级目录与越界；旧记录原字节不改。entry/reconcile 使用解析后备份目录，再做原有摘要检查。迁移后的平台工具路径保留。

用户本轮“不自动提交推送”优先于旧工具强制 clean/pushed 的流程。新增 `r022_preparation.py` 与 runner 的显式 `--local-preparation`：只接受固定 R-022 镜像/固件/资格摘要，绑定当前 runner、依赖脚本、全部当前交接文件和固定资格/时钟/代码报告。文件改变即拒绝。其他候选和 R-021 重复例外不享有该入口；正常路径原发布门保持。清单不是实机批准，既有硬件批准检查仍先执行，批准配置保持 pending。

R-022 新增执行 UUID 与拍摄就绪向底层 runner 传递；设备命令前拒绝缺失就绪、错误镜像/scope、已有 claim、consumed 或历史 issued 记录。实际发 boot 前用 exclusive-create/fsync 原子 claim，崩溃也不能自动重试；这不是给旧试验新授权。人手观察报告只把相同 UUID/R-022 的 issued 状态归入本次，门前退出不会误认旧 current 状态。

30 项离线测试通过：迁移路径/越界拒绝、本地绑定漂移、pending 仍拒绝、拍摄/身份/scope 拒绝、并发单次 claim、历史发图拒绝、旧状态归因、R-021/像素/无相机/恢复门回归。所有设备调用均为 mock，不含实机结果；证据 `out/development-fd-20261026/host-gates.json`。完整构建及打包证据 `run2/build-result.json`、`qualification1/result.json`，历史失败 `run1/build-result.json`。

## 下一笔可检查的实机结果

仍为 **R-022 / 计划 S-050**：冻结 `out/inherited-gop/qualified-dxe-log-8s-8680ea7/image.img`，SHA256 `f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b`。256×96，8 秒，73728 读/49152 写/3DSB，原保存/复核/恢复读回和 75 秒规则不变。只显示此前已完成 point13 的实际 status/ordinal，不冒充当前 provider 返回，不是固定字母实验。

离线准备命令不启动设备：

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 -B scripts/r022_preparation.py --output out/r022-preparation-next
```

当前还需用户明确 R-022 精确单次放行和新的拍摄开始/就绪。届时先刷新 enuma 身份、Android/root/A槽/解锁、设备与本地备份摘要和时钟条件，再协调开始拍摄，才可单次临时 boot。无当前恢复按键欠项；最近硬件状态仅 S-049 的历史恢复，不能冒充新鲜预检。拍摄对准左上 256×96 并保留屏边定位，锁焦、适当降曝光、关闭录音，覆盖启动至返回 Android；原始影音仅本地。

结果分别验收完整三行十六进制内容、固定时钟窗、受控返回和独立恢复；看不清即未知并停止追加，不猜数、不重复消费。S-001..049/R-020/R-021 保持 consumed，R-022 未 claim、未批准、未执行。

requirements22、BLEND/地址/SMMU/下游路由未闭合；真实全局 DEBUG、ConOut、正式 GOP、UniXNU 菜单与输入仍未实测。可读日志后用新取得的真实值推进，不能因本轮完整 FD 成功而强制解除准入。
