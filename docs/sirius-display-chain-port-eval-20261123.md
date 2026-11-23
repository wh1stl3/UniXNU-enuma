# sirius 显示链移植评估（2026-11-23）

结论：不移植整条链。两板已有同类 GOP/Legacy/CPU-copy 结构；先定位客户端为何未到达，再在获授权且审查之后考虑默认关闭的一次性像素自检。本次仅离线静态对照，未构建、未上机，`self-checked`。

## 来源与边界

`S` = `HuajiFruit/UniXNU-sirius@ac0c900485f3c0cd18de9707579a1cdcd3365503`（本地 `.cache/ref-sirius`）；`E` = 本仓历史候选 `out/enuma-gop-legacy-20261114-r2`；`E-core` = 该候选的 `build-r2/source/NativeLegacyDisplay.cpp`。`out/` 是本地忽略产物，非可发布源；与 r28 实际链接对象是否逐字节相同未在本次核实。S 仓许可见其 `LICENSE`，显示核心源码头标 BSD-2-Clause-Patent；此处只分析、没有复制代码。两板都以 iPad7,1 21H461 为 donor 不代表 provider/启动链可直接互换。

| 层 | sirius 文件:行 | enuma 对应与状态 |
|---|---|---|
| framebuffer 来源 | `S:package/LegacyDisplayProbe.cpp:590-605` 加载 IOSurface、等待 root，`PE_current_console` 取固件 GOP，检查尺寸、格式与步长 | **已有等价物**：`E:package/EnumaLegacyDisplay.cpp:28-32,76-85`；另检查 `v_display==1`。 |
| nub/设备树 | `S:package/LegacyDisplayProbe.cpp:605-628` 创建 `IOPlatformDevice`、GOP memory，挂 resource、phase 4 挂 `/arm-io` 的 `display-subsystem` | **已有，细节不同**：`E:package/EnumaLegacyDisplay.cpp:84-105` 同类 nub，强制 DT 成功而非 phase 4 条件。 |
| Legacy 对象和发布 | `S:package/LegacyDisplayProbe.cpp:505-...` 预置对象；`:647-665` probe→attach→start，无该路径显式 register；`S:drivers/GopFramebuffer/NativeLegacyDisplay.cpp:290-296,326-334` start 和注册 override。不能由调用点无显式 register 推断运行时没有被父类间接注册。 | **实现不同**：`E:package/EnumaLegacyDisplay.cpp:44-61,103-116` attach→probe→start→显式 register；`E-core:510-517` 门控注册。r28 两个 type 0 opener 的 override 返回 0，是观察窗的成功返回，不证明 compositor 就绪。 |
| surface 接口/请求 | `S:package/LegacyDisplayProbe.cpp:590-593` IOSurface root；`S:drivers/GopFramebuffer/NativeLegacyDisplay.cpp:573-624,644-647` 原家族 user client、校验单层全屏 IOSurface；`:407-419` 取 descriptor、宽高格式步长 | **已有等价物**：`E:package/EnumaLegacyDisplay.cpp:80-83`、`E-core:595-605,756-...`。这里只确认候选实现，不证明该 OS 上每种调用/格式均受支持，也不证明已收到 surface。 |
| 映射和 CPU 拷贝 | `S:drivers/GopFramebuffer/NativeLegacyDisplay.cpp:649-677` 映射 GOP；`:368-372,407-419,487-523` 已验证请求后准备 scanout、CPU 按行拷贝、barrier、完成 | **已有等价物**：`E-core:541-572,595-605,658-... ,680-... ,833-...`；`E:package/EnumaLegacyDisplay.cpp:150-162` 交出控制台并拒绝 GPU offer。实际 mapping/cache 策略以各候选为准，不能照搬板值。 |
| 刷新 / 完成 | `S:drivers/GopFramebuffer/NativeLegacyDisplay.cpp:220-... ,239-... ,545-565` 可选 timer vsync、完成并 retire；GOP 由固件既有显示路径扫描，不是软件调用一次硬件 flip；`:573-624` 先有合法 swap。 | **已有等价物**：`E-core:390-... ,409-... ,541-572,718-...`，门控下执行；`E:package/EnumaLegacyDisplay.cpp:150-159` 的 `prepare_scanout` 是释放控制台，不是启动显示控制器或产生 vblank。真实硬件 scanout 和像素尚未验证。 |

定位使用 `...` 指该函数后续范围，不表示版本间行号相同；`S` 与 `E-core` 是不同 revision，不把当前 UniXNU 主线代码替代候选。

## 能解决什么

sirius 报告已到可触摸 Setup，其作者记录包含成功 swap 和 CPU copy；见 `docs/sirius-path-to-setup-20261123.md:7-17,25-33`。这说明该组合在 sirius 可用，不证明其 provider 次序是客户端开始提交的原因。r28 的 `refresh=kick=scanout=swap=0` 仅表明板级对应观察点未命中；`swap=0` 不能区分根本未提交和到达该点前被拒，见 `docs/enuma-r28-device-20261123.md:37-42`。r29 的 backboardd 分派观察也仅限窗口，见 `docs/enuma-r29-device-20261123.md:11`。

**不能声称移植解决无客户端提交 surface**：CPU 拷贝位于请求校验之后，不产生用户态 compositor、surface 或 swap。若只替换后端而上游状态不变，预计仍无像素，swap/copy 仍为 0；注册、open 或 refresh/kick 计数可能因路径变化而变化，但没有必然变化，kick 本身也不是 swap 证据。对 probe/attach 顺序、显式注册或属性做隔离实验可能改变匹配，但现无因果证据，不能预言 opener 或 swap 改善。

## 代价、风险和替代

* 完整替换：预计 **中到大，约 3–6 个文件、数百行**（设备 provider、GOP 组件/绑定、构建选择、观察/测试及记录；具体依最终 revision 和 ABI 而变）。不是仅改一处 10 行；涉及受限原始 ABI、console 生命周期及服务发布。S 含板级 WC、面板和诊断分支，不能跨板复制。若改驱动初始化或启动链接线须按项目规则专项派发及 deep 审查；保留已有冻结 GOP 包，不能直接修改只读 UniXNU。
* 即使只改 `E` 对应 provider 的调用顺序/注册，约 1–2 个代码文件、10–40 行加测试/记录，也可能破坏已观察到的服务发布及两个 opener，或产生重复注册/不同匹配；不以 sirius 无显式调用作为删除注册的依据。新实验默认关闭、boot-arg 门控，并保证关闭时原路径逐项不变；诊断不能进入默认 recipe。
* 更小：在**不替换 provider**前提下，设计一次性、默认关闭的受控 GOP 测试图案：使用已验证映射及实际 `PE_Video` 格式/stride/范围，先确认安全的控制台交接、唯一写者及缓存可见性，再 CPU 填充有辨识度的小色块并做所需屏障；记录独立 attempt/result，人工记录图案是否稳定可见。GOP 既有扫描不需虚构“scanout API”或硬件 flip。屏幕仍用于日志/BootProgress 时不得并发覆盖；控制台释放可能中断日志，须先设计恢复/观测与审查，另获设备授权。预计 1–2 个代码文件、约 30–100 行加测试/记录；具体位置待选定并核对实际链接版本。
* 自检的成功仅证明当次被选区域 CPU 写入及可见显示路径，**不验证** IOSurface、用户客户端、swap、retire、面板 vblank、GPU 或一般同步；失败也不能区分映射、缓存、所有权、面板或其它覆盖。自检计数与真实 swap/copy 计数必须分开，不伪造 swap。直接填充测试没有经过 Legacy surface copy，所以不能说验证了整条显示链。

## 建议顺序及判据

1. 保持现有 provider；先用已有 r28/r29 观察边界继续追 compositor 启动、匹配与在校验前的返回路径，避免把未命中当作全局无提交。判据：找到首个明确失败/等待点或实际 swap 入口；没有则只报告未定位。
2. 若需要独立验证物理像素，先完成上述一次性自检设计与审查、重新获设备动作授权；判据为独立 attempt/result 与可辨识色块同次一致，且不虚增 swap。无图案仅记失败而非归因。
3. 仅若出现已验证 swap 而 CPU 拷贝/格式不匹配，按具体差异小范围复用 sirius 的算法，先核 ABI、许可证和原版来源、做默认关闭门控及回归，再考虑接入。无真实 swap 时先移植复制后端不能消除当前上游阻塞。
