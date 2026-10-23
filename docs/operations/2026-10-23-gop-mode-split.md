# Mode 读取拆分

固件26b1f99，保留旧0–4语义，新增5指针存在、6 Mode头、7 Info字段。只构建同源step2与step5，两者唯一固件宏差异为阶段编号。仍禁绘制，不调用QueryMode、不解引用显存，Core负责返回。旧step3失败原因仍未知。

主机240用例分别在O1/Oz、ASan/UBSan通过，包含四个提前退出边界；七AArch64对象、48标记、六固定Mu传输和七CLI拒绝检查通过。实际两份FD/30OEM/BootShim/v3与AutoGen/库清单通过，bundle四项负例及workspace通过。报告reports/enuma-gop-mode-split.json、reports/enuma-gop-audit-host.json。

新step2于21:45:28临时启动，ADB17.024秒、完整核验28.813秒，Android启动/root/原分区摘要通过；是否无按键尚待用户答复。原始目录见reports/enuma-gop-mode-device.json。step5已构建未启动。未flash/erase/改槽，未改内存或verified。

按用户最新规则，人工恢复后继续离线分析和出新软件。用户另提出构建职责归属：下一里程碑将编译入口迁至固件仓，设备仓保留版本校验薄封装及打包/设备/恢复职责；本组证据先固定，不混淆构建迁移与诊断变化。
