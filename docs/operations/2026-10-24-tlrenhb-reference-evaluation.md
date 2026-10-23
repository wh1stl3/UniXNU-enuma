# Tlrenhb/UniXNU-enuma 参考评估

只读评估固定提交 `b5e9984d07bfbdd9a1b3311e0658c0b61a5288fe`，14份相关文件摘要及最近CI元数据见 `reports/enuma-tlrenhb-reference-audit.json`。未执行对方脚本或导入其板级参数。

结论：作为研究来源保留，当前不切换 Boot v1、不替换本仓固件与显示探针主线。

对方 board.toml 明示 Boot v1 参数来自 umi/pipa；这些是参考机来源，不能替代本设备的启动格式资格。本仓 Boot v3 已有多轮 enuma 临时启动、受控返回与 Android/root/原分区核验。当前没有 ABL 拒收或头部解析失败证据，也没有证据把显示故障归因于 v3。只有出现格式相关失败，或可对照的 enuma v1 显示实测与明确因果依据，才值得另做受控 A/B；不得同时移植内存地址、大小或分区参数。

Boot v3被接受并不等于持续显示交接正确。对方同时使用显式DTB输入并讨论cont_splash保留区；本仓v3包保留原vendor_boot而不附加/重写DTB。这是应单独核对的输入路径差异，不能只凭头版本判定等价或归因。保存的Android FDT/保留区仅代表Android阶段，尚需核对ABL到UEFI时实际传入DT及显示状态；若证据指向DTB或持续显示交接，应先设计隔离变量的比较，再决定是否需要v1载体。

对方 build-enuma-uefi.sh 自称 skeleton，仍有日志读取和集成 TODO；当前 device checks 工作流涵盖板级解析、离线预检、脚本语法和 DTS 编译/摘要，并明确不编译内核。CI绿色不能当作内核或显示实机通过。README与measurements/provenance处于不同准备阶段；本次未独立验证匹配的内核/prelink产物。所审文件中未找到可替代当前早期显示门禁的 enuma 实测闭环。

值得继续审阅的部分包括 ADT、原始 trust member 工具、内核 archive/prelink 方式、panic 文本排版和 umi/cas 同 SoC 来源索引。须分别核对精确上游版本、输入、ABI、许可和板级差异后复用。panic patch 脚本含硬编码 Mach-O 地址并假设 framebuffer 可用；PMGR ABI桥与空显示 probe hook 不等于真实显示/时钟驱动，不能直接应用。

本轮仍完成 DSI 计数配置与有界增量只读探针。即使计数推进成立，也不证明当前 SSPP 路由、目标 buffer 的物理/IOVA关系、面板背光或可见写屏；菜单还需要可见像素闭环、文本后端和 DXE/BDS 继续执行。

来源：[固定 board.toml](https://github.com/Tlrenhb/UniXNU-enuma/blob/b5e9984d07bfbdd9a1b3311e0658c0b61a5288fe/board.toml)、[工作流](https://github.com/Tlrenhb/UniXNU-enuma/blob/b5e9984d07bfbdd9a1b3311e0658c0b61a5288fe/.github/workflows/checks.yml)、[固件轮次脚本](https://github.com/Tlrenhb/UniXNU-enuma/blob/b5e9984d07bfbdd9a1b3311e0658c0b61a5288fe/scripts/build-enuma-uefi.sh)。
