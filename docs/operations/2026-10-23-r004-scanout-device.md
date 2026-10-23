# R-004映射与有界只读实测

用户明确批准R-004最小映射与只读探针。固件9f50890已推送；原迁移表不改，在staging应用Display MDP 0x0ae00000/0x85000一条映射。实际staging差异检查确认其余区域字节一致。无RAM/heap/owned/verified或像素/寄存器写入变更。

25个只读谓词host用例O1/Oz+ASan/UBSan通过，AArch64对象无外部依赖；既有240 GOP用例/标记传输通过。对照step3和step8全链接、源锁、FD/30OEM/BootShim/v3、AutoGen/库、bundle四负例及workspace均通过。源锁58文件。actual linked step8 DLL/map/反汇编已归档在对应out/entry-probe目录。

第一次对照在fastboot身份门前置中止，未发boot；产品/槽/解锁GetVar均返回Variable Not found。精确选定原target正常reboot后Android/root/原槽/解锁/原摘要核验通过，保留为独立identity-abort。新一轮完整身份门通过才执行候选，未放宽解析。

22:37:26映射对照ADB15.878秒、完整核验29.626秒。22:39:15 step8 selector1 ADB21.187秒、核验37.050秒。两次用户确认全程无按键，Android/root/原摘要通过。step8比对照慢5.309秒，提示未命中成功门/走同步完成兜底；不称获得数值快照或描述匹配。互补selector2正在构建，只反转既有Core标记门，不改读取代码。

探针最多八管线/72次32位只读。即使谓词通过也不证明管线活动或颜色顺序。当前无绘制授权扩展，不直接启用SerialPortLib。若超时立即停追加并恢复，人工恢复后持续离线隔离，不原样重试失败镜像。原始设备标识、截图和产物仅out，不发布。

互补实测补充：22:45:27 selector2 ADB15.876秒/核验31.930秒，用户确认全程未按键。与selector1差5.311秒，支持严格谓词被拒绝且扫描返回的分类，仍无具体失败字段或数值/活动管线证据。互补源码输入相同，唯一定义差异为ENUMA_DIAG_GOP_QUERY，实际FD/v3及依赖审计通过。下一步先拆分候选地址存在性和其余字段，不写屏。
