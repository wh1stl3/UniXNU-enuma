# 当前进度：DSI计数只读探针已实现并完成构建审计

2026-10-24 Asia/Shanghai。用户要求实现DSI计数使能及有界计数增量只读探针，完成构建审计并落实所有文档后直接实机验证；用户可在场恢复，按需摄像。每笔前提交推送全部当前文档、即时设备门禁及超时停止追加规则保持，无新增逐笔审批要求。

## 当前软件与范围

固件f6c59badf5ee22f1720f22124a97384ad9739c15，设备gitlink及63项源锁固定。R-004已有映射内使用DSI基址0xae6b800/0xae6c000。step15各读TIMING_ENGINE_EN(+0)及FRAME_LINE_COUNT_EN(+0xa8)，共4读；至少一接口timing非零且enable低两位为3才成功。未符合则EFI_NOT_READY，不写使能。

step16先做同样前置，仅采样符合接口FRAME_COUNT(+0xac)，调用已有gBS->Stall一次100000微秒，再采样及复核原timing/enable字完全不变；最多12读。所有符合接口的UINT32模差不超过64且至少一个为1..64才成功；无符合接口、全部不动、异常差值、配置改变、等待异常均拒绝。非原子快照不能排除瞬变，近回绕复位可模拟进展；拒绝不等于管线不活动。支持结果也不证明当前SSPP路由、buffer物理/IOVA、面板背光或可见输出。

33项fake MMIO/wait用例在O1/Oz及ASan/UBSan通过，包含精确读序/上限、禁用不采样、不推进、1/64/65边界、回绕/复位、配置变化、等待错误/警告、null。真实AArch64对象仅既有gBS外部依赖；GOP补丁组合240项及真实Mu传输回归通过，非法像素组合拒绝。五份完整固件、补丁回退、30个OEM PE/DEPEX、AutoGen/库依赖、实际FD、192字节BootShim/3MiB FD/Boot v3及同源宏差异完成离线资格；这些不是硬件执行证明。实际代码审计细节以各FD报告及bundle为准。

| 候选 | step/query | Boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- | --- |
| counter-control | 14/1 | `5f75763ae804b976765e2d81655f17e31c3fb9bf142824ae5b4c7b087b42028c` | `a8d6dd93bdf7e5596a74e6b1897b58d41115cd381b26dabbde2b5c576eb473a1` |
| counter-ready | 15/1 | `09f5a287791ab2a4b1c6b9e539b66ae28e72116f246fbc5a8aa9c86046d9b327` | `95a7acc1fc69d01ec0059ee37a8a0e4d6d18c97553e9a97e9bfcda61808f921e` |
| counter-not-ready | 15/2 | `4458d6d6c7f4d8f7e5a657b209975b97eea021da1c2835767620fd5e7c8685fc` | `21dd82ad4e0a0121c007fcd461f73c42f645c32ae79812dab7795bc564676601` |
| counter-progress | 16/1 | `467fa418d6615b59af8cccf32a8e29b77c948a3389abb4198b90d9369be6c321` | `f032ee89e3cb8216ccc6306fc2eca36b92a81d037ebf32f83939dbaf56a5f1ef` |
| counter-no-progress | 16/2 | `36ad981a3f40c12b77f186c41a24f76523660103c64fccfcf267763090c3b508` | `23d217567393dbfd2cd98f7b6beaccda64b7121d46c87163923bdc1cf4e62702` |

同源step14/query1作为时序基线，随后step15及step16分别query1/query2。query1接非错误标记，query2接错误标记，命中后Core延时2秒；未命中走7秒同步完成兜底，非watchdog。互补时序仅分类谓词分支，不能当寄存器数值日志。若step15拒绝，step16仍为相同前置受限只读，拒绝归为条件不足而非不活动。

## 最新设备结果

尚未执行本轮 f6c59ba 新候选。最近实际设备为旧338db59 step14正/互补均无按键返回Android/root/原槽/解锁/原摘要通过；ADB15.906/22.281秒支持至少一接口时序使能非零，尚非数值或活动显示证明。

本轮互补结果尚未齐备，计数配置及进展谓词未判定。

## 下一步、恢复和限制

先对齐提交推送全部当前文档，再即时核验身份/备份/恢复并临时启动 counter-control；逐笔受控返回和恢复核验后再推进。

只读采用必要前后截图和主机日志/时序，实际设备输出、判读变化或恢复时再录像。白点是用户键盘反光，不能记为显示成功。Android/fastboot恢复已有证据，TWRP/UART未验证；无返回即停追加、先恢复，当轮落实STATUS/HANDOFF/WORKLOG/DECISIONS及审核/人工状态，恢复核验后继续离线分析和新软件，不原样重试失败镜像。

R-005保持consumed，不重放像素实验；无像素访问、显示或计数MMIO写入、新映射、内存大小/基址及verified变更，不flash/erase/改槽。51MiB heap、512MiB owned、example=true保持。尚未确认可见写屏，未进入XNU，文本后端尚未集成，菜单仍需可见像素闭环和DXE/BDS继续执行。

Tlrenhb参考仓固定b5e9984评估见operations/2026-10-24-tlrenhb-reference-evaluation.md及reports/enuma-tlrenhb-reference-audit.json。可审阅ADT/trust/prelink及同SoC来源；其Boot v1取自umi/pipa，当前未找到enuma格式/显示因果证据，本仓保留已受控实测的Boot v3。不得借用其4GiB owned或板级布局。

用户要求结合公开资料更明确判断；当前首查“第一个合法SSPP并非活动路由”，次查持续显示交接/实际状态，Boot头格式低优先级。对应已锁小米内核52a2f18的6份源码已只读固定摘要；其CTL挂接与INTF_STATUS版本路径见operations/2026-10-24-display-fault-hypotheses.md及reports/enuma-native-display-diagnosis-sources.json。旧时序谓词不冒充真实接口状态。完成本轮计数后优先核对SSPP→LM/CTL→INTF/双DSI路径与实际状态；v3被接受不等于显示交接完整，DTB/vendor_boot差异单独核对。

当前证据：config/dsi-counters-probes.json、reports/enuma-dsi-counters-{host,bundle,device,preflight}.json（device/preflight仅已实际产生时存在）、firmware/docs/dsi-counters.md。逐份快照/原始日志/镜像/标识/备份/相机仅out。旧step14与R-005按各自source-history源锁保存，不冒充当前新源码实测。顶层build/FD/payload报告对应最后构建候选。

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。
