# 当前进度：混合拒绝原因六类正反取证

2026-10-24 Asia/Shanghai。用户“继续 进度决策稍微大胆一点”，沿已有在场恢复、只读直接实测及相机自行旋转要求推进。

## 主判断

中等置信优先假设：ABL遗留混合状态与保守观察器不匹配（边框位或合法alpha模式），而非整个DSI停摆。接口双窗、staging和1:1几何已获支持，但step21只说明严格模式不成立。优先取得拒绝类别来改变下一项实现；若分类为dim/额外源，则直接转向对应stage/覆盖区域核查；若border-only，则修正观察器假设并查实际输出链路。假设可由本轮结果推翻。

## 实现与资格

固件 8fd3e62bc5d6af5bdd91670cbebeb9a4ac23b008，68项源锁及设备gitlink固定；旧ff3db30沿config/source-history/uefi-ff3db30.lock.json冻结，step19/20/21头文件和Core marker通道字节不变。同源step20/query1对照，step22/query1正向及query2反向。

step22沿原首描述、首关联CTL/LM、major/minor6.0、1:1几何、同一活动DSI两窗各非回绕递增1..64和稳定性。最多289次原映射内读取。局部只屏蔽staging border bit24来解码，绝不写寄存器；完整原staging字仍参与稳定复查。分类：0严格原模式；1仅border位偏离且其他单源/无dim/BASE或常量opaque条件满足；2其他/未知staging或stage编码；3 dim bit16存在（可能伴border/alpha）；4无额外staging及dim但非BASE alpha/op偏离精确常量模式；5继承门控/等待/采样稳定性失败。2优先于3，3优先于4，1只在无其他偏离时输出。类2不等于实际其他高层，类3不等于实际遮挡，类4不等于透明。

采样结束后正向等待class×4秒，反向等待(5-class)×4秒；都走原匹配Core2秒路径、原warning marker，反向故意返回FAIL marker不称设备错误。最多2次100000us采样等待+1次<=20000000us编码等待，总20.2秒，原75秒观察期限不变。编码期间不再读MMIO，不能把前段采样稳定扩张为整个等待稳定。编码等待错误不能当正常分类。

主机解码要求同源资格、三笔完成/无按键/独立恢复，正反差值最近8秒间距类别残差<=2秒、各自对照预测残差<=2秒、合计增量20秒残差<=3秒，任一不符则unknown，不取最接近类别硬判。不当数值寄存器转储、精确采样频率或可见性证明。

194项O1/Oz+ASan/UBSan覆盖全部六类/正反等待/优先级/稳定性/错误及精确289读；两方向AArch64仅gBS，真实Mu GOP补丁/marker回归、10项解码/像素/恢复守卫、源锁/workspace通过。固定小米52a2f18 CTL/LM/MDSS/CRTC和原enuma FDT源事实沿enuma-scanout-blend-sources.json审计。三份完整链接/回退、30OEM PE/DEPEX、AutoGen/库、实际FD受限指令指纹、Boot v3及同源宏差异bundle通过。PE指纹不是完整动态MMIO/store/CFG证明，边界另由锁定源码和主机用例复核。

| 候选 | step/query | Boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- | --- |
| reason22-control | 20/1 | `9ded5fa6f8e27878d75face87bd473b207e5124652493272640145aab18c304a` | `dcaed1f3cd1d89bfcc9b1f6c4221b012c5b503e4bfb7e4ecca3d619389c71041` |
| reason22-forward | 22/1 | `429c3c14ec2ee527a554012140049baad1f1ac67fb84bd925c849ce7df64d97e` | `8b2b2695c0556a1719a7c78c81e4f1cb35fdeccd591617de6673e3a421052cec` |
| reason22-reverse | 22/2 | `59d748bb55766d9082e529c00993800caf196831067c95bc4def32de5e84ca3c` | `82057cbf7e667260af60b85c378ebc221d44b5e2f88dd3628fa3c501640f7e4c` |

## 最新实测

reason22-control step20/query1：2026-10-24 16:02:03，recovered-android-boot-complete；ADB 16.079秒/Android完成 32.829秒；用户无按键 True，独立恢复 True，原分区摘要 True。

六类正反编码尚未齐备，类别未知。

## 下一步与边界

全部当前文档提交推送后，以即时身份/备份/恢复门禁临时启动reason22-forward；受控返回及独立恢复/无按键确认后继续。

用户可在场恢复；相机保留原图、自行旋转判读，必要前后截图，真实输出/判读变化/恢复时录像。键盘反光不当输出。即时enuma身份、Android完成/root/原槽/解锁/匹配备份及boot/vendor_boot原摘要核验；Android/fastboot已核对，TWRP/UART未验证。超时立即停追加、先恢复并当轮写明状态，恢复核验后离线分析新候选、不原样重试失败镜像。

R-005 consumed，不重放像素；无像素/MMIO/分区写入、flash/erase/改槽、新映射/内存大小/基址/verified变更。51MiB heap、512MiB owned、example=true及Boot v3保持。构建/镜像/标识/原日志/备份/相机仅out。仍未可见写屏、未放行DXE/BDS/UniXNU菜单、文本后端未集成、未进入XNU。配置分类不解决真实LM→pingpong/DSC、fetch/IOVA/cache或面板输出证明。

证据firmware/docs/scanout-blend-reason.md、config/scanout-blend-reason-probes.json、reports/enuma-scanout-blend-reason-{host,bundle,device,preflight}.json（device仅实际产生时存在）、scripts/decode_scanout_reason.py和operations/2026-10-24-scanout-blend-reason.md；故障假设见display-fault-hypotheses.md。每笔前全部当前文档提交推送，远端状态须实际核验。

## 超时与恢复更新（取代以上待执行状态）

# 当前进度：step22超时已人工恢复，转离线修复

2026-10-24 Asia/Shanghai。用户要求更大胆推进，但本轮新证据通道失败，不能把目标当结果。

## 硬停与恢复事实

8fd3e62同源step20基线16.078秒ADB返回、32.828秒Android完成（精确以报告为准），用户确认全程无按键、独立恢复通过。全套文档31b405d推送后，2026-10-24 16:03:42临时启动step22正向，Boot v3 SHA-256 `429c3c14ec2ee527a554012140049baad1f1ac67fb84bd925c849ce7df64d97e`，FD `8b2b2695c0556a1719a7c78c81e4f1cb35fdeccd591617de6673e3a421052cec`。fastboot boot命令成功仅说明发送/启动请求。约16:04:58到达75秒观察期限，16:05:02确认manual-recovery-needed，无ADB/fastboot自动返回；立即停止追加镜像，step22反向未执行。按AGENTS执行失联/不可控返回规则触发硬停。

用户按请求长按电源恢复并明确回复已到Android；2026-10-24T16:06:02.205849+08:00独立核验enuma、sys.boot_completed=1、root、原槽、解锁、匹配备份和boot/vendor_boot原摘要通过。实际当前状态为Android完成，人工恢复后已解除恢复阻塞；该笔不能记为自动受控返回或无按键成功。超时及恢复相机保留原图并自行旋转判读，原始日志/标识/备份/图像仅out。

## 主判断和未执行项

step22六类取证失败，paired_decode=false，类别未知；反向候选已资格但冻结未执行。新增长编码等待（最多20秒）及从早拒绝改为完整采样是首要隔离点，中等置信；不能据超时判定面板、DSI停摆、staging、dim或alpha，更不能把旧step21拒绝升级为遮挡。Boot v3同源基线正常，格式切换低优先级。源码/主机/完整固件审计通过没有覆盖真实设备长等待行为，这一限制已显现。

## 下一步

按用户人工恢复后持续工作规则，立即继续离线分析/新软件，不原样重试step22。废弃本轮长编码通道用于继续实测，改回既有两次Stall(100000)及Core2/7秒判据；先独立验证“仅候选非virtual staging，忽略已知border bit24”这一配置条件，将dim/alpha与长等待全部移出新探针。新候选必须完成资格、所有当前文档推送及即时恢复门禁后才可实测。当前没有新待批准项，尚无新的自动返回资格。

R-005 consumed，无像素/MMIO/分区写、新映射/内存大小/基址/verified变更；Boot v3、51MiB heap、512MiB owned、example=true保持。用户可在场恢复，摄像头自行旋转。Android/fastboot恢复已核对，TWRP/UART未验证。仍未可见日志/菜单、文本后端未集成、未进入XNU。

证据reports/enuma-scanout-blend-reason-device.json、enuma-scanout-blend-reason-preflight.json、operations/2026-10-24-scanout-blend-reason.md；源码8fd3e62及资格见原bundle/host。历史step21/step20结果保持，不追溯改写。当前文档本轮提交推送，发布以远端核验为准。
