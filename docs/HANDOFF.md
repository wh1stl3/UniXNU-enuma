# 当前状态：D-225，S-019受控返回，准备互补S-020

2026-10-25T21:54:38+08:00。用户明确“继续推进 触发硬停再停”。本轮恢复显示只读故障隔离及直接临时boot授权；完整资格、当前文档提交推送与即时身份/备份/相机/恢复门禁后执行，不逐笔申请。出现75秒无已识别返回、恢复/采集异常或授权边界问题，立即停止追加并记录硬停。本轮不复活旧图或像素批准，原始影音仅本地out，不录音/上传。

S-019 query1已单次发出并受控回Android、独立恢复通过；S-019 consumed。单笔时序不分类，当前文档推送与即时门禁后继续S-020 query2；S-020尚未发出。时序：{"issued_at": "2026-10-25 21:53:31", "issued_at_utc": "2026-10-25T13:53:31.737879+00:00", "boot_command_return_seconds": 2.625, "fastboot_disconnect_observed_seconds": 5.093, "fastboot_return_seconds": null, "adb_return_seconds": 25.422, "boot_complete_seconds": 39.531}。

新独立入口EnumaNativeObserve：沿已有R-004的Display MDP 0xae00000/0x85000，只允许revision及两路INTF的Timing、Enable、STATUS、Frame八个偏移；STATUS bit0门控Frame，最多26读、两次100ms。完整源与实际PE确认无像素/MMIO写入或GOP发布。原完整Evidence/VideoCapture/Topology/Decode及GOP准入不变，无新内存/board字段/verified/分区变更，RAMOOPS开关均0，未走warm。

诊断谓词是采集成功且两路ActiveThroughout/非零稳定Timing/稳定Enable/两窗非回绕Frame增量1..64均为3；ExactEnable3独立记录，不参与本谓词。query1匹配=>2秒，其他情况（包括metadata/采集拒绝）=>7秒；query2精确反转。二者均在相同精确GUID的CoreStartImage返回hook终止，不让失败流向后续dispatcher。延时仅支持间接分类，不是直接寄存器日志，更不是可见显示。

预先固定配对negative-minus-positive：ADB出现与Android完成两项均+3..+7秒支持本谓词；均-7..-3秒支持其补集；其余ambiguous并停止追加这对计划。跨启动状态变化、Android噪声仍可混淆。补集含metadata/采集失败，不能唯一写为接口停止。未取得本机真实值前不放宽完整GOP准入。

固定固件57ae4ffb136f5330d6e9b759f21202f1d12cebc5已推送。S-019镜像14ae5bb1ba4cdabae2bbc9744d724bf3a4fdf1378bdba06d1586e2d2d36a84d5，FD49df9f370cf1ef38640cda339c014617334a0c7578cacfad17942436bae0acd8；S-020镜像7379bf4da9f31357f076c4652f62365452a194901565ecd710ada74972a2c463，FD37f3e7ab6027896b5a131cdd982e8bb157e375467b217b13e510946d972987e0。两份均103817216字节，完整96MiB FAT、Boot v3回环、实际PE/编译宏/源/映射记录与不可变归档通过。归档out/inherited-gop/qualified-native-57ae4ff-q1/q2；资格reports/enuma-native-display-q1/q2-qualification.json，代码reports/enuma-native-display-code.json。

48项ASan/UBSan与AArch64对象通过，原Mu Blt/拓扑/330边界oracle/164结果回归通过；新增混合CLI与8项错误scope门禁回归通过。实际Core可执行段与S-010已审cold终止代码一致，provider全代码及互补差异已审并绑定摘要；原INF/构造器、Reset库缺席保持。主判断仍是精确Enable门在观察之前拒绝（中等置信），原生setup写3的反证保留；本次独立观测用于检验该判断，而非预写结果。

最新独立恢复证据out\device-tests\20261025T215438-recovery-reconciliation.json：Android完成/root/A槽/解锁/设备与本地备份双分区摘要通过；相机前置桌面已目视。实际runner在每笔前再次核对唯一enuma、匹配备份、fastboot精确机型/槽/解锁，发出后先确认断开再接受返回。主机75秒期限不是固件自动返回保证。相机录制关键节点，原图保留并自行旋转，按键动作不明确时不猜测。

历史S-018 warm对照已超时并恢复；所有S-001..018及旧R-005/R-007均consumed、不重试。显示交付仍须相机确认固件自产色条/阶段字及受控恢复；真实GOP、扫描源CPU/SMMU关系、背光I2C ABI及XNU/iPadOS仍未实机闭合。下一步由本对结果决定继续闭合路由/源布局或分解活动性；不以整套warm/ramoops修通作为显示前置。
