# SimpleFb PE入口返回层实测

2026-10-23 Asia/Shanghai。在[point20调用前2/7/2](2026-10-23-simplefb-guid-timing-result.md)形成时序证据后，沿用户继续实机、自行录像授权，复用既有point21直接PE返回门，不增加或修改固件源码。

## 候选与构建

固定固件82ce8a53b6146df003414cf712237929348bbc57、UniXNU5fdbd5d及相同source_inputs；完整SimpleFb文件GUID dcfd1e6d-788d-4ffc-8e1b-ca2f75651a92、GUID-only、ordinal1占位，stage13/detail21。保留SimpleFb metadata Blt拒绝绘制和EnumaProbe早退；正常Dispatcher完成7秒兜底保持，不能覆盖驱动内部卡死。内存/example/verified/OEM字节不变。

| 延时 | FD SHA256 | boot v3 SHA256 |
| --- | --- | --- |
| 2秒 | 316f4b4ddf308127577f1a48e0f38ea23d4688bf435c94944532a6bbfdaf9523 | 307cf2f1026b2767920a9b7f111362309e53730be07fe8a86acab0a30ab7030f |
| 7秒 | 见结构报告 | 22839e0f4217393cf8858214c96d329bb69aecf5be73f95b12fbe861010fa758 |

实际AArch64、官方Core patch还原、30原厂PE/DEPEX、3MiB FD、192B BootShim、raw/v3及官方unpack逐字节回读通过。两份归档的完整source_inputs与point20一致，实际FD/镜像摘要重新计算通过。build/workspace qualification串行，后者重查通过。[构建与运行结构报告](../../reports/enuma-simplefb-return-timing.json)含完整源锁/FD信息；产物只在out。

归档名：out/entry-probe/evening-simplefb-return-guid-only-queue1-stage13-delay{2,7}-point21-guiddcfd1e6d-simplefb-metadata。最后一次2秒严格复用第一次同镜像，不重建。

## 三笔实际结果

| 发出时间 +08 | 延时 | ADB首次返回秒 | Android完成秒 |
| --- | --- | --- | --- |
| 18:37:42 | 2秒 | 16.102 | 31.777 |
| 18:42:34 | 7秒 | 22.565 | 36.202 |
| 18:43:41 | 原2秒复测 | 16.081 | 29.909 |

均为临时fastboot boot，启动前完整身份/备份/原摘要门禁通过，试后Android完成/root/boot_a与vendor_boot_a原摘要通过。用户明确确认三笔全程均未按电源或音量键；runner没有在返回fastboot路径主动发恢复reboot。未flash/erase/改槽。

7秒减两端2秒为6.463/6.484秒，两个2秒样本相差-0.021秒。差值大于配置增加的5秒，不能伪称精确5秒或把差额归因驱动；USB检测、原厂启动、轮询等仍有噪声。结合两次短延时重复与调用前对照，响应支持完整GUID的point21直接PE EntryPoint返回路径已到达，强于单次复位或仅7秒完成兜底。这是时序推断，非直接执行日志或已读EFI状态。

## 结论与限制

固定Core Image.c在 `Image->Status = Image->EntryPoint(...)` 之后调用point21，位于CoreExit/LongJump之前；包装器含构造器与驱动入口，因此该响应支持本轮SimpleFb包装器已返回，削弱“稳定卡在其内部”的解释。不能由此排除所有偶发卡死，也不能追溯解释旧233a9d8失败。

point21不筛选返回值，成功、失败均可命中。SimpleFb可能在GetFrameBufferInfos/AllocateGopMemory/SetFrameBufferModeDetails/CreateFrameBufferConfig/InstallMultipleProtocolInterfaces返回错误；EFI_SUCCESS/GOP安装、模式字段、实际scanout/像素可用都未证明。CoreExit后、StartImage最终返回、后续DXE/BDS也尚未证明，不能提前撤绘制守卫或称菜单可用。

下一步优先复用既有StartImage成功/失败门（17/16）或明确状态观测，确认是否完成返回和状态；再核对唯一GOP、QueryMode/几何/FB范围与受控绘制条件。不能把本报告转写成*_verified=true，不能以它启用XNU/菜单全路径。

## 录像

三段均1920×1080 MJPG，所有帧完整解码且数量与单调时间戳一致。私有目录out/camera-capture/20261023T183721-simplefb-return-2s、20261023T184213-simplefb-return-7s、20261023T184320-simplefb-return-2s，对应设备结果183728、184220、184327。报告仅发布摘要/计数，不公开原画面、序列号或原日志。

抽查首2秒25秒小米标志、7秒25秒黑屏/54秒Android锁屏、末2秒48秒锁屏，未见需辨认的UEFI日志；没有进行逐帧OCR，不能排除未抽查瞬间内容。使用者说“看不清再手机复现”已记入流程，本轮没有需手机补录节点。摄像头均已释放，当前设备保持最后一笔核验通过后的Android。
