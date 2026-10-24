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

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。

接手顺序AGENTS/STATUS/DECISIONS/NEED-REVIEW。
