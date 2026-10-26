# 当前状态：D-283，S-047固定UEFI文字可见，已恢复Android

2026-10-26T10:25:23+08:00。R-019唯一镜像5e189f4ed32fa9b25a5b07bc974d950fd48929cc19818a12c7c982379ab42f60已执行并consumed，不重试。**左上区域首次可辨认固定UEFI文字；不是全局DEBUG、ConOut/Print、真实日志或UniXNU菜单通过。** 当前无硬停；按结果继续推进有界真实日志/控制台离线工作。固件bb60fb0500f2565cc05cbfd0a20067cae14aecd8已推送并固定，历史S-046白条证据保留。

## 本次实机与视觉结果

S-047于2026-10-26 10:17:03+08:00发图，fastboot product/A槽/unlocked第0轮通过。boot返回0，命令2.625秒，USB断开5.109秒，ADB41.390秒，Android55.625秒。新boot-id三样本origin33.130..33.238秒、宽0.108秒，唯一命中预声明code5。它间接支持本次4096字保存/第二次原始配置复核/文字图案/500ms/精确恢复读回，最多12288读/8192写/3DSB，660MDP只读/四100ms采样等待，运行EL1且覆盖页NormalWT；不导出原始像素数值。

AVI352帧全部可解码，完整屏幕/原点可见。人工检查原分辨率帧与只作最近邻放大的局部：frame103(21.922s)无字，104(22.125s)、105(22.344s)可辨认UEFI，106(22.563s)消失；可见样本跨度0.219s，开关外侧括区0.641s，与500ms保持相容，不称精确时长/亮度测量。末帧351为Android桌面。此为固定四字位图，不是任意字体或运行日志系统。

结果reports/enuma-native-route-S-047-result.json；文字视觉证据reports/enuma-s047-visible-text.json。原始影音和检查图仅out/camera-capture/20261026T101646-system-transport，AVI SHA256cab404e23d4c9e7426c54a6b08ab3a745fa13eed8947319fa3849adc326503ed，不上传、不录音。

## 恢复与证据边界

最新独立恢复 `out\device-tests\20261026T101839-recovery-reconciliation.json`：Android完成/root/A槽/解锁，boot_a/vendor_boot_a及本地备份摘要一致。S-001..047全部consumed，R-018/R-019均consumed，不复用单图授权。此次没有发图前拒绝或硬停。

主判断：左上128x32内的继承CPU视图和mask-aware白/黑组合已能产生可辨认字形，并完成本次恢复。新增行8..31的该次读写完成获得code5支持。仍不证明全屏/右半/彩色/持续更新或完整物理路由，不清BLEND|ADDRESS|TOPOLOGY=22、通用alpha/最终stage2/SMMU义务，不能发布正式GOP或改任何verified。

## 下一步与硬停

离线推进来自真实CPU/固件状态的有界日志记录、编码和显示，而非再只验静态字样；优先复用已有安全数据，避免新MRS/寄存器/映射。全局DEBUG仍Null SerialPort，Print/DiagDraw/GraphicsConsole/菜单已存在但尚未执行或接入合格GOP；当前诊断早于BDS返回。原DiagDraw固定颜色和Mu Blt Reserved丢弃问题仍待生产接入解决，见operations/2026-10-26-uefi-console-menu-validation.md。

只读前置ADB/fastboot/校准时序，不采相机；实际文字/画面连续本地记录。无按键待办。新镜像/像素范围不继承已消耗R-019；离线与已有只读授权继续。code4恢复未建立、75秒无识别恢复、恢复失败、所需相机/时基失败或时间码歧义时停止追加并当轮文档/恢复/提交推送。发图前身份异常按D-233可控恢复后仅一次重入，不重试任何已发图。
