# OEM progress-v2：分阶段可见取证候选

2026-10-27。用户要求调整OEM候选镜像；只在enuma-oem-display隔离worktree开发和构建，不上机。R027与旧OEM镜像17d0169e6bd1…保留，不回写旧资格。新版源码变化会使旧资格的当前源码校验过期，不将旧资格重新绑定到新源码。

## 实验与观察

保持原始DisplayDxe与本机K81资源，不加入MMU-only补丁，不加入XNU或UFS。采用显式oem-progress-v2实验配置、新session/trial，最多五个独立320×160窗口，各8秒，总等待最多40秒。每个窗口重新取样路由及CPU属性，保存/写入/恢复/反读；前一个恢复未确认或任何取证失败即终止。

| 阶段 | 触发 | 能证明的范围 |
| --- | --- | --- |
| E01 | 首个包装服务转发前 | 已到达该调用前的记录与取证路径 |
| S02 | 同一服务实际返回后 | 该服务返回及真实EFI_STATUS |
| E03 | 首次SID GUID的LocateProtocol转发前 | 已到达该查找调用前 |
| S04 | 对应LocateProtocol实际返回后 | 查找返回及真实EFI_STATUS，不能证明协议方法完成 |
| S05 | 精确目标句柄的CoreStartImage返回后 | 真实驱动启动返回值，不代表GOP、ConOut或BDS成功 |

SID GUID固定54b6d3b4-5d33-4f91-8600-6c41d5deb19a。若首个服务就是SID查找，阶段顺序允许01、03、02、04、05；若未查找SID则没有03/04。再次查找不重复绘制。阶段5没有服务call/RVA，Q表示trace的下一序号；其他阶段Q为真实事件序号。

每页严格5行×20字符：首行E/S与两位阶段及C调用号；Q序号；O调用者RVA；进入页为E无状态、返回页为S加完整状态；G为本次64位session标识。只使用既有字库。scripts/decode_oem_progress_page.py要求明确session和完整转录，不将输入文字当作已拍到的屏幕。原始媒体仍仅本地。

## 覆盖与限制

三项Boot Services包装器继续记录原始调用，新增AfterForward观察器仅在实际转发返回、记录完成并恢复TPL之后运行。没有伪造OEM成功或修改返回值。Core返回钩子放在真实CoreStartImage调用之后、既有point13停点之前；静态状态和上下文保持整个驱动生命周期。

没有独立看门狗、跨AP/DMA排他证明或持久RAM取证。如果OEM在首个包装服务前卡住，不会出现首屏；SID协议内部四个方法和直接MMIO仍无覆盖。后段OEM改变扫描/CPU状态可能导致画面出口拒绝，因此没有S05不能直接判OEM未返回。每次8秒观察会扰动时序，最后一张可见画面不是根因定位。

新镜像先解决阶段区分；生产GOP/模式/真实扫描、DarwinBoot/EBS/XNU入口属于后续独立停点，本次不自动延伸。新候选尚未实测，不继承旧候选的单次执行许可。恢复实机前须当前身份/备份/恢复路径、录像和人工恢复准备；75秒无返回停止追加，沿既有恢复流程处理。

## 软件验证

out/oem-progress-20261027/check3：状态机、五阶段输出失败、真实错误码、原服务不返回、重复SID、无服务调用的驱动返回、TPL/重入/计数耗尽，以及像素保存/恢复异常，通过ASan/UBSan。原precall/service回归也通过。

binding3：精确PE重定位/句柄绑定、交叉变体拒绝及新板级AArch64对象检查通过。Python阶段解码/候选/模拟运输等29项通过。binding1宏与类型名冲突失败已修正，失败输出保留。最终FD/机器码/Boot v3结果待后续本节追加，不能预写通过。
## 最终软件资格

build2完整FD通过；qualification1最终机器码审查、32项删除指令拒绝、原厂PE/FV审计、Boot v3/AOSP解包往返通过。镜像SHA256 adbb2c41216bc0c934af4046fe8c0127ce40a6c22c12bfc3f2c7880eee80679f，位于out/oem-progress-20261027/qualification1/image.img。check4宿主回归通过，binding3通过，Python 29项通过。首次build1因保留旧分支函数未使用告警失败，标注两个兼容函数unused后重建，未关闭整体告警；失败日志保留。

编译器将Core返回钩子内联进CoreDispatcher。审计实际机器码中CoreStartImage之后的句柄门控、x0状态保存/恢复和OemProgressReturned调用，并逐项删除指令验证拒绝；没有依赖已被优化掉的源码符号。

固件源码已本地提交3adfb77。镜像仍按bdfe65f6基准加显式源码快照描述，不冒充干净提交构建。旧OEM及R027摘要复核不变。单次ledger未消费；当前不上机，共享主线不改，新源码及报告本地保存。
