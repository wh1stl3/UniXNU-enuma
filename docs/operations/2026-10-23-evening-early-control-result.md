# 晚间首笔early-control实测

2026-10-23 Asia/Shanghai。用户先授权本机USB摄像头采集，调整取景后明确“启动镜像看看”。本笔只执行既有计划第一项，未追加目标2/7/2。

## 实际动作与结果

先复查三镜像bundle，再打开Rapoo摄像头/DirectShow，录像和第一帧成功后调用已有scripts/run_enuma_entry_probe.py。runner核对唯一enuma、Android完成/root/BL解锁/槽_a、备份和boot_a/vendor_boot_a原摘要；重启fastboot并核对产品/槽/解锁后仅fastboot boot。

镜像early-control-2s，固件82ce8a5，SHA297110a4b97fb05a146b128050837445d719806e21f2e4ddb0cd63c388601996。18:24:02 +08临时启动返回0；ADB16.134秒，Android完成30.613秒，root与原boot/vendor_boot摘要通过。用户随后确认没有按电源/音量键，设备自行返回。未见返回fastboot，不将其记为fastboot路径验证；恢复终点为Android。无flash/erase/改槽。

本候选是stage12/ordinal1加载前2秒早期对照，不含菜单/XNU或屏幕文字输出目标。单次自行返回支持可控恢复，但不是精确证明入口门命中，更不是SimpleFb主体/GOP协议/出图通过。原233a9d8首次需人工恢复的失败保持。

## 外部画面

1920×1080 MJPG录像约50.37秒墙钟，摄像头先于试前检查开始，覆盖fastboot切换/临时启动与Android恢复。原录像及逐秒帧仅out/camera-capture/20261023T182341-early-control，原runner结果在out/device-tests/20261023T182347-dxe-queue-entry；不提交或公开相机原画面。

抽查录像相对起点17秒为黑屏/反光、25秒为小米/Android标志、35秒为HyperOS、49秒为Android锁屏；抽查未见UEFI文字。不是逐帧全图OCR，也不能从未见文字推断驱动未执行。所有录像帧可解码且数量匹配单调时钟时间戳；AVI头固定5fps，实际抓帧间隔有抖动，时序分析用observation.local.json逐帧时间戳，不用播放器时长替代boot发出后的ADB计时。

公开[结果摘要](../../reports/enuma-evening-early-control.json)含镜像/录像摘要、恢复状态与用户确认，不含序列号或原画面。相机采集进程已经退出并释放设备。下一项仍是SimpleFb GUID调用前2秒，须独立复核恢复/观测条件，不盲跑整组。
