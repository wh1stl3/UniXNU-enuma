> **2026-10-28 当前：** [far-chain-v7镜像与资格](docs/operations/2026-10-27-oem-far-chain-v7.md)已完成，未claim/上机。OEM期间只记RAM，真实返回后继续DXE，整轮分派完成才输出一张汇总，仍在BDS前恢复。旧v6已消费，旧拍摄就绪不复用；以下旧“当前/未上机”文字按历史阅读。现行STATUS/HANDOFF。

> **2026-10-27 最新：** v6已单次消费，原厂主入口ChipInfo查询前E01已人工确认，用户无操作自行回Android且独立核验通过；原始查询/方法/SID/Core返回仍未证实。无人工欠项，不重试v6，现行状态见STATUS/HANDOFF。以下构建/未上机表述保留为历史。

> **2026-10-27 当前入口：** [STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[main-entry-v6分析与镜像](docs/operations/2026-10-27-oem-main-entry-v6.md)。新v6完整固件/Boot header v3镜像与离线资格已完成，未上机；v5两页确认真实配置安装返回EFI_SUCCESS，已consumed并恢复Android。共享主线只读、R027冻结，本轮不继承旧拍摄就绪。
>
> 以下按历史记录阅读，不以旧“当前”段落覆盖上述入口。

> **D-323 当前入口：** [交接](docs/HANDOFF.md)、[DisplayDxe 接续 prompt](docs/2026-10-27-displaydxe-handoff-prompt.md)。实机暂停；追踪组件离线验证通过，尚未接入原厂驱动。以下旧进度按历史阅读。

# UniXNU-enuma

<!-- path-migration-policy-2026-10-26 -->
> **2026-10-26路径迁移：** 后续工作、新文档、脚本调用示例与交接统一使用 `D:/Code/PortingiOS/enuma` 下的本机型新仓库路径，不与另一机型混用。仓库位置、旧资料库及历史证据定位见[统一迁移索引](../../PATH-MIGRATION.md)；旧记录不构成当前路径或新验证结论。

小米平板5 Pro 5G / SM8250-AC的iPadOS17.7.11移植。当前主线按用户D-170要求：准备尽可能完整的启动链，采集实际报错并逐轮修复；单点早停仅作必要备用。

D-284，S-047固定UEFI文字可见且设备已恢复Android；按授权安全交接结束旧会话写入。接续直接推进UEFI固件开发与真实日志，不重复字形验证。R-019 consumed，不重试。R-018 consumed，不重试。只读前置用ADB/fastboot和时序，无相机；可见输出试验再用摄像头。详见[当前状态](docs/STATUS.md)。原始影音仅本地。

接手读[AGENTS](AGENTS.md)、[STATUS](docs/STATUS.md)、[HANDOFF](docs/HANDOFF.md)、[完整链路线](docs/operations/2026-10-25-full-boot-mainline.md)、[ADT/FAT进展](docs/operations/2026-10-25-full-adt-fat.md)、[boot v3运输](docs/operations/2026-10-25-boot-v3-payload-transport.md)、[S-001试启动](docs/operations/2026-10-25-system-transport-trial.md)、[S-002隔离方案](docs/operations/2026-10-25-display-thread-off.md)、[返回边界候选](docs/operations/2026-10-25-full-input-return-boundary.md)及[交接词](docs/2026-10-25-handoff-prompt.md)。所有内存/verified/设备恢复和破坏性分区门禁保持，源码pin不自动更新，参考仓只读，原始产物仅out/。

远端：[设备仓](https://github.com/wh1stl3/UniXNU-enuma)、[固件仓](https://github.com/wh1stl3/uefi-enuma)。

S-045已完成且consumed，最近独立核验恢复Android；R-018已由S-046执行并consumed，详见STATUS/HANDOFF与NEED-REVIEW。


### D-298 当前进度

完整开发 FD/Boot v3 已编译和离线核验，保留 BDS 前停点；下一录像候选仍是冻结 R-022 的 8 秒真实日志页，尚待精确单次放行和当前拍摄确认。无自动提交推送或实机部署。见 [当前交接](docs/HANDOFF.md) 与 [D-298 构建及准备](docs/operations/2026-10-26-development-fd-and-r022-preparation.md)。


## D-299：R-022单次放行与录像前预检

R-022单次已放行，enuma只读预检通过，等待当前录像开始确认；未发送镜像。见 docs/operations/2026-10-26-r022-preissue.md。


## D-300：S-050数值可读、圆角遮挡与停止追加

S-050完成并恢复Android。真实日志ordinal31/status0可读，圆角遮住页标使完整页面未通过；R-022已消耗，停止追加实机，继续离线分析。当前入口docs/HANDOFF.md。


## D-301：内缩归因真实日志新候选

2026-10-26，用户要求准备下一次并尽可能推进。已完成R023 replay2五行/320×160/(64,96)/8秒和严格GUID序号归因、失败测试、完整FD/FAT/Boot v3及实际PE审查；镜像360b5ec7eeb26f76858069fba78d3f69bbe90d40f125730dfcd324dbe69fbd8a。R023 pending/计划S051未发图；新原子claim/本地绑定，不复用R022或旧录像确认。最后设备证据S050 Android恢复，本轮纯离线；不提交推送，保留迁移/冻结产物/媒体，requirements22与GOP/DEBUG/菜单未提升。详见docs/operations/2026-10-26-r023-attributed-inset-log.md。


## D-302：R-023单次放行及当前录像就绪

2026-10-26T12:41:22.383347+00:00，用户明确“录像就绪 开始推送”，仅镜像360b5ec7eeb26f76858069fba78d3f69bbe90d40f125730dfcd324dbe69fbd8a一次S051临时boot。R023 approved，当前人工拍摄就绪；即时身份/备份/恢复/时钟门由原guarded runner核验，未发图前不称通过。不得自动重试，旧consumed不变，无Git推送/分区刷写。执行证据入口out/r023-live-20261026。


## D-303：S051已恢复，内容待用户核对

R023一次已consumed，20:41:44发图，Android65.062秒，原点40.729..40.802唯一code5；20:42:57独立恢复通过。原始照片五行在屏内；用户要求人工逐字核对，独立判读已保存且未查询GUID目录，当前全文验收pending，不追加实机、不提交推送。证据reports/enuma-native-route-S-051-result.json与out/r023-live-20261026/postcheck.json。


## D-304：S051内容交叉核对及I2C归因

用户提供五行人工转录，与此前独立保存的助手判读按字段上下文/hex大小写规范化后逐字一致：ordinal31、status0、sequence185、GUID04de8591-d2b3-4077-bbbe-b12070094eb6。绑定本镜像实际PE目录唯一I2C；仅证明此前I2C StartImage返回EFI_SUCCESS，不证明总线/外设功能。照片中五行完整避开圆角；S/5、O/0字形相同确有辨识缺陷，依靠标签位置区分，后续新候选改善，不覆盖冻结图。原S051结果报告保存当时pending事实；新证据reports/enuma-s051-visible-log.json关闭人工核对项。R023已consumed，不再启动，无新实机授权、无提交推送。


## D-305：诊断日志与菜单前控制台的新完整构建

2026-10-26，用户要求继续直到编译下一版。replay3故障优先归因/25独立字形、有界129行ConOut回放/首错锁存及DSC宏传递已实现；主机/ARM/QEMU真实菜单链和独立晚期Probe PE链接通过。完整FD 1179eb69f81f303c0fd6012b3aaa7597aed589366a4dc88462391a389f44d2b7，Boot v3 e789df474e05e4de37f329cc4a1dd623cb1975ede0ae48b134bcf866db9f2969。完整诊断FD保留EFI_UNSUPPORTED Probe安全入口，晚期代码只在独立console-link2模块中链接，不能混为实机菜单镜像。build1/2失败保留，build3成功。证据reports/enuma-diagnostic-log-development.json、out/diagnostic-log-20261026及docs/operations/2026-10-26-diagnostic-log-and-console-drain.md。R024仅离线未批准，无设备动作、提交推送或verified/requirements提升；旧冻结/消费证据及媒体未改。设备HEAD89b609e、固件基线8680ea7，实际源以新manifest为准。


## D-306：R024单次批准与录像就绪，S052尚未发图

用户明确“批准实机 录像已就绪”，仅D305镜像e789df474e05e4de37f329cc4a1dd623cb1975ede0ae48b134bcf866db9f2969一次临时boot，内缩(64,96)/320×160/8秒、replay3真实完成返回，仍不进正式GOP/ConOut/菜单。独立execution1元数据派生保持镜像原字节；execution-review和新R024一次性runner测试通过。S052未claim/未发图，立即执行门仍核对enuma身份/root/A槽/解锁/备份/时钟，异常停止追加并恢复。旧consumed保持，不提交推送；本地manifest绑定当前文档与脚本。执行证据out/r024-live-20261026；媒体目录D:/Code/PortingiOS/enuma/Media-enuma/S-052-R024。


## D-307：S052真实日志核对完成与固定人工校验流程

R024已单次消费，21:56:12发图，Android66.234秒，原点40.761..40.818唯一code5；21:58:12独立恢复通过。用户“能对上”确认助手先保存后展示的五行，随后查本镜像目录归因I2C StartImage返回EFI_SUCCESS（ordinal31/sequence185/GUID04de8591-d2b3-4077-bbbe-b12070094eb6）。新字形/完整页面本图可读，不称全部字形/8秒持续或正式GOP/ConOut/DEBUG/菜单通过；requirements22不清。证据reports/enuma-native-route-S-052-result.json、reports/enuma-s052-visible-log.json、out/r024-live-20261026。用户“以后都这样校验”：助手先独立读图落盘→展示五行→用户确认/纠正→精确镜像目录归因；不确定写?，不补猜，不再要求用户先盲抄。媒体本地、旧消费不复活，无追加启动/提交推送。


当前入口（D-320）：[交接](docs/HANDOFF.md)、[R027后置菜单实现与资格](docs/operations/2026-10-27-deferred-menu-firmware.md)。新候选离线完成，实际连接/本次录像/单次放行待满足；R026/S054已消费，不自动推送。
