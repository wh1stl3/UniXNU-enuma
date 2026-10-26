# 安全交接：D-284，S-047文字可见，旧会话结束并交出写入权

2026-10-26T10:37:59+08:00。按用户已授权的安全收尾指令，本会话不再开启新实验、新实现或构建；完成最终只读恢复核验及文档提交推送后结束，交出写入权，等待管理方创建唯一接续会话。**这是会话安全交接，不是设备硬停。nuwa未改动。**

用户最新主线要求：“继续推进 触发硬停再停 uefi四个字母文字正常显示之后该推进uefi固件开发和日志打印了 应该不需要继续验证该功能”。**固定UEFI字样已经正常显示，不再追加字母、图案或重复点屏验证；接续应直接推进UEFI固件开发、真实日志记录/屏幕输出与启动阶段诊断。**

## 已完成：S-047 / R-019

- 固件main `bb60fb0500f2565cc05cbfd0a20067cae14aecd8`已推送并固定；设备仓实测结果提交 `afbfa49`已推送。当前安全收尾提交只更新交接文档与脱敏最终恢复证据，最终提交ID见git HEAD和本轮最终回复。
- R-019唯一批准镜像 `5e189f4ed32fa9b25a5b07bc974d950fd48929cc19818a12c7c982379ab42f60`已执行并consumed，不重试。S-001..047全部consumed；R-018也已consumed。
- S-047发图2026-10-26 10:17:03+08:00，第0轮fastboot product/enuma、slot/A、unlocked门通过。boot返回0；命令2.625秒、USB断开5.109秒、ADB41.390秒、Android55.625秒。
- 新boot-id三样本origin33.130..33.238秒、宽0.108秒，唯一命中预先声明code5。间接支持该次128x32保存/第二次配置复核/固定文字/500ms保持/精确恢复读回完成，最多12288像素读/8192写/3DSB、660MDP只读/四100ms采样。无原始像素值导出。
- AVI352帧全部解码。frame103(21.922s)无字，104(22.125s)、105(22.344s)可辨认UEFI，106(22.563s)消失，末帧351为Android桌面。可见样本跨度0.219s、外侧开关括区0.641s，与500ms相容，不称精确测时或亮度测量。
- 结果 `reports/enuma-native-route-S-047-result.json`；视觉文字证据 `reports/enuma-s047-visible-text.json`。此前S-046最小白条和恢复证据继续保留。

## 当前设备、进程与工作树

最终独立只读核验 `out\device-tests\20261026T103544-recovery-reconciliation.json` 通过：Android完成、root、A槽、解锁，设备boot_a/vendor_boot_a和本地备份摘要一致。此后不再操作设备。无人工恢复/按键待办，没有触发本轮设备硬停。

S-047设备runner和摄像头命令均已返回0，AVI完整解码，相机已释放；没有本会话正在运行的设备操作、录制、恢复或构建。安全收尾前设备仓与firmware均清洁；收尾仅保存现有状态、最新用户指令和最终恢复报告，完成提交推送并再次检查清洁后结束。**没有R-020候选、没有新日志实现改动、没有未提交的后续源码；关于日志的探索到只读源码审查为止。** 不丢弃任何现有证据。

原始影音、原分辨率帧、裁图和检查图仅本地 `out/camera-capture/20261026T101646-system-transport`，AVI SHA256 `cab404e23d4c9e7426c54a6b08ab3a745fa13eed8947319fa3849adc326503ed`；不上传GitHub/Release/CI/外部存储，不录音。公开的只有经检查的文字/JSON与摘要。只读前置不需相机，真实日志/画面观察再采摄像头。

## 固定构建与来源

工作仓 `D:/Code/UniXNU-enuma`；固件源码是其 `firmware/` 子模块，不是另一份并行checkout。两仓main，禁止并行写入；nuwa、PortingiOS、参考上游只读。

归档 `out/inherited-gop/qualified-native-cpu-text-bb60fb0`；FD `9c5046669399564bbdb61028a4b579dbb7fe3b6b58fc3bb769d5c38b6827482b`；provider `e008583ad4b4190bf249983d7c3eebd85672e7231bb50052496f78b599cbf2de`；Core `a27c5b3f2f58ddfd536a9cdeda722d19482cea2f97c4dae7868e60981d9fa69f`；手工实际代码摘要 `343bc70da6a56a01c554d256b2d90b20e3484736e86ed3180a2002e0b5483422`。qualification/code报告的review_required=false；它们属于已消耗S-047，不能再次执行。

已有主机证据：原对比色回归、文字24种byte排列/所有12288读失败点和8192写失败点/真实stride/完整恢复、两种真实UEFI Arm回调编译，15项native、12项历史pixel、10项FD策略测试通过。收尾没有代码改变，不重复构建/测试。

## 未完成与接续主线

固定四字位图不是全局DEBUG、ConOut/Print、任意字体、真实运行日志、完整GOP或UniXNU菜单通过。左上区域的该次事务和字形可见，不能外推全屏/右半/彩色/持续绘制，不清BLEND|ADDRESS|TOPOLOGY=22、通用alpha、EL1最终stage2/SMMU义务，不改任何verified。

接续首先读AGENTS、本文、DECISIONS、NEED-REVIEW与 `docs/operations/2026-10-26-uefi-console-menu-validation.md`，再按用户最新主线推进真实固件日志与启动链。不要另建字母、白条或字形验证工作项。已审查的关键实现位置：

- `firmware/Platforms/Xiaomi/enumaPkg/Include/PlatformConfig.inc`：全局SerialPortLib实际为Null，现有DEBUG不会因为小区域能显示就自动上屏。
- `firmware/Platforms/Xiaomi/enumaPkg/Application/EnumaProbe/EnumaProbe.c`：Line同时调用Print和DiagDraw；生成的DarwinProbe.inc来自hash-locked上游，不能直接改只读参考源。
- `firmware/Resources/Scripts/enuma_preflight.py`：在隔离staging提取DarwinProbe.inc，复用已锁定DiagFont。原DiagDraw固定ff000000/ffffffff，通道/alpha适配与Print隔离尚未解决。
- `firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedGopLib/InheritedGop.c`：正式GOP仍拒绝requirements!=0；Mu FrameBufferBltLib的RGB转换会丢弃Reserved，仅给Blt输入Reserved=ff不能保证目标alpha为ff。
- `firmware/Platforms/Xiaomi/enumaPkg/Library/InheritedScanoutLib/`中的PixelTransaction.h、PixelText.h、CpuStage1.h与 `firmware/diagnostics/EnumaPixelTransactionArm.h`：已实测的有界mask-aware字形/保存恢复与CPU条件，可作实现参考，不能把consumed镜像重新启动。
- `firmware/patches/dxe-dispatch-details.patch`、`dxe-driver-checkpoints.patch`、`dxe-dispatch-return.patch`及 `diagnostics/EnumaDispatchDetailCheckpoint.h`：当前exact SimpleFb GUID/detail16终端早于BDS返回，控制台连接/Print/菜单没有执行。真实日志接入与启动进展需从这里和实际链接库清单分析，而不是重复静态字样。

本会话没有创建或批准新的日志候选；探索中读过已有CPU查询、原始Blend捕获和字体格式，但没有实施、没有新试验编号。接续不得把探索想法当已完成、已审计或已批准。用户的主线推进指令持续有效，依实际任务范围与以下仍适用边界判断后续动作，不重复申请已经明确授予的批准。

## 授权、硬停与交接边界

R-019只对上述精确镜像的一次128x32固定文字实验授权，现consumed；不恢复旧批准、不重复已发图，不把它伪称通用GOP/寄存器/映射/分区授权。当前用户明确转向UEFI固件开发和真实日志打印；接续要完成授权内实现/构建/审查，避免再以字形功能验证绕行。

原R-004 MDP0xae00000/0x85000、Splash0x9c000000/0x2400000保持。内存基址/大小、任何verified=true、破坏性分区操作等仍按原门禁；禁止擅自flash/erase/改槽。每次新实机前对齐全部当前文档并提交推送，核对选定enuma、身份/备份/恢复、实际所需观测通道和精确构建资格。

恢复未建立code4、75秒无识别恢复、实际恢复失败、所需相机/时基失效或码歧义时停止追加启动，优先恢复并当轮写清原因、候选、设备实际模式、恢复结果及继续条件，再提交推送。发图前身份查询失败按D-233可控恢复核验后仅重入一次；未发图不算consumed，不忽略FAILED正文。正常有效结果不是硬停。

管理方会等待旧会话明确结束，再创建唯一接续会话；旧会话在最终回复后不再写入、不再开启操作。交接入口为本文和docs/STATUS.md，最终提交/清洁/推送状态以本轮最终核验及回复为准。


接续工具环境：Windows Python为 `C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -B`；WSL Ubuntu-22.04的仓库路径 `/mnt/d/Code/UniXNU-enuma`，Python `out/firmware-tools/bin/python -B`，有tomli/uefi_firmware与clang/ASan/UBSan。Windows负责固定AOSP路径的Boot v3打包和相机，WSL负责固件构建/FD/资格/控制台审计；PE反汇编工具在out/reverse-tools。固件实现入口Resources/Scripts/build_enuma_firmware.py，设备仓同名脚本验证clean pin再兼容调用。不要在构建运行中恢复staging或混用不同source pin；历史资格归档保持不变。`work/save_native_route_trial.py`、`work/qualify_cpu_candidate.py`等为本地忽略辅助脚本，现有S-047字段含text=True；使用前审查，不能把旧qualification默认当新的日志候选。
