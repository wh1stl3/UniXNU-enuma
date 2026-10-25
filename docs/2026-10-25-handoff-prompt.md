# 当前状态：D-228，S-021已受控返回，准备S-022七秒常量

2026-10-25T22:16:21+08:00。用户本轮要求“继续推进 触发硬停再停”。S-021已单次发出、受控回Android并独立恢复核验，已consumed；S-022尚未发出。当前时钟界限：{"method": "host request interval minus quantized Linux uptime; 3-sample intersection", "boot_id_sha256": "9107737f47587883261dd4e628610a32b0ce06c886dd3804452cf7fc34b44505", "origin_monotonic_lower": 177088.955, "origin_monotonic_upper": 177089.025, "uncertainty_seconds": 0.07000000000698492, "calibrated_firmware_delay": false, "origin_after_issue_lower": 12.25199999997858, "origin_after_issue_upper": 12.321999999985565}。没有新增像素/MMIO写、映射、board/verified/分区操作。原始视频/图像只留本地out，不录音/上传。

S-019/S-020已双双自动返回Android并独立核验。ADB差-4.281秒支持补集方向，但Android完成差-1.359秒未进预设[-7,-3]窗口，正式结果保持ambiguous；旧对冻结且两图consumed，不换阈值或追认寄存器状态。两笔没有发生75秒超时/恢复失败，不能虚构为设备硬停。80290f4已发布该真实结果。

显示仍优先：为避免Android用户态启动波动继续遮蔽只读显示结果，先校准更窄的时基。Linux官方proc文档将uptime定义为启动后时间；主机每次用请求前后monotonic夹住uptime读发生时刻，并计入0.01秒量化，三样本求内核启动原点区间。原始样本/boot id仅本地；公开只保留boot-id摘要、区间与不确定度。先前同boot六次只读采样交集85ms仅证明同boot一致，不是UEFI延时资格，也不能回算缺少当时样本的S-019。来源https://docs.kernel.org/filesystems/proc.html，证据reports/enuma-boot-origin-preflight.json。

新固件ed1d894eb3b8dc611d37e3cb5e7ec21583ccede5已推送；native constant control沿相同INF/构造器和已审Core exact GUID返回点，query1固定warning1=>cold延时2秒，query2固定warning5=>7秒；无map查找、显示读取/采样/等待/GOP发布。实际PE/宏/源/完整FAT与Boot v3/原R-004记录/不可变归档已核对，实际Core可执行段与S-010已审cold完全一致；provider二者只有返回常量1/5的一条MOV差异，完整控制入口已审。Ramoops/warm均关闭。

S-021图afe1e310bd07d2b1cd74275f9a9b2fe66e945fb956aee4cce3b80d529c457c43，FDee67bdb7ee0054f29c74580db44a0ae9bb800e6c8668490ff92af5f1f28f333e；S-022图6f7ad961fa49d91bac5398d318514468bdf1a0d943908c6000fc3f675804cabe，FD3d53a7db8a22625f886bff79696736adb55c232eebf4a951ddd8f8a49ee2f0a0。均103817216字节/完整96MiB FAT；归档out/inherited-gop/qualified-native-control-ed1d894-q1及out/inherited-gop/qualified-native-control-ed1d894-q2，资格reports/enuma-native-display-q1/q2-qualification.json、实际代码reports/enuma-native-display-code.json。旧双路观测采集器/完整GOP门不变，不能把本次常量对照当显示进展实测。

新的只读主机采集仅显式--boot-clock启用：重启前捕获旧boot id/uptime，Android完成及分区恢复通过后再取三样本；必须boot-id变化、时序/格式有效、区间相交且宽<=0.25秒、内核原点位于发出之后。不满足则不解码并停止追加、先恢复/交接。样本错误不改写已完成的设备恢复事实。单元覆盖量化/请求延迟、旧boot、非法数值/格式、时钟倒退/不相容及过宽区间，原恢复/fastboot身份和native scope门禁回归通过。

预先固定校准：S-022原点区间减S-021区间，整个差区间必须落在[4,6]秒，且两笔新boot/恢复与摄像均通过，才认为该时基能辨别已知5秒差；任何失败/模糊校准冻结该新计划并停止追加设备动作。即便通过仍只支持时基、非唯一UEFI路径证明；显示谓词须另行新候选，不复用S-019/020或放宽GOP。ADB与Android完成原时序仍完整记录，不为新方法篡改旧判据。

执行前源/两仓发布和全部当前文档对齐；即时唯一enuma身份、A槽/解锁、匹配本地boot_a/vendor_boot_a备份与设备摘要、既有受控/人工恢复路径和相机门禁保持。最近恢复证据out\device-tests\20261025T221621-recovery-reconciliation.json，Android完成/root/A槽/解锁及两分区设备与备份摘要通过；相机桌面已确认。75秒无识别返回仍停止追加，主机期限不冒称固件返回保证。真实GOP、小图案/阶段字、CPU/SMMU扫描源关系、I2C背光及XNU/iPadOS仍未实机闭合。
