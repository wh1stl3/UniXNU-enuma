# D-295：真实日志归因文本、ConOut回放与菜单文本依赖代码

2026-10-26，Asia/Shanghai。按用户“继续离线推进、优先落代码”实施；没有设备、相机、提交推送、固件FD构建、重包或旧staging恢复。新源码属于未资格开发工作树；不代表R-022来源变更或实机通过。接手HEAD仍设备89b609e/实际固件子模块8680ea7，独立uefi-enuma未改。

## 已实现的行为

`firmware/diagnostics/EnumaBootJournalView.h` 是v1快照的新增归因文本视图。原`EnumaBootJournal.h`、私有协议结构/GUID、`PixelLogPage.h`及R-022三行页面均不改。

- 首行标明cached、dropped、next；后续每行保留完整64位sequence/status、32位ordinal/point及canonical GUID。GUID前3个字段按EFI内存LE字节正确转换，不再要求人工从原`g=`内存字节反推UUID。
- point13=start-return、14=load-return、21=entry-return、22=after-exit保留收到的真实状态；15=before-start、20=before-entry明确输出`not-returned`，其他checkpoint输出`not-a-return`，不会把到达调用前的占位SUCCESS当作返回成功。
- 验证快照计数、loss/next关系、连续sequence、GUID存在标记；坏快照在sink调用前拒绝。一调用至多一行，cursor只在sink接受后推进；仍是单writer静止快照、非AP/异常logger，没有新增共享物理RAM或写协议。

`scripts/decode_dxe_journal.py` 严格解码该格式，校验完整序列和语义。可用显式`--inf`绑定canonical GUID到BASE_NAME、来源路径及INF原字节SHA256，重复GUID保留多个候选，不擅自选一个。输出记录transcript摘要；没有启动ID时不伪造。按同GUID前后顺序显示`preceding_start_sequence`；若多个未闭合start则明确ambiguous；当前尚未返回的start单列`unclosed_before_start`。这不是跨启动配对或挂死证明，前一驱动return不会冒充当前provider返回。INF名称只绑定源码元数据，不证明该PE已打包或执行。

`firmware/diagnostics/EnumaJournalConsole.h` 提供真正的晚期ConOut消费者：

- 校验v1/Bytes/callback及现有OutputString后才取快照，调用方提供独立workspace；失败保留具体EFI_STATUS。
- 使用固定CHAR16缓冲，将每行ASCII及最后LF转换为一次CRLF OutputString；拒绝中途控制字符、不完整行和超限输入，避免UefiLib Print内部隐式缓冲/接收端选择。
- error及warning（包括unknown glyph）均不算完整接受；cursor不推进，不自动重试。OutputString失败时可能已输出部分/整行，不能宣称exactly once。普通Probe行也使用有界`EnumaConsoleWriteLine`并返回实际status。
- 不连接驱动、不切模式、不清屏、不回退raw像素、不接全局DEBUG。OutputString仍可由真实控制台驱动写屏，绝不是“无像素操作”的实机权限例外。

`EnumaProbe.c` 的Line改为仅调用上述ConOut入口，移除Print+DiagDraw双写和对原始帧缓冲的cache flush，INF移除CacheMaintenanceLib。`enuma_preflight.py` 的纯函数`probe_memory_helpers()`只从固定DarwinBoot提取GetMap/RunEnd，不再把旧DiagDraw/字体/直接Fb[]写入代码带到EnumaProbe。prepare会把新增日志/控制台头复制到Probe自己的staging；本轮没有调用prepare或改动原staging。

真实Probe已接入`ReplayJournal()`：定位原私有协议→取得静止快照→有界最多129行归因回放→检查结果→菜单前置→原UniXNURun入口。`ENUMA_PROBE_JOURNAL_REPLAY`默认0，仅允许0/1；测试显式开启，未给固件构建器增加自动启用开关。回放失败/警告直接返回，不循环重试、不用菜单覆盖故障。当前实现没有分页/读屏暂停，不声称快速完整回放的129行都可由人眼读清。

`firmware/diagnostics/EnumaMenuConsole.h` 已接入真实菜单调用前：对存在的ConOut核对Mode、当前mode索引、QueryMode及Ui文本路径实际使用的OutputString/SetAttribute/SetCursorPosition/ClearScreen/EnableCursor。Columns>=2、Rows>=8才接受，阻止文本列减1及footer减行在不合格几何下进入UI。QueryMode警告/错误原样返回。检查本身仅QueryMode，不执行绘制或模式变更。

ConOut不存在不单独阻止原GOP/headless路线；但“存在且不完整”的ConOut保守地阻止进入菜单，即使某个纯图形配置可能绕过文本。这是当前wrapper的明确取舍：它尚未读取UniXNU配置，不能提前知道是否会走文本回退。没有改写只读UniXNU上游Ui/Menu代码，不能称已经修复其所有GOP、布局、配置或输入问题。

## 离线验证

最终证据`out/journal-console-dev-20261026/run4/result.json`：17项命令执行通过，命令、stdout/stderr、源码摘要和栈文件完整保留。

1. 真实新C formatter/console sink采用固定Mu的真实X64 UEFI类型，在ASan/UBSan下运行。正确canonical GUID/阶段/full64状态、128条环回、当前未闭合start、损坏序列/loss/计数/HasGuid拒绝通过；ConOut缺失/ABI错/取快照失败、error/warning/已部分输出、CRLF、行长度及不自动重试通过。
2. 菜单文本前置的空/缺回调、无效mode、QueryMode错误/警告、0/1列及0/7行拒绝，2×8最小几何接受；未调用模式/属性/光标/清屏/输出函数。这是软件回调验证，不是实际2×8可用菜单布局结论。
3. C实际输出→严格Python归因解码端到端通过（6事件及128事件环回）；合成INF映射绑定真实Probe INF摘要。4组decoder单测覆盖当前provider与此前return区分、缺行/重排/伪造状态拒绝、空快照/loss、重复GUID及伪造INF字段拒绝。
4. 编译真实`EnumaProbe.c` AArch64对象：回放0、回放1、RAM payload+回放1三个分支，真实固定EDK头及固定DarwinBoot派生内存helper。栈报告分别688/1120/1104字节，静态快照位于BSS；不是完整链接栈预算。nm确认三对象仍依赖UniXNURun且无DiagDraw/WriteBackDataCacheRange依赖。非法selector=2编译拒绝。
5. 旧journal 10000事件及原8秒事务24通道/960读写故障边界回归通过；原三行转录3组测试通过。未覆盖本轮新FD、QEMU、全局DEBUG、实际ConOut或菜单输入/超时/返回。

开发中run1通过较早集合；run2因新测试用了错误EDK类型别名编译失败，改为实际`EFI_SIMPLE_TEXT_OUTPUT_MODE`后run3通过；最终新增兼容及对象检查的run4全通过。旧结果未覆盖，失败不记通过。最初PowerShell裸传逗号形式的sanitizer参数在shell解析阶段拒绝，未运行clang；最终入口统一由Python argv调用。

重现（必须新建输出目录，不覆盖旧证据）：

```powershell
wsl --exec python3 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/test_journal_console.py --output /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/journal-console-next/run1
wsl --exec python3 /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/scripts/decode_dxe_journal.py --transcript /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/out/journal-console-dev-20261026/run4/transcript.txt --inf /mnt/d/Code/PortingiOS/enuma/UniXNU-enuma/firmware/Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.inf
```

第二条使用**合成测试**transcript；GUID不匹配该INF时不填driver_source，不是本机运行值。`synthetic-catalog.json`才是刻意替换GUID后验证映射的合成结果，不能当真实Probe日志。

## 资格、冻结及下一步

这次改动实际改变3份已锁定固件源：EnumaProbe.c、EnumaProbe.inf、enuma_preflight.py，新增3个固件头。旧device source lock/firmware migration/extensions摘要不改、不伪装匹配；完整构建前必须为新开发源形成独立提交/锁及metadata资格。当前用户禁止自动提交推送，且工作树脏，不运行适配器、source-lock同步或官方构建，更不修改R-022资格。旧console-readiness源绑定中的Probe行/摘要现应明确视为历史，不拿它证明新代码；新代码以run4源摘要为准。

R-022镜像`f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b`及完整冻结归档、原报告/审批配置保留。R-022仍pending、S-050未执行，S-001..049/R-020/R-021消费不变；没有新R编号、没有新执行资格。当前没有恢复按键待办。

收尾`out/journal-console-dev-20261026/preservation-final.json`确认：467份报告/配置/归档无摘要变化，镜像摘要不变，run4全部源绑定与最终代码一致，33份既有设备仓迁移脏文件与原副本逐字节相同，WORKLOG/DECISIONS保留接手前字节前缀。源码锁漂移精确为上述3份已修改源；没有更新旧锁来掩盖开发状态。所有本轮检查进程已完成。

已解决的是**可归因日志格式、真实ConOut消费者及wrapper文本依赖保护**；还没有解决正式GOP准入、BDS控制台连接、全局DEBUG共享后端、128条上屏分页或菜单输入/受控返回。要求22/alpha/SMMU/verified保持。新消费者依赖一个已经正确连接的晚期ConOut，不调用ConnectAll来绕过准入。后续先在新开发资格下形成完整构建和可保存/分页的日志显示方案，实机仍等用户另行放行；不能把当前源码或晚间可用当作R-022执行批准。
