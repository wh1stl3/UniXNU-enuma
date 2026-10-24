# 当前进度：同源step20对照超时已恢复，转启动状态隔离

2026-10-24 Asia/Shanghai。用户要求更大胆推进；新证据已推翻“仅step22长等待/新增blend逻辑导致超时”的单一解释，当前不追加显示探针。

## 两次硬停与已核验恢复

8fd3e62 step22正向16:03:42启动，75秒无自动ADB/fastboot返回，立即停追加；用户长按恢复，16:06:02 Android完成/root/原槽/解锁/匹配备份及原boot/vendor_boot摘要独立通过，0efa313推送。反向未执行、冻结，六类未知。

恢复后按持续工作规则完成隔离新软件c45e52a：step23从step20仅加局部staging解码，允许border，不新增MMIO地址、不读dim/alpha/LM模式、不长等待；最大250读/两次100ms。69项sanitizer用例/AArch64及完整三份构建/实际FD/OEM/依赖/Boot v3审计通过，86adc68文档推送后2026-10-24 16:20:56启动同源step20对照（尚未执行step23）。Boot v3 SHA-256 `459961e1675150602631647e6db7760a929bed19f922111dd3bccc606d9f0416`，FD `7e2ec318f63505bbddaa19c663acd8ae6e2ab50f260338f6667853d384279bf3`。约16:22:12观察期限内仍无返回，16:22:16确认manual-recovery-needed，再次停止追加；stage23正/互补均未执行、冻结。

用户再次长按恢复并明确确认Android；2026-10-24T16:23:08.877428+08:00独立enuma、sys.boot_completed=1、root、原槽、解锁、匹配备份及原分区摘要通过。当前实际Android完成、恢复阻塞解除；不能称两笔自动返回或无按键成功。硬停来源AGENTS失联/无法受控返回规则，每次均优先恢复，当前交接本轮落实。无分区写入，原始日志/备份/标识/相机只存out，摄像头自行旋转判读。

## 已完成离线分析与更新主判断

成功reason22-control与失败stage23-control宏完全一致，均79模块；77个PE/DEPEX完全相同，仅PcdDxe和SimpleFbDxe二进制差异。SimpleFb的.text、.data、.pdata、.reloc逐节SHA完全相同，仅.rdata不同。详见reports/enuma-step20-control-comparison.json。因此新显示算法代码差异的解释进一步下降；.rdata差异是否纯元数据及PcdDxe差异仍需解析，不能现在称完全相同固件。前次step22超时不应唯一归因长等待，结论已修正。

中等置信首查：恢复后启动链/ABL遗留状态差异、跨构建PCD/元数据/打包状态及早期执行位置。现无早期日志或返回marker，不能证明执行到了SimpleFb/MMIO，面板/DSI/staging/alpha皆不能据超时定责。Boot v3格式此前同源基线多次正常，整体切换v1仍低优先级。

## 下一步（离线继续）

冻结step22失败正向及未执行反向、stage23失败对照及未执行正互补，不重试。继续解析两个差异PE的节/PCD有效数据，核对BootShim/打包字节；据此准备具有更早停止点、无显示MMIO/等待的新启动定位软件，先资格和全文档推送，再即时身份/恢复门禁后才可实测。用户人工恢复后继续离线规则有效；本次不以恢复后盲加显示探针作为推进。当前无新增批准项或人工待办，未宣称新自动返回资格。

R-005 consumed，禁像素/MMIO/分区写、新映射/内存大小/基址/verified变更；51MiB heap、512MiB owned、example=true/Boot v3保持。TWRP/UART未验证。尚无可见日志/菜单，文本后端未集成，未进入XNU。

证据enuma-scanout-sole-stage-device/preflight、enuma-step20-control-comparison及operations/2026-10-24-scanout-sole-stage.md；新源码c45e52a资格沿bundle/host，超时不能冒充运行通过。当前文档推送状态以实际Git远端核验为准。

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。

接手顺序AGENTS/STATUS/DECISIONS/NEED-REVIEW。
