# D-293：冻结R022，补齐离线格式反读与输出链依赖

2026-10-26T05:49:29.611853+00:00。用户要求实机晚上才能进行，本轮仅离线；不按时钟自动启动，不重复请求恢复在场。R022仍pending，S050未执行；即使到晚上，也须有效精确放行、最新采集就绪及即时门禁。原S001..049/R020/R021消费和观测硬停记录不变。

新增实现限于设备仓主机工具与测试，没有修改固件、重构建FD、重包镜像或刷新资格。固件8680ea79d6fd14d4526d314f430e9812955cb78a和R022镜像f684ef22ea79178953ff8efcc81fb2243f189a096ef276a676c6a27e7b4b6e5b冻结；读取归档manifest与当前qualification相等，并重新核对实际镜像摘要。

主判断：现有实拍失败更符合曝光/焦点与两秒观察时间不足（用户直接反馈）而非已证实的数字格式损坏。新离线证据排除了本轮所测理想栅格中的高低32位拼接、hex位丢失、列位置、环回后最新return选择等错误，不能排除真实像素通道/取样、压缩/运动/曝光或硬件显示错误。可推翻条件：清晰原片中的数字与同一启动的独立快照不符，或清晰栅格仍缺行/位；目前无独立实机值，不能伪造预期答案。

## 真正新增结果

1. tests/cached_log_format.c 调用真实生产EnumaBootLogAppend、EnumaLogPageFromSnapshot、EnumaPixelLogAt，输出96组完整页面。每组先写满并环回128条，随后追加目标point13及非return point20，验证选择最近已完成return，而不是直接取最后一条。
2. scripts/check_cached_log_format.py 以独立3×5字形表反读精确256×96二值栅格，检查全部2,359,296像素（含间距/空白），覆盖64个status单bit、0、全1及混合值、不同32位ordinal与丢失标记。C侧ASan/UBSan通过。单像素改变必须拒绝，不用模糊匹配补字。
3. scripts/decode_cached_log_text.py 严格解析三行人工转录，重组完整64位status，保留ordinal、cached和旧记录丢失信息。缺行、?、O误作hex零、大小写错、上下行错、首空白缺失、换行或超宽均拒绝；3组单元测试通过。工具结果screen_log_verified始终false，不凭字符串宣告实机成功。
4. scripts/audit_console_readiness.py 绑定源码摘要/具体行号、源内顺序及六模块真实静态库列表，核对冻结R022一致。此为静态依赖审计，不是运行证明。官方backend会在finally撤回Core诊断patch，当前staging未打补丁的Dispatcher不能冒充实际编译输入；本报告记录固定patch及现有实际PE审阅的独立边界。

字形存在固定上下文碰撞：O/0、S/5、C/c。标记位置已知时可解析；不能把此工具变成对任意照片自动OCR。生产页只显示最近point13的ordinal/status与loss标记，不显示事件sequence/GUID/其他127条，也没有独立启动ID、CRC或实机参考快照。三行可读是阶段性内容验收，不等于全部RAM日志可追溯。

## 实际执行顺序及可验项

| 可验项 | 依赖/实际顺序 | 本轮独立结果 | 实机验收条件 |
|---|---|---|---|
| DXE RAM记录 | 在detail过滤/复位前追加，128条环形；生产者须静止才复制 | 旧10000事件回归保留；新增环回后选择与64位反读通过 | 本轮未读取真实完整快照；不能从时间推断全部值 |
| 私有快照发布 | 第一个detail中尝试安装一次，失败不重试；provider校验version/bytes/callback | 固定源及既有PE审阅，协议失败路径既有回归 | 依赖DXE服务/同步单writer；不是AP/异常/早期SEC logger |
| 当前页日志含义 | provider执行内先Snapshot，然后像素事务，再返回；CoreStartImage返回后才追加该次point13 | 静态因果链确认 | 页面无法含当前这一次provider尚未发生的返回；可能属于前一驱动，不据此认定当前驱动失败 |
| 受控屏幕sink | Native6/requirements22独立诊断分支→EL1/全帧WT→ABI快照→page→保存/绘制/8秒/恢复读回 | 原R022资格保留，未扩大读写、cache、路由或面积 | 原片逐字读清三行，独立记status/ordinal/loss；不猜值；仍需时钟/恢复后验 |
| 128条文本回放API | immutable snapshot，单行callback接受后推进cursor，调用者控制取消 | 旧sink拒绝重试与边界测试保留；未接入新屏幕sink | 失败sink可能已部分输出，重试不代表恰好一次；不能宣称已上屏128条 |
| 早期/连续DEBUG | SEC/DXE有效输出后端；当前六模块链接BaseDebugLibSerialPort+Null SerialPortLib | 六份实际库清单摘要匹配 | GOP或ConOut出现不会自动重连DEBUG；需另行实现/资格，不提前猜地址绘制 |
| Print/ConOut | Print→UefiLib InternalPrint→Console.OutputString；BDS BeforeConsole登记设备路径→默认console连接→AfterConsole | 源码顺序/已有FD模块证据 | 当前早停不进BDS。需要正式GOP/设备路径/GraphicsConsole绑定、实际Print输出与返回；不能用DiagDraw替代 |
| DiagDraw | EnumaProbe Line先Print再DiagDraw；后者定位GOP并按stride直接存ff000000/ffffffff | 存储路径与代码已存在，不是GOP Blt | 需独立通道/alpha/同步/写入范围资格；R022不执行它，不借旧授权 |
| UniXNU日志 | UniXNULog→DEBUG及可选EFI_SERIAL_IO_PROTOCOL.Write | 已核源码，无ConOut路径 | SerialIo是否存在未知；Null SerialPortLib不能单独证明SerialIo不存在，菜单可见也不等于日志可见 |
| UniXNU UI初始化 | ConnectAll→config→注入driver→UiInit→MenuRun；UiInit先GOP，再ConOut QueryMode，否则headless | 固定源码路径已审计，模块已打包 | GOP满足完整准入且Blt真实可见；文本路径需ConOut；菜单还须输入/超时/返回可控，当前均未运行 |
| 恢复/时钟 | 新鲜身份/备份/恢复检查→断开/返回观察→3样本boot-id时钟→恢复后验 | S049旧结果闭环；本轮未调用设备工具 | R022仅唯一code5完整39.252..41.748秒窗可作间接支持；失败/重叠/不可读/75秒未返回立即停追加 |

## 晚间最小现场条件

本轮不等待到某时刻启动，不建立自动任务。用户明确放行R022这一新8秒镜像单次继续后，文档/批准记录先提交推送。随后确认拍摄已开始或明确就绪；提前对准左上角原点区域、锁焦、压低白字曝光，关闭录音，持续拍到Android。主机摄像头已断开，使用已有显式human-primary-only入口。旧ready和历史备份后验均不能当作当下状态。

现场读取表格须保持高32位与低32位分行，不靠预设值填补。可使用 `python scripts/decode_cached_log_text.py --lines "C0d Oxxxxxxxx" "Sxxxxxxxx" " xxxxxxxx"` 检查已确读的字面转录（x为占位，不能实际提交为数字）；模糊处记unknown而不是硬填。建议另记拍摄文件本地路径/摘要与启动身份；照片/视频只留out，不上传。

75秒观察期限不变。S049约56.859秒恢复+6秒仅预计约63秒，不保证新图自动返回；未关闭/延长看门狗。超时、观察/时钟失败或恢复异常停止追加，仅沿原允许路径安全恢复并同轮落档。当前无恢复按键欠项，不追加泛问。

继续的有价值工作边界：现在缺的是新8秒候选的清晰现场证据及其后实际失败点。离线不能判定对焦改善、实际status值、GOP或菜单成功。本轮不为增加工作量接入另一屏幕sink、扩大字体/区域、延长其他计时或复建同一产物。若之后设计GUID/sequence页或错误优先页，必须作为新版本和新范围另行资格，不冒充R022。

requirements22、alpha、SMMU、全部verified与内存/破坏性分区边界保持。nuwa、旧会话未触碰。证据：reports/enuma-cached-log-format.json、reports/enuma-console-readiness.json、原R022qualification/PE审阅以及reports/enuma-native-route-S-049-result.json。
