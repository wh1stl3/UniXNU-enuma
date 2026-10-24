# 当前进度：首候选单源/无dim混合配置检查

2026-10-24 Asia/Shanghai。用户明确继续推进主线，沿在场恢复及摄像头自行旋转规则。沿已有在场恢复及只读直接实测授权推进。

## 主判断与证据边界

此前实测支持首候选staging关联、所选DSI双窗递增和1:1矩形包含，降低完全未挂接、接口停摆和简单尺寸越界嫌疑。本轮优先核对局部其他staging源、dim/color-fill和保守alpha配置。中等置信工作假设：若这些配置也通过，主查应转向LM实际输出链路及fetch/地址可见性；Boot v3解析仍低优先级。它们是可推翻假设，不能把配置状态当真实fetch或面板输出。

## 新实现及离线资格

固件 ff3db3009da309e7435a063c88247d10ec9f75ae，设备gitlink和67项源锁固定。旧012715b由config/source-history/uefi-012715b.lock.json冻结，step19/20头文件字节不变。同源step20/query1对照及step21/query1正向、query2互补。

step21保留首描述不替换、首关联CTL/LM、major/minor6.0、同一所选活动DSI两窗各非回绕递增1..64、1:1输出包含及描述/配置稳定。新增保守模式要求四个选中CTL_LAYER字只含候选非virtual源，编码stage1..12，无其他/未知/virtual/边框字段。按本机FDT读取11个blend op（0x20..0x110/步长0x18），全部dim bit16清零；BASE编码1无独立alpha寄存器，非BASE要求选中op精确0x100和packed FG255/BG0 alpha0x00ff0000。LM_OP_MODE及全部新增字在每窗后保持。最多289次既有映射内只读和两次Stall(100000)，无像素/MMIO写入、新映射/分配/依赖。固定小米52a2f18 CTL/LM/MDSS/CRTC源码及保存enuma FDT契约已审计。

174项O1/Oz+ASan/UBSan、8源×12编码、额外/未知字段、dim/alpha/配置变化、精确289读及AArch64仅gBS通过；真实Mu GOP补丁组合/entry marker、源锁/workspace及5项像素/恢复守卫通过。三份完整链接/回退、30OEM PE/DEPEX、生成依赖、实际FD指令指纹、Boot v3及同源宏差异bundle通过。实际PE指纹不是完整动态MMIO/store/CFG证明；边界由锁定源码和主机故障注入另行审查。

限制：这是保守配置模式，非穷尽可见性分类。拒绝可能来自其他/未知/边框staging、dim、合法pixel-alpha/其他模式、状态变化或继承门控，不能直接称遮挡/透明。通过只降低该LM局部配置解释，不证明影子状态已生效、SSPP排除区、scaler/decimator、实际LM→pingpong/DSC/fetch/IOVA/cache或面板可见，更不追认历史R-005结果。

| 候选 | step/query | Boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- | --- |
| blend21-control | 20/1 | `c8722cc15e81561b29cd7bf325a5a45f7a5d30a0580c73de5be799cfdc6ed8ec` | `1cba088a92ad664dcbc7b370ecdec3e132982f91f7d3cf9daecc62a7924b02d4` |
| blend21-single | 21/1 | `0a2b8544c806fdd960d0fdf35a94b94a19055a90bc5e940d5496d3c8467c7c39` | `f07555d7dc5a68b010d1a6cfe4f1539d9c3ae3e6c7cb2be3ca41e183ce635b62` |
| blend21-unproven | 21/2 | `a2cc5cb6583df89e580f26b53911d875783473e0b74f66554c4cbe62c88d8de0` | `bd71348194da620500feb8256b98e457389bf0a655be0de37b93b5e363781b14` |

query1支持非错误marker、query2支持错误marker；Core匹配延时2秒，未匹配同步兜底7秒。主机时序只作有条件的间接谓词证据，不当寄存器数值/精确100ms或频率证明。

## 最新实测

blend21-control step20/query1：2026-10-24 15:28:59；recovered-android-boot-complete；ADB 17.141秒 / Android完成 32.688秒；用户无按键 True，独立恢复 True，原分区摘要 True。

blend21-single step21/query1：2026-10-24 15:30:40；recovered-android-boot-complete；ADB 21.5秒 / Android完成 35.953秒；用户无按键 True，独立恢复 True，原分区摘要 True。

单源混合互补尚未齐备，未判定保守配置模式。

## 下一步与恢复

全部当前文档提交推送后，按即时身份/备份/恢复门禁临时boot blend21-unproven；受控返回、独立恢复及无按键确认后继续。

用户可在场恢复，新摄像头保存原图并自行顺时针90度旋转后判读，必要前后截图；实际输出/判读变化/恢复操作时录像。键盘反光不作显示输出。Android/root/原槽/解锁/备份及boot、vendor_boot原摘要即时核验；Android/fastboot已核对，TWRP/UART未验证。超时立即停止追加并优先恢复，当轮落实原因/模式/恢复交接；恢复核验后继续离线修复新候选，不原样重试失败镜像。

R-005 consumed，不重放像素；无分区写入、flash/erase/改槽、新内存/映射/大小/基址或verified变更。51MiB heap、512MiB owned、example=true及Boot v3保持。构建/镜像/原始日志/相机/标识/备份仅out。尚无可见写屏；文本后端未INF/FDF/调用者集成，诊断Core主动返回，DXE/BDS/UniXNU菜单未放行，未进入XNU。

证据：firmware/docs/scanout-blend.md、config/scanout-blend-probes.json、reports/enuma-scanout-blend-{sources,host,bundle,device,preflight}.json（device仅实际产生时存在），operations/2026-10-24-scanout-blend.md及display-fault-hypotheses.md。每笔设备动作前所有当前文档先提交推送，远端发布以Git核验为准。
