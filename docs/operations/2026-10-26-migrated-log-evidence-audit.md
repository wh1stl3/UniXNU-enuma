# D-294：迁移后日志证据绑定与失败路径复核

2026-10-26（Asia/Shanghai）。本轮用户明确仅离线，实机暂停至另行精确放行且当前拍摄就绪；禁止自动提交推送、重置、清理、改权限及第二写入者。没有设备命令、相机、固件构建或重打包，没有新硬件硬停；既有内容观测停点继续有效。

## 工作区与冻结边界

当前根 `D:/Code/PortingiOS/enuma/UniXNU-enuma`，HEAD `89b609eeafc94e81021a35b0e0cbdb8c5eca9441`。实际固件子模块 HEAD `8680ea79d6fd14d4526d314f430e9812955cb78a`；独立 `D:/Code/PortingiOS/enuma/uefi-enuma` HEAD `74598dfa2b223716450de044caf937c4a30e51f5`，不是替代构建输入，不同步/切换/修复它。

迁移前后未提交改动保留；本轮接手快照在 `out/migration-log-audit-20261026/workspace-*/`，含状态、未暂存/暂存diff及原有修改文件副本。历史路径只追溯，不执行；没有改写历史报告中的旧路径。新运行全部使用迁移后路径。

收尾保全结果见`out/migration-log-audit-20261026/preservation-final.json`：467份报告/配置/归档检查点摘要无变化，reports/config无tracked差异，首次115项绑定与最终报告对应项完全一致；37份不属本轮交接更新的原有脏文件与接手副本逐字节相同。STATUS/HANDOFF改写前原字节另存`pre-D294-*.md`；DECISIONS只追加本轮记录，保留原迁移修改。快照进程已结束，没有遗留本轮构建/设备/取证进程。

R-022 归档 `out/inherited-gop/qualified-dxe-log-8s-8680ea7` 保留原字节。镜像 SHA256 `f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b`；FD `7bee85343b6f8837c1081f5cb08db939facfc1ec084c6f498d918ded1e02f035`。仍256×96/8秒、73728读/49152写/3DSB。R-022 pending、S-050未执行；S-001..049和R-020/R-021消费事实不变。`review_required=false` 是历史资格字段，不是免除执行批准；`execution_approval_required=true` 仍须成立。

## 本轮运行及结果

- 新增 `scripts/audit_migrated_log_evidence.py`，只读归档及绑定源，不加载构建后端；输出仅允许本仓out/内的新文件。最终118项通过：资格与归档逐字节一致、完整files清单摘要/长度、固定镜像/FD/固件身份、scope、源摘要/行锚点和六模块静态库清单。报告 `out/migration-log-audit-20261026/bindings-final.json`。首次115项结果保留于bindings.json，最终增加三个固定身份条件。
- 7项负向检查通过：mock归档损坏及源漂移均拒绝，四种外部/绝对路径拒绝，既有输出拒绝覆盖。使用读结果替身，不修改真实归档或源。`negative-checks.json`保留结果。
- `config/uefi-source.lock.json` 的122个固定文件摘要均匹配，见`source-lock-check.json`。这不代表整个当前工作树干净或迁移后完整固件已重资格。适配器 `_backend()` 要求HEAD匹配且`git status --porcelain --ignore-submodules=all`为空；当前固件AGENTS/README迁移改动使干净条件不满足。未执行适配器入口，因为其main在后端检查前会调用`restore_mu_baseline.py`。
- 新目录内直接编译并运行既有生产C回归：journal、protocol-on、protocol-fail、8秒事务、独立格式反读；均启用ASan/UBSan。96页/2359296像素、64位status和环回后最近point13、单像素损坏拒绝通过；8秒事务覆盖24通道布局/960读写故障边界及屏障、复核、保持失败。严格三行转录3组测试通过。共11条编译/运行命令及输入摘要见`host-checks.json`，运行器`run_checks.py`同目录保留。测试自身stdout的历史“live-status”措辞不能改变缓存页含义。

Windows `python` 为商店占位入口，本轮用WSL Python 3.10.12和`/usr/bin/clang`。重跑证据审计示例（输出必须换一个未存在的名称）：

```powershell
wsl --exec python3 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/audit_migrated_log_evidence.py --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/migration-log-audit-next/bindings.json
```

旧`audit_console_readiness.py`、`check_cached_log_format.py`、`check_log_replay.py`和`test_boot_journal.py`会写固定报告或旧测试目录，本轮不直接执行这些入口；直接调用既有测试和纯解析函数，输出另存。不以新主机执行结果覆盖原资格。没有执行完整FD、Arm对象、QEMU、设备或媒体可读性测试，本轮这些项不写通过。

## 失败路径、证据含义及菜单依赖

| 路径 | 复核事实 | 剩余边界 |
|---|---|---|
| Core发布 | attempted先置位，安装失败不重试；失败回归通过，RAM追加继续 | 屏幕可能因无协议而拒绝；不能把无日志当无DXE事件 |
| provider快照 | Native6/requirements22、WT/EL1、服务/ABI/callback与point13页全部成功才进入事务；失败return1 | 复合拒绝码不能唯一定位依赖失败；完整调用入口未作主机端到端仿真 |
| 日志选择 | 最近已完成point13；调用provider内取快照，当前provider的Core返回记录尚未产生 | 不显示GUID/sequence/启动ID；无法独立归因当前驱动；ordinal不是唯一事件ID |
| 保存/绘制 | save或revalidate失败前无store；首个write尝试后完整restore/readback；pattern/hold失败分别2/3 | 原读取内容须有效；复位/CPU异常不会自动走C恢复代码；回调模拟不证明真实硬件 |
| restore失败 | 任一恢复写/屏障/读回失败返回4；恢复循环不因中途错误提前结束 | 硬停码优先，不能按“已尝试恢复”宣布恢复完成；75秒规则保持 |
| DEBUG / ConOut | 六模块链接列表仍绑定Null SerialPortLib；Print和DiagDraw独立；早停在BDS前 | 需要单独实现/资格/运行证据，不从缓存页成功升级 |
| 正式GOP / 菜单 | requirements22、alpha/SMMU仍未闭合；BDS控制台连接在AfterConsole前，可能SetMode/清屏；UniXNU先driver再Ui/Menu | 不能为菜单直接解除早停或清22；菜单画面、输入选择/取消、超时/返回分别验收 |

主判断保持：先获得清晰、可逐字转录的真实缓存返回，才有可用错误内容推进归因；当前离线没有新证据支持改字体/扩面积或重做固定字母点屏。完整日志的可追溯性仍缺GUID/sequence/启动绑定；若以后设计新页面，须新版本/范围另资格，不覆盖R-022。现有全局DEBUG、ConOut和正式GOP依赖不能用菜单编译成功跳过。

后续现场仍需用户对R-022精确单次放行、文档/批准记录按当时指令完成发布门、新鲜身份/匹配备份/恢复/时钟和当前人手拍摄确认。当前禁止自动提交推送，未准备发布也不启动设备。晚间可用不触发自动动作；不泛问恢复，无当前恢复按键欠项。原始影音仅本地out/，不上传、不录音。所有verified、内存字段及分区边界保持。
