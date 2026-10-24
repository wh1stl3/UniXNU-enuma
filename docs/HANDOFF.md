# 当前进度：首候选输出矩形与关联LM几何检查

2026-10-24 Asia/Shanghai。用户明确可以开始实机工作，并要求自行旋转摄像头画面。沿已有在场恢复及只读直接实测授权推进。

## 主判断与证据边界

f0cef6f 三笔同源对照/正互补支持首个合法SSPP的CTL/LM稳定staging关联及所选DSI递增，降低“首候选完全未挂接”和“整个接口停摆”的嫌疑。目前工作假设：混合裁剪/遮挡或LM实际输出链路与fetch/地址可见性更值得首查，置信中等；面板后段保留，Boot v3解析低优先级。尚未证明实际内存取数、LM→pingpong/DSC连接或可见像素。先分辨配置几何，再据结果排序；不靠放宽谓词取得通过。

## 新实现及离线资格

固件 012715b070a583ae636a3a33419ea3843ad7f2ad，设备gitlink和66项源锁固定。旧f0cef6f资格由config/source-history/uefi-f0cef6f.lock.json冻结，step19头文件字节不变。本轮step19/query1同源对照，step20/query1正向及query2互补。

step20保留首描述不替换、major/minor6.0、CTL/LM挂接、同一所选活动DSI两窗各非回绕递增1..64以及描述/配置稳定检查。增加SSPP OUT_SIZE(+0x0c)、OUT_XY(+0x10)和所选LM OUT_SIZE(+4)：要求源/输出宽高相同、至少128x8、整个输出矩形位于LM配置宽高内，三字在每个窗口后不变。固定小米52a2f18及原enuma FDT确认六LM偏移0x45000..0x4a000/步长0x1000、长度0x320。最多250次既有映射内MMIO读取、两次既有Stall(100000)，无像素/MMIO写入、新映射、分配、库或构造器。

63项O1/Oz+ASan/UBSan用例及精确250读上界、AArch64仅gBS依赖通过；固定小米源/FDT、真实Mu GOP补丁组合/marker回归、源锁/workspace和5项像素/恢复守卫测试通过。三份完整链接/回退、30OEM PE/DEPEX、生成依赖、实际FD指令指纹、Boot v3及同源宏差异bundle通过。实际PE指纹不是完整动态MMIO/store/CFG证明；禁写边界另由锁定源码及有界主机用例审查。配置几何通过不证明scaler/decimator模式、翻转、排除区、alpha/遮挡、物理输出路由、fetch或历史R-005结果；失败也不能单凭复合拒绝认定裁剪。

| 候选 | step/query | Boot v3 SHA-256 | FD SHA-256 |
| --- | --- | --- | --- |
| geometry20-control | 19/1 | `20f079b4682e0365f2a3e7a1c1707829446c49d0738857458d89dc13d4ddaefd` | `80ba35f62b86a9cf94f7784fb3930e0a57f9848bd4c1ab8bfc511d2746ce93c2` |
| geometry20-contained | 20/1 | `dfa50d73be6a856202f238901d2308a60fbc3bb94a09e4dfd2009b5ce568b28f` | `ee00f53ecb7416af78698be802767875f11266ea55c88ebad70733c2982f7454` |
| geometry20-unproven | 20/2 | `b2964a650722ca57184188210fb5f272eed91e038dec9296c0a5b131c0e5c50d` | `7071fbb1945fb553eb20b805733fa1280ff1902063310082d9c62d13f8b8f5d1` |

query1支持非错误marker、query2支持错误marker；Core匹配延时2秒，未匹配同步兜底7秒。主机时序只作有条件的间接谓词证据，不当寄存器数值/精确100ms或频率证明。

## 最新实测

geometry20-control step19/query1：2026-10-24 15:06:43；recovered-android-boot-complete；ADB 18.188秒 / Android完成 32.984秒；用户无按键 True，独立恢复 True，原分区摘要 True。

geometry20-contained step20/query1：2026-10-24 15:08:19；recovered-android-boot-complete；ADB 17.141秒 / Android完成 29.609秒；用户无按键 True，独立恢复 True，原分区摘要 True。

geometry20-unproven step20/query2：2026-10-24 15:10:01；recovered-android-boot-complete；ADB 22.531秒 / Android完成 37.015秒；用户无按键 True，独立恢复 True，原分区摘要 True。

同源step19对照和step20正/互补时序支持：保留首候选稳定staging及所选活动DSI两窗递增条件，首候选源/输出宽高相同、至少128x8、整个输出矩形位于关联LM配置范围内，输出大小/位置/LM大小每窗保持。仅配置几何，不证明scaler/decimator模式、排除区、alpha/遮挡、LM实际输出、fetch或可见路由。 query1-query2 ADB差-5.39秒包含启动噪声，不能当精确频率或实测100ms。

## 下一步与恢复

稳定配置几何获得支持，降低简单源/输出尺寸不匹配和矩形越界嫌疑；下一步首查alpha/遮挡及LM→pingpong/DSC实际连接，与fetch/地址可见性并列中等优先。若取得可见的候选像素/fetch对应证据则可推翻该主判断；再查面板后段。 R-005 consumed，不重放像素或盲写寄存器。

用户可在场恢复，新摄像头保存原图并自行顺时针90度旋转后判读，必要前后截图；实际输出/判读变化/恢复操作时录像。键盘反光不作显示输出。Android/root/原槽/解锁/备份及boot、vendor_boot原摘要即时核验；Android/fastboot已核对，TWRP/UART未验证。超时立即停止追加并优先恢复，当轮落实原因/模式/恢复交接；恢复核验后继续离线修复新候选，不原样重试失败镜像。

R-005 consumed，不重放像素；无分区写入、flash/erase/改槽、新内存/映射/大小/基址或verified变更。51MiB heap、512MiB owned、example=true及Boot v3保持。构建/镜像/原始日志/相机/标识/备份仅out。尚无可见写屏；文本后端未INF/FDF/调用者集成，诊断Core主动返回，DXE/BDS/UniXNU菜单未放行，未进入XNU。

证据：firmware/docs/scanout-geometry.md、config/scanout-geometry-probes.json、reports/enuma-scanout-geometry-{sources,host,bundle,device,preflight}.json（device仅实际产生时存在），operations/2026-10-24-scanout-geometry.md及display-fault-hypotheses.md。每笔设备动作前所有当前文档先提交推送，远端发布以Git核验为准。

## 系统与内核现状

目标enuma/SM8250，iPadOS17.7.11/21H461，iPad7,1/j120ap，XNU10063.141.1/4KiB，UniXNU5fdbd5d。CI39927966148/head250cdf9已真实链接源平台内核，21417672字节、SHA b940f550a70155db5c29d274dff0874216cc0d58ab030b01e2c8a93315c6052d；不是enuma运行证据，未预链接donor或启动。donor46415872字节/237模块和静态闭包计划通过，未emit预链接镜像。

64MiB配置FAT已生成，仅发现/reset配置，尚未接publisher/打包启动；完整ADT/载荷输送/内存/EBS/入口仍待闭合。NativeUfs为SM8550参数，当前禁用；未创建系统卷或写userdata。EnumaScreen文本后端仅host/AArch64对象，未INF/FDF/调用者集成。

详见operations/2026-10-23-system-kernel-userland-roadmap.md、2026-10-23-discovery-volume-platform-link.md。历史资料不替代当前实测和授权。

接手顺序AGENTS、STATUS、DECISIONS、NEED-REVIEW。
