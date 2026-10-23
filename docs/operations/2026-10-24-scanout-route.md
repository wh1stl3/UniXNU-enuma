# 当前进度：候选SSPP挂接与所选DSI双窗关联探针完成构建审计

2026-10-24 Asia/Shanghai。用户“继续”，沿已确认在场恢复、按需摄像及直接只读实测授权推进。主判断：接口计数已能推进，首查原候选buffer/SSPP图层选择与后续显示接管，Boot v3格式低优先级。每笔前全部当前文档提交推送、即时身份/备份/恢复及超时停追加规则保持。

## 当前实现和离线资格

固件f0cef6f1505f636f815f5d3653ed467f84f72922，设备gitlink与65项源锁固定。step19严格取历史step12/R-005算法的第一个合法有界描述，不自动换后面的buffer来取得通过。硬件major/minor须6.0；原enuma FDT的六CTL在0x2000..0x2a00，非其他SM8250示例的0x1000。CTL_INTF_ACTIVE(+0xf4) bit1/2对应两个DSI；各CTL六LM的四个staging字按固定小米52a2f18位表解码VIG0..3/DMA0..3非virtual源，包含LM5主字偏移0x24。

选择首个挂接该Source、又选择实际活动DSI的CTL/LM，要求该同一DSI在两次既有Stall(100000)窗口各严格非回绕递增1..64。复查活动bit0、timing/enable、CTL完整接口掩码、选中LM四字、候选原始六描述字及最终版本不变。最多241次MMIO只读和两次等待；不访问像素、不写显示/计数寄存器，不新增库/构造器/分配/映射。

限制：这是稳定staging配置关联加所选接口递增。CTL/LM可能是shadow/残留寄存器；并未证明该LM实际通过pingpong/DSC送到该接口，也未证明fetch成功、可见区域/alpha/遮挡、面板/背光或物理IOVA关系。失败可来自描述/版本/活动/挂接/稳定性/等待/递增任一条件，不能仅凭失败宣称原buffer无路由。通过则降低“完全未挂接的候选”嫌疑，但不认证像素地址正确或屏幕成功。

51项fake MMIO/wait用例O1/Oz+ASan/UBSan通过，含八源位域、secondary位、virtual-only拒绝、LM5、首描述不替换、所选接口/配置变化、回绕/零/过大增量、等待错误及精确241读上界；真实AArch64仅既有gBS。固定小米CTL/catalog/SSPP/INTF摘要及原FDT偏移通过，GOP补丁组合/真实Mu传输、像素旗标/恢复身份、源锁/workspace通过。三份完整链接/补丁回退、30OEM PE/DEPEX、生成AutoGen/库、BootShim/FD/Boot v3与同源宏差异bundle通过。step18 actual PE沿原受限CFG数据流检查；step19优化动态地址只检查实际PE中的CTL/帧/状态/等待/界限指令指纹，非完整MMIO加载/存储/控制流证明。只读边界另由锁定源码callback和主机测试约束，不能将机器指纹说成完整禁写证明。

| 候选 | step/query | Boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- | --- |
| route-control | 18/1 | `0c0700b7565d2cc54cb9b2ef41ac954e3181df294a50d812ac75b3d3134a1936` | `776217c67a2999fec6983630b3b9570c55087debf57be36fb7c6109f218542f5` |
| route-associated | 19/1 | `4faec747aa34c4d084fcff1a089ac9373957ece07aff4c77d43a18cbdeb7aebb` | `44305c57daf2730081475928cc29b111821b2013d758749224c10a9c75aae6f7` |
| route-unproven | 19/2 | `d01bd6e3d1f66c7eff5a36563dd5c8a79c20c27ee1845f3b4a6d09e0fc0a4d32` | `84c3b03576f0eb383769d67e6c63874ce122aaf50083c94bf357637ab96d6f76` |

同源step18/query1计数对照后执行step19正/互补。query1命中非错误marker、query2命中错误marker，Core命中延时2秒，未命中7秒同步完成兜底，非watchdog。单笔短返回不当数值或路径证明，互补差异需与同源对照和无按键/恢复事实共同解释。

## 最新设备结果

route-control step18/query1：2026-10-24 03:30:35，recovered-android-boot-complete；ADB16.937秒/Android完成31.14秒；用户无按键True，原分区摘要True，独立恢复核验True。

route-associated step19/query1：2026-10-24 03:32:02，recovered-android-boot-complete；ADB16.938秒/Android完成32.422秒；用户无按键True，原分区摘要True，独立恢复核验True。

关联互补尚未齐备，未判定首候选的稳定staging关联。

## 下一步与恢复边界

先提交推送全部当前文档，再以即时身份/备份/恢复门禁临时启动 route-unproven；每笔受控返回和独立恢复/无按键核验后推进。

用户可在场恢复；必要前后截图与主机日志，实际输出/判读变化/恢复动作时录像。键盘反光不作输出。Android/fastboot恢复已核对，TWRP/UART未验证；超时停追加先恢复并当轮落实交接，恢复核验后继续离线分析和新软件，不原样重试失败镜像。

R-005 consumed，不重放像素。无MMIO/像素/分区写入、新内存/映射/大小/基址/verified变更，51MiB heap/512MiB owned/example=true/Boot v3保持。旧60f38e9原生资格通过source-history/uefi-60f38e9.lock.json冻结，其余历史沿各自源锁，不冒充新源码实测。顶层build/FD/payload报告对应最后候选，逐份完整快照/镜像/原始日志/相机/标识/备份仅out。

证据：firmware/docs/scanout-route.md、config/scanout-route-probes.json、reports/enuma-scanout-route-{sources,host,bundle,device,preflight}.json（设备/预检只在实际产生时存在），operations/2026-10-24-scanout-route.md。故障判断及可推翻条件见operations/2026-10-24-display-fault-hypotheses.md；用户要求基于本机/公开资料大胆给出可推翻主判断已列AGENTS持久规则。尚无可见写屏，文本后端未接入，诊断Core主动返回，DXE/BDS/UniXNU菜单未放行，未进入XNU。
